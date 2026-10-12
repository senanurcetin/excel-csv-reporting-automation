#!/usr/bin/env python3
"""Independently reconcile committed synthetic demo outputs without dependencies.

Validates checked-in aggregates, not the full source-to-output pipeline.
Run from any directory: python scripts/verify_release_evidence.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def money(value: str | Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


def main() -> None:
    summary = json.loads((OUT / "validation_summary.json").read_text(encoding="utf-8"))
    sales = read_rows("cleaned_sales.csv")
    exclusions = read_rows("quality_issues.csv")

    assert len(sales) == summary["valid_rows"], "Clean sales count mismatch"
    assert len(exclusions) == summary["excluded_rows"], "Exclusion count mismatch"
    assert len(sales) + len(exclusions) == summary["source_rows"], "Source reconciliation mismatch"

    normalized = [row["order_id"].strip().upper() for row in sales]
    assert len(set(normalized)) == summary["unique_valid_orders"], "Duplicated valid order ID"

    revenue = sum((money(row["recognized_revenue_usd"]) for row in sales), Decimal("0.00"))
    assert revenue == money(summary["recognized_revenue_usd"]), "Recognized revenue mismatch"

    statuses = Counter(row["status"] for row in sales)
    assert statuses["paid"] + statuses["completed"] == summary["paid_or_completed_orders"]
    assert statuses["refunded"] == summary["refunded_orders"]
    assert statuses["cancelled"] == summary["cancelled_orders"]

    for row in sales:
        recognized = money(row["recognized_revenue_usd"])
        if row["status"] not in ("paid", "completed"):
            assert recognized == 0, "Revenue recognized for refunded/cancelled order"
        else:
            assert recognized == money(row["order_value_usd"]), "Recognized order value mismatch"

    groups = (
        ("category", lambda row: row["category"], "category_kpis.csv"),
        ("month", lambda row: row["order_date"][:7], "monthly_kpis.csv"),
        ("segment", lambda row: row["segment"], "segment_kpis.csv"),
    )
    for key, extract, filename in groups:
        counts: Counter[str] = Counter()
        revenue_by_group: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for row in sales:
            label = extract(row)
            counts[label] += 1
            revenue_by_group[label] += money(row["recognized_revenue_usd"])
        aggregate = read_rows(filename)
        assert set(counts) == {row[key] for row in aggregate}, f"Missing {key} group"
        for row in aggregate:
            label = row[key]
            assert counts[label] == int(row["orders"]), f"{key} order count mismatch: {label}"
            assert money(revenue_by_group[label]) == money(row["recognized_revenue_usd"]), (
                f"{key} revenue mismatch: {label}"
            )

    # No external data is accessed and no outputs are changed.
    print(
        f"PASS: {len(sales)} valid + {len(exclusions)} excluded "
        f"= {summary['source_rows']} source rows; "
        f"recognized revenue USD {revenue:.2f}; "
        "category/month/segment and status reconciliations match."
    )


if __name__ == "__main__":
    main()
