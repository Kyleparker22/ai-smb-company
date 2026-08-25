#!/usr/bin/env python3
"""yourco — Firecrawl connector (site → LLM-ready markdown). ADOPTED 2026-07-05.

The one sanctioned crawl path (decisions/2026-07-05_tool-triage.md): a rented commodity API —
public open-web pages only, robots.txt respected by the vendor, and a HARD DENYLIST of ToS-gated
platforms baked in below (Rafi: agents/rafi/social-platform-scraping-assessment.md — licensed
paths only for social; this tool refuses those domains by design, do NOT remove the check).

Consumers: Bella (audit prep — crawl the prospect's own site before call 1), Mario (AEO/GEO —
category/entity pages), Kimi (discovery — client's own site → Company Brain). Complements native
Enrich (single-page extraction); doesn't replace it.

Setup: paste the key into runtime/.firecrawl.env as  FIRECRAWL_API_KEY=fc-...
(gitignored; on the VPS create the same file in the repo checkout). Free tier ≈500 credits;
1 page ≈1 credit. Crawls are capped at --limit (default 10, max 50) so a run can't eat the plan.

Usage:
  python3 runtime/firecrawl.py --self-check
  python3 runtime/firecrawl.py --scrape https://example.com                      # 1 page → stdout
  python3 runtime/firecrawl.py --scrape https://example.com --out page.md
  python3 runtime/firecrawl.py --crawl https://example.com --limit 15 --out-dir clients/<x>/site-crawl/
"""
import os, re, sys, json, time, argparse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("FIRECRAWL_BASE", "https://api.firecrawl.dev/v2")

# Rafi's bounds: ToS-gated platforms are licensed-access-only — never crawled. Registrable-domain match.
DENYLIST = {
    "x.com", "twitter.com", "linkedin.com", "facebook.com", "instagram.com", "threads.net",
    "tiktok.com", "reddit.com", "youtube.com", "pinterest.com", "snapchat.com", "quora.com",
}


def _load_env():
    p = os.path.join(HERE, ".firecrawl.env")
    if not os.path.exists(p):
        return
    for line in open(p):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
KEY = os.environ.get("FIRECRAWL_API_KEY", "").strip()


def _denied(url):
    host = re.sub(r"^https?://", "", url).split("/")[0].split(":")[0].lower()
    parts = host.split(".")
    for i in range(len(parts) - 1):
        if ".".join(parts[i:]) in DENYLIST:
            return ".".join(parts[i:])
    return None


def _call(method, path, body=None, timeout=120):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode(errors="replace")[:500]}


def _guard(url):
    d = _denied(url)
    if d:
        sys.exit(f"REFUSED: {d} is a ToS-gated platform — licensed access only "
                 f"(agents/rafi/social-platform-scraping-assessment.md). This check is load-bearing; do not bypass.")
    if not KEY:
        sys.exit("No FIRECRAWL_API_KEY — paste it into runtime/.firecrawl.env (see docstring).")


def scrape(url):
    _guard(url)
    r = _call("POST", "/scrape", {"url": url, "formats": ["markdown"]})
    if r.get("error") or not r.get("success"):
        sys.exit("scrape failed: " + json.dumps(r)[:500])
    return r["data"].get("markdown", ""), r["data"].get("metadata", {})


def crawl(url, limit, out_dir):
    _guard(url)
    limit = max(1, min(limit, 50))  # spend cap — raise deliberately, not by accident
    r = _call("POST", "/crawl", {"url": url, "limit": limit, "scrapeOptions": {"formats": ["markdown"]}})
    job = r.get("id")
    if not job:
        sys.exit("crawl start failed: " + json.dumps(r)[:500])
    print(f"crawl job {job} started (limit {limit}) — polling…")
    while True:
        time.sleep(5)
        st = _call("GET", f"/crawl/{job}")
        status = st.get("status")
        if status in ("completed", "failed", "cancelled"):
            break
        print(f"  {status}: {st.get('completed', '?')}/{st.get('total', '?')} pages")
    if status != "completed":
        sys.exit(f"crawl ended {status}: " + json.dumps(st)[:300])
    pages = st.get("data", [])
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for p in pages:
        src = (p.get("metadata") or {}).get("sourceURL", "page")
        slug = re.sub(r"[^a-z0-9]+", "-", re.sub(r"^https?://", "", src).lower()).strip("-")[:80] or "index"
        path = os.path.join(out_dir, slug + ".md")
        with open(path, "w") as f:
            f.write(f"<!-- source: {src} | fetched via Firecrawl {time.strftime('%Y-%m-%d')} -->\n\n")
            f.write(p.get("markdown", ""))
        written.append(path)
    return written


def main():
    ap = argparse.ArgumentParser(description="yourco Firecrawl connector")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--scrape", metavar="URL")
    ap.add_argument("--crawl", metavar="URL")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--out", metavar="FILE")
    ap.add_argument("--out-dir", metavar="DIR", default="site-crawl")
    a = ap.parse_args()

    if a.self_check:
        print("key:", "set (…" + KEY[-4:] + ")" if KEY else "MISSING — paste into runtime/.firecrawl.env")
        print("base:", BASE)
        print("denylist:", ", ".join(sorted(DENYLIST)))
        if KEY:
            r = _call("GET", "/team/credit-usage")
            print("api:", "reachable — " + json.dumps(r)[:200] if not r.get("error") else f"error {r}")
        return
    if a.scrape:
        md, meta = scrape(a.scrape)
        if a.out:
            with open(a.out, "w") as f:
                f.write(f"<!-- source: {a.scrape} | fetched via Firecrawl {time.strftime('%Y-%m-%d')} -->\n\n" + md)
            print(f"wrote {a.out} ({len(md)} chars) — {meta.get('title', '')}")
        else:
            print(md)
        return
    if a.crawl:
        written = crawl(a.crawl, a.limit, a.out_dir)
        print(f"wrote {len(written)} pages to {a.out_dir}/")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
