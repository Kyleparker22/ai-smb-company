#!/usr/bin/env python3
"""The simulated company — instantiate a PROSPECT's business, before they give us anything.

Every operated-AI sale dies in the same place: the prospect must hand over data,
tenant access, and an IT conversation *before* they have seen a single thing work.
So the value lands after the risk, and most deals never get there.

This inverts the order. From a short profile — what they told us across a table —
it generates their own business as a working walkthrough: their crew names, their
job types, their ticket sizes, their volume. Zero data access. Zero integration.
Zero permission. They watch their company run, then decide whether to hand us the
real thing.

SAME CODE, DIFFERENT DATA (`playground/_README.md`): this fills the real, live
`clients/_yourco-template/demo-kit/` — it never forks it. A forked demo drifts from
the product the day either side changes, and then you are demoing a thing you do
not sell.

THE HONESTY RULE, and it is not optional. Numbers here are MODELLED FROM WHAT THEY
TOLD US, never presented as achieved results. yourco is pre-revenue; a generated
demo that implies delivered outcomes would breach the credibility gate on the one
surface a prospect trusts most. The template's own "mockup on sample data" banner
stays, and the outcome bucket says modelled, not measured.

Run:
    python3 playground/prospect.py --example > /tmp/p.json
    python3 playground/prospect.py --profile /tmp/p.json
    python3 playground/prospect.py --profile /tmp/p.json --out-root /somewhere/safe
"""
import json, os, sys, argparse, random, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(REPO, "clients", "_yourco-template", "demo-kit")
DEFAULT_ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.join(HERE, "data")
TODAY = datetime.date.today()

EXAMPLE = {
    "client": "Ridgeline Grading",
    "brand": "#3f5d45",
    "useCase": "Signed-estimate coordination",
    "approver": "Dana",
    "trigger": "an estimate signs",
    "jobTypes": [
        {"name": "Driveway regrade + base", "low": 9000, "high": 22000},
        {"name": "Lot clearing & rough grade", "low": 14000, "high": 38000},
        {"name": "Drainage correction", "low": 6000, "high": 15000},
    ],
    "customers": ["The Alvarez family", "Brookfield Storage LLC", "Dan & Marie Whitcomb",
                  "Hollis Property Group", "Terry Nakamura"],
    "suppliers": ["Vulcan Aggregate", "Piedmont Pipe & Supply", "Carolina Erosion Control"],
    "subs": ["Beltline Hauling", "Ace Survey Co."],
    "jobsPerMonth": 14,
    "depositPct": 30,
    "statedAdminHoursPerWeek": 9,
}


def _money(n):
    return "${:,.2f}".format(n)


def _k(n):
    return f"${n/1000:.0f}K" if n >= 1000 else f"${n:.0f}"


def build_config(p, rng):
    client = p["client"]
    brand = p.get("brand", "#2c5f2d")
    approver = p.get("approver", "the owner")
    trigger = p.get("trigger", "a job signs")
    jobs = p["jobTypes"]
    customers = list(p.get("customers") or [])
    suppliers = list(p.get("suppliers") or ["your main supplier"])
    subs = list(p.get("subs") or ["your sub"])
    per_month = int(p.get("jobsPerMonth", 12))
    dep_pct = float(p.get("depositPct", 35))
    admin_h = float(p.get("statedAdminHoursPerWeek", 8))

    # The hero job on the approval screen — a real one of THEIR job types, at a
    # ticket inside the range they gave us.
    jt = rng.choice(jobs)
    total = round(rng.uniform(jt["low"], jt["high"]) / 25) * 25
    dep = round(total * dep_pct / 100, 2)
    cust = customers[0] if customers else "your customer"

    in_flight = max(2, round(per_month / 4))
    approved_msgs = in_flight * 3
    weekly_saved = round(admin_h * 0.7)          # modelled, stated as modelled below
    monthly_saved = round(weekly_saved * 4.33)
    avg_ticket = sum((j["low"] + j["high"]) / 2 for j in jobs) / len(jobs)
    monthly_volume = round(avg_ticket * per_month)

    cfg = {
        "client": client, "brand": brand, "employee": "your digital employee",
        "useCase": p.get("useCase", "Job coordination"),
        "tagline": (f"When {trigger}, your employee runs the early-stage coordination — and you approve "
                    f"anything customer-facing from your phone. Here's the whole thing, on a sample job."),
        "steps": [
            {"n": 1, "flow": True, "title": f"{trigger[0].upper() + trigger[1:]}",
             "desc": "Your employee reads it, applies your pricing, sorts materials, spots subs — and "
                     "drafts everything. Nothing sends yet."},
            {"n": 2, "href": "approval.html", "title": f"{approver} approves the deposit",
             "desc": "The customer email + text, with the amount locked by code. One tap to send."},
            {"n": 3, "href": "board.html", "title": "Watch every job from one board",
             "desc": "Deposit, suppliers, subs — where each job stands, plus a daily nudge list of "
                     "anything stuck."},
            {"n": 4, "href": "report.html", "title": "A monthly report of what it did",
             "desc": "Volume, outcomes, hours saved — and the reliability behind it."},
        ],
        "approval": {
            "approver": approver,
            "intro": "one message is ready for your okay",
            "items": [{
                "kind": "Customer deposit", "to": cust, "sub": jt["name"],
                "locked": _money(dep),
                "lockedSub": f"{dep_pct:g}% of {_money(total)} · computed by code",
                "email": (f"Subject: Deposit Request — Your {jt['name']} Project\n\n"
                          f"Hi {cust.split()[0] if cust else 'there'},\n\n"
                          f"Thank you for choosing {client} for your {jt['name'].lower()}.\n\n"
                          f"To reserve your spot on our schedule, we're requesting your deposit of "
                          f"{_money(dep)}, which represents {dep_pct:g}% of the {_money(total)} project "
                          f"total.\n\nYou can pay by check, card, or transfer.\n\nWarm regards,\n{client}"),
                "sms": (f"Hi! Your {client} deposit of {_money(dep)} is ready, and a detailed email is on "
                        f"its way. Thanks so much!"),
                "together": "Sends as email and text together, from your own number.",
            }],
        },
        "board": {
            "title": "jobs in flight",
            "metrics": [
                {"v": str(in_flight), "l": "jobs in flight"},
                {"v": "1", "l": "greenlit this week", "accent": True},
                {"v": str(approved_msgs), "l": "messages you approved"},
                {"v": f"~{weekly_saved}", "l": "hrs of coordination saved this week", "accent": True},
            ],
            "nudges": [
                f"<b>{suppliers[0]}</b> ({cust.split()[0] if cust else 'job'}) — order sent 2 days ago, "
                f"no reply. Auto-follow-up drafted, waiting for your okay.",
                f"<b>{subs[0]}</b> — scope sent, not yet confirmed. Chased once; will chase again "
                f"tomorrow morning.",
                f"<b>Deposit</b> — {cust} hasn't paid yet. Sitting {rng.randint(2, 5)} days; a reminder "
                f"is drafted.",
            ],
        },
        "report": {
            "metrics": [
                {"v": str(per_month), "l": "jobs coordinated"},
                {"v": "~3.5 hrs", "l": "avg from signed → first customer contact"},
                {"v": f"~{monthly_saved}", "l": "hours of coordination saved this month", "accent": True},
            ],
            "buckets": [
                {"v": _k(monthly_volume),
                 "l": f"volume coordinated — modelled from the {per_month} jobs/mo you told us, "
                      f"not a measured result"},
                {"v": f"~{monthly_saved} hrs",
                 "l": f"coordination hours back — modelled from your stated {admin_h:g} admin hrs/week",
                 "accent": True},
                {"v": "0", "l": "risk mitigation — unapproved sends, missed jobs, or wrong dollar figures"},
            ],
            "did": [
                f"Deposit requests sent the same hour {trigger} — every pricing tier applied correctly.",
                f"Material orders routed to {suppliers[0]}"
                + (f" and {suppliers[1]}" if len(suppliers) > 1 else "")
                + ", with delivery dates tracked.",
                f"Subs ({', '.join(subs)}) notified with scope + windows; chased the ones that went quiet.",
                "Flagged deposits and replies sitting too long, before they became a problem.",
            ],
            "reliability": [
                {"v": "0", "l": "messages sent without your approval"},
                {"v": "100%", "l": "of dollar figures computed by tested code"},
                {"v": "—", "l": "uptime · this is a walkthrough, not a running system"},
            ],
            "reliabilityLine": (
                "Every send in this walkthrough would be approved by a human before it left. The figures "
                "above are modelled from the numbers you gave us — they are not results we have "
                "delivered, and we will not show you numbers we have not earned."),
        },
    }
    return cfg


def render_config_js(cfg, p):
    return (
        "/* ============================================================================\n"
        f"   GENERATED by playground/prospect.py on {TODAY} for {cfg['client']}.\n"
        "   SYNTHETIC WALKTHROUGH — every name, job and figure below is modelled from the\n"
        "   profile the prospect gave us. Nothing here is their real data, and nothing here\n"
        "   is a result yourco has delivered. Do not edit by hand: edit the profile and\n"
        "   regenerate, or this drifts from what they actually told us.\n"
        f"   Profile: {json.dumps(p.get('_profilePath', 'inline'))}\n"
        "   ========================================================================== */\n"
        "window.DEMO = " + json.dumps(cfg, indent=2, ensure_ascii=False) + ";\n")


def main():
    ap = argparse.ArgumentParser(description="Generate a prospect's simulated company walkthrough.")
    ap.add_argument("--profile", help="path to the prospect profile JSON")
    ap.add_argument("--example", action="store_true", help="print an example profile and exit")
    ap.add_argument("--out-root", default=None,
                    help=f"sandbox root to write into (default {DEFAULT_ROOT})")
    ap.add_argument("--seed", type=int, default=7, help="same profile + same seed = same world")
    a = ap.parse_args()

    if a.example:
        print(json.dumps(EXAMPLE, indent=2)); return 0
    if not a.profile:
        ap.print_help(); return 1
    if not os.path.isdir(TEMPLATE):
        print(f"refused: the live demo kit is missing at {TEMPLATE} — this generator fills the real "
              f"template and will not invent a substitute", file=sys.stderr)
        return 2

    with open(a.profile) as f:
        p = json.load(f)
    for req in ("client", "jobTypes"):
        if not p.get(req):
            print(f"refused: profile needs {req!r} — a walkthrough built on defaults is not their "
                  f"business, it is ours with their logo on it", file=sys.stderr)
            return 2
    p["_profilePath"] = os.path.abspath(a.profile)

    root = a.out_root or DEFAULT_ROOT
    slug = "".join(c if c.isalnum() else "-" for c in p["client"].lower()).strip("-")
    dest = os.path.join(root, "_prospects", slug, "demo-kit")

    # Never write into the live repo tree — a generated prospect demo landing in
    # clients/ would look like a real engagement folder to every other reader.
    if os.path.abspath(dest).startswith(os.path.abspath(os.path.join(REPO, "clients"))):
        print("refused: refusing to write a synthetic walkthrough into clients/", file=sys.stderr)
        return 2

    os.makedirs(dest, exist_ok=True)
    for fn in os.listdir(TEMPLATE):
        if fn == "config.js":
            continue
        src = os.path.join(TEMPLATE, fn)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dest, fn))

    rng = random.Random(a.seed)
    cfg = build_config(p, rng)
    with open(os.path.join(dest, "config.js"), "w") as f:
        f.write(render_config_js(cfg, p))
    with open(os.path.join(root, "_prospects", slug, "_SYNTHETIC.md"), "w") as f:
        f.write(f"# {p['client']} — synthetic walkthrough\n\n"
                f"Generated {TODAY} by `playground/prospect.py` from `{p['_profilePath']}`.\n\n"
                f"Every name, job, and figure is **modelled from what the prospect told us**. None of it "
                f"is their real data. None of it is a result yourco has delivered. The kit's own "
                f"\"mockup on sample data\" banner stays on every screen.\n\n"
                f"Regenerate rather than hand-editing: `python3 playground/prospect.py --profile "
                f"{p['_profilePath']}`\n")

    print(f"built {p['client']} → {dest}")
    print(f"  {len(cfg['steps'])} steps · hero job: {cfg['approval']['items'][0]['sub']} "
          f"({cfg['approval']['items'][0]['locked']} deposit)")
    print(f"  open {os.path.join(dest, 'index.html')}")
    print("  figures are modelled from their stated volume and labelled as such — not delivered results.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
