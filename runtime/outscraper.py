#!/usr/bin/env python3
"""yourco — native Outscraper connector (Google Maps sourcing for Reilly).

Pulls local-business listings from Google Maps via Outscraper's API — name, address, phone, website.
The source that catches weak-digital-footprint local SMBs (trades) that Vibe/Instantly miss; the
"only in Outscraper" tag is a positive ICP signal for landscaping/hardscaping (per
decisions/2026-06-07_multi-source-sourcing.md). Sourcing only — no outreach.

Pure stdlib. Key from env (OUTSCRAPER_API_KEY), e.g. runtime/.outscraper.env (gitignored).
Costs money per request — confirm before large pulls. Compliance: Google Maps *public business*
listings via a managed service (lower-risk than personal-data scraping); Rafi confirms posture.

Usage:
  python3 runtime/outscraper.py --self-check
  python3 runtime/outscraper.py --search "landscaping, Yourtown" --limit 10
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("OUTSCRAPER_BASE", "https://api.app.outscraper.com")


def _load_env():
    p = os.path.join(HERE, ".outscraper.env")
    if not os.path.exists(p):
        return
    for line in open(p):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
KEY = os.environ.get("OUTSCRAPER_API_KEY", "").strip()


def _domain(url):
    if not url:
        return ""
    try:
        host = urllib.parse.urlparse(url if "//" in url else "https://" + url).hostname or ""
        return host.lower().lstrip("www.") if host else ""
    except Exception:
        return ""


def search(query, limit=10, region="US"):
    """Google Maps search → list of normalized prospects (the common schema)."""
    if not KEY:
        raise RuntimeError("no OUTSCRAPER_API_KEY (set it in runtime/.outscraper.env)")
    qs = urllib.parse.urlencode({"query": query, "limit": limit, "region": region, "async": "false"})
    req = urllib.request.Request(f"{BASE}/maps/search-v3?{qs}",
                                 headers={"X-API-KEY": KEY, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Outscraper {e.code}: {e.read().decode()[:300]}")
    # response: {data: [[{...biz...}, ...]]}  (one result-array per query)
    blocks = payload.get("data", [])
    rows = blocks[0] if (blocks and isinstance(blocks[0], list)) else blocks
    out = []
    for b in rows:
        out.append({
            "name": b.get("name", ""),
            "domain": _domain(b.get("site", "")),
            "phone": b.get("phone", ""),
            "address": b.get("full_address", b.get("address", "")),
            "owner": "", "employees": "", "revenue": "",
            "source": ["outscraper"],
            "_raw_site": b.get("site", ""),
        })
    return out


def _self_check():
    print("yourco Outscraper connector — config check")
    print(f"  API key set: {bool(KEY)}   base: {BASE}")
    print("  scope: Google Maps public business listings · sourcing only · costs $ per request.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-check" in a:
        sys.exit(_self_check())
    if "--search" in a:
        q = a[a.index("--search") + 1]
        lim = int(a[a.index("--limit") + 1]) if "--limit" in a else 10
        res = search(q, lim)
        print(f"{len(res)} results for {q!r}:")
        for r in res:
            print(f"  - {r['name']} | {r['domain'] or '(no site)'} | {r['phone']} | {r['address']}")
        sys.exit(0)
    print(__doc__)
