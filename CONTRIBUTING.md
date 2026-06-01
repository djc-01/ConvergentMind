# Contributing to ConvergentMind

Thanks for considering a contribution.

This project is still an early prototype, so the most valuable contributions are the ones that improve clarity, reliability, and extensibility without making the codebase much heavier.

## Good first contribution areas

- improve documentation and examples
- tighten tests around existing behavior
- improve logging, diagnostics, and replay artifacts
- make camera, browser, or planner integrations more robust
- improve safety guardrails and failure handling

## Development setup

```powershell
cd path\to\convergentmind
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pip install -e .
```

If you want to run Playwright-backed browser checks:

```powershell
py -3.13 -m playwright install chromium
```

## Before opening a PR

- run `py -3.13 -m pytest -q`
- keep changes focused and easy to review
- update README, examples, or roadmap when the change affects project behavior or direction
- prefer small, composable improvements over large rewrites

## Style expectations

- keep the code readable and explicit
- prefer small modules with clear responsibilities
- avoid introducing complexity unless it unlocks a clear capability
- preserve the current "prototype, but clean" character of the repo

## Scope guidance

Changes are especially welcome when they move the project toward:

- better multimodal observation
- better verification and safety
- better modularity between sensing, planning, and acting
- better developer experience

If you plan a larger architectural change, it is helpful to open an issue or a short design note first so the direction can be discussed before implementation.
