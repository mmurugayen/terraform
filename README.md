# terraform

Source reviewed for this merge: [`bcd6cf08da5ab`](https://github.com/mmurugayen/terraform/commit/bcd6cf08da5abe84a3e48f9c276d4bb212b15de9) on `main`.

This repository contains shared correlated diagnostics and a Python MCP stdio adapter. It does not contain a deployable application or a Terraform infrastructure module.

## Correlated diagnostics and MCP investigation

[Feature GYS-OBS-001](docs/product/backlog/GYS-OBS-001.md) adds structured diagnostics,
[MCP investigation and verified recovery learning](docs/OBSERVABILITY_MCP.md).
The source inventory and CI contracts track new implementation boundaries.

## Contents and setup

- `scripts/`: the diagnostics contract, logging helpers, MCP adapter and source inventory check.
- `config/`: example log-source settings, source boundaries and shared-file provenance.
- `tests/`: MCP transport, privacy and operation-tracing contracts.
- `docs/`: integration instructions, source coverage and dated validation evidence.

Use Python 3.11 or newer. The diagnostics adapter has no third-party Python dependencies.

```bash
git clone --branch main https://github.com/mmurugayen/terraform.git
cd terraform
python3 scripts/check_observability_coverage.py
python3 -m unittest discover -s tests -p 'test_observability_mcp.py' -v
python3 -m unittest discover -s tests -p 'test_operation_tracing.py' -v
```

The Observability contracts workflow runs these checks on a self-hosted Linux x64 runner. Follow the [MCP guide](docs/OBSERVABILITY_MCP.md) to configure protected log files and start the adapter. Backend recovery requires separate configuration and the existing approval process.

## Documentation history

The [documentation audit](docs/current/DOCUMENTATION_AUDIT.md) retains the earlier placeholder-source review. Its inventory and validation counts refer to that dated snapshot. This merge updates the README for the diagnostics source now present; see the [merge validation](docs/current/VALIDATION.md#merge-validation).

No application deployment or live provider qualification is asserted by this documentation change.
