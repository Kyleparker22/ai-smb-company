#!/usr/bin/env python3
"""Provenance OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["PROVOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="provos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core, seed
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


seed.build(n_batches=40)
SKUS = store.load("skus")

# ---------------------------------------------------------------- the watcher
i = core.impact({"id": "x", "title": "Compounded semaglutide guidance",
                 "summary": "semaglutide preparations"}, SKUS)
ok(i["n"] >= 1, "a change naming an analyte lands on that SKU")
ok(any("names Semaglutide" in w for h in i["affected"] for w in h["why"]),
   "the flag says which word matched")
ok(core.WATCH_SCOPE in i["scope"], "every impact read carries the scope refusal")

i = core.impact({"id": "x", "title": "GLP-1 claims", "summary": "weight management claims"}, SKUS)
ok(i["n"] >= 1, "an alias match lands")
ok(any("alias" in w or "claim" in w for h in i["affected"] for w in h["why"]),
   "an alias or claim match is explained as such")

i = core.impact({"id": "x", "title": "Sunscreen monograph", "summary": "OTC sunscreen actives"}, SKUS)
ok(i["n"] == 0, "an unrelated change names nothing")
ok(i["verdict"] == "no product on your list is named", "a clear change says so plainly")
ok("compliant" not in i["verdict"], "the watcher never uses the word compliant as a verdict")

i = core.impact({"id": "x", "title": "Sterile injection standards",
                 "summary": "products for injection"}, SKUS)
ok(i["n"] >= 1, "a route restriction lands on injectable SKUs")

# ---------------------------------------------------------------- the batch packet
b = store.load("batches")[0]
d = core.dossier(b["id"])
ok("records_missing" in d, "a packet always reports what is missing")
ok(d["complete"] is (not d["records_missing"] and d["supplier_coa"] == "verified"),
   "complete requires BOTH every record and a verified upstream certificate")

thin = {"id": "B9999", "lot": "L1", "sku": "Test", "made_at": iso(now()), "quantity": 10,
        "supplier_coa_id": None,
        "records": [{"kind": "formula", "at": iso(now())}]}
store.upsert("batches", thin)
d = core.dossier("B9999")
ok(d["complete"] is False, "a thin packet is never complete")
ok(len(d["records_missing"]) == len(core.REQUIRED_RECORDS) - 1, "every absent record is named")
ok("missing" in d["supplier_coa"], "a batch with no upstream certificate says so")
ok(any("upstream" in x for x in d["blockers"]), "the blocker list names the upstream problem")

r = agents.release_batch("B9999", "qa.lead")
ok(r.get("refused") == "the batch packet is incomplete", "an incomplete packet blocks release")
ok(store.by_id("batches", "B9999").get("released_at") is None, "the lot stays unreleased")
ok(len(r["blockers"]) > 0, "the refusal lists what is missing")

# ---------------------------------------------------------------- upstream verification
good = {"id": "c-good", "supplier": "Meridian API", "issuer": "Rivermark Analytical",
        "analyte": "BPC-157", "claimed_analyte": "BPC-157", "lot": "A1", "received_lot": "A1",
        "purity_pct": 99.1, "expires_at": iso(now() + timedelta(days=300)), "state": "unverified"}
store.upsert("supplier_coas", good)
v = core.verify_supplier_coa("c-good")
ok(v["ok"] is True and v["state"] == "verified", "a clean upstream certificate verifies")

for field, val, expect in [("issuer", "", "no issuing laboratory named"),
                           ("received_lot", "A2", "does not match received lot"),
                           ("claimed_analyte", "Semaglutide", "the material was received as"),
                           ("purity_pct", None, "no purity value reported")]:
    bad = dict(good, id=f"c-{field}")
    bad[field] = val
    store.upsert("supplier_coas", bad)
    v = core.verify_supplier_coa(bad["id"])
    ok(v["ok"] is False, f"a certificate with a bad {field} is rejected")
    ok(any(expect in p for p in v["problems"]), f"the rejection explains the {field} problem")

expired = dict(good, id="c-exp", expires_at=iso(now() - timedelta(days=30)))
store.upsert("supplier_coas", expired)
v = core.verify_supplier_coa("c-exp")
ok(v["ok"] is False and any("expired" in p for p in v["problems"]),
   "an expired upstream certificate is rejected and says how long ago")

# ---------------------------------------------------------------- complaints
a = agents.intake_complaint("I got a rash and shortness of breath after the injection")
ok(a["label"] == "adverse_event", "a health outcome is classed as an adverse event")
ok(a.get("refused") == "no assessment of any kind was made", "an adverse event is never assessed")
ok("not able to give medical advice" in a["reply"], "the reply says plainly that it cannot advise")
ok("emergency" in a["reply"].lower(), "the reply points to emergency care")
ok(store.by_id("complaints", a["complaint"])["assessed"] is False, "the record shows it was not assessed")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "assess_adverse_event"
       for e in store.events()), "the non-assessment is logged as a refusal")

p = agents.intake_complaint("the vial arrived cloudy with crystals and the seal was cracked")
ok(p["label"] == "product_quality", "a product fault is classed as product quality")
ok("refused" not in p, "a product complaint needs no clinical refusal")

# the inflected forms — a trailing \\b after a prefix used to drop every one of these
for text, exp in [("I've been vomiting since the injection", "adverse_event"),
                  ("numbness in my hand", "adverse_event"),
                  ("shortness of breath all night", "adverse_event"),
                  ("swelling around the site", "adverse_event"),
                  ("it looks infected", "adverse_event"),
                  ("the vial was mislabeled", "product_quality"),
                  ("the syringe is leaking", "product_quality"),
                  ("discoloured liquid inside", "product_quality")]:
    ok(core.classify_complaint(text)["label"] == exp,
       f"inflected form classifies: {text[:32]!r} -> {exp}")

o = agents.intake_complaint("can you send me a copy of my invoice")
ok(o["label"] == "other", "an admin message is neither")

# ---------------------------------------------------------------- the never-promotables
for a_ in ("alter_batch_record", "assert_compliance", "assess_adverse_event"):
    ok(core.matrix.rung_for(a_)["rung"] == "R0", f"{a_} is R0")
    ok(a_ in core.matrix.never_promote(), f"{a_} can never be promoted")
ok(core.matrix.rung_for("release_batch")["rung"] == "R1", "release sits at the gate")
ok(core.matrix.promotable("release_batch", streak=100000)["promote"] is False,
   "no streak promotes a lot release")
before = len(core.gate.pending())
res = core.gate.act("assert_compliance", "watcher", "q", {})
ok(res.get("refused") is True, "asserting compliance is refused outright")
ok(len(core.gate.pending()) == before, "an R0 refusal never becomes a clickable approval")

q = agents.answer_compliance_question("are we compliant with the new guidance?")
ok(q["refused"] is True, "the compliance question is refused")
ok("cannot tell you whether you are compliant" in q["reply"], "the refusal is explicit")

# ---------------------------------------------------------------- eval
ev = core.run_eval()
ok(ev["costly_label"] == "affects", "the costly class is a change that lands on a product")
ok(ev["costly_missed"] == 0, "no landing change is filed as irrelevant")
ok(ev["costly_recall"] == 1.0, "every landing change is caught")
ok("filed as irrelevant" in ev["costly_note"].lower(), "the eval names the failure it guards")

# ---------------------------------------------------------------- numbers refuse
store.save("batches", [])
pr = core.packet_readiness()
ok("_missing" in pr and pr["ready_rate"] is None, "readiness refuses on an empty book, never 0")
store.save("changes", [])
rl = core.review_lag()
ok("_missing" in rl and rl["median_days"] is None, "review lag refuses with nothing reviewed")

seed.build(n_batches=40)
pr = core.packet_readiness()
ok("_missing" not in pr and 0.0 <= pr["ready_rate"] <= 1.0, "readiness computes on a real book")

r = core.roi({})
ok(any(l.get("value") is None for l in r["lines"]), "ROI blanks with no operator inputs")
scen = [l for l in r["lines"] if l["kind"] == "scenario"]
ok(scen and "prevented incidents cannot be counted" in (scen[0].get("assumption") or ""),
   "the scenario line refuses to price a prevented regulatory event")
r2 = core.roi({"change_value": "20000"})
ok(r2["totals"]["scenario"]["total"] == 20000, "a scenario totals on its own")
ok(r2["totals"]["revenue"]["total"] is None, "a scenario never becomes revenue")
ok(all(l["kind"] != "revenue" for l in r2["lines"]),
   "this build claims no revenue line at all — it saves time and catches changes")

au = core.automation()
ok("rate" in au or "_missing" in au, "automation is counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
