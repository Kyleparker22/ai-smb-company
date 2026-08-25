#!/usr/bin/env python3
"""Playground seeder — builds a synthetic yourco at any scale.

    python3 playground/seed.py                 # default: 15 live clients, six months out
    python3 playground/seed.py --clients 40    # what does HQ look like at 40?
    python3 playground/seed.py --clients 0     # the empty state, honestly
    python3 playground/seed.py --wipe          # delete the playground tree

the Founder's ask (2026-08-07): "build and test things to see what they look like or how they
function before pushing anything live, and enter test data to see how things flow."

WHY THIS IS DATA-ONLY
The playground runs the REAL servers (crm/server.py, dashboard/server.py) with
YOURCO_DATA_ROOT pointed here. Code and HTML are never copied, so the sandbox always shows
the current CRM and the current HQ. A playground that forked the code would drift the day
either side changed — the "change one, sweep all" failure CLAUDE.md names as the #1
cross-session bug. It therefore cannot drift: there is only one copy of the code.

WHAT IS SEEDED vs SNAPSHOT
- Seeded (invented): the CRM, client engagement folders, finance, dashboard state, loop
  artifacts. Every CRM record carries `example: true`.
- Snapshot (copied verbatim from the live repo at seed time): the process/reference docs the
  Board reads — counsel gates, the launch-gate, the three backlogs, the agent registry, the
  loop prompts and timers. These are the OS's own documents, not client data; faking them
  would make the Board meaningless. They are a point-in-time copy — reseed to refresh.

EVERY NAME HERE IS INVENTED. No real person, client, or prospect appears in this file.
Deterministic: same --seed gives the same world, so a bug is reproducible.
"""
import os, sys, json, random, shutil, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(REPO, "clients", "_yourco-template")

# Reference docs copied verbatim so the Board has real gates/backlogs to read.
SNAPSHOT = [
    "processes/counsel-gates.md", "processes/launch-gate.md",
    "processes/automation-roadmap.md", "crm/_backlog.md",
    "offerings/_frontier-roadmap.md", "runtime/agent-registry.json",
]
SNAPSHOT_DIRS = ["runtime/prompts", "runtime/systemd",
                 # The connector curriculum is CONTENT, not data — the console renders these
                 # lesson bodies verbatim and the training gate keys off their filenames.
                 # Inventing lessons would make the sandbox teach something yourco doesn't.
                 "processes/partnerships/connector-training"]

VERTICALS = ["Landscaping", "Roofing", "HVAC", "Dental", "Med Spa", "Law Firm", "Real Estate",
             "Auto Detailing", "Pest Control", "Plumbing", "Fitness Studio", "Veterinary",
             "Accounting", "Staffing", "Electrical", "Pool Service", "Catering", "Optometry"]
CITIES = ["Riverton, FL", "Tampa, FL", "Clearwater, FL", "Sarasota, FL", "Yourtown",
          "Raleigh, ST", "Asheville, ST", "Savannah, GA", "Mobile, AL", "Knoxville, TN"]
# Invented company names — deliberately generic-plausible, none real.
STEMS = ["Ridgeline", "Copperfield", "Blue Heron", "Ironwood", "Stonebridge", "Harborview",
         "Kestrel", "Lantern", "Meridian", "Northgate", "Willowbrook", "Cedar Point",
         "Falcon Ridge", "Great Oak", "Silverbrook", "Tidewater", "Foxglove", "Amberline",
         "Brightwater", "Clearfield", "Dunmore", "Eastvale", "Fairhaven", "Granite Hill",
         "Hollowpine", "Junipero", "Larkspur", "Marbleton", "Oakhurst", "Pinecrest",
         "Quarrystone", "Redfern", "Summerhill", "Thornbury", "Vantage", "Westmoor"]
SUFFIX = {"Landscaping": "Landscapes", "Roofing": "Roofing Co.", "HVAC": "Air & Heat",
          "Dental": "Family Dental", "Med Spa": "Aesthetics", "Law Firm": "Law Group",
          "Real Estate": "Realty", "Auto Detailing": "Auto Care", "Pest Control": "Pest Solutions",
          "Plumbing": "Plumbing", "Fitness Studio": "Fitness", "Veterinary": "Animal Hospital",
          "Accounting": "CPA Group", "Staffing": "Staffing Partners", "Electrical": "Electric",
          "Pool Service": "Pools", "Catering": "Catering Co.", "Optometry": "Eye Care"}
FIRST = ["Dana", "Marcus", "Priya", "Elliot", "Rosa", "Tobias", "Nadia", "Curtis", "Imani",
         "Vaughn", "Leona", "Desmond", "Fatima", "Grant", "Sylvia", "Omar", "Bree", "Hollis",
         "Marisol", "Terrence", "Junie", "Kwame", "Adele", "Rune", "Paloma", "Emmett"]
LAST = ["Alvarez", "Brennan", "Castillo", "Duval", "Ferraro", "Gadsden", "Halloran", "Ibarra",
        "Jessup", "Kowalski", "Lindqvist", "Moreau", "Nakamura", "Okonjo", "Pelletier",
        "Quintero", "Rasmussen", "Sowande", "Thibodeaux", "Ulrich", "Vasquez", "Whitlock"]
MODULES = ["intake", "scheduling", "quoting", "follow-up", "dispatch", "billing", "reporting"]
PILLARS = ["Intake", "Sales", "Customer", "Operations", "Back Office", "Marketing"]
OUTCOMES = ["quotes out same-day", "after-hours calls answered", "invoices sent on time",
            "follow-ups never dropped", "jobs scheduled without a call", "reviews requested"]


def d(days_ago):
    return (datetime.date.today() - datetime.timedelta(days=days_ago)).isoformat()


def money(n):
    return f"${n:,}"


# --------------------------------------------------------------------------
def build_crm(rng, n_live, n_motion, n_bench):
    """A CRM at scale, on the real ladder, with every record flagged example:true."""
    stages = [
        {"key": "relationship", "label": "Relationship"}, {"key": "firsttouch", "label": "First Touch"},
        {"key": "sitdown", "label": "Sit-Down"}, {"key": "audit", "label": "Audit"},
        {"key": "proposal", "label": "Proposal"}, {"key": "signed", "label": "Signed"},
        {"key": "build", "label": "Build"}, {"key": "live", "label": "Live"},
        {"key": "expand", "label": "Expand"},
    ]
    companies, contacts, deals, activities, tasks = [], [], [], [], []
    names = rng.sample(STEMS, min(len(STEMS), n_live + n_motion + n_bench))
    i = 0

    def make(stage, age_days, retainer, build_fee):
        nonlocal i
        stem = names[i] if i < len(names) else f"{rng.choice(STEMS)} {i}"
        vert = rng.choice(VERTICALS)
        cid, pid, did = f"pc{i}", f"pp{i}", f"pd{i}"
        nm = f"{stem} {SUFFIX.get(vert, 'Co.')}"
        companies.append({"id": cid, "name": nm, "vertical": vert, "size": f"{rng.randint(4,60)} staff",
                          "location": rng.choice(CITIES), "source": rng.choice(
                              ["warm network", "referral — connector", "referral — client", "inbound"]),
                          "status": "client" if stage in ("live", "expand") else "prospect",
                          "owner": rng.choice(["the Founder", "Reilly"]), "domain": "", "example": True,
                          "referrer": "", "referredByCompany": ""})
        contacts.append({"id": pid, "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}", "companyId": cid,
                         "role": rng.choice(["Owner", "GM", "Operations Manager", "Managing Partner"]),
                         "email": f"owner@{stem.lower().replace(' ','')}.example",
                         "phone": f"555-01{i:02d}", "lastTouch": d(rng.randint(0, 20)),
                         "status": "client" if stage in ("live", "expand") else "warm", "example": True})
        touch = rng.randint(0, 9) if stage in ("live", "expand") else rng.randint(0, 30)
        deals.append({"id": did, "name": f"{nm} — AI OS", "companyId": cid,
                      "useCase": rng.choice(MODULES) + " + " + rng.choice(MODULES),
                      "stage": stage, "buildFee": build_fee, "retainer": retainer,
                      "value": retainer * 12 + build_fee,
                      "nextAction": rng.choice([
                          "Weekly readout + expansion conversation", "Confirm module 2 scope",
                          "Review eval failures from last week", "Send the monthly outcome report",
                          "Book the quarterly business review"]) if stage in ("live", "expand") else
                      rng.choice(["Send the audit findings", "Scope the OS bands", "Book the sit-down",
                                  "Follow up on the proposal", "Kick off the build"]),
                      "nextDate": d(-rng.randint(1, 21)), "lastTouch": d(touch),
                      "owner": "the Founder", "example": True, "stageSince": d(age_days)})
        for k in range(rng.randint(2, 5)):
            activities.append({"id": f"pa{i}_{k}", "dealId": did, "companyId": cid,
                               "date": d(touch + k * rng.randint(3, 12)), "type": rng.choice(
                                   ["call", "meeting", "email", "readout"]),
                               "note": rng.choice([
                                   "Weekly readout sent; no issues raised.",
                                   "Owner asked about adding a second module.",
                                   "Reviewed eval results — one gate tightened.",
                                   "Escalation handled inside the approval gate.",
                                   "Discussed expanding to the back-office pillar."]), "example": True})
        i += 1
        return did

    for _ in range(n_live):
        make(rng.choice(["live"] * 5 + ["expand"]), rng.randint(40, 220),
             rng.choice([1000, 1500, 2000, 2500, 3000]), rng.choice([0, 2500, 5000]))
    for _ in range(n_motion):
        make(rng.choice(["sitdown", "audit", "proposal", "signed", "build"]), rng.randint(5, 60),
             rng.choice([1000, 1500, 2000]), rng.choice([0, 2500]))
    for _ in range(n_bench):
        make("relationship", rng.randint(20, 120), 0, 0)

    # --- connectors -------------------------------------------------------
    # The Connector Console + trust ladder read these. Rungs are EARNED from evidence, never
    # granted: R1 needs a referral that reached a real conversation, R2 needs one live+retained
    # 90d, R3 needs 3+. So the seeder attributes real referrals rather than stamping a rung —
    # otherwise the sandbox would show a ladder that the ladder code disagrees with.
    live_ids = [x for x in deals if x["stage"] in ("live", "expand")]
    motion_ids = [x for x in deals if x["stage"] in ("sitdown", "audit", "proposal")]
    connectors = []
    plan = [("active", 4), ("active", 3), ("active", 1), ("active", 1), ("prospect", 0), ("prospect", 0)]
    ci = 0
    for status, n_ref in plan:
        nm = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        pid = f"pconn{ci}"
        connectors.append({
            "id": pid, "name": nm, "companyId": None, "role": None,
            "email": f"{nm.split()[0].lower()}@example.test", "phone": f"555-02{ci:02d}",
            "lastTouch": d(rng.randint(1, 25)),
            "status": f"{'active' if status == 'active' else 'warm — prospective'} connector",
            "example": True, "relationship": rng.choice(["Friend", "Former colleague", "Family"]),
            "kind": "internal", "teamRole": "connector", "teamStatus": status,
            "joinedDate": d(rng.randint(90, 300)) if status == "active" else "",
        })
        # attribute referrals to real companies so the ladder can compute a rung from evidence
        pool = (live_ids if n_ref >= 3 else motion_ids + live_ids)
        for k in range(n_ref):
            if not pool:
                break
            dl = pool[(ci * 3 + k) % len(pool)]
            co = next(c for c in companies if c["id"] == dl["companyId"])
            co["referrer"] = nm
            co["referredDate"] = d(rng.randint(120, 320))
            co["source"] = "referral — connector"
        ci += 1
    contacts.extend(connectors)

    for n, due, done in [("Quarterly business reviews — schedule all live accounts", d(-9), False),
                         ("Renewal notice window opens for 3 accounts", d(-4), False),
                         ("Reconcile connector commissions for the month", d(3), False)]:
        tasks.append({"id": f"pt{len(tasks)}", "title": n, "due": due, "done": done, "example": True})

    return {"meta": {"updated": d(0), "owner": "David",
                     "note": "SYNTHETIC PLAYGROUND DATA — every record is example:true. "
                             "Generated by playground/seed.py. Nothing here is a real company or person."},
            "stages": stages, "companies": companies, "contacts": contacts, "deals": deals,
            "closed": [], "activities": activities, "tasks": tasks,
            "repApplicants": [], "graph": {"nodes": [], "edges": []}, "dispatch": {}}


# --------------------------------------------------------------------------
def build_client_folder(root, rng, company, deal, contact):
    """One engagement folder with the artifacts clients.py actually reads."""
    slug = company["name"].lower().replace(" ", "-").replace(".", "").replace("&", "and")
    f = os.path.join(root, "clients", slug)
    os.makedirs(os.path.join(f, "ledger"), exist_ok=True)
    live = deal["stage"] in ("live", "expand")
    months_live = rng.randint(1, 7) if live else 0
    emp = rng.choice(FIRST)

    open(os.path.join(f, "_README.md"), "w").write(
        f"# {company['name']} — engagement summary\n\n"
        f"> SYNTHETIC. Generated by `playground/seed.py`.\n\n"
        f"- **Vertical / use case:** {company['vertical']} — {deal['useCase']}\n"
        f"- **Named employee:** {emp} · {emp.lower()}@{slug}.example\n"
        f"- **Signed:** {d(months_live * 30 + 14)} · **Go-live:** {d(months_live * 30)}\n"
        f"- **Status:** {'live' if live else deal['stage']}\n"
        f"- **Owner (delivery):** Kimi\n")

    # cost.md — a real-shaped ledger, including the honest messiness (ranges, unpriced rows)
    rows = []
    rows.append(f"| {d(months_live*30+30)} | discovery | Audit + scoping + proposal | ~600k | "
                f"~${rng.randint(8,18)} | est. |")
    rows.append(f"| {d(months_live*30+14)} | build | Module build through go-live | ~{rng.randint(2,6)}M | "
                f"~${rng.randint(20,45)}–{rng.randint(50,80)} | est. |")
    rows.append(f"| {d(months_live*30+13)} | tools | Telephony + voice provisioning | — | "
                f"{rng.randint(2,9)} credits | metered |")
    for m in range(months_live):
        rows.append(f"| {d(m*30+2)} | run | Month {months_live-m} operation — all modules | "
                    f"~{rng.randint(1,4)}M | ~${rng.randint(12,40)} | metered |")
    open(os.path.join(f, "cost.md"), "w").write(
        f"# Cost — {company['name']}\n\n"
        f"**Pricing in effect:** build fee {money(deal['buildFee'])} (one-time) · "
        f"monthly retainer {money(deal['retainer'])} · vertical ref: pricing/v0/{company['vertical'].lower()}.md\n\n"
        "| Date | Phase | What | Tokens | $ | Evidence |\n|------|-------|------|--------|---|----------|\n"
        + "\n".join(rows) + "\n")

    # contract.md — only for signed-and-beyond, so the view shows the real 'None' case too
    if deal["stage"] in ("signed", "build", "live", "expand"):
        eff = months_live * 30
        nxt = -(30 - (eff % 30)) if live else -25
        open(os.path.join(f, "contract.md"), "w").write(
            f"# Contract — {company['name']}\n\n> SYNTHETIC.\n\n"
            "| Field | Value |\n|---|---|\n"
            f"| Status | executed |\n| Agreement | Engagement Agreement |\n"
            f"| Signed | {d(eff+14)} · by {contact['name']}, {contact['role']} |\n"
            f"| Effective | {d(eff)} |\n| Initial term | month-to-month |\n"
            f"| Renews | auto-monthly |\n| Notice required | 30 days |\n"
            f"| Notice deadline | {d(nxt)} |\n"
            f"| Build fee | {money(deal['buildFee'])} |\n| Retainer | {money(deal['retainer'])}/mo · net 0 · ACH |\n"
            f"| DPA | {'signed ' + d(eff) if rng.random() > .4 else 'pending'} |\n"
            f"| BAA | not required |\n"
            f"| Counsel-reviewed | {'yes' if rng.random() > .5 else 'no — counsel gate #1 open'} |\n")

    for name, body in [
        ("03_eval.md", f"# Eval — {company['name']}\n\nGates per module; pass required before any rung moves.\n"),
        ("go-live.md", f"# Go-live — {company['name']}\n\nWent live {d(months_live*30)}.\n" if live
         else f"# Go-live — {company['name']}\n\nNot yet scheduled.\n"),
        ("weekly-readout.md", f"# Weekly readout — {company['name']}\n\nLatest: {d(rng.randint(1,9))}\n"),
        ("autonomy-matrix.md", f"# Autonomy — {company['name']}\n\nPer-action rungs, earned on eval evidence.\n"),
    ]:
        if live or name in ("03_eval.md", "go-live.md"):
            open(os.path.join(f, name), "w").write(body)
    src = os.path.join(TEMPLATE, "client-console.html")
    if live and os.path.exists(src):
        shutil.copy2(src, os.path.join(f, "client-console.html"))

    # ledger — the moat layer's own record, one file per month live
    for m in range(months_live):
        month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=m * 30)).strftime("%Y-%m")
        lines = []
        for a in range(rng.randint(30, 90)):
            lines.append(json.dumps({
                "record_type": "action_record", "id": f"a-{month}-{a:04d}", "ts": d(m * 30 + a % 28) + "T09:00:00-04:00",
                "module": rng.choice(MODULES), "pillar": rng.choice(PILLARS),
                "action_type": rng.choice(["draft_reply", "book_slot", "send_quote", "log_record"]),
                "autonomy_tier": rng.choice(["R1", "R1", "R2", "R2", "R3"]),
                "outcome_class": rng.choice(["completed", "approved+sent", "approved+sent", "escalated"]),
                "approval": None, "eval_ref": None, "links": []}))
        # Evals run per gate on a cadence. A gate that fails is usually FIXED — so a fail is
        # normally followed by a pass on the same gate a few days later. Only ~1 engagement in
        # 4 is left with a genuinely open gate. Without this the seeder made every mature
        # client permanently red, which told you nothing.
        for gate in ("reply-accuracy", "booking-correctness", "quote-math", "tone-match"):
            mod = rng.choice(MODULES)
            e = 0
            for day in (2, 12, 22):
                fail = rng.random() < 0.14
                lines.append(json.dumps({
                    "record_type": "eval_record", "id": f"e-{month}-{gate}-{e:02d}",
                    "ts": d(m * 30 + (28 - day)) + "T10:00:00-04:00", "module": mod, "gate_name": gate,
                    "result": "fail" if fail else "pass", "sample_size": rng.choice([20, 25, 40]),
                    "notes": "", "action_ids": []}))
                e += 1
                if fail and rng.random() < 0.8:  # remediated: a passing re-run 3 days later
                    lines.append(json.dumps({
                        "record_type": "eval_record", "id": f"e-{month}-{gate}-{e:02d}",
                        "ts": d(m * 30 + (28 - day) - 3) + "T10:00:00-04:00", "module": mod,
                        "gate_name": gate, "result": "pass", "sample_size": 40,
                        "notes": "re-run after fix", "action_ids": []}))
                    e += 1
        if rng.random() < 0.35:
            unresolved = rng.random() < 0.3 and m == 0
            lines.append(json.dumps({
                "record_type": "incident_record", "id": f"i-{month}-0001", "ts": d(m * 30 + 3) + "T09:02:44-04:00",
                "severity": rng.choice(["low", "low", "medium"]), "module": rng.choice(MODULES),
                "what_happened": "connector retried before success", "caught_by": rng.choice(["watchdog", "eval"]),
                "impact": "none", "remediation": "retry budget raised; eval case added",
                "resolved_ts": None if unresolved else d(m * 30 + 3) + "T09:31:00-04:00"}))
        lines.append(json.dumps({
            "record_type": "outcome_record", "id": f"o-{month}-0001", "ts": d(m * 30) + "T17:00:00-04:00",
            "outcome_name": rng.choice(OUTCOMES),
            "metric": {"name": "count", "value": rng.randint(20, 180), "source": "client system", "period": month},
            "evidence_links": []}))
        if rng.random() < 0.4:
            lines.append(json.dumps({
                "record_type": "autonomy_event", "id": f"au-{month}-0001", "ts": d(m * 30 + 12) + "T08:00:00-04:00",
                "module": rng.choice(MODULES), "action_type": "draft_reply", "from_tier": "R1", "to_tier": "R2",
                "evidence": "streak_summary: 40/40 approved unmodified over 21 days", "approved_by": "the Founder"}))
        open(os.path.join(f, "ledger", f"{month}.jsonl"), "w").write("\n".join(lines) + "\n")
    return slug, months_live


# --------------------------------------------------------------------------
def seed_training(root, crm):
    """Advance each connector's training by calling the REAL training code.

    Deliberately not hand-writing `meta.connectorTraining`. That structure is owned by
    crm/connector_training.py, and a seeder that fabricates its own copy would drift from the
    schema and — worse — could produce a state the real code can never produce, so the sandbox
    would be teaching a fiction. Driving mark_lesson()/confirm_lesson() means the playground
    exercises the actual gates: a connector can never mark another's training, R2+ marks are
    SUBMISSIONS that an operator must confirm, and nothing unconfirmed moves the ceiling.
    """
    os.environ["YOURCO_DATA_ROOT"] = root          # must precede the import — it binds CRM
    sys.path.insert(0, os.path.join(REPO, "crm"))
    try:
        import connector_training as T
    except Exception as e:
        print(f"  training   skipped ({e})")
        return
    conns = [c["name"] for c in crm["contacts"]
             if c.get("teamRole") == "connector" and c.get("teamStatus") == "active"]
    # a spread: one fully trained, one mid, one just onboarded, one deliberately left at zero
    depth = {0: "R3", 1: "R2", 2: "R0", 3: None}
    by_rung = {}
    for L in T.load_lessons():
        by_rung.setdefault(L.get("rung"), []).append(L)
    marked = confirmed = 0
    for i, name in enumerate(conns):
        want = depth.get(i, "R0")
        if not want:
            continue
        for key in ("R0", "R1", "R2", "R3"):
            if key > want:
                break
            for L in by_rung.get(key, []):
                try:
                    T.mark_lesson(name, L["slug"], acknowledged=L.get("acknowledge"))
                    marked += 1
                except Exception:
                    continue  # a refusal here is the gate doing its job
                if key >= "R2":  # R2+ needs an operator to confirm before it counts
                    try:
                        T.confirm_lesson("the Founder", name, L["slug"])
                        confirmed += 1
                    except Exception:
                        pass
    del os.environ["YOURCO_DATA_ROOT"]
    print(f"  training   {marked} lessons marked · {confirmed} operator-confirmed (R2+)")


def main():
    ap = argparse.ArgumentParser(description="Seed the yourco playground with synthetic data.")
    ap.add_argument("--clients", type=int, default=15, help="live/expand engagements (default 15)")
    ap.add_argument("--motion", type=int, default=10, help="deals in motion behind them")
    ap.add_argument("--bench", type=int, default=18, help="warm relationships on the bench")
    ap.add_argument("--seed", type=int, default=7, help="RNG seed — same seed, same world")
    ap.add_argument("--wipe", action="store_true", help="delete the playground data tree and exit")
    a = ap.parse_args()

    root = os.path.join(HERE, "data")
    if a.wipe:
        shutil.rmtree(root, ignore_errors=True)
        print(f"wiped {root}")
        return
    shutil.rmtree(root, ignore_errors=True)
    for sub in ("crm", "dashboard", "clients", "finance", "loops", "processes", "offerings",
                "runtime", "agents/bird/connector-demos", "_connector-consoles"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)

    rng = random.Random(a.seed)
    crm = build_crm(rng, a.clients, a.motion, a.bench)
    json.dump(crm, open(os.path.join(root, "crm", "data.json"), "w"), indent=2)

    # engagement folders for everything sold-or-beyond
    by_c = {c["id"]: c for c in crm["companies"]}
    by_p = {p["companyId"]: p for p in crm["contacts"]}
    made, rev_rows = [], []
    for deal in crm["deals"]:
        if deal["stage"] not in ("signed", "build", "live", "expand"):
            continue
        co = by_c[deal["companyId"]]
        slug, months = build_client_folder(root, rng, co, deal, by_p[deal["companyId"]])
        made.append(slug)
        for m in range(months):
            month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=m * 30)).strftime("%Y-%m")
            rev_rows.append(f"| {month} | {co['name']} | Monthly retainer | {money(deal['retainer'])} | "
                            f"{d(m*30)} | {d(m*30+1)} | paid |")
        if months and deal["buildFee"]:
            rev_rows.append(f"| {d(months*30)[:7]} | {co['name']} | Build fee | {money(deal['buildFee'])} | "
                            f"{d(months*30+14)} | {d(months*30+12)} | paid |")

    mrr = sum(x["retainer"] for x in crm["deals"] if x["stage"] in ("live", "expand"))
    open(os.path.join(root, "finance", "revenue.md"), "w").write(
        "# revenue.md — SYNTHETIC PLAYGROUND DATA\n\n"
        "| month | client | description | amount | invoice_date | paid_date | status |\n"
        "|-------|--------|-------------|--------|--------------|-----------|--------|\n"
        + ("\n".join(rev_rows) if rev_rows else "| — | — | — | — | — | — | — |")
        + f"\n\n## Running totals\n- MRR: {money(mrr)}\n")

    # dashboard state — start from the live shape so every tab renders, then override metrics
    live_dash = json.load(open(os.path.join(REPO, "dashboard", "data.json")))
    live_dash.setdefault("company", {}).setdefault("metrics", {})
    live_dash["company"]["metrics"].update({"clients": a.clients, "mrr": mrr, "cash": 90000})
    live_dash["meta"] = {"updated": d(0), "note": "SYNTHETIC PLAYGROUND DATA — playground/seed.py"}
    json.dump(live_dash, open(os.path.join(root, "dashboard", "data.json"), "w"), indent=2)
    for f in ("goals.json", "todo.json"):
        shutil.copy2(os.path.join(REPO, "dashboard", f), os.path.join(root, "dashboard", f))

    # loop artifacts — fresh, so the Board's liveness lane shows a HEALTHY runtime for contrast
    for loop in ("open-loops", "gap-audit", "customer-health", "monday-briefing", "sales",
                 "finance", "eval-review", "inbox-triage", "crm-autolog", "initiative",
                 "melanie-briefing", "pipeline-report", "content", "source-watch", "advisor",
                 "brand-audit", "aeo-geo", "brett-ideas", "pricing-review", "_watchdog",
                 "_consistency", "_governance", "_crm-hygiene", "sadie", "demo-prep"):
        p = os.path.join(root, "loops", loop)
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, f"{d(rng.randint(0,3))}.md"), "w").write(
            f"# {loop} — synthetic playground artifact\n\n"
            "Written by playground/seed.py so loop-liveness reads healthy in the sandbox.\n\n"
            "## The queue\n\n| # | Item | Whose | Waiting since | Age | Next step |\n"
            "|---|---|---|---|---|---|\n"
            f"| 1 | **Sample open item** — a synthetic queue row so the Board renders. | the Founder | {d(6)} | 6d | Do the thing. |\n"
            if loop == "open-loops" else
            f"# {loop} — synthetic playground artifact\n\nWritten by playground/seed.py.\n")

    # snapshot the OS's own reference docs — faking these would make the Board meaningless
    for rel in SNAPSHOT:
        src, dst = os.path.join(REPO, rel), os.path.join(root, rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    for rel in SNAPSHOT_DIRS:
        src, dst = os.path.join(REPO, rel), os.path.join(root, rel)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    seed_training(root, crm)

    open(os.path.join(root, "_SYNTHETIC.md"), "w").write(
        f"# This tree is synthetic\n\nGenerated {d(0)} by `playground/seed.py` "
        f"(--clients {a.clients} --motion {a.motion} --bench {a.bench} --seed {a.seed}).\n"
        "Every company, person, deal, dollar and ledger record is invented. Nothing here is real.\n"
        "Reference docs under processes/, offerings/ and runtime/ are a verbatim SNAPSHOT of the "
        "live repo at seed time — reseed to refresh them.\n")

    print(f"seeded {root}")
    print(f"  CRM        {len(crm['companies'])} companies · {len(crm['deals'])} deals "
          f"({a.clients} live, {a.motion} in motion, {a.bench} bench) · {len(crm['activities'])} activities")
    print(f"  clients/   {len(made)} engagement folders")
    print(f"  finance    MRR {money(mrr)} · {len(rev_rows)} revenue rows")
    conns = [c for c in crm["contacts"] if c.get("teamRole") == "connector"]
    print(f"  connectors {len(conns)} ({sum(1 for c in conns if c['teamStatus']=='active')} active) · "
          f"{sum(1 for c in crm['companies'] if c.get('referrer'))} referred companies")
    print(f"  loops/     25 fresh artifacts")
    print("\nrun it:  ./playground/run.sh          (CRM :8890 · HQ :8891)")


if __name__ == "__main__":
    main()
