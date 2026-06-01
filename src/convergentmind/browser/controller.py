from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Error, Locator, Page, Playwright, sync_playwright

from convergentmind.schemas import ActionResult, PlannedAction


ROLE_MAP = {
    "button": "button",
    "textbox": "textbox",
    "link": "link",
    "checkbox": "checkbox",
    "combobox": "combobox",
    "searchbox": "searchbox",
}


class BrowserController(AbstractContextManager["BrowserController"]):
    def __init__(
        self,
        *,
        headless: bool = True,
        browser_executable: str | None = None,
        browser_channel: str | None = None,
    ) -> None:
        self.headless = headless
        self.browser_executable = browser_executable
        self.browser_channel = browser_channel
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    def __enter__(self) -> "BrowserController":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    def start(self) -> None:
        self._playwright = sync_playwright().start()
        launch_options: dict[str, object] = {"headless": self.headless}
        if self.browser_executable:
            launch_options["executable_path"] = self.browser_executable
        elif self.browser_channel:
            launch_options["channel"] = self.browser_channel

        try:
            self._browser = self._playwright.chromium.launch(**launch_options)
        except Error as exc:
            fallback = discover_system_browser()
            if fallback is None:
                raise
            fallback_options: dict[str, object] = {"headless": self.headless, "executable_path": fallback}
            self._browser = self._playwright.chromium.launch(**fallback_options)
        self._context = self._browser.new_context(viewport={"width": 1440, "height": 1200})
        self.page = self._context.new_page()

    def stop(self) -> None:
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self.page = None
        self._context = None
        self._browser = None
        self._playwright = None

    def goto(self, url: str) -> ActionResult:
        assert self.page is not None
        self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
        return ActionResult(success=True, message=f"Navigated to {url}")

    def execute(self, action: PlannedAction) -> ActionResult:
        assert self.page is not None
        try:
            if action.kind.value == "goto":
                return self.goto(action.url or "")
            if action.kind.value == "click":
                locator = self._resolve_locator(action)
                locator.first.click(timeout=10000)
                return ActionResult(success=True, message="Click executed")
            if action.kind.value == "type":
                locator = self._resolve_locator(action)
                locator.first.fill(action.text or "", timeout=10000)
                return ActionResult(success=True, message="Text entered", data={"text": action.text})
            if action.kind.value == "wait":
                self.page.wait_for_timeout(action.duration_ms or 500)
                return ActionResult(success=True, message=f"Waited {action.duration_ms} ms")
            if action.kind.value == "extract":
                text = self.page.locator("body").inner_text(timeout=5000)
                return ActionResult(success=True, message="Text extracted", data={"text": text[:4000], "query": action.query})
            if action.kind.value == "done":
                return ActionResult(success=True, message=action.final_message or "Task completed")
            if action.kind.value == "fail":
                return ActionResult(success=False, message=action.final_message or "Task failed", error=action.final_message)
        except Error as exc:
            return ActionResult(success=False, message="Browser action failed", error=str(exc))
        return ActionResult(success=False, message="Unsupported action", error=action.kind.value)

    def _resolve_locator(self, action: PlannedAction) -> Locator:
        assert self.page is not None
        if action.selector:
            return self.page.locator(action.selector)
        if action.label:
            return self.page.get_by_label(action.label, exact=False)
        if action.role:
            role = ROLE_MAP.get(action.role.lower())
            if role:
                return self.page.get_by_role(role, name=action.target_text, exact=False)
        if action.target_text:
            return self.page.get_by_text(action.target_text, exact=False)
        if action.nth is not None:
            return self.page.locator("button, a, input, textarea, select").nth(action.nth)
        raise ValueError("Action does not contain a usable locator")


def discover_system_browser() -> str | None:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None
