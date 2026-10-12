"""Regression tests for input boundaries, reconciliation, and report safety.

All pipeline scenarios use synthetic in-memory customer references; the tests
do not need a production database, live services, or external credentials.
"""
from __future__ import annotations

import csv
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import processor  # noqa: E402
from processor import (  # noqa: E402
    DataQualityError,
    SALES_COLUMNS,
    read_sales,
    safe_csv_text,
    validate_sale,
    write_csv,
)
from reporting import chart_rows, issue_rows  # noqa: E402


@pytest.fixture
def customers():
    return {
        "C-1": {
            "customer_id": "C-1",
            "customer_name": "Test Customer",
            "segment": "Enterprise",
            "region": "West",
        }
    }


def sale(**changes):
    row = {
        "order_id": "ORD-1",
        "order_date": "2024-02-29",
        "customer_id": "C-1",
        "category": "hardware",
        "quantity": "3",
        "unit_price_usd": "1.25",
        "status": "paid",
    }
    row.update(changes)
    return row


def write_sales(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=SALES_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


@pytest.mark.parametrize(
    ("status", "expected_revenue"),
    [
        ("paid", "3.75"),
        ("completed", "3.75"),
        ("refunded", "0.00"),
        ("cancelled", "0.00"),
    ],
)
def test_revenue_recognition_by_status(customers, status, expected_revenue):
    accepted, problems = validate_sale(sale(status=status), customers)
    assert problems == []
    assert accepted is not None
    assert accepted["order_value_usd"] == "3.75"
    assert accepted["recognized_revenue_usd"] == expected_revenue


def test_sale_normalizes_identifiers_dimensions_and_status(customers):
    accepted, problems = validate_sale(
        sale(order_id=" ord-9 ", customer_id=" c-1 ", category="  spare PARTS ",
             status=" COMPLETED "),
        customers,
    )
    assert problems == []
    assert accepted is not None
    assert (accepted["order_id"], accepted["customer_id"]) == ("ORD-9", "C-1")
    assert (accepted["category"], accepted["status"]) == ("Spare Parts", "completed")


@pytest.mark.parametrize(
    "order_date",
    ["2023-02-29", "2024-02-30", "2024-13-01", "2024-2-9", "2024-02-29T10:00", ""],
)
def test_rejects_invalid_or_non_iso_dates(customers, order_date):
    accepted, problems = validate_sale(sale(order_date=order_date), customers)
    assert accepted is None
    assert "invalid_date" in problems


@pytest.mark.parametrize("quantity", ["0", "-1", "1.0", "1e2", "", "two"])
def test_rejects_nonpositive_or_noninteger_quantities(customers, quantity):
    accepted, problems = validate_sale(sale(quantity=quantity), customers)
    assert accepted is None
    assert "invalid_quantity" in problems


@pytest.mark.parametrize(
    "unit_price",
    ["-0.01", "1.234", "NaN", "Infinity", "-Infinity", "", "one dollar"],
)
def test_rejects_negative_overprecise_or_nonfinite_prices(customers, unit_price):
    accepted, problems = validate_sale(sale(unit_price_usd=unit_price), customers)
    assert accepted is None
    assert "invalid_unit_price" in problems


def test_collects_independent_quality_issues_for_one_row(customers):
    accepted, problems = validate_sale(
        sale(order_id="", customer_id="UNKNOWN", category="", status="pending",
             order_date="2024-02-30", quantity="0", unit_price_usd="NaN"),
        customers,
    )
    assert accepted is None
    assert set(problems) == {
        "missing_order_id", "unknown_customer", "missing_category",
        "invalid_status", "invalid_date", "invalid_quantity",
        "invalid_unit_price",
    }


def test_read_sales_accepts_bom_and_normalizes_headers(tmp_path):
    path = tmp_path / "orders.csv"
    headers = ",".join(f" {key.upper()} " for key in SALES_COLUMNS)
    values = ",".join(sale()[key] for key in SALES_COLUMNS)
    path.write_text("\ufeff" + headers + "\n" + values + "\n", encoding="utf-8")
    assert read_sales(path) == [sale()]


def test_read_sales_rejects_duplicate_normalized_headers(tmp_path):
    path = tmp_path / "orders.csv"
    path.write_text(",".join([*SALES_COLUMNS, " ORDER_ID "]) + "\n",
                    encoding="utf-8")
    with pytest.raises(DataQualityError, match="duplicate column names"):
        read_sales(path)


def test_read_sales_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(DataQualityError, match="empty"):
        read_sales(path)


def test_pipeline_quarantines_case_insensitive_conflicting_ids(tmp_path, customers, monkeypatch):
    monkeypatch.setattr(processor, "read_customers", lambda _: customers)
    path = tmp_path / "orders.csv"
    write_sales(path, [
        sale(order_id="ord-1", category="Hardware"),
        sale(order_id=" ORD-1 ", category="Software"),
        sale(order_id="ord-2", unit_price_usd="2.00"),
    ])
    report = processor.run_pipeline(path, tmp_path / "unused.xlsx", tmp_path / "out")
    assert (report["source_rows"], report["valid_rows"], report["excluded_rows"]) == (3, 1, 2)
    assert report["issues"] == {"conflicting_order_id": 2}
    assert report["recognized_revenue_usd"] == "6.00"
    with (tmp_path / "out" / "quality_issues.csv").open(newline="", encoding="utf-8") as stream:
        rejected = list(csv.DictReader(stream))
    assert [r["_csv_row"] for r in rejected] == ["2", "3"]


def test_pipeline_keeps_one_case_insensitive_exact_duplicate(tmp_path, customers, monkeypatch):
    monkeypatch.setattr(processor, "read_customers", lambda _: customers)
    path = tmp_path / "orders.csv"
    write_sales(path, [
        sale(order_id="ord-1"),
        sale(order_id=" ORD-1 ", customer_id=" c-1 ", category=" HARDWARE ",
             status="PAID"),
    ])
    report = processor.run_pipeline(path, tmp_path / "unused.xlsx", tmp_path / "out")
    assert (report["valid_rows"], report["excluded_rows"]) == (1, 1)
    assert report["issues"] == {"exact_duplicate_order_id": 1}
    assert report["recognized_revenue_usd"] == "3.75"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("=1+1", "'=1+1"),
        ("+SUM(A1:A2)", "'+SUM(A1:A2)"),
        ("-1+2", "'-1+2"),
        ("@SUM(1,2)", "'@SUM(1,2)"),
        ("normal", "normal"),
        ("", ""),
        (None, ""),
    ],
)
def test_csv_formula_safety(raw, expected):
    assert safe_csv_text(raw) == expected


def test_write_csv_escapes_only_designated_text_fields(tmp_path):
    path = tmp_path / "export.csv"
    write_csv(
        path,
        [{"name": "=HYPERLINK(1)", "category": "@Risk", "amount": "1.25"}],
        ["name", "category", "amount"],
        {"name", "category"},
    )
    with path.open(newline="", encoding="utf-8") as stream:
        assert list(csv.DictReader(stream)) == [
            {"name": "'=HYPERLINK(1)", "category": "'@Risk", "amount": "1.25"}
        ]


def test_charts_escape_labels_and_bound_bars():
    html = chart_rows(
        [
            {"category": "<script>alert(1)</script>", "recognized_revenue_usd": "0.00"},
            {"category": "Stable", "recognized_revenue_usd": "3.00"},
        ],
        "category",
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert 'style="width:0.0%"' in html
    assert 'style="width:100.0%"' in html
    assert "$3.00" in html


def test_zero_revenue_charts_do_not_divide_by_zero():
    assert 'style="width:0.0%"' in chart_rows(
        [{"category": "Zero", "recognized_revenue_usd": "0.00"}],
        "category",
    )
    assert "No values available." in chart_rows([], "category")


def test_issue_table_escapes_untrusted_labels():
    html = issue_rows({"<script>alert</script>": 2})
    assert "<script>" not in html
    assert "&lt;Script&gt;" in html
    assert "2</td>" in html
