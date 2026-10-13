---
description: Read-only source-backed acceptance for Quality Test Engineer agent
---

# Quality Test Engineer — custom agent acceptance

Read-only source acceptance. Explicit agent selection can be through GitHub Copilot CLI `--agent=quality-test-engineer` or a supported IDE agent selector. The external harness, not this answer, must record requested agent ID and CLI exit code. Do not label NOT RUN simply because the IDE was not used. If the actually loaded runtime profile is not independently confirmed, label agent identity UNVERIFIED separately from source review.

Read these checked-in files, recording any that are absent:
- `README.md`
- `processor.py`
- `reporting.py`
- `run_demo.py`
- `tests/test_pipeline.py`
- `tests/test_contract_edges.py`
- `tests/test_cli_contract.py`

Answer these four checks based ONLY on inspected source:
1. Trace CSV/XLSX header, encoding/BOM, duplicate customer and malformed-row handling; give a concrete synthetic boundary that existing tests cover or miss.
2. Inspect money/quantity parsing, Decimal precision and reconciliation; distinguish a documented invariant from a mere aggregate output.
3. Explain CSV spreadsheet-formula safety and HTML escaping of customer-controlled text, citing actual writer/report code and tests.
4. Describe CLI missing-file/error exit behavior and a deterministic tmp_path regression, without executing the CLI.

For every check, return PASS/FAIL/UNVERIFIED and concrete source-path/function/test evidence. Clearly label source reasoning versus unexecuted tests, CI, datasets, deployment or live systems. No edits, code execution, shell commands, CI/Actions/CircleCI/Vercel, installs, external APIs, private data or secrets. No real customer records, external services, output overwrites, or workflow reruns.
