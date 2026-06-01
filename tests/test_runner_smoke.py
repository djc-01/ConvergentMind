from __future__ import annotations

from pathlib import Path

from convergentmind.config import AppConfig
from convergentmind.runner import AgentRunner
from convergentmind.schemas import ActionResult, CameraSnapshot, Observation, PlannedAction, VerificationResult


class FakePage:
    def __init__(self) -> None:
        self.url = "https://example.com"

    def title(self) -> str:
        return "Fake Page"


class FakeController:
    def __init__(
        self,
        *,
        headless: bool = True,
        browser_executable: str | None = None,
        browser_channel: str | None = None,
    ) -> None:
        self.page = FakePage()
        self.actions: list[str] = []

    def __enter__(self) -> "FakeController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def goto(self, url: str) -> ActionResult:
        self.page.url = url
        self.actions.append(f"goto:{url}")
        return ActionResult(success=True, message=f"goto {url}")

    def execute(self, action: PlannedAction) -> ActionResult:
        self.actions.append(action.kind.value)
        return ActionResult(success=action.kind.value != "fail", message=action.kind.value)


class FakeObserver:
    def observe(self, page, *, screenshot_path: Path, last_action_result=None) -> Observation:
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_text("fake", encoding="utf-8")
        return Observation(
            url=page.url,
            title=page.title(),
            screenshot_path=screenshot_path,
            visible_text="Fake page with form and submit button",
            elements=[],
            last_action_result=last_action_result,
        )


class FakePlanner:
    def __init__(self) -> None:
        self._actions = [
            PlannedAction(kind="type", reason="fill name", label="Name", text="Ada"),
            PlannedAction(kind="click", reason="submit", target_text="Submit Demo"),
            PlannedAction(kind="done", reason="finished", final_message="Task completed"),
        ]

    def plan(self, *, goal: str, observation: Observation, memory: list[str]) -> PlannedAction:
        return self._actions.pop(0)


class FakeVerifier:
    def verify(self, **kwargs) -> VerificationResult:
        return VerificationResult(success=True, summary="Looks good", should_retry=False)


def test_runner_smoke(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("convergentmind.runner.BrowserController", FakeController)

    config = AppConfig(
        openai_api_key="sk-test",
        project_root=tmp_path,
        runs_dir=tmp_path / "runs",
        allowed_domains=["example.com"],
    )
    runner = AgentRunner(config=config, planner=FakePlanner(), verifier=FakeVerifier())
    runner.observer = FakeObserver()
    result = runner.run(goal="Submit the fake form", start_url="https://example.com")

    assert result.status == "completed"
    assert result.final_result == "Task completed"
    summary = (result.run_dir / "summary.json").read_text(encoding="utf-8")
    assert "Task completed" in summary


class FakeCameraStream:
    def __init__(self, source: str, *, warmup_seconds: float = 1.0, read_timeout_seconds: float = 5.0) -> None:
        self.source = source
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def capture_snapshot(self, output_path: Path) -> CameraSnapshot:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("camera", encoding="utf-8")
        return CameraSnapshot(
            source=str(self.source),
            frame_path=output_path,
            timestamp="2026-06-01T10:00:00Z",
            width=640,
            height=480,
            status="ok",
        )


def test_runner_with_camera_stream(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("convergentmind.runner.BrowserController", FakeController)
    monkeypatch.setattr("convergentmind.runner.CameraStream", FakeCameraStream)

    config = AppConfig(
        openai_api_key="sk-test",
        project_root=tmp_path,
        runs_dir=tmp_path / "runs",
        allowed_domains=["example.com"],
        camera_source="0",
    )
    runner = AgentRunner(config=config, planner=FakePlanner(), verifier=FakeVerifier())
    runner.observer = FakeObserver()
    result = runner.run(goal="Submit the fake form", start_url="https://example.com")

    summary = (result.run_dir / "summary.json").read_text(encoding="utf-8")
    assert "before_camera_frame" in summary
    assert "before_camera.png" in summary
