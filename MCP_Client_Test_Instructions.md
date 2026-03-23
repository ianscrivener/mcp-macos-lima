# MCP Client Test Instructions

## 1. Objective

This document defines a comprehensive, repeatable process for validating the mcp-lima server across multiple AI clients on macOS.

Target clients:
- Claude Code
- GitHub Copilot Chat
- Codex
- Gemini

Primary goals:
- Verify consistent tool discovery and invocation across clients
- Verify behavior and response contracts for success paths and failure paths
- Verify safety behavior for destructive operations (preview then confirm)
- Produce comparable evidence and pass/fail results across all clients

## 2. Scope

In scope:
- mcp-lima Phase 1 tools:
  - lima_create
  - lima_start
  - lima_stop
  - lima_restart
  - lima_delete
  - lima_list
  - lima_edit
  - lima_info
  - lima_shell
  - lima_copy

Out of scope:
- Performance benchmarking under heavy concurrency
- Non-macOS host validation
- Phase 2 and Phase 3 tool surfaces

## 3. Test Environment Requirements

Host requirements:
- macOS
- limactl installed and available on PATH
- Existing Lima default instance available (or ability to create one)

Repository and Python requirements:
- Open this repository in each client
- Project path:
  - /Users/ianscrivener/zzCODE26zz/Skills_MCP/mcp/lima-macos-mcp
- Project virtual environment present at:
  - /Users/ianscrivener/zzCODE26zz/Skills_MCP/mcp/lima-macos-mcp/.venv

MCP runtime command (recommended):
- Working directory:
  - /Users/ianscrivener/zzCODE26zz/Skills_MCP/mcp/lima-macos-mcp
- Command:
  - uv run mcp-lima

## 4. Pre-Test Safety Rules

- Do not delete the default instance unless explicitly approved.
- Use disposable instances for destructive testing.
- Required disposable name format:
  - mcp-delete-test-<client>-<timestamp>
- Always execute delete in two steps:
  1. confirm false preview
  2. confirm true execution

## 5. Response Contract Expectations

Every tool response must be parseable JSON object.

Expected keys on standard responses:
- error
- command
- exit_code
- stdout
- stderr
- data (when available)

Expected delete preview response shape:
- error false
- preview true
- action delete
- instance <name>
- message includes confirm true guidance

## 6. Known Compatibility Notes

- limactl info on the current environment returns JSON by default.
- limactl info --json is not supported on current limactl version and should not be required.
- limactl list --json may emit multiple JSON objects; parser must handle multi-document output.

## 7. Standard Test Sequence (Run In Every Client)

Use the same sequence in each client with the same expected outcomes.

### Test A: Tool Discovery

Actions:
1. Request list of available tools from MCP server.

Expected:
- All 10 Phase 1 tools are visible.
- Tool names are correct.
- No unexpected duplicate names.

### Test B: Health Check

Actions:
1. Call lima_healthcheck.

Expected:
- error false
- status ok

### Test C: Start and List

Actions:
1. Call lima_start for default.
2. Call lima_list.

Expected:
- start returns error false, exit_code 0
- list returns error false
- list data includes default instance

### Test D: Info

Actions:
1. Call lima_info.

Expected:
- error false
- stdout or data contains valid info payload
- no dependency on info --json flag

### Test E: Shell Command

Actions:
1. Call lima_shell on default with command uname -a.

Expected:
- error false
- stdout contains Linux kernel line

### Test F: Copy

Actions:
1. Call lima_copy from default:/etc/hostname to /tmp/lima-hostname-test-<client>.txt.
2. Verify local file exists and has non-empty content.

Expected:
- copy returns error false, exit_code 0
- file exists
- first line is hostname-like text

### Test G: Stop

Actions:
1. Call lima_stop for default.
2. Call lima_list.

Expected:
- stop returns error false, exit_code 0
- default status is Stopped

### Test H: Delete Preview and Confirm (Disposable Instance)

Actions:
1. Create disposable instance name.
2. Call lima_create for disposable instance.
3. Call lima_delete with confirm false.
4. Verify disposable instance still exists.
5. Call lima_delete with confirm true.
6. Verify disposable instance no longer exists.

Expected:
- create success (or already exists if rerun)
- preview returns preview true and does not delete
- confirm delete executes and removes instance

### Test I: Invalid Input and Error Contract

Actions:
1. Call lima_shell with nonexistent instance name.
2. Call lima_copy with empty sources list.
3. Call lima_edit with no patch fields.

Expected:
- each returns parseable JSON object
- each has error true
- each includes command and exit_code where applicable
- each includes useful stderr message

### Test J: Timeout Handling

Actions:
1. Call a long-running operation with intentionally low timeout_seconds (for example start with timeout 1).

Expected:
- returns error true
- exit_code 124
- stderr indicates timeout

## 8. Per-Client Execution Notes

### Claude Code

- Open repo and ensure MCP server is configured in Claude Code.
- Ask Claude Code to run the Standard Test Sequence A through J exactly.
- Instruct it to create a report file at:
  - reports/mcp-client-results-claude-code.md

### GitHub Copilot Chat

- Open same repo in VS Code with MCP connection configured.
- Ask Copilot to run Standard Test Sequence A through J exactly.
- Instruct it to create report file at:
  - reports/mcp-client-results-copilot.md

### Codex

- Open this repository in Codex.
- Configure Codex MCP client to run the server command.
- Ask Codex to run Standard Test Sequence A through J exactly.
- Instruct it to create report file at:
  - reports/mcp-client-results-codex.md

### Gemini

- Configure Gemini environment to connect to same MCP server command and working directory.
- Ask Gemini to run Standard Test Sequence A through J exactly.
- Instruct it to create report file at:
  - reports/mcp-client-results-gemini.md

## 9. Required Report Format (All Clients)

Each client must generate a report with these sections:

1. Client Metadata
- client name
- client version
- date/time
- host OS
- limactl version
- server working directory

2. MCP Connection Metadata
- command used
- startup success
- tool discovery count

3. Test Matrix Table
Columns:
- Test ID
- Test Name
- Pass or Fail
- Evidence
- Notes

4. Failure Details
For each failure:
- exact prompt used
- tool args used
- raw response snippet
- classification (client issue, server issue, environment issue)

5. Final Verdict
- Ready
- Ready with caveats
- Not ready

## 10. Pass Criteria

Client-level pass:
- All mandatory tests A through H pass
- Error contract tests in I pass with parseable JSON
- Timeout test J returns normalized timeout response

Cross-client pass:
- 3 out of 4 clients pass with no server-side behavior mismatch
- No destructive safety regression
- No non-parseable JSON responses

## 11. Failure Triage Rules

If only one client fails and others pass:
- classify as probable client integration/config issue first

If all clients fail same test:
- classify as probable server or environment issue

If failures are non-deterministic across reruns:
- classify as flaky; rerun failed test 3 times and record variance

## 12. Quick Prompt Template To Use In Each Client

Copy and run this prompt in each client:

Perform the full MCP validation sequence against mcp-lima using the test protocol in MCP_Client_Test_Instructions.md sections 7 through 11. Execute tests A through J exactly. Use a disposable instance name for destructive tests and do not delete default. Capture raw response snippets for each test. Produce a report at reports/mcp-client-results-<client>.md using the required report format in section 9. At the end, provide a final readiness verdict and list server-side issues separately from client-side issues.

## 13. Post-Test Cleanup

After each client run:
- Ensure default instance is Stopped unless intentionally left Running.
- Ensure disposable test instances are deleted.
- Keep generated report file.

After all clients run:
- Compare all report files side by side.
- Open issues only for server-side mismatches and reproducible failures.

## 14. Current Baseline Status (Reference)

Already validated in this repository before cross-client execution:
- Core happy-path commands are working with real limactl
- Delete preview and confirm flow verified on disposable instance
- Multi-document JSON parsing fix implemented for list output
- Unit tests passing

Use this as baseline context, but do not skip any client test steps.
