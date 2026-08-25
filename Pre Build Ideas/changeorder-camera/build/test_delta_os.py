#!/usr/bin/env python3
"""Delta OS — the suite. `python3 test_delta_os.py`."""
import inspect, os, sys, tempfile
from pathlib import Path

os.environ["DELTAOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="deltaos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
from _kit.store import iso, now, parse

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
ok(len(store.load("jobs")) == 6, "6 jobs seeded")
ok(len(store.load("plan_lines")) >= 40, "~40 plan lines seeded")
ok(len(store.load("observations")) >= 24, "~25 observations seeded")
ok(core.clause_for_job("jb_06") is None, "one contract deliberately has no notice clause")
ok(core.rate_schedule()["_source"].startswith("DEFAULT"), "the rate schedule names its source")

print("== triage: the backcharge reads first ==")
for text, want in [(c["input"], c["label"]) for c in core.EVAL_CASES]:
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]!r} → {want}")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no backcharge missed")
ok(ev["costly_label"] == "backcharge", "the costly label is the backcharge")
ok("MONEY GONE" in ev["costly_note"], "costly note names the stake")
ok(ev["n"] >= 15, "15+ labelled cases incl. the empty one")

print("== the diff engine ==")
r = core.diff("jb_01")
ok(r["clean_matches"] >= 1, "jb_01 has clean matches")
ok("dl_ob_demo_qty" in r["created"], "the quantity delta detected")
ok(not store.by_id("deltas", "dl_ob_clean_1"), "a matching observation produces NO delta")
for j in ("jb_02", "jb_03", "jb_04", "jb_05", "jb_06"):
    core.diff(j)
r2 = core.diff("jb_01")
ok(r2["created"] == [] and r2["already_detected"] >= 1, "diff is idempotent — no duplicate deltas")
ok(sum(1 for d in store.load("deltas")) == 7, "exactly the 7 seeded departures became deltas")

d_qty = store.by_id("deltas", "dl_ob_demo_qty")
ok(d_qty["classification_draft"] == "added_scope", "qty above plan drafts added_scope")
ok(d_qty["plan_says"] == '5/8" Type X drywall — 1200 sf (rev 3)', "plan-says cites spec, qty, rev")
ok("1450" in d_qty["field_shows"], "field-shows carries the observed qty")
ok(d_qty["photo_ref"] == "IMG_2214.jpg" and d_qty["plan_rev"] == 3, "photo ref + plan rev cited")
ok(d_qty["confirmed"] is False and "DRAFT" in d_qty["note"], "classification drafted, not final")
d_spec = store.by_id("deltas", "dl_ob_demo_spec")
ok(d_spec["classification_draft"] == "changed_spec", "spec departure drafts changed_spec")
d_rw = store.by_id("deltas", "dl_ob_demo_rework")
ok(d_rw["classification_draft"] == "rework", "tear-out language drafts rework")
d_un = store.by_id("deltas", "dl_ob_demo_unplanned")
ok(d_un["unplanned"] is True and d_un["plan_line_id"] is None, "no plan line → UNPLANNED delta")
ok("no plan line" in d_un["plan_says"], "the unplanned delta says so, never assumes")

print("== unconfirmed pricing refused — structurally ==")
r = agents.draft_change_order("dl_ob_demo_qty")
ok("refused" in r and "unconfirmed" in r["refused"], "pricing an unconfirmed delta refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "invoice_unconfirmed_delta"
       for e in store.events()), "invoice_unconfirmed_delta refused + logged R0")
ok(list(inspect.signature(core.co_math).parameters) == ["delta"],
   "co_math takes only the delta — no force/override parameter exists")
sig = inspect.signature(agents.draft_change_order).parameters
ok("force" not in sig and "override" not in sig and "skip_confirm" not in sig,
   "draft_change_order has no force path")
ok(not hasattr(core, "force_price") and not hasattr(agents, "force_price"),
   "no force_price anywhere")

print("== confirmation is the human act ==")
r = agents.confirm_delta("dl_ob_demo_qty")
ok("refused" in r and "human act" in r["refused"], "confirm without a human refused")
r = agents.confirm_delta("dl_ob_demo_qty", human="pm")
ok(r["confirmed"] and r["classification"] == "added_scope", "a human confirms the draft class")
r = agents.confirm_delta("dl_ob_demo_rework", human="pm", classification="changed_spec")
ok(r["overrode_draft"], "the human can override the drafted classification")
ok(store.by_id("deltas", "dl_ob_demo_rework")["confirmed_class"] == "changed_spec",
   "the confirmed class is the human's, recorded")

print("== the change order: recorded rates only ==")
r = agents.draft_change_order("dl_ob_demo_qty")
ok(r["math"]["amount"] == 250 * 3.10, "CO price = qty delta × the recorded rate (250sf × $3.10)")
ok("recorded rate schedule" in r["draft"], "the CO names its price source")
ok("IMG_2214.jpg" in r["draft"] and "rev 3" in r["draft"], "the CO cites the photo + plan rev")
ok(r["gate"]["rung"] == "R1" and not r["gate"]["executed"], "the CO queues for a human — never auto-sends")
agents.confirm_delta("dl_ob_demo_spec", human="pm")
r = agents.draft_change_order("dl_ob_demo_spec")
ok(r["math"]["amount"] == 800 * 5.40, "changed-spec CO prices the field spec from the schedule")
ok("never silently netted" in r["draft"], "the plan-spec credit is a stated human line")
agents.confirm_delta("dl_ob_demo_offsched", human="pm")
r = agents.draft_change_order("dl_ob_demo_offsched")
ok("refused" in r and "not on the recorded rate schedule" in r["refused"],
   "an off-schedule spec refuses to price")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "price_off_rate_schedule"
       for e in store.events()), "price_off_rate_schedule refused + logged R0")

print("== the notice letter: the recorded clause, verbatim ==")
st = core.notice_status({"days": 10, "text": "x", "method": "y"}, iso(now() - timedelta(days=3)))
ok(st["days_remaining"] == 7 and not st["expired"], "window math: 10-day clause, day 3 → 7 remain")
r = agents.draft_notice_letter("dl_ob_demo_qty")
clause = core.clause_for_job("jb_01")
ok(clause["text"] in r["draft"], "the recorded clause is cited VERBATIM in the letter")
ok(r["status"]["days_remaining"] == 10 and "DATE ALERT" in r["status"]["label"],
   "days remaining computed as a DATE ALERT, not legal advice")
ok("Days remaining: 10" in r["draft"], "the letter states the days remaining")
ok(r["gate"]["rung"] == "R1" and not r["gate"]["executed"], "the notice queues for a human")
ok("argues nothing" in r["draft"], "the notice preserves the record; it argues nothing")

print("== expired window: honest, never backdated ==")
agents.confirm_delta("dl_ob_demo_expired", human="pm")
r = agents.draft_notice_letter("dl_ob_demo_expired")
ok(r["status"]["expired"] and r["status"]["days_remaining"] == -7,
   "5-day clause, photo 12 days old → expired by 7")
ok(r["draft"].startswith("This letter is late and says so"),
   "the expired letter LEADS with the honest line")
ok("expired 7 days ago" in r["draft"], "it names how late")
ok("backdated notice is a forgery" in r["draft"], "it refuses to backdate, and says why")
ok(f"Dated: {iso(now())[:10]}" in r["draft"], "the letter is dated today — never backdated")
ok(core.clause_for_job("jb_04")["text"] in r["draft"], "the expired letter still cites the clause")

print("== no recorded clause: the letter refuses and names the gap ==")
agents.confirm_delta("dl_ob_demo_noclause", human="pm")
r = agents.draft_notice_letter("dl_ob_demo_noclause")
ok("refused" in r and "no notice clause recorded" in r["refused"], "no clause → no letter")
ok("Marquette Lofts" in r["refused"], "the refusal names the job with the gap")
ok("Record the clause" in r["refused"], "the refusal says how to fix it")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "notice_without_recorded_clause"
       for e in store.events()), "notice_without_recorded_clause refused + logged R0")
r = agents.draft_notice_letter("dl_ob_demo_spec")
ok("draft" in r or "confirm the delta first" in str(r.get("refused", "")),
   "a clause-bearing job drafts (or asks for the confirm first) — never silently skips")

print("== the verbal go-ahead: a note, not a signed change order ==")
deltas_before = len(store.load("deltas"))
out = agents.handle_message("ms_demo_verbal")
step = out["steps"][0]
ok(out["classification"]["label"] == "verbal_directive", "the go-ahead is read as a directive")
ok('"go ahead and add the soffit in the lobby, we\'ll paper it later"' in step["draft"],
   "the GC's words are quoted back VERBATIM")
ok("a note, not a signed change order" in step["draft"], "the quote-back names what the note is")
ok("a note, not a signed change order" in step["refused"], "no CO was created by the message")
ok(len(store.load("deltas")) == deltas_before, "the verbal directive created no delta and no CO")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "treat_verbal_as_signed"
       for e in store.events()), "treat_verbal_as_signed refused + logged R0")
job = store.by_id("jobs", "jb_01")
ok(any("soffit" in n["verbatim"] for n in job.get("verbal_notes") or []),
   "the verbatim note is on the job file")

print("== the backcharge: evidence pulled, never conceded, never argued ==")
out = agents.handle_message("ms_demo_backcharge")
step = out["steps"][0]
ok(out["classification"]["label"] == "backcharge", "the accusation is read as a backcharge")
ok(len(step["evidence"]["observations"]) >= 1 and step["evidence"]["plan_lines"] >= 1,
   "the dated record is pulled — photos and plan lines")
ok("concedes nothing and argues nothing" in step["draft"], "software takes no position")
ok("dated site photos" in step["draft"], "the reply cites the pulled record")
ok("you'll hear that from us first" in step["draft"], "honesty runs both ways in the copy")

print("== white-label ==")
for m in store.load("messages"):
    if m.get("draft_reply"):
        ok("yourco" not in m["draft_reply"].lower(), f"white-label: {m['id']}")
co_draft = agents.draft_change_order("dl_ob_demo_qty")["draft"]
ok("yourco" not in co_draft.lower(), "white-label: the CO")

print("== matrix ==")
for a in ("invoice_unconfirmed_delta", "treat_verbal_as_signed",
          "notice_without_recorded_clause", "price_off_rate_schedule"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("invoice_unconfirmed_delta", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "invoice_unconfirmed_delta" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")
ok(core.matrix.rung_for("draft_change_order")["rung"] == "R1", "outward paper sits at R1")
ok(core.matrix.rung_for("detect_delta")["rung"] == "R2", "internal detection sits at R2")

print("== closeout ledger + the same-day stat ==")
cl = core.closeout_ledger()
ok(cl["by_state"].get("detected", 0) + cl["by_state"].get("confirmed", 0) >= 1,
   "the ledger counts deltas by state")
det = cl["detection"]
ok(det["same_day"] >= 6 and det["found_later"] >= 1,
   "same-day vs found-later counted (the 12-day-old photo reads found-later, honestly)")
ok("counted" in det["note"], "the detection stat names its basis")

print("== this week, counted (baseline delta) ==")
base = core.this_week()
agents.confirm_delta("dl_ob_demo_unplanned", human="pm")
rec = core.this_week()
ok(rec["deltas_confirmed"] == base["deltas_confirmed"] + 1, "a confirm moves the counted stat by 1")
store.log_event("draft_notice_letter", "dl_ob_demo_qty", "human:owner", "R1", {})
rec2 = core.this_week()
ok(rec2["notices_sent"] == base["notices_sent"] + 1, "human-sent notices counted; agent drafts are not")
ok("counted" in rec2["note"], "the week names its basis")

print("== roi: typed, blank when unrecorded ==")
r = core.roi({})
ok(r["recorded"]["deltas_detected"] == 7, "deltas detected is counted, recorded")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Change orders captured"]["kind"] == "revenue", "captured COs are revenue-typed")
ok(labels["CO value noticed inside its window"]["kind"] == "cash_timing", "kept windows are cash timing")
ok(labels["Closeout write-offs, your history"]["kind"] == "scenario", "write-offs are a scenario")
ok(labels["PM hours on change paperwork"]["kind"] == "time_saved", "PM hours are time_saved")
ok(labels["Closeout write-offs, your history"]["value"] is None
   and "closeout_writeoffs" in labels["Closeout write-offs, your history"]["_missing"],
   "the scenario line is BLANK until the operator supplies it — never estimated")
ok(labels["Change orders captured"]["value"] is None, "revenue line blank without the confirm rate")
r2 = core.roi({"confirm_rate": 0.8, "avg_co_value": 900})
l2 = {l["label"]: l for l in r2["lines"]}
ok(l2["Change orders captured"]["value"] == round(7 * 900 * 0.8, 2),
   "revenue computes only from given + counted inputs, arithmetic shown")

print("== signature is recorded, never inferred ==")
r = agents.record_co_signature("dl_ob_demo_qty")
ok("refused" in r and "human act" in r["refused"], "recording a signature needs a human")
r = agents.record_co_signature("dl_ob_demo_qty", human="owner")
ok(r["state"] == "signed" and r["value"] == 775.0, "a human records the signed CO with its value")

print("== demo fixtures are never swept ==")
seed.main()  # fresh state: demo messages unhandled
out = agents.run_all()
ok(out["messages"]["demo_skipped"] == 2, "the two demo messages are skipped by the sweep")
ok(not store.by_id("messages", "ms_demo_verbal").get("handled_at"),
   "the demo verbal directive is driven by the demo button, never the sweep")
ok(out["messages"]["handled"] >= 6, "the regular messages are handled")
ok(out["diff"]["created"] == 7 and out["diff"]["clean_matches"] == 18,
   "the sweep diff finds the 7 departures and 18 clean matches")

print("== append-only events ==")
ids_before = [e["id"] for e in store.events()]
agents.confirm_delta("dl_ob_demo_qty", human="pm")
ids_after = [e["id"] for e in store.events()]
ok(ids_after[:len(ids_before)] == ids_before and len(ids_after) > len(ids_before),
   "the event log only grows — a correction is a new event, never an edit")
ok(not hasattr(store, "delete_event") and not hasattr(store, "edit_event"),
   "no delete/edit path on the log")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused with the reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
