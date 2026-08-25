#!/usr/bin/env python3
"""Property OS — the money domain.

Rent charges, payments, the delinquency ladder, the trust ledger, owner
statements, and disbursement batches.

THE LINE THIS MODULE NEVER CROSSES
----------------------------------
This software ACCOUNTS for money. It never MOVES money.

It posts charges derived from signed leases, records payments a human tells it
about, keeps a double-entry trust ledger, drafts disbursement batches, and
generates statements. Executing a transfer — ACH, wire, check — is permanently
R0 in the autonomy matrix: a human performs it at the bank and then records
here that they did. There is no payment-processor integration and none should
be added without counsel; likewise the trust ledger is BOOKKEEPING SOFTWARE,
not a compliance program — state trust-account rules (e.g. NCREC's for ST
property managers) bind the operator, and a counsel/CPA review gates any use
with real funds. Both warnings are load-bearing, not decorative.

THE LEDGER
----------
Double-entry, append-only. Accounts:

  trust_cash                 asset      the pooled trust bank account
  operating_cash             asset      yourco/manager operating account
  owner:<owner_id>           liability  what the trust owes each owner
  deposits:<tenant_id>       liability  each resident's security deposit
  fees_earned                income     management fees (offsets the transfer
                                        of fee cash out of trust)

Every transaction balances: sum(debits) == sum(credits). The reconciliation
invariant — trust_cash == sum(owner liabilities) + sum(deposit liabilities) —
is CHECKED, never assumed, and a breach is reported loudly rather than
papered over. An owner sub-ledger may never be driven negative by a draft
this module produces.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import by_id, iso, load, log_event, nid, now, parse, save, store_lock

GRACE_DAYS = 5          # rent due on the 1st; late fee/reminder territory after this
REMIND_AT = 5           # first (templated, R2) reminder
NOTICE_AT = 10          # firm-notice DRAFT (R1 — a human sends it)
PLAN_AT = 20            # payment-plan proposal (R1)
REFERRAL_AT = 45        # legal referral (R0 — drafted, never sent, forever)
MGMT_FEE_PCT = 0.08     # per-owner override via owner["mgmt_fee_pct"]
INVOICE_TOLERANCE = 0.10  # invoice within 10% of the approved quote auto-matches


# ---------------------------------------------------------------- the ledger

def post(entries, memo, actor, kind, subject=None, at=None):
    """Append one balanced transaction. entries: [(account, debit, credit)].

    Raises on an unbalanced transaction rather than storing it — a ledger with
    one unbalanced row in it is not a ledger, and no caller has a legitimate
    reason to write one.
    """
    d = round(sum(e[1] for e in entries), 2)
    c = round(sum(e[2] for e in entries), 2)
    if abs(d - c) > 0.005:
        raise ValueError(f"unbalanced transaction: debits {d} != credits {c} ({memo})")
    txn = {"id": nid("txn"), "at": at or iso(), "memo": memo, "actor": actor,
           "kind": kind, "subject": subject,
           "entries": [{"account": a, "debit": dr, "credit": cr}
                       for a, dr, cr in entries]}
    with store_lock():
        rows = load("ledger")
        rows.append(txn)
        save("ledger", rows)
    return txn


def balances(ledger=None):
    """Account balances. Assets carry debit-normal balance, liabilities and
    income credit-normal — returned as positive numbers in their own sign
    convention so a reader never has to remember which side is which.
    """
    bal = {}
    for t in (ledger if ledger is not None else load("ledger")):
        for e in t["entries"]:
            bal[e["account"]] = bal.get(e["account"], 0) + e["debit"] - e["credit"]
    out = {}
    for acct, v in bal.items():
        if acct in ("trust_cash", "operating_cash"):
            out[acct] = round(v, 2)                 # debit-normal
        else:
            out[acct] = round(-v, 2)                # credit-normal
    return out


def reconcile(ledger=None):
    """The invariant that defines a trust account: the cash equals what is
    owed out of it. Reported, never assumed."""
    b = balances(ledger)
    trust = b.get("trust_cash", 0)
    owed = round(sum(v for a, v in b.items()
                     if a.startswith("owner:") or a.startswith("deposits:")), 2)
    ok = abs(trust - owed) < 0.01
    negatives = {a: v for a, v in b.items()
                 if (a.startswith("owner:") or a.startswith("deposits:")) and v < -0.005}
    return {"ok": ok and not negatives, "trust_cash": trust, "liabilities": owed,
            "difference": round(trust - owed, 2), "negative_subledgers": negatives,
            "note": None if ok else
            "TRUST OUT OF BALANCE — stop disbursing and reconcile before anything else"}


# ---------------------------------------------------------------- charges

def month_key(dt):
    return dt.strftime("%Y-%m")


def post_rent_charges(months_back=0):
    """Post this month's rent charge for every occupied unit. Idempotent per
    unit-month. Derived directly from the signed lease — that is why it is R3.
    """
    posted = []
    with store_lock():
        charges = load("charges")
        have = {(c["unit_id"], c["month"]) for c in charges}
        target = now() - timedelta(days=30 * months_back)
        mk = month_key(target)
        for u in load("units"):
            if not u.get("tenant_id") or (u["id"], mk) in have:
                continue
            lease = u.get("lease", {})
            start, end = parse(lease.get("start")), parse(lease.get("end"))
            if not start or start > now() or (end and end < target - timedelta(days=31)):
                continue
            c = {"id": nid("chg"), "unit_id": u["id"], "tenant_id": u["tenant_id"],
                 "month": mk, "amount": u["rent"],
                 "due": iso(target.replace(day=1)), "kind": "rent"}
            charges.append(c)
            posted.append(c)
        save("charges", charges)
    for c in posted:
        log_event("charge_posted", c["id"], "agent:collections", "R3",
                  {"unit": c["unit_id"], "month": c["month"], "amount": c["amount"]})
    return posted


def record_payment(tenant_id, amount, method="ach", actor="human:mgr_1",
                   at=None, memo=None):
    """A HUMAN records that money arrived (check logged, bank feed, receipt).
    The recording writes the ledger; nothing here initiated the movement.
    Applies to the oldest unpaid charge first.
    """
    t = by_id("tenants", tenant_id)
    if not t:
        return None
    u = by_id("units", t.get("unit_id")) or {}
    prop = by_id("properties", u.get("property_id")) or {}
    owner_id = prop.get("owner_id", "unknown")
    p = {"id": nid("pay"), "tenant_id": tenant_id, "unit_id": u.get("id"),
         "amount": round(float(amount), 2), "method": method, "at": at or iso(),
         "recorded_by": actor}
    with store_lock():
        rows = load("payments")
        rows.append(p)
        save("payments", rows)
    post([("trust_cash", p["amount"], 0), (f"owner:{owner_id}", 0, p["amount"])],
         memo or f"rent received — {t.get('name')} ({u.get('label')})",
         actor, "rent_received", subject=p["id"], at=p["at"])
    log_event("payment_recorded", p["id"], actor, None,
              {"tenant": t.get("name"), "amount": p["amount"], "method": method})
    return p


def tenant_balance(tenant_id, charges=None, payments=None):
    ch = [c for c in (charges if charges is not None else load("charges"))
          if c["tenant_id"] == tenant_id]
    pay = [p for p in (payments if payments is not None else load("payments"))
           if p["tenant_id"] == tenant_id]
    owed = round(sum(c["amount"] for c in ch) - sum(p["amount"] for p in pay), 2)
    return {"tenant_id": tenant_id, "charged": round(sum(c["amount"] for c in ch), 2),
            "paid": round(sum(p["amount"] for p in pay), 2), "balance": max(0.0, owed),
            "credit": round(-owed, 2) if owed < 0 else 0.0}


def delinquency(charges=None, payments=None):
    """Who is behind, how far, and what the ladder allows next.

    FIFO application: payments retire the oldest charge first, so 'days late'
    is measured on the oldest charge still carrying a balance.
    """
    charges = charges if charges is not None else load("charges")
    payments = payments if payments is not None else load("payments")
    by_tenant = {}
    for c in sorted(charges, key=lambda c: c["due"]):
        by_tenant.setdefault(c["tenant_id"], []).append(c)
    paid = {}
    for p in payments:
        paid[p["tenant_id"]] = paid.get(p["tenant_id"], 0) + p["amount"]
    out = []
    for tid, chs in by_tenant.items():
        remaining = paid.get(tid, 0)
        oldest_due, balance = None, 0.0
        for c in chs:
            applied = min(remaining, c["amount"])
            remaining -= applied
            short = round(c["amount"] - applied, 2)
            if short > 0.005:
                balance = round(balance + short, 2)
                if oldest_due is None:
                    oldest_due = c["due"]
        if balance <= 0.005:
            continue
        days = int((now() - parse(oldest_due)).days) if oldest_due else 0
        stage = ("current" if days <= GRACE_DAYS else
                 "remind" if days < NOTICE_AT else
                 "notice" if days < PLAN_AT else
                 "plan" if days < REFERRAL_AT else "referral")
        t = by_id("tenants", tid) or {}
        u = by_id("units", t.get("unit_id")) or {}
        out.append({"tenant_id": tid, "tenant": t.get("name"),
                    "unit_id": u.get("id"), "unit": u.get("label"),
                    "property_id": u.get("property_id"),
                    "balance": balance, "days_late": days, "stage": stage,
                    "oldest_due": oldest_due})
    out.sort(key=lambda d: -d["days_late"])
    return out


def late_history(tenant_id, months=12, charges=None, payments=None):
    """Late/missed pattern for the renewal-risk model. A payment is late when
    it lands after due + grace; a charge with no covering payment is missed.
    Simplified FIFO attribution — stated, not hidden."""
    cutoff = now() - timedelta(days=30 * months)
    ch = sorted((c for c in (charges if charges is not None else load("charges"))
                 if c["tenant_id"] == tenant_id and (parse(c["due"]) or now()) > cutoff),
                key=lambda c: c["due"])
    pay = sorted((p for p in (payments if payments is not None else load("payments"))
                  if p["tenant_id"] == tenant_id),
                 key=lambda p: p["at"])
    late = missed = 0
    pi, credit = 0, 0.0
    for c in ch:
        need = c["amount"]
        covered_by = None
        while need > 0.005:
            if credit > 0.005:
                take = min(credit, need)
                credit -= take
                need -= take
                continue
            if pi >= len(pay):
                break
            covered_by = pay[pi]
            credit = covered_by["amount"]
            pi += 1
        if need > 0.005:
            missed += 1
        elif covered_by and parse(covered_by["at"]) > parse(c["due"]) + timedelta(days=GRACE_DAYS):
            late += 1
    return {"late": late, "missed": missed, "months": months}


# ---------------------------------------------------------------- deposits

def hold_deposit(tenant_id, amount, actor="human:mgr_1", at=None):
    post([("trust_cash", amount, 0), (f"deposits:{tenant_id}", 0, amount)],
         f"security deposit held — {(by_id('tenants', tenant_id) or {}).get('name')}",
         actor, "deposit_held", subject=tenant_id, at=at)


def deposit_held(tenant_id):
    return balances().get(f"deposits:{tenant_id}", 0.0)


# ---------------------------------------------------------------- invoices

def match_invoice(request, invoice_amount):
    """Invoice against the approved quote. Within tolerance: clean match.
    Beyond it, or with no quote to match: a human reviews. The second half of
    the spend control — we gated the quote and then never saw the bill.
    """
    q = request.get("quote")
    inv = round(float(invoice_amount), 2)
    if not q:
        return {"match": False, "invoice": inv, "quote": None,
                "reason": "no approved quote on file to match against"}
    drift = (inv - q) / q
    return {"match": abs(drift) <= INVOICE_TOLERANCE, "invoice": inv, "quote": q,
            "drift_pct": round(drift * 100, 1),
            "reason": (None if abs(drift) <= INVOICE_TOLERANCE else
                       f"invoice is {drift:+.0%} against the approved ${q} quote")}


def record_vendor_invoice_paid(request, actor="human:mgr_1"):
    """Human marks the vendor bill paid out of trust (they paid it; this
    records it). Expense hits the owner's sub-ledger."""
    amt = request.get("invoice_amount") or request.get("actual_cost")
    if not amt:
        return None
    prop = by_id("properties", request.get("property_id")) or {}
    owner_id = prop.get("owner_id", "unknown")
    return post([(f"owner:{owner_id}", amt, 0), ("trust_cash", 0, amt)],
                f"vendor invoice paid — {request.get('title', '')[:40]}",
                actor, "expense_paid", subject=request["id"])


# ---------------------------------------------------------------- statements

def owner_statement(owner_id, month=None):
    """One owner, one month: collected, spent, fee, net, trust position.
    Everything is summed from ledger rows — the statement cannot disagree
    with the ledger because it IS the ledger, grouped."""
    owner = by_id("owners", owner_id)
    if not owner:
        return None
    mk = month or month_key(now())
    txns = [t for t in load("ledger") if t["at"][:7] == mk]
    acct = f"owner:{owner_id}"
    collected = sum(e["credit"] for t in txns if t["kind"] == "rent_received"
                    for e in t["entries"] if e["account"] == acct)
    expenses = sum(e["debit"] for t in txns if t["kind"] == "expense_paid"
                   for e in t["entries"] if e["account"] == acct)
    fees = sum(e["debit"] for t in txns if t["kind"] == "mgmt_fee"
               for e in t["entries"] if e["account"] == acct)
    draws = sum(e["debit"] for t in txns if t["kind"] == "disbursement"
                for e in t["entries"] if e["account"] == acct)
    return {"owner": owner["name"], "owner_id": owner_id, "month": mk,
            "rent_collected": round(collected, 2),
            "maintenance_paid": round(expenses, 2),
            "management_fee": round(fees, 2),
            # NET is the operating result: collected minus costs. Draws are the
            # owner taking their own money OUT — a distribution, not a cost.
            # Subtracting them produced "net -$706,934" on a month where the
            # owner simply caught up on six months of accumulated draws.
            "net": round(collected - expenses - fees, 2),
            "owner_draws": round(draws, 2),
            "trust_delta": round(collected - expenses - fees - draws, 2),
            "trust_balance_now": balances().get(acct, 0.0),
            "basis": "grouped directly from ledger transactions dated in the month — "
                     "the statement cannot disagree with the ledger"}


def take_mgmt_fee(owner_id, month=None, actor="agent:ledger"):
    """Fee on the month's collections, moved trust -> operating. Idempotent
    per owner-month."""
    mk = month or month_key(now())
    for t in load("ledger"):
        if t["kind"] == "mgmt_fee" and t.get("subject") == f"{owner_id}:{mk}":
            return None
    owner = by_id("owners", owner_id) or {}
    pct = owner.get("mgmt_fee_pct", MGMT_FEE_PCT)
    acct = f"owner:{owner_id}"
    collected = sum(e["credit"] for t in load("ledger")
                    if t["kind"] == "rent_received" and t["at"][:7] == mk
                    for e in t["entries"] if e["account"] == acct)
    fee = round(collected * pct, 2)
    if fee < 0.01:
        return None
    return post([(acct, fee, 0), ("trust_cash", 0, fee),
                 ("operating_cash", fee, 0), ("fees_earned", 0, fee)],
                f"management fee {pct:.0%} on ${collected:,.0f} collected — {mk}",
                actor, "mgmt_fee", subject=f"{owner_id}:{mk}")


# ---------------------------------------------------------------- batches

def draft_disbursement_batch(actor="agent:ledger"):
    """Draft the owner-draw batch: each owner's sub-ledger balance above their
    reserve floor. DRAFTING is R2. EXECUTING is a human at a bank — this
    module has no way to move the money and must never grow one.
    """
    b = balances()
    lines = []
    for o in load("owners"):
        bal = b.get(f"owner:{o['id']}", 0.0)
        floor = o.get("reserve_floor", 250 * len(o.get("properties", [])))
        amt = round(bal - floor, 2)
        if amt >= 50:
            lines.append({"owner_id": o["id"], "owner": o["name"], "amount": amt,
                          "reserve_floor": floor, "subledger_balance": bal})
    if not lines:
        return None
    batch = {"id": nid("bat"), "at": iso(), "status": "draft",
             "lines": lines, "total": round(sum(l["amount"] for l in lines), 2),
             "note": "DRAFT ONLY. Nothing in this system can move money. A human "
                     "executes these at the bank, then records execution here."}
    with store_lock():
        rows = load("batches")
        # one live draft at a time — a second draft supersedes, never stacks
        rows = [x for x in rows if x.get("status") != "draft"]
        rows.append(batch)
        save("batches", rows)
    log_event("batch_drafted", batch["id"], actor, "R2",
              {"lines": len(lines), "total": batch["total"]})
    return batch


def execute_batch(batch_id, actor, reference):
    """The human's record that THEY moved the money. Requires a bank reference
    string — 'trust me' is not a reference. Rejects execution that would
    break the trust invariant."""
    with store_lock():
        rows = load("batches")
        batch = next((x for x in rows if x["id"] == batch_id), None)
        if not batch or batch.get("status") != "draft":
            return {"error": "no such draft batch"}
        if not actor.startswith("human:"):
            return {"error": "execution is recorded by a human, never an agent — "
                             "software does not move money here"}
        if not (reference or "").strip():
            return {"error": "a bank reference is required to record execution"}
        b = balances()
        for l in batch["lines"]:
            if b.get(f"owner:{l['owner_id']}", 0) < l["amount"] - 0.01:
                return {"error": f"executing would overdraw owner:{l['owner_id']} — "
                                 "re-draft against current balances"}
        batch["status"] = "executed"
        batch["executed_at"] = iso()
        batch["executed_by"] = actor
        batch["bank_reference"] = reference.strip()
        save("batches", rows)
    for l in batch["lines"]:
        post([(f"owner:{l['owner_id']}", l["amount"], 0),
              ("trust_cash", 0, l["amount"])],
             f"owner disbursement — {l['owner']} (ref {batch['bank_reference']})",
             actor, "disbursement", subject=batch["id"])
    log_event("batch_executed", batch["id"], actor, None,
              {"total": batch["total"], "reference": batch["bank_reference"]})
    return {"batch": batch}
