# AGENTS.md — OutSystems projects

<!-- Drop this file (or append it) at the root of any repository or workspace that holds OutSystems work.
     It is read by Codex, Jules, Aider, Claude Code, Gemini CLI and other agents that honour AGENTS.md. -->

## OutSystems development standards
This workspace follows the **outsystems-architecture** skill. If the folder is not in this repository, set the path to where it is installed.

- Entry point: `outsystems-architecture/SKILL.md`. Read it before any OutSystems design, build or review task.
- Always-on rules: `outsystems-architecture/adapters/core-rules.md`.
- Details on demand: `outsystems-architecture/references/` (architecture canvas, module standard, data and logic, UI, integration and caching, performance, security, audit, scale, lessons learned, Service Studio MCP).
- Reviews: `outsystems-architecture/references/review-checklist.md`. Cite rule IDs.
- Dependency validation: `python outsystems-architecture/scripts/validate_architecture.py deps.json --strict`.
- Deliverables: `outsystems-architecture/templates/`.

Project-specific architecture decisions (if any) are recorded here and override the house standard:
- <none yet>
