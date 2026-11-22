# Performance standards

Sources: OutSystems 11 docs *Performance Top 10 Rules*, *Performance Best Practices – References*, *OutSystems Platform Best Practices: Performance*, and *Code analysis patterns: Performance*. Also project experience.

## Top 10 (official)
1. **Index your entities** on the attributes used in filters, sorts and joins.
2. **Set up database maintenance plans**: rebuild indexes, update statistics, back up transaction logs often, tune file growth. Involve the DBA.
3. **Start from Service Center reports** (slow screens, queries, timers, integrations, extensions) before tuning anything.
4. **Don't join over a linked server**: the remote table is loaded completely.
5. **Tune web server memory** (.NET process recycling, JVM settings). Prefer 64-bit.
6. **Isolate large text and binary data**: text over 2000 characters becomes a slow type. Use a 1-to-1 extension entity and fetch it only when needed.
7. **Avoid long-running timers and batch jobs**: process in parts, auto-timeout, re-wake. Code Quality flags timers that run over 30 minutes.
8. **Keep screen preparation light** (Traditional Web) and **keep client events free of server calls** (Reactive).
9. **Don't use preparation data in screen actions** (Traditional Web ViewState).
10. **Fetch only the fields you need**: use dedicated Structures as action input and output.

## Queries
- Use Max. Records on every list aggregate, and `TOP` / `OFFSET-FETCH` / `ROWNUM` **inside** SQL.
- No aggregates or SQL inside loops. Merge **chains of connected aggregates** into one with joins.
- `List.Empty`, not `List.Count`. Use a dedicated count query when you need a count.
- Iterate once; no `[i]` indexing; no type casts in filters.
- Archive old data into separate entities. Purge logs, history and audit data on a schedule.
- Use delete rules on purpose (cascading deletes on big tables are expensive).

## Reactive / Mobile
- **No server calls in On Initialize / On Ready / On Render / On After Fetch.**
- **One server request per user action**: combine sequential server calls into one server action.
- Use Fetch On Demand for data that isn't needed right away. Pass data down to blocks in lists, and don't re-query per item.
- Default server request timeout ≤ 10 s.
- Mobile: local storage first, a small denormalized local model, asynchronous sync, a simple splash screen.
- Keep CSS in the theme (screen CSS causes flicker), and keep images and resources within the size limits.

## Server logic
- Keep session variables small (Traditional Web). Compound or list session variables slow every request.
- Never update site properties at runtime: it invalidates the module cache.
- Use "Cache in Minutes" for expensive reads that rarely change (reference data, menus).
- Avoid chained web service calls: return as much as possible in one call. Use asynchronous logic (BPT, timers, Light BPT) for work the user doesn't need to wait for.
- Prefer **public actions** to **local web services** (local web services use threads per call), but weigh this against the extra reference complexity. No circular references.
- Use **connection pooling** for external databases accessed from extensions.

## Infrastructure and operations
- Use a dedicated front-end or zone for timers, and stagger timer schedules.
- Configure virtual memory and system settings according to the OutSystems checklist.
- Watch the slow-query and slow-integration reports regularly. Fix problems before users notice them.

## Module health signals (official guidance)
- A module larger than about **4 MB** usually points to poor architecture (large resources, too many concepts). Split it, and move resources out.
- More than about **20 site properties** in one module points to bad design.
- Modules with too many public elements or screens (Code Quality "monolithic" patterns) should be split by concept or UI flow.
