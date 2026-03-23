#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_file="${repo_dir}/mac_config_snippet.json"

json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

escaped_repo_dir="$(json_escape "${repo_dir}")"

cat > "${output_file}" <<EOF
{
  "mcpServers": {
    "mcp-macos-lima": {
      "command": "uv",
      "args": ["run", "mcp-lima"],
      "cwd": "${escaped_repo_dir}"
    }
  }
}
EOF

printf 'Created %s\n' "${output_file}"
