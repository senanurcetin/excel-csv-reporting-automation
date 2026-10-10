from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from processor import DataQualityError, run_pipeline, safe_csv_text  # noqa: E402


def load_rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_demo_has_reconciled_outputs(tmp_path):
    summary = run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path)
    valid = load_rows(tmp_path / "cleaned_sales.csv")
    rejected = load_rows(tmp_path / "quality_issues.csv")
    assert summary["source_rows"] == summary["valid_rows"] + summary["excluded_rows"]
    assert summary["reconciliation_passed"] is True
    assert len(valid) == summary["valid_rows"]
    assert len(rejected) == summary["excluded_rows"]
    assert len({x["order_id"] for x in valid}) == len(valid)
    assert sum((float(x["recognized_revenue_usd"]) for x in valid)) == pytest.approx(float(summary["recognized_revenue_usd"]))
    assert (tmp_path / "dashboard.html").exists()
    assert (tmp_path / "validation_summary.json").exists()


def test_refunds_and_cancellations_not_in_revenue(tmp_path):
    summary = run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path)
    clean = load_rows(tmp_path / "cleaned_sales.csv")
    for order in clean:
        if order["status"] in ("refunded", "cancelled"):
            assert order["recognized_revenue_usd"] == "0.00"
    assert summary["refunded_orders"] > 0 and summary["cancelled_orders"] > 0


def test_input_anomalies_are_visible(tmp_path):
    report = run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path)
    issues = report["issues"]
    assert issues.get("unknown_customer", 0) >= 1
    assert issues.get("invalid_date", 0) >= 1
    assert issues.get("invalid_quantity", 0) >= 1
    assert issues.get("invalid_unit_price", 0) >= 1
    assert issues.get("exact_duplicate_order_id", 0) >= 1
    assert issues.get("conflicting_order_id", 0) >= 2


def test_adding_unknown_customer_is_quarantined(tmp_path):
    rows = load_rows(ROOT / "inputs/sales.csv")
    row = rows[0].copy()
    row["order_id"] = "NEW-Z999"
    row["customer_id"] = "DOES-NOT-EXIST"
    rows.append(row)
    custom_sales = tmp_path / "input.csv"
    with custom_sales.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summary = run_pipeline(custom_sales, ROOT / "inputs/customers.xlsx", tmp_path / "result")
    assert summary["issues"]["unknown_customer"] >= 2
    assert summary["source_rows"] == len(rows)


def test_bad_schema_fails_fast(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("order_id,quantity\nA,1\n", encoding="utf-8")
    with pytest.raises(DataQualityError, match="missing columns"):
        run_pipeline(path, ROOT / "inputs/customers.xlsx", tmp_path / "out")


def test_csv_formula_injection_protection():
    assert safe_csv_text("=HYPERLINK('evil')").startswith("'")
    assert safe_csv_text("@bad").startswith("'")
    assert safe_csv_text("normal") == "normal"


def test_report_is_deterministic(tmp_path):
    first = run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path / "a")
    second = run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path / "b")
    assert first == second
    assert (tmp_path / "a" / "cleaned_sales.csv").read_bytes() == (tmp_path / "b" / "cleaned_sales.csv").read_bytes()
    assert json.loads((tmp_path / "a" / "validation_summary.json").read_text()) == first


def test_conflicting_order_id_drops_both_rows(tmp_path):
    run_pipeline(ROOT / "inputs/sales.csv", ROOT / "inputs/customers.xlsx", tmp_path)
    valid_ids = {r["order_id"] for r in load_rows(tmp_path / "cleaned_sales.csv")}
    rejected = load_rows(tmp_path / "quality_issues.csv")
    assert "ORD-9001" not in valid_ids
    assert sum("conflicting_order_id" in r["issues"] for r in rejected) == 2
    assert sum(r["order_id"] == "ORD-9001" for r in rejected) == 2


def test_html_escapes_untrusted_category(tmp_path):
    rows = load_rows(ROOT / "inputs/sales.csv")
    rows[0]["category"] = "<script>alert(1)</script>"
    local_file = tmp_path / "input.csv"
    with local_file.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    run_pipeline(local_file, ROOT / "inputs/customers.xlsx", tmp_path / "reports")
    html = (tmp_path / "reports" / "dashboard.html").read_text(encoding="utf-8")
    assert "&lt;Script&gt;Alert(1)&lt;/Script&gt;" in html
    assert "<script>alert(1)</script>" not in html
