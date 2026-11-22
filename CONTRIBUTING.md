# Contributing

Thanks for helping improve **outsystems-architecture**. This repository is an agent skill: Markdown that AI agents (and people) read to design, build and review OutSystems 11 applications. Every change must stay **accurate, sourced, agent-independent and concise**.

## Ways to contribute
- **Propose a rule**: open a "Rule proposal" issue with the problem, the rule, the severity and a source.
- **Report a wrong or outdated rule**: open a "Bug / inaccuracy" issue and link the official documentation that contradicts it.
- **Add a lesson learned**: a real mistake from a real project, written as *problem → cause → rule*, with no client or personal details.
- **Improve tooling**: the validator (`scripts/validate_architecture.py` / `.mjs`), the consistency checker, or the CI workflows.

## Content rules
1. **Cite sources.** Every new rule needs a source in `research/sources.md`: **O** (official OutSystems docs, Forge, product updates) or **C** (community: MVPs, forum, blogs). Official sources win when they disagree with community ones. Record the disagreement in the reference file.
2. **Paraphrase, don't copy.** Summarize the documentation in your own words. Short quotes only.
3. **No confidential data.** No client names, internal hostnames, credentials, tokens, phone numbers, personal data or screenshots of private systems. Use neutral example names (`Orders_CS`, `Customer_IS`, `Claims_BL`).
4. **Explain the reason.** Agents follow rules better when they know *why*. Prefer one sentence of reasoning to an all-caps MUST.
5. **Agent-independent.** Plain Markdown, and standard-library scripts only. Don't add instructions that only work in one agent, except in `adapters/` or `references/service-studio-mcp.md`.
6. **Keep SKILL.md small** (aim for under 200 lines). Details go into `references/`, and SKILL.md points to them.

## Rule IDs
- Every enforceable rule lives in `references/review-checklist.md` as `| ID | Severity | Rule |`.
- **IDs are stable.** Never renumber or reuse an ID. New rules take the next free number in their group (`ARC`, `HSE`, `DAT`, `INT`, `UI`, `PERF`, `SEC`, `AUD`, `MNT`, `OPS`, `TST`). To retire a rule, keep the row and mark it *Deprecated*.
- When a rule maps to an OutSystems Code Quality pattern, tag it `[CQ]` and add the mapping to `references/code-quality-patterns.md`.
- Severity: **Blocker** (deployability or security), **Major** (architecture, performance, maintenance cost), **Minor** (convention or hygiene).

## Validator changes
- Keep `validate_architecture.py` and `validate_architecture.mjs` **identical in behaviour**. CI compares their JSON output.
- Add or adjust `scripts/example_deps*.json` so that every rule is exercised. After an intended change in output, regenerate the expected results and review the diff:
  ```
  node scripts/test_validator.mjs --update
  ```

## Before you open a pull request
```
node scripts/check_skill.mjs          # frontmatter, links, rule IDs, versions
node scripts/test_validator.mjs       # validator against expected results
python scripts/validate_architecture.py scripts/example_deps.json --strict
```
- Update `CHANGELOG.md` (under *Unreleased*, or a new version). Bump `metadata.version` in `SKILL.md` for releases (semantic versioning: new rules = minor, wording fixes = patch, a changed meaning of existing IDs = major).
- If you changed `adapters/core-rules.md`, copy the same text into the marked block of `adapters/copilot-instructions.md`.

## Code of conduct
By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
