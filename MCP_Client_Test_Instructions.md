# MCP Client Test Instructions (mcp-macos-lima)

## Objective
Validate `mcp-macos-lima` consistently across Claude Code, GitHub Copilot Chat, Codex, and Gemini.

## Repository Context

- Repository root: `mcp-macos-lima`
- MCP command: `uv run mcp-lima`
- Reports root: `test_reports/mcp_lima/`

## Python Environment Prerequisites

- UV must be installed before running setup or MCP server commands.

Install/check UV:

```bash
brew install uv
uv --version
```

## Setup

```bash
git clone git@github.com:ianscrivener/mcp-macos-lima.git
cd mcp-macos-lima
uv venv
source .venv/bin/activate
uv sync --extra dev
```

`uv sync --extra dev` is mandatory so all required runtime and test modules are installed.

## MCP Client Connection

If the MCP server is not already configured in your client, add it with:

- command: `uv`
- args: `run mcp-lima`
- working directory: repository root (`mcp-macos-lima`)

## Test Scope

Phase 1 tools:

- `lima_healthcheck`

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

## Standard Sequence (A-J)

1. Tool discovery
2. Health check (`lima_healthcheck`)
3. Start and list
4. Info
5. Shell command
6. Copy
7. Stop
8. Delete preview + confirm (disposable instance only)
9. Invalid input/error contract
10. Timeout handling

During step 2 and step 8, explicitly verify response-envelope compliance.

## Safety Rules

- Do not delete `default` unless explicitly approved.
- Use disposable names: `mcp-delete-test-<client>-<timestamp>`.
- Delete requires preview first (`confirm=false`), then execute (`confirm=true`).

## Response Contract

All tool responses must be parseable JSON and must include standard fields:

- `error`
- `command`
- `exit_code`
- `stdout`
- `stderr`
- `data` (when present)

Contract checks are mandatory for:

- `lima_healthcheck`
- `lima_delete(confirm=false)` preview response

Both must include the standard fields listed above.

## Local Test Commands

Run tests after MCP validation and before finalizing reports:

```bash
uv run python -m pytest -m "not integration"
uv run python -m pytest
```

Use `python -m pytest` to avoid PATH/script resolution issues in mixed shell environments.

## Additional Validation Checks

- Verify `lima_edit(instance="default", memory="2GiB")` does not fail due to raw unit suffix handling.
- Record the observed command/result in the report if memory normalization behavior changes.

## Per-Client Report Paths

- `test_reports/mcp_lima/claude_code/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/copilot/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/codex/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/gemini/mcp-client-results-<date>.md`

Create the directory when needed, then write the report file under the matching client path.

## Required Report Sections

1. Client metadata
2. MCP connection metadata
3. A-J test matrix (pass/fail + evidence)
4. Failure details
5. Final verdict (`Ready`, `Ready with caveats`, `Not ready`)

## GitHub Workflow

```bash
git checkout main
git pull origin main
# run tests and update reports
git add -A
git commit -m "Update lima test reports"
git push origin main
```
