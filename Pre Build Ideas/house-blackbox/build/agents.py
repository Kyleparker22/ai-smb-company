#!/usr/bin/env python3
"""Blackbox OS — the agents. Everything routes through `core.gate`. Stdlib only.

Deliberately absent: any function that changes a member's locked price mid-term.
That is not an oversight — `reprice_mid_term` is R0 structural, so the code
path does not exist to be misused."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "emergency":
        gas = core.is_gas(m.get("text", ""))
        gate.act("log_emergency", "dispatch", msg_id,
                 {"verbatim": m.get("text", ""), "gas": gas, "from": m.get("from")})
        if gas:
            ev = store.log_event("refused", msg_id, "agent:dispatch", "R0",
                                 {"action": "dismiss_gas_smell",
                                  "why": "a gas smell gets the evacuate script verbatim, "
                                         "never reassurance"})
            body = _gas_copy(m)
            out["steps"].append({"action": "gas_script", "draft": body, "event": ev["id"],
                                 "why": "the evacuate script rides verbatim — R0 forbids "
                                        "softening it"})
        else:
            body = _emergency_copy(m)
            out["steps"].append({"action": "emergency_dispatch", "draft": body,
                                 "why": "a no-heat/no-cool/burst call goes to the top of the "
                                        "board, never a queue"})
        gate.act("draft_emergency_reply", "dispatch", msg_id,
                 {"summary": m.get("text", "")[:60], "gas": gas, "preview": body[:110]})
        m["draft_reply"] = body
    elif c["label"] == "fairness":
        r = fairness_reply(m)
        out["steps"].append(r)
    elif c["label"] == "quote_ask":
        gate.act("log_quote_request", "membership", msg_id, {"from": m.get("from")})
        if m.get("home_id"):
            r = draft_quote(m["home_id"], message=m)
            out["steps"].append(r)
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "no home record matched this sender — a person links "
                                        "the black box before any price is spoken"})
    elif c["label"] == "booking":
        body = _booking_copy(m)
        gate.act("draft_booking_reply", "scheduler", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_booking_reply", "draft": body,
                             "why": "answered from the schedule"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


# ---------------------------------------------------------------- quotes

def draft_quote(home_id, message=None):
    home = store.by_id("homes", home_id)
    if not home:
        return {"error": "no such home"}
    q = core.membership_quote(home)
    okc, whyc = core.quote_complete(q)
    assert okc, whyc  # structural: a quote that hides a factor cannot ship
    if q["provisional"]:
        ev = store.log_event("refused", home_id, "agent:membership", "R0",
                             {"action": "invent_component_age",
                              "why": q["reason"]})
        body = _provisional_copy(home, q)
        r = gate.act("draft_quote", "membership", home_id,
                     {"summary": f"PROVISIONAL ${q['monthly']:.0f}/mo — {q['unknown_components']}",
                      "preview": body[:110]})
        return {"action": "draft_quote", "quote": q, "draft": body, "gate": r,
                "refused": ("a personalized price was NOT produced — "
                            + q["reason"]), "event": ev["id"],
                "why": "unrecorded ages price provisional, never guessed"}
    body = _quote_copy(home, q)
    r = gate.act("draft_quote", "membership", home_id,
                 {"summary": f"${q['monthly']:.0f}/mo — {len(q['factors'])} factors shown",
                  "preview": body[:110]})
    return {"action": "draft_quote", "quote": q, "draft": body, "gate": r,
            "why": "priced from the home's own black box — every factor in dollars"}


def _factor_lines(q):
    out = []
    for f in q["factors"]:
        sign = "+" if f["dollars"] >= 0 else "-"
        out.append(f"  {sign}${abs(f['dollars']):.0f}/mo — {f['why']}")
    return "\n".join(out)


def _quote_copy(home, q):
    who = (home.get("owner") or "there").split()[0]
    return (f"Hi {who} — here is your membership price, computed from your own home's record, "
            f"line by line:\n{_factor_lines(q)}\nTotal: ${q['monthly']:.0f}/mo, locked for the "
            f"term. Nothing here is a market number: if any line looks wrong, tell us and we "
            f"correct the record — the price follows the record, in both directions.")


def _provisional_copy(home, q):
    who = (home.get("owner") or "there").split()[0]
    return (f"Hi {who} — honest answer: we can't give you a personalized price yet. "
            f"{q['reason']} Until then the plan is a flat ${q['monthly']:.0f}/mo, and the "
            f"moment the record is complete your price is recomputed from it — shown line "
            f"by line, in both directions.")


# ---------------------------------------------------------------- fairness

def fairness_reply(m):
    home = store.by_id("homes", m.get("home_id") or "")
    if not home:
        return {"action": "route_human",
                "why": "fairness challenge with no home record matched — a person links the "
                       "record; the answer is always the asker's own factors"}
    q = core.membership_quote(home)
    if q["provisional"]:
        body = _provisional_copy(home, q)
    else:
        who = (home.get("owner") or "there").split()[0]
        body = (f"Hi {who} — fair question, and here is the honest answer: your price is not "
                f"set against anyone else's. It is computed from your own home's record:\n"
                f"{_factor_lines(q)}\nTotal: ${q['monthly']:.0f}/mo. Your neighbor's plan is "
                f"computed the same way from their record — a younger furnace or a different "
                f"history is the whole difference. If any line above looks wrong, tell us and "
                f"we correct the record; the price follows it.")
    okf, whyf = core.fairness_ok(body)
    assert okf, whyf  # structural: the shipped copy passes its own check
    gate.act("draft_fairness_reply", "membership", m["id"],
             {"summary": m.get("text", "")[:60], "preview": body[:110]})
    m["draft_reply"] = body
    return {"action": "draft_fairness_reply", "draft": body,
            "why": "the asker's own factors, verbatim — never 'market rates'"}


# ---------------------------------------------------------------- renewals

def renewal_notice(member_id):
    rp = core.renewal_reprice(member_id)
    if "error" in rp:
        return rp
    m = store.by_id("members", member_id)
    home = store.by_id("homes", m["home_id"]) or {}
    who = (home.get("owner") or m.get("owner") or "there").split()[0]
    if rp.get("provisional"):
        body = (f"Hi {who} — at renewal your plan goes provisional: {rp['quote']['reason']} "
                f"Flat ${rp['quote']['monthly']:.0f}/mo until the record is complete.")
    else:
        delta_lines = "\n".join(f"  {d['why']}" for d in rp["deltas"]) or "  no factor moved"
        arrow = {"up": "up", "down": "DOWN", "flat": "unchanged"}[rp["direction"]]
        body = (f"Hi {who} — your renewal, from your home's own record. Last term: "
                f"${rp['locked_price']:.0f}/mo. This term: ${rp['new_monthly']:.0f}/mo "
                f"({arrow}). What moved, exactly:\n{delta_lines}\nEvery line traces to your "
                f"equipment record — nothing else sets the price.")
    r = gate.act("draft_renewal_notice", "membership", member_id,
                 {"summary": f"${rp.get('locked_price', 0):.0f} → "
                             f"${(rp.get('new_monthly') or rp['quote']['monthly']):.0f}/mo "
                             f"({rp.get('direction', 'provisional')})",
                  "preview": body[:110]})
    if not rp.get("provisional"):
        m.update(renewal_price=rp["new_monthly"], renewal_direction=rp["direction"],
                 renewal_deltas=rp["deltas"], renewal_at=iso())
        store.upsert("members", m)
    return {"action": "draft_renewal_notice", "reprice": rp, "draft": body, "gate": r,
            "why": "the factor deltas ride verbatim — a price that moved names what moved it"}


def renewal_sweep(window_days=45, limit=25):
    out = {"drafted": 0, "skipped": 0}
    ref = now()
    for m in store.load("members"):
        if out["drafted"] >= limit:
            break
        if m.get("demo_tag") or m.get("renewal_price") is not None or not m.get("term_end"):
            out["skipped"] += 1
            continue
        end = parse(m["term_end"])
        if not end or not (0 <= (end - ref).days <= window_days):
            out["skipped"] += 1
            continue
        renewal_notice(m["id"])
        out["drafted"] += 1
    return out


# ---------------------------------------------------------------- copy

def _gas_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"{who} — {core.GAS_SCRIPT} A dispatcher is being paged with your address right "
            f"now and will call you once you're outside.")


def _emergency_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — this goes to the top of the board, not a queue. A dispatcher is "
            f"being paged now with your address and your home's equipment record, so the "
            f"tech arrives knowing what's in the house. If at any point you smell gas, "
            f"leave first and call from outside.")


def _booking_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling the schedule now; you'll get two concrete time windows to "
            f"pick from in a moment. The visit also updates your home's record, which is "
            f"what your membership price is computed from.")


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "renewals": renewal_sweep()}
