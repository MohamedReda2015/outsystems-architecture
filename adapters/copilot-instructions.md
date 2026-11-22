<!-- Copy to .github/copilot-instructions.md (GitHub Copilot) or paste into any assistant's custom instructions. -->

# OutSystems standards

When helping with OutSystems 11 work, follow the `outsystems-architecture` skill:
- Read `outsystems-architecture/SKILL.md`, and the `references/` file for the topic at hand.
- Apply the always-on rules in `outsystems-architecture/adapters/core-rules.md` (included below for assistants that cannot open files).

<!-- BEGIN core rules: keep in sync with adapters/core-rules.md -->
Project architecture chooses supported conventions; the house chain supplies defaults. Installed contracts and official documentation determine platform facts. Flag unresolved material conflicts.

Canvas rules for modules and apps:
- No upward references.
- No side references between End-User modules.
- No cycles between Core or Foundation modules.
- A `_CS` never consumes BL, CW, API, Sync or Eng.

Module contents:
- CS: read-only public entities + CRUD wrappers (audit columns, no role checks, never called from the client).
- BL: Structures; thin Service Actions with authorization checks over private `_Logic` actions; use-case write actions with only the allowed fields.
- CW: blocks that use BL and raise Events.
- FE: screens hosting CW blocks, with custom roles.

Reactive security:
- Client-called aggregates and actions are REST endpoints.
- No Anonymous or Registered screens unless intended.
- `GetUserId()` server-side only, never a parameter.
- Role + ownership checks in BL.
- No whole-record writes from the client.
- Secret site properties use Is Secret.

Always:
- External systems behind `<Concept>_IS` with normalized structures and errors raised as exceptions.
- Only the needed fields.
- Soft-delete filters in every query.
- No server calls in client events; one server call per user action.
- Diagnose before fixing: exact symptom and environment, evidence, one falsifiable hypothesis at a time, read-only until the fix is asked for.
- Automated deployments: LifeTime API with a service-account token in an environment variable; one plan per run; agents never deploy to Pre-Production/Production, never publish modules.
- Timers: `Timer_` prefix, batches, timeout, re-wake.
- Max. Records / `TOP`; `List.Empty`.
- Large text and binary data in extension entities.
- No site property updates in logic.
- Verify before reporting.
- No Production publishing without approval.
- Use `references/verification-and-reliability.md` for evidence and domain acceptance checks. Distinguish prepared, validated, merged, published and runtime verified; preserve task scope and existing authorization.
<!-- END core rules -->
