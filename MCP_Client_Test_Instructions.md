# MCP Client Test Instructions (mcp-macos-lima)

## Objective
Validate `mcp-macos-lima` consistently across Claude Code, GitHub Copilot Chat, Codex, and Gemini.

## Repository Context

- Repository root: `mcp-macos-lima`
- MCP command: `uv run mcp-lima`
- Reports root: `test_reports/mcp_lima/`

## Setup

```bash
git clone git@github.com:ianscrivener/mcp-macos-lima.git
cd mcp-macos-lima
uv venv
source .venv/bin/activate
uv sync --extra dev
```

## Test Scope

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

## Standard Sequence (A-J)

1. Tool discovery
2. Health check
3. Start and list
4. Info
5. Shell command
6. Copy
7. Stop
8. Delete preview + confirm (disposable instance only)
9. Invalid input/error contract
10. Timeout handling

## Safety Rules

- Do not delete `default` unless explicitly approved.
- Use disposable names: `mcp-delete-test-<client>-<timestamp>`.
- Delete requires preview first (`confirm=false`), then execute (`confirm=true`).

## Response Contract

All tool responses must be parseable JSON and should include standard fields:

- `error`
- `command`
- `exit_code`
- `stdout`
- `stderr`
- `data` (when present)

## Per-Client Report Paths

- `test_reports/mcp_lima/claude_code/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/copilot/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/codex/mcp-client-results-<date>.md`
- `test_reports/mcp_lima/gemini/mcp-client-results-<date>.md`

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
