#!/usr/bin/env python3
"""Receipt OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    """Triage one message. A wire-change request is recorded VERBATIM in the
    control ledger (that record is the first receipt of the chain), the
    callback path is stated, and acting from the message is refused at R0."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "wire_change":
        entry = core.ledger_append("wire_change_request", wire_id=m.get("wire_id"),
                                   detail={"verbatim": m.get("text", ""),
                                           "channel": m.get("channel", "email"),
                                           "from": m.get("from")},
                                   demo_tag=m.get("demo_tag"))
        gate.act("route_wire_change", "intake", msg_id, {"summary": m.get("text", "")[:60],
                                                         "ledger": entry["id"]})
        ev = store.log_event("refused", msg_id, "agent:intake", "R0",
                             {"action": "act_on_emailed_wire_change", "why": c["why"]})
        out["steps"].append({
            "action": "route_wire_change", "said": core.WIRE_PROTOCOL,
            "ledger": entry["id"], "recorded_verbatim": True,
            "callback_path": (f"verification happens by a HUMAN calling {core.CALLBACK_REF}; "
                              f"when the call is made, the receipt is recorded with who called "
                              f"and that reference — the email's number has no field to land in"),
            "why": c["why"], "event": ev["id"]})
    elif c["label"] == "insurer_info":
        body = _insurer_copy(m)
        okp, why = core.premium_ok(body)
        assert okp, why  # structural: the shipped copy passes its own check
        gate.act("draft_insurer_reply", "backoffice", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_insurer_reply", "draft": body,
                             "why": "the coverage-year file answers — counts, exceptions, "
                                    "drill record; no premium claim"})
    elif c["label"] == "realtor_proof":
        r = draft_realtor_proof()
        out["steps"].append({"action": "draft_realtor_proof", "draft": r["proof"],
                             "why": "counted proof, zero client data — scrub-checked before it drafts"})
    elif c["label"] == "closing_status":
        out["steps"].append({"action": "route_human",
                             "why": "closing status lives in the closing file system — a person answers"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _insurer_copy(m):
    cov = core.coverage_year()
    untested = [c for c, d in cov["drills"].items() if d["status"] == "UNTESTED"]
    return (f"Our coverage-year control file is ready for your underwriter: "
            f"{cov['verifications']} callback verifications, {cov['blocked_attempts']} blocked "
            f"attempts, {cov['dual_control_releases']} dual-control releases, and the exceptions "
            f"list — {len(cov['exceptions'])} wire(s) that moved with a gap, each named. "
            f"Drill record included"
            + (f"; {', '.join(untested)} is listed as UNTESTED because no drill ran this period"
               if untested else "")
            + ". Underwriters price; we evidence — you will find no premium claim in the file.")


def act_on_wire_change(msg_id):
    """The probe surface a demo pushes on: ask the system to act on the
    emailed change. Refused at R0 — never an approvable row."""
    return gate.act("act_on_emailed_wire_change", "intake", msg_id)


def record_callback(wire_id, who_called):
    """The verified-callback path. A HUMAN places the call; the system records
    the receipt. `number_called_ref` is fixed by construction — this function
    has no parameter that could carry the email's number into the record."""
    detail = {"who_called": who_called, "number_called_ref": core.CALLBACK_REF}
    r = gate.act("record_control_event", "ledger", wire_id, dict(detail, control="callback_verification"),
                 execute=lambda: core.ledger_append("callback_verification", wire_id, detail))
    return r


def record_dual_control(wire_id, human_a, human_b):
    """Two named humans on every release. The same name twice is a
    single-control release wearing a costume — refused."""
    if not human_a or not human_b or human_a == human_b:
        ev = store.log_event("refused", wire_id, "agent:ledger", "R0",
                             {"action": "record_dual_control",
                              "why": "dual control needs two distinct humans"})
        return {"refused": "dual control needs two distinct named humans — the same name twice "
                           "is a single-control release wearing a costume", "event": ev["id"]}
    detail = {"human_a": human_a, "human_b": human_b}
    return gate.act("record_control_event", "ledger", wire_id, dict(detail, control="dual_control_release"),
                    execute=lambda: core.ledger_append("dual_control_release", wire_id, detail))


def record_drill(control, result, run_by):
    if control not in core.CONTROLS:
        return {"error": f"unknown control: {control}"}
    detail = {"control": control, "result": result, "run_by": run_by}
    return gate.act("record_control_event", "ledger", f"drill:{control}", detail,
                    execute=lambda: core.ledger_append("drill_result", None, detail))


def attest_control(control):
    """Can the file say this control is in place? Only with a drill behind it —
    and even then it says 'tested', with the date. UNTESTED → the claim is
    refused at R0 and the honest read comes back instead."""
    st = core.drill_status(control)
    if st["status"] == "UNTESTED":
        r = gate.act("claim_untested_control", "backoffice", control, {"status": st})
        return {"refused": True, "status": st, "gate": r,
                "why": "no drill on record — the file reads UNTESTED, never 'in place'"}
    return {"refused": False, "status": st,
            "why": "tested — the packet cites the drill record with its date; the attestation "
                   "rides in the R1 packet, never asserted standalone"}


def draft_renewal_packet():
    """The insurer-facing renewal packet: the counted year, the exceptions
    honestly listed, the drill record, and no premium claim anywhere. R1 —
    a human sends it."""
    cov = core.coverage_year()
    text = core.render_renewal_packet(cov)
    okp, why = core.premium_ok(text)
    assert okp, why  # structural: the packet passes its own forbidden-language check
    r = gate.act("draft_renewal_packet", "backoffice", "renewal",
                 {"summary": f"{cov['wires_moved']} wires · {len(cov['exceptions'])} exception(s) "
                             f"· drill record incl UNTESTED",
                  "preview": text[:110]})
    return {"packet": text, "coverage": cov, "gate": r}


def draft_realtor_proof():
    """The realtor-facing one-pager: counted verifications and blocks, zero
    client data (scrub-proven), white-label. R1 — a human sends it."""
    cov = core.coverage_year()
    cfg = store.load("config")
    tested = [c for c, d in cov["drills"].items() if d["status"] != "UNTESTED"]
    text = (
        f"{cfg.get('company', 'the agency')} — wire security, evidenced\n\n"
        f"Every buyer's funds move under recorded controls, and the controls leave receipts:\n"
        f"  - {cov['verifications']} wire-change callback verifications this policy period — "
        f"verification is a call to {core.CALLBACK_REF}\n"
        f"  - {cov['blocked_attempts']} fraudulent or unverifiable wire attempts blocked\n"
        f"  - {cov['dual_control_releases']} dual-control releases — two named humans on each\n"
        f"  - controls are drilled, not assumed: {len(tested)} of {len(core.CONTROLS)} drilled "
        f"this period; anything undrilled is listed as UNTESTED in our own file\n\n"
        f"No client names, file numbers, or amounts appear in this document by construction.\n"
        f"Counted from the control ledger — never asserted."
    )
    leaks = core.client_data_leaks(text)
    assert not leaks, f"client data leaked into the one-pager: {leaks}"  # structural
    r = gate.act("draft_realtor_proof", "frontdesk", "realtor_proof",
                 {"summary": f"{cov['verifications']} verifications · {cov['blocked_attempts']} "
                             f"blocks · zero client data", "preview": text[:110]})
    return {"proof": text, "scrub": {"leaks": 0, "checked_against": "every recorded party name, "
                                     "file number, and amount"}, "gate": r}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
