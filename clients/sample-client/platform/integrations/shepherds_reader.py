#!/usr/bin/env python3
"""Shepherd's Landscape Supply availability reader (Yourtown, ST).

Reads PUBLIC product pages from shepherdssupply.com (Wix Stores) and extracts
name / SKU / price / in-stock from each page's schema.org JSON-LD.

Compliance posture (checked 2026-08-07, re-verify if behavior changes):
  - robots.txt: `User-agent: * / Allow: /` — crawling explicitly permitted.
  - No login, no credentials, public pages only.
  - Polite: identifying User-Agent w/ contact, 1 req/sec default, weekly cadence.
  - Wix JSON-LD quirk: keys are `Offers` / `Availability` (capitalized).

Output: data/shared/availability-shepherds.json
Usage:  python3 shepherds_reader.py [--limit N] [--delay SECS]
"""
import argparse, json, re, sys, time, urllib.request
from pathlib import Path

BASE = "https://www.shepherdssupply.com"
SITEMAP = BASE + "/store-products-sitemap.xml"
UA = "SampleClientDesignStudio/1.0 (weekly availability check; contact founder@yourco.example.com)"
OUT = Path(__file__).resolve().parent.parent / "data" / "shared" / "availability-shepherds.json"


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def product_urls():
    xml = get(SITEMAP)
    return re.findall(r"<loc>(%s/product-page/[^<]+)</loc>" % re.escape(BASE), xml)


def ci(d, key):
    """Case-insensitive dict get (Wix capitalizes Offers/Availability)."""
    for k, v in d.items():
        if k.lower() == key.lower():
            return v
    return None


def parse_product(html):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if d.get("@type") != "Product":
            continue
        offer = ci(d, "offers") or {}
        avail = str(ci(offer, "availability") or "")
        price = ci(offer, "price")
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = None
        return {"name": d.get("name"), "sku": d.get("sku"),
                "price": price if price else None,  # Wix shows 0 for call-for-price
                "inStock": "InStock" in avail if avail else None}
    return None


def run(limit=None, delay=1.0):
    urls = product_urls()
    total = len(urls)
    if limit:
        urls = urls[:limit]
    items, errors = [], 0
    for i, url in enumerate(urls):
        try:
            p = parse_product(get(url))
            if p:
                p["url"] = url
                items.append(p)
        except Exception:
            errors += 1
        if delay:
            time.sleep(delay)
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(urls)}…", file=sys.stderr)
    out = {"source": "shepherds", "label": "Shepherd's Landscape Supply (public site read)",
           "pulled": time.strftime("%Y-%m-%dT%H:%M:%S"), "site_total": total,
           "fetched": len(urls), "parsed": len(items), "errors": errors,
           "in_stock": sum(1 for i in items if i["inStock"]),
           "out_of_stock": sum(1 for i in items if i["inStock"] is False),
           "items": items}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1))
    tmp.replace(OUT)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only first N products (testing)")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    a = ap.parse_args()
    r = run(a.limit, a.delay)
    print(json.dumps({k: v for k, v in r.items() if k != "items"}, indent=1))
