#!/usr/bin/env python3
"""yourco — what a build ACTUALLY cost, measured from Claude Code's own session transcripts.

WHY THIS EXISTS: the Anthropic Admin cost API meters the *API* (the VPS runtime loops). the Founder's
building happens in **Claude Code**, which bills the subscription, not the API — so the biggest
token consumer in the business was invisible to every ledger. Claude Code does, however, write a
local JSONL transcript per session with real `usage` on every assistant turn. That's ground truth,
and this reads it.

Pairs with `runtime/build_journal.py` (which captures TIME + the step sequence). This supplies the
tokens those sessions burned, so a build's cost stops being a self-reported guess.

ATTRIBUTION IS THE HONEST PART. A transcript has no client field; a session is attributed by counting
mentions of each client's identifiers. So:
  • a session that mentions exactly one client is attributed to it,
  • a session mentioning several is reported as SHARED and listed under each, never split by
    invented percentages,
  • totals report attributed / shared / unattributed separately and never silently merge them.

Usage:
  python3 runtime/session_tokens.py                     # per-client summary
  python3 runtime/session_tokens.py --client sample-client   # sessions behind one client
  python3 runtime/session_tokens.py --sessions           # every session, largest first
  python3 runtime/session_tokens.py --json
"""
import os, sys, json, glob, datetime, collections

HOME = os.path.expanduser("~")
PROJECT_DIRS = [d for d in glob.glob(os.path.join(HOME, ".claude", "projects", "*YourCo*"))]

# Identifiers that mark a session as touching a client. Deliberately specific — generic words
# ("realty", "storm") would false-positive across unrelated sessions.
CLIENTS = {
    "sample-client":    ["sample-client", "Sample Client", "Client Owner", "field-to-quote", "field to quote"],
    "prospect-a":  ["prospect-a", "Sample Product", "storm-verified", "Prospect A", "stormverified"],
    "sample-realty":   ["sample-realty", "Sample Realty"],
}

# list prices $/MTok (input, output, cache_read, cache_write). Unknown models are counted in tokens
# but excluded from $ — never priced by guess.
PRICES = {
    # Current (2026-08). Older entries stay — this is a historical lookup, not a roster.
    "claude-opus-5": (5, 25, 0.5, 6.25), "claude-sonnet-5": (3, 15, 0.3, 3.75),
    "claude-opus-4-8": (5, 25, 0.5, 6.25), "claude-opus-4-7": (5, 25, 0.5, 6.25),
    "claude-opus-4-6": (5, 25, 0.5, 6.25), "claude-opus-4-5": (5, 25, 0.5, 6.25),
    "claude-sonnet-4-6": (3, 15, 0.3, 3.75), "claude-sonnet-4-5": (3, 15, 0.3, 3.75),
    "claude-haiku-4-5": (1, 5, 0.1, 1.25), "claude-fable-5": (10, 50, 1.0, 12.5),
}


def price_for(model):
    for k, v in PRICES.items():
        if model.startswith(k):
            return v
    return None


def scan_session(path):
    """Stream one transcript: token totals by model, client mentions, date range. Never loads whole."""
    tot = collections.defaultdict(lambda: dict(inp=0, out=0, cr=0, cw=0, turns=0))
    hits = collections.Counter()
    first = last = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                low = line.lower()
                for client, keys in CLIENTS.items():
                    if any(k in low for k in keys):
                        hits[client] += 1
                if '"usage"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                ts = rec.get("timestamp") or ""
                if ts:
                    first = min(first or ts, ts); last = max(last or ts, ts)
                msg = rec.get("message") or {}
                u = msg.get("usage") or rec.get("usage") or {}
                if not u:
                    continue
                m = msg.get("model") or rec.get("model") or "unknown"
                if m == "<synthetic>":   # Claude Code's own non-billed synthetic turns
                    continue
                t = tot[m]
                t["inp"] += u.get("input_tokens", 0) or 0
                t["out"] += u.get("output_tokens", 0) or 0
                t["cr"] += u.get("cache_read_input_tokens", 0) or 0
                t["cw"] += u.get("cache_creation_input_tokens", 0) or 0
                t["turns"] += 1
    except OSError:
        return None
    if not tot:
        return None
    cost, unpriced_models, unpriced_tok = 0.0, set(), 0
    for m, t in tot.items():
        p = price_for(m)
        if p:
            cost += (t["inp"] * p[0] + t["out"] * p[1] + t["cr"] * p[2] + t["cw"] * p[3]) / 1e6
        else:   # e.g. claude-opus-5 — list price not known to this tool; NEVER guessed
            unpriced_models.add(m)
            unpriced_tok += t["inp"] + t["out"] + t["cr"] + t["cw"]
    agg = dict(inp=sum(t["inp"] for t in tot.values()), out=sum(t["out"] for t in tot.values()),
               cr=sum(t["cr"] for t in tot.values()), cw=sum(t["cw"] for t in tot.values()),
               turns=sum(t["turns"] for t in tot.values()))
    agg["new"] = agg["inp"] + agg["cw"] + agg["out"]   # tokens genuinely produced/ingested once
    agg["total"] = agg["new"] + agg["cr"]                # raw billable volume (cache reads dominate)
    return {"file": os.path.basename(path), "path": path, "models": dict(tot), "agg": agg,
            "cost": round(cost, 2), "unpricedModels": sorted(unpriced_models),
            "unpricedTokens": unpriced_tok,
            "clients": [c for c, _ in hits.most_common() if hits[c] >= 3],  # >=3 mentions = real
            "mentions": dict(hits), "first": (first or "")[:10], "last": (last or "")[:10]}


def scan_all():
    out = []
    for d in PROJECT_DIRS:
        for p in glob.glob(os.path.join(d, "*.jsonl")):
            s = scan_session(p)
            if s:
                out.append(s)
    return sorted(out, key=lambda s: -s["agg"]["total"])


def main():
    sessions = scan_all()
    if "--json" in sys.argv:
        print(json.dumps(sessions, indent=1)); return
    if "--sessions" in sys.argv:
        print(f"{'tokens':>12}  {'$':>8}  {'turns':>6}  dates                clients")
        for s in sessions[:40]:
            print(f"{s['agg']['total']:>12,}  {s['cost']:>8,.2f}  {s['agg']['turns']:>6}  "
                  f"{s['first']}→{s['last']}  {','.join(s['clients']) or '—'}")
        return
    if "--client" in sys.argv:
        want = sys.argv[sys.argv.index("--client") + 1]
        rows = [s for s in sessions if want in s["clients"]]
        print(f"# {want} — {len(rows)} session(s) mentioning it\n")
        for s in rows:
            shared = [c for c in s["clients"] if c != want]
            print(f"  {s['agg']['total']:>11,} tok  ${s['cost']:>7,.2f}  {s['first']}→{s['last']}"
                  f"  {s['agg']['turns']:>4} turns" + (f"  ⚠ SHARED with {','.join(shared)}" if shared else ""))
        return

    solo, shared = collections.defaultdict(list), collections.defaultdict(list)
    for s in sessions:
        if len(s["clients"]) == 1:
            solo[s["clients"][0]].append(s)
        elif len(s["clients"]) > 1:
            for c in s["clients"]:
                shared[c].append(s)
    unattributed = [s for s in sessions if not s["clients"]]

    print(f"# Build token forensics — measured from {len(sessions)} Claude Code session transcripts")
    print(f"  source: ~/.claude/projects/*YourCo* · generated {datetime.date.today().isoformat()}")
    print("  Claude Code bills the SUBSCRIPTION, not the API — these tokens appear in no invoice.")
    print("  $ = list-price equivalent (what this would have cost on the API), not an amount billed.\n")
    print(f"{'client':<18}{'solo':>6}{'NEW tokens':>14}{'cache re-reads':>16}{'$eq':>10}   shared sessions")
    for c in CLIENTS:
        ss = solo.get(c, []); sh = shared.get(c, [])
        print(f"{c:<18}{len(ss):>6}{sum(x['agg']['new'] for x in ss):>14,}"
              f"{sum(x['agg']['cr'] for x in ss):>16,}{sum(x['cost'] for x in ss):>10,.2f}"
              f"   {len(sh)} sessions, {sum(x['agg']['new'] for x in sh):,} new tok")
    up = sorted({m for s in sessions for m in s["unpricedModels"]})
    upt = sum(s["unpricedTokens"] for s in sessions)
    print(f"\n  unattributed (no client mentioned): {len(unattributed)} sessions · "
          f"{sum(s['agg']['new'] for s in unattributed):,} new tokens")
    print(f"  ALL sessions: {sum(s['agg']['new'] for s in sessions):,} NEW tokens · "
          f"{sum(s['agg']['cr'] for s in sessions):,} cache re-reads · "
          f"${sum(s['cost'] for s in sessions):,.2f} list-price equivalent (priced models only)")
    if up:
        print(f"  ⚠ {upt:,} tokens ran on models this tool has no list price for ({', '.join(up)}) — "
              f"counted in tokens, EXCLUDED from $. The $ column is therefore a FLOOR, not a total.")
    print("\n  NEW tokens = uncached input + cache writes + output — what the work actually produced.")
    print("  Cache re-reads are ~95% of raw volume (the same context re-read each turn); real billing,")
    print("  but reporting them as 'tokens the build needed' would overstate the work by ~20x.")
    print("\n  Shared sessions are counted under EVERY client they touch and never split by an "
          "invented ratio — add them by judgment, not arithmetic.")


if __name__ == "__main__":
    main()
