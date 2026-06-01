from __future__ import annotations

import pytest
from pydantic import ValidationError

from convergentmind.schemas import PlannedAction


def test_invalid_click_without_locator_fails() -> None:
    with pytest.raises(ValidationError):
        PlannedAction(kind="click", reason="Need to click submit")


def test_type_requires_text() -> None:
    with pytest.raises(ValidationError):
        PlannedAction(kind="type", reason="Fill the box", label="Name")


def test_wait_requires_duration() -> None:
    with pytest.raises(ValidationError):
        PlannedAction(kind="wait", reason="Wait for page")


def test_done_requires_message() -> None:
    with pytest.raises(ValidationError):
        PlannedAction(kind="done", reason="All finished")
