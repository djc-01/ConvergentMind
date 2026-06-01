from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ActionKind(str, Enum):
    GOTO = "goto"
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"
    WAIT = "wait"
    DONE = "done"
    FAIL = "fail"


class UIElement(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tag: str
    role: str | None = None
    text: str | None = None
    label: str | None = None
    placeholder: str | None = None
    name: str | None = None
    type: str | None = None
    selector_hint: str | None = None


class ActionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    message: str
    error: str | None = None
    data: dict[str, Any] | None = None


class CameraSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    frame_path: Path
    timestamp: str
    width: int
    height: int
    status: Literal["ok", "unavailable"]
    note: str | None = None


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    title: str
    screenshot_path: Path
    visible_text: str
    elements: list[UIElement] = Field(default_factory=list)
    camera_snapshot: CameraSnapshot | None = None
    last_action_result: ActionResult | None = None


class PlannedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: ActionKind
    reason: str
    url: str | None = None
    selector: str | None = None
    text: str | None = None
    label: str | None = None
    role: str | None = None
    target_text: str | None = None
    nth: int | None = None
    duration_ms: int | None = None
    query: str | None = None
    final_message: str | None = None

    @model_validator(mode="after")
    def validate_fields(self) -> "PlannedAction":
        locator_present = any([self.selector, self.label, self.role, self.target_text, self.nth is not None])
        if self.kind == ActionKind.GOTO and not self.url:
            raise ValueError("goto actions require url")
        if self.kind == ActionKind.CLICK and not locator_present:
            raise ValueError("click actions require selector, label, role, target_text, or nth")
        if self.kind == ActionKind.TYPE:
            if not self.text:
                raise ValueError("type actions require text")
            if not locator_present:
                raise ValueError("type actions require selector, label, role, target_text, or nth")
        if self.kind == ActionKind.WAIT and not self.duration_ms:
            raise ValueError("wait actions require duration_ms")
        if self.kind == ActionKind.EXTRACT and not self.query:
            raise ValueError("extract actions require query")
        if self.kind in {ActionKind.DONE, ActionKind.FAIL} and not self.final_message:
            raise ValueError("done/fail actions require final_message")
        return self


class VerificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    summary: str
    should_retry: bool = False


class StepRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_index: int
    planned_action: PlannedAction
    before: Observation
    after: Observation | None = None
    action_result: ActionResult
    verification: VerificationResult | None = None


class TaskState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    start_url: str
    steps: list[StepRecord] = Field(default_factory=list)
    short_term_memory: list[str] = Field(default_factory=list)
    final_result: str | None = None
    consecutive_failures: int = 0
    status: Literal["running", "completed", "failed"] = "running"
