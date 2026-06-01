# ConvergentMind Examples

This folder collects concrete ways to run and extend ConvergentMind.

Before running the demo-page examples below, create a file URL:

```powershell
$demoPath = (Resolve-Path .\tests\fixtures\demo_page.html).Path.Replace('\', '/')
$demoUrl = "file:///$demoPath"
```

## 1. Fastest successful path

Use the bundled demo page, local camera `0`, and the offline planner:

```powershell
py -3.13 -m convergentmind.cli run --goal "Fill the form and submit it." --url $demoUrl --camera-source 0 --offline-demo
```

What you should get:

- a successful run status
- a new `runs/<run-id>/` directory
- browser screenshots for each step
- camera frames for each step
- a `summary.json` file for replay

## 2. Browser-only inspection

Useful when debugging page perception without the camera channel:

```powershell
py -3.13 -m convergentmind.cli inspect --url $demoUrl
```

## 3. Browser + camera inspection

Useful when checking that camera capture is wired correctly:

```powershell
py -3.13 -m convergentmind.cli inspect --url $demoUrl --camera-source 0
```

## 4. Environment diagnosis before online runs

Use this before trying the OpenAI-backed planner:

```powershell
py -3.13 -m convergentmind.cli doctor --camera-source 0
```

What to look for:

- whether a local browser can be found
- whether the camera source is configured
- which model IDs the current provider exposes
- whether your configured model is actually available

## 5. External video stream input

You can replace the camera index with a stream URL or local video file:

```powershell
py -3.13 -m convergentmind.cli inspect --url $demoUrl --camera-source "rtsp://example-camera/live"
```

or:

```powershell
py -3.13 -m convergentmind.cli inspect --url $demoUrl --camera-source "D:/videos/sample.mp4"
```

## 6. Where to extend next

If you want to contribute a meaningful next step, the most natural extension points are:

- `src/convergentmind/camera/stream.py` for richer video ingestion
- `src/convergentmind/llm/planner.py` for better structured planning
- `src/convergentmind/llm/verifier.py` for stronger post-action checks
- `src/convergentmind/runner.py` for memory, retries, and policy logic
