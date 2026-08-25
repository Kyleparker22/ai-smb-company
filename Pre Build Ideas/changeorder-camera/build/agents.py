#!/usr/bin/env python3
"""Delta OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None

    if c["label"] == "backcharge":
        ev = core.pull_backcharge_evidence(m.get("job_id"))
        body = _backcharge_copy(m, job, ev)
        gate.act("draft_backcharge_response", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110],
                  "photos_pulled": len(ev["observations"])})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_backcharge_response", "draft": body,
                             "evidence": ev, "why": c["why"]})
    elif c["label"] == "verbal_directive":
        note = {"at": m.get("at") or iso(), "from": m.get("from"),
                "verbatim": m.get("text", "")}
        if job:
            job.setdefault("verbal_notes", []).append(note)
            store.upsert("jobs", job)
        gate.act("log_verbal_note", "intake", msg_id,
                 {"verbatim": note["verbatim"], "from": note["from"]})
        r0 = gate.act("treat_verbal_as_signed", "intake", msg_id,
                      {"why": "the go-ahead is recorded and quoted back — nothing signs, "
                              "prices, or invoices from a note"})
        body = _quoteback_copy(m)
        gate.act("draft_verbal_quoteback", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "log_verbal_note", "draft": body,
                             "refused": "a note, not a signed change order — no CO was created "
                                        "by this message",
                             "why": c["why"], "event": r0.get("event")})
    elif c["label"] == "schedule_ask":
        body = _schedule_copy(m, job)
        gate.act("draft_schedule_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_schedule_reply", "draft": body, "why": c["why"]})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _first(m):
    return (m.get("from") or "there").split()[0].rstrip(",.")


def _backcharge_copy(m, job, ev):
    jname = (job or {}).get("name", "the job")
    n = len(ev.get("observations") or [])
    revs = ", ".join(str(r) for r in (ev.get("plan_revs") or [])) or "on file"
    return (f"Hi {_first(m)} — before anyone argues from memory, we've pulled the record for "
            f"{jname}: {n} dated site photos with refs, the plan lines in force (revs {revs}), "
            f"and the delta ledger for the area. This message concedes nothing and argues "
            f"nothing — software doesn't take positions on money. A person reviews the pulled "
            f"record today and calls you with ours; if the record shows a miss on our side, "
            f"you'll hear that from us first.")


def _quoteback_copy(m):
    when = str(m.get("at") or iso())[:10]
    return (f"Hi {_first(m)} — putting this in writing before memory rewrites it. On {when} you "
            f"said: \"{m.get('text', '')}\". That's on the job file now as a note, not a signed "
            f"change order — nothing prices or invoices from a note. If the crew proceeds, "
            f"today's site photos pick the work up as a delta, the change order drafts from the "
            f"recorded rate schedule, and it comes to you for signature the same day.")


def _schedule_copy(m, job):
    jname = (job or {}).get("name", "the job")
    return (f"Hi {_first(m)} — the honest answer comes from the record, not a guess: we're "
            f"pulling the plan-line ledger and this week's dated observations for {jname} now. "
            f"You'll get a date with its arithmetic shown today — and if it slips, you'll hear "
            f"it from us before you notice it.")


# ---------------------------------------------------------------- the human act

def confirm_delta(delta_id, human=None, classification=None):
    """Confirmation is THE human act. Everything downstream (pricing, the CO,
    the notice letter) hangs off `confirmed=True`; there is no other switch."""
    d = store.by_id("deltas", delta_id)
    if not d:
        return {"error": "no such delta"}
    if not human:
        return {"refused": "confirmation is the human act — the classification is a draft "
                           "until a person owns it; a wrong delta invoiced is worse than a "
                           "missed one"}
    if classification and classification not in ("added_scope", "changed_spec", "rework"):
        return {"error": f"unknown classification {classification!r}"}
    d["confirmed"] = True
    d["confirmed_by"] = human
    d["confirmed_at"] = iso()
    d["confirmed_class"] = classification or d.get("classification_draft")
    core.advance_delta(d, "confirmed")
    store.upsert("deltas", d)
    store.log_event("confirm_delta", delta_id, f"human:{human}", "R1",
                    {"classification": d["confirmed_class"],
                     "was_draft": d.get("classification_draft")})
    return {"confirmed": True, "classification": d["confirmed_class"],
            "overrode_draft": d["confirmed_class"] != d.get("classification_draft")}


# ---------------------------------------------------------------- the self-writing paper

def draft_change_order(delta_id):
    d = store.by_id("deltas", delta_id)
    if not d:
        return {"error": "no such delta"}
    math = core.co_math(d)
    if "refused" in math:
        r = gate.act(math["action"], "paper", delta_id, {"why": math["refused"]})
        return {"refused": math["refused"], "event": r.get("event")}
    d["co_amount"] = math["amount"]
    store.upsert("deltas", d)
    job = store.by_id("jobs", d["job_id"]) or {}
    body = _co_copy(d, job, math)
    r = gate.act("draft_change_order", "paper", delta_id,
                 {"summary": f"${math['amount']:,.2f} — {job.get('name')} / {d['location']}",
                  "preview": body[:110], "amount": math["amount"]})
    return {"math": math, "draft": body, "gate": r}


def _co_copy(d, job, math):
    company = store.load("config").get("company", "")
    credit = ""
    if (d.get("confirmed_class") or d.get("classification_draft")) == "changed_spec" and d.get("plan_spec"):
        credit = (f"\nCredit for the plan spec ({d['plan_spec']}) is a stated human line on "
                  f"this CO before it goes out — never silently netted.")
    return (f"CHANGE ORDER (DRAFT) — {job.get('name')} / {d['location']}\n"
            f"To: {job.get('gc')}\n"
            f"Plan of record: {d['plan_says']}\n"
            f"Field condition (photo {d.get('photo_ref')}, dated {str(d.get('discovery_at'))[:10]}): "
            f"{d['field_shows']}\n"
            f"Classification (confirmed by {d.get('confirmed_by')}): {d.get('confirmed_class')}\n"
            f"Price: {math['basis']} — from the recorded rate schedule, not a negotiation number."
            f"{credit}\n"
            f"This draft moves only on a human's send. — {company}")


def draft_notice_letter(delta_id, ref=None):
    d = store.by_id("deltas", delta_id)
    if not d:
        return {"error": "no such delta"}
    job = store.by_id("jobs", d["job_id"]) or {}
    clause = core.clause_for_job(d["job_id"])
    if not clause:
        why = (f"no notice clause recorded for the {job.get('name', 'job')} subcontract — the "
               f"letter cites the clause verbatim or it does not draft. Record the clause "
               f"(days + method) from the subcontract and this letter writes itself.")
        r = gate.act("notice_without_recorded_clause", "paper", delta_id, {"why": why})
        return {"refused": why, "event": r.get("event")}
    if not d.get("confirmed"):
        return {"refused": "the notice asserts a changed condition on the record — confirm the "
                           "delta first so the assertion is a human's, not a classifier's"}
    st = core.notice_status(clause, d.get("discovery_at"), ref=ref)
    body = _notice_copy(d, job, clause, st)
    r = gate.act("draft_notice_letter", "paper", delta_id,
                 {"summary": f"{job.get('name')} / {d['location']} — "
                             + (f"EXPIRED {-st['days_remaining']}d ago" if st["expired"]
                                else f"{st['days_remaining']}d remaining"),
                  "preview": body[:110], "expired": st["expired"]})
    return {"status": st, "draft": body, "gate": r}


def _notice_copy(d, job, clause, st):
    company = store.load("config").get("company", "")
    today = iso(now())[:10]
    lines = []
    if st["expired"]:
        lines.append(f"This letter is late and says so: the recorded notice window expired "
                     f"{-st['days_remaining']} days ago. It is dated today — a backdated notice "
                     f"is a forgery, not a fix — and it is still worth sending: the photo record "
                     f"below is dated the day the condition appeared.")
    lines += [
        f"Dated: {today}",
        f"To: {job.get('gc')} — re {job.get('name')}, {d['location']}",
        f"Your subcontract's recorded notice clause reads: \"{clause['text']}\"",
        f"Method on record: {clause['method']}.",
        f"Discovery (dated photo {d.get('photo_ref')}): {str(d.get('discovery_at'))[:10]}. "
        f"Days allowed: {st['days_allowed']}. "
        + (f"Days remaining: {st['days_remaining']} — {st['label']}." if not st["expired"]
           else "The window has run; the record stands on its dates."),
        f"Condition: plan of record shows {d['plan_says']}; the field shows {d['field_shows']} "
        f"(plan rev {d.get('plan_rev') if d.get('plan_rev') is not None else 'n/a — no plan line at this location'} cited).",
        "A change order follows under the subcontract's changes article. This notice preserves "
        "the record; it argues nothing.",
        f"— {company}",
    ]
    return "\n".join(lines)


def record_co_signature(delta_id, human=None, signed=True):
    """The GC's signature (or rejection) is recorded by a human — never inferred."""
    d = store.by_id("deltas", delta_id)
    if not d:
        return {"error": "no such delta"}
    if not human:
        return {"refused": "recording a signature is a human act — a person confirms what "
                           "came back"}
    if not d.get("co_amount"):
        return {"refused": "no priced CO on this delta yet — nothing to sign"}
    if signed:
        d["signed_at"] = iso()
        d["signed_value"] = d["co_amount"]
        core.advance_delta(d, "signed")
    else:
        core.advance_delta(d, "rejected")
    store.upsert("deltas", d)
    store.log_event("co_signed" if signed else "co_rejected", delta_id,
                    f"human:{human}", "R1", {"value": d.get("co_amount")})
    return {"state": d["state"], "value": d.get("co_amount")}


# ---------------------------------------------------------------- sweeps

def run_diff_all():
    out = {"jobs": 0, "created": 0, "clean_matches": 0}
    for j in store.load("jobs"):
        r = core.diff(j["id"])
        out["jobs"] += 1
        out["created"] += len(r.get("created") or [])
        out["clean_matches"] += r.get("clean_matches", 0)
    return out


def run_all():
    handled = skipped = 0
    for m in store.load("messages"):
        if m.get("handled_at"):
            continue
        if m.get("demo_tag"):
            skipped += 1  # demo fixtures are driven by the demo buttons, never swept
            continue
        handle_message(m["id"])
        handled += 1
    return {"messages": {"handled": handled, "demo_skipped": skipped},
            "diff": run_diff_all()}
