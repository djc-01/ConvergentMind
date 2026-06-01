from __future__ import annotations

from typing import Any

from playwright.sync_api import Page

from convergentmind.schemas import UIElement


EXTRACT_INTERACTIVE_JS = """
(limit) => {
  function isVisible(el) {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style && style.visibility !== 'hidden' && style.display !== 'none' &&
      rect.width > 0 && rect.height > 0;
  }

  function makeSelector(el) {
    if (el.id) return `#${el.id}`;
    if (el.name) return `${el.tagName.toLowerCase()}[name="${el.name}"]`;
    return el.tagName.toLowerCase();
  }

  const nodes = Array.from(document.querySelectorAll(
    'button, a, input, textarea, select, [role], [contenteditable="true"]'
  ));

  return nodes
    .filter(isVisible)
    .slice(0, limit)
    .map((el) => ({
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role'),
      text: (el.innerText || el.textContent || '').trim().slice(0, 120),
      label: el.getAttribute('aria-label') || el.labels?.[0]?.innerText?.trim() || null,
      placeholder: el.getAttribute('placeholder'),
      name: el.getAttribute('name'),
      type: el.getAttribute('type'),
      selector_hint: makeSelector(el),
    }));
}
"""


def extract_interactive_elements(page: Page, *, limit: int = 30) -> list[UIElement]:
    raw_elements: list[dict[str, Any]] = page.evaluate(EXTRACT_INTERACTIVE_JS, limit)
    return [UIElement.model_validate(item) for item in raw_elements]
