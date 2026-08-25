#!/usr/bin/env python3
"""Quote Desk OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["QUOTEDESK_DATA_ROOT"] = tempfile.mkdtemp(prefix="quotedesk_test_")

import agents, core, seed                    # noqa: E402
from core import gate, store                 # noqa: E402
from _kit.store import iso, now              # noqa: E402

P = F = 0


def ok(c, l):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print(f"  FAIL: {l}")


def section(t):
    print(f"\n{t}")


CATALOG = [
    {"sku": "SKU-1001", "description": "1/2 in brass ball valve threaded", "list": 18.4,
     "cost": 11.2, "status": "active", "uom": "ea", "family": "valves", "spec": "1/2 in",
     "material": "brass"},
    {"sku": "SKU-1002", "description": "3/4 in brass ball valve threaded", "list": 24.1,
     "cost": 15.0, "status": "active", "uom": "ea", "family": "valves", "spec": "3/4 in",
     "material": "brass"},
    {"sku": "SKU-1003", "description": "1 in bronze gate valve", "list": 40.0, "cost": 24.0,
     "status": "discontinued", "superseded_by": "SKU-1004", "uom": "ea", "family": "valves",
     "spec": "1 in", "material": "bronze"},
    {"sku": "SKU-1004", "description": "1 in stainless gate valve", "list": 52.0, "cost": 30.0,
     "status": "active", "uom": "ea", "family": "valves", "spec": "1 in", "material": "stainless"},
]
CUST = {"id": "cu_1", "name": "YourCo", "tier": "standard", "bought": ["SKU-1001"],
        "agreement": {"SKU-1002": 17.00}, "ship_to": "Dock 3", "terms": "Net 30"}
OTHER = {"id": "cu_2", "name": "Beta", "tier": "spot", "bought": [], "agreement": {}}
XREF = [{"customer_id": "cu_1", "customer_part": "YOURCO-77", "sku": "SKU-1001"}]

section("a low-confidence line never enters a quote")
for desc in ["widget", "", "part per drawing", "misc hardware as discussed", "same as last order"]:
    m = core.match_line({"description": desc, "qty": 1}, CATALOG, CUST, XREF)
    ok(not m["sku"] or m["confidence"] < core.MATCH_THRESHOLD,
       f"'{desc}' does not produce a confident match")
    ok(m["why"], "and it says why")

amb = core.match_line({"description": "brass ball valve threaded", "qty": 1}, CATALOG, CUST, XREF)
ok(amb["sku"] is None, "two catalog items scoring almost the same yields NO match")
ok("almost the same" in amb["why"], "and the reason names both candidates")

good = core.match_line({"description": "YOURCO-77", "customer_part": "YOURCO-77", "qty": 4},
                       CATALOG, CUST, XREF)
ok(good["sku"] == "SKU-1001" and good["confidence"] > 0.9, "their part number matches via xref")
ok("cross-reference" in good["why"], "and says it came from the cross-reference")
ok(core.match_line({"description": "SKU-1002", "qty": 1}, CATALOG, CUST, XREF)["sku"] == "SKU-1002",
   "our own SKU verbatim matches")
noxref = core.match_line({"description": "BETA-99", "customer_part": "BETA-99", "qty": 1},
                         CATALOG, CUST, XREF)
ok(noxref["sku"] is None and "not in our cross-reference" in noxref["why"],
   "an unknown customer part is stated as unknown, not guessed")

e = core.eval_matching()
ok(e["costly_missed"] == 0, "no line that should have been queued was matched instead")
ok(e["costly_recall"] == 1.0, "recall on 'queue' is reported alone and is 1.0")

section("one customer's pricing can never price another")
p1 = core.price_line(CATALOG[1], CUST, 10)
p2 = core.price_line(CATALOG[1], OTHER, 10)
ok(p1["unit"] == 17.00 and p1["basis"] == "customer agreement", "YourCo gets its agreed price")
ok(p2["unit"] != 17.00, "Beta does not")
ok("tier" in p2["basis"], "Beta is priced from its own tier")
ok("cross_customer_price" in core.MATRIX.never_promote(),
   "cross-customer pricing is declared and never promotes")
ok(core.MATRIX.rung_for("cross_customer_price")["rung"] == "R0", "at R0 — the system never does it")

section("the margin floor")
cheap = {"sku": "SKU-9", "description": "x", "list": 10.0, "cost": 9.5, "status": "active"}
ok(core.price_line(cheap, CUST, 1)["below_floor"] is True, "a thin line is flagged below floor")
ok(core.price_line(CATALOG[0], CUST, 1)["below_floor"] is False, "a healthy line is not")
ok(core.MATRIX.rung_for("price_below_floor")["rung"] == "R1", "below-floor pricing is gated")
ok("price_below_floor" in core.MATRIX.never_promote(), "and never promotes")

section("a substitution is never silent")
sub = core.substitution_for(CATALOG[2], CATALOG)
ok(sub and sub["proposed"] == "SKU-1004", "a discontinued part proposes its successor")
ok(any(d["field"] == "material" for d in sub["differences"]),
   "and the material difference is named, not buried")
ok(sub["silent_ok"] is False, "the substitution is explicitly not silent-safe")
ok(core.substitution_for(CATALOG[0], CATALOG) is None, "an active part needs no substitution")
orphan = dict(CATALOG[2], superseded_by="SKU-NOPE")
ok(core.substitution_for(orphan, CATALOG)["proposed"] is None,
   "a discontinued part with no successor on file proposes nothing")
ok("propose_substitution" in core.MATRIX.never_promote(), "substitutions never promote")

section("a discrepant PO never becomes an order")
quote = {"lines": [{"sku": "SKU-1001", "qty": 20, "unit": 24.5, "uom": "ea"},
                   {"sku": "SKU-1002", "qty": 8, "unit": 61.0, "uom": "ea"}],
         "ship_to": "Dock 3", "terms": "Net 30"}
clean = {"lines": [dict(l) for l in quote["lines"]], "ship_to": "Dock 3", "terms": "Net 30"}
ok(core.reconcile(clean, quote)["clean"], "a matching PO reconciles")
for mutation, kind in [
        ({"lines": [{**quote["lines"][0], "qty": 200}, quote["lines"][1]]}, "quantity"),
        ({"lines": [{**quote["lines"][0], "unit": 22.0}, quote["lines"][1]]}, "price"),
        ({"lines": [{**quote["lines"][0], "uom": "bx"}, quote["lines"][1]]}, "uom"),
        ({"lines": [quote["lines"][0]]}, "sku"),
        ({"ship_to": "Somewhere else"}, "ship_to"),
        ({"terms": "Net 60"}, "terms")]:
    po = {**clean, **mutation}
    r = core.reconcile(po, quote)
    ok(not r["clean"], f"a {kind} discrepancy is caught")
    ok(any(d["type"] == kind for d in r["discrepancies"]), f"and typed as {kind}")
    ok("WHOLE order holds" in r["why"], "and the whole order holds, not just the line")
ok(core.MATRIX.rung_for("write_discrepant_order")["rung"] == "R0",
   "writing a discrepant order is R0 — the system never does it")
ok("write_discrepant_order" in core.MATRIX.never_promote(), "and never promotes")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.turnaround([]).get("_missing"), "too few quotes → no median turnaround")
ok(core.open_quote_value([]).get("_missing"), "no sent quotes → no open value")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
win = [l for l in core.roi({"rfqs_wk": 90, "hours_saved_per_quote": 0.5,
                            "loaded_rate": 38})["lines"] if l["label"].startswith("Win-rate")][0]
ok(win["value"] is None, "the win-rate line stays blank")
ok("WILL NOT PUT A NUMBER HERE" in win["note"],
   "and says on its face it will not borrow an industry statistic")
ok("90 days" in win["note"], "naming what would be needed instead")

section("the seeded distributor, end to end")
st = seed.build(12, 20)
ok(st["catalog"] > 40 and st["rfqs"] > 200, "the seed builds a distributor with a year of history")

r = agents.build_quote("rq_demo")
q = r["quote"]
ok(r["queued"] >= 2, "the messy demo RFQ queues its unguessable lines")
ok(all(l["confidence"] >= core.MATCH_THRESHOLD for l in q["lines"]),
   "and every priced line cleared the threshold")
ok(r["substitutions"] >= 1, "the discontinued part produces a substitution proposal")
ok(q["state"] in ("awaiting_approval", "queued_for_human"),
   "so the quote does not go out on its own")

res = agents.ingest_po("po_demo")
ok(res["verdict"] == "exception", "the PO with a quantity difference is an exception")
ok(any(d["type"] == "quantity" for d in res["discrepancies"]), "typed as a quantity difference")
ok(not store.load("orders"), "and no order was written")
clean_res = agents.ingest_po("po_demo_clean")
ok(clean_res["verdict"] == "order", "the clean PO writes an order")
ok(len(store.load("orders")) == 1, "exactly one order exists")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "write_discrepant_order" and e["rung"] != "R0" for e in evs),
   "no discrepant order ever executed")
ids = [e["id"] for e in evs]
agents.followups()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

led = core.margin_ledger()
thin = [k for k, v in led["by_family"].items() if v.get("_missing")]
ok(led["decided_quotes"] > 100, "the ledger has recorded outcomes")
ok(isinstance(led["by_turnaround"], dict), "and buckets turnaround")
ok(all("win_rate" in v or "_missing" in v for v in led["by_discount_depth"].values()),
   "every bucket either has a rate or says why not")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("cross_customer_price", "quoter", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before, "and it adds nothing to the approval queue")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "cross_customer_price"
       for e in store.load("events")), "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
