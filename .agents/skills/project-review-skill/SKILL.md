---
name: project-review-skill
description: Use this skill for read-only review of project quality, architecture consistency, reproducibility, security, tests, and documentation.
---

Purpose:
Help Codex review the project without changing files.

Review priorities:
1. Correctness
2. Reproducibility
3. Security
4. No secrets
5. No ML data leakage
6. Test coverage
7. Documentation consistency
8. Readability

Check:
- whether code matches AGENTS.md;
- whether code matches docs/01_iot_plan.md;
- whether telemetry matches docs/02_data_contract.md;
- whether ML matches docs/03_ml_plan.md;
- whether acceptance criteria are satisfied;
- whether .env is ignored;
- whether commands in README work;
- whether generated artifacts are reproducible.

Return format:
- critical issues;
- medium issues;
- minor issues;
- recommended next actions.

Do not edit files unless explicitly asked.