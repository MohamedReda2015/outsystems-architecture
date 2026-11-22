# Security standards

Sources: OutSystems 11 *Best practices for reactive web security* (Aug 2026), *Code analysis patterns: Security*, *OutSystems Platform Best Practices: Security*, *Use Services to Expose Functionality*. Community: Noesis "The 10 rules of role-based security" (an MVP's experiments), DoItLean "Stop using CRUD actions on the client-side", OutSystems blog "Best practices for Reactive web apps", Synobsys ADR-003.

## Contents
1. The Reactive/Mobile threat model
2. Authorization rules
3. Write operations (no mass assignment)
4. Read operations
5. Public screens and account flows
6. Secrets and configuration
7. Input and output
8. Integrations and exposed APIs
9. Multi-tenancy
10. Environments and dependencies

## 1. The Reactive/Mobile threat model
- Everything on the client is **under the user's control**: UI, client actions, screen and block variables, input parameters, and **client variables** (stored in the browser's local storage and shared between apps). An attacker can change any of it, and can replay requests with their own values.
- **Every screen aggregate, data action and server action called from the client becomes a REST endpoint.** It is protected only by the **screen's roles** (or the block's caller), and it accepts whatever parameters the client sends.
- On a screen with the **Anonymous** role, those endpoints are **public**. With the **Registered** role, anyone logged in to *any* app on the same server can call them.
- Hiding or disabling UI is **not** security. A disabled button can be re-enabled in the browser's dev tools, so set Visible = False when the user may not use it, **and** check on the server.
- **Blocks don't inherit** the conditions used to show them. Protect each block's queries and actions on their own.

## 2. Authorization rules
1. Give every screen **custom app roles**, and avoid Anonymous and Registered unless the screen is meant to be public. Use "Internal Access Only" for UI flows and web services that only internal clients use.
2. **One screen per role profile** when the functionality differs by role. Mixing roles on one screen and hiding parts client-side can be tampered with.
3. Any server action reachable from the client whose required roles differ from the screen's, or that needs record-level rules (ownership, ACL, status), **must check on the server**:
   - `Check<Role>Role(GetUserId())`;
   - plus an ownership or ACL check, e.g. "`GetUserId()` = record owner", or a join with the ACL entity.
4. In the house standard, those checks live in the **BL** action (Service Action or its `_Logic`) that the CW block's server action calls. **CS CRUD wrappers don't check roles**, and only BL, timers and processes call them (Synobsys ADR-003). Keep all writes behind use-case actions in BL.
5. **Identity always comes from the server.** Never pass `GetUserId()`, a user id, a tenant id or a role flag as a parameter from the client, a block input or a client variable. Call `GetUserId()` inside the aggregate filter, data action or server action. Code Quality flags these: "Insecure usage of GetUserId on client context / in block parameters".
6. Service Actions receive the caller's **UserId, TenantId, Locale and Request Key**, so `GetUserId()` and `Check<Role>Role()` work inside them. Check there too.
7. For UI only (showing or hiding), read roles client-side with `$public.Security.checkIfCurrentUserHasRole($roles.<Role>)` in OnInitialize. Don't fetch permissions with server calls just to show or hide things.
8. Don't do security checks that need server work in **OnInitialize**. Do them in the aggregate or data action: if the query returns nothing, the screen is empty. Optionally redirect in On After Fetch.
9. Offline mobile: role checks on the device are UX only. Re-check on the server when data syncs. Don't keep sensitive data in local storage.

## 3. Write operations (no mass assignment)
- Don't call entity `CreateOrUpdate` (or a CRUD wrapper that takes the **whole record**) from client logic. The client could change any attribute.
- Create **use-case actions in BL** that take only the fields the user may change, e.g. `Order_Save(OrderId, DeliveryDate, Notes)` or `Product_UpdatePrice(ProductId, Price)`. They:
  1. check the role and the record's ownership or status;
  2. load the current record on the server;
  3. assign only the allowed fields;
  4. call the CS wrapper.
- Validate everything again on the server: mandatory fields, formats, ranges, state transitions. Client validation is only for user experience.

## 4. Read operations
- Fetch **only the data the screen needs**: dedicated Structures in data actions, or aggregates that return only the used attributes (recent platform versions optimize this). Don't send whole entities with sensitive columns to the browser.
- Filter by the user **inside** the aggregate or SQL (`GetUserId()`, `Check<Role>Role()`), never by a screen variable.
- For a detail screen, put the ACL check in the query (inner join with the ACL entity), not in OnInitialize.
- Screen aggregates must not expose **system entities** (Users, etc.) on Anonymous or Registered screens.
- Don't put sensitive information in **screen parameters** (URLs). In Traditional Web, preparation output can end up in the ViewState.

## 5. Public screens and account flows
- On an Anonymous screen, every server call must be safe with *any* input: no way to read or change data that isn't yours.
- Password reset or registration: verify identity with a **one-time code** (SMS or email OTP, a time-limited signed link, an authenticator) generated and checked on the server. Reset the password only with a valid token.
- Rate-limit public actions (login, OTP send, search) against abuse.
- External identity providers (SSO, national ID): **register** the app's callback URL with the provider for each environment.
- External users with no platform user get an explicit actor identity (e.g. `IDP:<externalId>`), which is checked against the record's owner on every call.

## 6. Secrets and configuration
- Don't hard-code secrets, URLs or keys anywhere, including in JavaScript and CSS.
- **Site properties that hold secrets: set `Is Secret = Yes`** (Platform Server 11.25.0+). They are then encrypted at rest and masked in Service Center. On older platforms, use an encrypted configuration entity that is decrypted only on the server.
- Reuse existing shared configuration (e.g. an identity-provider module's `GetConfig` / `GetSecurityValue`) instead of copying secrets. Take **only** the dependencies you need, because broad references can pull in tenant-specific entities.
- Don't log secrets, tokens or full personal data. Mask IDs in the UI and in logs.
- Don't put API keys, tokens or passwords in URLs (query strings end up in web server logs).
- Store passwords only as platform-managed hashes, never encrypted or plain text in your own entities.

## 7. Input and output
- SQL: keep **Expand Inline off**. If you can't avoid it, use `EncodeSql()` on **string literals only** (never on whole SQL fragments) and `BuildSafe_InClauseIntegerList` / `BuildSafe_InClauseTextList` for IN lists. Never use `Replace` to escape.
- Output encoding: keep Escape Content on; use `EncodeHtml`, `EncodeJavaScript` and `EncodeUrl`; use `SanitizeHtml` for rich text.
- Uploads: allow-list file types, limit the size, and **scan for viruses** before storing the content. Store binaries in an extension entity only after the scan passes.
- Content Security Policy: prefer apps without `unsafe-inline` / `unsafe-eval` (now optional in O11). Keep JavaScript in screen, block or module scripts, not inline.

## 8. Integrations and exposed APIs
- Authentication logic lives in the `_IS` (OnBeforeRequest, token handling). HTTPS only. Every call has a timeout and normalized exceptions.
- Exposed REST APIs: require SSL/TLS and authentication (Basic, custom or OAuth), or "Internal Access Only". Validate every input. Return no internal error details.
- Exposed APIs have no global exception handler, so catch exceptions in each method and map them to proper HTTP status codes and messages.
- Audit integration calls where compliance requires it.

## 9. Multi-tenancy (logical separation — recommended)
- Mark modules or entities multi-tenant. The platform adds and filters a Tenant ID column, and indexes it.
- Users share one URL and the tenant is inferred from the username, so usernames must be unique (`user@company`).
- Data leaks between tenants only through **Show Tenant Identifier** and **`TenantSwitch()`**. Allow them only in internal tenant-admin apps, and run an automated report on every deployment that lists where they are used.
- Use fake or scrambled data in non-production. Purge or archive to keep table sizes down.
- Scaling: scale the database server up first, then move tenants to another production environment. A separate database per tenant needs a hand-built data-access layer, so avoid it unless required.

## 10. Environments and dependencies
- Test screens, sandbox apps and BDD test apps are **never deployed** beyond Dev/QA. They are usually public and powerful.
- Keep Forge components and plugins up to date, and track their known vulnerabilities.
- Don't publish to Production or run destructive operations without approval. Resolve outdated references before deploying.
