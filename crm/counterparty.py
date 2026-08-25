#!/usr/bin/env python3
"""The counterparty record — the buyer's copy, and their right to dispute a row.

Every CRM on earth is single-player. It holds *our* account of a relationship, invisible to
the other party, who is meanwhile keeping their own account that contradicts it. Nobody ever
reconciles them, and the divergence is discovered at the worst possible moment — usually in
a renewal conversation, as "that's not what you told us."

Shared deal rooms and mutual action plans already exist (Dock, Aligned, Recapped), so a
buyer-visible plan is NOT the new part. **The new part is the adversarial half: the buyer can
formally DISPUTE a row, and the dispute becomes a tracked defect in our own record.**

Nobody ships that, and the reason is structural rather than imaginative: in a normal CRM the
data cannot survive being shown. 79% of opportunity data never gets entered and 37% of reps
admit fabricating fields to pass validation — hand that to a buyer and every dispute lands.
yourco's record is agent-maintained, stamped with who verified it and when, and its insight
layer refuses to state what it cannot defend. **The moat is what makes the feature survivable**,
which is the strongest kind of product idea: one a competitor cannot copy without first
rebuilding the discipline underneath it.

WHAT GOES IN THE BUYER'S COPY — only rows we would be willing to defend to their face:
  · promises we made (crm/promises.py), with dates and status
  · what we recorded THEM as saying — the mirror steps marked cleared, and by whom
  · outcomes measured since go-live (clients/<slug>/outcomes.jsonl)
  · the next action we owe them
Deliberately excluded: win probability, adversarial reads, ghost positions, warm-path value,
internal notes. Those are our judgements about them, not the shared record of what happened,
and showing them would be a category error dressed as transparency.

SENDING: this module NEVER sends. It renders a file. the Founder sends (CLAUDE.md — "the Founder sends;
agents draft"), and nothing here is shared until he does.

Run:
    python3 crm/counterparty.py --deal <id>          # the buyer-facing record, as text
    python3 crm/counterparty.py --deal <id> --write  # render to crm/counterparty/<slug>.html
    python3 crm/counterparty.py --disputes           # every open dispute, as OUR defect list
    python3 crm/counterparty.py --json
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
OUTDIR = os.path.join(DATA_DIR, "counterparty")
TODAY = datetime.date.today()

# A dispute's life. `corrected` is the important one: the buyer was right and we changed the
# record. That is the outcome the whole mechanism exists to produce, and it is counted.
STATUSES = ("open", "corrected", "rejected", "withdrawn")


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")


def holders(data):
    for d in data.get("deals", []) or []:
        yield d
    for c in data.get("closed", []) or []:
        yield c


def record_for(data, deal_id):
    """The buyer's copy of one deal — only rows we would defend to their face."""
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    h = next((x for x in holders(data) if x.get("id") == deal_id), None)
    if not h:
        return None
    co = cos.get(h.get("companyId"), {})
    steps = (data.get("meta", {}) or {}).get("mirrorSteps") or []
    labels = {s["key"]: s.get("label", s["key"]) for s in steps}

    promises = []
    for p in h.get("promises") or []:
        due = _d(p.get("due"))
        st = p.get("status") or "open"
        promises.append({
            "id": p.get("id"), "text": p.get("text"), "due": p.get("due"),
            "status": st, "deliveredOn": p.get("deliveredOn"),
            "overdue": bool(due and due < TODAY and st == "open"),
        })

    # What we recorded THEM as saying. Only `yes` steps — an unknown step is our gap, and
    # showing a buyer a list of things we failed to find out is noise to them.
    theirs = []
    st_map = (h.get("mirror") or {}).get("steps") or {}
    for k, v in st_map.items():
        status = v.get("status") if isinstance(v, dict) else v
        if str(status) != "yes":
            continue
        theirs.append({"key": k, "label": labels.get(k, k),
                       "note": (v.get("note") if isinstance(v, dict) else "") or "",
                       "recordedOn": (v.get("at") if isinstance(v, dict) else None)})

    outcomes = []
    cd = os.path.join(REPO, "clients", _slug(co.get("name")))
    oj = os.path.join(cd, "outcomes.jsonl")
    if os.path.isfile(oj):
        for line in open(oj, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("{\"_"):
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if str(o.get("note", "")).startswith("EXAMPLE"):
                continue
            outcomes.append(o)

    disputes = h.get("disputes") or []
    return {
        "dealId": h.get("id"), "company": co.get("name") or h.get("name"),
        "generated": TODAY.isoformat(),
        "nextAction": h.get("nextAction"), "nextDate": h.get("nextDate"),
        "promises": promises, "theirLadder": theirs, "outcomes": outcomes,
        "disputes": disputes,
        "openPromises": sum(1 for p in promises if p["status"] == "open"),
        "overduePromises": sum(1 for p in promises if p["overdue"]),
    }


def disputes(data=None):
    """Every dispute across the CRM, read as OUR data-quality defect list.

    A dispute is not a complaint to be managed — it is evidence that our record and reality
    disagreed, which is precisely the failure the insight layer exists to prevent. The
    correction rate is the number that matters: a high one means the mechanism works; a zero
    one on a live book means nobody is actually being shown their record."""
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    rows = []
    for h in holders(data):
        for x in h.get("disputes") or []:
            rows.append({
                "id": x.get("id"), "dealId": h.get("id"),
                "company": cos.get(h.get("companyId"), {}).get("name") or h.get("name"),
                "rowKind": x.get("rowKind"), "rowRef": x.get("rowRef"),
                "ourClaim": x.get("ourClaim"), "theirClaim": x.get("theirClaim"),
                "raisedOn": x.get("raisedOn"), "raisedBy": x.get("raisedBy"),
                "status": x.get("status") or "open", "resolution": x.get("resolution") or "",
                "ageDays": (TODAY - _d(x.get("raisedOn"))).days if _d(x.get("raisedOn")) else None,
            })
    rows.sort(key=lambda r: (r["status"] != "open", -(r["ageDays"] or 0)))
    resolved = [r for r in rows if r["status"] in ("corrected", "rejected")]
    corrected = [r for r in rows if r["status"] == "corrected"]
    shared = [h.get("id") for h in holders(data) if h.get("counterpartySharedOn")]
    return {
        "generated": TODAY.isoformat(), "rows": rows, "statuses": STATUSES,
        "open": sum(1 for r in rows if r["status"] == "open"),
        "corrected": len(corrected), "resolved": len(resolved),
        "sharedRecords": len(shared),
        "correctionRate": (round(len(corrected) / len(resolved) * 100) if resolved else None),
        "reading": (
            f"{len(rows)} dispute(s) raised, {len(corrected)} of which corrected our record."
            if rows else
            (f"No disputes — and {len(shared)} record(s) have ever been shared, so that is a "
             f"measure of nothing yet." if not shared else
             f"{len(shared)} record(s) shared, no disputes raised. Either the record is accurate "
             f"or nobody read it; do not report this as accuracy until a dispute has been possible.")),
        "honesty": ("A dispute is a defect in OUR record, not a complaint to manage. The number "
                    "worth watching is the correction rate: disputes we accepted and fixed. A book "
                    "with shared records and zero disputes is unproven, not clean."),
    }


def render_html(rec):
    """The buyer's copy. yourco-branded on purpose: this is the shared record BETWEEN two
    parties, so the white-label rule (client brand only) does not apply — it applies to
    surfaces we build FOR a client's own customers."""
    P = rec["promises"]
    rows = "".join(
        f'<tr><td>{p["text"] or ""}</td><td>{p["due"] or "—"}</td>'
        f'<td class="{ "od" if p["overdue"] else p["status"] }">'
        f'{"overdue" if p["overdue"] else p["status"]}</td>'
        f'<td><button data-dispute="promise:{p["id"]}">Dispute this row</button></td></tr>'
        for p in P) or '<tr><td colspan="4" class="mut">Nothing recorded yet.</td></tr>'
    ladder = "".join(
        f'<li>{t["label"]}{" — " + t["note"] if t["note"] else ""}'
        f' <button data-dispute="ladder:{t["key"]}">Not accurate</button></li>'
        for t in rec["theirLadder"]) or '<li class="mut">Nothing recorded yet.</li>'
    outs = "".join(
        f'<tr><td>{o.get("metric","")}</td><td>{o.get("baseline","")} → {o.get("value","")}'
        f'{o.get("unit","")}</td><td>{o.get("date","")}</td>'
        f'<td><button data-dispute="outcome:{o.get("metric","")}">Dispute</button></td></tr>'
        for o in rec["outcomes"]) or '<tr><td colspan="4" class="mut">No outcomes measured yet.</td></tr>'
    return f"""<h1>{rec['company']} &amp; yourco — the shared record</h1>
<p class="sub">Everything below is what <b>yourco's own system</b> says about this engagement, as of
{rec['generated']}. It is the same record we work from — not a summary written for you.
<b>If any row is wrong, dispute it.</b> A disputed row is logged as a defect in our record and
someone answers it; it does not disappear quietly.</p>

<h2>What we promised you</h2>
<table><tr><th>Promise</th><th>By</th><th>Status</th><th></th></tr>{rows}</table>

<h2>What we recorded you as saying</h2>
<p class="sub">If we wrote down something you did not say, that is exactly the kind of error
worth catching — it is what our next step is built on.</p>
<ul>{ladder}</ul>

<h2>What has actually changed</h2>
<table><tr><th>Measure</th><th>Before → now</th><th>As of</th><th></th></tr>{outs}</table>

<h2>What we owe you next</h2>
<p>{rec['nextAction'] or '—'}{' · by ' + rec['nextDate'] if rec.get('nextDate') else ''}</p>

<p class="foot">Not shown here, deliberately: our internal judgements about this deal — win
odds, risk reads, forecast position. Those are our opinions about you rather than the shared
record of what happened, and publishing them would be a category error dressed as transparency.</p>
"""


def main():
    with open(DATA) as f:
        data = json.load(f)
    if "--disputes" in sys.argv:
        r = disputes(data)
        if "--json" in sys.argv:
            print(json.dumps(r, indent=2)); return
        print(f"Disputes — our record vs theirs\n\n  {r['reading']}\n")
        for x in r["rows"]:
            print(f"  [{x['status']}] {x['company']} · {x['rowKind']} — ours: {x['ourClaim']}")
            print(f"        theirs: {x['theirClaim']}")
        print(f"\n  {r['honesty']}")
        return
    if "--deal" in sys.argv:
        did = sys.argv[sys.argv.index("--deal") + 1]
        rec = record_for(data, did)
        if not rec:
            print(f"No deal '{did}'."); return
        if "--json" in sys.argv:
            print(json.dumps(rec, indent=2)); return
        if "--write" in sys.argv:
            os.makedirs(OUTDIR, exist_ok=True)
            p = os.path.join(OUTDIR, _slug(rec["company"]) + ".html")
            with open(p, "w", encoding="utf-8") as f:
                f.write(render_html(rec))
            print(f"Wrote {p}\n\nNOT SENT. the Founder sends; agents draft (CLAUDE.md).")
            return
        print(f"{rec['company']} — the shared record ({rec['generated']})\n")
        print(f"  Promises: {len(rec['promises'])} ({rec['openPromises']} open, "
              f"{rec['overduePromises']} overdue)")
        print(f"  Their ladder, as we recorded it: {len(rec['theirLadder'])} step(s) cleared")
        print(f"  Outcomes measured: {len(rec['outcomes'])}")
        print(f"  Disputes raised: {len(rec['disputes'])}")
        print(f"\n  Next we owe them: {rec['nextAction'] or '—'}")
        return
    r = disputes(data)
    print("Counterparty record — the buyer's copy, and their right to dispute it\n")
    print(f"  {r['reading']}")
    print(f"\n  Use --deal <id> for one record, --disputes for the defect list.")


if __name__ == "__main__":
    main()
