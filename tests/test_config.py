from __future__ import annotations

from pathlib import Path

import pytest

from convergentmind.config import AppConfig


def test_config_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        AppConfig.from_env(require_api_key=True)


def test_config_loads_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.5")
    monkeypatch.setenv("AGENT_MAX_STEPS", "5")
    monkeypatch.setenv("AGENT_MAX_CONSECUTIVE_FAILURES", "2")
    monkeypatch.setenv("AGENT_HEADLESS", "false")
    monkeypatch.setenv("AGENT_ALLOWED_DOMAINS", "example.com,openai.com")
    monkeypatch.setenv("AGENT_CAMERA_SOURCE", "0")
    monkeypatch.setenv("AGENT_CAMERA_WARMUP_SECONDS", "0.5")
    monkeypatch.setenv("AGENT_CAMERA_READ_TIMEOUT_SECONDS", "8.0")

    config = AppConfig.from_env(require_api_key=True)

    assert config.openai_model == "gpt-5.5"
    assert config.max_steps == 5
    assert config.max_consecutive_failures == 2
    assert config.headless is False
    assert config.allowed_domains == ["example.com", "openai.com"]
    assert config.camera_source == "0"
    assert config.camera_warmup_seconds == 0.5
    assert config.camera_read_timeout_seconds == 8.0
    assert isinstance(config.runs_dir, Path)
