# Agent Instructions

## Before changing code

Always inspect the relevant existing files first.

Do not assume the input data schema.

Do not create mock data unless explicitly requested.

Do not modify raw data files.

Do not rewrite working modules unnecessarily.

## For analytical work

Prefer reproducible Python scripts/modules.

Save important outputs under `results/`.

Record assumptions and limitations.

Do not fabricate metrics.

## For new dependencies

Before adding a dependency:

1. Check whether an existing dependency can solve the problem.
2. Explain why the new dependency is needed.
3. Add it to requirements.txt only if justified.

## For LLM features

Keep LLM calls isolated from deterministic analytics.

Never send the full dataset to the LLM unnecessarily.

Prefer structured tool calls and compact evidence.

## Completion requirements

After implementing a feature:

- run relevant tests
- run the module on a small sample
- report files changed
- report commands executed
- report remaining issues
