import asyncio

from fastmcp import FastMCP

from mcp_lima.server import create_server


def test_create_server_returns_fastmcp():
    assert isinstance(create_server(), FastMCP)


def test_create_server_name():
    assert create_server().name == "mcp-lima"


def test_all_expected_tools_registered():
    server = create_server()
    tools = asyncio.run(server.list_tools())
    tool_names = {t.name for t in tools}
    expected = {
        "lima_create", "lima_start", "lima_stop", "lima_restart", "lima_delete",
        "lima_list", "lima_info", "lima_edit",
        "lima_shell", "lima_copy",
        "lima_healthcheck",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


def test_healthcheck_returns_ok():
    server = create_server()
    result = asyncio.run(server.call_tool("lima_healthcheck", {}))
    payload = result.structured_content
    assert payload["status"] == "ok"
    assert payload["server"] == "mcp-lima"
    assert payload["error"] is False
    assert payload["command"] == ["internal", "lima_healthcheck"]
    assert payload["exit_code"] == 0
    assert payload["stdout"] == ""
    assert payload["stderr"] == ""
    assert payload["data"] == {"status": "ok", "server": "mcp-lima"}
