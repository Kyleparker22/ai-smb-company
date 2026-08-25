#!/usr/bin/env python3
"""End-to-end test of the CRM insight layer against a COPY of the real data.

Proves the write paths (prediction capture, promise ledger, mirror marks) actually
flow through to the computed outputs — without mutating the live CRM.
"""
import json, os, sys, shutil, tempfile, datetime, importlib

CRM = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(CRM)
sys.path.insert(0, CRM)

tmp = tempfile.mkdtemp(prefix="crmtest")
shutil.copy(os.path.join(CRM, "data.json"), os.path.join(tmp, "data.json"))
DATA = os.path.join(tmp, "data.json")
TODAY = datetime.date.today()
OK, FAIL = [], []


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(f"{name}{(' — ' + detail) if detail else ''}")


def load():
    with open(DATA) as f:
        return json.load(f)


def dump(d):
    with open(DATA, "w") as f:
        json.dump(d, f, indent=2)


# ---------------------------------------------------------------- 1. calibration
import calibration
d = load()
deal = next(x for x in d["deals"] if x["id"] == "d11")          # Sample Client, at proposal
deal["predictions"] = [{"id": "pr1", "at": "2026-06-20", "atStage": "proposal",
                        "closeDate": "2026-07-15", "amount": 12000, "confidence": 70, "by": "the Founder"}]
r = calibration.compute(d)
check("calibration: open prediction counted", r["predictionsOpen"] == 1, str(r["predictionsOpen"]))
check("calibration: overdue vs own date detected", len(r["overdue"]) == 1 and r["overdue"][0]["daysPastPrediction"] > 0,
      json.dumps(r["overdue"][0]) if r["overdue"] else "none")
check("calibration: refuses bias below MIN_N", r["bias"]["_all"]["status"] == "insufficient")

# now resolve five warm deals won, with a consistent 20-day slip and 0.8x value
d2 = load()
d2["closed"] = []
for i in range(5):
    d2["closed"].append({
        "id": f"z{i}", "name": f"Test {i}", "companyId": "c11", "outcome": "won",
        "value": 8000, "closedDate": "2026-07-01", "stage": "proposal",
        "predictions": [{"id": f"p{i}", "at": "2026-05-01", "atStage": "proposal",
                         "closeDate": "2026-06-11", "amount": 10000, "confidence": 70, "by": "the Founder"}]})
r2 = calibration.compute(d2)
seg = None
for k, b in r2["bias"].items():
    if b["status"] == "measured" and k != "_all":
        seg = b
check("calibration: bias measured at MIN_N", seg is not None and seg["resolved"] == 5,
      json.dumps({k: v["status"] for k, v in r2["bias"].items()}))
if seg:
    check("calibration: timing bias = +20d", seg["timingBiasDays"] == 20.0, str(seg["timingBiasDays"]))
    check("calibration: amount bias = 0.8x", seg["amountBias"] == 0.8, str(seg["amountBias"]))
    check("calibration: reading names the direction", "later" in (seg["reading"] or ""), seg["reading"])
check("calibration: corrected forecast differs from raw",
      r2["correctedWeighted"] != r2["rawWeighted"] or r2["uncorrectedDeals"] == len(r2["forecast"]),
      f"{r2['rawWeighted']} -> {r2['correctedWeighted']}")

# ---------------------------------------------------------------- 2. promises
import promises as pm
pm.DATA = DATA
d3 = load()
deal3 = next(x for x in d3["deals"] if x["id"] == "d11")
deal3["promises"] = [
    {"id": "pm1", "text": "Weekly build walkthrough every Thursday", "madeOn": "2026-07-01",
     "due": "2026-07-10", "source": "call", "status": "open", "severity": "high"},
    {"id": "pm2", "text": "Supplier drafts wired to Aspire", "madeOn": "2026-07-01",
     "due": (TODAY + datetime.timedelta(days=14)).isoformat(), "source": "proposal", "status": "open"},
    {"id": "pm3", "text": "Send the dry-run prototype", "madeOn": "2026-06-20",
     "due": "2026-06-25", "source": "meeting", "status": "delivered", "deliveredOn": "2026-06-24"},
]
r3 = pm.compute(d3)
check("promises: ledger picks up all three", len(r3["promises"]) == 3, str(len(r3["promises"])))
check("promises: overdue flagged", r3["overdue"] == 1, str(r3["overdue"]))
check("promises: delivered not counted as debt", r3["open"] == 2, str(r3["open"]))
deb = r3["debt"][0]
check("promises: debt state = in debt", deb["state"] == "in debt", deb["state"])
check("promises: severity weighted", deb["weight"] == 5, str(deb["weight"]))   # high(3) + normal(2)
check("promises: worst days late computed", deb["worstDaysLate"] > 0, str(deb["worstDaysLate"]))
cands = pm.scan(d3)
check("promises: scanner still proposes without accepting", all(c["status"] == "candidate" for c in cands),
      str(len(cands)))

# ---------------------------------------------------------------- 3. mirror
import mirror
d4 = load()
deal4 = next(x for x in d4["deals"] if x["id"] == "d11")
deal4["mirror"] = {"champion": "Client Owner", "steps": {
    "felt": {"status": "yes", "note": "said it unprompted on the 06-14 call"},
    "internal": {"status": "yes", "note": "Colton is in the loop"},
    "budget": {"status": "no", "note": "has not named the line"}}}
r4 = mirror.compute(d4)
row = next(x for x in r4["rows"] if x["dealId"] == "d11")
check("mirror: cleared steps counted", row["cleared"] == ["felt", "internal"], str(row["cleared"]))
check("mirror: depth stops at first gap", row["depth"] == 2, str(row["depth"]))
check("mirror: overreach = what the stage assumes", set(row["overreach"]) == {"budget", "risk", "story"},
      str(row["overreach"]))
check("mirror: unknown never counted as cleared", "risk" not in row["cleared"])
check("mirror: unmapped deals reported separately", r4["unmappedDeals"] == 2, str(r4["unmappedDeals"]))
check("mirror: pre-convo deals are not mirrored at all",
      not any(x["stage"] == "pre-convo" for x in r4["rows"]), "a pre-conversation deal has no buyer ladder")

# ---------------------------------------------------------------- 4. adversarial
import adversarial as adv
d5 = load()
r5 = adv.compute(d5)
check("spread: every in-motion deal read", len(r5["reads"]) == 3, str(len(r5["reads"])))
for rd in r5["reads"]:
    check(f"spread: {rd['company'][:18]} scores in range",
          0 <= rd["prosecution"] <= 100 and 0 <= rd["defence"] <= 100)
    check(f"spread: {rd['company'][:18]} has a next action", bool(rd["nextAction"]))
# the load-bearing property: our own activity must NOT move the prosecution
d6 = load()
deal6 = next(x for x in d6["deals"] if x["id"] == "d11")
before = next(x for x in adv.compute(d6)["reads"] if x["dealId"] == "d11")
deal6.setdefault("artifacts", []).append({"id": "aX", "name": "Another thing we built", "status": "built",
                                          "date": TODAY.isoformat(), "link": "", "reaction": ""})
after = next(x for x in adv.compute(d6)["reads"] if x["dealId"] == "d11")
check("spread: OUR work does not move the prosecution", before["prosecution"] == after["prosecution"],
      f"{before['prosecution']} -> {after['prosecution']}")
check("spread: OUR work does move the defence", after["defence"] >= before["defence"],
      f"{before['defence']} -> {after['defence']}")
check("spread: adding our own work widens the disagreement", after["spread"] >= before["spread"],
      f"{before['spread']} -> {after['spread']}")
# a buyer-side action must move BOTH
d7 = load()
d7["activities"].insert(0, {"date": TODAY.isoformat(), "type": "meeting", "companyId": "c11",
                            "who": "the Founder", "summary": "Client Owner called and asked to sign"})
after2 = next(x for x in adv.compute(d7)["reads"] if x["dealId"] == "d11")
check("spread: THEIR action moves the prosecution", after2["prosecution"] > before["prosecution"],
      f"{before['prosecution']} -> {after2['prosecution']}")

# ---------------------------------------------------------------- 5. warm path
import warmpath as wp
d8 = load()
r8 = wp.compute(d8)
check("warmpath: reach is positive", r8["reachNow"] > 0, str(r8["reachNow"]))
check("warmpath: ranking is a real counterfactual",
      any(x["deltaEV"] > 0 for x in r8["ranked"]), "no positive delta")
# warming someone must never reduce total reach
base = r8["reachNow"]
for x in r8["ranked"]:
    check(f"warmpath: {x['person'][:16]} delta is non-negative", x["deltaEV"] >= 0, str(x["deltaEV"]))
check("warmpath: orphans reported, not silently zeroed", len(r8["orphans"]) > 0, str(len(r8["orphans"])))
# a cold contact warmed should unlock more than an already-warm one, all else equal
d9 = load()
for p in d9["contacts"]:
    if p.get("name") == "the Client Owner":
        p["lastTouch"] = TODAY.isoformat()
r9 = wp.compute(d9)
g_before = next(x["deltaEV"] for x in r8["ranked"] if x["person"] == "the Client Owner")
g_after = next(x["deltaEV"] for x in r9["ranked"] if x["person"] == "the Client Owner")
check("warmpath: a freshly-touched person is worth less to warm again", g_after < g_before,
      f"{g_before} -> {g_after}")

# ---------------------------------------------------------------- 6. autonomy
import autonomy as au
d10 = load()
r10 = au.compute(d10)
check("autonomy: headline is action autonomy", r10["headline"] == r10["actionDial"]["pct"])
check("autonomy: observation reported separately", r10["observationDial"]["pct"] is not None)
check("autonomy: send stays gated at ceiling R1",
      any(a["key"] == "send-external" and a["rung"] == "R1" and a["ceiling"] == "R1" for a in r10["actions"]))
check("autonomy: nothing self-promotes",
      all(a["rung"] in ("R0", "R1", "R2", "R3") for a in r10["actions"]))
# an agent-authored activity must raise the dial
d11 = load()
d11["activities"].insert(0, {"date": TODAY.isoformat(), "type": "stage", "companyId": "c11",
                             "who": "David", "summary": "agent advanced it"})
r11 = au.compute(d11)
check("autonomy: an agent action raises the dial", (r11["headline"] or 0) > (r10["headline"] or 0),
      f"{r10['headline']} -> {r11['headline']}")

# ---------------------------------------------------------------- 7. ghost invariants
import ghost
d12 = load()
g = ghost.compute()
check("ghost: reconstructed >1 board state", g["revisions"] > 1, str(g["revisions"]))
check("ghost: no dollar claimed on an unmeasured path",
      all((row["evGap"] is None) for row in g["ghost"] if row["unpricedRungs"]))
check("ghost: measured total excludes unpriced deals",
      g["totalEvGap"] == 0 or all(r["priced"] for r in g["ghost"] if r["evGap"]))
check("ghost: every ghost stage is on the ladder",
      all(r["ghost"] in g["order"] for r in g["ghost"]))
check("ghost: bench time is not charged as pipeline delay",
      all(r["originStage"] in g["order"] for r in g["ghost"]))

# ---------------------------------------------------------------- 8. expansion / referral gates
import expansion as EX
import tempfile as _tf
_out = _tf.mkdtemp(prefix="crmout")
EX.CLIENTS = _out
os.makedirs(os.path.join(_out, "sample-client"))
_ledger = os.path.join(_out, "sample-client", "outcomes.jsonl")
d13 = load()
_deal = next(x for x in d13["deals"] if x.get("companyId") == "c11")
_deal["stage"] = "live"; _deal["promises"] = []
_deal["stageSince"] = (TODAY - datetime.timedelta(days=70)).isoformat()

def _row():
    return EX.compute(d13)["clients"][0]

check("expansion: no client live -> no rows at all", not EX.compute(load())["clients"])
r = _row()
check("expansion: refuses with no outcomes ledger", not r["expansionReady"] and not r["referralReady"])
check("expansion: names the missing ledger", any("outcomes.jsonl" in b for b in r["expansionBlockers"]))
with open(_ledger, "w") as f:
    f.write(json.dumps({"date": TODAY.isoformat(), "metric": "quote turnaround", "value": 2,
                        "unit": " days", "baseline": 42, "direction": "down", "module": "Sales"}) + "\n")
r = _row()
check("expansion: a DOWN metric beating baseline counts as realised", len(r["realised"]) == 1,
      json.dumps(r["realised"]))
check("expansion: opens when clean + realised + nothing owed", r["expansionReady"] and r["referralReady"])
check("expansion: proposes an unbuilt pillar, not 'sell more'", r["nextModule"] in EX.PILLARS, str(r["nextModule"]))
with open(_ledger, "a") as f:   # a down-moving metric that never declared its direction
    f.write(json.dumps({"date": TODAY.isoformat(), "metric": "admin hours", "value": 3,
                        "baseline": 11, "module": "Operations"}) + "\n")
r = _row()
check("expansion: refuses an undeclared direction rather than guessing",
      not r["expansionReady"] and any("direction" in b for b in r["expansionBlockers"]))
_deal["promises"] = [{"id": "z", "text": "weekly walkthrough", "status": "open",
                      "due": (TODAY - datetime.timedelta(days=9)).isoformat()}]
r = _row()
check("expansion: promise debt closes the referral gate",
      not r["referralReady"] and any("owe" in b or "spends" in b for b in r["referralBlockers"]))
_deal["stageSince"] = (TODAY - datetime.timedelta(days=7)).isoformat()
_deal["promises"] = []
r = _row()
check("expansion: too new to expand even when realised",
      not r["expansionReady"] and any("needs" in b for b in r["expansionBlockers"]))
shutil.rmtree(_out, ignore_errors=True)


# ===================== the 2026-08-13 modules ==========================================
# Each of these is built to REFUSE rather than guess, so the tests assert the refusals as
# hard as the answers — a module that quietly starts reporting a number off two data points
# is the exact regression that matters here.
import pricing_power, autopsy, capacity, antipipeline, counterparty, blocks, decision_pl

_d = load()
# Start from a KNOWN baseline. The first cut of this test assumed no deal carried a price
# event, then broke the moment a real quote was backfilled onto Sample Client — a test that
# depends on live data content fails for the wrong reason and teaches you to ignore it.
for _x in _d.get("deals", []) + _d.get("closed", []):
    _x.pop("priceEvents", None)

# ---- price events ---------------------------------------------------------------------
_pd = _d["deals"][0]
_pd["priceEvents"] = [{"id": "t1", "date": TODAY.isoformat(), "kind": "quoted",
                       "amount": 1000, "noPushback": True}]
r = pricing_power.compute(_d)
check("price: refuses a pattern below MIN_EVENTS",
      r["status"] == "insufficient" and r["needs"] == pricing_power.MIN_EVENTS - 1)
check("price: never claims noPushback stats while refusing", r["acceptedNoPushback"] is None)

# five priced deals -> it should measure, and see the underpricing signal
for i, dd in enumerate(_d["deals"][:5]):
    dd["priceEvents"] = [{"id": f"q{i}", "date": TODAY.isoformat(), "kind": "quoted",
                          "amount": 1000, "noPushback": True}]
r = pricing_power.compute(_d)
check("price: measures at MIN_EVENTS", r["status"] == "measured")
check("price: flags accepted-without-pushback", r["acceptedNoPushback"]["pct"] == 100)
check("price: floor test counts sub-floor quotes", r["floorTest"]["quotedBelowFloor"] == 5)
# noPushback must be HUMAN-recorded, never inferred from a missing counter
for dd in _d["deals"][:5]:
    dd["priceEvents"][0]["noPushback"] = False
r = pricing_power.compute(_d)
check("price: noPushback is recorded, never inferred from silence",
      r["acceptedNoPushback"]["n"] == 0)

# ---- loss autopsy ----------------------------------------------------------------------
_d2 = load()
_d2["closed"] = [{"id": "cx", "companyId": _d2["companies"][0]["id"], "outcome": "lost",
                  "closedDate": TODAY.isoformat(), "why": "went with a competitor",
                  "value": 12000,
                  "mirrorAtClose": {"steps": {"felt": "yes", "internal": "yes", "budget": "no"}}}]
r = autopsy.compute(_d2)
check("autopsy: cause read from the first uncleared rung",
      r["rows"][0]["firstGap"] == "budget" and r["rows"][0]["cause"] == "inertia")
check("autopsy: catches the competitor-vs-inertia contradiction",
      "no-decision" in (r["rows"][0]["contradiction"] or ""))
check("autopsy: refuses a pattern below MIN_LOSSES", r["status"] == "insufficient")
_d2["closed"][0].pop("mirrorAtClose")
r = autopsy.compute(_d2)
check("autopsy: unmapped rather than guessed when no ladder exists",
      r["rows"][0]["cause"] == "unmapped")

# ---- capacity ---------------------------------------------------------------------------
r = capacity.compute(load())
check("capacity: refuses the hours model with no build evidence",
      r["hours"]["status"] == "refused" and "toEnable" in r["hours"])
_d3 = load()
_d3.setdefault("meta", {})["capacity"] = {"maxConcurrentBuilds": 1}
_d3["deals"][0]["predictions"] = [{"at": TODAY.isoformat(), "closeDate":
                                   (TODAY + datetime.timedelta(days=3)).isoformat()}]
_d3["deals"][1]["predictions"] = [{"at": TODAY.isoformat(), "closeDate":
                                   (TODAY + datetime.timedelta(days=5)).isoformat()}]
r = capacity.compute(_d3)
check("capacity: detects overlapping build windows", len(r["collisions"]) >= 1)
check("capacity: reports over-ceiling against a STATED ceiling",
      r["status"] == "over" and r["peakConcurrent"] == 2)
_d3["meta"]["capacity"] = {}
r = capacity.compute(_d3)
check("capacity: refuses an over/under verdict with no stated ceiling",
      r["status"] == "ceiling unset")

# ---- anti-pipeline ------------------------------------------------------------------------
r = antipipeline.compute(load())
check("antipipeline: flags a sub-floor retainer",
      any(f["kind"] == "under-floor" for row in r["rows"] for f in row["flags"]))
check("antipipeline: our-gap flags never count against a deal",
      all(row["score"] == sum(antipipeline.SEVERITY.get(f["severity"], 2)
                              for f in row["flags"] if f["kind"] != "our-gap")
          for row in r["rows"]))
check("antipipeline: never auto-declines", "Nothing here declines a deal" in r["honesty"])

# ---- counterparty --------------------------------------------------------------------------
_d4 = load()
_d4["deals"][0]["disputes"] = [{"id": "dz", "rowKind": "promise", "ourClaim": "we said Friday",
                                "theirClaim": "you said Wednesday", "raisedOn": TODAY.isoformat(),
                                "status": "corrected"}]
r = counterparty.disputes(_d4)
check("counterparty: correction rate counts corrections", r["corrected"] == 1)
r0 = counterparty.disputes(load())
check("counterparty: zero disputes on an unshared book is not reported as accuracy",
      "measure of nothing" in r0["reading"])
rec = counterparty.record_for(load(), _d4["deals"][0]["id"])
check("counterparty: buyer copy excludes our internal judgements",
      all(k not in rec for k in ("winProb", "spread", "ghost", "warmpath")))

# ---- blocks --------------------------------------------------------------------------------
reg = blocks.registry()
check("blocks: every block names its owner and rung",
      all(b.get("owner") and b.get("rung") for b in reg["blocks"]))
_ran = {k: blocks.run_block(k) for k in ("scoring", "win-loss", "decisions", "decline")}
check("blocks: delegation resolves for every wired block",
      all(v["status"] == "ok" for v in _ran.values()),
      str({k: v.get("why") for k, v in _ran.items() if v["status"] != "ok"}))
check("blocks: a non-compute block refuses instead of erroring",
      blocks.run_block("enrichment")["status"] == "refused")
check("blocks: unknown block names are rejected",
      blocks.run_block("nope")["status"] == "unknown")


# ---- conversation signals (the live signal layer) --------------------------------------
import conversation, enrich_waterfall, mcp_server

_tx = ("the Founder: how does quoting work today?\n"
       "Client Owner: the problem is we lose four jobs a month waiting on quotes.\n"
       "Client Owner: I talked to my partner about this last week.\n"
       "Client Owner: That's a lot. Not right now, maybe after the season.\n"
       "Client Owner: I'll send you the last twenty quotes.\n"
       "the Founder: We'd be at $3,000 a month.\n"
       "the Founder: I'll have the walkthrough ready by Friday.\n")
_c = conversation.scan_text(_tx, "Sample Client", "2026-08-13", our_names=("the Founder",))
_k = lambda kind: [x for x in _c if x["kind"] == kind]
check("conversation: mirror evidence taken from THEIR words",
      any(x["key"] == "felt" for x in _k("mirror")))
check("conversation: never proposes a mirror step from a line WE spoke",
      all(x["speaker"] != "the Founder" for x in _k("mirror")))
check("conversation: every candidate carries its quote",
      all(x.get("quote") for x in _c))
check("conversation: objection captured with its type",
      any(x["key"] == "timing" for x in _k("objection")))
check("conversation: price attributed to who named it",
      any(x.get("namedBy") == "us" for x in _k("price")))
check("conversation: buyer commitment is a their-move", len(_k("their-move")) >= 1)
# the bug that mattered: a BUYER's "I'll send you..." must not enter OUR promise ledger
check("conversation: buyer commitments never become our promises",
      all(x["speaker"] != "Client Owner" for x in _k("promise")),
      str([x["quote"][:40] for x in _k("promise")]))
check("conversation: our own promise IS captured",
      any("walkthrough" in x["quote"] for x in _k("promise")))
check("conversation: nothing is auto-confirmed",
      all(x["status"] == "candidate" for x in _c))

# ---- waterfall enrichment ---------------------------------------------------------------
check("enrich: rejects a role mailbox as a person's email",
      enrich_waterfall.verify_email("info@yourco.com")[0] is False)
check("enrich: rejects a malformed address",
      enrich_waterfall.verify_email("bob@@yourco")[0] is False)
check("enrich: rejects an off-domain address when the site is known",
      enrich_waterfall.verify_email("bob@gmail.com", {"website": "https://yourco.com"})[0] is False)
check("enrich: accepts a matching personal address",
      enrich_waterfall.verify_email("bob@yourco.com", {"website": "https://yourco.com"})[0] is True)
check("enrich: size must be a count, not a band",
      enrich_waterfall.verify_size("10-50")[0] is False and enrich_waterfall.verify_size("12")[0] is True)
_r = enrich_waterfall.enrich_field("email", "YourCo", {"website": "https://yourco.com"})
check("enrich: a field with no verified value REFUSES rather than returning a guess",
      _r["status"] == "refused" and _r["value"] is None)
check("enrich: every attempt is logged with what it cost",
      all("billed" in a for a in _r["attempts"]))
_r2 = enrich_waterfall.enrich_field("website", "YourCo Co", {})
check("enrich: chain stops at the first VERIFIED hit",
      _r2["status"] == "verified" and _r2["provider"] == "site-guess")

# ---- MCP server ---------------------------------------------------------------------------
_t = mcp_server.tools()
check("mcp: exposes one tool per block plus the two extras",
      len(_t) == len(blocks.BLOCKS) + 2)
check("mcp: every tool advertises its autonomy rung",
      all("rung" in x["description"] for x in _t))
_init = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
check("mcp: initialize returns a protocol version", "protocolVersion" in _init["result"])
_call = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                           "params": {"name": "crm_decline", "arguments": {}}})
_payload = json.loads(_call["result"]["content"][0]["text"])
check("mcp: a tool call returns the block's answer with its rung",
      _payload.get("rung") == "R0" and _payload.get("status") == "ok")
_bad = mcp_server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                          "params": {"name": "crm_nope", "arguments": {}}})
check("mcp: an unknown tool is content, not a transport error",
      "error" not in _bad and "content" in _bad["result"])
check("mcp: no tool writes, sends, or spends",
      all(not any(w in x["name"] for w in ("write", "send", "enrich_run", "post"))
          for x in _t))

print(f"\n{len(OK)} passed, {len(FAIL)} failed\n")
for f in FAIL:
    print("  FAIL " + f)
if not FAIL:
    for o in OK:
        print("  ok   " + o)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if FAIL else 0)
