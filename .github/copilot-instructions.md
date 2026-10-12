# GitHub Copilot repository instructions — Excel/CSV Reporting Automation

## Scope
This Python project reads synthetic sales and customer data, validates transactions, reconciles recognized revenue and writes CSV/HTML reports. Data validation and output escaping are correctness and security boundaries.

## Project map
- `processor.py`: import, validation, revenue recognition, duplicate handling, CSV safety and end-to-end pipeline.
- `reporting.py`: report generation, HTML escaping and presentation helpers.
- `run_demo.py`: CLI flags, error handling and demo pipeline.
- `tests/test_pipeline.py`: existing core pipeline coverage.
- `tests/test_contract_edges.py`: additional data quality and export regressions (if present on the active branch).
- `.github/agents/quality-test-engineer.agent.md`: manually selectable focused test specialist.

## Rules for changes
- Always inspect the module and existing tests first; use deterministic pytest fixtures, `tmp_path`, in-memory synthetic records and no customer data.
- Run `python -m pytest -q <target_test.py>` for focused checks and `python -m pytest -q` for the suite when available.
- Preserve Decimal/currency precision, ISO date checks, case-insensitive duplicate handling and reconciliation between raw, excluded and valid rows.
- Treat any CSV cell or HTML output derived from input as untrusted: guard formula injection and escape HTML.
- Keep output paths confined to explicit temporary locations during tests; no network, database, credentials or external services.
- Never interpret a passed synthetic fixture as validation of arbitrary real datasets. Report tests actually run and their results.
- Do not modify README, license, workflows, dataset files, developer-program content or deployment configuration unless explicitly part of the task. PRs should remain focused and be reviewed before merge.
