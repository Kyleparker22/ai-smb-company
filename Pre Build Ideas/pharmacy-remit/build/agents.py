#!/usr/bin/env python3
"""Remit OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


# ---------------------------------------------------------------- intake

def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "wrong_med":
        # The queue is structurally refused; the fixed script IS the reply,
        # sent at R2 because safety cannot wait for a click.
        ev = store.log_event("refused", msg_id, "agent:intake", "R0",
                             {"action": "wrong_med_message_queued",
                              "why": "the pharmacist-now script is the whole reply, "
                                     "immediately — this never waits in a queue"})
        r = gate.act("pharmacist_now_reply", "intake", msg_id,
                     {"summary": m.get("text", "")[:60], "script": "fixed"},
                     execute=lambda: core.PHARMACIST_NOW)
        m["reply"] = core.PHARMACIST_NOW
        out["steps"].append({"action": "pharmacist_now", "draft": core.PHARMACIST_NOW,
                             "refused": "queuing this message was refused — the script above "
                                        "went out whole, and the pharmacist is being "
                                        "interrupted now",
                             "why": c["why"], "gate": r, "event": ev["id"]})
    elif c["label"] == "pbm_question":
        body = _pbm_copy(m)
        gate.act("draft_pbm_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_pbm_reply", "draft": body,
                             "why": "the plan's own recorded words do the talking"})
    elif c["label"] == "price_complaint":
        body = _price_copy(m)
        gate.act("draft_price_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_price_reply", "draft": body,
                             "why": "answered from the fill record, line by line"})
    elif c["label"] == "refill":
        body = _refill_copy(m)
        gate.act("draft_refill_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_refill_reply", "draft": body,
                             "why": "answered from the fill record"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _pbm_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling your claim record with the plan now. What you'll get is the "
            f"plan's own recorded rejection reason, verbatim, and exactly what fixes it. If it "
            f"needs a prior authorization we start the request today and tell you what your "
            f"prescriber has to sign. Nothing in this answer is a guess.")


def _price_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — fair question, and it gets answered from the record, not a shrug: your "
            f"copay is set by your plan, so we're pulling what it billed this fill against last "
            f"fill and will show you the difference line by line. If the plan moved your drug to "
            f"a different tier, we'll say so plainly and lay out the options.")


def _refill_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking the fill record now; you'll get a yes/no with the ready time "
            f"in a moment. If it's waiting on the prescriber or the plan, we'll say which one, "
            f"and what we've already done about it.")


# ---------------------------------------------------------------- the autopsy sweep

def autopsy_sweep():
    out = {"audited": 0, "unauditable": [], "flagged": 0}
    existing = {f["id"] for f in store.load("findings")}
    for rm in store.load("remits"):
        a = core.autopsy(rm)
        if a.get("unauditable"):
            out["unauditable"].append(rm["pbm"])
            continue
        gate.act("run_autopsy", "audit", rm["id"],
                 {"summary": (f"{rm['pbm']} · {a['summary']['lines']} lines · "
                              f"{a['summary']['underpaid']} underpaid · "
                              f"{a['summary']['ambiguous']} ambiguous")})
        out["audited"] += 1
        for al in a["lines"]:
            if al["class"] == "correct":
                continue
            fid = f"fd_{rm['id']}_{al['script_ref']}"
            if fid in existing:
                continue
            f = core.finding_from_line(rm, al)
            store.upsert("findings", f)
            existing.add(fid)
            gate.act("flag_underpayment", "audit", fid,
                     {"summary": (f"{al['class']} "
                                  f"{'$%.2f' % al['delta'] if al.get('delta') is not None else '(both readings to a human)'}"
                                  f" — {al.get('clause') or 'clause unresolved'}")[:100]})
            out["flagged"] += 1
    return out


# ---------------------------------------------------------------- appeals

def draft_appeal(finding_id):
    f = store.by_id("findings", finding_id)
    if not f:
        return {"error": "no such finding"}
    if f.get("class") == "ambiguous":
        ev = store.log_event("refused", finding_id, "agent:recovery", "R0",
                             {"action": "auto_resolve_ambiguous_clause",
                              "why": "an appeal must cite one clause; this line has two "
                                     "plausible readings — a human picks, with both shown"})
        return {"refused": ("cannot appeal an ambiguous line — an appeal cites one clause and "
                            "this contract supports two readings. Both go to a human; software "
                            "never picks the convenient one."),
                "readings": f.get("readings"), "event": ev["id"]}
    if f.get("state") == "corrected":
        return {"note": "already corrected — nothing left to appeal"}
    c = core.contracts().get(f["pbm"]) or {}
    days_left = core.appeal_days_left(f)
    body = _appeal_copy(f, c, days_left)
    okp, why = core.phi_scrub_ok(body)
    assert okp, why  # structural: appeal drafts carry no patient identifiers
    r = gate.act("draft_appeal", "recovery", finding_id,
                 {"summary": (f"${f.get('delta') or 0:,.2f} — "
                              f"{(f.get('clause') or f.get('dir_clause') or '')[:56]}"),
                  "preview": body[:110]})
    f["state"] = "appeal_drafted"
    f["appeal_draft"] = body
    store.upsert("findings", f)
    return {"draft": body, "gate": r, "days_left": days_left}


def _appeal_copy(f, c, days_left):
    tail = (f"Submitted under {c.get('appeal_clause')}"
            + (f" ({days_left} days remaining)." if days_left is not None and days_left >= 0
               else " — NOTE: the recorded window has lapsed; escalation applies."))
    if f.get("class") == "dir_drift":
        return (f"Re: remittance {f['remit']}, script {f['script_ref']} ({f['drug']}, "
                f"qty {int(f['qty'])}). DIR withheld ${f['dir_taken']:.2f} against "
                f"${f['dir_expected']:.2f} due under {f['dir_clause']} — an over-withholding "
                f"of ${f['delta']:.2f}. We request a corrected remittance for the difference, "
                f"to the cent. {tail}")
    return (f"Re: remittance {f['remit']}, script {f['script_ref']} ({f['drug']}, "
            f"qty {int(f['qty'])}). Paid ${f['paid']:.2f} against ${f['expected']:.2f} due "
            f"under {f['clause']} ({f['basis']}) — an underpayment of ${f['delta']:.2f}. "
            f"We request reprocessing and a corrected remittance for the difference, to the "
            f"cent. {tail}")


# ---------------------------------------------------------------- the human acts

def resolve_ambiguous(finding_id, reading=None, human=None):
    f = store.by_id("findings", finding_id)
    if not f:
        return {"error": "no such finding"}
    if f.get("class") != "ambiguous":
        return {"error": "not an ambiguous finding"}
    if human in (None, ""):
        ev = store.log_event("refused", finding_id, "agent:audit", "R0",
                             {"action": "auto_resolve_ambiguous_clause",
                              "why": "software never resolves an ambiguous clause — both "
                                     "readings go to a human"})
        return {"refused": ("both readings go to a human — software never picks the "
                            "convenient one"),
                "readings": f.get("readings"), "event": ev["id"]}
    try:
        idx = int(reading)
        rd = (f.get("readings") or [])[idx]
    except (TypeError, ValueError, IndexError):
        return {"error": "pick a reading by index — both are shown"}
    delta = round(rd["expected"] - float(f.get("paid") or 0), 2)
    store.log_event("ambiguous_resolved", finding_id, f"human:{human}", "R1",
                    {"clause": rd["clause"], "delta": delta})
    if delta >= 0.01:
        f.update({"class": "underpaid", "expected": rd["expected"], "clause": rd["clause"],
                  "basis": rd["basis"], "delta": delta, "state": "open",
                  "why": f"resolved by {human} to {rd['clause']} — short ${delta:.2f}"})
    else:
        f.update({"class": "correct", "delta": 0.0, "state": "resolved_correct",
                  "why": f"resolved by {human} to {rd['clause']} — paid matches"})
    store.upsert("findings", f)
    return {"resolved": True, "finding": f}


def record_correction(finding_id, amount=None, human=None):
    f = store.by_id("findings", finding_id)
    if not f:
        return {"error": "no such finding"}
    if human in (None, ""):
        return {"refused": "a correction is posted by a human from the PBM's corrected "
                           "remittance — never assumed"}
    if amount in (None, ""):
        return {"error": "the corrected amount is required — it is the counted number"}
    amount = round(float(amount), 2)
    f.update({"state": "corrected", "corrected_amount": amount, "corrected_at": iso()})
    store.upsert("findings", f)
    ev = store.log_event("correction_recorded", finding_id, f"human:{human}", "R1",
                         {"action": "record_correction", "amount": amount})
    return {"corrected": True, "amount": amount, "event": ev["id"]}


# ---------------------------------------------------------------- the window sweep

def window_sweep(limit=25):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="appeal_window_alert", since_days=7)}
    for row in core.ledger()["rows"]:
        if out["alerts"] >= limit:
            break
        if row["id"] in already or row.get("state") in ("corrected", "resolved_correct"):
            continue
        dl = row.get("days_left")
        if dl is None or dl > 14:
            continue
        gate.act("appeal_window_alert", "recovery", row["id"],
                 {"summary": ((f"window CLOSED {-dl}d ago" if dl < 0
                               else f"{dl}d left in the appeal window")
                              + f" — ${row.get('delta') or 0:,.2f} {row['class']} at {row['pbm']}"),
                  "days_left": dl})
        out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "autopsy": autopsy_sweep(),
            "windows": window_sweep()}
