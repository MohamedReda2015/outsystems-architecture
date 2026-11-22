---
name: outsystems-architecture
description: Design, review and evolve OutSystems 11 application architecture, module boundaries, dependencies, deployment and verification. Distinguishes official Architecture Canvas rules from the house FE/CW/BL/CS pattern. Use for O11 architecture or cross-module changes; use domain skills for implementation details and ODC guidance for ODC.
license: MIT
metadata:
  version: 2.0.0
  updated: "2026-11-22"
  platform: OutSystems 11 (Reactive Web, Mobile, Traditional Web)
  agent-independent: "true"
---

# OutSystems-Architecture

## Scope, evidence and consistency

- Run bundled scripts from the skill directory or use absolute paths; do not assume they exist in the application checkout.
- Establish O11/ODC, application type, installed component versions and the target environment from available evidence; ask only for information that changes the work.
- Separate **platform facts**, **house defaults**, **project decisions** and **observed lessons**. Project conventions choose among supported designs; they cannot change runtime behavior. The FE/CW/BL/CS chain is an O11 house pattern, not an ODC requirement.
- Preserve the user's requested scope and existing authorization. Continue routine reversible work; a skill does not authorize publishing, dependency changes or production operations beyond that scope. Do not introduce phase-by-phase approval unless the user or environment requires it.
- Prefer installed API signatures and version-matched official documentation. A repository development branch, community workaround or old project observation is evidence to investigate, not a release guarantee.
- Report evidence separately: **prepared → model validated → merged → published → runtime verified**. A static checker passing proves only its covered checks on the supplied inventory. Unknown, blocked and not tested remain explicit.
- Read [verification and reliability](references/verification-and-reliability.md) when changing data contracts, concurrent operations, runtime behavior or verification. It contains the concrete acceptance checks and sources for this skill.


This skill makes an agent design, build, secure, deploy and review OutSystems 11 software the way a senior OutSystems architect would. It covers correct layering, clean dependencies, predictable naming, a secure Reactive design, and the patterns and SOPs that keep applications fast and independently deployable. It is written for any agent (Claude, Copilot, Cursor, Codex, a custom LLM agent, or a human), so it relies on plain Markdown and one optional script (Python or Node).

## Why this matters

An OutSystems factory grows into dozens of apps and hundreds of modules with different owners and release cadences. LifeTime plans application deployments while Service Studio publishes modules. Strong references couple producer changes to consumer refresh/republication; impact analysis determines what a particular deployment needs. Wrong layering forces unrelated apps to be deployed together and creates cycles that block publishing. In Reactive and Mobile apps, **every aggregate and server action the client calls becomes a REST endpoint** that users can call with any input they like. Almost every rule below protects *lifecycle independence* or *server-side trust*.

## Applying conventions

Use the project's documented architecture, naming and design choices where supported. Use this skill's house defaults when the project has no decision. Official documentation and installed contracts determine platform behavior; house preferences never override those facts. Record a consequential deviation and its reason. Escalate unresolved security, data-integrity or compatibility conflicts, not ordinary naming or layout choices.

## 1. The Architecture Canvas (official, 3 layers)

| Layer | Holds | Typical suffixes |
|---|---|---|
| **End-User** | UI and processes for one user journey. Consumes Core and Foundation. **Never provides reusable services.** | none (it appears in the URL), `_FE`, `_Front_End`, `_BO`, `_Portal` |
| **Core** | Business concepts as reusable services: entities, business rules, business widgets. | `_CS`, `_BL`, `_CW`, `_Sync`, `_Eng`, `_API`/`_OAPI`; mobile: `_MCS`, `_MCW`, `_MUI`, `_MDB` |
| **Foundation** | Business-agnostic: libraries, integration wrappers, themes, UI patterns, drivers, native code. | `_Lib`, `_IS`, `_Th`, `_Pat`, `_Drv`, `_FS`, `_Ext` |

O11 has no Orchestration layer: screen destinations are weak references. Classify every module in **Discovery** so Code Quality can validate it.

**Canvas validation rules apply to strong references** (modules and applications). Weak Service Actions and screen destinations are excluded from these graph violations; still review their contracts and operational coupling:
- **R1. No upward references.**
- **R2. No side references between End-User modules.** Move the shared element down: to Core if it is business-related, to a Library if it is not.
- **R3. No cycles** among Core or Foundation modules.
- **Sublayers**: a `_CS` never consumes `_BL`, `_CW`, `_API`, `_Sync` or `_Eng` (ARC-10).

**Application composition**:
1. Layer the modules correctly.
2. Layer the apps correctly. An app sits in the layer of its highest module.
3. One owner per app.
4. One sponsor or line of business per app.

Shared Cores move, with all their dependencies, into a Core app. Different teams' apps use weak references only, except to Foundation apps.

Details and fixes: `references/architecture-canvas.md`.

## 2. House standard: the 4-module pattern

```
<App>_Front_End  (End-User)    Screens only: layout, navigation, parameters (ids) to blocks, custom roles.
      │ consumes
<App>_CW         (Core)        Public Reactive blocks + UI helpers. Data via BL Service Actions. Events out.
      │ consumes
<App>_BL         (Core)        ALL Structures, thin public Service Actions (auth check → private _Logic),
      │ consumes                use-case write actions, roles, site properties, integration orchestration.
<App>_CS         (Core)        Entities (Public, Expose Read-Only) + public CRUD wrappers (audit columns,
                                integrity validation, no role checks, never called from the client).
```

- One-way chain with no skipping and no cycles. **Strict mode** (the default): screens use CW blocks only, and blocks use BL only. Relaxed mode (FE or CW reading CS entities) only when the project's own architecture says so.
- **Required folders** in each module:

  | Module | Folders |
  |---|---|
  | CS | `Entities/<Concept>`, `Lookups`, `CRUD` |
  | BL | `Structures`, `ServiceActions`, `PrivateActions`, `Integrations` |
  | CW | `Blocks/<Concept>`, `UIHelpers` |
  | FE | UI flows by journey |

- **Naming**: English and PascalCase; foreign keys end in `Id`; `Timer_` prefix for timer actions; `_Logic` for private implementations; `On<Event>` for handlers. Use specific names, and pick one documented action style (`Entity_Verb` or `EntityVerb`).
- Integrations, timers and themes go in `_IS`, `_Sync` and `_Th` modules. One CS per concept, never one giant data module.

Full specification: `references/module-standard.md`.

## 3. How to work (any agent)

### Designing
Follow `references/design-process.md`:
1. **Disclose** concepts and functional, non-functional and integration needs.
2. **Organize** them on the canvas.
3. **Assemble** modules and apps from the patterns.
4. Validate.

Write the result with `templates/architecture-blueprint.md`.

### Building
1. **Inventory first.** Read what already exists (modules, references, elements). Reuse before you create.
2. Build bottom-up: CS → BL → CW → FE (plus IS and Sync where needed). Publish the producer, then refresh its consumers.
3. Apply the rules for the task at hand:
   - data and logic (`references/data-and-logic.md`): read-only entities, CRUD wrappers, soft delete, Service vs Server Actions, queries, exceptions, timers, configuration, flow style;
   - security (`references/security.md`): **read it before building any screen or server action that the client can call**;
   - UI (`references/ui-standards.md`): data fetching, blocks, themes, mobile;
   - integrations and caching (`references/integration-and-caching.md`).
4. **Never hard-code** configuration, URLs, secrets or business thresholds. Secret site properties use **Is Secret** (Platform Server 11.25+).
5. Never publish to Production, and never run destructive or irreversible platform operations, without the user's explicit instruction.
6. Report only what you verified in the platform. "Implemented" means it exists and validates, not that you wrote code for it.
7. Meet the Definition of Done (`references/lifecycle-and-sop.md` §3), then finish with `templates/build-report.md`.

If you drive Service Studio through the MCP / Model API, read `references/service-studio-mcp.md` and the installed Service Studio MCP skill first. Keep the live tool contract authoritative; do not copy old session details into a new task.

### Reviewing or enforcing
1. Collect the module list, layers, apps and references. Run the validator:
   ```
   python scripts/validate_architecture.py deps.json --strict    # Python 3
   node   scripts/validate_architecture.mjs deps.json --strict   # same checks, Node 16+
   ```
   For the input format, see either script's header or `scripts/example_deps.json`.
2. Read the app's **Code Quality** findings and **TrueChange** warnings, and map them with `references/code-quality-patterns.md`.
3. Walk through `references/review-checklist.md`. Every rule has an ID (e.g. `ARC-10`, `SEC-09`) and a severity. Triage in this order: Security → Performance → Architecture → Maintainability.
4. Write the result with `templates/review-report.md`: findings by severity, each with its rule ID, the evidence and a concrete fix.

### Deploying, hotfixing, testing
Follow `references/lifecycle-and-sop.md` and the project release policy: LifeTime for governed environment promotion, impact analysis, per-environment configuration, migrations, hotfix/backport and appropriate tests. Deployment windows are a project operational decision.

## 4. Rules quick reference (most often broken)

**Security (Reactive / Mobile)**:
- The client is untrusted. Every client-called aggregate, data action and server action is a REST endpoint that require server-side authorization for the requested record and operation; screen roles alone are insufficient.
- Use custom roles on every screen; no Anonymous or Registered unless intended (SEC-07, SEC-08).
- **Identity comes from the server only**: `GetUserId()` inside the aggregate or action, never as a parameter or block input (SEC-09).
- Role **and** record-ownership checks go in the BL action, not just on hidden buttons (SEC-01). One screen per role profile (SEC-13).
- No whole-record `CreateOrUpdate` from the client: use use-case actions with only the allowed fields (SEC-11).

**Architecture**:
- Reusable logic in an End-User module, or one End-User module referencing another → move it to Core or a Library (ARC-02).
- A CS depending on BL, Sync or API → move the element down (ARC-10).
- A screen or block reading CS directly → go through a BL Service Action (HSE-03).

**Data**:
- An entity writable by other modules → turn on Expose Read-Only and use CRUD wrappers that set the audit columns (DAT-01).
- Structures in CS, or wide entity records as parameters → Structures in BL, with only the needed fields (HSE-02, DAT-04).
- A chain of Service Actions treated as atomic → one Service Action over private Server Actions, or explicit compensation (DAT-05).

**Performance**:
- A server call in On Initialize, On Ready or On After Fetch, or several server calls in one client action → data actions, or one combined server action (PERF-08, PERF-15).
- A query in a loop, `List.Count` used as an emptiness test, or unlimited records → join, use `List.Empty`, set Max. Records or `TOP` (DAT-10, PERF-14).

**Timers and configuration**:
- A long timer with no checkpoint → batches, logical timeout, commit, re-wake, kill switch (DAT-09).
- A site property updated in logic, or a secret in a plain site property → use an entity, or set Is Secret (DAT-11, SEC-03).

**Integrations**:
- An external API called outside an `_IS`, or an `_IS` exposing generated structures → `<Concept>_IS` with normalized structures and exceptions (INT-01, INT-02).

## 5. Reference map (read only what the task needs)

| File | Read when |
|---|---|
| `references/architecture-canvas.md` | designing, validating or fixing module or app dependencies |
| `references/module-standard.md` | creating or reviewing CS/BL/CW/FE modules, naming, folders, module health |
| `references/design-process.md` | turning requirements into a blueprint |
| `references/data-and-logic.md` | entities, actions, transactions, queries, exceptions, timers, config, flow style |
| `references/security.md` | **any screen, server action, API, role, secret or public flow** |
| `references/ui-standards.md` | Reactive or Mobile screens, data fetching, blocks, themes, CSS, accessibility |
| `references/integration-and-caching.md` | REST/SOAP, external systems, sync, cold/hot/distributed cache, API versioning |
| `references/performance.md` | performance tuning or review |
| `references/audit-trail.md` | audit logging, Audit_Lib, compliance |
| `references/domain-driven-and-scale.md` | large factories, many teams, domains, microservices, multi-tenant, mobile with many teams |
| `references/code-quality-patterns.md` | interpreting or predicting Code Quality (AI Mentor Studio) and Discovery findings |
| `references/lifecycle-and-sop.md` | environments, LifeTime, deployments, hotfixes, Definition of Done, code review, testing, CI/CD |
| `references/lessons-learned.md` | before any real build: mistakes already made once |
| `references/service-studio-mcp.md` | editing modules through the Service Studio MCP / Model API |
| `references/review-checklist.md` | any review or "is this correct?" question |
| `scripts/validate_architecture.py` / `.mjs` | automatic dependency validation from a JSON export |
| `research/sources.md` | where a rule comes from (official vs community), to cite or re-verify |
