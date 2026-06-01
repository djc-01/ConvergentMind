from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from convergentmind.schemas import StepRecord, TaskState


class RunRecorder:
    def __init__(self, runs_dir: Path) -> None:
        self.runs_dir = runs_dir

    def create_run(self) -> tuple[str, Path]:
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "steps").mkdir(parents=True, exist_ok=True)
        return run_id, run_dir

    def record_step(self, run_dir: Path, step_record: StepRecord) -> None:
        path = run_dir / "steps" / f"step_{step_record.step_index:02d}.json"
        path.write_text(step_record.model_dump_json(indent=2), encoding="utf-8")

    def write_summary(self, run_dir: Path, payload: dict[str, Any]) -> None:
        path = run_dir / "summary.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def summarize_state(self, run_id: str, run_dir: Path, state: TaskState) -> dict[str, Any]:
        return {
            "run_id": run_id,
            "status": state.status,
            "goal": state.goal,
            "start_url": state.start_url,
            "final_result": state.final_result,
            "consecutive_failures": state.consecutive_failures,
            "steps": [
                {
                    "index": step.step_index,
                    "action": step.planned_action.model_dump(),
                    "result": step.action_result.model_dump(),
                    "verification": step.verification.model_dump() if step.verification else None,
                    "before_screenshot": str(step.before.screenshot_path),
                    "after_screenshot": str(step.after.screenshot_path) if step.after else None,
                    "before_camera_frame": str(step.before.camera_snapshot.frame_path) if step.before.camera_snapshot else None,
                    "after_camera_frame": str(step.after.camera_snapshot.frame_path) if step.after and step.after.camera_snapshot else None,
                }
                for step in state.steps
            ],
            "run_dir": str(run_dir),
        }
