# Current documentation: terraform

Last source review: **2026-09-14**, default branch `main`, commit [`d5649a5a040c`](https://github.com/mmurugayen/terraform/commit/d5649a5a040cbad149a2940f84766c46f6b05f04). This records a documentation review of the linked source snapshot.

Reviewed 2026-09-14 against `12f71db2e5d1dd164a98b8c8a6a724f9d6642d7e`. The source contains a diagnostic utility; no domain product or Terraform resources are declared.

- [Architecture](ARCHITECTURE.md)
- [Workflow](WORKFLOWS.md)
- [Audit and complete inventory](DOCUMENTATION_AUDIT.md)
- [Validation](VALIDATION.md)
- [Repository README](../../README.md)


[Integration review and latest validation](MERGE_REVIEW.md).

## Maintaining the diagrams

Edit [diagrams.json](diagrams/diagrams.json), then run `python3 docs/current/diagrams/render.py`. Commit sources and generated SVGs together.

Check reproducibility with `python3 docs/current/diagrams/render.py --check`. Architecture `units` contain components; workflow `nodes` describe actions and alternatives. Refresh the source commit after comparing implementation changes.
