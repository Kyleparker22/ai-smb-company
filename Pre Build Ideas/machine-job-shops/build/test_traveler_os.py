#!/usr/bin/env python3
"""Traveler OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["TRAVELEROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="traveleros-test-")
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


# ---------------------------------------------------------------- cert flags + eval
f = core.rfq_flags("qty 200 brackets, AS9100 required, certs with shipment")
ok(f["cert_required"] and "as9100" in f["flags"] and "traceability" in f["flags"],
   "AS9100 + certs language flags")
ok(core.rfq_flags("ITAR controlled drawing attached")["flags"] == ["itar"], "ITAR flags")
ok(core.rfq_flags("medical implant assembly, ISO 13485")["cert_required"], "medical flags")
ok(not core.rfq_flags("qty 50 pins, 303 stainless, need by friday")["cert_required"],
   "commercial work does not flag")

ev = core.run_eval()
ok(ev["costly_label"] == "cert" and ev["costly_missed"] == 0,
   f"zero missed cert flags in the shipped eval ({ev['costly_missed']})")
ok("BARBECUE" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- material freshness
store.wipe()
store.save("config", {"company": "t", "machine_rate_hr": 95, "margin_floor": 0.35})
store.save("materials", [
    {"id": "fresh", "label": "6061", "price": 4.2, "priced_at": iso(now() - timedelta(days=3))},
    {"id": "stale", "label": "Ti64", "price": 38.0, "priced_at": iso(now() - timedelta(days=40))},
    {"id": "undated", "label": "brass", "price": 5.9},
])
ok(core.material_check("fresh")["ok"], "a fresh price passes")
c = core.material_check("stale")
ok(not c["ok"] and "metal moved" in c["refused"], "a stale price refuses the quote")
c = core.material_check("undated")
ok(not c["ok"] and "guess with a number on it" in c["refused"], "an undated price refuses")
ok(not core.material_check("ghost")["ok"], "an unrecorded material refuses")

q = core.quote_rfq({"material": "fresh", "est_hours": 10, "material_qty": 20})
ok(q.get("total") and q["lines"]["material"] == 84.0, "a quote computes with the arithmetic shown")
q = core.quote_rfq({"material": "stale", "est_hours": 10, "material_qty": 20})
ok(q.get("refused"), "the stale-material quote refuses end to end")
q = core.quote_rfq({"material": "fresh", "material_qty": 20})
ok(q.get("refused") and "estimator sets hours" in q["refused"], "no hours → no quote")
store.save("config", {"company": "t", "margin_floor": 0.35})
q = core.quote_rfq({"material": "fresh", "est_hours": 10, "material_qty": 20})
ok(q.get("refused") and "fact, not a feeling" in q["refused"], "no machine rate → no quote")
store.save("config", {"company": "t", "machine_rate_hr": 95, "margin_floor": 0.35})

# ---------------------------------------------------------------- the cert gate
oks, why = core.can_ship({"cert_required": True, "material_cert_id": "m1", "inspection_id": "i1"})
ok(oks, "complete paper ships (via R1)")
oks, why = core.can_ship({"cert_required": True, "material_cert_id": None, "inspection_id": "i1"})
ok(not oks and "cannot certify" in why and "material cert" in why,
   "a missing material cert blocks with the paper named")
oks, why = core.can_ship({"cert_required": True, "material_cert_id": "m1", "inspection_id": None})
ok(not oks and "inspection record" in why, "a missing inspection blocks")
oks, why = core.can_ship({"cert_required": False})
ok(oks, "commercial work ships on sign-off")

store.save("jobs", [{"id": "j1", "name": "x", "cert_required": True,
                     "material_cert_id": None, "inspection_id": "i1"}])
r = agents.ship_job("j1")
ok("refused" in r and any(e["detail"].get("action") == "ship_without_certs"
                          for e in store.events(kind="refused", subject="j1")),
   "the ship refusal is logged")
ok(not any(a for a in store.load("approvals") if a.get("subject") == "j1"),
   "no release draft exists for the blocked job")

# ---------------------------------------------------------------- promise dates
store.save("machines", [])
p = core.promise_date(30)
ok(p.get("_missing") and "without the math" in p["_missing"],
   "no capacity recorded → no promise")
store.save("machines", [{"id": "m1", "capacity_hrs_wk": 100}])
store.save("jobs", [{"id": "j2", "hours_remaining": 200}])
p = core.promise_date(50)
ok(p["weeks_out"] == 2.5 and "not optimism" in p["basis"],
   "the promise is arithmetic: (200+50)/100 weeks")

# ---------------------------------------------------------------- OTD floor
store.save("jobs", [])
o = core.otd()
ok(o.get("_missing") and "need 20" in o["_missing"], "OTD refuses below its floor")
jobs = []
for i in range(30):
    promised = now() - timedelta(days=50)
    jobs.append({"id": f"o{i}", "promised_at": iso(promised),
                 "shipped_at": iso(promised + timedelta(days=-1 if i < 24 else 3))})
store.save("jobs", jobs)
o = core.otd()
ok(o["rate"] == 0.8, "OTD is counted: 24 of 30 on time")

# ---------------------------------------------------------------- R0 probes
for action in ("quote_stale_material", "ship_without_certs", "waive_inspection",
               "promise_without_capacity"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("quote_stale_material", "ship_without_certs", "waive_inspection",
                           "promise_without_capacity")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Same-day quotes won"]["value"] is None,
   "the quote line is blank without the operator's lift")
ok(labels["The cert discipline"]["kind"] == "scenario",
   "the cert discipline is never monetized by us")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("flight hardware, source inspection required before ship", True),
                   ("parts go on a surgical robot arm, dhr paperwork needed", True),
                   ("20 weld fixtures for the shop next door, no paper needed", False)):
    ok(core.rfq_flags(text)["cert_required"] == want, f"flags: {text[:44]} → cert={want}")

# ---------------------------------------------------------------- quote copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

q9 = {"total": 4820, "note": "6061 plate priced 2026-08-10"}
body = agents._quote_copy({}, q9, {"cert_required": True, "flags": ["as9100"]})
ok("$4,820" in body and "AS9100" in body, "the cover names the number and the cert regime")
ok("tell us if we've" in body, "the cert read is offered back for correction")
ok("Valid 14 days" in body and "metal moves" in body, "the quote expires out loud")
body2 = agents._quote_copy({}, q9, {"cert_required": False, "flags": []})
ok("AS9100" not in body2, "commercial work gets no cert line")
ok("yourco" not in (body + body2).lower(), "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
store.log_event("draft_quote", "rf1", "human:estimator", "R1", {})
store.log_event("release_to_ship", "jb1", "human:shipping", "R1", {})
store.log_event("draft_promise_date", "jb1", "human:scheduler", "R1", {})
rec = core.recovered_this_week()
ok(rec["quotes_sent"] == base["quotes_sent"] + 1
   and rec["jobs_shipped"] == base["jobs_shipped"] + 1
   and rec["dates_committed"] == base["dates_committed"] + 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
