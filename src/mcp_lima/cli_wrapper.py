from __future__ import annotations

import json
import subprocess
from typing import Any

from .models import CommandResponse


class LimaCLI:
    def __init__(self, binary: str = "limactl") -> None:
        self.binary = binary

    def run(self, args: list[str], timeout_seconds: int = 60, parse_json: bool = False) -> dict[str, Any]:
        command = [self.binary, *args]
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except FileNotFoundError:
            return CommandResponse(
                error=True,
                command=command,
                exit_code=127,
                stderr=f"{self.binary} not found on PATH",
                message="Install Lima and ensure limactl is available.",
            ).model_dump()
        except subprocess.TimeoutExpired:
            return CommandResponse(
                error=True,
                command=command,
                exit_code=124,
                stderr=f"Command timed out after {timeout_seconds} seconds",
            ).model_dump()

        if proc.returncode != 0:
            return CommandResponse(
                error=True,
                command=command,
                exit_code=proc.returncode,
                stdout=(proc.stdout or "").strip(),
                stderr=(proc.stderr or "").strip(),
            ).model_dump()

        parsed_data: Any | None = None
        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()
        if parse_json and stdout:
            parsed_data = self._parse_json_output(stdout)

        return CommandResponse(
            error=False,
            command=command,
            exit_code=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            data=parsed_data,
        ).model_dump()

    def _parse_json_output(self, stdout: str) -> Any | None:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass

        # limactl list --json may emit multiple JSON objects in sequence.
        decoder = json.JSONDecoder()
        idx = 0
        items: list[Any] = []
        text = stdout

        while idx < len(text):
            while idx < len(text) and text[idx].isspace():
                idx += 1
            if idx >= len(text):
                break
            try:
                obj, next_idx = decoder.raw_decode(text, idx)
            except json.JSONDecodeError:
                return None
            items.append(obj)
            idx = next_idx

        if not items:
            return None
        if len(items) == 1:
            return items[0]
        return items
