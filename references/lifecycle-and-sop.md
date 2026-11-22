# Lifecycle, SOPs and quality gates

Sources: OutSystems 11 *OutSystems Platform Best Practices* (Teamwork, Logic), Code Quality docs, BDDFramework (Forge) and OutSystems testing articles, the `OutSystems/outsystems-pipeline` project, OutSystems community forum threads on hotfixes and rollbacks, and the ITNEXT technical-debt checklist by an OutSystems MVP. Treat the community items as practice, not platform rules.

## Contents
1. Team setup
2. Environments and LifeTime
3. Definition of Ready / Done
4. Development SOP (per change)
5. Code review SOP
6. Deployment SOP
7. Hotfix SOP
8. Testing strategy
9. CI/CD
10. Monitoring and technical debt

## 1. Team setup
- One named OutSystems user per team member. Never share accounts.
- Everyone uses the **same Service Studio version**, matching the Platform Server.
- One owner team per application (see architecture-canvas.md, app rule 3).
- Agree who works on which element. Avoid two people editing the same screen, block or action at the same time; merges keep only one side of a conflict.
- Code, comments and documentation are in **English**.

## 2. Environments and LifeTime
- Use at least **Dev → Test/QA → Production**. Add **Pre-Production** (a copy of Prod) where hotfixes and performance tests need it. Mobile with several teams may add an **Integration** environment.
- **Use LifeTime** for versioning and every deployment. **Don't publish single modules** to non-Dev environments: deploy applications.
- Tag an application version before deploying it. Keep the deployment notes (what, why, the manual steps).
- **Site property values, timer schedules, effective URLs, integration endpoints and DB connections are set per environment** in Service Center or LifeTime. LifeTime does not migrate site property values. Document them in the deployment notes.
- Restrict who may deploy to Production (LifeTime permissions).
- Sandbox, test and BDD-test apps are never deployed to Production.

## 3. Definition of Ready / Done
**Ready**:
- the user story has acceptance criteria (Given-When-Then);
- the data source is known;
- the architecture impact (new module, dependency, integration) is agreed;
- UI mock-up and roles are defined.

**Done**:
- [ ] Built to the module standard; folders and names follow conventions; descriptions filled in.
- [ ] No new TrueChange errors, and **no more warnings than before**. Hidden warnings carry a documented reason.
- [ ] "**Remove Unused Dependencies**" run on every module touched.
- [ ] Architecture validator / Discovery: no new violations.
- [ ] Code Quality: no new findings after the next sync (about 12 h).
- [ ] No reminder comments, disabled code or test screens left behind.
- [ ] Automated tests added or updated (BDD for server logic) and passing.
- [ ] Security: roles on screens; server-side checks; no Anonymous or Registered access unless intended.
- [ ] Peer reviewed (section 5).
- [ ] Deployment notes updated (site properties, data scripts, manual steps).

## 4. Development SOP (per change)
1. Pull the latest version (open from the server, never from an old local `.oml`).
2. Inventory: is there already an element that does this? Reuse it before creating one.
3. Build bottom-up (CS → BL → CW → FE). Publish the producer first, then refresh dependencies in the consumers.
4. Use 1-Click Publish in Dev often. Fix TrueChange errors and warnings as you go.
5. Before handing over, run the Definition of Done.

## 5. Code review SOP
Review every change before it goes to QA. The reviewer uses `review-checklist.md` and checks, at minimum:
- **Implementation**: it does what the story asks; it is not duplicating existing logic; it sits in the right app, module and folder.
- **Security**: authorization on the server; no identity or roles from the client; record-level checks; input validated; no secrets.
- **Errors**: specific handlers before AllExceptions; user-friendly messages; logging with enough context.
- **Readability**: flows go vertically, top to bottom, with branches and exceptions to the right; no overlapping arrows; every Assign and If has a label; complex logic is commented; the flow does one thing.
- **Queries**: aggregates preferred; joins correct (with vs. without); Max. Records; indexes; no hard-coded values.
- **Screens**: no inline CSS; theme classes only; checked at 100 % zoom and at each breakpoint; supported browsers.
- **Dependencies**: no broken references; unused dependencies removed.
- **Tests**: automated tests updated.

Discuss the result with the author. The goal is shared knowledge, not blame. Ask for a peer review whenever you are unsure about a change.

## 6. Deployment SOP
1. Create a LifeTime deployment plan: source → target, applications plus their dependencies, with tags.
2. Check LifeTime's **impact analysis**. Resolve outdated or missing consumers before deploying. Never deploy with broken references.
3. Run the regression tests in the target environment (CI pipeline, section 9).
4. **Don't deploy to Production during business hours**, except for agreed emergency hotfixes.
5. After deployment, set the per-environment values, run the data scripts, check timers, then smoke-test and watch the error logs.
6. Rollback: LifeTime can redeploy an earlier tagged version. A **forward fix (hotfix)** is usually less risky than a rollback, because data and schema may already have changed.

## 7. Hotfix SOP
1. Reproduce the problem in the environment that matches Production (Pre-Prod, or QA restored to the Production version).
2. Apply the fix there, on the Production code line. Never ship untested Dev work along with it.
3. **Test the hotfix**, then deploy it to Production through LifeTime.
4. **Port the fix back immediately** to Dev and QA so the next release doesn't lose it. In LifeTime, mark the hotfix as solved once it has been merged.
5. Record the root cause, and add a lesson or checklist rule if needed.

## 8. Testing strategy
- **Test pyramid**: many fast server-side tests, fewer integration or API tests, few UI end-to-end tests.
- **BDDFramework** (Forge, O11):
  - Scenarios are written as Given-When-Then and test **server-side logic** through public server actions.
  - Keep tests in separate **test modules or apps** (e.g. `<App>_Tests`) that reference the BL or CS under test.
  - Not supported in Production, and never consumed by Production apps.
  - Screen actions of Traditional Web screens can't be tested this way.
- Unit Testing Framework (Forge) can be used for fine-grained tests. Use API tests (Postman or similar) for exposed REST endpoints. Use UI automation (Selenium, Playwright) only for critical journeys.
- Make tests repeatable: create and clean up their own data, with no dependency on the order tests run in.
- Test the negative security cases: a user without the role, another user's record id, a tampered request.

## 9. CI/CD
- **outsystems-pipeline** (OutSystems on GitHub, a Python package; Jenkins and Azure DevOps examples):
  - uses the LifeTime Deployment API to deploy tagged versions between environments;
  - runs the BDD regression tests through the test-execution REST API;
  - stops the pipeline if the regression fails.
  - Needs a LifeTime service account token and the CI/CD probe in the regression environment.
- Gate each promotion on: green regression tests, no new Code Quality or Discovery findings, and the architecture validator (`scripts/validate_architecture.*`, exit code 1 means fail).

## 10. Monitoring and technical debt
- Watch the Service Center error logs, slow queries and slow integrations regularly, even when nobody is complaining. Watch the timer runs too.
- Run timers on a dedicated server or deployment zone where possible. Stagger timer schedules so they don't all start together.
- Review Code Quality technical debt regularly. Plan refactoring as part of the roadmap, not "later".
- Keep Forge components and plugins **up to date**, because they can carry known vulnerabilities. Avoid unmaintained components.
- Turn off extension auditing in Production.
