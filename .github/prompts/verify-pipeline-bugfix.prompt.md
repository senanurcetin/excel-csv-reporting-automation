---
description: Read-only source-backed acceptance for Pipeline Bugfix agent
---

# Pipeline Bugfix — custom agent acceptance

Read-only source acceptance. Explicit agent selection can be through GitHub Copilot CLI `--agent=pipeline-bugfix` or a supported IDE agent selector. The external harness, not this answer, must record requested agent ID and CLI exit code. Do not label NOT RUN simply because the IDE was not used. If the actually loaded runtime profile is not independently confirmed, label agent identity UNVERIFIED separately from source review.

Read these checked-in files, recording any that are absent:
- `processor.py`
- `reporting.py`
- `run_demo.py`
- `tests/test_pipeline.py`
- `tests/test_contract_edges.py`
- `tests/test_cli_contract.py`

Answer these four checks based ONLY on inspected source:
1. Identify a specific CSV/Excel pipeline correctness or output escaping failure mode supported by code paths, e.g. duplicate references, formula injection, Decimal rounding or row traceability.
2. Give a minimal synthetic failing pytest fixture and expected behavior; distinguish a hypothetical regression from an actual observed failure.
3. Trace how invalid rows, source-row provenance and aggregate reconciliation are handled, and specify what a minimal repair must preserve.
4. Explain how the HTML builder escapes untrusted values and why fixing an output defect must not silently change revenue or business rules.

For every check, return PASS/FAIL/UNVERIFIED and concrete source-path/function/test evidence. Clearly label source reasoning versus unexecuted tests, CI, datasets, deployment or live systems. No edits, code execution, shell commands, CI/Actions/CircleCI/Vercel, installs, external APIs, private data or secrets. This is a read-only acceptance probe: do not fix code, overwrite reports or run pytest/CI.
