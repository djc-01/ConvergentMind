from __future__ import annotations

from pathlib import Path

from convergentmind.camera.stream import CameraStream
from convergentmind.schemas import CameraSnapshot


class CameraObserver:
    def __init__(self, stream: CameraStream) -> None:
        self.stream = stream

    def capture(self, *, output_path: Path) -> CameraSnapshot:
        return self.stream.capture_snapshot(output_path)
