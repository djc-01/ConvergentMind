from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from convergentmind.browser.extractor import extract_interactive_elements
from convergentmind.schemas import ActionResult, Observation


class BrowserObserver:
    def observe(
        self,
        page: Page,
        *,
        screenshot_path: Path,
        last_action_result: ActionResult | None = None,
    ) -> Observation:
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)
        elements = extract_interactive_elements(page)
        visible_text = page.locator("body").inner_text(timeout=5000).strip()
        return Observation(
            url=page.url,
            title=page.title(),
            screenshot_path=screenshot_path,
            visible_text=visible_text[:4000],
            elements=elements,
            last_action_result=last_action_result,
        )
