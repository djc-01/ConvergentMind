from __future__ import annotations

from convergentmind.schemas import (
    ActionResult,
    ActionKind,
    Observation,
    PlannedAction,
    VerificationResult,
)


class DemoPlanner:
    """A deterministic planner for the bundled demo form."""

    def __init__(self) -> None:
        self._step = 0

    def plan(self, *, goal: str, observation: Observation, memory: list[str]) -> PlannedAction:
        text = observation.visible_text.lower()
        if "submitted for" in text:
            return PlannedAction(
                kind=ActionKind.DONE,
                reason="The page already shows a submission result.",
                final_message="Demo task completed successfully.",
            )

        if self._step == 0:
            self._step = 1
            return PlannedAction(
                kind=ActionKind.TYPE,
                reason="Fill the name field first.",
                label="Name",
                text="Agent Practice",
            )
        if self._step == 1:
            self._step = 2
            return PlannedAction(
                kind=ActionKind.TYPE,
                reason="Fill the email field next.",
                label="Email",
                text="agent@example.com",
            )
        if self._step == 2:
            self._step = 3
            return PlannedAction(
                kind=ActionKind.CLICK,
                reason="Submit the demo form.",
                target_text="Submit Demo",
            )
        if self._step == 3:
            self._step = 4
            return PlannedAction(
                kind=ActionKind.WAIT,
                reason="Allow the page to update after submit.",
                duration_ms=500,
            )
        return PlannedAction(
            kind=ActionKind.DONE,
            reason="The local demo sequence has finished.",
            final_message="Demo task completed successfully.",
        )


class DemoVerifier:
    def verify(
        self,
        *,
        goal: str,
        planned_action: PlannedAction,
        before: Observation,
        after: Observation,
        action_result: ActionResult,
    ) -> VerificationResult:
        if not action_result.success:
            return VerificationResult(success=False, summary=action_result.error or action_result.message, should_retry=False)

        after_text = after.visible_text.lower()
        if planned_action.kind == ActionKind.CLICK and "submitted for" in after_text:
            return VerificationResult(success=True, summary="Submission result appeared.", should_retry=False)
        if planned_action.kind == ActionKind.TYPE:
            return VerificationResult(success=True, summary="Typing action completed.", should_retry=False)
        if planned_action.kind == ActionKind.WAIT and "submitted for" in after_text:
            return VerificationResult(success=True, summary="Page settled with submission result.", should_retry=False)
        return VerificationResult(success=True, summary="Action completed.", should_retry=False)
