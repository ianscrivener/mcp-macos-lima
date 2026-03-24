from __future__ import annotations

import re
from typing import Any

from fastmcp import FastMCP

from ..cli_wrapper import LimaCLI
from .lifecycle import normalize_instance


def normalize_memory_value(memory: str | int | float) -> str:
    if isinstance(memory, (int, float)):
        return str(memory)

    text = str(memory).strip()

    gib_match = re.fullmatch(r"(?i)(\d+(?:\.\d+)?)\s*(gib|gb|g)?", text)
    if gib_match:
        return gib_match.group(1)

    mib_match = re.fullmatch(r"(?i)(\d+(?:\.\d+)?)\s*(mib|mb|m)", text)
    if mib_match:
        gib_value = float(mib_match.group(1)) / 1024
        return f"{gib_value:.3f}".rstrip("0").rstrip(".")

    return text


def register_instance_tools(mcp: FastMCP, cli: LimaCLI) -> None:
    @mcp.tool
    def lima_list(timeout_seconds: int = 60) -> dict[str, Any]:
        return cli.run(["list", "--json"], timeout_seconds=timeout_seconds, parse_json=True)

    @mcp.tool
    def lima_info(json_output: bool = True, timeout_seconds: int = 60) -> dict[str, Any]:
        # limactl info already returns JSON on current Lima versions.
        if json_output:
            return cli.run(["info"], timeout_seconds=timeout_seconds, parse_json=True)
        return cli.run(["info"], timeout_seconds=timeout_seconds)

    @mcp.tool
    def lima_edit(
        instance: str = "default",
        cpus: int | None = None,
        memory: str | int | float | None = None,
        disk: str | int | None = None,
        vm_type: str | None = None,
        mount_type: str | None = None,
        mount_writable: bool | None = None,
        network: str | None = None,
        rosetta: bool | None = None,
        timeout_seconds: int = 300,
    ) -> dict[str, Any]:
        name = normalize_instance(instance)
        args: list[str] = ["edit", name]

        if cpus is not None:
            args.extend(["--cpus", str(cpus)])
        if memory is not None:
            args.extend(["--memory", normalize_memory_value(memory)])
        if disk is not None:
            args.extend(["--disk", str(disk)])
        if vm_type is not None:
            args.extend(["--vm-type", vm_type])
        if mount_type is not None:
            args.extend(["--mount-type", mount_type])
        if network is not None:
            args.extend(["--network", network])
        if mount_writable is True:
            args.append("--mount-writable")
        if rosetta is True:
            args.append("--rosetta")

        if len(args) == 2:
            return {
                "error": True,
                "exit_code": 2,
                "stderr": "No patch fields supplied. Provide one or more editable fields.",
                "command": [cli.binary, *args],
            }

        return cli.run(args, timeout_seconds=timeout_seconds)
