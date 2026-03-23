import subprocess

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
