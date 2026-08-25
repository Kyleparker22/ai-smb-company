#!/usr/bin/env python3
"""The spend teardown — audit the whole stack, find the money already leaving.

The hardest thing to ask a business with no budget line for AI is for a budget
line for AI. So don't. Audit what they are already paying — every tool, seat,
subscription, retainer and service — and the conversation stops being about new
spend and becomes about spend they have already approved and stopped watching.

Two halves, deliberately never summed into one headline:

  EVIDENCED    money that is provably gone or provably idle — unused seats at a
               known per-seat price, duplicate tools doing one job, a
               reconciliation error someone can point at in their own books.
               (Sample Realty's trust-account review found -$1,830.51 of exactly
               this. That number is real because it came out of her ledger.)

  MODELLED     what a replacement or consolidation might save. Assumption-stated,
               always, and never added to the evidenced column. A teardown that
               blends the two produces a big number nobody can defend, and the
               first defended question kills the whole document.

REPLACEABILITY is fenced by the B7 guardrails (`decisions/2026-08-07_saas-replacement-wedge.md`):
single-workflow horizontal tools only. Systems of record, compliance-locked tools
and anything with real network effects are marked OUT OF SCOPE by this module and
cannot be overridden by an optimistic input — that fence is the difference between
a wedge and a weekend replacement that loses someone's data.

Run:
    python3 runtime/spend_teardown.py --example > /tmp/stack.json
    python3 runtime/spend_teardown.py --inventory /tmp/stack.json
    python3 runtime/spend_teardown.py --inventory /tmp/stack.json --json
"""
import json, os, sys, argparse, datetime

TODAY = datetime.date.today()

# Categories that this instrument will never mark replaceable, whatever the input says.
OUT_OF_SCOPE = {
    "system-of-record": "the book of record — replacing it risks the data the business runs on",
    "compliance-locked": "regulatory/audit obligations ride on this tool's own attestations",
    "network-effect": "its value is the other people on it; a replacement has none of them",
    "payments": "money movement — regulated, and the failure mode is somebody's payroll",
}
CLONABLE = {"forms", "scheduling", "e-sign", "approval-flow", "dashboard", "reporting",
            "project-tracker", "intake", "notifications"}

EXAMPLE = {
    "business": "Ridgeline Grading",
    "items": [
        {"name": "Field service platform", "annual": 28000, "category": "system-of-record",
         "seats": 12, "seatsUsed": 5, "screensUsed": 7, "screensTotal": 40},
        {"name": "Separate scheduling app", "annual": 4200, "category": "scheduling",
         "seats": 12, "seatsUsed": 3, "overlapsWith": "Field service platform"},
        {"name": "E-signature tool", "annual": 1800, "category": "e-sign", "seats": 5, "seatsUsed": 1},
        {"name": "Form builder", "annual": 1440, "category": "forms", "seats": 3, "seatsUsed": 1},
        {"name": "Consumer AI chat seats", "annual": 960, "category": "intake",
         "seats": 4, "seatsUsed": 4, "aiTool": True, "sanctioned": False,
         "customerDataEntered": True},
        {"name": "Payroll", "annual": 3600, "category": "payments", "seats": 1, "seatsUsed": 1},
    ],
    "findings": [
        {"what": "Cross-funded owner draw never reconciled between property ledgers",
         "amount": 1830.51, "evidence": "their own trust-account journal, FY reconciliation"},
        {"what": "Duplicate supplier invoice paid twice in March", "amount": 940.00,
         "evidence": "bank export vs AP ledger"},
    ],
}


def analyse(inv):
    items = inv.get("items") or []
    total = sum(float(i.get("annual") or 0) for i in items)

    idle, overlaps, shadow, replaceable, out_of_scope = [], [], [], [], []
    for i in items:
        annual = float(i.get("annual") or 0)
        seats, used = i.get("seats"), i.get("seatsUsed")
        cat = (i.get("category") or "").lower()

        # Idle seats — evidenced, because the per-seat price is theirs and the
        # count is theirs. No modelling involved.
        if seats and used is not None and seats > used and annual:
            per_seat = annual / seats
            idle.append({"name": i["name"], "idleSeats": seats - used,
                         "perSeat": round(per_seat, 2),
                         "annualIdle": round(per_seat * (seats - used), 2)})

        if i.get("overlapsWith"):
            overlaps.append({"name": i["name"], "with": i["overlapsWith"], "annual": annual})

        if i.get("aiTool") and not i.get("sanctioned", False):
            shadow.append({"name": i["name"], "annual": annual,
                           "customerData": bool(i.get("customerDataEntered")),
                           "risk": ("customer data is being entered into an unsanctioned AI tool"
                                    if i.get("customerDataEntered") else
                                    "unsanctioned AI tool in use — no approval or audit trail")})

        if cat in OUT_OF_SCOPE:
            out_of_scope.append({"name": i["name"], "category": cat,
                                 "why": OUT_OF_SCOPE[cat], "annual": annual})
        elif cat in CLONABLE:
            util = None
            if i.get("screensUsed") and i.get("screensTotal"):
                util = round(100.0 * i["screensUsed"] / i["screensTotal"], 1)
            replaceable.append({"name": i["name"], "category": cat, "annual": annual,
                                "utilisationPct": util})
        else:
            out_of_scope.append({"name": i["name"], "category": cat or "uncategorised",
                                 "why": "not classified into the clonable tier — left alone by default",
                                 "annual": annual})

    findings = inv.get("findings") or []
    found = sum(float(f.get("amount") or 0) for f in findings)
    undocumented = [f for f in findings if not f.get("evidence")]

    evidenced_idle = sum(x["annualIdle"] for x in idle)
    modelled_overlap = sum(x["annual"] for x in overlaps)
    modelled_replace = sum(x["annual"] for x in replaceable)

    return {
        "generated": TODAY.isoformat(), "business": inv.get("business", "—"),
        "itemCount": len(items), "annualStackSpend": round(total, 2),
        # Cash and idle are BOTH evidenced, and are still not the same claim. A
        # reconciliation error is money that left. An idle seat is money that is
        # being spent on nothing — recoverable only if the contract lets them drop
        # seats. Summing the two produces a headline that dies on "so can I get
        # that sixteen grand back?" — no, not necessarily, and the teardown should
        # say so before they ask.
        "evidenced": {
            "foundMoney": round(found, 2),
            "findings": findings,
            "idleSeatSpend": round(evidenced_idle, 2),
            "idle": idle,
            "idleCaveat": ("Idle seats are evidenced as idle, not as recoverable — whether the spend "
                           "comes back depends on their contract's seat minimums and renewal terms. "
                           "Checked before it is ever quoted as a saving."),
        },
        "modelled": {
            "duplicateToolSpend": round(modelled_overlap, 2),
            "overlaps": overlaps,
            "replaceableToolSpend": round(modelled_replace, 2),
            "replaceable": replaceable,
            "note": ("Modelled, not evidenced. Replacing or consolidating a tool has a build and an "
                     "operating cost; these figures are the gross line items, not net savings, and no "
                     "net number is claimed here."),
        },
        "governance": {"shadowAI": shadow},
        "outOfScope": out_of_scope,
        "warnings": ([f"{len(undocumented)} finding(s) carry no evidence field — a found-money figure "
                      f"without a document behind it is the one number that will be challenged first"]
                     if undocumented else []),
        "honesty": (
            "The evidenced column is money that is provably gone or provably idle, traceable to their "
            "own records. The modelled column is what consolidation might return, gross, before what it "
            "costs to replace anything. They are never added together — a blended headline is the "
            "number that collapses under the first real question."),
    }


def main():
    ap = argparse.ArgumentParser(description="Tear down a business's whole stack spend.")
    ap.add_argument("--inventory")
    ap.add_argument("--example", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.example:
        print(json.dumps(EXAMPLE, indent=2)); return 0
    if not a.inventory:
        ap.print_help(); return 1
    with open(a.inventory) as f:
        inv = json.load(f)
    if not inv.get("items"):
        print("refused: no line items — a teardown with nothing torn down is a sales deck",
              file=sys.stderr)
        return 2

    r = analyse(inv)
    if a.json:
        print(json.dumps(r, indent=2)); return 0

    print(f"Spend teardown — {r['business']} · {r['generated']}\n")
    print(f"  Stack on the books: {r['itemCount']} line items, "
          f"${r['annualStackSpend']:,.0f}/yr\n")

    e = r["evidenced"]
    print(f"  EVIDENCED CASH — ${e['foundMoney']:,.2f} · money that provably left")
    for f in e["findings"]:
        print(f"    ${f['amount']:>10,.2f}  {f['what']}")
        print(f"                  evidence: {f.get('evidence') or 'NONE GIVEN'}")
    print()
    print(f"  EVIDENCED IDLE — ${e['idleSeatSpend']:,.2f}/yr · spend against nothing")
    for x in e["idle"]:
        print(f"    ${x['annualIdle']:>10,.2f}  {x['name']} — {x['idleSeats']} idle seat(s) "
              f"@ ${x['perSeat']:,.2f}/yr")
    print(f"    {e['idleCaveat']}")
    print()

    m = r["modelled"]
    print(f"  MODELLED — gross line items, not net savings")
    for x in m["overlaps"]:
        print(f"    ${x['annual']:>10,.0f}  {x['name']} duplicates {x['with']}")
    for x in m["replaceable"]:
        u = f" · {x['utilisationPct']}% of it used" if x["utilisationPct"] is not None else ""
        print(f"    ${x['annual']:>10,.0f}  {x['name']} ({x['category']}){u}")
    print(f"    {m['note']}\n")

    if r["governance"]["shadowAI"]:
        print("  GOVERNANCE")
        for s in r["governance"]["shadowAI"]:
            print(f"    ! {s['name']} — {s['risk']}")
        print()

    print("  LEFT ALONE (out of the replaceable tier by rule)")
    for x in r["outOfScope"]:
        print(f"    · {x['name']} ({x['category']}) — {x['why']}")
    for w in r["warnings"]:
        print(f"\n  WARNING: {w}")
    print(f"\n  {r['honesty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
