#!/usr/bin/env python3
"""Gate OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["GATEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="gateos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core
from core import store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------- the SCRA stop
okl, why = core.can_lien_step({"military_flag": True, "scra_verified_at": iso()})
ok(not okl and "federal violation" in why, "a military-flagged tenant blocks every lien step")
okl, why = core.can_lien_step({"scra_verified_at": None})
ok(not okl and "unverified" in why, "an unverified tenant blocks too — the gamble has the same downside")
okl, why = core.can_lien_step({"scra_verified_at": iso(), "military_flag": False})
ok(okl, "verified non-military may proceed to the calendar")

store.wipe()
store.save("config", {"company": "t", "lien_rules": core.DEFAULT_LIEN_RULES})
store.save("tenants", [
    {"id": "t_mil", "name": "A", "state_code": "TX", "military_flag": True,
     "delinquent_since": iso(now() - timedelta(days=40))},
    {"id": "t_unv", "name": "B", "state_code": "TX", "scra_verified_at": None,
     "delinquent_since": iso(now() - timedelta(days=40))},
    {"id": "t_ok", "name": "C", "state_code": "TX",
     "scra_verified_at": iso(now() - timedelta(days=1)),
     "delinquent_since": iso(now() - timedelta(days=40))},
])
r = agents.lien_step("t_mil")
ok("refused" in r, "the agent path refuses the military lien step")
ok(any(e["kind"] == "refused" for e in store.events(subject="t_mil")), "the refusal is logged")
r = agents.lien_step("t_unv")
ok("refused" in r, "the unverified lien step is refused")
r = agents.lien_step("t_ok")
ok(r.get("calendar", {}).get("steps"), "the verified tenant gets the date-alert calendar")

# ---------------------------------------------------------------- the calendar
cal = core.lien_calendar(store.by_id("tenants", "t_ok"))
steps = {s["step"]: s for s in cal["steps"]}
ok(steps["lien notice"]["days_left"] in (-11, -10), "TX lien notice computes from delinquency (30d)")
ok(all(s["label"].startswith("DATE ALERT") for s in cal["steps"]),
   "every step is a date alert, not legal advice")
ok("replace with counsel-reviewed" in cal["rules_source"], "the rule set names itself a default")
cal = core.lien_calendar({"state_code": "ZZ", "scra_verified_at": iso(),
                          "delinquent_since": iso(now())})
ok(cal.get("_missing"), "a state with no rule set is refused, not defaulted")

# swap rules → dates move
custom = {"_source": "custom", "TX": {"steps": [
    {"key": "lien_notice", "label": "lien notice", "days_delinquent": 90}]}}
store.save("config", {"company": "t", "lien_rules": custom})
cal = core.lien_calendar(store.by_id("tenants", "t_ok"))
ok(cal["steps"][0]["days_left"] in (49, 50), "changing the rule set changes the computed dates")
store.save("config", {"company": "t", "lien_rules": core.DEFAULT_LIEN_RULES})

# ---------------------------------------------------------------- triage + eval
ok(core.read_message("I'm deployed overseas until March")["label"] == "military_signal",
   "a deployment message is a military signal")
ok(core.read_message("just got PCS orders")["label"] == "military_signal", "PCS orders signal")
ok(core.read_message("I'll pay friday I promise")["label"] == "payment_promise", "a promise records")
ok(core.read_message("moving out end of the month")["label"] == "moveout", "moveout classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")
ev = core.run_eval()
ok(ev["costly_label"] == "military_signal" and ev["costly_missed"] == 0,
   f"zero missed military signals in the shipped eval ({ev['costly_missed']})")
ok("FEDERAL VIOLATION" in ev["costly_note"], "the eval names the stake")

# a military message freezes the ladder on the tenant
store.save("messages", [{"id": "m1", "tenant_id": "t_ok",
                         "text": "my husband is active duty, he handles the unit", "at": iso()}])
r = agents.handle_message("m1")
t = store.by_id("tenants", "t_ok")
ok(t.get("military_flag") and not t.get("scra_verified_at"),
   "the signal flags the tenant and voids stale verification")
ok("refused" in agents.lien_step("t_ok"), "…and the ladder is now frozen for that tenant")
ok(any(a["action"] == "verify_scra" for a in store.load("approvals")),
   "human SCRA verification is queued")

# ---------------------------------------------------------------- dunning
t2 = {"id": "d1", "name": "D", "delinquent_since": iso(now() - timedelta(days=10)),
      "dunning_touches": [], "unit": "A1"}
plan = core.dunning_plan(t2)
ok(plan["action"] == "draft" and "work something out" in plan["text"],
   "the reminder template is gentle")
okt, why = core.dunning_text_ok("final warning before we auction your unit and sell your stuff")
ok(not okt and "never threatens" in why, "threat language is structurally refused")
t2["dunning_touches"] = [{"at": iso(now() - timedelta(days=30))}] * core.DUNNING_MAX_TOUCHES
ok(core.dunning_plan(t2)["action"] == "human", "the ladder is bounded — then a person")

# ---------------------------------------------------------------- occupancy
store.save("facilities", [{"id": "f1", "name": "A", "unit_count": 100},
                          {"id": "f2", "name": "B", "unit_count": None}])
store.save("tenants", [{"id": f"x{i}", "facility_id": "f1", "status": "active"} for i in range(60)])
occ = {o["facility"]: o for o in core.occupancy()}
ok(occ["A"]["rate"] == 0.6, "occupancy is counted")
ok(occ["B"]["rate"] is None and "denominator is missing" in occ["B"]["_missing"],
   "a facility with no unit count refuses its rate")

# ---------------------------------------------------------------- R0 probes
for action in ("initiate_auction", "cut_lock", "sell_contents", "threaten_tenant"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("initiate_auction", "cut_lock", "sell_contents", "threaten_tenant")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Delinquency days shortened"]["value"] is None,
   "the cash-timing line is blank without the operator's estimate")
ok(labels["The SCRA discipline"]["kind"] == "scenario",
   "SCRA discipline is never monetized — statutory damages are not our number")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("my wife is stationed at bragg, I'm listed on her unit", "military_signal"),
                   ("I will pay when I get paid on the 15th", "payment_promise"),
                   ("we'll be vacating unit 214 by sunday", "moveout")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

# ---------------------------------------------------------------- the stepped ladder copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

t9 = {"id": "tn9", "name": "Dev Osei", "unit": "B-214", "balance": 285, "status": "active",
      "delinquent_since": _iso(_now() - timedelta(days=12))}
store.upsert("tenants", t9)
p1 = core.dunning_plan(t9)
ok(p1["touch"] == 1 and "didn't come through" in p1["text"], "touch 1 is the friendly nudge")
t9["dunning_touches"] = [{"at": _iso(_now() - timedelta(days=6)), "step": 1}]
p2 = core.dunning_plan(t9)
ok(p2["touch"] == 2 and "$285" in p2["text"], "touch 2 states the ledger balance")
t9["dunning_touches"].append({"at": _iso(_now() - timedelta(days=6)), "step": 2})
p3 = core.dunning_plan(t9)
ok(p3["touch"] == 3 and "person calls you directly" in p3["text"],
   "touch 3 hands off to a human voice")
for p in (p1, p2, p3):
    okd, _w = core.dunning_text_ok(p["text"])
    ok(okd, f"touch {p['touch']} copy passes the threat check")
ok("yourco" not in (p1["text"] + p2["text"] + p3["text"]).lower(),
   "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- move-out copy
mo = agents._moveout_copy(t9)
ok("Dev" in mo and "B-214" in mo and "walkthrough" in mo,
   "move-out copy names tenant, unit, and the billing-stop rule")
ok("stops the billing" in mo, "the walkthrough date is stated as what stops the bill")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
base_cured = rec["delinquencies_cured"]
t9["cured_at"] = _iso(_now() - timedelta(days=1))
store.upsert("tenants", t9)
store.log_event("draft_reminder", "tn9", "human:manager", "R1", {})
rec = core.recovered_this_week()
ok(rec["delinquencies_cured"] == base_cured + 1 and rec["cured_value"] >= 285,
   "a cured delinquency is counted with its balance")
ok(rec["reminders_sent"] == 1, "human-sent reminders are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
