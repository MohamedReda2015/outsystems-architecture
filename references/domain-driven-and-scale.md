# Scaling: domains, many teams, mobile at scale, customizable products

Source: OutSystems 11 docs *OutSystems Domain Driven Architecture* (and its sub-pages), *Building mobile apps with multiple independent teams*, *How to Create Customized Versions of a Base Application*.

## Domain-driven architecture (large factories, many teams)
**When**: development and deployment slow down because everything depends on everything. DDD is a poor fit when domain complexity is low and technical complexity is high. Start simple and decouple as teams and complexity grow.

**Design**: break the business's macro-processes down by line of business (or other functional criteria) until the granularity is right. Give each domain **one multidisciplinary owner team** with light, stable public interfaces. Use a shared ("ubiquitous") language.

**Domain types**:
- **Vertical**: serves one line of business. An orchestrator domain counts as vertical.
- **Horizontal**: shared core business services used by several verticals.

**Coupling**:
- **Inside a domain**: strong coupling is fine (in-process calls, one DB transaction).
- **Across domains**: loose coupling through a domain API with two parts:
  - **public read-only entities** for list, search and mashup;
  - **Service Actions** for transactions and detail retrieval.

**Allowed references between domains** (anything else is a finding):
| From → To | Allowed |
|---|---|
| Vertical → Vertical | Service Actions, Structures (Entities only if configured) |
| Horizontal → Horizontal | Service Actions, Structures, Entities (Server Actions only if configured, as an exception for composite logic or transactions) |
| Vertical → Horizontal | Service Actions, Structures, and Entities as weak downward references. **Strong** references only to elements of a **Foundation app** (themes, UI patterns, plugins). |

**Patterns**:
- **Several transactions in one**: a Service Action calls several Server Actions inside a single transaction.
- **Query model**: expose only the subset of data needed to list and search. Details and updates go through Service Actions or REST.

The same canvas rules apply inside and across domains. Validate with Discovery.

## Mobile with many independent teams
Bottom → top:
1. **BL Common**: shared CS/MCS, plugins, IS and the common mobile theme.
2. **BL MCS** (one per business line): local database, CRUD, and BL that wraps the server CS actions.
3. **BL Sync** (one per business line): defines public SyncUnits such as `Login`, `Splash`, `All`.
4. **Sync Common**: the orchestrator. Its `OfflineDataSync` routes, e.g., `"Login,BL1"` to BL1's sync.
5. **BL MCW**: the line's layouts, content blocks and **own theme** (fewer CSS merges between teams). Blocks raise events for navigation; they don't navigate.
6. **BL MUI**: "master blocks", one per screen, that bubble navigation events up.
7. **BL App**: the team's sandbox app with screens and navigation, for testing in isolation. **Never deployed to Production**.
8. **Major App**: the single real app. It has one UI flow per business line, each with that line's theme (which inherits the common theme), and the global `OnException`.

Team practice: agree on who edits which screen or block (a visual merge conflict keeps only one side), and sandboxes go Dev → Test → PreProd only.

## Customizable product (base application + customer versions)
Design the base product so customizations sit **on top of** it (separate modules or apps that consume the base product's Core services, blocks and theme), instead of editing it. You can then upgrade the base product without overwriting the customizations. Keep extension points explicit: configuration entities, overridable themes, and blocks with placeholders or events.
