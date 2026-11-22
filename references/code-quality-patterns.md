# Code Quality patterns (formerly AI Mentor Studio) → rule IDs

Source: OutSystems 11 docs, *Manage technical debt → Code analysis patterns* (last updated Aug 2026). **AI Mentor Studio is now called Code Quality.** It analyzes the factory about every 12 hours and scores technical debt. It works together with **Discovery** (architecture layer classification) and Service Studio **TrueChange** warnings.

Use this file to:
1. predict what Code Quality will flag before it runs;
2. explain a Code Quality finding and fix it;
3. map findings to this skill's rule IDs in reviews.

**Triage order** recommended by OutSystems staff: **Security → Performance → Architecture → Maintainability**. Pattern weights can be tuned per organization (Maintenance tab).
"(R)" = Reactive/Mobile only, "(M)" = Mobile only, "(T)" = Traditional Web only.

## Architecture
| Code Quality pattern | Fix | Rule |
|---|---|---|
| Lack of module classification | Classify every module's layer in Discovery. A mixed module takes its top layer. | ARC-11 |
| End-user (or Orchestration) module providing services | Move the consumed elements to Core or Foundation | ARC-02, ARC-06 |
| Core module consumed by Foundation | Move the element down, or rethink the Foundation consumer | ARC-01 |
| Cyclic references between modules / applications | Move elements to the consumer or to a new module | ARC-03, ARC-04 |
| End-user / Orchestration application providing services | Move the consumed modules into Core or Foundation apps | ARC-04 |
| Core application consumed by Foundations | Move the module, or rethink the consumer | ARC-04 |
| **Core module providing services to sublayers** (CS consuming BL / API / Sync) | Move the consumed logic down into the CS sublayer | ARC-10 |
| Foundation module providing services to sublayers | Higher sublayers compose lower ones, never the other way round | ARC-10 |
| Public Entities aren't read-only | Turn on Expose Read-Only; add your own public CRUD actions with validation and audit | DAT-01 |
| Foundation or Core module with screens | Move screens to End-User modules. Exceptions: exception screens and reusable popups **suffixed `Popup`**. Remove test screens. | ARC-08 |
| Monolithic service module (too many public elements) | Split it by concept, into an acyclic graph | ARC-12 |
| Monolithic web UI module (too many screens) (T/R) | Split the independent UI flows (no destinations between them) into separate modules | ARC-12 |
| Monolithic mobile UI module (M) | Keep all flows in one module, but screens only as containers; content comes from per-area `_MCW` blocks | UI-05 |
| Client and server entities/logic not isolated (M) | Use a server `Account_CS` plus a per-app client module (`MB_Account_CS`, `MA_Account_CS`) | UI-05 |
| Team strongly coupled with another team | Use weak references (Service Actions) across teams; only Foundation apps may be strongly shared | ARC-14 |

## Performance
| Pattern | Fix | Rule |
|---|---|---|
| Unlimited records in Aggregate | Set Max. Records | DAT-10 |
| Unlimited records in SQL | Use `TOP n` / `ROWNUM` in the SQL itself: Max. Records only limits what is shown | DAT-10 |
| Aggregate or SQL inside a cycle / Inadequate data preparation | One query before the loop (join), or one SQL | DAT-10 |
| Sequence of connected Aggregates | Merge them into one aggregate with joins | PERF-13 |
| Inefficient empty list test | Use `List.Empty`, not `List.Count` (Count runs another query) | PERF-14 |
| Inefficient query count | A dedicated, simplified count query | PERF-14 |
| **Server requests in client events** (R) | No server calls in On Initialize / On Ready / On Render / On After Fetch; use data actions and aggregates | PERF-08 |
| **Multiple server requests inside a client action** (R) | Combine them into **one** server action (one request, one transaction) | PERF-15 |
| Long server requests timeout (R) | Module default server request timeout ≤ 10 s; prepare or cache data in advance | PERF-16 |
| Non-optimized local data fetch / local storage / not using local storage (M) | Fetch in data fetches, not client events; denormalized local entities; sync instead of many data actions | UI-05 |
| Incorrect / no asynchronous offline sync, bad-network handling (M) | `OfflineDataSync` with SyncUnits, `TriggerOfflineDataSync`, `OnSyncComplete`, `GetNetworkStatus` | UI-05 |
| Complex splash screen (M) | Minimal blocks, no server calls | UI-05 |
| CSS in the screen's style sheet (R) | Move it to a theme class | UI-04 |
| Inline CSS style | Use theme or block CSS, not extended `style` properties | UI-04 |
| Inline JavaScript (T) | Put scripts at screen or block level | UI-07 |
| Large image / large resource | Images under 150 KB (mobile) / 500 KB (web), max 1024 px; large resources external or in the DB | PERF-17 |
| Large session variable (T) | Keep only ids or context; store the rest in an entity keyed by session | PERF-18 |
| Site property update | Never update site properties in logic (it invalidates the module cache); use an entity | DAT-11 |
| Query data in ViewState / Large input parameter or local variable in ViewState (T) | Pass ids to screen actions and re-query | PERF-09 |
| Avoid long-running Timers (> 30 min) | Wake-timer pattern with checkpoints and partial commits | DAT-09 |

## Security
| Pattern | Fix | Rule |
|---|---|---|
| **Automatically generated publicly exposed REST endpoint** (R) | A server action called from an Anonymous screen is a public endpoint: remove Anonymous, or re-validate every input on the server | SEC-07, SEC-08 |
| Avoid Anonymous role on screens / **avoid Registered role on screens** | Use custom app roles (Registered = any user logged in to *any* app on the server) | SEC-07 |
| **Insecure usage of GetUserId on client context** (R) | Never pass the user id from the client as a parameter; call `GetUserId()` on the server | SEC-09 |
| **Insecure GetUserId in client block parameters** (R) | Same, for block input parameters | SEC-09 |
| Screen aggregates exposing system entities on anonymous/registered screens (R) | Remove them, or restrict the role and filter by `GetUserId()` in the aggregate | SEC-10 |
| SQL injection (T) / Vulnerable SQL injection (R) | Turn off Expand Inline. If unavoidable: `EncodeSql` on literals only, `BuildSafe_InClauseIntegerList/TextList` for IN lists, never `Replace` | SEC-02 |
| JavaScript or HTML injection (T) | Escape Content; `EncodeHtml`, `EncodeJavaScript`, `EncodeUrl`, `SanitizeHtml` | SEC-02 |
| Visible disabled button | Hide it (Visible = False) instead of only disabling it; and check on the server | SEC-11 |
| Exposed REST services are not secured | Use SSL/TLS and authentication on exposed REST (or Internal Access Only) | SEC-12 |
| **Exposed secrets in site properties** | Set **Is Secret = Yes** (Platform Server 11.25.0+): encrypted at rest and masked | SEC-03 |

## Maintainability
| Pattern | Fix | Rule |
|---|---|---|
| Duplicated code | Extract to a reusable action ("Extract to Action") | MNT-01 |
| Missing descriptions on public element or parameter | Describe the module, public elements and their parameters. Standard names (Id, Name, CreatedBy...) are exempt. | HSE-06 |
| **Unidentified public action managing transaction** | End the description with `[commit transaction]` / `[abort transaction]` | MNT-02 |
| Long undocumented flow (preparation or screen action > 20 nodes; action > 40 nodes) | Split the flow, and comment it | MNT-03 |
| Too much disabled code / unreachable logic (hard-coded True/False) | Delete it; remove stale feature flags | MNT-04 |
| Unused actions / unused aggregate or SQL | Delete them | MNT-05 |
| Reminder comments | Resolve them before promoting to QA | MNT-06 |
| Consuming deprecated element | Migrate to the replacement | MNT-07 |

## Using Code Quality in the SOP
- Check Code Quality within about 12 hours of finishing work (one sync cycle). Resolve every new finding before QA.
- Don't let findings, or TrueChange warnings, grow from release to release.
- A "Won't fix" decision needs a recorded reason. Example: Foundation apps allowed to expose strong references to other teams.
