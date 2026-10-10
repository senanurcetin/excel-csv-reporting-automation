"""CLI: python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx"""
from __future__ import annotations

import argparse
from pathlib import Path

from processor import DataQualityError, run_pipeline


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Clean synthetic Excel/CSV data and generate audited KPI reports.")
    parser.add_argument("--sales", type=Path, default=root / "inputs" / "sales.csv")
    parser.add_argument("--customers", type=Path, default=root / "inputs" / "customers.xlsx")
    parser.add_argument("--output", type=Path, default=root / "outputs")
    args = parser.parse_args()
    try:
        report = run_pipeline(args.sales, args.customers, args.output)
    except (DataQualityError, FileNotFoundError) as exc:
        parser.exit(2, f"Data error: {exc}\n")
    print(f"Input: {report['source_rows']} | Valid: {report['valid_rows']} | Excluded: {report['excluded_rows']}")
    print(f"Recognized revenue: ${report['recognized_revenue_usd']} USD")
    print(f"Quality reconciliation: {'PASS' if report['reconciliation_passed'] else 'FAIL'}")
    print(f"Open report: {args.output / 'dashboard.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
