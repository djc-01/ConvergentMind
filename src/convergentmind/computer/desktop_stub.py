from __future__ import annotations

from convergentmind.computer.base import ComputerController
from convergentmind.schemas import ActionResult, PlannedAction


class DesktopComputerStub(ComputerController):
    def execute(self, action: PlannedAction) -> ActionResult:
        return ActionResult(
            success=False,
            message="Desktop computer control is not implemented in v1.",
            error=f"Unsupported desktop action: {action.kind.value}",
        )
