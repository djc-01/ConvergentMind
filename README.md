# ConvergentMind

[![CI](https://github.com/Chocologician/ConvergentMind/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Chocologician/ConvergentMind/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/convergentmind.svg)](https://pypi.org/project/convergentmind/)
[![Python](https://img.shields.io/badge/python-3.13%2B-3776AB.svg)](https://github.com/Chocologician/ConvergentMind)
[![License](https://img.shields.io/github/license/Chocologician/ConvergentMind.svg)](LICENSE)

ConvergentMind is a small, hackable, local-first research platform for browser-first multimodal agents. It gives you a clear `observe -> plan -> act -> verify` loop that can combine:

- observe a web page
- observe the outside world through a camera or video stream
- plan the next action
- act inside the browser
- verify whether the action actually helped
- record the full run for replay and debugging

The project is intentionally lightweight, but it is built to be extended, tested, and replayed like a real tool instead of a one-off demo.

## value

ConvergentMind is useful if you are:

- building browser agents that need more than page-only perception
- exploring multimodal planning with browser state plus camera or video context
- teaching or debugging explicit agent loops without hiding the control flow behind a large framework

It focuses on a gap that many agent repos skip: connecting browser-state reasoning with a second "world" channel while keeping the pipeline easy to inspect and replay.

## Why this project exists

Most browser agents can only see inside the page. Most vision demos can only describe an image. ConvergentMind sits in the middle:

- it treats browser state as one perception channel
- it treats camera input as another perception channel
- it keeps the agent loop explicit: observe -> plan -> act -> verify
- it stays small enough to understand and extend

## Why it matters

- It provides a practical base layer between browser-agent tooling and broader multimodal agent research.
- It is a good teaching and experimentation surface for observation, planning, verification, and replay.
- The offline demo path keeps the full workflow reproducible even when model access is unavailable or unstable.

## What works today

- browser observation with screenshot, visible text, and interactive elements
- browser control with `goto`, `click`, `type`, `extract`, and `wait`
- optional camera or external video-stream snapshots per observation step
- OpenAI-compatible planner and verifier integration
- local run logging and replay
- environment diagnostics with `doctor`
- offline demo mode when no usable text model is available
- automatic fallback to local Edge or Chrome when Playwright Chromium is missing

## Current limitations

- the camera channel is snapshot-based, not true temporal video reasoning
- actions are limited to the browser; there is no physical-world actuation
- online planning depends on your configured provider exposing a usable text-capable model
- the current demo focuses on clear architecture and iteration speed over production hardening

## Project status

Stable today:

- local browser observation and action execution
- local replay artifacts for inspection and debugging
- optional camera or stream snapshots per step
- offline demo mode for no-model smoke tests

Next up:

- richer world summaries from camera input
- stronger verification and failure recovery
- better replay and inspection UX

Contributions are especially welcome in tests, docs, diagnostics, replay artifacts, and planner/verifier quality.

## Quick start

Use `py -3.13` on this machine instead of bare `python`. On macOS or Linux, replace `py -3.13` with `python3.13` or your preferred Python launcher.

```powershell
cd path\to\convergentmind
py -3.13 -m pip install -e ".[dev]"
py -3.13 -m playwright install chromium
Copy-Item .env.example .env
```

Minimal `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=
OPENAI_MODEL=
AGENT_CAMERA_SOURCE=0
```

Notes:

- `OPENAI_MODEL` can be filled later when your provider exposes a suitable text model
- if you use an OpenAI-compatible proxy, set `OPENAI_BASE_URL`
- if your provider is not ready yet, use `--offline-demo`

## The three commands to know first

In PowerShell, you can turn the bundled demo page into a `file:///` URL like this:

```powershell
$demoPath = (Resolve-Path .\tests\fixtures\demo_page.html).Path.Replace('\', '/')
$demoUrl = "file:///$demoPath"
```

Inspect a page:

```powershell
py -3.13 -m convergentmind.cli inspect --url $demoUrl
```

Run the full local pipeline with browser + camera + offline planner:

```powershell
py -3.13 -m convergentmind.cli run --goal "Fill the form and submit it." --url $demoUrl --camera-source 0 --offline-demo
```

Check whether your current environment is ready for online model-backed runs:

```powershell
py -3.13 -m convergentmind.cli doctor --camera-source 0
```

## Example run output

Successful offline runs should look roughly like this:

```text
Run finished with status: completed
Run ID: 20260601-224500-demo
Artifacts: runs/20260601-224500-demo
```

Typical artifacts:

```text
runs/<run-id>/
  browser/
  camera/
  steps/
  summary.json
```

Example `summary.json` shape:

```json
{
  "status": "completed",
  "goal": "Fill the form and submit it.",
  "step_count": 4,
  "final_result": "Submitted the form successfully."
}
```

## Repository structure

```text
convergentmind/
  src/convergentmind/
  tests/
  examples/
  .env.example
  .gitignore
  pyproject.toml
  requirements.txt
  README.md
  ROADMAP.md
```

Key modules:

- [cli.py](src/convergentmind/cli.py): command entrypoints
- [runner.py](src/convergentmind/runner.py): main agent loop
- [browser/controller.py](src/convergentmind/browser/controller.py): browser execution
- [browser/observer.py](src/convergentmind/browser/observer.py): browser observation
- [camera/stream.py](src/convergentmind/camera/stream.py): camera/video-stream ingestion
- [llm/planner.py](src/convergentmind/llm/planner.py): next-action planning
- [llm/verifier.py](src/convergentmind/llm/verifier.py): post-action verification
- [logs/recorder.py](src/convergentmind/logs/recorder.py): run artifacts and summaries

## Architecture

1. The browser observer captures page text, page metadata, page screenshot, and interactive elements.
2. The camera stream reader continuously reads a local camera, video file, or network stream.
3. The runner merges both channels into a single `Observation`.
4. The planner chooses the next browser action from the goal, memory, screenshots, and structured state.
5. The browser controller executes the action.
6. The verifier checks whether the page moved closer to the goal.
7. The recorder saves screenshots, camera frames, step JSON, and the final run summary.

## Examples

See [examples/README.md](examples/README.md) for runnable flows and [examples/sample_goals.md](examples/sample_goals.md) for goal ideas.

## Releases and packaging

- install locally with `pip install -e ".[dev]"`
- build release artifacts with `py -3.13 -m build`
- follow [RELEASING.md](RELEASING.md) for TestPyPI, PyPI, and GitHub release steps

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the planned evolution of this project.

## Testing

```powershell
py -3.13 -m pytest -q
```

If Playwright Chromium is not installed, the browser-observer test may be skipped. Runtime fallback to local Edge or Chrome still works.

## Safety notes

- allowed domains are restricted by default to the start URL domain
- camera frames are context only and do not trigger physical-world actions
- this demo should not be used for payments, account deletion, or sensitive real-world operations

## Community

- use GitHub Discussions for questions, feedback, and roadmap ideas
- use Issues for reproducible bugs and scoped feature requests
- see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance
