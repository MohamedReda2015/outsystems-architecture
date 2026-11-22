#!/usr/bin/env node
// Validate an OutSystems 11 module/application dependency graph (Node.js 16+, no packages).
// Same rules, input and exit codes as validate_architecture.py:
// String references are strong; objects use {target, kind}. Weak service-action
// and screen-destination edges are excluded from Canvas checks. Unknown edges
// are conservative; external modules are unvalidated, never assumed Foundation.
//   node validate_architecture.mjs deps.json [--strict] [--json]
// Exit code: 0 = no Blocker/Major, 1 = Blocker/Major found, 2 = bad input.
import { readFileSync } from "node:fs";

const RANK = { "foundation": 0, "core": 1, "end-user": 2 };
const SUFFIXES = {
  cs: ["core", "cs"], mcs: ["core", "cs"], mdb: ["core", "cs"],
  bl: ["core", "bl"],
  cw: ["core", "cw"], mcw: ["core", "cw"], mui: ["core", "cw"],
  sync: ["core", "other"], eng: ["core", "other"], api: ["core", "other"],
  bpt: ["core", "other"], wf: ["core", "other"],
  lib: ["foundation", "other"], is: ["foundation", "other"],
  th: ["foundation", "other"], theme: ["foundation", "other"],
  pat: ["foundation", "other"], drv: ["foundation", "other"],
  ext: ["foundation", "other"],
  fe: ["end-user", "fe"], front_end: ["end-user", "fe"],
  frontend: ["end-user", "fe"], bo: ["end-user", "fe"],
  portal: ["end-user", "fe"], app: ["end-user", "fe"],
};
const KNOWN_FOUNDATION = new Set(["outsystemsui", "outsystemsuimobile", "outsystemssampledatadb", "users", "system", "(system)"]);
const SEV_ORDER = { Blocker: 0, Major: 1, Minor: 2, Info: 3 };

const CS_SUBS = new Set(["cs", "mcs", "mdb"]);
function suffixOf(name) {
  const low = name.toLowerCase();
  for (const suf of Object.keys(SUFFIXES).sort((a, b) => b.length - a.length)) if (low.endsWith("_" + suf)) return suf;
  return null;
}

function infer(name) {
  const low = name.toLowerCase();
  for (const suf of Object.keys(SUFFIXES).sort((a, b) => b.length - a.length)) {
    if (low.endsWith("_" + suf)) return [...SUFFIXES[suf], true];
  }
  return ["end-user", "fe", false];
}

function tarjan(nodes, edges) {
  const index = new Map(), low = new Map(), onstack = new Set(), stack = [], out = [];
  let counter = 0;
  const strong = (v) => {
    index.set(v, counter); low.set(v, counter); counter++;
    stack.push(v); onstack.add(v);
    for (const w of edges[v] || []) {
      if (!index.has(w)) { strong(w); low.set(v, Math.min(low.get(v), low.get(w))); }
      else if (onstack.has(w)) low.set(v, Math.min(low.get(v), index.get(w)));
    }
    if (low.get(v) === index.get(v)) {
      const comp = [];
      for (;;) { const w = stack.pop(); onstack.delete(w); comp.push(w); if (w === v) break; }
      if (comp.length > 1) out.push(comp.sort());
    }
  };
  for (const v of nodes) if (!index.has(v)) strong(v);
  return out;
}

export function validate(data, strict) {
  const findings = [];
  const add = (rule, severity, message) => findings.push({ rule, severity, message });
  if (!data || typeof data !== "object" || !Array.isArray(data.modules))
    throw new Error("inventory must contain a 'modules' array");
  const mods = Object.create(null);
  const refCounts = { strong: 0, weak: 0, unknown: 0 }, unknownRefs = [];
  for (const m of data.modules) {
    if (!m || typeof m !== "object" || typeof m.name !== "string" || !m.name.trim())
      throw new Error("each module must have a non-empty string name");
    const name = m.name;
    if (Object.hasOwn(mods, name)) throw new Error(`duplicate module '${name}'`);
    if ("layer" in m && typeof m.layer !== "string") throw new Error(`${name}: layer must be a string`);
    if ("app" in m && m.app !== null && typeof m.app !== "string") throw new Error(`${name}: app must be a string or null`);
    let [layer, role, matched] = infer(name);
    const explicit = "layer" in m;
    layer = (m.layer ?? layer).toLowerCase();
    if (!Object.hasOwn(RANK, layer)) throw new Error(`${name}: unknown layer '${layer}'`);
    role = m.role ?? ((matched || !explicit || layer === "end-user") ? role : "other");
    if ("role" in m && !["fe", "cw", "bl", "cs", "other"].includes(m.role))
      throw new Error(`${name}: unknown role '${m.role}'`);
    if (!matched && !explicit)
      add("ARC-07", "Minor", `${name}: no canvas suffix; assumed End-User. Add a suffix or an explicit "layer".`);
    const refs = "references" in m ? m.references : [];
    if (!Array.isArray(refs)) throw new Error(`${name}: references must be an array`);
    const parsed = [];
    for (const ref of refs) {
      const target = typeof ref === "string" ? ref : ref?.target;
      const kind = typeof ref === "string" ? "strong" : (ref && "kind" in Object(ref) ? ref.kind : "strong");
      if (typeof target !== "string" || !target.trim() || !["strong", "weak", "service-action", "screen-destination", "unknown"].includes(kind))
        throw new Error(`${name}: invalid reference; expected target and supported kind`);
      if (target === name) continue;
      const strength = ["weak", "service-action", "screen-destination"].includes(kind) ? "weak" : kind;
      refCounts[strength]++;
      if (kind === "unknown") unknownRefs.push(`${name} -> ${target}`);
      parsed.push({ target, kind, strength });
    }
    mods[name] = { layer, role, app: m.app ?? null, sub: "role" in m ? m.role : suffixOf(name), refs: parsed };
  }

  const externals = new Set();
  const edges = Object.create(null), houseEdges = Object.create(null);
  for (const [n, m] of Object.entries(mods)) {
    edges[n] = [];
    houseEdges[n] = [];
    for (const ref of m.refs) {
      const r = ref.target;
      if (r in mods) {
        if (ref.strength !== "weak" && !edges[n].includes(r)) edges[n].push(r);
        if (ref.kind !== "screen-destination" && !houseEdges[n].includes(r)) houseEdges[n].push(r);
      } else externals.add(r);
    }
  }

  for (const [n, m] of Object.entries(mods)) {
    for (const r of edges[n]) {
      const p = mods[r];
      if (RANK[m.layer] < RANK[p.layer])
        add("ARC-01", "Blocker", `Upward reference: ${n} (${m.layer}) -> ${r} (${p.layer}). Move the consumed element to a lower layer.`);
      else if (m.layer === "end-user" && p.layer === "end-user")
        add("ARC-02", "Blocker", `Side reference between End-User modules: ${n} -> ${r}. Move the shared element to Core (business) or a Library (agnostic).`);
      else if (m.layer === "core" && p.layer === "core" && CS_SUBS.has(m.sub) && p.sub !== null && !CS_SUBS.has(p.sub))
        add("ARC-10", "Major", `Core sublayer violation: ${n} (core service) -> ${r} (_${p.sub.toUpperCase()}). A CS must not depend on BL/CW/API/Sync/Eng; move the consumed element down into a CS.`);
    }
  }
  for (const comp of tarjan(Object.keys(mods), edges))
    add("ARC-03", "Major", `Cycle between modules: ${comp.join(" <-> ")}. Move elements, merge, or add a composition module on top.`);

  const apps = Object.create(null);
  for (const [n, m] of Object.entries(mods)) {
    if (!m.app) continue;
    const a = (apps[m.app] ??= { layer: "foundation", mods: [] });
    a.mods.push(n);
    if (RANK[m.layer] > RANK[a.layer]) a.layer = m.layer;
  }
  const appEdges = Object.fromEntries(Object.keys(apps).map((a) => [a, new Set()]));
  for (const [n, m] of Object.entries(mods))
    for (const r of edges[n]) {
      const ca = m.app, pa = mods[r].app;
      if (ca && pa && ca !== pa) appEdges[ca].add(pa);
    }
  for (const [a, targets] of Object.entries(appEdges)) {
    for (const t of [...targets].sort()) {
      const la = apps[a].layer, lt = apps[t].layer;
      if (RANK[la] < RANK[lt])
        add("ARC-04", "Major", `Upward application reference: ${a} (${la} app) -> ${t} (${lt} app). Move the shared modules (and their dependencies) into a Core/Foundation app.`);
      else if (la === "end-user" && lt === "end-user")
        add("ARC-04", "Major", `Side reference between End-User apps: ${a} -> ${t}. Move the shared modules (and their dependencies) into a Core app.`);
    }
  }
  const appEdgeLists = Object.fromEntries(Object.entries(appEdges).map(([a, s]) => [a, [...s].sort()]));
  for (const comp of tarjan(Object.keys(apps), appEdgeLists))
    add("ARC-04", "Major", `Cycle between applications: ${comp.join(" <-> ")} (they must be deployed together).`);

  if (strict) {
    const forbidden = {
      fe: { bl: "HSE-03", cs: "HSE-03" },
      cw: { cs: "HSE-03", fe: "HSE-01" },
      bl: { cw: "HSE-01", fe: "HSE-01" },
      // CS -> BL/CW is reported as ARC-10 (official sublayer rule); CS -> FE as ARC-01.
    };
    const why = { "fe|bl": "screens must consume CW blocks only", "fe|cs": "screens must not touch CS entities/CRUD", "cw|cs": "blocks must go through BL Service Actions, not CS" };
    for (const [n, m] of Object.entries(mods))
      for (const r of houseEdges[n]) {
        const rule = forbidden[m.role]?.[mods[r].role];
        if (rule) {
          const reason = why[`${m.role}|${mods[r].role}`] ?? "breaks the FE -> CW -> BL -> CS chain";
          add(rule, "Major", `House standard: ${n} (${m.role.toUpperCase()}) -> ${r} (${mods[r].role.toUpperCase()}): ${reason}.`);
        }
      }
  }

  if (externals.size) add("INFO", "Info", "External references not validated: " + [...externals].sort().join(", "));
  if (unknownRefs.length) add("INFO", "Info", "Unknown reference strength checked conservatively as strong: " + unknownRefs.sort().join(", "));
  if (!Object.keys(mods).length) add("INFO", "Info", "Empty inventory: no modules assessed.");

  // Plain code-point ordering, identical to Python's sorted(), so both scripts emit the same JSON.
  const cmp = (x, y) => (x < y ? -1 : x > y ? 1 : 0);
  findings.sort((a, b) => SEV_ORDER[a.severity] - SEV_ORDER[b.severity] || cmp(a.rule, b.rule) || cmp(a.message, b.message));
  const count = (s) => findings.filter((f) => f.severity === s).length;
  const summary = {
    modules: Object.keys(mods).length, applications: Object.keys(apps).length, strict,
    counts: { Blocker: count("Blocker"), Major: count("Major"), Minor: count("Minor") },
    layers: Object.fromEntries(Object.entries(mods).sort((a, b) => cmp(a[0], b[0])).map(([n, m]) => [n, m.layer])),
    application_layers: Object.fromEntries(Object.entries(apps).sort((a, b) => cmp(a[0], b[0])).map(([a, v]) => [a, v.layer])),
    reference_counts: refCounts,
    external_modules: [...externals].sort(),
    validation_complete: !!Object.keys(mods).length && !externals.size && !unknownRefs.length,
  };
  return { summary, findings };
}

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith("--"));
if (!file) { console.error("usage: node validate_architecture.mjs deps.json [--strict] [--json]"); process.exit(2); }
let result;
try {
  result = validate(JSON.parse(readFileSync(file, "utf8")), args.includes("--strict"));
} catch (e) { console.error(`error: ${e.message}`); process.exit(2); }
const { summary, findings } = result;
if (args.includes("--json")) console.log(JSON.stringify({ summary, findings }, null, 2));
else {
  const c = summary.counts;
  console.log(`Modules: ${summary.modules}  Applications: ${summary.applications}  Mode: ${summary.strict ? "strict (house standard)" : "canvas"}`);
  console.log(`Blocker: ${c.Blocker}  Major: ${c.Major}  Minor: ${c.Minor}`);
  for (const f of findings) console.log(`[${f.severity}] ${f.rule}: ${f.message}`);
  if (!findings.some((f) => f.severity !== "Info")) console.log("PASS: no covered architecture violations found in the supplied inventory.");
}
process.exit(summary.counts.Blocker || summary.counts.Major ? 1 : 0);
