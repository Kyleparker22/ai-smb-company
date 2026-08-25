#!/usr/bin/env python3
"""yourco dashboard — derived-data layer (Atlas).

Derives the numbers the dashboard used to hand-maintain (and rot):
- loop health: every sanctioned timer -> schedule, latest committed artifact, on-time/stale/never
- autonomy ladder: live rungs parsed from runtime/autonomy-matrix.md
- gate status: launch-gate.md + counsel-gates.md rollup
- needs-the Founder queue: Jim's newest loops/open-loops/ artifact (+ seed inventory counts)
- watchdog chips: latest loops/_consistency/ + loops/_governance/ reports (clean vs drift)
- runway: finance/runway.md snapshot (cash/MRR/runway, or the cash-TBD nag with day count)
- git activity: 7-day commit pulse (loop commits vs human commits)

Two ways in:
  python3 dashboard/refresh.py     # writes the `derived` block into data.json (for static/committed views)
  server.py imports derive()       # /api/dashboard recomputes it live on every poll

Single source of truth stays runtime/agent-registry.json + the repo itself; this file only reads.
"""
import json, os, re, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: YOURCO_DATA_ROOT redirects every source read below to the sandbox tree.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
DATA_DIR = os.path.join(ROOT, "dashboard") if PLAYGROUND else HERE

# timer key -> loops/ artifact dir when it isn't just loops/<key>
ARTIFACT_DIR = {
    "watchdog": "_watchdog",
    "agent-registry": "_governance",
    "consistency": "_consistency",
    "sadie-intent": "sadie",
    "open-loops-chaser": "open-loops",
    "evidence-sweep": "_trust",
    # Added 2026-08-23. crm-hygiene writes to loops/_crm-hygiene/ (leading underscore, like the other
    # machine-written stores) while this map defaulted to loops/crm-hygiene/. The directory does not
    # exist, so a loop that had produced 26 dated artifacts — newest 2026-08-21, the day before this
    # was found — was reported to HQ as "never ran". Half the loop alarms on the dashboard were wrong.
    "crm-hygiene": "_crm-hygiene",
    # The heartbeat writes one JSONL store, not a dated artifact per run (added 2026-08-25). Without
    # this row HQ would score a beat-every-15-minutes loop as "never ran" — the exact bug the
    # crm-hygiene line above records, caught this time by the invariant instead of by eye.
    "heartbeat": "_health",
    # finance-close writes its readout to finance/readouts/YYYY-MM.md, not to loops/. It was
    # marked UNTRACKED with the note "audit 07-04: never wired on host" — true when written, wrong
    # since the timer landed. Being untracked excluded it from the tracked count, so HQ never
    # scored it, so nobody noticed it fired on 2026-08-03 and produced nothing. Three weeks of a
    # monthly close silently not happening, hidden by a stale parenthetical.
    "finance-close": os.path.join("..", "finance", "readouts"),
}

# Loops whose evidence is an append-only JSONL store rather than one dated file per run. Scoring these
# by filename finds nothing and calls them "never", which is the opposite of the truth: evidence-sweep
# has 233 records in loops/_trust/actions.jsonl. Health comes from the newest `ts` in the store instead.
JSONL_STORE = {"evidence-sweep", "heartbeat"}
# loops with no committed per-run artifact (health can't be derived from the repo)
UNTRACKED = {
    "runtime-alarm": "hourly alarm; alerts only, no artifact",
    "demo-prep": "staged — deps pending; writes to clients/",
}
CLIENT_INFRA = {"storm-publish", "storm-alerts"}  # Sample Product product infra, not agent loops
# loops that have never fired, with a diagnosed root cause (health stays "never" so the nag stays)
NEVER_NOTE = {
    "melanie-briefing": "timer installed 2026-07-06 (was never enabled for 3 weeks) — first fire Tue 07:45; 'never' clears itself after that run",
    # Not a loop and not late: committed 2026-08-25, and enabling a systemd unit is a HOST action
    # nobody in a Cowork session can take. Saying WHY it has never fired is the difference between a
    # nag and a next step.
    "heartbeat": "committed 2026-08-25, not yet enabled — host action: `sudo systemctl enable --now yourco-heartbeat.timer`. Until it runs, dashboard/uptime.py reads unmeasured, never 100%",
}

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
MONTH_RE = re.compile(r"^(\d{4}-\d{2})(?!-\d)")   # monthly artifacts: YYYY-MM.md


def _read(path):
    try:
        with open(os.path.join(ROOT, path)) as f:
            return f.read()
    except OSError:
        return ""


def _cadence(cal):
    """OnCalendar= -> (label, grace_days). grace = how old the newest artifact may be before 'stale'."""
    if re.search(r"\*:\d+/\d+", cal):
        return "sub-hourly", None
    if re.search(r"01,04,07,10", cal):
        return "quarterly", 100
    if re.search(r"\*-\*-(01|1\.\.7)", cal) or "*-*-1..7" in cal:
        # 38, not 37, and the number comes from the SOP rather than from taste. A monthly artifact
        # is dated to the 1st of the period it covers (see MONTH_RE below), so an ON-TIME close is
        # already 32-38 days "old" the day it is written — the worst case being a 31-day month whose
        # next first Monday falls on the 7th (2026-08 closed 2026-09-07 is exactly that, and it is
        # the very next close due). At 37 that on-time close sat precisely on the boundary with zero
        # headroom. finance/monthly_close.md defines its own watchdog as "a month with no readout by
        # the 8th", which is period-start + 38 — so the grace is set to the SOP's own trigger.
        return "monthly", 38
    if "Mon-Fri" in cal:
        return "weekdays", 4
    if re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", cal.strip()):
        return "weekly", 10
    if re.search(r"\*-\*-\* \*:00", cal):
        return "hourly", None
    return "daily", 3


def runtime_switch():
    """Is the headless runtime switched OFF — and can this machine even tell?

    `runtime/.paused` is a 0-byte, gitignored file that makes EVERY loop a no-op before it
    spends a token. It is the single highest-leverage piece of state in the OS and until
    2026-08-23 no HQ surface could see it: the dashboard reported "17 stale, 3 never ran"
    while the actual cause was one `touch`. A switched-off OS read as a broken one, and the
    story that stuck was "billing" during a week when total spend was $2.71.

    Provenance matters here, so this refuses rather than guesses. The file is host-local, so
    an HQ running on the Mac genuinely CANNOT see the VPS's switch. The discriminator is
    `loops/_runtime/` — runtime/run-loop.sh writes per-run logs there and the directory is gitignored,
    so its presence means "this checkout IS the runtime box".

      paused=True   the file is here, seen directly
      paused=False  we are on the runtime box and the file is absent — proven off
      paused=None   we cannot see it from this machine; say so, never imply "running"
    """
    # The runtime box is DEFINITIONALLY the checkout at $HOME/yourco-os — runtime/run-loop.sh hardcodes
    # REPO="$HOME/yourco-os". An empty loops/_runtime/ directory also exists on the Mac (left over
    # before it was gitignored), so directory-presence alone is not the discriminator; its having
    # CONTENT is, and the path check is exact. Either signal is sufficient.
    on_runtime = (os.path.realpath(ROOT) == os.path.realpath(os.path.expanduser("~/yourco-os"))
                  or bool(os.path.isdir(os.path.join(ROOT, "loops", "_runtime"))
                          and os.listdir(os.path.join(ROOT, "loops", "_runtime"))))
    pfile = os.path.join(ROOT, "runtime", ".paused")
    if os.path.exists(pfile):
        try:
            since = datetime.datetime.fromtimestamp(os.path.getmtime(pfile)).isoformat(timespec="seconds")
        except OSError:
            since = None
        return {"paused": True, "since": since, "evidence": "runtime/.paused is present on this host",
                "note": "Every loop is a no-op until this file is removed. "
                        "Resume: rm ~/yourco-os/runtime/.paused"}
    if on_runtime:
        return {"paused": False, "since": None,
                "evidence": "this checkout is the runtime box and .paused is absent",
                "note": "loops are armed"}
    return {"paused": None, "since": None,
            "evidence": "runtime/.paused is host-local and gitignored — it cannot be read from this machine",
            "note": "Loop health below is derived from committed artifacts only. If loops look stale, "
                    "check the switch on the runtime box before concluding anything is broken: "
                    "ssh user@your-vps 'ls -l ~/yourco-os/runtime/.paused'"}


def _last_run(key):
    """When did this loop last actually FIRE, and did it produce anything?

    Artifact dates alone conflate two very different failures: a loop that never fires, and a
    loop that fires on schedule and silently writes nothing. pipeline-report is the live
    example — its timer ran 2026-08-17 while its newest artifact is dated 2026-07-06. Those
    need opposite fixes, and "stale" said nothing about which one you had.

    runtime/run-loop.sh appends one line per run to loops/_runtime/<loop>.log. That directory is
    gitignored (per-run logs are noise), so this only resolves on the runtime box; elsewhere it
    returns None and the caller must not pretend otherwise.
    """
    path = os.path.join(ROOT, "loops", "_runtime", f"{key}.log")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except OSError:
        return None
    if not lines:
        return None
    last = lines[-1]
    m = re.match(r"\[(\d{4}-\d{2}-\d{2})", last)
    return {"date": m.group(1) if m else None,
            "paused": "PAUSED" in last,
            "line": last[:160]}


def _loops(today):
    sysd = os.path.join(ROOT, "runtime", "systemd")
    out = []
    if not os.path.isdir(sysd):
        return out
    for fn in sorted(os.listdir(sysd)):
        if not fn.endswith(".timer"):
            continue
        key = fn[len("yourco-"):-len(".timer")] if fn.startswith("yourco-") else fn[:-6]
        cal = ""
        for line in _read(os.path.join("runtime", "systemd", fn)).splitlines():
            if line.startswith("OnCalendar="):
                cal = line.split("=", 1)[1].strip()
        label, grace = _cadence(cal)
        kind = "client-infra" if key in CLIENT_INFRA else "internal"
        adir = os.path.join(ROOT, "loops", ARTIFACT_DIR.get(key, key))
        last = None
        if key in JSONL_STORE and os.path.isdir(adir):
            newest = ""
            for fn2 in os.listdir(adir):
                if not fn2.endswith(".jsonl"):
                    continue
                try:
                    with open(os.path.join(adir, fn2), "r", encoding="utf-8", errors="replace") as fh:
                        for ln in fh:
                            ln = ln.strip()
                            if not ln:
                                continue
                            _ts = (json.loads(ln).get("ts") or "")[:10]
                            if _ts > newest:
                                newest = _ts
                except (OSError, ValueError):
                    continue
            last = newest or None
        elif os.path.isdir(adir):
            dates = [m.group(1) for f in os.listdir(adir) for m in [DATE_RE.match(f)] if m]
            if not dates:
                # Month-granularity artifacts. The monthly close writes finance/readouts/YYYY-MM.md,
                # which a YYYY-MM-DD pattern never matches — so a loop with a real readout scored
                # "never ran". Normalise to the first of that month: for a monthly cadence the day
                # within the month is not information, and claiming one would be inventing precision.
                dates = [m.group(1) + "-01" for f in os.listdir(adir)
                         for m in [MONTH_RE.match(f)] if m]
            last = max(dates) if dates else None
        if kind == "client-infra":
            health, note = "n/a", "client infra (Sample Product) — outside loop health"
        elif key in UNTRACKED:
            health, note = "untracked", UNTRACKED[key]
        elif last is None:
            health, note = "never", NEVER_NOTE.get(key, "no artifact ever committed")
        else:
            age = (today - datetime.date.fromisoformat(last)).days
            health = "stale" if (grace is not None and age > grace) else "on-time"
            note = f"{age}d ago"
        # Separate the two failures that "stale" used to hide. Only resolvable on the runtime
        # box (the run log is gitignored); elsewhere lastRun is None and nothing is claimed.
        run = _last_run(key)
        if health == "stale" and run:
            if run.get("paused"):
                note = f"{note} — last run was SKIPPED (runtime paused)"
            elif run.get("date") and run["date"] > (last or ""):
                note = f"{note} — but it FIRED {run['date']} and wrote nothing"
        out.append({"loop": key, "schedule": cal, "cadence": label, "kind": kind,
                    "lastArtifact": last, "health": health, "note": note,
                    "lastRun": (run or {}).get("date"),
                    "lastRunPaused": (run or {}).get("paused"),
                    "ranWithoutOutput": bool(run and health == "stale" and not run.get("paused")
                                             and run.get("date") and run["date"] > (last or ""))})
    return out


def _autonomy():
    txt = _read("runtime/autonomy-matrix.md")
    m = re.search(r"## Current rungs.*?\n((?:\|.*\n)+)", txt)
    rows = []
    if m:
        for line in m.group(1).splitlines()[2:]:  # skip header + separator
            cells = [c.strip().strip("*").strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0]:
                rows.append({"action": cells[0].replace("**", ""), "rung": cells[1].replace("**", ""),
                             "ceiling": cells[2]})
    return rows


def _gates():
    oak = "unknown"
    m = re.search(r"^\| Status \| (.+?) \|", _read("processes/launch-gate.md"), re.M)
    if m:
        oak = re.sub(r"\*+", "", m.group(1)).strip()
    txt = _read("processes/counsel-gates.md")
    sec = re.search(r"## The gates.*?\n((?:\|.*\n)+)", txt, re.S)
    counts = {"blockedHard": 0, "awaitingCounsel": 0, "notStarted": 0, "cleared": 0, "total": 0}
    if sec:
        for line in sec.group(1).splitlines()[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or not cells[0].strip():
                continue
            counts["total"] += 1
            s = cells[3]
            if "🔴" in s: counts["blockedHard"] += 1
            elif "🟠" in s: counts["awaitingCounsel"] += 1
            elif "✅" in s: counts["cleared"] += 1
            else: counts["notStarted"] += 1
    return {"OtherVenture": oak, "counsel": counts}


def _needs_founder(today):
    """'Needs the Founder' tile: parse Jim's newest open-loops queue artifact in loops/open-loops/
    (files YYYY-MM-DD.md; _seed-*.md items under '## Queue'/'## Added' headings count too)."""
    d = os.path.join(ROOT, "loops", "open-loops")
    if not os.path.isdir(d):
        return None
    runs = sorted(f for f in os.listdir(d) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f))
    seeds = sorted(f for f in os.listdir(d) if f.startswith("_seed") and f.endswith(".md"))
    if not runs and not seeds:
        return None
    items, date = [], None
    if runs:
        date = runs[-1][:-3]
        txt = _read(os.path.join("loops", "open-loops", runs[-1]))
        sec = re.search(r"## The queue.*?\n(.*?)(?=\n## |\Z)", txt, re.S)
        for line in (sec.group(1) if sec else txt).splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5 or not re.match(r"\d", cells[0]):
                continue  # header / separator / prose rows
            sev = "🔴" if "🔴" in cells[0] else ("🟡" if "🟡" in cells[0] else "")
            m = re.search(r"\*\*(.+?)\*\*", cells[1])
            name = re.sub(r"[*`]", "", (m.group(1) if m else cells[1])).strip()
            items.append({"n": int(re.match(r"\d+", cells[0]).group()), "sev": sev,
                          "name": name[:90], "age": cells[4]})
    seed_count = 0
    for fn in seeds:
        heading = ""
        for line in _read(os.path.join("loops", "open-loops", fn)).splitlines():
            if line.startswith("## "):
                heading = line[3:].strip().lower()
                continue
            if not (heading.startswith("queue") or heading.startswith("added")):
                continue
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            c0 = cells[0] if cells else ""
            if (len(cells) < 3 or not c0 or c0 in ("Item", "#")
                    or set(c0) <= set("-: ") or c0.startswith("~~") or "✅" in s):
                continue  # header / separator / cleared rows
            seed_count += 1
    return {"date": date, "items": items[:8], "count": len(items), "seedCount": seed_count,
            "total": len(items) + seed_count, "source": "via Jim's open-loops chaser"}


def _latest_report(dirname):
    """Newest dated report in loops/<dirname>/ -> (YYYY-MM-DD, text) or (None, None)."""
    d = os.path.join(ROOT, "loops", dirname)
    if not os.path.isdir(d):
        return None, None
    # exact YYYY-MM-DD.md only — companion docs (2026-07-06_stat-refresh-sources.md) sort
    # after the dated report and would otherwise be read as "the" report
    fs = sorted(f for f in os.listdir(d) if DATE_RE.match(f) and f.endswith(".md") and len(f) == 13)
    if not fs:
        return None, None
    return fs[-1][:10], _read(os.path.join("loops", dirname, fs[-1]))


def _watchdogs():
    """Consistency + governance chips, each from that watchdog's latest committed report."""
    out = {}
    date, txt = _latest_report("_consistency")
    if txt is None:
        out["consistency"] = {"status": "missing"}
    elif "**ALL ALIGNED**" in txt:
        out["consistency"] = {"status": "clean", "count": 0, "date": date}
    elif "**DRIFT FOUND**" in txt:
        m = re.search(r"(\d+)\s+drift item", txt)
        out["consistency"] = {"status": "drift", "count": int(m.group(1)) if m else 1, "date": date}
    else:
        out["consistency"] = {"status": "unknown", "date": date}
    date, txt = _latest_report("_governance")
    if txt is None:
        out["governance"] = {"status": "missing"}
    else:
        res = re.search(r"\*\*Result:\*\*\s*(.+)", txt)
        line = res.group(1) if res else ""
        if "✅" in line or "clean" in line.lower():
            out["governance"] = {"status": "clean", "count": 0, "date": date}
        elif "DRIFT" in line.upper():
            n = len(re.findall(r"^\|\s*DRIFT\s*\|", txt, re.M))
            out["governance"] = {"status": "drift", "count": n or 1, "date": date}
        else:
            out["governance"] = {"status": "unknown", "date": date}
    return out


def _runway(today):
    """finance/runway.md snapshot table -> cash / MRR / runway (or the cash-TBD nag with day count)."""
    txt = _read("finance/runway.md")
    if not txt:
        return None
    m = re.search(r"as of (\d{4}-\d{2}-\d{2})", txt)
    as_of = m.group(1) if m else None

    def row(label):
        r = re.search(r"^\|\s*" + label + r"\s*\|\s*(.+?)\s*\|", txt, re.M)
        return re.sub(r"\*+", "", r.group(1)).strip() if r else None

    cash, mrr, burn = row("Cash on hand"), row("MRR"), row("Monthly burn")
    out = {"asOf": as_of, "cash": cash, "mrr": mrr, "burn": burn,
           "cashTBD": bool(cash and "TBD" in cash.upper()), "daysSinceAsOf": None,
           "runwayMonths": None}
    if as_of:
        try:
            out["daysSinceAsOf"] = (today - datetime.date.fromisoformat(as_of)).days
        except ValueError:
            pass
    if not out["cashTBD"]:
        def num(s):
            n = re.search(r"([\d,]+(?:\.\d+)?)", s or "")
            return float(n.group(1).replace(",", "")) if n else None
        c, b = num(cash), num(burn)
        if c is not None and b:
            out["runwayMonths"] = round(c / b, 1)
    return out


# loops whose owner can't be parsed from a runtime/prompts/<key>.md "You are <Name>" first line
LOOP_AGENT_FALLBACK = {"demo-prep": "reilly", "sadie-intent": "sadie",
                       "agent-registry": "rafi", "runtime-alarm": "atlas"}
_loop_agent_cache = {}


def _loop_agent(key):
    """Timer key -> owning agent slug (lowercase), from the loop prompt's 'You are <Name>' line."""
    if key not in _loop_agent_cache:
        m = re.match(r"You are (\w+),", _read(f"runtime/prompts/{key}.md"))
        _loop_agent_cache[key] = m.group(1).lower() if m else LOOP_AGENT_FALLBACK.get(key)
    return _loop_agent_cache[key]


def _md_cell(s):
    """Roster table cell -> readable plain text (strip bold/links, keep paths + arrows)."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s or "")
    return re.sub(r"\*+", "", s).strip()


# The roster's Name column carries population tags — "**Atlas**<br/>🏠 **internal**". Everything
# from the <br/> on is a tag, not a name. Left unstripped it produced keys like
# "atlas<br/>🏠 internal", which silently broke the loop->agent join for EVERY agent: _loop_agent
# returns "brett", agentDetail was keyed "brett<br/>🏠 internal", nothing matched, and the Agents
# tab's recent/upcoming panels rendered empty for the whole roster without erroring once.
TAG_RE = re.compile(r"<br\s*/?>.*$", re.S | re.I)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿️‍]+")


def _agent_name(cell):
    """The Name cell -> just the name. Tags, emoji and markup removed."""
    s = TAG_RE.sub("", cell or "")
    s = EMOJI_RE.sub("", _md_cell(s))
    return re.sub(r"\s+", " ", s).strip(" -—·")


def _roster():
    """04_agent_roster.md tables -> {slug: responsibilities}. Current table: Name/Role/Trigger/
    Scope/Gate/Status. Planned table: Name/Role/Build-when/Scope/Notes."""
    txt = _read("04_agent_roster.md")
    out = {}

    def rows(section):
        m = re.search(section + r".*?\n((?:\|.*\n)+)", txt, re.S)
        return m.group(1).splitlines()[2:] if m else []

    for line in rows(r"## Current agents"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        name = _agent_name(c[0]) if c else ""
        if name and len(c) >= 6:
            out[name.lower()] = {"name": name, "planned": False, "role": _md_cell(c[1]),
                                 "trigger": _md_cell(c[2]), "scope": _md_cell(c[3]),
                                 "gate": _md_cell(c[4]), "statusNote": _md_cell(c[5])}
    for line in rows(r"## Planned agents"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        name = _agent_name(c[0]) if c else ""
        if name and len(c) >= 5 and name.lower() not in out:
            out[name.lower()] = {"name": name, "planned": True, "role": _md_cell(c[1]),
                                 "trigger": _md_cell(c[2]), "scope": _md_cell(c[3]),
                                 "gate": "", "statusNote": _md_cell(c[4])}
    return out


def _agent_detail(today, loops):
    """Per-agent drill-down for the HQ Agents tab: responsibilities (roster), recently completed
    (loop artifacts + slack-command commits, 14d), pending/upcoming (armed loops + activation
    trigger for dormant agents). Keyed by lowercase agent name."""
    detail = _roster()
    by_agent = {}
    for l in loops:
        if l["kind"] != "internal":
            continue
        slug = _loop_agent(l["loop"])
        if slug:
            by_agent.setdefault(slug, []).append(l)
    try:
        log = subprocess.run(["git", "log", "--since=14 days ago", "--format=%ad|%s",
                              "--date=short"], cwd=ROOT, capture_output=True, text=True,
                             timeout=10).stdout.splitlines()
    except Exception:
        log = []
    for slug, d in detail.items():
        # recent: last dated artifacts across this agent's loops (what actually ran)
        recent = []
        for l in by_agent.get(slug, []):
            adir = os.path.join(ROOT, "loops", ARTIFACT_DIR.get(l["loop"], l["loop"]))
            if os.path.isdir(adir):
                dated = sorted(f for f in os.listdir(adir) if DATE_RE.match(f))
                for f in dated[-3:]:
                    recent.append({"date": f[:10], "what": f"{l['loop']} run",
                                   "path": f"loops/{ARTIFACT_DIR.get(l['loop'], l['loop'])}/{f}"})
        # + Slack-commanded work committed by the listener ("slack:<agent> ..." subjects)
        for line in log:
            date, _, subj = line.partition("|")
            if subj.startswith(f"slack:{slug} "):
                recent.append({"date": date, "what": "Slack command completed (committed)",
                               "path": None})
        recent.sort(key=lambda r: r["date"], reverse=True)
        d["recent"] = recent[:8]
        # upcoming: armed loops with schedule + health; dormant agents show their activation trigger
        d["loops"] = [{"loop": l["loop"], "cadence": l["cadence"], "schedule": l["schedule"],
                       "lastArtifact": l["lastArtifact"], "health": l["health"], "note": l["note"]}
                      for l in by_agent.get(slug, [])]
        d["upcoming"] = [{"what": f"{l['loop']} ({l['cadence']})", "when": l["schedule"],
                          "health": l["health"]} for l in by_agent.get(slug, [])]
        if not d["upcoming"] and d.get("trigger"):
            t = d["trigger"]
            if not re.match(r"(?i)activates|scheduled|build when", t):
                t = ("activates when: " if d["planned"] else "runs when: ") + t
            d["upcoming"] = [{"what": t, "when": "", "health": ""}]
    return detail


def _git():
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    subjects = run("log", "--since=7 days ago", "--format=%s").splitlines()
    loop_commits = sum(1 for s in subjects if s.startswith("loop:"))
    return {"commits7d": len(subjects), "loopCommits7d": loop_commits,
            "humanCommits7d": len(subjects) - loop_commits,
            "lastCommit": run("log", "-1", "--format=%h %ad %s", "--date=short")}


def _biz_days(from_iso, to_iso):
    """Business days from the day after from_iso through to_iso (mirrors the CRM's bizDaysBetween)."""
    try:
        a = datetime.date.fromisoformat(from_iso); b = datetime.date.fromisoformat(to_iso)
    except (ValueError, TypeError):
        return None
    n, t = 0, a + datetime.timedelta(days=1)
    while t <= b:
        if t.weekday() < 5:
            n += 1
        t += datetime.timedelta(days=1)
    return n


def _intro_sla(today):
    """Referred-intro response health from the CRM (the connector program's ≤1-biz-day SLA).
    What the Founder+Partner B measure they keep fast — and 'we respond same-day' is a connector recruiting line."""
    try:
        crm = json.load(open(os.path.join(ROOT, "crm", "data.json")))
    except (OSError, json.JSONDecodeError):
        return {"referred": 0}
    deals = {d.get("companyId"): d for d in crm.get("deals", [])}
    acts = crm.get("activities", [])
    t_iso = today.isoformat()
    referred = waiting = blown = 0
    resp_days = []
    for c in crm.get("companies", []):
        if not ((c.get("referrer") or "").strip() or c.get("referredByCompany")):
            continue
        rd = c.get("referredDate")
        if not rd:
            continue
        referred += 1
        touches = [a["date"] for a in acts if a.get("companyId") == c.get("id") and (a.get("date") or "") >= rd]
        d = deals.get(c.get("id"))
        if d and (d.get("lastTouch") or "") >= rd:
            touches.append(d["lastTouch"])
        if touches:
            resp_days.append(_biz_days(rd, min(touches)) or 0)
        else:
            waiting += 1
            if (_biz_days(rd, t_iso) or 0) > 1:
                blown += 1
    resp_days.sort()
    median = resp_days[len(resp_days) // 2] if resp_days else None
    return {"referred": referred, "waiting": waiting, "slaBlown": blown,
            "medianRespBizDays": median, "responded": len(resp_days)}


def derive(today=None):
    today = today or datetime.date.today()
    loops = _loops(today)
    internal = [l for l in loops if l["kind"] == "internal"]
    tracked = [l for l in internal if l["health"] in ("on-time", "stale", "never")]
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        # The switch comes FIRST because it reframes everything under it: if the runtime is
        # paused, "17 stale" is not a fault report, it is the expected consequence of one file.
        "runtimeSwitch": runtime_switch(),
        "loops": loops,
        "loopSummary": {
            "built": len(internal),
            "tracked": len(tracked),
            "onTime": sum(1 for l in tracked if l["health"] == "on-time"),
            "stale": sum(1 for l in tracked if l["health"] == "stale"),
            "neverRan": sum(1 for l in tracked if l["health"] == "never"),
            # Of the stale ones, how many fired anyway and wrote nothing? That is a real bug;
            # a paused skip is not. Resolvable only on the runtime box — 0 elsewhere, not "none".
            "firedNoOutput": sum(1 for l in tracked if l.get("ranWithoutOutput")),
        },
        "agentDetail": _agent_detail(today, loops),
        "autonomy": _autonomy(),
        "gates": _gates(),
        "needsFounder": _needs_founder(today),
        "introSla": _intro_sla(today),
        "watchdogs": _watchdogs(),
        "runway": _runway(today),
        "git": _git(),
        "source": "derived from runtime/systemd + loops/ artifacts + autonomy-matrix + gate trackers "
                  "+ open-loops queue + consistency/governance reports + finance/runway.md + git",
    }


if __name__ == "__main__":
    d = derive()
    path = os.path.join(DATA_DIR, "data.json")
    with open(path) as f:
        data = json.load(f)
    data["derived"] = d
    data.setdefault("meta", {})["derivedAt"] = d["generatedAt"]
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    s = d["loopSummary"]
    print(f"derived -> data.json  loops: {s['onTime']} on-time / {s['stale']} stale / "
          f"{s['neverRan']} never (of {s['built']} built)  gates: OtherVenture='{d['gates']['OtherVenture'][:40]}' "
          f"counsel {d['gates']['counsel']['cleared']}/{d['gates']['counsel']['total']} cleared  "
          f"git 7d: {d['git']['commits7d']} commits ({d['git']['loopCommits7d']} loop)")
    nk, wd, rw = d["needsFounder"], d["watchdogs"], d["runway"]
    print(f"  needs-the Founder: {(str(nk['total']) + ' items (' + str(nk['count']) + ' queue + ' + str(nk['seedCount']) + ' seed, ' + str(nk['date']) + ')') if nk else 'no queue artifact yet'}")
    print(f"  watchdogs: consistency={wd['consistency']['status']}"
          f"{'×' + str(wd['consistency'].get('count')) if wd['consistency']['status'] == 'drift' else ''}"
          f" governance={wd['governance']['status']}"
          f"{'×' + str(wd['governance'].get('count')) if wd['governance']['status'] == 'drift' else ''}")
    print(f"  runway: {('cash TBD — ' + str(rw['daysSinceAsOf']) + 'd since ' + str(rw['asOf'])) if rw and rw['cashTBD'] else ((rw['cash'] or '—') + ' cash · ' + (rw['mrr'] or '—') + ' MRR' if rw else 'no finance/runway.md')}")
    for l in d["loops"]:
        if l["health"] in ("stale", "never"):
            print(f"  ⚠ {l['loop']:<22} {l['health']:<6} {l['note']}")
