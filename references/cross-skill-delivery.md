# Cross-skill delivery contract

Use this house convention when a requirement crosses skill boundaries. It is a portable handoff, not an extra approval ceremony or a claim that these fields are native OutSystems features. Keep an existing project tracker or spec format when it already carries the information.

## Ownership and routing

| Skill | Owns | Gives the next skill |
|---|---|---|
| outsystems-brd-analysis | Source baseline, requirements, decisions and story scope | Stable source/register IDs, affected stories, measurable NFRs and unresolved dependencies |
| outsystems-user-story-implementation | Delivery coordination and acceptance evidence | Story/AC IDs, scoped tasks, acceptance cases and result ledger |
| outsystems-architecture | Boundaries, contracts and dependency order | Producer/consumer versions, ownership, migration and rollback constraints |
| outsystems-backend-conventions | Data and server execution | Authorization, input/output/error contracts, side effects and transaction boundaries |
| outsystems-frontend-conventions | Client behavior and interaction state | Query identity, permission mapping and recovery behavior |
| outsystems-live-style-guide | Rendered appearance and accessibility | Theme baseline, visual states and assistive-technology acceptance checks |
| outsystems-bpt | O11 process execution | Correlation, progression, recovery and in-flight instance policy |
| outsystems-cmf | O11 case behavior | Case/status/activity identities, access and installed API contracts |

Load only the skills needed for the change. BPT, CMF and the O11 Canvas do not become ODC APIs or deployment models by analogy. A plain state transition may need neither BPT nor CMF.

## Minimum trace

Record source revision and locator → requirement ID → story + criterion ID → task → owning module/app and element → test → observed result. Criterion IDs are scoped by story; task/test IDs are unique within their trace file. Preserve original IDs when importing from another tracker.

For each observation record application version, environment, role, locale, test-data/provider mode, time, and an evidence reference. Use explicit unknowns. A source revision change invalidates only affected assumptions and tests; it does not silently reuse a previous Pass. An older deployed app cannot prove a change still in an edit session.

Report **prepared → model validated → merged → published → runtime verified** separately. These are evidence stages, not automatic platform operations. A report can be complete while implementation remains blocked. A failed or untested criterion cannot become Pass by adding an explanation; an agreed scope change has its own decision and remaining scope.

## Execution order and authority

Order tasks by actual dependencies: an integration wrapper needed by business logic must be available before its caller is validated. The familiar CS/BL/IS/CW/FE list describes responsibilities, not an unconditional publishing order. For incompatible changes, plan producer compatibility, consumer refresh, data migration, activation and recovery together.

Reuse authorization already present in the request. A requirement gap blocks its dependent work, not independent authorized work. Analysis-only requests stop at analysis. A user-reserved publish or dependency step remains a named handoff; do not infer a universal manual-publish rule from that project choice.

## Basis and limits

OutSystems distinguishes platform integrity checks from application testing and recommends a risk-based mix of component and end-to-end tests: [testing guidelines](https://success.outsystems.com/documentation/11/testing_apps/outsystems_testing_guidelines/) and [testability](https://success.outsystems.com/documentation/11/testing_apps/develop_for_testability/). ODC has its own [UI testing guidance](https://success.outsystems.com/documentation/outsystems_developer_cloud/testing_apps/web_ui_testing/). The [Scrum Guide](https://scrumguides.org/scrum-guide.html) distinguishes refinement from meeting the Definition of Done; a formal Definition of Ready is a team practice. The trace format and evidence stages above are house conventions derived from delivery failures, not official product guarantees. Sources reviewed 2026-11-22.
