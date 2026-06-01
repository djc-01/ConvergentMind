from __future__ import annotations

from pathlib import Path

from convergentmind.llm.planner import extract_json_object, summarize_observation
from convergentmind.schemas import ActionKind, CameraSnapshot, Observation, PlannedAction


def test_extract_json_object_from_code_fence() -> None:
    raw = """```json
{"kind":"click","reason":"submit the form","target_text":"Submit Demo"}
```"""
    payload = extract_json_object(raw)
    action = PlannedAction.model_validate(payload)
    assert action.kind == ActionKind.CLICK
    assert action.target_text == "Submit Demo"


def test_summarize_observation_includes_camera_snapshot() -> None:
    observation = Observation(
        url="https://example.com",
        title="Camera Demo",
        screenshot_path=Path("browser.png"),
        visible_text="Visible text",
        elements=[],
        camera_snapshot=CameraSnapshot(
            source="0",
            frame_path=Path("camera.png"),
            timestamp="2026-06-01T10:00:00Z",
            width=640,
            height=480,
            status="ok",
        ),
    )
    summary = summarize_observation(observation)
    assert "camera_snapshot" in summary
    assert "camera.png" in summary
