"""Offline CLI contract tests for the synthetic CSV/Excel reporting demo.

Exercise the public argparse entry point without a subprocess, network calls or
production data. All reports are written into pytest's temporary directory.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run_demo  # noqa: E402


def invoke(monkeypatch, *, sales: Path | None = None, customers: Path | None = None,
           output: Path | None = None, max_excluded_rows: int | None = None,
           max_excluded_percent: str | None = None):
    args = ["run_demo.py"]
    if sales is not None:
        args += ["--sales", str(sales)]
    if customers is not None:
        args += ["--customers", str(customers)]
    if output is not None:
        args += ["--output", str(output)]
    if max_excluded_rows is not None:
        args += ["--max-excluded-rows", str(max_excluded_rows)]
    if max_excluded_percent is not None:
        args += ["--max-excluded-percent", max_excluded_percent]
    monkeypatch.setattr(sys, "argv", args)
    return run_demo.main()


def test_cli_prints_audited_totals_revenue_and_report_path(tmp_path, monkeypatch, capsys):
    output = tmp_path / "reports"
    assert invoke(monkeypatch, output=output) == 0

    captured = capsys.readouterr()
    report = json.loads((output / "validation_summary.json").read_text(encoding="utf-8"))
    assert report["reconciliation_passed"] is True
    assert report["source_rows"] == report["valid_rows"] + report["excluded_rows"]
    assert (
        f"Input: {report['source_rows']} | Valid: {report['valid_rows']} | "
        f"Excluded: {report['excluded_rows']}"
    ) in captured.out
    assert f"Recognized revenue: ${report['recognized_revenue_usd']} USD" in captured.out
    assert "Quality reconciliation: PASS" in captured.out
    assert f"Open report: {output / 'dashboard.html'}" in captured.out
    assert (output / "dashboard.html").is_file()
    assert captured.err == ""


def test_cli_missing_sales_file_exits_two_without_false_success(tmp_path, monkeypatch, capsys):
    output = tmp_path / "reports"
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, sales=tmp_path / "not-found.csv", output=output)

    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert "Data error:" in captured.err
    assert "not-found.csv" in captured.err
    assert "Quality reconciliation: PASS" not in captured.out
    assert "Open report:" not in captured.out
    assert not (output / "dashboard.html").exists()


def test_cli_bad_sales_schema_exits_two_without_false_success(tmp_path, monkeypatch, capsys):
    bad_sales = tmp_path / "bad-schema.csv"
    bad_sales.write_text("order_id,quantity\nORD-1,1\n", encoding="utf-8")
    output = tmp_path / "reports"

    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, sales=bad_sales, output=output)

    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert "Data error:" in captured.err
    assert "missing columns" in captured.err
    assert "Quality reconciliation: PASS" not in captured.out
    assert "Open report:" not in captured.out
    assert not (output / "dashboard.html").exists()


def test_cli_honors_custom_sales_customers_and_output_paths(tmp_path, monkeypatch, capsys):
    sales = tmp_path / "custom-sales.csv"
    customers = tmp_path / "custom-customers.xlsx"
    output = tmp_path / "custom-output"
    shutil.copyfile(ROOT / "inputs" / "sales.csv", sales)
    shutil.copyfile(ROOT / "inputs" / "customers.xlsx", customers)

    assert invoke(monkeypatch, sales=sales, customers=customers, output=output) == 0
    captured = capsys.readouterr()
    assert f"Open report: {output / 'dashboard.html'}" in captured.out
    assert (output / "dashboard.html").is_file()
    assert (output / "cleaned_sales.csv").is_file()
    assert (output / "validation_summary.json").is_file()
    assert captured.err == ""


def test_cli_quality_gate_returns_distinct_failure_but_keeps_review_artifacts(
    tmp_path, monkeypatch, capsys
):
    output = tmp_path / "review-output"
    assert invoke(monkeypatch, output=output, max_excluded_rows=0) == 3
    printed = capsys.readouterr()
    summary = json.loads((output / "validation_summary.json").read_text(encoding="utf-8"))
    assert summary["excluded_rows"] > 0
    assert (output / "dashboard.html").is_file()
    assert (output / "quality_issues.csv").is_file()
    assert "Quality gate: FAIL" in printed.err
    assert "--max-excluded-rows=0" in printed.err
    assert f"Open report: {output / 'dashboard.html'}" in printed.out


def test_cli_quality_gate_accepts_allowed_exclusions(tmp_path, monkeypatch, capsys):
    output = tmp_path / "acceptable-output"
    assert invoke(monkeypatch, output=output, max_excluded_rows=8) == 0
    printed = capsys.readouterr()
    assert "Quality gate: PASS" in printed.out
    assert printed.err == ""


def test_cli_quality_gate_rejects_negative_threshold_before_writing(
    tmp_path, monkeypatch, capsys
):
    output = tmp_path / "should-not-exist"
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, output=output, max_excluded_rows=-1)
    assert exc.value.code == 2
    assert "non-negative" in capsys.readouterr().err
    assert not output.exists()

def test_cli_percent_gate_accepts_exact_boundary(tmp_path, monkeypatch, capsys):
    output = tmp_path / "at-boundary"
    assert invoke(monkeypatch, output=output, max_excluded_percent="4.00") == 0
    printed = capsys.readouterr()
    assert "Quality gate: PASS" in printed.out
    assert "--max-excluded-percent=4.00" in printed.out
    assert printed.err == ""
    assert (output / "quality_issues.csv").exists()


def test_cli_percent_gate_fails_below_boundary_and_preserves_reports(
    tmp_path, monkeypatch, capsys
):
    output = tmp_path / "below-boundary"
    assert invoke(monkeypatch, output=output, max_excluded_percent="3.99") == 3
    printed = capsys.readouterr()
    assert "Quality gate: FAIL" in printed.err
    assert "--max-excluded-percent=3.99" in printed.err
    assert (output / "validation_summary.json").exists()
    assert (output / "dashboard.html").exists()


def test_cli_combined_gates_require_both_conditions(tmp_path, monkeypatch, capsys):
    output = tmp_path / "both"
    assert invoke(monkeypatch, output=output, max_excluded_rows=8,
                  max_excluded_percent="3.99") == 3
    assert "--max-excluded-percent=3.99" in capsys.readouterr().err
    assert invoke(monkeypatch, output=output, max_excluded_rows=7,
                  max_excluded_percent="4.00") == 3
    assert "--max-excluded-rows=7" in capsys.readouterr().err
    assert invoke(monkeypatch, output=output, max_excluded_rows=8,
                  max_excluded_percent="4.00") == 0
    assert "Quality gate: PASS" in capsys.readouterr().out


@pytest.mark.parametrize("bad", ["-1", "100.01", "NaN", "Infinity", "abc"])
def test_cli_percent_gate_rejects_invalid_values_before_writing(
    tmp_path, monkeypatch, capsys, bad
):
    output = tmp_path / "no-output"
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, output=output, max_excluded_percent=bad)
    assert exc.value.code == 2
    assert "between 0 and 100" in capsys.readouterr().err
    assert not output.exists()


def test_cli_percent_gate_has_defined_zero_source_row_behavior(
    tmp_path, monkeypatch, capsys
):
    sales = tmp_path / "header-only.csv"
    sales.write_text(
        "order_id,order_date,customer_id,category,quantity,unit_price_usd,status\n",
        encoding="utf-8",
    )
    output = tmp_path / "zero-rows"
    assert invoke(monkeypatch, sales=sales, output=output,
                  max_excluded_percent="0") == 0
    assert "Quality gate: PASS" in capsys.readouterr().out
