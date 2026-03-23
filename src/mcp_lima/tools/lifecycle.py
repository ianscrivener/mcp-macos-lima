from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..cli_wrapper import LimaCLI
from ..models import DeletePreview

ADVANCED_ARG_FLAGS = {
    "cpus": "--cpus",
    "memory": "--memory",
    "disk": "--disk",
    "vm_type": "--vm-type",
    "network": "--network",
    "mount_type": "--mount-type",
    "mount_writable": "--mount-writable",
    "rosetta": "--rosetta",
    "plain": "--plain",
}


def normalize_instance(instance: str | None) -> str:
    return (instance or "default").strip() or "default"


def build_advanced_args(extra_args: dict[str, Any] | None) -> tuple[list[str], list[str]]:
    if not extra_args:
        return [], []

    args: list[str] = []
    ignored: list[str] = []
    for key, value in extra_args.items():
        flag = ADVANCED_ARG_FLAGS.get(key)
        if not flag:
            ignored.append(key)
            continue
        if isinstance(value, bool):
            if value:
                args.append(flag)
            continue
        args.extend([flag, str(value)])
    return args, ignored


def register_lifecycle_tools(mcp: FastMCP, cli: LimaCLI) -> None:
    @mcp.tool
    def lima_create(
        instance: str = "default",
        template: str | None = None,
        config_path: str | None = None,
        extra_args: dict[str, Any] | None = None,
        timeout_seconds: int = 600,
    ) -> dict[str, Any]:
        name = normalize_instance(instance)
        args = ["create", "--tty=false", "--name", name]
        advanced, ignored = build_advanced_args(extra_args)
        args.extend(advanced)

        if config_path:
            args.append(config_path)
        elif template:
            args.append(template)
        else:
            args.append("template://default")

        result = cli.run(args, timeout_seconds=timeout_seconds)
        result["ignored_extra_args"] = ignored
        return result

    @mcp.tool
    def lima_start(
        instance: str = "default",
        extra_args: dict[str, Any] | None = None,
        timeout_seconds: int = 600,
    ) -> dict[str, Any]:
        name = normalize_instance(instance)
        args = ["start", "--tty=false", name]
        advanced, ignored = build_advanced_args(extra_args)
        args.extend(advanced)
        result = cli.run(args, timeout_seconds=timeout_seconds)
        result["ignored_extra_args"] = ignored
        return result

    @mcp.tool
    def lima_stop(instance: str = "default", timeout_seconds: int = 180) -> dict[str, Any]:
        name = normalize_instance(instance)
        return cli.run(["stop", name], timeout_seconds=timeout_seconds)

    @mcp.tool
    def lima_restart(instance: str = "default", timeout_seconds: int = 600) -> dict[str, Any]:
        name = normalize_instance(instance)
        return cli.run(["restart", name], timeout_seconds=timeout_seconds)

    @mcp.tool
    def lima_delete(
        instance: str = "default",
        confirm: bool = False,
        timeout_seconds: int = 300,
    ) -> dict[str, Any]:
        name = normalize_instance(instance)
        if not confirm:
            return DeletePreview(instance=name).model_dump()
        return cli.run(["delete", name], timeout_seconds=timeout_seconds)
