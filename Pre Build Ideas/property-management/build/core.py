#!/usr/bin/env python3
"""Property OS — domain core.

Everything that is a *rule* lives here, not in the agents and not in the UI:
storage, the SLA matrix, the triage taxonomy, vendor scoring, lease math,
retention risk, component lifecycle economics, and the autonomy matrix.

Two honesty rules this module enforces for the whole product:
  1. A number that cannot be computed from recorded events is returned as
     None with a `_missing` reason — never estimated and never zero-filled.
  2. Every state change is written to the append-only event log with its
     actor (`agent:<name>` or `human:<id>`) and its autonomy rung. The
     "% automated" figure is COUNTED from that log; it is never asserted.

Stdlib only.
"""
import contextlib, fcntl, json, math, os, threading, time, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("PROPERTYOS_DATA_ROOT", ROOT / "data"))
_LOCK = threading.RLock()

# ---------------------------------------------------------------- time

def now():
    return datetime.now(timezone.utc)

def iso(dt=None):
    return (dt or now()).replace(microsecond=0).isoformat()

def parse(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def hours_between(a, b):
    a, b = parse(a) if isinstance(a, str) else a, parse(b) if isinstance(b, str) else b
    if not a or not b:
        return None
    return (b - a).total_seconds() / 3600.0

def days_until(s):
    d = parse(s)
    return None if not d else (d - now()).days

# ---------------------------------------------------------------- storage

TABLES = ("properties", "units", "tenants", "owners", "vendors", "requests",
          "components", "messages", "approvals", "events", "surveys", "config",
          "charges", "payments", "ledger", "batches", "turnovers",
          "referrals", "inquiries", "prospects")

def _path(table):
    return DATA / f"{table}.json"


_LOCK_DEPTH = threading.local()


@contextlib.contextmanager
def store_lock():
    """Hold this across any load -> modify -> save cycle.

    `load` and `save` each took the RLock individually, which made them
    independently safe and the CYCLE unsafe: under ThreadingHTTPServer, two
    concurrent writers interleaved and the later save clobbered the earlier
    one. Measured before fixing: 8 threads appending 320 events to the
    "append-only" log stored 72 of them. An audit log that loses 77% of its
    writes under two phones is not an audit log.

    Two layers because there are two kinds of concurrency here:
      - the RLock serialises threads inside one process (the HTTP server,
        which also runs agent sweeps in-process via /api/agents/run);
      - the fcntl lock serialises PROCESSES (a cron `agents.py --all` sweep
        against a live server), which a threading lock cannot see.
    Reads stay lock-light: save() writes a tmp file and atomically replaces,
    so a reader never observes a torn file.
    """
    DATA.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        # Re-entrancy guard for the FILE lock. The RLock re-enters fine, but
        # flock does not: a second open() on the lock file is a new file
        # description, and LOCK_EX on it blocks against our OWN outer hold —
        # the same thread deadlocks against itself. Found live: the vendor
        # job endpoint held store_lock and called log_event, which locks
        # again; every vendor action hung the server. Only the outermost
        # frame touches the file lock.
        depth = getattr(_LOCK_DEPTH, "d", 0)
        _LOCK_DEPTH.d = depth + 1
        try:
            if depth == 0:
                with open(DATA / ".lock", "w") as lf:
                    fcntl.flock(lf, fcntl.LOCK_EX)
                    try:
                        yield
                    finally:
                        fcntl.flock(lf, fcntl.LOCK_UN)
            else:
                yield
        finally:
            _LOCK_DEPTH.d = depth

def load(table, default=None):
    p = _path(table)
    if not p.exists():
        return default if default is not None else ([] if table != "config" else {})
    with _LOCK:
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return default if default is not None else ([] if table != "config" else {})

def save(table, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        tmp = _path(table).with_suffix(".tmp")
        tmp.write_text(json.dumps(rows, indent=1))
        tmp.replace(_path(table))

def upsert(table, row, key="id"):
    with store_lock():
        rows = load(table)
        for i, r in enumerate(rows):
            if r.get(key) == row.get(key):
                rows[i] = row
                break
        else:
            rows.append(row)
        save(table, rows)
    return row

def by_id(table, _id):
    for r in load(table):
        if r.get("id") == _id:
            return r
    return None

def nid(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

# ---------------------------------------------------------------- events

def log_event(kind, subject_id, actor, rung=None, detail=None, at=None):
    """Append-only. `actor` is 'agent:<name>' | 'human:<id>' | 'tenant:<id>'.

    `rung` is the autonomy rung the action executed at (R0..R3). Actions taken
    by an agent WITHOUT a rung are a bug — the % automated read depends on it,
    so we record 'R?' rather than silently dropping the row.
    """
    if actor.startswith("agent:") and not rung:
        rung = "R?"
    ev = {"id": nid("ev"), "at": at or iso(), "kind": kind, "subject": subject_id,
          "actor": actor, "rung": rung, "detail": detail or {}}
    with store_lock():
        rows = load("events")
        rows.append(ev)
        save("events", rows)
    return ev

# ---------------------------------------------------------------- the SLA matrix
# Response = time to a committed appointment. Resolve = time to fix.
# These are the industry-standard habitability clocks, not invented numbers;
# P1 is what most state landlord-tenant statutes treat as an emergency repair.

PRIORITIES = {
    "P1": {"label": "Emergency", "respond_h": 1, "resolve_h": 24,
           "examples": "no heat, flood, gas smell, no power, sewage, lockout, broken exterior lock"},
    "P2": {"label": "Urgent", "respond_h": 4, "resolve_h": 72,
           "examples": "no A/C in heat, no hot water, refrigerator out, single-toilet clog"},
    "P3": {"label": "Routine", "respond_h": 24, "resolve_h": 168,
           "examples": "dripping faucet, appliance quirk, slow drain, minor leak"},
    "P4": {"label": "Cosmetic", "respond_h": 72, "resolve_h": 720,
           "examples": "paint scuff, cabinet door, screen tear, caulk"},
}

STATUSES = ("submitted", "assigned", "in_progress", "resolved")
RESOLUTION_KINDS = ("fixed", "deflected", "no_access", "referred")

# ---------------------------------------------------------------- triage taxonomy
# Each entry: trade, default priority, the component it wires to, the guided
# self-fix (if a real one exists), and the median labor the vendor market
# charges. `self_fix` is the deflection lever — the single biggest cost line
# in small-portfolio maintenance is the truck roll that never needed to happen.

CATEGORIES = {
    "no_heat": dict(trade="hvac", priority="P1", component="furnace",
                    self_fix=None, median_cost=285, minutes=90,
                    keywords=["no heat", "heater", "heat isn", "heat doesn", "heat won", "heat not",
                              "furnace", "cold apartment", "freezing", "no warm air", "thermostat"]),
    "no_cooling": dict(trade="hvac", priority="P2", component="ac",
                       self_fix="ac_filter_breaker", median_cost=265, minutes=75,
                       keywords=["no ac", "a/c", "air conditioning", "not cooling", "hot apartment",
                                 "ac isn", "ac doesn", "ac won", "blowing warm", "blowing hot", "no cold air"]),
    "no_hot_water": dict(trade="plumbing", priority="P2", component="water_heater",
                         self_fix="wh_pilot_breaker", median_cost=310, minutes=90,
                         keywords=["no hot water", "water heater", "cold shower", "lukewarm",
                                   "water is cold", "water won't heat", "only cold water"]),
    "leak_active": dict(trade="plumbing", priority="P1", component="plumbing",
                        self_fix=None, median_cost=340, minutes=105,
                        keywords=["flooding", "water everywhere", "gushing", "burst", "pouring"]),
    "leak_slow": dict(trade="plumbing", priority="P3", component="plumbing",
                      self_fix=None, median_cost=190, minutes=60,
                      keywords=["drip", "leaking", "under sink", "small leak", "damp"]),
    "toilet_clog": dict(trade="plumbing", priority="P2", component="plumbing",
                        self_fix="toilet_plunge", median_cost=175, minutes=45,
                        keywords=["toilet", "clog", "won't flush", "overflow"]),
    "drain_slow": dict(trade="plumbing", priority="P3", component="plumbing",
                       self_fix="drain_hair", median_cost=165, minutes=45,
                       keywords=["slow drain", "sink draining", "backing up", "shower drain"]),
    "disposal": dict(trade="plumbing", priority="P3", component="disposal",
                     self_fix="disposal_reset", median_cost=145, minutes=35,
                     keywords=["garbage disposal", "disposal", "humming", "jammed"]),
    "no_power_partial": dict(trade="electrical", priority="P2", component="electrical",
                             self_fix="breaker_gfci", median_cost=210, minutes=50,
                             keywords=["outlet", "no power", "breaker", "outlets dead", "tripped"]),
    "no_power_full": dict(trade="electrical", priority="P1", component="electrical",
                          self_fix=None, median_cost=310, minutes=80,
                          keywords=["power out", "no electricity", "whole unit dark", "no power at all",
                                      "nothing has power", "lights won"]),
    "appliance": dict(trade="appliance", priority="P3", component="appliance",
                      self_fix=None, median_cost=225, minutes=70,
                      keywords=["dishwasher", "oven", "stove", "washer", "dryer", "refrigerator", "fridge"]),
    "lock_door": dict(trade="locksmith", priority="P1", component="doors",
                      self_fix=None, median_cost=195, minutes=45,
                      keywords=["locked out", "lock broken", "lock is broken",
                                "broken lock", "won't latch", "wont latch",
                                "doesn't latch", "won't lock", "can't lock",
                                "door won't", "deadbolt", "key snapped", "key"]),
    "pest": dict(trade="pest", priority="P2", component="unit",
                 self_fix=None, median_cost=175, minutes=60,
                 keywords=["roach", "mice", "rats", "ants", "bed bug", "pest", "bugs"]),
    "smoke_alarm": dict(trade="handyman", priority="P2", component="safety",
                        self_fix="alarm_battery", median_cost=95, minutes=25,
                        keywords=["smoke detector", "chirping", "beeping", "alarm"]),
    "mold_moisture": dict(trade="general", priority="P2", component="unit",
                          self_fix=None, median_cost=420, minutes=120,
                          keywords=["mold", "mildew", "musty", "black spots"]),
    "cosmetic": dict(trade="handyman", priority="P4", component="unit",
                     self_fix=None, median_cost=120, minutes=45,
                     keywords=["paint", "scuff", "cabinet", "blind", "screen", "caulk", "closet door"]),
    "other": dict(trade="handyman", priority="P3", component="unit",
                  self_fix=None, median_cost=160, minutes=50, keywords=[]),
}

# Guided self-fixes. Every one of these is a real, safe, tenant-performable
# action. Anything involving gas, standing water + electricity, or a panel
# beyond the breaker face is deliberately NOT here.
SELF_FIX = {
    "disposal_reset": dict(
        title="The disposal reset button fixes this about half the time",
        seconds=90, avoids=145,
        steps=["Turn the disposal switch OFF. Never put your hand in the drain.",
               "Look under the sink at the bottom of the disposal unit for a small red button.",
               "Press it firmly until it clicks and stays in.",
               "Run cold water, then flip the switch. If it hums but won't turn, stop — we'll send someone."]),
    "breaker_gfci": dict(
        title="Dead outlets are usually a tripped GFCI, not a repair",
        seconds=120, avoids=210,
        steps=["Check outlets in the bathroom, kitchen, garage and outside for a button marked RESET.",
               "Press RESET firmly. Often one GFCI outlet controls several others.",
               "Still dead? Open the breaker panel and look for a switch sitting between ON and OFF.",
               "Push it fully OFF, then fully ON. If it trips again immediately, stop — that's ours."]),
    "wh_pilot_breaker": dict(
        title="Two safe checks before we send a plumber",
        seconds=120, avoids=310,
        steps=["Electric heater: check the breaker panel for a tripped 'water heater' breaker.",
               "Check that nobody turned the heater's thermostat dial down.",
               "If you smell gas at any point, leave the unit and call us immediately — do not relight anything.",
               "We never ask tenants to relight a gas pilot. That's a licensed job."]),
    "ac_filter_breaker": dict(
        title="A clogged filter is the #1 cause of weak A/C",
        seconds=180, avoids=265,
        steps=["Find the return vent (big grille, usually a hallway or ceiling) and pull the filter.",
               "If it's grey and furry, that's your problem. Slide a new one in, arrow pointing toward the duct.",
               "Set the thermostat to COOL and at least 5 degrees below the room temp.",
               "Check the outdoor unit's breaker. If the coil is a block of ice, turn it to FAN only and tell us."]),
    "toilet_plunge": dict(
        title="Try this before we bill a plumber to the property",
        seconds=180, avoids=175,
        steps=["Do not flush again — that's how a clog becomes a flood.",
               "Shut the water off at the oval valve behind the toilet if the bowl is rising.",
               "Use a flange plunger (the kind with a sleeve), seal the drain, and push slowly 10–15 times.",
               "If a second toilet or the tub is also backing up, stop — that's a main line and it's ours."]),
    "drain_hair": dict(
        title="Most slow drains are six inches down",
        seconds=180, avoids=165,
        steps=["Pull the stopper straight up out of the drain.",
               "Use a plastic drain zip tool (we'll mail one free) to pull the hair clog.",
               "Flush with very hot water for 60 seconds.",
               "Please don't use chemical drain opener — it damages the trap and we'll have to replace it."]),
    "alarm_battery": dict(
        title="A chirp is a battery. A steady alarm is an evacuation.",
        seconds=120, avoids=95,
        steps=["If the alarm is sounding continuously, get everyone out and call 911 first.",
               "A single chirp every 30–60 seconds is a low battery.",
               "Twist the unit off its base, swap the 9V, twist back on.",
               "Tell us if the unit itself is over 10 years old — we replace those on our dime."]),
}

# ---------------------------------------------------------------- triage engine

EMERGENCY_WORDS = ["gas", "smoke", "fire", "sparking", "flood", "flooding", "sewage",
                   "no heat", "carbon monoxide", "burst", "electrical shock", "ceiling falling"]

# The systems whose failure makes a unit legally uninhabitable. When the resident
# tells us they cannot use one of these, that is a P1 no matter how mildly they
# worded it — and it must be decided by the RULES, not the model, because this is
# precisely the judgement that has to survive the model being unreachable.
#
# Residents systematically understate: "a bit chilly, the heat doesn't seem to be
# coming on" in February is a P1. The keyword lists above will never be complete
# enough to catch every phrasing, so the tenant's own answer carries the escalation.
HABITABILITY_SYSTEMS = {
    "no_heat": "heat", "no_hot_water": "hot water", "no_power_full": "electricity",
    "no_power_partial": "electricity", "toilet_clog": "a working toilet",
    "leak_active": "containment of running water", "no_cooling": "cooling",
    "lock_door": "a securable door", "mold_moisture": "air safe to breathe",
}
HABITABILITY_HINTS = ["heat", "heater", "furnace", "hot water", "water heater",
                      "power", "electricity", "toilet", "no water", "lock", "door won"]

def classify(text, photo_present=False, answers=None):
    """Deterministic first-pass triage. Returns the category, priority and
    confidence. When ANTHROPIC_API_KEY is set the vision model refines this
    (agents.triage) — but this floor always runs, so the product never depends
    on a model being reachable to route an emergency.
    """
    t = (text or "").lower()
    answers = answers or {}
    # A tie between two categories must resolve to the MORE severe one. This
    # was insertion order, which is arbitrary: "a damp patch and a musty smell"
    # scores equally for leak_slow (P3) and mold_moisture (P2), and the dict
    # happened to list the milder one first. Ambiguity resolves upward, always.
    rank = ["P4", "P3", "P2", "P1"]
    best, score = "other", 0
    for cat, spec in CATEGORIES.items():
        s = sum(3 if k in t else 0 for k in spec["keywords"])
        if s > score or (s == score and s > 0
                         and rank.index(spec["priority"]) > rank.index(CATEGORIES[best]["priority"])):
            best, score = cat, s
    spec = CATEGORIES[best]
    priority = spec["priority"]
    reasons = []
    # Escalators — these override the category default, upward only.
    for w in EMERGENCY_WORDS:
        if w in t:
            priority = "P1"
            reasons.append(f"emergency keyword: '{w}'")
            break
    if answers.get("water_spreading") is True:
        priority = "P1"; reasons.append("tenant reports water spreading")
    if answers.get("habitability") is True:
        system = HABITABILITY_SYSTEMS.get(best)
        if system is None and any(h in t for h in HABITABILITY_HINTS):
            # Category matching failed but the resident named a core system and
            # told us they can't use it. Escalate on their answer, not on our
            # keyword coverage — a miss here is a habitability failure.
            system = "an essential system"
        if system:
            priority = "P1"
            reasons.append(f"resident reports they cannot use {system} — habitability")
        elif priority in ("P3", "P4"):
            priority = "P2"
            reasons.append("resident cannot use a required fixture")
    if answers.get("vulnerable_occupant") is True and priority == "P2":
        priority = "P1"; reasons.append("infant / elderly / medical occupant on file")
    conf = min(0.95, 0.35 + 0.12 * score + (0.15 if photo_present else 0))
    return {"category": best, "priority": priority, "confidence": round(conf, 2),
            "reasons": reasons or [f"keyword match on {best}"],
            "trade": spec["trade"], "component_kind": spec["component"],
            "self_fix": spec["self_fix"], "est_cost": spec["median_cost"],
            "est_minutes": spec["minutes"], "source": "rules"}

def sla_due(request):
    p = PRIORITIES.get(request.get("priority", "P3"), PRIORITIES["P3"])
    sub = parse(request.get("submitted_at"))
    if not sub:
        return {}
    return {"respond_by": iso(sub + timedelta(hours=p["respond_h"])),
            "resolve_by": iso(sub + timedelta(hours=p["resolve_h"]))}

# ------------------------------------------------------------- availability
#
# The resident's stated windows for a vendor visit, captured at intake for
# "only when I'm home" / "call me first" requests. Three honest bounds:
#   - it is a STATEMENT, not a standing consent to enter. It is timestamped
#     and goes stale after AVAILABILITY_STALE_DAYS; stale windows are shown
#     for context but never auto-confirm and never read as permission.
#   - "anytime" residents are never asked (their availability is irrelevant)
#     and P1 emergencies skip it (entry is now, not Tuesday).
#   - matching is deterministic: a vendor picking one of the resident's own
#     windows is a match; anything else is a proposal the resident answers.

AVAILABILITY_STALE_DAYS = 14
AVAILABILITY_CHIPS = ("Weekday mornings (8-12)", "Weekday afternoons (12-5)",
                      "Weekday evenings (5-8)", "Weekends")


def availability_state(request, ref=None):
    ref = ref or now()
    av = request.get("availability") or {}
    windows = [w for w in (av.get("windows") or []) if w]
    if not windows:
        return {"state": "none", "windows": [],
                "note": "no availability on file — scheduling starts as a proposal either way"}
    stated = parse(av.get("stated_at"))
    if not stated:
        return {"state": "stale", "windows": windows, "stated_at": None,
                "note": "availability with no timestamp is treated as stale — never as consent"}
    age = (ref - stated).days
    if age > AVAILABILITY_STALE_DAYS:
        return {"state": "stale", "windows": windows, "stated_at": av.get("stated_at"),
                "age_days": age,
                "note": f"stated {age} days ago — stale. Reconfirm; stale availability is "
                        f"never treated as consent to enter"}
    return {"state": "fresh", "windows": windows, "stated_at": av.get("stated_at"),
            "age_days": age,
            "note": "the resident's own windows — a vendor picking one confirms instantly"}


def window_match(window, request, ref=None):
    """True only when `window` is verbatim one of the resident's FRESH stated
    windows. Deterministic on purpose — fuzzy overlap is how somebody gets
    scheduled into a slot they never offered."""
    st = availability_state(request, ref)
    return st["state"] == "fresh" and (window or "").strip() in st["windows"]


def sla_state(request):
    """on_track | at_risk | breached | met. at_risk = past 75% of the clock."""
    if request.get("status") == "resolved":
        due = request.get("resolve_by")
        end = request.get("resolved_at")
        if not due or not end:
            return "met"
        return "met" if parse(end) <= parse(due) else "breached"
    due = parse(request.get("resolve_by"))
    sub = parse(request.get("submitted_at"))
    if not due or not sub:
        return "on_track"
    total = (due - sub).total_seconds()
    gone = (now() - sub).total_seconds()
    if gone > total:
        return "breached"
    return "at_risk" if total and gone / total > 0.75 else "on_track"

# ---------------------------------------------------------------- vendor scoring
# The assignment decision is a market, not a phone tree. Five signals, each
# earned from recorded jobs. A vendor with < MIN_JOBS has no score and is
# labelled 'unrated' — we do not let a small sample masquerade as a rating.

MIN_JOBS_FOR_SCORE = 5

def vendor_scorecard(vendor, requests):
    jobs = [r for r in requests if r.get("vendor_id") == vendor["id"] and r.get("status") == "resolved"]
    n = len(jobs)
    if n < MIN_JOBS_FOR_SCORE:
        return {"vendor_id": vendor["id"], "jobs": n, "rated": False,
                "_missing": f"needs {MIN_JOBS_FOR_SCORE} resolved jobs, has {n}"}
    ftf = [j for j in jobs if not j.get("reopened")]
    resp = [h for h in (hours_between(j.get("assigned_at"), j.get("started_at")) for j in jobs) if h is not None]
    cycle = [h for h in (hours_between(j.get("assigned_at"), j.get("resolved_at")) for j in jobs) if h is not None]
    rat = [j["tenant_rating"] for j in jobs if j.get("tenant_rating")]
    met = [j for j in jobs if j.get("resolve_by") and j.get("resolved_at")
           and parse(j["resolved_at"]) <= parse(j["resolve_by"])]
    costs = [j.get("actual_cost") for j in jobs if j.get("actual_cost")]
    sc = {
        "vendor_id": vendor["id"], "jobs": n, "rated": True,
        "first_time_fix": round(len(ftf) / n, 3),
        "sla_hit": round(len(met) / n, 3) if jobs else None,
        "median_response_h": round(median(resp), 1) if resp else None,
        "median_cycle_h": round(median(cycle), 1) if cycle else None,
        "tenant_rating": round(sum(rat) / len(rat), 2) if rat else None,
        "avg_invoice": round(sum(costs) / len(costs)) if costs else None,
    }
    # Composite 0–100. Weights are stated, not hidden: a job done once and
    # done fast is worth more than a job done cheap, because the re-dispatch
    # is what actually costs the portfolio.
    parts, weights = [], []
    if sc["first_time_fix"] is not None:
        parts.append(sc["first_time_fix"] * 100); weights.append(0.35)
    if sc["sla_hit"] is not None:
        parts.append(sc["sla_hit"] * 100); weights.append(0.25)
    if sc["tenant_rating"] is not None:
        parts.append(sc["tenant_rating"] / 5 * 100); weights.append(0.25)
    if sc["median_response_h"] is not None:
        parts.append(max(0, 100 - sc["median_response_h"] * 4)); weights.append(0.15)
    sc["score"] = round(sum(p * w for p, w in zip(parts, weights)) / sum(weights)) if weights else None
    return sc


def vendor_recent_reviews(vendor_id, requests, limit=3):
    """The residents' own words about this vendor's finished work — ratings the
    tenant gave at the check-back, newest first. Only real reviews: a job
    without a rating contributes nothing, and nothing is summarized for them."""
    rows = [r for r in requests
            if r.get("vendor_id") == vendor_id and r.get("status") == "resolved"
            and r.get("tenant_rating")]
    rows.sort(key=lambda r: r.get("rated_at") or r.get("resolved_at") or "", reverse=True)
    return [{"rating": r["tenant_rating"], "comment": (r.get("tenant_comment") or "")[:280],
             "title": r.get("title"), "at": r.get("rated_at") or r.get("resolved_at")}
            for r in rows[:limit]]

def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2

def price_anomaly(request, requests):
    """Flags a quote that is out of family for its own job class. Uses the
    portfolio's own median for that category — not a national benchmark —
    because local labor rates make national benchmarks useless and wrong.
    """
    q = request.get("quote")
    if not q:
        return None
    peers = [r.get("actual_cost") or r.get("quote") for r in requests
             if r.get("category") == request.get("category") and r["id"] != request["id"]]
    peers = [p for p in peers if p]
    if len(peers) < 6:
        return {"flag": False, "_missing": f"only {len(peers)} comparable jobs on file, need 6"}
    med = median(peers)
    ratio = q / med if med else None
    return {"flag": bool(ratio and ratio >= 1.6), "quote": q, "median": round(med),
            "ratio": round(ratio, 2) if ratio else None, "n": len(peers),
            "note": "quote is %.0f%% of the portfolio median for this job class" % (ratio * 100) if ratio else None}

# ---------------------------------------------------------------- lease math

def lease_window(unit, days=60):
    end = unit.get("lease", {}).get("end")
    d = days_until(end)
    return d if d is not None and d <= days else None

def renewal_risk(unit, requests, surveys):
    """Non-renewal risk, 0–100, from maintenance telemetry — not a survey.

    This is the piece no small-portfolio product does. Turnover is the largest
    controllable line in the P&L (make-ready + vacancy + leasing fee), and the
    signal that predicts it is sitting in the ticket history months before the
    notice arrives. Every input is a recorded event; the drivers are returned
    so a manager can act on the cause, not the score.
    """
    uid = unit["id"]
    rs = [r for r in requests if r.get("unit_id") == uid]
    if not rs:
        return {"unit_id": uid, "score": None,
                "_missing": "no maintenance history for this unit — risk is unscored, not low",
                "drivers": [], "silent": True}
    recent = [r for r in rs if (parse(r["submitted_at"]) or now()) > now() - timedelta(days=365)]
    drivers, score = [], 0

    breached = [r for r in recent if r.get("sla_breached")]
    if breached:
        pts = min(30, 8 * len(breached))
        score += pts
        drivers.append({"factor": "SLA breaches in the last year", "n": len(breached), "points": pts})

    reopened = [r for r in recent if r.get("reopened")]
    if reopened:
        pts = min(20, 10 * len(reopened))
        score += pts
        drivers.append({"factor": "Requests that came back after 'resolved'", "n": len(reopened), "points": pts})

    open_now = [r for r in rs if r.get("status") != "resolved"]
    stale = [r for r in open_now if (hours_between(r["submitted_at"], iso()) or 0) > 336]
    if stale:
        pts = min(20, 10 * len(stale))
        score += pts
        drivers.append({"factor": "Open more than 14 days right now", "n": len(stale), "points": pts})

    rated = [r.get("tenant_rating") for r in recent if r.get("tenant_rating")]
    if rated:
        avg = sum(rated) / len(rated)
        if avg < 3.5:
            pts = int((3.5 - avg) * 14)
            score += pts
            drivers.append({"factor": "Average repair rating below 3.5", "n": round(avg, 1), "points": pts})

    if len(recent) >= 6:
        pts = min(15, 3 * (len(recent) - 5))
        score += pts
        drivers.append({"factor": "High request volume — the unit itself is the problem",
                        "n": len(recent), "points": pts})

    # Late rent is the strongest move-out predictor the model previously did
    # not ingest. Counted from real payment rows, never from a vibe.
    try:
        import money as _money
        lh = _money.late_history(unit.get("tenant_id"))
        if lh["late"] >= 2:
            pts = min(18, 6 * lh["late"])
            score += pts
            drivers.append({"factor": "Late rent payments in the last year",
                            "n": lh["late"], "points": pts})
        if lh["missed"] >= 1:
            pts = min(30, 15 * lh["missed"])
            score += pts
            drivers.append({"factor": "Missed rent charges", "n": lh["missed"], "points": pts})
    except Exception:
        pass   # money store absent (old seeds) — risk model runs without it

    sv = [s for s in surveys if s.get("unit_id") == uid]
    if sv:
        last = sorted(sv, key=lambda s: s["at"])[-1]
        if last.get("renew_intent") == "no":
            score += 35
            drivers.append({"factor": "Tenant stated they do not intend to renew", "n": 1, "points": 35})
        elif last.get("renew_intent") == "unsure":
            score += 15
            drivers.append({"factor": "Tenant unsure about renewing", "n": 1, "points": 15})

    return {"unit_id": uid, "score": min(100, score), "drivers": drivers,
            "band": "high" if score >= 45 else "watch" if score >= 20 else "stable",
            "basis": f"{len(recent)} requests in the trailing 12 months"}

def silent_units(units, requests, months=18):
    """A unit with no requests for a year and a half is not a happy unit by
    default — it is an unmeasured one. Two very different things hide here:
    a genuinely trouble-free unit, and a tenant who stopped asking (often
    while damage accumulates, which surfaces at move-out as a deposit fight).
    We surface it as a question, never as a verdict.
    """
    cutoff = now() - timedelta(days=30 * months)
    out = []
    for u in units:
        if not u.get("tenant_id"):
            continue
        rs = [r for r in requests if r.get("unit_id") == u["id"]]
        last = max((parse(r["submitted_at"]) for r in rs), default=None)
        moved = parse((by_id("tenants", u["tenant_id"]) or {}).get("move_in"))
        occupied_days = (now() - moved).days if moved else None
        if occupied_days and occupied_days > 30 * months and (last is None or last < cutoff):
            out.append({"unit_id": u["id"], "label": u["label"], "property_id": u["property_id"],
                        "last_request": iso(last) if last else None,
                        "occupied_days": occupied_days,
                        "question": "No request in %d+ months. Trouble-free, or has this tenant stopped asking?" % months})
    return out

# ---------------------------------------------------------------- component economics

COMPONENT_LIFE = {  # expected service life in years, and replacement cost band
    "water_heater": dict(life=11, replace=1450, label="Water heater"),
    "furnace": dict(life=18, replace=4200, label="Furnace"),
    "ac": dict(life=15, replace=5100, label="A/C condenser"),
    "disposal": dict(life=9, replace=320, label="Garbage disposal"),
    "appliance": dict(life=13, replace=780, label="Appliance"),
    "roof": dict(life=25, replace=11000, label="Roof section"),
    "plumbing": dict(life=40, replace=3800, label="Supply/drain run"),
    "electrical": dict(life=35, replace=2600, label="Panel/circuit"),
    "doors": dict(life=20, replace=650, label="Door/lock set"),
    "safety": dict(life=10, replace=110, label="Alarm"),
    "unit": dict(life=0, replace=0, label="Unit (no component)"),
}

# Preventive maintenance intervals per component kind. Interval from the last
# PM (or install) in days; each becomes a routine work order through the same
# dispatch market as reactive work. Deliberately short list — three real,
# code-or-economics-backed items beat a wall of theoretical ones.
PM_SCHEDULE = {
    "ac":           dict(task="Replace HVAC filter; inspect condensate line", every_days=120,
                         category="no_cooling", priority="P4", est=45),
    "furnace":      dict(task="Replace furnace filter; test ignition before season", every_days=180,
                         category="no_heat", priority="P4", est=45),
    "water_heater": dict(task="Flush water heater; inspect anode and TPR valve", every_days=365,
                         category="no_hot_water", priority="P4", est=90),
    "safety":       dict(task="Smoke/CO detector test and battery replacement (code-required)", every_days=365,
                         category="smoke_alarm", priority="P3", est=25),
}

REPLACE_RATIO = 0.55   # repair spend past 55% of replacement cost = stop repairing
LIFE_RATIO = 0.85      # or past 85% of expected life with any repair history

def component_verdict(comp, requests):
    """repair | plan_replacement | replace_now — with the arithmetic shown.

    A property manager who tells an owner 'your water heater is old' loses.
    One who says 'you have spent $840 repairing a $1,450 heater that is 3
    years past its service life, and the next failure is a 2am flood claim'
    gets the capital approved. That is the entire feature.
    """
    spec = COMPONENT_LIFE.get(comp.get("kind"), COMPONENT_LIFE["unit"])
    if not spec["life"]:
        return None
    # Preventive orders reference the component but are NOT evidence of
    # failure — counting a scheduled filter change as a "repair" pushed
    # healthy components over the replace-now line the sweep after PM
    # scheduling began. Only reactive work argues for replacement.
    jobs = [r for r in requests if r.get("component_id") == comp["id"]
            and not r.get("preventive")]
    spend = sum(r.get("actual_cost") or 0 for r in jobs)
    installed = parse(comp.get("installed"))
    age = (now() - installed).days / 365.25 if installed else None
    if age is None:
        return {"component_id": comp["id"], "verdict": "unknown",
                "_missing": "no install date on file — age cannot be computed",
                "action": "Capture the install date at the next vendor visit."}
    life_used = age / spec["life"]
    spend_ratio = spend / spec["replace"] if spec["replace"] else 0
    verdict = "repair"
    why = []
    if spend_ratio >= REPLACE_RATIO:
        verdict = "replace_now"
        why.append(f"${spend:,.0f} of repairs is {spend_ratio:.0%} of the ${spec['replace']:,} replacement cost")
    if life_used >= 1.0 and len(jobs) >= 2:
        verdict = "replace_now"
        why.append(f"{age:.1f} years old against an {spec['life']}-year service life, with {len(jobs)} repairs")
    elif life_used >= LIFE_RATIO and verdict == "repair":
        verdict = "plan_replacement"
        why.append(f"{age:.1f} of {spec['life']} expected years — budget it before it fails")
    return {"component_id": comp["id"], "unit_id": comp["unit_id"], "kind": comp["kind"],
            "label": spec["label"], "age_years": round(age, 1), "life_years": spec["life"],
            "repairs": len(jobs), "repair_spend": round(spend), "replace_cost": spec["replace"],
            "life_used": round(life_used, 2), "spend_ratio": round(spend_ratio, 2),
            "verdict": verdict, "why": why,
            "next_failure_exposure": spec["replace"] + (900 if comp["kind"] in ("water_heater", "plumbing") else 0)}

# ---------------------------------------------------------------- turnover
# notice -> moveout_scheduled -> inspected -> make_ready -> ready -> leased
# The pipeline exists to MEASURE the two numbers turn_cost currently assumes:
# days vacant, and make-ready spend. Assumptions on screen become measurements.

TURNOVER_STATES = ("notice", "moveout_scheduled", "inspected", "make_ready",
                   "ready", "leased")

MAKEREADY_TEMPLATE = [
    ("Full clean and re-key", "cosmetic", 180),
    ("Paint touch-up walls and trim", "cosmetic", 260),
    ("Carpet/floor clean or repair", "cosmetic", 220),
    ("Test every appliance, smoke/CO detectors", "appliance", 90),
]


def measured_vacancy(turnovers=None):
    """Median days vacant from COMPLETED turnovers. Below 3 completions the
    answer is the assumption, said out loud — never a median of one."""
    done = [t for t in (turnovers if turnovers is not None else load("turnovers"))
            if t.get("state") == "leased" and t.get("moved_out") and t.get("new_lease_start")]
    days = sorted(max(0, (parse(t["new_lease_start"]) - parse(t["moved_out"])).days)
                  for t in done)
    if len(days) < 3:
        return {"days": None, "n": len(days),
                "_missing": f"only {len(days)} completed turnovers — need 3 to state a "
                            "measured vacancy; the 32-day assumption applies until then"}
    m = days[len(days) // 2]
    return {"days": m, "n": len(days),
            "basis": f"median of {len(days)} completed turnovers, measured move-out to new lease start"}


# ---------------------------------------------------------------- the autonomy matrix
# Straight port of the house standard: the default trajectory of every action
# is full autonomy, earned per-action on evidence. R1 is the floor for
# anything with money, legal or entry consequences.
#
#   R0 propose only     — drafts, never acts
#   R1 approval gate    — acts on a human click
#   R2 notify-and-act   — acts, tells the human, reversible
#   R3 full autonomy    — acts silently, logged

AUTONOMY = {
    "triage_classify":        dict(rung="R3", reason="wrong guess costs a re-route, not money; corrected by the manager in one click"),
    "triage_request_photo":   dict(rung="R3", reason="asking the tenant a clarifying question is free and reversible"),
    "offer_self_fix":         dict(rung="R3", reason="only from the vetted SELF_FIX list; every card ends in an escape hatch to a real dispatch"),
    "assign_vendor":          dict(rung="R2", reason="reversible until the vendor confirms; manager is notified on every assignment"),
    "escalate_backup_vendor": dict(rung="R2", reason="SLA clock is objective; a late vendor being replaced is the intended behaviour"),
    "schedule_appointment":   dict(rung="R2", reason="tenant confirms the slot themselves — the human in the loop is the tenant"),
    "confirm_schedule_in_window": dict(rung="R2", reason="the resident stated the window and the vendor picked that exact window — both parties already said yes; confirming is recording an agreement, not making a decision"),
    "propose_schedule_outside_window": dict(rung="R2", reason="a window the resident never offered is a question, not a booking — it goes to the resident to answer, and nothing is scheduled until they do"),
    "approve_spend_under":    dict(rung="R2", reason="under the owner's standing per-job limit, which the owner set", limit=400),  # 400 is the fallback when an owner has set none
    "approve_spend_over":     dict(rung="R1", reason="above the owner's limit — a human approves, always"),
    # The emergency carve-out. A P1 is a habitability failure, and the clock on
    # it outranks the approval queue: management agreements delegate emergency
    # remediation up to a stated cap precisely so the repair happens first and
    # the price argument happens afterwards. The demo board showed why this
    # exists — a P1 lock-out sat breached for five days "awaiting owner
    # approval" over a $412 quote. Notice to the owner is sent the moment the
    # spend is committed; that notice is what makes this R2 and not R3. Above
    # the emergency cap it drops to R1 like everything else, because "emergency"
    # is a reason to move fast, not a blank cheque.
    "approve_spend_emergency": dict(rung="R2", reason="a P1 habitability clock outranks the approval queue — the owner's agreement delegates emergency remediation up to their emergency cap, with notice the moment it is committed", limit=2500),
    "message_tenant":         dict(rung="R2", reason="templated status comms; anything non-template drops to R1"),
    "message_tenant_custom":  dict(rung="R1", reason="free-text to a resident carries fair-housing exposure — drafted, never sent"),
    "message_owner":          dict(rung="R2", reason="reporting, not commitments"),
    "legal_notice":           dict(rung="R0", reason="entry notices, lease violations, non-renewals: an agent NEVER sends these. Draft only."),
    "renewal_offer":          dict(rung="R1", reason="a price commitment to a resident — manager sends"),
    "capital_recommendation": dict(rung="R0", reason="owner capital is the owner's call; the agent brings arithmetic, not a decision"),
    "close_request":          dict(rung="R2", reason="only after the tenant confirms the fix; without confirmation it stays open"),
    "reopen_request":         dict(rung="R3", reason="reopening is always the safe direction"),

    # --- the money loop. The one rule above all: software here accounts for
    #     money and prepares movement; it NEVER moves money. execute_payment is
    #     R0 permanently — like legal_notice, not because a model couldn't
    #     format an ACH file, but because moving other people's money is not an
    #     agent's decision, and no eval streak ever promotes it.
    "post_rent_charge":       dict(rung="R3", reason="derived directly from the signed lease terms; an error is corrected by adjustment, never by discretion"),
    "rent_reminder":          dict(rung="R2", reason="templated, dated, factual — the resident already knows the rent is due; free-text stays R1 via message_tenant_custom"),
    "delinquency_notice":     dict(rung="R1", reason="a firm notice changes the relationship's tone — a human sends it"),
    "payment_plan_proposal":  dict(rung="R1", reason="restructuring what a resident owes is a commitment — a human approves the terms"),
    "legal_referral":         dict(rung="R0", reason="referring a resident for collection or eviction is NEVER automated. Drafted for counsel, full stop"),
    "match_invoice":          dict(rung="R2", reason="arithmetic against the approved quote, inside a stated tolerance; outside it a human reviews"),
    "issue_statement":        dict(rung="R2", reason="the statement is the ledger grouped by month — reporting, not a commitment"),
    "take_mgmt_fee":          dict(rung="R2", reason="the fee percentage is in the signed management agreement; the arithmetic is shown on the statement"),
    "draft_payment_batch":    dict(rung="R2", reason="a DRAFT of who is owed what, floored by each owner's reserve — nothing moves until a human executes at the bank"),
    "execute_payment":        dict(rung="R0", reason="software never moves money here. A human executes at the bank and records that they did — permanently, like legal_notice"),
    "deposit_disposition":    dict(rung="R0", reason="a deposit itemization is a legal document on a state-statutory clock — drafted with the evidence attached, sent by a human"),

    # --- turnover + prevention
    "open_turnover":          dict(rung="R2", reason="a notice-to-vacate starts a measured clock; opening the pipeline is bookkeeping"),
    "create_makeready_tasks": dict(rung="R2", reason="template tasks from the make-ready checklist, dispatched through the same vendor market as everything else"),
    "schedule_preventive":    dict(rung="R3", reason="a filter change on a stated interval is the cheapest repair there is; skipping it is the expensive decision"),

    # --- growth intake. Two hard lines, both permanent:
    #     1. First-touch outreach to a referred owner is a human's call — the
    #        referral is a name, not consent to be contacted by software.
    #     2. NOTHING here ever evaluates a housing applicant. prospect_screening
    #        is R0 like legal_notice — except there is not even a draft to gate:
    #        growth.prospect_score() refuses by construction, and inquiries are
    #        worked strictly in the order received. Sameness is the fairness
    #        control, and it is the only screening this software will ever do.
    "record_referral":        dict(rung="R3", reason="bookkeeping — someone handed us a name; recording it changes nothing for anyone"),
    "referral_outreach":      dict(rung="R1", reason="the first touch to a referred owner is a relationship moment and a consent question — drafted, a human sends"),
    "acknowledge_inquiry":    dict(rung="R2", reason="the identical templated receipt every prospect gets — the sameness IS the fairness control; anything individualized is reply_inquiry"),
    "reply_inquiry":          dict(rung="R1", reason="free-text to a housing applicant carries maximum fair-housing exposure — drafted, never sent"),
    "prospect_screening":     dict(rung="R0", reason="software NEVER scores, ranks, or screens a housing applicant — permanently, like legal_notice. Inquiries are worked in the order received, full stop"),
    "rotate_share_link":      dict(rung="R2", reason="rotating the public one-pager link revokes the old one — reversible by rotating again"),

    # --- the Growth module (pipeline.py) — owner-prospect pipeline. One action
    #     is conspicuously ABSENT: there is no send action at any rung, because
    #     no send rail exists in v1. Every outbound message is drafted here and
    #     sent by a human from their own mailbox; building a send rail is a
    #     counsel-gated v2 decision (TCPA/CAN-SPAM/DNC), not a config flag.
    #     The test suite pins the absence.
    "import_referral":        dict(rung="R3", reason="the referral is already recorded in the ops module; mirroring it into the pipeline is bookkeeping"),
    "research_prospect":      dict(rung="R2", reason="assembling recorded facts into a brief; a wrong fact costs an edit, not a relationship"),
    "draft_first_touch":      dict(rung="R1", reason="first contact is a relationship moment and a consent question — drafted, a human sends, forever"),
    "draft_follow_up":        dict(rung="R1", reason="same exposure as the first touch — the cadence is automated, the words are approved"),
    "nag_human_on_cadence":   dict(rung="R2", reason="reminding the principal costs nothing and IS the discipline that wins pipelines"),
    "advance_prospect_stage": dict(rung="R2", reason="reversible bookkeeping, notified; contacted-and-beyond only moves on a human's say-so"),
    "draft_proposal":         dict(rung="R0", reason="a price + terms commitment — the principal's alone, like capital_recommendation. Pricing is never filled in by software"),
    "update_referrer":        dict(rung="R1", reason="telling an owner what became of their introduction — a human sends it"),
    "scaffold_won_client":    dict(rung="R2", reason="creating the ops-module records for a SIGNED client; reversible, and every default it sets is flagged for onboarding"),
    # Prospecting (added 2026-08-17 — the module is not referral-only; it
    # sources and works cold prospects too, with the same human-sends line).
    "import_target_list":     dict(rung="R2", reason="a sourced list widens who we may contact — imported with its provenance recorded, deduped, opt-outs honored, and the human notified"),
    "record_do_not_contact":  dict(rung="R3", reason="honoring an opt-out is always the safe direction; it is permanent and every import and draft respects it"),
    "rest_prospect":          dict(rung="R2", reason="after the touch cap with no reply, the cadence STOPS — persistence past silence is how outreach becomes spam; a human may revive deliberately"),
}

def rung_for(action, amount=None, limit=None):
    """`limit` is the OWNER's standing per-job limit for this property.

    It used to be ignored: the spend gate compared against the constant in
    AUTONOMY, so an owner who set a $250 limit still had $399 jobs approved
    without them. The owner-configurable limit was decorative. Pass it, and the
    constant becomes what it should have been all along — the fallback for an
    owner who never set one.
    """
    spec = AUTONOMY.get(action)
    if not spec:
        return {"rung": "R1", "reason": "unknown action class defaults to the approval gate"}
    if action in ("approve_spend_under", "approve_spend_emergency") and amount is not None:
        cap = spec.get("limit", 0) if limit is None else limit
        if amount > cap:
            over = dict(AUTONOMY["approve_spend_over"], action="approve_spend_over",
                        limit=cap)
            if action == "approve_spend_emergency":
                over["reason"] = ("above even the owner's emergency authority — "
                                  "the one approval a human must make at P1 speed")
            return over
    return dict(spec, action=action, limit=spec.get("limit") if limit is None else limit)

def automation_rate(events, window_days=90):
    """The honest % automated: of the actions that MOVE work, what share ran
    without a human touching them. Counted from the event log.

    Deliberately excludes tenant-originated events — a tenant filing a request
    is not the OS automating anything, and counting it would inflate the number
    to meaninglessness, which is exactly what vendor 'automation' claims do.
    """
    cutoff = now() - timedelta(days=window_days)
    rows = [e for e in events if (parse(e["at"]) or now()) >= cutoff]
    moving = [e for e in rows if e["kind"] in MOVING_KINDS]
    if len(moving) < 30:
        return {"rate": None, "_missing": f"only {len(moving)} pipeline-moving actions in {window_days} days; need 30 to state a rate"}
    auto = [e for e in moving if e["actor"].startswith("agent:") and e.get("rung") in ("R2", "R3")]
    gated = [e for e in moving if e["actor"].startswith("agent:") and e.get("rung") in ("R0", "R1")]
    human = [e for e in moving if e["actor"].startswith("human:")]
    return {"rate": round(len(auto) / len(moving), 3), "moving": len(moving),
            "autonomous": len(auto), "agent_gated": len(gated), "human_originated": len(human),
            "window_days": window_days,
            "note": "counted from the event log; tenant-originated events excluded by design"}

MOVING_KINDS = {"triaged", "assigned", "reassigned", "scheduled", "started", "resolved",
                "closed", "reopened", "escalated", "deflected", "spend_approved",
                "message_sent", "renewal_offered", "vendor_swapped",
                "charge_posted", "invoice_matched", "statement_issued",
                "batch_drafted", "batch_executed", "payment_recorded",
                "pm_scheduled", "turnover_advanced", "job_accepted", "job_completed"}

# ---------------------------------------------------------------- portfolio reads

def open_requests(requests=None):
    return [r for r in (requests if requests is not None else load("requests")) if r.get("status") != "resolved"]

def avg_resolution_hours(requests=None, days=90, priority=None):
    rs = requests if requests is not None else load("requests")
    cutoff = now() - timedelta(days=days)
    done = [r for r in rs if r.get("status") == "resolved" and r.get("resolved_at")
            and (parse(r["resolved_at"]) or now()) >= cutoff
            and (priority is None or r.get("priority") == priority)]
    hrs = [h for h in (hours_between(r["submitted_at"], r["resolved_at"]) for r in done) if h is not None]
    if len(hrs) < 5:
        return {"hours": None, "n": len(hrs),
                "_missing": f"only {len(hrs)} resolved requests in {days} days; need 5 for an average worth reporting"}
    return {"hours": round(sum(hrs) / len(hrs), 1), "median": round(median(hrs), 1),
            "n": len(hrs), "window_days": days, "priority": priority or "all"}

def deflection_savings(requests=None, days=90):
    rs = requests if requests is not None else load("requests")
    cutoff = now() - timedelta(days=days)
    d = [r for r in rs if r.get("resolution_kind") == "deflected"
         and (parse(r.get("resolved_at") or r["submitted_at"]) or now()) >= cutoff]
    saved = sum(CATEGORIES.get(r.get("category"), CATEGORIES["other"])["median_cost"] for r in d)
    total = [r for r in rs if (parse(r["submitted_at"]) or now()) >= cutoff]
    return {"deflected": len(d), "of_total": len(total),
            "rate": round(len(d) / len(total), 3) if total else None,
            "avoided_cost": saved, "window_days": days,
            "basis": "each avoided dispatch valued at the portfolio median for its job class"}
