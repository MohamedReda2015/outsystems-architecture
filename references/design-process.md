# Design process — from requirements to blueprint

Source: OutSystems 11 docs *From architecture to development*, *Translating business concepts into application modules*.

## The 3-step loop (repeat until stable, and again during implementation)
1. **Disclose**: list the user stories, functional requirements, non-functional requirements (browsers, devices, offline, performance, security) and **integration needs** (which external systems, master of which data, read or write, volumes, latency).
2. **Organize**: place each concept on the canvas:
   - user journeys go in End-User;
   - business concepts (entities and rules) go in Core;
   - integrations, themes and utilities go in Foundation.
3. **Assemble**: turn concepts into modules using the recommended patterns:
   - Join concepts that are conceptually related.
   - Don't join concepts that are too complex or have different lifecycles.
   - Isolate reusable logic from the integration logic that consumers don't care about.

## Choosing granularity
Balance a manageable number of modules against manageable complexity and lifecycle independence per module. Split for **complexity**, **independent lifecycles** (teams, sponsors) and **service isolation**.

## Integration decision (pick the pattern per concept)
- Must data always be live, with no replica allowed? → **Direct integration** through `_IS`.
- Data is searched, listed or joined often and changes rarely? → **Cold cache** of summary fields in `_CS`, filled by a batch sync (`_Sync`, or a timer in CS).
- Details are reused after the first fetch? → add **Lazy-load details**.
- Summary fields must be real-time? → **Real-time sync** callback through `_API` (queued or ordered for high volume).
- Several source systems hold the same concept? → a **Transparency service** (one `_Sync` that orchestrates, plus `_IS` with one `_Drv` per system for writes).
See integration-and-caching.md.

## Worked example (official Soccer Fields sample)
Requirements: list and search fields (by name, city, size) that come from an external REST API, and let players book them. Must be responsive and online.

| Module | Layer | Responsibility |
|---|---|---|
| `SoccerFields` | End-User | Screens to find and book fields (Home module). |
| `SF_Th` | Foundation | App theme, created first. |
| `Booking_BL` | Core | Booking logic composing the Field and Player concepts. |
| `Player_CS` | Core | Player entity and related entities. |
| `Field_CS` | Core | Local replica (cold cache) of the field summary. Entities are public and read-only, with CRUD actions `Field_Create` and `Field_CreateOrUpdate`. |
| `Field_Sync` | Core | Daily timer: reads `Field_IS`, writes `Field_CS`. |
| `Field_IS` | Foundation | Consumes the REST API, sends the API key in OnBeforeRequest, and exposes `Field_IS_GetSummaryFields` returning its own `Field_IS_Summary` structure. |

Applications:
- **Soccer Fields** (End-User app): `SoccerFields`, `SF_Th`, `Booking_BL`, `Player_CS`. These Cores are used only by this app, so they can stay here.
- **Field Core Services** (Core app): `Field_IS`, `Field_CS`, `Field_Sync`, all Blank modules with no screens.

## Blueprint deliverable
Use `templates/architecture-blueprint.md`:
- the concepts table;
- the canvas placement;
- a module table (name, layer, app, responsibility, public contract);
- the dependency list;
- the integration patterns chosen and why;
- open questions.

Validate it with `scripts/validate_architecture.py --strict` before building.
