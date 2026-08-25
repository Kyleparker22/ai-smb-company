#!/usr/bin/env python3
"""yourco — the online Revenue Leak Snapshot intake handler (Bella's self-serve front door).

A prospect completes the online Revenue Leak Snapshot (agents/webb/pages/yourco-site-v2/snapshot.html),
which POSTs {name, email, company, phone, vertical, slug, answers, computed} to /api/snapshot.
This module turns that into three things:
  1. a CRM warm lead   — company (source "online snapshot"), contact, prospect-stage deal, + an activity
                          capturing the findings. Owner: Bella. Dedupes against the CRM (once per lead).
  2. a Slack summary    — the findings, ready to post to #yourco-bella + ping the Founder.
  3. an email summary    — the findings, ready to draft to the Founder (founder@yourco.example.com).

STAGED, same gate as the rest of the site: nothing sends until the website is deployed and the
runtime connectors/keys are live. `handle()` writes the CRM only when commit=True; the Slack/email
bodies are returned as text for the (draft-only, approval-gated) connectors to deliver. Decision:
decisions/2026-06-16_online-snapshot.md. CRM conventions mirror runtime/promote.py.

Usage:
  python3 runtime/snapshot_intake.py --self-check          # sample payload, dry run (no writes)
  python3 runtime/snapshot_intake.py --self-check --commit  # write the sample lead into the CRM
"""
import os, sys, json, re, datetime

def _today():
    """Creation date for a new company. `createdAtSource` distinguishes this from the dates
    recovered out of git for the 25 companies that predate the field (2026-08-13) — a recovered
    date and an observed one must never read the same."""
    import datetime as _dt
    return _dt.date.today().isoformat()


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "dashboard"))

OWNER = "Bella"          # Bella owns the online Revenue Leak Snapshot end to end
FOUNDER = "founder@yourco.example.com"
SLACK_CHANNEL = "#yourco-bella"
LEAK_INDEX = os.path.join(REPO, "clients", "webb", "pages", "yourco-site-v2", "leak-index-data.json")


def _record_leak_index(p):
    """Feed the Industry Leak Index (the data moat): append this audit's ANONYMIZED leak to the
    per-vertical aggregate. No name/email/company ever stored here — just slug + the computed leak.
    Only records real, quantified audits (haveNums). Safe no-op if the data file is absent."""
    c = p.get("computed", {}) or {}
    slug = (p.get("slug") or "").strip().lower()
    leak = c.get("monthlyLeak")
    if not (c.get("haveNums") and slug and isinstance(leak, (int, float)) and leak > 0):
        return False
    try:
        data = json.load(open(LEAK_INDEX))
    except Exception:
        return False
    imp = data.setdefault("yourco", {"count": 0, "byVertical": {}})
    bv = imp.setdefault("byVertical", {})
    row = bv.setdefault(slug, {"count": 0, "avgLeak": 0})
    # running mean
    new_count = row["count"] + 1
    row["avgLeak"] = round((row["avgLeak"] * row["count"] + leak) / new_count)
    row["count"] = new_count
    imp["count"] = imp.get("count", 0) + 1
    json.dump(data, open(LEAK_INDEX, "w"), indent=2, ensure_ascii=False)
    return True


def _norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"\b(llc|inc|co|corp|ltd|the|company|services|service|group)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _next_id(prefix, items):
    n = max([int(re.sub(r"\D", "", x.get("id", "")) or 0) for x in items
             if x.get("id", "").startswith(prefix)] + [0])
    return f"{prefix}{n + 1}"


def _money(n):
    try:
        return "$" + format(int(round(float(n))), ",d")
    except Exception:
        return "$0"


def _findings_lines(p):
    """Human-readable findings block shared by Slack + email."""
    c = p.get("computed", {}) or {}
    lines = []
    if c.get("haveNums"):
        lines.append(f"• Estimated leak: {_money(c.get('monthlyLeak', 0))}/mo (~{_money(c.get('annualLeak', 0))}/yr), from their own numbers.")
    else:
        lines.append("• They skipped the hard numbers — leak not quantified (qualitative snapshot shown).")
    if c.get("topPain"):
        lines.append(f"• Self-reported #1 pain: {c['topPain']}.")
    if c.get("hoursYr"):
        lines.append(f"• ~{int(c['hoursYr']):,} owner admin-hours/yr in play.")
    a = p.get("answers", {}) or {}
    raw = {k: v for k, v in a.items() if k not in ("name", "email", "company", "phone")}
    if raw:
        lines.append("• Raw answers: " + ", ".join(f"{k}={v}" for k, v in raw.items()))
    return "\n".join(lines)


def slack_summary(p):
    who = f"{p.get('name','?')} · {p.get('company','?')}"
    contact = " · ".join(x for x in [p.get("email", ""), p.get("phone", "")] if x)
    return (f":mag: *New online Revenue Leak Snapshot — {p.get('vertical','?')}*\n"
            f"*{who}*\n{contact}\n\n{_findings_lines(p)}\n\n"
            f"_In CRM as a warm lead (source: online snapshot), owner {OWNER}. Next: review + book the discovery call._")


def email_summary(p):
    subject = f"[Revenue Leak Snapshot] {p.get('company','?')} — {p.get('vertical','?')}"
    body = (f"New online Revenue Leak Snapshot completed.\n\n"
            f"Name:     {p.get('name','')}\n"
            f"Company:  {p.get('company','')}\n"
            f"Vertical: {p.get('vertical','')}\n"
            f"Email:    {p.get('email','')}\n"
            f"Phone:    {p.get('phone','') or '—'}\n\n"
            f"Findings\n--------\n{_findings_lines(p)}\n\n"
            f"In the CRM as a warm lead (source: online snapshot), owner {OWNER}.\n"
            f"Next step: review the findings and book the discovery call.\n")
    return {"to": FOUNDER, "subject": subject, "body": body}


def handle(p, commit=False):
    """Write the prospect into the CRM as a warm lead (online snapshot). Dedupes by email/company.
    Returns {action, slack, email, crm_written}. commit=False = dry run (no file write)."""
    crm = json.load(open(CRM))
    companies = crm.setdefault("companies", [])
    contacts = crm.setdefault("contacts", [])
    deals = crm.setdefault("deals", [])
    activities = crm.setdefault("activities", [])
    have_email = {(c.get("email") or "").strip().lower() for c in contacts if c.get("email")}
    have_company = {_norm_name(c.get("name", "")) for c in companies}

    email = (p.get("email") or "").strip().lower()
    cname = p.get("company") or p.get("name") or ""
    dup = (email and email in have_email) or (cname and _norm_name(cname) in have_company)
    today = datetime.date.today().isoformat()
    c = p.get("computed", {}) or {}
    leak = f"{_money(c.get('monthlyLeak',0))}/mo" if c.get("haveNums") else "not quantified"
    finding_summary = f"Online Revenue Leak Snapshot ({p.get('vertical','')}). Est. leak {leak}. Top pain: {c.get('topPain') or 'n/a'}."

    out = {"slack": slack_summary(p), "email": email_summary(p), "duplicate": bool(dup), "crm_written": False}

    # Feed the Industry Leak Index (anonymized, every completed audit — independent of CRM dedup).
    if commit:
        out["leak_index_recorded"] = _record_leak_index(p)

    if dup:
        out["action"] = "already in CRM — logging an activity only (no duplicate company)"
        # still log the fresh audit as an activity against the existing company, if we can find it
        if commit:
            match = next((co for co in companies if _norm_name(co.get("name", "")) == _norm_name(cname)), None)
            activities.append({"date": today, "type": "snapshot", "companyId": match["id"] if match else None,
                               "who": p.get("name", ""), "summary": finding_summary,
                               "nextAction": "Review findings + book discovery call"})
            _save(crm)
            out["crm_written"] = True
        return out

    if not commit:
        out["action"] = "would create: company + contact + prospect deal + activity (warm lead, source 'online snapshot')"
        return out

    cid = _next_id("c", companies)
    companies.append({"id": cid, "name": cname or "(unknown)", "vertical": p.get("vertical", ""),
                      "size": "", "location": "", "source": "online snapshot",
                      "channel": "inbound-site", "channelSource": "recorded",
                      "status": "prospect", "owner": OWNER, "domain": "", "example": False,
                      "createdAt": _today(), "createdAtSource": "recorded"})
    contacts.append({"id": _next_id("p", contacts), "name": p.get("name", ""), "companyId": cid,
                     "role": "Owner", "relationship": "completed the online Revenue Leak Snapshot",
                     "email": p.get("email", ""), "phone": p.get("phone", ""),
                     "lastTouch": today, "status": "warm — online snapshot", "example": False,
                     # TCPA opt-in carried from the form (proof of consent: timestamp + exact text)
                     "sms_consent": bool(p.get("sms_consent")), "consent": p.get("consent")})
    deals.append({"id": _next_id("d", deals), "name": f"{cname or p.get('name','')} — online revenue leak snapshot",
                  "companyId": cid, "useCase": (c.get("topPain") or "TBD — qualify on discovery call"),
                  # Retired rung, same bug as the other four intake paths (fixed 2026-08-25).
                  # NOTE: this funnel is PARKED (CLAUDE.md — the per-vertical snapshot is in
                  # _parked/), so its `snapshot` activity type is deliberately left outside
                  # meta.activityTypes rather than having vocabulary invented for idle code.
                  "stage": "pre-convo", "buildFee": None, "retainer": None, "value": 0,
                  "nextAction": "Review findings + book discovery call", "nextDate": "", "lastTouch": today,
                  "owner": OWNER, "stageSince": today, "example": False,
                  "stageHistory": [{"stage": "pre-convo", "at": today, "source": "recorded"}]})
    activities.append({"date": today, "type": "snapshot", "companyId": cid, "who": p.get("name", ""),
                       "summary": finding_summary, "nextAction": "Review findings + book discovery call"})
    _save(crm)
    out["action"] = "created warm lead (company + contact + deal + activity)"
    out["crm_written"] = True
    return out


def _save(crm):
    crm.setdefault("meta", {})["updated"] = datetime.date.today().isoformat()
    json.dump(crm, open(CRM, "w"), indent=1, ensure_ascii=False)
    try:
        import melanie
        melanie.write_mirror(crm)
    except Exception:
        pass


_SAMPLE = {
    "source": "online-snapshot", "vertical": "Hardscaping", "slug": "hardscaping",
    "name": "Sample Owner", "email": "sample.owner@example.com", "company": "Sample Hardscapes (TEST)",
    "phone": "(555) 010-0101",
    "answers": {"leads": "40", "missed": "2", "job_value": "12000", "admin_hours": "15",
                "proposal_speed": "2", "top_pain": "1"},
    "computed": {"monthlyLeak": 26640, "annualLeak": 319680, "hoursYr": 780,
                 "topPain": "Get proposals out faster", "haveNums": True}
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-check" in args:
        commit = "--commit" in args
        res = handle(_SAMPLE, commit=commit)
        print("=== SLACK ===\n" + res["slack"])
        print("\n=== EMAIL ===\nTo: " + res["email"]["to"] + "\nSubject: " + res["email"]["subject"] + "\n\n" + res["email"]["body"])
        print("=== CRM ===\naction: " + res["action"] + f"  (written={res['crm_written']}, duplicate={res['duplicate']})")
        if not commit:
            print("\n(dry run — add --commit to write the sample lead into crm/data.json.)")
    else:
        print(__doc__)
