#!/usr/bin/env python3
"""The Board — one inventory of every open item in the OS, computed live.

the Founder's question this answers: "what still needs to be worked on, what doesn't, and
what needs to be added?"  Before this, the answer lived in eight places and half of
them were stale (open-loops 9d, gap-audit 56d, todo.json empty).

DESIGN RULE — nothing here is hand-maintained.  Every item is derived from a file
that some other owner already keeps current, so the Board cannot rot independently
of its sources.  When a source IS stale, that is shown as a fact (see `sources`),
never hidden: the 2026-08-07 gap audit's core finding is that this OS fails by not
noticing absence, so absence is rendered, not swallowed.

Sources
  loops/open-loops/<latest>.md ....... Jim's human-action queue + the parked inventory
  loops/gap-audit/<latest>.md ........ what should exist but doesn't
  processes/counsel-gates.md ......... every legal blocker
  processes/launch-gate.md .......... the master launch gate
  crm/data.json ...................... deals in motion, bench, open tasks
  crm/_backlog.md .................... David's unscheduled CRM builds
  processes/automation-roadmap.md .... unbuilt automations
  offerings/_frontier-roadmap.md ..... the Frontier Ten status board
  loops/*/ + runtime/agent-registry.json ... loop liveness (days since last artifact)

Read-only.  Never writes.  Exposed as GET /api/board.
"""
import os, re, json, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: YOURCO_DATA_ROOT redirects every source read below to the sandbox tree.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))

LANES = ["Commercial", "Money", "Legal", "System", "Build", "Clients"]
# states, in the order a founder should triage them
STATES = ["needs-you", "blocked", "missing", "backlog", "parked"]

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
REPORT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(_[a-z0-9-]+)?\.md$")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿️‍]+")


def today():
    return datetime.date.today()


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _load(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _mtime_date(rel):
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, rel)))
    except OSError:
        return None


def _age(d):
    """Days between an ISO date (or date object) and today. None if unparseable."""
    if not d:
        return None
    if isinstance(d, str):
        m = DATE_RE.search(d)
        if not m:
            return None
        try:
            d = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            return None
    return (today() - d).days


def _clean(s):
    """Markdown cell -> plain text: drop emoji, bold/italic markers, links, footnote parens."""
    s = EMOJI_RE.sub("", s or "")
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip(" *_")


def _rest(s):
    """A cell with its leading **bold headline** removed — the detail, minus the title the row
    already shows. Without this every open-loops row printed its own title twice."""
    body = re.sub(r"^\s*\*\*.+?\*\*\s*", "", s or "", count=1)   # the headline
    body = re.sub(r"^\s*\*\([^)]*\)\*\s*", "", body, count=1)    # a *(Owner, when)* aside
    body = re.sub(r"^\s*[—:.\-–]+\s*", "", body)                 # the separator left behind
    return _clean(body) or _clean(s)


def _bold(s):
    """First **bold** run in a cell — the item's headline. Falls back to the first sentence."""
    m = re.search(r"\*\*(.+?)\*\*", s or "")
    if m:
        return _clean(m.group(1)).rstrip(".—- ")
    # No bold: keep the whole cell. Splitting on the em-dash here collapsed two distinct
    # counsel gates ("Sample Product — data reselling" and "— partnership terms") to one title.
    return _clean(s)[:120]


def _sev(cell):
    """Severity from the house emoji convention, highest wins."""
    if "🔴🔴" in cell:
        return "critical"
    if "🔴" in cell:
        return "high"
    if "🟠" in cell:
        return "med"
    if "🟡" in cell:
        return "low"
    return "none"


def _tables(md, heading_re):
    """Every pipe-table under the first heading matching heading_re, as lists of cells.
    Stops at the next heading of the same-or-shallower level."""
    lines = md.splitlines()
    start = None
    level = 2
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{2,4})\s*(.+)$", ln)
        if m and re.search(heading_re, m.group(2), re.I):
            start, level = i + 1, len(m.group(1))
            break
    if start is None:
        return []
    rows = []
    for ln in lines[start:]:
        m = re.match(r"^(#{2,4})\s", ln)
        if m and len(m.group(1)) <= level:
            break
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue  # separator
        rows.append(cells)
    return rows[1:] if rows else []  # drop the header row


# --------------------------------------------------------------------------
# Owners — who of the three partners, added 2026-08-10
#
# Until membership went to three (the Founder / Partner B / Mike, 50/35/15) the Board's owner field was
# decoration: every "needs-you" meant the Founder, and the string said so. With three partners the
# same board silently asserts a single-founder company. This layer makes the human dimension
# real, and it is the ONE place where a hand-maintained input is correct: a partner assignment
# is a decision, not a derivable fact — so it rides an overlay (same shape as goals.json:
# human targets, derived currents), and an assignment whose item has gone is reported stale
# rather than quietly kept.
# --------------------------------------------------------------------------
PARTNERS = {"the Founder": "the Founder", "Partner B": "Partner B", "mike": "Mike"}
ASSIGNMENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assignments.json")


def item_key(title):
    """Content-derived, stable id for an assignment to bind to.

    The `id` field is positional for several sources ("ol-2" is the queue's row 2), so it
    renames itself whenever the queue reorders. A title hash survives reordering; if the title
    is edited the assignment shows up as stale, which is the honest outcome — it IS a different
    item now, and silently re-pointing it would be a guess."""
    norm = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", (title or "").lower())).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:10]


_agent_names = None


def _agents():
    """Roster agent names, lowercased — so an item owned by David or Reilly is reported as
    agent-owned rather than lumped in with genuinely ownerless work. Those are different
    problems: one is delegated, the other is dropped."""
    global _agent_names
    if _agent_names is None:
        d = _load("dashboard/data.json") or {}
        _agent_names = {(a.get("name") or "").split()[0].lower()
                        for a in (d.get("agents") or []) if a.get("name")}
        _agent_names.discard("")
    return _agent_names


def _owner_keys(owner):
    """An owner string -> the partners named in it. 'Ray / the Founder' -> ['the Founder'] (Ray is an
    agent); 'Kemba / platform' -> [] (no partner). Word-boundary matched so 'Reed' the
    video agent is never read as 'Partner B' the partner — they differ by two letters and one of
    them is a person who owns 35% of the company."""
    s = (owner or "").lower()
    return [k for k in PARTNERS if re.search(r"\b" + k + r"\b", s)]


def _owner_agents(owner):
    """Roster agents named in an owner string."""
    s = (owner or "").lower()
    return sorted(a for a in _agents() if re.search(r"\b" + re.escape(a) + r"\b", s))


def load_assignments():
    """{itemKey: {to, note, at}} — normalized, unknown partners dropped."""
    d = _load(os.path.relpath(ASSIGNMENTS, ROOT)) or {}
    out = {}
    for k, v in (d.get("assignments") or {}).items():
        if not isinstance(v, dict):
            continue
        to = str(v.get("to") or "").lower()
        if to not in PARTNERS:
            continue
        out[str(k)[:20]] = {"to": to, "note": str(v.get("note") or "")[:300],
                            "at": str(v.get("at") or "")[:10]}
    return out


def save_assignment(key, to, note=""):
    """Set (or clear, with to=None) one assignment. Atomic write; returns the full map."""
    d = _load(os.path.relpath(ASSIGNMENTS, ROOT)) or {}
    if not isinstance(d.get("assignments"), dict):
        d = {"_readme": "Partner assignments for The Board, keyed by board.item_key(title). "
                        "Hand-maintained on purpose — who owns a thing is a decision, not a "
                        "derivable fact. Everything else on the Board stays derived.",
             "assignments": {}}
    key = str(key)[:20]
    if to is None:
        d["assignments"].pop(key, None)
    else:
        if str(to).lower() not in PARTNERS:
            raise ValueError("unknown partner")
        d["assignments"][key] = {"to": str(to).lower(), "note": str(note or "")[:300],
                                 "at": today().isoformat()}
    d["updated"] = today().isoformat()
    tmp = ASSIGNMENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, ASSIGNMENTS)
    return load_assignments()


def _item(**kw):
    kw.setdefault("sev", "none")
    kw.setdefault("owner", "the Founder")
    kw.setdefault("age", None)
    kw.setdefault("next", "")
    kw.setdefault("detail", "")
    return kw


# --------------------------------------------------------------------------
# 1. Open loops — the human-action queue (Jim)
# --------------------------------------------------------------------------
def _latest_report(folder):
    """(stem, relpath) of the newest dated artifact in a loops/ dir, or (None, None)."""
    p = os.path.join(ROOT, folder)
    try:
        names = [f for f in os.listdir(p) if REPORT_RE.match(f)]
    except OSError:
        return None, None
    if not names:
        return None, None
    # bare 2026-08-07.md wins a same-day tie over 2026-08-07_suffixed.md
    names.sort(key=lambda s: (s[:10], len(s) == 13, s), reverse=True)
    return names[0][:-3], os.path.join(folder, names[0])


def open_loops():
    """-> (items, stem, mentioned_ids). `mentioned_ids` is every CRM deal/task id the queue
    already names (d29, t_2fa, …) so the CRM pass doesn't re-report the same item twice —
    Jim's write-up is the richer of the two, so it wins."""
    stem, rel = _latest_report("loops/open-loops")
    if not rel:
        return [], None, set()
    md = _read(rel)
    mentioned = set(re.findall(r"\b(?:d\d{1,3}|t_[a-z0-9_]+)\b", md))
    out = []
    # The queue: | # | Item | Whose | Waiting since | Age | Next step |
    for r in _tables(md, r"the queue"):
        if len(r) < 6:
            continue
        num, item, whose, since, _age_col, nxt = r[0], r[1], r[2], r[3], r[4], r[5]
        if not _clean(item):
            continue
        out.append(_item(
            id="ol-" + re.sub(r"\D", "", num or "0"),
            title=_bold(item),
            detail=_rest(item),
            lane=_lane_for(item + " " + nxt),
            state="needs-you",
            owner=_clean(whose) or "the Founder",
            since=_clean(since),
            age=_age(since),
            next=_clean(nxt),
            sev=_sev(num),
            source=rel,
        ))
    # Parked by decision: | Parked item | The gate | What would unpark it |
    for r in _tables(md, r"parked by decision"):
        if len(r) < 3 or not _clean(r[0]):
            continue
        out.append(_item(
            id="pk-" + re.sub(r"[^a-z0-9]+", "-", _clean(r[0]).lower())[:32],
            title=_bold(r[0]),
            detail="Parked by: " + _clean(r[1]),
            lane=_lane_for(r[0] + " " + r[1]),
            state="parked",
            owner="—",
            since="",
            next=_clean(r[2]),
            source=rel,
        ))
    return out, stem, mentioned


# --------------------------------------------------------------------------
# 2. Gap audit — what should exist but doesn't
# --------------------------------------------------------------------------
def gap_audit():
    """Only the audit's 'Verdict — build order' is read.

    Deliberately NOT parsed: the sweep tables. Sweep 1 rows carry both their June marker and
    their August one, so a 🔴-in-June/✅-CLOSED-in-August row reads as an open gap unless you
    track column positions that shift between runs — three closed stages were reported missing
    before this was narrowed. Sweep 3 is mechanical, and system_items() computes those same
    facts live from the repo, which cannot go stale between audits. The verdict is the audit's
    own distillation of what's left, in priority order, and it is the durable contract."""
    stem, rel = _latest_report("loops/gap-audit")
    if not rel:
        return [], None
    md = _read(rel)
    out = []
    m = re.search(r"^##\s*Verdict.*$", md, re.M)
    if not m:
        return out, stem
    tail = md[m.end():].split("\n## ")[0]
    for n, line in enumerate(re.findall(r"^\d+\.\s+(.+)$", tail, re.M), 1):
        title = _bold(line)
        if not title:
            continue
        owner = re.search(r"\*\(([^,)]+)", line)  # the *(Owner, when)* aside
        out.append(_item(
            id="gv-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:32],
            title=title,
            detail=_rest(line),
            lane=_lane_for(line),
            state="missing",
            owner=_clean(owner.group(1)) if owner else "the Founder",
            since="",
            next=f"Gap-audit build order #{n}.",
            sev="high" if n <= 3 else "med",
            source=rel,
        ))
    return out, stem


# --------------------------------------------------------------------------
# 3. Legal gates
# --------------------------------------------------------------------------
def gates():
    out = []
    md = _read("processes/counsel-gates.md")
    for r in _tables(md, r"^the gates"):
        if len(r) < 4 or not _clean(r[1]):
            continue
        status = r[3]
        if "✅" in status:
            continue  # cleared gates are not open items
        out.append(_item(
            id="cg-" + re.sub(r"\D", "", r[0] or "0"),
            title=_bold(r[1]),
            detail=("Blocks: " + _clean(r[2])) if len(r) > 2 else "",
            lane="Legal",
            state="blocked",
            owner="Ray / the Founder",
            since="",
            next=_clean(status),
            sev="critical" if "🔴" in status else ("med" if "🟠" in status else "low"),
            source="processes/counsel-gates.md",
        ))

    # OtherVenture — the master gate. Its own scope/resolution fields being unfilled IS the finding.
    ok = _read("processes/launch-gate.md")
    if ok:
        open_gate = "🔴" in ok
        # Both markers. The 2026-08-25 rewrite replaced "*the Founder to fill" with a louder
        # "UNRECORDED — the Founder only" and silently blinded this counter AND the consistency check —
        # one reworded string, two readers. Matching on either is the cheap insurance.
        unfilled = ok.count("*the Founder to fill") + len(re.findall(r"UNRECORDED\s*[\u2014-]\s*the Founder only", ok))
        out.append(_item(
            id="cg-OtherVenture",
            title="launch-gate — the master launch gate",
            detail=(f"Blocks every external surface (site, outbound, partnerships, press, social) — "
                    f"26 staged pages, 61 booking links, 34 bench companies, and 3 agents' owned "
                    f"numbers that cannot become non-zero until it lifts. "
                    f"{unfilled} of its own fields are still unrecorded: what the gate IS, and what "
                    f"would clear it. Until the second one exists, 'cleared' is not a testable state "
                    f"and no one in the OS can say what would lift it."
                    if unfilled else "Blocks every external surface."),
            lane="Legal",
            state="blocked" if open_gate else "parked",
            owner="the Founder",
            since="2026-06-12",
            age=_age("2026-06-12"),
            next="Fill the gate definition + resolution condition, then re-estimate.",
            sev="critical",
            source="processes/launch-gate.md",
        ))
    return out


# --------------------------------------------------------------------------
# 4. CRM — deals in motion, the untouched bench, open tasks
# --------------------------------------------------------------------------
BENCH = {"relationship", "parked", "prospect"}
CLOSED = {"live", "expand"}
STALE_DAYS = 14


def crm_items(covered=frozenset()):
    """`covered` = deal/task ids the open-loops queue already reports; skipped here so the
    Board shows one row per real-world item rather than one per source that mentions it."""
    crm = _load("crm/data.json")
    if not crm:
        return []
    labels = {s.get("key"): s.get("label", s.get("key")) for s in crm.get("stages", []) or []}
    comp = {c.get("id"): c.get("name", "") for c in crm.get("companies", []) or []}
    out, bench_cold = [], []

    for d in crm.get("deals", []) or []:
        stage = (d.get("stage") or "").lower()
        name = d.get("name") or comp.get(d.get("companyId")) or d.get("id")
        if d.get("id") in covered and stage not in BENCH:
            continue  # already surfaced, with more context, by the open-loops queue
        touch_age = _age(d.get("lastTouch"))
        due_age = _age(d.get("nextDate"))
        if stage in BENCH:
            # A bench deal with no touch at all, or a badly overdue date, is cold inventory.
            if touch_age is None or touch_age > 30 or (due_age is not None and due_age > 0):
                bench_cold.append((name, touch_age, due_age))
            continue
        if stage in CLOSED:
            continue
        overdue = due_age is not None and due_age > 0
        stale = touch_age is not None and touch_age > STALE_DAYS
        if not (overdue or stale or d.get("nextDate") in (None, "")):
            continue  # healthy, in motion, with a future date — nothing to surface
        bits = []
        if overdue:
            bits.append(f"next action {due_age}d past due")
        if stale:
            bits.append(f"last touch {touch_age}d ago")
        if not d.get("nextDate"):
            bits.append("no next date set")
        out.append(_item(
            id="deal-" + str(d.get("id")),
            title=f"{name}",
            detail=f"{labels.get(stage, stage)} — " + ", ".join(bits) + ".",
            lane="Clients" if stage in ("signed", "build") else "Commercial",
            state="needs-you",
            owner=d.get("owner") or "the Founder",
            since=d.get("lastTouch") or "",
            age=touch_age,
            next=_clean(d.get("nextAction") or ""),
            sev="high" if (overdue and due_age > 14) or (stale and touch_age > 30) else "med",
            source="crm/data.json",
        ))

    if bench_cold:
        oldest = max((a for _, a, _ in bench_cold if a is not None), default=None)
        never = sum(1 for _, a, _ in bench_cold if a is None)
        out.append(_item(
            id="deal-bench",
            title=f"{len(bench_cold)} warm relationships going cold",
            detail=(f"{never} have never been touched; "
                    f"oldest touch is {oldest}d ago. " if never else f"oldest touch is {oldest}d ago. ")
                   + "The warm network is the stated GTM motion (warm intros first, all industries).",
            lane="Commercial",
            state="needs-you",
            owner="the Founder / Reilly",
            since="",
            age=oldest,
            next="Work the bench or formally park it — 'not yet' at this age is a decision made by drift.",
            sev="high",
            source="crm/data.json",
        ))

    for t in crm.get("tasks", []) or []:
        if t.get("done") or t.get("id") in covered:
            continue
        due = t.get("due") or ""
        da = _age(due)
        out.append(_item(
            id="task-" + str(t.get("id")),
            title=_clean(t.get("title") or t.get("text") or t.get("id")),
            detail=(f"Task overdue by {da}d." if da and da > 0 else
                    ("Task with no due date — nothing will ever nag it." if not due else "Task open.")),
            lane="Commercial",
            state="needs-you",
            owner="the Founder",
            since=due,
            age=da,
            sev="med" if (da and da > 30) else "low",
            source="crm/data.json",
        ))
    return out


# --------------------------------------------------------------------------
# 5. System — loop liveness. The gap audit's #1 finding: silence must be visible.
# --------------------------------------------------------------------------
DETERMINISTIC = {"crm-hygiene", "sadie-intent", "agent-registry", "consistency",
                 "storm-alerts", "storm-publish", "runtime-alarm", "granola-crm-sync"}
SKIP_DIRS = {"_runtime", "_instantly", "_anthropic"}
# expected cadence in days, by loop-name fragment — anything else defaults to weekly
CADENCE = {"inbox-triage": 1, "open-loops": 1, "sadie": 1, "initiative": 1, "crm-autolog": 1,
           "melanie-briefing": 1, "customer-health": 7, "monday-briefing": 7, "watchdog": 7,
           "eval-review": 7, "sales": 7, "finance": 7, "content": 7, "source-watch": 7,
           "advisor": 14, "brett-ideas": 14, "pipeline-report": 7, "consistency": 7,
           "governance": 7, "aeo-geo": 30, "brand-audit": 30, "gap-audit": 30,
           "pricing-review": 90, "audit": 90, "advisory": 30}


def tripwire_items():
    """Decisions whose own stated expiry condition has now come true.

    Added 2026-08-24. `dashboard/tripwires.py` has evaluated these since 08-07 and had exactly one
    reader: the weekly evidence-sweep loop — which was paused. So on the day this was written a
    trip-wire had FIRED on the three-member partner split (its own check
    `counselGatesBlocked >= 6 and not OtherVentureCleared` had come true) and no surface a human opens
    said so. The Board is documented as "start here when the question is what still needs doing";
    a decision announcing its own death is exactly that, and it was the one class of open item the
    Board could not see.

    Only `contradicted` and `due` land here — `watching` is a live check that has NOT fired, and
    putting 23 of those on the Board would bury the one that matters. `uncovered` is deliberately
    excluded: a decision that never stated a trip-wire is a to-do for the Founder, not an open item, and
    tripwires.py is explicit that backfilling one would be inventing a reopen condition after the
    fact.
    """
    out = []
    try:
        import tripwires
        tw = tripwires.build()
    except Exception:
        return out          # never let an instrumentation failure blank the Board
    for r in tw.get("fired", []):
        contradicted = r.get("verdict") == "contradicted"
        note = _clean(r.get("checkNote") or r.get("overturnIf") or "")
        out.append(_item(
            id="tw-" + re.sub(r"[^a-z0-9]+", "-", (r.get("file") or "").lower()).strip("-"),
            title=r.get("title") or os.path.basename(r.get("file", "")),
            detail=(("Its own trip-wire fired: " if contradicted else "Review date passed: ")
                    + (note[:400] if note else "no condition text recorded")),
            # Lane comes from the CHECK EXPRESSION, not the title. The check names the facts the
            # decision actually depends on (`counselGatesBlocked`, `OtherVentureCleared`), which is a far
            # better domain signal than a headline: on the partner split the title alone classified
            # as "Clients" — filing a governance blocker where nobody looks for it. camelCase is
            # split first so the word-boundary lane regexes can see `gates` and `OtherVenture` at all.
            lane=_lane_for(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", r.get("check") or "").lower()
                           + " " + (r.get("title") or "") + " " + note),
            state="needs-you",
            owner="the Founder",
            since=r.get("date") or "",
            age=r.get("ageDays"),
            next=("Re-decide or restate the condition — " + (r.get("file") or "")),
            sev="critical" if contradicted else "med",
            source=r.get("file") or "decisions/",
        ))
    return out


def rejection_items():
    """Rejections whose own reopen condition has now come true.

    Added 2026-08-24, and the sibling of tripwire_items() above. `rejections/` is the anti-library:
    what yourco decided NOT to do, each entry carrying the condition that would reopen it, evaluated
    against the same 21-fact map by the same engine as decisions/. Its `--due` view was a CLI nobody
    ran, and board.py had no reference to rejections at all — so a rejection reality had reopened
    reached no surface a human opens. All seven were `standing` on the day this was written, so
    nothing was being missed; nothing would have told you when one flipped.

    `standing` and `unconditional` are deliberately excluded. Standing is the normal state. An
    `unconditional` entry (no reopen condition written) is a real flag, but it is a *documentation*
    gap for whoever writes rejections — not open work on the Board, and putting it here would bury
    the reopened ones under entries that will never change.
    """
    out = []
    try:
        import sys as _sys
        _rt = os.path.join(ROOT, "runtime")
        if _rt not in _sys.path:
            _sys.path.insert(0, _rt)
        import rejections as _rej
        rows = _rej.status_all().get("rejections", [])
    except Exception:
        return out          # instrumentation must never blank the Board
    for r in rows:
        if r.get("verdict") not in ("reopened", "due"):
            continue
        why = _clean(r.get("detail") or r.get("revisit") or "")
        out.append(_item(
            id="rej-" + re.sub(r"[^a-z0-9]+", "-", (r.get("file") or "").lower()).strip("-"),
            title="Reopened: " + (r.get("title") or r.get("file", "")),
            detail=("The condition this rejection named has come true — "
                    + (why[:380] if why else "no condition text recorded")
                    + " · Re-proposing is expected; it just has to carry evidence."),
            lane=_lane_for(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", r.get("check") or "").lower()
                           + " " + (r.get("title") or "") + " " + (r.get("tags") or "")),
            state="needs-you",
            owner="the Founder",
            since=r.get("date") or "",
            next="Re-decide, or restate the condition — " + (r.get("path") or "rejections/"),
            sev="high",
            source=r.get("path") or "rejections/",
        ))
    return out


def _cadence_for(name):
    for k, v in CADENCE.items():
        if k in name:
            return v
    return 7


# loops/ dir -> sanctioned timer stem, where the two names diverge. Without this a renamed loop
# looks unsanctioned, and a retired folder (loops/melanie/) looks like a live loop gone dark.
DIR_TO_TIMER = {"open-loops": "open-loops-chaser", "sadie": "sadie-intent",
                "_governance": "agent-registry", "_advisory": "advisor",
                "granola-crm-sync": "granola-crm-sync"}
# folders that are deliberate archives / manual reviews, not timer-driven loops
UNTIMED_OK = {"_audit", "gap-audit"}


def system_items():
    out = []
    loops_dir = os.path.join(ROOT, "loops")
    try:
        names = sorted(os.listdir(loops_dir))
    except OSError:
        names = []
    reg = _load("runtime/agent-registry.json") or {}
    sanctioned = {re.sub(r"^yourco-|\.timer$", "", t) for t in (reg.get("sanctioned_timers") or [])}
    dark, retired, empty = [], [], []
    for n in names:
        if n in SKIP_DIRS or not os.path.isdir(os.path.join(loops_dir, n)):
            continue
        stem, _ = _latest_report("loops/" + n)
        timer = DIR_TO_TIMER.get(n, n.lstrip("_"))
        tracked = timer in sanctioned
        if stem is None:
            empty.append(n)
            continue
        a = _age(stem)
        if not tracked:
            # No sanctioned timer can ever write here again. Aging it as "past due" would be a
            # lie about a folder nobody promised to keep current.
            if n not in UNTIMED_OK and a is not None and a > 30:
                retired.append((n, a))
            continue
        cad = _cadence_for(n)
        if a is not None and a > cad * 2:
            dark.append((n, a, cad))

    if empty:
        out.append(_item(
            id="loop-empty",
            title=f"{len(empty)} loop folder(s) have never produced an artifact",
            detail=", ".join(empty) + " — the folder exists and nothing has ever been written to it.",
            lane="System", state="missing", owner="Kemba / platform", since="",
            next="Wire them or delete the folders — an empty loop dir reads as coverage that isn't there.",
            sev="med", source="loops/",
        ))
    if retired:
        retired.sort(key=lambda x: -x[1])
        out.append(_item(
            id="loop-retired",
            title=f"{len(retired)} loop folder(s) have no sanctioned timer",
            detail=", ".join(f"{n} (last {a}d ago)" for n, a in retired) +
                   " — artifacts exist but no timer in agent-registry.json can write there again. "
                   "Retired, renamed, or never wired; the folder doesn't say which.",
            lane="System", state="missing", owner="Kemba / platform", since="",
            next="Archive the retired ones and wire the rest — a stale folder reads as a live loop.",
            sev="low", source="runtime/agent-registry.json",
        ))
    if dark:
        dark.sort(key=lambda x: -x[1])
        worst = ", ".join(f"{n} ({a}d)" for n, a, _ in dark[:6])
        out.append(_item(
            id="loop-dark",
            title=f"{len(dark)} loops are past due — the runtime is not keeping cadence",
            detail=("Days since last committed artifact vs expected cadence. Worst: " + worst +
                    (", …" if len(dark) > 6 else "") +
                    ". The runtime alarm only fires on FAILED runs, so a loop that stops running "
                    "reports 'all clear' — this is the one indicator that shows silence."),
            lane="System", state="needs-you", owner="the Founder / platform", since="",
            age=dark[0][1],
            next="Fund the API + enable auto-reload, or formally park the runtime and stop calling it always-on.",
            sev="critical" if dark[0][1] > 7 else "high",
            source="loops/",
        ))

    # Wiring drift: prompts with no timer can never run.
    try:
        prompts = {f[:-3] for f in os.listdir(os.path.join(ROOT, "runtime/prompts"))
                   if f.endswith(".md") and not f.startswith("_")}
        timers = {re.sub(r"^yourco-|\.timer$", "", f)
                  for f in os.listdir(os.path.join(ROOT, "runtime/systemd")) if f.endswith(".timer")}
    except OSError:
        prompts, timers = set(), set()
    orphan = sorted(prompts - timers)
    if orphan:
        out.append(_item(
            id="wire-orphan-prompt",
            title=f"{len(orphan)} loop prompt(s) have no systemd timer",
            detail=", ".join(orphan) + " — written work that can never execute.",
            lane="System", state="missing", owner="Kemba / platform", since="",
            next="Add the timer + service per runtime/agent-wiring-checklist.md, or archive the prompt.",
            sev="med", source="runtime/prompts/",
        ))

    # Dashboard loop count vs the canonical registry.
    dash = _load("dashboard/data.json") or {}
    reg = _load("runtime/agent-registry.json") or {}
    listed = len(dash.get("loops", []) or [])
    sanctioned = len(reg.get("sanctioned_timers", []) or [])
    if sanctioned and listed and abs(sanctioned - listed) >= 3:
        out.append(_item(
            id="wire-loop-count",
            title=f"Dashboard lists {listed} loops; the registry sanctions {sanctioned}",
            detail="dashboard/data.json loops[] is hand-maintained and has drifted behind "
                   "runtime/agent-registry.json — the canonical list. Every count the cockpit shows "
                   "inherits the error.",
            lane="System", state="missing", owner="Atlas", since="",
            next="Derive loops[] from the registry in refresh.py the way loop health already is.",
            sev="med", source="dashboard/data.json",
        ))
    return out


# --------------------------------------------------------------------------
# 6. Build backlogs — ideas that exist but aren't scheduled
# --------------------------------------------------------------------------
def backlog_items():
    out = []

    # CRM backlog — bolded bullet leads under any heading.
    # A bullet marked shipped is NOT open work. This is explicit rather than incidental: marking
    # five shipped items on 2026-08-23 happened to break the `- **` adjacency the regex needs, so
    # they dropped off The Board for the right reason by the wrong mechanism — a reformat would
    # have resurrected them. Skipping on the marker means the intent lives in the code.
    md = _read("crm/_backlog.md")
    for raw in md.splitlines():
        m = re.match(r"^-\s+(.*)$", raw)
        if not m:
            continue
        body = m.group(1)
        if re.match(r"^(✅|~~|\*\*?DONE\b|SHIPPED\b)", body) or "✅ SHIPPED" in body:
            continue                       # shipped — graduated out of the backlog
        b = re.match(r"^\*\*(.+?)\*\*(.*)$", body)
        if not b:
            continue
        line = (b.group(1), b.group(2))
        title = _clean(line[0])
        if not title:
            continue
        out.append(_item(
            id="bl-crm-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:28],
            title=title, detail=_clean(line[1])[:240],
            lane="Build", state="backlog", owner="David", since="",
            next="Prioritize or delete — the file's own rule is 'graduate or drop'.",
            sev="low", source="crm/_backlog.md",
        ))

    # Automation roadmap — any row whose status isn't done.
    md = _read("processes/automation-roadmap.md")
    for ln in md.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4 or all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        status = cells[-1]
        title = _bold(cells[0])
        if not title or title.lower() in ("automation", "removes", "owner"):
            continue
        if re.search(r"live|done|✅|built", status, re.I):
            continue
        if not re.search(r"not started|pending|designed|not wired|plan", status, re.I):
            continue
        out.append(_item(
            id="bl-auto-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:28],
            title=title,
            detail="Removes: " + _clean(cells[1])[:180] if len(cells) > 1 else "",
            lane="Build", state="backlog",
            owner=_clean(cells[2]) if len(cells) > 2 else "—",
            since="", next=_clean(status), sev="low",
            source="processes/automation-roadmap.md",
        ))

    # Frontier roadmap — the status board; anything not actively building is backlog.
    for r in _tables(_read("offerings/_frontier-roadmap.md"), r"status board"):
        if len(r) < 5:
            continue
        title, status, trigger = _bold(r[1]), _clean(r[3]), _clean(r[4])
        if not title:
            continue
        building = bool(re.search(r"BUILDING|WRITING|ARCHITECTING", r[3]))
        out.append(_item(
            id="bl-fr-" + re.sub(r"[^a-z0-9]+", "-", title.lower())[:28],
            title=title, detail=_clean(r[2])[:200],
            lane="Build", state="backlog",
            owner=_clean(r[5]) if len(r) > 5 else "—",
            since="", next=("In progress — " + status) if building else ("Trigger: " + trigger),
            sev="low", source="offerings/_frontier-roadmap.md",
        ))
    return out


# --------------------------------------------------------------------------
# lane inference
# --------------------------------------------------------------------------
# Keyword weights per lane. Scored, not first-match: an item mentioning both "billing" and
# "runtime" belongs to System, and first-match ordering got that wrong. Every term is matched
# on word boundaries — the first cut of this used bare substrings and put "warm-network outreach"
# in Legal because "delegate" contains "gate".
LANE_HINTS = {
    "Money": r"cash|runway|burn|billing|payment|payments|stripe|invoice|invoicing|credits?|spend|subscriptions?|subs|cancel|cancellations?|price|pricing|finance|financial|margin|insolvent",
    "Legal": r"counsel|legal|gates?|gated|contracts?|agreements?|nda|dpa|compliance|securities|mlm|10dlc|tcpa|ftsa|consent|privacy|OtherVenture|upl|licensing",
    "System": r"runtime|loops?|timers?|systemd|watchdog|alarm|heartbeat|dashboard|wiring|wired|2fa|vps|api|slack|connectors?|prompt|prompts|liveness|dark",
    "Clients": r"southern|parker|Prospect A|storm|clients?|engagements?|onboard|onboarding|offboard|offboarding|delivery|console",
    "Commercial": r"outreach|prospects?|warm|referrals?|connectors?|audits?|proposals?|deals?|pipeline|leads?|sales|campaigns?|warmup|instantly|network|intros?",
    "Build": r"backlog|roadmap|spec|specced|build|prototype|template|module|offering",
}
_LANE_RE = {lane: re.compile(r"\b(?:" + pat + r")\b", re.I) for lane, pat in LANE_HINTS.items()}
# Tie-break by specificity, most specific first. A named client beats a generic legal mention:
# "Prospect A — paper the partnership (counsel gate #11)" is a Clients item, not a Legal one.
_LANE_PRIORITY = ["Clients", "Money", "System", "Legal", "Commercial", "Build"]


def _lane_for(text):
    t = text or ""
    scores = {lane: len(rx.findall(t)) for lane, rx in _LANE_RE.items()}
    lane, n = max(scores.items(), key=lambda kv: (kv[1], -_LANE_PRIORITY.index(kv[0])))
    return lane if n else "Build"


# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------
SEV_RANK = {"critical": 0, "high": 1, "med": 2, "low": 3, "none": 4}
STATE_RANK = {s: i for i, s in enumerate(STATES)}


def unshown_assets():
    """Assets produced and never put in front of anybody.

    Added 2026-08-25. Reed's and Pickle's owned numbers are both blocked by ONE missing habit —
    nothing is registered on the deal it was used on — and a metric that reads blank is invisible in
    exactly the way `learnings/ops/2026-08-07_absence-is-invisible-to-this-os` describes. Without a
    row here, "nobody has ever shown a prospect a piece of collateral" is a fact no surface states.

    Fires only when there are live conversations to have shown them IN. Producing assets before
    there is anybody to show them to is a sequencing choice, not a defect, and flagging it then
    would be noise."""
    crm = _load("crm/data.json")
    if not crm:
        return []
    in_motion = [d for d in (crm.get("deals") or []) if _in_motion_board(d)]
    if not in_motion:
        return []      # nothing to show anything to — this is not yet a finding
    shown = {(a.get("type") or "") for d in (crm.get("deals") or []) + (crm.get("closed") or [])
             for a in (d.get("artifacts") or []) if (a.get("status") or "") in ("shown", "reacted")}
    made = {}
    try:
        made["collateral"] = len([f for f in os.listdir(os.path.join(ROOT, "agents/pickle/collateral"))
                                  if not f.startswith("_")])
    except OSError:
        pass
    try:
        import client_metrics                       # lazy: client_metrics imports this module back
        pub = client_metrics._published_assets()
        if pub:
            made["video"] = len(pub)
    except Exception:
        pass
    missing = {k: n for k, n in made.items() if n and k not in shown}
    if not missing:
        return []
    what = " · ".join(f"{n} {k}" for k, n in sorted(missing.items()))
    return [_item(
        id="assets-unshown",
        title=f"{sum(missing.values())} produced asset(s) have never been shown to anyone",
        detail=(f"{what} produced, and not one is registered on a deal as shown. "
                f"{len(in_motion)} deal(s) are in motion to have shown them in. This is the single "
                f"habit blocking both Reed's and Pickle's owned numbers — register it on the deal "
                f"(dossier → + artifact → type, status `shown`) and both go from refused to real."),
        lane="Commercial",
        state="needs-you",
        owner="the Founder",
        since="",
        next="Show one, and log it. Or record that the asset is not fit for these conversations — "
             "that is also an answer, and it is a different one from silence.",
        sev="med",
        source="agents/pickle/collateral/ + agents/Reed/_asset_registry.md vs crm/data.json",
    )]


def _in_motion_board(d):
    """A deal being actively worked. `pre-convo` excluded deliberately — the same split HQ's metric
    uses (dashboard/server.py BENCH_STAGES); you cannot show collateral to someone you have not
    spoken to."""
    return (d.get("stage") or "") not in BENCH | CLOSED | {"pre-convo"}


def build():
    ol, ol_stem, covered = open_loops()
    ga, ga_stem = gap_audit()
    items = (ol + ga + gates() + crm_items(covered) + system_items() + backlog_items()
             + tripwire_items() + rejection_items() + unshown_assets())

    # de-dupe on id, keeping the most severe instance
    best = {}
    for it in items:
        cur = best.get(it["id"])
        if cur is None or SEV_RANK[it["sev"]] < SEV_RANK[cur["sev"]]:
            best[it["id"]] = it
    items = list(best.values())

    items.sort(key=lambda i: (STATE_RANK.get(i["state"], 9), SEV_RANK[i["sev"]],
                              -(i["age"] or 0), i["title"]))

    # ---- owners: which of the three partners, if any ---------------------
    assigns = load_assignments()
    seen_keys = set()
    for it in items:
        it["key"] = item_key(it["title"])
        seen_keys.add(it["key"])
        derived = _owner_keys(it.get("owner"))
        a = assigns.get(it["key"])
        it["assignedTo"] = a["to"] if a else None
        it["assignNote"] = a["note"] if a else ""
        # An explicit assignment wins over the owner string it was made to override; the
        # derived reading is kept alongside so the override is always visible as an override.
        it["ownerKeys"] = [a["to"]] if a else derived
        it["derivedOwners"] = derived
        it["ownerAgents"] = _owner_agents(it.get("owner"))
        # Three distinct states, and conflating them hides the one that matters:
        #   partner — a named partner owns it
        #   agent     — delegated to a roster agent (owned, just not by a human)
        #   unowned   — nobody at all; this is the pile that quietly becomes the Founder's
        it["ownerClass"] = ("partner" if it["ownerKeys"]
                            else "agent" if it["ownerAgents"] else "unowned")
        it["unowned"] = it["ownerClass"] == "unowned"

    counts = {"byState": {}, "byLane": {}, "bySev": {}, "byOwner": {}}
    for it in items:
        for k, v in (("byState", it["state"]), ("byLane", it["lane"]), ("bySev", it["sev"])):
            counts[k][v] = counts[k].get(v, 0) + 1
        for o in (it["ownerKeys"] or [it["ownerClass"]]):
            counts["byOwner"][o] = counts["byOwner"].get(o, 0) + 1

    # Source freshness — the gap audit's rule: show staleness, never hide it.
    def src(label, rel, stem, expected):
        d = stem or (_mtime_date(rel).isoformat() if _mtime_date(rel) else None)
        a = _age(d)
        return {"label": label, "path": rel, "date": d, "age": a, "expected": expected,
                "stale": a is not None and a > expected}

    sources = [
        src("Open loops (needs you)", "loops/open-loops", ol_stem, 1),
        src("Gap audit (what's missing)", "loops/gap-audit", ga_stem, 30),
        src("Counsel gates", "processes/counsel-gates.md", None, 7),
        src("launch-gate", "processes/launch-gate.md", None, 30),
        src("CRM", "crm/data.json", (_load("crm/data.json") or {}).get("meta", {}).get("updated"), 3),
        src("CRM backlog", "crm/_backlog.md", None, 60),
        src("Automation roadmap", "processes/automation-roadmap.md", None, 60),
        src("Frontier roadmap", "offerings/_frontier-roadmap.md", None, 30),
    ]

    needs = [i for i in items if i["state"] == "needs-you"]
    # The load-bearing partner number: how much of the "needs a partner" pile is on each of
    # the three. Rendered even when two of them are zero — especially then, since a board that
    # reads 100% the Founder while the company has three partners is the finding, not a blank.
    needs_by_owner = {}
    for i in needs:
        for o in (i["ownerKeys"] or [i["ownerClass"]]):
            needs_by_owner[o] = needs_by_owner.get(o, 0) + 1
    stale_assigns = [{"key": k, **v} for k, v in assigns.items() if k not in seen_keys]

    return {
        "items": items,
        "counts": counts,
        "lanes": LANES,
        "states": STATES,
        "sources": sources,
        "partners": [{"key": k, "label": v} for k, v in PARTNERS.items()],
        "owners": {
            "byOwner": counts["byOwner"],
            "needsByOwner": needs_by_owner,
            "assigned": sum(1 for i in items if i["assignedTo"]),
            "agentOwned": counts["byOwner"].get("agent", 0),
            "unowned": counts["byOwner"].get("unowned", 0),
            "staleAssignments": stale_assigns,
            "note": "Owner is read from each source's own owner field, then overridden by an "
                    "explicit assignment (dashboard/assignments.json). Assignments are the one "
                    "hand-maintained input on this Board, because who owns a thing is a "
                    "decision and not a derivable fact. An assignment whose item is gone or "
                    "renamed is listed as stale rather than silently kept.",
        },
        "headline": {
            "needsYou": len(needs),
            "needsByOwner": needs_by_owner,
            "critical": sum(1 for i in items if i["sev"] == "critical"),
            "blocked": counts["byState"].get("blocked", 0),
            "missing": counts["byState"].get("missing", 0),
            "backlog": counts["byState"].get("backlog", 0),
            "parked": counts["byState"].get("parked", 0),
            "oldestDays": max((i["age"] or 0) for i in needs) if needs else 0,
            "staleSources": sum(1 for s in sources if s["stale"]),
        },
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


if __name__ == "__main__":
    b = build()
    h = b["headline"]
    print(f"{len(b['items'])} items — {h['needsYou']} need you ({h['critical']} critical), "
          f"{h['blocked']} blocked, {h['missing']} missing, {h['backlog']} backlog, {h['parked']} parked")
    print(f"oldest open item: {h['oldestDays']}d · stale sources: {h['staleSources']}/{len(b['sources'])}")
    for s in b["sources"]:
        print(f"  {'STALE' if s['stale'] else '  ok '}  {s['label']:<28} {s['date']} ({s['age']}d)")
    for i in b["items"][:15]:
        print(f"  [{i['state']:<9}] [{i['sev']:<8}] {i['lane']:<10} {i['title'][:70]}")
