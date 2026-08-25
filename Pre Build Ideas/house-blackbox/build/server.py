#!/usr/bin/env python3
"""Blackbox OS — server. Stdlib only, 127.0.0.1:8882."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso, now, parse

PORT = 8882


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    homes = store.load("homes")
    members = store.load("members")
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    thin = sum(1 for h in homes if not h.get("demo_tag")
               and any(c.get("install_year") in (None, "") for c in h.get("components") or []))
    return {"config": store.load("config"),
            "board": {"homes": len([h for h in homes if not h.get("demo_tag")]),
                      "members": len([m for m in members if not m.get("demo_tag")]),
                      "thin_records": thin,
                      "messages_open": len(msgs),
                      "renewals_due_90d": core.renewals_due_90d(),
                      "honesty": core.honesty_board(),
                      "won": core.won_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def homes_list(q, b):
    rows = []
    for h in store.load("homes"):
        comps = h.get("components") or []
        unknown = [c["kind"] for c in comps if c.get("install_year") in (None, "")]
        rows.append({"id": h["id"], "owner": h.get("owner"), "address": h.get("address"),
                     "demo_tag": h.get("demo_tag"), "components": len(comps),
                     "unknown": unknown,
                     "callbacks_36mo": core.callbacks_in_window(h)})
    rows.sort(key=lambda r: (not bool(r["demo_tag"]), r["id"]))
    return {"rows": rows[:40], "total": len(rows)}


def members_list(q, b):
    ref = now()
    rows = []
    for m in store.load("members"):
        end = parse(m.get("term_end"))
        rows.append({"id": m["id"], "owner": m.get("owner"), "home_id": m.get("home_id"),
                     "locked_price": m.get("locked_price"), "demo_tag": m.get("demo_tag"),
                     "term_end": m.get("term_end"),
                     "days_to_renewal": (end - ref).days if end else None,
                     "renewal_price": m.get("renewal_price"),
                     "renewal_direction": m.get("renewal_direction")})
    rows.sort(key=lambda r: (not bool(r["demo_tag"]), r["days_to_renewal"] or 9999))
    return {"rows": rows[:40], "total": len(rows)}


def reprice_midterm(q, b):
    # Deliberately NOT a price change: there is no code path that writes a
    # locked price mid-term. This endpoint exists so the refusal is visible.
    return gate.act("reprice_mid_term", "membership", q["id"],
                    {"why_asked": (b or {}).get("why", "operator probe")})


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/homes"): homes_list,
    ("GET", "/api/homes/<id>"): lambda q, b: core.blackbox(
        store.by_id("homes", q["id"]) or {"id": q["id"]}),
    ("POST", "/api/homes/<id>/quote"): lambda q, b: agents.draft_quote(q["id"]),
    ("GET", "/api/members"): members_list,
    ("POST", "/api/members/<id>/reprice-midterm"): reprice_midterm,
    ("POST", "/api/members/<id>/renewal"): lambda q, b: agents.renewal_notice(q["id"]),
    ("GET", "/api/honesty"): lambda q, b: {"honesty": core.honesty_board()},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "owner"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "owner"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Blackbox OS")
