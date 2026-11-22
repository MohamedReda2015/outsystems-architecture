# OutSystems standards — core rules (compact, for any agent)

You are working on OutSystems 11. The full skill is in the `outsystems-architecture/` folder. `SKILL.md` is the entry point, and the `references/` files hold the details. Read the relevant reference before designing, building, securing or reviewing. These core rules always apply.

**Precedence**: project choices govern supported conventions; house rules supply defaults. Installed contracts and official version-matched documentation determine platform behavior. Escalate unresolved material conflicts, not routine preference differences.

**Architecture Canvas (3 layers)**:
- End-User: screens, never reusable.
- Core: `_CS`, `_BL`, `_CW`, `_Sync`, `_Eng`, `_API`; mobile `_MCS`, `_MCW`, `_MUI`.
- Foundation: `_Lib`, `_IS`, `_Th`, `_Pat`, `_Drv`.

The Canvas rules below apply to strong references between modules/applications; Service Actions, screen destinations and data-type-only references are weak. Mixed pairs remain strong. House sublayer checks are separate:
- no upward references;
- no side references between End-User modules;
- no cycles between Core or Foundation modules;
- a `_CS` never consumes BL, CW, API, Sync or Eng.

An app sits in the layer of its highest module. One owner and one sponsor per app.

**House 4-module pattern (strict)**: `<App>_Front_End` → `<App>_CW` → `<App>_BL` → `<App>_CS`.
- CS: Public + Expose Read-Only entities, and CRUD wrappers (audit columns, integrity checks, no role checks, never called from the client).
- BL: all Structures; thin Service Actions (auth check → private `_Logic`); use-case write actions that take only the allowed fields.
- CW: public blocks that call BL and raise Events.
- FE: screens hosting CW blocks, with custom roles.

**Reactive/Mobile security**:
- Every client-called aggregate, data action and server action is a REST endpoint.
- No Anonymous or Registered screens unless intended.
- `GetUserId()` only on the server, never passed from the client or through block parameters.
- Role **and** record-ownership checks in BL.
- No whole-record writes from the client.
- No sensitive data in client variables or screen parameters.
- Secret site properties use Is Secret.

**Always**:
- Inventory and reuse before creating.
- Wrap external systems in `<Concept>_IS` with normalized structures and errors raised as exceptions.
- Pass Structures with only the needed fields.
- Filter soft-deleted rows in every query.
- No server calls in client events; one server call per user action.
- Timers: `Timer_` prefix, batches, logical timeout, commit, re-wake, kill switch.
- Max. Records / `TOP`; `List.Empty`.
- Large text and binary data in extension entities.
- Never update site properties in logic.
- Report only what you verified.

**Never**: publish to Production or run destructive operations without explicit approval; invent data sources; expose auto-generated REST structures; ship test screens or test apps beyond QA.

**Reviews**: cite rule IDs from `references/review-checklist.md`. Map Code Quality findings with `references/code-quality-patterns.md`. Validate dependencies with `scripts/validate_architecture.(py|mjs) deps.json --strict`.
- Use `references/verification-and-reliability.md` for evidence and domain acceptance checks. Distinguish prepared, validated, merged, published and runtime verified; preserve task scope and existing authorization.
