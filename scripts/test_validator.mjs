#!/usr/bin/env node
// Regression test: runs validate_architecture.mjs on the example inputs and compares
// the JSON output (and exit code) with scripts/expected/*.json.
//   node scripts/test_validator.mjs            # test
//   node scripts/test_validator.mjs --update   # rewrite the expected files after an intended change
import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL(".", import.meta.url));
const CASES = [
  { name: "good_canvas", input: "example_deps.json", args: [], exit: 0 },
  { name: "good_strict", input: "example_deps.json", args: ["--strict"], exit: 0 },
  { name: "bad_canvas", input: "example_deps_bad.json", args: [], exit: 1 },
  { name: "bad_strict", input: "example_deps_bad.json", args: ["--strict"], exit: 1 },
];
const update = process.argv.includes("--update");
let failed = 0;
mkdirSync(join(DIR, "expected"), { recursive: true });

for (const c of CASES) {
  const r = spawnSync(process.execPath, [join(DIR, "validate_architecture.mjs"), join(DIR, c.input), ...c.args, "--json"], { encoding: "utf8" });
  const out = r.stdout.replace(/\r\n/g, "\n");
  const file = join(DIR, "expected", `${c.name}.json`);
  if (update) { writeFileSync(file, out); console.log(`updated ${c.name}`); continue; }
  let expected = "";
  try { expected = readFileSync(file, "utf8").replace(/\r\n/g, "\n"); } catch { expected = "<missing>"; }
  const ok = r.status === c.exit && out === expected;
  if (!ok) failed++;
  console.log(`${ok ? "PASS" : "FAIL"} ${c.name} (exit ${r.status}, expected ${c.exit}${out === expected ? "" : ", output differs"})`);
}
if (!update) { console.log(failed ? `${failed} case(s) failed` : "all cases passed"); process.exit(failed ? 1 : 0); }
