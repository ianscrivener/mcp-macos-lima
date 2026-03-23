# Product Requirements Document (PRD)


## Problem

Managing Colima container runtimes on macOS requires manual CLI interaction. There is no structured way for AI assistants to discover, invoke, or orchestrate Colima operations — creating friction in AI-assisted development workflows that depend on local container infrastructure.

## Solution

A FastMCP (Python) server exposing Colima CLI operations as MCP tools. The server wraps `colima`, returning structured JSON responses suitable for AI agent consumption.

## Delivery

|  |  |
| --- | --- |
| **Name** | `mcp-colima` |
| **Runtime** | Python 3.11+ / FastMCP |
| **Host dependency** | `colima` (latest, Homebrew) |
| **Transport** | stdio |
| **Config** | Claude Desktop / Claude Code |

## Phasing

| Phase | Scope |
| --- | --- |
| **Phase 1 — MVP** | Core tools (7 tools) |
| **Phase 2** | Kubernetes, delete, ssh-config |
| **Phase 3** | AI/models, nerdctl, utility commands |

---

## Tool Surface

| Category | Command | Core | Description |
| --- | --- | --- | --- |
| **Lifecycle** | `start [profile]` | Y | Start VM (creates if needed) |
|  | `stop [profile]` | Y | Stop VM |
|  | `restart [profile]` | Y | Restart VM |
|  | `delete [profile]` | N | Delete VM (preserves data since v0.9) |
|  | `status [profile]` | Y | Show VM status and resources |
|  | `list` | Y | List all profiles with status |
| **Access** | `ssh [profile]` | Y | SSH into VM |
|  | `ssh-config [profile]` | N | Show SSH config |
| **Kubernetes** | `kubernetes start` | N | Start k8s on running instance |
|  | `kubernetes stop` | N | Stop k8s |
|  | `kubernetes reset` | N | Reset k8s cluster |
| **AI/Models** | `model run <model>` | N | Run AI model interactively (krunkit) |
|  | `model serve <model>` | N | Serve model with web chat UI |
| **Containerd** | `nerdctl -- <cmd>` | N | Run nerdctl commands |
|  | `nerdctl install` | N | Install nerdctl to $PATH |
| **Config/Util** | `template` | N | Generate config template YAML |
|  | `update` | N | Update Colima |
|  | `prune [profile]` | N | Prune unused data |
|  | `version` | Y | Show version |
|  | `completion` | N | Generate shell completions |

**Phase 1 scope: 7 tools** — start, stop, restart, status, list, ssh, version

Detailed parameter mapping maintained in `METHODS_SUPPORTED.md`.

---

## Design Patterns

**CLI wrapping:** All tools call `colima` via `subprocess.run()`, parse output (preferring `--json` where available), and return structured JSON.

**Error handling:** Non-zero exit codes return `{ "error": true, "exit_code": N, "stderr": "..." }`. Tools never raise — they always return a parseable response.

**Profile targeting:** All lifecycle tools accept an optional profile name, defaulting to `default`.

**Destructive operations:** `delete` and `kubernetes reset` require an explicit `confirm=True` parameter. Without it, they return a preview of what would be affected.

**Timeouts:** Long-running operations (start, restart) include a configurable timeout defaulting to 5 minutes.

## Constraints

-   macOS host only (targeting macOS dev workflows)
-   Requires `colima` pre-installed via Homebrew
-   stdio transport — no remote/networked access
-   No secrets or credentials handled

## Success Criteria

-   Phase 1 tools pass basic smoke tests (start/stop/list/status cycle)
-   Structured JSON output for all tools
-   Works in both Claude Desktop and Claude Code
-   `METHODS_SUPPORTED.md` is accurate and current

## Open Questions

1.  Should `start` expose the full flag surface (30+ flags) or use a simplified parameter set with an `--edit` escape hatch?
2.  Should `ssh` support streaming/interactive sessions or only one-shot commands?
3.  Is there value in a shared Python package with `mcp-lima` for common patterns (subprocess wrapper, JSON parsing, error handling)?