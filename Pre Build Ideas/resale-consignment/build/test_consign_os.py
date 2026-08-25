#!/usr/bin/env python3
"""Consign OS — the suite. `python3 test_consign_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CONSIGNOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="consignos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import gate, store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


print("== seed ==")
seed.main()
ok(len(store.load("items")) >= 400, "items seeded")

print("== triage: the claim reads first ==")
for case in core.EVAL_CASES:
    got = core.read_message(case["input"])["label"]
    ok(got == case["label"], f"triage: {case['input'][:44] or '(empty)'} → {case['label']} (got {got})")

print("== the claim protocol: no denial, no verdict ==")
out = agents.handle_message("ms_demo_fake")
step = out["steps"][0]
ok(step["action"] == "log_claim", "the claim is logged")
ok("no denial" in step["refused"] and "verdict" in step["refused"],
   "nothing ruled — neither a denial nor an authenticity verdict")
ok("Nothing about your claim is decided by this message" in step["draft"],
   "the ack decides nothing")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "deny_claim"
       for e in store.events()), "deny_claim refused + logged")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "certify_authenticity"
       for e in store.events()), "certify_authenticity refused + logged — fake is also a verdict")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== authenticity: the record speaks or nothing does ==")
bl = core.brand_line(store.by_id("items", "it_demo_lv"))
ok("Tagged Louis Vuitton by the consignor" in bl["line"] and "not authenticated" in bl["line"],
   "no cert → the consignor tag is the whole statement")
ok("authentic" not in bl["line"].lower().replace("not authenticated", ""),
   "software never says 'authentic' on its own")
blc = core.brand_line(store.by_id("items", "it_demo_cert"))
ok("Meridian Authentication Co." in blc["line"] and "MA-88412" in blc["line"],
   "a recorded cert is CITED — the certificate is the statement")
ok("not our judgment" in blc["line"], "and named as not the software's judgment")
okc, why = core.listing_ok("guaranteed real, 100% authentic bag")
ok(not okc and "forbidden" in why, "authenticity claims are structurally refused without a cert")
okc, _ = core.listing_ok("authenticated by Meridian (cert MA-88412)",
                         store.by_id("items", "it_demo_cert"))
ok(okc, "citing the recorded cert passes")
out = agents.handle_message("ms_demo_auth")
body = out["steps"][0]["draft"]
ok("MA-88412" in body, "the auth reply cites the recorded cert")
ok(core.listing_ok(body, store.by_id("items", "it_demo_cert"))[0],
   "the shipped copy passes its own claim check structurally")

print("== the payout is the agreement's arithmetic ==")
m = core.payout_math(store.by_id("items", "it_demo_sold"))
ok(m["amount"] == round(380 * 0.5, 2), "sale × the consignor's RECORDED split (0.5, not default)")
ok("agreement's arithmetic" in m["basis"], "the basis names the agreement")
ok("recorded consignor_split applies" in m["agreement_source"],
   "the per-consignor override is named, not silent")
m2 = core.payout_math(store.by_id("items", "it_demo_nosplit"))
ok("refused" in m2 and "sold_price" in m2["refused"],
   "a missing input → refused with the field named")
out = agents.handle_message("ms_demo_payout")
step = out["steps"][0]
ok(step["action"] == "draft_payout" and "agreement's arithmetic" in step["draft"],
   "the payout ask is answered from the ledger, the agreement cited")
ok(any(p["amount"] == 190.0 for p in step["payouts"]), "with the recorded split's number")

print("== markdowns follow the recorded schedule ==")
md = core.markdown_price(store.by_id("items", "it_demo_interm"))
ok(md["factor"] == 0.8 and md["price"] == round(130 * 0.8, 2),
   "day 30 → the schedule's 0.8, the schedule's arithmetic")
md0 = core.markdown_price(store.by_id("items", "it_demo_lv"))
ok(md0["factor"] == 1.0, "inside 30 days → full price")
ok("refused" in core.markdown_price({"consignor_id": "cn_003"}),
   "no listing date → no schedule clock to run")

print("== the offer floor clamp ==")
out = agents.handle_message("ms_demo_offer")
step = out["steps"][0]
ok(step["check"]["action"] == "counter", "$40 against a $55 floor → a counter, never an acceptance")
ok("$55" in step["draft"] and "floor" in step["draft"], "the counter names the floor")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "accept_below_floor"
       for e in store.events()), "accept_below_floor refused + logged")
out = agents.handle_message("ms_demo_offer_ok")
ok(out["steps"][0]["check"]["action"] == "accept_draft",
   "$60 clears the floor → an acceptance DRAFTS for a human")
g = [e for e in store.events(kind="queued_for_approval")
     if (e.get("detail") or {}).get("action") == "draft_offer_reply"]
ok(g and g[-1].get("rung") == "R1", "and the reply queues at R1")
out = agents.handle_message("ms_demo_nofloor")
ok("refused" in out["steps"][0] and "consignor decides" in out["steps"][0]["why"],
   "no recorded floor → software doesn't negotiate at all")

print("== the wall: prohibited and unrecorded ==")
r = agents.list_item("it_demo_recall")
ok("refused" in r and "prohibited" in r["refused"], "the drop-side crib never reaches a channel")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "list_prohibited_item"
       for e in store.events()), "list_prohibited_item logged")
r = agents.list_item("it_demo_nocond")
ok("refused" in r and "condition" in r["refused"],
   "no recorded condition → no listing; the damage dispute starts there")
r = agents.list_item("it_demo_dresser")
ok("listing" in r and r["gate"]["rung"] == "R1" and r["gate"]["executed"] is False,
   "a clean item drafts and queues — a human publishes")
ok("as recorded at intake" in r["listing"]["body"], "the description carries the intake record")
ok("personal" not in " ".join(r["listing"]["channels"]),
   "channels are the shop's business surfaces")
ok("yourco" not in r["listing"]["body"].lower(), "listing copy is white-label")
d = core.describe(store.by_id("items", "it_demo_nofloor"))
ok("not recorded" in d["body"], "a field the record doesn't carry says so — never a guess")
ok("personal_account" not in core.CHANNELS and "marketplace_business" in core.CHANNELS,
   "no personal-account channel exists by construction")

print("== the clock ==")
okd, why = core.can_donate(store.by_id("items", "it_demo_interm"))
ok(not okd and "conversion" in why, "donating in term is refused as conversion")
r = agents.donate("it_demo_reclaim")
ok("refused" in r, "donating inside the reclaim window is refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "donate_before_clock"
       for e in store.events()), "donate_before_clock logged")
r = agents.donate("it_demo_expired")
ok("refused" in r and "human act" in r["refused"], "even past the clock, no human → no donation")
r = agents.donate("it_demo_expired", human="owner")
ok(r.get("donated") and "only now" in r["why"], "a human donates after the clock, and only then")
st = core.clock_state(store.by_id("items", "it_demo_reclaim"))
ok(st["state"] == "reclaim_window" and "DATE ALERT" in st["label"],
   "the reclaim window is a DATE ALERT")

print("== the reclaim ladder is bounded ==")
it = store.by_id("items", "it_demo_reclaim")
plan = core.reclaim_plan(it)
ok(plan["action"] == "draft_notice", "an item in the window is due a notice")
it["reclaim_touches"] = [{"at": iso(now() - timedelta(days=1))}]
ok(core.reclaim_plan(it)["action"] == "none", "inside the cooldown → no touch")
it["reclaim_touches"] = [{"at": iso(now() - timedelta(days=30 - i))} for i in range(3)]
plan = core.reclaim_plan(it)
ok(plan["action"] == "none" and "silence is an answer" in plan["why"],
   "the ladder exhausts at 3 — silence is an answer")

print("== matrix ==")
for a in ("certify_authenticity", "deny_claim", "settle_off_agreement", "accept_below_floor",
          "list_prohibited_item", "donate_before_clock"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("certify_authenticity", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "certify_authenticity" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no claim missed")
ok("COUNTERFEIT" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("aged_value" in r["recorded"], "aged inventory value is counted")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Listing hours returned"]["kind"] == "time_saved", "listing hours are time_saved")
ok(labels["The counterfeit file"]["kind"] == "scenario", "the counterfeit file is a scenario")
ok(labels["The counterfeit file"]["value"] is None, "and stays blank with no input")

print("== the board refuses to estimate ==")
fb = core.floor_board()
ok(fb["owed_total"] >= 0 and "never estimated" in fb["note"],
   "payouts owed are counted; the unpayable are named")

print("== recovered, counted ==")
base = core.recovered_this_week()
it = store.by_id("items", "it_demo_lv")
it["status"] = "sold"
it["sold_at"] = iso(now() - timedelta(days=1))
it["sold_price"] = 480
store.upsert("items", it)
store.log_event("publish_listing", "it_demo_dresser", "human:owner", "R1", {})
store.log_event("publish_listing", "it_x", "agent:listings", "R1", {})
rec = core.recovered_this_week()
ok(rec["items_sold"] == base["items_sold"] + 1, "a sale is counted from the ledger")
ok(rec["listings_published"] == base["listings_published"] + 1,
   "human publishes count; agent drafts don't")
ok("human sends count" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused")

print("== events are append-only, every agent action carries a rung ==")
evs = store.events()
ok(all(not (str(e.get("actor", "")).startswith("agent:") and not e.get("rung"))
       for e in evs if e["kind"] != "seeded" and (e.get("detail") or {}).get("action")
       != "publish_listing_blocked"),
   "no agent action logged without a rung (the non-R0 listing block carries none by design)")
ids = [e["id"] for e in evs]
agents.reclaim_sweep()
ok([e["id"] for e in store.events()][:len(ids)] == ids, "the event log is append-only")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
