# Sources

Read 2026-11-22. **O** = official OutSystems documentation or OutSystems-owned; **C** = community (MVPs, partners, forum, blogs). Community sources fill gaps only; where they disagree with official docs, the official docs win.

## Official (O)
| Topic | URL | Used in |
|---|---|---|
| App architecture: index and all sub-pages (canvas, validation, SOA, integration patterns, app composition, 4 rules, theme, multi-tenant, microservices, DDD, from architecture to development, mobile with many teams, audit trail, hot cache, distributed cache, performance references, top-10) | https://success.outsystems.com/documentation/11/app_architecture/ | architecture-canvas, module-standard, design-process, integration-and-caching, audit-trail, domain-driven-and-scale, performance |
| OutSystems Platform Best Practices (naming, coding, DB, queries, architecture, teamwork, logic, security, performance) | https://success.outsystems.com/documentation/11/onboarding_developers/outsystems_platform_best_practices/ | module-standard, data-and-logic, performance, lifecycle-and-sop |
| Best practices for reactive web security (Aug 2026) | https://success.outsystems.com/documentation/11/security_and_compliance/best_practices_for_reactive_web_security/ | security |
| Code analysis patterns (Code Quality, formerly AI Mentor Studio; Aug 2026) | https://success.outsystems.com/documentation/11/monitoring_and_troubleshooting_apps/manage_technical_debt/code_analysis_patterns/ | code-quality-patterns, review-checklist, security, performance, ui-standards |
| Use Services to Expose Functionality (official) | https://success.outsystems.com/documentation/11/building_apps/reusing_and_refactoring/use_services_to_expose_functionality/ | data-and-logic |
| 8 Best Practices for Building a Reactive Web App (OutSystems blog, MVP author) | https://www.outsystems.com/blog/posts/best-practices-reactive-web-app/ | ui-standards, security |
| BDDFramework (Forge) / BDD testing guide | https://www.outsystems.com/forge/component-overview/1201/bddframework-o11 · https://www.outsystems.com/blog/posts/intro-bddframework-testing/ | lifecycle-and-sop |
| outsystems-pipeline (CI/CD with the LifeTime API) | https://github.com/OutSystems/outsystems-pipeline (wiki) | lifecycle-and-sop |
| Product update: stricter CSP (unsafe-inline / unsafe-eval optional) | https://www.outsystems.com/product-updates/o11-stricter-content-security-policies | security |

## Community (C)
| Topic | URL | Used in |
|---|---|---|
| Synobsys standards: module naming, action naming, code review checklist, code style guide, ADR-003 (secure server actions) | https://synobsys.github.io/ | module-standard, data-and-logic, lifecycle-and-sop, security |
| "The 10 rules of role-based security" (Noesis, MVP) | https://medium.com/noesis-low-code-solutions/outsystems-react-mobile-the-10-rules-of-role-based-access-control-953dba243dc | security |
| "Stop using CRUD actions on the client-side" (DoItLean) | https://medium.com/@samuel.n.marques/outsystems-reactive-security-stop-using-crud-actions-on-the-client-side-1110df1efc84 | security, module-standard |
| "Top 8 best practices on how to develop a timer" (KinetIT) | https://medium.com/kinetit/top-8-best-practices-on-how-to-develop-a-timer-d45d420442aa | data-and-logic |
| "Exception Handling Standards" (Noesis) | https://medium.com/noesis-low-code-solutions/outsystems-exception-handling-standards-d17c6ac235ca | data-and-logic |
| "Containing and reducing technical debt in O11" (ITNEXT, MVP) | https://itnext.io/suggestions-for-containing-and-reducing-technical-debt-in-outsystems-11-a62caf104678 | lifecycle-and-sop |
| Forum: CW / BL / CS responsibilities (MVP discussion) | https://www.outsystems.com/forums/discussion/100293/architecture-module-cw-bl-cs/ | module-standard |
| Forum: hotfix placement, rollback vs forward fix | https://www.outsystems.com/forums/discussion/99733/where-to-apply-hotfix/ · https://www.outsystems.com/forums/discussion/15466/ | lifecycle-and-sop |
| Forum: module naming cheat sheet | https://www.outsystems.com/forums/discussion/59771/cheat-sheet-outsystems-module-naming-convention/ | module-standard |
| Accessibility (OutSystems UI, WCAG 2.1 AA; EAA) | https://www.outsystems.com/blog/posts/outsystems-ui-digital-accessibility/ · https://www.outsystems.com/legal/european-accessibility-act/ | ui-standards |
| maiurnarendra/outsystems-ai-skills v0.14.1 (GitHub, MIT, reviewed 2026-11-22): debugging, lifetime-deploy | https://github.com/maiurnarendra/outsystems-ai-skills | debugging, lifecycle-and-sop (OPS-08, OPS-09) |
| OutSystems product updates (2026): O11 MCP (read GA / write Beta, Compare and Merge), Traditional-to-Reactive conversion (GA, producer-to-consumer), Performance Analytics for Reactive and Mobile (Beta, linked to Code Quality, formerly AI Mentor Studio) | https://outsystems.com/product-updates/outsystems-11-mcp · https://www.outsystems.com/product-updates/o11-traditional-to-reactive · https://www.outsystems.com/product-updates/o11-performance-analytics-for-reactive-and-mobile-applications-beta | service-studio-mcp, lifecycle-and-sop (MNT-09), performance |
| OutSystems/outsystems11-mcp (official skill, contract 2, design notes) and community Idea 15580 (per-environment MCP control) | https://github.com/OutSystems/outsystems11-mcp · https://www.outsystems.com/Ideas/15580/ | service-studio-mcp (OPS-10) |
| Forge "MCP Server (O11)" community component (BSD-3) | https://www.outsystems.com/forge/component-overview/22079/mcp-server-o11 | integration-and-caching (INT-07) |

## Not verified / open
- The full text of the official "Apply a hotfix" and "Deployment plans" pages was not retrieved. The hotfix SOP is based on official best-practice bullets and community threads.
- The Code Quality "monolithic module" thresholds are not published. The 4 MB and 20-site-property signals come from the Platform Best Practices page.


## Reliability review — 2026-11-22

See [verification and reliability](../references/verification-and-reliability.md) for primary sources, provenance and acceptance cases. Platform facts are separated from house policy and anonymized project observations. A community mirror is not an official publication; installed contracts and version-matched official sources take precedence. Runtime claims were not retested in a live tenant during this documentation review.

## Eight-skill delivery review — 2026-11-22

- Official: [OutSystems testing guidelines](https://success.outsystems.com/documentation/11/testing_apps/outsystems_testing_guidelines/); [develop for testability](https://success.outsystems.com/documentation/11/testing_apps/develop_for_testability/); [ODC UI testing](https://success.outsystems.com/documentation/outsystems_developer_cloud/testing_apps/web_ui_testing/).
- Standard: [Scrum Guide](https://scrumguides.org/scrum-guide.html); W3C [status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html), [redundant entry](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html) and [accessible authentication](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html) where UI criteria apply.
- Engineering recommendations and generalized project observations: source/app baselines, historical identity, complete consumer imports, action-specific fields, mock/live consistency and honest blocked-work reporting. See `references/verification-and-reliability.md`; these recommendations are distinguished from platform facts.
