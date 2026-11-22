# Integration and caching patterns

Source: OutSystems 11 docs: Service-oriented architectures, Integration Patterns for Core Services Abstraction, Hot Cache, Distributed caching, Microservices.

## Contents
1. The three service levels
2. Integration Wrapper Canvas (how to write an `_IS` action)
3. Data-need classification and pattern catalogue
4. Cache layers and hot cache
5. Distributed cache
6. Exposing APIs and versioning
7. Microservices in OutSystems

## 1. The three service levels
| Level | Module | Responsibility | Business logic? |
|---|---|---|---|
| External API | `<Concept>_API` | Exposes services to external consumers (REST/SOAP). Translates each consumer's format into internal structures, keeps several API versions, audits external calls. | No |
| Core Services | `<Concept>_CS` (+ `_BL`) | Business rules + core entities, **system-agnostic**: unaware of who consumes it and of which external system is the master. Often holds a **local cache** of legacy data. | Yes |
| Integration Services | `<Concept>_IS` | Technical wrapper of external producers. Normalizes structures and hides protocol, authentication, errors and retries. Can merge one concept spread over several systems (CRM + ERP → one Customer). | No |

Use one `_IS` **per concept**, not per external system. One system may serve several concepts with different lifecycles, and one concept may be spread over several systems.

## 2. Integration Wrapper Canvas
Every public `_IS` action does, in order:
1. **Validation / security**: check inputs, and that the user may make the call. Raise a user exception on failure.
2. **Authentication**: prepare credentials or tokens (OnBeforeRequest for headers such as API keys; read secrets from encrypted config).
3. **Map inputs**: normalized input → external format.
4. **Call and audit**: call the API and log the integration if a trail is needed.
5. **Normalize error handling**: turn error payloads and status codes into **exceptions**. Don't return error outputs.
6. **Normalize outputs**: external structures → the `_IS`'s own structures (`<Concept>_IS_<Purpose>`). **Never** expose the auto-generated REST/SOAP structures to consumers.
7. **Exception handling**: usually left to the caller. Use it here only to audit or to normalize messages that reach the UI.

## 3. Data needs and pattern catalogue
Classify the fields first:
- **Summary fields**: used for lists, search and joins. Stable (name, city).
- **Detail fields**: needed only for one record. Change more often or are sensitive (balance).

| Pattern | Use when | Pros | Cons |
|---|---|---|---|
| **Direct integration** | Live data is required, or a replica is forbidden | Always current | Many APIs (one per retrieval case), latency, load on the source, no aggregates or mashup |
| **Cold cache (summary) + batch sync** — *recommended default* | Summary data is searched or listed often | Simple, stable IS (one "get changed since" method), mashup with aggregates, less load | Data can be stale |
| **Isolated sync** (`_Sync` module) | Sync is complex, often tuned, or orchestrates several sources (customers before contracts) | Consumers are unaffected by sync code, and it is easy to remove when the legacy system is retired | One more module |
| **Real-time sync** | Summary fields must be current (e.g. vehicle position) | Always current | Source must call back via `_API`; high volume needs a **queue**, and concurrent updates need **ordering** |
| **Lazy-load details** | Details are reused after the first fetch | Fewer calls | Needs an expiry or last-updated check, a separate detail entity, and a cleanup timer |
| **Transparency service** | Same concept from several sources | Consumers see one replica | For writes: the `_IS` routes to one `_Drv` per system, all with the same signatures |

Sync rules:
- Sync **one way** (master → CS).
- Writes go **write-through**: commit to the master synchronously first, then update the cache.
- Use timestamp deltas.
- Use the timer rules in data-and-logic.md §8.

## 4. Cache layers and hot cache
Layers (use only what you need): **Client-side** (mobile local storage) → **Hot** (pre-calculated data for active processes) → **Cold** (normalized local replica) → **Staging** (raw import) → **Master of records**.
Most apps only need Cold. "Cache in Minutes" on actions and aggregates is the separate built-in in-memory cache on each server.

**Hot cache recipe**:
1. Design entities that fit the use case (e.g. a per-customer catalog with final prices) and put them in a `_BL` module (`Catalog_BL`).
2. Fill them from an engine module (`Promotion_Eng`) using timers or BPT processes triggered by business events (monthly catalog, weekly specials, a membership change).
3. Synchronize only what changed: recalculate just the affected records.
4. **Purge** inactive or old data, with heavy purges scheduled off-peak. Keep only active data.

## 5. Distributed cache
Worth it with many front-end servers, state shared across servers or apps, data moved out of Session, very short-lived data, large cached data (hundreds of MB), or a need for versioning and optimistic locking. The local cache is per server and unsynchronized.
- **Cache-aside**: read the cache; on a miss, read the store and put the result in the cache; invalidate or update the entry on writes. With read-only entities and CRUD wrappers, put the cache logic **inside the CRUD actions** so consumers don't see it.
- **Background data push**: a timer refreshes the cache for slow sources or data with a known update interval.
- Give each entry an expiry when it is created or updated.

## 6. Exposing APIs and versioning
- The `_API` module exposes REST endpoints that call BL/CS. It has no logic of its own, only authentication, mapping and auditing.
- Adding a new method is fine in the current version. A new **optional** attribute is non-disruptive. A new **mandatory** attribute or a renamed or retyped attribute is **disruptive**: publish a new version (`/v2`), keep the old one if consumers can't move, and deprecate it.

### Exposing logic to AI agents (`INT-07`)
Apps can serve **MCP tools** to outside AI agents — built in-house or with a Forge component (a community "MCP Server" component exists for O11; it is not an OutSystems product). Treat every tool as an exposed API: an `_API`-level module that only calls BL, authentication per client, authorization per tool **and per record** on the server (the agent acts with someone's rights), strict input validation, rate limits, and an audit of each call. Expose the smallest useful set of read tools first; writes need the same use-case discipline as any client. Review a third-party component's code, maintenance and security model before production. This is different from the **Service Studio MCP**, which lets agents edit your modules at design time (`references/service-studio-mcp.md`).

## 7. Microservices in OutSystems
- A standard installation already gives a service-oriented architecture. Real microservices (a separate infrastructure per service, REST only) lose RAD: no shared entities or aggregates, and no shared blocks.
- If you adopt them, build **Extended Services** on the consumer side: a local cache, blocks and composite logic over the REST API.
- Split infrastructures only between loosely coupled services. Start by isolating each service in its own DB catalog inside one infrastructure.
