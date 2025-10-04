Monolith Refactor (experimental)
================================

This folder contains an experimental proof-of-concept that combines several
analysis steps into a single, monolith-like CLI for rapid prototyping.

Key points
- Lives on branch `monolith-experiment` only. No production changes are made.
- Intentionally minimal and uses `--dry-run` widely so it can be executed
  without installing heavy dependencies.
- If you want to try it locally, create a virtualenv and run `pytest` in the
  folder to exercise the smoke test.

Files
- `analysis_monolith.py` - small CLI with subcommands `score`, `compare`, `model`.
- `tests/test_smoke.py` - pytest smoke test that runs `analysis_monolith.py --dry-run`.

Notes
- Per repository policy, the canonical `install.sh` remains authoritative for
  installing dependencies for the main project. This experiment is intentionally
  isolated and optional.
