# Architecture verification and evolution

Use for cross-module changes, architecture reviews and release planning. The controls below are engineering guidance; recorded project lessons are observations, not universal platform limitations.

## Dependency evidence (ARV-01)

Inventory each edge with consumer, producer, consumed element, reference strength, producer version and consumer freshness. Screen destinations, Service Actions and data-type elements (entities/structures) are weak references; a block, Server Action, role or other strong element can still make the same module pair strongly coupled. If a pair has both, retain both edges. A weak edge does not mean zero security, availability, schema or transaction coupling.

Run the Canvas graph checks on strong references. Run the selected house pattern checks separately; that pattern may deliberately disallow calls which the Canvas permits. Do not label every FE-to-FE screen navigation a Canvas violation. Unknown external modules are **unvalidated**, not proven Foundation modules. Suffixes are inference; explicit inventory wins.

The two architecture validators accept legacy string references as strong, or objects such as `{"target":"Orders_BL","kind":"service-action"}` and `{"target":"Orders_Portal","kind":"screen-destination"}`. Use `kind: "weak"` for data-type-only entity/structure references and `kind: "strong"` for blocks/Server Actions and other strong elements. Use `kind: "unknown"` when unresolved: it is conservatively checked and reported. No findings means no covered violation in that inventory, not a complete platform audit.

## Producer/consumer delivery (ARV-02)

For each contract change, record:

| Item | Evidence needed |
|---|---|
| Target | Environment, app/module identity, branch/version where applicable |
| Producer | Actual public action/entity/structure and complete attributes/types |
| Consumer | Imported contract version, missing fields, usages requiring change |
| Delivery | Producer publish, consumer dependency refresh, consumer validation and publish |
| Verification | Runtime route, role, data fixture and observed outcome |

An imported entity exposing only `Id` is an incomplete schema for field mapping. Obtain the producer contract; do not guess the missing attributes. Do not repeatedly attempt unsupported dependency editing when the user owns that step. Give the smallest exact handoff, and continue independent work.

Preserve element keys and public signatures during refactors. Adding an output field can require dependency refresh and downstream mapping changes even when the action name is unchanged. An incompatible change needs a versioned contract or a coordinated consumer migration.

## Data ownership and migration (ARV-03)

- Trace each displayed field to a source entity/API, relation and temporal meaning. Distinguish the current master record from the application/submission snapshot and from an external identifier. Similar names or numeric types do not prove identity equivalence.
- Plan schema evolution as **expand → backfill → switch consumers → contract**. Make backfills resumable, reconcile counts and define rollback/forward-repair before removing old fields. Code rollback does not undo data migration or sent messages.
- Choose one owner for status, task assignment and audit facts. Derived read models need explicit synchronization and reconciliation, not competing write paths.
- Switch mock and real providers for the whole related view together. Unknown sections show unavailable/empty with an explanation; do not attach sample money, people or cases to a real identity.

## Verification and handoff (ARV-04)

Track requirement → element → evidence. Distinguish generated code, temporary-model validation, merged module, published artifact and runtime result. Test permissions and negative paths as well as the happy path. A missing dependency, expired browser session or unopened module limits only the affected evidence; it must not become a success claim.

For deployment, capture environment-specific settings, secrets by reference only, producer/consumer order, schema steps, running-process compatibility, smoke tests, monitoring and recovery owner. Follow the project's release window and authorization instead of inventing a universal ban on business-hours deployment.

## Review scenarios

1. Two portals navigate to each other with weak screen destinations: no strong cycle finding; a shared block between them still requires review.
2. A source entity reference has only `Id`: mapping the missing amount is blocked by evidence, not filled with a guessed column.
3. A temporary model validates but the consumer was never refreshed: report model validation and the missing delivery step, not runtime completion.

## Sources and provenance

- [Official strong and weak dependencies](https://success.outsystems.com/documentation/11/building_apps/reusing_and_refactoring/understand_strong_and_weak_dependencies/): element types and mixed-pair classification.

- [Official Architecture Canvas](https://github.com/OutSystems/docs-product/blob/master/src/app-architecture/design-architecture/01-4-layer-canvas.md) and [official architecture explanation](https://www.outsystems.com/blog/posts/application-architecture): strong versus weak dependency treatment.
- [Official Service Actions guidance](https://success.outsystems.com/documentation/11/building_apps/reusing_and_refactoring/use_services_to_expose_functionality/): contract, deployment and transaction differences.
- [Service Studio MCP contract](https://github.com/OutSystems/outsystems11-mcp): use the installed skill and live tool descriptions for model work.
- Anonymized prior-project observations reviewed 2026-11-22: stale imported contracts, historical-versus-current record confusion, temporary-model-only validation and mixed mock/real dashboards. These support the evidence checks above, not a claim that any platform action was retested during this skill review.

### Acceptance ownership and change activation

For each cross-module criterion, name the owning contract and its producers/consumers; include strong and weak references in deployment-impact review even when only strong edges affect Canvas cycles. Read the refreshed consumer signature, including structure attributes, before declaring the dependency available. An imported entity exposing only an identifier is incomplete evidence for a query that needs more fields.

Specify compatibility windows, backfill ownership and the activation point for new required fields or status meanings. Verify an old consumer against the compatible producer before switching the new consumer. Keep deployment recovery distinct from reversing committed business data. Carry source revision, target app version and unresolved manual steps into the story report.

Use [the cross-skill delivery contract](cross-skill-delivery.md) for ownership and trace fields. These are deployment planning recommendations; actual capabilities come from the selected O11/ODC environment.
