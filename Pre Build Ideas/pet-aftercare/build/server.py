#!/usr/bin/env python3
"""Ember OS — server. Stdlib only, 127.0.0.1:8880."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8880


def _pet_row(p):
    st = core.chain_status(p)
    return {"id": p["id"], "name": p.get("name"), "species": p.get("species"),
            "family": p.get("family"), "tag": p.get("tag"),
            "service_level": p.get("service_level"), "election_ref": p.get("election_ref"),
            "chain_state": st["state"], "at": st.get("at"),
            "why": st.get("why"), "demo_tag": p.get("demo_tag"),
            "returned": bool(p.get("returned_at"))}


def board(q, b):
    pets = store.load("pets")
    in_care = [p for p in pets if not p.get("returned_at") and not p.get("final_disposition_at")]
    holds = [p for p in in_care if core.chain_status(p)["state"] == "HOLD"]
    ready = [p for p in in_care if p.get("ashes_ready_at")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"in_care": len(in_care), "chains_on_hold": len(holds),
                      "ready_to_come_home": len(ready), "messages_open": len(msgs),
                      "clinics": len(store.load("clinics")),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def pets_list(q, b):
    rows = [_pet_row(p) for p in store.load("pets")]
    rows.sort(key=lambda r: (r["chain_state"] != "HOLD", not r["demo_tag"]))
    return {"rows": rows[:80], "total": len(rows),
            "holds": sum(1 for r in rows if r["chain_state"] == "HOLD")}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/pets"): pets_list,
    ("GET", "/api/pets/<id>/chain"): lambda q, b: core.chain_narrative(
        store.by_id("pets", q["id"]) or {}),
    ("POST", "/api/pets/<id>/transfer"): lambda q, b: core.record_transfer(
        q["id"], to=b.get("to"), tag_read=b.get("tag"), by=b.get("by")),
    ("POST", "/api/loads/<id>/add"): lambda q, b: core.add_to_load(q["id"], b.get("pet")),
    ("POST", "/api/pets/<id>/service-level"): lambda q, b: core.change_service_level(
        q["id"], b.get("level"), human=b.get("human"), consent_ref=b.get("consent_ref")),
    ("POST", "/api/pets/<id>/proof-approve"): lambda q, b: core.approve_proof(
        q["id"], family=b.get("family"), ref=b.get("ref")),
    ("POST", "/api/pets/<id>/disposition"): lambda q, b: core.final_disposition(
        q["id"], human=b.get("human")),
    ("POST", "/api/tone-check"): lambda q, b: agents.try_family_draft(
        b.get("text", ""), b.get("pet_id")),
    ("GET", "/api/returns"): lambda q, b: core.return_board(),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "owner"), b.get("approve", True)),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Ember OS")
