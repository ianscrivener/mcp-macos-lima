import asyncio
import shutil
import subprocess

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def limactl_available():
    """Skip all integration tests if limactl is not on PATH."""
    if not shutil.which("limactl"):
        pytest.skip("limactl not found on PATH")


@pytest.fixture(scope="module")
def default_running(limactl_available):
    """Skip if the 'default' Lima instance is not in Running state."""
    proc = subprocess.run(
        ["limactl", "list", "--json"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0 or "Running" not in proc.stdout:
        pytest.skip("Lima 'default' instance is not running")


# ---------------------------------------------------------------------------
# Basic availability
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_limactl_is_available_for_integration(limactl_available):
    proc = subprocess.run(["limactl", "--help"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0


@pytest.mark.integration
def test_limactl_version(limactl_available):
    proc = subprocess.run(["limactl", "--version"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0
    assert "limactl" in proc.stdout.lower() or "limactl" in proc.stderr.lower()


# ---------------------------------------------------------------------------
# LimaCLI wrapper — real subprocess calls
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_cli_wrapper_list(limactl_available):
    from mcp_lima.cli_wrapper import LimaCLI

    cli = LimaCLI()
    result = cli.run(["list", "--json"], parse_json=True)
    assert result["error"] is False
    # data is either a single instance dict or a list of them
    assert result["data"] is not None


@pytest.mark.integration
def test_cli_wrapper_info(limactl_available):
    from mcp_lima.cli_wrapper import LimaCLI

    cli = LimaCLI()
    result = cli.run(["info"], parse_json=True)
    assert result["error"] is False


@pytest.mark.integration
def test_cli_wrapper_nonexistent_binary():
    from mcp_lima.cli_wrapper import LimaCLI

    cli = LimaCLI(binary="limactl-does-not-exist")
    result = cli.run(["list"])
    assert result["error"] is True
    assert result["exit_code"] == 127


# ---------------------------------------------------------------------------
# lima_list tool — real run
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_lima_list_tool_real(limactl_available):
    from mcp_lima.server import create_server

    server = create_server()
    result = asyncio.run(server.call_tool("lima_list", {})).structured_content
    assert result["error"] is False


# ---------------------------------------------------------------------------
# lima_shell tool — real run against running instance
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_lima_shell_uname(default_running):
    from mcp_lima.server import create_server

    server = create_server()
    result = asyncio.run(
        server.call_tool("lima_shell", {"command": "uname -s", "instance": "default"})
    ).structured_content
    assert result["error"] is False
    assert "Linux" in result["stdout"]


@pytest.mark.integration
def test_lima_shell_error_exit_code(default_running):
    from mcp_lima.server import create_server

    server = create_server()
    result = asyncio.run(
        server.call_tool("lima_shell", {"command": "exit 42", "instance": "default"})
    ).structured_content
    assert result["error"] is True
    assert result["exit_code"] == 42
