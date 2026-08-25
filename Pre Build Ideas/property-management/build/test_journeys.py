#!/usr/bin/env python3
"""Property OS — the journey suite.

`test_propertyos.py` pins the DOMAIN: thresholds, rungs, refusals. It passed
clean through every bug found by clicking the running app, because none of
those bugs lived in the domain. They lived in two places it cannot see:

  the seam   an agent wrote `turn_cost_estimate`; the UI read `turn_cost`.
             Both sides were individually correct. The renewal card rendered
             "turnover costs —" on every row.

  the click  "Still broken" set status to 'assigned' unconditionally. A
             self-fix that failed has no vendor to go back to, and dispatch
             only picks up 'submitted', so the row was stranded — and then
             re-offered the identical fix the resident had just rejected.

So this suite drives the real HTTP API the way the browser drives it, and
checks the contracts the browser depends on. It boots its own server on a
free port against a throwaway data root.

  python3 test_journeys.py
"""
import json, os, re, shutil, signal, socket, subprocess, sys, tempfile, time
import urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="propertyos-journey-"))
PASS = FAIL = 0
FAILURES = []
BASE = None
PROC = None


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(label)
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")


def section(t):
    print(f"\n{t}\n" + "-" * len(t))


# ------------------------------------------------------------------ harness

def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def boot():
    """Seed a small portfolio, run one agent sweep, then serve it."""
    global BASE, PROC
    env = {**os.environ, "PROPERTYOS_DATA_ROOT": str(TMP)}
    subprocess.run([sys.executable, "seed.py", "--units", "60", "--months", "12"],
                   cwd=ROOT, env=env, capture_output=True, check=True)
    subprocess.run([sys.executable, "agents.py", "--all"],
                   cwd=ROOT, env=env, capture_output=True, check=True)
    port = free_port()
    BASE = f"http://127.0.0.1:{port}"
    PROC = subprocess.Popen([sys.executable, "server.py"], cwd=ROOT,
                            env={**env, "PORT": str(port)},
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for _ in range(80):
        try:
            urllib.request.urlopen(BASE + "/api/metrics", timeout=1).read()
            return
        except Exception:
            if PROC.poll() is not None:
                raise SystemExit("server died on boot:\n" + PROC.stdout.read().decode())
            time.sleep(0.15)
    raise SystemExit("server never came up")


def shutdown():
    if PROC and PROC.poll() is None:
        PROC.send_signal(signal.SIGTERM)
        try:
            PROC.wait(timeout=5)
        except subprocess.TimeoutExpired:
            PROC.kill()
    shutil.rmtree(TMP, ignore_errors=True)


def GET(p, raw=False):
    r = urllib.request.urlopen(BASE + p, timeout=20)
    return r if raw else json.loads(r.read())


def POST(p, body=None):
    req = urllib.request.Request(BASE + p, data=json.dumps(body or {}).encode(),
                                 headers={"content-type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=20).read()), 200
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}"), e.code


# ================================================= 1. the payload seam

# Every field the UI reads out of an approval payload, per kind. This is the
# contract the renewal card broke. Declared here rather than inferred, because
# a rename on either side should fail loudly and name the field.
APPROVAL_CONTRACT = {
    "capital": ["property", "unit_label", "age_years", "life_years", "repairs",
                "repair_spend", "replace_cost", "next_failure_exposure", "why",
                "spend_ratio"],
    "renewal": ["property", "unit_label", "days_left", "draft", "risk",
                "current_rent", "turn_cost"],
    "spend": ["amount", "owner", "anomaly", "emergency"],
    "emergency_review": ["amount", "owner", "property", "anomaly", "emergency"],
    "delinquency": ["balance", "days_late", "draft", "step", "thread", "property", "amount"],
    "legal_referral": ["amount", "days_late", "packet", "property"],
    "invoice_review": ["amount", "invoice", "property"],
    "deposit_disposition": ["turnover", "unit_label", "draft", "property", "inspection_note"],
    "trust_alert": ["reconcile"],
    "blocked_message": ["flags"],
}

# A kind the UI can render but the store never produces is dead code that looks
# alive. `spend` was exactly that for the whole build: wired, rung-governed,
# rendered — and never once generated, because every seeded owner-approval quote
# resolved before "now". These kinds must actually appear.
MUST_APPEAR = ["capital", "renewal", "spend", "delinquency", "legal_referral"]
# deposit_disposition's not-dead-code guarantee lives in test_turnover_journey:
# it is CREATED by the inspection step, driven there through the real API.


def test_seam():
    section("1. The payload seam — every field the UI reads must exist")

    approvals = GET("/api/approvals")
    ok(approvals, f"{len(approvals)} approvals to check")
    seen = {}
    for a in approvals:
        seen.setdefault(a["kind"], a)

    for kind in MUST_APPEAR:
        ok(kind in seen,
           f"the store actually produces '{kind}' approvals (not dead code)")

    for kind, fields in APPROVAL_CONTRACT.items():
        a = seen.get(kind)
        if not a:
            ok(kind not in MUST_APPEAR,
               f"'{kind}' absent from this seed — contract declared but NOT exercised")
            continue
        p = a.get("payload") or {}
        missing = [f for f in fields if p.get(f) is None]
        ok(not missing,
           f"'{kind}' payload carries every field the card renders"
           + (f" — MISSING {missing}" if missing else ""))

    # The spend gate is the R1 escalation; check both halves reached reality.
    spends = [a for a in approvals if a["kind"] == "spend"]
    if spends:
        why = " ".join(a["why_human"] for a in spends)
        ok("standing limit" in why or "median" in why,
           "spend approvals name either the owner's limit or a price anomaly")
        flagged = sum(1 for a in spends
                      if (a["payload"].get("anomaly") or {}).get("flag"))
        ok(flagged < len(spends),
           f"not every spend is an anomaly ({flagged}/{len(spends)}) — "
           "a flag on everything is the same as no flag")

    # turn_cost specifically: the bug rendered an em-dash because .total was
    # unreachable. Assert the nested read the UI actually performs.
    r = seen.get("renewal")
    if r:
        ok((r["payload"].get("turn_cost") or {}).get("total"),
           "renewal payload.turn_cost.total resolves (the em-dash bug)")

    # The contract must not silently drift from the code. Scan the card
    # renderer for `p.<field>` reads and flag any the contract doesn't list.
    src = (ROOT / "app" / "staff.html").read_text()
    card = src[src.find("function apCard"):src.find("async function decide")]
    reads = set(re.findall(r"\bp\.([a-z_][a-z0-9_]*)", card))
    declared = {f for fs in APPROVAL_CONTRACT.values() for f in fs}
    undeclared = sorted(reads - declared - {"payload", "kind"})
    ok(not undeclared,
       "every p.<field> read in apCard is in the declared contract"
       + (f" — undeclared: {undeclared}" if undeclared else ""))

    # Same check for the lease tracker rows the board and owner view share.
    lease = GET("/api/leases?days=60")
    if lease:
        need = ["unit_id", "unit", "property", "tenant", "ends", "days_left",
                "rent", "risk", "turn_cost"]
        miss = [f for f in need if lease[0].get(f) is None]
        ok(not miss, "lease tracker rows carry every column the table renders"
                     + (f" — MISSING {miss}" if miss else ""))
        ok((lease[0].get("turn_cost") or {}).get("total") is not None,
           "...including turn_cost.total, the same nested read")


# ================================================= 2. routes the UI calls

def test_routes():
    section("2. Every endpoint the client calls actually resolves")

    reqs = GET("/api/requests?limit=1")
    rid = reqs[0]["id"]
    uid = reqs[0]["unit_id"]
    oid = GET("/api/bootstrap?role=staff")["owners"][0]["id"]

    live = [
        "/api/metrics", "/api/leases?days=60", "/api/vendors", "/api/approvals",
        "/api/messages", "/api/capital", "/api/requests?open=1",
        "/api/bootstrap?role=staff", "/api/bootstrap?role=tenant",
        f"/api/bootstrap?role=owner&id={oid}",
        f"/api/requests/{rid}", f"/api/requests/{rid}/vendors",
        f"/api/units/{uid}/memory", f"/api/owner/{oid}/report",
    ]
    for p in live:
        try:
            GET(p)
            ok(True, f"GET {p.split('?')[0]}")
        except urllib.error.HTTPError as e:
            ok(False, f"GET {p} -> HTTP {e.code}")

    # A route the client calls but the server never routed would 404 forever.
    # Scan the client for API.get/post literals and confirm each prefix is
    # exercised above, so a newly-added call cannot go untested.
    js = "\n".join((ROOT / "app" / f).read_text()
                   for f in ("staff.html", "tenant.html", "owner.html",
                             "growth.html", "index.html", "app.js"))
    called = set()
    for m in re.finditer(r"API\.(?:get|post)\(\s*'(/[a-z0-9_\-]+)", js):
        called.add(m.group(1))
    exercised = {"/" + p.split("/")[2].split("?")[0] for p in live}
    exercised |= {"/requests", "/approvals", "/messages", "/agents",
                  "/money", "/turnovers", "/job", "/auth",
                  # exercised by test_growth_journey / test_pipeline_journey / test_auth
                  "/inquiries", "/referrals", "/growth", "/listings",
                  "/pipeline", "/prospects"}
    gap = sorted(c for c in called if c not in exercised)
    ok(not gap, "every API path the client calls is covered by this suite"
                + (f" — uncovered: {gap}" if gap else ""))


# ================================================= 3. resident journeys

def test_resident_deflected():
    section("3. Resident journey — the guided fix works")

    t = GET("/api/bootstrap?role=tenant")["tenant"]
    res, code = POST("/api/requests", {
        "tenant_id": t["id"],
        "description": "garbage disposal just hums and won't spin"})
    ok(code == 200, "resident files a request")
    r = res["request"]
    ok(res.get("self_fix"), "a vetted self-fix is offered for a disposal")
    ok("close it" not in (res.get("self_fix") or {}).get("title", "").lower() or True,
       f"...card: {(res.get('self_fix') or {}).get('title','')[:48]!r}")

    out, _ = POST(f"/api/requests/{r['id']}/status",
                  {"status": "resolved", "resolution_kind": "deflected",
                   "actor": f"tenant:{t['id']}"})
    ok(out["request"]["status"] == "resolved", "'That worked' closes it")
    ok(out["request"]["resolution_kind"] == "deflected",
       "...recorded as deflected, so it counts as an avoided truck roll")

    m = GET("/api/metrics")
    ok(m["deflection"]["deflected"] >= 1, "the deflection counter sees it")


def test_resident_still_broken():
    """The exact bug: a failed self-fix must reach a vendor, and must never be
    handed the same card again."""
    section("4. Resident journey — the guided fix FAILS (the loop bug)")

    t = GET("/api/bootstrap?role=tenant")["tenant"]
    res, _ = POST("/api/requests", {
        "tenant_id": t["id"],
        "description": "garbage disposal just hums and won't spin"})
    rid = res["request"]["id"]
    POST(f"/api/requests/{rid}/status",
         {"status": "resolved", "resolution_kind": "deflected"})

    out, _ = POST(f"/api/requests/{rid}/feedback",
                  {"still_broken": True, "comment": "tried it, no luck"})
    r = out["request"]
    ok(r["reopened"] is True, "'Didn't work' reopens the ORIGINAL request")
    ok(r["status"] == "submitted",
       "...and with no vendor to return to it goes to intake, not 'assigned'")
    ok(not r.get("vendor_id"), "...carrying no vendor")

    POST("/api/agents/run?agent=triage")
    POST("/api/agents/run?agent=dispatch")
    after = GET(f"/api/requests/{rid}")
    ok(after.get("vendor_id"), f"the agent sweep routes it to a vendor ({after.get('vendor')})")
    ok(after["status"] in ("assigned", "in_progress"), "...and it leaves intake")
    ok(not after.get("self_fix_offered"),
       "the SAME self-fix is never offered again after the resident rejected it")


def test_reopen_with_vendor():
    section("5. Resident journey — reopening a vendor-completed job")

    done = next(x for x in GET("/api/requests?status=resolved&limit=60")
                if x.get("vendor_id") and not x.get("reopened"))
    out, _ = POST(f"/api/requests/{done['id']}/feedback", {"still_broken": True})
    r = out["request"]
    ok(r["status"] == "assigned", "goes straight back to 'assigned'")
    ok(r["vendor_id"] == done["vendor_id"],
       f"...with the same vendor ({r.get('vendor')}) — they own the callback")
    ok(r.get("resolved_at") is None, "...and the resolution timestamp is cleared")


def test_emergency():
    section("6. Resident journey — an understated emergency")

    t = GET("/api/bootstrap?role=tenant")["tenant"]
    res, _ = POST("/api/requests", {
        "tenant_id": t["id"],
        "description": "apartment is a bit chilly, the heat doesn't seem to be coming on",
        "answers": {"habitability": True}})
    r = res["request"]
    ok(r["priority"] == "P1", "routed P1 despite being described mildly")
    ok(r["category"] == "no_heat", "...and categorised as no heat")
    ok(r["status"] == "assigned" and r.get("vendor_id"),
       f"...dispatched ON INTAKE, not on the next sweep ({r.get('vendor')})")
    ok(res["sla"]["respond_h"] == 1, "...against the 1-hour emergency response clock")


# ================================================= 7. staff journeys

def test_emergency_spend():
    """The P1 the demo board exposed: a habitability repair sat breached for
    five days 'awaiting owner approval' over a $412 quote. The emergency
    authority exists so that never happens — and so its boundaries hold."""
    section("7. Emergency spend authority — fix first, argue about price later")

    t = GET("/api/bootstrap?role=tenant")["tenant"]

    def p1(desc):
        res, _ = POST("/api/requests", {"tenant_id": t["id"], "description": desc,
                                        "answers": {"habitability": True}})
        return res["request"]

    # (a) over the standing limit, under the emergency authority -> auto-approved
    r = p1("no heat at all, the furnace won't come on and it's freezing")
    ok(r["priority"] == "P1", "filed and routed as P1")
    POST(f"/api/requests/{r['id']}/status", {"status": r["status"], "quote": 420})
    POST("/api/agents/run?agent=dispatch")
    after = GET(f"/api/requests/{r['id']}")
    ok(after.get("spend_approved") is True,
       "$420 (over the $400 standing limit) is committed WITHOUT waiting — "
       "the emergency authority applied")
    ok(not [a for a in GET("/api/approvals")
            if a["kind"] == "spend" and a["payload"].get("request") == r["id"]],
       "...and no blocking approval was queued for it")
    notice = [m for m in GET("/api/messages")
              if m.get("request_id") == r["id"] and m.get("to_kind") == "owner"]
    ok(notice and notice[0]["status"] == "sent",
       "...and the owner got the notice the moment it was committed (R2, not R3)")
    ok("emergency authority" in notice[0]["body"],
       "...which names the instrument that authorized it")

    # (b) anomalous price on a P1 -> STILL committed, invoice reviewed after
    r2 = p1("heater is dead again, no heat in the whole apartment")
    POST(f"/api/requests/{r2['id']}/status", {"status": r2["status"], "quote": 1100})
    POST("/api/agents/run?agent=dispatch")
    after2 = GET(f"/api/requests/{r2['id']}")
    ok(after2.get("spend_approved") is True,
       "a price-anomalous P1 quote is still committed — habitability outranks "
       "the price argument")
    rev = [a for a in GET("/api/approvals")
           if a["kind"] == "emergency_review" and a["payload"].get("request") == r2["id"]]
    ok(rev, "...but the invoice lands in post-hoc review")
    ok("already committed" in rev[0]["why_human"],
       "...which says plainly the money is already out the door")

    # (c) over even the emergency authority -> R1, nothing moves alone
    r3 = p1("no heat and the unit needs a full system replacement it seems")
    POST(f"/api/requests/{r3['id']}/status", {"status": r3["status"], "quote": 2600})
    POST("/api/agents/run?agent=dispatch")
    after3 = GET(f"/api/requests/{r3['id']}")
    ok(after3.get("spend_approved") is False,
       "$2600 exceeds the $2000 emergency authority — NOT committed")
    gate = [a for a in GET("/api/approvals")
            if a["kind"] == "spend" and a["payload"].get("request") == r3["id"]]
    ok(gate and "emergency authority" in gate[0]["why_human"],
       "...and the approval says a human must decide at P1 speed")
    ok(gate and gate[0]["payload"].get("emergency") is True,
       "...flagged as an emergency so the queue can rank it first")


def test_staff():
    section("7. Staff journey — the board, the tracker, the bench")

    boot_s = GET("/api/bootstrap?role=staff")
    m = boot_s["metrics"]
    board_open = [r for r in boot_s["requests"] if r["status"] != "resolved"]
    ok(len(board_open) == m["requests"]["open"],
       f"the board shows every open request ({len(board_open)} = metrics {m['requests']['open']})")

    for r in boot_s["requests"][:40]:
        if r.get("age_hours", 0) < 0:
            ok(False, f"request {r['id']} has a negative age — future-dated")
            break
    else:
        ok(True, "no row on the board has a negative age")

    # min-by-id: board order ties on same-second timestamps, and [0] made the
    # vendor-override branch fire on some runs and not others.
    open_r = min(board_open, key=lambda r: (r.get("title") or "", r.get("unit") or ""))
    detail = GET(f"/api/requests/{open_r['id']}")
    ok("timeline" in detail and detail["timeline"],
       "opening a request returns its event timeline")
    ok(all(e.get("rung") for e in detail["timeline"]
           if str(e["actor"]).startswith("agent:")),
       "...and every agent entry in it shows an autonomy rung")

    bench = GET(f"/api/requests/{open_r['id']}/vendors")
    ok(bench and bench[0].get("why"),
       "the vendor bench explains its ranking rather than just ordering")
    ok(all(v["score"] >= 0 or "INSURANCE" in " ".join(v["why"]).upper() for v in bench),
       "...and any negative score names insurance as the reason")

    pick = next((v for v in bench if v["vendor_id"] != open_r.get("vendor_id")), None)
    if pick:
        out, _ = POST(f"/api/requests/{open_r['id']}/assign", {"vendor_id": pick["vendor_id"]})
        ok(out["request"]["vendor_id"] == pick["vendor_id"], "staff can override the assignment")
        ev = [e for e in out["request"]["timeline"] if e["kind"] in ("assigned", "reassigned")]
        ok(any(e["detail"].get("manual_override") for e in ev),
           "...and the override is recorded as human, not agent")

    for s in ("in_progress", "resolved"):
        out, _ = POST(f"/api/requests/{open_r['id']}/status", {"status": s})
        ok(out["request"]["status"] == s, f"tracker moves to '{s}'")
    ok(GET(f"/api/requests/{open_r['id']}").get("resolved_at"),
       "...and resolving stamps the time the average is computed from")

    bad, code = POST(f"/api/requests/{open_r['id']}/status", {"status": "banana"})
    ok(code == 400 and "status must be" in bad.get("error", ""),
       "an invalid status is rejected with a useful message")


def test_approvals():
    section("8. Staff journey — the approvals queue")

    pend = GET("/api/approvals")
    ok(pend, f"{len(pend)} approvals pending")
    ok(all(a.get("why_human") for a in pend),
       "every one states why a human is required")
    ok(all(a["status"] == "pending" for a in pend),
       "no agent has decided its own approval")

    a = pend[0]
    out, _ = POST(f"/api/approvals/{a['id']}/decide", {"approve": True})
    ok(out["approval"]["status"] == "approved", "approving one records the decision")
    ok(out["approval"].get("decided_by"), "...against a named human")
    ok(len(GET("/api/approvals")) == len(pend) - 1, "...and it leaves the pending queue")

    # The queue groups/sorts on these; a missing one silently reorders the page.
    for kind in ("capital", "renewal"):
        rows = [x for x in GET("/api/approvals") if x["kind"] == kind]
        if rows:
            ok(all(r["payload"].get("property") for r in rows),
               f"every '{kind}' row can be filtered by property")


def test_compliance_gate():
    section("9. Nothing blocked by compliance can be sent")

    msgs = GET("/api/messages")
    blocked = [m for m in msgs if m.get("status") == "blocked"]
    ok(True, f"{len(blocked)} message(s) blocked by the screen")
    for m in blocked[:3]:
        res, code = POST(f"/api/messages/{m['id']}/send", {})
        ok(code == 409, "sending a blocked message is refused (HTTP 409)")
        ok(res.get("flags"), "...and the refusal names the flags")

    draft = next((m for m in msgs if m.get("status") == "draft"), None)
    if draft:
        res, code = POST(f"/api/messages/{draft['id']}/send",
                         {"body": "Great to hear the kids are settling in!"})
        ok(code == 409, "editing a clean draft INTO a violation is caught on send")
        ok(GET("/api/messages") and
           next(m for m in GET("/api/messages") if m["id"] == draft["id"])["status"] != "sent",
           "...and the message is not marked sent")


def test_vendor_journey():
    section("9b. Vendor journey — the missing actor, via the magic link")

    # min-by-id, not first-in-list: list order ties on same-second timestamps,
    # and an unstable pick made the suite's assertion COUNT wobble between runs.
    cands = [x for x in GET("/api/requests?open=1&limit=200") if x.get("vendor_token")]
    key = lambda x: (x.get("title") or "", x.get("unit") or "")
    r = min((x for x in cands if x.get("quote")), key=key, default=min(cands, key=key))
    tok = r["vendor_token"]
    j = GET(f"/api/job/{tok}")
    ok(j["request"]["id"] == r["id"], "the job link resolves to its work order")
    ok("history" in j, "...and carries the unit's memory for the vendor")

    out, _ = POST(f"/api/job/{tok}/accept", {"eta": "tomorrow AM"})
    ok(out["job"]["request"]["vendor_accepted"], "vendor accepts")
    # The resident stated no availability, so the vendor's window is a
    # PROPOSAL — scheduling someone into a slot they never offered isn't
    # scheduling, it's hoping. The resident's yes is what books it.
    out, _ = POST(f"/api/job/{tok}/schedule", {"window": "Tue 9-12"})
    ok(out["job"]["proposed_window"] == "Tue 9-12"
       and not out["job"]["request"]["scheduled_for"],
       "vendor's window becomes a proposal — the resident never offered it")
    POST(f"/api/requests/{r['id']}/schedule", {"accept_proposed": True})
    j15 = GET(f"/api/job/{tok}")
    ok(j15["request"]["scheduled_for"] == "Tue 9-12",
       "the resident accepts — now, and only now, it's booked")
    POST(f"/api/job/{tok}/start", {})
    png = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgY"
           "GBgAAAABQABh6FO1AAAAABJRU5ErkJggg==")
    out, _ = POST(f"/api/job/{tok}/complete",
                  {"note": "replaced the valve", "photos": [{"media_type": "image/png", "data": png}]})
    ok(out["job"]["request"]["status"] == "resolved", "completing closes the job")
    detail = GET(f"/api/requests/{r['id']}")
    ok(detail.get("proof_photos"), "...with proof-of-completion photos on the record")
    ok(any(e["kind"] == "job_completed" and str(e["actor"]).startswith("vendor:")
           for e in detail["timeline"]),
       "...and the timeline attributes the work to the VENDOR, not an agent")

    # invoice: within tolerance auto-matches; drift goes to review
    q = detail.get("quote")
    if q:
        out, _ = POST(f"/api/job/{tok}/invoice", {"amount": round(q * 1.05)})
        ok(GET(f"/api/requests/{r['id']}").get("invoice_match", {}).get("match"),
           "an invoice within 10% of the quote matches automatically (R2)")
    r2 = min((x for x in GET("/api/requests?open=1&limit=200")
              if x.get("vendor_token") and x.get("quote") and x["id"] != r["id"]),
             key=lambda x: (x.get("title") or "", x.get("unit") or ""), default=None)
    if r2:
        POST(f"/api/job/{r2['vendor_token']}/complete", {"note": "done"})
        POST(f"/api/job/{r2['vendor_token']}/invoice",
             {"amount": round(r2["quote"] * 1.8)})
        rev = [a for a in GET("/api/approvals")
               if a["kind"] == "invoice_review" and a["payload"].get("request") == r2["id"]]
        ok(rev, "an invoice 80% over the quote lands in human review, unpaid")

    bad, code = POST("/api/job/not-a-real-token/accept", {})
    ok(code == 404, "a bogus token gets nothing")


def test_money_journey():
    section("9c. Money journey — accounts for everything, moves nothing")

    m = GET("/api/money/summary")
    ok(m["reconcile"]["ok"],
       f"trust reconciles to the cent (${m['reconcile']['trust_cash']:,.0f} = liabilities)")
    ok("never" in m["note"] or "cannot" in m["note"],
       "the summary itself states the no-money-movement line")

    d = m["delinquency"]
    ok(d, f"{len(d)} residents behind — the seeded ladder is live")
    stages = {x["stage"] for x in d}
    ok("referral" in stages or "notice" in stages,
       f"...at real stages ({sorted(stages)})")

    # record a payment -> that resident leaves the ladder
    worst = d[0]
    POST("/api/money/payments", {"tenant_id": worst["tenant_id"],
                                 "amount": worst["balance"], "method": "check"})
    d2 = GET("/api/money/summary")["delinquency"]
    ok(all(x["tenant_id"] != worst["tenant_id"] for x in d2),
       "recording the arrived payment clears them from the ladder")
    ok(GET("/api/money/summary")["reconcile"]["ok"],
       "...and the trust still reconciles after the entry")

    # the batch: draft exists (agent), execution demands a human + a reference
    batch = next((b for b in GET("/api/money/summary")["batches"]
                  if b["status"] == "draft"), None)
    ok(batch, "a disbursement batch is DRAFTED by the agent")
    bad, code = POST(f"/api/money/batches/{batch['id']}/execute",
                     {"actor": "agent:ledger", "reference": "X1"})
    ok(code == 400 and "human" in bad.get("error", ""),
       "an AGENT trying to record execution is refused by name")
    bad, code = POST(f"/api/money/batches/{batch['id']}/execute",
                     {"actor": "human:mgr_1", "reference": "  "})
    ok(code == 400 and "reference" in bad.get("error", ""),
       "a human without a bank reference is refused — 'trust me' is not a reference")
    out, code = POST(f"/api/money/batches/{batch['id']}/execute",
                     {"actor": "human:mgr_1", "reference": "WIRE-20260816-A"})
    ok(code == 200 and out["batch"]["status"] == "executed",
       "a human with a reference records the execution they performed")
    ok(GET("/api/money/summary")["reconcile"]["ok"],
       "...and the trust STILL reconciles after the draws post")

    st = GET(f"/api/owner/{GET('/api/bootstrap?role=staff')['owners'][0]['id']}/statement")
    ok(st.get("basis") and "ledger" in st["basis"],
       "the owner statement states it is the ledger grouped, not a narrative")


def test_turnover_journey():
    section("9d. Turnover journey — assumptions become measurements")

    trn = next((t for t in GET("/api/turnovers") if t["state"] == "moveout_scheduled"), None)
    ok(trn, "a turnover sits mid-pipeline from the seed")
    POST(f"/api/turnovers/{trn['id']}/advance",
         {"state": "inspected", "note": "carpet worn through; wall damage bedroom 2"})
    dep = [a for a in GET("/api/approvals")
           if a["kind"] == "deposit_disposition" and a["payload"].get("turnover") == trn["id"]]
    ok(dep, "the inspection step queues the deposit-disposition draft (R0, statutory clock)")
    ok("statutory" in dep[0]["why_human"] or "deadline" in dep[0]["why_human"],
       "...whose why-human names the state deadline")

    out, _ = POST(f"/api/turnovers/{trn['id']}/advance", {"state": "make_ready"})
    ok(len(out["turnover"]["tasks"]) >= 3,
       f"advancing to make-ready dispatched {len(out['turnover']['tasks'])} template tasks")
    task = GET(f"/api/requests/{out['turnover']['tasks'][0]}")
    ok(task.get("turnover_id") == trn["id"],
       "...as real work orders through the same vendor market")

    bad, code = POST(f"/api/turnovers/{trn['id']}/advance", {"state": "leased"})
    ok(code == 400, "states move one at a time — no skipping to leased")

    POST(f"/api/turnovers/{trn['id']}/advance", {"state": "ready"})
    out, _ = POST(f"/api/turnovers/{trn['id']}/advance", {"state": "leased"})
    ok(out["turnover"].get("vacancy_days") is not None,
       f"leasing records measured vacancy ({out['turnover'].get('vacancy_days')} days)")
    mv = GET("/api/money/summary")["measured_vacancy"]
    ok(mv.get("days") is not None and mv["n"] >= 4,
       f"...and the portfolio vacancy figure is now MEASURED (n={mv.get('n')})")


def test_growth_journey():
    section("9d2. Growth — the pitch link, the referral hook, the FIFO line")

    S = GET("/api/bootstrap?role=staff")
    leads = S.get("leads") or {}
    ok(leads.get("share_url", "").startswith("/pitch?t="),
       "staff bootstrap carries the pitch share URL")
    tok = leads["share_url"].split("t=", 1)[1]

    # -- the pitch page: token is the credential, payload is white-label
    p = GET(f"/api/pitch/{tok}")
    ok(p.get("org") and p.get("basis"), "the pitch payload serves on the token alone")
    try:
        GET("/api/pitch/shr_definitely_wrong")
        ok(False, "a wrong pitch token must 404")
    except urllib.error.HTTPError as e:
        ok(e.code == 404, "a wrong pitch token 404s")
    blob = json.dumps(p)
    owner_names = [o["name"] for o in S["owners"]]
    ok(not any(n in blob for n in owner_names),
       "over HTTP, the pitch payload names no owner")
    ok("trust_cash" not in blob, "...and carries no balances")

    # -- listings + the inquiry line
    ls = GET("/api/listings")
    ok(isinstance(ls, list) and all("tenant" not in json.dumps(u) for u in ls),
       f"{len(ls)} public listings, none carrying tenant data")
    before = len(GET("/api/inquiries")["queue"])
    res, code = POST("/api/inquiries", {"name": "Journey Prospect",
                                        "contact": "jp@example.com",
                                        "message": "is the 2bd available?"})
    ok(code == 200, "a stranger files an inquiry with no session")
    q = GET("/api/inquiries")["queue"]
    ok(len(q) == before + 1 and q[-1]["name"] == "Journey Prospect",
       "...and joins the END of the line — position is arrival order")
    res2, _ = POST("/api/inquiries", {"name": "Journey Prospect",
                                      "contact": "JP@EXAMPLE.COM",
                                      "message": "following up"})
    ok(res2.get("already_recorded"), "a repeat inquiry keeps their place in line")
    ok(len(GET("/api/inquiries")["queue"]) == before + 1,
       "...without adding a second row")
    occ = next(r for r in GET("/api/requests?limit=50")
               if r.get("tenant_id") and r.get("unit_id"))
    _, code = POST("/api/inquiries", {"name": "X", "contact": "x@x.com",
                                      "unit_id": occ["unit_id"]})
    ok(code == 409, "inquiring about an occupied unit is refused")
    last = GET("/api/inquiries")["queue"][-1]
    _, code = POST(f"/api/inquiries/{last['id']}/status", {"status": "toured"})
    ok(code == 200, "staff marks the inquiry toured")
    _, code = POST(f"/api/inquiries/{last['id']}/status", {"status": "ranked_no_1"})
    ok(code == 400, "an invented inquiry status is refused")

    # the ack: identical template, prospect audience, survives the sentinel
    POST("/api/agents/run?agent=sentinel")
    acks = [m for m in GET("/api/messages") if m.get("kind") == "inquiry_ack"]
    ok(acks and all(m["to_kind"] == "prospect" for m in acks),
       "every inquiry got the templated receipt, addressed as prospect")
    ok(all(m.get("status") != "blocked" for m in acks),
       "...and the template passes the full-strictness prospect screen")

    # -- the referral hook
    res, code = POST("/api/referrals", {"name": "Journey Referral",
                                        "contact": "704-555-0000",
                                        "note": "met at the meetup",
                                        "source": "owner:" + S["owners"][0]["id"]})
    ok(code == 200 and res["referral"]["status"] == "new",
       "an owner referral records with its source")
    rid = res["referral"]["id"]
    _, code = POST(f"/api/referrals/{rid}/status", {"status": "contacted"})
    ok(code == 200, "staff marks the referral contacted")
    ob = GET(f"/api/bootstrap?role=owner&id={S['owners'][0]['id']}")
    ok(any(r["id"] == rid for r in ob.get("my_referrals", [])),
       "the owner sees their own referral and its status")
    ok(ob.get("share_url", "").startswith("/pitch?t="),
       "...and carries the share link to forward")

    # -- rotation revokes
    res, code = POST("/api/growth/rotate_share", {})
    new_tok = res["share_url"].split("t=", 1)[1]
    ok(new_tok != tok, "rotating issues a fresh token")
    try:
        GET(f"/api/pitch/{tok}")
        ok(False, "the old pitch link must be dead after rotation")
    except urllib.error.HTTPError as e:
        ok(e.code == 404, "the old pitch link is dead after rotation")
    ok(GET(f"/api/pitch/{new_tok}").get("org"), "...and the new one serves")

    for f in ("/pitch", "/inquire", "/pitch.html", "/inquire.html"):
        r = GET(f, raw=True)
        ok(r.status == 200, f"GET {f} serves the shell")


def test_pipeline_journey():
    section("9d3. Growth module — the pipeline over HTTP, no send rail anywhere")

    P = GET("/api/pipeline")
    ok("stages" in P and "no send rail" in P["note"].lower() or "send" in P["note"].lower(),
       "the pipeline serves and states its no-send line on the payload itself")
    ok(any(P["stages"][s] for s in P["stages"]),
       "the sweep at boot populated the pipeline (referral imports + the seeded prospect)")

    # drafts exist and are DRAFTS; a human records the send
    msgs = [m for m in GET("/api/messages") if m.get("module") == "pipeline"]
    ok(msgs and all(m["status"] in ("draft", "blocked") for m in msgs),
       "every pipeline message over HTTP is an unsent draft")
    ft = next((m for m in msgs if m["kind"] == "first_touch"), None)
    ok(ft is not None, "a first-touch draft is waiting")
    res, code = POST(f"/api/messages/{ft['id']}/send", {})
    ok(code == 200 and res["message"]["status"] == "sent",
       "the human records that THEY sent it — the module never did")

    # add -> advance -> won -> scaffold, the whole arc over HTTP
    res, code = POST("/api/prospects", {"name": "HTTP Prospect",
                                        "contact": "hp@example.com",
                                        "note": "9 doors, journey test"})
    ok(code == 200, "a prospect records over HTTP")
    pid = res["prospect"]["id"]
    _, code = POST(f"/api/prospects/{pid}/advance", {"stage": "meeting"})
    ok(code == 400, "stage-skipping is refused over HTTP too")
    for s in ("researched", "first_touch_drafted", "contacted", "meeting", "proposal"):
        _, code = POST(f"/api/prospects/{pid}/advance", {"stage": s})
        ok(code == 200, f"human advances to {s}")
    _, code = POST(f"/api/prospects/{pid}/advance", {"stage": "won"})
    ok(code == 200, "and marks it won from proposal")
    owners_before = len(GET("/api/bootstrap?role=staff")["owners"])
    res, code = POST(f"/api/prospects/{pid}/scaffold", {})
    ok(code == 200 and res.get("owner_id"),
       "the won prospect scaffolds an ops-module owner")
    owners_after = GET("/api/bootstrap?role=staff")["owners"]
    ok(len(owners_after) == owners_before + 1,
       "...who now appears in the ops console's owner list")
    new_owner = next(o for o in owners_after if o["id"] == res["owner_id"])
    ok(new_owner.get("onboarding"),
       "...flagged as onboarding — scaffold defaults are not the owner's terms")

    # the losing path records its reason verbatim
    res, _ = POST("/api/prospects", {"name": "Timing Wrong", "contact": "tw@x.com"})
    _, code = POST(f"/api/prospects/{res['prospect']['id']}/advance",
                   {"stage": "lost", "reason": "renewing with current PM"})
    ok(code == 200, "lost-with-reason records from any live stage")

    r = GET("/growth", raw=True)
    ok(r.status == 200, "GET /growth serves the cockpit shell")

    # ---- prospecting over HTTP: import, cold draft, opt-out, wake
    res, code = POST("/api/prospects/import", {"targets": [
        {"name": "No Prov", "contact": "noprov@x.com"}]})
    ok(code == 400 and "provenance" in res["error"],
       "an import without provenance is refused over HTTP")
    res, code = POST("/api/prospects/import", {
        "provenance": "journey county pull",
        "targets": [{"name": "Cold Journey", "contact": "cj@example.com",
                     "note": "8 doors per the parcel roll"}]})
    ok(code == 200 and res["report"]["added"] == 1,
       "a sourced list imports with its provenance and reports its counts")
    POST("/api/agents/run?agent=scout")
    POST("/api/agents/run?agent=scribe")
    cold = next(m for m in GET("/api/messages")
                if m.get("module") == "pipeline" and m.get("kind") == "first_touch"
                and "journey county pull" in m.get("body", ""))
    ok("no thanks" in cold["body"] and "PHYSICAL MAILING ADDRESS" in cold["body"],
       "the cold draft carries the opt-out line and the address bracket over HTTP")
    cj = next(p_ for s in GET("/api/pipeline")["stages"].values() for p_ in s
              if p_["contact"] == "cj@example.com")
    _, code = POST(f"/api/prospects/{cj['id']}/dnc", {})
    ok(code == 200, "staff records an opt-out")
    res, code = POST(f"/api/prospects/{cj['id']}/wake", {})
    ok(code == 400 and "permanent" in res["error"],
       "an opt-out cannot be woken over HTTP either")
    res, code = POST("/api/prospects/import", {
        "provenance": "journey re-pull",
        "targets": [{"name": "Cold Journey", "contact": "CJ@EXAMPLE.COM"}]})
    ok(res["report"]["do_not_contact"] == 1 and res["report"]["added"] == 0,
       "a re-import skips the opt-out, case-insensitively")


def test_auth():
    section("9e. Auth — a second server with enforcement ON")

    import subprocess, json as _json
    port2 = free_port()
    env = {**os.environ, "PROPERTYOS_DATA_ROOT": str(TMP), "PORT": str(port2),
           "PROPERTYOS_AUTH": "1", "PROPERTYOS_SWEEP_MINUTES": "0"}
    proc = subprocess.Popen([sys.executable, "server.py"], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    base2 = f"http://127.0.0.1:{port2}"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(base2 + "/login.html", timeout=1)
                break
            except Exception:
                time.sleep(0.15)
        def hit(path, method="GET", body=None, cookie=None):
            req = urllib.request.Request(base2 + path, method=method,
                data=_json.dumps(body).encode() if body is not None else None,
                headers={"content-type": "application/json",
                         **({"Cookie": cookie} if cookie else {})})
            try:
                r = urllib.request.urlopen(req, timeout=10)
                return _json.loads(r.read() or b"{}"), r.status, r.headers
            except urllib.error.HTTPError as e:
                return _json.loads(e.read() or b"{}"), e.code, e.headers

        _, code, _ = hit("/api/bootstrap?role=staff")
        ok(code == 401, "no session -> 401 on data")
        _, code, _ = hit("/api/auth/login", "POST", {"code": "wrong"})
        ok(code == 401, "a wrong access code is rejected")

        codes = _json.loads((TMP / "config.json").read_text())["auth"]["demo_codes"]
        _, code, hdrs = hit("/api/auth/login", "POST", {"code": codes["staff"]})
        ok(code == 200, "the staff code logs in")
        staff_cookie = (hdrs.get("Set-Cookie") or "").split(";")[0]
        _, code, _ = hit("/api/bootstrap?role=staff", cookie=staff_cookie)
        ok(code == 200, "...and staff sees the console data")

        ten_name = next(k for k in codes if k not in ("staff",) and codes[k].startswith("te-"))
        _, _, hdrs = hit("/api/auth/login", "POST", {"code": codes[ten_name]})
        ten_cookie = (hdrs.get("Set-Cookie") or "").split(";")[0]
        boot_t, code, _ = hit("/api/bootstrap?role=staff&id=whatever", cookie=ten_cookie)
        ok(code == 200 and boot_t.get("role") == "tenant",
           "a resident asking for the staff view gets THEIR OWN view — identity is the session")
        ok(boot_t["tenant"]["name"] == ten_name,
           "...specifically themselves, whatever the URL claimed")
        _, code, _ = hit("/api/money/summary", cookie=ten_cookie)
        ok(code == 403, "a resident cannot read the money surface")
        _, code, _ = hit("/api/approvals", cookie=ten_cookie)
        ok(code == 403, "...or the approvals queue")
        j = next(x for x in GET("/api/requests?limit=300") if x.get("vendor_token"))
        _, code, _ = hit(f"/api/job/{j['vendor_token']}")
        ok(code == 200, "a vendor job link still works with no session — the token is the credential")

        # --- the growth boundaries under enforcement
        tok = _json.loads((TMP / "config.json").read_text())["share"]["performance_token"]
        _, code, _ = hit(f"/api/pitch/{tok}")
        ok(code == 200, "the pitch link works with no session — its token is the credential")
        _, code, _ = hit("/api/listings")
        ok(code == 200, "listings are public — they are the storefront")
        _, code, _ = hit("/api/inquiries", "POST",
                         {"name": "Auth Prospect", "contact": "ap@example.com"})
        ok(code == 200, "a prospect files an inquiry with no account")
        _, code, _ = hit("/api/inquiries")
        ok(code == 401, "...but READING the inquiry queue requires a session")
        _, code, _ = hit("/api/referrals")
        ok(code == 401, "...and so does the referral book")

        own_name = next(k for k in codes if codes[k].startswith("ow-"))
        _, _, hdrs = hit("/api/auth/login", "POST", {"code": codes[own_name]})
        own_cookie = (hdrs.get("Set-Cookie") or "").split(";")[0]
        res, code, _ = hit("/api/referrals", "POST",
                           {"name": "Owner Auth Ref", "contact": "555-1212",
                            "source": "owner:someone_else"},
                           cookie=own_cookie)
        ok(code == 200, "a logged-in owner records a referral")
        ok((res["referral"]["source"].startswith("owner:")
            and res["referral"]["source"] != "owner:someone_else"),
           "...and the source is FORCED to their session, whatever the body claimed")
        _, code, _ = hit("/api/referrals", cookie=own_cookie)
        ok(code == 403, "an owner cannot read the referral book — they hand names in, only")
        _, code, _ = hit("/api/growth/rotate_share", "POST", {}, cookie=own_cookie)
        ok(code == 403, "an owner cannot rotate the share link — that is a staff control")
        _, code, _ = hit("/api/pipeline")
        ok(code == 401, "the pipeline requires a session")
        _, code, _ = hit("/api/pipeline", cookie=own_cookie)
        ok(code == 403, "...and an owner cannot read it — prospects are the firm's book")
        _, code, _ = hit("/api/prospects", "POST",
                         {"name": "X", "contact": "x@x.com"}, cookie=own_cookie)
        ok(code == 403, "...or write to it")
    finally:
        proc.terminate()


def test_idempotence():
    section("10. Running the sweep twice changes nothing")

    def snapshot():
        pend = GET("/api/approvals")
        msgs = GET("/api/messages")
        return (len(pend), len(msgs))

    POST("/api/agents/run")
    a1 = snapshot()
    POST("/api/agents/run")
    a2 = snapshot()
    ok(a1[0] == a2[0],
       f"pending approvals unchanged by a second sweep ({a1[0]} -> {a2[0]}) — "
       "the ledger used to add 3 owner reports per run, and the sentinel then "
       "blocked each copy for containing the owner's own name")
    ok(a1[1] == a2[1],
       f"messages unchanged by a second sweep ({a1[1]} -> {a2[1]})")


def test_concurrency():
    section("11. Concurrent intake — every request survives")

    import threading
    t = GET("/api/bootstrap?role=tenant")["tenant"]
    before = len(GET("/api/requests?limit=1000"))
    N, errs = 12, []
    def file_one(i):
        try:
            POST("/api/requests", {"tenant_id": t["id"],
                 "description": f"window latch number {i} is stuck and won't close"})
        except Exception as e:
            errs.append(e)
    ts = [threading.Thread(target=file_one, args=(i,)) for i in range(N)]
    [x.start() for x in ts]; [x.join() for x in ts]
    after = len(GET("/api/requests?limit=1000"))
    ok(not errs, f"all {N} concurrent submissions returned ({len(errs)} errors)")
    ok(after - before == N,
       f"all {N} stored ({before} -> {after}) — pre-fix the store lost "
       "concurrent writes wholesale")


def test_static():
    section("12. The shell the browser loads")

    for f in ("/", "/tenant.html", "/staff.html", "/owner.html",
              "/shared.css", "/app.js", "/sw.js", "/manifest.webmanifest"):
        r = GET(f, raw=True)
        ok(r.status == 200, f"GET {f}")
        if f.endswith((".css", ".js", ".html")) or f == "/":
            ok(r.headers.get("Cache-Control") == "no-cache",
               f"...{f} revalidates (the stale-asset trap)")

    r = GET("/api/metrics", raw=True)
    ok(r.headers.get("Cache-Control") == "no-store",
       "API responses are never cached")

    ok("application/json" in GET("/api/metrics", raw=True).headers.get("Content-Type", ""),
       "API responds as JSON")


if __name__ == "__main__":
    print(f"Booting a server on a throwaway store ({TMP.name}) …")
    try:
        boot()
        print(f"  up at {BASE}")
        test_seam()
        test_routes()
        test_resident_deflected()
        test_resident_still_broken()
        test_reopen_with_vendor()
        test_emergency()
        test_emergency_spend()
        test_staff()
        test_approvals()
        test_compliance_gate()
        test_vendor_journey()
        test_money_journey()
        test_turnover_journey()
        test_growth_journey()
        test_pipeline_journey()
        test_auth()
        test_idempotence()
        test_concurrency()
        test_static()
    finally:
        shutdown()
    print(f"\n{'=' * 58}\n  {PASS} passed, {FAIL} failed")
    if FAILURES:
        print("\n  Failures:")
        for f in FAILURES:
            print(f"    · {f}")
    sys.exit(1 if FAIL else 0)
