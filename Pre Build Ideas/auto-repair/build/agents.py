#!/usr/bin/env python3
"""Bay OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def classify_sweep():
    """Classify every unlabelled declined item. Safety items become call tasks
    immediately — they never wait for a re-offer cycle."""
    out = {"classified": 0, "safety_calls": 0}
    for d in store.load("declined"):
        if d.get("label"):
            continue
        c = core.classify_item(d.get("text", ""))
        d.update(label=c["label"], why=c["why"])
        store.upsert("declined", d)
        gate.act("classify_item", "sheetreader", d["id"], {"label": c["label"], "why": c["why"]})
        out["classified"] += 1
        if c["label"] == "safety_critical" and not d.get("demo_tag"):
            gate.act("safety_call_task", "sheetreader", d["id"],
                     {"summary": f"CALL, don't text: {d.get('text','')[:70]}",
                      "rule": core.SAFETY_CONTACT_RULE})
            out["safety_calls"] += 1
    return out


def reoffer_sweep(limit=25):
    """Draft re-offers for non-safety items past cooldown. Bounded per run."""
    out = {"drafted": 0, "call_tasks": 0, "skipped": 0}
    for d in store.load("declined"):
        if out["drafted"] >= limit:
            break
        plan = core.reoffer_plan(d)
        if plan["action"] == "draft_reoffer":
            okt, why = core.can_text(d)
            if not okt:  # defence in depth — reoffer_plan already routed safety away
                store.log_event("refused", d["id"], "agent:recovery", "R0",
                                {"action": "send_safety_text", "why": why})
                continue
            touch_n = len(d.get("touches") or []) + 1
            body = _reoffer_copy(d, touch_n)
            gate.act("draft_reoffer", "recovery", d["id"],
                     {"summary": f"${d.get('value',0):,.0f} declined {d.get('label')}: {d.get('text','')[:60]}",
                      "touch": touch_n, "preview": body[:110]})
            d.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
            store.upsert("declined", d)
            out["drafted"] += 1
        elif plan["action"] == "call_task":
            out["call_tasks"] += 1
        else:
            out["skipped"] += 1
    return out


def _reoffer_copy(d, touch_n):
    """Drafted for a human to send. Factual, from the sheet, priced from the
    estimate on file. Never urgency theater, never a safety claim either way."""
    cust = store.by_id("customers", d.get("customer_id")) or {}
    name = (cust.get("name") or "there").split()[0]
    item = (d.get("text") or "the item on your inspection sheet").rstrip(".")
    val = f"${d.get('value', 0):,.0f}"
    when = (d.get("declined_at") or "")[:10]
    return {
        1: (f"Hi {name} — from your last visit ({when}) we still have this on file: "
            f"\"{item}\". The estimate was {val} and it still stands. Want us to set a time?"),
        2: (f"Hi {name} — quick follow-up on \"{item}\". Same {val} estimate; parts are "
            f"available this week. Reply Y and we'll find you a slot."),
        3: (f"Hi {name} — last note from us on \"{item}\" ({val}). If now isn't the time, "
            f"no problem — we'll leave it on your file and you can pick it up whenever."),
    }.get(touch_n, f"Hi {name} — following up on \"{item}\" ({val}).")


def _nudge_copy(r, age):
    return (f"Hi — your estimate for ${r.get('total', 0):,.0f} from {age} days ago is still "
            f"open. Happy to walk through it line by line, adjust, or get you scheduled — "
            f"whatever helps you decide.")


def price_quote(job_kind):
    """The price question, answered honestly: a band from OUR closed ROs of that
    kind, or a refusal that says why. A firm number never leaves software."""
    band = core.price_band(job_kind)
    ev = store.log_event("refused", job_kind, "agent:frontdesk", "R0",
                        {"action": "quote_firm_price",
                         "why": "a firm price needs a technician and an inspected car"})
    if "_missing" in band:
        return {"band": None, "why": band["_missing"], "refusal_event": ev["id"],
                "say": ("I can't give you a fair number for that from our history yet — "
                        "let's get eyes on the car and the advisor will price it exactly.")}
    lo, hi = band["band"]
    return {"band": band["band"], "n": band["n"], "basis": band["basis"], "refusal_event": ev["id"],
            "say": (f"For that job our own recent work has run ${lo:,}–${hi:,} depending on what "
                    f"we find — a firm number takes an inspection, and the advisor confirms it "
                    f"before any work starts.")}


def send_text(item_id):
    """The API surface a demo pushes on: try to text a declined item."""
    d = store.by_id("declined", item_id)
    if not d:
        return {"error": "no such item"}
    okt, why = core.can_text(d)
    if not okt:
        ev = store.log_event("refused", item_id, "agent:recovery", "R0",
                             {"action": "send_safety_text", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_reoffer", "recovery", item_id,
                    {"summary": f"text re-offer: {d.get('text','')[:60]}"})


def call_sweep():
    out = {"handled": 0}
    for call in store.load("calls"):
        if call.get("handled_at"):
            continue
        c = core.classify_call(call.get("transcript", ""))
        call.update(label=c["label"], handled_at=iso())
        store.upsert("calls", call)
        gate.act("classify_call", "frontdesk", call["id"], {"label": c["label"], "why": c["why"]})
        if c["label"] == "no_phone_diagnosis":
            store.log_event("refused", call["id"], "agent:frontdesk", "R0",
                            {"action": "phone_diagnosis", "why": c["why"]})
        out["handled"] += 1
    return out


def nudge_sweep():
    """One nudge per presented-and-aging estimate per week."""
    out = {"drafted": 0}
    recent = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=7)
              if (e.get("detail") or {}).get("action") == "draft_approval_nudge"}
    for r in store.load("ros"):
        if r.get("state") != "presented" or r.get("closed_at") or r["id"] in recent or r.get("demo_tag"):
            continue
        from _kit.store import parse
        age = (now() - (parse(r.get("presented_at")) or now())).days
        if age < 3:
            continue
        body = _nudge_copy(r, age)
        gate.act("draft_approval_nudge", "advisor", r["id"],
                 {"summary": f"estimate ${r.get('total',0):,.0f} presented {age}d ago",
                  "age_days": age, "preview": body[:110]})
        out["drafted"] += 1
    return out


def run_all():
    return {"classify": classify_sweep(), "reoffer": reoffer_sweep(),
            "calls": call_sweep(), "nudges": nudge_sweep()}
