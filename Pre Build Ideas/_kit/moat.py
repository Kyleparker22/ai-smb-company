#!/usr/bin/env python3
"""The moat layer, shared by every pre-build vertical.

Reliability · eval · observability · approval · audit log — the cross-cutting
layer from `processes/ai-os-modules.md` that is present under every yourco OS
by definition and is never sold as a line item. Four pieces:

  Matrix   — the per-action autonomy rungs (R0..R3) with a stated reason each
  Gate     — the approval gate: R0/R1 queue for a human, R2/R3 execute + log
  Eval     — scored classifiers, with the COSTLY error rate reported separately
  Roi      — an ROI panel that computes from the operator's own inputs, shows
             its arithmetic, and refuses any line whose input is not recorded

House rules encoded here rather than left to discipline:
  · R1 is the floor for anything with money, legal, safety or licensure
    consequence, and a NEVER-promotable action can never leave its rung.
  · A promotion needs a recorded streak — not a vibe (`decisions/2026-07-05`).
  · A refusal is a first-class result, not an error.

Stdlib only.
"""
from .store import iso, now, parse, unmeasured

RUNGS = ("R0", "R1", "R2", "R3")
RUNG_LABEL = {
    "R0": "propose only — drafts, never acts",
    "R1": "approval gate — acts on a human click",
    "R2": "notify-and-act — acts, tells the human, reversible",
    "R3": "full autonomy — acts silently, logged",
}


class Matrix:
    """Per-action autonomy. Every action declares a rung AND why it sits there."""

    def __init__(self, actions):
        for name, spec in actions.items():
            if spec.get("rung") not in RUNGS:
                raise ValueError(f"{name}: rung must be one of {RUNGS}")
            if not spec.get("reason"):
                raise ValueError(f"{name}: an action without a stated reason is not a decision")
        self.actions = actions

    def rung_for(self, action, amount=None):
        spec = self.actions.get(action)
        if not spec:
            return {"action": action, "rung": "R1",
                    "reason": "unknown action class defaults to the approval gate",
                    "never_promote": True}
        out = dict(spec, action=action)
        # A money threshold demotes to the gate — the standing-limit pattern.
        limit = spec.get("limit")
        if limit is not None and amount is not None and amount > limit:
            out["rung"] = "R1"
            out["reason"] = f"{spec['reason']} — above the standing limit of {limit}, so a human approves"
        return out

    def never_promote(self):
        return sorted(k for k, v in self.actions.items() if v.get("never_promote"))

    def promotable(self, action, streak, calibration_ok=True, need=20):
        """Can this action climb a rung? Streak + calibration, per the house rule
        (`decisions/2026-08-13_agent-substrate-upgrade.md`): a clean streak alone
        cannot tell reliable from lucky."""
        spec = self.actions.get(action, {})
        if spec.get("never_promote"):
            return {"promote": False, "why": "this action is permanently excluded from promotion"}
        if streak < need:
            return {"promote": False, "why": f"streak {streak}/{need} clean actions"}
        if not calibration_ok:
            return {"promote": False, "why": "streak met, but the agent has not shown it knows when it is unsure"}
        return {"promote": True, "why": f"{streak} clean actions and calibration evidence on file"}


class Gate:
    """The approval gate. R2/R3 execute; R0/R1 become an approval row a human
    decides. Nothing outward-facing ever bypasses this."""

    def __init__(self, store, matrix, table="approvals"):
        self.store, self.matrix, self.table = store, matrix, table

    def act(self, action, agent, subject, detail=None, amount=None, execute=None):
        r = self.matrix.rung_for(action, amount=amount)
        detail = dict(detail or {})
        detail["rung_reason"] = r["reason"]
        if r["rung"] in ("R2", "R3"):
            result = execute() if execute else None
            ev = self.store.log_event(action, subject, f"agent:{agent}", r["rung"], detail)
            return {"executed": True, "rung": r["rung"], "event": ev["id"], "result": result}
        if r["rung"] == "R0":
            # R0 means THE SYSTEM NEVER DOES THIS. It is not a slow yes, so it
            # never becomes a row with an Approve button next to it — putting one
            # there would tell a buyer that a human can click past the
            # prohibition. It is recorded as a refusal and nothing else.
            ev = self.store.log_event("refused", subject, f"agent:{agent}", "R0",
                                      {**detail, "action": action})
            return {"executed": False, "refused": True, "rung": "R0",
                    "event": ev["id"], "reason": r["reason"]}
        row = {"id": self.store.nid("ap"), "at": iso(), "action": action, "agent": agent,
               "subject": subject, "rung": r["rung"], "reason": r["reason"],
               "amount": amount, "detail": detail, "state": "pending",
               "decided_at": None, "decided_by": None}
        self.store.upsert(self.table, row)
        self.store.log_event("queued_for_approval", subject, f"agent:{agent}", r["rung"],
                             {"action": action, "approval": row["id"]})
        return {"executed": False, "rung": r["rung"], "approval": row["id"],
                "reason": r["reason"]}

    def decide(self, approval_id, human, approve=True, note=None, execute=None):
        row = self.store.by_id(self.table, approval_id)
        if not row or row["state"] != "pending":
            return {"ok": False, "why": "no pending approval with that id"}
        row["state"] = "approved" if approve else "rejected"
        row["decided_at"], row["decided_by"], row["note"] = iso(), human, note
        self.store.upsert(self.table, row)
        result = execute() if (approve and execute) else None
        self.store.log_event(row["action"] if approve else "approval_rejected",
                             row["subject"], f"human:{human}", row["rung"],
                             {"approval": approval_id, "note": note})
        return {"ok": True, "state": row["state"], "result": result}

    def pending(self):
        return [a for a in self.store.load(self.table) if a.get("state") == "pending"]


class Eval:
    """A scored classifier run against a labelled set.

    The point is not the headline accuracy. It is `costly`: the error class that
    actually hurts in this vertical (a missed emergency, a false 'covered', a
    wrongly matched part, a missed fraud) is ALWAYS reported on its own, because
    an aggregate score hides exactly the failure the buyer is paying to avoid.
    """

    def __init__(self, name, costly_label, costly_note):
        self.name, self.costly_label, self.costly_note = name, costly_label, costly_note

    def run(self, cases, predict):
        if not cases:
            return unmeasured("no labelled cases — an eval with no set is not an eval", field="score")
        rows, hits = [], 0
        tp = fp = fn = 0
        for c in cases:
            got = predict(c["input"])
            ok = got == c["label"]
            hits += ok
            if c["label"] == self.costly_label:
                tp += ok
                fn += (not ok)
            elif got == self.costly_label:
                fp += 1
            rows.append({"input": c["input"], "expected": c["label"], "got": got, "ok": ok})
        pos = tp + fn
        return {
            "name": self.name, "n": len(cases),
            "accuracy": round(hits / len(cases), 3),
            "costly_label": self.costly_label,
            "costly_recall": round(tp / pos, 3) if pos else None,
            "costly_missed": fn, "costly_false_alarms": fp,
            "costly_note": self.costly_note,
            "misses": [r for r in rows if not r["ok"]][:20],
            "generated": iso(),
        }


class Roi:
    """An ROI panel. Every line computes from the operator's OWN inputs, shows
    its arithmetic, and renders blank with a reason when an input is not
    recorded. Lines may be typed so the panel can refuse to add unlike things.

    kinds:  revenue | cash_timing | time_saved | scenario
    A `scenario` line is never presented as a saving (prevented incidents
    cannot be counted); a `time_saved` line is never summed into a revenue
    headline.
    """

    KINDS = ("revenue", "cash_timing", "time_saved", "scenario")

    def __init__(self, title):
        self.title, self.lines = title, []

    def line(self, label, kind, formula, inputs, compute, note=None, assumption=None):
        if kind not in self.KINDS:
            raise ValueError(f"unknown ROI line kind: {kind}")
        self.lines.append(dict(label=label, kind=kind, formula=formula, inputs=inputs,
                               compute=compute, note=note, assumption=assumption))
        return self

    def render(self, given):
        out = []
        for ln in self.lines:
            absent = [k for k in ln["inputs"] if given.get(k) in (None, "")]
            if absent:
                out.append({"label": ln["label"], "kind": ln["kind"], "formula": ln["formula"],
                            "value": None, "_missing": f"needs {', '.join(absent)}",
                            "note": ln["note"], "assumption": ln["assumption"]})
                continue
            try:
                val = ln["compute"](given)
            except Exception as e:  # a compute that blows up is a refusal, not a zero
                out.append({"label": ln["label"], "kind": ln["kind"], "formula": ln["formula"],
                            "value": None, "_missing": f"could not compute: {e}",
                            "note": ln["note"], "assumption": ln["assumption"]})
                continue
            if isinstance(val, dict) and "_missing" in val:
                val = dict(val)
                val.update(label=ln["label"], kind=ln["kind"], formula=ln["formula"],
                           note=ln["note"], assumption=ln["assumption"])
                out.append(val)
                continue
            out.append({"label": ln["label"], "kind": ln["kind"], "formula": ln["formula"],
                        "value": round(val, 2) if isinstance(val, (int, float)) else val,
                        "note": ln["note"], "assumption": ln["assumption"]})
        totals = {}
        for k in self.KINDS:
            vals = [o["value"] for o in out if o["kind"] == k and o.get("value") is not None]
            blanks = [o for o in out if o["kind"] == k and o.get("value") is None]
            totals[k] = {"total": round(sum(vals), 2) if vals else None,
                         "lines": len(vals), "blank": len(blanks)}
        return {
            "title": self.title, "generated": iso(), "lines": out, "totals": totals,
            "label": "THIS IS A MODEL — it computes from the numbers you gave us and "
                     "shows its arithmetic. It is not a forecast, not a guarantee, and "
                     "no line here comes from an industry benchmark.",
            "rules": ["time saved is reported in hours and dollars separately from revenue "
                      "and is never added into a revenue headline",
                      "a scenario line is an exposure you decide the value of — prevented "
                      "incidents cannot be counted",
                      "a line with an input we do not have is blank, never estimated"],
        }


# ---------------------------------------------------------------- streaks (for promotion)

def clean_streak(events, action, until_kind="corrected"):
    """Consecutive completed actions of this kind with no correction event after.
    The evidence half of the promotion rule; deliberately dumb and countable."""
    streak = 0
    for e in reversed(events):
        if e.get("kind") == until_kind and e.get("detail", {}).get("action") == action:
            break
        if e.get("kind") == action and str(e.get("actor", "")).startswith("agent:"):
            streak += 1
    return streak
