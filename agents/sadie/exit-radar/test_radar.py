#!/usr/bin/env python3
"""Exit Radar — the honesty suite. Same doctrine as every yourco build: each
assertion pins a REFUSAL or a routing rule that would decay silently if
someone tuned it to make the pipeline look fuller.

  python3 test_radar.py
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="exit-radar-test-"))
os.environ["EXIT_RADAR_DATA"] = str(TMP)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import radar  # noqa: E402

PASS = FAIL = 0
FAILURES = []


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(label)
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")


PROV = {"url": "https://localnews.example.com/retiring-owner",
        "source": "local news"}

# ---------------------------------------------------------------- intake
print("\n1. Intake — provenance and the no-scrape line")

c, err = radar.add_candidate({"name": "Test Plumbing Co"})
ok(c is None and "provenance" in err, "a candidate without provenance is refused")

c, err = radar.add_candidate({
    "name": "Hand Read Deli",
    "provenance": {"url": "https://www.bizbuysell.com/listing/123",
                   "source": "BizBuySell"}})
ok(c is None and "human" in err.lower(),
   "a ToS-gated listing URL is refused WITHOUT the human-read attestation")

c, err = radar.add_candidate({
    "name": "Hand Read Deli", "status": "listed", "contact_path": "broker",
    "broker": "Jane Broker",
    "provenance": {"url": "https://www.bizbuysell.com/listing/123",
                   "source": "BizBuySell — read by hand", "human_read": True}})
ok(c is not None, "...and accepted WITH it — humans read, software records")
ok(not hasattr(radar, "fetch") and "urllib.request" not in
   Path(radar.__file__).read_text(),
   "radar.py contains no fetcher at all — the no-scrape rule is structural")

c, err = radar.add_candidate({
    "name": "Anon Landscaping (Yourtownmetro)", "status": "expired",
    "contact_path": "anonymized", "provenance": PROV})
ok(c["stage"] == "broker_referral",
   "an anonymized listing routes to Bird (partner cat. 9) at intake — never outreach")

c, err = radar.add_candidate({
    "name": "Sold HVAC Inc", "status": "sold", "contact_path": "owner_direct",
    "provenance": PROV})
ok(c["stage"] == "eta_lane",
   "a sold business routes to the ETA lane — the BUYER is the prospect")

c, err = radar.add_candidate({
    "name": "Ray's Auto Repair", "status": "expired",
    "contact_path": "owner_direct", "owner_name": "Ray Ortiz",
    "contact": "ray@raysauto.example.com", "provenance": PROV,
    "note": "retiring after 31 years per the article"})
ok(c["stage"] == "found", "an owner-reachable expired listing lands in triage")
rid = c["id"]

dup, _ = radar.add_candidate({
    "name": "ray's auto repair", "status": "listed",
    "contact_path": "owner_direct", "provenance": PROV})
ok(dup["id"] == rid and len(dup["signals"]) == 1,
   "a repeat signal merges onto the existing candidate (case-insensitive)")
ok(dup["status"] == "expired",
   "...and the HIGHER-ranked status wins — a merge never downgrades the signal")

# ---------------------------------------------------------------- scoring
print("\n2. Scoring — recorded facts, reasons attached")

s = radar.score(radar.load("candidates")[-1])
ok(s["total"] > 0 and s["parts"],
   "a score decomposes into named parts — no opaque number")
exp = radar.STATUSES["expired"]["score"]
ok(exp > radar.STATUSES["listed"]["score"] > radar.STATUSES["sold"]["score"],
   "expired > listed > sold — the decision's signal ranking is the code's")

# ---------------------------------------------------------------- stages
print("\n3. Stage machine — routing rules that cannot be walked around")

anon = next(x for x in radar.load("candidates") if x["contact_path"] == "anonymized")
_, err = radar.set_stage(anon["id"], "staged")
ok(err and "anonymized" in err,
   "an anonymized candidate can NEVER be staged — nobody to honestly address")

_, err = radar.set_stage(rid, "staged")
ok(err and "qualified" in err, "staging requires qualification first — review is not optional")
radar.set_stage(rid, "qualified")
c2, err = radar.set_stage(rid, "staged")
ok(err is None and c2["stage"] == "staged", "qualified → staged works")

# ---------------------------------------------------------------- drafts
print("\n4. The pitch screen — the decision's guardrails as refusals")

for bad, why_frag in [
        ("You could walk away day one.", "walk away"),
        ("Fully autonomous from day one.", "day one"),
        ("We guarantee results.", "guarantee"),
        ("We will grow your revenue.", "grow"),
        ("We're interested in buying your business.", "buyer")]:
    res = radar.screen_pitch(bad)
    ok(not res["clean"], f"screen refuses: {bad!r}")

c3 = next(x for x in radar.load("candidates") if x["id"] == rid)
d, err = radar.draft_for(c3)
ok(d is not None, "the exit pitch drafts for an owner-reachable candidate")
ok("not buyers" in d["body"], "...and states plainly that yourco is NOT a buyer")
ok("trending toward zero as the system earns it" in " ".join(d["body"].split()),
   "...uses the canonical earned-autonomy framing, never day-one")
flat = " ".join(d["body"].split()).lower()
ok("no longer want to sell" in flat and "easier sale at a better price" in flat
   and "a successor can actually take" in flat,
   "the pitch carries all THREE sides — don't sell / sell for more / hand it off")
ok(radar.screen_pitch(d["body"])["clean"], "...and passes its own screen")
ok("PHYSICAL MAILING ADDRESS" in d["body"] and "won't write again" in d["body"],
   "...carries the address bracket and the opt-out promise")
ok("$" not in d["body"],
   "no financial figures in the draft — this candidate published none")

d2, _ = radar.draft_for(c3)
ok(d2["at"] == d["at"], "drafting twice returns the same draft — idempotent")

bk, _ = radar.draft_for(next(x for x in radar.load("candidates")
                             if x["stage"] == "broker_referral"))
ok(bk and bk["kind"] == "broker_intro" and "unsellable" in bk["body"],
   "a broker-routed candidate gets the category-9 intro, not the owner pitch")

eta = next(x for x in radar.load("candidates") if x["stage"] == "eta_lane")
d3, err = radar.draft_for(eta)
ok(d3 is None and "buyer" in err.lower(),
   "the ETA lane drafts NOTHING here — a different pitch to a different person")

# financials only as published
cf, _ = radar.add_candidate({
    "name": "Numbers Bakery", "status": "listed", "contact_path": "owner_direct",
    "owner_name": "Pat Lee", "published_financials": "$310k SDE per the listing",
    "provenance": {"url": "https://broker.example.com/listing", "source": "broker site read by hand",
                   "human_read": True}})
d4, _ = radar.draft_for(cf)
ok("your own listing" in d4["body"] and "310k" in d4["body"],
   "published financials appear ONLY as the listing's own numbers, attributed")

# ---------------------------------------------------------------- dnc + export
print("\n5. The export — only who may honestly be contacted, and DNC is forever")

out = radar.export_sadie_json()
ok(all(o["source"] == ["sadie", "exit-radar"] for o in out),
   "export uses Sadie's hand-off schema — the EXISTING cold pipeline, no parallel rail")
ok(len(out) == 1 and out[0]["company"] == "Ray's Auto Repair",
   "only staged, owner-reachable candidates export")
ok(all(o["intent"]["url"] for o in out),
   "every exported row carries its provenance URL into the campaign")

radar.mark_dnc(rid)
ok(radar.export_sadie_json() == [], "a DNC candidate vanishes from the export")
_, err = radar.set_stage(rid, "qualified")
ok(err and "permanent" in err, "...and can never be re-staged — no is no")

ok("OtherVenture" in radar.board()["note"] or "gated" in radar.board()["note"],
   "the board states the send gate on the payload itself")

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'=' * 56}\n  {PASS} passed, {FAIL} failed")
if FAILURES:
    for f in FAILURES:
        print(f"    · {f}")
sys.exit(1 if FAIL else 0)
