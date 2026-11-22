# Editing modules through the Service Studio MCP / Model API

Read this only when an agent changes `.oml` modules through Service Studio's MCP server (`applyModelApiCode`, `getDataModel`, `omlMerge`, ...). The behaviour was verified by test on OutSystems 11 in late 2026. Re-check it against your version.

## Session and workflow
- Get a session token once (the user approves a dialog in Service Studio), and reuse it.
- The module must be **open in Service Studio**. Check with `listApps`.
- `startOmlEditSession` → small focused `applyModelApiCode` calls (one concern per call) → after each call, check `exceptionMessage` and every validation message of type Error → read the result back with `get*` → `omlMerge` → `endOmlEditSession`.
- Run at most **one call per module at a time**: parallel reads fail with "OML not found".
- **Dependencies can't be added by the tool.** Stop and ask the user to publish the producer and add the reference in Manage Dependencies, **then click Apply**. Users have said "done" before applying. Probe `eSpace.References` and report what is missing. While an edit session is open, end it and start a new one to see new references (`omlReset` is not enough).
- After publishing a producer, refresh references on the consumer, then publish the consumer. `omlPublish` ends the edit session. Publish only when the user asks.
- If publish or refresh tools reject the call for a missing session token, call the MCP HTTP endpoint directly with the token in the arguments, from a script.
- Large modules take minutes per call: raise the MCP read/write timeout (e.g. 600 s) and call through a script with a long timeout, or do the change by hand.
- Keep long lambdas in files and run them from a small caller script, so large outputs stay out of the agent's context.

## Model API facts that are easy to get wrong
- `CreateServerEntity` / `CreateStaticEntity` come with **no attributes**: create `Id`, set `IsAutoNumber = AutoNumber.Yes`, set `entity.IdentifierAttribute`. Folders for entities use `ESpaceTreeFolder.ServerEntities`.
- Set entity `Public` and `ExposeReadOnly`. A foreign key is `attr.DataType = other.IdentifierType` with `DeleteRule`. Indexes: `CreateIndex()`, `.Unique`, `.AddAttribute`.
- `CreateServiceAction` (and sometimes `CreateServerAction` in Service modules) has **no Start or End node**: create them.
- New blocks are **not public** by default: set `block.Public = true`.
- Static records resolve as `Entities.<Static>.<Record>` only when the static entity is an explicit dependency.
- Aggregates in logic: `CreateNode<IAggregateNode>`, `AsDatabaseAggregate.CreateSource / CreateJoin / CreateFilter / CreateSort` (`SortDirection = Sort.Descending`), `SetMaxRecords`.
- `dynamic` is not available in the sandbox. LINQ, `Dictionary` and local functions work.
- Translations can't be written through the API: use Service Studio's export and import.
- **Block stylesheets**: appending to a non-empty `StyleSheet` merged but was **not deployed**. CSS set on a block in the same merge that created it does deploy. Keep CSS in small style-only blocks, and recreate the block (and its instances) to change the CSS. After publishing, fetch the served CSS file to verify.
- A client expression can't use `Check<Role>Role()` (the validator rejects it).
- Some screens return empty from `getScreen`: walk them with `GetAllDescendantsOfType<T>()` in a read-only probe instead.

## Safety
- Treat read-only probes (code that throws its findings without changing anything) as the default first step.
- Never change modules the user did not name. Never publish to shared environments without approval.
