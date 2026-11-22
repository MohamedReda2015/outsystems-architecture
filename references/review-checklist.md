# Review checklist (enforceable rules)

Canvas graph findings apply to strong references; weak Service Actions, screens and data-type-only dependencies are assessed for contracts and runtime coupling separately. Mixed module pairs remain strong. House rules are project conventions, not additional platform dependency types.


Every rule has an ID, a severity and a check. Cite the ID in findings. The IDs stay stable between versions: new rules get new numbers.

**Severity**:
- **Blocker**: breaks deployability or security. Fix before release.
- **Major**: violates the architecture or causes real performance or maintenance cost. Fix this release.
- **Minor**: convention or hygiene. Fix when you touch the code.

**Tags**:
- `[auto]` = checked by `scripts/validate_architecture.*`.
- `[CQ]` = also detected by OutSystems Code Quality (formerly AI Mentor Studio); see code-quality-patterns.md.
- `[TC]` = a Service Studio TrueChange warning.

## ARC — Architecture Canvas (modules and apps)
| ID | Sev | Rule | Check / fix |
|---|---|---|---|
| ARC-01 | Blocker | No upward references (Foundation→Core/End-User, Core→End-User) `[auto][CQ]` | Move the consumed element down |
| ARC-02 | Blocker | No side references between End-User modules `[auto][CQ]` | Move it to Core (business) or a Library (agnostic) |
| ARC-03 | Major | No cycles among Core or Foundation modules `[auto][CQ]` | Move, merge, or add a composition module on top |
| ARC-04 | Major | An app sits in the layer of its highest module; the same rules apply between apps `[auto][CQ]` | Move shared modules and their dependencies into a Core or Foundation app |
| ARC-05 | Major | One owner and one sponsor (line of business) per app | Split the app |
| ARC-06 | Major | End-User modules expose no reusable public elements `[CQ]` | Make them private or move them down |
| ARC-07 | Minor | Every module name has a canvas suffix (or is a known End-User name) `[auto]` | Rename |
| ARC-08 | Major | No business screens in Core or Foundation modules (except exception screens and `...Popup` screens); no test screens left in modules `[CQ]` | Move to End-User or delete |
| ARC-09 | Minor | The theme holds only look-and-feel, layouts, menu, login, exceptions and transversal roles | Move utilities to a `_Lib` |
| ARC-10 | Major | Core sublayers: a CS never consumes BL, CW, API, Sync or Eng; Foundation sublayers compose only downward `[auto][CQ]` | Move the consumed element down |
| ARC-11 | Minor | Every module is classified by layer in Discovery `[CQ]` | Classify it (a mixed module takes its top layer) |
| ARC-12 | Major | No monolithic modules: too many public elements, too many screens, over about 4 MB, over about 20 site properties `[CQ]` | Split by concept or UI flow, and move resources out |
| ARC-13 | Minor | Extensions are wrapped in modules; no business logic in extensions; extensions not used just to consume web services | Refactor |
| ARC-14 | Major | Different teams' apps use only weak references, except to Foundation apps `[CQ]` | Use Service Actions, or move the element to a Foundation app |

## HSE — House 4-module standard (strict mode)
| ID | Sev | Rule |
|---|---|---|
| HSE-01 | Major | The chain is FE → CW → BL → CS: no skipped layers, no reverse references `[auto --strict]` |
| HSE-02 | Major | Structures live in BL, not in CS |
| HSE-03 | Major | Screens use CW blocks only; blocks use BL Service Actions and Structures only (no CS entities or CRUD) `[auto --strict, module level]` |
| HSE-04 | Minor | Required folders exist (CS: Entities/<Concept>, Lookups, CRUD; BL: Structures, ServiceActions, PrivateActions, Integrations; CW: Blocks, UIHelpers; FE: flows by journey) |
| HSE-05 | Minor | Naming follows one documented style (house `Entity_Verb` or `EntityVerb`); English; PascalCase; foreign keys end in `Id`; `Timer_` prefix; `_Logic` for private implementations; `On<Event>` handlers |
| HSE-06 | Minor | Every module, public element and parameter has a meaningful Description `[CQ]` |

## DAT — Data and logic
| ID | Sev | Rule |
|---|---|---|
| DAT-01 | Major | Entities are Public + Expose Read-Only; writes only through CS CRUD wrappers `[CQ]` |
| DAT-02 | Major | Audit columns are set only inside the CRUD wrappers |
| DAT-03 | Major | Soft-deleted rows are filtered in **every** query, including joined children |
| DAT-04 | Major | Public actions take and return Structures with only the needed fields (no wide entity records) |
| DAT-05 | Major | Multi-step writes run in one private Server Action behind a thin Service Action; Service Action sequences have compensation |
| DAT-06 | Major | Foreign keys have a deliberate Delete Rule; mandatory attributes are marked; text lengths are set; no entity with hundreds of attributes |
| DAT-07 | Minor | Static entities for fixed lists, referenced by record name, never by literal id or hard-coded value |
| DAT-08 | Major | Specific exception handlers before AllExceptions; standard logging action; user-friendly messages; no silent swallowing |
| DAT-09 | Blocker | Timers: `Timer_` action, batches, logical timeout, checkpoint and commit, self re-wake, kill switch, run log; nothing runs over 30 min `[CQ]` |
| DAT-10 | Major | No queries in loops; Max. Records on aggregates; `TOP`/`ROWNUM` in SQL; SQL parameterized `[CQ]` |
| DAT-11 | Major | No site property updates in logic; at most about 20 site properties per module `[CQ]` |
| DAT-12 | Minor | Public actions that commit or abort the transaction say so in their Description (`[commit transaction]`) `[CQ]` |

## INT — Integrations
| ID | Sev | Rule |
|---|---|---|
| INT-01 | Major | External systems are called only through a `<Concept>_IS` (one per concept) |
| INT-02 | Major | `_IS` exposes its own normalized structures, never auto-generated REST/SOAP types |
| INT-03 | Major | `_IS` turns error responses into exceptions; authentication lives inside the `_IS`; every call has a timeout |
| INT-04 | Minor | `_IS` and `_API` contain no business logic |
| INT-05 | Major | The integration pattern was chosen deliberately; sync is one-way; writes are write-through |
| INT-06 | Major | API and Service Action changes follow versioning (breaking change = new version; deprecate the old one) |

## UI — Screens, blocks, themes
| ID | Sev | Rule |
|---|---|---|
| UI-01 | Major | Screens are placeholders; content and logic live in CW blocks |
| UI-02 | Major | Blocks communicate through Events; they don't navigate to other modules' screens |
| UI-03 | Minor | Blocks are configured through parameters, with no hidden dependency on screen state; lists inside lists get data passed down |
| UI-04 | Minor | No inline CSS; no CSS in screen stylesheets; theme classes only; prefixed custom classes `[CQ]` |
| UI-05 | Major | Mobile: one End-User module; MCW per area; client logic separate from server CS; denormalized local storage; async sync with SyncUnits; simple splash `[CQ]` |
| UI-06 | Minor | Every screen has a specific name, a title and custom roles |
| UI-07 | Minor | No inline JavaScript; scripts at screen, block or module level, commented `[CQ]` |
| UI-08 | Minor | Accessibility: labels, focus handling, contrast, alt text (WCAG 2.1 AA target) |

## PERF — Performance
| ID | Sev | Rule |
|---|---|---|
| PERF-01 | Major | Indexes on attributes used in filters, sorts and joins |
| PERF-04 | Major | No joins across a linked server |
| PERF-06 | Major | Large text (over 2000 characters) and binary data in a 1-to-1 extension entity |
| PERF-08 | Major | No server calls in client events (On Initialize / Ready / Render / After Fetch); screen preparation is light `[CQ]` |
| PERF-09 | Minor | (Traditional Web) no preparation data or large variables in screen actions / ViewState `[CQ]` |
| PERF-10 | Major | Only the needed fields are fetched (Structures as I/O) |
| PERF-11 | Minor | Public actions preferred over local web services; connection pooling for external DBs |
| PERF-12 | Minor | High-volume tables are archived or purged on a schedule |
| PERF-13 | Major | No chains of connected aggregates; merge them with joins `[CQ]` |
| PERF-14 | Minor | `List.Empty` instead of `List.Count`; dedicated count queries `[CQ]` |
| PERF-15 | Major | One server request per user action (no sequences of server calls in client actions) `[CQ]` |
| PERF-16 | Minor | Default server request timeout ≤ 10 s (Reactive/Mobile) `[CQ]` |
| PERF-17 | Minor | Images ≤ 150 KB (mobile) / 500 KB (web), ≤ 1024 px; large resources outside the module `[CQ]` |
| PERF-18 | Major | No large (compound or list) session variables `[CQ]` |

## SEC — Security
| ID | Sev | Rule |
|---|---|---|
| SEC-01 | Blocker | Authorization is enforced on the server (role checks in BL plus record-ownership or ACL checks) |
| SEC-02 | Blocker | No SQL injection (Expand Inline off; `EncodeSql` on literals only; `BuildSafe_InClause*`); output is encoded `[CQ]` |
| SEC-03 | Blocker | No hard-coded secrets, URLs or keys; secret site properties have **Is Secret = Yes** (PS 11.25+) or an encrypted store `[CQ]` |
| SEC-04 | Major | Uploads are validated (type, size, antivirus) before content is stored |
| SEC-05 | Blocker | Multi-tenant: no Show Tenant Identifier or `TenantSwitch` outside approved admin apps |
| SEC-06 | Major | No secrets or full personal data in logs or URLs; IDs masked in the UI |
| SEC-07 | Major | Screens use custom roles; no **Anonymous** or **Registered** unless intended `[CQ]` |
| SEC-08 | Blocker | Server actions, aggregates and data actions reachable from Anonymous screens re-validate every input `[CQ]` |
| SEC-09 | Blocker | Identity never comes from the client: no `GetUserId()` or user id passed as an action or block parameter `[CQ]` |
| SEC-10 | Major | No system entities (Users, etc.) in screen aggregates on Anonymous or Registered screens `[CQ]` |
| SEC-11 | Major | No whole-record writes from the client (use-case actions with only the allowed fields); forbidden buttons hidden, not just disabled `[CQ]` |
| SEC-12 | Major | Exposed REST APIs use TLS and authentication (or Internal Access Only) and catch exceptions in each method `[CQ]` |
| SEC-13 | Major | No sensitive data or authorization flags in client variables or screen parameters; one screen per role profile |
| SEC-14 | Major | Test screens and sandbox or test apps are never deployed beyond QA; Forge components and plugins are kept up to date |

## AUD — Audit
| ID | Sev | Rule |
|---|---|---|
| AUD-01 | Major | A business audit exists where compliance needs it (centralized Audit_Lib or an entity history) |
| AUD-02 | Minor | Audit writes are fast or async (staging plus a timer) and have a retention policy |
| AUD-03 | Minor | Platform logs are exported if they must be kept longer than the default retention |

## MNT — Maintainability
| ID | Sev | Rule |
|---|---|---|
| MNT-01 | Minor | No duplicated logic; extract a reusable action `[CQ]` |
| MNT-02 | Minor | Public actions that manage transactions are tagged in their description (see DAT-12) `[CQ]` |
| MNT-03 | Minor | No long undocumented flows (screen action or preparation over about 20 nodes; action over about 40); vertical, tidy flows with labels `[CQ]` |
| MNT-04 | Minor | No disabled code or unreachable logic (hard-coded True/False) `[CQ]` |
| MNT-05 | Minor | No unused actions, aggregates, SQL or dependencies ("Remove Unused Dependencies") `[CQ]` |
| MNT-06 | Minor | No reminder comments promoted to QA `[CQ]` |
| MNT-07 | Major | No consumption of deprecated elements `[CQ]` |
| MNT-08 | Minor | TrueChange warnings don't increase; hidden warnings have a documented reason `[TC]` |

## OPS — Lifecycle and SOP (lifecycle-and-sop.md)
| ID | Sev | Rule |
|---|---|---|
| OPS-01 | Major | Deployments go through LifeTime with tagged app versions; no single-module publishing outside Dev |
| OPS-02 | Major | Impact analysis is clean (no outdated or broken consumers) before deploying |
| OPS-03 | Minor | No Production deployments in business hours, except approved hotfixes |
| OPS-04 | Major | Hotfixes are tested in a Production-equivalent environment and ported back to Dev and QA right away |
| OPS-05 | Minor | Per-environment values (site properties, endpoints, timers) are documented in the deployment notes |
| OPS-06 | Minor | Definition of Done met (review, tests, Code Quality clean, unused dependencies removed) |
| OPS-07 | Minor | One user per developer; the same Service Studio version across the team |

## TST — Testing
| ID | Sev | Rule |
|---|---|---|
| TST-01 | Major | Critical server logic has automated tests (BDDFramework, Given-When-Then) in separate test modules or apps |
| TST-02 | Minor | Negative security tests: missing role, another user's id, tampered input |
| TST-03 | Minor | Tests are repeatable (they create and clean their own data) and run in the CI regression stage |
| TST-04 | Major | Test apps never reach Production |

## How to run a review
1. Get the module, app and reference list (Service Center, Discovery or Code Quality, or the Model API) and run the validator.
2. Read the current **Code Quality** findings and the **TrueChange** warnings for the apps under review. Map them with code-quality-patterns.md.
3. Sample each module type: CS entities and CRUD, BL public actions, CW blocks, FE screens, IS actions, timers, exposed APIs.
4. Record each finding as: ID · severity · element (`Module.Folder.Element`) · evidence · fix. Order the findings: Security, Performance, Architecture, Maintainability.
5. Summarize the counts by severity and the top 3 risks. Fill in `templates/review-report.md`.


## Reliability and evidence (2026-11 review)

These manual checks complement, rather than extend the claimed coverage of, the static scripts. Details and acceptance cases: [verification and reliability](verification-and-reliability.md).

| ID | Severity | Rule |
|---|---|---|
| ARV-01 | Major | Classify strong, weak and unknown dependency edges; do not claim full coverage from a partial graph. |
| ARV-02 | Major | Verify producer contracts and consumer freshness before mapping fields or declaring delivery complete. |
| ARV-03 | Major | Preserve temporal identity and plan data migrations; never mix real identities with sample dependent data. |
| ARV-04 | Major | Report prepared, validated, merged, published and runtime-tested evidence separately. |
