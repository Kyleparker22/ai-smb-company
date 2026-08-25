#!/usr/bin/env python3
"""Close OS — the agents: the chaser, the intake classifier, the scope ledger.

No agent here takes a tax position. A client question that touches treatment,
deductibility, entity choice or a filing position is routed to a CPA unanswered
— there is no code path that composes an answer to one.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · the chaser

def chaser(ref=None):
    ref = ref or now()
    items = store.load("open_items")
    by_eng = {}
    for i in items:
        by_eng.setdefault(i["engagement_id"], []).append(i)
    engs = store.index("engagements")
    clients = store.index("clients")

    sent, held, escalated = 0, [], 0
    per_client = {}
    for eng_id, mine in by_eng.items():
        eng = engs.get(eng_id)
        if not eng or eng.get("state") == "complete":
            continue
        client = clients.get(eng["client_id"], {})
        for item in mine:
            due, why = core.due_chase(item, mine, ref)
            if why:
                held.append({"item": item["id"], "type": item["type"],
                             "client": client.get("name"), "why": why})
                continue
            # ONE ladder step per item per run. Firing every overdue step at once
            # would send a client five messages in a minute the first time this
            # is pointed at a neglected backlog — which is how a chaser becomes
            # the thing everybody mutes.
            for t in due[-1:]:
                bundle = per_client.setdefault((client.get("id"), eng_id),
                                               {"client": client, "eng": eng, "items": [], "step": t})
                bundle["items"].append(item)
                bundle["step"] = t if t["day"] > bundle["step"]["day"] else bundle["step"]
                item.setdefault("touches", []).append({"day": t["day"], "at": iso(ref),
                                                       "channel": t["channel"], "kind": t["kind"]})
                store.upsert("open_items", item)
                sent += 1

    drafts = []
    for (cid, eng_id), b in per_client.items():
        t = b["step"]
        body = _chase_copy(b["client"], b["eng"], b["items"], t)
        action = "chase_escalate" if t["kind"] == "escalate" else (
            "request_items" if t["kind"] == "request" else "chase_nudge")
        res = gate.act(action, "chaser", eng_id,
                       {"summary": f"{b['client'].get('name')} · {len(b['items'])} outstanding · "
                                   f"{t['kind']}", "preview": body[:130],
                        "channel": t["channel"]})
        if action == "chase_escalate":
            escalated += 1
        drafts.append({"client": b["client"].get("name"), "engagement": eng_id,
                       "step": t["kind"], "channel": t["channel"], "items": len(b["items"]),
                       "body": body, "approval": res.get("approval"),
                       "executed": res.get("executed")})
    return {"touches": sent, "bundles": len(drafts), "escalated": escalated,
            "held": held[:15], "drafts": drafts[:12],
            "note": "one message per client per engagement listing only what is STILL outstanding — "
                    "never a re-sent generic list, and never a chase for something already received"}


def chase_state(ref=None):
    """READS the chase. Distinct from `chaser()`, which is the sweep — a screen
    that silently re-runs a sweep shows an empty list the second time anyone
    opens it (this was a real bug in the agency build)."""
    ref = ref or now()
    engs = store.index("engagements")
    clients = store.index("clients")
    by_eng = {}
    for i in store.load("open_items"):
        by_eng.setdefault(i["engagement_id"], []).append(i)

    rows, held = [], []
    for eng_id, mine in by_eng.items():
        eng = engs.get(eng_id)
        if not eng or eng.get("state") == "complete":
            continue
        client = clients.get(eng["client_id"], {})
        outstanding = [i for i in mine if i.get("state") != "received"]
        touched = [i for i in outstanding if i.get("touches")]
        if not touched:
            continue
        last = max((t for i in touched for t in i["touches"]), key=lambda t: t["day"])
        step = next((l for l in core.LADDER if l["day"] == last["day"]), core.LADDER[0])
        rows.append({"client": client.get("name"), "engagement": eng_id,
                     "step": step["kind"], "channel": step["channel"],
                     "items": len(outstanding),
                     "body": _chase_copy(client, eng, outstanding, step),
                     "executed": step["kind"] != "escalate"})
        for i in mine:
            due, why = core.due_chase(i, mine, ref)
            if why and "already received" not in why:
                held.append({"item": i["id"], "type": i["type"],
                             "client": client.get("name"), "why": why})
    rows.sort(key=lambda r: (0 if r["step"] == "escalate" else 1, -r["items"]))
    return {"drafts": rows[:40], "bundles": len(rows),
            "escalated": sum(1 for r in rows if r["step"] == "escalate"),
            "touches": sum(r["items"] for r in rows),
            "held": held[:15],
            "note": "one message per client per engagement listing only what is STILL outstanding — "
                    "never a re-sent generic list, and never a chase for something already received"}


def _chase_copy(client, eng, items, step):
    name = (client.get("contact") or client.get("name") or "there").split()[0]
    label = core.ENGAGEMENT_TYPES[eng["type"]]["label"].lower()
    # dedupe: three receipts requests read as one line to a human, and a list that
    # repeats itself is the first thing a client stops reading
    seen, labels = set(), []
    for i in items:
        lbl = core.ITEM_TYPES.get(i["type"], {}).get("label", i["type"])
        if lbl not in seen:
            seen.add(lbl)
            labels.append(lbl)
    lst = "; ".join(labels[:6]) + (f" (+{len(labels)-6} more)" if len(labels) > 6 else "")
    if step["kind"] == "request":
        return (f"Hi {name} — starting your {label}. Here's what we need from you: {lst}. "
                f"Everything else is on us.")
    if step["kind"] == "nudge":
        return (f"Hi {name} — down to {len(items)} item(s) on the {label}: {lst}. "
                f"Ignore anything you've already sent; this list is only what's still open.")
    if step["kind"] == "short":
        return f"Hi {name} — still need: {lst}. Link's in the portal."
    if step["kind"] == "deadline":
        d = eng.get("due", "")[:10]
        return (f"Hi {name} — the {label} is due {d}. Without {lst} we can't finish it in time, "
                f"and the fallback is an extension rather than a rushed return.")
    return (f"[PARTNER TASK — {eng.get('owner','unassigned')}] {client.get('name')}: {len(items)} "
            f"item(s) outstanding on the {label} since {items[0].get('requested_at','')[:10]}. "
            f"Four touches sent. The ladder ends here — this one is a phone call.")


# ---------------------------------------------------------------- 2 · intake classifier

def intake(ref=None):
    ref = ref or now()
    engs = store.index("engagements")
    items = store.load("documents")
    by_eng = {}
    for i in store.load("open_items"):
        by_eng.setdefault(i["engagement_id"], []).append(i)

    filed, flagged, queued = [], [], []
    for doc in items:
        if doc.get("processed_at"):
            continue
        eng = engs.get(doc.get("engagement_id"))
        if not eng:
            continue
        m = core.match_document(doc, by_eng.get(eng["id"], []), eng, ref)
        doc["processed_at"] = iso(ref)
        doc["read"] = m["read"]
        doc["outcome"] = m["action"]
        doc["outcome_why"] = m["why"]

        if m["action"] == "file":
            def _file(doc=doc, m=m):
                item = store.by_id("open_items", m["matched"])
                if item:
                    item["state"] = "received"
                    item["received_at"] = iso(ref)
                    item["document_id"] = doc["id"]
                    store.upsert("open_items", item)
                doc["filed_to"] = m["matched"]
                doc["renamed"] = _house_name(doc, eng, m["read"])
                store.upsert("documents", doc)
                return doc["id"]
            gate.act("file_document", "intake", doc["id"],
                     {"summary": f"{doc['filename']} → {m['matched']}", "why": m["why"]},
                     execute=_file)
            filed.append({"doc": doc["id"], "filename": doc["filename"],
                          "renamed": doc.get("renamed"), "why": m["why"]})
        elif m["action"] == "flag":
            gate.act("flag_mismatch", "intake", doc["id"],
                     {"summary": f"{doc['filename']} — {m['why']}"})
            flagged.append({"doc": doc["id"], "filename": doc["filename"], "why": m["why"]})
        else:
            queued.append({"doc": doc["id"], "filename": doc["filename"], "why": m["why"],
                           "confidence": m["read"]["confidence"]})
        store.upsert("documents", doc)
    return {"filed": filed[:15], "flagged": flagged[:15], "human_queue": queued[:15],
            "counts": {"filed": len(filed), "flag": len(flagged), "human_queue": len(queued)},
            "note": "a mismatch is flagged with its reason and never filed. Nothing is ever "
                    "deleted — a correction is a new event and both states stay in the log"}


def _house_name(doc, eng, read):
    parts = [eng.get("entity", "entity").replace(" ", "_"),
             str(read.get("year") or "unknown-year"),
             f"{read['month']:02d}" if read.get("month") else None,
             read.get("type") or "unknown-type"]
    return "_".join(p for p in parts if p) + ".pdf"


# ---------------------------------------------------------------- 3 · the tax-question stop

TAX_QUESTION = [
    r"can i (deduct|write off|expense)", r"is (it|this) deductible", r"should i (elect|convert|take)",
    r"s-?corp|c-?corp election", r"how (do|should) i (treat|handle|report)",
    r"(what|how much) (do|will) i owe", r"depreciat|section 179|bonus depreciation",
    r"basis|qbi|199a", r"is this taxable", r"do i (have to|need to) (file|report)",
    r"penalt|audit risk", r"1031|like ?kind",
]
_TQ = [re.compile(p, re.I) for p in TAX_QUESTION]


def client_message(engagement_id, text, ref=None):
    """One inbound client message. Two things can happen and neither is an answer
    to a tax question."""
    ref = ref or now()
    eng = store.by_id("engagements", engagement_id)
    if not eng:
        return {"error": "no such engagement"}
    out = {"engagement": engagement_id, "steps": []}

    hit = next((rx.search(text) for rx in _TQ if rx.search(text)), None)
    if hit:
        gate.act("answer_tax_question", "intake", engagement_id,
                 {"summary": "tax question — routed unanswered", "matched": hit.group(0)})
        out["steps"].append({
            "action": "route_to_cpa", "matched": hit.group(0),
            "said": "That's a question for your CPA rather than me — I've put it in front of "
                    f"{eng.get('owner','them')} with the thread attached, and they'll answer it directly.",
            "refused": "no tax position, no deductibility opinion, no entity-choice advice, "
                       "no filing recommendation"})

    letter = (store.by_id("clients", eng["client_id"]) or {}).get("engagement_letter", {})
    for d in core.detect_scope(text, letter):
        res = core.log_scope_event(eng, d, evidence=text)
        if res.get("logged"):
            gate.act("log_scope_event", "scope", res["id"],
                     {"summary": f"{d['label']} — outside “{(d['citation'] or '')[:60]}”",
                      "citation": d["citation"]})
            out["steps"].append({"action": "log_scope_event", "label": d["label"],
                                 "citation": d["citation"], "why": "the letter does not cover this"})
        else:
            out["steps"].append({"action": "no_scope_event", "label": d["label"],
                                 "why": res["why"]})
    if not out["steps"]:
        out["steps"].append({"action": "routine", "said": "Thanks — logged against the engagement."})
    return out


def run_all():
    return {"chase": {k: v for k, v in chaser().items() if k in ("touches", "bundles", "escalated")},
            "intake": intake()["counts"]}
