# Changelog

All notable changes to this skill. Versions follow [semantic versioning](https://semver.org/) of `metadata.version` in `SKILL.md`.

## 2.0.0 — 2026-11-22
**Breaking: the skill is renamed** from `outsystems-standards` to **`outsystems-architecture`** (display title "OutSystems-Architecture").
- The skill `name`, folder, install paths, release zip (`outsystems-architecture-vX.Y.Z.zip`), adapter paths and Cursor rule file (`adapters/cursor/outsystems-architecture.mdc`) all change.
- Existing installs: delete the old `outsystems-standards` folder and install the new one. Update any `AGENTS.md`, Cursor or Copilot files that point to `outsystems-standards/`.
- Content and rule IDs are unchanged.

## 1.2.0 — 2026-11-22
Prepared for public release on GitHub.

**Added**
- `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `SECURITY.md`.
- GitHub issue templates (rule proposal, inaccuracy) and a pull request template.
- CI workflow:
  - skill consistency check;
  - validator regression;
  - Python ↔ Node output equality;
  - packaging smoke test.
- Release workflow: a tag `vX.Y.Z` builds and publishes `outsystems-standards-vX.Y.Z.zip`.
- `scripts/check_skill.mjs`: frontmatter, links, rule IDs, changelog/version match, secret and personal-data patterns.
- `scripts/test_validator.mjs` and `scripts/expected/*.json` (regression baselines).
- `.gitignore` and `.gitattributes` (LF endings; repository plumbing excluded from the packaged zip).

**Changed**
- README rewritten for a public audience: installing for each agent, usage examples, layout, validator, rule IDs, versioning, disclaimer (not affiliated with OutSystems).
- `SKILL.md` license changed from internal use to MIT.
- Private project names and identifiers replaced with neutral examples (`Orders_*`, `IDP:<externalId>`, `OrderClerk`, `ord-card`, `Claims_Front_End`).
- `validate_architecture.mjs` now sorts by plain code point (identical to Python's `sorted`), so both validators emit byte-identical JSON.

## 1.1.0 — 2026-11-22
Research-driven update covering official OutSystems 11 docs and community practice. Full rationale: `research/assessment-2026-11.md`. Sources: `research/sources.md`.

**Added**
- `references/code-quality-patterns.md`: the full official Code Quality (formerly AI Mentor Studio) catalogue, mapped to fixes and rule IDs.
- `references/lifecycle-and-sop.md`: team setup, environments and LifeTime, Definition of Ready/Done, development, code review, deployment, hotfix, testing (BDD), CI/CD (outsystems-pipeline), monitoring and technical debt.
- Checklist rules ARC-10 to ARC-14, DAT-11, DAT-12, UI-07, UI-08, PERF-13 to PERF-18, SEC-08 to SEC-14, MNT-01 to MNT-08, OPS-01 to OPS-07, TST-01 to TST-04.
- Validator rule **ARC-10** (Core sublayers: a CS must not consume BL, CW, API, Sync or Eng), in both the Python and Node versions. The bad example now triggers it.
- `research/` folder (sources and assessment) and this changelog.

**Changed**
- `security.md` rewritten around the Reactive/Mobile threat model:
  - endpoint exposure;
  - Anonymous and Registered roles;
  - server-side identity;
  - no mass assignment;
  - one screen per role;
  - OTP flows;
  - Is Secret site properties;
  - CSP;
  - exposed API exception handling.
- `data-and-logic.md`:
  - official Service vs Server Action table (transactions, rollback, session context, communication exceptions, versioning, transaction tags);
  - query rules (`TOP`, `List.Empty`, aggregate chains);
  - exception standards;
  - expanded timer rules;
  - site property rules;
  - a new flow-readability section.
- `ui-standards.md`: Reactive data-fetch rules (no server calls in client events, one request per user action, On Demand fetching, lists in lists, ≤10 s timeout), CSS and JavaScript placement, image limits, UI security, accessibility (WCAG 2.1 AA, EAA), and mobile sync and client/server isolation.
- `performance.md`: Code Quality performance patterns and module health signals (4 MB, 20 site properties).
- `module-standard.md`: official naming baseline plus the community alternative, integrity validations allowed in CS, no role checks in CRUD, use-case write actions in BL, one CS per concept, more suffixes (`_OAPI`, `_FS`), module health signals.
- `architecture-canvas.md`: Discovery classification, the sublayer rule, the team-coupling rule, and the official 3-responsibility summary.
- `SKILL.md` (v1.1.0): broader trigger description, security-first quick rules, Code Quality and SOP workflow steps, new reference map entries. Security rules are never relaxed by precedence.
- `adapters/core-rules.md` and the Copilot block: Reactive security and new performance rules.

**Unchanged**: rule IDs from 1.0.0 keep their meaning; templates; lessons-learned; Service Studio MCP notes.

## 1.0.0 — 2026-11-22
Initial version: Architecture Canvas, the house 4-module standard, design process, data and logic, UI, integration and caching, performance, security, audit, scale, lessons learned, Service Studio MCP notes, review checklist, templates, validator, and adapters.
