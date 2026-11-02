"""CLI: python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
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


def bounded_percentage(raw: str) -> Decimal:
    """Parse a finite percentage with decimal precision, rejecting NaN and infinity."""
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("must be between 0 and 100 percent") from exc
    if not value.is_finite() or value < 0 or value > 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100 percent")
    return value


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
    parser.add_argument(
        "--max-excluded-percent",
        type=bounded_percentage,
        default=None,
        metavar="PCT",
        help="Optional percentage gate from 0 to 100; all configured gates must pass.",
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
    if args.max_excluded_rows is not None or args.max_excluded_percent is not None:
        excluded = report["excluded_rows"]
        source = report["source_rows"]
        limits = []
        violations = []
        if args.max_excluded_rows is not None:
            desc = f"excluded rows {excluded} <= --max-excluded-rows={args.max_excluded_rows}"
            limits.append(desc)
            if excluded > args.max_excluded_rows:
                violations.append(
                    f"excluded rows {excluded} exceed --max-excluded-rows={args.max_excluded_rows}"
                )
        if args.max_excluded_percent is not None:
            # Exact Decimal arithmetic avoids floating-point boundary errors.
            # A header-only source has zero excluded rows and passes a 0% gate.
            actual = Decimal(excluded) * 100 / Decimal(source) if source else Decimal(0)
            limits.append(
                f"excluded rate {actual:.2f}% <= "
                f"--max-excluded-percent={args.max_excluded_percent}"
            )
            if Decimal(excluded) * 100 > args.max_excluded_percent * Decimal(source):
                violations.append(
                    f"excluded rate {actual:.2f}% exceeds "
                    f"--max-excluded-percent={args.max_excluded_percent}"
                )
        if violations:
            print(
                "Quality gate: FAIL (" + "; ".join(violations)
                + "; review quality_issues.csv)",
                file=sys.stderr,
            )
            return 3
        print("Quality gate: PASS (" + "; ".join(limits) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
