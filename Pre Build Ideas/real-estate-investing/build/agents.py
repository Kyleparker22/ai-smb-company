#!/usr/bin/env python3
"""Deal OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})
    listing = store.by_id("listings", m.get("listing_id")) if m.get("listing_id") else None

    if c["label"] == "advice_ask":
        ev = store.log_event("refused", msg_id, "agent:desk", "R0",
                             {"action": "recommend_purchase",
                              "why": "a verdict from software is unlicensed investment advice"})
        body = _advice_copy(m, listing)
        okd, why = core.advice_ok(body)
        assert okd, why      # structural: the shipped copy passes its own check
        gate.act("draft_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_reply", "draft": body,
                             "refused": "no verdict was produced — the arithmetic, the bands, "
                                        "and the decision stays yours",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "run_numbers":
        if listing:
            res = analyze(listing["id"])
            body = _numbers_copy(m, listing, res)
            gate.act("draft_reply", "desk", msg_id,
                     {"summary": f"underwrite {listing.get('address')}", "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "run_underwrite", "analysis": res["summary"],
                                 "draft": body, "why": c["why"]})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "no listing linked — a person matches the address first"})
    elif c["label"] == "scenario_ask":
        body = _scenario_copy(m, listing)
        gate.act("draft_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_reply", "draft": body,
                             "why": "answered with bands and the grid — never one confident number"})
    elif c["label"] == "criteria_update":
        g = gate.act("record_criteria", "desk", msg_id,
                     {"summary": f"criteria change requested: {m.get('text', '')[:70]}",
                      "verbatim": m.get("text", "")})
        out["steps"].append({"action": "record_criteria", "gate": g,
                             "why": "the investor's bar is theirs — recorded from their words, "
                                    "a human confirms before the screen re-runs"})
    elif c["label"] == "status":
        wk = core.screened_this_week()
        body = (f"This week, counted: {wk['underwrites']} underwrites run, "
                f"{wk['cleared_bar']} deal(s) cleared your recorded bar. Nothing here is a "
                f"recommendation — the ranked screen with why-traces is in your dashboard.")
        gate.act("draft_reply", "desk", msg_id, {"summary": "status", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_reply", "draft": body,
                             "why": "answered from the screen's own record"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _advice_copy(m, listing):
    who = (m.get("from") or "there").split()[0]
    tail = ""
    if listing:
        uw = core.underwrite(listing, "ltr")
        if "refused" not in uw:
            tail = (f" On {listing.get('address')}: at the stated assumptions it models "
                    f"${uw['cashflow_monthly']:,.0f}/mo, DSCR {uw['dscr']}, "
                    f"{uw['cash_on_cash']:.1%} cash-on-cash — every input is on the sheet.")
    return (f"Hi {who} — honest answer: we don't do verdicts, on purpose. A yes from a tool is "
            f"someone else's judgment wearing math.{tail} What we can give you is the full "
            f"arithmetic, the bear/base/bull bands, and the stress grid — and the decision "
            f"stays yours. {core.NOT_ADVICE}")


def _numbers_copy(m, listing, res):
    who = (m.get("from") or "there").split()[0]
    s = res["summary"]
    lines = []
    for st, r in s.items():
        if r.get("unmeasured"):
            lines.append(f"{st.upper()}: not measurable — {r['refused'][:80]}")
        else:
            lines.append(f"{st.upper()}: ${r['cashflow_monthly']:,.0f}/mo, DSCR {r['dscr']}, "
                         f"CoC {r['cash_on_cash']:.1%}")
    return (f"Hi {who} — {listing.get('address')}, all three ways, same stated assumptions: "
            + " · ".join(lines) +
            f". Payoff on the 30-year runs {s[next(iter(s))]['payoff']['years']} years as "
            f"amortized. Full sheet with every input is attached. {core.NOT_ADVICE}")


def _scenario_copy(m, listing):
    who = (m.get("from") or "there").split()[0]
    if listing:
        sens = core.sensitivity(listing, "ltr")
        if "refused" not in sens:
            worst = sens["grid"][-1][0]
            return (f"Hi {who} — the honest way to answer a what-if is the grid, not a "
                    f"prediction. Worst corner we model (rates +2, rent -10%): DSCR "
                    f"{worst['dscr']}, CoC {worst['coc']:.1%}. {sens['note']} {core.NOT_ADVICE}")
    return (f"Hi {who} — we answer what-ifs with bands and the stress grid rather than one "
            f"confident number — a point prediction about rates is fiction with decimals. "
            f"Tell me the property and I'll run the full grid. {core.NOT_ADVICE}")


# ---------------------------------------------------------------- analysis

def analyze(listing_id, overrides=None):
    """All three strategies, one listing. Records the analysis (counted, with
    whether it cleared the recorded bar)."""
    l = store.by_id("listings", listing_id)
    if not l:
        return {"error": "no such listing"}
    summary = {}
    for s in core.STRATEGIES:
        summary[s] = core.underwrite(l, s, overrides)
    gate.act("run_underwrite", "underwriter", listing_id,
             {"summary": f"{l.get('address')} × 3 strategies"})
    crit = (store.load("criteria") or [None])[0]
    cleared = False
    if crit:
        cleared = any("refused" not in r and r["dscr"] >= crit["min_dscr"]
                      and r["cash_on_cash"] >= crit["min_coc"] for r in summary.values())
    store.upsert("analyses", {"id": store.nid("an"), "listing_id": listing_id,
                              "at": iso(), "cleared_bar": cleared})
    return {"listing": l, "summary": summary, "cleared_bar": cleared,
            "not_advice": core.NOT_ADVICE}


def screen_sweep(limit=10):
    """Run the screen; draft alerts (R1) for NEW deals clearing the bar."""
    scr = core.deal_screen()
    if "refused" in scr:
        return scr
    drafted = 0
    for row in scr["rows"]:
        l = store.by_id("listings", row["listing"]["id"])
        if l.get("alert_drafted") or drafted >= limit:
            continue
        body = (f"New match on your recorded bar: {l['address']} at ${l['price']:,} — "
                f"models {row['cashflow_monthly']:,.0f}/mo as {row['strategy'].upper()}, "
                f"DSCR {row['dscr']}, CoC {row['cash_on_cash']:.1%}. {row['why']}. "
                f"Full sheet ready. {core.NOT_ADVICE}")
        okd, why = core.advice_ok(body)
        assert okd, why
        gate.act("draft_deal_alert", "screener", l["id"],
                 {"summary": f"{l['address']} clears the bar", "preview": body[:110]})
        l["alert_drafted"] = iso()
        store.upsert("listings", l)
        drafted += 1
    return {"screened": scr["considered"], "matches": len(scr["rows"]),
            "alerts_drafted": drafted,
            "note": "alerts drafted for a human to send — a six-figure nudge never sends itself"}


def rate_watch():
    """Stale rates flag every market they touch. Always the safe direction."""
    flagged = []
    for mkt in store.load("markets"):
        r = core.market_rate(mkt)
        if r.get("stale"):
            gate.act("flag_rate_move", "watch", mkt["id"],
                     {"summary": f"{mkt.get('name')}: rate {r['age_days']}d old — every number "
                                 f"it touches is flagged stale"})
            flagged.append(mkt["id"])
    return {"flagged": flagged,
            "note": "a stale rate is disclosed on every underwrite it feeds, never silently used"}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at") and not m.get("demo_tag"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "screen": screen_sweep(),
            "rates": rate_watch()}
