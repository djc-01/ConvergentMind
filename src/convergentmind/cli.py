from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from convergentmind.browser.controller import discover_system_browser
from convergentmind.config import AppConfig
from convergentmind.llm.client import OpenAIClientError, OpenAIResponsesClient
from convergentmind.llm.planner import OpenAIPlanner
from convergentmind.llm.verifier import OpenAIVerifier
from convergentmind.local_demo import DemoPlanner, DemoVerifier
from convergentmind.runner import AgentRunner

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ConvergentMind multimodal agent prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the agent loop")
    run_parser.add_argument("--goal", required=True)
    run_parser.add_argument("--url", required=True)
    run_parser.add_argument("--camera-source", help="Camera index, file path, or stream URL")
    run_parser.add_argument("--offline-demo", action="store_true", help="Use a built-in local planner/verifier instead of OpenAI")

    inspect_parser = subparsers.add_parser("inspect", help="Capture a single observation")
    inspect_parser.add_argument("--url", required=True)
    inspect_parser.add_argument("--camera-source", help="Camera index, file path, or stream URL")

    replay_parser = subparsers.add_parser("replay", help="Replay a prior run summary")
    replay_parser.add_argument("--run-id", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check local environment and OpenAI endpoint status")
    doctor_parser.add_argument("--camera-source", help="Optional camera index, file path, or stream URL")

    return parser


def command_run(goal: str, url: str, camera_source: str | None = None, offline_demo: bool = False) -> int:
    config = AppConfig.from_env(require_api_key=not offline_demo, start_url=url).with_overrides(camera_source=camera_source)
    try:
        if offline_demo:
            planner = DemoPlanner()
            verifier = DemoVerifier()
        else:
            client = OpenAIResponsesClient(config)
            planner = OpenAIPlanner(client, config)
            verifier = OpenAIVerifier(client, config)
        runner = AgentRunner(config=config, planner=planner, verifier=verifier)
        result = runner.run(goal=goal, start_url=url)
    except OpenAIClientError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("Tip: run `convergentmind doctor` to inspect model availability, or add `--offline-demo` to test the local pipeline.")
        return 2

    status = "[green]completed[/green]" if result.status == "completed" else "[red]failed[/red]"
    console.print(f"Run finished with status: {status}")
    console.print(f"Run ID: {result.run_id}")
    if result.final_result:
        console.print(result.final_result)
    if result.run_dir:
        console.print(f"Artifacts: {result.run_dir}")
    return 0 if result.status == "completed" else 1


def command_inspect(url: str, camera_source: str | None = None) -> int:
    config = AppConfig.from_env(require_api_key=False, start_url=url).with_overrides(camera_source=camera_source)
    runner = AgentRunner(config=config, planner=None, verifier=None)
    observation, run_id, run_dir = runner.inspect(url)
    console.print(f"Run ID: {run_id}")
    console.print(f"Artifacts: {run_dir}")
    table = Table(title="Observation")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("URL", observation.url)
    table.add_row("Title", observation.title)
    table.add_row("Screenshot", str(observation.screenshot_path))
    table.add_row("Visible text", observation.visible_text[:500])
    table.add_row("Elements", str(len(observation.elements)))
    table.add_row("Camera", str(observation.camera_snapshot.frame_path) if observation.camera_snapshot else "disabled")
    console.print(table)
    return 0


def command_replay(run_id: str) -> int:
    config = AppConfig.from_env(require_api_key=False)
    summary_path = config.runs_dir / run_id / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Run summary not found: {summary_path}")
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    console.print_json(data=payload)
    return 0


def command_doctor(camera_source: str | None = None) -> int:
    config = AppConfig.from_env(require_api_key=False).with_overrides(camera_source=camera_source)
    discovered_browser = config.browser_executable or discover_system_browser()
    table = Table(title="ConvergentMind Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    table.add_row("Python package", "ok", "convergentmind import path is available")
    table.add_row(
        "Browser fallback",
        "ok" if discovered_browser or config.browser_channel else "warn",
        config.browser_executable or config.browser_channel or discovered_browser or "No local Edge/Chrome discovered",
    )
    table.add_row("Camera source", "configured" if config.camera_source else "disabled", config.camera_source or "No camera source configured")
    table.add_row("OpenAI base URL", "set" if config.openai_base_url else "default", config.openai_base_url or "Official default")
    table.add_row("OpenAI model", "configured", config.openai_model)

    if config.openai_api_key:
        try:
            client = OpenAIResponsesClient(config)
            model_ids = client.list_model_ids()
            table.add_row("Model listing", "ok", ", ".join(model_ids[:10]) if model_ids else "No models returned")
            if config.openai_model not in model_ids:
                table.add_row("Model availability", "warn", f"Configured model '{config.openai_model}' not present in listed models")
            else:
                table.add_row("Model availability", "ok", f"Configured model '{config.openai_model}' is listed")
        except OpenAIClientError as exc:
            table.add_row("Model listing", "error", str(exc))
    else:
        table.add_row("Model listing", "skipped", "OPENAI_API_KEY is not set")

    console.print(table)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        return command_run(goal=args.goal, url=args.url, camera_source=args.camera_source, offline_demo=args.offline_demo)
    if args.command == "inspect":
        return command_inspect(url=args.url, camera_source=args.camera_source)
    if args.command == "replay":
        return command_replay(run_id=args.run_id)
    if args.command == "doctor":
        return command_doctor(camera_source=args.camera_source)
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
