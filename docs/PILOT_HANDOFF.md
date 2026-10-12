# Reproducible pilot handoff and acceptance evidence

This is a **synthetic-data demonstration**, not a completed client engagement, signed acceptance, or production data-processing service.

## Reviewer path

1. Read [the fixed-scope pilot proposal](../PILOT_SCOPE.md) for commercial boundaries.
2. Review the [source data](../inputs/) and [sample outputs](../outputs/).
3. Run the pipeline and verify the output reconciliation using the commands below.
4. Inspect [business-rule tests](../tests/) and the [offline HTML dashboard](../outputs/dashboard.html).
5. Check every exclusion against [quality_issues.csv](../outputs/quality_issues.csv); do not silently repair or discard rows.

## Input contracts

| Input | Required columns | Required validation |
| --- | --- | --- |
| `inputs/sales.csv` | `order_id`, `order_date`, `customer_id`, `category`, `quantity`, `unit_price_usd`, `status` | ISO dates, positive integer quantity, non-negative USD price at most two decimals, allowed statuses `paid`, `completed`, `refunded`, `cancelled`; normalized IDs must be consistent |
| `inputs/customers.xlsx` (first worksheet) | `customer_id`, `customer_name`, `segment`, `region` | Nonempty unique normalized customer IDs; no ambiguous many-to-many join |

Conflicting duplicate order IDs are quarantined; exact repeated IDs retain the first occurrence. Customer IDs absent from the reference table are excluded. See [README](../README.md) for the full decision table.

## Output contracts

| Artifact | Review criterion |
| --- | --- |
| `cleaned_sales.csv` | Cleaned join and normalized transaction amounts; no silently duplicated order IDs |
| `quality_issues.csv` | Excluded source rows and issue codes, suitable for remediation review |
| `category_kpis.csv`, `monthly_kpis.csv`, `segment_kpis.csv` | Documented reporting grains and independently reconcilable totals |
| `validation_summary.json` | Source/valid/excluded counts, recognized revenue, refunds, cancellations, and reconciliation flag |
| `dashboard.html` | Offline report generated from the same reconciled output, not separately entered numbers |

The business rule recognizes only `paid` and `completed` order values as revenue. Refunds/cancellations appear separately and are not subtracted twice. This rule is a **scenario-specific reporting policy**, not an assertion of accounting compliance.

## Demonstration acceptance snapshot

The committed example `outputs/validation_summary.json` records:

- 200 input rows, 192 valid rows, 8 excluded rows; reconciliation passed.
- Recognized synthetic revenue: **USD 56,975.50**.
- 159 paid/completed orders, 18 refunded, 15 cancelled in the valid dataset.

These are reproducibility reference values for **these exact sample inputs**, not service-level guarantees or customer figures.

## Independent review

```bash
python -m pip install -r requirements.txt
python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx --output outputs
python -m pytest -q
```

Run from the repository root. Check that source, valid and excluded counts reconcile, inspect all exceptions, and confirm the KPI outputs before approving any use. Re-running overwrites the example outputs, so keep a copy if comparing generated artifacts.

## Real customer engagement gate

Before ingesting any client files, explicitly agree on purpose and lawful access; data minimization and retention; accepted source layouts and time zones; accounting/KPI policy; exception review ownership; acceptance tests; security controls; and delivery/usage rights. Use sanitized sample data during discovery. No private records, credentials or customer identifiers belong in a public issue, pull request or demo.
