from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from convergentmind.browser.controller import BrowserController
from convergentmind.browser.observer import BrowserObserver
from convergentmind.camera.observer import CameraObserver
from convergentmind.camera.stream import CameraStream
from convergentmind.config import AppConfig, is_url_allowed
from convergentmind.logs.recorder import RunRecorder
from convergentmind.memory import ShortTermMemory
from convergentmind.schemas import ActionResult, ActionKind, CameraSnapshot, Observation, StepRecord, TaskState


@dataclass
class RunResult:
    run_id: str
    run_dir: Path
    status: str
    final_result: str | None


class AgentRunner:
    def __init__(self, *, config: AppConfig, planner, verifier) -> None:
        self.config = config
        self.planner = planner
        self.verifier = verifier
        self.recorder = RunRecorder(config.runs_dir)
        self.observer = BrowserObserver()
        self.camera_observer: CameraObserver | None = None
        self.memory = ShortTermMemory()

    def inspect(self, url: str) -> tuple[Observation, str, Path]:
        run_id, run_dir = self.recorder.create_run()
        camera_stream = self._start_camera_if_needed()
        try:
            with BrowserController(
                headless=self.config.headless,
                browser_executable=self.config.browser_executable,
                browser_channel=self.config.browser_channel,
            ) as controller:
                controller.goto(url)
                observation = self._observe(
                    controller,
                    run_dir=run_dir,
                    screenshot_name="inspect.png",
                    camera_name="inspect_camera.png",
                )
            return observation, run_id, run_dir
        finally:
            self._stop_camera(camera_stream)

    def run(self, *, goal: str, start_url: str) -> RunResult:
        if self.planner is None or self.verifier is None:
            raise ValueError("Planner and verifier are required for run()")
        state = TaskState(goal=goal, start_url=start_url)
        run_id, run_dir = self.recorder.create_run()
        last_action_result: ActionResult | None = None

        camera_stream = self._start_camera_if_needed()
        try:
            with BrowserController(
                headless=self.config.headless,
                browser_executable=self.config.browser_executable,
                browser_channel=self.config.browser_channel,
            ) as controller:
                initial_result = controller.goto(start_url)
                last_action_result = initial_result
                self.memory.add(f"Opened start URL: {start_url}")
                if self.config.camera_source:
                    self.memory.add(f"Camera source enabled: {self.config.camera_source}")

                for step_index in range(self.config.max_steps):
                    before = self._observe(
                        controller,
                        run_dir=run_dir,
                        screenshot_name=f"steps/step_{step_index:02d}_before.png",
                        camera_name=f"steps/step_{step_index:02d}_before_camera.png",
                        last_action_result=last_action_result,
                    )

                    action = self.planner.plan(goal=goal, observation=before, memory=self.memory.snapshot())
                    if action.kind == ActionKind.GOTO and action.url and not is_url_allowed(action.url, self.config.allowed_domains):
                        action_result = ActionResult(
                            success=False,
                            message="Blocked navigation to non-allowed domain",
                            error=action.url,
                        )
                        verification = None
                        after = before
                    elif action.kind in {ActionKind.DONE, ActionKind.FAIL}:
                        action_result = controller.execute(action)
                        verification = None
                        after = before
                    else:
                        action_result = controller.execute(action)
                        after = self._observe(
                            controller,
                            run_dir=run_dir,
                            screenshot_name=f"steps/step_{step_index:02d}_after.png",
                            camera_name=f"steps/step_{step_index:02d}_after_camera.png",
                            last_action_result=action_result,
                        )
                        verification = self.verifier.verify(
                            goal=goal,
                            planned_action=action,
                            before=before,
                            after=after,
                            action_result=action_result,
                        )

                    record = StepRecord(
                        step_index=step_index,
                        planned_action=action,
                        before=before,
                        after=after,
                        action_result=action_result,
                        verification=verification,
                    )
                    state.steps.append(record)
                    self.recorder.record_step(run_dir, record)

                    memory_line = f"Step {step_index}: {action.kind.value} -> {action_result.message}"
                    if verification:
                        memory_line += f" | verify: {verification.summary}"
                    self.memory.add(memory_line)
                    last_action_result = action_result

                    if action.kind == ActionKind.DONE and action_result.success:
                        state.status = "completed"
                        state.final_result = action.final_message
                        break
                    if action.kind == ActionKind.FAIL:
                        state.status = "failed"
                        state.final_result = action.final_message
                        break

                    if action_result.success and verification and verification.success:
                        state.consecutive_failures = 0
                    else:
                        state.consecutive_failures += 1

                    if state.consecutive_failures >= self.config.max_consecutive_failures:
                        state.status = "failed"
                        state.final_result = "Stopped after too many consecutive failures."
                        break
                else:
                    state.status = "failed"
                    state.final_result = "Stopped after reaching the maximum step count."
        finally:
            self._stop_camera(camera_stream)

        state.short_term_memory = self.memory.snapshot()
        summary = self.recorder.summarize_state(run_id, run_dir, state)
        self.recorder.write_summary(run_dir, summary)
        return RunResult(run_id=run_id, run_dir=run_dir, status=state.status, final_result=state.final_result)

    def _start_camera_if_needed(self) -> CameraStream | None:
        if not self.config.camera_source:
            self.camera_observer = None
            return None
        stream = CameraStream(
            self.config.camera_source,
            warmup_seconds=self.config.camera_warmup_seconds,
            read_timeout_seconds=self.config.camera_read_timeout_seconds,
        )
        stream.start()
        self.camera_observer = CameraObserver(stream)
        return stream

    def _stop_camera(self, stream: CameraStream | None) -> None:
        if stream is not None:
            stream.stop()
        self.camera_observer = None

    def _observe(
        self,
        controller: BrowserController,
        *,
        run_dir: Path,
        screenshot_name: str,
        camera_name: str,
        last_action_result: ActionResult | None = None,
    ) -> Observation:
        observation = self.observer.observe(
            controller.page,
            screenshot_path=run_dir / screenshot_name,
            last_action_result=last_action_result,
        )
        if self.camera_observer is None:
            return observation
        try:
            camera_snapshot = self.camera_observer.capture(output_path=run_dir / camera_name)
        except Exception as exc:
            camera_snapshot = CameraSnapshot(
                source=str(self.config.camera_source),
                frame_path=run_dir / camera_name,
                timestamp=datetime.now(UTC).isoformat(),
                width=0,
                height=0,
                status="unavailable",
                note=str(exc),
            )
        return observation.model_copy(update={"camera_snapshot": camera_snapshot})
