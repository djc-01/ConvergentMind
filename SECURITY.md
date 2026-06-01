# Security Policy

## Supported scope

ConvergentMind is a local-first research platform for browser-centered multimodal agent experiments. The current maintenance scope covers:

- browser observation and browser control
- camera or video-stream context capture
- local replay artifacts and diagnostics
- OpenAI-compatible planner and verifier integrations

This repository is not intended for high-risk automation or production safety guarantees.

## High-risk use restrictions

Do not use this project for:

- payments or financial transfers
- account deletion or irreversible user actions
- handling regulated personal data
- physical-world actuation or robotics
- safety-critical or medical decision workflows

The current architecture is designed for experimentation, evaluation, and local debugging, not autonomous execution in sensitive environments.

## Reporting a vulnerability

Please report vulnerabilities privately when possible:

1. Use GitHub's private vulnerability reporting flow if it is enabled for this repository.
2. If private reporting is not available, open a minimal issue without exploit details and clearly mark it as a security concern.

When reporting, include:

- affected command or module
- reproduction steps
- expected impact
- whether credentials, browsing scope, or file access are involved

I will triage the report as quickly as possible, but please note that this is a maintainer-run open source project without a formal response SLA.
