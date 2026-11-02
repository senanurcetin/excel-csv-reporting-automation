# Security and data-handling policy

**Project scope:** synthetic CSV/XLSX ingestion, reconciliation and offline report generation. The hosted page shows synthetic sample KPIs; **it is not a secure customer file-upload service** and is not offered as a managed production processor.

## Reporting a suspected vulnerability

Do not post exploits, credentials, private financial data, screenshots of customer records or vulnerable deployment details in a public issue. Use the repository owner's public professional contact **senanur.cetin.work@gmail.com** with a concise summary, affected component, minimal **synthetic** reproduction and expected/observed impact. Ask for a secure disclosure channel before sending confidential material. No guaranteed response time or formal bug-bounty program is offered.

For ordinary non-sensitive defects, use a GitHub issue or PR with synthetic fixtures.

## Threat model and operational boundaries

Potential risks include:

- **Untrusted CSV/XLSX content:** malformed or oversized input, formula-like cells, delimiter/newline/encoding tricks, and spreadsheet formula execution when opening exported files in spreadsheet software. The demo's existing validation **does not establish** exhaustive protection against these cases.
- **Confidentiality:** joined output includes customer names and commercial amounts when run on real files. Neither the bundled sample nor GitHub issues, build logs or publicly hosted dashboards may be used as a sink for real client data.
- **File access and retention:** command-line input/output paths are chosen by the operator. Run in an isolated, access-controlled local directory, outside a public Git checkout, and define retention/deletion before any real engagement.
- **Dependency and supply-chain exposure:** dependencies from `requirements.txt` are installed into the operator's Python environment; use a disposable environment and review updates. A successful CI run is not a security audit.
- **Accounting/KPI semantics:** recognizing only `paid` and `completed` statuses is a *sample policy*. Results must not be used for financial statements without approved accounting definitions and independent reconciliation.

## Safe demonstration

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/verify_release_evidence.py
python run_demo.py --sales inputs/sales.csv --customers inputs/customers.xlsx --output outputs
```

All bundled input records are fictional. The last command writes to `outputs/` and may replace existing sample reports. Review `PILOT_SCOPE.md` and `docs/PILOT_HANDOFF.md` for input/output contracts.

**Before any real client pilot:** establish lawful access, minimum necessary fields, confidentiality and data-processing terms, named reviewer, storage encryption/access controls, retention/deletion plan, acceptance checks, incident contacts and a tested clean-up process. Those controls are **not implemented by this repository** and require separate implementation and verification.
