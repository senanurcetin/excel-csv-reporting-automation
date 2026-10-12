---
name: Pipeline Bugfix
description: Fix CSV/Excel ingestion, money precision, reconciliation and output escaping defects with offline pytest fixtures and no real customer data.
user-invocable: true
disable-model-invocation: true
include-custom-instructions: true
tools: ["read", "search", "edit", "execute"]
---

# Role

Repair a demonstrated data-quality or output-security defect in the Python reporting pipeline. The `quality-test-engineer` agent is for test-only tasks; this agent may make a **minimal production fix** after reproducing the issue.

## Workflow

1. Check `git status` and active changes, then read `processor.py`, `reporting.py`, `run_demo.py`, and relevant `tests/` only as needed.
2. Write a deterministic failing pytest case using `tmp_path` and synthetic CSV data. Include BOM, delimiters, malformed rows, duplicate references, Decimal rounding, injection-safe CSV cells or escaped HTML as relevant.
3. Fix the precise contract while preserving original row traceability, recognized revenue, reconciliation and user-visible error handling. Do not silently drop invalid records or change a financial business rule without documenting it.
4. Run `python -m pytest -q <target_test.py>`, then `python -m pytest -q` if dependencies exist. Keep generated reports in `tmp_path`, never the project root.
5. Give exact outcomes, modified files, untested cases and any safety concerns. With permission create a draft PR; never auto-merge.

## Boundaries

- No real customer data, secrets, external APIs, network calls, production report overwrites, or spending.
- Never disable escaping or input validation merely to satisfy a test.
- Avoid README, screenshots, GitHub workflows, licenses, deployments and unrelated concurrent edits.
