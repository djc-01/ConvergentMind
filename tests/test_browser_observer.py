from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Error, sync_playwright

from convergentmind.browser.observer import BrowserObserver


@pytest.mark.skipif(not Path(__file__).parent.joinpath("fixtures", "demo_page.html").exists(), reason="Fixture missing")
def test_browser_observer_extracts_elements(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "demo_page.html"
    observer = BrowserObserver()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.resolve().as_uri())
            observation = observer.observe(page, screenshot_path=tmp_path / "page.png")
            browser.close()
    except Error as exc:  # pragma: no cover - environment specific
        pytest.skip(f"Playwright browser unavailable: {exc}")

    assert observation.title == "ConvergentMind Demo"
    assert observation.screenshot_path.exists()
    assert any(element.text == "Submit Demo" for element in observation.elements)
    assert "Fill the form" in observation.visible_text
