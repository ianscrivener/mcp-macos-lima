#!/usr/bin/env bash
# reset_claude_config.sh
#
# Removes MCP servers and plugins from Claude Code / Claude Desktop configs.
# Edit this file BEFORE running: comment out (#) any entries you want to KEEP.
#
# MCP servers  → ~/Library/Application Support/Claude/claude_desktop_config.json
# Plugins      → ~/.claude/settings.json (enabledPlugins section)
#
# Usage: bash reset_claude_config.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

CLAUDE_DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
CLAUDE_CODE_SETTINGS="$HOME/.claude/settings.json"

# ─── Helpers ────────────────────────────────────────────────────────────────

backup() {
    local file="$1"
    local bak="${file}.bak.$(date +%Y%m%d_%H%M%S)"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] Would backup: $file → $bak"
    else
        cp "$file" "$bak"
        echo "Backed up: $file → $bak"
    fi
}

remove_mcp() {
    local name="$1"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] Would remove MCP server: $name"
        return
    fi
    python3 - "$CLAUDE_DESKTOP_CONFIG" "$name" <<'EOF'
import sys, json
path, key = sys.argv[1], sys.argv[2]
with open(path) as f:
    cfg = json.load(f)
if key in cfg.get("mcpServers", {}):
    del cfg["mcpServers"][key]
    with open(path, "w") as f:
        json.dump(cfg, f, indent=4)
    print(f"  Removed MCP server: {key}")
else:
    print(f"  Already absent (skip): {key}")
EOF
}

remove_plugin() {
    local name="$1"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[dry-run] Would disable plugin: $name"
        return
    fi
    python3 - "$CLAUDE_CODE_SETTINGS" "$name" <<'EOF'
import sys, json
path, key = sys.argv[1], sys.argv[2]
with open(path) as f:
    cfg = json.load(f)
if key in cfg.get("enabledPlugins", {}):
    del cfg["enabledPlugins"][key]
    with open(path, "w") as f:
        json.dump(cfg, f, indent=4)
    print(f"  Removed plugin: {key}")
else:
    print(f"  Already absent (skip): {key}")
EOF
}

# ─── MCP Servers (claude_desktop_config.json) ───────────────────────────────
# Comment out any line below to KEEP that MCP server.

echo ""
echo "=== MCP Servers ==="
backup "$CLAUDE_DESKTOP_CONFIG"

# remove_mcp "mcp-macos-colima"
# remove_mcp "mcp-macos-lima"
# remove_mcp "openrouter"
# remove_mcp "@mcp-get-community/server-curl"
# remove_mcp "lmstudio"
# remove_mcp "postgres_prompts26"
# remove_mcp "postgres_babel_engine"
# remove_mcp "postgres_babel_score"
# remove_mcp "postgres_obsidian26"
# remove_mcp "clickhouse"
# remove_mcp "svelte"
# remove_mcp "Homebrew"
# remove_mcp "playwright"
# remove_mcp "obsidian-mcp-tools"
# remove_mcp "mcp-tts-kokoro"
# remove_mcp "fastmail"

# ─── Plugins (enabledPlugins in ~/.claude/settings.json) ────────────────────
# Comment out any line below to KEEP that plugin.

echo ""
echo "=== Plugins ==="
backup "$CLAUDE_CODE_SETTINGS"

remove_plugin "claude-md-management@claude-plugins-official"
remove_plugin "code-review@claude-plugins-official"
remove_plugin "code-simplifier@claude-plugins-official"
remove_plugin "context7@claude-plugins-official"
remove_plugin "frontend-design@claude-plugins-official"
remove_plugin "github@claude-plugins-official"
remove_plugin "security-guidance@claude-plugins-official"
remove_plugin "ralph-loop@claude-plugins-official"
remove_plugin "skill-creator@claude-plugins-official"
remove_plugin "claude-hud@claude-hud"
remove_plugin "pyright-lsp@claude-plugins-official"
remove_plugin "coderabbit@claude-plugins-official"
remove_plugin "superpowers@claude-plugins-official"
remove_plugin "typescript-lsp@claude-plugins-official"
remove_plugin "aws-serverless@claude-plugins-official"
remove_plugin "mintlify@claude-plugins-official"
remove_plugin "vercel@claude-plugins-official"
remove_plugin "claude-code-setup@claude-plugins-official"

echo ""
echo "Done. Restart Claude Code and Claude Desktop for changes to take effect."
