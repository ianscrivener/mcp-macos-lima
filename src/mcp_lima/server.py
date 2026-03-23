from __future__ import annotations

from fastmcp import FastMCP

from .cli_wrapper import LimaCLI
from .tools.access import register_access_tools
from .tools.instances import register_instance_tools
from .tools.lifecycle import register_lifecycle_tools


def create_server() -> FastMCP:
    mcp = FastMCP(name="mcp-lima")
    cli = LimaCLI()

    register_lifecycle_tools(mcp, cli)
    register_instance_tools(mcp, cli)
    register_access_tools(mcp, cli)

    @mcp.tool
    def lima_healthcheck() -> dict[str, str]:
        return {"status": "ok", "server": "mcp-lima"}

    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
