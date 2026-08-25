#!/usr/bin/env python3
"""yourco — scoped connector writes onto the ONE CRM database (`crm/data.json`).

the Founder's ask for Connector Console v2 was "data flows both ways so both sides update". The answer here
is deliberately NOT a second database that syncs: there is one file, `crm/data.json`, and the console
is a **scoped view with scoped writes** onto it. Both sides are updated by construction — there is no
sync job, no divergence, and no conflict resolution to get wrong.

Three properties every write in this module holds:

1. **Locked + atomic.** Every write goes through `dashboard/melanie.crm_lock()` +
   `melanie._atomic_dump()` + `melanie.write_mirror()` — the same path `runtime/site_intake.py` uses.
   The CRM has several writers; none of them may tear or clobber another.
2. **Scoped.** `can_write()` is the single gate. A connector may write ONLY:
     • their own goal targets,
     • their downline's goal targets (the Founder's explicit ask — an upline helps set goals),
     • connector-authored fields (`note`, `nextAction`) on companies THEY referred.
   Everything else — another connector's anything, a downline member's records or payout data, and
   every yourco-internal field (stage, retainer, owner, margin, cost…) — is REFUSED, and a refusal
   writes nothing at all: no CRM mutation, no activity, no log event.
3. **On the permanent record.** Every accepted write appends an event to the append-only attribution
   log (`crm/_attribution-log.jsonl`) naming the connector who made it — including when an upline
   edits a downline member's goals, where `by` and `connector` differ on purpose.

Both-ways visibility: a connector's note also appends a `Connector note` activity row, which is the
CRM's own feed — so the internal side sees connector-authored updates in the surface David already
reads, without the connector ever writing an internal field.

Usage (library — the Connector Console is the only caller today):
  ok, why = can_write("Alice", {"kind": "goal", "subject": "Dana"})
  connector_writes.set_goal_targets("Alice", "Dana", {"liveClients": 3})
  connector_writes.set_referral_fields("Alice", "c12", {"note": "…", "nextAction": "…"})

Pass `d=<dict>` + `commit=False` to exercise every path against an in-memory fixture without touching
`crm/data.json` or the log (that is how this module is tested).

STAGED: the connector program is counsel- + launch-gated. Nothing here is connector-reachable until
the console is served with real authentication (see `_README.md` §Identity).
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
ROOT = os.path.dirname(HERE)
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
import connector_ladder as ladder                 # rungs, UNLOCKS, the attribution log
from connector_statements import books            # THE book math — never forked


class ScopeError(PermissionError):
    """A write a connector is not permitted to make. Raised BEFORE anything is mutated."""


# ---- what a connector may set on themselves ------------------------------------------
# Goal metrics are deliberately the things the ladder ALREADY measures, so a goal can never be
# self-reported: the current value is computed from the CRM, and only the target is typed.
GOAL_METRICS = {
    "referrals":    {"label": "Referrals made",        "kind": "count"},
    "conversations": {"label": "Real conversations",   "kind": "count"},
    "liveClients":  {"label": "Live referred clients", "kind": "count"},
    "referredMRR":  {"label": "Referred MRR",          "kind": "money"},
}

# The ONLY fields on a referral a connector may author. Both are connector-owned by construction —
# they are stored under `meta.connectorNotes`, never on the deal/company record itself, so a
# connector write can never overwrite an yourco field even if this allowlist were bypassed.
REFERRAL_FIELDS = {
    "note":       {"label": "Your notes",  "max": 2000},
    "nextAction": {"label": "Next action", "max": 300},
}

# Named purely so a refusal can say WHICH internal thing was refused rather than a generic "no".
# (Not load-bearing for safety — the allowlists above are. This is for a legible error message.)
YOURCO_INTERNAL_FIELDS = frozenset({
    "stage", "stageSince", "retainer", "buildFee", "value", "owner", "margin", "cost", "mrr",
    "commission", "rate", "tier", "rung", "unlocks", "teamStatus", "teamRole", "referrer",
    "referredByCompany", "example", "status", "id", "companyId", "nextDate", "useCase",
})

MAX_TARGET = 1_000_000_000  # a target is a number a human types; reject absurd values outright

# ---- Sourcer submissions (v2, `decisions/2026-08-11_connector-program-v2.md`) -----------------
# A submitted contact is a **Sourcer** referral: the connector hands over a name, yourco does the
# outreach. That inversion is why `provenance` and `consent` are REQUIRED rather than nice-to-have —
# yourco becomes the caller, so TCPA / FL FTSA / CAN-SPAM attach to us for every one of these, and
# "where did this contact come from" has to be answerable per row (checklist item 17a).
SUBMISSION_FIELDS = {
    "business":   {"label": "Business name",     "max": 200, "required": True},
    "contact":    {"label": "Owner's name",      "max": 120, "required": True},
    "email":      {"label": "Email",             "max": 200, "required": False},
    "phone":      {"label": "Phone",             "max": 40,  "required": False},
    "provenance": {"label": "How you know them", "max": 500, "required": True},
    "note":       {"label": "Anything useful",   "max": 1000, "required": False},
}
# Tri-state on purpose. "unknown" is a legitimate, common answer for a Sourcer submission and must be
# recordable as itself — collapsing it into "no" would understate the outreach risk, and collapsing it
# into "yes" would overstate consent we do not have.
CONSENT_VALUES = ("yes", "no", "unknown")
# The per-connector monthly submission cap is a BRACKETED OPEN — the Founder's number, not an agent's
# (`referral-program.md` §"The submission bounty"). The mechanism is live and reads
# `meta.connectorSubmissionCap`; with nothing set there is no cap, and `cap_state()` reports that as an
# unset control rather than pretending a default was chosen. Safe pre-launch because nothing is payable.
CAP_META_KEY = "connectorSubmissionCap"


def _norm(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def cap_state(actor, d=None):
    """(cap, used_this_month, remaining_or_None). `cap` is None when the Founder has not set one."""
    d = load(d)
    cap = (d.get("meta") or {}).get(CAP_META_KEY)
    cap = int(cap) if isinstance(cap, (int, float)) and cap > 0 else None
    month = datetime.date.today().strftime("%Y-%m")
    used = sum(1 for r in ((d.get("meta") or {}).get("connectorSubmissions") or [])
               if (r.get("connector") or "") == actor
               and (r.get("submittedAt") or "").startswith(month)
               and (r.get("status") or "") != "rejected")
    return cap, used, (None if cap is None else max(0, cap - used))


def duplicate_of(fields, d=None, exclude_id=None):
    """An existing submission for the same business/email/phone, or None.

    Duplicate submission is THE gaming surface on a per-contact bounty (the same owner sold twice, by
    one connector or by two). Detection is here, not in the console, so every caller gets it.
    """
    d = load(d)
    keys = {("email", _norm(fields.get("email"))), ("phone", _norm(fields.get("phone"))),
            ("business", _norm(fields.get("business")))}
    keys = {(k, v) for k, v in keys if v}
    for r in ((d.get("meta") or {}).get("connectorSubmissions") or []):
        if exclude_id and r.get("id") == exclude_id:
            continue
        if (r.get("status") or "") == "rejected":
            continue
        for k, v in keys:
            if v and _norm(r.get(k)) == v:
                return r
    return None


# ---- period ---------------------------------------------------------------------------
def quarter_of(day=None):
    day = day or datetime.date.today()
    return f"{day.year}-Q{(day.month - 1) // 3 + 1}"


def quarter_bounds(period):
    y, q = int(period[:4]), int(period[-1])
    start = datetime.date(y, 3 * (q - 1) + 1, 1)
    end = datetime.date(y + (q == 4), (3 * q) % 12 + 1, 1) - datetime.timedelta(days=1)
    return start, end


# ---- load / save ------------------------------------------------------------------------
def load(d=None):
    return d if d is not None else json.load(open(CRM))


def _locked_update(apply_fn):
    """Read-modify-write the live CRM entirely inside the cross-process lock.

    `apply_fn(d)` mutates and returns whatever the caller wants back. Load happens INSIDE the lock
    so a concurrent writer's committed change can never be read stale and written back over.
    """
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import melanie
    with melanie.crm_lock():
        d = json.load(open(CRM))
        out = apply_fn(d)
        d.setdefault("meta", {})["updated"] = datetime.date.today().isoformat()
        melanie._atomic_dump(CRM, d)
        melanie.write_mirror(d)
    return out


# ---- scope ------------------------------------------------------------------------------
def connectors_state(d):
    return ladder.compute(d)


def downline_of(actor, d):
    """The actor's full downline, uncapped depth, cycle-guarded — `books()`' own function."""
    _c, _cr, downline = books(d)
    return downline(actor)


def own_company_ids(actor, d):
    connectors, _cr, _dl = books(d)
    book = connectors.get(actor, {"active": [], "inactive": []})
    return {r["companyId"] for r in book["active"] + book["inactive"]}


def can_write(actor, target, d=None):
    """The single gate. Returns (allowed: bool, reason: str). Pure — inspects, never mutates.

    `target` is a dict describing the intended write:
      {"kind": "goal",     "subject": <connector name>, "fields": {metric: value, …}}
      {"kind": "referral", "companyId": <id>,           "fields": {field: value, …}}
    """
    d = load(d)
    state = connectors_state(d)
    actor = (actor or "").strip()
    if actor not in state:
        return False, f"{actor or 'You'} is not a connector in yourco's records — nothing is writable."

    kind = (target or {}).get("kind")
    fields = (target or {}).get("fields") or {}

    if kind == "goal":
        subject = (target.get("subject") or "").strip()
        if subject not in state:
            return False, f"{subject or 'That person'} is not a connector — no goals to set."
        if subject != actor and subject not in downline_of(actor, d):
            return False, (f"{subject} is not in your downline. You can set your own goals and the "
                           f"goals of connectors you recruited — nobody else's.")
        bad = [k for k in fields if k not in GOAL_METRICS]
        if bad:
            return False, (f"Not a goal metric: {', '.join(sorted(bad))}. Goals are set on what "
                           f"yourco already measures: {', '.join(GOAL_METRICS)}.")
        for k, v in fields.items():
            if v is None:
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                return False, f"{GOAL_METRICS[k]['label']}: a target must be a number."
            if v < 0 or v > MAX_TARGET:
                return False, f"{GOAL_METRICS[k]['label']}: that target is out of range."
        return True, ""

    if kind == "referral":
        cid = target.get("companyId")
        mine = own_company_ids(actor, d)
        if cid not in mine:
            return False, ("That referral is not yours. You can only edit records for businesses "
                           "you referred — not another connector's, and not your downline's.")
        bad = sorted(k for k in fields if k not in REFERRAL_FIELDS)
        if bad:
            internal = [k for k in bad if k in YOURCO_INTERNAL_FIELDS]
            if internal:
                return False, (f"{', '.join(internal)} {'is' if len(internal) == 1 else 'are'} "
                               f"yourco's internal field(s) — read-only to you. Stage, retainer, and "
                               f"ownership are set by yourco from its own records, which is exactly "
                               f"why the numbers on your page can be trusted.")
            return False, f"Not an editable field: {', '.join(bad)}."
        for k, v in fields.items():
            if v is not None and len(str(v)) > REFERRAL_FIELDS[k]["max"]:
                return False, f"{REFERRAL_FIELDS[k]['label']}: too long (max {REFERRAL_FIELDS[k]['max']} characters)."
        return True, ""

    if kind == "submission":
        # Gated on the ladder, like every other capability — never on a rung number written here.
        # `can_for` asks UNLOCKS about the rung they HOLD (evidence ∧ training), not the one they earned.
        if not ladder.can_for(state.get(actor), "submit_contacts"):
            return False, ("Submitting contacts is not open to you yet. It unlocks at R0 — if you are "
                           "seeing this, your onboarding is not finished.")
        bad = sorted(k for k in fields if k not in SUBMISSION_FIELDS and k != "consent")
        if bad:
            return False, f"Not a submission field: {', '.join(bad)}."
        for k, spec in SUBMISSION_FIELDS.items():
            v = (fields.get(k) or "").strip()
            if spec["required"] and not v:
                return False, (f"{spec['label']} is required. "
                               + ("yourco makes this call, so we have to be able to say where the "
                                  "contact came from — a submission without it cannot be verified."
                                  if k == "provenance" else "")).strip()
            if len(v) > spec["max"]:
                return False, f"{spec['label']}: too long (max {spec['max']} characters)."
        if not ((fields.get("email") or "").strip() or (fields.get("phone") or "").strip()):
            return False, "A submission needs an email or a phone number — otherwise nobody can reach them."
        if (fields.get("consent") or "unknown").strip() not in CONSENT_VALUES:
            return False, f"Consent must be one of: {', '.join(CONSENT_VALUES)}."
        dup = duplicate_of(fields, d)
        if dup:
            same = (dup.get("connector") or "") == actor
            return False, (("You already submitted this contact on "
                            f"{(dup.get('submittedAt') or '')[:10]}.") if same else
                           ("This business is already in yourco's records from an earlier submission. "
                            "One referrer per company, ever — first logged touch wins "
                            "(referral-program.md §Attribution rules)."))
        cap, used, left = cap_state(actor, d)
        if cap is not None and left <= 0:
            return False, f"You've submitted {used} contacts this month, which is the cap ({cap})."
        return True, ""

    return False, ("Not something the console can write. A connector may set goals (their own and "
                   "their downline's), add notes to their own referrals, and submit contacts — "
                   "nothing else.")


def _require(actor, target, d):
    ok, why = can_write(actor, target, d)
    if not ok:
        raise ScopeError(why)


# ---- the writes -------------------------------------------------------------------------
def set_goal_targets(actor, subject, targets, period=None, d=None, commit=True, log=None):
    """Set/clear goal targets for `subject` (self or downline). Returns the stored goal record.

    A value of None clears that target. Refusal raises ScopeError and writes NOTHING.
    """
    # Scope is checked FIRST, against the data the caller gave us (fixture) or the live CRM.
    # A refusal raises here — before the lock is taken and before anything is mutated.
    _require(actor, {"kind": "goal", "subject": subject, "fields": targets}, load(d))
    period = period or quarter_of()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    box = {}

    def apply(dd):
        goals = dd.setdefault("meta", {}).setdefault("connectorGoals", {})
        rec = goals.setdefault(subject, {}).setdefault(period, {"targets": {}})
        before = dict(rec.get("targets") or {})
        for k, v in targets.items():
            if v is None:
                rec["targets"].pop(k, None)
            else:
                rec["targets"][k] = float(v) if GOAL_METRICS[k]["kind"] == "money" else int(float(v))
        rec["updated"] = now
        rec["updatedBy"] = actor
        box["changed"] = {k: rec["targets"].get(k) for k in targets
                          if before.get(k) != rec["targets"].get(k)}
        return rec

    rec = _locked_update(apply) if (commit and d is None) else apply(load(d))
    changed = box["changed"]
    if changed:
        emit = log if log is not None else ladder.log_event
        emit("goal.set", connector=subject, by=actor,
             onBehalf=(actor != subject), period=period, targets=changed,
             note=(f"Goal targets set by {actor}" + (" (upline)" if actor != subject else "")))
    return rec


def set_referral_fields(actor, company_id, fields, d=None, commit=True, log=None):
    """Set connector-authored fields on one of the actor's OWN referrals.

    Stored under `meta.connectorNotes[<companyId>]` — namespaced, so no yourco field on the company
    or deal record is ever touched. A changed note also appends a `Connector note` activity so the
    update surfaces in the CRM's own feed (this is the "both ways" in one database, not a sync).
    Refusal raises ScopeError and writes NOTHING.
    """
    _require(actor, {"kind": "referral", "companyId": company_id, "fields": fields}, load(d))
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    box = {}

    def apply(dd):
        notes = dd.setdefault("meta", {}).setdefault("connectorNotes", {})
        rec = notes.setdefault(str(company_id), {})
        before = {k: rec.get(k) for k in fields}
        for k, v in fields.items():
            val = (str(v).strip() or None) if v is not None else None
            if val is None:
                rec.pop(k, None)
            else:
                rec[k] = val
        rec["by"] = actor
        rec["updated"] = now
        changed = {k: rec.get(k) for k in fields if before.get(k) != rec.get(k)}
        by_id = {c["id"]: c for c in dd.get("companies", [])}
        cname = (by_id.get(company_id) or {}).get("name") or str(company_id)
        if changed:  # the "both ways": the connector's update lands in the CRM's own activity feed
            dd.setdefault("activities", []).append(
                # "Connector note" verbatim — it is a registered type in `meta.activityTypes`, and the
                # Activity tab builds its filter FROM the data, so an unregistered spelling would
                # appear as a stray one-off option rather than the type it is.
                {"date": today, "type": "Connector note", "companyId": company_id, "who": actor,
                 "summary": f"Connector note from {actor} on {cname}: {(rec.get('note') or '—')[:300]}",
                 "nextAction": rec.get("nextAction") or ""})
        box.update(changed=changed, company=cname)
        return rec

    rec = _locked_update(apply) if (commit and d is None) else apply(load(d))
    changed = box["changed"]
    if changed:
        emit = log if log is not None else ladder.log_event
        emit("referral.noted", connector=actor, by=actor, company=box["company"],
             fields=sorted(changed), note=(rec.get("note") or "")[:300])
    return rec


def submit_contact(actor, fields, d=None, commit=True, log=None):
    """A connector submits a sourced contact (Sourcer mode). Returns the stored submission record.

    Lands at `meta.connectorSubmissions` in state `pending` — NOT as a CRM company. It becomes a
    company only if yourco verifies it and works it, because a company row nobody has verified is a
    pipeline that cannot be called. Refusal raises ScopeError and writes NOTHING.
    """
    fields = {k: (str(v).strip() if v is not None else "") for k, v in (fields or {}).items()}
    _require(actor, {"kind": "submission", "fields": fields}, load(d))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rec = {"id": f"sub-{now.replace(':', '').replace('-', '')}-{_norm(fields.get('business'))[:12]}",
           "connector": actor, "mode": "sourcer", "status": "pending",
           "submittedAt": now, "consent": (fields.get("consent") or "unknown"),
           **{k: fields.get(k, "") for k in SUBMISSION_FIELDS}}

    def apply(dd):
        dd.setdefault("meta", {}).setdefault("connectorSubmissions", []).append(rec)
        return rec

    out = _locked_update(apply) if (commit and d is None) else apply(load(d))
    emit = log if log is not None else ladder.log_event
    emit("submission.received", connector=actor, by=actor, submissionId=rec["id"],
         business=rec["business"], consent=rec["consent"], mode="sourcer",
         note=f"Sourced contact submitted by {actor}: {rec['business']} — awaiting verification")
    return out


def verify_submission(operator, submission_id, status, d=None, commit=True, log=None, reason=""):
    """An OPERATOR verifies (or rejects) a submission. This is what makes the first bounty step real.

    Never something a connector can do for their own submission — the bounty pays on this transition,
    so self-verification would be self-payment. The 24–48h SLA on this queue is a promise made to
    someone waiting to be paid (`decisions/2026-08-11_connector-program-v2.md`, obligation 4).
    """
    from connector_statements import SUBMISSION_STATES
    operator = (operator or "").strip()
    if not operator:
        raise ScopeError("Verification must name the operator doing it — the record is the point.")
    if status not in SUBMISSION_STATES:
        raise ScopeError(f"Status must be one of: {', '.join(SUBMISSION_STATES)}.")
    d0 = load(d)
    rows = ((d0.get("meta") or {}).get("connectorSubmissions") or [])
    cur = next((r for r in rows if r.get("id") == submission_id), None)
    if not cur:
        raise ScopeError("No such submission.")
    if (cur.get("connector") or "") == operator:
        raise ScopeError("A connector cannot verify their own submission — the bounty pays on this step.")
    if cur.get("status") == status:
        return cur                                         # idempotent, no second log entry
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    box = {}

    def apply(dd):
        for r in dd.setdefault("meta", {}).setdefault("connectorSubmissions", []):
            if r.get("id") != submission_id:
                continue
            box["before"] = r.get("status")
            r["status"] = status
            r["verifiedAt"] = now
            r["verifiedBy"] = operator
            if reason:
                r["reason"] = reason
            return r
        return None

    out = _locked_update(apply) if (commit and d is None) else apply(load(d))
    emit = log if log is not None else ladder.log_event
    emit("submission.verified", connector=cur.get("connector"), by=operator,
         submissionId=submission_id, business=cur.get("business"),
         status=status, previous=box.get("before"), reason=reason or None,
         note=f"Submission {status} by {operator}" + (f" — {reason}" if reason else ""))
    return out


def promote_submission(operator, submission_id, company_id=None, d=None, commit=True, log=None):
    """Turn a verified submission into a real CRM company — and stamp the referral as **Sourcer**.

    This is the join that was missing. `meta.referralMode` was read by the console and written by
    nothing, so every real referral rendered as *"Your introduction"* even when yourco had made the
    approach — the whole Introducer/Sourcer distinction was inert in production
    (`decisions/2026-08-11_connector-program-v2.md`). A submission only ever becomes a company
    HERE, so this is the one place that can know the mode, and it sets it.

    It also does what the promote-* skills do for other lead sources: creates the company, attaches
    the owner as a contact, and tags the referrer so the commission math picks it up. Passing an
    existing `company_id` links to it instead of creating a duplicate.
    """
    operator = (operator or "").strip()
    if not operator:
        raise ScopeError("Promoting a submission must name the operator doing it.")
    d0 = load(d)
    sub = next((r for r in ((d0.get("meta") or {}).get("connectorSubmissions") or [])
                if r.get("id") == submission_id), None)
    if not sub:
        raise ScopeError("No such submission.")
    if (sub.get("status") or "") not in ("verified", "booked", "client"):
        raise ScopeError("Only a verified submission becomes a company — verify it first, or it "
                         "enters the pipeline as something nobody has checked.")
    if sub.get("companyId"):
        raise ScopeError(f"Already promoted to {sub['companyId']}.")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    today = datetime.date.today().isoformat()
    box = {}

    def apply(dd):
        companies = dd.setdefault("companies", [])
        cid = company_id
        if cid:
            co = next((c for c in companies if c.get("id") == cid), None)
            if not co:
                raise ScopeError(f"No company {cid} to link to.")
        else:
            n = max([int(re.sub(r"\D", "", c.get("id") or "0") or 0) for c in companies] or [0]) + 1
            cid = f"c{n}"
            co = {"id": cid, "name": sub.get("business") or "Unnamed", "status": "prospect",
                  "source": "connector submission", "createdAt": today,
                  "createdAtSource": "promoted from a connector submission"}
            companies.append(co)
        # The referrer tag is what `books()` reads to compute commission — without it the connector
        # would have handed us a client and earned nothing.
        co["referrer"] = sub.get("connector")
        dd.setdefault("meta", {}).setdefault("referralMode", {})[str(cid)] = "sourcer"

        contacts = dd.setdefault("contacts", [])
        if (sub.get("contact") or "").strip() and not any(
                p.get("companyId") == cid and (p.get("name") or "").strip().lower()
                == sub["contact"].strip().lower() for p in contacts):
            pn = max([int(re.sub(r"\D", "", p.get("id") or "0") or 0) for p in contacts] or [0]) + 1
            contacts.append({"id": f"p{pn}", "companyId": cid, "name": sub["contact"].strip(),
                             "email": sub.get("email") or "", "phone": sub.get("phone") or "",
                             "role": "Owner", "status": "active",
                             "sourcedBy": sub.get("connector"),
                             "relationship": sub.get("provenance") or "", "lastTouch": today})
        for r in dd["meta"]["connectorSubmissions"]:
            if r.get("id") == submission_id:
                r["companyId"] = cid
                r["promotedAt"] = now
                r["promotedBy"] = operator
        box["cid"] = cid
        box["name"] = co["name"]
        return co

    out = _locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("submission.promoted", connector=sub.get("connector"), by=operator,
         submissionId=submission_id, company=box.get("name"), companyId=box.get("cid"),
         mode="sourcer",
         note=f"{box.get('name')} entered the CRM from {sub.get('connector')}'s submission — "
              f"tagged Sourcer, so the console will say yourco made the approach")
    return out


def pending_submissions(d=None):
    """The operator's verification queue, oldest first — the 24–48h SLA is measured against this."""
    d = load(d)
    rows = [r for r in ((d.get("meta") or {}).get("connectorSubmissions") or [])
            if (r.get("status") or "pending") == "pending"]
    return sorted(rows, key=lambda r: r.get("submittedAt") or "")


# ---- read helpers the console uses (kept next to the writes they mirror) -----------------
def goals_for(name, d=None, period=None):
    d = load(d)
    period = period or quarter_of()
    return ((d.get("meta") or {}).get("connectorGoals") or {}).get(name, {}).get(period, {"targets": {}})


def notes_for(company_id, d=None):
    d = load(d)
    return ((d.get("meta") or {}).get("connectorNotes") or {}).get(str(company_id), {})


if __name__ == "__main__":
    # A refusal matrix against the LIVE CRM, read-only — no argument writes anything.
    d = load()
    state = connectors_state(d)
    names = sorted(state)
    print(f"# connector_writes — scope check against the live CRM ({len(names)} connector contacts)\n")
    actor = names[0] if names else None
    if not actor:
        print("No connector contacts — nothing to check.")
        sys.exit(0)
    other = names[1] if len(names) > 1 else actor
    probes = [
        ("own goal", actor, {"kind": "goal", "subject": actor, "fields": {"liveClients": 3}}),
        ("someone else's goal", actor, {"kind": "goal", "subject": other, "fields": {"liveClients": 3}}),
        ("made-up metric", actor, {"kind": "goal", "subject": actor, "fields": {"commission": 9}}),
        ("a company they did not refer", actor, {"kind": "referral", "companyId": "c1", "fields": {"note": "x"}}),
        ("an yourco field", actor, {"kind": "referral", "companyId": "c1", "fields": {"retainer": 1}}),
        ("an unknown write kind", actor, {"kind": "payout", "fields": {}}),
        ("a submission, complete", actor, {"kind": "submission", "fields": {
            "business": "Northside Dental", "contact": "Dana Reyes", "phone": "555-0100",
            "provenance": "my dentist for six years", "consent": "yes"}}),
        ("a submission with no provenance", actor, {"kind": "submission", "fields": {
            "business": "Northside Dental", "contact": "Dana Reyes", "phone": "555-0100"}}),
        ("a submission nobody can reach", actor, {"kind": "submission", "fields": {
            "business": "Northside Dental", "contact": "Dana Reyes",
            "provenance": "my dentist"}}),
    ]
    for label, who, t in probes:
        ok, why = can_write(who, t, d)
        print(f"  {'ALLOW ' if ok else 'REFUSE'}  {label:<32} {why}")
    print("\n(read-only — this entrypoint never writes)")
