# OutSystems-Architecture

[![CI](https://github.com/MohamedReda2015/outsystems-architecture/actions/workflows/ci.yml/badge.svg)](https://github.com/MohamedReda2015/outsystems-architecture/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![OutSystems 11](https://img.shields.io/badge/OutSystems-11-red)
![Agent independent](https://img.shields.io/badge/agents-Claude%20%7C%20Copilot%20%7C%20Cursor%20%7C%20Codex%20%7C%20any-6f42c1)

**An agent skill that teaches AI coding agents, and people, to design, build, secure, deploy and review OutSystems 11 applications the way a senior OutSystems architect would.**

It packages the official **Architecture Canvas** (3 layers), a strict **Front_End → CW → BL → CS** module pattern, Reactive/Mobile **security rules**, integration and caching patterns, the official **Code Quality** (formerly AI Mentor Studio) pattern catalogue, **LifeTime SOPs**, and lessons learned from real projects. Each rule has a stable ID and a severity, so any agent can enforce it in reviews.

It is plain Markdown plus a small dependency validator in Python *or* Node, so it works with Claude (Code, Desktop, API), GitHub Copilot, Cursor, Codex, Gemini CLI, Aider, or your own LLM agents.


---

## Contents
- [What you get](#what-you-get)
- [Install](#install)
- [Use it](#use-it)
- [Repository layout](#repository-layout)
- [Architecture validator](#architecture-validator)
- [Rule IDs and severities](#rule-ids-and-severities)
- [Versioning and releases](#versioning-and-releases)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

## What you get
| Area | Highlights |
|---|---|
| Architecture | End-User / Core / Foundation layers; no upward, side or cyclic references; Core sublayers; 4 app-composition rules; theme isolation; domains and multi-team mobile |
| House module standard | `<App>_CS` (read-only entities + CRUD wrappers), `<App>_BL` (Structures, thin Service Actions, use-case writes), `<App>_CW` (blocks + events), `<App>_Front_End` (screens only); folders and naming |
| Security | Reactive endpoint threat model, custom roles (no Anonymous or Registered), server-side identity, no mass assignment, Is Secret site properties, SQL, HTML and upload safety, multi-tenancy |
| Data and logic | Service vs Server Action semantics, transactions, soft delete, queries, exceptions, timers (wake pattern), configuration, flow style |
| Performance | Official top-10, Code Quality performance patterns, Reactive data fetching, module health signals |
| Integration | `_IS` wrapper canvas, cold/hot/distributed caching, sync patterns, API versioning |
| Quality and SOP | Code Quality catalogue mapped to fixes, Definition of Done, code review, deployment, hotfix, BDD testing, CI/CD |
| Tooling | Dependency validator (Python and Node, identical output), consistency checker, review and blueprint templates |

## Install
The repository root **is** the skill: `SKILL.md` sits at the top level.

**Claude Code**: for all projects:
```bash
git clone https://github.com/MohamedReda2015/outsystems-architecture ~/.claude/skills/outsystems-architecture
```
```powershell
git clone https://github.com/MohamedReda2015/outsystems-architecture "$HOME\.claude\skills\outsystems-architecture"
```
For one project only, clone it into `<repo>/.claude/skills/outsystems-architecture`. The skill triggers automatically from its description.

**Claude.ai / Claude Desktop**: download `outsystems-architecture-vX.Y.Z.zip` from [Releases](https://github.com/MohamedReda2015/outsystems-architecture/releases) and upload it under *Settings → Capabilities → Skills*.

**Claude API / Agent SDK**: upload it as a custom Skill, or put `SKILL.md` in the system prompt and give the agent read access to `references/`.

**Codex, Gemini CLI, Aider, Jules and other AGENTS.md readers**: add the repo as a folder or submodule of your project and copy [`adapters/AGENTS.md`](adapters/AGENTS.md) to your repository root.

**Cursor**: add the folder to the repo and copy [`adapters/cursor/outsystems-architecture.mdc`](adapters/cursor/outsystems-architecture.mdc) to `.cursor/rules/`.

**GitHub Copilot**: copy [`adapters/copilot-instructions.md`](adapters/copilot-instructions.md) to `.github/copilot-instructions.md`.

**Custom or multi-agent systems**: put [`adapters/core-rules.md`](adapters/core-rules.md) in every agent's system prompt, and give agents a file-read tool for the rest. Suggested roles:
- **Architect**: `design-process`, `architecture-canvas` and `module-standard` → a blueprint.
- **Builders** (one per layer): `data-and-logic`, `ui-standards`, `security` → build reports.
- **Reviewer**: `review-checklist`, `code-quality-patterns` and the validator → a review report that blocks on any Blocker.

## Use it
Example prompts once it is installed:
- "Design the module and app architecture for a leave-request system that reads employees from SAP."
- "Review these modules against our standards" (paste or export the module and dependency list).
- "Is it OK for my Reactive screen to pass `GetUserId()` to a server action?"
- "Code Quality flags 'Sequence of connected Aggregates' on CustomerDetail. How do I fix it?"
- "Write the hotfix procedure for our Dev/QA/Prod LifeTime setup."

The agent follows `SKILL.md`: it applies the precedence rules (project architecture > house standard > official guidance, and security is never relaxed), reads only the reference files it needs, and reports findings with rule IDs.

## Repository layout
```
SKILL.md                     entry point (frontmatter + workflow + quick rules + reference map)
references/                  details loaded on demand
  architecture-canvas.md       layers, suffixes, validation and sublayer rules, app composition, themes
  module-standard.md           CS/BL/CW/FE contract, dependencies, folders, naming, module health
  design-process.md            Disclose → Organize → Assemble, worked example
  data-and-logic.md            entities, CRUD/audit, soft delete, Service vs Server Actions, queries, exceptions, timers
  security.md                  Reactive/Mobile threat model, authorization, writes and reads, secrets, multi-tenancy
  ui-standards.md              screens, Reactive data fetching, blocks, themes/CSS, accessibility, mobile
  integration-and-caching.md   IS/Sync/API, wrapper canvas, cache patterns, versioning, microservices
  performance.md               official top-10 + Code Quality performance rules
  audit-trail.md               Audit_Lib patterns and API
  domain-driven-and-scale.md   domains, multi-team mobile, customizable products
  code-quality-patterns.md     official Code Quality catalogue → fixes + rule IDs
  lifecycle-and-sop.md         team setup, LifeTime, DoD, code review, deployment, hotfix, testing, CI/CD
  lessons-learned.md           real project mistakes → rules
  service-studio-mcp.md        notes for agents editing modules through the Service Studio MCP / Model API
  review-checklist.md          all enforceable rules with IDs and severities
templates/                   architecture blueprint, build report, review report
scripts/                     validate_architecture.py / .mjs, example inputs, check_skill.mjs, test_validator.mjs
adapters/                    core-rules.md, AGENTS.md, Cursor rule, Copilot instructions
research/                    sources.md (official vs community), assessment notes
```

## Architecture validator
Checks a module and application dependency graph against the canvas rules (ARC-01..04, ARC-07, ARC-10) and, with `--strict`, the house rules (HSE-01, HSE-03). Python 3 and Node 16+ versions produce identical output.
```bash
python scripts/validate_architecture.py scripts/example_deps.json --strict
node   scripts/validate_architecture.mjs scripts/example_deps_bad.json --strict   # shows each rule firing
```
Input is a JSON list of modules with `name`, `app`, `references` (and optionally `layer`, `role`). Layers come from the name suffix (`_CS`, `_BL`, `_IS`, ...). Build it from Service Center, Discovery or Code Quality exports, or the Service Studio Model API. Add `--json` for machine-readable output. **Exit code 1 means Blocker or Major findings**, so you can use it as a CI gate in your own OutSystems pipelines.

## Rule IDs and severities
Every rule lives in [`references/review-checklist.md`](references/review-checklist.md):

| Group | Covers |
|---|---|
| `ARC` | Architecture Canvas |
| `HSE` | House module standard |
| `DAT` | Data and logic |
| `INT` | Integrations |
| `UI` | Screens, blocks, themes |
| `PERF` | Performance |
| `SEC` | Security |
| `AUD` | Audit |
| `MNT` | Maintainability |
| `OPS` | Lifecycle and SOP |
| `TST` | Testing |

Severities: **Blocker** (deployability or security), **Major** (architecture, performance or maintenance cost), **Minor** (hygiene). IDs are stable across versions. `[CQ]` marks rules that OutSystems Code Quality also detects.

## Versioning and releases
[Semantic versioning](https://semver.org/) of `metadata.version` in `SKILL.md`:
- new rules = minor;
- wording or fixes = patch;
- a changed meaning of existing IDs = major.

See [CHANGELOG.md](CHANGELOG.md). Pushing a tag `vX.Y.Z` that matches the SKILL.md version runs the checks and publishes a release with the packaged `outsystems-architecture-vX.Y.Z.zip`. Build the same zip locally with:
```bash
git archive --format=zip --prefix=outsystems-architecture/ -o outsystems-architecture.zip HEAD
```

## Contributing
Rule proposals, corrections and real-world lessons are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md): cite a source, paraphrase, include no confidential data, keep rule IDs stable, and run the checks:
```bash
python tests/test_validator.py -v  # Node on PATH, or set OUTSYSTEMS_NODE
```
Also see the [Code of Conduct](CODE_OF_CONDUCT.md) and the [Security policy](SECURITY.md).

**Companion skill**: `references/ui-standards.md` covers the architecture side of UI. If you also use the separate `outsystems-live-style-guide` skill (design tokens, themes, patterns, accessibility tooling), agents will defer to it for detailed UI and UX work. It is optional, not part of this repository.

## Disclaimer
This is an independent community project. It is **not affiliated with, endorsed by, or supported by OutSystems**. "OutSystems", "Service Studio", "LifeTime", "Forge" and related names are trademarks of OutSystems. The content paraphrases public OutSystems documentation and community material, credited in [`research/sources.md`](research/sources.md), together with the authors' own experience. Always check critical decisions against the [official documentation](https://success.outsystems.com/documentation/11/) for your platform version.

## License
[MIT](LICENSE).


## Reliability review (Unreleased)

The updated guidance separates installed platform behavior, house conventions and observed project lessons. Read [verification and reliability](references/verification-and-reliability.md) for domain acceptance checks and primary sources. Changes are recorded under Unreleased; this does not declare a new upstream release.

Repository maintenance checks (full Git checkout):

```sh
node scripts/check_skill.mjs
node scripts/test_validator.mjs
python tests/test_validator.py -v
```

These maintenance scripts are excluded from the release archive.
