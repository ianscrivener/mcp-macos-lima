# mcp-lima

FastMCP server for core Lima operations on macOS.

## Scope

Phase 1 tools:

- `lima_create`
- `lima_start`
- `lima_stop`
- `lima_restart`
- `lima_delete`
- `lima_list`
- `lima_edit`
- `lima_info`
- `lima_shell`
- `lima_copy`

## Prerequisites

- macOS host
- `limactl` installed and available on `PATH`
- Python 3.11+
- UV package manager

## Setup

```bash
cd mcp/lima-macos-mcp
uv venv
source .venv/bin/activate
uv sync --extra dev
```

## Run

```bash
source .venv/bin/activate
uv run mcp-lima
```

FastMCP defaults to stdio transport, which is suitable for MCP clients like Claude Desktop and Claude Code.

## Tests

```bash
source .venv/bin/activate
uv run pytest -m "not integration" --cov=. --cov-report=term-missing
uv run pytest --cov=. --cov-report=term-missing
```

## Notes

- Tool responses are always parseable JSON objects.
- Non-zero CLI exits are normalized into `{ "error": true, ... }` responses.
- `lima_delete` supports preview-first behavior when `confirm` is false.
# mcp-macos-lima
