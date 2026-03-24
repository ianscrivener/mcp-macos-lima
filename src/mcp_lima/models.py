from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommandResponse(BaseModel):
    error: bool = False
    command: list[str]
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    data: Any | None = None
    message: str | None = None
    ignored_extra_args: list[str] = Field(default_factory=list)


class HealthcheckResponse(CommandResponse):
    status: str = "ok"
    server: str


class DeletePreview(CommandResponse):
    preview: bool = True
    action: str = "delete"
    instance: str
