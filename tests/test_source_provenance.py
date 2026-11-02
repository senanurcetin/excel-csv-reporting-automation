"""Offline provenance regression checks for the reporting input files."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from processor import hash_source_file, run_pipeline  # noqa: E402


def test_report_hashes_original_csv_and_workbook_bytes(tmp_path):
    sales = ROOT / "inputs" / "sales.csv"
    customers = ROOT / "inputs" / "customers.xlsx"
    output = tmp_path / "report"

    result = run_pipeline(sales, customers, output)
    expected = {
        "sales_csv": hashlib.sha256(sales.read_bytes()).hexdigest(),
        "customers_xlsx": hashlib.sha256(customers.read_bytes()).hexdigest(),
    }
    assert result["source_sha256"] == expected
    saved = json.loads((output / "validation_summary.json").read_text(encoding="utf-8"))
    assert saved["source_sha256"] == expected
    assert all(len(digest) == 64 for digest in expected.values())


def test_input_byte_change_changes_digest_even_when_records_match(tmp_path):
    source = ROOT / "inputs" / "sales.csv"
    customers = ROOT / "inputs" / "customers.xlsx"
    modified = tmp_path / "modified-sales.csv"
    modified.write_bytes(source.read_bytes() + b"\n")

    before = run_pipeline(source, customers, tmp_path / "before")
    after = run_pipeline(modified, customers, tmp_path / "after")
    assert before["source_rows"] == after["source_rows"]
    assert before["source_sha256"]["sales_csv"] != after["source_sha256"]["sales_csv"]
    assert before["source_sha256"]["customers_xlsx"] == after["source_sha256"]["customers_xlsx"]


def test_hash_source_file_supports_empty_and_large_binary_inputs(tmp_path):
    path = tmp_path / "example.bin"
    for data in (b"", b"abc", b"R" * (1024 * 1024 + 43)):
        path.write_bytes(data)
        assert hash_source_file(path) == hashlib.sha256(data).hexdigest()
