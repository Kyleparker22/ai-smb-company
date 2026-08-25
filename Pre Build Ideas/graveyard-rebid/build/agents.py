#!/usr/bin/env python3
"""Rebid OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import is_missing, iso, now, parse


# ---------------------------------------------------------------- the re-bid desk

def rebid(quote_id):
    """The standing order fires — or names, honestly, why it doesn't."""
    q = store.by_id("graveyard", quote_id)
    if not q:
        return {"error": "no such graveyard quote"}
    chk = core.rebid_check(q)
    if not chk["go"]:
        if chk["kind"] == "capability":
            r = gate.act("rebid_capability_loss", "desk", quote_id,
                         {"part": q.get("part"), "why": chk["why"]})
            return {"refused": chk["why"], "event": r["event"]}
        if chk["kind"] == "stand_down":
            r = gate.act("sell_uncounted_capacity", "desk", quote_id,
                         {"part": q.get("part"), "why": chk["why"]})
            return {"refused": chk["why"], "stand_down": True, "event": r["event"]}
        if chk["kind"] == "unrebiddable":
            ev = store.log_event("refused", quote_id, "agent:desk", "R0",
                                 {"action": "rebid_unrecorded_inputs", "why": chk["why"]})
            return {"refused": chk["why"], "event": ev["id"]}
        # cooldown / silence / no_idle / not_defensible — bounds, not errors
        return {"skipped": chk["why"], "kind": chk["kind"]}
    assert chk["price"] >= chk["floor"]["floor_price"]  # structural: never below the floor
    body = _rebid_copy(q, chk)
    g = gate.act("draft_rebid", "desk", quote_id,
                 {"summary": f"{q.get('part')} — ${chk['price']:,.0f}, wk {chk['week_of']}",
                  "preview": body[:110], "hours": float(q["hours"]),
                  "machine_class": q["machine_class"], "week_of": chk["week_of"],
                  "price": chk["price"], "floor": chk["floor"]})
    q["last_rebid_at"] = iso()
    q.setdefault("rebid_history", []).append(
        {"at": iso(), "price": chk["price"], "week_of": chk["week_of"], "response": None})
    store.upsert("graveyard", q)
    return {"drafted": True, "price": chk["price"], "week_of": chk["week_of"],
            "held_hours": chk["held_hours"], "draft": body, "floor": chk["floor"],
            "gate": g}


def _rebid_copy(q, chk):
    who = (q.get("contact") or "there").split()[0]
    f = chk["floor"]
    return (f"Hi {who} — you had us quote {q.get('part')} and the job went elsewhere at "
            f"${q.get('died_at_price', 0):,.0f}. We have open capacity the week of "
            f"{chk['week_of']}: same part, ${chk['price']:,.0f} — here's why the price moved. "
            f"Counted idle hours on our {q['machine_class']} cell price at marginal cost, not "
            f"full shop rate, and the arithmetic comes attached, line by line: "
            f"{f['arithmetic']}. If the work is placed and working, no reply needed — silence "
            f"is an answer, and we won't ask again this quarter.")


def propose_bid(quote_id, price):
    """A hand-typed price meets the floor. Below it there is NO PATH — the
    refusal prints the arithmetic. At or above it, the answer is the re-bid
    desk, so counted capacity gets checked too; this never drafts on its own."""
    q = store.by_id("graveyard", quote_id)
    if not q:
        return {"error": "no such graveyard quote"}
    f = core.floor_math(q)
    if "refused" in f:
        ev = store.log_event("refused", quote_id, "agent:desk", "R0",
                             {"action": "rebid_unrecorded_inputs", "why": f["refused"]})
        return {"refused": f["refused"], "event": ev["id"]}
    if price in (None, ""):
        return {"error": "no price given"}
    price = float(price)
    if price < f["floor_price"]:
        r = gate.act("bid_below_marginal_floor", "desk", quote_id,
                     {"price": price, "floor": f,
                      "why": f"${price:,.2f} is below the ${f['floor_price']:,.2f} floor"})
        return {"refused": (f"NO PATH — ${price:,.2f} is below the marginal floor of "
                            f"${f['floor_price']:,.2f}. {f['arithmetic']}. There is no rung, "
                            f"no click, and no approval that reaches under the floor."),
                "floor": f, "event": r["event"]}
    return {"ok": True, "floor": f,
            "note": f"${price:,.2f} clears the ${f['floor_price']:,.2f} floor — route it "
                    f"through the re-bid desk so counted capacity is checked before anything "
                    f"drafts"}


def record_loss(data):
    """A lost quote enters the graveyard and becomes a standing order — or is
    named UNREBIDDABLE at the door, so nobody discovers it a quarter late."""
    q = {"id": store.nid("gq"), "part": data.get("part"),
         "machine_class": data.get("machine_class"), "hours": data.get("hours"),
         "material_cost": data.get("material_cost"),
         "died_at_price": data.get("died_at_price"),
         "loss_reason": data.get("loss_reason") or "silence",
         "contact": data.get("contact"), "lost_at": data.get("lost_at") or iso()}
    store.upsert("graveyard", q)
    gate.act("record_loss", "desk", q["id"],
             {"part": q.get("part"), "loss_reason": q["loss_reason"]})
    return {"recorded": True, "quote": q, "status": core.quote_status(q)}


# ---------------------------------------------------------------- the deadline RFQ

def answer_deadline(m):
    """'Need 200 by Friday, can you?' — answered from COUNTED idle hours for
    the class, never optimism. No counted math, no committed answer."""
    mc, qty, hpp = m.get("machine_class"), m.get("qty"), m.get("hours_per_pc")
    missing = [k for k, v in (("machine_class", mc), ("qty", qty), ("hours_per_pc", hpp))
               if v in (None, "")]
    if missing:
        r = gate.act("promise_capacity_optimism", "desk", m["id"],
                     {"why": f"missing recorded {', '.join(missing)} — a yes without "
                             f"counted math is optimism"})
        return {"refused": (f"no committed answer — missing recorded {', '.join(missing)}. "
                            f"An estimator records them, then the counted math answers; "
                            f"optimism never does."), "event": r["event"]}
    needed = round(float(qty) * float(hpp), 1)
    wk = core.next_week()
    idle = core.counted_idle(mc, wk)
    if is_missing(idle):
        r = gate.act("sell_uncounted_capacity", "desk", m["id"], {"why": idle["_missing"]})
        return {"refused": (f"the desk stands down — {idle['_missing']}. A person confirms "
                            f"the schedule before any answer moves."),
                "stand_down": True, "event": r["event"]}
    who = (m.get("from") or "there").split()[0]
    if idle["idle_hours"] >= needed:
        answer = "yes"
        body = (f"Hi {who} — checked against the counted schedule, not a gut feel: we have "
                f"{idle['idle_hours']:g} counted idle hours on {mc} the week of {wk}; "
                f"{qty:g} pcs needs ~{needed:g}h — yes, bookable. Say the word and it goes "
                f"on the board today.")
    else:
        answer = "no"
        body = (f"Hi {who} — honest answer from the counted schedule: {qty:g} pcs needs "
                f"~{needed:g}h and we have {idle['idle_hours']:g} counted idle hours on {mc} "
                f"that week. We don't promise hours we can't count — we can hit the following "
                f"week, or split the run; your call.")
    g = gate.act("answer_deadline_rfq", "desk", m["id"],
                 {"summary": f"{answer} — needs {needed:g}h vs {idle['idle_hours']:g}h counted "
                             f"idle ({core.reserved_hours(mc, wk):g}h held by pending re-bids)",
                  "preview": body[:110], "basis": idle["basis"]})
    return {"answer": answer, "needed_hours": needed, "counted": idle, "draft": body,
            "gate": g}


# ---------------------------------------------------------------- intake

def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "deadline_rfq":
        r = answer_deadline(m)
        step = {"action": "answer_deadline_rfq", "why": c["why"]}
        step.update({k: v for k, v in r.items() if k in
                     ("answer", "draft", "refused", "stand_down", "needed_hours")})
        out["steps"].append(step)
        if "draft" in r:
            m["draft_reply"] = r["draft"]
    elif c["label"] == "rebid_reply":
        _mark_rebid_response(m, "reply")
        body = _rebid_reply_copy(m)
        gate.act("draft_rebid_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_rebid_reply", "draft": body,
                             "why": "a live buyer on a resurrected quote — a human closes"})
    elif c["label"] == "quote_status":
        body = _status_copy(m)
        gate.act("draft_status_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "answered from the quote record"})
    elif c["label"] == "spec_change":
        out["steps"].append({"action": "route_estimator",
                             "why": "a spec change voids the recorded hours — the estimator "
                                    "re-records hours and material before any number moves"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _mark_rebid_response(m, response):
    qid = m.get("quote_id")
    if not qid:
        return
    q = store.by_id("graveyard", qid)
    if not q:
        return
    hist = q.get("rebid_history") or []
    if hist and hist[-1].get("response") is None:
        hist[-1]["response"] = response
        q["rebid_history"] = hist
        store.upsert("graveyard", q)


def _rebid_reply_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — good to hear from you. The number stands as quoted: it's built from "
            f"our counted idle hours and the arithmetic came attached, so there's nothing to "
            f"haggle and nothing hidden. A person is on this today to talk timing and a PO.")


def _status_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling the quote record now: you'll get exactly where it sits — "
            f"received, in estimating, or priced — with dates, in one reply. Nothing here "
            f"guesses; the record answers.")


# ---------------------------------------------------------------- sweeps

def rebid_sweep(limit=12):
    """The graveyard sweep: every standing order checked against counted idle.
    Drafts hold their hours, so the sweep can never sell the same counted hour
    twice. Demo fixtures are skipped — the buttons own those."""
    out = {"drafted": 0, "watching": 0, "stood_down": 0, "skipped": 0}
    for q in store.load("graveyard"):
        if q.get("demo_tag"):
            continue
        chk = core.rebid_check(q)
        if chk["go"]:
            if out["drafted"] >= limit:
                out["watching"] += 1
                continue
            r = rebid(q["id"])
            out["drafted" if r.get("drafted") else "skipped"] += 1
        elif chk["kind"] in ("no_idle", "cooldown"):
            out["watching"] += 1
        elif chk["kind"] == "stand_down":
            out["stood_down"] += 1
        else:
            out["skipped"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at") and not m.get("demo_tag"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "rebids": rebid_sweep()}
