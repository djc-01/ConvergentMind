from __future__ import annotations

import json
from pathlib import Path

from convergentmind.config import AppConfig
from convergentmind.llm.client import OpenAIResponsesClient
from convergentmind.llm.planner import extract_json_object, summarize_observation
from convergentmind.prompts import VERIFIER_SYSTEM_PROMPT, build_verifier_user_prompt
from convergentmind.schemas import ActionResult, Observation, PlannedAction, VerificationResult


class OpenAIVerifier:
    def __init__(self, client: OpenAIResponsesClient, config: AppConfig) -> None:
        self.client = client
        self.config = config

    def verify(
        self,
        *,
        goal: str,
        planned_action: PlannedAction,
        before: Observation,
        after: Observation,
        action_result: ActionResult,
    ) -> VerificationResult:
        prompt = build_verifier_user_prompt(
            goal=goal,
            planned_action_json=planned_action.model_dump_json(indent=2),
            before_summary=summarize_observation(before),
            after_summary=summarize_observation(after),
            action_result_summary=json.dumps(action_result.model_dump(), ensure_ascii=False, indent=2),
        )
        response = self.client.create_json_response(
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=prompt,
            screenshot_path=Path(after.screenshot_path),
            extra_image_paths=(
                [Path(after.camera_snapshot.frame_path)]
                if after.camera_snapshot and after.camera_snapshot.status == "ok" and Path(after.camera_snapshot.frame_path).exists()
                else None
            ),
        )
        data = extract_json_object(response.output_text)
        return VerificationResult.model_validate(data)
