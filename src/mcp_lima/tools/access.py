from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..cli_wrapper import LimaCLI
from .lifecycle import normalize_instance


def register_access_tools(mcp: FastMCP, cli: LimaCLI) -> None:
    @mcp.tool
    def lima_shell(
        command: str,
        instance: str = "default",
        timeout_seconds: int = 120,
    ) -> dict[str, Any]:
        name = normalize_instance(instance)
        return cli.run(["shell", name, "sh", "-lc", command], timeout_seconds=timeout_seconds)

    @mcp.tool
    def lima_copy(
        sources: list[str],
        destination: str,
        timeout_seconds: int = 180,
    ) -> dict[str, Any]:
        if not sources:
            return {
                "error": True,
                "exit_code": 2,
                "stderr": "At least one source is required.",
                "command": [cli.binary, "copy"],
            }
        args = ["copy", *sources, destination]
        return cli.run(args, timeout_seconds=timeout_seconds)
