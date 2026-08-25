#!/usr/bin/env python3
"""Stone OS — the suite. `python3 test_stone_os.py`."""
import inspect, os, sys, tempfile
from pathlib import Path

os.environ["STONEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="stoneos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import gate, store
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
ok(len(store.load("orders")) >= 300, "orders seeded")
ok(len(store.load("cemeteries")) == 14, "14 cemeteries")
ok(sum(1 for c in store.load("cemeteries") if not c.get("rules")) == 2,
   "two cemeteries deliberately have no recorded rules — UNKNOWN is live")

print("== triage: the proof change reads first ==")
for case in core.EVAL_CASES:
    got = core.read_message(case["input"])["label"]
    ok(got == case["label"],
       f"triage: {case['input'][:44] or '(empty)'} → {case['label']} (got {got})")

print("== the proof gate: only the family approves ==")
r = gate.act("approve_proof", "probe", "pr_demo_typo", {})
ok(r.get("refused") and r["rung"] == "R0", "software approval refused at R0")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "approve_proof"
       for e in store.events()), "approve_proof refusal logged")
ok(not any(a_["action"] == "approve_proof" and a_["state"] == "pending"
           for a_ in store.load("approvals")),
   "R0 never becomes an approvable row — a refusal, not a slow yes")
r = agents.start_engraving("or_demo_typo")
ok("refused" in r and "no recorded family approval" in r["refused"],
   "engraving without the approval record is refused, with the reason")
ok("Granite is not reworked" in r["refused"], "and the refusal names the stake")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "start_engraving_without_proof_approval"
       for e in store.events()), "start_engraving_without_proof_approval logged")
sig = inspect.signature(agents.start_engraving)
ok(list(sig.parameters) == ["order_id"],
   "no force/skip parameter exists — the approval record is the only path")
ok(not hasattr(core, "force_engrave") and not hasattr(agents, "force_engrave"),
   "no bypass function exists anywhere")

print("== the approval is a recorded human act ==")
r = agents.record_family_approval("pr_demo_typo", family_member="Dana Merrow",
                                  signature_ref=None, staff="owner")
ok("refused" in r and "signature" in r["refused"],
   "no signature reference → not a record; refused")
r = agents.record_family_approval("pr_demo_typo", family_member="Dana Merrow",
                                  signature_ref="SIG-2211", staff="owner")
ok(r.get("approved") and r["approval"]["signature_ref"] == "SIG-2211",
   "the family's approval records with a signature ref")
ev = [e for e in store.events(kind="proof_approved")][-1]
ok(ev["actor"] == "human:owner" and (ev["detail"] or {}).get("party") == "family",
   "recorded as a HUMAN act, party: family — software recorded it, did not make it")
r = agents.start_engraving("or_demo_typo")
ok(r.get("started") and r["gate"]["rung"] == "R2",
   "with the record on file, engraving queues at R2")
ok("SIG-2211" in r["why"], "and the permission cites the signature ref")

print("== cemetery rulebook: cited or UNKNOWN ==")
c = core.compliance(store.by_id("orders", "or_demo_norules"))
ok(c.get("_missing") and "UNKNOWN" in c["_missing"],
   "no recorded rules → UNKNOWN via unmeasured, never assumed")
ok("Old Pioneer Burial Ground" in c["_missing"], "the ruleless cemetery is named")
c = core.compliance(store.by_id("orders", "or_demo_precure"))
ok(c.get("state") == "cited" and c["cemetery"] == "St. Brigid Cemetery",
   "recorded rules → every check cites")
ok(all("recorded from the St. Brigid Cemetery rules sheet" in ch["cite"]
       for ch in c["checks"]), "each check cites the recorded rules sheet")
ok("never declares compliance beyond" in c["note"], "the note states the limit")
r = gate.act("declare_cemetery_compliant", "probe", "or_demo_norules", {})
ok(r.get("refused"), "declare_cemetery_compliant R0 probe refused")
ok(not any(a_["action"] == "declare_cemetery_compliant" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "and creates no approvable row")

print("== setting: two date checks, dates named ==")
o = store.by_id("orders", "or_demo_precure")
r = agents.schedule_setting("or_demo_precure")
ok("refused" in r and "Granite over green concrete" in r["refused"],
   "setting pre-cure refused")
poured = parse(o["foundation_poured_at"]).date().isoformat()
ok(poured in r["refused"] and "settable" in r["refused"],
   f"the refusal names the pour date ({poured}) and the settable date")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "set_before_cure"
       for e in store.events()), "set_before_cure logged")
r = agents.schedule_setting("or_demo_noca")
ok("refused" in r and "no recorded cemetery approval" in r["refused"],
   "no cemetery approval on record → refused, even with the foundation poured")
r = agents.schedule_setting("or_demo_ready")
ok(r.get("clear") and r["gate"]["rung"] == "R1",
   "both date checks clear → the setting request DRAFTS at R1")
ok("cured" in r["why"] and "approval recorded" in r["why"], "the why cites both records")
ok("yourco" not in r["draft"].lower(), "the setting draft is white-label")

print("== the costly message: the family's correction ==")
out = agents.handle_message("ms_demo_proof")
step = out["steps"][0]
ok(step["action"] == "record_proof_change", "the correction is recorded")
ok("1941" in step["draft"] and "not 1942" in step["draft"],
   "the ack carries the correction verbatim")
ok("nothing is carved until you have seen and approved" in step["draft"].lower()
   .replace("\n", " "), "the ack promises the hold, not a date")
ok("software never" in step["refused"] or "only the family" in step["refused"],
   "nothing approved by the message")
o = store.by_id("orders", "or_demo_typo")
ok(o.get("engraving_hold"), "the engraving hold is on the order record")
r = agents.start_engraving("or_demo_typo")
ok("refused" in r and "hold" in r["refused"],
   "even an approved proof does not clear a correction hold")
ok("yourco" not in step["draft"].lower(), "white-label")
ok(core.tone_ok(step["draft"])[0], "and passes the tone check")

print("== grief-safe tone, structural ==")
okt, why = core.tone_ok("act now — final notice, last chance to pay")
ok(not okt and "act now" in why and "final notice" in why,
   "urgency language is structurally refused")
ok(core.tone_ok("whenever you are ready, we are here")[0], "gentle copy passes")
drafts = [agents._balance_copy(store.by_id("orders", "or_demo_balance"), n)
          for n in (1, 2, 3)]
for m_id in ("ms_demo_timeline", "ms_demo_balance", "ms_demo_inquiry"):
    outm = agents.handle_message(m_id)
    d = outm["steps"][0].get("draft")
    if d:
        drafts.append(d)
ok(all(core.tone_ok(d)[0] for d in drafts), "every family-facing draft passes the tone check")
ok(all("yourco" not in d.lower() for d in drafts), "every draft is white-label")

print("== the balance ladder is bounded ==")
o = store.by_id("orders", "or_demo_balance")
plan = core.balance_plan(o)
ok(plan["action"] == "draft_reminder" and "touch 1 of 3" in plan["why"],
   "an aging balance is due a first touch")
o["balance_touches"] = [{"at": iso(now() - timedelta(days=3))}]
ok(core.balance_plan(o)["action"] == "none", "inside the 14-day cooldown → no touch")
o["balance_touches"] = [{"at": iso(now() - timedelta(days=60 - i * 15))} for i in range(3)]
plan = core.balance_plan(o)
ok(plan["action"] == "none" and "silence is an answer" in plan["why"],
   "the ladder exhausts at 3 — silence is an answer")
ok("person" in plan["why"], "what happens next is a person's call")
b3 = agents._balance_copy(o, 3)
ok("last note" in b3 and "will not write about it again" in b3,
   "touch 3 says it is the last, kindly")
out = agents.balance_sweep(limit=5)
ok(out["drafted"] <= 5, "the sweep is capped")
ok(all(not (store.by_id("orders", a["subject"]) or {}).get("demo_tag")
       for a in store.load("approvals") if a["action"] == "draft_balance_reminder"),
   "the sweep skips demo_tag rows")

print("== pipeline board ==")
pb = core.pipeline_board()
ok(pb["active"] > 0 and pb["stalled"] >= 1, "active orders counted, stalls found")
stalled = [r for r in pb["rows"] if r["stalled"]]
ok(all(r.get("blocker") for r in stalled), "every stalled order names a blocker")
ok(any(str(r.get("blocker", "")).startswith("unrecorded") for r in stalled),
   "a stall nobody explained reads 'unrecorded' — never a guess")

print("== matrix ==")
for a in ("approve_proof", "start_engraving_without_proof_approval",
          "declare_cemetery_compliant", "set_before_cure"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
ok(core.matrix.rung_for("draft_balance_reminder")["rung"] == "R1",
   "every outward draft sits at R1")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no proof change missed")
ok("GRANITE IS NOT REWORKED" in ev["costly_note"], "the costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("open_balances" in r["recorded"] and r["recorded"]["open_balances"] > 0,
   "open balances are counted from the ledger")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Balances collected sooner"]["kind"] == "cash_timing",
   "balance collection is cash timing")
ok(labels["Office hours returned"]["kind"] == "time_saved", "office hours are time_saved")
ok(labels["The remake that didn't happen"]["kind"] == "scenario",
   "the remake is a scenario")
ok(labels["The remake that didn't happen"]["value"] is None,
   "and stays blank with no input — a prevented remake is never our number")

print("== recovered, counted ==")
base = core.recovered_this_week()
o = store.by_id("orders", "or_demo_balance")
o["balance_paid_at"] = iso(now() - timedelta(days=1))
o["balance_paid_amount"] = 1800
store.upsert("orders", o)
store.log_event("draft_family_update", "or_demo_precure", "human:owner", "R1", {})
store.log_event("draft_family_update", "or_x", "agent:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["balances_collected"] == base["balances_collected"] + 1,
   "a collected balance is counted from the ledger")
ok(rec["balance_cash"] >= base["balance_cash"] + 1800, "with its cash")
ok(rec["family_notes_sent"] == base["family_notes_sent"] + 1,
   "the human send counts; the agent draft does not")
ok(rec["proofs_family_approved"] >= 1, "the recorded family approval is counted")
ok("human sends count" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print("== events are append-only, every agent action carries a rung ==")
evs = store.events()
ok(all(not (str(e.get("actor", "")).startswith("agent:") and not e.get("rung"))
       for e in evs), "no agent action logged without a rung")
ids = [e["id"] for e in evs]
agents.balance_sweep()
ok([e["id"] for e in store.events()][:len(ids)] == ids, "the event log is append-only")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
