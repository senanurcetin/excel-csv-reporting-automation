"""CLI: python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from processor import DataQualityError, run_pipeline


def non_negative_integer(raw: str) -> int:
    try:
        number = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return number


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Clean synthetic Excel/CSV data and generate audited KPI reports.")
    parser.add_argument("--sales", type=Path, default=root / "inputs" / "sales.csv")
    parser.add_argument("--customers", type=Path, default=root / "inputs" / "customers.xlsx")
    parser.add_argument("--output", type=Path, default=root / "outputs")
    parser.add_argument(
        "--max-excluded-rows",
        type=non_negative_integer,
        default=None,
        metavar="N",
        help="Optional quality gate: exit 3 if excluded source rows exceed N; keep review outputs.",
    )
    args = parser.parse_args()
    try:
        report = run_pipeline(args.sales, args.customers, args.output)
    except (DataQualityError, FileNotFoundError) as exc:
        parser.exit(2, f"Data error: {exc}\n")
    print(f"Input: {report['source_rows']} | Valid: {report['valid_rows']} | Excluded: {report['excluded_rows']}")
    print(f"Recognized revenue: ${report['recognized_revenue_usd']} USD")
    print(f"Quality reconciliation: {'PASS' if report['reconciliation_passed'] else 'FAIL'}")
    print(f"Open report: {args.output / 'dashboard.html'}")
    if args.max_excluded_rows is not None:
        excluded = report["excluded_rows"]
        if excluded > args.max_excluded_rows:
            print(
                f"Quality gate: FAIL (excluded rows {excluded} exceed "
                f"--max-excluded-rows={args.max_excluded_rows}; review quality_issues.csv)",
                file=sys.stderr,
            )
            return 3
        print(
            f"Quality gate: PASS (excluded rows {excluded} <= "
            f"--max-excluded-rows={args.max_excluded_rows})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
