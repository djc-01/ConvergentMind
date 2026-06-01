# ConvergentMind Roadmap

This project is still early. The current codebase proves out the multimodal loop and the developer ergonomics around it. The next goal is to turn that loop into a stronger research and prototyping platform.

## Guiding direction

ConvergentMind is moving toward an agent that can:

- perceive both browser state and the physical environment
- reason over multiple time steps instead of isolated snapshots
- act safely under explicit constraints
- expose enough structure that new tools and agent roles can be added without rewriting the core loop

## Phase 1: solidify the current prototype

Status: mostly done

Focus:

- keep the browser + camera + logging pipeline stable
- improve provider diagnostics and error messages
- keep the offline demo path healthy so the repo remains runnable without external model access
- make the repository friendlier to contributors

Expected outcomes:

- reproducible setup
- predictable CLI behavior
- clear documentation of known limits

## Phase 2: better world understanding

Status: next

Focus:

- add a `world_summary` step that turns raw camera frames into stable text or structured scene state
- support multiple recent frames instead of a single latest-frame snapshot
- track scene changes over time
- let planner and verifier consume both raw images and structured world state

Expected outcomes:

- less brittle prompts
- better explainability
- easier debugging of "why did the agent think that?" failures

## Phase 3: stronger agent architecture

Status: planned

Focus:

- split responsibilities between planner, verifier, and world-model specialist agents
- add richer short-term and episodic memory
- introduce stricter action policies and approval hooks
- add more explicit action schemas and failure recovery behavior

Expected outcomes:

- more reliable loops
- clearer traces
- safer experimentation with larger tasks

## Phase 4: better human interface

Status: planned

Focus:

- add a lightweight replay UI
- show browser screenshots and camera frames side by side
- add step-by-step timeline inspection
- expose useful artifacts for demos, debugging, and reports

Expected outcomes:

- easier iteration
- better collaboration
- more compelling demos

## Phase 5: beyond browser-only execution

Status: later

Focus:

- optional desktop automation
- optional physical-world integration points
- better bridging between what the camera sees and what tools can do

Expected outcomes:

- a fuller multimodal agent stack
- cleaner extension path toward real embodied workflows

## Non-goals for now

- production-grade secret handling
- autonomous high-risk real-world actions
- general-purpose robotics
- large-scale orchestration infrastructure

The immediate priority is still a reliable, understandable, local-first prototype.
