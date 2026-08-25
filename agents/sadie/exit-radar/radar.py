#!/usr/bin/env python3
"""Exit Radar — yourco's sourcing platform for SMBs in ownership transition.

The platform behind `decisions/2026-07-29_exit-flip-targeting-lane.md`: an
owner who has listed their business for sale (or listed and failed to sell)
has published a timestamped "I want out" — the purest owner-drain signal that
exists, and owner-drain is already an Audit scoring axis. The pitch is
two-sided by decision: *don't sell — the OS removes the reason you're
selling*, or *sell for more — the OS removes the owner-dependence that's
discounting your multiple*. Every conversation has a win condition.

WHAT THIS PLATFORM IS NOT (the rails it must never leave)
---------------------------------------------------------
- **No scraping. Ever.** BizBuySell and its peers are ToS-gated commercial
  databases (Rafi posture; `rejections/2026-07-05_detection-evasion-scrapers`
  is a standing bound). This tool contains NO fetcher. Candidates arrive from
  compliant research (public news, Google Alerts RSS, WebSearch) or from a
  HUMAN reading a listing site by hand — and a candidate whose provenance URL
  is on a ToS-gated platform is refused unless it is explicitly marked
  `human_read`, the attestation that a person, not a program, read the page.
- **Never a fake buyer.** The sleazy version of this platform poses as an
  acquisition inquiry to get past the broker, then pitches services. yourco
  states plainly what it is in every draft; the pitch screen refuses any
  draft that expresses buying interest.
- **Nothing sends.** Drafts are staged for the existing cold pipeline
  (Sadie hand-off schema → `runtime/sourcing.py --sadie-json`) and every
  send waits on the launch-gate like all outbound. the Founder sends; agents draft.
- **No invented numbers.** Financials exist on a candidate only if the
  listing/article stated them (recorded with provenance). A draft never
  cites a figure about THEIR business that they didn't publish, and never
  makes a growth promise about ours (credibility gate: qualitative only,
  pre-proof).

ROUTING (per the decision)
--------------------------
  owner-reachable + qualified  -> exit-themed cold campaign (Reilly stages,
                                  Michelle's two-sided copy, CRM on reply)
  broker-anonymized            -> Bird, as partner-category-9 input ("send us
                                  your unsellable listings") — NOT outreach
  sold / under contract        -> the ETA lane (the BUYER is the prospect —
                                  `decisions/2026-06-16_eta-company-os-offering`)

Stdlib only. Store: JSON files in ./data (committed — yourco pipeline data,
same posture as crm/).
"""
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("EXIT_RADAR_DATA", HERE / "data"))

# ------------------------------------------------------------------ storage

def now():
    return datetime.now(timezone.utc)


def iso(dt=None):
    return (dt or now()).replace(microsecond=0).isoformat()


def nid(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def load(name, default=None):
    p = DATA / f"{name}.json"
    if not p.exists():
        return default if default is not None else []
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return default if default is not None else []


def save(name, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = (DATA / f"{name}.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(rows, indent=1))
    tmp.replace(DATA / f"{name}.json")


# ------------------------------------------------------------------ taxonomy

# Listing statuses, ranked by signal quality. The decision's read: an EXPIRED
# listing (tried to leave, couldn't) beats a fresh one — the owner-dependence
# discount has already been demonstrated by the market.
STATUSES = {
    "expired":         dict(score=40, label="Listed and didn't sell",
                            why="the market already told them the business is owner-dependent"),
    "relisted":        dict(score=34, label="Relisted",
                            why="second attempt — motivation confirmed twice"),
    "listed":          dict(score=26, label="Currently listed",
                            why="a public, timestamped 'I want out'"),
    "retirement_news": dict(score=22, label="Retirement/succession announcement",
                            why="usually owner-direct and pre-broker — earliest touch"),
    "under_contract":  dict(score=12, label="Under contract",
                            why="seller side closing; the BUYER becomes the ETA prospect"),
    "sold":            dict(score=10, label="Sold",
                            why="new owner, change-ready on day one — pure ETA lane"),
}

CONTACT_PATHS = ("owner_direct", "broker", "anonymized")

STAGES = ("found", "qualified", "staged", "broker_referral", "eta_lane",
          "dismissed")

# ToS-gated commercial listing databases: a human may READ them; software may
# not fetch them, and a candidate citing one must carry the human_read
# attestation. This list is a floor, not a ceiling — unknown broker platforms
# get the same treatment by the `marketplace` heuristic below.
TOS_GATED_DOMAINS = {
    "bizbuysell.com", "bizquest.com", "businessesforsale.com",
    "businessbroker.net", "dealstream.com", "loopnet.com", "flippa.com",
    "sunbeltnetwork.com", "tworld.com", "transworldba.com",
    "murphybusiness.com", "vikingmergers.com",
}


def _domain(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", (url or "").lower())
    return m.group(1) if m else ""


def is_tos_gated(url):
    d = _domain(url)
    return any(d == g or d.endswith("." + g) for g in TOS_GATED_DOMAINS)


# ------------------------------------------------------------------ intake

REQUIRED_PROVENANCE = ("url", "source")


def add_candidate(body, actor="human:the Founder"):
    """One candidate in. Provenance is mandatory and structural — where the
    signal came from, when, and whether a human read it. Refusals are the
    compliance posture expressed as code."""
    name = (body.get("name") or "").strip()
    if not name:
        return None, "a business name (or the listing's own anonymized label) is required"
    prov = body.get("provenance") or {}
    missing = [k for k in REQUIRED_PROVENANCE if not (prov.get(k) or "").strip()]
    if missing:
        return None, (f"provenance is mandatory — missing {missing}. We don't "
                      "work signals we can't say how we found")
    if is_tos_gated(prov["url"]) and not prov.get("human_read"):
        return None, ("that URL is a ToS-gated listing platform — it may only "
                      "enter this system with human_read=true, the attestation "
                      "that a PERSON read the page. Software never fetches it")
    status = body.get("status", "listed")
    if status not in STATUSES:
        return None, f"status must be one of {sorted(STATUSES)}"
    contact_path = body.get("contact_path", "anonymized")
    if contact_path not in CONTACT_PATHS:
        return None, f"contact_path must be one of {CONTACT_PATHS}"

    with_lock = load("candidates")
    dupe = next((c for c in with_lock
                 if c["name"].lower() == name.lower()
                 and c.get("location", "").lower() == (body.get("location") or "").lower()
                 and c["stage"] != "dismissed"), None)
    if dupe:
        dupe.setdefault("signals", []).append(
            {"at": iso(), "status": status, "provenance": prov})
        # A repeat signal upgrades the status when the new one ranks higher.
        if STATUSES[status]["score"] > STATUSES[dupe["status"]]["score"]:
            dupe["status"] = status
        save("candidates", with_lock)
        return dupe, None

    row = {
        "id": nid("xc"), "at": iso(), "name": name[:120],
        "industry": (body.get("industry") or "")[:60],
        "location": (body.get("location") or "")[:80],
        "status": status, "contact_path": contact_path,
        "owner_name": (body.get("owner_name") or "")[:80],
        "contact": (body.get("contact") or "")[:120],
        "broker": (body.get("broker") or "")[:120],
        # Financials only as PUBLISHED — never inferred, never estimated.
        "published_financials": body.get("published_financials") or None,
        "note": (body.get("note") or "")[:600],
        "provenance": {"url": prov["url"][:400], "source": prov["source"][:120],
                       "accessed": prov.get("accessed") or iso()[:10],
                       "human_read": bool(prov.get("human_read"))},
        "signals": [], "stage": "found", "stage_at": iso(),
        "drafts": [], "dnc": None, "added_by": actor,
    }
    # Routing by construction, not by discipline:
    if status in ("sold", "under_contract"):
        row["stage"] = "eta_lane"
        row["route_why"] = ("the seller is leaving; the BUYER is the prospect "
                            "— ETA/Company-OS lane, not exit-flip outreach")
    elif contact_path == "anonymized":
        row["stage"] = "broker_referral"
        row["route_why"] = ("no reachable owner — this is partner-category-9 "
                            "input for Bird, never anonymous outreach")
    with_lock.append(row)
    save("candidates", with_lock)
    return row, None


def import_candidates(body, actor="human:the Founder"):
    """Bulk import (a research sweep's output, a hand-read listing session).
    Same refusals per row, reported not silently dropped."""
    rows = body.get("candidates") or []
    if not rows:
        return None, "no candidates in the import"
    report = {"added": 0, "merged": 0, "refused": [], "by_stage": {}}
    before = {c["id"] for c in load("candidates")}
    for r in rows[:200]:
        row, err = add_candidate(r, actor=actor)
        if err:
            report["refused"].append({"name": r.get("name", "?"), "why": err})
            continue
        if row["id"] in before:
            report["merged"] += 1
        else:
            report["added"] += 1
            before.add(row["id"])
        report["by_stage"][row["stage"]] = report["by_stage"].get(row["stage"], 0) + 1
    return report, None


# ------------------------------------------------------------------ scoring

def score(c):
    """Rank for triage order. Recorded facts only; every component named so
    the console can show WHY a candidate sits where it sits."""
    parts = []
    base = STATUSES[c["status"]]["score"]
    parts.append((STATUSES[c["status"]]["label"], base))
    if c["contact_path"] == "owner_direct":
        parts.append(("owner directly reachable", 20))
    elif c["contact_path"] == "broker":
        parts.append(("reachable through a named broker", 8))
    if len(c.get("signals", [])) >= 1:
        parts.append((f"{len(c['signals'])} repeat signal(s)", 6 * len(c["signals"])))
    if c.get("published_financials"):
        parts.append(("financials published — conversation has numbers", 5))
    try:
        age = (now() - datetime.fromisoformat(c["at"])).days
        if age <= 14:
            parts.append(("fresh (≤14d)", 5))
    except ValueError:
        pass
    return {"total": sum(p[1] for p in parts), "parts": parts}


# ------------------------------------------------------------------ stages

def set_stage(cid, to, actor="human:the Founder", why=None):
    if to not in STAGES:
        return None, f"stage must be one of {STAGES}"
    rows = load("candidates")
    c = next((x for x in rows if x["id"] == cid), None)
    if not c:
        return None, "not found"
    if c.get("dnc"):
        return None, "they asked not to be contacted — permanent"
    if to == "staged" and c["contact_path"] == "anonymized":
        return None, ("an anonymized listing cannot be staged for outreach — "
                      "there is nobody to honestly address. Route: broker_referral")
    if to == "staged" and c["stage"] != "qualified":
        return None, "only a qualified candidate stages — review comes first"
    c["stage"] = to
    c["stage_at"] = iso()
    if why:
        c["stage_why"] = str(why)[:300]
    save("candidates", rows)
    return c, None


def mark_dnc(cid):
    rows = load("candidates")
    c = next((x for x in rows if x["id"] == cid), None)
    if not c:
        return None, "not found"
    c["dnc"] = iso()
    c["stage"] = "dismissed"
    save("candidates", rows)
    return c, None


# ------------------------------------------------------------------ drafts

# The two-sided pitch, exactly per the decision's guardrails:
#  - never "walk away day one" (autonomy is EARNED — the canonical framing)
#  - no growth promises pre-proof (qualitative only)
#  - no posing as a buyer, honest disclosure always
#  - no numbers about THEIR business unless they published them
# Three-sided since 2026-08-17 (`decisions/2026-08-17_succession-three-play-map`):
# don't sell / sell for more / hand it off without selling. The third side is
# the succession-readiness angle — most owners' real problem is that NO path
# (sale, family, employees, keep) survives the business's dependence on them.
EXIT_PITCH_TEMPLATE = """Hi {first},

I saw {signal_line} — so I'll be straight about who's writing: I run yourco,
we build and operate AI systems for small businesses, and we are not buyers.

Owners usually get to a listing by one of three roads, and we're useful on
all of them:

If you're selling because the business can't run without you — that's the
thing we remove. Your week becomes a few hours of approvals, trending toward
zero as the system earns it, while the business keeps its cash flow. Some
owners find they no longer want to sell.

If you genuinely want the exit — owner-dependence is the classic discount on
a small-business multiple. A business that demonstrably runs without its
owner is an easier sale at a better price.

And if what you'd really prefer is handing it on — to family, a manager, or
your own people — the same dependence is what makes that handoff fail. A
business that runs without you is one a successor can actually
take.{financials_line}

Twenty minutes to hear which of those is actually you? If the answer is "I
just want the check, leave me alone," say so and I won't write again.

[YOUR SIGN-OFF]
[PHYSICAL MAILING ADDRESS — required on commercial email]"""

BROKER_INTRO_TEMPLATE = """Hi {first},

You have listings that won't close because the business can't run without
its owner — most brokers do. I run yourco; we build and operate AI systems
that remove exactly that dependence.

The offer, plainly: send us your unsellable owner-dependent listings. We
make them sellable — or the owner decides to keep a business that now runs
without them, and either way the introduction came from you and we treat it
that way.

Worth a call? I'm not asking you to endorse anything you haven't seen — the
first conversation is me showing you how it works.

[YOUR SIGN-OFF]
[PHYSICAL MAILING ADDRESS — required on commercial email]"""

# The screen. A draft that trips ANY of these is refused, not stored — the
# guardrails are the decision's own, plus the never-a-buyer rule.
PITCH_BANNED = [
    ("walk away", "day-one abandonment framing — autonomy is earned, never day-one"),
    ("from day one", "day-one autonomy framing — the moat-killer the standard names"),
    ("fully autonomous", "overpromise — the matrix earns rungs per action"),
    ("guarantee", "an unconditional promise"),
    ("will grow", "a growth promise with zero case studies behind it"),
    ("grow your revenue", "a growth promise with zero case studies behind it"),
    ("double your", "a growth promise"),
    ("10x", "a growth promise"),
    ("interested in buying", "posing as a buyer — the one deception this lane must never touch"),
    ("interested in acquiring", "posing as a buyer"),
    ("we'd like to acquire", "posing as a buyer"),
    ("potential buyer", "posing as a buyer"),
]


def screen_pitch(text):
    t = (text or "").lower()
    flags = [{"term": term, "why": why} for term, why in PITCH_BANNED if term in t]
    return {"clean": not flags, "flags": flags}


def draft_for(c):
    """Build the right draft for the candidate's route. Refused (None, err)
    if the result would trip the screen — which the templates never do by
    construction; the screen exists for edited/imported copy."""
    first = (c.get("owner_name") or "").split(" ")[0] or "there"
    if c["stage"] == "eta_lane":
        return None, ("ETA-lane candidates are the BUYER's conversation "
                      "(2026-06-16_eta-company-os-offering) — this platform "
                      "tracks them and drafts nothing; a different pitch to a "
                      "different person is not a template swap")
    if c["stage"] == "broker_referral" or c["contact_path"] == "broker":
        broker_first = (c.get("broker") or "").split(" ")[0] or "there"
        body = BROKER_INTRO_TEMPLATE.format(first=broker_first)
        kind = "broker_intro"
    else:
        st = STATUSES[c["status"]]
        signal_line = {
            "expired":  "your listing for {n} has come off the market",
            "relisted": "{n} is back on the market",
            "listed":   "{n} is listed for sale",
            "retirement_news": "the news that you're planning your exit from {n}",
        }.get(c["status"], "{n} is in transition").format(n=c["name"])
        fin = c.get("published_financials")
        financials_line = ""
        if fin:
            financials_line = ("\n\n(Those aren't my numbers — they're the ones "
                               f"in your own listing: {str(fin)[:120]}.)")
        body = EXIT_PITCH_TEMPLATE.format(first=first, signal_line=signal_line,
                                          financials_line=financials_line)
        kind = "exit_pitch"
    res = screen_pitch(body)
    if not res["clean"]:
        return None, f"draft refused by the pitch screen: {res['flags']}"
    rows = load("candidates")
    cc = next((x for x in rows if x["id"] == c["id"]), None)
    if cc is None:
        return None, "not found"
    if any(d["kind"] == kind for d in cc.get("drafts", [])):
        return next(d for d in cc["drafts"] if d["kind"] == kind), None
    d = {"kind": kind, "at": iso(), "body": body, "status": "draft",
         "note": "the Founder sends; agents draft. Sends are OtherVenture-gated like all outbound."}
    cc.setdefault("drafts", []).append(d)
    save("candidates", rows)
    return d, None


# ------------------------------------------------------------------ export

def export_sadie_json():
    """The hand-off: qualified-and-staged, owner-reachable, not-DNC candidates
    in Sadie's schema for `runtime/sourcing.py --sadie-json` → the exit-themed
    Instantly campaign. Everything else stays here — broker referrals go to
    Bird by hand, the ETA lane is its own conversation, and nothing anonymized
    or opted-out ever leaves this store."""
    out = []
    for c in load("candidates"):
        if c["stage"] != "staged" or c.get("dnc"):
            continue
        if c["contact_path"] == "anonymized":
            continue          # unreachable by construction; belt and braces
        contact = c.get("contact", "")
        out.append({
            "name": c.get("owner_name") or c["name"],
            "company": c["name"],
            "email": contact if "@" in contact else None,
            "phone": contact if "@" not in contact and contact else None,
            "intent": {"signal": f"{STATUSES[c['status']]['label']} — "
                                 f"{c.get('industry') or 'SMB'}, {c.get('location') or '?'}",
                       "url": c["provenance"]["url"],
                       "platform": c["provenance"]["source"]},
            "source": ["sadie", "exit-radar"],
        })
    return out


# ------------------------------------------------------------------ reads

def board():
    rows = load("candidates")
    by_stage = {s: [] for s in STAGES}
    for c in sorted(rows, key=lambda x: -score(x)["total"]):
        by_stage[c["stage"]].append({**c, "score": score(c)})
    outcomes = [c for c in rows if c["stage"] in ("staged", "dismissed")]
    return {
        "stages": by_stage,
        "counts": {s: len(by_stage[s]) for s in STAGES},
        "total": len(rows),
        "note": ("Every send is OtherVenture-gated and human-made. Anonymized "
                 "listings route to Bird (partner category 9), sold/under-"
                 "contract to the ETA lane; nothing here fetches a listing "
                 "platform — humans read, software records."),
        "statuses": {k: v["label"] for k, v in STATUSES.items()},
    }


# ------------------------------------------------------------------ cli

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Exit Radar — see module docstring")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--export", action="store_true",
                    help="print sadie-json for runtime/sourcing.py --sadie-json")
    ap.add_argument("--import-file", help="JSON file: {candidates:[...]}")
    a = ap.parse_args()
    if a.board:
        b = board()
        for s in STAGES:
            for c in b["stages"][s]:
                print(f"{s:16} {c['score']['total']:>3}  {c['name']}  "
                      f"[{c['status']}/{c['contact_path']}]  {c.get('location','')}")
        print(f"\n{b['note']}")
    elif a.export:
        print(json.dumps(export_sadie_json(), indent=1))
    elif a.import_file:
        rep, err = import_candidates(json.loads(Path(a.import_file).read_text()))
        print(json.dumps(rep or {"error": err}, indent=1))
    else:
        ap.print_help()
