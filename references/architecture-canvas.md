# Architecture Canvas — layers, validation and app composition

Source: OutSystems 11 documentation, *App architecture → Designing the Architecture of Your OutSystems Applications* (Architecture Canvas, Validating your application architecture, Application composition and its sub-pages).

## Contents
1. Purpose
2. Layers and module types
3. Strong vs weak references
4. The 3 validation rules (with fixes)
5. Application composition and the 4 rules
6. Theme isolation
7. Typical evolution and how to fix app coupling

## 1. Purpose
The Architecture Canvas is a tool for designing service-oriented architectures in OutSystems. It promotes the right level of abstraction for reusable services and the isolation of functional modules. A medium-to-large installation runs 20+ applications and 200+ interdependent modules, each with its own sponsor and change pace. New apps change fast, while widely reused services change slowly. A good architecture keeps these lifecycles **independent** and keeps the impact of any change small.

Architecture is not a one-time activity. Repeat these two steps as new concepts emerge: (1) identify concepts, (2) define modules.

## 2. Layers and module types

| Layer | Nature | Module types and suffixes | Examples |
|---|---|---|---|
| **End-User** | User interfaces and processes that reuse Core and Foundation to deliver user stories. Must **not** expose reusable services. | End-user / Front-end module: no suffix, `_FE`, `_Front_End`, `_BO` (back office), `_Portal`. Mobile: a single End-User module per app. | `SoccerFields`, `Claims_Front_End` |
| **Core** | Services around business concepts that export reusable entities, business rules and business widgets. | `_CS` Core Services (entities + core rules); `_BL` Business Logic (composes several cores, e.g. `Booking_BL` = Field + Player); `_CW` Core Widgets (business blocks); `_Sync` synchronization timers; `_Eng` calculation or processing engines; `_API` exposure to external consumers; mobile `_MCS`, `_MCW`, `_MUI`, `_MDB` (local storage) | `Customer_CS`, `Catalog_BL`, `Promotion_Eng` |
| **Foundation** | Business-agnostic services that extend the framework: libraries, UI patterns, connectors to external systems, native code. | `_Lib` library or utilities; `_IS` integration service (wrapper of an external system, no business logic); `_Th` theme; `_Pat` UI patterns; `_Drv` driver (one per external system behind an `_IS`); `_Ext` extension wrapper | `Audit_Lib`, `Customer_IS`, `SF_Th` |

Library modules (the "Library" module type in Service Studio) can be referenced in both directions without creating cycles of the *application*. They are still Foundation and must not contain business logic.

## 3. Strong vs weak references
- **Strong**: Server Actions, Client Actions, blocks, images, resources, scripts, themes, roles, processes and process activities. These couple the consumer to producer implementation.
- **Weak**: screens, Service Actions, database/local-storage/static entities and structures. Data-type signatures can still change and require consumer updates. If any consumed element in a module pair is strong, that pair is strongly coupled. See [official dependency types](https://success.outsystems.com/documentation/11/building_apps/reusing_and_refactoring/understand_strong_and_weak_dependencies/).
- Prefer weak references between applications and domains. Within one tightly coupled module group, strong references are acceptable.

## 4. The 3 validation rules
OutSystems **Discovery** (Forge) and **Code Quality** (formerly AI Mentor Studio / Architecture Dashboard) check these automatically on real dependencies. **Classify every module's layer in Discovery**: an unclassified module can't be validated (Code Quality: "Lack of module classification"). A module that mixes layers is classified as its highest layer.

### Sublayer rule (Code Quality)
Inside **Core**, references go from higher sublayers to lower ones: `_BL`, `_API`, `_Sync`, `_Eng` and `_CW` may consume `_CS`, but **a `_CS` must not consume BL, API, Sync, Eng or CW** (ARC-10). The same applies inside **Foundation**: a higher sublayer composes lower ones, never the reverse. A violation usually means a core concept has become dependent on one particular business composition. Move the consumed piece down.

### Team coupling (Code Quality)
Apps owned by different teams should consume each other only through **weak** references (Service Actions, entities read through the data model, structures). Only Foundation apps, which are stable and business-agnostic, may be strongly referenced across teams (ARC-14).

### Rule 1 — No upward references
**Symptom**: a lower layer (Foundation or Core) references a higher layer (Core or End-User). This builds a cluster in which every pair of modules is circularly dependent, so any consumer of one module inherits the whole cluster: a bigger runtime footprint, and constant "outdated" warnings.
**Cause**: services are not properly isolated.
**Fix**: move the consumed element down to a lower layer. For example, move the reusable piece of End-user A into a Library, or into the existing lower module if it fits that concept.

### Rule 2 — No side references between End-User modules
**Symptom**: End-user A uses something from End-user B, even a single formatting function, and so inherits all of B's dependencies.
**Cause**: End-User modules must not provide reusable services, otherwise they lose lifecycle independence.
**Fix**: move the element to a new or existing lower module: **Core** if it is business-related, **Library** if it is business-agnostic.

### Rule 3 — No cycles between Core or Foundation modules
Side references between Core modules (or between Libraries) are allowed, but a cycle is not.
**Cause**: the concepts are badly abstracted. Either the two modules are strongly coupled, or one direction of the dependency should not exist.
**Fix**:
- If one direction is wrong (B should not use A), move the elements of A that B uses into a new module (if they are a reusable concept of their own) or into B (if they were misplaced).
- If the modules are strongly coupled, **merge** them.
- If the merge would be too large, keep both as base concepts and create a **third module on top** that holds the composition logic (usually business rules for an end-user process that needs both concepts).

## 5. Application composition
- An **application** is a set of modules and extensions and is the **minimum deployment unit** in LifeTime. A wrong composition means apps cannot evolve independently, and deploying one forces others to be deployed with it.
- An app sits in the layer of its **highest** module: only Foundation modules makes a Foundation app; any Core module makes a Core app; any End-User module makes an End-User app.
- R1, R2 and R3 also apply **between applications**. An End-User app may contain Core and Library modules only while no other app uses them.

### The 4 rules for correct application composition
1. **Layer your modules correctly.** If the module architecture has violations, a clean app architecture is impossible.
2. **Layer your applications correctly.** Apply the canvas to apps.
3. **Don't mix owners.** One team is accountable for each app. If two teams must change shared services, split the app so ownership is clear.
4. **Don't mix sponsors.** Isolate each line of business in its own app (e.g. a Portal over Auto, Life and Property simulators becomes Portal, one app per line of business, and a Common services app).

A Core-services application contains Blank or Service modules with **no screens**. Service modules physically cannot hold UI, client logic or session variables, which enforces this.

The official best-practices page recommends 3 responsibilities: *Business Processes* (End-User), *Core Entities* (Core) and *Connectors* (Foundation). It also recommends:
- wrapping extensions in modules;
- giving each module a clear responsibility;
- removing unused references;
- not using extensions for business logic or just to consume web services.

## 6. Isolating an application Theme
A Theme module (`_Th`) contains: the CSS, layout blocks, logo images, the login flow and exception handling, menu and navigation logic, and transversal roles (job roles such as Manager or Employee that may drive the menu). It is **not** a general place for assets and utilities.
- **Same look, same menu and login** (one portal): one Global theme reused by all apps.
- **Same look, different menus or logins**: each app gets its own theme that **inherits** the Global theme (base theme) and adds its own menu and login. Change the look only in the Global theme.
- Common blocks from Core should rely on the **base** theme. A block takes on the CSS of the consuming module, so it adapts to each app's look.
- In a new End-User app, create the theme module first (e.g. `SF_Th`), then the front-end module, and set the front-end module as the app's Home module.

## 7. Typical evolution and how to fix app coupling
1. Project 1 creates one app with every module it needs.
2. Project 2 creates another app for a different process.
3. In project 3, App 1 starts reusing Core C from App 2 and App 2 reuses Core B from App 1. The modules themselves have no violation, but the **apps** now reference each other in a cycle and must be deployed together.
4. **Fix**: move the shared Cores **and everything they depend on** (e.g. Library B and Library C) into a new **Core application**. The End-User apps can then evolve at their own pace, and the Core app holds the critical shared resources that need careful change management.
