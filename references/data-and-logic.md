# Data and logic standards

## Contents
1. Entities
2. CRUD wrappers and audit columns
3. Soft delete
4. Structures and action signatures
5. Service Actions vs Server Actions (transactions)
6. Queries (aggregates and SQL)
7. Exceptions
8. Timers and batch jobs
9. Configuration (site properties, config entities)
10. Roles and authorization
11. BPT / processes
12. Flow readability (code style)

## 1. Entities
- Entities are singular, live in a folder per concept in `_CS`, and are set `Public = Yes`, `Expose Read-Only = Yes`.
- Every entity gets an explicit Id (AutoNumber long integer unless there is a reason not to) and a Description.
- Foreign keys are typed as the referenced entity's identifier, with an explicit **Delete Rule**: `Protect` by default, `Delete` only for owned children, `Ignore` only for logs and history.
- Mark mandatory attributes. Set text **lengths** deliberately. Text over 2000 characters becomes a slow large-text column: move it, and any binary data, into a **1-to-1 extension entity** and fetch it only when needed.
- Use **static entities** for fixed lists (statuses, types). Reference records as `Entities.<Static>.<Record>`, never by literal id. A consumer that uses static records by name needs the static entity as an explicit dependency.
- Add **indexes** for attributes used in filters, sorts and joins. Add unique indexes for natural keys.
- Mark multi-tenant entities deliberately (see security.md).

## 2. CRUD wrappers and audit columns
- Writes go through public `<Entity>_Create / _Update / _CreateOrUpdate / _Delete` in `_CS/CRUD`. These wrap the built-in entity actions.
- Standard audit columns on business entities: `CreatedBy` (User Id or an actor text such as `IDP:<externalId>` for external users with no platform user), `CreatedOn`, `UpdatedBy`, `UpdatedOn`. **The CRUD wrapper sets them**, and callers never assign them. Lesson learned: when both the callers and the wrapper set them, values drift.
- For change history, keep a `<Entity>History` entity (or call Audit_Lib) inside the wrapper. See audit-trail.md.
- Bulk updates (SQL) bypass the wrappers. Audit the operation as a whole and document the exception.

## 3. Soft delete
When records must be recoverable or auditable:
- Add an `IsDeleted` boolean (plus `DeletedBy` and `DeletedOn` if needed) and make `<Entity>_Delete` set it.
- **Every** query that reads the entity filters `not <Entity>.IsDeleted`, including joined children. For outer joins: `Child.Id = NullIdentifier() or not Child.IsDeleted`.
- Review tip: search for every aggregate or SQL on the entity and check the filter. Missing one filter is the classic bug.

## 4. Structures and action signatures
- Structures live in `_BL` (house standard) and are public, named by purpose.
- Actions take and return **Structures that carry only the fields needed**, not whole entity records, because wide records move unnecessary data and tie consumers to the data model.
- Input validation happens at the **top of the public action**. Raise a user exception with a clear message, and never return error flags that callers can ignore.
- Every public action, parameter and structure attribute gets a Description.

## 5. Service Actions vs Server Actions
Official comparison, from *Use Services to Expose Functionality*:

| | Server Action (public) | Service Action |
|---|---|---|
| Dependency | **Strong**: consumers must be refreshed and republished when the implementation changes | **Weak**: an implementation change takes effect immediately |
| Execution | In the caller's process, request and **transaction** | Remote call (REST) in **its own process and transaction** |
| Rollback | Rolls back with the caller | A caller's rollback does **not** undo it, and it doesn't undo earlier Service Actions |
| Session context | Same session | Only **UserId, TenantId, Locale and Request Key** are passed. `GetUserId()` and `Check<Role>Role()` work; session variables don't. |
| Reach | Same environment | Same environment only, with impact analysis in Manage Dependencies |
| Failure modes | Exceptions | User exceptions **and Communication exceptions** (network or timeout) reach the consumer |

Rules:
- Use Service Actions for the BL's public contract between apps and teams (lifecycle independence). Use Server Actions inside one app or module group when a shared transaction is required, and for CS CRUD.
- **Thin Service Action pattern**: `FileRequest_Submit` (Service Action) → `FileRequest_Submit_Logic` (private Server Action) holds the multi-step logic, so everything commits or rolls back **together**. The `_Logic` action can also be rebuilt safely while the public contract stays the same.
- A sequence of Service Actions is **not** atomic. Design a compensating action, or put the whole sequence behind one Service Action that calls Server Actions in a single transaction.
- Keep Service Action payloads small (remote call cost). Handle `CommunicationException` in consumers.
- Versioning: a breaking signature change creates a new action (`Customer_GetV2`, or `CustomerGetV2` under the no-underscore convention). Keep V1 until every consumer has moved, then deprecate it (Code Quality flags consumers of deprecated elements).
- A public action that commits or aborts the transaction says so at the end of its description: `[commit transaction]` / `[abort transaction]` (Code Quality pattern).

## 6. Queries
- Prefer **Aggregates**: they are optimized, fetch only the used columns, and are refactor-safe. Use **SQL** nodes for what aggregates can't express (complex grouping, bulk operations, DB functions). Parameterize them, never concatenate user input, and set **Expand Inline** only for trusted, sanitized values.
- Set **Max. Records** for lists and paginate on screens. In SQL, limit rows **in the statement** (`TOP n`, `OFFSET/FETCH`, `ROWNUM`). An SQL node's Max. Records only limits what is displayed, not what is fetched.
- Don't run queries inside loops. Join or batch instead. Merge **chains of aggregates** that feed each other into one aggregate with joins.
- Test for "no results" with `List.Empty`, **not** `List.Count` (Count runs another query). Write a dedicated, simple count query when you really need a count.
- Iterate query output once with For Each. Avoid index access (`List[i]`) in loops.
- Avoid type casts in aggregate filters and joins: they block index use.
- Don't put business logic in SQL. Indent and comment SQL, and remember that SQL is database-specific.
- Don't join across a linked server (the remote table is loaded completely).
- Sort descending in aggregates with the sort direction (or `ListSort` in logic).
- Avoid entities with hundreds of attributes. Split them by usage, e.g. a 1-to-1 extension.

## 7. Exceptions
- Define **user exceptions** per module for business errors (`InvalidRequest`, `NotAuthorized`). Raise them with a user-friendly message.
- Handle exceptions at the **boundaries**: screen or block actions and timer entry points. A global `OnException` lives in the Front-End or theme, and the Major App in mobile.
- In handlers: `Abort Transaction` when the work must roll back, and `Log Error` for unexpected exceptions. Never swallow exceptions silently.
- Order handlers from **specific to general**: user exceptions, then Database or Communication exceptions, then **AllExceptions** as the safety net. A handled exception never reaches the global handler, so log it where you handle it.
- Use **one standard logging action** (in a Foundation `_Lib` or Audit_Lib). It records the module, the action, the key inputs (masked), the user, the message, and a correlation id or Request Key.
- Messages shown to users are business language: what happened, and what to do next. Technical detail goes to the log only.
- Service Actions: user and communication exceptions reach the consumer, so catch them at the consumer boundary and translate them.
- Exposed REST APIs have no global handler. Catch exceptions in each method and return proper HTTP status codes and error bodies.
- For APIs and service contracts that must report several functional errors at once, return a result Structure (`Success`, `Messages[] {Code, Text}`) and keep exceptions for exceptional cases.
- Integrations turn external error responses into exceptions inside the `_IS` (normalize errors).

## 8. Timers and batch jobs
Timers must never time out, never repeat work, finish the job, and keep data consistent:
- Set a **logical timeout** (e.g. 10 minutes) below the platform timeout.
- Process in **batches**. Save progress in a control entity (last processed id or timestamp, current page). Commit per batch (`CommitTransaction`).
- When the logical timeout is reached, save progress, **wake the timer again** (`Wake<Timer>`) and end.
- Use delta sync with timestamps (only changed records). Schedule heavy jobs off-peak.
- Keep timer logic in Core modules (`_Sync`, `_Eng`, or the `_CS` / `_BL` that owns the data), not in UI modules.
- Name the action a timer runs `Timer_<Name>` (official convention), and use it only from that timer.
- Platform facts:
  - The default timeout is 20 minutes, and timers that fail are **retried automatically**, so non-idempotent logic will reprocess data.
  - Code Quality flags timers that run over 30 minutes.
  - Timers and BPT activities run in their **own session**: session variables start at their defaults.
- Add a **kill switch** and an **enable flag** (a config entity or site property read at runtime) so a timer can be stopped without a deployment.
- **Log every run**: start, end, status (success, partial, failed), counts and errors. Show the runs in a small back office.
- Stagger schedules so heavy timers don't all start together. Use a dedicated timer server or zone for heavy loads.
- Process each record in isolation: catch the error per record, mark it failed, and continue. Commit every *n* records.

## 9. Configuration
- **No hard-coded** URLs, endpoints, keys, phone numbers, thresholds, email addresses or feature switches.
- Use **site properties** (in the module that uses them, usually `_BL` or `_IS`) for simple environment-specific values, with a Description and a safe default.
  - **Never update site properties from application logic**: it invalidates the module cache (a Code Quality pattern). Values that change at runtime belong in an entity.
  - More than about 20 site properties in one module usually means bad design. Move them to a configuration entity.
  - LifeTime doesn't migrate site property values: set them per environment and document them in the deployment notes.
- Use **static entities** instead of hard-coded values for fixed lists and codes.
- Use **configuration entities** with a small back office for values that business users change, or that are lists.
- **Secrets** (client secrets, API keys): use a site property with **Is Secret = Yes** (Platform Server 11.25.0+; encrypted and masked). On older platforms, use an encrypted config entity decrypted only on the server. Reuse an existing shared configuration (e.g. an identity-provider config module) instead of duplicating secrets into new site properties.
- Test overrides (e.g. "send all SMS to this number") are site properties that are empty in production, and the code checks them explicitly.

## 10. Roles and authorization
- Define roles in `_BL` (or the theme for transversal job roles) as **public**.
- Check authorization **on the server**, inside the BL action (`Check<Role>Role(GetUserId())` plus record ownership), as well as on the screen's role settings. Client-side checks are only for UX. Identity is never a parameter from the client.
- Screens: untick "Anonymous" and "Registered" unless intended, and tick the specific roles.
- Full rules, including use-case write actions instead of passing whole records: security.md.

## 12. Flow readability (code style)
- Lay out flows **vertically**, top to bottom. Put the main branch, and exception or error branches, **to the right**. Start loops on a diagonal. Avoid crossing arrows.
- Give every Assign, If and Switch a meaningful **label**. Comment complex logic. Fill in descriptions and example strings for expressions.
- Keep actions small: one task each. Code Quality flags screen actions or preparations over about 20 nodes and other actions over about 40 nodes without comments. Use "Extract to Action".
- Remove disabled code, unreachable branches (hard-coded True/False), unused actions and queries, and reminder comments before QA.

## 11. BPT / processes
Use BPT processes for long-running, event-triggered workflows (e.g. rebuilding a customer's catalog after a sale). Keep activities small and idempotent. Put processes in Core modules, next to the entity that triggers them.
