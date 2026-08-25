#!/usr/bin/env python3
"""The kit's own honesty suite.

Every build's suite exercises the kit indirectly; this one pins the shared
contracts directly, so a kit regression fails HERE first instead of surfacing
as ten mysterious build failures. Run from anywhere:

    python3 "Pre Build Ideas/_kit/test_kit.py"
"""
import http.client
import socket
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _kit import serve                                        # noqa: E402
from _kit.moat import Eval, Gate, Matrix, Roi                 # noqa: E402
from _kit.store import Store, automation_rate, is_missing, iso, now, unmeasured  # noqa: E402
from datetime import timedelta                                # noqa: E402

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


tmp = Path(tempfile.mkdtemp(prefix="kit-test-"))
store = Store(tmp, ("things",))

# ---------------------------------------------------------------- the missing contract
m = unmeasured("no recorded inputs", field="rate")
ok(m["rate"] is None and m["_missing"] == "no recorded inputs", "unmeasured returns None + reason")
ok(is_missing(m) and not is_missing({"rate": 0}), "is_missing keys on _missing, not on zero")

# ---------------------------------------------------------------- the event log
ev = store.log_event("sent", "x1", "agent:tester")
ok(ev["rung"] == "R?", "an agent event without a rung is stamped R?, never dropped")
store.log_event("sent", "x2", "human:op", "R1")
ok(len(store.events(kind="sent")) == 2, "events append; nothing rewrites")

# ---------------------------------------------------------------- counted automation
store2 = Store(tmp / "auto", ("t",))
r = automation_rate(store2.load("events"), {"sent"})
ok(is_missing(r) and "need 30" in r["_missing"], "below the floor the rate is refused, not stated")

for i in range(20):
    store2.log_event("sent", f"s{i}", "agent:a", "R3")
for i in range(10):
    store2.log_event("queued_for_approval", f"q{i}", "agent:a", "R1", {"action": "sent"})
for i in range(5):
    store2.log_event("refused", f"r{i}", "agent:a", "R0", {"action": "sent"})
r = automation_rate(store2.load("events"), {"sent"})
ok(r["moving"] == 35, "gate-held and refused actions count in the denominator")
ok(r["rate"] == round(20 / 35, 3), "the rate is autonomous/moving, not executed/executed")
r2 = automation_rate(store2.load("events"), {"sent"}, exclude_actors=("agent:",))
ok(is_missing(r2), "excluding every actor drops below the floor and refuses again")

# ---------------------------------------------------------------- the matrix
mx = Matrix({
    "draft": {"rung": "R3", "reason": "reversible, internal"},
    "send": {"rung": "R1", "reason": "outward-facing"},
    "pay": {"rung": "R2", "reason": "small refunds auto", "limit": 100},
    "diagnose": {"rung": "R0", "reason": "licensure boundary", "never_promote": True},
})
ok(mx.rung_for("unknown_thing")["rung"] == "R1", "an unknown action defaults to the gate")
ok(mx.rung_for("unknown_thing")["never_promote"], "…and can never promote from ignorance")
ok(mx.rung_for("pay", amount=500)["rung"] == "R1", "over the standing limit demotes to the gate")
ok(mx.rung_for("pay", amount=50)["rung"] == "R2", "under the limit keeps its rung")
ok(not mx.promotable("diagnose", streak=999)["promote"], "never_promote beats any streak")
ok(not mx.promotable("send", streak=5)["promote"], "a short streak does not promote")
ok(not mx.promotable("send", streak=25, calibration_ok=False)["promote"],
   "streak without calibration does not promote — clean cannot be told from lucky")
ok(mx.promotable("send", streak=25, calibration_ok=True)["promote"], "streak + calibration promotes")
try:
    Matrix({"x": {"rung": "R1"}})
    ok(False, "a rung without a reason must be rejected")
except ValueError:
    ok(True, "a rung without a reason is rejected at construction")

# ---------------------------------------------------------------- the gate
gstore = Store(tmp / "gate", ("t",))
gate = Gate(gstore, mx)

res = gate.act("diagnose", "tester", "p1")
ok(res.get("refused") and not res["executed"], "R0 returns a refusal, not a result")
ok(gate.pending() == [], "an R0 action NEVER becomes an approvable row")
ok(any(e["kind"] == "refused" for e in gstore.events()), "the refusal is logged as an event")

res = gate.act("send", "tester", "p2")
ok(not res["executed"] and res.get("approval"), "R1 queues for a human")
ok(len(gate.pending()) == 1, "the pending queue holds it")
ran = []
dec = gate.decide(res["approval"], "op", approve=True, execute=lambda: ran.append(1))
ok(dec["ok"] and ran == [1], "a human approval executes")
ok(any(e["actor"] == "human:op" and e["kind"] == "send" for e in gstore.events()),
   "the executed action is logged to the HUMAN actor")
ok(not gate.decide(res["approval"], "op")["ok"], "a decided approval cannot be re-decided")

res = gate.act("draft", "tester", "p3", execute=lambda: "done")
ok(res["executed"] and res["result"] == "done", "R3 executes and logs")

# ---------------------------------------------------------------- eval
e = Eval("t", "emergency", "a missed emergency is the costly error")
ok(is_missing(e.run([], lambda x: x)), "an eval with no labelled set refuses to score")
out = e.run([{"input": "a", "label": "emergency"}, {"input": "b", "label": "routine"},
             {"input": "c", "label": "emergency"}],
            lambda x: "emergency" if x in ("a", "b") else "routine")
ok(out["costly_missed"] == 1 and out["costly_false_alarms"] == 1,
   "the costly error class is counted on its own")
ok(out["costly_recall"] == 0.5, "costly recall reported separately from accuracy")

# ---------------------------------------------------------------- roi
roi = (Roi("test")
       .line("recovered", "revenue", "a*b", ["a", "b"], lambda g: float(g["a"]) * float(g["b"]))
       .line("hours", "time_saved", "h", ["h"], lambda g: float(g["h"]))
       .line("exposure", "scenario", "e", ["e"], lambda g: float(g["e"]))
       .line("breaks", "revenue", "1/x", ["x"], lambda g: 1 / float(g["x"])))
r = roi.render({"a": "10", "b": "5", "e": "1000", "x": "0"})
lines = {ln["label"]: ln for ln in r["lines"]}
ok(lines["recovered"]["value"] == 50, "a line with inputs computes and shows its arithmetic")
ok(lines["hours"]["value"] is None and "needs h" in lines["hours"]["_missing"],
   "a line missing an input renders blank with the reason — never estimated")
ok(lines["breaks"]["value"] is None and "could not compute" in lines["breaks"]["_missing"],
   "a compute that blows up is a refusal, not a zero")
ok(r["totals"]["revenue"]["total"] == 50 and r["totals"]["scenario"]["total"] == 1000,
   "totals are per-kind — a scenario is never summed into revenue")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
try:
    Roi("x").line("bad", "profit", "", [], lambda g: 0)
    ok(False, "an untyped ROI line must be rejected")
except ValueError:
    ok(True, "an unknown ROI line kind is rejected")

# ---------------------------------------------------------------- the shared server
app_dir = tmp / "app"
app_dir.mkdir()
(app_dir / "index.html").write_text("<html>ok</html>")
# Ask the OS for a free port instead of hardcoding one. This read PORT = 8878 until 2026-08-24 —
# a port `.claude/launch.json` assigns to prebuild-fix-os (appliance-repair). Whenever that build
# was running, serve.run could not bind and BOTH http assertions below failed as
# "the routes table serves JSON" / "<id> path params are matched" — pointing at the router, which
# was fine, instead of at the collision, which was the whole problem. A test that reports the wrong
# component is worse than a test that fails.
with socket.socket() as _s:
    _s.bind(("127.0.0.1", 0))
    PORT = _s.getsockname()[1]
threading.Thread(target=serve.run, args=(app_dir, {
    ("GET", "/api/ping"): lambda q, b: {"pong": True},
    ("GET", "/api/thing/<id>"): lambda q, b: {"id": q["id"]},
}, PORT, "kit-test"), daemon=True).start()

# Wait for the bind rather than sleeping and hoping — and if it never comes up, say THAT.
_bound = False
for _ in range(40):
    time.sleep(0.05)
    with socket.socket() as _c:
        if _c.connect_ex(("127.0.0.1", PORT)) == 0:
            _bound = True
            break
ok(_bound, f"the kit server binds (port {PORT})")


def raw_get(path):
    c = http.client.HTTPConnection("127.0.0.1", PORT)
    c.request("GET", path)
    r = c.getresponse()
    return r.status, r.read()


st, body = raw_get("/api/ping")
ok(st == 200 and b"pong" in body, "the routes table serves JSON")
st, body = raw_get("/api/thing/abc%20d")
ok(st == 200 and b"abc d" in body, "<id> path params are matched and unquoted")
st, _ = raw_get("/api/nope")
ok(st == 404, "an unknown API route is a 404, not a crash")
st, _ = raw_get("/_kit/kit.css")
ok(st == 200, "kit assets are served from the shared folder")
st, _ = raw_get("/_kit/../serve.py")
ok(st == 404, "a .. traversal out of the kit folder is refused")
st, _ = raw_get("/_kit/../../CLAUDE.md")
ok(st == 404, "a deep traversal toward workspace files is refused")
st, _ = raw_get("/_kit/%2e%2e/serve.py")
ok(st == 404, "an encoded traversal is refused too")

shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
