# Architecture blueprint — <Application name>

Version: <n> · Date: <yyyy-mm-dd> · Author: <name/agent> · Rules mode: strict | relaxed (reason)

## 1. Scope and requirements
- **Functional**: <user stories>
- **Non-functional**: <devices, browsers, offline, performance, security, languages>
- **Integrations**: <system · master of which data · read/write · volume · latency>

## 2. Concepts on the canvas
| Concept | Layer (End-User / Core / Foundation) | Notes |
|---|---|---|

## 3. Modules
| Module | Layer | Application | Type (Reactive / Blank / Service / Library / Mobile) | Responsibility | Public contract (key Service Actions / blocks / entities) |
|---|---|---|---|---|---|

## 4. Applications
| Application | Layer (highest module) | Owner | Sponsor / LOB | Modules |
|---|---|---|---|---|

## 5. Dependencies
| Consumer | Producer | Elements | Strong / weak |
|---|---|---|---|

Validator result: `python scripts/validate_architecture.py deps.json --strict` → <PASS / findings>

## 6. Patterns chosen
| Concept | Pattern (direct / cold cache + sync / real-time / lazy / transparency / hot cache / audit) | Why |
|---|---|---|

## 7. Configuration, security and roles
- Site properties / config entities: <name · module · purpose>
- Roles: <role · where checked>
- Secrets: <where stored, how read>

## 8. Open questions and decisions
| # | Question / conflict | Decision | Decided by |
|---|---|---|---|


## Evidence and acceptance

- Platform/app type, installed versions/theme where relevant, target environment:
- Existing project decisions and authorized delivery scope:
- Requirement → element/contract → source of data → verification evidence:
- Concurrency, retry/unknown outcome, authorization and failure cases relevant to this change:
- Delivery status: prepared / model validated / merged / published / runtime verified (record only observed stages):
- Not tested, missing dependency or blocked evidence, and the exact next step:
