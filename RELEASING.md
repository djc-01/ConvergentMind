# Releasing ConvergentMind

This repository keeps releases lightweight and explicit. A release should leave the project installable, testable, and easy to evaluate from the README.

## Pre-release checklist

1. Make sure the working tree is clean.
2. Run the test suite:

   ```powershell
   py -3.13 -m pytest -q
   ```

3. Build the distribution artifacts:

   ```powershell
   py -3.13 -m build
   ```

4. Smoke-test the editable install and the offline demo path.
5. Update `README.md`, `CHANGELOG.md`, and `ROADMAP.md` if behavior or direction changed.

## Versioning

ConvergentMind uses practical semantic versioning:

- patch: documentation, packaging, reliability, and small bug fixes
- minor: a user-visible capability or workflow improvement
- major: breaking CLI or schema changes

When preparing a release, keep the version in sync in both places:

- `pyproject.toml`
- `src/convergentmind/__init__.py`

## Build locally

Install release tooling if needed:

```powershell
py -3.13 -m pip install -e ".[dev]"
```

Then build:

```powershell
py -3.13 -m build
```

Artifacts will be created in `dist/`.

## Publish to TestPyPI

```powershell
py -3.13 -m pip install twine
py -3.13 -m twine upload --repository testpypi dist/*
```

Use TestPyPI first when validating metadata or first-time packaging changes.

## Publish to PyPI

```powershell
py -3.13 -m pip install twine
py -3.13 -m twine upload dist/*
```

Make sure the package page shows:

- a clear project description
- working README rendering
- the expected Python version support
- license and project links

## Tag and GitHub Release

1. Create and push a git tag such as `v0.1.0`.
2. Open the GitHub Releases page and create a release from that tag.
3. Use the template below for release notes.

## Release notes template

````md
## Highlights

- ...

## Fixes and maintenance

- ...

## Known limitations

- ...

## Install or upgrade

```bash
pip install --upgrade convergentmind
```
````
