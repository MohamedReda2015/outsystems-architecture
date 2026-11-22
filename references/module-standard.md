# House module standard — Front_End → CW → BL → CS

This is the default way to build a business capability. It narrows the official Architecture Canvas into one predictable pattern, so that every app built by the team looks the same and any agent can find any element.

## Contents
1. The modules and their contract
2. Allowed dependencies (strict and relaxed)
3. Folder layout per module
4. Naming conventions
5. Supporting module types
6. When to add or split modules

## 1. The modules and their contract

### `<App>_CS` — Core Services (Core layer)
**Contains**
- Entities, each concept in its own folder (`Entities/FileRequest`, `Entities/FileTemplate`, ...). Static entities go in `Lookups`.
- For every entity: `Public = Yes`, **`Expose Read-Only = Yes`**.
- Public **CRUD server actions** in folder `CRUD`: `<Entity>_Create`, `<Entity>_Update`, `<Entity>_CreateOrUpdate`, `<Entity>_Delete` (soft delete where required). They wrap the platform's built-in entity actions and are the only way to write data. They also set the audit columns (`CreatedBy`, `CreatedOn`, `UpdatedBy`, `UpdatedOn`), so nobody can forget them.
- Large text or binary data lives in a 1-to-1 extension entity (e.g. `FileRequestFile` + `FileRequestFileContent`).
- Indexes on the attributes used in filters, sorts and joins.

**Must not contain**: Structures, business rules, UI, integrations. Validations that are **always true for the entity**, whatever the use case, *may* live in the CRUD wrapper: mandatory fields, formats, uniqueness, referential integrity. This is MVP consensus on the OutSystems forum. Rules that depend on use case, role or other data belong in BL.
CRUD wrappers **don't check roles**. Only BL, timers and processes call them, never client logic directly (security.md §2–3).

**Why**: read-only exposure makes every write go through one place, which gives consistent audit, validation and cache invalidation, and keeps the data model stable for its consumers. It is also an official Code Quality pattern ("Public Entities aren't read-only").

**Don't put the whole data model in one module.** OutSystems recommends modules as *functional units*: one CS per business concept or cluster (`Customer_CS`, `Order_CS`), not one giant `Data_CS` for the whole factory.

### `<App>_BL` — Business Logic (Core layer)
**Contains**
- **All Structures** of the app (DTOs), public, in folder `Structures`. Name them by purpose, e.g. `FileRequestSummary`, `FileRequestDetail`, `FileRequestSaveInput`.
- **Public Service Actions** in `ServiceActions`: the module's contract to the layers above. Keep them **thin**: check authorization (role + record ownership, with `GetUserId()` on the server), validate input, call a private `<Name>_Logic` server action, return Structures.
- **Use-case write actions** take only the fields the user may change (`Order_Save(OrderId, DeliveryDate, Notes)`). Never a whole entity record from the client (prevents mass assignment).
- **Private server actions** in `PrivateActions`: rules, validation, calculation, aggregation, orchestration. Multi-step writes live here, so they share one transaction (see data-and-logic.md).
- Integration orchestration in `Integrations` (calls into `_IS` modules).
- Roles (public, for server-side checks), site properties (configuration), user exceptions.

**Consumes**: CS entities and CRUD actions, `_IS` modules, Libraries.

### `<App>_CW` — Core Widgets (Core layer)
**Contains**
- Reusable Reactive **Blocks** grouped by concept (`Blocks/FileRequest/...`), set `Public = Yes`.
- Blocks get their data from **data actions that call BL Service Actions**, and render BL Structures.
- **UIHelpers**: client actions and functions for presentation only (format currency, mask an ID, build a CSS class).
- Blocks communicate outward through **Events** (e.g. `OnSaved`, `OnNavigate`). They never navigate to another module's screens themselves.

**Must not**: reference CS entities or CRUD actions; contain business rules.

### `<App>_Front_End` — End-User
**Contains**: screens, grouped into UI flows by journey. Each screen sets its layout, places CW blocks, passes input parameters, handles block events (navigation, feedback messages) and declares the roles allowed to access it.
**Must not**: call BL Service Actions or CS directly (in strict mode), or hold reusable logic.

## 2. Allowed dependencies

### Strict mode (default house standard)
| From \ To | CS | BL | CW | FE | _IS | _Lib / _Th / _Pat | OutSystemsUI |
|---|---|---|---|---|---|---|---|
| **CS** | – | ✗ | ✗ | ✗ | only if the CS caches data written through an IS (write-through) | ✓ | ✗ |
| **BL** | ✓ | (other BL, no cycles) | ✗ | ✗ | ✓ | ✓ | ✗ |
| **CW** | ✗ (static entities as types are tolerated) | ✓ Service Actions + Structures | (other CW, no cycles) | ✗ | ✗ | ✓ | ✓ |
| **FE** | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ (theme, patterns) | ✓ |

### Relaxed mode (official canvas, when the project says so)
The Front-End may also consume BL Service Actions and read CS entities. That is still legal under the canvas, because both are Core and FE is above them. Use relaxed mode only when the project's architecture document says so (see "Precedence of rules" in SKILL.md).

## 3. Folder layout

```
<App>_CS            Entities/<Concept>/...   Lookups/   CRUD/
<App>_BL            Structures/   ServiceActions/   PrivateActions/   Integrations/   (Roles, Site Properties at module level)
<App>_CW            Blocks/<Concept>/...   UIHelpers/
<App>_Front_End     UI Flows: one per journey (e.g. Requests, Templates, Admin); Common flow for layout/menu if no _Th
<Concept>_IS        REST/SOAP under Integrations; Wrappers/ (public normalized actions); Structures/ (normalized)
<Concept>_Sync      Timers/   SyncLogic/
```
Group CRUD persistence actions apart from state-transition actions (`Submit`, `Approve`, `Reject`, `Return`), which get a folder of their own (e.g. `Workflow`).

## 4. Naming conventions
Official baseline (*OutSystems Platform Best Practices*):
- English for code and comments; meaningful names (`Customer`, not `Cstr`); PascalCase.
- Foreign keys end in `Id`. Records are named after their entity (`Customer`, not `record`).
- Screens grouped with a prefix (`Customer_Edit`, `Customer_Show`). Timer actions prefixed `Timer_`.
- Name your Table, List and Form widgets.
- No empty labels or descriptions. The module suffixes are a widely used convention, not a platform rule.

House rules on top of that:
- **Modules**: `<AppOrConcept>_<Suffix>` with the suffixes from architecture-canvas.md. The theme uses a short app abbreviation: `SF_Th`.
  - End-user modules carry **no technical suffix** when the module name appears in the URL. Users see it, so `SoccerFields` beats `SF_FE` for public URLs (community convention). Internal back offices may use `_FE` / `_BO`.
  - Optionally prefix modules with an **application acronym** in large factories (`SFC_Booking_CS`, `FLC_Field_IS`) so the owning app is obvious.
  - More community suffixes: `_OAPI` (internal API module exposing versioned Service Actions), `_FS` (Foundation service for non-functional needs, e.g. auditing), `_MBL` / `_MPat` (mobile variants), `Template_<Name>` (theme templates).
- **Entities**: singular PascalCase nouns (`FileRequest`). Static entities are singular too (`RequestStatus`). Attributes are PascalCase; foreign keys are `<Entity>Id`; booleans read as questions (`IsDeleted`, `HasAttachments`).
- **Actions**: `<Entity or Concept>_<Verb>[Qualifier]`, e.g. `FileRequest_Create`, `FileRequest_GetList`, `FileRequest_Submit`. Private implementations end in `_Logic`. Integration wrappers: `<Concept>_IS_<Verb><Object>` (e.g. `Field_IS_GetSummaryFields`). Timer actions: `Timer_<Name>`. Screen and block event handlers: `On<Event>` (`OnSave`, `OnCustomerSelected`).
  - Common alternative (Synobsys): no underscores, `<Entity><Verb>` (`CustomerCreate`), Service Actions versioned `CustomerGetV1`. **Pick one style per factory and record it.** Never mix styles inside one app. Keep names short.
  - Breaking Service Action changes get a version suffix (`Customer_GetV2`). Keep the old version until every consumer has moved, then mark it deprecated.
- **Structures**: `<Concept><Purpose>` (`FileRequestSummary`). IS structures: `<Concept>_IS_<Purpose>`.
- **Blocks**: a noun phrase for what they show (`RequestStatusBadge`, `FileRequestForm`, `TemplateCard`). **Screens**: what the user does (`FileRequestList`, `FileRequestDetail`, `TemplateEdit`). Never generic names.
- **Site properties**: PascalCase nouns with units where needed (`SmsSenderName`, `RequestExpiryDays`).
- **Roles**: job roles (`OrderClerk`, `Approver`).
- Every public element gets a **Description**. It shows up in the consumer's Manage Dependencies dialog and is what other teams read.

## 5. Supporting module types
| Module | When | Notes |
|---|---|---|
| `<Concept>_IS` | Any external system | Technical wrapper only. Hides protocol, authentication, mapping and errors. One per *concept*, not per external system. |
| `<Concept>_Sync` | Timers that copy external data into a CS | Isolates sync from CS consumers. References IS + CS. |
| `<Concept>_API` | Exposing services to external consumers | Technical wrapper over BL/CS. Versioned. No business logic. |
| `<App>_Th` | Each End-User app (or a global one) | See architecture-canvas.md §6. |
| `<Name>_Lib` | Business-agnostic utilities | No entities tied to a business concept. |
| `<Name>_Eng` | Heavy processing (hot cache, calculations) | Fills hot-cache entities owned by a BL. |

## 6. When to add or split modules
**Health signals**:
- module larger than about 4 MB;
- more than about 20 site properties;
- too many public elements (a "monolithic service module");
- too many screens (a "monolithic web UI module");
- screens in a Core or Foundation module (except exception screens and reusable `...Popup` screens).

Any of these means it is time to split or move.

Split a concept into more modules when it is too **complex** for one module, when parts need **independent lifecycles** (different teams or sponsors), or when **service isolation** needs it (an integration pattern). Merge modules that are strongly coupled or cycle with each other. Don't create a `_CW` or `_BL` "just because": the official sample skips `_CW` until reusable blocks exist. In the house standard the 4 modules are the default for any app with UI and its own data.
