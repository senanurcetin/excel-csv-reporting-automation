# Reviewer brief — Auditable CSV/Excel KPI Reporting Pilot

**Audience:** BI agencies, analytics consultants and operations teams considering a tightly scoped reporting automation. **Example data:** entirely synthetic, including deliberate defects.

## The work package

Ingest an order-export CSV and a customer-reference Excel workbook, validate records, reconcile recognized revenue and produce a repeatable KPI pack with a traceable exception log.

| Evaluation question | Source |
|---|---|
| What are the agreed input schemas? | [CSV and workbook contract](../README.md#input-contract) and [synthetic inputs](../inputs/) |
| Which records count as revenue? | [Documented status and duplicate rules](../README.md#explicit-testable-business-rules) |
| Can a client trace exclusions? | [Quality issue register](../outputs/quality_issues.csv) and [validation summary](../outputs/validation_summary.json) |
| What exactly is delivered? | [Generated KPI outputs](../outputs/) and [standalone HTML report](../outputs/dashboard.html) |
| How is acceptance defined? | [Fixed-scope pilot brief](../PILOT_SCOPE.md) |
| Can it be validated offline? | `python run_demo.py` and `python -m pytest -q`; see [quick start](../README.md#quick-start) |

## Why this is useful

- Every excluded source row is assigned a reason rather than silently dropped.
- KPI outputs can be reconciled to the accepted source rows and reproduced with unchanged inputs.
- Local execution avoids the need to upload real client records to a public dashboard.

## Boundaries

The public hosted dashboard is a **static rendering of synthetic sample output**; it does not accept or process private uploads. Recognized-revenue rules are demo assumptions, not accounting advice. Actual scope, pricing, IP ownership and acceptance rules require agreement before client delivery.

**Commercial handoff:** [Pilot scope](../PILOT_SCOPE.md) · [Project README](../README.md).
