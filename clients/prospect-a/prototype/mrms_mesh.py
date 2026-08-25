#!/usr/bin/env python3
"""
MRMS MESH adapter — radar-derived max hail size (the HailTrace replacement).

NOAA MRMS `MESH_Max_1440min` = Maximum Estimated Size of Hail over the rolling
past 24h, radar-derived across CONUS, refreshed ~every 2 min. Public + KEYLESS:

    https://mrms.ncep.noaa.gov/2D/MESH_Max_1440min/

This is the accuracy edge Nick asked for: it fixes "atmospheric estimate vs
ground truth" by giving a measured radar hail size for a swath even where no
human filed a Local Storm Report.

Two honest constraints:
  1. The files are GRIB2 (binary grid) → needs `pygrib` (pip install pygrib,
     which needs the eccodes system lib). The core engine (storm_poc.py) stays
     pure-stdlib and imports this module *guardedly* — if pygrib isn't present,
     fetch_mesh() returns [] and the engine runs fine without it.
  2. The realtime dir only retains ~recent files (hours, not months). MESH is a
     NEAR-REAL-TIME layer (live alerts / today's swath), not a 12-month lookback.
     For history, IEM archives MRMS separately — a v2 add.

Output matches the engine's report shape (see fetch_iem in storm_poc.py):
    {"date","hazard":"hail","value":<inches>,"damage":False,"county",
     "lon","lat","src":"NOAA MRMS MESH (radar)","time",...}

Run standalone to self-test:  python3 mrms_mesh.py
"""
import gzip, io, json, os, urllib.request, urllib.parse
from datetime import date

MESH_DIR = "https://mrms.ncep.noaa.gov/2D/MESH_Max_1440min/"
UA = {"User-Agent": "yourco-storm-verified/0.1 (roofing storm verification)"}

# Florida bounding box (lat/lon) — MESH is CONUS; we only decode over FL.
FL_BBOX = {"lat1": 24.3, "lat2": 31.1, "lon1": -87.7, "lon2": -79.8}
MM_PER_IN = 25.4
HAIL_MIN_IN = 0.75            # roofing threshold, matches storm_poc.HAIL_MIN
BIN_DEG = 0.15               # ~16km blobs — one report per blob (bounds geocode calls)

_county_cache = {}


def _pygrib():
    """Guarded import — None if pygrib/eccodes isn't installed (engine still runs)."""
    try:
        import pygrib
        return pygrib
    except Exception:
        return None


def _latest_grib_url():
    """Newest MESH_Max_1440min file in the realtime dir (keyless HTTP index scrape)."""
    try:
        req = urllib.request.Request(MESH_DIR, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception:
        return None
    # Apache autoindex: filenames like MRMS_MESH_Max_1440min_00.50_YYYYMMDD-HHMMSS.grib2.gz
    names = [tok.split('"')[0] for tok in html.split('href="') if tok.startswith("MRMS_")]
    names = [n for n in names if n.endswith(".grib2.gz")]
    if not names:
        return None
    names.sort()                     # timestamp is lexically sortable → last = newest
    return MESH_DIR + names[-1]


def _latlon_to_county(lat, lon):
    """Reverse-geocode a point to a county name via the free FCC census-block API.
    Cached per coarse bin so we make only a handful of calls."""
    key = (round(lat, 2), round(lon, 2))
    if key in _county_cache:
        return _county_cache[key]
    url = ("https://geo.fcc.gov/api/census/block/find?"
           + urllib.parse.urlencode({"latitude": lat, "longitude": lon, "censusYear": "2020",
                                     "showall": "false", "format": "json"}))
    county = None
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            js = json.loads(r.read().decode("utf-8", "replace"))
        name = (js.get("County") or {}).get("name")
        if name:
            county = name.replace(" County", "").strip()
    except Exception:
        county = None
    _county_cache[key] = county
    return county


def fetch_mesh(days=1, hail_min_in=HAIL_MIN_IN, bbox=FL_BBOX):
    """Return radar-hail 'reports' (engine shape) from the latest MESH grid.
    `days` is accepted for a uniform signature with the other fetchers; the
    realtime product is a rolling 24h max, so we read the newest file."""
    pygrib = _pygrib()
    if pygrib is None:
        return []                                     # deps absent → engine runs without MESH
    url = _latest_grib_url()
    if not url:
        return []
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = gzip.decompress(r.read())
    except Exception:
        return []

    # pygrib reads from a path; write the decompressed GRIB2 to a temp file.
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mesh.grib2")
    try:
        with open(tmp, "wb") as f:
            f.write(raw)
        grbs = pygrib.open(tmp)
        grb = grbs[1]
        # values (mm) + lat/lon arrays clipped to the FL bounding box
        vals, lats, lons = grb.data(lat1=bbox["lat1"], lat2=bbox["lat2"],
                                    lon1=bbox["lon1"] % 360, lon2=bbox["lon2"] % 360)
        grbs.close()
    except Exception:
        return []
    finally:
        try: os.remove(tmp)
        except OSError: pass

    thresh_mm = hail_min_in * MM_PER_IN
    # Reduce the grid to significant-hail blobs: keep the max cell per coarse bin.
    blobs = {}                                        # bin -> (mm, lat, lon)
    it = zip(vals.ravel(), lats.ravel(), lons.ravel())
    for v, la, lo in it:
        try:
            mm = float(v)
        except (TypeError, ValueError):
            continue
        if mm < thresh_mm or mm > 250:                # >250mm(~10") = radar artifact
            continue
        lo = lo - 360 if lo > 180 else lo
        b = (round(la / BIN_DEG), round(lo / BIN_DEG))
        if b not in blobs or mm > blobs[b][0]:
            blobs[b] = (mm, la, lo)

    today = date.today().strftime("%Y-%m-%d")
    out = []
    for mm, la, lo in blobs.values():
        county = _latlon_to_county(la, lo)            # cached, one call per blob
        if not county:
            continue
        out.append({"date": today, "hazard": "hail", "value": round(mm / MM_PER_IN, 2),
                    "damage": False, "county": county, "lon": round(lo, 3), "lat": round(la, 3),
                    "src": "NOAA MRMS MESH (radar)", "time": None, "reporter": "radar",
                    "qualifier": "radar-estimated (MESH)", "remark": f"MESH {mm:.0f}mm max-24h"})
    return out


if __name__ == "__main__":
    pg = _pygrib()
    print(f"pygrib available: {bool(pg)}")
    if not pg:
        print("  → install on the hosted build:  pip install pygrib  (needs eccodes system lib)")
        print("  → engine runs without it; MESH stays dark until installed.")
        raise SystemExit(0)
    print(f"latest MESH file: {_latest_grib_url()}")
    reps = fetch_mesh()
    print(f"{len(reps)} radar-hail blobs over FL (>= {HAIL_MIN_IN}\"):")
    for r in sorted(reps, key=lambda x: -x['value'])[:15]:
        print(f"  {r['county']:16} {r['value']:.2f}\"  ({r['lat']},{r['lon']})")
