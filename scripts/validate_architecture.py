#!/usr/bin/env python3
"""Validate an OutSystems 11 module/application dependency graph.

Checks the official Architecture Canvas rules (ARC-01..04, ARC-07, ARC-10 Core sublayers) and,
with --strict, the house Front_End -> CW -> BL -> CS rules (HSE-01, HSE-03).

Standard library only. Usage:
    python validate_architecture.py deps.json [--strict] [--json]

Input JSON:
{
  "modules": [
    {"name": "Orders_CS", "app": "Orders", "references": ["Audit_Lib"]},
    {"name": "Orders_Front_End", "app": "Orders", "layer": "end-user",
     "references": ["Orders_CW", "Orders_Th", "OutSystemsUI"]}
  ]
}
"layer" (end-user | core | foundation) and "role" (fe | cw | bl | cs | other)
are optional; when absent they are inferred from the module-name suffix.
References to modules not listed are treated as external Foundation
(e.g. OutSystemsUI) and are not validated.

Exit code: 0 = no Blocker/Major findings, 1 = Blocker/Major found, 2 = bad input.
"""
import argparse
import json
import sys

RANK = {"foundation": 0, "core": 1, "end-user": 2}

# suffix (lower-case, without leading underscore) -> (layer, role)
SUFFIXES = {
    "cs": ("core", "cs"), "mcs": ("core", "cs"), "mdb": ("core", "cs"),
    "bl": ("core", "bl"),
    "cw": ("core", "cw"), "mcw": ("core", "cw"), "mui": ("core", "cw"),
    "sync": ("core", "other"), "eng": ("core", "other"), "api": ("core", "other"),
    "lib": ("foundation", "other"), "is": ("foundation", "other"),
    "th": ("foundation", "other"), "theme": ("foundation", "other"),
    "pat": ("foundation", "other"), "drv": ("foundation", "other"),
    "ext": ("foundation", "other"),
    "fe": ("end-user", "fe"), "front_end": ("end-user", "fe"),
    "frontend": ("end-user", "fe"), "bo": ("end-user", "fe"),
    "portal": ("end-user", "fe"), "app": ("end-user", "fe"),
}
KNOWN_FOUNDATION = {"outsystemsui", "outsystemsuimobile", "outsystemssampledatadb",
                    "users", "system", "(system)"}

SEV_ORDER = {"Blocker": 0, "Major": 1, "Minor": 2, "Info": 3}


CS_SUBS = {"cs", "mcs", "mdb"}


def suffix_of(name):
    low = name.lower()
    for suf in sorted(SUFFIXES, key=len, reverse=True):
        if low.endswith("_" + suf):
            return suf
    return None


def infer(name):
    low = name.lower()
    # longest suffix first so "front_end" wins over "end"
    for suf in sorted(SUFFIXES, key=len, reverse=True):
        if low.endswith("_" + suf):
            return SUFFIXES[suf][0], SUFFIXES[suf][1], True
    return "end-user", "fe", False


def tarjan(nodes, edges):
    index, low, onstack, stack, out = {}, {}, set(), [], []
    counter = [0]
    sys.setrecursionlimit(max(10000, len(nodes) * 4))

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        onstack.add(v)
        for w in edges.get(v, ()):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp))

    for v in nodes:
        if v not in index:
            strong(v)
    return out


def validate(data, strict):
    findings = []

    def add(rule, sev, msg):
        findings.append({"rule": rule, "severity": sev, "message": msg})

    mods = {}
    for m in data.get("modules", []):
        name = m["name"]
        layer, role, matched = infer(name)
        explicit = "layer" in m
        layer = m.get("layer", layer).lower()
        if layer not in RANK:
            raise ValueError(f"{name}: unknown layer '{layer}'")
        role = m.get("role", role if (matched or not explicit or layer == "end-user") else "other")
        if not matched and not explicit:
            add("ARC-07", "Minor", f"{name}: no canvas suffix; assumed End-User. "
                "Add a suffix or an explicit \"layer\".")
        mods[name] = {"layer": layer, "role": role, "app": m.get("app"),
                      "sub": suffix_of(name),
                      "refs": [r for r in m.get("references", []) if r != name]}

    externals = set()
    edges = {n: [] for n in mods}
    for n, m in mods.items():
        for r in m["refs"]:
            if r in mods:
                edges[n].append(r)
            else:
                externals.add(r)

    # ---- module level -------------------------------------------------
    for n, m in mods.items():
        for r in edges[n]:
            p = mods[r]
            if RANK[m["layer"]] < RANK[p["layer"]]:
                add("ARC-01", "Blocker", f"Upward reference: {n} ({m['layer']}) -> {r} ({p['layer']}). "
                    "Move the consumed element to a lower layer.")
            elif m["layer"] == "end-user" and p["layer"] == "end-user":
                add("ARC-02", "Blocker", f"Side reference between End-User modules: {n} -> {r}. "
                    "Move the shared element to Core (business) or a Library (agnostic).")
            elif (m["layer"] == "core" and p["layer"] == "core" and m["sub"] in CS_SUBS
                  and p["sub"] is not None and p["sub"] not in CS_SUBS):
                add("ARC-10", "Major", f"Core sublayer violation: {n} (core service) -> {r} (_{p['sub'].upper()}). "
                    "A CS must not depend on BL/CW/API/Sync/Eng; move the consumed element down into a CS.")

    for comp in tarjan(list(mods), edges):
        add("ARC-03", "Major", "Cycle between modules: " + " <-> ".join(comp) +
            ". Move elements, merge, or add a composition module on top.")

    # ---- application level --------------------------------------------
    apps = {}
    for n, m in mods.items():
        if m["app"]:
            a = apps.setdefault(m["app"], {"layer": "foundation", "mods": []})
            a["mods"].append(n)
            if RANK[m["layer"]] > RANK[a["layer"]]:
                a["layer"] = m["layer"]
    app_edges = {a: set() for a in apps}
    for n, m in mods.items():
        for r in edges[n]:
            ca, pa = m["app"], mods[r]["app"]
            if ca and pa and ca != pa:
                app_edges[ca].add(pa)
    for a, targets in app_edges.items():
        for t in sorted(targets):
            la, lt = apps[a]["layer"], apps[t]["layer"]
            if RANK[la] < RANK[lt]:
                add("ARC-04", "Major", f"Upward application reference: {a} ({la} app) -> {t} ({lt} app). "
                    "Move the shared modules (and their dependencies) into a Core/Foundation app.")
            elif la == "end-user" and lt == "end-user":
                add("ARC-04", "Major", f"Side reference between End-User apps: {a} -> {t}. "
                    "Move the shared modules (and their dependencies) into a Core app.")
    for comp in tarjan(list(apps), {a: sorted(t) for a, t in app_edges.items()}):
        add("ARC-04", "Major", "Cycle between applications: " + " <-> ".join(comp) +
            " (they must be deployed together).")

    # ---- house strict rules -------------------------------------------
    if strict:
        forbidden = {
            "fe": {"bl": "HSE-03", "cs": "HSE-03"},
            "cw": {"cs": "HSE-03", "fe": "HSE-01"},
            "bl": {"cw": "HSE-01", "fe": "HSE-01"},
            # CS -> BL/CW is reported as ARC-10 (official sublayer rule); CS -> FE as ARC-01.
        }
        why = {
            ("fe", "bl"): "screens must consume CW blocks only",
            ("fe", "cs"): "screens must not touch CS entities/CRUD",
            ("cw", "cs"): "blocks must go through BL Service Actions, not CS",
        }
        for n, m in mods.items():
            for r in edges[n]:
                rule = forbidden.get(m["role"], {}).get(mods[r]["role"])
                if rule:
                    reason = why.get((m["role"], mods[r]["role"]), "breaks the FE -> CW -> BL -> CS chain")
                    add(rule, "Major", f"House standard: {n} ({m['role'].upper()}) -> {r} "
                        f"({mods[r]['role'].upper()}): {reason}.")

    if externals:
        unknown = sorted(e for e in externals if e.lower() not in KNOWN_FOUNDATION)
        if unknown:
            add("INFO", "Info", "External references not validated (treated as Foundation): " + ", ".join(unknown))

    findings.sort(key=lambda f: (SEV_ORDER[f["severity"]], f["rule"], f["message"]))
    summary = {
        "modules": len(mods), "applications": len(apps), "strict": strict,
        "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in ("Blocker", "Major", "Minor")},
        "layers": {n: m["layer"] for n, m in sorted(mods.items())},
        "application_layers": {a: v["layer"] for a, v in sorted(apps.items())},
    }
    return summary, findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deps", help="dependency JSON file")
    ap.add_argument("--strict", action="store_true", help="also enforce the house FE->CW->BL->CS rules")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = ap.parse_args()
    try:
        with open(args.deps, encoding="utf-8") as fh:
            data = json.load(fh)
        summary, findings = validate(data, args.strict)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"summary": summary, "findings": findings}, indent=2))
    else:
        c = summary["counts"]
        mode = "strict (house standard)" if args.strict else "canvas"
        print(f"Modules: {summary['modules']}  Applications: {summary['applications']}  Mode: {mode}")
        print(f"Blocker: {c['Blocker']}  Major: {c['Major']}  Minor: {c['Minor']}")
        for f in findings:
            print(f"[{f['severity']}] {f['rule']}: {f['message']}")
        if not any(f["severity"] in ("Blocker", "Major", "Minor") for f in findings):
            print("PASS: no architecture violations found.")
    return 1 if summary["counts"]["Blocker"] or summary["counts"]["Major"] else 0


if __name__ == "__main__":
    sys.exit(main())
