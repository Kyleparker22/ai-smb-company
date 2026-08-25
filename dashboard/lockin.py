#!/usr/bin/env python3
"""Lock-in — the partner review→lock run, tracked instead of remembered.

`processes/partner-b-walkthrough-schedule.md` sets a ten-session run from 2026-08-11 to 08-26:
review one domain, lock it the next session, across nine working days. It is a real project
with a deadline and a defined scope, and until now it lived as a static markdown table —
nothing anywhere could answer "how many domains are actually locked?"

THE SCHEDULE IS NOT COPIED HERE.  The calendar table, the per-domain material links, the
standing rules and the prep checklist are all PARSED out of that file on every call. Edit the
schedule, and this view follows. A second copy of the dates would drift within a week, which
is the failure mode CLAUDE.md's change-one-sweep-all rule exists to prevent.

HOW "LOCKED" IS DECIDED — from evidence, per the schedule's own rule
  The schedule already states it: *"Every lock produces a decision entry. Use the log-decision
  skill the same day — a domain 'locked' with nothing in decisions/ is not locked."* So lock
  state is derived from `decisions/`, never from a checkbox somebody has to remember to tick:

    locked      a decision carries the marker `**Locks:** <domain>`  (definitive)
    likely      a decision dated on/after the review names the domain in its title (INFERRED —
                shown as unconfirmed, because a title match is a guess, not a record)
    slipped     the lock date has passed with neither of the above
    due         the lock is scheduled for today
    reviewing   reviewed, lock not yet due
    upcoming    hasn't started

  The distinction between `locked` and `likely` is the whole honesty design. A title-keyword
  match would quietly turn "we talked about marketing" into "marketing is locked", so it never
  claims the strong word — it asks for the marker instead.

Read-only. Exposed as GET /api/lockin.
"""
import os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEDULE = "processes/partner-b-walkthrough-schedule.md"
DECISIONS = os.path.join(ROOT, "decisions")

YEAR = 2026  # the run's year; the schedule writes dates as "Tue 8/11"
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
DATE_CELL_RE = re.compile(r"(\d{1,2})/(\d{1,2})")
LOCKS_MARKER_RE = re.compile(r"^\s*[-*]?\s*\*\*Locks:?\*\*\s*(.+)$", re.M | re.I)


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _slug(name):
    """Normalize a domain name so the calendar's two spellings of the same domain pair up —
    'Overall organization + simplicity of the business' (review) vs 'Organization + simplicity'
    (lock). Without this the last domain would look reviewed-but-never-locked forever."""
    s = (name or "").lower()
    s = re.sub(r"\b(overall|of the business|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return " ".join(s.split())


def _same(a, b):
    a, b = _slug(a), _slug(b)
    if not a or not b:
        return False
    return a == b or a.startswith(b[:12]) or b.startswith(a[:12])


# ---- the calendar ----------------------------------------------------------
def _calendar(txt):
    """The 'THE ACTUAL CALENDAR' table -> [{date, lock:[...], review:[...], sameDay}]."""
    sec = re.search(r"## THE ACTUAL CALENDAR.*?\n((?:\|.*\n)+)", txt, re.S)
    if not sec:
        return []
    rows = []
    for line in sec.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        m = DATE_CELL_RE.search(cells[0])
        if not m:
            continue  # header row
        try:
            d = datetime.date(YEAR, int(m.group(1)), int(m.group(2))).isoformat()
        except ValueError:
            continue
        rows.append({
            "date": d,
            "label": re.sub(r"[*]", "", cells[0]).strip(),
            "lock": BOLD_RE.findall(cells[1]),
            "review": BOLD_RE.findall(cells[2]),
            # "(review *and* lock, all three, same day)" — the first two sessions do both
            "sameDay": bool(re.search(r"review\s*\*?and\*?\s*lock", cells[2], re.I)),
            "reviewRaw": re.sub(r"\*+", "", cells[2]).strip(),
        })
    return rows


def _materials(txt):
    """The 'Where each domain's material lives' bullets -> {lead-in: prose}."""
    sec = re.search(r"\*\*Where each domain's material lives\*\*.*?\n(.*?)(?=\n\*\*Standing rules)",
                    txt, re.S)
    out = {}
    if not sec:
        return out
    for chunk in re.split(r"\n(?=- \*\*)", sec.group(1)):
        m = re.match(r"-\s*\*\*(.+?)\*\*\s*[—–-]\s*(.+)", chunk.strip(), re.S)
        if m:
            out[m.group(1).strip()] = re.sub(r"\s+", " ", m.group(2)).strip()
    return out


def _material_for(domain, materials):
    for lead, prose in materials.items():
        if any(_same(domain, part) for part in re.split(r"[/·]", lead)):
            return {"heading": lead, "text": prose}
    return None


def _rules(txt):
    sec = re.search(r"\*\*Standing rules for this run:\*\*\n(.*?)(?=\n## )", txt, re.S)
    if not sec:
        return []
    return [re.sub(r"\s+", " ", re.sub(r"\*+", "", c)).strip(" -")
            for c in re.split(r"\n(?=- )", sec.group(1)) if c.strip().startswith("- ")]


def _prep(txt):
    sec = re.search(r"## What to prepare before Session 1\n(.*?)(?=\n## )", txt, re.S)
    if not sec:
        return []
    out = []
    for line in sec.group(1).splitlines():
        m = re.match(r"\s*- \[( |x|X)\]\s*(.+)", line)
        if m:
            out.append({"done": m.group(1).lower() == "x",
                        "text": re.sub(r"\s+", " ", re.sub(r"\*+", "", m.group(2))).strip()})
    return out


# ---- lock evidence ---------------------------------------------------------
def _lock_evidence():
    """Scan decisions/ once. -> ([{file,date,title,locks:[...]}], by nothing else)."""
    rows = []
    try:
        names = sorted(f for f in os.listdir(DECISIONS)
                       if f.endswith(".md") and not f.startswith("_"))
    except OSError:
        return rows
    for fn in names:
        txt = _read(f"decisions/{fn}")
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_", fn)
        title = next((l[2:].strip() for l in txt.splitlines() if l.startswith("# ")), fn[:-3])
        rows.append({
            "file": f"decisions/{fn}",
            "date": m.group(1) if m else None,
            "title": re.sub(r"^Decision\s*[—–-]\s*", "", title).strip(),
            "locks": [x.strip() for mm in LOCKS_MARKER_RE.findall(txt)
                      for x in re.split(r"[,;+]| and ", mm) if x.strip()],
        })
    return rows


# Keywords used ONLY for the weak, clearly-labelled "likely" inference.
INFER = {
    "business plan": r"business.?plan",
    "financial model": r"financial model|model recalibration|projections",
    "crm": r"\bcrm\b",
    "hq": r"\bhq\b|dashboard",
    "connector console": r"connector console",
    "connector/referral program": r"connector|referral",
    "agents": r"\bagents?\b|roster",
    "sales": r"\bsales\b|pipeline|outbound",
    "marketing": r"marketing|content|demand",
    "software / tools / expenses / costs": r"tool|expense|cost|spend|stack",
    "back office": r"back.?office|onboarding|offboarding|payments",
    "legal": r"legal|counsel|operating agreement|\boa\b",
    "organization + simplicity": r"organi[sz]ation|simplic",
    "who to add to the crm": r"warm.?network|prospects? to add",
}


def _infer_rx(domain):
    for k, rx in INFER.items():
        if _same(domain, k):
            return rx
    return None


def _status(dom, ev, today):
    """Decide one domain's state from evidence + the calendar. Order matters: definitive
    evidence beats the calendar, and the calendar beats an inference."""
    marker = [e for e in ev if any(_same(dom["domain"], l) for l in e["locks"])]
    if marker:
        return "locked", marker[0], "decision carries the **Locks:** marker"

    rx = _infer_rx(dom["domain"])
    likely = []
    if rx and dom.get("reviewDate"):
        likely = [e for e in ev if e["date"] and e["date"] >= dom["reviewDate"]
                  and re.search(rx, e["title"], re.I)]
    if likely:
        return "likely", likely[-1], ("a decision dated in-window names this domain — INFERRED "
                                      "from the title, not recorded. Add `**Locks:** "
                                      f"{dom['domain']}` to confirm it.")

    lock = dom.get("lockDate")
    rev = dom.get("reviewDate")
    if lock and lock < today:
        return "slipped", None, f"lock was due {lock} and no decision records it"
    if lock and lock == today:
        return "due", None, "scheduled to lock today"
    if rev and rev <= today:
        return "reviewing", None, f"reviewed {rev}, locks {lock or '—'}"
    return "upcoming", None, ""


ORDER = {"slipped": 0, "due": 1, "reviewing": 2, "likely": 3, "upcoming": 4, "locked": 5}


def build(today=None):
    today = (today or datetime.date.today()).isoformat()
    txt = _read(SCHEDULE)
    if not txt:
        return {"error": f"{SCHEDULE} not found — the run's schedule is its source of truth"}

    cal = _calendar(txt)
    materials = _materials(txt)
    ev = _lock_evidence()

    # domain -> its review date and its lock date, paired across rows
    doms = []
    for row in cal:
        for name in row["review"]:
            if any(_same(name, d["domain"]) for d in doms):
                continue
            doms.append({"domain": name, "reviewDate": row["date"],
                         "reviewLabel": row["label"],
                         "lockDate": row["date"] if row["sameDay"] else None,
                         "sameDay": row["sameDay"]})
    for row in cal:
        for name in row["lock"]:
            hit = next((d for d in doms if _same(name, d["domain"])), None)
            if hit and not hit["lockDate"]:
                hit["lockDate"] = row["date"]
            elif not hit:  # locked but never listed as reviewed — surface, don't drop
                doms.append({"domain": name, "reviewDate": None, "reviewLabel": "",
                             "lockDate": row["date"], "sameDay": False})

    for d in doms:
        st, src, why = _status(d, ev, today)
        d["status"], d["evidence"], d["why"] = st, src, why
        d["material"] = _material_for(d["domain"], materials)
        d["noLockDate"] = d["lockDate"] is None

    counts = {k: sum(1 for d in doms if d["status"] == k) for k in ORDER}
    doms.sort(key=lambda d: (ORDER.get(d["status"], 9), d.get("lockDate") or "9999",
                             d["domain"]))

    upcoming = [r for r in cal if r["date"] >= today]
    past = [r for r in cal if r["date"] < today]
    today_row = next((r for r in cal if r["date"] == today), None)
    next_row = upcoming[0] if upcoming else None

    locked_n = counts["locked"]
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "today": today,
        "schedule": SCHEDULE,
        "calendar": cal,
        "domains": doms,
        "counts": counts,
        "total": len(doms),
        "lockedConfirmed": locked_n,
        "progress": f"{locked_n} of {len(doms)} domains locked with a decision entry",
        "todaySession": today_row,
        "nextSession": next_row,
        "sessionsDone": len(past),
        "sessionsTotal": len(cal),
        "runStart": cal[0]["date"] if cal else None,
        "runEnd": cal[-1]["date"] if cal else None,
        "notStarted": bool(cal) and today < cal[0]["date"],
        "rules": _rules(txt),
        "prep": _prep(txt),
        "prepOpen": sum(1 for p in _prep(txt) if not p["done"]),
        "note": ("Lock state is derived from decisions/, per the schedule's own rule: a domain "
                 "'locked' with nothing in decisions/ is not locked. `locked` requires a "
                 "`**Locks:** <domain>` marker; `likely` is a title-keyword guess shown as "
                 "unconfirmed and never counted as locked. The calendar, material links, rules "
                 "and prep list are parsed from the schedule file, never copied — edit it and "
                 "this follows."),
    }


if __name__ == "__main__":
    d = build()
    if d.get("error"):
        raise SystemExit(d["error"])
    print(f"LOCK-IN RUN — {d['runStart']} → {d['runEnd']} · session {d['sessionsDone']}/{d['sessionsTotal']}")
    print(f"  {d['progress']}")
    print("  " + " · ".join(f"{k} {v}" for k, v in d["counts"].items() if v))
    n = d["todaySession"] or d["nextSession"]
    if n:
        when = "TODAY" if d["todaySession"] else "next"
        print(f"\n  {when}: {n['label']} — review {', '.join(n['review']) or '—'}"
              + (f" · lock {', '.join(n['lock'])}" if n["lock"] else "")
              + ("  (review AND lock, same day)" if n["sameDay"] else ""))
    print()
    for x in d["domains"]:
        ev = f"  <- {x['evidence']['file']}" if x.get("evidence") else ""
        print(f"  [{x['status']:<9}] {x['domain'][:44]:<46} review {x['reviewDate'] or '—'} "
              f"lock {x['lockDate'] or '—'}{ev}")
        if x["why"]:
            print(f"              {x['why'][:110]}")
    if d["prepOpen"]:
        print(f"\n  prep before session 1 — {d['prepOpen']} open:")
        for p in d["prep"]:
            if not p["done"]:
                print(f"    [ ] {p['text'][:104]}")
