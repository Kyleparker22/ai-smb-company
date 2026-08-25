#!/usr/bin/env python3
"""Warm-path routing with a price.

LinkedIn answers "who can introduce me." That is the easy half and it is worth
little on its own. The question that actually allocates a founder's week is:

    "Which SINGLE relationship, warmed this week, unlocks the most pipeline?"

The network is modelled as a circuit. Every edge has a conductance built from its
declared strength and from how long it has been since that person was actually
touched — warmth decays. Path conductance is multiplicative, so every extra hop
and every cold link costs. Reach to a company is its best path from the Founder.

The ranking is a counterfactual, not a centrality score: for each person, warm
THEM (reset their decay to a touch today) and recompute the whole network's
money-weighted reach. The delta is what that coffee is worth.

Run:
    python3 crm/warmpath.py           # the ranked weekly action
    python3 crm/warmpath.py --json
"""
import json, os, sys, math, datetime, heapq

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

HALFLIFE_DAYS = 120      # warmth halves every ~4 months without contact
UNKNOWN_WARMTH = 0.5     # never-touched / no date: the honest middle, and it is flagged
DEFAULT_STRENGTH = 2     # on a 1-3 scale, when an edge doesn't declare one
ROOT = "the Founder"
BENCH = {"parked"}


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def amount_of(d):
    v = float(d.get("value") or 0)
    return v or float(d.get("retainer") or 0) * 12 + float(d.get("buildFee") or 0)


def warmth(last_touch):
    d = _d(last_touch)
    if not d:
        return UNKNOWN_WARMTH, None
    age = max(0, (TODAY - d).days)
    return max(0.05, 0.5 ** (age / HALFLIFE_DAYS)), age


def build(data, warm_person=None):
    """Undirected conductance graph. warm_person = pretend we touched them today."""
    contacts = {}
    for p in data.get("contacts", []) or []:
        contacts.setdefault(p.get("name"), p)
    adj, meta = {}, {}
    for e in data.get("graph", {}).get("edges", []) or []:
        a, b = e.get("from"), e.get("to")
        if not a or not b:
            continue
        s = float(e.get("strength") or DEFAULT_STRENGTH) / 3.0
        lt = (contacts.get(b) or {}).get("lastTouch")
        w, age = warmth(lt)
        if warm_person and b == warm_person:
            w, age = 1.0, 0
        if warm_person and a == warm_person:
            w = max(w, 1.0)
        c = max(1e-6, min(1.0, s * w))
        adj.setdefault(a, []).append((b, c))
        adj.setdefault(b, []).append((a, c))
        meta[(a, b)] = {"rel": e.get("rel"), "strength": e.get("strength"), "warmth": round(w, 3),
                        "ageDays": age, "conductance": round(c, 4)}
    return adj, meta, contacts


def best_paths(adj, root=ROOT):
    """Max-product path from root to every node (Dijkstra on -log conductance)."""
    dist = {root: 0.0}
    prev = {}
    pq = [(0.0, root)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist.get(n, math.inf) + 1e-12:
            continue
        for m, c in adj.get(n, []):
            nd = d - math.log(c)
            if nd < dist.get(m, math.inf) - 1e-12:
                dist[m] = nd
                prev[m] = n
                heapq.heappush(pq, (nd, m))
    conduct = {n: math.exp(-v) for n, v in dist.items()}
    return conduct, prev


def path_to(prev, node, root=ROOT):
    out, cur, guard = [], node, 0
    while cur is not None and guard < 30:
        out.append(cur)
        if cur == root:
            break
        cur = prev.get(cur)
        guard += 1
    return list(reversed(out))


def reach(data, warm_person=None):
    """Money-weighted reach: Σ over companies of value × conductance of the best path to it."""
    adj, meta, contacts = build(data, warm_person)
    conduct, prev = best_paths(adj)
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    deals = {}
    for d in data.get("deals", []) or []:
        if d.get("stage") in BENCH:
            continue
        deals.setdefault(d.get("companyId"), []).append(d)

    rows, total = [], 0.0
    for cid, co in cos.items():
        if co.get("archived"):      # retired companies aren't targets — they'd sit in `orphans` forever
            continue
        money = sum(amount_of(d) for d in deals.get(cid, []))
        people = [p for p in data.get("contacts", []) or [] if p.get("companyId") == cid]
        best = (0.0, None)
        for p in people:
            c = conduct.get(p.get("name"), 0.0)
            if c > best[0]:
                best = (c, p.get("name"))
        rows.append({"companyId": cid, "company": co.get("name"), "money": money,
                     "conductance": round(best[0], 4), "via": best[1],
                     "path": path_to(prev, best[1]) if best[1] else [],
                     "stage": (deals.get(cid) or [{}])[0].get("stage")})
        total += money * best[0]
    return total, rows, meta, conduct, adj


def compute(data):
    base_total, rows, meta, conduct, adj = reach(data)
    people = sorted({n for n in adj if n != ROOT})

    ranked = []
    for person in people:
        t, _, _, _, _ = reach(data, warm_person=person)
        delta = t - base_total
        contact = next((p for p in data.get("contacts", []) or [] if p.get("name") == person), {})
        w, age = warmth(contact.get("lastTouch"))
        on_path = [r for r in rows if person in (r["path"] or [])]
        unlocked = sorted([r for r in on_path if r["money"] > 0], key=lambda r: -r["money"])
        ranked.append({
            "unlocksUnpriced": [r["company"] for r in on_path if r["money"] <= 0],
            "person": person, "deltaEV": round(delta), "reachNow": round(base_total),
            "warmth": round(w, 3), "lastTouch": contact.get("lastTouch") or None,
            "ageDays": age, "unknownWarmth": age is None,
            "role": contact.get("role") or "", "relationship": contact.get("relationship") or "",
            "unlocks": [{"company": r["company"], "money": r["money"], "stage": r["stage"]} for r in unlocked[:6]],
            "onPathsFor": len(unlocked),
        })
    ranked.sort(key=lambda r: -r["deltaEV"])

    priced = [r for r in rows if r["money"] > 0]
    unreachable = sorted([r for r in priced if r["conductance"] <= 0], key=lambda r: -r["money"])
    no_value = [r["company"] for r in rows if r["money"] <= 0 and r["conductance"] > 0]
    # A company nobody in the graph touches isn't cold — it's unmapped. That's a data gap
    # worth naming, because the router silently scores it zero either way.
    orphans = sorted([{"company": r["company"], "stage": r["stage"], "money": r["money"]}
                      for r in rows if not r["path"]], key=lambda r: -(r["money"] or 0))

    return {
        "generated": TODAY.isoformat(),
        "root": ROOT,
        "halfLifeDays": HALFLIFE_DAYS,
        "reachNow": round(base_total),
        "ranked": ranked,
        "routes": sorted(rows, key=lambda r: (-r["money"], -r["conductance"])),
        "unreachable": unreachable,
        "orphans": orphans,
        "pricedCompanies": len(priced), "totalCompanies": len(rows),
        "unpricedReachable": no_value,
        "honesty": (f"Reach is money × path conductance, so it only counts companies that carry a value in the CRM: "
                    f"{len(priced)} of {len(rows)}. Warmth decays on a {HALFLIFE_DAYS}-day half-life from each "
                    f"person's lastTouch; a contact with no lastTouch is scored at {UNKNOWN_WARMTH} and flagged "
                    "rather than assumed warm. The ranking is a counterfactual — warm this person today, recompute "
                    "the whole network — not a centrality score."),
    }


def main():
    with open(DATA) as f:
        data = json.load(f)
    r = compute(data)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Warm-path routing — network reach today: ${r['reachNow']:,} "
          f"({r['pricedCompanies']} of {r['totalCompanies']} companies carry a value)\n")
    print("Warm ONE of these this week — ranked by what it unlocks:")
    for x in r["ranked"][:10]:
        if x["deltaEV"] <= 0 and not x["unlocks"] and not x["unlocksUnpriced"]:
            continue
        age = "never touched" if x["unknownWarmth"] else f"{x['ageDays']}d cold"
        extra = f" · {len(x['unlocksUnpriced'])} unpriced" if x["unlocksUnpriced"] else ""
        print(f"  {x['person'][:26]:<26} +${x['deltaEV']:>7,}   warmth {x['warmth']:.2f} ({age})"
              f"   on {x['onPathsFor']} priced path(s){extra}")
        for u in x["unlocks"][:3]:
            print(f"      ↳ {u['company']} — ${u['money']:,.0f} ({u['stage']})")
    if r["unreachable"]:
        print("\nPriced but NO warm path exists (these are cold, whatever the CRM says):")
        for u in r["unreachable"]:
            print(f"  {u['company']} — ${u['money']:,.0f}")
    if r["orphans"]:
        print(f"\nUnmapped — {len(r['orphans'])} company(ies) have no person in the warm graph at all "
              "(a graph gap, not a cold lead):")
        for o in r["orphans"][:8]:
            tail = f" — ${o['money']:,.0f}" if o["money"] else ""
            print(f"  {o['company']}{tail}")
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
