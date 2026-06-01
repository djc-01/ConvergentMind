from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from openai import OpenAI

from convergentmind.config import AppConfig


class OpenAIClientError(RuntimeError):
    """Raised when the configured OpenAI-compatible endpoint is unavailable or misconfigured."""


class OpenAIResponsesClient:
    def __init__(self, config: AppConfig) -> None:
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIResponsesClient.")
        self.config = config
        client_kwargs = {"api_key": config.openai_api_key}
        if config.openai_base_url:
            client_kwargs["base_url"] = config.openai_base_url
        self.client = OpenAI(**client_kwargs)

    @staticmethod
    def image_to_data_url(path: Path) -> str:
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{payload}"

    def create_json_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        screenshot_path: Path | None = None,
        extra_image_paths: list[Path] | None = None,
        model: str | None = None,
    ) -> Any:
        content: list[dict[str, Any]] = [{"type": "input_text", "text": user_prompt}]
        if screenshot_path is not None:
            content.append(
                {
                    "type": "input_image",
                    "image_url": self.image_to_data_url(screenshot_path),
                }
            )
        for image_path in extra_image_paths or []:
            content.append(
                {
                    "type": "input_image",
                    "image_url": self.image_to_data_url(image_path),
                }
            )
        try:
            return self.client.responses.create(
                model=model or self.config.openai_model,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                    {"role": "user", "content": content},
                ],
                text={"format": {"type": "json_object"}},
            )
        except Exception as exc:
            raise OpenAIClientError(self._format_client_error(exc)) from exc

    def list_model_ids(self) -> list[str]:
        try:
            models = self.client.models.list()
            return sorted(model.id for model in models.data)
        except Exception as exc:
            raise OpenAIClientError(self._format_client_error(exc)) from exc

    def _format_client_error(self, exc: Exception) -> str:
        base = f"OpenAI request failed for model '{self.config.openai_model}'."
        if self.config.openai_base_url:
            base += f" Endpoint: {self.config.openai_base_url}."
        base += f" Original error: {exc}"
        return base
