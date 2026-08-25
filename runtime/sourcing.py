#!/usr/bin/env python3
"""yourco — multi-source sourcing pipeline (Reilly). Implements decisions/2026-06-07_multi-source-sourcing.md
+ decisions/2026-06-15_prospect-data-architecture.md.

Pull prospects from the approved sources, normalize to one schema, dedupe hierarchically (domain →
phone → name), and **stage the deduped batch into an Instantly campaign** — the cold/outbound system
of record. Cold leads do NOT go into the native CRM; they graduate there only when they reply
(runtime/promote.py). A prospect that appears in all sources is high-confidence; one only in
Outscraper is a weak-footprint local SMB — a positive ICP signal for trades. Dry-run by default;
--commit stages into Instantly (staging only — never sends). Sourcing only, never outreach.

Sources:
  • Outscraper — pulled directly (HTTP) by this script.
  • Instantly SuperSearch — pulled directly if available (runtime/instantly.py).
  • Vibe — an MCP, so it's fed in: an agent (Reilly) runs the Vibe tool, saves normalized results
    to a JSON file, and passes --vibe-json <path>. (Common schema: list of {name,domain,phone,address,...}.)

Instantly is email-first: records without an email (raw Outscraper = phone+address, no site) can't be
sequenced and are reported separately as "needs enrichment first" — this never invents an email.

Usage:
  python3 runtime/sourcing.py --outscraper "landscaping, Yourtown" --limit 10 --campaign "Landscaping ST"
  python3 runtime/sourcing.py --outscraper "..." --vibe-json vibe.json --campaign "Landscaping ST" --commit
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "dashboard"))


def _norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"\b(llc|inc|co|corp|ltd|the|company|services|service|group)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _norm_phone(s):
    return re.sub(r"\D", "", s or "")[-10:]  # last 10 digits


def dedupe(records):
    """Merge records that match on domain → phone → normalized name. Unions source[]."""
    merged = []
    for r in records:
        r = dict(r); r.setdefault("source", [])
        hit = None
        for m in merged:
            if r.get("domain") and r["domain"] == m.get("domain"):
                hit = m; break
            if r.get("phone") and _norm_phone(r["phone"]) and _norm_phone(r["phone"]) == _norm_phone(m.get("phone", "")):
                hit = m; break
            if _norm_name(r.get("name", "")) and _norm_name(r["name"]) == _norm_name(m.get("name", "")):
                hit = m; break
        if hit:
            for k in ("domain", "phone", "address", "owner"):
                if not hit.get(k) and r.get(k):
                    hit[k] = r[k]
            hit["source"] = sorted(set(hit["source"]) | set(r["source"]))
        else:
            merged.append(r)
    return merged


def _record_to_lead(r):
    """Map a sourced record to an Instantly lead. Email required — Instantly is email-first.
    Sadie's intent signal (if present) rides along as custom variables so Reilly's first touch can
    reference the actual trigger ("saw your post about missed calls…") via merge vars."""
    nm = (r.get("owner") or "").split()
    tags = "+".join(r.get("source", []))
    intent = r.get("intent") or {}
    return {"email": r.get("email", ""), "first_name": nm[0] if nm else "",
            "last_name": " ".join(nm[1:]) if len(nm) > 1 else "",
            "company_name": r.get("name", ""),
            # custom variables travel with the lead so the source + intent signal survive into Instantly
            "yourco_source": tags, "yourco_phone": r.get("phone", ""),
            "yourco_address": r.get("address", ""),
            "yourco_intent": intent.get("signal", ""),        # what they said / the pain they showed
            "yourco_intent_url": intent.get("url", ""),       # link to the post/thread/job
            "yourco_intent_platform": intent.get("platform", "")}  # reddit / x / linkedin / job-board


def _crm_index():
    """David's check: the set of who we already have a RELATIONSHIP with (CRM), so cold outreach
    never touches them. Returns (domains, emails, norm-names) from crm/data.json."""
    try:
        crm = json.load(open(CRM))
    except Exception:
        return set(), set(), set()
    comps = crm.get("companies", [])
    contacts = crm.get("contacts", [])
    domains = {(c.get("domain") or "").lower() for c in comps if c.get("domain")}
    names = {_norm_name(c.get("name", "")) for c in comps if c.get("name")}
    emails = {(p.get("email") or "").lower() for p in contacts if p.get("email")}
    return domains, emails, names


def stage_into_instantly(records, campaign, dry_run=True):
    """Stage deduped records into an Instantly campaign (the cold system of record). Staging only —
    never starts or sends. Two guards: (1) David's CRM-dedup — records already a relationship are
    pulled out (never cold-contacted); (2) email-first — no-email records reported separately."""
    import instantly
    cd, ce, cn = _crm_index()
    known, fresh = [], []
    for r in records:
        if ((r.get("domain", "").lower() in cd and r.get("domain")) or
                (r.get("email", "").lower() in ce and r.get("email")) or
                (_norm_name(r.get("name", "")) in cn and r.get("name"))):
            known.append(r)        # already a relationship → David's domain, not cold outreach
        else:
            fresh.append(r)
    with_email = [r for r in fresh if r.get("email")]
    no_email = [r for r in fresh if not r.get("email")]
    camp = instantly.find_campaign(campaign)
    if not camp:
        return {"error": f"campaign '{campaign}' not found — create it in Instantly first.",
                "no_email": [r.get("name", "") for r in no_email],
                "already_in_crm": [r.get("name", "") for r in known]}
    leads = [_record_to_lead(r) for r in with_email]
    staged = instantly.add_leads(camp.get("id"), leads, dry_run=dry_run)
    return {"campaign": campaign, "campaign_id": camp.get("id"),
            "staged": [r.get("name", "") for r in with_email], "staged_detail": staged,
            "no_email": [r.get("name", "") for r in no_email],
            "already_in_crm": [r.get("name", "") for r in known]}


if __name__ == "__main__":
    a = sys.argv[1:]
    commit = "--commit" in a
    campaign = a[a.index("--campaign") + 1] if "--campaign" in a else ""
    records = []
    if "--outscraper" in a:
        import outscraper
        q = a[a.index("--outscraper") + 1]
        lim = int(a[a.index("--limit") + 1]) if "--limit" in a else 10
        rows = outscraper.search(q, lim)
        print(f"Outscraper: {len(rows)} from {q!r}")
        records += rows
    if "--instantly-search" in a:
        try:
            import instantly
            q = a[a.index("--instantly-search") + 1]
            rows = instantly.supersearch(q)
            print(f"Instantly SuperSearch: {len(rows)}")
            records += rows
        except Exception as e:
            print(f"Instantly SuperSearch skipped: {e}")
    if "--vibe-json" in a:
        rows = json.load(open(a[a.index("--vibe-json") + 1]))
        for r in rows:
            r.setdefault("source", ["vibe"])
        print(f"Vibe (from file): {len(rows)}")
        records += rows
    if "--sadie-json" in a:
        # Sadie's intent leads: [{name, domain?, email?, phone?, intent:{signal,url,platform}}]
        rows = json.load(open(a[a.index("--sadie-json") + 1]))
        for r in rows:
            r.setdefault("source", ["sadie"])
        print(f"Sadie (intent leads): {len(rows)} — staged cold into their own intent campaign")
        records += rows
    if not records:
        print(__doc__); sys.exit(0)
    merged = dedupe(records)
    print(f"\n{len(records)} raw → {len(merged)} after dedupe.")
    if not campaign:
        print("No --campaign given. Cold leads stage into an Instantly campaign (the cold system of record),")
        print("not the CRM. Pass --campaign \"<name>\" (create it in Instantly first). Deduped preview:")
        for r in merged:
            print(f"  • {r.get('name','')}  [{'+'.join(r.get('source',[]))}]"
                  f"{'  (no email — needs Enrich)' if not r.get('email') else ''}")
        sys.exit(0)
    res = stage_into_instantly(merged, campaign, dry_run=not commit)
    if res.get("error"):
        print(f"ERROR: {res['error']}")
        if res.get("no_email"):
            print(f"  ({len(res['no_email'])} had no email anyway — need Enrich before Instantly.)")
        sys.exit(1)
    print(f"{'COMMITTED (staged into Instantly — NOT sent)' if commit else 'DRY RUN'}: "
          f"{len(res['staged'])} staged into '{campaign}', {len(res['no_email'])} no-email, "
          f"{len(res.get('already_in_crm', []))} already a relationship (skipped cold).")
    for n in res["staged"]:
        print(f"  → {n}")
    for n in res["no_email"]:
        print(f"  ⊘ {n}  (phone/SMS-channel or needs email enrichment first)")
    for n in res.get("already_in_crm", []):
        print(f"  ◆ {n}  (already in CRM — David's domain; route warm/human, NOT cold)")
    if not commit:
        print("\n(dry run — re-run with --commit to stage into Instantly. Staging only; never sends.)")
