#!/usr/bin/env python3
"""Deal OS — the suite. `python3 test_deal_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["DEALOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="dealos_test_")
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
ok(len(store.load("listings")) >= 90, "listings seeded")
ok(len(store.load("comps")) > 100, "comps seeded")

print("== the mortgage math is pinned to hand-checked fixtures ==")
# $300,000 at 6% / 30yr — the canonical fixture: payment $1,798.65
p = core.monthly_payment(300000, 0.06, 30)
ok(abs(p - 1798.65) < 0.01, f"payment fixture: got {p:.2f}, want 1798.65")
am = core.amortization(300000, 0.06, 30)
ok(am["payoff_month"] == 360, "no-extra payoff is exactly month 360")
ok(abs(am["total_interest"] - 347514.57) < 1.0,
   f"total interest fixture ~347,514 (got {am['total_interest']:,.0f})")
am2 = core.amortization(300000, 0.06, 30, extra_monthly=300)
ok(am2["payoff_month"] < 300, f"$300/mo extra pays off years early (month {am2['payoff_month']})")
ok(am2["total_interest"] < am["total_interest"] * 0.75,
   "and saves more than a quarter of the interest")
ok(core.monthly_payment(120000, 0.0, 30) == 120000 / 360, "zero-rate edge is straight division")
bad = core.amortization(100000, 0.30, 30, extra_monthly=-3000)
ok("error" in bad, "a payment that can't cover interest says so, never loops forever")

print("== triage: the advice ask reads first ==")
for case in core.EVAL_CASES:
    got = core.read_message(case["input"])["label"]
    ok(got == case["label"],
       f"triage: {case['input'][:44] or '(empty)'} → {case['label']} (got {got})")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no advice ask missed")
ok("UNLICENSED INVESTMENT ADVICE" in ev["costly_note"], "costly note names the stake")

print("== the advice line: never a verdict ==")
out = agents.handle_message("ms_demo_advice")
step = out["steps"][0]
ok("no verdict was produced" in step["refused"], "no verdict — stated in the refusal")
ok("decision" in step["draft"] and "yours" in step["draft"], "the decision stays theirs")
ok("Not investment advice" in step["draft"], "the not-advice line ships in the copy")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "recommend_purchase"
       for e in store.events()), "recommend_purchase refused + logged")
ok(core.advice_ok(step["draft"])[0], "the shipped copy passes its own guarantee check")
ok(not core.advice_ok("this one is guaranteed to appreciate, you can't lose")[0],
   "guarantee language is structurally refused")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== underwriting traces to inputs ==")
l = store.by_id("listings", "ls_demo_birch")
uw = core.underwrite(l, "ltr")
ok("refused" not in uw, "the Harbor Point demo underwrites as LTR")
ok(uw["label"].startswith("THIS IS A MODEL"), "the result labels itself a model")
ok("assumptions" in uw["inputs"] and uw["inputs"]["assumptions"]["down_pct"] == 0.25,
   "every assumption rides the result (provenance)")
ok(uw["inputs"]["comps"]["n"] >= 5, "the rent number cites its comp count")
ok(uw["dscr"] is not None and uw["cash_on_cash"] is not None, "DSCR and CoC computed")
# hand-check NOI consistency: cashflow = NOI - debt service, CoC = cashflow / cash_in
ok(abs(uw["cashflow_year1"] - (uw["noi"] - uw["debt_service"])) < 1.0,
   "cashflow is exactly NOI minus debt service")
ok(abs(uw["cash_on_cash"] - uw["cashflow_year1"] / uw["cash_in"]) < 5e-4,
   "CoC is cashflow over cash in (to rounding)")
uw_ovr = core.underwrite(l, "ltr", {"down_pct": 0.40})
ok(uw_ovr["cash_in"] > uw["cash_in"] and uw_ovr["inputs"]["assumptions"]["down_pct"] == 0.40,
   "overriding an assumption changes the math and shows on the sheet")

print("== the comp floor: no comps, no number ==")
fern = store.by_id("listings", "ls_demo_fern")
uw_str = core.underwrite(fern, "str")
ok("refused" in uw_str and "floor is" in uw_str["refused"],
   "Maplewood STR refuses — the floor and count are named, occupancy is not invented")
r0 = gate.act("estimate_below_comp_floor", "probe", "x", {})
ok(r0.get("refused"), "R0 probe refused")
ok(not any(a["action"] == "estimate_below_comp_floor" and a["state"] == "pending"
           for a in store.load("approvals")), "and never becomes an approvable row")
uw_fern_ltr = core.underwrite(fern, "ltr")
ok("refused" not in uw_fern_ltr, "the same listing underwrites fine where comps exist (LTR)")

print("== bands, never points ==")
b = core.exit_bands(l, "ltr", 10)
ok(set(b["bands"]) == {"bear", "base", "bull"}, "a 10-year exit is three bands")
ok(b["bands"]["bear"]["exit_value"] < b["bands"]["base"]["exit_value"]
   < b["bands"]["bull"]["exit_value"], "and the bands are ordered")
ok("fiction" in b["label"], "the label says why one number would be a lie")
ok("trailing" in b["appreciation_basis"], "base growth is the market's own recorded history")
pt = core.point_estimate(l, "ltr", 10)
ok("refused" in pt and "fiction" in pt["refused"],
   "a 10-year point estimate is refused outright")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action")
       == "project_point_estimate_long_horizon" for e in store.events()),
   "and the refusal is on the record")
pt2 = core.point_estimate(l, "ltr", 2)
ok("refused" not in pt2, "the near horizon still answers (with bands attached)")
irr = core._irr([-100, 0, 0, 0, 0, 200])
ok(irr is not None and abs(irr - 0.1487) < 0.002,
   f"IRR bisection fixture: double in 5 years ≈ 14.9% (got {irr})")

print("== the stress grid ==")
g = core.sensitivity(l, "ltr")
ok(len(g["grid"]) == 5 and len(g["grid"][0]) == 3, "5 rate rows × 3 rent columns")
worst = g["grid"][-1][0]
best = g["grid"][0][-1]
ok(worst["dscr"] < best["dscr"], "the worst corner is honestly worse than the best")
ok("bottom-right corner" in g["note"] or "doesn't work" in g["note"],
   "the note says what the grid is for")

print("== the deal screen ranks by THEIR bar ==")
scr = core.deal_screen()
ok("refused" not in scr, "criteria exist — the screen runs")
crit = scr["criteria"]
for r in scr["rows"]:
    ok(r["dscr"] >= crit["min_dscr"] and r["cash_on_cash"] >= crit["min_coc"],
       f"every ranked row clears the recorded bar ({r['listing']['id']})")
    break
ok(all(r["dscr"] >= crit["min_dscr"] for r in scr["rows"]), "…all rows clear min DSCR")
ok(all("YOUR bar" in r["why"] for r in scr["rows"]), "every row carries its why-trace")
ok(scr["skipped"]["below_bar"] + scr["skipped"]["over_price"] > 0,
   "and what was skipped is counted, not hidden")
ok("Not investment advice" in scr["not_advice"], "the screen itself carries the line")
store.save("criteria", [])
scr2 = core.deal_screen()
ok("refused" in scr2 and "your bar, not ours" in scr2["refused"],
   "no recorded criteria → no ranking")
seed.main()  # restore

print("== stale data flags, never silently used ==")
mk = store.by_id("markets", "mk_cedar")
r = core.market_rate(mk)
ok(r["stale"] is True and "STALE" in r["note"], "Cedar Falls' 44-day-old rate reads stale")
cedar_listing = next(x for x in store.load("listings")
                     if x["market_id"] == "mk_cedar" and not x.get("demo_tag"))
uw_c = core.underwrite(cedar_listing, "ltr")
ok(uw_c.get("stale_flag") is True, "and every underwrite it feeds carries the flag")
fresh = core.market_rate(store.by_id("markets", "mk_harbor"))
ok(fresh["stale"] is False, "a fresh rate doesn't cry wolf")

print("== appreciation honesty ==")
ok("cagr" in core.appreciation_base(store.by_id("markets", "mk_maple")),
   "history-backed market yields a trailing CAGR")
ok(core.appreciation_base({"appreciation_history": []}).get("_missing"),
   "no history → unmeasured, 'astrology' named")

print("== the sweeps ==")
sw = agents.screen_sweep()
ok(sw["alerts_drafted"] >= 1, "new matches draft alerts")
g1 = [e for e in store.events(kind="queued_for_approval")
      if (e.get("detail") or {}).get("action") == "draft_deal_alert"]
ok(g1 and g1[-1].get("rung") == "R1", "a six-figure nudge queues R1 — it never sends itself")
rw = agents.rate_watch()
ok("mk_cedar" in rw["flagged"], "the rate watch flags the stale market")

print("== matrix ==")
for a in ("recommend_purchase", "guarantee_return", "project_point_estimate_long_horizon",
          "estimate_below_comp_floor"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r0 = gate.act("recommend_purchase", "probe", "x", {})
ok(r0.get("refused") and not any(a["action"] == "recommend_purchase" and a["state"] == "pending"
                                 for a in store.load("approvals")),
   "R0 probe refused and never approvable")

print("== roi + counted week ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the operator ROI labels itself a model")
labels = {x["label"]: x for x in r["lines"]}
ok(labels["The bad buy avoided"]["kind"] == "scenario"
   and labels["The bad buy avoided"]["value"] is None,
   "the bad-buy line is a scenario that stays blank")
base_wk = core.screened_this_week()
agents.analyze("ls_demo_birch")
store.log_event("draft_deal_alert", "ls_x", "human:operator", "R1", {})
store.log_event("draft_deal_alert", "ls_y", "agent:screener", "R1", {})
wk = core.screened_this_week()
ok(wk["underwrites"] == base_wk["underwrites"] + 1, "an underwrite is counted")
ok(wk["alerts_sent"] == base_wk["alerts_sent"] + 1,
   "human sends count; agent drafts don't")

print("== automation + append-only ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")
ids = [e["id"] for e in store.events()]
agents.rate_watch()
ok([e["id"] for e in store.events()][:len(ids)] == ids, "the event log is append-only")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
