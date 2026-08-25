#!/usr/bin/env python3
"""The shared store + append-only event log for every pre-build vertical.

Ported from `Pre Build Ideas/property-management/build/core.py` rather than re-invented, because
the honesty rules only hold if there is exactly one implementation of them.

Two rules this module exists to enforce for all ten builds:
  1. A number that cannot be computed from recorded events is returned as
     None with a `_missing` reason — never estimated and never zero-filled.
     (See `unmeasured()`; the UI renders the reason, never a fake 0.)
  2. Every state change is written to the append-only event log with its
     actor (`agent:<name>` or `human:<id>`) and its autonomy rung. The
     "% automated" figure is COUNTED from that log; it is never asserted.

Stdlib only.
"""
import json, os, threading, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

_LOCK = threading.RLock()


# ---------------------------------------------------------------- time

def now():
    return datetime.now(timezone.utc)


def iso(dt=None):
    return (dt or now()).replace(microsecond=0).isoformat()


def parse(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def hours_between(a, b):
    da, db = parse(a), parse(b)
    if not da or not db:
        return None
    return round((db - da).total_seconds() / 3600.0, 2)


def days_until(s, ref=None):
    d = parse(s)
    if not d:
        return None
    return (d - (ref or now())).days


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


# ---------------------------------------------------------------- the missing contract

def unmeasured(reason, field="value", **extra):
    """The ONLY way a build is allowed to not have a number.

    Returns {<field>: None, "_missing": "<why>"} — the UI renders the reason
    as `unmeasured — <reason>`. There is deliberately no `default=0` argument:
    a zero-filled metric is the dishonesty this whole store exists to prevent.
    """
    out = {field: None, "_missing": reason}
    out.update(extra)
    return out


def is_missing(x):
    return isinstance(x, dict) and "_missing" in x


# ---------------------------------------------------------------- storage

class Store:
    """JSON-file store, one file per table, atomic writes, process-local lock."""

    def __init__(self, data_dir, tables, env_var=None):
        if env_var and os.environ.get(env_var):
            data_dir = os.environ[env_var]
        self.dir = Path(data_dir)
        self.tables = tuple(tables)
        if "events" not in self.tables:
            self.tables += ("events",)

    # -- files

    def _path(self, table):
        return self.dir / f"{table}.json"

    def load(self, table, default=None):
        p = self._path(table)
        empty = default if default is not None else ({} if table == "config" else [])
        if not p.exists():
            return empty
        with _LOCK:
            try:
                return json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                return empty

    def save(self, table, rows):
        self.dir.mkdir(parents=True, exist_ok=True)
        with _LOCK:
            tmp = self._path(table).with_suffix(".tmp")
            tmp.write_text(json.dumps(rows, indent=1))
            tmp.replace(self._path(table))

    def upsert(self, table, row, key="id"):
        rows = self.load(table)
        for i, r in enumerate(rows):
            if r.get(key) == row.get(key):
                rows[i] = row
                break
        else:
            rows.append(row)
        self.save(table, rows)
        return row

    def by_id(self, table, _id):
        for r in self.load(table):
            if r.get("id") == _id:
                return r
        return None

    def index(self, table, key="id"):
        return {r.get(key): r for r in self.load(table)}

    @staticmethod
    def nid(prefix):
        return f"{prefix}_{uuid.uuid4().hex[:10]}"

    def wipe(self):
        for t in self.tables:
            p = self._path(t)
            if p.exists():
                p.unlink()

    # -- the append-only log

    def log_event(self, kind, subject, actor, rung=None, detail=None, at=None):
        """Append-only. `actor` is 'agent:<name>' | 'human:<id>' | '<party>:<id>'.

        An agent action recorded WITHOUT a rung is a bug — the % automated read
        depends on it — so we write 'R?' rather than silently dropping the row.
        Nothing in any build may rewrite or delete an event; a correction is a
        NEW event, and both states stay in the log.
        """
        if actor.startswith("agent:") and not rung:
            rung = "R?"
        ev = {"id": self.nid("ev"), "at": at or iso(), "kind": kind,
              "subject": subject, "actor": actor, "rung": rung, "detail": detail or {}}
        with _LOCK:
            rows = self.load("events")
            rows.append(ev)
            self.save("events", rows)
        return ev

    def events(self, kind=None, subject=None, since_days=None):
        rows = self.load("events")
        if kind:
            kinds = {kind} if isinstance(kind, str) else set(kind)
            rows = [e for e in rows if e.get("kind") in kinds]
        if subject:
            rows = [e for e in rows if e.get("subject") == subject]
        if since_days is not None:
            cutoff = now() - timedelta(days=since_days)
            rows = [e for e in rows if (parse(e.get("at")) or now()) >= cutoff]
        return rows


# ---------------------------------------------------------------- counted automation

def automation_rate(events, moving_kinds, window_days=90, floor=30, exclude_actors=()):
    """The honest % automated: of the actions that MOVE work, what share ran
    without a human touching them. COUNTED from the event log.

    `exclude_actors` drops originating parties (a customer filing a request is
    not the OS automating anything; counting it inflates the number to
    meaninglessness, which is exactly what vendor 'automation' claims do).
    Below `floor` moving actions we refuse to state a rate at all.
    """
    cutoff = now() - timedelta(days=window_days)
    kinds = set(moving_kinds)
    rows = [e for e in events if (parse(e.get("at")) or now()) >= cutoff]

    def is_moving(e):
        # An action the gate HELD for a human is still work the OS moved on —
        # it belongs in the denominator. Leaving it out was the bug that made
        # every build report a perfect automation rate: the only actions that
        # got counted were the ones that had already run.
        if e.get("kind") in kinds:
            return True
        # A gate-held action and an outright refusal are both work the OS moved
        # on, so both belong in the denominator.
        return (e.get("kind") in ("queued_for_approval", "refused")
                and (e.get("detail") or {}).get("action") in kinds)

    moving = [e for e in rows if is_moving(e)
              and not any(str(e.get("actor", "")).startswith(p) for p in exclude_actors)]
    if len(moving) < floor:
        return unmeasured(
            f"only {len(moving)} pipeline-moving actions in {window_days} days; "
            f"need {floor} to state a rate", field="rate", moving=len(moving))
    auto = [e for e in moving if e["actor"].startswith("agent:") and e.get("rung") in ("R2", "R3")]
    gated = [e for e in moving if e["actor"].startswith("agent:") and e.get("rung") in ("R0", "R1", "R?")]
    human = [e for e in moving if not e["actor"].startswith("agent:")]
    return {"rate": round(len(auto) / len(moving), 3), "moving": len(moving),
            "autonomous": len(auto), "agent_gated": len(gated), "human_originated": len(human),
            "window_days": window_days,
            "note": "counted from the event log; originating parties excluded by design"}
