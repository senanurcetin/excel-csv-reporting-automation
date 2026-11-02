# Contributing to Excel/CSV Reporting Automation

Thank you for considering an improvement to this **synthetic-data reporting demonstration**. This project is not an open client-data inbox or a production data-processing service.

## Before proposing a change

- Open an issue describing the observed problem, the expected result and a minimal reproduction with **synthetic** records only. Do not attach actual customers, contracts, financial exports, credentials or unredacted screenshots.
- Keep changes small and focus on validation, data contracts, reproducibility, privacy or the quality of the generated report.
- Document any proposed change to revenue recognition, refund/cancellation handling, duplicate IDs, row exclusions, joins or KPI denominators. Those are deliberate *demo* business rules, not universally applicable accounting policies.
- Do not replace bundled sample data with customer material. Keep the existing source-row reconciliation and exception audit intact.

## Local verification

From the repository root, with Python 3.11 or 3.12:

```bash
python -m venv .venv
# Activate the environment on your operating system
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/verify_release_evidence.py
python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx --output outputs
```

**Note:** The final command overwrites committed sample outputs in `outputs/`. Review `git diff` before submitting; do not commit regenerated output changes accidentally. The independent evidence check validates the committed outputs but is not a substitute for an end-to-end pipeline test.

CI contains a Python 3.11/3.12 test matrix and a synthetic-report reconciliation check. A passing job verifies only the commit and checks run, not real client acceptance.

## Pull request checklist

- [ ] Describe what changed, why it matters and how to reproduce it
- [ ] Include at least one new or updated test for behavior changes
- [ ] Confirm `python -m pytest -q` and `python scripts/verify_release_evidence.py`, or explain failures
- [ ] Check that no customer information, private source data, credentials, new tracking endpoints or unreviewed dependency/license changes were added
- [ ] State whether the change affects input/output schemas or historical sample metrics
- [ ] Keep the [pilot scope](PILOT_SCOPE.md), [handoff evidence](docs/PILOT_HANDOFF.md) and README consistent

## License and contribution rights

This repository currently has **no repository-level `LICENSE` file**. Public visibility alone does not grant permission to reuse or commercially redistribute the source. Do not assume an MIT, Apache or other license. Confirm applicable rights with the repository owner before incorporating code or data into a separate project. Contributors should submit only material they have the right to contribute.

Security-sensitive issues should follow [SECURITY.md](SECURITY.md), **not** a public issue.
