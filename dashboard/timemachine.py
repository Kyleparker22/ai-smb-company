#!/usr/bin/env python3
"""Time machine — HQ as of any past date, and `git blame` for business metrics.

Ordinary companies can't do this. Their numbers live in SaaS silos that keep a current
value and, at best, a chart; nobody can point at the exact change that moved one. yourco's
numbers live in a git repo, so every metric has a commit, an author, and a diff behind it.

TWO QUESTIONS IT ANSWERS

  as-of   "What did HQ say on 2026-07-01?"  Rebuilds the metric set from the repo as it
          stood at the last commit on or before that date.

  blame   "What moved MRR / pipeline value / deal count, and who did it?"  Walks the
          commits that touched the CRM, computes the metric at each one, and returns only
          the commits where it actually CHANGED — with the commit, the author, and the
          agent or human responsible. That change list is also the bisect answer: the
          commit where a number first went wrong is simply the first row past the good one.

NO FORKED MATH.  Historical documents are pushed through `server.goals_currents(crm=…)` and
`server.pipeline_summary(crm=…)` — the same functions the live dashboard calls. A number from
2026-07-01 and today's number are produced by one implementation, so a drift between "then"
and "now" is a real change in the business and never an artifact of two code paths.

ATTRIBUTION.  Commit subjects carry the convention already in use: `loop:` = a runtime loop,
`slack:<agent>` = an agent acting on a Slack command, anything else = a human session. The
`actor` field reports which, so "who moved this number" is answered from the repo's own
record rather than guessed.

HONESTY.  A revision where the file didn't exist yet returns `absent`, not zero — the CRM
was created on some commit, and before it, "MRR was 0" would be a fabrication about a
company that hadn't started measuring. Git failures surface as errors, never as empty data.

Read-only. Exposed as GET /api/timemachine and GET /api/blame.
"""
import os, re, sys, json, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CRM_PATH = "crm/data.json"
MAX_COMMITS = 150       # bounded walk — a runaway history can't stall the dashboard poll
GIT_TIMEOUT = 20

_show_cache = {}        # sha -> parsed CRM doc (or None). Immutable by definition, so safe forever.
_build_cache = {}       # (kind, arg) -> (built_at, payload)
CACHE_TTL = 300


def _git(*args, timeout=GIT_TIMEOUT):
    try:
        p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                           timeout=timeout)
        return p.stdout if p.returncode == 0 else None
    except Exception:
        return None


def _crm_at(sha):
    """The CRM document as of a commit. None = the file did not exist there (or git failed)."""
    if sha in _show_cache:
        return _show_cache[sha]
    raw = _git("show", f"{sha}:{CRM_PATH}")
    doc = None
    if raw:
        try:
            doc = json.loads(raw)
        except ValueError:
            doc = None
    _show_cache[sha] = doc
    return doc


def _crm_at_many(shas):
    """Fetch many revisions of the CRM in ONE `git cat-file --batch` process.

    The obvious implementation — `git show <sha>:path` per commit — spawns a process per
    revision and made a 56-commit blame take ~20s on a cold pack. One batch call does the
    same work in a single read. Results land in the same cache `_crm_at` uses."""
    want = [s for s in shas if s not in _show_cache]
    if not want:
        return
    stdin = "".join(f"{s}:{CRM_PATH}\n" for s in want)
    try:
        p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=stdin.encode(),
                           capture_output=True, timeout=90)
        if p.returncode != 0:
            return  # leave uncached; callers fall back to _crm_at one at a time
        out = p.stdout
    except Exception:
        return

    pos, i = 0, 0
    while pos < len(out) and i < len(want):
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].decode("utf-8", "replace").split()
        pos = nl + 1
        # "<oid> missing" (or "<input> missing") -> the file didn't exist at that revision
        if len(header) < 3 or header[-1] == "missing":
            _show_cache[want[i]] = None
            i += 1
            continue
        try:
            size = int(header[2])
        except ValueError:
            break
        body, pos = out[pos:pos + size], pos + size + 1  # +1 for the trailing newline
        try:
            _show_cache[want[i]] = json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            _show_cache[want[i]] = None
        i += 1
    for s in want[i:]:  # anything the batch didn't cover stays uncached, never wrongly None
        _show_cache.pop(s, None)


def _actor(subject, author):
    """Who moved it. The repo's own commit conventions, not a guess."""
    s = (subject or "").strip()
    m = re.match(r"^slack:([a-z]+)\b", s)
    if m:
        return {"kind": "agent", "who": m.group(1), "via": "Slack command"}
    if s.startswith("loop:"):
        m = re.match(r"^loop:\s*([a-z0-9-]+)", s)
        return {"kind": "loop", "who": m.group(1) if m else "runtime", "via": "runtime loop"}
    return {"kind": "human", "who": author or "the Founder", "via": "working session"}


def _commits_touching(path, since=None, limit=MAX_COMMITS):
    args = ["log", f"--max-count={limit}", "--date=short", "--format=%H\x1f%ad\x1f%an\x1f%s"]
    if since:
        args.append(f"--since={since}")
    args += ["--", path]
    out = _git(*args)
    if out is None:
        return None
    rows = []
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 4:
            rows.append({"sha": parts[0], "date": parts[1], "author": parts[2], "subject": parts[3]})
    rows.reverse()  # oldest first — a change list reads forward in time
    return rows


# ---- metrics, computed by the LIVE functions --------------------------------
METRICS = [
    ("mrr", "MRR", "$"), ("liveClients", "Live clients", ""),
    ("dealsInMotion", "Deals in motion", ""), ("newProspects", "Bench / prospects", ""),
    ("referredMRR", "Referred MRR", "$"), ("activeConnectors", "Active connectors", ""),
    ("prospectiveConnectors", "Connector prospects", ""),
    ("pipelineValue", "Pipeline value", "$"), ("companies", "Companies", ""),
    ("contacts", "Contacts", ""),
]
METRIC_KEYS = [m[0] for m in METRICS]


def _metrics_from(crm):
    """One CRM document -> the metric set, via the same functions HQ renders from."""
    import server
    cur = server.goals_currents(crm)
    pipe = server.pipeline_summary(crm) or {}
    out = {k: cur.get(k) for k in
           ("mrr", "liveClients", "dealsInMotion", "newProspects", "referredMRR",
            "activeConnectors", "prospectiveConnectors")}
    out["pipelineValue"] = pipe.get("value")
    out["companies"] = pipe.get("companies")
    out["contacts"] = pipe.get("contacts")
    out["byStage"] = pipe.get("byStage")
    return out


# ---- repo shape (the company's size on that day) ---------------------------
SHAPE = [("decisions", r"^decisions/\d{4}-.*\.md$"),
         ("clients", r"^clients/[^_/][^/]*/_README\.md$"),
         ("loopArtifacts", r"^loops/[^/]+/\d{4}-\d{2}-\d{2}.*\.md$"),
         ("skills", r"^\.claude/skills/[^/]+/SKILL\.md$"),
         ("runtimeLoops", r"^runtime/systemd/.*\.timer$")]


def _shape_at(sha):
    # generous timeout: a full recursive tree read off a cold pack is slow the first time
    out = _git("ls-tree", "-r", "--name-only", sha, timeout=90)
    if out is None:
        return None
    names = out.splitlines()
    return {label: sum(1 for n in names if re.match(rx, n)) for label, rx in SHAPE}


# ---- as-of ------------------------------------------------------------------
def as_of(date):
    """HQ's numbers at the last commit on or before `date` (YYYY-MM-DD)."""
    try:
        datetime.date.fromisoformat(date)
    except (ValueError, TypeError):
        return {"error": "date must be YYYY-MM-DD"}
    key = ("asof", date)
    hit = _build_cache.get(key)
    if hit and (datetime.datetime.now() - hit[0]).total_seconds() < CACHE_TTL:
        return hit[1]

    # --before is exclusive of later times on the day, so ask for the end of that day
    sha = (_git("rev-list", "-1", f"--before={date} 23:59:59", "HEAD") or "").strip()
    if not sha:
        out = {"error": f"no commit on or before {date} — the repo starts later than that"}
        _build_cache[key] = (datetime.datetime.now(), out)
        return out
    info = (_git("log", "-1", "--date=short", "--format=%ad\x1f%an\x1f%s", sha) or "").split("\x1f")
    crm = _crm_at(sha)
    payload = {
        "date": date,
        "commit": {"sha": sha[:9], "date": info[0] if info else None,
                   "author": info[1] if len(info) > 1 else None,
                   "subject": info[2].strip() if len(info) > 2 else None},
        "shape": _shape_at(sha),
        "metrics": None,
        "absent": crm is None,
        "note": None,
    }
    if payload["shape"] is None:  # a failed tree read is said out loud, not left as a blank
        payload["shapeNote"] = "repo shape unavailable — the tree read failed or timed out"
    if crm is None:
        payload["note"] = (f"{CRM_PATH} does not exist at this revision. That is reported as "
                           f"absent, not as zero — the company had not started measuring yet, "
                           f"and a zero here would be a fabrication.")
    else:
        payload["metrics"] = _metrics_from(crm)
    today = datetime.date.today().isoformat()
    if date < today:
        live = _crm_at("HEAD")
        payload["today"] = _metrics_from(live) if live else None
    _build_cache[key] = (datetime.datetime.now(), payload)
    return payload


# ---- blame ------------------------------------------------------------------
def blame(metric="mrr", since=None, limit=MAX_COMMITS):
    """Every commit where `metric` actually changed — the business-metric equivalent of
    `git blame`, and the bisect answer for "when did this break?"."""
    if metric not in METRIC_KEYS:
        return {"error": f"unknown metric '{metric}'", "metrics": METRIC_KEYS}
    key = ("blame", metric, since, limit)
    hit = _build_cache.get(key)
    if hit and (datetime.datetime.now() - hit[0]).total_seconds() < CACHE_TTL:
        return hit[1]

    commits = _commits_touching(CRM_PATH, since, limit)
    if commits is None:
        return {"error": "git unavailable — history could not be read"}

    _crm_at_many([c["sha"] for c in commits])  # one batch read instead of N subprocesses
    changes, prev, series, walked = [], None, [], 0
    for c in commits:
        crm = _crm_at(c["sha"])
        if crm is None:
            continue
        walked += 1
        try:
            v = _metrics_from(crm).get(metric)
        except Exception:
            continue
        series.append({"date": c["date"], "value": v})
        if prev is None:
            prev = v
            changes.append({**c, "sha": c["sha"][:9], "from": None, "to": v,
                            "delta": None, "actor": _actor(c["subject"], c["author"]),
                            "first": True})
            continue
        if v != prev:
            delta = (v - prev) if isinstance(v, (int, float)) and isinstance(prev, (int, float)) else None
            changes.append({**c, "sha": c["sha"][:9], "from": prev, "to": v, "delta": delta,
                            "actor": _actor(c["subject"], c["author"]), "first": False})
            prev = v

    label = next((m[1] for m in METRICS if m[0] == metric), metric)
    unit = next((m[2] for m in METRICS if m[0] == metric), "")
    out = {
        "metric": metric, "label": label, "unit": unit,
        "commitsWalked": walked,
        "commitsWithFile": len(commits),
        "truncated": len(commits) >= limit,
        "changes": list(reversed(changes)),   # newest first for reading
        "series": series,
        "current": series[-1]["value"] if series else None,
        "note": ("Only commits where the value CHANGED are listed; the CRM is touched far more "
                 "often than any single metric moves. 'first' marks the earliest revision walked, "
                 "which is a starting point, not a change."),
        "available": [{"key": k, "label": l, "unit": u} for k, l, u in METRICS],
    }
    if out["truncated"]:
        out["note"] += (f" Walk capped at {limit} commits touching {CRM_PATH} — anything older "
                        f"is NOT included, so an unchanged-looking history may simply be cut off.")
    _build_cache[key] = (datetime.datetime.now(), out)
    return out


def _repo_start():
    """Date of the root commit — the day this OS started existing."""
    root = (_git("rev-list", "--max-parents=0", "HEAD") or "").split()
    if not root:
        return None
    return (_git("log", "-1", "--date=short", "--format=%ad", root[-1]) or "").strip() or None


def build(date=None, metric="mrr"):
    """The combined payload HQ's Time Machine panel renders."""
    date = date or (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "asOf": as_of(date),
        "blame": blame(metric),
        "metrics": [{"key": k, "label": l, "unit": u} for k, l, u in METRICS],
        # the ROOT commit's date. `log --reverse --max-count=1` looks right and isn't:
        # git applies max-count before reversing, so it returns the NEWEST commit.
        "repoStart": _repo_start(),
    }


if __name__ == "__main__":
    a = sys.argv[1:]
    d = a[0] if a and re.match(r"^\d{4}-\d{2}-\d{2}$", a[0]) else "2026-07-01"
    m = a[1] if len(a) > 1 else "pipelineValue"
    snap = as_of(d)
    print(f"HQ AS OF {d} — commit {snap.get('commit', {}).get('sha')} "
          f"({snap.get('commit', {}).get('date')})")
    if snap.get("error"):
        print("  " + snap["error"])
    elif snap["absent"]:
        print("  " + snap["note"])
    else:
        for k, label, unit in METRICS:
            then, now = snap["metrics"].get(k), (snap.get("today") or {}).get(k)
            print(f"  {label:<22} {unit}{then}" + (f"   ->  today {unit}{now}" if now is not None else ""))
        print(f"  repo shape: {snap['shape']}")
    b = blame(m)
    print(f"\nBLAME — {b.get('label', m)}  ({b.get('commitsWalked')} revisions walked)")
    for c in (b.get("changes") or [])[:12]:
        arrow = "start" if c["first"] else f"{c['from']} -> {c['to']}"
        print(f"  {c['date']}  {arrow:<22} {c['actor']['kind']}:{c['actor']['who']:<12} {c['subject'][:64]}")
