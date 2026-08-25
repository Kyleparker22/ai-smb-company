#!/usr/bin/env python3
"""yourco — connector monthly statements (Charles, monthly close; anyone, on demand).

Renders one transparent statement per connector from crm/data.json — actives, tier, rate, per-client
commission, next-tier nudge — plus a client-credit section (Type 1, $100/mo per active referred
client). Visible fairness is the point: a connector who can see exactly how their number is computed
never opens a dispute (referral-program.md §Attribution rules).

Semantics mirror the CRM Referrals view:
  • Type 2 (connector): company.referrer names the connector (free text/code). "Active" = the
    company has a deal with stage "live"; commission = tier rate × sum of active retainers.
  • Tier: meta.referralTiers {rates:[10,12.5,15], thresholds:[6,11]} — <6 actives → rates[0],
    <11 → rates[1], else rates[2].
  • Downline override (counsel-gated — rendered as INFORMATIONAL until Ray clears it):
    meta.repRecruiters maps connector → recruiter; override% × active MRR of the full downline.
  • Type 1 (client refers client): company.referredByCompany → the referring client's credit,
    $100/mo per active referred client. (A legacy free-text referrer naming a live client also
    counts as Type 1, per the Referrals view.)

Usage:
  python3 crm/connector_statements.py            # print all statements (dry, nothing written)
  python3 crm/connector_statements.py --write    # write crm/statements/YYYY-MM/<connector>.md + index
Read-only against the CRM; never modifies data.json.
"""
import os, sys, json, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
# CLIENT_CREDIT is RETIRED (2026-08-13) — one rate card; see books() above.

# ---- the submission bounty (v2, `decisions/2026-08-11_connector-program-v2.md`) ---------
# A Sourcer submission pays in two steps, on top of any commission it later earns. Both are
# NON-REVENUE events — yourco pays before a dollar is collected — which is precisely why the
# combination of this, recruiting at R1, and uncapped override depth is counsel checklist item 4c.
# These constants are THE amounts; no surface may restate them (change-one-sweep-all).
BOUNTY_VERIFIED = 25    # contact submitted and verified as a real, reachable business owner
BOUNTY_BOOKED = 25      # that contact books a real conversation (the ladder's own R1 evidence)
# Nothing accrued here is payable until the program launches AND counsel clears §A/§B — the same
# posture the downline override already carries. `bounties()` computes; it never authorises payment.
BOUNTY_PAYABLE = False
SUBMISSION_STATES = ("pending", "verified", "rejected", "booked", "client")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "unknown"


# ---- the tier basis (changed 2026-08-13, `decisions/2026-08-13_connector-console-v3.md`) ------
# Tiers used to band on **active client COUNT** (1–5 / 6–10 / 11+). That is only sane when deal
# sizes are tight, and yourco's are not: the retainer band runs $3k → $10k+, a 3.3× spread. Under
# count-banding a connector with 3 × $10,000 clients ($30k of referred revenue) sat at 10% while a
# connector with 6 × $1,000 clients ($6k) earned 12.5% — the bigger producer paid a lower rate, and
# the program quietly rewarded referring the SMALLEST businesses it could find.
#
# Tiers now band on **live referred MRR**, at round Core-floor multiples: $15,000 is 5 × $3,000 and
# $30,000 is 10 × $3,000 (the Founder set the upper band to $30,000 on 2026-08-13).
#
# ⚠️ These are NOT identical to the old count thresholds, and an earlier comment here wrongly said
# they were. The count rule was tier 2 at **6** actives and tier 3 at **11**, i.e. $18,000 and
# $33,000 of Core-floor revenue. The MRR bands are one client looser at each end: an all-Core book
# now reaches 12.5% at 5 clients instead of 6, and 15% at 10 instead of 11. That is a small, real,
# deliberate comp change in the connector's favour — not a like-for-like restatement. The change the
# basis exists to make is still the important one: a connector with 3 × $10,000 clients out-earns one
# with 6 × $1,000 clients, which the count rule had backwards.
#
# `MRR_THRESHOLDS` is the default; `meta.referralTiers.mrrThresholds` overrides. A CRM still carrying
# only the old count `thresholds` is read in COUNT mode — see `_tier_basis()` — so no existing data
# silently re-tiers itself under a rule it was never scored against.
MRR_THRESHOLDS = [15_000, 30_000]
CORE_FLOOR = 3_000          # what a client-equivalent is quoted against on the console


def _tier_basis(tiers):
    """'mrr' (the default) or 'count' (legacy). Explicit, because it changes what a rate means."""
    return "count" if (tiers or {}).get("basis") == "count" else "mrr"


def _tier(n, tiers):
    """Tier + rate. `n` is live referred MRR under the 'mrr' basis, active client count under 'count'.

    Kept as one function on purpose: every surface that prices a book calls THIS, so the basis can
    never be right in the statement and wrong in the console.
    """
    rates = (tiers or {}).get("rates", [10, 12.5, 15])
    if _tier_basis(tiers) == "count":
        lo, hi = ((tiers or {}).get("thresholds") or [6, 11])[:2]
    else:
        lo, hi = ((tiers or {}).get("mrrThresholds") or MRR_THRESHOLDS)[:2]
    if n >= hi: return 3, rates[2]
    if n >= lo: return 2, rates[1]
    return 1, rates[0]


def tier_input(book, tiers):
    """The number `_tier` should be asked about for this book. One place, so callers cannot differ."""
    active = book.get("active") or []
    return (len(active) if _tier_basis(tiers) == "count"
            else sum(a.get("mrr") or 0 for a in active))


def tier_progress_note(book, tiers):
    """'$4,000/mo → 12.5%' plus the client-equivalent gloss. A threshold nobody can act on is noise.

    Returns (next_rate, gap_text) or (None, 'top tier'). The client-equivalent is quoted against the
    connector's OWN average retainer when they have one, and against the Core floor when they don't —
    stated either way, because "≈3 more clients" means nothing if you can't tell which average it used.
    """
    active = book.get("active") or []
    rates = (tiers or {}).get("rates", [10, 12.5, 15])
    basis = _tier_basis(tiers)
    cur = tier_input(book, tiers)
    lo, hi = (((tiers or {}).get("thresholds") or [6, 11])[:2] if basis == "count"
              else ((tiers or {}).get("mrrThresholds") or MRR_THRESHOLDS)[:2])
    target, nxt = ((lo, rates[1]) if cur < lo else (hi, rates[2]) if cur < hi else (None, None))
    if target is None:
        return None, "top tier"
    gap = target - cur
    if basis == "count":
        return nxt, f"{gap} more active client{'s' if gap != 1 else ''}"
    avg = (sum(a.get("mrr") or 0 for a in active) / len(active)) if active else 0
    ref = avg if avg > 0 else CORE_FLOOR
    n_eq = max(1, round(gap / ref)) if ref else 0
    basis_word = "your average" if avg > 0 else f"a ${CORE_FLOOR:,.0f} client"
    return nxt, f"${gap:,.0f}/mo more (≈{n_eq} more client{'s' if n_eq != 1 else ''} at {basis_word})"


def books(d):
    """THE per-connector book computation — one source of truth.

    Returns (connectors, client_credits, downline_fn). `connectors` maps connector name ->
    {"active": [{company, companyId, mrr, stage}], "inactive": [...same...]}. Extracted from build()
    2026-08-07 so connector_ladder.py (rungs) and the Connector Console read the SAME math the
    statements and the CRM Referrals cockpit use — never a fork (connector-os.md §2).
    """
    tiers = (d.get("meta") or {}).get("referralTiers") or {}
    recruiters = (d.get("meta") or {}).get("repRecruiters") or {}
    deals = d.get("deals", [])
    # "active" = a company with at least one live deal. `expand` was retired as a stage
    # 2026-08-13 — an expansion is now a SECOND DEAL on the same company that reaches Live in
    # its own right. So this can no longer be a dict keyed by companyId: that silently kept
    # only the last deal and would under-report a client who expanded, which is precisely the
    # client a connector should earn most on. Key -> the SUM of that company's live retainers.
    live_mrr = {}
    for x in deals:
        if x.get("stage") == "live":
            cid = x.get("companyId")
            live_mrr[cid] = live_mrr.get(cid, 0.0) + float(x.get("retainer") or 0)
    live = {cid: {"retainer": m} for cid, m in live_mrr.items()}
    any_deal = {x.get("companyId"): x for x in deals}
    by_id = {c["id"]: c for c in d.get("companies", [])}
    live_client_names = {(by_id[cid].get("name") or "").strip().lower() for cid in live if cid in by_id}

    # ONE RATE CARD since 2026-08-13 (`decisions/2026-08-13_one-referral-rate-card.md`).
    # A referring CLIENT used to be routed out of the connector book entirely and paid a flat
    # $100/mo credit; now they earn the same escalator as anyone else. So they stay IN the book,
    # and `is_client` records only how they get paid: credit against their own bill first, cash
    # above it. `client_credits` is kept as a returned name -> [referred companies] index for
    # callers that want the client-referrer subset — it no longer carries a rate.
    connectors, client_credits = {}, {}
    for c in d.get("companies", []):
        ref = (c.get("referrer") or "").strip()
        # Both link styles resolve to one referrer NAME so the keying is uniform, exactly as
        # buildRepPayouts() does in the CRM UI. Two engines, one definition.
        if c.get("referredByCompany") and c["referredByCompany"] in by_id:
            ref = (by_id[c["referredByCompany"]].get("name") or "").strip()
        deal = live.get(c["id"])
        if not ref:
            continue
        if ref.strip().lower() == (c.get("name") or "").strip().lower():
            continue                          # self-dealing guard: nobody earns on their own bill
        if ref.lower() in live_client_names and deal:
            client_credits.setdefault(ref, []).append(c["name"])
        e = connectors.setdefault(ref, {"active": [], "inactive": [],
                                        "is_client": ref.lower() in live_client_names})
        od = any_deal.get(c["id"]) or {}
        (e["active"] if deal else e["inactive"]).append(
            {"company": c["name"], "companyId": c["id"],
             "mrr": float(deal.get("retainer") or 0) if deal else 0.0,
             "stage": od.get("stage") or "", "stageSince": od.get("stageSince") or ""})

    # full-downline per connector (override is counsel-gated → informational; depth uncapped by
    # decision 2026-08-07_override-depth-uncapped.md — cycle-guarded)
    def downline(name, seen=None):
        seen = seen if seen is not None else set()
        out = []
        for kid, rec in recruiters.items():
            if rec == name and kid not in seen:
                seen.add(kid)
                out.append(kid)
                out += downline(kid, seen)
        return out

    # what a client-connector pays US today — the ceiling on their credit before cash overflow
    for name, e in connectors.items():
        if not e.get("is_client"):
            e["bill"] = 0.0
            continue
        cid = next((c["id"] for c in d.get("companies", [])
                    if (c.get("name") or "").strip().lower() == name.lower()), None)
        e["bill"] = float((live.get(cid) or {}).get("retainer") or 0) if cid else 0.0

    return connectors, client_credits, downline


def submissions(d, connector=None):
    """Sourced-contact submissions, newest first. One connector's, or everyone's.

    Stored at `meta.connectorSubmissions` as a flat list — deliberately NOT on the companies table:
    a submitted contact is not yet a company, and manufacturing a CRM company row from an unverified
    third-party contact is how a pipeline fills with things nobody can call.
    """
    rows = ((d.get("meta") or {}).get("connectorSubmissions") or [])
    if connector is not None:
        rows = [r for r in rows if (r.get("connector") or "") == connector]
    return sorted(rows, key=lambda r: r.get("submittedAt") or "", reverse=True)


def bounties(d, connector=None):
    """THE bounty ledger — one computation, same as `books()` is for commission. Never forked.

    Returns {connector: {"rows": [...], "verified": n, "booked": n, "earned": $, "pending": n,
                         "rejected": n, "payable": bool}}. `earned` is what the two-step bounty has
    ACCRUED; with BOUNTY_PAYABLE False it is explicitly not a payable balance, and every surface that
    renders it must say so — the console and the statement both do.
    """
    out = {}
    for r in submissions(d, connector):
        who = (r.get("connector") or "").strip()
        if not who:
            continue
        e = out.setdefault(who, {"rows": [], "verified": 0, "booked": 0, "pending": 0,
                                 "rejected": 0, "earned": 0.0, "payable": BOUNTY_PAYABLE})
        st = (r.get("status") or "pending").strip()
        # `booked` and `client` both imply the contact was verified first — the bounty is cumulative,
        # so a contact that went straight to a booked call still earns both steps.
        earned = 0.0
        if st in ("verified", "booked", "client"):
            earned += BOUNTY_VERIFIED
            e["verified"] += 1
        if st in ("booked", "client"):
            earned += BOUNTY_BOOKED
            e["booked"] += 1
        if st == "pending":
            e["pending"] += 1
        if st == "rejected":
            e["rejected"] += 1
        e["earned"] += earned
        e["rows"].append({**r, "earned": earned})
    return out


def build():
    d = json.load(open(CRM))
    tiers = (d.get("meta") or {}).get("referralTiers") or {}
    connectors, client_credits, downline = books(d)
    bounty_book = bounties(d)
    month = datetime.date.today().strftime("%Y-%m")
    stmts = {}
    # A connector may have submissions but no referred companies yet — that is the whole point of the
    # bounty (it pays before a book exists), so they must still get a statement.
    for name in sorted(set(connectors) | set(bounty_book)):
        e = connectors.get(name) or {"active": [], "inactive": []}
        n = len(e["active"])
        book = sum(a["mrr"] for a in e["active"])
        # Tier is asked about `tier_input`, never about a number computed here — the basis lives in
        # one place so the statement and the console can't disagree about what earns a rate.
        tier_n, rate = _tier(tier_input(e, tiers), tiers)
        commission = round(book * rate / 100, 2)
        dl = downline(name)
        dl_mrr = sum(a["mrr"] for k in dl for a in connectors.get(k, {}).get("active", []))
        ov_pct = float(tiers.get("override") or 0)
        _nxt, nudge_txt = tier_progress_note(e, tiers)
        nudge = f"{nudge_txt} → {_nxt}%" if _nxt else nudge_txt
        L = [f"# Connector statement — {name} — {month}", "",
             f"**Tier {tier_n}** · rate **{rate}%** · **${book:,.0f}/mo** live referred revenue across "
             f"**{n}** active client{'s' if n != 1 else ''} · next tier: {nudge}", "",
             "| Referred client | Status | Retainer | Commission |", "|---|---|---:|---:|"]
        for a in sorted(e["active"], key=lambda x: -x["mrr"]):
            L.append(f"| {a['company']} | active | ${a['mrr']:,.0f}/mo | ${a['mrr'] * rate / 100:,.2f} |")
        for a in e["inactive"]:
            L.append(f"| {a['company']} | not yet live | — | — |")
        L += ["", f"**Direct commission: ${commission:,.2f}/mo** (rate × collected retainers; paid 2nd Friday on collected revenue)"]
        b = bounty_book.get(name)
        if b:
            L += ["", f"## Submission bounty (Sourcer referrals)", "",
                  f"{b['verified']} verified contact{'s' if b['verified'] != 1 else ''} × ${BOUNTY_VERIFIED} + "
                  f"{b['booked']} booked call{'s' if b['booked'] != 1 else ''} × ${BOUNTY_BOOKED} = "
                  f"**${b['earned']:,.2f} accrued**"
                  + (f" · {b['pending']} awaiting verification" if b["pending"] else "")
                  + (f" · {b['rejected']} not verified" if b["rejected"] else "")]
            if not b["payable"]:
                L += ["", "⚠️ **ACCRUED, NOT PAYABLE.** The submission bounty is staged with the rest of "
                          "the connector program — nothing is paid until launch and counsel clear "
                          "(`decisions/2026-08-11_connector-program-v2.md`)."]
        if dl:
            L += ["", f"Downline ({len(dl)}: {', '.join(dl)}) MRR ${dl_mrr:,.0f} → override {ov_pct}% = "
                      f"${dl_mrr * ov_pct / 100:,.2f}/mo — **INFORMATIONAL: the downline override is "
                      f"counsel-gated and not payable until cleared** (referral-program.md)."]
        L += ["", "*Computed from the CRM by yourco. Rules: `processes/partnerships/referral-program.md` "
                  "§Attribution rules. Questions → founder@yourco.example.com.*"]
        stmts[_slug(name)] = "\n".join(L) + "\n"

    # No flat rate to print any more — a client-connector's number IS their commission, split
    # into the part that comes off their bill and the part paid in cash.
    credit_lines = []
    for k, v in sorted(client_credits.items()):
        e = connectors.get(k) or {}
        mrr = sum(x["mrr"] for x in e.get("active", []))
        _tn, rate = _tier(tier_input(e, tiers), tiers)
        com = mrr * rate / 100
        bill = float(e.get("bill") or 0)
        cred, cash = min(com, bill), max(0.0, com - bill)
        credit_lines.append(
            f"- **{k}** — {len(v)} active referred client{'s' if len(v) != 1 else ''} · "
            f"{rate}% of ${mrr:,.0f} = ${com:,.2f}/mo → **${cred:,.2f} off their bill**"
            + (f" + **${cash:,.2f} cash** (above their ${bill:,.0f} bill)" if cash > 0.005 else "")
            + f": {', '.join(v)}")
    return month, stmts, credit_lines


def main():
    month, stmts, credits = build()
    write = "--write" in sys.argv
    outdir = os.path.join(HERE, "statements", month)
    index = [f"# Connector statements — {month}", ""]
    if not stmts:
        index.append("No connectors with referred companies in the CRM yet (program pre-launch).")
    for slug, text in stmts.items():
        index.append(f"- [{slug}]({slug}.md)")
        if write:
            os.makedirs(outdir, exist_ok=True)
            open(os.path.join(outdir, f"{slug}.md"), "w").write(text)
        else:
            print(text)
    index += ["", "## Client-connectors (same escalator, taken off their own bill first)"]
    index += credits or ["- none yet"]
    if write:
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "_index.md"), "w").write("\n".join(index) + "\n")
        print(f"Wrote {len(stmts)} statement(s) + index → crm/statements/{month}/")
    else:
        print("\n".join(index))
        print("\n(dry run — add --write to save)")


if __name__ == "__main__":
    main()
