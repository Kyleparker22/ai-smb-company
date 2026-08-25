#!/usr/bin/env python3
"""Rehearsal OS — the agents. Everything routes through `core.gate`.

No agent here gives a coverage opinion, promises a payout, rehearses a policy
it has not read, uses fear language, or hands out a single-number severity —
those four are R0 in the matrix and structural in this file (the shipped copy
asserts its own checks). Stdlib only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def _account_for(name):
    for a in store.load("accounts"):
        if a.get("insured") == name:
            return a
    return None


# ---------------------------------------------------------------- intake triage

def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})
    acct = _account_for(m.get("from"))

    if c["label"] == "active_claim":
        claim = {"id": store.nid("cl"), "message_id": msg_id, "text": m.get("text"),
                 "account_id": acct["id"] if acct else None, "insured": m.get("from"),
                 "filed_at": m.get("at") or iso()}
        store.upsert("claims", claim)
        gate.act("log_claim_intake", "claims_desk", claim["id"],
                 {"verbatim": m.get("text", ""), "from": m.get("from")})
        ev = store.log_event("refused", claim["id"], "agent:claims_desk", "R0",
                             {"action": "promise_coverage",
                              "why": "no coverage opinions mid-crisis — only the carrier "
                                     "adjusts the claim; the script cites the recorded "
                                     "carrier and claim line and nothing more"})
        body = _claim_script(m, acct)
        okf, whyf = core.fear_ok(body)
        assert okf, whyf                      # structural: the shipped copy passes its checks
        oko, whyo = core.opinion_free(body)
        assert oko, whyo
        gate.act("draft_claim_script", "claims_desk", claim["id"],
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "log_claim_intake", "claim": claim["id"],
                             "draft": body,
                             "refused": "no coverage opinion rides in this message — only "
                                        "the carrier adjusts a real claim",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "rehearsal_ask":
        if not acct:
            out["steps"].append({"action": "route_human",
                                 "why": "no account matches this sender — a person links "
                                        "the message before anything rehearses"})
        else:
            r = rehearse_account(acct["id"])
            if r.get("unreadable"):
                out["steps"].append({"action": "refused_unreadable", "refused": r["why"],
                                     "event": r.get("event")})
            else:
                body = _fix_cover_copy(acct, r["rehearsal"])
                okf, whyf = core.fear_ok(body)
                assert okf, whyf
                oko, whyo = core.opinion_free(body)
                assert oko, whyo
                gate.act("draft_fix_sheet", "rehearsal", acct["id"],
                         {"summary": f"{acct['insured']} — rehearsal + fix sheet",
                          "preview": body[:110]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_fix_sheet", "draft": body,
                                     "rehearsal": r["row"],
                                     "why": "the rehearsal's arithmetic does the talking — "
                                            "tone-checked structurally, sent by a human"})
    elif c["label"] == "quote_ask":
        out["steps"].append({"action": "route_producer",
                             "why": "quoting is a licensed act — a producer quotes; the "
                                    "rehearsal can ride along with the quote"})
    elif c["label"] == "policy_question":
        body = _policy_reply_copy(m, acct)
        okf, whyf = core.fear_ok(body)
        assert okf, whyf
        oko, whyo = core.opinion_free(body)
        assert oko, whyo
        gate.act("draft_policy_reply", "policy_desk", msg_id,
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_policy_reply", "draft": body,
                             "why": "the recorded policy answers verbatim, forms cited — "
                                    "no opinion about what the carrier would do"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


# ---------------------------------------------------------------- the copy
#
# THE CLAIMS-REPORTING SCRIPT. Cites the recorded carrier and claim line,
# gives the safe next steps, and says out loud that nothing here is a
# coverage opinion. Verbatim-tested.

def _claim_script(m, acct):
    who = (m.get("from") or "there").split()[0]
    if acct and acct.get("carrier") and acct.get("carrier_claim_line"):
        return (f"{who}, here's exactly what to do right now: if you can reach it safely, "
                f"stop the source (water main, breaker), and call {acct['carrier']}'s 24-hour "
                f"claim line at {acct['carrier_claim_line']} — say you need to report a loss "
                f"in progress. Take photos as it stands and keep receipts for anything you "
                f"buy tonight. We've opened a file on our side and a person from this office "
                f"will call you today. What your policy pays is the carrier's decision at "
                f"adjustment — not something we'd guess at mid-crisis — and we'll walk "
                f"through all of it with you once you're safe and dry.")
    return (f"{who}, here's what to do right now: if you can reach it safely, stop the "
            f"source, then call the 24-hour claim number printed on your policy "
            f"declarations page and report the loss in progress. Take photos as it stands "
            f"and keep receipts. We've opened a file on our side and a person from this "
            f"office will call you today to stay with it — what your policy pays is the "
            f"carrier's decision at adjustment, and we'll walk through it together.")


def _fix_cover_copy(acct, rehearsal):
    who = (acct.get("insured") or "there").split()[0]
    gap = rehearsal.get("gap_typical_total") or 0
    return (f"{who} — before your renewal we rehearsed the three claims most likely to hit "
            f"a policy like yours, against the policy you actually hold: the recorded "
            f"limits, deductibles, and exclusions, each cited by form number. At the "
            f"typical severity, today's policy leaves about ${gap:,.0f} with you across "
            f"those three, and the sheet shows exactly which recorded forms drive each "
            f"dollar, at low, typical, and severe. Each line has the endorsement that "
            f"closes it, priced from the filed rate card. This is arithmetic on your "
            f"recorded policy — not a prediction, and not a coverage decision; only your "
            f"carrier adjusts a real claim. Fifteen minutes before renewal and you'll know "
            f"precisely what you're buying.")


def _policy_reply_copy(m, acct):
    who = (m.get("from") or "there").split()[0]
    if acct and acct.get("policy_recorded"):
        perils = ", ".join(c["peril"] for c in (acct.get("coverages") or [])[:6])
        return (f"{who} — pulling your recorded policy now: the answer comes verbatim from "
                f"the forms on file ({perils}), with the form numbers cited, and a person "
                f"here reads it before it goes out. What the carrier would do with any "
                f"particular claim is the carrier's call — we quote the document, we don't "
                f"guess for it.")
    return (f"{who} — honest answer: your policy detail isn't in our record yet, so we "
            f"won't guess at it. We're pulling the forms from the carrier and a person here "
            f"will come back with the exact language, cited. We read policies before we "
            f"answer for them.")


# ---------------------------------------------------------------- the rehearsal

def rehearse_account(account_id):
    a = store.by_id("accounts", account_id)
    if not a:
        return {"error": "no such account"}
    r = core.rehearse(a)
    if r.get("unreadable"):
        ev = store.log_event("refused", account_id, "agent:rehearsal", "R0",
                             {"action": "rehearse_unread_policy", "why": r["why"]})
        return {"unreadable": True, "why": r["why"], "event": ev["id"]}
    row = {"id": store.nid("rh"), "account_id": account_id, "at": iso(),
           "gap_typical_total": r["gap_typical_total"],
           "gaps": [g for s in r["scenarios"] for g in s["gap_lines"]]}

    def execute():
        store.upsert("rehearsals", row)
        for g in row["gaps"]:
            store.log_event("gap_found", account_id, "agent:rehearsal", "R2",
                            {"key": g["key"], "kind": g["kind"], "cite": g["cite"],
                             "scenario": g["scenario_key"], "gap_typical": g["gap"]})
        return row["id"]

    res = gate.act("run_rehearsal", "rehearsal", account_id,
                   {"summary": f"{a.get('insured')} — typical gap "
                               f"${r['gap_typical_total']:,.0f} across "
                               f"{len(r['scenarios'])} scenario(s)"},
                   execute=execute)
    return {"rehearsal": r, "row": row["id"], "gate": res}


def refuse_single_number(account_id, severity):
    """The API was asked for one number. It doesn't have one to give."""
    ev = store.log_event("refused", account_id, "agent:rehearsal", "R0",
                         {"action": "single_number_severity", "asked_for": severity,
                          "why": core.SINGLE_NUMBER_WHY})
    return {"refused": core.SINGLE_NUMBER_WHY, "event": ev["id"]}


def draft_fix_sheet(account_id):
    a = store.by_id("accounts", account_id)
    if not a:
        return {"error": "no such account"}
    sheet = core.fix_sheet(a)
    if sheet.get("unreadable"):
        ev = store.log_event("refused", account_id, "agent:rehearsal", "R0",
                             {"action": "rehearse_unread_policy", "why": sheet["why"]})
        return {"unreadable": True, "why": sheet["why"], "event": ev["id"]}
    r = core.rehearse(a)
    body = _fix_cover_copy(a, r)
    okf, whyf = core.fear_ok(body)
    assert okf, whyf
    oko, whyo = core.opinion_free(body)
    assert oko, whyo
    res = gate.act("draft_fix_sheet", "rehearsal", account_id,
                   {"summary": f"{a.get('insured')} — {len(sheet['lines'])} fix line(s), "
                               f"{sheet['unpriced']} unpriced",
                    "preview": body[:110]})
    return {"sheet": sheet, "cover": body, "gate": res}


def draft_renewal_packet(account_id):
    """The renewal packet = the rehearsal + the fix sheet, drafted R1."""
    a = store.by_id("accounts", account_id)
    if not a:
        return {"error": "no such account"}
    r = core.rehearse(a)
    if r.get("unreadable"):
        ev = store.log_event("refused", account_id, "agent:rehearsal", "R0",
                             {"action": "rehearse_unread_policy", "why": r["why"]})
        return {"unreadable": True, "why": r["why"], "event": ev["id"]}
    sheet = core.fix_sheet(a)
    body = _fix_cover_copy(a, r)
    okf, whyf = core.fear_ok(body)
    assert okf, whyf
    oko, whyo = core.opinion_free(body)
    assert oko, whyo
    res = gate.act("draft_renewal_packet", "renewal_desk", account_id,
                   {"summary": f"{a.get('insured')} — renewal packet, typical gap "
                               f"${r['gap_typical_total']:,.0f}",
                    "preview": body[:110]})
    return {"packet": {"rehearsal": r, "fix_sheet": sheet, "cover": body,
                       "label": core.REHEARSAL_LABEL},
            "gate": res}


# ---------------------------------------------------------------- closing a gap

def record_endorsement(account_id, kind, key):
    """R1: a human records the endorsement; only then is the gap closed."""
    a = store.by_id("accounts", account_id)
    if not a:
        return {"error": "no such account"}
    return gate.act("record_endorsement", "renewal_desk", account_id,
                    {"summary": f"record endorsement {key} ({kind}) on "
                                f"{a.get('insured')}", "kind": kind, "key": key})


def apply_endorsement(account_id, kind, key, human):
    """The execute half — runs only on a human's approval click."""
    a = store.by_id("accounts", account_id)
    if not a:
        return {"error": "no such account"}
    a.setdefault("endorsements", []).append({"kind": kind, "key": key, "at": iso(),
                                             "by": human})
    store.upsert("accounts", a)
    store.log_event("gap_closed", account_id, f"human:{human}", "R1",
                    {"kind": kind, "key": key})
    return {"recorded": True, "account": account_id, "key": key}


# ---------------------------------------------------------------- probes (demo)

def check_client_draft(text, subject="probe"):
    """Every client draft passes here or is refused — the tone check and the
    opinion check, both structural, both logged when they fire."""
    okf, whyf = core.fear_ok(text)
    if not okf:
        ev = store.log_event("refused", subject, "agent:copy_desk", "R0",
                             {"action": "fear_language", "why": whyf})
        return {"refused": whyf, "event": ev["id"]}
    oko, whyo = core.opinion_free(text)
    if not oko:
        ev = store.log_event("refused", subject, "agent:copy_desk", "R0",
                             {"action": "promise_coverage", "why": whyo})
        return {"refused": whyo, "event": ev["id"]}
    return {"ok": True, "note": "passes the tone check and the opinion check"}


# ---------------------------------------------------------------- sweeps

def renewal_sweep(limit=40):
    """T-60: rehearse every in-window account that hasn't been, skipping demo
    fixtures; UNREADABLE accounts get their refusal on the record instead."""
    out = {"rehearsed": 0, "unreadable": 0, "skipped": 0}
    for row in core.renewal_radar()["rows"]:
        if row.get("demo_tag") or row["status"] == "rehearsed":
            out["skipped"] += 1
            continue
        if out["rehearsed"] >= limit:
            continue          # keep counting skips; rehearse the rest next sweep
        r = rehearse_account(row["account"])
        if r.get("unreadable"):
            out["unreadable"] += 1
        else:
            out["rehearsed"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "renewals": renewal_sweep()}
