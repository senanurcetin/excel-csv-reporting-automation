"""Reproducible, auditable CSV+Excel cleaning and reporting workflow."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from reporting import build_html

SALES_COLUMNS = (
    "order_id", "order_date", "customer_id", "category", "quantity", "unit_price_usd", "status"
)
CUSTOMER_COLUMNS = ("customer_id", "customer_name", "segment", "region")
VALID_STATUSES = {"paid", "completed", "refunded", "cancelled"}
CENTS = Decimal("0.01")
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


class DataQualityError(ValueError):
    """Raised when a required input/schema or reference table is ambiguous."""


def clean_text(value: object) -> str:
    return str(value if value is not None else "").strip()


def identifier(value: object) -> str:
    return clean_text(value).upper()


def safe_csv_text(value: object) -> str:
    """Protect text fields when CSVs are opened in spreadsheet applications."""
    text = clean_text(value)
    if text and text[0] in FORMULA_PREFIXES:
        return "'" + text
    return text


def money(value: Decimal) -> str:
    return str(value.quantize(CENTS, rounding=ROUND_HALF_UP))


def read_customers(path: Path) -> dict[str, dict[str, str]]:
    # Only read the workbook; all deliverable data outputs are CSV/HTML/JSON.
    import pandas as pd

    frame = pd.read_excel(path, dtype=str, keep_default_na=False, engine="openpyxl")
    frame.columns = [clean_text(col).lower() for col in frame.columns]
    missing = set(CUSTOMER_COLUMNS) - set(frame.columns)
    if missing:
        raise DataQualityError(f"customers.xlsx missing required columns: {', '.join(sorted(missing))}")
    customers: dict[str, dict[str, str]] = {}
    for row_number, data in enumerate(frame[list(CUSTOMER_COLUMNS)].to_dict("records"), start=2):
        cust_id = identifier(data["customer_id"])
        if not cust_id:
            raise DataQualityError(f"customers.xlsx row {row_number}: blank customer_id")
        if cust_id in customers:
            raise DataQualityError(f"customers.xlsx: duplicate customer_id {cust_id}; resolve manually")
        name = clean_text(data["customer_name"])
        segment = clean_text(data["segment"]).title()
        region = clean_text(data["region"]).title()
        if not name or not segment or not region:
            raise DataQualityError(f"customers.xlsx row {row_number}: incomplete customer dimensions")
        customers[cust_id] = {
            "customer_id": cust_id,
            "customer_name": name,
            "segment": segment,
            "region": region,
        }
    if not customers:
        raise DataQualityError("customers.xlsx contains no customers")
    return customers


def read_sales(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataQualityError("sales.csv is empty")
        # Strip harmless header whitespace, reject ambiguous duplicates.
        normalized = [clean_text(col).lower() for col in reader.fieldnames]
        if len(set(normalized)) != len(normalized):
            raise DataQualityError("sales.csv has duplicate column names")
        missing = set(SALES_COLUMNS) - set(normalized)
        if missing:
            raise DataQualityError(f"sales.csv missing columns: {', '.join(sorted(missing))}")
        reader.fieldnames = normalized
        return [dict(r) for r in reader]


def validate_sale(raw: dict[str, str], customers: dict[str, dict[str, str]]) -> tuple[dict | None, list[str]]:
    reasons: list[str] = []
    order_id = identifier(raw["order_id"])
    customer_id = identifier(raw["customer_id"])
    category = clean_text(raw["category"]).title()
    status = clean_text(raw["status"]).lower()
    raw_date = clean_text(raw["order_date"])

    if not order_id:
        reasons.append("missing_order_id")
    if not customer_id or customer_id not in customers:
        reasons.append("unknown_customer")
    if not category:
        reasons.append("missing_category")
    if status not in VALID_STATUSES:
        reasons.append("invalid_status")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
        reasons.append("invalid_date")
    else:
        try:
            date.fromisoformat(raw_date)
        except ValueError:
            reasons.append("invalid_date")

    qty_raw = clean_text(raw["quantity"])
    try:
        if not re.fullmatch(r"\d+", qty_raw):
            raise ValueError
        quantity = int(qty_raw)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        quantity = 0
        reasons.append("invalid_quantity")

    try:
        price = Decimal(clean_text(raw["unit_price_usd"]))
        if not price.is_finite() or price < 0 or price.as_tuple().exponent < -2:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        price = Decimal("0")
        reasons.append("invalid_unit_price")

    if reasons:
        return None, reasons
    joined = {**customers[customer_id],
        "order_id": order_id,
        "order_date": raw_date,
        "category": category,
        "quantity": quantity,
        "unit_price_usd": money(price),
        "order_value_usd": money(price * quantity),
        "status": status,
        "recognized_revenue_usd": money(price * quantity if status in {"paid", "completed"} else Decimal("0")),
    }
    return joined, []


def write_csv(path: Path, rows: list[dict], cols: list[str], text_cols: set[str] | None = None) -> None:
    text_cols = text_cols or set()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({col: safe_csv_text(r.get(col, "")) if col in text_cols else r.get(col, "") for col in cols})


def run_pipeline(sales_path: Path, customers_path: Path, output_dir: Path) -> dict:
    sales_path, customers_path, output_dir = Path(sales_path), Path(customers_path), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    customers = read_customers(customers_path)
    raws = read_sales(sales_path)

    staged: list[dict] = []
    excluded: list[dict] = []
    seen_ids: dict[str, list[dict]] = defaultdict(list)
    for line, raw in enumerate(raws, start=2):
        normalized = {c: clean_text(raw[c]) for c in SALES_COLUMNS}
        normalized["_csv_row"] = line
        # Track all duplicate IDs, including invalid rows, to avoid accidental reuse.
        if identifier(raw["order_id"]):
            seen_ids[identifier(raw["order_id"])].append(normalized)
        staged.append(normalized)

    conflicted_ids: set[str] = set()
    identical_ids: set[str] = set()
    for oid, group in seen_ids.items():
        if len(group) < 2:
            continue
        signatures = {tuple(clean_text(r[c]).strip().lower() for c in SALES_COLUMNS) for r in group}
        if len(signatures) > 1:
            conflicted_ids.add(oid)
        else:
            identical_ids.add(oid)
    identical_first_seen: set[str] = set()
    accepted: list[dict] = []
    for raw in staged:
        oid = identifier(raw["order_id"])
        validated, reasons = validate_sale(raw, customers)
        if oid in conflicted_ids:
            reasons.append("conflicting_order_id")
        elif oid in identical_ids:
            if oid in identical_first_seen:
                reasons.append("exact_duplicate_order_id")
            else:
                identical_first_seen.add(oid)
        if reasons:
            excluded.append({**raw, "issues": ";".join(sorted(set(reasons)))})
        else:
            assert validated is not None
            accepted.append(validated)

    category_totals = defaultdict(lambda: {"orders": 0, "recognized_revenue": Decimal("0")})
    month_totals = defaultdict(lambda: {"orders": 0, "recognized_revenue": Decimal("0")})
    segment_totals = defaultdict(lambda: {"orders": 0, "recognized_revenue": Decimal("0")})
    status_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()
    paid_value = refunded_value = cancelled_value = Decimal("0")
    for row in accepted:
        revenue = Decimal(row["recognized_revenue_usd"])
        amount = Decimal(row["order_value_usd"])
        status_counts[row["status"]] += 1
        if row["status"] in {"paid", "completed"}:
            paid_value += amount
        elif row["status"] == "refunded":
            refunded_value += amount
        else:
            cancelled_value += amount
        for key, val in ((category_totals, row["category"]), (month_totals, row["order_date"][:7]), (segment_totals, row["segment"])):
            key[val]["orders"] += 1
            key[val]["recognized_revenue"] += revenue
    for row in excluded:
        issue_counts.update(row["issues"].split(";"))

    report: dict = {
        "source_rows": len(raws),
        "valid_rows": len(accepted),
        "excluded_rows": len(excluded),
        "reconciliation_passed": len(accepted) + len(excluded) == len(raws),
        "unique_valid_orders": len({r["order_id"] for r in accepted}),
        "recognized_revenue_usd": money(paid_value),
        "refunded_order_value_usd": money(refunded_value),
        "cancelled_order_value_usd": money(cancelled_value),
        "paid_or_completed_orders": status_counts["paid"] + status_counts["completed"],
        "refunded_orders": status_counts["refunded"],
        "cancelled_orders": status_counts["cancelled"],
        "issues": dict(sorted(issue_counts.items())),
        "category_kpis": [{"category": name, "orders": v["orders"], "recognized_revenue_usd": money(v["recognized_revenue"])} for name, v in sorted(category_totals.items())],
        "monthly_kpis": [{"month": name, "orders": v["orders"], "recognized_revenue_usd": money(v["recognized_revenue"])} for name, v in sorted(month_totals.items())],
        "segment_kpis": [{"segment": name, "orders": v["orders"], "recognized_revenue_usd": money(v["recognized_revenue"])} for name, v in sorted(segment_totals.items())],
        "business_rules": [
            "All sample inputs are synthetic; no client data is included.",
            "Customer IDs and order IDs are case-insensitive and trimmed.",
            "Paid/completed orders contribute to recognized revenue; refunded/cancelled orders contribute zero.",
            "Refunded/cancelled order value is displayed separately, not double-subtracted.",
            "Only YYYY-MM-DD order dates are accepted; prices allow at most two decimal places.",
            "Conflicting repeated order IDs quarantine all involved rows; exact duplicates retain one row.",
            "Unknown customers and invalid business-critical fields are excluded and logged."
        ]
    }

    columns = ["order_id", "order_date", "customer_id", "customer_name", "segment", "region", "category", "quantity", "unit_price_usd", "order_value_usd", "status", "recognized_revenue_usd"]
    write_csv(output_dir / "cleaned_sales.csv", accepted, columns, {"order_id", "customer_id", "customer_name", "segment", "region", "category", "status"})
    write_csv(output_dir / "quality_issues.csv", excluded, ["_csv_row", *SALES_COLUMNS, "issues"], set(SALES_COLUMNS) - {"quantity", "unit_price_usd"} | {"quantity", "unit_price_usd"})
    write_csv(output_dir / "category_kpis.csv", report["category_kpis"], ["category", "orders", "recognized_revenue_usd"], {"category"})
    write_csv(output_dir / "monthly_kpis.csv", report["monthly_kpis"], ["month", "orders", "recognized_revenue_usd"])
    write_csv(output_dir / "segment_kpis.csv", report["segment_kpis"], ["segment", "orders", "recognized_revenue_usd"], {"segment"})
    (output_dir / "validation_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "dashboard.html").write_text(build_html(report), encoding="utf-8")
    return report
