# Outreach Checklist

This file is the lightweight promotion plan for building the first layer of public project signals around ConvergentMind.

## Initial targets

- 10 to 20 GitHub stars
- 5 to 10 issues or discussions
- 2 to 3 public feedback links
- 3 GitHub releases
- a visible PyPI package page and early download history

## Share sequence

1. Enable GitHub Discussions and post the three drafts from `DISCUSSION_STARTERS.md`.
2. Publish one short launch post on a platform you already use.
3. Publish one short technical post about why browser-only agents are not enough for some tasks.
4. Ask 3 to 5 friends, teammates, or interested builders to try the offline demo and leave one public response each.
5. Convert any recurring feedback into issues, roadmap updates, or release notes.

## Short launch post draft

```md
I open-sourced ConvergentMind, a small local-first research platform for browser-first multimodal agents.

The idea is simple: combine browser state, optional camera input, explicit planning and verification, and replayable artifacts so the agent loop stays inspectable.

It is aimed at people building browser agents, multimodal tooling, or teaching/debugging agent workflows.

Repo: https://github.com/Chocologician/ConvergentMind
```

## Technical post draft

```md
Most browser agents can only see the page. Most vision demos can only describe an image. I wanted a smaller platform that sits in the middle.

ConvergentMind keeps the loop explicit:

observe -> plan -> act -> verify

and lets that loop consume both browser state and camera or video context. The goal is not a giant framework; it is a clean base for experiments, debugging, and replay.

Repo: https://github.com/Chocologician/ConvergentMind
```

## Ask for feedback

Send a short personal note with one concrete ask:

- try the offline demo
- open one issue if something breaks
- reply with one sentence about what felt promising or confusing

Those small public signals are more useful than a vague "please share" request.
