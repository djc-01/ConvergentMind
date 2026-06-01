from __future__ import annotations

import json
from pathlib import Path

from convergentmind.config import AppConfig
from convergentmind.llm.client import OpenAIResponsesClient
from convergentmind.prompts import PLANNER_SYSTEM_PROMPT, build_planner_user_prompt
from convergentmind.schemas import Observation, PlannedAction


def summarize_observation(observation: Observation) -> str:
    elements = [
        {
            "tag": item.tag,
            "role": item.role,
            "text": item.text,
            "label": item.label,
            "placeholder": item.placeholder,
        }
        for item in observation.elements[:12]
    ]
    payload = {
        "url": observation.url,
        "title": observation.title,
        "visible_text": observation.visible_text[:1200],
        "elements": elements,
        "camera_snapshot": observation.camera_snapshot.model_dump(mode="json") if observation.camera_snapshot else None,
        "last_action_result": observation.last_action_result.model_dump(mode="json") if observation.last_action_result else None,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def extract_json_object(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


class OpenAIPlanner:
    def __init__(self, client: OpenAIResponsesClient, config: AppConfig) -> None:
        self.client = client
        self.config = config

    def plan(self, *, goal: str, observation: Observation, memory: list[str]) -> PlannedAction:
        prompt = build_planner_user_prompt(goal=goal, memory=memory, observation_summary=summarize_observation(observation))
        response = self.client.create_json_response(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=prompt,
            screenshot_path=Path(observation.screenshot_path),
            extra_image_paths=(
                [Path(observation.camera_snapshot.frame_path)]
                if observation.camera_snapshot and observation.camera_snapshot.status == "ok" and Path(observation.camera_snapshot.frame_path).exists()
                else None
            ),
        )
        data = extract_json_object(response.output_text)
        return PlannedAction.model_validate(data)
