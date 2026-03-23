# INSTALL_MCP (mcp-macos-lima)

This guide explains how to install and configure the Lima MCP server (`mcp-lima`) for Claude, GitHub Copilot, Codex, and other MCP-capable clients.

## 1. Prerequisites

- macOS
- Python 3.11+
- Homebrew
- UV package manager
- Lima CLI (`limactl`)

Install missing tools:

    brew install uv
    brew install lima

Verify:

    uv --version
    limactl --version

## 2. Clone And Set Up

    git clone git@github.com:ianscrivener/mcp-macos-lima.git
    cd mcp-macos-lima
    uv venv
    source .venv/bin/activate
    uv sync --extra dev

Important: `uv sync --extra dev` is required so runtime and test dependencies are installed.

## 3. MCP Server Definition

Use these values in your MCP client:

- server name: `mcp-macos-lima`
- command: `uv`
- args: `run mcp-lima`
- working directory (`cwd`): absolute path to your `mcp-macos-lima` repository

JSON-style example:

    {
      "mcpServers": {
        "mcp-macos-lima": {
          "command": "uv",
          "args": ["run", "mcp-lima"],
          "cwd": "/absolute/path/to/mcp-macos-lima"
        }
      }
    }

## 4. Client Notes

### Claude (Claude Code / Claude Desktop)

- Open MCP settings.
- Add the server using command/args/cwd above.
- Restart the client.
- Confirm tool discovery.

### GitHub Copilot (VS Code)

- Open MCP server management.
- Add one server (`mcp-macos-lima`) with the same command/args/cwd.
- Reload VS Code if required.

### Codex

- Open MCP/server configuration.
- Register the server with the same command/args/cwd.
- Restart/reload and verify tools appear.

## 5. Quick Verification

After registration, run:

- `lima_healthcheck`

Expected response includes:

- `status: ok`
- `server: mcp-lima`

## 6. Troubleshooting

### `uv` not found

- Install UV: `brew install uv`
- Verify from terminal: `uv --version`

### Python modules missing

- Re-run:

    source .venv/bin/activate
    uv sync --extra dev

### `limactl` not found

- Install Lima via Homebrew.
- Verify `limactl --version`.

### Server starts but no tools appear

- Recheck `cwd` path.
- Recheck command/args values.
- Restart the client after config changes.
