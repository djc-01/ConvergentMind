from __future__ import annotations

from abc import ABC, abstractmethod

from convergentmind.schemas import ActionResult, PlannedAction


class ComputerController(ABC):
    @abstractmethod
    def execute(self, action: PlannedAction) -> ActionResult:
        raise NotImplementedError
