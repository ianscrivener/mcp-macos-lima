"""Unit tests for all tool modules.

FastMCP 3.x does not expose _tool_manager; tools are invoked via
  asyncio.run(mcp.call_tool(name, kwargs))
which returns a ToolResult whose .structured_content holds the dict.
"""
import asyncio
import subprocess
import unittest.mock as mock

import pytest

from mcp_lima.tools.lifecycle import build_advanced_args, normalize_instance
from mcp_lima.tools.instances import normalize_memory_value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _call(mcp, name, **kwargs):
    """Invoke a registered tool and return its structured_content dict."""
    result = asyncio.run(mcp.call_tool(name, kwargs))
    return result.structured_content


def _make_mcp_and_cli(register_fn, returncode=0, stdout="", stderr="", side_effect=None):
    """Build a FastMCP + LimaCLI with subprocess.run mocked, register tools."""
    from fastmcp import FastMCP
    from mcp_lima.cli_wrapper import LimaCLI

    completed = subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )
    patch_target = side_effect if side_effect else completed
    ctx = mock.patch("subprocess.run", side_effect=side_effect) if side_effect \
        else mock.patch("subprocess.run", return_value=completed)

    with ctx:
        cli = LimaCLI()
        mcp = FastMCP(name="test")
        register_fn(mcp, cli)
        return mcp, cli, ctx


# ---------------------------------------------------------------------------
# normalize_instance
# ---------------------------------------------------------------------------

def test_normalize_instance_defaults_to_default():
    assert normalize_instance(None) == "default"
    assert normalize_instance("") == "default"


def test_normalize_instance_strips_whitespace():
    assert normalize_instance("  myvm  ") == "myvm"


def test_normalize_instance_whitespace_only_falls_back():
    assert normalize_instance("   ") == "default"


def test_normalize_instance_preserves_name():
    assert normalize_instance("dev") == "dev"


# ---------------------------------------------------------------------------
# build_advanced_args
# ---------------------------------------------------------------------------

def test_build_advanced_args_allowlist():
    args, ignored = build_advanced_args(
        {"cpus": 4, "memory": "8GiB", "mount_writable": True, "unknown": "x"}
    )
    assert "--cpus" in args
    assert "--memory" in args
    assert "--mount-writable" in args
    assert ignored == ["unknown"]


def test_build_advanced_args_none_returns_empty():
    assert build_advanced_args(None) == ([], [])


def test_build_advanced_args_empty_dict():
    assert build_advanced_args({}) == ([], [])


def test_build_advanced_args_bool_false_omits_flag():
    args, ignored = build_advanced_args({"mount_writable": False})
    assert "--mount-writable" not in args
    assert ignored == []


def test_build_advanced_args_rosetta_true():
    args, _ = build_advanced_args({"rosetta": True})
    assert "--rosetta" in args


def test_build_advanced_args_all_ignored():
    args, ignored = build_advanced_args({"foo": "bar", "baz": 1})
    assert args == []
    assert set(ignored) == {"foo", "baz"}


def test_normalize_memory_value_gib_string():
    assert normalize_memory_value("2GiB") == "2"
    assert normalize_memory_value("2 gb") == "2"


def test_normalize_memory_value_mib_string():
    assert normalize_memory_value("1024MiB") == "1"
    assert normalize_memory_value("1536MB") == "1.5"


# ---------------------------------------------------------------------------
# lifecycle tools
# ---------------------------------------------------------------------------

class TestLifecycleTools:
    def _mcp(self, returncode=0, stdout="", stderr="", side_effect=None):
        from fastmcp import FastMCP
        from mcp_lima.cli_wrapper import LimaCLI
        from mcp_lima.tools.lifecycle import register_lifecycle_tools

        completed = subprocess.CompletedProcess(
            args=[], returncode=returncode, stdout=stdout, stderr=stderr
        )
        if side_effect:
            patcher = mock.patch("subprocess.run", side_effect=side_effect)
        else:
            patcher = mock.patch("subprocess.run", return_value=completed)

        self._patcher = patcher
        patcher.start()
        cli = LimaCLI()
        mcp = FastMCP(name="test")
        register_lifecycle_tools(mcp, cli)
        self._mock = mock.patch("subprocess.run").start  # kept reference
        return mcp

    def teardown_method(self):
        mock.patch.stopall()

    def test_lima_create_default_template(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_create")
            assert result["error"] is False
            cmd = m.call_args[0][0]
            assert "template://default" in cmd

    def test_lima_create_with_template(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            _call(mcp, "lima_create", template="debian")
            assert "debian" in m.call_args[0][0]

    def test_lima_create_with_config_path(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            _call(mcp, "lima_create", config_path="/tmp/myvm.yaml")
            assert "/tmp/myvm.yaml" in m.call_args[0][0]

    def test_lima_create_extra_args_ignored_returned(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )):
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_create", extra_args={"cpus": 2, "bogus": "val"})
            assert "bogus" in result["ignored_extra_args"]

    def test_lima_start(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_start", instance="myvm")
            assert result["error"] is False
            assert "myvm" in m.call_args[0][0]

    def test_lima_stop(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_stop")
            assert result["error"] is False
            assert "stop" in m.call_args[0][0]

    def test_lima_restart(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )):
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_restart", instance="dev")
            assert result["error"] is False

    def test_lima_delete_preview_when_not_confirmed(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )):
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_delete", instance="myvm", confirm=False)
            assert result["preview"] is True
            assert result["action"] == "delete"
            assert result["instance"] == "myvm"
            assert "confirm=true" in result["message"].lower()
            assert result["error"] is False
            assert result["command"] == ["limactl", "delete", "myvm"]
            assert result["exit_code"] == 0
            assert result["stdout"] == ""
            assert result["stderr"] == ""
            assert result["data"] == {"preview": True, "action": "delete", "instance": "myvm"}

    def test_lima_delete_executes_when_confirmed(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )) as m:
            from fastmcp import FastMCP
            from mcp_lima.cli_wrapper import LimaCLI
            from mcp_lima.tools.lifecycle import register_lifecycle_tools
            cli = LimaCLI()
            mcp = FastMCP(name="test")
            register_lifecycle_tools(mcp, cli)
            result = _call(mcp, "lima_delete", instance="myvm", confirm=True)
            assert result["error"] is False
            cmd = m.call_args[0][0]
            assert "delete" in cmd
            assert "myvm" in cmd


# ---------------------------------------------------------------------------
# instances tools
# ---------------------------------------------------------------------------

class TestInstancesTools:
    def _setup(self, returncode=0, stdout="", stderr=""):
        from fastmcp import FastMCP
        from mcp_lima.cli_wrapper import LimaCLI
        from mcp_lima.tools.instances import register_instance_tools
        self._patcher = mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=returncode, stdout=stdout, stderr=stderr
        ))
        self._mock = self._patcher.start()
        cli = LimaCLI()
        mcp = FastMCP(name="test")
        register_instance_tools(mcp, cli)
        return mcp

    def teardown_method(self):
        mock.patch.stopall()

    def test_lima_list_parses_json(self):
        mcp = self._setup(stdout='{"name":"default"}')
        result = _call(mcp, "lima_list")
        assert result["error"] is False
        assert result["data"] == {"name": "default"}

    def test_lima_list_error(self):
        mcp = self._setup(returncode=1)
        result = _call(mcp, "lima_list")
        assert result["error"] is True

    def test_lima_info_json(self):
        mcp = self._setup(stdout='{"version":"2.1.0"}')
        result = _call(mcp, "lima_info", json_output=True)
        assert result["data"] == {"version": "2.1.0"}

    def test_lima_info_no_json(self):
        mcp = self._setup(stdout='{"version":"2.1.0"}')
        result = _call(mcp, "lima_info", json_output=False)
        assert result["data"] is None
        assert result["stdout"] == '{"version":"2.1.0"}'

    def test_lima_edit_no_fields_returns_error(self):
        mcp = self._setup()
        result = _call(mcp, "lima_edit", instance="default")
        assert result["error"] is True
        assert result["exit_code"] == 2
        assert "No patch fields" in result["stderr"]

    def test_lima_edit_cpus(self):
        mcp = self._setup()
        result = _call(mcp, "lima_edit", instance="default", cpus=4)
        assert result["error"] is False
        cmd = self._mock.call_args[0][0]
        assert "--cpus" in cmd and "4" in cmd

    def test_lima_edit_memory(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", memory="8GiB")
        cmd = self._mock.call_args[0][0]
        assert "--memory" in cmd
        memory_index = cmd.index("--memory") + 1
        assert cmd[memory_index] == "8"

    def test_lima_edit_mount_writable_false_omitted(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", cpus=2, mount_writable=False)
        assert "--mount-writable" not in self._mock.call_args[0][0]

    def test_lima_edit_rosetta_true(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", rosetta=True)
        assert "--rosetta" in self._mock.call_args[0][0]

    def test_lima_edit_disk(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", disk="50GiB")
        cmd = self._mock.call_args[0][0]
        assert "--disk" in cmd and "50GiB" in cmd

    def test_lima_edit_vm_type(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", vm_type="qemu")
        cmd = self._mock.call_args[0][0]
        assert "--vm-type" in cmd and "qemu" in cmd

    def test_lima_edit_network(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", network="vzNAT")
        cmd = self._mock.call_args[0][0]
        assert "--network" in cmd and "vzNAT" in cmd

    def test_lima_edit_mount_type(self):
        mcp = self._setup()
        _call(mcp, "lima_edit", instance="default", mount_type="9p")
        cmd = self._mock.call_args[0][0]
        assert "--mount-type" in cmd and "9p" in cmd


# ---------------------------------------------------------------------------
# access tools
# ---------------------------------------------------------------------------

class TestAccessTools:
    def _setup(self, returncode=0, stdout="", stderr=""):
        from fastmcp import FastMCP
        from mcp_lima.cli_wrapper import LimaCLI
        from mcp_lima.tools.access import register_access_tools
        self._patcher = mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=returncode, stdout=stdout, stderr=stderr
        ))
        self._mock = self._patcher.start()
        cli = LimaCLI()
        mcp = FastMCP(name="test")
        register_access_tools(mcp, cli)
        return mcp

    def teardown_method(self):
        mock.patch.stopall()

    def test_lima_shell_runs_command(self):
        mcp = self._setup(stdout="hello")
        result = _call(mcp, "lima_shell", command="echo hello", instance="default")
        assert result["error"] is False
        assert result["stdout"] == "hello"
        cmd = self._mock.call_args[0][0]
        assert "shell" in cmd
        assert "echo hello" in cmd

    def test_lima_shell_non_default_instance(self):
        mcp = self._setup()
        _call(mcp, "lima_shell", command="uname", instance="dev")
        assert "dev" in self._mock.call_args[0][0]

    def test_lima_shell_error_propagated(self):
        mcp = self._setup(returncode=1)
        result = _call(mcp, "lima_shell", command="false")
        assert result["error"] is True

    def test_lima_copy_success(self):
        mcp = self._setup()
        result = _call(mcp, "lima_copy", sources=["default:/tmp/foo.txt"], destination="/Users/ian/foo.txt")
        assert result["error"] is False
        cmd = self._mock.call_args[0][0]
        assert "copy" in cmd
        assert "default:/tmp/foo.txt" in cmd

    def test_lima_copy_empty_sources_returns_error(self):
        mcp = self._setup()
        result = _call(mcp, "lima_copy", sources=[], destination="/tmp/out")
        assert result["error"] is True
        assert result["exit_code"] == 2
        assert "source" in result["stderr"].lower()

    def test_lima_copy_multiple_sources(self):
        mcp = self._setup()
        _call(mcp, "lima_copy", sources=["default:/a", "default:/b"], destination="/tmp/out")
        cmd = self._mock.call_args[0][0]
        assert "default:/a" in cmd
        assert "default:/b" in cmd
