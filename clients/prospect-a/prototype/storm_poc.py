#!/usr/bin/env python3
"""
yourco · Storm Verification Engine — Prospect A (Roofing, Florida)

Pulls storm data from MULTIPLE sources, cross-verifies for agreement, scores
confidence, picks a recommended ACTION (canvass / dispatch / standby), and emits
a Nick-approves -> broadcast-to-roofers alert.

SOURCE REGISTRY (edit SOURCES to add/swap — when Nick names the sites he trusts,
add an adapter here and flip enabled=True):

  live now (free):
    · IEM Local Storm Reports   structured NWS ground-truth reports (hail size,
                                wind, tornado) w/ county + lat/lon  [primary]
    · NOAA SPC Storm Reports    national compiled storm reports        [corroborate]
    · NWS Active Alerts         official forecaster/radar warnings     [corroborate]
  ready to connect (needs API key):
    · HailTrace                 hail-specific, radar-verified, roofer-grade
    · Tomorrow.io               broad severe-weather API (forecast + nowcast)

Verification is the moat: a storm is HIGH confidence only when independent
signals agree (>=2 ground reports, or a report + an official NWS warning).

Usage:  python3 storm_poc.py          # last 10 days, Florida
        DAYS=14 STATE=FL python3 storm_poc.py
"""
import csv, io, json, os, re, urllib.request, urllib.parse
from datetime import date, timedelta
from collections import defaultdict

STATE     = os.environ.get("STATE", "FL").upper()
DAYS      = int(os.environ.get("DAYS", "10"))
HAIL_MIN  = float(os.environ.get("HAIL_MIN", "0.75"))  # inches — Nick's threshold (>3/4")
WIND_MIN  = float(os.environ.get("WIND_MIN", "55"))    # mph — Nick's threshold
UA        = {"User-Agent": "StormVerified/1.0 (yourco; https://yourco.com; founder@yourco.example.com)"}

# ------- source registry (the swap point) -------
SOURCES = [
    {"key": "iem",       "label": "NOAA Local Storm Reports", "tier": "free", "enabled": True,
     "note": "NOAA ground truth — the insurance source of record (hail size, wind, tornado + county/lat-lon)"},
    {"key": "spc",       "label": "NOAA SPC (national)",      "tier": "free", "enabled": True,
     "note": "NOAA national compiled storm reports — corroboration"},
    {"key": "nws",       "label": "NWS Live Alerts",          "tier": "free", "enabled": True,
     "note": "official forecaster/radar warnings — the speed layer"},
    {"key": "mesh",      "label": "NOAA MRMS MESH (radar hail)", "tier": "free",
     "enabled": os.environ.get("MESH") == "1",
     "note": "radar-derived max hail size, keyless — the HailTrace replacement; needs pygrib on the host, then MESH=1 (see mrms_mesh.py / DATA-SOURCES.md)"},
    # Nick's data sources (paid keys approved 2026-07-03). Each auto-enables when
    # its key/creds are present in the environment.
    {"key": "xweather", "label": "Xweather", "tier": "premium",
     "enabled": bool(os.environ.get("XWEATHER_CLIENT_ID") and os.environ.get("XWEATHER_CLIENT_SECRET")),
     "note": "NOAA-verified storm reports API — set XWEATHER_CLIENT_ID / XWEATHER_CLIENT_SECRET"},
    {"key": "visualcrossing", "label": "Visual Crossing", "tier": "premium",
     "enabled": bool(os.environ.get("VISUALCROSSING_KEY")),
     "note": "Timeline API — historical hail/tornado/wind-damage events + wind gusts (severe-risk/CAPE avail. for staging) — set VISUALCROSSING_KEY"},
    {"key": "hailtrace", "label": "HailTrace", "tier": "premium",
     "enabled": bool(os.environ.get("HAILTRACE_KEY")),
     "note": "hail-specific radar-verified swaths — set HAILTRACE_KEY (confirm endpoint against HailTrace API docs)"},
]

# ------- action triggers (configurable — the alert can fire different things) -------
TRIGGERS = [
    {"key": "knock_all", "label": "Door-knock — all crews", "desc": "Big event — every crew to the area now.",
     "template": "\U0001F6A8 VERIFIED: {county} Co {md} — {hazard} ({conf}). Big one — all crews door-knock now, get there first. —Nick"},
    {"key": "knock", "label": "Door-knock — area", "desc": "Send the area's crew to door-knock.",
     "template": "VERIFIED storm: {county} Co {md} — {hazard} ({conf}). Door-knock priority — beat everyone there. —Nick"},
    {"key": "monitor", "label": "Monitor — reports pending", "desc": "Waiting on more reports; hold for the go.",
     "template": "Watching {county} Co {md} — {hazard} ({conf}). Reports still coming in — hold for the go. —Nick"},
]

_MARINE = re.compile(r"^[A-Z]{2,3}\d{3}$")


def _get(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace"), r.status


def _hazard(typetext):
    t = (typetext or "").upper()
    if "TORNADO" in t:                       return "tornado"
    if "HAIL" in t:                          return "hail"
    if "MARINE" in t:                        return None       # offshore
    if "WND" in t or "WIND" in t:            return "wind"
    return None                              # funnel/rain/flood/etc — not roofing


# ---- SOURCE 1 (primary): IEM Local Storm Reports (structured, w/ geometry) ----
def fetch_iem(days):
    sts = (date.today() - timedelta(days=days)).strftime("%Y-%m-%dT00:00Z")
    ets = date.today().strftime("%Y-%m-%dT23:59Z")
    url = ("https://mesonet.agron.iastate.edu/geojson/lsr.geojson?"
           + urllib.parse.urlencode({"sts": sts, "ets": ets, "states": STATE}))
    try:
        body, status = _get(url)
        feats = json.loads(body).get("features", []) if status == 200 else []
    except Exception:
        return []
    out = []
    for f in feats:
        p = f.get("properties", {})
        hz = _hazard(p.get("typetext"))
        if hz is None:
            continue
        county = (p.get("county") or "").strip()
        if not county or _MARINE.match(county):
            continue
        # magnitude -> inches (hail) or mph (wind)
        mag, unit = p.get("magnitude"), (p.get("unit") or "").upper()
        val, damage = None, False
        try:
            m = float(mag)
            if hz == "hail":                 val = m
            elif hz == "wind":               val = m * 1.15 if unit.startswith("K") else m
        except (TypeError, ValueError):
            if hz == "wind" and "DMG" in (p.get("typetext") or "").upper():
                damage = True                # damage report w/ no measured speed
        geom = (f.get("geometry") or {}).get("coordinates") or [None, None]
        out.append({"date": (p.get("valid") or "")[:10], "hazard": hz, "value": val,
                    "damage": damage, "county": county, "lon": geom[0], "lat": geom[1],
                    "src": "NOAA LSR", "time": p.get("valid"), "reporter": p.get("source"),
                    "qualifier": p.get("qualifier") or p.get("magf"), "remark": p.get("remark")})
    return out


# ---- SOURCE (optional): Xweather — NOAA-verified alerts API (Nick's key) ----
def fetch_xweather(days):
    """Off until Nick's key is in .env (XWEATHER_CLIENT_ID / XWEATHER_CLIENT_SECRET).
    Answers his 'I don't know how to integrate it': add the two creds and this
    lights up as a live source. Field mapping is best-effort — confirm against the
    first live response (Xweather/Aeris nests vary by plan) and tweak if needed."""
    cid = os.environ.get("XWEATHER_CLIENT_ID")
    sec = os.environ.get("XWEATHER_CLIENT_SECRET")
    if not (cid and sec):
        return []
    url = ("https://data.api.xweather.com/stormreports/search?"
           + urllib.parse.urlencode({"query": f"state:{STATE.lower()}", "from": f"-{days}days",
                                     "to": "now", "filter": "hail,wind", "limit": "500",
                                     "client_id": cid, "client_secret": sec}))
    try:
        body, status = _get(url)
        js = json.loads(body)
        rows = js.get("response", []) if js.get("success") else []
    except Exception:
        return []
    out = []
    for r in rows:
        rep = r.get("report", r) if isinstance(r.get("report"), dict) else r
        hz = _hazard(rep.get("type") or rep.get("code") or "")
        if hz is None:
            continue
        place, loc = r.get("place", {}) or {}, r.get("loc", {}) or {}
        county = (place.get("county") or "").strip()
        if not county or _MARINE.match(county):
            continue
        det = r.get("detail", {}) if isinstance(r.get("detail"), dict) else {}
        val = None
        try:
            val = float(det.get("size") if hz == "hail" else (det.get("windSpeedMPH") or det.get("mag")))
        except (TypeError, ValueError):
            val = None
        out.append({"date": (r.get("dateTimeISO") or "")[:10], "hazard": hz, "value": val,
                    "damage": False, "county": county,
                    "lon": loc.get("long"), "lat": loc.get("lat"), "src": "Xweather"})
    return out


# ---- SOURCE (Nick's): Visual Crossing — historical hail/tornado/wind events ----
def fetch_visualcrossing(days):
    """Set VISUALCROSSING_KEY to enable. Uses the Timeline API's `events` include
    (historical HAIL / TORNADO / WIND-DAMAGE events, with size where available) —
    a real severe-weather source — plus daily windgust as a wind fallback. Event
    object field names vary; parsing is defensive — confirm against a live response.
    (severerisk/CAPE are also available here and would make a good staging signal.)"""
    key = os.environ.get("VISUALCROSSING_KEY")
    if not key:
        return []
    # Throttle: VC bills per record and its data (events/severe-risk) doesn't change
    # every 20 min. Cache results ~12h and serve the cache in between, so we fetch
    # only ~2x/day (~370 records/day — well under the free 1000/day tier).
    import time
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vc_cache.json")
    ttl = int(os.environ.get("VISUALCROSSING_TTL_HOURS", "12")) * 3600
    try:
        if os.path.exists(cache):
            c = json.load(open(cache))
            if time.time() - c.get("ts", 0) < ttl:
                return c.get("reports", [])
    except Exception:
        pass
    from fl_places import FL_PLACES
    start = (date.today() - timedelta(days=days)).isoformat()
    end = date.today().isoformat()
    out = []
    for p in FL_PLACES:
        url = ("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
               f"{p['lat']},{p['lon']}/{start}/{end}?"
               + urllib.parse.urlencode({"unitGroup": "us", "include": "days,events",
                                         "key": key, "contentType": "json"}))
        try:
            body, status = _get(url)
            arr = json.loads(body).get("days", []) if status == 200 else []
        except Exception:
            continue
        for d in arr:
            dt = d.get("datetime")
            # (a) severe EVENTS — hail / tornado / wind damage
            for ev in d.get("events") or []:
                t = str(ev.get("type") or ev.get("eventType") or "").lower()
                if "hail" in t:
                    hz, val = "hail", ev.get("size") or ev.get("hailSize")
                elif "tornado" in t:
                    hz, val = "tornado", None
                elif "wind" in t:
                    hz, val = "wind", ev.get("speed") or ev.get("gust") or ev.get("windSpeed")
                else:
                    continue
                try:
                    val = float(val) if val is not None else None
                except (TypeError, ValueError):
                    val = None
                out.append({"date": (ev.get("datetime") or dt or "")[:10], "hazard": hz, "value": val,
                            "damage": "damage" in t, "county": p["county"],
                            "lon": ev.get("longitude") or p["lon"], "lat": ev.get("latitude") or p["lat"],
                            "src": "Visual Crossing"})
            # (b) daily wind-gust fallback (wind corroboration when no discrete event)
            try:
                g = float(d.get("windgust") or 0)
            except (TypeError, ValueError):
                g = 0
            if g >= WIND_MIN:
                out.append({"date": dt, "hazard": "wind", "value": round(g), "damage": False,
                            "county": p["county"], "lon": p["lon"], "lat": p["lat"], "src": "Visual Crossing"})
    try:
        json.dump({"ts": time.time(), "reports": out}, open(cache, "w"))
    except Exception:
        pass
    return out


# ---- SOURCE (Nick's): HailTrace — radar-verified hail swaths ----
def fetch_hailtrace(days):
    """HailTrace's radar-verified hail (size + swath). Set HAILTRACE_KEY to enable.
    HailTrace's API is partner/enterprise — drop in the documented endpoint + map
    the response to the report dict (hazard='hail', value=size_in, county/lat/lon).
    Returns [] until we have their API docs, so the engine runs cleanly meanwhile."""
    key = os.environ.get("HAILTRACE_KEY")
    if not key:
        return []
    # TODO(nick's HailTrace API docs): fetch FL hail swaths for `days`, then:
    #   out.append({"date","hazard":"hail","value":<inches>,"damage":False,
    #               "county","lon","lat","src":"HailTrace"})
    return []


# ---- SOURCE 2 (corroborate): NOAA SPC daily storm reports ----
def fetch_spc(days):
    keys = set()
    for i in range(days):
        d = date.today() - timedelta(days=i)
        try:
            body, status = _get(f"https://www.spc.noaa.gov/climo/reports/{d:%y%m%d}_rpts_filtered.csv")
        except Exception:
            continue
        if status != 200 or not body.strip():
            continue
        hz = None
        for row in csv.reader(io.StringIO(body)):
            if not row or len(row) < 8:
                continue
            if row[0] == "Time":
                hz = {"F_Scale": "tornado", "Speed": "wind", "Size": "hail"}.get(row[1]); continue
            if hz is None or row[4].upper() != STATE or _MARINE.match(row[3].strip()):
                continue
            keys.add((row[3].strip().lower(), f"{d:%Y-%m-%d}"))   # (county, date)
    return keys


# ---- SOURCE 3 (corroborate): NWS active alerts ----
def fetch_nws():
    try:
        body, status = _get(f"https://api.weather.gov/alerts/active?area={STATE}")
        feats = json.loads(body).get("features", []) if status == 200 else []
    except Exception:
        return []
    out = []
    for f in feats:
        p = f.get("properties", {})
        if any(k in p.get("event", "") for k in ("Tornado", "Severe Thunderstorm", "Special Weather")):
            out.append({"event": p.get("event", ""), "areaDesc": p.get("areaDesc", "")})
    return out


def recommend_trigger(v):
    # big events -> all crews; solid HIGH -> area door-knock; else monitor (still waiting on reports)
    if v["tornado"] or (v["max_hail_in"] or 0) >= 1.25 or (v["max_wind_mph"] or 0) >= 70:
        return "knock_all"
    if v["confidence"] == "HIGH" and v["roofing_relevant"]:
        return "knock"
    return "monitor"


def hazard_str(v):
    bits = []
    if v["max_hail_in"] is not None:  bits.append(f'HAIL to {v["max_hail_in"]:.2f}"')
    if v["max_wind_mph"] is not None: bits.append(f'WIND {v["max_wind_mph"]:.0f}mph')
    elif v["wind_damage"]:            bits.append("WIND damage")
    if v["tornado"]:                  bits.append("TORNADO")
    return " + ".join(bits) or "storm reports"


def severity_grade(hail, wind, tornado):
    """A–D severity grade on the PEAK reading (what damage/claims key on)."""
    if tornado or (hail or 0) >= 1.5 or (wind or 0) >= 70: return "A"
    if (hail or 0) >= 1.0 or (wind or 0) >= 60:            return "B"
    if (hail or 0) >= HAIL_MIN or (wind or 0) >= WIND_MIN: return "C"
    return "D"


def verify():
    reports = (fetch_iem(DAYS) + fetch_xweather(DAYS)
               + fetch_visualcrossing(DAYS) + fetch_hailtrace(DAYS))   # ground reports across live sources
    if next((s for s in SOURCES if s["key"] == "mesh"), {}).get("enabled"):
        try:                                            # radar hail — guarded (pygrib optional)
            from mrms_mesh import fetch_mesh
            reports += fetch_mesh(DAYS)
        except Exception:
            pass
    spc = fetch_spc(DAYS)
    nws = fetch_nws()
    nws_text = " | ".join(a["areaDesc"] for a in nws).lower()

    clusters = defaultdict(lambda: {"hail": [], "wind": [], "tornado": False, "damage": False,
                                     "lat": None, "lon": None, "srcs": set(), "evidence": []})
    for r in reports:
        c = clusters[(r["county"], r["date"])]
        c["srcs"].add(r.get("src", "NOAA LSR"))
        c["evidence"].append({"src": r.get("src"), "hazard": r["hazard"], "value": r.get("value"),
                              "time": r.get("time"), "reporter": r.get("reporter"),
                              "qualifier": r.get("qualifier"), "remark": r.get("remark")})
        if r["hazard"] == "hail" and r["value"] is not None: c["hail"].append(r["value"])
        if r["hazard"] == "wind" and r["value"] is not None: c["wind"].append(r["value"])
        if r["hazard"] == "wind" and r["damage"]:            c["damage"] = True
        if r["hazard"] == "tornado":                         c["tornado"] = True
        if c["lat"] is None and r["lat"] is not None:        c["lat"], c["lon"] = r["lat"], r["lon"]

    verified = []
    for (county, dt), c in clusters.items():
        n = len(c["hail"]) + len(c["wind"]) + (1 if c["tornado"] else 0) + (1 if c["damage"] else 0)
        max_hail = max(c["hail"], default=None)
        max_wind = max(c["wind"], default=None)
        # Average the readings across sources/stations too — a consensus value more
        # accurate than a single outlier report (Nick's ask). Peak drives damage +
        # claims; the average drives confidence and grading.
        avg_hail = round(sum(c["hail"]) / len(c["hail"]), 2) if c["hail"] else None
        avg_wind = round(sum(c["wind"]) / len(c["wind"])) if c["wind"] else None
        # roofing-relevant = genuinely damaging. Bare "wind damage" LSRs (a limb
        # down) are too noisy to alert on — kept as a flag, not a trigger.
        relevant = ((max_hail or 0) >= HAIL_MIN or (max_wind or 0) >= WIND_MIN or c["tornado"])
        spc_ok = (county.lower(), dt) in spc
        nws_ok = county.lower() in nws_text and bool(nws)
        conf = "HIGH" if (n >= 2 or (n >= 1 and (spc_ok or nws_ok))) else "MEDIUM"
        hits = sorted(c["srcs"]) + (["NOAA SPC"] if spc_ok else []) + (["NWS warning"] if nws_ok else [])
        v = {"county": county, "date": dt, "lat": c["lat"], "lon": c["lon"],
             "reports": n, "max_hail_in": max_hail, "max_wind_mph": max_wind,
             "avg_hail_in": avg_hail, "avg_wind_mph": avg_wind,
             "grade": severity_grade(max_hail, max_wind, c["tornado"]),
             "tornado": c["tornado"], "wind_damage": c["damage"],
             "roofing_relevant": relevant, "confidence": conf, "sources_hit": hits,
             "evidence": c["evidence"]}
        v["trigger"] = recommend_trigger(v)
        verified.append(v)

    verified.sort(key=lambda v: (v["roofing_relevant"], v["confidence"] == "HIGH",
                                 v["reports"], v["date"]), reverse=True)
    return verified, len(reports), nws


def main():
    verified, raw, nws = verify()
    rel = [v for v in verified if v["roofing_relevant"]]
    live = [s["label"] for s in SOURCES if s["enabled"]]

    print("=" * 62)
    print(f"  yourco · STORM VERIFICATION — {STATE}   (last {DAYS} days, thru {date.today():%Y-%m-%d})")
    print(f"  live sources: {', '.join(live)}")
    print(f"  ready to connect: {', '.join(s['label'] for s in SOURCES if not s['enabled'])}")
    print("=" * 62)
    print(f"  {raw} raw reports  ->  {len(verified)} verified areas  ->  {len(rel)} roofing-relevant\n")

    tmap = {t["key"]: t for t in TRIGGERS}
    for v in rel[:12]:
        bar = "▓" if v["confidence"] == "HIGH" else "▒"
        trig = tmap[v["trigger"]]
        msg = trig["template"].format(county=v["county"], md=v["date"][5:],
                                      hazard=hazard_str(v), conf=v["confidence"])
        print(f"{bar} {v['confidence']}  ·  {v['county']} County  ·  {v['date']}   [{trig['label']}]")
        print(f"   {hazard_str(v)}   — verified by: {', '.join(v['sources_hit'])}")
        print(f'   → "{msg}"\n')

    with open("last_run.json", "w") as f:
        json.dump({"generated": f"{date.today():%Y-%m-%d}", "state": STATE, "window_days": DAYS,
                   "raw_reports": raw, "sources": SOURCES, "triggers": TRIGGERS,
                   "verified": verified, "active_nws_alerts": nws}, f, indent=2)
    print("  (full results -> last_run.json;  build the visual demo -> python3 build_demo.py)")


if __name__ == "__main__":
    main()
