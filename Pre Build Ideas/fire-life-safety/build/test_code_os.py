#!/usr/bin/env python3
"""Code OS — the suite. `python3 test_code_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CODEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="codeos_test_")
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
ok(len(store.load("devices")) >= 900, "devices seeded")
ok(len(store.load("deficiencies")) == 50, "deficiencies seeded")

print("== triage: impairment first ==")
for text, want in (("the riser valve is shut off on floor 3 after the leak", "impairment"),
                   ("sprinkler system is down in the east wing", "impairment"),
                   ("panel is showing trouble and the horn circuit is dead", "impairment"),
                   ("do we need a fire watch while the pump is being repaired", "impairment"),
                   ("the alarm panel is offline at the warehouse", "impairment"),
                   ("fire marshal left a notice after his walk-through", "marshal"),
                   ("city inspector is coming tuesday, can you be here", "marshal"),
                   ("when is our annual due for the extinguishers", "due_ask"),
                   ("when was the backflow last tested", "due_ask"),
                   ("how much to replace the three bad heads you found", "quote_ask"),
                   ("price on fixing the emergency lights from the report", "quote_ask"),
                   ("", "human"),
                   ("invoice received, thanks", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the impairment protocol ==")
out = agents.handle_message("ms_demo_impair")
step = out["steps"][0]
ok(step["action"] == "escalate_impairment", "impairment escalates at R2")
ok("fire watch" in step["said"].lower(), "the fire-watch language is verbatim")
ok("never downgrades" in step["said"], "the protocol restates the downgrade rule")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "downgrade_impairment"
       for e in store.events()), "downgrade_impairment refused + logged")

print("== the marshal wall ==")
out = agents.handle_message("ms_demo_marshal")
ok(out["steps"][0]["refused"] == "software never corresponds with the AHJ", "AHJ refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "correspond_with_ahj"
       for e in store.events()), "correspond_with_ahj logged")

print("== the device calendar: UNKNOWN, never compliant ==")
d = core.device_state({"kind": "sprinkler", "last_inspected": None})
ok(d["state"] == "unknown" and "not compliant" in d["why"], "no record reads UNKNOWN")
d = core.device_state({"kind": "sprinkler",
                       "last_inspected": iso(now() - timedelta(days=400))})
ok(d["state"] == "overdue" and d["days_overdue"] in (34, 35, 36), "overdue computed from the record")
d = core.device_state({"kind": "kitchen_hood",
                       "last_inspected": iso(now() - timedelta(days=160))})
ok(d["state"] == "due", "the 180-day hood interval applies")

print("== marking needs a recorded result ==")
r = agents.mark_device("dv_demo_unknown")
ok("refused" in r, "marking without a result refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "mark_compliant_without_record"
       for e in store.events()), "mark_compliant_without_record logged")
ok(store.by_id("devices", "dv_demo_unknown")["last_inspected"] is None,
   "the device state did not change")
r = agents.mark_device("dv_demo_unknown", human="inspector", result="pass")
ok(r.get("marked") and store.by_id("devices", "dv_demo_unknown")["last_inspected"],
   "an inspector's recorded result changes the state")

print("== the deficiency ladder ==")
f9 = {"id": "df_x", "site_id": "si_000", "site_name": "Meridian Plaza",
      "finding": "three heads painted over in the stockroom", "code_ref": "NFPA 25",
      "quote": 480, "found_at": iso(now() - timedelta(days=20))}
store.upsert("deficiencies", f9)
ok(core.deficiency_plan(f9)["action"] == "draft_chase", "an aged finding is due a touch")
f9["touches"] = [{"at": iso(now() - timedelta(days=3))}]
ok(core.deficiency_plan(f9)["action"] == "none", "10-day cooldown holds")
f9["touches"] = [{"at": iso(now() - timedelta(days=40 - i))} for i in range(3)]
ok("silence is an answer" in core.deficiency_plan(f9)["why"], "ladder exhausts at 3")
b1 = agents._deficiency_copy(f9, 1)
ok("NFPA 25" in b1 and "$480" in b1, "the chase cites the finding's code reference and quote")
b2 = agents._deficiency_copy(f9, 2)
ok("that's a fine\noutcome too" in b2 or "a fine \noutcome" in b2 or "fine outcome" in b2.replace("\n", " "),
   "touch 2 offers the honest exit")
ok(not any(w in (b1 + b2).lower() for w in ("burn", "die", "tragedy")),
   "no fear copy in the ladder")
ok("yourco" not in (b1 + b2).lower(), "white-label")

print("== matrix ==")
for a in ("mark_compliant_without_record", "downgrade_impairment", "close_impairment",
          "certify_inspection", "correspond_with_ahj"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("certify_inspection", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "certify_inspection" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no impairment missed")
ok("SPRINKLERS" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("overdue_devices" in r["recorded"] and "open_deficiency_value" in r["recorded"],
   "counts recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The impairment log"]["kind"] == "scenario", "the log is a scenario, never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
f9["repaired_at"] = iso(now() - timedelta(days=1))
store.upsert("deficiencies", f9)
rec = core.recovered_this_week()
ok(rec["deficiencies_repaired"] == base["deficiencies_repaired"] + 1
   and rec["repaired_value"] >= 480, "a repair is counted with its quote")
ok(rec["impairments_escalated"] >= 1, "escalations counted from the log")
ok(rec["devices_inspected"] >= 1, "the inspector's mark is counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
