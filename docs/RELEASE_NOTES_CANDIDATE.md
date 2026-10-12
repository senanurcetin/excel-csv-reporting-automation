# Initial demonstration release — candidate notes

**Status:** Candidate only. No GitHub tag or Release has been created by this document. The proposed first stable version (`v1.0.0`) should be published only after reviewing the exact release commit, dependency installation, demo outputs, tests and repository permissions.

## Intended scope

- Python CSV and Excel reconciliation workflow with a standalone HTML KPI report.
- Explicit treatment of duplicate order IDs, missing customer references, invalid order fields and quarantined records.
- Reproducible sample outputs and machine-readable `validation_summary.json`.
- CLI entry point `python run_demo.py` and accompanying pytest checks.

## Reproducibility reference

The committed synthetic sample contains 200 source rows, 192 valid rows and 8 exclusions, with USD 56,975.50 recognized revenue under a **demo-specific** revenue definition. Source data and entities are fictional; this is not a statement of customer revenue.

## Known limitations

- No production API integration, authentication, managed deployment or client-data hosting.
- The policy that only paid/completed orders count as recognized revenue is a demonstrative rule, **not a universal accounting standard**.
- Real projects require a contract, data-processing authorization, a reviewed schema and independent acceptance testing.
- The hosted dashboard represents a static/synthetic sample and does not process uploaded private files.

## Checklist before creating a tag

- [ ] Confirm the selected target commit and verify the README accurately describes it.
- [ ] Run `python run_demo.py` on the committed synthetic sample.
- [ ] Run `python -m pytest -q` and review the results.
- [ ] Reconcile input/valid/excluded counts, revenue and category/segment/month totals.
- [ ] Inspect the dependency and licensing policy; decide explicitly whether to publish a software license.
- [ ] After validation, create the reviewed GitHub Release using these notes; do not represent this candidate as already published.

Related: [handoff and acceptance evidence](PILOT_HANDOFF.md) and [pilot scope](../PILOT_SCOPE.md).
