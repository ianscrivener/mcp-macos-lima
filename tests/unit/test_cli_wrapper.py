import subprocess

import pytest

from mcp_lima.cli_wrapper import LimaCLI


def test_run_success_with_json(mocker):
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["limactl", "list", "--json"], returncode=0, stdout='[{"name":"default"}]', stderr=""
        ),
    )
    cli = LimaCLI()
    result = cli.run(["list", "--json"], parse_json=True)
    assert result["error"] is False
    assert result["data"] == [{"name": "default"}]


def test_run_non_zero_exit(mocker):
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["limactl", "start", "default"], returncode=1, stdout="", stderr="boom"
        ),
    )
    cli = LimaCLI()
    result = cli.run(["start", "default"])
    assert result["error"] is True
    assert result["exit_code"] == 1
    assert result["stderr"] == "boom"


def test_run_timeout(mocker):
    mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="limactl start", timeout=1))
    cli = LimaCLI()
    result = cli.run(["start", "default"], timeout_seconds=1)
    assert result["error"] is True
    assert result["exit_code"] == 124


def test_run_success_with_concatenated_json(mocker):
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["limactl", "list", "--json"],
            returncode=0,
            stdout='{"name":"a"}\n{"name":"b"}',
            stderr="",
        ),
    )
    cli = LimaCLI()
    result = cli.run(["list", "--json"], parse_json=True)
    assert result["error"] is False
    assert isinstance(result["data"], list)
    assert result["data"] == [{"name": "a"}, {"name": "b"}]


def test_run_binary_not_found(mocker):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    cli = LimaCLI()
    result = cli.run(["list"])
    assert result["error"] is True
    assert result["exit_code"] == 127
    assert "not found" in result["stderr"]
    assert result["message"] is not None


def test_run_success_without_json_parse(mocker):
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["limactl", "info"], returncode=0, stdout='{"version":"2.1.0"}', stderr=""
        ),
    )
    cli = LimaCLI()
    result = cli.run(["info"], parse_json=False)
    assert result["error"] is False
    assert result["data"] is None
    assert result["stdout"] == '{"version":"2.1.0"}'


def test_run_success_empty_stdout_with_parse_json(mocker):
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["limactl", "stop", "default"], returncode=0, stdout="", stderr=""
        ),
    )
    cli = LimaCLI()
    result = cli.run(["stop", "default"], parse_json=True)
    assert result["error"] is False
    assert result["data"] is None


def test_run_custom_binary(mocker):
    mock = mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
    )
    cli = LimaCLI(binary="/usr/local/bin/limactl")
    cli.run(["list"])
    assert mock.call_args[0][0][0] == "/usr/local/bin/limactl"


def test_parse_json_output_invalid_returns_none():
    cli = LimaCLI()
    result = cli._parse_json_output("not json at all !!!")
    assert result is None


def test_parse_json_output_single_object():
    cli = LimaCLI()
    result = cli._parse_json_output('{"name":"default"}')
    assert result == {"name": "default"}


def test_parse_json_output_single_item_sequence():
    """Single JSON object parsed via streaming decoder returns the object, not a list."""
    cli = LimaCLI()
    result = cli._parse_json_output('{"name":"only"}')
    assert result == {"name": "only"}


@pytest.mark.parametrize("stdout,expected", [
    ('{"a":1}\n{"b":2}\n{"c":3}', [{"a": 1}, {"b": 2}, {"c": 3}]),
    ('  {"x":true}  {"y":false}  ', [{"x": True}, {"y": False}]),
])
def test_parse_json_output_multi_object_variants(stdout, expected):
    cli = LimaCLI()
    assert cli._parse_json_output(stdout) == expected
