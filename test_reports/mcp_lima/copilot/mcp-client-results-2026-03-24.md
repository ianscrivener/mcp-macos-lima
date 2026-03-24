# MCP Client Test Report — Copilot — 2026-03-24

## Client metadata
- Client: GitHub Copilot Chat (GPT-5.3-Codex)
- Host OS: macOS (Darwin 25.3.0, arm64)
- MCP tooling: invoking `uv run mcp-lima`
- Report timestamp: 2026-03-24T10:37:24.781511+00:00 (UTC)

## MCP connection metadata
- Command: `uv run mcp-lima`
- Working directory: `/Users/ianscrivener/zzCODE26zz/Skills_MCP/mcp-macos-lima`
- Environment: `uv 0.8.3`; `limactl version 2.1.0`
- Disposable test instance: `mcp-delete-test-copilot-20260324-103724`

## A-J test matrix
Step | Description | Status | Evidence
---|---|---|---
A | Tool discovery | Pass | Exposed tools: `lima_healthcheck`, `lima_create`, `lima_start`, `lima_stop`, `lima_restart`, `lima_delete`, `lima_list`, `lima_edit`, `lima_info`, `lima_shell`, `lima_copy`
B | Health check (`lima_healthcheck`) | Pass with caveat | Functional response: `{"status":"ok","server":"mcp-lima"}`
C | Start and list | Pass | Created disposable instance, started successfully, `lima_list` returned parseable JSON and showed test instance `status:"Running"`
D | Info | Pass | `lima_info(json_output=true)` returned `exit_code: 0` and parsed JSON
E | Shell command | Pass | `lima_shell(instance=..., command="printf 'copilot-shell-ok\\n'; uname -srm")` returned `exit_code: 0` and expected stdout
F | Copy | Pass | Copied `/tmp/mcp-lima-copilot-copy-*.txt` to guest and verified content `copilot-copy-check`
G | Stop | Pass | `lima_stop(instance=...)` returned `exit_code: 0`
H | Delete preview + confirm | Pass with caveat | `confirm=false` returned preview object; `confirm=true` deleted test instance with `exit_code: 0`
I | Invalid input/error contract | Pass | `lima_copy(sources=[])` and `lima_edit(instance="default")` returned structured error objects
J | Timeout handling | Pass | `lima_shell(instance="default", command="sleep 2", timeout_seconds=1)` returned `error:true`, `exit_code:124`

## Additional live-tool coverage
- `lima_restart(instance="default")` succeeded end-to-end.
- `lima_edit(instance="default", memory="2GiB")` failed with Lima CLI error: `invalid argument "2GiB" for "--memory" flag`.

## Contract checks
- `lima_healthcheck` standard envelope present (`error`, `command`, `exit_code`, `stdout`, `stderr`, `data`): **No**
- `lima_delete(confirm=false)` preview standard envelope present: **No**

## Local automated test coverage (current workspace state)
- `uv run pytest` in `mcp-macos-lima`: **63 passed, 0 failed**
- Previously failing FastMCP-internal integration tests are now fixed by using public `call_tool` invocation.

## Failure details
- No operational failures in A-J flow.
- Two response-contract caveats remain:
  - `lima_healthcheck` returns custom success object instead of the standard envelope.
  - `lima_delete(confirm=false)` preview response omits standard envelope fields.
- `lima_edit` memory format compatibility caveat remains for values like `"2GiB"` against current Lima CLI.

## Final verdict
Ready with caveats

Server behavior is operationally robust across the full A-J flow and local test suite is green. Remaining gaps are response-envelope consistency for two user-visible responses and memory-argument compatibility with current `limactl edit` expectations.
