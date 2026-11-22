# Research assessment — outsystems-architecture v1.0.0 → v1.1.0

Date: 2026-11-22. Scope: the skill as a whole, checked against official OutSystems 11 documentation and community practice (see sources.md). The goal was to find gaps, errors and improvements, and to apply them.

## Summary
v1.0.0 was strong on architecture: the canvas, the 3 rules, application composition, integration patterns and the house 4-module pattern all matched the official documentation. It was weak on four things OutSystems now measures and documents:
1. the **Reactive/Mobile security model**;
2. the official **Code Quality** pattern catalogue;
3. **lifecycle SOPs** (deployment, hotfix, Definition of Done, review, testing, CI/CD);
4. **maintainability** rules.

It also had a few imprecise or outdated statements. All of these are fixed in v1.1.0.

## Findings
| # | Area | Finding (v1.0.0) | Severity | Evidence | Change in v1.1.0 |
|---|---|---|---|---|---|
| 1 | Security | No model of Reactive endpoint exposure: every client-called aggregate or server action is a REST endpoint; Anonymous and Registered screens expose it | High | Official Reactive security page; CQ "Automatically generated publicly exposed REST endpoint"; Noesis 10 rules | security.md rewritten (§1–5); SEC-07, SEC-08 |
| 2 | Security | Passing `GetUserId()` or a user id from the client or through block parameters was not forbidden | High | CQ "Insecure usage of GetUserId…" ×2 | SEC-09; security §2.5 |
| 3 | Security | Mass assignment: whole-record CreateOrUpdate called from the client was not addressed | High | DoItLean article; OutSystems blog "Protect writes" | SEC-11; use-case write actions in BL |
| 4 | Security | Secrets advice was outdated: site properties now support **Is Secret** (PS 11.25+) | Medium | CQ "Exposed secrets in site properties" | SEC-03, data-and-logic §9 |
| 5 | Security | Missing: the Registered role, system entities on public screens, disabled vs hidden buttons, one screen per role, client variables, test screens in QA/Prod, outdated Forge components | Medium | Official security page; CQ security patterns | SEC-10, SEC-11, SEC-13, SEC-14 |
| 6 | Architecture | No Core sublayer rule (a CS consuming BL, Sync or API); the validator didn't check it | Medium | CQ "Core module providing services to sublayers" | ARC-10; validator rule added and tested |
| 7 | Architecture | No Discovery classification, monolithic-module, team-coupling or extension rules | Low | CQ architecture patterns; Platform Best Practices | ARC-11 to ARC-14 |
| 8 | Data | The Service Action description was imprecise: no rollback semantics, no communication exceptions, which session context is passed | Medium | *Use Services to Expose Functionality* | data-and-logic §5 rewritten with the official comparison table |
| 9 | Data | Missing query rules: `TOP` in SQL, `List.Empty`, chains of aggregates, `[i]` indexing, type casts | Medium | CQ performance patterns; Best Practices | DAT-10, PERF-13, PERF-14 |
| 10 | Data | Timers lacked the `Timer_` prefix, 20-min default timeout and retry, 30-min CQ limit, kill switch, run log and staggering | Medium | CQ; Best Practices; KinetIT | DAT-09 expanded |
| 11 | Data | Site properties: no ban on runtime updates and no 20-per-module signal | Medium | CQ "Site property update"; Best Practices | DAT-11 |
| 12 | Logic | Exception handling lacked handler ordering, a standard logging action, Service Action and REST API behaviour, and a functional-error structure | Medium | Noesis; forum threads | data-and-logic §7 |
| 13 | UI/Perf | "Keep On Initialize light" was too weak: CQ forbids server calls in client events and multiple server calls per client action | Medium | CQ performance patterns | PERF-08, PERF-15, PERF-16; ui-standards data-fetching section |
| 14 | UI | Missing: CSS in screen stylesheets and inline CSS or JavaScript, image and resource limits, Popup suffix, accessibility target, CSP | Low | CQ; OutSystems accessibility | UI-04, UI-07, UI-08, PERF-17 |
| 15 | Mobile | Missing: client/server isolation (`MB_Account_CS`), async sync, network status, simple splash | Low | CQ mobile patterns | ui-standards mobile section; UI-05 |
| 16 | Maintainability | No rules for descriptions, transaction tags, long flows, disabled or unreachable code, unused elements, reminders, deprecated elements, TrueChange growth | Medium | CQ maintainability patterns; ITNEXT tech-debt checklist | MNT-01 to MNT-08; DAT-12 |
| 17 | SOP | No lifecycle guidance (LifeTime, deployment, hotfix, DoD, review, testing, CI) | High | Best Practices (Teamwork); BDDFramework; outsystems-pipeline; forum | New lifecycle-and-sop.md; OPS-01 to OPS-07, TST-01 to TST-04 |
| 18 | Naming | Didn't cover the official naming baseline (English, FK `Id`, screen prefixes, `Timer_`) or the common no-underscore alternative | Low | Best Practices; Synobsys | module-standard §4; HSE-05 |
| 19 | Module std | CS "no validation" was too strict. MVP consensus: integrity validations that always hold may live in CRUD; CRUD has no role checks | Low | Forum discussion 100293; Synobsys ADR-003 | module-standard §1 |
| 20 | Tooling | No map from Code Quality findings to fixes or rule IDs | Medium | CQ catalogue | New code-quality-patterns.md |

## Points confirmed correct (no change needed)
- The canvas layers, the 3 validation rules, app composition and the 4 rules, theme isolation: these match the official documentation.
- Read-only entities with CRUD wrappers is now an official Code Quality pattern.
- `_IS` per concept, the wrapper canvas, cold cache + sync, the `_Sync` isolation pattern.
- Large text and binary data isolation, indexes, the wake-timer pattern, Structures as I/O.

## Points where sources disagree (how the skill resolves them)
- **Where to put security checks**: the OutSystems blog says "put security logic in CRUD"; Synobsys ADR-003 says CRUD has no role checks and only BL calls it. The skill uses **use-case BL actions with the checks, and CRUD with integrity rules only**. The goal both sides share is that every write path reachable from the client is checked on the server.
- **Can CW or FE read CS entities?** Several MVPs accept it, while the house strict mode forbids it. The skill keeps strict as the default and allows relaxed mode through project precedence. Security rules apply in both modes.
- **Action naming with or without underscores**: both are in use. The skill asks each factory to pick one style and record it.

## Recommendations for projects using this skill
1. Run the validator and Code Quality on existing apps and log the findings with the new IDs. Do **SEC-07, SEC-08, SEC-09 and SEC-11** first.
2. Check every Reactive screen for Anonymous or Registered roles and for `GetUserId()` passed from the client. Check every client-callable save action for whole-record parameters.
3. Move secrets in plain site properties to **Is Secret** (check the Platform Server version is 11.25 or later).
4. Add BDD tests for the critical BL actions, plus negative security cases.
5. Write the factory's naming style and precedence decisions into each project's AGENTS.md.
