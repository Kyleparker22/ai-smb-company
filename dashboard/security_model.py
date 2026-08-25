#!/usr/bin/env python3
"""Security model — the control set, rendered from the live config instead of from marketing.

Every AI vendor publishes a trust-centre PDF a human wrote. Nobody renders the **actual current**
control set. yourco can, because the controls are files:

  runtime/headless-settings.reference.json  the approval gate — what the agents may and may not do
  runtime/autonomy-matrix.md                every action's rung and its ceiling
  loops/_trust/drills.jsonl                 the injected faults, and whether they were caught
  runtime/agent-registry.json               the sanctioned surface (units, prompts, connectors)

The claim this page makes is not "we take security seriously." It is: *this agent cannot send
email; here is the config line that prevents it; here is the injection drill it survived, on this
date.* A competitor without the instrumentation cannot forge that, which is the whole point —
it converts the moat from an adjective into a citation.

FOUR RULES
1. **Nothing is asserted that isn't read from a file.** Every control carries its source path.
2. **An untested control says so.** A deny rule with no drill behind it is a *claim*, not a proven
   control, and renders as `untested`. The distinction is the page's entire credibility.
3. **The reference file is not the running file.** The active gate is the VPS's own
   `~/.claude/settings.json`; this repo holds a reference copy. The page says which one it read,
   because a security page that implies it inspected production when it read a copy is worse than
   no page.
4. **Internal until OtherVenture.** `EXTERNAL_OK = False`. Nothing here is client-facing until the
   launch gate clears (`processes/launch-gate.md`) — the page is built now and shown later.

Read-only. GET /api/security-model.
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "runtime"))

GATE = "runtime/headless-settings.reference.json"
MATRIX = "runtime/autonomy-matrix.md"
REGISTRY = "runtime/agent-registry.json"

EXTERNAL_OK = False  # rule 4 — flip only when the launch-gate clears

# A deny rule is only a *proven* control if something tried to break it. This maps the controls
# that matter to the drill that tests them; anything unmapped renders `untested`, on purpose.
CONTROL_DRILLS = {
    "send": "canary-injection",
    "delete": "canary-injection",
    "Bash": "canary-injection",
    "scope": "unauthorized-scope",
    "data": "silent-schema-drift",
}

# Plain-language meaning for the deny rules that carry the most weight. Anything not listed
# renders with its raw rule name rather than an invented explanation.
PLAIN = {
    "Bash": "The agents cannot run shell commands. This is the load-bearing one: an agent that "
            "can shell can bypass every other control on this page.",
    "mcp__gmail__send_email": "The agents cannot send email. They draft; a human sends.",
    "mcp__gmail__delete_email": "The agents cannot delete email.",
    "mcp__gmail__batch_delete_emails": "The agents cannot bulk-delete email.",
}


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _gate():
    raw = _read(GATE)
    if not raw:
        return {"error": f"{GATE} not found — the control set cannot be stated", "source": GATE}
    try:
        d = json.loads(raw)
    except ValueError as e:
        return {"error": f"{GATE} is not valid JSON ({e}) — refusing to describe a config "
                         f"this page cannot parse", "source": GATE}
    perms = d.get("permissions") or {}
    allow, deny = perms.get("allow") or [], perms.get("deny") or []
    return {
        "source": GATE,
        "isReferenceCopy": True,
        "activeFileNote": ("The ACTIVE gate is the runtime host's own ~/.claude/settings.json. "
                           "This page read the repo's reference copy — they are kept in sync by "
                           "hand, so a drift between them is possible and is not detected here."),
        "defaultMode": perms.get("defaultMode"),
        "allow": sorted(allow),
        "deny": sorted(deny),
        "allowCount": len(allow),
        "denyCount": len(deny),
    }


def _drills():
    """Every drill's last verdict, from the append-only store — the proof half of the page."""
    try:
        from ledger import Ledger
        import trust_ledger as TL
    except Exception as e:
        return {"error": f"drill record unavailable: {type(e).__name__}: {e}", "byDrill": {}}
    evs = Ledger("loops/_trust/drills.jsonl").project()["events"]
    armed = [e for e in evs if e.get("kind") == "armed"]
    verdicts = {e.get("run"): e for e in evs if e.get("kind") in ("detected", "missed", "expired")}
    by = {}
    for a in armed:
        v = verdicts.get(a["seq"])
        by[a.get("drill")] = {
            "drill": a.get("drill"),
            "lastRun": (a.get("ts") or "")[:10],
            "verdict": ("detected" if v and v.get("kind") == "detected"
                        else "UNDETECTED" if v else "open"),
            "by": (v or {}).get("by"),
        }
    return {"byDrill": by, "catalog": [d["id"] for d in TL.DRILLS], "runs": len(armed)}


def _rungs():
    try:
        import refresh
        return refresh._autonomy()
    except Exception:
        return []


def _control_rows(gate, drills):
    """One row per deny rule: what it forbids, in plain language, and whether anything tested it."""
    rows = []
    for rule in gate.get("deny", []):
        key = next((k for k in CONTROL_DRILLS if k.lower() in rule.lower()), None)
        drill_id = CONTROL_DRILLS.get(key) if key else None
        d = (drills.get("byDrill") or {}).get(drill_id) if drill_id else None
        if d and d["verdict"] == "detected":
            proof, state = f"{drill_id} — detected {d['lastRun']}", "proven"
        elif d:
            proof, state = f"{drill_id} — {d['verdict']} ({d['lastRun']})", "failed"
        elif drill_id:
            proof, state = f"{drill_id} defined but never armed", "untested"
        else:
            proof, state = "no drill maps to this control", "untested"
        rows.append({
            "rule": rule,
            "means": PLAIN.get(rule) or "",
            "state": state,
            "proof": proof,
            "source": gate["source"],
        })
    order = {"failed": 0, "untested": 1, "proven": 2}
    rows.sort(key=lambda r: (order.get(r["state"], 9), r["rule"]))
    return rows


def build():
    gate = _gate()
    if gate.get("error"):
        return {"error": gate["error"], "source": gate.get("source")}
    drills = _drills()
    rows = _control_rows(gate, drills)
    rungs = _rungs()

    proven = sum(1 for r in rows if r["state"] == "proven")
    untested = sum(1 for r in rows if r["state"] == "untested")
    failed = sum(1 for r in rows if r["state"] == "failed")

    gated_forever = re.search(r"## What stays gated regardless of evidence\s*\n(.*?)(?=\n## |\Z)",
                              _read(MATRIX), re.S)
    forever = [re.sub(r"[*`]", "", l).strip(" -") for l in
               (gated_forever.group(1).splitlines() if gated_forever else []) if l.strip().startswith("-")]

    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "external": EXTERNAL_OK,
        "externalNote": ("INTERNAL ONLY. Nothing on this page is client-facing until the OtherVenture "
                         "gate clears (processes/launch-gate.md). Built now, shown later."),
        "gate": gate,
        "controls": rows,
        "summary": {"deny": len(rows), "proven": proven, "untested": untested, "failed": failed,
                    "allow": gate["allowCount"]},
        "rungs": rungs,
        "gatedRegardlessOfEvidence": forever,
        "drills": drills,
        "headline": (f"{len(rows)} deny rules in force · {proven} proven by a drill · "
                     f"{untested} untested" + (f" · {failed} FAILED" if failed else "")),
        "honesty": [
            "Every control on this page is read from a file and cites it — nothing is asserted.",
            "A deny rule with no drill behind it renders `untested`. It is a claim, not a proven "
            "control, and calling it proven would be the exact overstatement this page exists to "
            "avoid.",
            gate["activeFileNote"],
        ],
        "sources": {"gate": GATE, "rungs": MATRIX, "drills": "loops/_trust/drills.jsonl",
                    "registry": REGISTRY},
    }


if __name__ == "__main__":
    d = build()
    if d.get("error"):
        raise SystemExit(d["error"])
    print("SECURITY MODEL — " + d["headline"])
    print("  " + d["externalNote"] + "\n")
    for r in d["controls"]:
        print(f"  [{r['state']:<8}] {r['rule']}")
        if r["means"]:
            print(f"             {r['means'][:96]}")
        print(f"             proof: {r['proof']}")
    print(f"\n  allow-list: {d['summary']['allow']} entries · rungs parsed: {len(d['rungs'])}")
    print("  gated regardless of evidence:")
    for f in d["gatedRegardlessOfEvidence"]:
        print(f"    · {f[:100]}")
