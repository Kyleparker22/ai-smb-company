#!/usr/bin/env python3
"""yourco — the connector trust ladder + the append-only attribution log.

The foundation of the Connector OS (`processes/partnerships/connector-os.md`,
`decisions/2026-08-07_connector-os.md`). Two things live here:

1. **The attribution log** (`crm/_attribution-log.jsonl`) — append-only, one JSON object per line,
   monotonic `seq`, never edited. Corrections are NEW entries citing the corrected id. This is the
   audit trail the Connector Console exposes: the first referral program you can audit.

2. **The trust ladder** — rungs R0–R4 computed FROM CRM DATA (never granted by mood), mirroring the
   agent autonomy matrix: autonomy is earned on evidence and lost when the evidence reverses.
   `UNLOCKS` is the machine-readable gate the console, the spotter, and the demo arsenal all read —
   one definition of what a rung permits, so no surface can drift from the policy.

**Training gate (the Founder, 2026-08-07).** Evidence alone is no longer sufficient to hold a rung. Each rung
has its own training (`crm/connector_training.py` + `processes/partnerships/connector-training/`), and
the rung a connector **holds** is `min(evidence rung, training ceiling)`. Both numbers are returned by
`compute()` and must stay apart: "you've earned R2 on evidence — finish R1 training to claim it" is
the whole point, and it cannot be said from one number. `UNLOCKS` is untouched and remains the single
gate — it is simply asked about the **held** rung, via `can()` / `can_for()`.

Book math is imported from `connector_statements.books()` — the same computation the statements and
the CRM Referrals cockpit use. Never forked (connector-os.md §2).

Usage:
  python3 crm/connector_ladder.py                 # report every connector's rung + evidence
  python3 crm/connector_ladder.py --sync          # append rung.changed events for any rung that moved
  python3 crm/connector_ladder.py --json          # machine output (the console reads this shape)
  python3 crm/connector_ladder.py --log [N]       # tail the attribution log
  python3 crm/connector_ladder.py --append '<json>'   # append one event (internal callers use log_event)

STAGED: the ladder is internal plumbing — nothing here is connector-facing. The console, spotter, and
arsenal that consume it are counsel- + launch-gated.
"""
import os, sys, json, uuid, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch (2026-08-07): YOURCO_DATA_ROOT moves DATA only — code stays at HERE.
# See playground/_README.md.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
CRM = os.path.join(DATA_DIR, "data.json")
# The attribution log is APPEND-ONLY and is the permanent record of who earned what. In the
# playground it must land in the sandbox, or practice submissions would be written into the
# real ledger and be indistinguishable from earned evidence.
LOG = os.path.join(DATA_DIR, "_attribution-log.jsonl")
sys.path.insert(0, HERE)
from connector_statements import books, _tier, tier_input  # one source of truth for the book math

# A referral has reached "a real conversation" once the decision-maker engaged (R1 evidence).
CONVERSATION_STAGES = {"discovery", "sitdown", "audit", "proposal", "signed", "build", "live"}  # sitdown+audit merged into discovery 2026-08-11; aliases kept
LIVE_STAGES = {"live"}   # `expand` retired 2026-08-13
RETENTION_DAYS = 90  # R2: live AND retained this long

# The ladder. `key` order IS the rung order. Every surface reads UNLOCKS — never its own copy.
RUNGS = [
    {"n": 0, "key": "R0", "name": "Joined",
     "earn": "signed agreement + W-9 on file"},
    {"n": 1, "key": "R1", "name": "Proven",
     "earn": "1 referral reaching a real conversation (sit-down/audit or beyond)"},
    {"n": 2, "key": "R2", "name": "Producing",
     "earn": f"first referred client live and retained {RETENTION_DAYS} days"},
    {"n": 3, "key": "R3", "name": "Trusted",
     "earn": "3+ live referred clients, retention holding, zero conduct flags"},
    {"n": 4, "key": "R4", "name": "Advisor track",
     "earn": "sustained book + the Founder's judgment (granted, not computed)"},
]
# `recruit_connectors` moved R2 → R1 on 2026-08-11 (`decisions/2026-08-11_connector-program-v2.md`).
# Two things were true: R2 requires a client live AND retained 90 days, so with zero signed clients
# NO connector could recruit anyone, indefinitely — and the R2 gate was simultaneously the
# active-book qualification offered to counsel in place of the depth cap the Founder declined
# (`decisions/2026-08-07_override-depth-uncapped.md`). Moving it unblocks the program and removes
# that guardrail; the trade is recorded in the decision and asked of counsel as checklist item 4c.
UNLOCKS = {
    "R0": ["warm_intros", "console", "referral_spotter", "submit_contacts"],
    "R1": ["demo_generation", "own_digital_employee", "recruit_connectors"],
    "R2": ["quote_locked_prices", "co_brand"],
    "R3": ["run_audit_with_oversight", "deep_co_brand"],
    "R4": ["own_book_yourco_delivers"],
}


def unlocks_at(rung_n):
    """Every capability available at or below this rung — the gate surfaces enforce."""
    out = []
    for r in RUNGS:
        if r["n"] <= rung_n:
            out += UNLOCKS.get(r["key"], [])
    return out


def can(rung_n, capability):
    return capability in unlocks_at(rung_n)


def can_for(state, capability):
    """The training-aware wrapper: ask `UNLOCKS` about the rung this connector actually HOLDS.

    Deliberately a thin wrapper rather than a second policy list — there is one `UNLOCKS`, and the
    only thing training changes is which rung number gets handed to it. A caller that has a
    `compute()` entry should use this; a caller that has a bare number should be sure that number is
    the held rung and not the evidence rung.
    """
    return can((state or {}).get("rungN", -1), capability)


# ---- the append-only attribution log -------------------------------------------------
def read_events():
    """Every event, oldest first. A corrupt line is skipped, never fatal (the log must always read)."""
    out = []
    if not os.path.exists(LOG):
        return out
    with open(LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def log_event(event, **fields):
    """Append one immutable event. Single write() to an O_APPEND handle — concurrent-writer safe.

    NEVER edits or removes a prior line. To correct history, append a 'correction' event whose
    `corrects` names the bad event id. That property is what makes the log auditable.
    """
    evs = read_events()
    rec = {"seq": (evs[-1]["seq"] + 1) if evs else 1,
           "id": uuid.uuid4().hex[:12],
           "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "event": event}
    rec.update(fields)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def events_for(connector):
    """One connector's own history — what their console shows them."""
    return [e for e in read_events() if (e.get("connector") or "") == connector]


# ---- rung computation ----------------------------------------------------------------
def _days_since(iso):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat((iso or "")[:10])).days
    except ValueError:
        return None


def compute(d=None):
    """Every connector's rung + the evidence behind it. Pure read — computes, never writes.

    Three rung numbers come back, and they are not interchangeable:
      `evidenceRungN`   what the CRM says they produced.
      `trainingCeilingN` highest rung whose prerequisite training is finished (fails CLOSED).
      `rungN`           what they HOLD = min(the two). This is the one `UNLOCKS` is asked about.
    """
    d = d or json.load(open(CRM))
    import connector_training as training     # imported here, not at module scope: training imports us
    meta = d.get("meta") or {}
    tiers = meta.get("referralTiers") or {}
    ladder_meta = meta.get("connectorLadder") or {}
    advisor_track = {n.strip().lower() for n in (ladder_meta.get("advisorTrack") or [])}
    flags = {k.strip().lower() for k in (ladder_meta.get("conductFlags") or [])}
    connectors, _credits, downline = books(d)

    # every internal connector contact — including those with no referrals yet
    people = {}
    for c in d.get("contacts", []):
        if c.get("kind") == "internal" and c.get("teamRole") == "connector":
            people[(c.get("name") or "").strip()] = c

    out = {}
    for name, contact in sorted(people.items()):
        if not name:
            continue
        book = connectors.get(name, {"active": [], "inactive": []})
        all_refs = book["active"] + book["inactive"]
        signed = (contact.get("teamStatus") == "active")
        conversations = [r for r in all_refs if r.get("stage") in CONVERSATION_STAGES]
        lives = [r for r in book["active"] if r.get("stage") in LIVE_STAGES]
        retained = [r for r in lives
                    if (_days_since(r.get("stageSince")) or 0) >= RETENTION_DAYS]
        flagged = name.lower() in flags

        # rung: highest rung whose evidence holds. Evidence reversing = the rung drops.
        n = -1
        if signed:
            n = 0
            if conversations:
                n = 1
            if retained:
                n = 2
            if len(lives) >= 3 and not flagged:
                n = 3
            if name.lower() in advisor_track:
                n = 4

        # ---- the training gate -------------------------------------------------------
        # Evidence says what they produced; training says how far that evidence may carry them.
        # The rung they HOLD is the lesser, and it is the only one `UNLOCKS` is ever asked about.
        tstate = training.state_for(name, d)
        ceiling = tstate["ceilingN"]
        ev_n = n
        held = min(ev_n, ceiling) if ev_n >= 0 else ev_n
        blocked = ev_n > held
        ev_rung = next((r for r in RUNGS if r["n"] == max(ev_n, 0)), None) if ev_n >= 0 else None
        rung = next(r for r in RUNGS if r["n"] == max(held, 0)) if held >= 0 else None
        n = held                                    # from here down, `n` means the HELD rung

        nxt = next((r for r in RUNGS if r["n"] == n + 1), None) if 0 <= n < 4 else None
        tier_n, rate = _tier(tier_input(book, tiers), tiers)
        out[name] = {
            "connector": name,
            "contactId": contact.get("id"),
            "teamStatus": contact.get("teamStatus") or "prospect",
            "rung": rung["key"] if rung else None,
            "rungN": n,
            "rungName": rung["name"] if rung else "Not joined",
            "evidenceRung": ev_rung["key"] if ev_rung else None,
            "evidenceRungN": ev_n,
            "evidenceRungName": ev_rung["name"] if ev_rung else "Not joined",
            "trainingCeiling": RUNGS[ceiling]["key"],
            "trainingCeilingN": ceiling,
            "blockedByTraining": blocked,
            # the training that must be finished to claim the rung the evidence already earned
            "trainingNeeded": (tstate["blockingRung"] if blocked else None),
            "training": tstate,
            "nextRung": nxt["key"] if nxt else None,
            "nextRungEarn": nxt["earn"] if nxt else None,
            "unlocks": unlocks_at(n) if n >= 0 else [],
            "evidence": {
                "signed": signed,
                "referrals": len(all_refs),
                "conversations": len(conversations),
                "live": len(lives),
                f"retained{RETENTION_DAYS}d": len(retained),
                "conductFlag": flagged,
                "advisorTrack": name.lower() in advisor_track,
            },
            "book": {"active": len(book["active"]), "activeMRR": sum(a["mrr"] for a in book["active"]),
                     "tier": tier_n, "rate": rate},
            "downline": downline(name),
        }
    return out


def sync(d=None, events=None, log=None):
    """Compute rungs, diff against the last rung.changed in the log, append events for movement.

    This is what makes the ladder real rather than aspirational: rungs move because the evidence
    moved, and every movement is on the permanent record with the evidence that caused it.

    `d` / `events` / `log` are injectable so the whole diff can be exercised against a fixture
    without reading or writing the live CRM or the live attribution log.
    """
    current = compute(d)
    emit = log if log is not None else log_event
    last, last_block = {}, {}
    for e in (events if events is not None else read_events()):
        if e.get("event") == "rung.changed" and e.get("connector"):
            last[e["connector"]] = e.get("to")
        if e.get("event") == "rung.blocked_by_training" and e.get("connector"):
            last_block[e["connector"]] = (e.get("evidenceRung"), e.get("heldRung"))
    moved, blocked = [], []
    for name, s in current.items():
        was, now = last.get(name), s["rung"]
        if was != now:
            rec = emit("rung.changed", connector=name, **{"from": was, "to": now},
                            direction=("up" if (was is None or (now or "R0") > was) else "down"),
                            evidence=s["evidence"], by="connector_ladder.py")
            moved.append((name, was, now, rec["id"]))
        # Evidence outrunning training is genuinely useful signal for Bird — somebody is producing and
        # the only thing in their way is a lesson. Logged when the shape of the block CHANGES, so the
        # log records the event rather than re-stating it on every sync.
        shape = (s["evidenceRung"], s["rung"]) if s["blockedByTraining"] else None
        if shape and last_block.get(name) != shape:
            rec = emit("rung.blocked_by_training", connector=name,
                            evidenceRung=s["evidenceRung"], heldRung=s["rung"],
                            trainingNeeded=s["trainingNeeded"], by="connector_ladder.py",
                            note=(f'{name} has earned {s["evidenceRung"]} on evidence but holds '
                                  f'{s["rung"]} — {s["trainingNeeded"]} training is unfinished.'))
            blocked.append((name, s["evidenceRung"], s["rung"], s["trainingNeeded"], rec["id"]))
    return current, moved, blocked


def main():
    if "--append" in sys.argv:
        payload = json.loads(sys.argv[sys.argv.index("--append") + 1])
        print(json.dumps(log_event(payload.pop("event", "note"), **payload), indent=1))
        return
    if "--log" in sys.argv:
        i = sys.argv.index("--log")
        n = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 20
        evs = read_events()[-n:]
        print(f"# attribution log — {len(read_events())} event(s) total, showing last {len(evs)}\n")
        for e in evs:
            extra = " ".join(f"{k}={e[k]}" for k in ("connector", "company", "from", "to")
                             if e.get(k) is not None)
            print(f"  #{e['seq']:<4} {e['ts']}  {e['event']:<20} {extra}")
        return
    do_sync = "--sync" in sys.argv
    state, moved, blocked = sync() if do_sync else (compute(), [], [])
    if "--json" in sys.argv:
        print(json.dumps(state, indent=1))
        return
    print(f"# Connector trust ladder — {datetime.date.today().isoformat()}"
          f"{' (synced)' if do_sync else ' (dry — add --sync to record movement)'}\n")
    if not state:
        print("No connector contacts in the CRM yet.")
        return
    joined = [s for s in state.values() if s["rungN"] >= 0]
    print(f"{len(state)} connector(s) · {len(joined)} joined (R0+) · "
          f"{len(state) - len(joined)} not yet signed (program is counsel-gated)\n")
    print("| Connector | Holds | Evidence | Training ceiling | Referrals | Conversations | Live |")
    print("|---|---|---|---|---:|---:|---:|")
    for name, s in sorted(state.items(), key=lambda kv: (-kv[1]["rungN"], kv[0])):
        ev = s["evidence"]
        flag = " ⚠️" if s["blockedByTraining"] else ""
        print(f"| {name} | {s['rung'] or '—'} · {s['rungName']}{flag} | {s['evidenceRung'] or '—'} | "
              f"{s['trainingCeiling']} | {ev['referrals']} | {ev['conversations']} | {ev['live']} |")
    if moved:
        print("\n## Rung movement recorded")
        for name, was, now, eid in moved:
            print(f"- **{name}**: {was or '—'} → {now or '—'}  (event {eid})")
    if blocked:
        print("\n## Evidence ahead of training (recorded)")
        for name, evr, held, need, eid in blocked:
            print(f"- **{name}**: earned {evr}, holds {held} — {need} training unfinished  (event {eid})")
    stuck = [s for s in state.values() if s["blockedByTraining"]]
    if stuck and not do_sync:
        print(f"\n⚠️ {len(stuck)} connector(s) have evidence ahead of their training "
              f"(--sync records it).")
    print(f"\n*Rungs are computed from CRM evidence, never granted — and a rung is only HELD once that "
          f"rung's prerequisite training is done (`crm/connector_training.py`). Unlocks: `UNLOCKS` in "
          f"this file, asked about the HELD rung — the console, spotter, and demo arsenal all gate on "
          f"it. Log: `crm/_attribution-log.jsonl` ({len(read_events())} events).*")


if __name__ == "__main__":
    main()
