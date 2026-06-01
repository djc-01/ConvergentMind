from __future__ import annotations

from convergentmind.camera.stream import normalize_camera_source


def test_normalize_camera_source_supports_numeric_index() -> None:
    assert normalize_camera_source("0") == 0
    assert normalize_camera_source("12") == 12


def test_normalize_camera_source_preserves_urls_and_paths() -> None:
    assert normalize_camera_source("rtsp://camera/live") == "rtsp://camera/live"
    assert normalize_camera_source(r"C:\videos\sample.mp4") == r"C:\videos\sample.mp4"
