#!/usr/bin/env python3
"""yourco — the connector TRAINING GATE: curriculum state, and the one write that records it.

the Founder's design (2026-08-07): **training gates everything.**

1. A newly onboarded connector at R0 can reach **only the Learnings section** of their console.
   Every other section — referrals, earnings, tier, goals, reporting, upline, history, Resources —
   is locked until they finish **R0 training**.
2. **Every rung has its own training** (R0…R4).
3. Training gates *advancement*: a connector cannot hold rung N+1 until rung N's training is done,
   **in addition to** the CRM evidence the ladder already requires. Evidence alone is no longer enough.
4. A connector **cannot see the next rung's training until they have earned that rung on evidence** —
   and a locked lesson stays *visible as locked* (title + the rung that opens it), never hidden.

Two rungs' worth of vocabulary, and the whole UX hangs on keeping them apart:

  * **evidence rung** — what the CRM says they have produced (`connector_ladder.compute()`'s old number).
  * **training ceiling** — the highest rung whose *prerequisite* training is finished.
  * **held rung** — `min(evidence, ceiling)`. This is the rung that governs `UNLOCKS`, and it is the
    one the console calls "your rung".

So a connector with R2 evidence and only R0 training complete **holds R1**, and their console says so
in those words: *you've earned R2 on evidence — finish R1 training to claim it.* Collapsing the two
numbers into one would delete the only sentence that makes the gate feel fair instead of arbitrary.

**Fail closed.** A rung whose curriculum is missing or empty is `complete: False` — it blocks
advancement past itself and says so. A gate that opens when its content goes missing is not a gate.
(For R0 that means an empty content directory locks every console; the page states plainly that this
is yourco's gap, not the connector's.)

## How completion is recorded — the decision, and its weakness, stated plainly

**The connector marks each lesson complete in their own console.** That is it: self-recorded, one
click, timestamped, appended to the append-only attribution log as `training.completed` with the
connector, the rung, and the lesson. A lesson may carry an `acknowledge:` line in its frontmatter — a
single sentence naming the hard rule it teaches ("I will not quote a price…") — and marking it
complete records *that exact sentence* alongside the timestamp, so the record shows what was attested
to rather than only that a button was pressed.

**The weakness, said out loud: self-marked completion proves exposure, not comprehension.** Somebody
can open a lesson, click, and have learned nothing. This is chosen anyway because the alternatives are
worse today: a graded quiz means inventing right answers for policy that is still in counsel review,
and an operator sign-off means the gate advances at Bird's inbox speed for a program with no live
connectors yet. What this design *does* give is a dated, per-lesson, per-rule record on an immutable
log — which is exactly what a classification or compliance question later asks for ("show me what this
person was told, and when"). If the Founder wants a real comprehension bar before launch, the honest upgrade
is an operator confirmation on **R2+ plus the recruiting lesson** (where money and a downline start), and the log
event already carries a `by` field to hold it. That is a decision, not a code change, so it is not
made here.

## Why this is a separate module from `connector_writes.py`

`can_write()` remains the single gate for the writes it owns (goals · referral notes). Training
completion is a new kind of write with a different scope rule — **only ever your own, only ever a
lesson you can already see** — and no third party (not an upline, not an operator) may record it for
you. It reuses `connector_writes._locked_update`, so there is exactly one locked/atomic/mirrored write
path onto `crm/data.json`; only the allowlist is new. Folding a `kind: "training"` branch into
`can_write()` would be tidier and is the recommended follow-up for that file's owner.

Operator confirmation: a connector's mark on an R2/R3/R4 lesson — **or on any lesson unlocking a
`CONFIRM_CAPS` capability, wherever the ladder puts it** — is a SUBMISSION; it does not count until an
operator confirms it (`--pending` to see the queue, `--confirm "<name>" <slug> --by "<operator>"`). A
connector can never confirm their own, and nothing can be confirmed that was never submitted —
confirmation attests to a conversation, so there must be something to attest to. The capability escape
hatch exists because recruiting moved to R1 on 2026-08-11 and a bare rung threshold would have silently
downgraded it to self-marked (`decisions/2026-08-11_connector-program-v2.md`).

Storage: `meta.connectorTraining[<connector name>][<rung>] = {"lessons": {<slug>: {...}}, "completedAt": …}`
— namespaced under `meta` exactly like `connectorGoals` / `connectorNotes`, so a connector-authored
record can never overwrite an yourco field.

Usage:
  python3 crm/connector_training.py                  # curriculum + every connector's training state
  python3 crm/connector_training.py --curriculum     # the lessons, by rung
  from connector_training import state_for, ceiling_for, mark_lesson, can_mark

STAGED: the connector program is counsel- + launch-gated. Nothing here is connector-reachable until
the console is served with real authentication.
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch (2026-08-07): YOURCO_DATA_ROOT moves DATA only — code stays at HERE.
# See playground/_README.md.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
CRM = os.path.join(DATA_DIR, "data.json")
CONTENT_DIR = os.path.join(ROOT, "processes", "partnerships", "connector-training")
sys.path.insert(0, HERE)
import connector_ladder as ladder                    # RUNGS (the rung order) + the attribution log

META_KEY = "connectorTraining"
# the Founder 2026-08-07: self-marking proves exposure, not comprehension. From R2 up — the rungs where money
# (quoting prices) starts — a connector's mark is a SUBMISSION, and an operator must confirm it before
# it counts. R0/R1 stay self-marked so onboarding isn't inbox-blocked.
CONFIRM_FROM_RUNG = 2
# …but the rule the Founder actually stated was "money and recruiting", and on 2026-08-11 recruiting moved to
# R1 (`decisions/2026-08-11_connector-program-v2.md`). A pure rung threshold would have silently
# self-marked the recruiting lesson — the capability is what carries the stakes, not the rung number it
# happens to sit on. So confirmation is ALSO required for any lesson unlocking one of these, wherever
# the ladder puts it. Add a capability here rather than lowering the threshold and dragging all of R1
# into an operator's inbox.
CONFIRM_CAPS = frozenset({"recruit_connectors"})


def needs_confirmation(lesson, rung=None):
    """Does this lesson need an operator's confirmation, not just the connector's mark?

    `lesson` is a loaded lesson dict (or None, when only the rung is known). True if the rung is at or
    above CONFIRM_FROM_RUNG, or the lesson unlocks a capability in CONFIRM_CAPS.
    """
    rung = rung or (lesson or {}).get("rung") or "R0"
    if RUNG_N.get(rung, 0) >= CONFIRM_FROM_RUNG:
        return True
    return ((lesson or {}).get("unlocks") or "").strip() in CONFIRM_CAPS

RUNG_KEYS = [r["key"] for r in ladder.RUNGS]
RUNG_N = {r["key"]: r["n"] for r in ladder.RUNGS}
MAX_ACK = 400


class ScopeError(PermissionError):
    """A training write a connector may not make. Raised BEFORE anything is mutated."""


# ---- the curriculum (content, never hardcoded here) -----------------------------------
def _frontmatter(text):
    """The same minimal `--- key: value ---` reader the console uses. No YAML dependency."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, text[end + 4:].lstrip("\n")


def load_lessons(content_dir=None):
    """Every lesson file, ordered. A lesson's `rung:` is which rung's TRAINING it belongs to."""
    d = content_dir or CONTENT_DIR
    out = []
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        meta, body = _frontmatter(open(os.path.join(d, fn), encoding="utf-8").read())
        meta.update(slug=fn[:-3], body=body)
        try:
            meta["order"] = int(meta.get("order") or 999)
        except ValueError:
            meta["order"] = 999
        rung = (meta.get("rung") or "R0").strip()
        rung = rung if rung in RUNG_N else "R0"
        # If the lesson names a capability, the rung that GRANTS that capability wins over the rung
        # typed into the frontmatter — `UNLOCKS` stays the single gate and the curriculum cannot
        # drift from it. (The console resolves the same way, so both bucket a lesson identically.)
        cap = (meta.get("unlocks") or "").strip()
        if cap:
            rung = next((k for k, v in ladder.UNLOCKS.items() if cap in v), rung)
        meta["rung"] = rung
        meta["stub"] = (meta.get("status") or "").lower() == "stub"
        out.append(meta)
    out.sort(key=lambda m: (m["order"], m["slug"]))
    return out


def curriculum(content_dir=None):
    """{rung key: [lesson, …]} for every rung on the ladder — including rungs with nothing yet."""
    by_rung = {k: [] for k in RUNG_KEYS}
    for L in load_lessons(content_dir):
        by_rung[L["rung"]].append(L)
    return by_rung


# ---- state ----------------------------------------------------------------------------
def _record(name, d):
    return ((d.get("meta") or {}).get(META_KEY) or {}).get(name, {}) or {}


def state_for(name, d=None, content_dir=None):
    """One connector's training state, per rung. Pure read — computes, never writes.

    Returns:
      {"byRung": {"R0": {rung, rungName, lessons:[…], total, done, complete, completedAt, exists}, …},
       "ceilingN": int,          # highest rung they may HOLD given training
       "ceiling": "R1",
       "blockingRung": "R1",     # the first rung whose training is unfinished (None if all done)
       "rungOrder": [...]}
    """
    d = d if d is not None else json.load(open(CRM))
    rec = _record(name, d)
    cur = curriculum(content_dir)
    by_rung, ceiling, blocking = {}, len(RUNG_KEYS) - 1, None
    for r in ladder.RUNGS:
        key = r["key"]
        lessons = cur.get(key, [])
        marks = (rec.get(key) or {}).get("lessons") or {}
        rows = []
        for L in lessons:
            m = marks.get(L["slug"]) or {}
            marked, confirmed = bool(m.get("at")), bool(m.get("confirmedAt"))
            # R2+, or any lesson unlocking a CONFIRM_CAPS capability: the connector's mark is a
            # submission; an operator's confirmation is what completes it.
            lesson_confirm = needs_confirmation(L, key)
            done = (marked and confirmed) if lesson_confirm else marked
            rows.append({"slug": L["slug"], "title": L.get("title") or L["slug"],
                         "minutes": L.get("minutes"), "stub": L["stub"],
                         "acknowledge": L.get("acknowledge"),
                         "done": done, "doneAt": m.get("at"),
                         "acknowledged": m.get("acknowledged"),
                         "needsConfirmation": lesson_confirm,
                         "status": ("confirmed" if confirmed else "submitted" if marked else "open"),
                         "confirmedAt": m.get("confirmedAt"), "confirmedBy": m.get("confirmedBy")})
        done = sum(1 for x in rows if x["done"])
        # FAIL CLOSED: a rung with no curriculum is not complete — it blocks past itself and says why.
        complete = bool(rows) and done == len(rows)
        by_rung[key] = {"rung": key, "rungName": r["name"], "lessons": rows,
                        "total": len(rows), "done": done, "complete": complete,
                        "exists": bool(rows),
                        "needsConfirmation": any(x["needsConfirmation"] for x in rows),
                        "awaitingConfirmation": sum(1 for x in rows if x["status"] == "submitted"),
                        "completedAt": (rec.get(key) or {}).get("completedAt") if complete else None}
        if not complete and blocking is None:
            blocking, ceiling = key, r["n"]
    return {"byRung": by_rung, "ceilingN": ceiling, "ceiling": RUNG_KEYS[ceiling],
            "blockingRung": blocking, "rungOrder": list(RUNG_KEYS)}


def ceiling_for(name, d=None, content_dir=None):
    """The highest rung `name` may HOLD. `connector_ladder.compute()` mins this with the evidence rung."""
    return state_for(name, d, content_dir)["ceilingN"]


def lesson_rung(slug, content_dir=None):
    for L in load_lessons(content_dir):
        if L["slug"] == slug:
            return L["rung"], L
    return None, None


# ---- the write ------------------------------------------------------------------------
def can_mark(actor, slug, d=None, content_dir=None):
    """The gate. (allowed, reason). Pure — inspects, never mutates.

    Only ever your OWN training, and only a lesson you can already SEE — visibility runs off the
    **evidence** rung, not the held one, or a training-blocked connector could never unblock
    themselves (they would need the rung to read the lesson that grants the rung).
    """
    d = d if d is not None else json.load(open(CRM))
    actor = (actor or "").strip()
    state = ladder.compute(d)
    if actor not in state:
        return False, f"{actor or 'You'} is not a connector in yourco's records — nothing is writable."
    rung, L = lesson_rung(slug, content_dir)
    if not rung:
        return False, "No such lesson."
    ev = state[actor].get("evidenceRungN", state[actor]["rungN"])
    if ev < 0:
        return False, ("Your training starts when you join. Nothing is recordable before the agreement "
                       "and W-9 are on file.")
    if RUNG_N[rung] > ev:
        return False, (f"That lesson opens at {rung}. You cannot complete training for a rung you have "
                       f"not earned yet — the evidence comes first, then its training.")
    return True, ""


def mark_lesson(actor, slug, acknowledged=None, d=None, commit=True, log=None, content_dir=None):
    """Record that `actor` completed `slug`. Their OWN training only. Refusal writes NOTHING.

    Idempotent: re-marking a lesson already done changes nothing and logs nothing.
    """
    d_in = d
    d = d if d is not None else json.load(open(CRM))
    ok, why = can_mark(actor, slug, d, content_dir)
    if not ok:
        raise ScopeError(why)
    rung, L = lesson_rung(slug, content_dir)
    ack = (L or {}).get("acknowledge")
    if ack and acknowledged is not None and str(acknowledged).strip()[:MAX_ACK] != ack[:MAX_ACK]:
        # The page must not be able to invent what somebody agreed to. The stored text is the
        # LESSON's sentence, never the client's — this only catches a tampered payload loudly.
        print(f"[training] ignoring client-supplied acknowledgement for {slug!r}", file=sys.stderr)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    box = {}

    def apply(dd):
        book = dd.setdefault("meta", {}).setdefault(META_KEY, {}).setdefault(actor, {})
        rec = book.setdefault(rung, {"lessons": {}})
        lessons = rec.setdefault("lessons", {})
        box["already"] = bool((lessons.get(slug) or {}).get("at"))
        if not box["already"]:
            lessons[slug] = {"at": now, "by": actor,
                             **({"acknowledged": ack} if ack else {})}
        # the rung is complete when every lesson currently in its curriculum is marked. Recomputed
        # live: if yourco later ADDS a lesson to a rung, that rung honestly reopens.
        req = curriculum(content_dir).get(rung, [])
        required = [x["slug"] for x in req]
        confirm_by_slug = {x["slug"]: needs_confirmation(x, rung) for x in req}
        def _done(sl):    # R2+ / CONFIRM_CAPS need an operator's confirmation, not just the mark
            m = lessons.get(sl) or {}
            return bool(m.get("confirmedAt")) if confirm_by_slug.get(sl) else bool(m.get("at"))
        full = bool(required) and all(_done(s) for s in required)
        if full and not rec.get("completedAt"):
            rec["completedAt"] = now
        elif not full:
            rec.pop("completedAt", None)
        box.update(rungComplete=full, done=sum(1 for s in required if _done(s)),
                   total=len(required), needsConfirm=confirm_by_slug.get(slug, False))
        return rec

    if commit and d_in is None:
        sys.path.insert(0, HERE)
        from connector_writes import _locked_update      # ONE locked/atomic/mirrored write path
        rec = _locked_update(apply)
    else:
        rec = apply(d)
    if box.get("already"):
        return rec                                       # nothing changed → nothing logged
    emit = log if log is not None else ladder.log_event
    submitted = box.get("needsConfirm")
    emit("training.submitted" if submitted else "training.completed",
         connector=actor, by=actor, rung=rung, lesson=slug,
         lessonTitle=(L or {}).get("title") or slug,
         rungComplete=box["rungComplete"], progress=f'{box["done"]} of {box["total"]} confirmed'
         if submitted else f'{box["done"]} of {box["total"]}',
         acknowledged=ack or None, awaitingOperator=bool(submitted),
         note=(f'Submitted by {actor} — {rung} is operator-confirmed; it does NOT count until an '
               f'operator confirms it' if submitted
               else f'Self-recorded as complete by {actor}'
                    + (f' — rung {rung} training finished' if box["rungComplete"] else '')))
    return rec


# ---- operator confirmation (R2+, plus CONFIRM_CAPS wherever they sit) ------------------
def pending_confirmations(d=None, content_dir=None):
    """Every submitted-but-unconfirmed lesson that requires confirmation. The operator's queue."""
    d = d if d is not None else json.load(open(CRM))
    by_slug = {L["slug"]: L for L in load_lessons(content_dir)}
    out = []
    for name, book in ((d.get("meta") or {}).get(META_KEY) or {}).items():
        for rung, rec in (book or {}).items():
            for slug, m in ((rec or {}).get("lessons") or {}).items():
                # Resolve per lesson, not per rung: a CONFIRM_CAPS lesson at R1 still queues here.
                if not needs_confirmation(by_slug.get(slug), rung):
                    continue
                if m.get("at") and not m.get("confirmedAt"):
                    out.append({"connector": name, "rung": rung, "lesson": slug,
                                "submittedAt": m["at"], "acknowledged": m.get("acknowledged")})
    return sorted(out, key=lambda x: x["submittedAt"])


def confirm_lesson(operator, connector, slug, d=None, commit=True, log=None, content_dir=None):
    """An OPERATOR confirms a connector's submission. This is the thing that makes it count.

    Deliberately not something a connector can do for themselves at any rung, and not something an
    operator can do for a lesson that was never submitted — confirmation attests to a conversation
    that happened, so there must be a submission to attest to.
    """
    d_in = d
    d = d if d is not None else json.load(open(CRM))
    operator = (operator or "").strip()
    if not operator:
        raise ScopeError("Confirmation must name the operator doing it — the record is the point.")
    if operator == (connector or "").strip():
        raise ScopeError("A connector cannot confirm their own training. That is what R2+ confirmation is for.")
    rung, L = lesson_rung(slug, content_dir)
    if not rung:
        raise ScopeError("No such lesson.")
    if not needs_confirmation(L, rung):
        raise ScopeError(f"{rung} training is self-marked — there is nothing for an operator to confirm.")
    m = (((((d.get("meta") or {}).get(META_KEY) or {}).get(connector) or {}).get(rung) or {})
         .get("lessons") or {}).get(slug) or {}
    if not m.get("at"):
        raise ScopeError(f"{connector} has not submitted {slug} yet — nothing to confirm.")
    if m.get("confirmedAt"):
        return None                                       # already confirmed → idempotent, no log
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    box = {}

    def apply(dd):
        rec = dd["meta"][META_KEY][connector][rung]
        rec["lessons"][slug].update(confirmedAt=now, confirmedBy=operator)
        required = [x["slug"] for x in curriculum(content_dir).get(rung, [])]
        full = bool(required) and all((rec["lessons"].get(s) or {}).get("confirmedAt") for s in required)
        if full and not rec.get("completedAt"):
            rec["completedAt"] = now
        elif not full:
            rec.pop("completedAt", None)
        box.update(rungComplete=full,
                   done=sum(1 for s in required if (rec["lessons"].get(s) or {}).get("confirmedAt")),
                   total=len(required))
        return rec

    if commit and d_in is None:
        sys.path.insert(0, HERE)
        from connector_writes import _locked_update
        rec = _locked_update(apply)
    else:
        rec = apply(d)
    emit = log if log is not None else ladder.log_event
    emit("training.confirmed", connector=connector, by=operator, rung=rung, lesson=slug,
         lessonTitle=(L or {}).get("title") or slug, rungComplete=box["rungComplete"],
         progress=f'{box["done"]} of {box["total"]}',
         note=(f'{operator} confirmed {connector} completed this {rung} lesson'
               + (f' — {rung} training finished; the rung is now claimable' if box["rungComplete"] else '')))
    return rec


# ---- report ---------------------------------------------------------------------------
def main():
    d = json.load(open(CRM))
    cur = curriculum()
    if "--curriculum" in sys.argv:
        print(f"# Connector curriculum — {sum(len(v) for v in cur.values())} lesson(s)\n")
        for r in ladder.RUNGS:
            ls = cur[r["key"]]
            print(f"## {r['key']} · {r['name']} — {len(ls)} lesson(s)"
                  + ("" if ls else "   ⚠️ none: this rung BLOCKS advancement past itself"))
            for L in ls:
                print(f"   - {L['slug']:<34} {L.get('title','')}"
                      f"{'  [stub]' if L['stub'] else ''}")
            print()
        return
    if "--pending" in sys.argv:                        # the operator's confirmation queue
        q = pending_confirmations(d)
        print(f"# Awaiting operator confirmation — {len(q)} submission(s)"
              f"   (R{CONFIRM_FROM_RUNG}+ only; R0/R1 are self-marked)\n")
        for x in q:
            print(f"  {x['submittedAt'][:10]}  {x['connector']:<24} {x['rung']}  {x['lesson']}")
            if x.get("acknowledged"):
                print(f"      acknowledged: \"{x['acknowledged'][:96]}\"")
        if q:
            print(f"\n  Confirm with:  python3 crm/connector_training.py --confirm "
                  f"\"{q[0]['connector']}\" {q[0]['lesson']} --by \"<your name>\"")
            print("  Confirmation attests you had the conversation and they can actually do it —")
            print("  it is not a formality, and it is recorded against your name permanently.")
        return
    if "--confirm" in sys.argv:
        i = sys.argv.index("--confirm")
        who, slug = sys.argv[i + 1], sys.argv[i + 2]
        by = sys.argv[sys.argv.index("--by") + 1] if "--by" in sys.argv else ""
        try:
            rec = confirm_lesson(by, who, slug)
        except ScopeError as e:
            print(f"REFUSED — {e}"); sys.exit(1)
        print(f"confirmed: {who} · {slug} · by {by}" if rec else "already confirmed — nothing changed")
        return
    state = ladder.compute(d)
    print(f"# Connector training state — {datetime.date.today().isoformat()}\n")
    print(f"Curriculum: " + " · ".join(f"{k} {len(v)}" for k, v in cur.items()) + "\n")
    if not state:
        print("No connector contacts in the CRM.")
        return
    print("| Connector | Evidence | Training ceiling | Holds | Blocked on |")
    print("|---|---|---|---|---|")
    for name, s in sorted(state.items(), key=lambda kv: (-kv[1]["rungN"], kv[0])):
        t = s.get("training") or {}
        print(f"| {name} | {s.get('evidenceRung') or '—'} | {s.get('trainingCeiling') or '—'} | "
              f"{s['rung'] or '—'} | {t.get('blockingRung') or '—'} |")
    print("\n*Held rung = min(evidence, training ceiling). Training completion is SELF-RECORDED in the "
          "console — it proves exposure, not comprehension; see this file's header.*")


if __name__ == "__main__":
    main()
