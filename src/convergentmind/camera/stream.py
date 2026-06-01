from __future__ import annotations

import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2

from convergentmind.schemas import CameraSnapshot


def normalize_camera_source(source: str | None) -> int | str | None:
    if source is None:
        return None
    stripped = source.strip()
    if stripped.isdigit():
        return int(stripped)
    return stripped


class CameraStream:
    def __init__(
        self,
        source: str,
        *,
        warmup_seconds: float = 1.0,
        read_timeout_seconds: float = 5.0,
    ) -> None:
        self.source = source
        self.normalized_source = normalize_camera_source(source)
        self.warmup_seconds = warmup_seconds
        self.read_timeout_seconds = read_timeout_seconds
        self._capture: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._latest_frame: Any | None = None
        self._latest_timestamp: datetime | None = None
        self._last_error: str | None = None

    def start(self) -> None:
        self._capture = cv2.VideoCapture(self.normalized_source)
        if not self._capture.isOpened():
            raise RuntimeError(f"Unable to open camera source: {self.source}")
        self._thread = threading.Thread(target=self._reader_loop, name="camera-stream-reader", daemon=True)
        self._thread.start()
        deadline = time.time() + self.read_timeout_seconds
        while time.time() < deadline:
            with self._lock:
                if self._latest_frame is not None:
                    break
                last_error = self._last_error
            if last_error:
                raise RuntimeError(last_error)
            time.sleep(0.05)
        else:
            raise RuntimeError(f"Timed out waiting for frames from camera source: {self.source}")
        if self.warmup_seconds > 0:
            time.sleep(self.warmup_seconds)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._capture is not None:
            self._capture.release()
        self._thread = None
        self._capture = None

    def capture_snapshot(self, output_path: Path) -> CameraSnapshot:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            if self._latest_frame is None or self._latest_timestamp is None:
                raise RuntimeError(self._last_error or "Camera frame is not available yet.")
            frame = self._latest_frame.copy()
            timestamp = self._latest_timestamp
        success = cv2.imwrite(str(output_path), frame)
        if not success:
            raise RuntimeError(f"Failed to write camera frame to {output_path}")
        height, width = frame.shape[:2]
        return CameraSnapshot(
            source=str(self.source),
            frame_path=output_path,
            timestamp=timestamp.astimezone(UTC).isoformat(),
            width=width,
            height=height,
            status="ok",
        )

    def _reader_loop(self) -> None:
        assert self._capture is not None
        while not self._stop_event.is_set():
            ok, frame = self._capture.read()
            if ok:
                with self._lock:
                    self._latest_frame = frame
                    self._latest_timestamp = datetime.now(UTC)
                    self._last_error = None
            else:
                with self._lock:
                    self._last_error = f"Failed to read frame from camera source: {self.source}"
                time.sleep(0.05)
