#!/usr/bin/env python3
"""yourco — Recraft AI connector (static + vector image generation). SCAFFOLD, PARKED.

⚠️ NO PUBLIC API as of 2026-06-17 (the Founder confirmed). Recraft is **web-app only** right now — use recraft.ai's
UI for design work. This connector is parked + kept only in case Recraft opens public API access later; do NOT
rely on it until then. (The endpoint below is a placeholder, unverified.)


Recraft fills yourco's static-design gap: raster + VECTOR brand imagery (logos, icons, landing-page
graphics, social stills) with a commercial license. Used by Reed (production) + Webb (site). It's a
web app first — most design work happens in recraft.ai's UI; this connector is for the OPTIONAL headless
path (agents generating images programmatically).

Status: STAGED — no API key yet. Get one at recraft.ai (Pro plan for commercial rights), paste into
runtime/.recraft.env. Pure stdlib (urllib). Generating an image COSTS CREDITS, so dry_run is the default;
nothing calls the paid API without --commit.

Usage:
  python3 runtime/recraft.py --self-check
  python3 runtime/recraft.py --generate "indigo geometric mark, minimal, brand logo" --style vector_illustration   # dry-run
  python3 runtime/recraft.py --generate "..." --commit          # actually generate (spends credits)
"""
import os, sys, json, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("RECRAFT_BASE", "https://external.api.recraft.ai/v1")


def _load_env():
    p = os.path.join(HERE, ".recraft.env")
    if not os.path.exists(p):
        return
    for line in open(p):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
KEY = os.environ.get("RECRAFT_API_KEY", "").strip()


def generate(prompt, style="digital_illustration", size="1024x1024", n=1, dry_run=True):
    """Generate image(s). style: digital_illustration | vector_illustration | realistic_image (verify the
    current set + endpoint against Recraft's API docs before binding reliance). dry_run reports without
    spending credits. Returns the API response (image URLs) on commit."""
    if not KEY:
        return {"staged": True, "reason": "no RECRAFT_API_KEY yet — sign up at recraft.ai + paste into runtime/.recraft.env",
                "would_generate": {"prompt": prompt, "style": style, "size": size, "n": n}}
    if dry_run:
        return {"dry_run": True, "prompt": prompt, "style": style, "size": size, "n": n,
                "note": "re-run with --commit to actually generate (spends Recraft credits)"}
    body = {"prompt": prompt, "style": style, "size": size, "n": n}
    req = urllib.request.Request(BASE + "/images/generations", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Recraft POST /images/generations -> {e.code}: {e.read().decode()[:300]}")


def _self_check():
    print("yourco Recraft connector — config check (SCAFFOLD / staged)")
    print(f"  API key set: {bool(KEY)}   base: {BASE}")
    print("  use: static + vector brand imagery (Reed/Webb); also the tool for a bespoke yourco logo.")
    print("  guard: dry_run default — generating images costs credits; needs --commit + a key.")
    print("  status: STAGED — sign up at recraft.ai (Pro = commercial rights), paste key into runtime/.recraft.env.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-check" in a or not a:
        sys.exit(_self_check())
    if "--generate" in a:
        prompt = a[a.index("--generate") + 1]
        style = a[a.index("--style") + 1] if "--style" in a else "digital_illustration"
        res = generate(prompt, style=style, dry_run="--commit" not in a)
        print(json.dumps(res, indent=2))
        sys.exit(0)
    print(__doc__)
