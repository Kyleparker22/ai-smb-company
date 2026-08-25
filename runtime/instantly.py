#!/usr/bin/env python3
"""yourco — native Instantly connector (Reilly's outbound tool, owned, no third-party MCP).

Stages leads into Instantly campaigns and reads reply/status. **Staging only — it never starts or
sends a campaign.** Sends stay gated by Reilly's batch approval + warmup + Polo's per-vertical pricing
lock + the OtherVenture launch gate; this just loads the leads so the send is one human action in Instantly.

Pure stdlib (urllib) — no pip install. Key from env (INSTANTLY_API_KEY), e.g. runtime/.instantly.env
(gitignored). Lives on the runtime where Reilly runs; callable from Cowork too with the same key.

Usage:
  python3 runtime/instantly.py --self-check                 # config check, no network
  python3 runtime/instantly.py --campaigns                  # list campaigns (live)
  python3 runtime/instantly.py --create "<name>"            # dry-run: preview the campaign + sequence
  python3 runtime/instantly.py --create "<name>" --commit   # create it (DRAFT/PAUSED — never activated)
  python3 runtime/instantly.py --stage "<campaign>" --vertical landscaping --dry-run
  python3 runtime/instantly.py --stage "<campaign>" --vertical landscaping   # actually add (still no send)
  python3 runtime/instantly.py --leads "<campaign>"                          # list leads + who has a demo_url
  python3 runtime/instantly.py --write-demos "<campaign>" --base "https://yourco.com/prospect-demo.html?p="           # dry-run: per-lead demo_url
  python3 runtime/instantly.py --write-demos "<campaign>" --base "…?p=" --commit   # write {{demo_url}} (never sends)
  python3 runtime/instantly.py --eval-batch "<campaign>" [--sample 10]  # pre-send gate: mechanical M1-M5 -> loops/outreach-eval/*.mechanical.json

Verify endpoint shapes against the current Instantly API v2 docs before binding reliance — field names
have evolved; this targets the documented v2 surface.
"""
import os, sys, json, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
BASE = os.environ.get("INSTANTLY_BASE", "https://api.instantly.ai/api/v2")


def _load_env():
    """Read runtime/.instantly.env (KEY=value) without overriding real env vars."""
    p = os.path.join(HERE, ".instantly.env")
    if not os.path.exists(p):
        return
    for line in open(p):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
KEY = os.environ.get("INSTANTLY_API_KEY", "").strip()


def _req(method, path, body=None):
    if not KEY:
        raise RuntimeError("no INSTANTLY_API_KEY (set it in runtime/.instantly.env)")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Authorization": "Bearer " + KEY,
                                        "Content-Type": "application/json",
                                        "Accept": "application/json",
                                        # Instantly's API is behind Cloudflare, which 403s (code 1010)
                                        # the default urllib UA. A normal UA gets through.
                                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                      "Chrome/124.0 Safari/537.36"})
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Instantly {method} {path} -> {e.code}: {e.read().decode()[:300]}")


# ---- read ----------------------------------------------------------------
def list_campaigns():
    return _req("GET", "/campaigns")


def find_campaign(name):
    data = list_campaigns()
    items = data.get("items", data if isinstance(data, list) else [])
    for c in items:
        if (c.get("name", "").strip().lower() == (name or "").strip().lower()):
            return c
    return None


def campaign_analytics(campaign_id):
    return _req("GET", f"/campaigns/analytics?id={campaign_id}")


# A lead's interest/reply status that counts as "warm" — i.e. graduates to the CRM.
# Instantly exposes interest status as small ints (1=interested, 2=meeting booked, 3=meeting completed,
# 4=closed/won) plus string statuses on some plans. We treat any positive-interest signal as warm.
WARM_STATUS = {1, 2, 3, 4}
WARM_STATUS_STR = {"interested", "meeting_booked", "meeting_completed", "won", "closed", "positive"}


def _is_warm(lead):
    st = lead.get("lead_interest_status", lead.get("interest_status", lead.get("status")))
    if isinstance(st, (int, float)):
        return int(st) in WARM_STATUS
    if isinstance(st, str):
        return st.strip().lower() in WARM_STATUS_STR
    # fallback: an explicit reply with no negative/OOO classification
    return bool(lead.get("email_reply_count") or lead.get("replied"))


def warm_replies(campaign=None, limit=100):
    """Read leads that replied with positive intent (optionally scoped to one campaign), normalized for
    promotion into the CRM. NOTE: Instantly's leads/replies surface varies by plan + has evolved — verify
    the endpoint/field names against current v2 docs before binding reliance. Callers degrade gracefully.
    Returns: [{name, email, company, phone, status, source:['instantly']}]."""
    body = {"limit": limit}
    if campaign:
        camp = find_campaign(campaign)
        if camp:
            body["campaign"] = camp.get("id")
    data = _req("POST", "/leads/list", body)
    items = data.get("items", data if isinstance(data, list) else [])
    out = []
    for l in items:
        if not _is_warm(l):
            continue
        nm = ((l.get("first_name", "") + " " + l.get("last_name", "")).strip()
              or l.get("name", ""))
        out.append({"name": nm, "email": l.get("email", ""),
                    "company": l.get("company_name", l.get("company", "")),
                    "phone": l.get("phone", l.get("yourco_phone", "")),
                    "status": l.get("lead_interest_status", l.get("status", "replied")),
                    "campaign": l.get("campaign", ""), "source": ["instantly"]})
    return out


def supersearch(query, limit=25):
    """Instantly SuperSearch (B2B lead finder) → normalized prospects (the common schema).
    NOTE: SuperSearch API exposure varies by plan; this targets the documented surface and may need
    the endpoint/field names adjusted. Callers (sourcing.py) degrade gracefully if it's unavailable."""
    data = _req("POST", "/supersearch", {"search": query, "limit": limit})
    items = data.get("items", data if isinstance(data, list) else [])
    out = []
    for b in items:
        site = (b.get("website") or b.get("domain") or "")
        out.append({"name": b.get("company_name", b.get("organization", "")),
                    "domain": site.replace("https://", "").replace("http://", "").split("/")[0].lstrip("www."),
                    "phone": b.get("phone", ""), "address": b.get("location", ""),
                    "owner": (b.get("first_name", "") + " " + b.get("last_name", "")).strip(),
                    "employees": b.get("employee_count", ""), "revenue": b.get("revenue", ""),
                    "source": ["instantly"]})
    return out


# ---- create campaign + load Reilly's paused sequence (NEVER activates) ----
SEQUENCE_MD = os.path.join(REPO, "processes", "outbound", "sequence-copy.md")


def parse_sequence_copy(path=SEQUENCE_MD):
    """Parse Reilly's sequence-copy.md → ordered email steps. Returns
    [{day:int, subjects:[str], body:str}]. Stops at the SMS / checklist sections (not email steps).
    The copy already uses Instantly's native {{var|fallback}} syntax — no conversion needed."""
    import re as _re
    lines = open(path, encoding="utf-8").read().splitlines()
    steps, cur, in_body, body = [], None, False, []

    def _close():
        nonlocal cur, body
        if cur is not None:
            cur["body"] = "\n".join(body).strip()
            steps.append(cur)
        cur, body = None, []

    for ln in lines:
        h = _re.match(r"##\s+Touch\s+\d+\s+—\s+Day\s+(\d+)", ln)
        if h:
            _close()
            cur = {"day": int(h.group(1)), "subjects": [], "body": ""}
            in_body = False
            continue
        if ln.startswith("## ") and ("SMS" in ln or "Pre-send" in ln or "checklist" in ln.lower()):
            _close()
            break
        if cur is None:
            continue
        sub = _re.match(r"\*\*Subject(?:\s+[AB])?:\*\*\s*`(.+?)`", ln)
        if sub:
            cur["subjects"].append(sub.group(1))
            continue
        if ln.strip() == "```":
            in_body = not in_body
            continue
        if in_body:
            body.append(ln)
    _close()
    return [s for s in steps if s.get("subjects") and s.get("body")]


def _build_sequence_steps(parsed):
    """Map parsed touches → Instantly sequence steps. delay = days since the previous step (Instantly's
    'wait N days before this step'). Touch 1 = delay 0. Subject A/B become two variants on step 1."""
    steps, prev_day = [], 0
    for i, s in enumerate(parsed):
        delay = 0 if i == 0 else max(0, s["day"] - prev_day)
        prev_day = s["day"]
        html = s["body"].replace("\n", "<br>\n")
        variants = [{"subject": subj, "body": html} for subj in s["subjects"]] or [{"subject": "", "body": html}]
        steps.append({"type": "email", "delay": delay, "variants": variants})
    return steps


def create_campaign(name, parsed=None, dry_run=True):
    """Create an Instantly campaign loaded with Reilly's sequence — **in DRAFT/PAUSED state, never
    activated.** A new v2 campaign defaults to draft; this module never calls the activate endpoint, so
    nothing can send from here. dry_run prints the payload without POSTing.
    NOTE: verify the v2 /campaigns create schema against current docs before binding reliance — field
    names (campaign_schedule/sequences/steps/variants) have evolved. Returns the API response (or the
    would-be payload on dry_run)."""
    if parsed is None:
        parsed = parse_sequence_copy()
    steps = _build_sequence_steps(parsed)
    payload = {
        "name": name,
        # Mon–Fri, 9–5 ET. Schedule only governs WHEN an *active* campaign would send; it stays paused.
        "campaign_schedule": {"schedules": [{
            "name": "Business hours",
            "timing": {"from": "09:00", "to": "17:00"},
            "days": {"0": False, "1": True, "2": True, "3": True, "4": True, "5": True, "6": False},
            "timezone": "America/New_York"}]},
        "sequences": [{"steps": steps}],
    }
    if dry_run:
        return {"dry_run": True, "name": name, "steps": len(steps),
                "subjects": [v["subject"] for s in steps for v in s["variants"]], "payload": payload}
    resp = _req("POST", "/campaigns", payload)
    # Hard guard: we create in draft and never activate. If the API ever returned an active status,
    # surface it loudly rather than let a live campaign exist silently.
    status = resp.get("status")
    resp["_yourco_guard"] = ("OK — draft/paused; not activated" if status in (None, 0, "draft", "paused")
                             else f"WARNING: unexpected status {status!r} — verify it is NOT sending")
    return resp


# ---- stage (NEVER sends) --------------------------------------------------
def add_lead(campaign_id, email, first_name="", last_name="", company_name="", **custom):
    """Add ONE lead to a campaign (staging). Does not start or send the campaign."""
    body = {"campaign": campaign_id, "email": email, "first_name": first_name,
            "last_name": last_name, "company_name": company_name}
    if custom:
        body["custom_variables"] = custom
    return _req("POST", "/leads", body)


def add_leads(campaign_id, leads, dry_run=True):
    """leads = [{email, first_name?, last_name?, company_name?, ...}]. dry_run prints, doesn't push."""
    out = []
    for l in leads:
        if not l.get("email"):
            continue
        if dry_run:
            out.append({"would_add": l.get("email"), "company": l.get("company_name", "")})
        else:
            out.append(add_lead(campaign_id, **l))
    return out


def leads_from_crm(vertical=None):
    """Build a lead list from the CRM: sourced/not-contacted companies (optionally a vertical) whose
    contact has an email. Pulls from crm/data.json — never invents an email."""
    crm = json.load(open(CRM))
    comp = {c["id"]: c for c in crm.get("companies", [])}
    leads = []
    for p in crm.get("contacts", []):
        c = comp.get(p.get("companyId"))
        if not c or not p.get("email"):
            continue
        if vertical and vertical.lower() not in (c.get("vertical", "").lower()):
            continue
        nm = (p.get("name") or "").split()
        leads.append({"email": p["email"], "first_name": nm[0] if nm else "",
                      "last_name": " ".join(nm[1:]) if len(nm) > 1 else "",
                      "company_name": c.get("name", "")})
    return leads


# ---- demo-prep: read leads + write each lead's demo_url (NEVER sends) ------
# Powers the demo-prep loop (decisions/2026-06-17_auto-demo-prep-loop.md): read a campaign's leads, then
# write a per-lead `demo_url` custom variable (which Email 1 merges via {{demo_url}}). Writing a custom
# variable does NOT send — sending stays a human action in Instantly. Verify the /leads/list + lead-update
# field names against current v2 docs before binding reliance; callers degrade gracefully.
import re as _re_dp


def _slug(s):
    s = (s or "").lower()
    s = _re_dp.sub(r"\b(llc|inc|co|corp|ltd|the|company|services|service|group)\b", "", s)
    return _re_dp.sub(r"[^a-z0-9]+", "-", s).strip("-")


def campaign_leads(campaign, limit=500):
    """All leads in a campaign, normalized: [{id, email, first_name, last_name, company, demo_url, custom}].
    `demo_url` is pulled from the lead's existing custom variables (None if not set yet)."""
    body = {"limit": limit}
    camp = find_campaign(campaign) if campaign else None
    if camp:
        body["campaign"] = camp.get("id")
    data = _req("POST", "/leads/list", body)
    items = data.get("items", data if isinstance(data, list) else [])
    out = []
    for l in items:
        cv = l.get("custom_variables") or {}
        out.append({"id": l.get("id", l.get("lead_id", "")), "email": l.get("email", ""),
                    "first_name": l.get("first_name", ""), "last_name": l.get("last_name", ""),
                    "company": l.get("company_name", l.get("company", "")),
                    "demo_url": cv.get("demo_url") or l.get("demo_url"), "custom": cv})
    return out


def set_lead_variables(lead_id, variables):
    """Write/merge custom variables on ONE lead (e.g. {'demo_url': '...'}). PATCH — does not send."""
    if not lead_id:
        raise ValueError("set_lead_variables: missing lead_id")
    return _req("PATCH", f"/leads/{lead_id}", {"custom_variables": variables})


def write_demo_urls(campaign, base_url=None, url_for=None, overwrite=False, dry_run=True):
    """For every lead in `campaign`, ensure a `demo_url` is set. The URL comes from `url_for(lead)` (a
    callable, used by the demo-prep loop once the demo generator exists) or, as a staged default, from
    `base_url` + a slug of the lead's company. Leads that already have a demo_url are skipped unless
    overwrite=True. Leads with no resolvable URL are reported (never guessed). dry_run reports without writing.
    Returns {written:[...], have_url:[...], no_url:[...]}. NEVER sends — only writes the merge variable."""
    leads = campaign_leads(campaign)
    res = {"written": [], "have_url": [], "no_url": []}
    for l in leads:
        if l.get("demo_url") and not overwrite:
            res["have_url"].append(l["email"]); continue
        url = None
        if url_for:
            url = url_for(l)
        elif base_url:
            key = _slug(l.get("company") or l.get("email", "").split("@")[0])
            url = (base_url + key) if key else None
        if not url:
            res["no_url"].append(l["email"]); continue
        if dry_run:
            res["written"].append({"email": l["email"], "demo_url": url, "dry_run": True})
        else:
            set_lead_variables(l["id"], {"demo_url": url})
            res["written"].append({"email": l["email"], "demo_url": url})
    return res


# ---- pre-send eval gate: mechanical pre-pass (M1–M5) -----------------------
# The scriptable half of processes/outbound/pre-send-eval-gate.md. Emits JSON to
# loops/outreach-eval/<date>_<campaign-slug>.mechanical.json for Kolby's judgment pass
# (runtime/prompts/outreach-eval.md). Read-only against Instantly + the CRM — never sends.
# M6–M8 (batch cap, CAN-SPAM elements, Rafi/SMS) are judgment/context checks and stay Kolby's.
EVAL_DIR = os.path.join(REPO, "loops", "outreach-eval")

# Campaign statuses that mean "not sending". Instantly v2 uses small ints (0=draft, 1=active,
# 2=paused) and strings on some surfaces — anything not in this set fails M1 loudly.
NOT_SENDING = {None, 0, 2, "draft", "paused", "0", "2"}


def _fetch_ok(url, want=None, timeout=20):
    """GET a demo_url; True if it returns 200 AND (when `want` given) the page text contains the
    lead's business-name token, case-insensitive. Never raises — returns (ok, note)."""
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                               "Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            if resp.status != 200:
                return False, f"HTTP {resp.status}"
            if want:
                body = resp.read(300_000).decode("utf-8", "replace").lower()
                if want.lower() not in body:
                    return False, f"200 but business token {want!r} not on page"
            return True, "ok"
    except Exception as e:
        return False, f"fetch failed: {e.__class__.__name__}: {str(e)[:120]}"


def _name_token(company):
    """First significant word of the company name — the thing a personalized demo must render."""
    for w in _re_dp.sub(r"[^a-z0-9 ]+", " ", (company or "").lower()).split():
        if w not in ("the", "a", "llc", "inc", "co", "corp", "ltd") and len(w) > 2:
            return w
    return ""


def eval_batch(campaign, sample=10):
    """Mechanical checks M1–M5 for a staged batch → dict (also see --eval-batch CLI).
    M1 campaign not sending · M2 merge fields non-empty · M3 every lead has demo_url ·
    M4 sampled demo_urls resolve + show the business · M5 no lead already in the CRM (the
    architecture: crm/data.json is warm+ only, so ANY match = already ours, don't cold-contact)
    or in another campaign. Any check fail => mechanical_pass=False. Read-only."""
    camp = find_campaign(campaign)
    if not camp:
        return {"campaign": campaign, "error": "campaign not found", "mechanical_pass": False}
    checks = {}

    # M1 — campaign is not sending
    status = camp.get("status")
    checks["M1_paused"] = {"pass": status in NOT_SENDING, "status": status}

    leads = campaign_leads(campaign)
    # M2 — merge fields non-empty on every lead
    bad_fields = [l["email"] or "(no email)" for l in leads
                  if not (l.get("email") and l.get("first_name") and l.get("company"))]
    checks["M2_merge_fields"] = {"pass": not bad_fields, "missing_on": bad_fields}

    # M3 — every lead has a demo_url
    no_demo = [l["email"] for l in leads if not l.get("demo_url")]
    checks["M3_demo_urls_set"] = {"pass": not no_demo, "missing_on": no_demo}

    # M4 — sampled demo_urls resolve AND render that lead's business
    with_demo = [l for l in leads if l.get("demo_url")]
    step = max(1, len(with_demo) // max(1, sample))
    picked = with_demo[::step][:sample]  # deterministic spread, no RNG needed
    m4 = []
    for l in picked:
        ok, note = _fetch_ok(l["demo_url"], want=_name_token(l.get("company")))
        m4.append({"email": l["email"], "url": l["demo_url"], "ok": ok, "note": note})
    checks["M4_demos_resolve"] = {"pass": all(x["ok"] for x in m4) and bool(m4), "sampled": m4}

    # M5a — no lead already in the CRM (warm+ only lives there; a hit means they're already ours)
    try:
        crm = json.load(open(CRM))
        crm_emails = {(p.get("email") or "").strip().lower() for p in crm.get("contacts", []) if p.get("email")}
        in_crm = [l["email"] for l in leads if (l.get("email") or "").strip().lower() in crm_emails]
    except Exception as e:
        in_crm = [f"(CRM unreadable: {e})"]
    # M5b — no lead staged in another campaign (double-contact guard); degrade gracefully
    dupes = []
    try:
        data = list_campaigns()
        others = [c for c in data.get("items", data if isinstance(data, list) else [])
                  if c.get("id") != camp.get("id")]
        here = {(l.get("email") or "").strip().lower() for l in leads}
        for c in others:
            for l in campaign_leads(c.get("name", "")):
                if (l.get("email") or "").strip().lower() in here:
                    dupes.append({"email": l["email"], "also_in": c.get("name", c.get("id"))})
    except Exception as e:
        dupes = [{"error": f"cross-campaign check degraded: {str(e)[:120]}"}]
    m5_pass = not in_crm and not any(d.get("email") for d in dupes if isinstance(d, dict))
    checks["M5_dedupe"] = {"pass": m5_pass, "already_in_crm": in_crm, "in_other_campaigns": dupes}

    return {"campaign": camp.get("name", campaign), "campaign_id": camp.get("id"),
            "lead_count": len(leads), "sample_size": len(picked), "checks": checks,
            "mechanical_pass": all(c["pass"] for c in checks.values()),
            "note": "M1–M5 only — M6–M8 + the six-dimension judgment pass are Kolby's "
                    "(processes/outbound/pre-send-eval-gate.md). Read-only; never sends."}


def write_eval_batch(campaign, sample=10):
    """Run eval_batch and write the JSON where Kolby's gate prompt reads it. Returns (result, path)."""
    import datetime
    res = eval_batch(campaign, sample=sample)
    os.makedirs(EVAL_DIR, exist_ok=True)
    path = os.path.join(EVAL_DIR, f"{datetime.date.today().isoformat()}_{_slug(campaign)}.mechanical.json")
    res["generated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    json.dump(res, open(path, "w"), indent=2)
    return res, path


# ---- cli ------------------------------------------------------------------
def _self_check():
    print(f"yourco Instantly connector — config check")
    print(f"  API key set: {bool(KEY)}   base: {BASE}")
    print(f"  CRM source:  {CRM} ({'found' if os.path.exists(CRM) else 'MISSING'})")
    print(f"  sequence:    {SEQUENCE_MD} ({'found' if os.path.exists(SEQUENCE_MD) else 'MISSING'})")
    try:
        n = len(parse_sequence_copy())
        print(f"  parsed sequence steps: {n} (Reilly's paused 4-touch copy)")
    except Exception as e:
        print(f"  parsed sequence steps: ERROR — {e}")
    print("  demo-prep: campaign_leads() + write_demo_urls() available — writes per-lead {{demo_url}}, never sends.")
    print("  guard: STAGING ONLY — creates campaigns in DRAFT/PAUSED, writes merge vars; never activates or sends.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-check" in a:
        sys.exit(_self_check())
    if "--campaigns" in a:
        print(json.dumps(list_campaigns(), indent=2)); sys.exit(0)
    if "--create" in a:
        name = a[a.index("--create") + 1]
        commit = "--commit" in a
        res = create_campaign(name, dry_run=not commit)
        if res.get("dry_run"):
            print(f"DRY RUN — would create campaign '{name}' with {res['steps']} email steps (DRAFT/PAUSED).")
            print("  subjects:")
            for s in res["subjects"]:
                print(f"    • {s}")
            print("\n(re-run with --commit to create it. It will be DRAFT/PAUSED — never activated.)")
        else:
            print(f"Created campaign '{name}'. Guard: {res.get('_yourco_guard')}")
            print(json.dumps({k: v for k, v in res.items() if k != 'payload'}, indent=2)[:800])
        sys.exit(0)
    if "--leads" in a:
        name = a[a.index("--leads") + 1]
        leads = campaign_leads(name)
        have = sum(1 for l in leads if l.get("demo_url"))
        print(f"{len(leads)} leads in '{name}' — {have} already have a demo_url, {len(leads)-have} missing.")
        for l in leads[:10]:
            print(f"  {l['email']:<34} demo_url={'set' if l.get('demo_url') else '—'}  ({l.get('company','')})")
        sys.exit(0)
    if "--write-demos" in a:
        name = a[a.index("--write-demos") + 1]
        base = a[a.index("--base") + 1] if "--base" in a else None
        commit = "--commit" in a
        if not base:
            print("usage: --write-demos \"<campaign>\" --base \"https://yourco.com/prospect-demo.html?p=\" [--commit]")
            print("(base is the per-prospect demo URL prefix; the real demo generator supplies url_for once built.)")
            sys.exit(1)
        res = write_demo_urls(name, base_url=base, dry_run=not commit)
        print(f"{'DRY RUN — ' if not commit else ''}demo_url write for '{name}': "
              f"{len(res['written'])} {'would be ' if not commit else ''}written, "
              f"{len(res['have_url'])} already set, {len(res['no_url'])} had no resolvable URL. (never sends)")
        for w in res["written"][:10]:
            print(f"  {w['email']} -> {w['demo_url']}")
        if not commit:
            print("\n(re-run with --commit to write the merge vars. This only sets {{demo_url}}; it never sends.)")
        sys.exit(0)
    if "--eval-batch" in a:
        name = a[a.index("--eval-batch") + 1]
        sample = int(a[a.index("--sample") + 1]) if "--sample" in a else 10
        res, path = write_eval_batch(name, sample=sample)
        verdict = "PASS" if res.get("mechanical_pass") else "FAIL"
        print(f"MECHANICAL PRE-PASS {verdict} — '{res.get('campaign', name)}' "
              f"({res.get('lead_count', '?')} leads, {res.get('sample_size', 0)} demos fetched)")
        for k, c in (res.get("checks") or {}).items():
            print(f"  {'✓' if c['pass'] else '✗'} {k}")
        print(f"  written: {path}")
        print("(M1–M5 only. Kolby's judgment pass — runtime/prompts/outreach-eval.md — reads this file; "
              "the batch needs his dated PASS artifact before any send.)")
        sys.exit(0 if res.get("mechanical_pass") else 1)
    if "--stage" in a:
        name = a[a.index("--stage") + 1]
        vertical = a[a.index("--vertical") + 1] if "--vertical" in a else None
        dry = "--dry-run" in a
        camp = find_campaign(name)
        if not camp:
            print(f"campaign '{name}' not found — create it in Instantly first."); sys.exit(1)
        cid = camp.get("id")
        leads = leads_from_crm(vertical)
        print(f"{'DRY RUN — ' if dry else ''}staging {len(leads)} leads into '{name}' ({cid}). No send.")
        for r in add_leads(cid, leads, dry_run=dry):
            print("  ", r)
        sys.exit(0)
    print(__doc__)
