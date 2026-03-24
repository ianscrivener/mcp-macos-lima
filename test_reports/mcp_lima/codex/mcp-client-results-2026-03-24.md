# MCP Client Test Report — Codex — 2026-03-24

## Client metadata
- Client: Codex (GPT-5-based coding agent)
- Host OS: macOS (Darwin 25.3.0, arm64)
- MCP tooling: invoking `uv run mcp-lima`
- Report timestamp: 2026-03-24T09:53:34Z (UTC)

## MCP connection metadata
- Command: `uv run mcp-lima`
- Working directory: `/Users/ianscrivener/bin/mcp-servers/mcp-macos-lima`
- Server state prior to tests: `default` Lima instance already present and running; it was not stopped, deleted, or modified
- Environment: `uv 0.8.3`; dev dependencies installed with `uv sync --extra dev`
- Disposable test instance: `mcp-delete-test-codex-20260324-095334`

## A-J test matrix
Step | Description | Status | Evidence
---|---|---|---
A | Tool discovery | Pass | Client exposed `lima_healthcheck`, `lima_create`, `lima_start`, `lima_stop`, `lima_restart`, `lima_delete`, `lima_list`, `lima_edit`, `lima_info`, `lima_shell`, `lima_copy`
B | Health check (`lima_healthcheck`) | Fail | Functional response was `{"status":"ok","server":"mcp-lima"}`, but it did not match the documented standard response envelope (`error`, `command`, `exit_code`, `stdout`, `stderr`, `data`)
C | Start and list | Pass | Created disposable instance, started it successfully, and `lima_list` returned parseable JSON including `status:"Running"` and `cpus:2` for `mcp-delete-test-codex-20260324-095334`
D | Info | Pass | `lima_info(json_output=true)` returned exit code `0` and parsed JSON with Lima version `2.1.0`, templates, host metadata, and plugin data
E | Shell command | Pass | `lima_shell(instance=..., command="printf 'codex-shell-ok\\n'; uname -srm")` returned exit code `0` and stdout `codex-shell-ok` plus `Linux 6.17.0-14-generic aarch64`
F | Copy | Pass | Copied `/tmp/mcp-lima-codex-copy.txt` to `mcp-delete-test-codex-20260324-095334:/tmp/mcp-lima-codex-copy.txt`; verified in-guest content with `cat` returning `codex-copy-check`
G | Stop | Pass | `lima_stop(instance=...)` returned exit code `0` and Lima reported the disposable instance had shut down
H | Delete preview + confirm | Fail | Preview behavior was correct, but `lima_delete(confirm=false)` returned `{"error":false,"preview":true,"action":"delete","instance":"...","message":"Set confirm=true to execute deletion."}` which also violates the documented standard response envelope; `confirm=true` then deleted the disposable instance successfully with exit code `0`
I | Invalid input/error contract | Pass | `lima_copy(sources=[])` returned `{"error":true,"exit_code":2,"stderr":"At least one source is required.","command":["limactl","copy"]}` and `lima_edit(instance="default")` returned `{"error":true,"exit_code":2,"stderr":"No patch fields supplied. Provide one or more editable fields.","command":["limactl","edit","default"]}`
J | Timeout handling | Pass | `lima_shell(instance="default", command="sleep 2", timeout_seconds=1)` returned `{"error":true,"exit_code":124,"stderr":"Command timed out after 1 seconds",...}`

Additional live-tool coverage:
- `lima_restart(instance="mcp-delete-test-codex-20260324-095334")` succeeded end-to-end.
- `lima_edit(instance="mcp-delete-test-codex-20260324-095334", cpus=2)` succeeded before boot and the updated CPU count appeared in `lima_list`.
- `lima_edit(instance="mcp-delete-test-codex-20260324-095334", memory="2GiB")` failed with Lima CLI error `invalid argument "2GiB" for "--memory" flag`, which suggests a mismatch between tool typing/tests and current Lima CLI expectations.

Local automated test coverage:
- Ran `uv sync --extra dev` successfully to install test dependencies.
- Ran `uv run pytest`: `60 passed, 3 failed`
- Failing tests:
  - `tests/integration/test_smoke_integration.py::test_lima_list_tool_real`
  - `tests/integration/test_smoke_integration.py::test_lima_shell_uname`
  - `tests/integration/test_smoke_integration.py::test_lima_shell_error_exit_code`
- Failure mode: all three integration tests access `mcp._tool_manager._tools`, but the current `FastMCP` object in this environment has no `_tool_manager` attribute, raising `AttributeError`.

## Failure details
- `lima_healthcheck` does not follow the documented response contract. It returns a custom success object instead of the standard envelope.
- `lima_delete(confirm=false)` does not follow the documented response contract. Preview mode omits `command`, `exit_code`, `stdout`, `stderr`, and `data`.
- The `lima_edit` memory path appears incompatible with the current Lima CLI when given values like `"2GiB"`, despite unit tests covering a string memory parameter.
- The local integration suite is not green because three tests depend on a FastMCP private attribute that is no longer available.

## Final verdict
Ready with caveats

Live MCP validation against a real Lima environment was broadly successful, including create, edit, start, list, info, shell, copy, restart, stop, delete, invalid-input handling, timeout handling, and cleanup. The server is not fully ready for an unconditional `Ready` verdict because two user-visible tools violate the documented response contract and the local integration test suite currently fails in three places.
