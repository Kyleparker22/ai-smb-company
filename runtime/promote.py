#!/usr/bin/env python3
"""yourco — the promotion gate: Instantly warm replies → the native CRM (Reilly).
Implements decisions/2026-06-15_prospect-data-architecture.md.

Cold prospects live in Instantly. The moment one replies with positive intent, it graduates into the
CRM as a real lead: a company (status "warm — replied"), a contact (with email, status "replied"), and
a `pre-convo`-stage deal owned by Reilly (the ladder's first rung since the 2026-08-07
restructure; this file still said `prospect` until 2026-08-25). This is the ONLY path by which
sourced cold leads enter the CRM.

Dry-run by default; --commit writes crm/data.json (and mirrors via melanie). Reads only — never sends,
never touches Instantly state. De-dupes against the CRM so a lead is promoted once.

Usage:
  python3 runtime/promote.py                          # dry run: show who would graduate (all campaigns)
  python3 runtime/promote.py --campaign "Landscaping ST"   # scope to one campaign
  python3 runtime/promote.py --vertical "Landscaping" --commit   # write them in, tag the vertical
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


def _norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"\b(llc|inc|co|corp|ltd|the|company|services|service|group)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _next_id(prefix, items):
    n = max([int(re.sub(r"\D", "", x.get("id", "")) or 0) for x in items
             if x.get("id", "").startswith(prefix)] + [0])
    return f"{prefix}{n + 1}"


def promote(warm, vertical="", dry_run=True):
    """warm = [{name, email, company, phone, status, ...}] from instantly.warm_replies().
    Promotes each into the CRM as a real lead. Skips any already present (by email or company name)."""
    crm = json.load(open(CRM))
    companies = crm.setdefault("companies", [])
    contacts = crm.setdefault("contacts", [])
    deals = crm.setdefault("deals", [])
    have_email = {(c.get("email") or "").strip().lower() for c in contacts if c.get("email")}
    have_company = {_norm_name(c.get("name", "")) for c in companies}

    today = datetime.date.today().isoformat()
    promoted, skipped = [], []
    for w in warm:
        email = (w.get("email") or "").strip().lower()
        cname = w.get("company") or w.get("name") or ""
        if (email and email in have_email) or (cname and _norm_name(cname) in have_company):
            skipped.append(cname or email)
            continue
        promoted.append(cname or w.get("name") or email)
        if dry_run:
            continue
        cid = _next_id("c", companies)
        companies.append({"id": cid, "name": cname or "(unknown company)", "vertical": vertical,
                          "size": "", "location": "", "source": "instantly (replied)",
                          # `channel` is the controlled answer to "which channel produced this
                          # company"; `source` keeps the human detail. crm/data.json
                          # meta.sourceChannels. Stamped at intake = channelSource "recorded".
                          "channel": "outbound", "channelSource": "recorded",
                          "status": "warm — replied", "owner": "Reilly", "domain": "",
                          "createdAt": _today(), "createdAtSource": "recorded"})
        if email:
            contacts.append({"id": _next_id("p", contacts), "name": w.get("name", ""), "companyId": cid,
                             "role": "", "email": w.get("email", ""), "phone": w.get("phone", ""),
                             "lastTouch": today, "status": "replied"})
        # THREE bugs fixed here 2026-08-25, all of which would have fired on the first real
        # campaign and none of which anything would have caught:
        #  1. stage was "prospect" — a rung that no longer exists (the ladder starts at pre-convo
        #     since the 2026-08-07 restructure), so every promoted lead would land off the board.
        #  2. the sequence status was written as a nested {"seq": {"status": ...}} that nothing
        #     reads; the schema field is a flat `seqStatus`, so the reply would have been invisible
        #     to the CRM UI and to Michelle's number.
        #  3. no stageHistory, so a deal promoted by outbound would carry no clock and the
        #     discovery→live duration would be lost for exactly the deals outbound produced.
        # promote.py only ever runs on leads _is_warm() has classified as interested, so
        # `replied-positive` is a statement of what happened, not an optimistic default.
        deals.append({"id": _next_id("d", deals), "name": f"{cname or w.get('name','')} — replied",
                      "companyId": cid, "useCase": "TBD — qualify on discovery call",
                      "stage": "pre-convo",
                      "buildFee": None, "retainer": None, "value": 0,
                      "nextAction": "Book a discovery call", "nextDate": "", "lastTouch": today,
                      "owner": "Reilly", "stageSince": today,
                      "stageHistory": [{"stage": "pre-convo", "at": today, "source": "recorded"}],
                      "seqStatus": "replied-positive"})
        if email:
            have_email.add(email)
        have_company.add(_norm_name(cname))

    if not dry_run and promoted:
        json.dump(crm, open(CRM, "w"), indent=2, ensure_ascii=False)
        try:
            import melanie
            melanie.write_mirror(crm)
        except Exception:
            pass
    return {"promoted": promoted, "skipped": skipped}


if __name__ == "__main__":
    a = sys.argv[1:]
    commit = "--commit" in a
    vertical = a[a.index("--vertical") + 1] if "--vertical" in a else ""
    campaign = a[a.index("--campaign") + 1] if "--campaign" in a else None
    try:
        import instantly
        warm = instantly.warm_replies(campaign=campaign)
    except Exception as e:
        print(f"Could not read Instantly warm replies: {e}")
        print("(Needs INSTANTLY_API_KEY in runtime/.instantly.env + a plan exposing the leads surface.)")
        sys.exit(1)
    print(f"Instantly warm replies found: {len(warm)}"
          f"{f' (campaign: {campaign})' if campaign else ' (all campaigns)'}")
    res = promote(warm, vertical=vertical, dry_run=not commit)
    print(f"{'COMMITTED to CRM' if commit else 'DRY RUN'}: "
          f"{len(res['promoted'])} promoted, {len(res['skipped'])} already in CRM (skipped).")
    for n in res["promoted"]:
        print(f"  ↑ {n}")
    if not commit:
        print("\n(dry run — re-run with --commit to write the CRM. Reads Instantly only; never sends.)")
