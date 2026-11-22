# Lessons learned from real OutSystems projects

Collected from builds of several enterprise OutSystems 11 Reactive applications (a request and file-exchange portal, an executive 360° dashboard, case-management apps). The names are generalized. Each lesson gives the problem, the cause and the rule.

## Architecture and process
1. **A project document can conflict with the house standard.** On one project, the project's own prompt put all DTO structures in CS and let the Front-End call CW, BL and CS directly, which contradicts the strict 4-layer standard. **Rule**: detect the conflict early, ask which one wins, and record the decision in the blueprint. Don't silently rework modules that are already built.
2. **A flat module tree turns into a mess fast.** **Rule**: create the folders first (entities by concept, CRUD apart from workflow or state actions, Structures, ServiceActions, PrivateActions, Integrations, Blocks by concept). Give screens and workflows specific names.
3. **"Done" claims from memory were wrong.** **Rule**: verify every created element by reading it back from the platform, and check validation errors and warnings after each change.
4. **Work in dependency order within the agreed scope**: discovery → design → CS → BL → CW → FE → verification. Continue authorized work without a new approval at every phase. Record producer/consumer readiness and any publishing or dependency step the user has reserved.
5. **Don't invent source data.** When the source of a field is unknown, mark it `NOT FOUND`. Keep demonstrations explicitly isolated in a mock mode. In a real-data journey, show unavailable data instead of fabricated values, and switch dependent blocks together so a real identity never displays sample financial or case details.
6. Keep a running **build log** (what was created per module, results, manual steps, open issues) with real timestamps.

## Data and logic
7. **Audit columns set in two places drifted.** **Rule**: only the CS CRUD wrapper sets `CreatedBy/On` and `UpdatedBy/On`. Callers pass the business data only.
8. **Soft delete needs a filter in every query.** After adding `IsDeleted`, every aggregate (list, get by id, lookups used by external flows, joined children) needed `not X.IsDeleted`. **Rule**: list every read of the entity and add the filter in one change. Outer-joined children use `Child.Id = NullIdentifier() or not Child.IsDeleted`.
9. **Service Actions run in their own transaction.** Multi-step writes split across several Service Actions can't roll back together. **Rule**: thin public Service Action → private `_Logic` server action that holds the multi-step logic.
10. **Binary files on main entities slowed lists down.** **Rule**: a 1-to-1 `<Entity>Content` extension entity, written only after the antivirus scan passes.
11. **Built-in helpers may be missing in an environment** (e.g. `GenerateGuid` and `BinaryDataSize` were not available without extra dependencies). **Rule**: check that a helper exists before designing around it. Fallbacks: SQL `CRYPT_GEN_RANDOM` / `DATALENGTH`, or a small library.
12. **Sort direction and other model details are easy to guess wrong.** Read back an existing element that already does the same thing before writing new logic.

## Integrations
13. **SMS delivery**: of several gateways available in one environment, only one login-plus-send pair actually delivered. Phone numbers had to be in the international format without "+", and messages needed the right category. **Rule**: wrap each gateway in its own `_IS` with number formatting in one place. Test delivery end-to-end with a test-override site property that is empty in production.
14. **SSO / national-ID login**: the identity provider's configuration (client id and encrypted secret) already existed in a shared IdP module. Copying it into the app's site properties duplicated secrets. **Rule**: consume the shared `GetConfig` / `GetSecurityValue` public actions, and take only those dependencies. Taking every public element of that module pulled in tenant-specific entities and caused "Invalid Reference … Show Tenant Identifier" errors.
15. **SSO failures can be environmental.** A staging client registration was invalid for every app, not just the new one. **Rule**: before debugging your own code, reproduce the failure with an existing app that uses the same provider. Remember that the new app's callback URL must be registered with the provider.
16. **Never expose auto-generated REST structures** beyond the `_IS`: an API change otherwise breaks every consumer.

## UI
17. **The corporate theme decides the layout.** The Front-End must set its base theme to the corporate theme and use its layout (header, menu placeholder, footer). That layout needed the theme's required script (e.g. jQuery) added to each screen. **Rule**: inspect an existing app built on the same theme before building screens.
18. **Custom CSS collided with OutSystems UI classes** (e.g. `.alert`). **Rule**: prefix custom classes.
19. **Block CSS loads before theme CSS**: overrides need higher specificity.
20. **Responsive testing**: the device class is fixed at page load, so reload after resizing. After republishing a Reactive app the browser may serve old JS, so clear the cache and reload.
21. **Reactive List + flex or grid**: hide the inner `<script>` element (`.list > script{display:none}`).
22. **Rebuilding a block**: keep the block (its key) and clear and recreate its content, or consumers lose their references.

## Large modules and tooling
23. Very large modules (around 10 MB) take minutes to open or change through automation, and can fail. **Rule**: do changes there in Service Studio by hand, or build the piece as a block in a small module and have it dropped in.
24. See service-studio-mcp.md for the limits of the automation tool.
