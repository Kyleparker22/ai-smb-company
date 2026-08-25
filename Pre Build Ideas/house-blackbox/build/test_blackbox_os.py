#!/usr/bin/env python3
"""Blackbox OS — the suite. `python3 test_blackbox_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["BLACKBOXOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="blackboxos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
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
ok(len(store.load("homes")) >= 1400, "homes seeded")
ok(len([m for m in store.load("members") if not m.get("demo_tag")]) >= 340, "members seeded")

print("== triage: the emergency reads first ==")
for text, want in (("we have no heat and it's 20 degrees outside", "emergency"),
                   ("the furnace died overnight", "emergency"),
                   ("ac is not working and it's 95 in the house", "emergency"),
                   ("i smell gas near the water heater", "emergency"),
                   ("there's a gas smell in the basement", "emergency"),
                   ("a pipe burst in the laundry room", "emergency"),
                   ("how much does the maintenance membership cost", "quote_ask"),
                   ("can you quote me the plan for my house", "quote_ask"),
                   ("why is my plan more than my neighbor's", "fairness"),
                   ("my neighbor pays less for the same plan", "fairness"),
                   ("can we schedule the spring tune-up", "booking"),
                   ("book a maintenance visit for next week", "booking"),
                   ("", "human"),
                   ("do you sell air filters", "human"),
                   ("what brands do you install", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '<empty>'} → {want}")

print("== the gas script, verbatim ==")
out = agents.handle_message("ms_demo_gas")
step = out["steps"][0]
ok(step["action"] == "gas_script", "a gas smell gets the script")
ok(core.GAS_SCRIPT in step["draft"], "the evacuate script rides VERBATIM")
ok("leave the house now" in step["draft"] and "911" in step["draft"], "the script says leave + 911")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dismiss_gas_smell"
       for e in store.events()), "dismiss_gas_smell refused + logged")
ok("yourco" not in step["draft"].lower(), "white-label")
out = agents.handle_message("ms_demo_noheat")
ok(out["steps"][0]["action"] == "emergency_dispatch", "no-heat dispatches, never queues")
ok("yourco" not in out["steps"][0]["draft"].lower(), "white-label (emergency)")

print("== the evidence-priced quote: every factor in dollars ==")
home = store.by_id("homes", "hm_demo_full")
q = core.membership_quote(home)
ok(not q["provisional"], "a full record prices personalized")
ok(abs(sum(f["dollars"] for f in q["factors"]) - q["monthly"]) < 0.005,
   "the shown factors ARE the price, to the cent")
labels = {f["label"]: f for f in q["factors"]}
ok(labels["furnace age"]["dollars"] == 9.0, "the 19-year furnace prices at the 15-year band (+$9)")
ok("19 years old" in labels["furnace age"]["why"], "the factor names the age")
ok(labels["clean history"]["dollars"] == -4.0, "zero callbacks earns the recorded credit (−$4)")
ok(labels["base plan"]["dollars"] == 18.0, "the recorded base rides as its own factor")
ok("DEFAULT evidence-pricing table" in q["table_source"], "the pricing table names its source")
ok(q["monthly"] == 26.0, "the demo quote computes to $26/mo")
okc, _ = core.quote_complete(q)
ok(okc, "quote_complete holds structurally")
ok(not core.quote_complete({"provisional": False, "monthly": 30.0,
                            "factors": q["factors"]})[0],
   "a price that exceeds its shown factors is caught as a hidden factor")
r = agents.draft_quote("hm_demo_full")
ok("line by line" in r["draft"] and "in both directions" in r["draft"],
   "the quote copy shows the math and the two-way promise")
ok(r["gate"]["rung"] == "R1", "the quote drafts at R1 — a human sends")
ok("yourco" not in r["draft"].lower(), "white-label (quote)")

print("== the unrecorded age: UNKNOWN → provisional, never guessed ==")
thin = store.by_id("homes", "hm_demo_thin")
bx = core.blackbox(thin)
wh = next(c for c in bx["components"] if c["kind"] == "water_heater")
ok(wh["age_years"] is None and "UNKNOWN" in wh["age_label"], "the black box reads UNKNOWN")
q2 = core.membership_quote(thin)
ok(q2["provisional"], "an unrecorded age makes the quote PROVISIONAL")
ok(q2["factors"] == [], "no per-component factors are faked")
ok("water_heater" in q2["reason"] and "prohibited" in q2["reason"],
   "the reason names the component and the prohibition")
ok(q2["monthly"] == 24.0, "the flat recorded provisional rate, nothing personalized")
r2 = agents.draft_quote("hm_demo_thin")
ok("refused" in r2 and "NOT produced" in r2["refused"], "the personalized price is refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "invent_component_age"
       for e in store.events()), "invent_component_age refused + logged")
ok("can't give you a personalized price yet" in r2["draft"], "the draft says so honestly")

print("== reprice_mid_term: structurally absent ==")
for name in ("reprice_mid_term", "set_locked_price", "update_locked_price",
             "change_member_price", "set_member_price", "midterm_reprice", "adjust_price"):
    ok(not hasattr(core, name) and not hasattr(agents, name), f"no code path named {name}")
m0 = store.by_id("members", "mb_demo_locked")
locked_before = m0["locked_price"]
r = core.gate.act("reprice_mid_term", "membership", "mb_demo_locked", {})
ok(r.get("refused") and r["rung"] == "R0", "a mid-term reprice probe is refused at R0")
ok(store.by_id("members", "mb_demo_locked")["locked_price"] == locked_before,
   "the locked price did not move")
ok(not any(a["action"] == "reprice_mid_term" for a in store.load("approvals")),
   "R0 never becomes an approvable row")

print("== renewal re-price: the deltas ride verbatim ==")
r = agents.renewal_notice("mb_demo_renew_up")
rp = r["reprice"]
ok(rp["direction"] == "up" and rp["locked_price"] == 24.0 and rp["new_monthly"] == 30.0,
   "the renewal computes 24 → 30")
d = next((x for x in rp["deltas"] if x["label"] == "furnace age"), None)
ok(d and d["delta"] == 6.0, "the furnace delta is +$6")
ok(d and "furnace crossed the 15-year band: +$6/mo" in d["why"], "the delta names the band crossing")
ok(d and d["why"] in r["draft"], "the renewal draft carries the delta VERBATIM")
ok(r["gate"]["rung"] == "R1", "the renewal notice drafts at R1")
ok("yourco" not in r["draft"].lower(), "white-label (renewal)")
r = agents.renewal_notice("mb_demo_renew_down")
rp = r["reprice"]
ok(rp["direction"] == "down" and rp["new_monthly"] == 22.0 and rp["locked_price"] == 32.0,
   "the down renewal computes 32 → 22")
lbls = {x["label"]: x for x in rp["deltas"]}
ok("callback history" in lbls and lbls["callback history"]["delta"] == -6.0,
   "callbacks aging out shows as −$6")
ok("clean history" in lbls and lbls["clean history"]["delta"] == -4.0,
   "the clean-history credit arrives as −$4")
ok("DOWN" in r["draft"], "the down renewal says DOWN, proudly")

print("== the honesty board ==")
h = core.honesty_board()
ok(h.get("went_down", 0) >= 1, "renewals that went DOWN are counted")
ok(h["renewed"] >= h["went_down"] + h.get("went_up", 0), "the board's arithmetic holds")
ok("counted" in h["note"], "the board names its basis")

print("== the fairness challenge: your factors, never the market ==")
out = agents.handle_message("ms_demo_fair")
step = out["steps"][0]
ok(step["action"] == "draft_fairness_reply", "the fairness challenge drafts a reply")
ok("your own home's record" in step["draft"], "the reply cites the asker's own record")
ok("19 years old" in step["draft"], "the asker's own furnace factor rides verbatim")
ok(core.fairness_ok(step["draft"])[0], "the shipped copy passes its own check structurally")
ok(not core.fairness_ok("that's just the market rate, everyone pays it")[0],
   "market-rate language is structurally refused")
ok("market" not in step["draft"].lower(), "no market language in the reply")
ok("yourco" not in step["draft"].lower(), "white-label (fairness)")

print("== matrix ==")
for a in ("invent_component_age", "reprice_mid_term", "hide_pricing_factor", "dismiss_gas_smell"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
for a in ("invent_component_age", "hide_pricing_factor", "dismiss_gas_smell"):
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused"), f"{a} probe refused")
    ok(not any(x["action"] == a and x["state"] == "pending" for x in store.load("approvals")),
       f"{a} never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no emergency missed")
ok("GAS SMELL" in ev["costly_note"] and ev["costly_note"][:20].upper() == ev["costly_note"][:20],
   "costly note is in caps and names the stake")
ok(ev["costly_label"] == "emergency", "the costly label is the emergency")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(r["recorded"]["quotes_90d"] >= 1, "quotes drafted are counted, not asserted")
ok("avg_monthly" in r["recorded"], "avg member price is counted")
lines = {l["label"]: l for l in r["lines"]}
ok(lines["Membership conversion"]["kind"] == "revenue", "conversion is typed revenue")
ok(lines["The price-trust story"]["kind"] == "scenario", "the trust story is a scenario")
ok(lines["The price-trust story"]["value"] is None
   and "trust_value" in lines["The price-trust story"]["_missing"],
   "the scenario line is blank until the operator owns a number")
ok(lines["Office hours on quoting & renewal math"]["kind"] == "time_saved",
   "office hours are time_saved, never summed into revenue")

print("== renewal sweep skips demo fixtures ==")
before = {m["id"]: m.get("renewal_price") for m in store.load("members") if m.get("demo_tag")}
sw = agents.renewal_sweep()
after = {m["id"]: m.get("renewal_price") for m in store.load("members") if m.get("demo_tag")}
ok(before == after, "the sweep never touches demo_tag members")
ok(sw["drafted"] + sw["skipped"] > 0, "the sweep ran over the book")

print("== this week, counted (baseline delta) ==")
base = core.won_this_week()
store.upsert("members", {"id": "mb_test_join", "home_id": "hm_0000", "owner": "Vance",
                         "locked_price": 21.0, "joined_at": iso(now()),
                         "term_start": iso(now()),
                         "term_end": iso(now() + timedelta(days=365))})
store.log_event("draft_quote", "hm_0000", "human:owner", "R1", {})
core.gate.act("draft_quote", "membership", "hm_0001", {"summary": "agent draft"})
rec = core.won_this_week()
ok(rec["members_joined"] == base["members_joined"] + 1, "a joined member counts")
ok(rec["quotes_sent"] == base["quotes_sent"] + 1,
   "a HUMAN-sent quote counts; the agent's gated draft does not")
ok("counted" in rec["note"], "the week names its basis")

print("== append-only events ==")
n0 = len(store.events())
store.log_event("probe", "x", "human:test", None, {})
ok(len(store.events()) == n0 + 1, "events only ever grow")
ok(not hasattr(store, "delete_event") and not hasattr(store, "rewrite_event"),
   "no code path deletes or rewrites an event")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused with the reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
