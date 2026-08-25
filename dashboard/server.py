#!/usr/bin/env python3
"""yourco dashboard backend — serves the dashboard + aggregates the OS's live data.

Run:  python3 dashboard/server.py    then open  http://127.0.0.1:8791

GET /api/dashboard -> { dashboard: data.json, pipeline: <live summary from crm/data.json>, generatedAt }
GET /api/reports   -> every loops/* report source + its dated artifacts (Reports tab rail)
GET /api/report?dir=&date= -> one report's markdown (strict validation; date omitted = latest)
GET /api/instantly -> Instantly outbound metrics (key from runtime/.instantly.env; cached 6h in loops/_instantly/)
GET/POST /api/todo -> the Founder's to-do list (dashboard/todo.json; POST = full-list overwrite, atomic)
Read-only aggregator (Atlas owns the source data; David owns the CRM). Local bind only.
As more tools land (QuickBooks...), extend the aggregation here and the relevant tab fills in.
"""
import json, os, re, sys, time, http.server, socketserver, datetime, urllib.request, urllib.error
from urllib.parse import urlparse, parse_qs

try:
    import melanie  # Phase-2 brain + voice (sibling module). Optional; endpoint degrades gracefully.
except Exception:
    melanie = None

try:
    import refresh  # derived layer (loop health, autonomy, gates, git) — recomputed live per poll
except Exception:
    refresh = None

try:
    import board  # The Board — every open item in the OS, aggregated live from its real sources
except Exception:
    board = None

try:
    import clients as clients_view  # The Clients view — one row per engagement, sources joined
except Exception:
    clients_view = None

try:
    import finance as finance_view  # The Finance view — the model, mirrored (read-only) + staleness
except Exception:
    finance_view = None

# ---- the Evidence door (added 2026-08-07) ---------------------------------
# Five views that each answer a question the OS could not previously answer about itself.
# Every one is read-only and degrades to an honest error rather than taking the poll down.
try:
    import trust as trust_view          # trust ledger · calibration market · immune drills
except Exception:
    trust_view = None
try:
    import tripwires as tripwires_view  # decisions watching themselves for expiry
except Exception:
    tripwires_view = None
try:
    import timemachine as tm_view       # HQ as of any date + business-metric blame
except Exception:
    tm_view = None
try:
    import twin as twin_view            # the DRI twin scoreboard
except Exception:
    twin_view = None
try:
    import vacancies as vacancies_view  # the org chart that grows from observed work
except Exception:
    vacancies_view = None
try:
    import lockin as lockin_view  # the partner review->lock run, state derived from decisions/
except Exception:
    lockin_view = None
try:
    import governance as governance_view  # the partner half: split, OA, gate #14, what's unrecorded
except Exception:
    governance_view = None
try:
    import advocate as advocate_view  # the people loop — is the connector flywheel turning?
except Exception:
    advocate_view = None

# ---- the six panel builds (2026-08-13) ------------------------------------
# Three point yourco's own instrumentation at the client (pregolive · client trip-wires ·
# counterfactual); three harden the OS itself (security model · sleep-time · agent expiry,
# which rides inside /api/vacancies). Writers live in runtime/; these are read-only views.
# computed from __file__, not ROOT — ROOT is defined further down this file
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "runtime"))
try:
    import security_model as secmodel_view
except Exception:
    secmodel_view = None
try:
    import pregolive as pregolive_view
except Exception:
    pregolive_view = None
try:
    import sleeptime as sleeptime_view
except Exception:
    sleeptime_view = None
try:
    import client_tripwires as ctw_view
except Exception:
    ctw_view = None
try:
    import counterfactual as counterfactual_view
except Exception:
    counterfactual_view = None
try:
    import skills as skills_view  # the skill library + whether each one is actually being used
except Exception:
    skills_view = None

# ---- the WBR door (2026-08-13) --------------------------------------------
# Amazon's discipline: controllable inputs above the outputs, the 6-12 chart, and a format lock.
# Plus the two views that need HQ to remember it was looked at, and the one that argues with it.
try:
    import wbr as wbr_view
except Exception:
    wbr_view = None
try:
    import prosecution as prosecution_view
except Exception:
    prosecution_view = None
try:
    import hq_usage as hq_usage_view
except Exception:
    hq_usage_view = None

# ---- the one number, and the number each agent owns (2026-08-25) ----------
# Nine co-equal goal metrics is zero goals, and 27 agents owned no numbers. Both halves are one fix:
# northstar.py reads the apex from goals.json (the Founder's) and the per-agent definitions from the
# sanctioned registry (Rafi's), and computes every value live. kpis.py defines the nine finance KPIs
# with the precondition each is waiting on, so client #1 does not arrive to an undefined formula.
try:
    import northstar as northstar_view
except Exception:
    northstar_view = None
try:
    import kpis as kpis_view
except Exception:
    kpis_view = None
try:
    import uptime as uptime_view
except Exception:
    uptime_view = None

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# Playground switch (2026-08-07): code + static assets stay under HERE; only DATA moves.
# See playground/_README.md. Unset YOURCO_DATA_ROOT = live, byte-identical behavior.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
DATA_DIR = os.path.join(ROOT, "dashboard") if PLAYGROUND else HERE
if PLAYGROUND:
    os.makedirs(DATA_DIR, exist_ok=True)
DASH = os.path.join(DATA_DIR, "data.json")
CRM = os.path.join(ROOT, "crm", "data.json")
PORT = int(os.environ.get("PORT", 8791))  # PORT env lets the Cowork preview assign a port
HOST = os.environ.get("DASH_HOST", "127.0.0.1")  # set 0.0.0.0 on the VPS for Tailscale
MAX_BODY = 2 * 1024 * 1024  # 2 MB cap on request bodies (anti-DoS)


ALLOWED_EXT = {".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp", ".woff", ".woff2"}


def _served_ok(path):
    """Static allowlist: only the dashboard's own web assets. Blocks melanie.env, *.py, dotfiles,
    and path-traversal — the static handler would otherwise expose the whole dashboard/ folder."""
    if path in ("", "/"):
        return True  # index.html
    if ".." in path:
        return False
    base = os.path.basename(path)
    if base.startswith("."):  # dotfiles incl. .env, .env.example
        return False
    ext = os.path.splitext(base)[1].lower()
    if ext not in ALLOWED_EXT:
        return False
    return base not in ("melanie.env", "melanie.env.example")


def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return None


def tasks_summary():
    crm = load(CRM)
    if not crm:
        return []
    comp = {c.get("id"): c.get("name") for c in crm.get("companies", [])}
    out = []
    for t in crm.get("tasks", []) or []:
        out.append({
            "text": t.get("text", ""),
            "due": t.get("due") or "",
            "done": bool(t.get("done")),
            "company": comp.get(t.get("companyId")) or "",
        })
    return out


def pipeline_summary(crm=None):
    # crm= lets a caller supply a document instead of reading the live file — used by
    # dashboard/timemachine.py to compute this exact summary from a historical revision,
    # so "pipeline value on 2026-07-01" is the same math as today's, never a re-implementation.
    crm = crm if crm is not None else load(CRM)
    if not crm:
        return None
    deals = crm.get("deals", [])
    stages = crm.get("stages", [])
    by = {s["key"]: 0 for s in stages}
    for d in deals:
        if d.get("stage") in by:
            by[d["stage"]] += 1
    # "pipeline" = deals in motion on the ladder; the Relationship/Parked bench counts separately
    # (same split the CRM's Pipeline vs Relationships views use — the Founder 2026-07-06, ladder 2026-08-07).
    in_motion = [d for d in deals if _in_motion(d)]
    prospects = [d for d in deals if (d.get("stage") or "") in BENCH_STAGES]
    return {
        "openDeals": len(in_motion),
        "prospects": len(prospects),
        "value": sum(_deal_annual(d) for d in in_motion),
        "prospectValue": sum(_deal_annual(d) for d in prospects),
        "byStage": [{"label": s["label"], "n": by.get(s["key"], 0)} for s in stages if s["key"] not in BENCH_STAGES],
        "contacts": len(crm.get("contacts", [])),
        "companies": len(crm.get("companies", [])),
    }


# ---- loop reports (the Reports tab) ---------------------------------------
LOOPS = os.path.join(ROOT, "loops")
# dated reports incl. suffixed ones (2026-07-06_intent-sweep.md) — some loops only write suffixed
# files (brett-ideas, sadie, _audit). NOTE: refresh.py's _latest_report keeps its strict exact-date
# rule on purpose; only this reports browser is inclusive.
REPORT_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(_[a-z0-9-]+)?\.md$")
REPORT_DIR_RE = re.compile(r"^_?[a-z0-9-]+$")
REPORT_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(_[a-z0-9-]+)?$")  # filename stem, e.g. "2026-07-06_intent-sweep"
REPORTS_SKIP = {"_runtime", "_instantly", "_anthropic"}  # per-run logs + API caches — not report sources


def _report_dates(folder):
    """Report filename stems in a loop dir, newest first by the 10-char date prefix;
    a bare dated report wins a same-day tie over suffixed companions."""
    try:
        stems = [f[:-3] for f in os.listdir(folder) if REPORT_FILE_RE.match(f)]
    except OSError:
        return []
    return sorted(stems, key=lambda s: (s[:10], len(s) == 10, s), reverse=True)


def reports_index():
    """GET /api/reports — every loops/* source with its dated reports (latest 30)."""
    sources = []
    try:
        names = sorted(os.listdir(LOOPS))
    except OSError:
        names = []
    for name in names:
        if name in REPORTS_SKIP or not REPORT_DIR_RE.match(name):
            continue
        folder = os.path.join(LOOPS, name)
        if not os.path.isdir(folder):
            continue
        dates = _report_dates(folder)[:30]
        sources.append({"dir": name, "dates": dates, "latest": dates[0] if dates else None})
    return {"sources": sources}


def report_payload(qs):
    """GET /api/report?dir=&date= — one report's markdown. Strict: dir shape + realpath inside
    loops/ (no traversal), date = exact stem pattern. Missing date -> latest. None on any miss."""
    d = (qs.get("dir") or [""])[0]
    date = (qs.get("date") or [""])[0]
    if not REPORT_DIR_RE.match(d) or d in REPORTS_SKIP:
        return None
    folder = os.path.join(LOOPS, d)
    root = os.path.realpath(LOOPS)
    if not os.path.isdir(folder) or not os.path.realpath(folder).startswith(root + os.sep):
        return None
    if date:
        if not REPORT_DATE_RE.match(date):
            return None
    else:
        dates = _report_dates(folder)
        if not dates:
            return None
        date = dates[0]
    fp = os.path.join(folder, date + ".md")
    if not os.path.realpath(fp).startswith(root + os.sep) or not os.path.isfile(fp):
        return None
    try:
        with open(fp, encoding="utf-8", errors="replace") as f:
            return {"dir": d, "date": date, "md": f.read()}
    except OSError:
        return None


# ---- the Founder's to-do list (Overview panel) ------------------------------------
TODO = os.path.join(DATA_DIR, "todo.json")


def todo_doc():
    """GET /api/todo — never errors: missing/corrupt file -> empty list."""
    d = load(TODO)
    if isinstance(d, dict) and isinstance(d.get("items"), list):
        return {"items": d["items"][:200]}
    return {"items": []}


def todo_save(doc):
    """POST /api/todo — normalize + overwrite atomically (tmp + os.replace). Returns the saved doc."""
    items = []
    for it in (doc.get("items") or [])[:200]:  # cap 200
        if not isinstance(it, dict):
            continue
        items.append({
            "id": str(it.get("id") or "")[:64],
            "text": str(it.get("text") or "")[:500],
            "done": bool(it.get("done")),
            "created": str(it.get("created") or "")[:10],
            "doneAt": str(it.get("doneAt"))[:10] if it.get("doneAt") else None,
        })
    out = {"items": items}
    tmp = TODO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, TODO)
    return out


# ---- Goals (targets the Founder edits in goals.json; currents computed live) ------
GOALS = os.path.join(DATA_DIR, "goals.json")
GOAL_METRICS = ("mrr", "liveClients", "dealsInMotion", "newProspects",
                "activeConnectors", "prospectiveConnectors", "activeAdvisors", "referredMRR",
                "marginPct")
QUARTER_RE = re.compile(r"^\d{4}-Q[1-4]$")


# The ladder's bench: stages that are NOT deals in motion (relationship/parked; "prospect" kept for
# legacy rows). One definition, mirrored from the CRM — a stage rename can't silently drift HQ again.
BENCH_STAGES = ("relationship", "parked", "prospect", "pre-convo")
CLOSED_STAGES = ("live", "expand")
# "a stage rename can't silently drift HQ again" — it did, on 2026-08-13. The CRM restructured
# its ladder and the bench became `pre-convo`; nothing swept this tuple, so HQ counted all 18
# bench deals as in-motion and reported 21 deals / $24k when the real figure was 3. Caught by
# dashboard/prosecution.py, not by eye. The legacy names stay so older data still classifies.
# Machine backstop: runtime/consistency-check.py now fails if any CRM stage key is unknown here.


def _in_motion(d):
    st = (d.get("stage") or "")
    return st not in BENCH_STAGES and st not in CLOSED_STAGES


def _deal_annual(d):
    """A deal's annualized value — explicit value wins, else retainer×12 + build fee (same math the
    CRM board totals use). Never fabricated: no numbers means 0."""
    v = d.get("value")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v:
        return v
    r = d.get("retainer") if isinstance(d.get("retainer"), (int, float)) and not isinstance(d.get("retainer"), bool) else 0
    b = d.get("buildFee") if isinstance(d.get("buildFee"), (int, float)) and not isinstance(d.get("buildFee"), bool) else 0
    return (r or 0) * 12 + (b or 0)


def _deal_monthly(d):
    """A live deal's $/mo — retainer preferred, value as fallback. Never fabricated."""
    r = d.get("retainer")
    if isinstance(r, (int, float)) and not isinstance(r, bool) and r:
        return r
    v = d.get("value")
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def goals_currents(crm=None):
    """Every goal metric computed fresh from crm/data.json per call — nothing cached or stored.
    Pre-revenue reality: live-stage deals = 0 today, so mrr/liveClients/referredMRR are honest zeros.

    crm= supplies a document instead of reading the live file (dashboard/timemachine.py passes
    historical revisions through here, so an as-of number and today's number are the same math)."""
    crm = (crm if crm is not None else load(CRM)) or {}
    deals = crm.get("deals", []) or []
    comps = {c.get("id"): c for c in (crm.get("companies", []) or [])}
    live = [d for d in deals if (d.get("stage") or "") == "live"]
    referred = 0
    for d in live:  # connector-driven share of MRR: live company w/ referrer attribution set
        c = comps.get(d.get("companyId")) or {}
        if (c.get("referrer") or "").strip() or (c.get("referredByCompany") or "").strip():
            referred += _deal_monthly(d)
    # in motion = open deals on the ladder past the Relationship bench; live counted as liveClients
    in_motion = sum(1 for d in deals if _in_motion(d))
    prospects = sum(1 for d in deals if (d.get("stage") or "") in BENCH_STAGES)
    internal = [c for c in (crm.get("contacts", []) or []) if c.get("kind") == "internal"]

    def team(role):  # missing teamStatus = prospect, NOT active (CRM convention)
        pool = [c for c in internal if c.get("teamRole") == role]
        active = sum(1 for c in pool if c.get("teamStatus") == "active")
        return active, len(pool) - active

    conn_active, conn_prospect = team("connector")
    adv_active, _ = team("advisor")
    mrr = sum(_deal_monthly(d) for d in live)
    # marginPct = (mrr − run costs) / mrr. Honest-null until BOTH exist: pre-revenue -> null, and
    # revenue with no per-client cost feed (clients/*/cost.md ledgers / metered per-engagement keys)
    # -> ALSO null — never render a fake 100% margin just because costs aren't wired yet.
    margin = None
    return {
        "mrr": mrr,
        "liveClients": len({d.get("companyId") or d.get("id") for d in live}),
        "dealsInMotion": in_motion,
        "newProspects": prospects,
        "activeConnectors": conn_active,
        "prospectiveConnectors": conn_prospect,
        "activeAdvisors": adv_active,
        "referredMRR": referred,
        "marginPct": margin,
        "_marginNote": "pre-revenue" if mrr == 0 else "needs per-client cost data (clients/*/cost.md + metered keys)",
    }


def goals_period():
    """Where we are in the current quarter/year — feeds the ahead/behind pace hints."""
    t = datetime.date.today()
    q = (t.month - 1) // 3 + 1
    q_start = datetime.date(t.year, 3 * (q - 1) + 1, 1)
    q_end = datetime.date(t.year + 1, 1, 1) if q == 4 else datetime.date(t.year, 3 * q + 1, 1)
    y_start, y_end = datetime.date(t.year, 1, 1), datetime.date(t.year + 1, 1, 1)
    nq, ny = (1, t.year + 1) if q == 4 else (q + 1, t.year)
    return {
        "quarter": f"{t.year}-Q{q}", "quarterLabel": f"Q{q} {t.year}",
        "nextQuarter": f"{ny}-Q{nq}", "nextQuarterLabel": f"Q{nq} {ny}",
        "yearLabel": str(t.year),
        "quarterPctElapsed": round((t - q_start).days / (q_end - q_start).days * 100),
        "yearPctElapsed": round((t - y_start).days / (y_end - y_start).days * 100),
    }


def _goals_norm_section(sec):
    """Normalize a targets section: known metric keys only, numbers-or-null, capped note strings."""
    sec = sec if isinstance(sec, dict) else {}
    t = sec.get("targets") if isinstance(sec.get("targets"), dict) else {}
    s = sec.get("_sources") if isinstance(sec.get("_sources"), dict) else {}
    return {
        "targets": {k: (t[k] if isinstance(t.get(k), (int, float)) and not isinstance(t.get(k), bool) else None)
                    for k in GOAL_METRICS},
        "_sources": {k: str(s[k])[:200] for k in GOAL_METRICS if s.get(k)},
    }


def goals_payload():
    """GET /api/goals — targets from goals.json + live currents + period pace context."""
    doc = load(GOALS)
    doc = doc if isinstance(doc, dict) else {}
    per = goals_period()
    quarters = doc.get("quarters") if isinstance(doc.get("quarters"), dict) else {}
    qout = {str(k): _goals_norm_section(v) for k, v in quarters.items() if QUARTER_RE.match(str(k))}
    for k in (per["quarter"], per["nextQuarter"]):  # panels always have something to render
        qout.setdefault(k, _goals_norm_section({}))
    year = doc.get("year") if isinstance(doc.get("year"), dict) else {}
    return {
        "updated": doc.get("updated") or None,
        "year": {"label": str(year.get("label") or per["yearLabel"]), **_goals_norm_section(year)},
        "quarters": qout,
        "current": goals_currents(),
        "period": per,
        # The apex. Declared once, in goals.json, and echoed here so the goal band can render one
        # metric as primary instead of nine as equals. Never a second place to change it.
        "northstar": (doc.get("northstar") if isinstance(doc.get("northstar"), dict) else None),
    }


def goals_save(body):
    """POST /api/goals — merge edited targets into goals.json (atomic tmp + os.replace).
    Known metric keys only, numbers-or-null only; an edited metric drops its prefill _source note.
    Returns the full GET payload so the client repaints from the saved truth."""
    doc = load(GOALS)
    doc = doc if isinstance(doc, dict) else {}
    if not isinstance(doc.get("year"), dict):
        doc["year"] = {"label": goals_period()["yearLabel"], "targets": {}}
    if not isinstance(doc.get("quarters"), dict):
        doc["quarters"] = {}

    def apply(section, targets):
        if not isinstance(targets, dict):
            return
        t = section.setdefault("targets", {})
        if not isinstance(t, dict):
            t = section["targets"] = {}
        for k, v in targets.items():
            if k not in GOAL_METRICS:
                continue
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))):
                raise ValueError("bad target for " + k)
            t[k] = v
            src = section.get("_sources")
            if isinstance(src, dict):  # the Founder's number now, not the plan's prefill
                src.pop(k, None)

    if isinstance(body.get("year"), dict):
        apply(doc["year"], body["year"].get("targets"))
    if isinstance(body.get("quarters"), dict):
        for qk, qv in body["quarters"].items():
            if not QUARTER_RE.match(str(qk)) or not isinstance(qv, dict):
                continue
            if qk not in doc["quarters"] and len(doc["quarters"]) >= 24:
                continue  # cap: no unbounded quarter growth from bad POSTs
            apply(doc["quarters"].setdefault(qk, {}), qv.get("targets"))
    doc["updated"] = datetime.date.today().isoformat()
    tmp = GOALS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, GOALS)
    return goals_payload()


# ---- Instantly outbound metrics (GTM strip) --------------------------------
INSTANTLY_ENV = os.path.join(ROOT, "runtime", ".instantly.env")
INSTANTLY_BASE = os.environ.get("INSTANTLY_BASE", "https://api.instantly.ai/api/v2")
INSTANTLY_CACHE_DIR = os.path.join(LOOPS, "_instantly")
INSTANTLY_CACHE = os.path.join(INSTANTLY_CACHE_DIR, "latest.json")
INSTANTLY_TTL = 6 * 3600  # reuse a successful pull for 6h — the poll never hammers the API
_instantly_memo = {"t": 0.0, "data": None}  # in-process memo (10 min) so errors don't re-fire either
_CAMPAIGN_STATUS = {0: "draft", 1: "active", 2: "paused", 3: "completed", 4: "running-subsequences",
                    -99: "suspended", -1: "accounts-unhealthy", -2: "bounce-protect"}


def _instantly_key():
    """INSTANTLY_API_KEY from env, else runtime/.instantly.env (gitignored KEY=VALUE file)."""
    key = os.environ.get("INSTANTLY_API_KEY", "").strip()
    if key:
        return key
    try:
        with open(INSTANTLY_ENV) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "INSTANTLY_API_KEY":
                    return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def _instantly_get(path, key):
    # normal UA: Instantly sits behind Cloudflare, which 403s the default urllib UA (see runtime/instantly.py)
    req = urllib.request.Request(INSTANTLY_BASE + path, headers={
        "Authorization": "Bearer " + key, "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode() or "{}")


def _items(d):
    return d.get("items", []) if isinstance(d, dict) else (d if isinstance(d, list) else [])


def instantly_metrics():
    """GET /api/instantly — campaigns + sending-account summary. Cached; never fabricates."""
    now = time.time()
    if _instantly_memo["data"] is not None and now - _instantly_memo["t"] < 600:
        return _instantly_memo["data"]
    try:  # fresh disk cache from a prior successful pull?
        if now - os.stat(INSTANTLY_CACHE).st_mtime < INSTANTLY_TTL:
            cached = load(INSTANTLY_CACHE)
            if cached and cached.get("connected") and not cached.get("error"):
                _instantly_memo.update(t=now, data=cached)
                return cached
    except OSError:
        pass
    key = _instantly_key()
    if not key:
        out = {"connected": False, "hint": "add INSTANTLY_API_KEY to runtime/.instantly.env"}
        _instantly_memo.update(t=now, data=out)
        return out
    try:
        camps = _items(_instantly_get("/campaigns", key))
        accts = _items(_instantly_get("/accounts", key))
    except Exception as e:
        out = {"connected": True, "error": ("Instantly API error: " + str(e))[:200]}
        _instantly_memo.update(t=now, data=out)
        return out  # honest error, not cached to disk — retried next memo expiry
    campaigns = [{"name": c.get("name") or "(unnamed)",
                  "status": _CAMPAIGN_STATUS.get(c.get("status"), str(c.get("status")))}
                 for c in camps if isinstance(c, dict)]
    # warmup: surface what the API actually returns (field names vary) — never invent
    statuses = [a.get("warmup_status") for a in accts if isinstance(a, dict) and "warmup_status" in a]
    scores = [a.get("stat_warmup_score") for a in accts
              if isinstance(a, dict) and isinstance(a.get("stat_warmup_score"), (int, float))]
    warmup = {}
    if statuses:
        warmup["active"] = sum(1 for s in statuses if s in (1, "1", "active"))
        warmup["of"] = len(statuses)
    if scores:
        warmup["avgScore"] = round(sum(scores) / len(scores))
    out = {"connected": True, "campaigns": campaigns, "accounts": len(accts),
           "warmup": warmup or None,
           "fetched": datetime.datetime.now().isoformat(timespec="seconds")}
    try:  # cache the success: latest.json + a dated pull
        os.makedirs(INSTANTLY_CACHE_DIR, exist_ok=True)
        blob = json.dumps(out, indent=1)
        with open(INSTANTLY_CACHE, "w") as f:
            f.write(blob)
        with open(os.path.join(INSTANTLY_CACHE_DIR, datetime.date.today().isoformat() + ".json"), "w") as f:
            f.write(blob)
    except OSError:
        pass
    _instantly_memo.update(t=now, data=out)
    return out


ANTHROPIC_ENV = os.path.join(ROOT, "runtime", ".anthropic-admin.env")
ANTHROPIC_CACHE_DIR = os.path.join(LOOPS, "_anthropic")
ANTHROPIC_CACHE = os.path.join(ANTHROPIC_CACHE_DIR, "latest.json")
_anthropic_memo = {"t": 0.0, "data": None}  # same memo discipline as Instantly


def _anthropic_admin_key():
    """ANTHROPIC_ADMIN_KEY from env, else runtime/.anthropic-admin.env (gitignored KEY=VALUE file)."""
    key = os.environ.get("ANTHROPIC_ADMIN_KEY", "").strip()
    if key:
        return key
    try:
        with open(ANTHROPIC_ENV) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "ANTHROPIC_ADMIN_KEY":
                    return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def anthropic_cost():
    """GET /api/anthropic-cost — org-wide model spend from the Admin cost_report API.
    This is yourco's REAL token bill (the number CLAUDE.md's token-economics section is about),
    feeding the Reports strip + Charles's close. Cached 6h; errors surfaced, never fabricated."""
    now = time.time()
    if _anthropic_memo["data"] is not None and now - _anthropic_memo["t"] < 600:
        return _anthropic_memo["data"]
    try:
        if now - os.stat(ANTHROPIC_CACHE).st_mtime < INSTANTLY_TTL:
            cached = load(ANTHROPIC_CACHE)
            if cached and cached.get("connected") and not cached.get("error"):
                _anthropic_memo.update(t=now, data=cached)
                return cached
    except OSError:
        pass
    key = _anthropic_admin_key()
    if not key:
        out = {"connected": False, "hint": "add ANTHROPIC_ADMIN_KEY to runtime/.anthropic-admin.env"}
        _anthropic_memo.update(t=now, data=out)
        return out
    start = (datetime.date.today() - datetime.timedelta(days=30)).isoformat() + "T00:00:00Z"
    try:
        url = ("https://api.anthropic.com/v1/organizations/cost_report?"
               + urllib.parse.urlencode({"starting_at": start, "bucket_width": "1d", "limit": 31}))
        req = urllib.request.Request(url, headers={"x-api-key": key,
                                                   "anthropic-version": "2023-06-01",
                                                   "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            page = json.loads(resp.read().decode() or "{}")
    except Exception as e:
        out = {"connected": True, "error": ("Anthropic Admin API error: " + str(e))[:200]}
        _anthropic_memo.update(t=now, data=out)
        return out
    days = []
    for b in page.get("data", []):
        usd = 0.0
        for r in b.get("results", []):
            try:
                # cost_report amounts are CENTS (verified 2026-07-06 by recomputing a day's cost
                # from usage_report token counts × list prices: 564.42 reported == $5.64 actual)
                usd += float(r.get("amount", 0) or 0) / 100.0
            except (TypeError, ValueError):
                pass
        days.append({"date": str(b.get("starting_at", ""))[:10], "usd": round(usd, 2)})
    days.sort(key=lambda d: d["date"])
    today = datetime.date.today().isoformat()
    week_cut = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    out = {"connected": True,
           "cost30d": round(sum(d["usd"] for d in days), 2),
           "cost7d": round(sum(d["usd"] for d in days if d["date"] >= week_cut), 2),
           "today": round(sum(d["usd"] for d in days if d["date"] == today), 2),
           "days": days, "currency": "USD", "truncated": bool(page.get("has_more")),
           "fetched": datetime.datetime.now().isoformat(timespec="seconds")}
    try:
        os.makedirs(ANTHROPIC_CACHE_DIR, exist_ok=True)
        blob = json.dumps(out, indent=1)
        with open(ANTHROPIC_CACHE, "w") as f:
            f.write(blob)
        with open(os.path.join(ANTHROPIC_CACHE_DIR, datetime.date.today().isoformat() + ".json"), "w") as f:
            f.write(blob)
    except OSError:
        pass
    _anthropic_memo.update(t=now, data=out)
    return out


def _safe(module, name):
    """Call a view module's build(), turning any failure into a named error the UI renders.
    One bad source must never blank a panel silently — an empty payload would read as
    'nothing to report', which is the opposite of what a crash means."""
    if not module:
        return {"error": f"{name} module unavailable"}
    try:
        return module.build()
    except Exception as e:
        return {"error": f"{name}: {type(e).__name__}: {e}"[:300]}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def end_headers(self):  # never serve a stale dashboard from browser cache
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def _send_json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/dashboard":
            try:
                derived = refresh.derive() if refresh else None
            except Exception:
                derived = None  # never let the derive layer take the dashboard down
            return self._send_json({
                "dashboard": load(DASH),
                "derived": derived,
                "pipeline": pipeline_summary(),
                "tasks": tasks_summary(),
                "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
        if path == "/api/board":  # The Board — open work across every source, computed live
            if not board:
                return self._send_json({"items": [], "error": "board module unavailable"})
            try:
                return self._send_json(board.build())
            except Exception as e:  # never let one bad source take the view down
                return self._send_json({"items": [], "error": str(e)[:200]})
        if path == "/api/mode":  # lets the UI render the playground banner
            return self._send_json({"playground": PLAYGROUND, "dataRoot": ROOT if PLAYGROUND else None})
        if path == "/api/finance":  # the financial model, mirrored from the workbook (read-only)
            if not finance_view:
                return self._send_json({"error": "finance module unavailable"})
            try:
                return self._send_json(finance_view.build())
            except Exception as e:
                return self._send_json({"error": f"finance view failed: {e}"})
        if path == "/api/clients":  # one row per engagement — status, money, contract, readiness
            if not clients_view:
                return self._send_json({"clients": [], "error": "clients module unavailable"})
            try:
                return self._send_json(clients_view.build())
            except Exception as e:
                return self._send_json({"clients": [], "error": str(e)[:200]})
        # ---- the Evidence door ----------------------------------------------
        # Each wrapped the same way: a module that fails returns a named error the UI can
        # render, never an empty object that would read as "nothing to report".
        if path == "/api/trust":  # trust ledger + calibration + immune drills
            return self._send_json(_safe(trust_view, "trust"))
        if path == "/api/skills":  # what skills exist, and which have gone quiet
            if not skills_view:
                return self._send_json({"error": "skills module unavailable"})
            return self._send_json(skills_view.skills())
        if path == "/api/search":  # kb — full-text over the repo, ranked by reality level
            # Deliberately NOT a model call: runtime/kb.py is deterministic, sub-second over 7.4 MB,
            # and returns the same answer twice. Search is retrieval, not judgment.
            qs = parse_qs(urlparse(self.path).query)   # parsed here; the shared one is later in do_GET
            q = (qs.get("q", [""])[0] or "").strip()
            if not q:
                return self._send_json({"refused": True, "why": "no query", "hits": []})
            try:
                import importlib.util as _ilu
                _sp = _ilu.spec_from_file_location(
                    "_kb", os.path.join(os.path.dirname(HERE), "runtime", "kb.py"))
                _kb = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_kb)
                lvl = (qs.get("level", [""])[0] or "").strip() or None
                return self._send_json(_kb.search(q, limit=25, level=lvl))
            except Exception as e:
                return self._send_json({"refused": True, "why": f"kb unavailable: {e}", "hits": []})
        if path == "/api/tripwires":  # decisions whose reasoning has expired
            return self._send_json(_safe(tripwires_view, "tripwires"))
        if path == "/api/twin":  # the DRI twin scoreboard
            return self._send_json(_safe(twin_view, "twin"))
        if path == "/api/vacancies":  # work with no owner -> absorb / activate / hire
            return self._send_json(_safe(vacancies_view, "vacancies"))
        if path == "/api/lockin":  # the partner review->lock run (Partners door)
            return self._send_json(_safe(lockin_view, "lockin"))
        if path == "/api/governance":  # the governance half of the Partners door
            return self._send_json(_safe(governance_view, "governance"))
        if path == "/api/advocate":  # the people loop (flywheel §ADVOCATE) on the Partners door
            return self._send_json(_safe(advocate_view, "advocate"))
        if path == "/api/security-model":  # the control set, read from live config (internal only)
            return self._send_json(_safe(secmodel_view, "security-model"))
        if path == "/api/pregolive":  # injected-state simulation per client
            return self._send_json(_safe(pregolive_view, "pregolive"))
        if path == "/api/sleeptime":  # idle-capacity plan + the health gate that guards it
            return self._send_json(_safe(sleeptime_view, "sleeptime"))
        if path == "/api/client-tripwires":  # the client's own decisions, watched for expiry
            return self._send_json(_safe(ctw_view, "client-tripwires"))
        if path == "/api/counterfactual":  # the client's business as it would run without the OS
            return self._send_json(_safe(counterfactual_view, "counterfactual"))
        if path == "/api/wbr":  # controllable inputs + the 6-12 series (format-locked)
            return self._send_json(_safe(wbr_view, "wbr"))
        if path == "/api/northstar":  # the one number + the number each agent owns
            return self._send_json(_safe(northstar_view, "northstar"))
        if path == "/api/kpis":  # the nine KPIs, computed or refused with the precondition named
            return self._send_json(_safe(kpis_view, "kpis"))
        if path == "/api/uptime":  # runtime availability, computed from beats that never arrived
            return self._send_json(_safe(uptime_view, "uptime"))
        if path == "/api/prosecution":  # HQ arguing against its own headline numbers
            return self._send_json(_safe(prosecution_view, "prosecution"))
        if path == "/api/hq-usage":  # what changed since last look + the panel-usefulness audit
            return self._send_json(_safe(hq_usage_view, "hq-usage"))
        if path == "/api/timemachine":  # HQ as of a date + metric blame
            if not tm_view:
                return self._send_json({"error": "timemachine module unavailable"})
            qs = parse_qs(urlparse(self.path).query)
            date = (qs.get("date") or [""])[0] or None
            metric = (qs.get("metric") or ["pipelineValue"])[0]
            if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                return self._send_json({"error": "date must be YYYY-MM-DD"}, 400)
            if not re.fullmatch(r"[A-Za-z]{1,32}", metric):
                return self._send_json({"error": "bad metric"}, 400)
            try:
                return self._send_json(tm_view.build(date, metric))
            except Exception as e:
                return self._send_json({"error": str(e)[:200]})
        if path == "/api/reports":  # loop-report index for the Reports tab
            return self._send_json(reports_index())
        if path == "/api/report":  # one report's markdown (strict dir/date validation)
            payload = report_payload(parse_qs(urlparse(self.path).query))
            if payload is None:
                return self._send_json({"error": "not found"}, 404)
            return self._send_json(payload)
        if path == "/api/instantly":  # outbound metrics (cached 6h; honest when unwired)
            return self._send_json(instantly_metrics())
        if path == "/api/anthropic-cost":  # org model spend (Admin API; cached 6h; honest when unwired)
            return self._send_json(anthropic_cost())
        if path == "/api/goals":  # targets (goals.json) + currents computed live from the CRM
            return self._send_json(goals_payload())
        if path == "/api/todo":  # the Founder's to-do list (Overview panel)
            return self._send_json(todo_doc())
        if path == "/api/melanie":  # status probe: tells the console if the brain/voice are wired
            return self._send_json(melanie.status() if melanie else {"brain": False, "voice": False})
        if path == "/api/melanie/briefing":  # spoken open-the-dashboard briefing
            return self._send_json(melanie.briefing() if melanie else {"text": None, "audio": None, "backend": "unavailable"})
        # Static fallback serves directory=HERE, which also holds melanie.env (live API keys) and
        # *.py — never let those out over HTTP. Serve only the dashboard's own web assets.
        if not _served_ok(path):
            self.send_error(404)
            return
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path == "/api/finance/edit":  # assumption edits -> workbook + pending
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:
                return self._send_json({"error": "too_large"}, 413)
            origin = self.headers.get("Origin")  # cross-origin (CSRF) guard
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"error": "cross_origin_blocked"}, 403)
            try:
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"error": "bad_request"}, 400)
            if not isinstance(body, dict) or not isinstance(body.get("edits"), dict):
                return self._send_json({"error": "bad_request"}, 400)
            try:
                sys.path.insert(0, os.path.join(ROOT, "runtime"))
                import finance_model_edit as fme
                return self._send_json(fme.apply(body["edits"], by=str(body.get("by") or "hq")[:40]))
            except Exception as e:
                return self._send_json({"ok": False, "error": f"edit failed: {e}"}, 500)
        if urlparse(self.path).path == "/api/goals":  # inline target edits from the Goals tab
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:  # anti-DoS
                return self._send_json({"error": "too_large"}, 413)
            origin = self.headers.get("Origin")  # cross-origin (CSRF) guard
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"error": "cross_origin_blocked"}, 403)
            try:
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"error": "bad_request"}, 400)
            if not isinstance(body, dict):
                return self._send_json({"error": "bad_request"}, 400)
            try:
                return self._send_json(goals_save(body))
            except ValueError:
                return self._send_json({"error": "bad_target"}, 400)
            except OSError:
                return self._send_json({"error": "write_failed"}, 500)
        if urlparse(self.path).path == "/api/hq-visit":  # a door was opened; snapshot the company
            if not hq_usage_view:
                return self._send_json({"error": "hq_usage unavailable"}, 503)
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:
                return self._send_json({"error": "too_large"}, 413)
            origin = self.headers.get("Origin")
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"error": "cross_origin_blocked"}, 403)
            try:
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"error": "bad_request"}, 400)
            door = str(body.get("door") or "")
            if not re.fullmatch(r"[a-z][a-z0-9-]{0,30}", door):
                return self._send_json({"error": "bad_door"}, 400)
            try:
                ev = hq_usage_view.record_visit(door, body.get("panels") or [])
                return self._send_json({"recorded": ev["seq"]})
            except Exception as e:
                return self._send_json({"error": str(e)[:200]}, 500)
        if urlparse(self.path).path == "/api/board/assign":  # partner assignment from a Board row
            if not board:
                return self._send_json({"error": "board module unavailable"}, 503)
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:
                return self._send_json({"error": "too_large"}, 413)
            origin = self.headers.get("Origin")  # cross-origin (CSRF) guard
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"error": "cross_origin_blocked"}, 403)
            try:
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"error": "bad_request"}, 400)
            key = str(body.get("key") or "")
            if not re.fullmatch(r"[0-9a-f]{6,20}", key):
                return self._send_json({"error": "bad_key"}, 400)
            to = body.get("to") or None
            try:
                return self._send_json({"assignments": board.save_assignment(key, to,
                                                                             body.get("note") or "")})
            except ValueError:
                return self._send_json({"error": "unknown_partner"}, 400)
            except OSError:
                return self._send_json({"error": "write_failed"}, 500)
        if urlparse(self.path).path == "/api/todo":  # full-list overwrite from the Overview panel
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:  # anti-DoS
                return self._send_json({"error": "too_large"}, 413)
            origin = self.headers.get("Origin")  # cross-origin (CSRF) guard
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"error": "cross_origin_blocked"}, 403)
            try:
                doc = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"error": "bad_request"}, 400)
            if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
                return self._send_json({"error": "bad_request"}, 400)
            try:
                return self._send_json(todo_save(doc))
            except OSError:
                return self._send_json({"error": "write_failed"}, 500)
        if urlparse(self.path).path == "/api/melanie":
            if not melanie:
                return self._send_json({"text": None, "audio": None, "backend": "unavailable"})
            try:
                n = int(self.headers.get("Content-Length", 0))
            except ValueError:
                n = 0
            if n > MAX_BODY:  # anti-DoS
                return self._send_json({"text": None, "audio": None, "backend": "too_large"}, 413)
            origin = self.headers.get("Origin")  # cross-origin (CSRF) guard
            if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                return self._send_json({"text": None, "audio": None, "backend": "cross_origin_blocked"}, 403)
            try:
                req = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send_json({"text": None, "audio": None, "backend": "bad_request"}, 400)
            return self._send_json(melanie.handle(req.get("question", "")))
        self.send_response(404)
        self.end_headers()

    def log_message(self, *a):
        pass


class _Server(socketserver.ThreadingTCPServer):
    # threaded: a slow upstream call (Instantly, melanie) must never stall the 15s dashboard poll
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    with _Server((HOST, PORT), Handler) as httpd:
        print(f"yourco dashboard -> http://{HOST}:{PORT}   (Ctrl+C to stop)")
        httpd.serve_forever()
