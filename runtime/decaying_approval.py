#!/usr/bin/env python3
"""The decaying approval — and the Founder's silence as an evidence channel.

TWO PIECES. The second is the one nobody appears to have built.

**1. The per-decision surface.** When an agent hits R1 today it emits a Slack line and a link to a
general dashboard, and the Founder goes and reconstructs the decision. Instead this renders the *minimum
surface for that one action*: the two or three facts that would change the answer, what happens if
he declines, the agent's stated confidence, and the exact commands for yes and no. Generative UI
is a known pattern; pointing it at an autonomy-gate approval and judging it on **time-to-decision**
is the part that is not.

**2. Silence as evidence, not as a blocked row.** Today an unanswered request sits on The Board
forever and means nothing. Here, an eligible request carries its safe default and a deadline; if
the deadline passes, the default fires, and — the novel bit — **that non-answer plus its outcome
becomes evidence toward the rung**. `processes/autonomy-matrix.md` says the human's routine time
trends to zero. This is what that looks like mechanically: not a human who approves faster, but a
queue that resolves safely without him and records what happened.

THE HARD BOUNDARY — and it is the whole safety story.
Decay applies ONLY where all three hold, checked deterministically, every time:

    (a) the action class is on the DECAYABLE list (reversible, internal-blast-radius only), AND
    (b) the request declares a working rollback, AND
    (c) the action's CURRENT RUNG in runtime/autonomy-matrix.md is already R2 or better.

(c) is the one that matters. Decaying an R1 action would be starting high-stakes autonomy on day
one with no eval record — the exact moat-killer the autonomy matrix names in bold. For anything
that fails these tests, **silence means NO**, the request expires unapproved, and that expiry is
recorded as a decision the Founder did not make rather than one the system made for him.

FIVE HONESTY RULES (tests in runtime/test_agentops.py):

1. **Ineligible -> silence means no.**  Never a default action, never a partial one.
2. **The rung is read LIVE from the matrix, never cached in the request.**  A request written
   while an action sat at R2 must not fire after that action was demoted.
3. **Silence alone is not evidence.**  Only silence + a fired default + a RESOLVED clean outcome
   counts. An unresolved default is an open item, not a win — the drills rule, applied here.
4. **The surface states what it does NOT know.**  A deciding fact nobody measured is listed as
   unmeasured; a confidence with no basis is listed as unstated.
5. **Nothing here sends anything.**  It records that a default fired. Whatever the default *is*
   still runs under the harness gate, which denies send/delete/Bash regardless.

CLI
  python3 runtime/decaying_approval.py --open --action "Calendar create/update" --agent jim \\
      --summary "hold 90m Tue for the Client Owner walkthrough" \\
      --fact "Client Owner has not confirmed" --fact "Tue 2-4pm is his stated window" \\
      --default "place the hold" --rollback "delete the event; no invite is sent" --hours 24 --p 0.8
  python3 runtime/decaying_approval.py --surface 1
  python3 runtime/decaying_approval.py --decide 1 --result approve|decline
  python3 runtime/decaying_approval.py --sweep [--commit]
  python3 runtime/decaying_approval.py --outcome 1 --result clean|incident
"""
import os, sys, json, argparse, datetime

CODE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(CODE)
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(os.path.dirname(CODE), "dashboard"))
from ledger import Ledger  # noqa: E402

STORE = "loops/_agentops/approvals.jsonl"

# Reversible, internal blast radius only. Everything outside this list is silence-means-no.
DECAYABLE = {
    "internal-write", "internal-post", "label-archive", "calendar-hold", "draft-only",
}
# Named explicitly so a future edit has to delete a line to widen the blast radius.
NEVER_DECAY = {
    "external-send", "money", "destructive", "config-change", "external-draft",
    "customer-facing", "regulated-advice",
}
MIN_RUNG = 2   # (c) — the action must already be at R2 or better


def _rung(action):
    """Live rung from the autonomy matrix (rule 2 — never cached into the request)."""
    try:
        import trust
        return trust._rung_of(action, trust._rung_map())
    except Exception as e:
        return f"unreadable ({type(e).__name__})"


def _rung_num(rung):
    s = str(rung)
    for n in (3, 2, 1, 0):
        if f"R{n}" in s:
            return n
    return None


def eligibility(action_class, action_name, rollback):
    """Deterministic, three-part. Returns (decayable: bool, reasons: [str])."""
    reasons = []
    if action_class in NEVER_DECAY:
        return False, [f"'{action_class}' is on the never-decay list — silence means NO. "
                       f"Blast radius is external or irreversible."]
    if action_class not in DECAYABLE:
        return False, [f"'{action_class}' is not on the decayable list ({', '.join(sorted(DECAYABLE))}) "
                       f"— refused rather than guessed. Silence means NO."]
    if not (rollback or "").strip():
        reasons.append("no rollback declared — a default that cannot be undone is not a safe default")
    rung = _rung(action_name)
    n = _rung_num(rung)
    if n is None:
        reasons.append(f"'{action_name}' has no rung in runtime/autonomy-matrix.md (read as "
                       f"'{rung}') — an action with no eval record cannot decay")
    elif n < MIN_RUNG:
        reasons.append(f"'{action_name}' is at {rung}; decay needs R{MIN_RUNG}+. Decaying an R1 "
                       f"action is day-one autonomy on an unproven action — the named moat-killer.")
    return (not reasons), (reasons or [f"decayable: {action_class} at {rung} with a declared rollback"])


def open_request(action_class, action_name, agent, summary, facts, default, rollback,
                 hours=24, p=None, unmeasured=()):
    ok, reasons = eligibility(action_class, action_name, rollback)
    deadline = (datetime.datetime.now() + datetime.timedelta(hours=hours)).isoformat(timespec="seconds")
    ev = Ledger(STORE).append(
        "request", action_class=action_class, action=action_name, agent=agent, summary=summary,
        facts=list(facts), unmeasured=list(unmeasured), default=default, rollback=rollback,
        deadline=deadline, decayable=ok, eligibility=reasons, p=p,
        rung_at_open=_rung(action_name))
    return {**ev, "decayable": ok, "eligibility": reasons}


def surface(seq):
    """The minimum decision surface for ONE action."""
    evs = Ledger(STORE).project()["events"]
    r = next((e for e in evs if e.get("seq") == seq and e.get("kind") == "request"), None)
    if not r:
        return None
    decided = next((e for e in evs if e.get("kind") in ("decision", "default-fired")
                    and e.get("request") == seq), None)
    live_rung = _rung(r.get("action"))
    ok, reasons = eligibility(r.get("action_class"), r.get("action"), r.get("rollback"))
    lines = [
        f"┌─ {r.get('agent')} needs a decision — {r.get('action')}",
        f"│  {r.get('summary')}",
        "│",
        "│  What would change the answer:",
    ]
    for f in r.get("facts") or []:
        lines.append(f"│    · {f}")
    for u in r.get("unmeasured") or []:                       # rule 4
        lines.append(f"│    · {u}  [UNMEASURED — nobody records this]")
    if not (r.get("facts") or r.get("unmeasured")):
        lines.append("│    · none stated — ask the agent what it based this on")
    conf = f"{r.get('p')}" if isinstance(r.get("p"), (int, float)) else "unstated"  # rule 4
    lines += [
        "│",
        f"│  If you say nothing: " + (
            f"{r.get('default')}  (at {r.get('deadline')})" if ok
            else "NOTHING HAPPENS. This request expires unapproved."),
        f"│  Undo:               {r.get('rollback') or 'none declared'}",
        f"│  Agent confidence:   {conf}",
        f"│  Rung (live):        {live_rung}" + (
            f"   ⚠ was {r.get('rung_at_open')} when opened" if live_rung != r.get("rung_at_open") else ""),
        "│",
    ]
    if not ok:
        lines.append("│  ⚠ NOT decay-eligible — silence means no:")
        for x in reasons:
            lines.append(f"│      {x}")
        lines.append("│")
    lines += [
        f"│  yes → python3 runtime/decaying_approval.py --decide {seq} --result approve",
        f"│  no  → python3 runtime/decaying_approval.py --decide {seq} --result decline",
        "└─" + (f" already {decided.get('kind')}" if decided else ""),
    ]
    return {"seq": seq, "request": r, "decayable": ok, "eligibility": reasons,
            "live_rung": live_rung, "decided": bool(decided), "render": "\n".join(lines)}


def decide(seq, result, note=""):
    if result not in ("approve", "decline"):
        raise ValueError("result must be 'approve' or 'decline'")
    return Ledger(STORE).append("decision", request=seq, result=result, note=note, by="the Founder")


def sweep(now=None, commit=False):
    """Past-deadline requests. Fires eligible defaults; expires everything else as NO."""
    now = now or datetime.datetime.now()
    evs = Ledger(STORE).project()["events"]
    closed = {e.get("request") for e in evs
              if e.get("kind") in ("decision", "default-fired", "expired")}
    out = []
    for r in evs:
        if r.get("kind") != "request" or r["seq"] in closed:
            continue
        try:
            overdue = datetime.datetime.fromisoformat(r.get("deadline")) <= now
        except (TypeError, ValueError):
            out.append({"seq": r["seq"], "verdict": "error",
                        "why": f"unparseable deadline {r.get('deadline')!r}"})
            continue
        if not overdue:
            continue
        # Rule 2: re-check eligibility against the LIVE rung, not the one cached at open.
        ok, reasons = eligibility(r.get("action_class"), r.get("action"), r.get("rollback"))
        if ok:
            act = {"seq": r["seq"], "verdict": "default-fired", "action": r.get("default"),
                   "why": "no answer by the deadline; the action is R2+ with a declared rollback"}
            if commit:
                Ledger(STORE).append("default-fired", request=r["seq"], action=r.get("default"),
                                     rung=_rung(r.get("action")), outcome=None)
        else:
            act = {"seq": r["seq"], "verdict": "expired-as-no", "why": "; ".join(reasons)}
            if commit:
                Ledger(STORE).append("expired", request=r["seq"], reason="; ".join(reasons))
        out.append(act)
    return {"swept": out, "committed": commit, "now": now.isoformat(timespec="seconds")}


def outcome(seq, result, note=""):
    """Resolve a fired default. Rule 3: only THIS makes a silence into evidence."""
    if result not in ("clean", "incident"):
        raise ValueError("result must be 'clean' or 'incident'")
    return Ledger(STORE).append("outcome", request=seq, result=result, note=note)


def evidence():
    """What silence has actually earned. Rule 3, enforced in the arithmetic."""
    evs = Ledger(STORE).project()["events"]
    fired = {e.get("request") for e in evs if e.get("kind") == "default-fired"}
    outs = {e.get("request"): e.get("result") for e in evs if e.get("kind") == "outcome"}
    clean = [s for s in fired if outs.get(s) == "clean"]
    inc = [s for s in fired if outs.get(s) == "incident"]
    unres = [s for s in fired if s not in outs]
    return {
        "defaults_fired": len(fired), "resolved_clean": len(clean), "resolved_incident": len(inc),
        "unresolved": len(unres),
        "counts_as_evidence": len(clean),
        "note": ("Only a fired default with a RESOLVED CLEAN outcome counts toward a rung. "
                 f"{len(unres)} fired default(s) are unresolved — those are open items, not wins. "
                 "An incident resets the streak like any other incident."),
        "expired_as_no": sum(1 for e in evs if e.get("kind") == "expired"),
    }


def main():
    ap = argparse.ArgumentParser(description="Decaying approvals — silence as evidence, safely.")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--action", default=""); ap.add_argument("--class", dest="klass", default="")
    ap.add_argument("--agent", default=""); ap.add_argument("--summary", default="")
    ap.add_argument("--fact", action="append", default=[])
    ap.add_argument("--unmeasured", action="append", default=[])
    ap.add_argument("--default", dest="dflt", default=""); ap.add_argument("--rollback", default="")
    ap.add_argument("--hours", type=float, default=24); ap.add_argument("--p", type=float)
    ap.add_argument("--surface", type=int); ap.add_argument("--decide", type=int)
    ap.add_argument("--result", default=""); ap.add_argument("--note", default="")
    ap.add_argument("--sweep", action="store_true"); ap.add_argument("--commit", action="store_true")
    ap.add_argument("--outcome", type=int); ap.add_argument("--evidence", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        if a.open:
            klass = a.klass or ("calendar-hold" if "calendar" in a.action.lower() else "internal-write")
            r = open_request(klass, a.action, a.agent, a.summary, a.fact, a.dflt, a.rollback,
                             a.hours, a.p, a.unmeasured)
            print(json.dumps(r, indent=2) if a.json else
                  f"opened seq={r['seq']}  decayable={r['decayable']}\n  "
                  + "\n  ".join(r["eligibility"]) + f"\n\n" + surface(r["seq"])["render"])
            return
        if a.surface:
            s = surface(a.surface)
            print("no such request" if not s else (json.dumps(s, indent=2) if a.json else s["render"]))
            return
        if a.decide:
            ev = decide(a.decide, a.result, a.note)
            print(f"recorded: request {a.decide} -> {a.result}"); return
        if a.outcome:
            ev = outcome(a.outcome, a.result, a.note)
            print(f"recorded: request {a.outcome} outcome -> {a.result}"); return
    except ValueError as e:
        print(f"REFUSED — {e}"); raise SystemExit(2)

    if a.evidence:
        e = evidence()
        print(json.dumps(e, indent=2) if a.json else
              f"Silence as evidence\n  defaults fired:   {e['defaults_fired']}\n"
              f"  resolved clean:   {e['resolved_clean']}   <- the only rows that count\n"
              f"  resolved incident:{e['resolved_incident']}\n  unresolved:       {e['unresolved']}\n"
              f"  expired as NO:    {e['expired_as_no']}\n\n  {e['note']}")
        return
    s = sweep(commit=a.commit)
    if a.json:
        print(json.dumps(s, indent=2)); return
    if not s["swept"]:
        print("  Nothing past its deadline.")
    for x in s["swept"]:
        print(f"  [{x['verdict']:<14}] request {x['seq']} — {x['why']}")
    print(f"\n  {'COMMITTED' if a.commit else 'dry run — pass --commit to record'}")


if __name__ == "__main__":
    main()
