# UI standards — Reactive Web and Mobile

> For the full UI/UX standard (OutSystems UI tokens, themes, patterns, responsive, WCAG accessibility, forms, RTL, CSS linter and contrast checker), use the companion skill **outsystems-live-style-guide**. This file covers only the architecture-side UI rules.

Sources: OutSystems 11 docs (Platform Best Practices, Code analysis patterns, Reactive web security), the OutSystems blog "8 Best Practices for Building a Reactive Web App", community articles on data-fetch patterns and role-based security, and project experience.

## Screens (End-User)
- Screens are **placeholders**: layout, CW blocks, parameters and event handlers. Content and logic live in blocks.
- Name screens specifically, grouped by a concept prefix where useful (`Customer_List`, `Customer_Detail`, or `CustomerList`). Give each a title and **custom roles**: no Anonymous or Registered unless it is meant to be public.
- **One screen per role profile** when the functionality differs by role (security.md §2).
- Input parameters are **ids**, never records or sensitive data. Keep screen parameters to a minimum.
- Navigation happens at screen level, in response to block events.
- Confirm destructive actions. Show feedback through a shared helper (feedback message or dialog).

## Data fetching (Reactive)
- Screen aggregates and data actions start **in parallel** after the screen loads (Fetch = **At Start**). Use **Fetch = On Demand** for data that isn't needed right away (tabs, popups, details) and refresh it when needed.
- **No server calls in client events** (On Initialize, On Ready, On Render, On After Fetch). They are serialized and delay rendering (Code Quality). Use aggregates and data actions instead. When one fetch depends on another, use On After Fetch of the first only to **trigger** the next refresh.
- **One server round-trip per user action.** Don't call several server actions or aggregates in a row from a client action. Write one server action that does the whole job (one request, one transaction).
- **Lists inside lists**: don't let each list item's block query the server. Fetch the data once and pass it to the child blocks as parameters.
- **Pagination**: Max. Records + StartIndex bound to the OutSystems UI Pagination pattern; refresh in `OnPaginationNavigate`.
- Menus: load the menu items through a server fetch that applies role checks, and cache the result. Don't hide unauthorized menu entries only on the client.
- Set the module's **default server request timeout to 10 s or less**. Raise it only for explicit long operations.
- Large data grids: server-side paging and filtering. Don't load thousands of rows to the client.

## Blocks (CW)
- Blocks are public, grouped by concept, configured through input parameters, and talk outward through **Events** (`OnSaved`, `OnSelect`, `OnNavigate`).
- A block's data comes from a data action that calls a **BL Service Action** and returns BL Structures. Refresh it in `OnParametersChanged`.
- Blocks **don't inherit** the checks that decided whether to show them. Every query and action inside a block applies its own server-side authorization (security.md).
- No hidden dependency on screen state: everything comes in through parameters.
- **Reusable popups**: put each popup's content in a block (`<Name>Popup`) with parameters and events. Use the `Popup` suffix for reusable popup screens in Core modules (Code Quality ignores those).
- To rebuild a block without breaking consumers, keep the block (its key) and clear and recreate its content.

## Themes and CSS
- Every app has a base theme built on OutSystems UI:
  - **Portal**: the menu and login live in the portal theme.
  - **Intranet**: shared login and look, but each app has its own menu (an app theme that inherits the global theme).
  - **Independent apps**: menu and login in each app.
- **CSS belongs in the theme** (or the block stylesheet for block-specific rules):
  - no CSS in **screen** stylesheets (Code Quality; it causes flicker on mobile);
  - **no inline `style`** extended properties;
  - no duplicate styles; temporary classes are replaced by theme classes before QA.
- Block CSS loads **before** theme CSS, so overriding a theme rule needs higher specificity.
- Prefix custom classes (`ord-card`). Don't redefine OutSystems UI class names (`alert`, `card`, `list`).
- Use OutSystems UI patterns (Columns, Card, Tabs, Accordion, Popup, Sidebar, Pagination, Dropdown) before building your own.
- Reactive List renders an inner `<script>`, so flex or grid layouts on `.list` need `.list > script { display:none }`.
- After resizing the viewport, **reload**: the device class is fixed at page load.
- JavaScript: put scripts at screen, block or module level (not inline); comment them; write cross-browser code; avoid custom JavaScript where an OutSystems pattern exists. Keeping JavaScript out of inline expressions also allows a strict Content Security Policy.

## Images and resources
- Images: about 150 KB (mobile) / 500 KB (web) at most, 1024 px maximum. Large media belongs outside the module (a CDN or a database file entity).
- Large resources (Excel templates, PDFs) go in a separate module or are served externally. They slow down publishing.

## Security in the UI
- Hide forbidden actions (**Visible = False**); don't just disable them (Enabled = False can be re-enabled in the browser). And still check on the server.
- Client-side role checks (`$public.Security.checkIfCurrentUserHasRole`) only control visibility.
- Never store sensitive data or authorization flags in **client variables** (browser local storage, shared between apps).

## Accessibility and i18n
- OutSystems UI patterns ship with ARIA roles and keyboard behaviour aimed at **WCAG 2.1 AA**. Custom widgets must keep that level:
  - labels on every input;
  - focus order, plus focus trap and Escape for dialogs;
  - contrast;
  - colour is never the only signal;
  - alt text on images.
- The European Accessibility Act applies to public-facing apps in the EU.
- Use multilingual locales (e.g. `en-US`, `ar-AE`). Translations go through Service Studio's export and import. The theme handles RTL.
- Check screens at 100 % zoom and at every breakpoint, in the supported browsers.

## Mobile specifics
- **One End-User module per mobile app** (native build requirement and single-page-app performance). Screens only host blocks from **`_MCW`** modules split by concept (Customer_MCW, Product_MCW, Common_MCW). **`_MUI`** modules compose screen-sized "master blocks".
- Keep **client and server logic separate**:
  - a generic server-side `Account_CS`;
  - one client-side module per app (`MB_Account_CS` / `MA_Account_CS`, or `_MCS`) holding the local entities and sync logic for that app.
- Local storage:
  - few entities, **denormalized**, one per screen use case;
  - labels instead of foreign keys;
  - no complex types;
  - fetch through data fetches, not client events.
- Sync:
  - `OfflineDataSync` with **SyncUnits**;
  - start it with `TriggerOfflineDataSync` (asynchronous);
  - update the UI on `OnSyncComplete`;
  - sync at login or splash, and on business events.
  - Handle poor networks with `GetNetworkStatus`, not just online or offline.
- Keep the **splash screen** simple: few blocks, no server calls.
- No Orchestration layer on mobile. Each team gets its own sandbox app (Dev → Test → PreProd only, **never Production**). See domain-driven-and-scale.md.
- Plugins live in Foundation modules. Keep them updated.
