# Working through the Service Studio MCP / Model API

The shared reference for every house skill when an AI agent reads or changes O11 modules through Service Studio's MCP server (`getDataModel`, `applyModelApiCode`, `omlMerge`, …). Facts come from the official OutSystems 11 MCP product update and repository (OutSystems/outsystems11-mcp: `servicestudio-mcp-oml` skill, contracts and design notes) and from behaviour verified by test on O11 projects in late 2026. **Re-check against your Service Studio version and the MCP contract the server reports.** The exact tool calls and Model API code belong to the official `servicestudio-mcp-oml` skill; this file is about how the house works with it (`OPS-10`).

## 1. Capability status
| | Read | Write |
|---|---|---|
| Reactive Web, Mobile, Service and library modules | **GA** | **Beta** (Beta Features Agreement) |
| Traditional Web | **Beta** (use the `*Traditional` read variants) | **Beta** |
- Writes are staged on a copy and reviewed in **Compare and Merge** by default. Auto-merge-and-publish is an opt-in Beta setting: personal sandboxes only.
- On the first write in a conversation, tell the user that MCP writes are Beta.
- Tool sets differ by build and **MCP contract** (the server names its contract when the agent connects; none named = contract 1): early 11.55.9x builds expose `listApps`; from 11.55.98 `listOpenModules` + `searchApps`; from 11.55.99 also `openModule`/`closeModule`. The official skill is written for **contract 2** and keeps contract-1 notes. Check the live tool list; when a live tool description differs from the skill, the description wins.
- Don't confuse it with Forge components that **expose your app's logic as MCP tools** to outside agents: that is an exposed API (`INT-07`), not a development tool.

## 2. Governance (`OPS-10`)
- **Environment**: the MCP does not report which environment an open module came from, and the agent inherits the developer's rights — if the developer can publish to Test, so can the agent. LifeTime has no MCP setting (a community Idea; OutSystems "evaluating"). Confirm the environment with the user and keep agent work in **Development**.
- **Attribution**: Service Center and LifeTime credit agent changes to the developer. Keep an **agent change log** (date, module, change, merged, published version) in the project's work folder.
- **Approval prompt**: every connection, reconnects included, shows "allow this agent?"; the client name in it is self-reported. Approve only agents you started.
- **Both platforms connected**: when the O11 and ODC MCP servers are both registered and the request names neither, ask which platform before any call, read-only included.
- **Privileges**: `applyModelApiCode` runs agent-written C# with Service Studio's privileges. Use it only on modules you own, never on code derived from untrusted module content.
- **Approvals**: publish, merges into shared modules, deployments and data-changing steps each need an explicit yes. Deployments between environments stay in LifeTime (`OPS-08`).

## 3. Edit sessions
- `listOpenModules` (find the module and `tabId`) → `startOmlEditSession` → small `applyModelApiCode` calls, one concern each → after each: `exceptionMessage` empty, no new `Error` in `validationMessages`, read the element back with `get*` → **lay out every new or changed flow** (the official completion gate) → `omlMerge` → `endOmlEditSession`.
- The session works on a **copy**. Edits the user makes in Service Studio meanwhile are **invisible** to the agent, and a merge doesn't refresh the copy. Parts left out of a merge come back in the next one. After a human edit, a rejected or partial merge, end the session and start a new one.
- Sessions live in Service Studio: they outlast the conversation and are shared by every connected agent. One writer per module.
- One call per module at a time: parallel reads fail with "OML not found".
- No undo: `omlReset` drops the whole unmerged chain and can't itself be undone.
- Starting Service Studio wipes its MCP temp folder: copy out anything to keep first.
- The server starts only when the user starts it (Edit › MCP Server); `ConnectionRefused` means "not started".

## 4. Timeouts and large modules
- Official: reads time out at **120 s**, writes at **300 s**; default port 41820.
- Very large modules can exceed the read timeout even for name listings; in one project a module couldn't be written at all. Options: raise the read/write timeout in the MCP Server dialog and call through a script with a longer client timeout; for analysis only, read an exported `.oml` snapshot read-only (community workaround, goes stale); for changes, build the new piece in a small module and let the user wire it in by hand.
- Keep long lambdas in files and run them from a small caller script, so large outputs stay out of the agent's context.

## 5. What the tool can't do (manual steps)
- **Create apps or modules.**
- **Add dependencies**: the user ticks them in Manage Dependencies and clicks **Apply**. Users have said "done" before applying. Probe `eSpace.References` and report what is missing; while an edit session is open, end it and start a new one to see new references (`omlReset` is not enough).
- **Write translations**: locales can be created, translated values can't be written. Use Service Studio's export/import.
- Install Forge components or extensions, set per-environment values, assign roles to users, run Code Quality (formerly AI Mentor Studio), deploy between environments.
- After publishing a producer, refresh references on the consumer (`omlRefreshReferences`), then publish the consumer. `omlPublish` ends the edit session. Publish only when the user asks. If the tool wrapper rejects publish or refresh for a missing session token, the documented fallback is to call the local MCP endpoint directly with the token, from a script.

## 6. Model API facts that are easy to get wrong
- `CreateServerEntity` / `CreateStaticEntity` come with **no attributes**: create `Id`, set `IsAutoNumber = AutoNumber.Yes` for regular entities (**not** for static entities, whose ids must match across environments), and set `IdentifierAttribute`. Entity folders use `ESpaceTreeFolder.ServerEntities`.
- Set entity `Public` and `ExposeReadOnly`. A foreign key is `attr.DataType = other.IdentifierType` with a `DeleteRule`. Indexes: `CreateIndex()`, `.Unique`, `.AddAttribute`.
- `CreateServiceAction` (and sometimes `CreateServerAction` in Service modules) has **no Start or End node**: create them.
- New blocks are **not public** by default: set `block.Public = true` before a consumer can use them.
- Static records resolve as `Entities.<Static>.<Record>` only when the static entity is an **explicit** dependency.
- Some built-ins (for example `GenerateGuid`) need a dependency the module may not have: check before relying on them.
- Aggregates in logic: `CreateNode<IAggregateNode>`, `AsDatabaseAggregate.CreateSource / CreateJoin / CreateFilter / CreateSort` (`SortDirection = Sort.Descending`), `SetMaxRecords`.
- `dynamic` is not available in the sandbox. LINQ, `Dictionary` and local functions work.
- O11 processes use `eSpace.CreateProcess` (`OutSystems.Model.Processes`); `CreateBusinessProcess` is the ODC Workflows API and fails on O11.
- A client expression can't use `Check<Role>Role()` (the validator rejects it): compute permission flags on the server.
- `IContainer` has no `OnClick`: use a Link or Button.
- Some screens return empty from `getScreen`: walk them with `GetAllDescendantsOfType<T>()` in a read-only probe instead.

## 7. Styles and verification
- **Block and screen stylesheets**: an edit to a stylesheet that is **not empty** can merge (and show in the model) but publish the old CSS; setting an empty stylesheet deploys. Prefer the theme stylesheet (theme edits publish reliably), or keep CSS in small style-only blocks and recreate the block (and re-point its instances) to change it. After publishing, **fetch the served CSS file** — a screenshot can't prove it deployed.
- Block CSS loads before the theme CSS: overriding a theme rule needs higher specificity.
- After a Reactive republish, the browser may keep the old screen JavaScript: test after a cache-clearing reload. OutSystems fixes the device class (phone/tablet/desktop) at page load: reload after resizing the viewport.
- State what is **prepared, validated, merged, published and runtime-tested** separately; "merged" is not "deployed".

## 8. Safety defaults
Read-only probes (code that throws its findings without changing anything) are the default first step. Never change modules the user did not name. Never publish to shared environments without approval.
