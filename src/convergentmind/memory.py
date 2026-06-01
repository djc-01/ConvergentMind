from __future__ import annotations

from collections import deque


class ShortTermMemory:
    def __init__(self, max_items: int = 8) -> None:
        self._items: deque[str] = deque(maxlen=max_items)

    def add(self, item: str) -> None:
        if item:
            self._items.append(item)

    def snapshot(self) -> list[str]:
        return list(self._items)
