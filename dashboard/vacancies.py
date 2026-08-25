#!/usr/bin/env python3
"""Vacancies — the org chart that grows from observed work instead of from planning.

Every company's org chart is drawn in advance and then argued about. yourco's work is all
in files: what escalated to the Founder, what nobody picked up, what has no owner, what an agent
owns on paper but keeps handing back. That is a labor-demand signal, and it can be read.

WHAT IT DOES.  Clusters the OS's genuinely-open work by domain, checks each cluster against
the roster and the activation triggers, and returns one of three verdicts:

  absorb    a LIVE agent already owns this domain, yet the work still lands on the Founder.
            The fix is that agent's scope or loop — not a new hire. This is usually the
            most valuable finding and the one a planning-first org chart never surfaces.
  activate  a built-but-dormant or planned agent covers it. The proposal is its activation
            trigger, quoted from where that trigger already lives.
  hire      nothing on the roster covers it. A new function is drafted — scope, first loop,
            and the wiring checklist to follow.

WHAT IT WILL NOT DO.  Propose only. It creates no agent, edits no roster, and files no task.
Org shape is the Founder's, exactly as goals are — the same rule that governs Melanie's initiative
loop, which may propose missions but never self-adopt them. It also does not name new
agents: naming is the Founder's, so a `hire` proposal describes the FUNCTION and leaves the name blank.

NOISE FLOOR.  A cluster is only reported when it has real weight (`MIN_ITEMS` open items, or
a critical item aged past `CRIT_AGE_DAYS`). Everything below the floor is counted and
reported as "below the floor", never silently dropped — a suppressed signal that nobody
knows was suppressed is how the OS fails by not noticing absence.

Sources: The Board (needs-you · missing · blocked), loop health from dashboard/refresh.py,
04_agent_roster.md, runtime/activation-triggers.md. Read-only. GET /api/vacancies.
"""
import os, re, sys, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: HERE is CODE; data resolves under DATA_DIR / the env-aware ROOT.
# Enforced by playground/check_isolation.py.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "dashboard") if os.environ.get("YOURCO_DATA_ROOT") else HERE
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MIN_ITEMS = 3          # a cluster needs this many open items to be worth a proposal…
CRIT_AGE_DAYS = 30     # …or one critical item that has been sitting this long
OPEN_STATES = ("needs-you", "missing", "blocked")

# Work is bucketed by WORK_RX (matched against the item's own text). Owners are found with
# ROLE_RX (matched against the agent's ROLE — the short, precise line in the roster).
#
# These are two different vocabularies on purpose. The first version matched agents with the
# same loose regex used on the work, against the agent's whole role+scope blob, and it put
# Reilly (outbound) in charge of Legal and Runtime because his scope prose happens to mention
# a gate and a connector. A long scope paragraph will match almost any domain; a role line
# won't. Role is the signal, scope is only a fallback — and a fallback match is labelled weak.
DOMAINS = [
    ("Money & runway",
     r"\b(?:cash|runway|burn|invoice|billing|payment|spend|budget|margin|revenue|financ|"
     r"quickbooks|bookkeep|tax|receivable|pric|stripe|card|refund)",
     r"\b(?:financ|account|ar\b|back.?office|bookkeep|pricing)"),
    ("Legal & compliance",
     r"\b(?:counsel|legal|attorney|contract|agreement|classif|complian|licens|securit|"
     r"insurance|liabilit|gate|nda|terms)",
     r"\b(?:legal|complian|contract|security|risk)"),
    ("Runtime & platform",
     r"\b(?:runtime|systemd|timer|vps|deploy|daemon|loop|connector|api key|credential|2fa|"
     r"infrastructur|host|server|backup|dark|cadence)",
     r"\b(?:platform|template|observab|ops\b|infrastructur)"),
    ("Outbound & pipeline",
     r"\b(?:outbound|outreach|prospect|lead|cold|instantly|campaign|warm|intro|pipeline|"
     r"deal|follow.?up|sourcing)",
     r"\b(?:outbound|sourcing|campaign|intent|lead|sales)"),
    ("Client delivery",
     r"\b(?:client|engagement|deliver|onboard|go.?live|proposal|southern|Client Owner|storm|demo|"
     r"audit|kickoff)",
     r"\b(?:deliver|onboard|customer health|audit|expansion|account growth)"),
    ("Brand, content & site",
     r"\b(?:brand|content|site|website|copy|post|carousel|video|design|seo|aeo|social|"
     r"collateral)",
     r"\b(?:brand|content|web|video|collateral|social|visibility|copy|messaging)"),
    ("CRM & data",
     r"\b(?:crm|data\.json|dedupe|hygiene|contact record|field|stage|attribution|duplicate)",
     r"\b(?:crm|revops|data)"),
    ("People & partners",
     r"\b(?:connector|advisor|partner|referral|recruit|roster|commission|equity|phantom|"
     r"downline)",
     r"\b(?:people|internal|expansion|account growth|chief of staff)"),
]


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _domain_of(text):
    """Bucket one work item. Best match wins — most distinct keyword hits, not first hit,
    so an item mentioning one stray word doesn't outrank the domain it's actually about."""
    t = (text or "").lower()
    best, best_n = None, 0
    for name, work_rx, _role_rx in DOMAINS:
        n = len(set(re.findall(work_rx, t)))
        if n > best_n:
            best, best_n = name, n
    return best


def _roster():
    """slug -> {name, role, scope, status, planned, trigger}. Roster prose from refresh
    (04_agent_roster.md), live/built status from dashboard/data.json."""
    out = {}
    try:
        import refresh
        out = {k: dict(v) for k, v in refresh._roster().items()}
    except Exception:
        pass
    try:
        import json
        with open(os.path.join(DATA_DIR, "data.json"), encoding="utf-8") as f:
            for a in (json.load(f).get("agents") or []):
                slug = (a.get("name") or "").lower()
                d = out.setdefault(slug, {"name": a.get("name"), "role": a.get("role") or "",
                                          "scope": "", "trigger": "", "planned": False})
                d["status"] = a.get("status")
                d.setdefault("role", a.get("role") or "")
    except Exception:
        pass
    for d in out.values():
        d.setdefault("status", "planned" if d.get("planned") else "built")
    return out


SCOPE_FALLBACK_MIN = 3  # distinct scope hits needed when no role matches at all


def _agents_for(role_rx, work_rx, roster):
    """Who owns this domain. Role match is the signal; a scope-only match is a labelled
    fallback, never treated as equivalent. Returns (live, dormant), best match first."""
    strong, weak = [], []
    for slug, d in roster.items():
        role = str(d.get("role") or "").lower()
        scope = " ".join(str(d.get(k) or "") for k in ("scope", "trigger", "statusNote")).lower()
        role_hits = len(set(re.findall(role_rx, role)))
        rec = {"slug": slug, "name": d.get("name") or slug.title(), "role": d.get("role"),
               "status": d.get("status"), "trigger": d.get("trigger")}
        if role_hits:
            strong.append((role_hits, {**rec, "match": "role"}))
            continue
        scope_hits = len(set(re.findall(work_rx, scope)))
        if scope_hits >= SCOPE_FALLBACK_MIN:
            weak.append((scope_hits, {**rec, "match": "scope (inferred — no role match)"}))
    # ties break on slug so the named owner is stable run to run, never dict-order luck
    picked = [a for _, a in sorted(strong, key=lambda x: (-x[0], x[1]["slug"]))] or \
             [a for _, a in sorted(weak, key=lambda x: (-x[0], x[1]["slug"]))]
    live = [a for a in picked if a.get("status") == "live"]
    dormant = [a for a in picked if a.get("status") != "live"]
    return live, dormant


def _activation_trigger(slug):
    """Quote the agent's activation trigger from where it already lives."""
    txt = _read("runtime/activation-triggers.md")
    m = re.search(r"^\|\s*\*{0,2}" + re.escape(slug.title()) + r"\*{0,2}\s*\|(.+)$", txt,
                  re.M | re.I)
    if m:
        cells = [c.strip() for c in m.group(1).split("|")]
        return re.sub(r"[*`]", "", " · ".join(c for c in cells if c))[:300]
    return None


def _open_items():
    try:
        import board
        return [i for i in (board.build().get("items") or []) if i.get("state") in OPEN_STATES]
    except Exception:
        return []


def _loop_gaps():
    """Stale / never-run loops are unowned or failing work — a labor signal like any other."""
    try:
        import refresh
        return [l for l in (refresh.derive().get("loops") or [])
                if l.get("kind") == "internal" and l.get("health") in ("stale", "never")]
    except Exception:
        return []


# --------------------------------------------------------------------------
# Retirement — the direction this org chart didn't have (added 2026-08-13)
#
# vacancies proposed hiring and activating and nothing proposed the opposite, which makes a
# roster that can only grow. Modelled on Entra Agent ID's lifecycle rule: an agent should not
# hold access longer than it needs it. Every agent gets a review date from
# runtime/agent-registry.json §agent_review; one that has produced nothing by it is PROPOSED for
# retirement. Proposes only — retiring an agent is the Founder's call, exactly as hiring one is.
#
# "Produced nothing" is read from evidence, never from an opinion: committed loop artifacts and
# the trust ledger. An agent with no loops armed and no recorded actions has, on the record,
# done nothing — and saying so is the point.
# --------------------------------------------------------------------------
def _registry_review():
    import json as _json
    try:
        reg = _json.loads(_read("runtime/agent-registry.json") or "{}")
    except ValueError:
        reg = {}
    r = reg.get("agent_review") or {}
    return {
        "defaultDays": r.get("defaultDays") or 90,
        "graceDays": r.get("graceDays") or 30,
        "sponsors": r.get("sponsors") or {},
        "reviewBy": r.get("reviewBy") or {},
        "exempt": r.get("exempt") or {},
        "present": bool(r),
    }


def _agent_production():
    """slug -> {lastArtifact, artifacts, ledgerActions, loops}. Evidence only."""
    out = {}
    try:
        import refresh
        det = refresh.derive().get("agentDetail") or {}
        for slug, d in det.items():
            recent = d.get("recent") or []
            out[slug] = {
                "artifacts": len(recent),
                "lastArtifact": max((r.get("date") or "" for r in recent), default="") or None,
                "loops": len(d.get("loops") or []),
                "planned": bool(d.get("planned")),
                "name": d.get("name") or slug.title(),
                "role": d.get("role") or "",
            }
    except Exception:
        pass
    try:  # the trust ledger counts actions the loop artifacts don't cover
        import sys as _s
        _s.path.insert(0, os.path.join(ROOT, "runtime"))
        from ledger import Ledger
        for e in Ledger("loops/_trust/actions.jsonl").read()["events"]:
            slug = (e.get("agent") or "").lower()
            if slug in out:
                out[slug]["ledgerActions"] = out[slug].get("ledgerActions", 0) + 1
    except Exception:
        pass

    # Third source, and it is load-bearing: several agents produce into agents/<slug>/ rather
    # than loops/ — Reed's video productions, Webb's pages, Pickle's collateral, Luka's brand
    # work. Counting only loop artifacts proposed all of them for retirement while their real
    # output sat in the repo. Proposing to retire an agent that demonstrably works is the error
    # that would make this whole surface untrustworthy, so workspace commits count as evidence.
    for slug in list(out):
        first = slug.split()[0]
        d = os.path.join(ROOT, "agents", first)
        if not os.path.isdir(d):
            continue
        try:
            log = subprocess.run(["git", "log", "--format=%ad", "--date=short", "--max-count=60",
                                  "--", f"agents/{first}/"],
                                 cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.split()
        except Exception as e:
            # Narrow, and recorded: a broad silent except here already hid a missing `import
            # subprocess` long enough to propose retiring two agents that demonstrably work.
            out[slug]["evidenceError"] = f"{type(e).__name__}: {e}"[:120]
            log = []
        # The OLDEST commit is the folder coming into existence — every agents/<slug>/ was created
        # in the same 2026-08-07 bulk move out of clients/. Counting it made all 27 agents look
        # productive and dropped the retire list to zero, which is the mirror of the bug above.
        # Only commits after the folder's creation are work.
        if len(log) > 1:
            work = sorted(log)[1:]   # drop the folder-creation commit
            out[slug]["workspaceCommits"] = len(work)
            out[slug]["lastWorkspace"] = max(work)
        elif log:
            out[slug]["workspaceCommits"] = 0
            out[slug]["folderOnly"] = log[0]
    return out


def retirements(roster, today=None):
    today = today or datetime.date.today()
    rv = _registry_review()
    prod = _agent_production()
    rows = []
    for slug, d in sorted(roster.items()):
        p = prod.get(slug, {})
        loop_out = (p.get("artifacts", 0) or 0) + (p.get("ledgerActions", 0) or 0)
        workspace = p.get("workspaceCommits", 0) or 0
        produced = loop_out + workspace
        armed = p.get("loops", 0) or 0
        status = d.get("status") or ("planned" if d.get("planned") else "built")
        # exempt is keyed by first name ("melanie"), the roster may carry a full name
        # ("Melanie Smooter") — match on the first token so a surname can't defeat an exemption
        first = slug.split()[0]
        last_out = max([x for x in (p.get("lastArtifact"), p.get("lastWorkspace")) if x], default=None)

        if first in rv["exempt"] or slug in rv["exempt"]:
            verdict, why = "exempt", rv["exempt"].get(first) or rv["exempt"][slug]
        elif produced:
            src = []
            if loop_out:
                src.append(f"{loop_out} loop/ledger")
            if workspace:
                src.append(f"{workspace} commits in agents/{first}/")
            verdict, why = "keep", f"{' · '.join(src)}, last {last_out or 'n/a'}"
        elif status == "planned":
            verdict, why = "not yet born", "planned, never activated — nothing to retire"
        elif armed:
            verdict, why = "watch", (f"{armed} loop(s) armed but no artifact recorded — that is a "
                                     f"broken loop, not a redundant agent; fix before retiring")
        else:
            verdict, why = "propose retire", (
                "no armed loop and no output recorded since the 2026-08-07 workspace "
                "reorganisation — read this as 'nothing since 08-07', not 'never': work done "
                "before the move lived under clients/<agent>/ and this window does not reach it")
        rows.append({
            "slug": slug, "name": d.get("name") or slug.title(), "role": d.get("role") or "",
            "status": status, "produced": produced, "armedLoops": armed,
            "lastArtifact": last_out,
            "reviewBy": rv["reviewBy"].get(slug),
            "sponsor": rv["sponsors"].get(slug) or rv["sponsors"].get("_default") or "unassigned",
            "verdict": verdict, "why": why,
        })
    order = {"propose retire": 0, "watch": 1, "not yet born": 2, "keep": 3, "exempt": 4}
    rows.sort(key=lambda r: (order.get(r["verdict"], 9), r["name"]))
    return {
        "rows": rows,
        "counts": {k: sum(1 for r in rows if r["verdict"] == k) for k in order},
        "policy": {"defaultDays": rv["defaultDays"], "graceDays": rv["graceDays"],
                   "configured": rv["present"]},
        "note": ("Proposes only — retiring an agent is the Founder's call, the same rule that governs "
                 "hiring one. Output is read from three evidence sources, never from an opinion: "
                 "committed loop artifacts, the trust ledger, and commits under agents/<slug>/. "
                 "An agent with loops armed but no artifacts is deliberately NOT proposed for "
                 "retirement — that is a broken loop, and retiring the agent would hide the bug "
                 "instead of fixing it."),
        "evidenceWindow": {
            "startsAt": "2026-08-07",
            "why": "agents/ was created by the 2026-08-07 move out of clients/, so each folder's "
                   "oldest commit is its creation and is excluded (counting it made all 27 look "
                   "productive). Output produced BEFORE the move lived under clients/<agent>/ and "
                   "is not visible to this window — a 'propose retire' therefore means 'nothing "
                   "since 08-07', which is a weaker claim than 'never' and must be read that way.",
        },
    }


def build():
    roster = _roster()
    items = _open_items()
    loops = _loop_gaps()

    clusters = {}
    unclassified = []
    for it in items:
        text = f"{it.get('title', '')} {it.get('detail', '')} {it.get('lane', '')}"
        dom = _domain_of(text)
        if not dom:
            unclassified.append(it.get("title", "")[:90])
            continue
        c = clusters.setdefault(dom, {"domain": dom, "items": [], "loops": [], "critical": 0,
                                      "maxAge": 0, "owners": set(), "lanes": set()})
        c["items"].append({"title": (it.get("title") or "")[:150], "state": it.get("state"),
                           "age": it.get("age"), "sev": it.get("sev"),
                           "owner": it.get("owner"), "source": it.get("source")})
        if (it.get("sev") or "") in ("critical", "high"):
            c["critical"] += 1
        c["maxAge"] = max(c["maxAge"], it.get("age") or 0)
        if it.get("owner"):
            c["owners"].add(it["owner"])
        if it.get("lane"):
            c["lanes"].add(it["lane"])

    for l in loops:
        dom = _domain_of(f"{l.get('loop', '')} {l.get('note', '')}") or "Runtime & platform"
        c = clusters.setdefault(dom, {"domain": dom, "items": [], "loops": [], "critical": 0,
                                      "maxAge": 0, "owners": set(), "lanes": set()})
        c["loops"].append({"loop": l.get("loop"), "health": l.get("health"),
                           "note": l.get("note"), "last": l.get("lastArtifact")})

    rx_by_domain = {name: (work_rx, role_rx) for name, work_rx, role_rx in DOMAINS}
    out, below = [], []
    for dom, c in clusters.items():
        weight = len(c["items"]) + len(c["loops"])
        qualifies = weight >= MIN_ITEMS or (c["critical"] and c["maxAge"] >= CRIT_AGE_DAYS)
        work_rx, role_rx = rx_by_domain[dom]
        live, dormant = _agents_for(role_rx, work_rx, roster)

        if live:
            others = (f" ({len(live) - 1} other live agent{'' if len(live) == 2 else 's'} also "
                      f"match{'es' if len(live) == 2 else ''} this domain)") if len(live) > 1 else ""
            verdict, headline = "absorb", (
                f"{live[0]['name']} already owns this domain, and {weight} open item"
                f"{'' if weight == 1 else 's'} still sit{'s' if weight == 1 else ''} on the Founder. "
                f"The gap is scope or cadence, not headcount.{others}")
            proposal = {
                "kind": "extend an existing agent",
                "agent": live[0]["name"],
                "what": f"Widen {live[0]['name']}'s loop to pick this work up, or add a "
                        f"recurring pass over it — see .claude/skills/add-runtime-loop/.",
                "name": None,
            }
        elif dormant:
            d0 = dormant[0]
            verdict, headline = "activate", (
                f"{d0['name']} is on the roster but not live, while {weight} open item"
                f"{'' if weight == 1 else 's'} in this domain wait.")
            proposal = {
                "kind": "activate a dormant agent",
                "agent": d0["name"],
                "what": (_activation_trigger(d0["slug"]) or d0.get("trigger")
                         or "no activation trigger recorded — write one first "
                            "(runtime/activation-triggers.md)"),
                "wiring": ".claude/skills/wire-new-agent/ (13 steps; half-done wiring is the "
                          "known failure mode)",
                "name": None,
            }
        else:
            verdict, headline = "hire", (
                f"Nothing on the roster covers this domain, and {weight} open item"
                f"{'' if weight == 1 else 's'} have nowhere to go but the Founder.")
            proposal = {
                "kind": "a function the roster is missing",
                "agent": None,
                "name": None,  # naming agents is the Founder's — deliberately left blank
                "what": f"Scope: own {dom.lower()} end to end — triage what arrives, act inside "
                        f"an earned rung, escalate the rest. First loop: a recurring pass over "
                        f"the sources these {weight} items came from.",
                "wiring": ".claude/skills/wire-new-agent/ then .claude/skills/add-runtime-loop/",
            }

        row = {
            "domain": dom, "weight": weight, "openItems": len(c["items"]),
            "staleLoops": len(c["loops"]), "critical": c["critical"], "maxAgeDays": c["maxAge"],
            "lanes": sorted(c["lanes"]), "namedOwners": sorted(c["owners"]),
            "liveAgents": live, "dormantAgents": dormant,
            "verdict": verdict, "headline": headline, "proposal": proposal,
            "evidence": sorted(c["items"], key=lambda i: -(i["age"] or 0))[:8],
            "evidenceLoops": c["loops"][:6],
        }
        (out if qualifies else below).append(row)

    order = {"hire": 0, "activate": 1, "absorb": 2}
    out.sort(key=lambda r: (order.get(r["verdict"], 9), -r["weight"]))
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "clusters": out,
        "belowFloor": [{"domain": r["domain"], "weight": r["weight"], "verdict": r["verdict"]}
                       for r in below],
        "unclassified": unclassified[:12],
        "unclassifiedCount": len(unclassified),
        "counts": {k: sum(1 for r in out if r["verdict"] == k) for k in order},
        "retire": retirements(roster),
        "scanned": {"openItems": len(items), "staleLoops": len(loops),
                    "rosterAgents": len(roster)},
        "floor": {"minItems": MIN_ITEMS, "criticalAgeDays": CRIT_AGE_DAYS},
        "note": ("Proposals only — nothing here creates an agent, edits the roster, or files a "
                 "task. Org shape is the Founder's. New-function proposals are deliberately unnamed: "
                 "naming agents is the Founder's too. Clusters below the noise floor are counted, not "
                 "hidden, and items that matched no domain are listed so the classifier's own "
                 "blind spots stay visible."),
    }


if __name__ == "__main__":
    d = build()
    print(f"VACANCIES — scanned {d['scanned']['openItems']} open items + "
          f"{d['scanned']['staleLoops']} stale loops against {d['scanned']['rosterAgents']} agents")
    print(f"  {d['counts']['hire']} hire · {d['counts']['activate']} activate · "
          f"{d['counts']['absorb']} absorb   ({len(d['belowFloor'])} below the floor)\n")
    for c in d["clusters"]:
        print(f"[{c['verdict'].upper()}] {c['domain']}  — {c['weight']} open "
              f"({c['critical']} critical, oldest {c['maxAgeDays']}d)")
        print(f"    {c['headline']}")
        p = c["proposal"]
        print(f"    -> {p['kind']}" + (f": {p['agent']}" if p.get("agent") else ""))
        print(f"       {p['what'][:150]}")
        for e in c["evidence"][:3]:
            print(f"       · [{e['state']}] {e['title'][:78]}")
        print()
    if d["unclassifiedCount"]:
        print(f"unclassified ({d['unclassifiedCount']}): " +
              "; ".join(d["unclassified"][:4]))
