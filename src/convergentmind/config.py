from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-5.4-mini"
    max_steps: int = Field(default=8, ge=1, le=50)
    max_consecutive_failures: int = Field(default=3, ge=1, le=10)
    headless: bool = True
    allowed_domains: list[str] = Field(default_factory=list)
    browser_executable: str | None = None
    browser_channel: str | None = None
    camera_source: str | None = None
    camera_warmup_seconds: float = Field(default=1.0, ge=0.0, le=10.0)
    camera_read_timeout_seconds: float = Field(default=5.0, ge=0.1, le=30.0)
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    runs_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "runs")

    @classmethod
    def from_env(
        cls,
        *,
        require_api_key: bool = True,
        start_url: str | None = None,
        env_file: str | os.PathLike[str] | None = None,
    ) -> "AppConfig":
        load_dotenv(dotenv_path=env_file)
        config = cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            max_steps=int(os.getenv("AGENT_MAX_STEPS", "8")),
            max_consecutive_failures=int(os.getenv("AGENT_MAX_CONSECUTIVE_FAILURES", "3")),
            headless=_parse_bool(os.getenv("AGENT_HEADLESS"), True),
            allowed_domains=_parse_csv(os.getenv("AGENT_ALLOWED_DOMAINS")),
            browser_executable=os.getenv("AGENT_BROWSER_EXECUTABLE") or None,
            browser_channel=os.getenv("AGENT_BROWSER_CHANNEL") or None,
            camera_source=os.getenv("AGENT_CAMERA_SOURCE") or None,
            camera_warmup_seconds=float(os.getenv("AGENT_CAMERA_WARMUP_SECONDS", "1.0")),
            camera_read_timeout_seconds=float(os.getenv("AGENT_CAMERA_READ_TIMEOUT_SECONDS", "5.0")),
        )
        if start_url and not config.allowed_domains:
            domain = domain_from_url(start_url)
            if domain:
                config.allowed_domains = [domain]
        if require_api_key and not config.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. Copy .env.example to .env and set a valid key before running the agent."
            )
        config.runs_dir.mkdir(parents=True, exist_ok=True)
        return config

    def with_overrides(
        self,
        *,
        camera_source: str | None = None,
        browser_executable: str | None = None,
        browser_channel: str | None = None,
    ) -> "AppConfig":
        updated = self.model_copy(deep=True)
        if camera_source is not None:
            updated.camera_source = camera_source
        if browser_executable is not None:
            updated.browser_executable = browser_executable
        if browser_channel is not None:
            updated.browser_channel = browser_channel
        updated.runs_dir.mkdir(parents=True, exist_ok=True)
        return updated


def domain_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    return parsed.hostname


def is_url_allowed(url: str, allowed_domains: Iterable[str]) -> bool:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return True
    domain = parsed.hostname
    if not domain:
        return False
    normalized = {item.lower() for item in allowed_domains}
    return not normalized or domain.lower() in normalized
