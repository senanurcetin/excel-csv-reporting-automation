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
           output: Path | None = None):
    args = ["run_demo.py"]
    if sales is not None:
        args += ["--sales", str(sales)]
    if customers is not None:
        args += ["--customers", str(customers)]
    if output is not None:
        args += ["--output", str(output)]
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
