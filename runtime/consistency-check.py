#!/usr/bin/env python3
"""yourco — cross-surface consistency watchdog.

WHY: sessions run in parallel and the repo is their only shared state. When one session changes a
canonical fact (commission terms, tier names, parked pages, the hero video), nothing used to force
every surface that *displays* that fact (site, packet, spec, CRM meta, CLAUDE.md) to update — so
facts drifted and the Founder had to catch it by eye (2026-07-05). This check makes the invariants explicit
and machine-checked, mirroring the agent-registry governance watchdog.

Deterministic, read-only, stdlib-only. Writes a dated report to loops/_consistency/<date>.md.
Exit 0 = aligned · exit 1 = drift found (the report lists each item).

Add an invariant every time a human catches drift by eye — that's the feed-forward loop.
Usage: python3 runtime/consistency-check.py [--quiet]
"""
import json, os, re, sys, datetime, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "agents/webb/pages/yourco-site-v2")
drift, ok = [], []

def site_pages():
    return [p for p in glob.glob(os.path.join(SITE, "*.html"))]

def read(p):
    try:
        with open(p, encoding="utf-8") as f: return f.read()
    except OSError: return ""

# ── 1. No commission percentages on the live site (rates live in the Partner Packet only) ──
COMMISSION_CTX = re.compile(r"(commission|referr|rep |partner tier|your rate|whole book)", re.I)
# 1% is the downline override. It was missed by the original list and reached connect.html on
# 2026-08-13 — caught by eye, so it is an invariant now (CLAUDE.md: never caught by eye twice).
RATE = re.compile(r"\b(1|10|12\.5|15|20)\s?%")
for p in site_pages():
    s = read(p)
    for m in RATE.finditer(s):
        ctx = s[max(0, m.start()-160):m.end()+160]
        if COMMISSION_CTX.search(ctx):
            drift.append(f"commission % on live site: {os.path.basename(p)} → …{ctx[120:260].strip()}…")
            break
else: pass
if not any("commission %" in d for d in drift): ok.append("no commission %s on live site")

# ── 2. No live-page references to parked pages ──
PARKED = ["hire.html","hire-onboarding.html","employees.html","build-your-employee.html",
          "roi-calculator.html","quiz.html","missed-money-meter.html","leak-index.html",
          "refer.html","team.html","org-chart.html","verticals.html","vertical-template.html","snapshot.html"]
pat = re.compile(r'["\'/](' + "|".join(re.escape(x) for x in PARKED) + r')["\'#?]')
hits = [os.path.basename(p) for p in site_pages() if pat.search(read(p))]
if hits: drift.append(f"live pages reference parked pages: {', '.join(hits)}")
else: ok.append("no parked-page references on live site")

# ── 3. pricing.html names the four locked OS levels ──
ps = read(os.path.join(SITE, "pricing.html"))
missing = [t for t in ("Core","Suite","Operation","Command") if t not in ps]
if missing: drift.append(f"pricing.html missing locked OS level names: {missing}")
else: ok.append("pricing.html carries Core/Suite/Operation/Command")

# ── 4. The inline hero explainer is wired and the file exists ──
idx = read(os.path.join(SITE, "index.html"))
if "yourco-explainer.mp4" not in idx: drift.append("index.html no longer references yourco-explainer.mp4")
elif not os.path.exists(os.path.join(SITE, "yourco-explainer.mp4")): ok.append("hero video referenced but not present — expected in a fresh template; add yours or drop the reference")  # was: drift.append("yourco-explainer.mp4 missing from the site folder")
else: ok.append("hero explainer wired + present")

# ── 5. Referral terms coherent: CRM meta == locked spec (10/12.5/15 @ 6/11, override 1) ──
try:
    meta = json.load(open(os.path.join(ROOT, "crm/data.json")))["meta"]["referralTiers"]
    want = {"rates": [10, 12.5, 15], "thresholds": [6, 11], "override": 1}
    if {k: meta.get(k) for k in want} != want:
        drift.append(f"CRM referralTiers != locked v1 terms: {meta}")
    else: ok.append("CRM referralTiers match locked v1")
except Exception as e:
    drift.append(f"could not verify CRM referralTiers: {e}")

# ── 6. Packet + spec + one-pager all carry the same locked rates ──
for rel in ("processes/partnerships/rep-packet.md","processes/partnerships/referral-program.md",
            "processes/partnerships/referral-recruitment-onepager.md"):
    s = read(os.path.join(ROOT, rel))
    if not ("12.5%" in s and "15%" in s and "10%" in s):
        drift.append(f"{rel}: locked rates (10/12.5/15) not all present — check for stale terms")
if not any("locked rates" in d for d in drift): ok.append("packet/spec/one-pager rates coherent")

# ── 7. Payout cadence consistent wherever stated ──
for rel in ("processes/partnerships/rep-packet.md","processes/partnerships/referral-program.md"):
    s = read(os.path.join(ROOT, rel))
    if "net-30" in s.lower() and "2nd Friday" not in s and "second Friday" not in s.lower():
        drift.append(f"{rel}: still says net-30 without the locked 2nd-Friday cadence")
if not any("net-30" in d for d in drift): ok.append("payout cadence coherent (2nd Friday)")


# ── 8. Stat freshness: cited sources on the live site must be ≤18 months old ──
# (the Founder 2026-07-06: "once a stat is outdated past 18 months, notify me so we can update it.")
# Heuristic: find citation contexts (class="src", "source:", "Source:") and extract month/year.
# Year-only citations are treated as Dec 31 of that year (most favorable) — flagged only when even
# that is older than the 18-month cutoff. New stats: always cite with month+year.
MONTHS = {m: i+1 for i, m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"])}
cutoff = datetime.date.today() - datetime.timedelta(days=548)  # ~18 months
CITE = re.compile(r'(class="src"[^>]*>|source:|Source:)([^<\n]{0,120})')
YEAR = re.compile(r"\b(20[12][0-9])\b")
MON = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", re.I)
stale = []
for p_ in site_pages():
    s_ = read(p_)
    for cm in CITE.finditer(s_):
        frag = cm.group(2)
        ym = YEAR.search(frag)
        if not ym: continue
        year = int(ym.group(1))
        mm = MON.search(frag)
        month = MONTHS[mm.group(1)[:3].lower()] if mm else 12
        day = 28 if mm else 31
        try: cited = datetime.date(year, month, day)
        except ValueError: cited = datetime.date(year, month, 28)
        if cited < cutoff:
            stale.append(f"stale stat (> 18 mo) on {os.path.basename(p_)}: \"{frag.strip()[:80]}\" — re-source or drop (Bella/Sadie)")
if stale: drift.extend(sorted(set(stale)))
else: ok.append("all cited stats on the live site are <= 18 months old")

# ── 9. Promise-vs-practice: every active engagement has a cost ledger with rows ──
# (the Founder 2026-07-06: CLAUDE.md promised per-client cost.md for weeks before any existed — a documented
#  convention with no machine check rots silently. Every clients/ folder with an active CRM deal at
#  proposal/build/live must have a cost.md containing at least one ledger row. Extend ENGAGEMENTS as
#  clients land — the scaffold-engagement skill copies cost.md from the template, so new folders pass.)
# ── CRM referential integrity: dual-profile links must resolve ──
# (the Founder 2026-08-11: Partner B's internal record pointed linkedContactId at p14, his client-side
#  row, which was deleted in a July dedupe. The UI's linkedPill() bails silently when it can't
#  resolve a link, so a broken pointer renders as NOTHING — invisible, not wrong, which is why it
#  survived a month and was only caught while fixing an unrelated duplicate. Deleting a contact is
#  the moment this breaks, and nothing in the delete path checks the other side.)
try:
    _c = json.load(open(os.path.join(ROOT, "crm/data.json")))
    _ids = {p.get("id") for p in _c.get("contacts", [])}
    _by = {p.get("id"): p for p in _c.get("contacts", [])}
    _bad = []
    for p in _c.get("contacts", []):
        l = p.get("linkedContactId")
        if not l:
            continue
        if l not in _ids:
            _bad.append(f"CRM: {p.get('name')} ({p.get('id')}) links to '{l}', which no longer exists — "
                        f"clear it or restore the profile (renders as nothing in the UI, so it hides)")
        elif _by[l].get("linkedContactId") != p.get("id"):
            _bad.append(f"CRM: {p.get('name')} links to {_by[l].get('name')}, but that record doesn't "
                        f"point back — dual profiles are meant to be mutual")
    if _bad: drift.extend(_bad)
    else: ok.append("every CRM dual-profile link resolves and is mutual")
except Exception as e:
    drift.append(f"could not verify CRM profile links: {e}")

ENGAGEMENTS = {"Sample Client": "clients/sample-client", "Sample Product": "clients/prospect-a",
               "Prospect A": "clients/prospect-a"}
try:
    _crm = json.load(open(os.path.join(ROOT, "crm/data.json")))
    _comp = {c.get("id"): c.get("name", "") for c in _crm.get("companies", [])}
    active = {_comp.get(d.get("companyId"), "") for d in _crm.get("deals", [])
              if (d.get("stage") or "").lower() in ("proposal", "build", "live") and not d.get("example")}
    missing_ledgers = []
    for name in sorted(n for n in active if n):
        folder = next((f for k, f in ENGAGEMENTS.items() if k.lower() in name.lower() or name.lower() in k.lower()), None)
        if not folder:
            missing_ledgers.append(f"active deal '{name}' has no known clients/ folder mapping — add it to ENGAGEMENTS in consistency-check.py")
            continue
        cost = read(os.path.join(ROOT, folder, "cost.md"))
        if not cost:
            missing_ledgers.append(f"{folder}/cost.md missing for active deal '{name}' — create from the template (log-build-cost skill)")
        elif not re.search(r"^\|\s*20\d\d-", cost, re.M):
            missing_ledgers.append(f"{folder}/cost.md has no ledger rows for active deal '{name}' — log spend (log-build-cost skill)")
    if missing_ledgers: drift.extend(missing_ledgers)
    else: ok.append("every active engagement has a cost.md with ledger rows")
except Exception as e:
    drift.append(f"could not verify engagement cost ledgers: {e}")

# ── 10. People taxonomy: "sales rep" is superseded by Connector (Advisors/Connectors, 2026-07-06) ──
# Live site + connector-facing partnership docs must not reintroduce the old role name.
# (Internal keys/paths — rep-intake, repApplicants, rep-packet.md filenames — are exempt by design.)
TAXO_SURFACES = site_pages() + [os.path.join(ROOT, p) for p in (
    "processes/partnerships/rep-packet.md", "processes/partnerships/rep-packet.html",
    "processes/partnerships/referral-program.md", "processes/partnerships/referral-recruitment-onepager.md")]
taxo_hits = [os.path.relpath(p, ROOT) for p in TAXO_SURFACES
             if re.search(r"\bsales[- ]reps?\b", read(p), re.I)]
if taxo_hits: drift.append(f"'sales rep' reappeared (superseded by Connector, decisions/2026-07-06_advisors-connectors-taxonomy.md): {', '.join(taxo_hits)}")
else: ok.append("people taxonomy holds (Connectors, no 'sales rep' on live surfaces)")

# ── 11. Collection-loop yield: a zero-streak means broken plumbing before it means a quiet market ──
# Sadie ran 14+ straight zero-signal sweeps (July 2026) because all three sources were unkeyed on the
# VPS — every run still reported OK (learnings/ops/2026-07-20_keyless-source-loop-silent-zero.md).
# N consecutive zeros, or any board admitting an unkeyed source, is drift to investigate.
ZERO_STREAK_N = 5
sadie_boards = sorted(glob.glob(os.path.join(ROOT, "loops/sadie/*_intent-sweep.md")))[-ZERO_STREAK_N:]
if len(sadie_boards) == ZERO_STREAK_N:
    zeros = [b for b in sadie_boards if re.search(r"^0 signal\(s\)", read(b), re.M)]
    if len(zeros) == ZERO_STREAK_N:
        drift.append(f"sadie-intent: {ZERO_STREAK_N} consecutive zero-signal sweeps — verify sources are keyed "
                     f"on the VPS before concluding the market is quiet (latest: {os.path.basename(sadie_boards[-1])})")
    else: ok.append(f"sadie-intent yield alive (not {ZERO_STREAK_N} straight zeros)")
    latest = read(sadie_boards[-1])
    if "⛔ unkeyed" in latest:
        drift.append(f"sadie-intent: latest board reports unkeyed source(s) — wire per runtime/intent-credentials-setup.md "
                     f"({os.path.basename(sadie_boards[-1])})")
    elif "Sources:" in latest: ok.append("sadie-intent sources all keyed")

# ── 12. Audit report: the 4-axis rubric stays internal (SOP §Report clarity, 2026-07-16; enforced 2026-07-27) ──
# The client-facing audit-report template drifted to rendering Money/Frequency/Owner-drain/Fixability
# scores on bottleneck cards, contradicting processes/audit-sop.md ("internal and stays internal").
# The client sees the heat bar + the one-word primary focus only — never the rubric.
AXIS_RUBRIC = re.compile(r"Owner-drain\s*<b>|Fixability\s*<b>|\bmoney\s*:\s*[1-5]\s*,\s*freq\s*:\s*[1-5]")
audit_tmpl = read(os.path.join(ROOT, "clients/_yourco-template/audit-report/index.html"))
if AXIS_RUBRIC.search(audit_tmpl):
    drift.append("audit-report template renders the internal 4-axis scores client-facing "
                 "(processes/audit-sop.md §Report clarity: heat bar + primary focus only)")
elif "primaryFocus" not in audit_tmpl:
    drift.append("audit-report template lost the one-word primaryFocus on the exec summary (SOP §Report clarity)")
else: ok.append("audit-report keeps the 4-axis rubric internal (heat bar + primary focus only)")

# ── 11. Connector classification language must be identical on every surface ──
# (the Founder 2026-08-07: connectors are independent contractors, treated like team. They get yourco email,
#  Slack, tools, and training — all of which argue employee status — so the ONLY thing protecting the
#  contractor position is that every document says the same thing and the practice matches it.
#  "It is inconsistency that creates liability, not either model.")
CONNECTOR_SURFACES = [
    "processes/partnerships/rep-packet.md", "processes/partnerships/rep-packet.html",
    "processes/partnerships/referral-recruitment-onepager.md",
    "processes/partnerships/legal/referral-partner-agreement.md",
    "processes/partnerships/legal/income-disclosure-statement.md",
]
CONTRACTOR_LINE = re.compile(r"independent (referrer|contractor|referral partner)", re.I)
# a connector described as an yourco employee anywhere = the contradiction that creates the exposure.
# Excludes the product ("digital employee"), the role name ("People Manager"), and counsel questions.
EMPLOYEE_CLAIM = re.compile(r"connectors?\s+(are|as)\s+(yourco\s+)?employees?", re.I)
class_missing, class_contra = [], []
for rel in CONNECTOR_SURFACES:
    s = read(os.path.join(ROOT, rel))
    if not s:
        class_missing.append(f"{rel}: surface missing — cannot verify connector classification language")
    elif not CONTRACTOR_LINE.search(s):
        class_missing.append(f"{rel}: no independent-contractor line — every connector surface must carry it")
for rel in CONNECTOR_SURFACES + ["processes/partnerships/connector-onboarding.md",
                                 "processes/partnerships/connector-os.md", "04_agent_roster.md"]:
    s = read(os.path.join(ROOT, rel))
    for m in EMPLOYEE_CLAIM.finditer(s):
        ctx = s[max(0, m.start()-120):m.end()+120]
        if "not" in ctx.lower()[:m.start()-max(0, m.start()-120)+12] or "reclassif" in ctx.lower():
            continue  # "connectors are NOT employees" / discussion of reclassification risk
        class_contra.append(f"{rel}: describes connectors AS employees — contradicts every other surface: …{ctx[100:220].strip()}…")
if class_missing or class_contra:
    drift.extend(class_missing + class_contra)
else:
    ok.append("connector classification language consistent (independent contractor on every surface)")

# ── 12. Every ladder rung has training content (the curriculum is load-bearing) ──
# Training now GATES rung advancement, so deleting or renaming a lesson silently reopens that rung and
# can demote live connectors. A rung with no lesson fails closed and locks everyone past it.
try:
    sys.path.insert(0, os.path.join(ROOT, "crm"))
    import connector_ladder as _cl
    _tdir = os.path.join(ROOT, "processes/partnerships/connector-training")
    _by_rung = {}
    for _f in glob.glob(os.path.join(_tdir, "*.md")):
        _m = re.search(r"^rung:\s*(R[0-4])", read(_f), re.M)
        if _m: _by_rung.setdefault(_m.group(1), []).append(os.path.basename(_f))
    _empty = [r["key"] for r in _cl.RUNGS if not _by_rung.get(r["key"])]
    if _empty:
        drift.append(f"ladder rung(s) with NO training content: {_empty} — training gates advancement, "
                     f"so an empty rung locks every connector past it (connector-training/)")
    else:
        ok.append(f"every ladder rung has training content ({sum(len(v) for v in _by_rung.values())} lessons)")
except Exception as e:
    drift.append(f"could not verify training curriculum coverage: {e}")

# ── Evidence door (added 2026-08-07, decisions/2026-08-07_evidence-door.md) ──
# These five views are trusted surfaces: the Founder reads them to learn things about the company he
# cannot otherwise check. A silently broken one is worse than no view at all, so the machine
# checks them rather than waiting for a human to notice by eye.

# 1. the append-only stores stay append-only and parseable
try:
    sys.path.insert(0, os.path.join(ROOT, "runtime"))
    from ledger import Ledger as _Ldg
    _stores = ["loops/_trust/actions.jsonl", "loops/_trust/forecasts.jsonl",
               "loops/_trust/drills.jsonl", "loops/_twin/predictions.jsonl"]
    _bad, _nonmono = [], []
    for _s in _stores:
        _r = _Ldg(_s).read()
        if not _r["exists"]:
            continue
        if _r["bad"]:
            _bad.append(f"{_s} ({_r['bad']} unreadable line(s))")
        _seqs = [e["seq"] for e in _r["events"]]
        if _seqs != sorted(set(_seqs)):
            _nonmono.append(_s)
    if _bad:
        drift.append(f"evidence store(s) hold unreadable lines: {', '.join(_bad)} — the ledger is "
                     f"the audit trail; a corrupt row means recorded evidence was lost")
    elif _nonmono:
        drift.append(f"evidence store(s) have duplicate or out-of-order seq: {', '.join(_nonmono)} "
                     f"— monotonic seq is what makes tampering detectable")
    else:
        ok.append(f"evidence stores parse clean with monotonic seq ({len(_stores)} checked)")
except Exception as e:
    drift.append(f"could not verify the evidence stores: {e}")

# 2. every Evidence view still imports and answers
try:
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    _broken = []
    for _m in ("trust", "tripwires", "timemachine", "twin", "vacancies"):
        try:
            _mod = __import__(_m)
            if not callable(getattr(_mod, "build", None)):
                _broken.append(f"{_m} (no build())")
        except Exception as _e:
            _broken.append(f"{_m} ({type(_e).__name__})")
    if _broken:
        drift.append(f"Evidence view(s) not importable: {', '.join(_broken)} — HQ would render an "
                     f"error panel where the Founder expects an answer")
    else:
        ok.append("all 5 Evidence views import and expose build()")
except Exception as e:
    drift.append(f"could not verify the Evidence views: {e}")

# 3. no trip-wire check is silently broken
try:
    import tripwires as _tw
    _d = _tw.build()
    if _d["checkErrors"]:
        drift.append(f"{len(_d['checkErrors'])} trip-wire check(s) cannot be evaluated: "
                     + "; ".join(f"{c['file']} ({c['error']})" for c in _d['checkErrors'][:3])
                     + " — a broken trip-wire protects nothing while looking like it does")
    else:
        ok.append(f"all {_d['covered']} trip-wire checks evaluate cleanly "
                  f"({_d['coveragePct']}% of {_d['total']} decisions carry one)")
except Exception as e:
    drift.append(f"could not verify trip-wires: {e}")

# 4. no drill run references a drill that left the catalog
try:
    import trust_ledger as _tl
    _runs = {e.get("drill") for e in _Ldg("loops/_trust/drills.jsonl").read()["events"]
             if e.get("drill")}
    _orphan = sorted(_runs - set(_tl.DRILL_BY_ID))
    if _orphan:
        drift.append(f"drill run(s) reference ids no longer in the catalog: {_orphan} — the "
                     f"detection record and the catalog have drifted apart")
    else:
        ok.append(f"every recorded drill run maps to a catalog entry ({len(_tl.DRILLS)} drills defined)")
except Exception as e:
    drift.append(f"could not verify the drill catalog: {e}")

# ── HQ's finance mirror matches the workbook ──
# Added 2026-08-10 with the Finance tab. The model lives on three surfaces (workbook,
# dashboard/finance_model.json, 06_business-plan.md §8) and the first two are machine-
# checkable: if HQ is serving figures from a superseded version of the workbook, that
# is drift nobody would notice by eye.
try:
    import subprocess as _sp
    _r = _sp.run([sys.executable, os.path.join(ROOT, "runtime/finance_model_sync.py"), "--check"],
                 capture_output=True, text=True, timeout=60, cwd=ROOT)
    if _r.returncode == 0:
        ok.append("HQ's finance mirror matches finance/yourco-financial-model.xlsx")
    else:
        drift.append(f"HQ's finance mirror is stale — {(_r.stdout + _r.stderr).strip().splitlines()[0]} "
                     f"(fix: python3 runtime/finance_model_sync.py, then commit the workbook AND "
                     f"dashboard/finance_model.json together)")
except Exception as e:
    drift.append(f"could not verify the finance mirror: {e}")

# ── 06_business-plan.md §8 matches the model (the THIRD surface) ──
# Added 2026-08-10 after Melanie's second plan review. The check above verifies two of the
# model's three surfaces; the plan was the unchecked one, and it drifted the same day: a
# session rewrote the salary sentence in §8 and left the principals' three-year totals
# eleven words later reading $1.49M/$1.30M/$1.03M against a model saying $1.52M/$1.32M/$1.05M.
# A two-surface guard on a three-surface fact is how that survived a deliberate sweep.
#
# Tolerance is 1% — the plan rounds to 2-3 significant figures on purpose, so an exact match
# would be noise. 1% passes every legitimate rounding here and still catches the ~2% miss above.
# A row that cannot be FOUND is reported, never silently passed: a table someone reformatted
# is exactly when this check matters most.
def _money(tok):
    """'$1.52M' → 1520000 · '$530k' → 530000 · '190' → 190. None if not a number."""
    t = tok.strip().replace("*", "").replace(",", "").replace("$", "").strip()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([MmKk])?", t)
    if not m: return None
    v = float(m.group(1))
    return v * {"m": 1e6, "k": 1e3}.get((m.group(2) or "").lower(), 1)

PLAN_ROWS = [
    # (row label in §8, how to pull the model value, how many values per cell)
    ("Active clients — Y1 / Y2 / Y3", lambda s: [s["years"][i]["clients"] for i in (0, 1, 2)], 3),
    ("ARR run-rate — end Y3",         lambda s: [s["years"][2]["arr"]],                        1),
    ("Recognized revenue — Y1",       lambda s: [s["years"][0]["revenue"]],                    1),
    ("Recognized revenue — Y3",       lambda s: [s["years"][2]["revenue"]],                    1),
    ("EBITDA — Y3",                   lambda s: [s["years"][2]["ebitda"]],                     1),
    ("Humans — end Y1 / Y3",          lambda s: [s["years"][0]["people"], s["years"][2]["people"]], 2),
]
CASES = ["Conservative", "Target", "Aggressive"]
_plan_bad, _plan_checked = [], 0
try:
    _fm = json.load(open(os.path.join(ROOT, "dashboard/finance_model.json"), encoding="utf-8"))
    _plan = read(os.path.join(ROOT, "06_business-plan.md"))

    for label, pull, arity in PLAN_ROWS:
        line = next((l for l in _plan.splitlines()
                     if l.lstrip().startswith("|") and label in l), None)
        if line is None:
            _plan_bad.append(f"§8 row '{label}' not found — table reformatted or row removed")
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            _plan_bad.append(f"§8 row '{label}' has {len(cells)} columns, expected 4")
            continue
        for case, cell in zip(CASES, cells[1:]):
            stated = [_money(t) for t in cell.replace("/", " / ").split("/")]
            stated = [v for v in stated if v is not None]
            actual = pull(_fm["scenarios"][case])
            if len(stated) != arity:
                _plan_bad.append(f"§8 '{label}' [{case}]: could not read {arity} number(s) from {cell!r}")
                continue
            for got, want in zip(stated, actual):
                _plan_checked += 1
                if want and abs(got - want) / abs(want) > 0.01:
                    _plan_bad.append(f"§8 '{label}' [{case}]: plan says {got:,.0f}, model says {want:,.0f}")

    # The principals' three-year totals — the assertion that actually drifted.
    m = re.search(r"three-year totals are the Founder\s+\*{0,2}\$?([\d.]+[MmKk]?)\*{0,2},\s*"
                  r"Partner B\s+\*{0,2}\$?([\d.]+[MmKk]?)\*{0,2},\s*"
                  r"Mike\s+\*{0,2}\$?([\d.]+[MmKk]?)\*{0,2}", _plan)
    if not m:
        _plan_bad.append("the principals' three-year totals sentence is missing from the plan")
    else:
        for who, tok in zip(("the Founder", "Partner B", "Mike"), m.groups()):
            got, want = _money(tok), _fm["principalEarnings3yr"]["Target"][who]
            _plan_checked += 1
            if got is None or abs(got - want) / abs(want) > 0.01:
                _plan_bad.append(f"principals' 3-yr total [{who}]: plan says {tok}, model says {want:,.0f}")

    if _plan_bad:
        drift.extend(f"06_business-plan.md drifted from the model — {b} "
                     f"(fix: correct the plan, never the model — §8 says the model is canonical)"
                     for b in _plan_bad)
    else:
        ok.append(f"06_business-plan.md §8 matches the model ({_plan_checked} figures)")
except Exception as e:
    drift.append(f"could not verify 06_business-plan.md against the model: {e}")

# ── counsel-gate numbers are unique ──
# Added 2026-08-08: two different gates were both numbered 13 for a month (the
# Sample Client postcard imagery gate and the SaaS-replacement ownership/IP gate),
# because a new gate was numbered from the row count instead of from the table's
# max. Docs across the repo then cited "gate #13" meaning two different things.
try:
    _gates = re.findall(r"^\|\s*(\d+)\s*\|", read("processes/counsel-gates.md"), re.M)
    _dupes = sorted({g for g in _gates if _gates.count(g) > 1}, key=int)
    if _dupes:
        drift.append(f"counsel-gates.md has duplicate gate number(s): {', '.join(_dupes)} — every "
                     f"'gate #N' reference in the repo is now ambiguous. Renumber the less-referenced "
                     f"row and sweep its citations in the same commit.")
    else:
        ok.append(f"counsel-gate numbers unique ({len(_gates)} gates, next free #{max(map(int, _gates)) + 1})")
except Exception as e:
    drift.append(f"could not verify counsel-gate numbering: {e}")

# ── 13. The business plan must speak the LOCKED OS-tier pricing (restored 2026-08-09) ──
# This guard existed as invariant #11 from 2026-07-06 and was DESTROYED when two clones diverged —
# which is exactly how the corrected plan ($670k/$4.4M/$12M) was lost and the retired $850/$750 lines
# came back for 34 days. Restored, renumbered (11 and 12 were reused by mistake on 08-07).
RETIRED_PRICES = [r"\$850\b", r"\$750/mo", r"~\$240k", r"Tier 1 \"handle it\"", r"Tier-1 ~\$4k"]
_plan = read(os.path.join(ROOT, "06_business-plan.md"))
_back = [p_ for p_ in RETIRED_PRICES if re.search(p_, _plan)]
if _back:
    drift.append(f"06_business-plan.md has retired pricing back in it ({_back}) — the locked ladder is "
                 f"Core $3-4k/mo → Command $8.5-10k/mo (pricing/v0/os-tiers.md). This exact regression "
                 f"cost 34 days once already.")
elif not re.search(r"3,100|Core.*\$3", _plan):
    drift.append("06_business-plan.md no longer references the OS-tier blended retainer — verify it wasn't reverted")
else:
    ok.append("06_business-plan.md speaks the locked OS-tier pricing")

# 5. the partner lock-in run still parses out of its schedule file
# HQ's Partners door reads processes/partner-b-walkthrough-schedule.md rather than keeping a second
# copy of the calendar. That's the right call, and it means an edit to the table's shape can
# silently empty the view — so the parse itself is an invariant.
try:
    import lockin as _lk
    _r = _lk.build()
    if _r.get("error"):
        drift.append(f"lock-in run unreadable: {_r['error']}")
    elif not _r.get("total") or not _r.get("sessionsTotal"):
        drift.append("lock-in run parsed to zero domains or zero sessions — the calendar table in "
                     "processes/partner-b-walkthrough-schedule.md changed shape and HQ's Partners door "
                     "is now blank")
    else:
        _orphan = [d["domain"] for d in _r["domains"]
                   if d["reviewDate"] and not d["lockDate"] and d["domain"] != "Who to add to the CRM"]
        if _orphan:
            drift.append(f"lock-in domain(s) reviewed but never scheduled to lock: {_orphan} — "
                         f"add a lock row to the calendar or they can never be marked done")
        else:
            ok.append(f"lock-in run parses: {_r['sessionsTotal']} sessions, {_r['total']} domains, "
                      f"{_r['lockedConfirmed']} locked")
except Exception as e:
    drift.append(f"could not verify the lock-in run: {e}")

# ── Connector Program v2 invariants (added 2026-08-11) ──────────────────────────────────
# These exist because the v2 change touched code + 9 documents at once, and the two facts most
# likely to be quoted from memory later are (a) which rung opens recruiting and (b) the bounty
# amounts. `UNLOCKS` and the BOUNTY_* constants are the sources; every doc must agree with them.
try:
    sys.path.insert(0, os.path.join(ROOT, "crm"))
    import connector_ladder as _cl, connector_statements as _cs, connector_training as _ct

    # (a) the recruiting rung — the docs must not describe a gate the code doesn't hold
    _recruit_rung = next((k for k, v in _cl.UNLOCKS.items() if "recruit_connectors" in v), None)
    if _recruit_rung != "R1":
        drift.append(f"recruit_connectors is at {_recruit_rung}; the v2 decision put it at R1 "
                     f"(decisions/2026-08-11_connector-program-v2.md) — sweep the docs if this moved on purpose")
    else:
        _stale = []
        for _p in ("processes/partnerships/connector-os.md",
                   "processes/partnerships/connector-onboarding.md",
                   "processes/partnerships/referral-program.md",
                   "processes/partnerships/rep-packet.md",
                   "processes/partnerships/connector-training/13-how-this-program-works.md",
                   "processes/partnerships/connector-training/04-building-a-team.md"):
            _s = read(os.path.join(ROOT, _p))
            # "recruit … at R2" in any order within a short window = a doc still teaching the old gate
            if re.search(r"recruit[^.\n]{0,80}\bR2\b|\bR2\b[^.\n]{0,80}recruit", _s, re.I):
                # allowed only when the sentence is explicitly marking the change as historical
                _win = re.search(r"[^.\n]*(recruit[^.\n]{0,80}\bR2\b|\bR2\b[^.\n]{0,80}recruit)[^.\n]*", _s, re.I)
                # `confirm` exempts the operator-confirmation sentence, which legitimately names R2 and
                # the recruiting lesson in one breath without claiming R2 is the recruiting gate.
                if not re.search(r"moved|used to|previously|was\b|no longer|not\b|changed|confirm",
                                 _win.group(0), re.I):
                    _stale.append(os.path.basename(_p))
        if _stale:
            drift.append(f"docs still teach recruiting at R2 after the move to R1: {_stale}")
        else:
            ok.append("recruiting gate is R1 in code and no doc still teaches R2")

    # (b) the bounty amounts — stated once in code, quoted in prose; they must match
    _v, _b = _cs.BOUNTY_VERIFIED, _cs.BOUNTY_BOOKED
    _bad = []
    for _p in ("processes/partnerships/referral-program.md",
               "processes/partnerships/connector-os.md",
               "processes/partnerships/connector-training/14-submitting-contacts.md",
               "CLAUDE.md"):
        _s = read(os.path.join(ROOT, _p))
        if "bounty" not in _s.lower() and "submission" not in _s.lower():
            continue
        for _amt in set(int(x) for x in re.findall(r"\$(\d{1,3})\b", _s)):
            if _amt in (_v, _b) or _amt == 100:      # 100 = the Type-1 client credit, a different fact
                continue
            _ctx = re.search(r"[^.\n]{0,90}\$" + str(_amt) + r"\b[^.\n]{0,60}", _s)
            if _ctx and re.search(r"bount|submi|verif|booked call", _ctx.group(0), re.I):
                _bad.append(f"{os.path.basename(_p)}: ${_amt} near bounty text (code says ${_v}/${_b})")
    if _bad:
        drift.append("bounty amount drift — " + "; ".join(_bad))
    else:
        ok.append(f"submission bounty is ${_v}/${_b} in code and every doc agrees")

    # (c) staged posture: nothing may claim the bounty is payable while it is not
    if _cs.BOUNTY_PAYABLE:
        ok.append("submission bounty is PAYABLE — launch/counsel must have cleared; verify §A/§B")
    else:
        _claims = [os.path.basename(_p) for _p in
                   ("processes/partnerships/referral-program.md", "processes/partnerships/connector-os.md")
                   if "not payable" not in read(os.path.join(ROOT, _p)).lower()]
        if _claims:
            drift.append(f"bounty is not payable but these don't say so: {_claims}")
        else:
            ok.append("bounty renders as accrued-not-payable everywhere it is described")

    # (d) the recruiting lesson keeps its operator confirmation wherever the ladder puts it
    _team = next((L for L in _ct.load_lessons()
                  if (L.get("unlocks") or "").strip() == "recruit_connectors"), None)
    if not _team:
        drift.append("no training lesson unlocks recruit_connectors — the capability has no curriculum")
    elif not _ct.needs_confirmation(_team, _team["rung"]):
        drift.append("the recruiting lesson is self-marked; it must stay operator-confirmed "
                     "(connector_training.CONFIRM_CAPS) now that it sits below R2")
    else:
        ok.append("recruiting lesson still requires an operator's confirmation at R1")

    # (e) every capability the ladder grants has training behind it.
    # Recorded exceptions, with the reason each is covered some other way — a documented absence, not
    # a silent pass. Deleting a line here means claiming a lesson now exists; check that it does.
    _NO_LESSON_OK = {
        "console": "the console IS the surface the training runs on",
        "co_brand": "covered by the quoting/co-branding lesson at the same rung",
        "deep_co_brand": "same lesson, deeper permission",
        "referral_spotter": "opt-in consent conversation at onboarding step 9 — a human conversation "
                            "about inbox/calendar permission, deliberately not a self-marked lesson",
    }
    _covered = {(L.get("unlocks") or "").strip() for L in _ct.load_lessons()}
    _uncovered = [c for caps in _cl.UNLOCKS.values() for c in caps
                  if c not in _covered and c not in _NO_LESSON_OK]
    if _uncovered:
        drift.append(f"capabilities with no lesson behind them: {sorted(_uncovered)}")
    else:
        ok.append(f"every gated capability has a lesson ({len(_NO_LESSON_OK)} recorded exceptions: "
                  f"{', '.join(sorted(_NO_LESSON_OK))})")
except Exception as e:
    drift.append(f"could not verify the connector program invariants: {e}")

# ── CRM stage keys: derived from the ladder, never hand-listed ──────────────────────────
# Added 2026-08-13 after the THIRD instance of stage-key drift. The 8/11 rename
# (sitdown/audit -> discovery, proposal -> demo-proposal, ...) left a hand-written array in
# the KPI band — `["sitdown","audit","proposal","signed","build"]` — which silently reported
# 0 qualified deals for two days. It read as a fact, not as a bug, which is what makes this
# class of drift expensive. Any NEW hand-written list of stage keys in the CRM UI fails here.
# Legitimate legacy-alias maps declare themselves with the word "alias" or "legacy" nearby.
try:
    import json as _json, re as _re
    _crm = os.path.join(ROOT, "crm")
    _stages = {s["key"] for s in _json.load(open(os.path.join(_crm, "data.json")))["stages"]}
    _dead = {"sitdown", "audit", "proposal", "signed", "build", "relationship", "givefirst",
             "prospect", "first-touch"} - _stages
    _offenders = []
    for _f in ("index.html",):
        _src = read(os.path.join(_crm, _f))
        for _m in _re.finditer(r'\[[^\[\]\n]{0,200}\]', _src):
            _lits = set(_re.findall(r'"([a-z][a-z-]{2,24})"', _m.group(0)))
            if len(_lits) < 2 or not (_lits & _dead):
                continue
            # Require the array to be a LIST OF STAGE KEYS and nothing else. Without this,
            # `["relationship","Relationship / how we know them","text"]` — a contact FIELD
            # descriptor — trips it, because "relationship" happens to be both a retired stage
            # key and a live field name. A real stage list has no non-stage members.
            if _lits - (_stages | _dead):
                continue
            _ctx = _src[max(0, _m.start() - 260):_m.end() + 80].lower()
            if "alias" in _ctx or "legacy" in _ctx or "pre-2026" in _ctx:
                continue                      # a declared back-compat map is fine
            _line = _src[:_m.start()].count("\n") + 1
            _offenders.append(f"{_f}:{_line} {sorted(_lits & _dead)}")
    if _offenders:
        drift.append("CRM hand-writes retired stage keys instead of deriving them from "
                     f"data.json stages — {'; '.join(_offenders[:4])}")
    else:
        ok.append(f"CRM stage keys derive from the ladder ({len(_stages)} rungs); "
                  "no undeclared use of a retired key")
except Exception as e:
    drift.append(f"could not verify CRM stage-key derivation: {e}")

# ── referral economics: ONE rate card, and two engines that agree ────────────────────────
# Added 2026-08-13 with `decisions/2026-08-13_one-referral-rate-card.md`. Two things drifted
# here and both cost real money:
#   (a) the flat $100/mo client credit was 10% of a $1,000/mo deal and was never re-based to
#       the $3,000 Core floor, so the same referral paid a connector $300 and a client $100;
#   (b) crm/index.html counted only stage "live" as paying while crm/connector_statements.py
#       counted "live" AND "expand", so an expanded client's referrer earned $0 in the cockpit
#       and $300 on the statement Charles sends.
# Money math split across a JS cockpit and a Python statement generator cannot be checked by
# eye, so it is checked here.
try:
    import json as _json
    _crm = os.path.join(ROOT, "crm")
    _idx = read(os.path.join(_crm, "index.html"))
    _stm = read(os.path.join(_crm, "connector_statements.py"))
    _re2 = __import__("re")
    _bad = []
    # Check CODE, not prose. The comments in both files necessarily NAME the retired identifiers
    # to explain why they are gone — a first cut of this invariant flagged its own documentation.
    _idx_code = _re2.sub(r"/\*.*?\*/", "", _idx, flags=_re2.S)
    _idx_code = _re2.sub(r"^\s*//.*$", "", _idx_code, flags=_re2.M)
    _stm_code = _re2.sub(r"^\s*#.*$", "", _stm, flags=_re2.M)
    # (a) the retired flat rate must not come back anywhere that computes
    if "CLIENT_CREDIT" in _idx_code or "clientReferralCredits" in _idx_code:
        _bad.append("crm/index.html still computes the retired flat client credit")
    if "CLIENT_CREDIT" in _stm_code:
        _bad.append("crm/connector_statements.py still computes with CLIENT_CREDIT")
    # (b) `expand` was retired as a rung 2026-08-13 — Live is terminal and an expansion is a
    # separate deal. Any module that still treats it as a stage will price a rung that no longer
    # exists, or (worse) report a live client as not-live. ghost.LEGACY is the one exception: it
    # MUST keep the alias so historical board states replayed out of git fold forward.
    _stage_files = ["index.html", "mirror.py", "calibration.py", "adversarial.py",
                    "expansion.py", "connector_ladder.py", "connector_statements.py"]
    for _f in _stage_files:
        _t = read(os.path.join(_crm, _f))
        _tc = _re2.sub(r"/\*.*?\*/", "", _t, flags=_re2.S)
        _tc = _re2.sub(r"^\s*(//|#).*$", "", _tc, flags=_re2.M)
        if '"expand"' in _tc or "'expand'" in _tc:
            _bad.append(f"crm/{_f} still treats `expand` as a stage")
    if '"expand": "live"' not in read(os.path.join(_crm, "ghost.py")):
        _bad.append("crm/ghost.py lost the expand->live LEGACY alias (git replay will break)")
    if any(s.get("key") == "expand" for s in
           _json.load(open(os.path.join(_crm, "data.json")))["stages"]):
        _bad.append("crm/data.json still lists `expand` on the ladder")
    # (c) a company can hold several deals — money must SUM, never read the first one
    if "const mrrOfCo" not in _idx:
        _bad.append("crm/index.html lost mrrOfCo — per-company MRR would read one deal only")
    if 'live = {x["companyId"]: x for x in deals' in _stm:
        _bad.append("crm/connector_statements.py keys live deals by company again — a second "
                    "live deal on one company is silently dropped")
    # the docs must not still teach two types
    _rp = read(os.path.join(ROOT, "processes/partnerships/referral-program.md"))
    if "$100/month off their own retainer" in _rp:
        _bad.append("referral-program.md still teaches the flat $100 client credit")
    if _bad:
        drift.append("referral economics drifted — " + "; ".join(_bad))
    else:
        ok.append("referral economics + ladder: one rate card, `expand` retired everywhere but "
                  "ghost's LEGACY alias, per-company MRR sums, and both engines "
                  "agree on which stages pay (live only — `expand` retired 2026-08-13)")
except Exception as e:
    drift.append(f"could not verify referral economics: {e}")

# ── the insight layer: every block delegates, nothing forks ─────────────────────────────
# Added 2026-08-13 with the block registry. `crm/blocks.py` packages 16 capabilities behind
# one interface — and the ONE way that goes wrong is a block that computes its own answer
# instead of delegating, giving the CRM two answers to one question. Same failure class as
# the payout-math incident earlier the same day.
try:
    import importlib.util as _ilu
    _crm = os.path.join(ROOT, "crm")
    _spec = _ilu.spec_from_file_location("_blocks", os.path.join(_crm, "blocks.py"))
    _bm = _ilu.module_from_spec(_spec)
    sys.path.insert(0, _crm)
    _spec.loader.exec_module(_bm)
    _bad = []
    for _k, _b in _bm.BLOCKS.items():
        if not _b.get("owner") or not _b.get("rung"):
            _bad.append(f"block `{_k}` has no owner/rung")
        _m = _b.get("module")
        if _m and not os.path.isfile(os.path.join(_crm, _m + ".py")):
            _bad.append(f"block `{_k}` points at crm/{_m}.py, which does not exist")
    # every insight the server serves must be reachable, and vice versa
    _srv = read(os.path.join(_crm, "server.py"))
    for _k in ("price", "autopsy", "capacity", "decisions", "antipipeline", "disputes", "blocks"):
        if f'"{_k}"' not in _srv:
            _bad.append(f"insight `{_k}` is not registered in crm/server.py")
    if _bad:
        drift.append("insight layer drifted — " + "; ".join(_bad[:5]))
    else:
        ok.append(f"insight layer: {len(_bm.BLOCKS)} blocks, each with an owner + rung, each "
                  f"delegating to a module that exists; all endpoints registered")
except Exception as e:
    drift.append(f"could not verify the insight layer: {e}")

# 6. every CRM stage key is classified by HQ  (added 2026-08-13 after it drifted)
# The CRM restructured its ladder and the bench became `pre-convo`; server.py's BENCH_STAGES
# still said `prospect`, so HQ counted all 18 bench deals as in-motion and reported 21 deals /
# $24k against a real figure of 3. A stage rename must never again be able to silently inflate
# the most-quoted number in the company.
try:
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import server as _srv
    _crm = json.load(open(os.path.join(ROOT, "crm", "data.json")))
    _keys = [s.get("key") for s in (_crm.get("stages") or []) if s.get("key")]
    _known = set(_srv.BENCH_STAGES) | set(_srv.CLOSED_STAGES)
    # a stage is "classified" if HQ either benches it, closes it, or deliberately treats it as
    # in-motion; the risk is a NEW key nobody considered, so compare against the ladder we know
    _unknown = [k for k in _keys if k not in _known and k not in
                ("discovery", "demo-proposal", "signed-onboarding", "build-implementation",
                 "testing", "expand")]
    if not _keys:
        drift.append("crm/data.json declares no stages — HQ's pipeline classification is unanchored")
    elif _unknown:
        drift.append(f"CRM stage key(s) unknown to dashboard/server.py: {_unknown} — HQ will "
                     f"silently treat them as deals IN MOTION and inflate the pipeline figure. "
                     f"Classify them in BENCH_STAGES/CLOSED_STAGES or add them to this check.")
    else:
        ok.append(f"all {len(_keys)} CRM stage keys are classified by HQ "
                  f"(bench: {', '.join(_srv.BENCH_STAGES)})")
except Exception as e:
    drift.append(f"could not verify CRM stage classification: {e}")

# ── Connector Console v3.1 invariants (added 2026-08-13) ────────────────────────────────
# Every one of these six builds earns its keep by REFUSING rather than guessing. A refusal that
# silently becomes a zero is the exact failure they exist to prevent, and it would be invisible on
# the page — so the staged flags and the sample floors are asserted here rather than trusted.
try:
    sys.path.insert(0, os.path.join(ROOT, "crm"))
    sys.path.insert(0, os.path.join(ROOT, "runtime"))
    import connector_statements as _cs2, connector_escrow as _ce, connector_perks as _cp
    import connector_calibration as _cc, connector_ghost as _cg, connector_approvals as _ca

    # (a) nothing in the connector program may be payable while the program is staged
    _pay = {"bounty": _cs2.BOUNTY_PAYABLE, "escrow": _ce.ESCROW_PAYABLE, "os-grant": _cp.GRANT_ACTIVE}
    _live = [k for k, v in _pay.items() if v]
    if _live:
        drift.append(f"connector payment(s) marked PAYABLE while the program is staged: {_live} — "
                     f"if launch + counsel cleared, say so in decisions/ and update this check")
    else:
        ok.append("every connector payment class is staged (bounty · escrow · OS grant)")

    # (b) the sample floors that make the refusals meaningful — a floor of 1 is not a floor
    _floors = {"ghost referrals": _cg.MIN_REFERRALS_FOR_TOTAL, "calibration": _cc.MIN_RESOLVED}
    _weak = [k for k, v in _floors.items() if v < 3]
    if _weak:
        drift.append(f"sample floor too low to defend a number: {_weak}")
    else:
        ok.append(f"refusal floors hold (ghost ≥{_cg.MIN_REFERRALS_FOR_TOTAL} referrals, "
                  f"calibration ≥{_cc.MIN_RESOLVED} resolved)")

    # (c) the ghost must never fork yourco's median — it filters `ghost.compute()`, it does not
    #     re-derive. A local median here would drift from the board and be impossible to spot by eye.
    _gsrc = read(os.path.join(ROOT, "crm/connector_ghost.py"))
    if re.search(r"\bdef\s+(velocit|median|occupanc)", _gsrc):
        drift.append("connector_ghost.py defines its own velocity/median — it must import ghost.py's")
    else:
        ok.append("connector ghost imports yourco's median, never re-derives it")

    # (d) tier basis: the docs quote thresholds, the code owns them
    _t = {"rates": [10, 12.5, 15]}
    _lo, _hi = _cs2.MRR_THRESHOLDS
    _spec = read(os.path.join(ROOT, "processes/partnerships/referral-program.md"))
    if f"${_lo:,}" not in _spec or f"${_hi:,}" not in _spec:
        drift.append(f"referral-program.md does not quote the MRR thresholds in code "
                     f"(${_lo:,} / ${_hi:,})")
    elif _cs2._tier(_lo, _t)[0] != 2 or _cs2._tier(_hi, _t)[0] != 3:
        drift.append("MRR thresholds do not produce the tiers they are documented to produce")
    else:
        ok.append(f"commission tiers band on MRR (${_lo:,} / ${_hi:,}) in code and spec")
    # The bands are round Core-floor multiples, NOT a like-for-like restatement of the old count
    # rule (6 and 11 actives = $18,000 / $33,000). They are one client looser at each end, which is
    # deliberate — but a doc that calls the change "the same thresholds" or "not a repricing" is
    # telling a connector something false about their own comp, so that phrasing is what this checks.
    _core = lambda n: {"active": [{"mrr": _cs2.CORE_FLOOR}] * n}
    if (_cs2._tier(_cs2.tier_input(_core(5), _t), _t)[1] != 12.5
            or _cs2._tier(_cs2.tier_input(_core(10), _t), _t)[1] != 15):
        drift.append(f"MRR bands are no longer round Core-floor multiples "
                     f"(5 × ${_cs2.CORE_FLOOR:,} → 12.5%, 10 × → 15%) — re-check every doc that "
                     f"quotes the client-equivalents")
    else:
        _claims = [os.path.basename(_p) for _p in
                   ("processes/partnerships/referral-program.md",
                    "decisions/2026-08-13_connector-console-v3.md")
                   if re.search(r"exactly the same place|not a repricing|like-for-like restatement(?! )",
                                read(os.path.join(ROOT, _p)), re.I)]
        if _claims:
            drift.append(f"these still call the MRR move backward-compatible, which it is not "
                         f"(it is one client looser at each end): {_claims}")
        else:
            ok.append("MRR bands are round Core multiples and no doc claims they are like-for-like")

    # The console kept its OWN copy of the bands and rendered "6–10 active" on a page whose rate was
    # already computed from revenue — caught by eye on 2026-08-13, which is exactly the failure the
    # watchdog exists to prevent. `tier_progress` must ask connector_statements, never restate.
    _con = read(os.path.join(ROOT, "processes/partnerships/connector-console/server.py"))
    _tp = re.search(r"def tier_progress\(.*?\n(?=\ndef )", _con, re.S)
    if not _tp:
        drift.append("connector console: tier_progress() not found — the tier basis check is blind")
    elif re.search(r'thresholds"\s*\)\s*or\s*\[6,\s*11\]', _tp.group(0)) and \
            "_tier_basis" not in _tp.group(0):
        drift.append("connector console: tier_progress() hardcodes the count thresholds again — it "
                     "must read the basis + bands from connector_statements")
    elif "active</span>" in _con and "_tier_basis" not in _tp.group(0):
        drift.append("connector console still renders count-style tier bands ('N active')")
    else:
        ok.append("connector console reads its tier bands from the money module, never its own copy")

    # (e) a complaint must always reset the approval gate to the floor
    _fx = {"meta": {"connectorApprovals": [
                {"id": f"a{i}", "connector": "X", "status": "approved",
                 "createdAt": "2026-01-01T00:00:00+00:00",
                 "decidedAt": "2026-01-01T00:00:00+00:00"} for i in range(20)]}}
    if _ca.rung_for("X", _fx)["key"] == "A0":
        drift.append("approval rung never rises — 20 clean approvals should reach A2")
    else:
        _fx["meta"]["connectorIncidents"] = [{"connector": "X", "kind": "complaint",
                                              "at": "2026-06-01T00:00:00+00:00"}]
        if _ca.rung_for("X", _fx)["key"] != "A0":
            drift.append("a complaint no longer resets the approval gate to A0")
        else:
            ok.append("approval gate rises on clean evidence and resets to A0 on a complaint")
except Exception as e:
    drift.append(f"could not verify the connector console v3.1 invariants: {e}")

# 7. the activity types HQ counts as inputs still exist in the CRM  (added 2026-08-13)
# dashboard/wbr.py counts controllable inputs by matching activity-type STRINGS. Rename or drop
# one in the CRM and the input silently reads zero forever — a metric that goes quiet looks like
# a bad week, not a broken join, which is the worst way for an instrument to fail.
try:
    _c = json.load(open(os.path.join(ROOT, "crm/data.json")))
    _types = set(_c.get("meta", {}).get("activityTypes") or [])
    _needed = {"Referral ask", "Referral", "Warm intro made", "Meeting", "Call", "Deliverable"}
    _gone = sorted(_needed - _types)
    if _gone:
        drift.append(f"activity type(s) HQ counts as WBR inputs are missing from the CRM: {_gone} "
                     f"— dashboard/wbr.py matches these strings exactly, so the input would read "
                     f"zero forever and look like a quiet week rather than a broken join")
    else:
        ok.append(f"all {len(_needed)} WBR input activity types present in the CRM")
    # data.js is auto-generated from data.json; a stale mirror serves the UI the old list
    _js = read(os.path.join(ROOT, "crm/data.js"))
    if _js and "Referral ask" not in _js:
        drift.append("crm/data.js does not carry 'Referral ask' — the static mirror is stale, so "
                     "the CRM UI will not offer the type even though data.json defines it. "
                     "Regenerate via crm/server.py write_mirror().")
    elif _js:
        ok.append("crm/data.js mirror carries the new activity type")
except Exception as e:
    drift.append(f"could not verify WBR input activity types: {e}")

# 8. every company carries a createdAt  (added 2026-08-13)
# newProspectsAdded counts companies whose createdAt falls in the window. A company written
# without one is invisible to that metric forever, and top-of-funnel replenishment would quietly
# under-report — the failure looks like a slow week, not a missing field.
try:
    _c8 = json.load(open(os.path.join(ROOT, "crm/data.json")))
    _cos = _c8.get("companies") or []
    _no = [c.get("name") or c.get("id") for c in _cos if not c.get("createdAt")]
    _src = {}
    for c in _cos:
        _src[c.get("createdAtSource") or "(unset)"] = _src.get(c.get("createdAtSource") or "(unset)", 0) + 1
    if _no:
        drift.append(f"{len(_no)} company/companies have no createdAt: {_no[:6]} — invisible to "
                     f"the newProspectsAdded input forever. Every creation path in runtime/ and "
                     f"crm/integrations/ sets it; one of them was missed, or a row was written by hand.")
    else:
        ok.append(f"all {len(_cos)} companies carry createdAt ({_src})")
except Exception as e:
    drift.append(f"could not verify company createdAt: {e}")


# 9. any doc stating the connector count must match the CRM  (added 2026-08-23)
# Caught by eye: the flywheel doc and the tool-triage ledger both read "0 active connectors, 23
# prospective" against a real 22. These numbers are the evidence base for the ⚠ belief-not-finding
# caveat on the whole people loop — if the count drifts, the caveat is arguing from a number nobody
# can reproduce, which is worse than having no number. Same reason the "0 referred clients" half is
# checked: the day a referral lands, that caveat has to be LIFTED, and nothing else would notice.
try:
    _c9 = json.load(open(os.path.join(ROOT, "crm/data.json")))
    _conn = [c for c in (_c9.get("contacts") or [])
             if c.get("kind") == "internal" and c.get("teamRole") == "connector"]
    # blank teamStatus reads 'prospect' by design (tsOf / connector_ladder) — mirror that here
    _act = sum(1 for c in _conn if c.get("teamStatus") == "active")
    _pro = len(_conn) - _act
    _refd = sum(1 for c in (_c9.get("companies") or []) if c.get("referrer"))
    _pat = re.compile(r"(\d+)\s+active connectors,\s*(\d+)\s+prospective", re.I)
    _refpat = re.compile(r"(\d+)\s+referred clients", re.I)
    _scanned, _bad = 0, []
    for _p in glob.glob(os.path.join(ROOT, "**/*.md"), recursive=True):
        _rel = os.path.relpath(_p, ROOT)
        if _rel.startswith(("loops/", "_archive/", ".claude/", ".git/")):
            continue  # dated artifacts are point-in-time records, not live claims
        _t = read(_p)
        for _m in _pat.finditer(_t):
            _scanned += 1
            if (int(_m.group(1)), int(_m.group(2))) != (_act, _pro):
                _bad.append(f"{_rel} says {_m.group(1)} active / {_m.group(2)} prospective")
        for _m in _refpat.finditer(_t):
            _scanned += 1
            if int(_m.group(1)) != _refd:
                _bad.append(f"{_rel} says {_m.group(1)} referred clients")
    if _bad:
        drift.append(f"connector counts disagree with the CRM (live: {_act} active / {_pro} "
                     f"prospective / {_refd} referred): " + "; ".join(_bad[:6]) +
                     ". These numbers carry the ⚠ belief-not-finding caveat on the people loop — "
                     "re-base them, or if a referral has landed, LIFT the caveat.")
    else:
        ok.append(f"every stated connector count matches the CRM ({_scanned} claim(s) checked: "
                  f"{_act} active / {_pro} prospective / {_refd} referred)")
except Exception as e:
    drift.append(f"could not verify stated connector counts: {e}")


# ── every top-level directory is named in CLAUDE.md's folder map ──
# Added 2026-08-22 after "Pre Build Ideas" (577 files, 25% of the repo) went a week
# unmapped: it entered via an automated `OS sync` backup commit, so no human ever hit
# the change-one-sweep-all rule. A folder the nightly backup imports is invisible to
# every discipline we have — this is the machine backstop for exactly that.
try:
    _claude = read(os.path.join(ROOT, "CLAUDE.md"))
    _dirs = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"],
                           capture_output=True, text=True, timeout=60).stdout.split("\0")
    _tops = sorted({d.split("/")[0] for d in _dirs if "/" in d})
    _unmapped = [d for d in _tops if f"`{d}/`" not in _claude and not d.startswith(".")]
    if _unmapped:
        _counts = []
        for _d in _unmapped:
            _n = len([x for x in _dirs if x.startswith(_d + "/")])
            _counts.append(f"{_d}/ ({_n} files)")
        drift.append("top-level folder(s) missing from CLAUDE.md's folder map: " +
                     ", ".join(_counts) + ". A session boots without knowing these exist. "
                     "Add each to the map with what it is and when to use it.")
    else:
        ok.append(f"all {len(_tops)} top-level folders are named in CLAUDE.md's folder map")
except Exception as e:
    drift.append(f"could not verify the folder map: {e}")


# ── no two launch.json entries claim the same port or the same name ──
# Added 2026-08-22: the 71 prebuilds were assigned 8821-8891 without checking that the
# playground already owned 8890/8891, so whichever started second silently failed to bind.
try:
    _lj = json.loads(read(os.path.join(ROOT, ".claude/launch.json")))["configurations"]
    _pc, _nc = {}, {}
    for _c in _lj:
        _pc.setdefault(_c["port"], []).append(_c["name"])
        _nc.setdefault(_c["name"], []).append(_c["port"])
    _dp = {k: v for k, v in _pc.items() if len(v) > 1}
    _dn = {k: v for k, v in _nc.items() if len(v) > 1}
    if _dp or _dn:
        _msg = []
        if _dp: _msg.append("ports claimed twice: " + "; ".join(f"{k} -> {', '.join(v)}" for k, v in _dp.items()))
        if _dn: _msg.append("names used twice: " + "; ".join(f"{k} -> {v}" for k, v in _dn.items()))
        drift.append(".claude/launch.json collisions — the second server to start fails to bind: " + " | ".join(_msg))
    else:
        ok.append(f"launch.json: {len(_lj)} entries, no duplicate port or name")
except Exception as e:
    drift.append(f"could not verify launch.json: {e}")


# ── the contact-email rule: founder@yourco.example.com, never hello@, never an OtherVenture address ──
# Added 2026-08-23. CLAUDE.md calls this out as having "leaked three times before it was
# written down" — and it had leaked three MORE times since: Sadie's Reddit User-Agent (a
# header Reddit's own servers receive) and three pieces of Pickle's prospect-facing
# collateral, all surviving the 2026-06-23 sweep that was supposed to end it. A rule that
# has leaked six times is not a rule anyone remembers; it is one a machine has to hold.
try:
    _banned = re.compile(r"hello@yourco\.com|@OtherVenture", re.I)
    # Three files legitimately contain the banned string because they DESCRIBE or IMPLEMENT the
    # ban rather than violate it. Everything else is a real leak.
    _exempt = ("agents/webb/pages/2026-06-23_os-alignment-and-email.md",  # the record OF the sweep
               "runtime/consistency-check.py",                            # states the pattern it bans
               "07_RULES.md")                                                # records the 2026-08-23 rewrite
    # .mailmap was deleted 2026-08-23 (history rewritten instead of remapped) but stays in the
    # glob: if anyone ever recreates one, this check must see it rather than skip it silently.
    _files = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "*.py", "*.md", "*.html",
                             "*.json", "*.sh", "*.txt", ".mailmap"],
                            capture_output=True, text=True, timeout=60).stdout.split("\0")
    _hits = []
    for _f in _files:
        if not _f or _f in _exempt or _f.startswith("_archive/"):
            continue
        try:
            _t = read(os.path.join(ROOT, _f))
        except Exception:
            continue
        # skip lines that are ABOUT the rule rather than violating it
        for _ln in _t.splitlines():
            if _banned.search(_ln) and "never" not in _ln.lower():
                _hits.append(_f)
                break
    if _hits:
        drift.append("banned contact address on " + str(len(_hits)) + " surface(s) — yourco's "
                     "contact email is founder@yourco.example.com everywhere, never hello@ and never an "
                     "OtherVenture address (CLAUDE.md, Founder): " + ", ".join(sorted(_hits)[:8]))
    else:
        ok.append(f"contact email is founder@yourco.example.com on every surface ({len([f for f in _files if f])} files scanned)")
except Exception as e:
    drift.append(f"could not verify the contact-email rule: {e}")


# ── the HUMAN front door must list every folder too ──
# Added 2026-08-23. CLAUDE.md stayed current because an agent reads it every session and notices
# when it is wrong. 00_README.md — the page a PERSON opens first — went 71 days stale, missed nine
# folders including agents/ (268 files) and Pre Build Ideas/ (577), and still described clients/ as
# holding agent folders, which stopped being true on 2026-08-07. The machine layer self-heals; the
# human layer had no equivalent. This is the equivalent.
try:
    _readme = read(os.path.join(ROOT, "00_README.md"))
    _dirs2 = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"],
                            capture_output=True, text=True, timeout=60).stdout.split("\0")
    _tops2 = sorted({d.split("/")[0] for d in _dirs2 if "/" in d})
    _miss2 = [d for d in _tops2 if f"`{d}/`" not in _readme]
    if _miss2:
        drift.append("00_README.md — the human front door — is missing folder(s): " +
                     ", ".join(f"{d}/ ({len([x for x in _dirs2 if x.startswith(d + '/')])} files)"
                               for d in _miss2) +
                     ". Someone handed this folder cold would not know these exist.")
    else:
        ok.append(f"00_README.md lists all {len(_tops2)} top-level folders")
except Exception as e:
    drift.append(f"could not verify the 00_README folder table: {e}")


# ── 07_RULES.md must point at every place a rule actually lives ──
# Added 2026-08-23 with 07_RULES.md itself. The index is only useful while it is complete; a rule
# source that exists but is not indexed is exactly the orphan the index was written to prevent.
try:
    _rules = read(os.path.join(ROOT, "07_RULES.md"))
    _sources = ["CLAUDE.md", ".claude/skills/", "runtime/prompts/_loop-contract.md",
                "06_business-plan.md", "runtime/consistency-check.py",
                "decisions/", "learnings/", "rejections/"]
    _absent = [x for x in _sources if x not in _rules]
    if _absent:
        drift.append("07_RULES.md no longer indexes every rule source — missing: " + ", ".join(_absent) +
                     ". An unindexed rule source is a rule nobody new will find.")
    else:
        ok.append(f"07_RULES.md indexes all {len(_sources)} rule sources")
except Exception as e:
    drift.append(f"could not verify 07_RULES.md: {e}")


# ── a root doc that has gone quiet while the thing it describes moved ──
# Added 2026-08-23. Advisory by design: staleness is a smell, not proof. 05_operating_rhythm.md and
# 03_internal_platform.md had gone 71 and 47 days without a touch while HQ grew four new doors.
# Threshold tightened 60 -> 30 days on 2026-08-23 after measuring the actual gap distribution:
# 0, 4, 9, 12, 48 days. There is clean air between 12 and 48, so 30 catches the one genuinely
# stale doc and produces no false positives. Revisit if a normal working gap ever exceeds 30.
try:
    _watch = {"00_README.md": ".", "01_company.md": ".", "02_delivery_loop.md": "clients",
              "03_internal_platform.md": "runtime", "04_agent_roster.md": "agents",
              "05_operating_rhythm.md": "dashboard", "07_RULES.md": ".claude/skills"}
    _stale = []
    for _doc, _watched in _watch.items():
        _d = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%at", "--", _doc],
                            capture_output=True, text=True, timeout=30).stdout.strip()
        _w = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%at", "--", _watched],
                            capture_output=True, text=True, timeout=30).stdout.strip()
        if not _d or not _w:
            continue
        _age = (int(_w) - int(_d)) / 86400.0
        if _age > 30:
            _stale.append(f"{_doc} (untouched {int(_age)}d while {_watched}/ kept moving)")
    if _stale:
        drift.append("root doc(s) have gone quiet while what they describe changed: " +
                     "; ".join(_stale) + ". Re-read and refresh, or archive if superseded.")
    else:
        ok.append(f"all {len(_watch)} root docs are current against what they describe")
except Exception as e:
    drift.append(f"could not verify root-doc freshness: {e}")


# ── every live deal must appear in the pipeline mirror ──
# Added 2026-08-23. clients/_pipeline.md is a hand-maintained MIRROR of crm/data.json, refreshed by the
# pipeline-report loop. That loop last ran 2026-07-06; the mirror then drifted silently for 48 days and
# lost 13 of 23 deals, including Sample Realty and Prospect A — two Discovery-stage engagements with
# active client folders. Nothing noticed, because nothing was watching a file whose whole job is to agree
# with another file. Scope is deliberately narrow: pre-convo is the bench and the mirror may legitimately
# omit it, so only deals at discovery-or-later are required. Matching is by company name, loosely, because
# the mirror is prose — a false "present" is better than nagging about a formatting difference.
try:
    _crm = json.loads(read(os.path.join(ROOT, "crm/data.json")))
    _mirror = read(os.path.join(ROOT, "clients/_pipeline.md")).lower()
    _names = {c["id"]: (c.get("name") or "") for c in _crm.get("companies", [])}
    _bench = {"pre-convo", "bench", "parked", "lost"}
    _absent = []
    for _d in _crm.get("deals", []):
        if (_d.get("stage") or "").lower() in _bench:
            continue
        _n = _names.get(_d.get("companyId"), "").strip()
        if not _n:
            continue
        # Match loosely and on purpose. The mirror is prose written by a human/loop and uses
        # short display names ("Sample Realty"), while the CRM carries legal ones ("Sample Realty
        # Home & Land, LLC"). A strict compare produced a FALSE ALARM on 2026-08-23 — it reported
        # Sample Realty and Prospect A as missing when both were present on lines 26-27. Try
        # progressively looser keys and accept the first hit: a false "present" is far cheaper than
        # a check that cries wolf and gets ignored.
        _lo = _n.lower().strip()
        _cand = [_lo, re.split(r"[/(—,]|\s-\s", _lo)[0].strip()]
        _w = re.split(r"\s+", _cand[-1])
        if len(_w) >= 2:
            _cand.append(" ".join(_w[:2]))
        if _w:
            _cand.append(_w[0])
        if not any(len(_k) >= 3 and _k in _mirror for _k in _cand):
            _absent.append(f"{_n} [{_d.get('stage')}]")
    if _absent:
        drift.append("clients/_pipeline.md is missing live deal(s) the CRM holds: " +
                     "; ".join(_absent[:8]) +
                     ". The mirror is refreshed by the pipeline-report loop — if that loop is stale, "
                     "that is the actual fault. Never fix this by hand-editing the CRM to match.")
    else:
        _live = sum(1 for _d in _crm.get("deals", [])
                    if (_d.get("stage") or "").lower() not in _bench)
        ok.append(f"clients/_pipeline.md mirrors all {_live} live deal(s) in the CRM")
except Exception as e:
    drift.append(f"could not verify the pipeline mirror: {e}")


# ── the machine mirror of the site must not lag the site ──
# Added 2026-08-23. runtime/site_machine.py generates llms.txt + a machine/*.md mirror of the staged
# site, for assistants reading on a buyer's behalf. Its own docstring is the argument for this check:
# "a hand-maintained mirror would be wrong within a month, and a wrong mirror is worse than none
# because nobody proofreads it." Nothing schedules it — it is run by hand during site work, which has
# held so far (regenerated 2026-08-18 alongside the pages) but only because someone remembered. A timer
# would mostly no-op; what is actually needed is for the repo to notice when the mirror falls behind.
try:
    _sitedir = os.path.join(ROOT, "agents/webb/pages/yourco-site-v2")
    _machine = os.path.join(_sitedir, "machine")
    if not os.path.isdir(_machine):
        drift.append("the site's machine mirror is missing entirely — regenerate with "
                     "`python3 runtime/site_machine.py` (agents/webb/pages/yourco-site-v2/machine/)")
    else:
        def _newest(paths):
            best = ""
            for _p in paths:
                _r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%at", "--", _p],
                                    capture_output=True, text=True, timeout=30).stdout.strip()
                if _r and _r > best:
                    best = _r
            return int(best or 0)
        _pages = [os.path.relpath(os.path.join(_sitedir, f), ROOT)
                  for f in os.listdir(_sitedir) if f.endswith(".html")]
        _site_at = _newest(_pages)
        _mirror_at = _newest([os.path.relpath(_machine, ROOT)])
        _lag = (_site_at - _mirror_at) / 86400.0
        if _lag > 7:
            drift.append(f"the site changed {int(_lag)} days after its machine mirror was last "
                         "regenerated — assistants reading agents/webb/pages/yourco-site-v2/machine/ "
                         "are being served the old argument. Fix: python3 runtime/site_machine.py")
        else:
            ok.append(f"the site's machine mirror is current ({len(_pages)} pages, mirror within "
                      f"{max(0, int(_lag))}d of the newest page)")
except Exception as e:
    drift.append(f"could not verify the site machine mirror: {e}")


# ── every runtime doc must declare whether the thing it describes is actually running ──
# Added 2026-08-23. runtime/ held 16 docs with one-time setup runbooks from June sitting beside live
# reference, and no way to tell them apart: a reader could not know whether a page described something
# running, something already done, or something never deployed. telegram-control-setup.md already had
# the answer ("Status: BUILT, not deployed") — this makes that one line the rule. The label is not
# checked for truth, only for presence; an honest wrong label is a normal doc bug, an ABSENT one means
# nobody decided.
try:
    _rt = os.path.join(ROOT, "runtime")
    _nostatus = []
    for _f in sorted(os.listdir(_rt)):
        if not _f.endswith(".md"):
            continue
        if "Status:" not in read(os.path.join("runtime", _f))[:1200]:
            _nostatus.append(_f)
    if _nostatus:
        drift.append("runtime doc(s) with no `Status:` line in their opening: " + ", ".join(_nostatus) +
                     ". Say whether it is LIVE, SETUP DONE, BUILT-not-deployed, UNVERIFIED or DORMANT — "
                     "a reader cannot tell a June runbook from live reference otherwise.")
    else:
        _n = len([f for f in os.listdir(_rt) if f.endswith(".md")])
        ok.append(f"all {_n} runtime docs declare a Status")
except Exception as e:
    drift.append(f"could not verify runtime doc statuses: {e}")


# ── every loop prompt must name its owning agent ──
# Added 2026-08-23. 24 of 25 loop prompts did not say whose loop they were. The relationship existed
# only as prose in 04_agent_roster.md, and only 10 of 25 loops were named there by slug — so a loop
# fired every morning with nothing in it recording who was accountable for the output. Every prompt
# already opened with "You are David/Mario/Luka…", so the fact was present but not addressable; this
# makes it a field. Owner names are checked against the agents/ folder so a typo or a retired agent
# cannot sit unnoticed in a running loop. "unassigned" is legal and deliberate — demo-prep is staged
# with no owner anywhere, and recording that honestly beats inventing a plausible one.
try:
    _pd = os.path.join(ROOT, "runtime", "prompts")
    _known = {d.lower() for d in os.listdir(os.path.join(ROOT, "agents"))
              if os.path.isdir(os.path.join(ROOT, "agents", d))} | {"unassigned"}
    _no_owner, _bad_owner = [], []
    for _f in sorted(os.listdir(_pd)):
        if not _f.endswith(".md") or _f.startswith("_"):
            continue
        _m = re.search(r"\*\*Owner:\*\*\s*([A-Za-z-]+)", read(os.path.join("runtime", "prompts", _f)))
        if not _m:
            _no_owner.append(_f[:-3])
        elif _m.group(1).lower() not in _known:
            _bad_owner.append(f"{_f[:-3]} -> {_m.group(1)}")
    if _no_owner or _bad_owner:
        _msg = []
        if _no_owner:
            _msg.append("no `**Owner:**` line: " + ", ".join(_no_owner))
        if _bad_owner:
            _msg.append("owner is not an agent in agents/: " + ", ".join(_bad_owner))
        drift.append("loop prompt ownership — " + " | ".join(_msg) +
                     ". A loop that fires with no named owner has no one accountable for its output.")
    else:
        _n = len([f for f in os.listdir(_pd) if f.endswith(".md") and not f.startswith("_")])
        ok.append(f"all {_n} loop prompts name an owning agent that exists in agents/")
except Exception as e:
    drift.append(f"could not verify loop prompt ownership: {e}")


# ── loop SOPs and loop prompts must stay paired, or the exception must be declared ──
# Added 2026-08-23. A recurring loop normally has two files: processes/loops/<name>.md (the method) and
# runtime/prompts/<name>.md (what the runtime executes). Unpaired is sometimes CORRECT — a Mac-local
# scheduled task has no VPS prompt, an activation-gated loop has no prompt until a client goes live, and
# some prompts are deliberately self-contained. What is not correct is an unpaired file nobody decided
# about: reilly-outbound.md sat in the live loop folder for 16 days with "DEPRECATED" as its own first
# line. The allow-lists below ARE the decision record — adding to one should be a deliberate act.
# Emptied 2026-08-24: all four entries (deal-agent, evidence-sweep, melanie-briefing, outreach-eval)
# were written SOPs on 2026-08-23, so the exemption stopped describing anything. The check reported
# them as stale exceptions for a day and this is that report being acted on — an allow-list that
# outlives its reason is how a rule quietly stops covering things. The set stays rather than being
# deleted: the NEXT deliberately-unpaired prompt belongs here.
_PROMPT_NO_SOP = set()
_SOP_NO_PROMPT = {"client-error-sweep", "granola-crm-sync", "session-friction-audit"}
try:
    _sop = {f[:-3] for f in os.listdir(os.path.join(ROOT, "processes/loops"))
            if f.endswith(".md") and not f.startswith("_")}
    _pr = {f[:-3] for f in os.listdir(os.path.join(ROOT, "runtime/prompts"))
           if f.endswith(".md") and not f.startswith("_")}
    _msgs = []
    _new_p = sorted((_pr - _sop) - _PROMPT_NO_SOP)
    _new_s = sorted((_sop - _pr) - _SOP_NO_PROMPT)
    _stale_p = sorted(_PROMPT_NO_SOP - (_pr - _sop))
    _stale_s = sorted(_SOP_NO_PROMPT - (_sop - _pr))
    if _new_p:
        _msgs.append("prompt(s) with no SOP and no declared exception: " + ", ".join(_new_p))
    if _new_s:
        _msgs.append("SOP(s) with no prompt and no declared exception: " + ", ".join(_new_s))
    if _stale_p or _stale_s:
        _msgs.append("stale exception(s) — now paired, remove from the allow-list: " +
                     ", ".join(_stale_p + _stale_s))
    if _msgs:
        drift.append("loop SOP/prompt pairing — " + " | ".join(_msgs) +
                     " (allow-lists live in runtime/consistency-check.py; see processes/_README.md)")
    else:
        ok.append(f"loop SOP/prompt pairing intact ({len(_sop & _pr)} paired, "
                  f"{len(_PROMPT_NO_SOP) + len(_SOP_NO_PROMPT)} declared exceptions)")
except Exception as e:
    drift.append(f"could not verify loop SOP/prompt pairing: {e}")


# ── every timer's artifact directory must actually resolve ──
# Added 2026-08-23. HQ derives loop health from "is there a dated file in loops/<name>/", with a small
# ARTIFACT_DIR map for the loops that write somewhere else. crm-hygiene writes to loops/_crm-hygiene/
# (leading underscore, like the other machine-written stores) and was missing from that map — so a loop
# with 26 artifacts, newest from the previous day, was reported as "never ran". Half the alarms on the
# health panel were false, which is worse than an unmonitored loop: it teaches you to distrust the panel.
# A directory that resolves is not proof the loop is healthy; it is only proof the ALARM is meaningful.
try:
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import refresh as _refresh
    _sysd = os.path.join(ROOT, "runtime", "systemd")
    _exempt = set(_refresh.UNTRACKED) | set(_refresh.CLIENT_INFRA)
    _unresolved = []
    for _fn in sorted(os.listdir(_sysd)):
        if not _fn.endswith(".timer"):
            continue
        _key = _fn[len("yourco-"):-len(".timer")] if _fn.startswith("yourco-") else _fn[:-6]
        if _key in _exempt:
            continue
        _tgt = _refresh.ARTIFACT_DIR.get(_key, _key)
        _dir = os.path.join(ROOT, "loops", _tgt)
        if not os.path.isdir(_dir):
            # a same-named store with a leading underscore is the classic miss
            _alt = "_" + _key
            _hint = (f" (loops/{_alt}/ exists — add it to ARTIFACT_DIR)"
                     if os.path.isdir(os.path.join(ROOT, "loops", _alt)) else "")
            _unresolved.append(f"{_key} -> loops/{_tgt}/ missing{_hint}")
    if _unresolved:
        drift.append("timer(s) whose artifact directory does not exist, so HQ will score them "
                     "'never ran' regardless of what they did: " + "; ".join(_unresolved) +
                     ". Fix the map in dashboard/refresh.py (ARTIFACT_DIR / JSONL_STORE / UNTRACKED), "
                     "not the loop.")
    else:
        _n = len([f for f in os.listdir(_sysd) if f.endswith(".timer")])
        ok.append(f"all {_n} timers resolve to a real artifact store (or a declared exception)")
except Exception as e:
    drift.append(f"could not verify timer artifact directories: {e}")


# ── metered spend must be explained by the ledger ──
# Added 2026-08-23. finance/token_spend.md records where model spend went, and nothing ever
# compared it to what Anthropic actually billed — so 577 files could be built across a month and
# appear in the ledger zero times while the books looked fine. A ledger with a missing row is
# indistinguishable from a ledger with nothing to add, unless something checks.
# Compares API spend to API spend ONLY: Cowork sessions run on the Max subscription at $0 marginal
# and never reach the meter, so including them would manufacture a discrepancy out of nothing.
# Thresholds are generous because this is a prompt to go and log the work, not an accusation.
try:
    sys.path.insert(0, os.path.join(ROOT, "runtime"))
    import cost_reconcile as _cr
    _rec = _cr.reconcile()
    _silent = _cr.silent_months()
    _bad = []
    for _m in _rec["months"][:3]:                       # only recent months are actionable
        if _m["unexplained"] is not None and _m["unexplained"] > 15:
            _bad.append(f"{_m['month']}: ${_m['metered']:.2f} metered, "
                        f"${_m['attributedApi']:.2f} explained -> ${_m['unexplained']:.2f} unaccounted")
    for _s in _silent[:3]:
        _bad.append(f"{_s['month']}: {_s['commits']} commits and ZERO ledger rows")
    if _bad:
        drift.append("model spend is not fully explained by finance/token_spend.md — " +
                     "; ".join(_bad) + ". Log the work with the `log-internal-cost` skill "
                     "(or `log-build-cost` if it was for a client). Full report: "
                     "python3 runtime/cost_reconcile.py")
    else:
        ok.append("metered model spend is explained by the ledger (recent months reconcile)")
except Exception as e:
    drift.append(f"could not reconcile model spend: {e}")


# ── every agent README points at the roster and declares how it stays current ──
# Added 2026-08-23. The roster carries role/trigger/scope/gate/status for all 27 agents; the folder
# READMEs had been restating it badly — scope in 5 of 27, gates in 12, all partial copies of a table
# that already had the answer. Each README now opens with a pointer instead of a copy, plus a
# "Stays current" line, because measuring it found the real gap: agents learn HOW THEY RUN (learnings/,
# read at Step 0) but not WHAT THEY KNOW — domain currency is Brett's alone, and no loop has ever
# re-examined an agent's Lineage. A gap stated 27 times gets fixed; a gap stated nowhere does not.
try:
    _ad = os.path.join(ROOT, "agents")
    _no_spec, _no_cur, _no_lin = [], [], []
    for _a in sorted(os.listdir(_ad)):
        _p = os.path.join(_ad, _a, "_README.md")
        if not os.path.isdir(os.path.join(_ad, _a)) or not os.path.exists(_p):
            continue
        _t = read(os.path.join("agents", _a, "_README.md"))
        if "**Spec:**" not in _t:
            _no_spec.append(_a)
        if "**Stays current:**" not in _t:
            _no_cur.append(_a)
        if not re.search(r"[Ll]ineage", _t):
            _no_lin.append(_a)
    _msg = []
    if _no_spec:
        _msg.append("no roster pointer: " + ", ".join(_no_spec))
    if _no_cur:
        _msg.append("no `Stays current:` line: " + ", ".join(_no_cur))
    if _no_lin:
        _msg.append("no Lineage: " + ", ".join(_no_lin))
    if _msg:
        drift.append("agent README(s) incomplete — " + " | ".join(_msg) +
                     ". The shape is set in agents/_README.md: point at the roster, never copy it, "
                     "and say how this agent stays current (or that it does not).")
    else:
        _n = len([a for a in os.listdir(_ad) if os.path.isdir(os.path.join(_ad, a))])
        ok.append(f"all {_n} agent READMEs point at the roster and declare their currency")
except Exception as e:
    drift.append(f"could not verify agent READMEs: {e}")


# ── the brand spec must be read by the loops that need it, and its tokens must exist upstream ──
# Added 2026-08-23. brand/DESIGN.md §8 declares "Step 0 of any surface-building task: read this file"
# and NOTHING honoured it — not even brand-audit, Luka's own monthly loop, which read only the
# narrative guidelines. A surface could violate every component idiom in §4 and pass the brand audit.
# Second half: §8 also sets the order of truth as guidelines -> DESIGN.md -> site. #1C2240 had been
# living in DESIGN.md and in four shipped surfaces while the guidelines had never heard of it — a
# token that travelled UP. Both halves are cheap to check and were invisible for months.
_BRAND_READERS = {"brand-audit", "content"}   # deliberately small: over-wiring is noise, not safety
try:
    _missing = []
    for _slug in sorted(_BRAND_READERS):
        _pp = os.path.join(ROOT, "runtime", "prompts", _slug + ".md")
        if not os.path.exists(_pp):
            _missing.append(f"{_slug} (prompt missing)")
        elif "DESIGN.md" not in read(os.path.join("runtime", "prompts", _slug + ".md")):
            _missing.append(_slug)
    _dhex = set(re.findall(r"#[0-9a-fA-F]{6}", read("brand/DESIGN.md")))
    _ghex = set(re.findall(r"#[0-9a-fA-F]{6}", read("brand/v0/brand-guidelines.md")))
    _up = sorted({h.upper() for h in _dhex} - {h.upper() for h in _ghex})
    _msg = []
    if _missing:
        _msg.append("prompt(s) that build or review a visual surface do not read brand/DESIGN.md: "
                    + ", ".join(_missing))
    if _up:
        _msg.append("token(s) in DESIGN.md with no entry in brand/v0/brand-guidelines.md: "
                    + ", ".join(_up) + " — tokens travel guidelines -> spec -> site, never upward")
    if _msg:
        drift.append("brand system — " + " | ".join(_msg))
    else:
        ok.append(f"brand: {len(_BRAND_READERS)} surface loops read DESIGN.md; "
                  f"all {len(_dhex)} spec tokens exist upstream in the guidelines")
except Exception as e:
    drift.append(f"could not verify the brand system: {e}")


# ── engagement folders: the required minimum, and a stage that matches the CRM ──
# Added 2026-08-23. Measured across the three engagements, only TWO files existed in all of them —
# _README.md and cost.md. Three engagements had invented three shapes, with subfolders meaning the
# same thing under different names (attachments/assets, deliverables/listing-presentation).
#
# The stage half is the more important one. the Founder asked whether clients/ should be prospects/ with
# folders MOVING on signature. It should not — a path that encodes stage is a second copy of a fact
# the CRM already owns, and the path is the copy that goes stale. So the folder stays put and the
# stage is declared explicitly, then checked. Explicitly, because prose cannot be trusted here:
# prospect-a's README says "LIVE" about the PRODUCT while the engagement is at discovery, and a
# grep for stage words would have called that a contradiction. An explicit field, or nothing.
_REQUIRED = ("_README.md", "cost.md", "01_discovery.md")
try:
    _cd = os.path.join(ROOT, "clients")
    _crm2 = json.loads(read("crm/data.json"))
    _names = {c["id"]: (c.get("name") or "") for c in _crm2.get("companies", [])}
    _stage_by_company = {}
    for _d in _crm2.get("deals", []):
        _n = _names.get(_d.get("companyId"), "").strip().lower()
        if _n:
            _stage_by_company[_n] = (_d.get("stage") or "").lower()
    _problems = []
    for _f in sorted(os.listdir(_cd)):
        _dir = os.path.join(_cd, _f)
        if not os.path.isdir(_dir) or _f.startswith("_"):
            continue                       # _yourco-template and _fixture-* are not engagements
        _missing = [r for r in _REQUIRED if not os.path.exists(os.path.join(_dir, r))]
        if _missing:
            _problems.append(f"{_f}: missing {', '.join(_missing)}")
        _txt = read(os.path.join("clients", _f, "_README.md"))
        _m = re.search(r"\*\*Stage:\*\*\s*`([a-z-]+)`", _txt)
        if not _m:
            _problems.append(f"{_f}: no explicit `**Stage:**` line")
            continue
        _declared = _m.group(1).lower()
        _live = next((v for k, v in _stage_by_company.items()
                      if k.startswith(_f.replace("-", " ")[:12]) or _f.replace("-", " ")[:12] in k), None)
        if _live and _declared != _live:
            _problems.append(f"{_f}: README says `{_declared}`, the CRM says `{_live}` — the CRM wins")
    if _problems:
        drift.append("engagement folder(s) off-contract — " + "; ".join(_problems) +
                     ". The minimum and the folder names are in clients/_README.md; stage is owned "
                     "by crm/data.json and mirrored, never authored, in the folder.")
    else:
        _n = len([f for f in os.listdir(_cd)
                  if os.path.isdir(os.path.join(_cd, f)) and not f.startswith("_")])
        ok.append(f"all {_n} engagement folders carry the required files and a stage matching the CRM")
except Exception as e:
    drift.append(f"could not verify engagement folders: {e}")


# ── the monthly close must actually produce a readout, and runway must be fresh ──
# Added 2026-08-23. finance/readouts/ held 2026-06.md and nothing else — July and August never
# happened — and it went unnoticed for three months because two bugs hid each other: HQ had
# finance-close marked UNTRACKED (note: "audit 07-04: never wired on host", true when written and
# wrong once the timer landed), which excluded it from loop health entirely; and when that was
# corrected it still read "never ran", because loop health matched YYYY-MM-DD filenames while a
# readout is YYYY-MM. Both fixed. This check is the backstop that does not depend on either.
#
# runway.md is checked separately and matters more: for a pre-revenue company with $0 cash it is
# THE number, and it only refreshes when the close runs. A stale runway figure is worse than an
# absent one, because it reads as current.
try:
    _rd = os.path.join(ROOT, "finance", "readouts")
    _months = sorted(f[:7] for f in os.listdir(_rd) if re.match(r"^\d{4}-\d{2}", f))
    _today = datetime.date.today()
    _prev = (_today.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
    _issues = []
    if not _months:
        _issues.append("finance/readouts/ is empty — the monthly close has never produced a readout")
    elif _months[-1] < _prev:
        _issues.append(f"newest readout is {_months[-1]}, but {_prev} should exist — "
                       f"the close has not run for at least one full month")
    _rw = read("finance/runway.md")
    _m = re.search(r"as of (\d{4}-\d{2}-\d{2})", _rw)
    if not _m:
        _issues.append("finance/runway.md states no `as of <date>` — its numbers cannot be aged")
    else:
        _age = (_today - datetime.date.fromisoformat(_m.group(1))).days
        if _age > 45:
            _issues.append(f"finance/runway.md is {_age} days old (as of {_m.group(1)}) — "
                           "cash, MRR and burn are being read as current when they are not")
    if _issues:
        drift.append("finance close — " + "; ".join(_issues) +
                     ". The close is the ritual runway.md depends on: processes/loops/finance-close.md.")
    else:
        ok.append(f"the monthly close is current (newest readout {_months[-1]}, runway fresh)")
except Exception as e:
    drift.append(f"could not verify the finance close: {e}")


# ── the CRM's documented stage ladder must match the one in the data ──
# Added 2026-08-23. crm/_README.md described the ladder as prospect -> discovery -> proposal -> build
# -> live. The real ladder in data.json is pre-convo -> discovery -> demo-proposal -> signed-onboarding
# -> build-implementation -> testing -> live (+ parked): WRONG ON 5 OF 7, with two stages missing.
#
# This is not cosmetic and the precedent is already in the repo. When `bench` was renamed `pre-convo`
# in August, a stale BENCH_STAGES in crm/server.py made HQ report 21 deals and $24,000 against a real
# 3 — caught only because the prosecution panel argued with its own headline. A stage rename touches
# the data, the server, the README and the mirror; this check is the cheapest of those to keep honest.
try:
    _stages = json.loads(read("crm/data.json")).get("stages", [])
    _keys = [s.get("key") for s in _stages if isinstance(s, dict) and s.get("key")]
    # Blockquote lines are commentary, not the ladder — the README's own note explaining WHICH
    # stages were renamed necessarily names the retired ones, and flagging that would make the
    # check fire on its own fix. Same shape as the contact-email check exempting the doc that
    # describes the ban. The table itself is never a blockquote.
    _rd = "\n".join(l for l in read("crm/_README.md").splitlines() if not l.lstrip().startswith(">"))
    _absent = [k for k in _keys if f"`{k}`" not in _rd]
    # and the reverse: a stage the README invents that the data does not have
    _retired = ("prospect", "proposal", "build", "bench")
    _ghosts = [g for g in _retired if f"`{g}`" in _rd and g not in _keys]
    _msgs = []
    if _absent:
        _msgs.append("stage(s) in data.json but not documented in crm/_README.md: " + ", ".join(_absent))
    if _ghosts:
        _msgs.append("crm/_README.md still names retired stage(s): " + ", ".join(_ghosts))
    if _msgs:
        drift.append("CRM stage ladder — " + " | ".join(_msgs) +
                     ". data.json owns the ladder; the README is a reading of it. A rename has to "
                     "sweep the data, server.py, the README and the mirror together.")
    else:
        ok.append(f"CRM stage ladder documented correctly ({len(_keys)} stages match data.json)")
except Exception as e:
    drift.append(f"could not verify the CRM stage ladder: {e}")


# ── the numbered spine is reserved ──
# Added 2026-08-23 after `01 Daily Logs/` was renamed to `daily-logs/`. The root docs are numbered
# 00–05 for one reason: they sort to the top of the listing and declare a reading order. A FOLDER
# whose name starts with a digit lands inside that run and reads as part of the doctrine — that one
# duplicated `01` and sat between the front door and the company doc for months. Files 00–05 are the
# spine; nothing else at root may lead with a number. CLAUDE.md is deliberately unnumbered.
try:
    _spine = {"00_README.md", "01_company.md", "02_delivery_loop.md",
              "03_internal_platform.md", "04_agent_roster.md", "05_operating_rhythm.md",
              "06_business-plan.md", "07_RULES.md"}
    # 06 joined 2026-08-23: the plan holds the owner's rules and the core principles, so it IS
    # doctrine and belongs in the reading order. CLAUDE.md deliberately does NOT get a number —
    # the harness loads it by that exact filename, and a number would also mislabel a file that is
    # read first and automatically as the seventh thing a human reads.
    _missing = sorted(n for n in _spine if not os.path.exists(os.path.join(ROOT, n)))
    _squatters = sorted(n for n in os.listdir(ROOT)
                        if n[:1].isdigit() and n not in _spine and not n.startswith("."))
    _msgs = []
    if _missing:
        _msgs.append("spine doc(s) missing from root: " + ", ".join(_missing))
    if _squatters:
        _msgs.append("non-spine entr(y/ies) leading with a digit at root: " + ", ".join(_squatters))
    if _msgs:
        drift.append("numbered spine — " + " | ".join(_msgs) +
                     ". 00–05 are the reading order a human sees first; anything else starting with "
                     "a number wedges into it and reads as doctrine. Rename it (lowercase, no "
                     "leading digit) and sweep every reference in the same commit.")
    else:
        ok.append(f"numbered spine intact ({len(_spine)} docs 00-07 present, nothing else at root leads with a digit)")
except Exception as e:
    drift.append(f"could not verify the numbered spine: {e}")


# ── counted claims in the docs match what is actually there ──
# Added 2026-08-23. 07_RULES.md exists to stop drift and its own headline rule is change-one-sweep-all
# — yet it claimed 47 invariants (64), 17 skills (18), 25 loop prompts (26) and 207 assertions (216),
# and CLAUDE.md claimed 75 agentops assertions (88). Every one of those numbers is DERIVABLE, so a
# human should never be the thing that keeps them true. Each row below is (file, regex with one
# capture group, the real number, what it counts). This check runs LAST so it can count itself.
def _suite_total(script):
    """Assertions a test suite actually reports (passed + failed). Static grep is wrong — it counts
    calls inside branches that never execute (222 vs 219 for test_evidence), and the prose should
    match what a human sees when they run it. ~3s; None means the suite could not be run at all,
    which is reported as unverifiable rather than as drift."""
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, script)],
                             capture_output=True, text=True, timeout=120).stdout
        m = re.search(r"(\d+) passed, (\d+) failed", out)
        return int(m.group(1)) + int(m.group(2)) if m else None
    except Exception:
        return None

def _count_bullets(section_start, section_end):
    body = read(os.path.join(ROOT, "CLAUDE.md"))
    seg = body.split(section_start)[-1].split(section_end)[0] if section_start in body else ""
    return sum(1 for ln in seg.splitlines() if ln.startswith("- "))

try:
    _skills = len([d for d in glob.glob(os.path.join(ROOT, ".claude/skills/*/")) ])
    _prompts = len([f for f in glob.glob(os.path.join(ROOT, "runtime/prompts/*.md"))
                    if not os.path.basename(f).startswith("_")])
    # Count the CHECK BLOCKS in this file, not the result lines. len(ok)+len(drift) was wrong twice
    # over: it counts result lines (a single check can append several) and it can only see the
    # checks that ran BEFORE this one, so it silently undercounted by however many were appended
    # below. Section headers are structural, unambiguous, and stable no matter where this block sits.
    _invariants = len(re.findall(r"^# \u2500\u2500 ", read(os.path.join(ROOT, "runtime/consistency-check.py")), re.M)) - 1  # -1 = the report header
    _ev, _ag = _suite_total("runtime/test_evidence.py"), _suite_total("runtime/test_agentops.py")
    # The owner's rules are a numbered list in §1. Rule 17 was added 2026-08-10 and the count was
    # never swept: the plan's own prose said "sixteen" and CLAUDE.md said 16, for two weeks.
    # HQ's door count is derivable from the nav markup. It was wrong on all three surfaces at once
    # (README said nine and listed nine, two spine docs said ten, the markup had eleven), because
    # every one of them was prose a human had to remember to update when a tab was added.
    _doors = len(set(re.findall(r'<button class="nlink tab[^>]*data-v="([a-z-]+)"',
                                read(os.path.join(ROOT, "dashboard/index.html")))))
    _WORDNUM = {n: w for n, w in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
    _offerings = len([d for d in glob.glob(os.path.join(ROOT, "offerings", "*")) if os.path.isdir(d)])
    _specs = len([d for d in glob.glob(os.path.join(ROOT, "offerings", "*"))
                  if os.path.isfile(os.path.join(d, "SPEC.md"))])
    _prebuilds = len([d for d in glob.glob(os.path.join(ROOT, "Pre Build Ideas", "*"))
                      if os.path.isfile(os.path.join(d, "BUILD.md"))])
    _board = len(re.findall(r"^\| \d+ \|",
                            read(os.path.join(ROOT, "offerings/_frontier-roadmap.md")), re.M))
    _agents_n = len([d for d in glob.glob(os.path.join(ROOT, "agents", "*")) if os.path.isdir(d)])
    _skills_n = len([d for d in glob.glob(os.path.join(ROOT, ".claude/skills", "*")) if os.path.isdir(d)])
    _plan_s = read(os.path.join(ROOT, "06_business-plan.md"))
    _s1 = _plan_s.split("## 1 \u00b7 Owner")[-1].split("### The company")[0] if "## 1 \u00b7 Owner" in _plan_s else ""
    _rules = len(re.findall(r"^\d+\. \*\*", _s1, re.M))

    _claims = [
        ("07_RULES.md",  r"(\d+) working rules",                         _count_bullets("## How to work in this OS", "## External-surface"), "bullets in CLAUDE.md §How to work"),
        ("07_RULES.md",  r"(\d+) external-surface rules",                _count_bullets("## External-surface rules", "## Folder map"), "bullets in CLAUDE.md §External-surface"),
        # REMOVED 2026-08-24: this fact is now self-declaring in CLAUDE.md via
        # `<!--#count: suite runtime/test_evidence.py-->`, checked by runtime/doc_claims.py. Keeping
        # a second guard here meant the annotation's own edit broke this regex — one fact, one guard,
        # the same collision that took invariants 10 and 12 out earlier today.
        # REMOVED for the template: this looked for a sentence only the source
        # company's CLAUDE.md contained. A rewritten boot context cannot match it.
        # REMOVED for the template: this looked for a sentence only the source
        # company's CLAUDE.md contained. A rewritten boot context cannot match it.
        ("06_business-plan.md", r"\*\(The (\w+) above are the owner's rules",        _rules, "numbered rules in its own \u00a71"),
        ("offerings/_frontier-roadmap.md", r"\*\*(\d+) boarded offerings\*\*", _board, "numbered rows in the status board"),
        ("offerings/_README.md",   r"\*\*the Frontier Board\*\*, (\d+) never-been-done", _board, "numbered rows in the status board"),
        # START-HERE.html is the clickable front door. It was rewritten 2026-08-23 and FOUR of its
        # counts were wrong 24 hours later — broken by that same day's work (property-management
        # moved into Pre Build Ideas/, the Skills door was added to HQ). Hand-fixing a page that
        # drifts in a day just repeats the cycle, so every number on it is derived here.
    ]
    _bad, _unfindable, _unverifiable = [], [], []
    for _f, _rx, _actual, _what in _claims:
        if _actual is None:
            _unverifiable.append(f"{_f}: could not run the suite for {_what}"); continue
        _m = re.search(_rx, read(os.path.join(ROOT, _f)))
        if not _m:
            _unfindable.append(f"{_f}: no claim matching /{_rx}/"); continue
        _WORDS = {w: i for i, w in enumerate(
            "zero one two three four five six seven eight nine ten eleven twelve thirteen "
            "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
        _got = _m.group(1)
        _got = _WORDS.get(_got.lower()) if not _got.isdigit() else int(_got)
        if _got != _actual:
            _bad.append(f"{_f} says {_m.group(1)}, actual {_actual} ({_what})")
    if _bad or _unfindable:
        drift.append("counted claims — " + " | ".join(_bad + _unfindable) +
                     ". These numbers are derivable; fix the prose (or the regex here if the "
                     "sentence was deliberately reworded) rather than letting a human re-check them.")
    else:
        _tail = f" ({len(_unverifiable)} unverifiable this run)" if _unverifiable else ""
        ok.append(f"counted claims in the docs match reality ({len(_claims)} checked){_tail}")
except Exception as e:
    drift.append(f"could not verify the counted claims: {e}")


# 10 + 12 REMOVED 2026-08-24 — the offerings and Pre Build Ideas prose counts they guarded
# now carry their own `<!--#count: ...-->` annotations, verified by runtime/doc_claims.py.
# Two guards on one fact is the duplication this repo keeps getting bitten by: when the
# annotations were added, THESE regexes stopped matching and reported the docs as broken
# while the docs were correct. One fact, one guard.

# 11. a dated filename must match the commit that created it  (added 2026-08-24)
# Caught by eye twice in two weeks, then a third time while adding this check. c5e0785 corrected a
# whole day's work from 08-17 to 08-23; b87b0f1 corrected a learnings entry's date; and while writing
# THIS invariant the author "fixed" a wedding-os date that had been right all along, because a long
# session's sense of "today" had drifted from the calendar. The git add-commit date is the only ground
# truth about when a file was written — a session's belief about the date is not. Note the third case
# is the one that matters: the failure runs in BOTH directions, so a check that only caught stale dates
# would have blessed the bad correction.
#
# Scope is deliberately a 14-day window. The point is to catch drift while it is fresh and free to fix;
# an old entry whose filename date legitimately predates its commit (the `rejections/` anti-library was
# created 2026-08-13 and backfilled with historical calls, correctly named for when each call was made)
# is not actionable and must not be re-reported every Monday forever. The weekly watchdog cadence means
# every new file still gets checked at least once. A genuine backfill inside the window opts out with a
# `date-verified:` marker in the body.
try:
    # TEMPLATE GUARD: in a freshly cloned template every historical filename shares one
    # import commit, so this check can only ever fail. Skip until there is real history.
    # An imported repo has history NEWER than its filenames: everything arrived in one commit
    # long after the dates in the names. Commit COUNT is the wrong test — it passes as soon as
    # you make a few commits of your own, which is when this started firing again.
    _first = subprocess.run(["git","-C",ROOT,"log","--reverse","--format=%ad","--date=short"],
                            capture_output=True, text=True).stdout.split("\n")[0].strip()
    if _first and _first > "2026-08-01":   # history begins after the artifacts it contains
        ok.append("dated filenames — skipped (repo has no history yet)")
        raise _SkipCheck()

    _WINDOW, _TOL = 14, 2
    _today = datetime.date.today()
    _out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ad", "--date=short",
                           "--name-only", "--reverse"],
                          cwd=ROOT, capture_output=True, text=True).stdout
    _added, _cur = {}, None
    for _ln in _out.splitlines():
        _ln = _ln.strip()
        if not _ln:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", _ln):
            _cur = _ln
        elif _cur:
            _added.setdefault(_ln, _cur)
    _stale, _future, _checked, _exempt = [], [], 0, 0
    for _pat in ("decisions/*.md", "rejections/*.md", "learnings/*/*.md"):
        for _p in sorted(glob.glob(os.path.join(ROOT, _pat))):
            _rel = os.path.relpath(_p, ROOT)
            _m = re.match(r".*?(\d{4}-\d{2}-\d{2})", os.path.basename(_p))
            if not _m:
                continue
            _fd = datetime.date.fromisoformat(_m.group(1))
            # a filename dated in the future is always wrong, at any age
            if _fd > _today:
                _future.append(f"{_rel} is dated {_fd}, which is after today ({_today})")
                continue
            _a = _added.get(_rel)
            if not _a:
                continue                      # uncommitted, or renamed — nothing to compare against
            _ad = datetime.date.fromisoformat(_a)
            if (_today - _ad).days > _WINDOW:
                continue                      # outside the window: fresh-drift check only
            _checked += 1
            _gap = (_ad - _fd).days
            if abs(_gap) <= _TOL:
                continue
            if re.search(r"date-verified:", read(_p), re.I):
                _exempt += 1
                continue
            _stale.append(f"{_rel} is named {_fd} but was committed {_ad} ({_gap:+d}d)")
    if _future:
        drift.append("future-dated file(s): " + "; ".join(_future) +
                     ". A date later than today cannot be an authoring date.")
    if _stale:
        drift.append(f"dated filename(s) disagree with their add-commit by more than {_TOL}d: " +
                     "; ".join(_stale) +
                     ". The commit date is the ground truth — rename the file, or add a "
                     "`date-verified:` line if the date is a deliberate backfill.")
    if not _future and not _stale:
        ok.append(f"dated filenames match their add-commits ({_checked} file(s) inside the "
                  f"{_WINDOW}d window, {_exempt} exempt)")
except Exception as e:
    pass
except _SkipCheck:
    pass
except Exception as e:
    drift.append(f"could not verify dated filenames: {e}")


# ── every systemd ExecStart points at a script that exists ──
# Added 2026-08-23 when run-loop.sh moved to runtime/. A unit's ExecStart is an ABSOLUTE path baked
# into a root-owned copy in /etc/systemd/system — moving or renaming a script in the repo does not
# update it, and nothing fails until the timer next fires. With the runtime paused, that could be
# weeks. Two halves:
#   repo  — checked everywhere: the paths in runtime/systemd/*.service must resolve inside the repo.
#   host  — checked only ON the runtime box: the INSTALLED units are what actually run, and they are
#           a separate copy that a git pull does not touch. Off-host this reports nothing at all
#           rather than guessing, because the Mac has no /etc/systemd/system to read.
try:
    _units = glob.glob(os.path.join(ROOT, "runtime/systemd/*.service"))
    _bad, _n = [], 0
    # \S+ over-captures: several units wrap the command in /bin/bash -lc '...', so the path can
    # pick up a trailing quote or semicolon. Stop at the first shell metacharacter.
    _rx = re.compile(r"^ExecStart=.*?(/home/claudeops/yourco-os/([^\s'\";&|]+))", re.M)
    for _u in _units:
        for _abs, _relp in _rx.findall(read(_u)):
            _n += 1
            if not os.path.exists(os.path.join(ROOT, _relp)):
                _bad.append(f"{os.path.basename(_u)} -> {_relp} (missing)")
    _host = "/etc/systemd/system"
    _hostbad, _hostn = [], 0
    if os.path.isdir(_host) and os.path.isdir("/home/claudeops/yourco-os"):
        for _u in sorted(glob.glob(os.path.join(_host, "yourco-*.service"))):
            for _abs, _relp in _rx.findall(read(_u)):
                _hostn += 1
                if not os.path.exists(_abs):
                    _hostbad.append(f"INSTALLED {os.path.basename(_u)} -> {_abs} (missing on disk)")
    if _bad or _hostbad:
        drift.append("systemd ExecStart paths — " + " | ".join(_bad + _hostbad) +
                     ". A unit names an absolute path; moving the script in git does not move it. "
                     "Fix the repo unit AND re-install it on the runtime host, then daemon-reload.")
    else:
        _tail = f" + {_hostn} installed on this host" if _hostn else " (installed units not visible from here)"
        ok.append(f"systemd ExecStart paths all resolve ({_n} in repo units{_tail})")
except Exception as e:
    drift.append(f"could not verify systemd ExecStart paths: {e}")


# ── HQ's own input file is not allowed to go quietly stale ──
# Added 2026-08-23. dashboard/data.json is TWO files in one: `derived` is rewritten by
# dashboard/refresh.py, and the other ~39% is hand-maintained. On the day this was written the
# hand-written half was 60 days old and the derived half 34, and `Today` rendered both with no
# indication of either — while `The Board`, two tabs away, refuses to trust a stale source without
# saying so. HQ applies its freshness discipline to every input except its own.
#
# Thresholds are deliberately different: `derived` is machine-written on a cadence, so a week of
# silence means the writer stopped. The hand-written half moves when the company moves, so it gets
# 45 days. The first draft of this check used 90 and would have PASSED the very situation that
# prompted it: at 60 days the hand-written half was claiming 20 loops when there were 26, and
# listing a June launch date as current focus. A threshold that does not fire on the observed
# failure is decoration, so it is set from the evidence rather than from what feels polite.
try:
    _hq = json.load(open(os.path.join(ROOT, "dashboard/data.json"), encoding="utf-8"))
    _m = _hq.get("meta", {})
    _today = datetime.date.today()
    def _age(v):
        try: return (_today - datetime.date.fromisoformat(str(v)[:10])).days
        except Exception: return None
    _d_age, _h_age = _age(_m.get("derivedAt")), _age(_m.get("updated"))
    _msgs = []
    if _d_age is None:
        _msgs.append("meta.derivedAt is missing or unparseable — refresh.py stamps it every run")
    elif _d_age > 7:
        _msgs.append(f"derived block is {_d_age} days old (refresh.py has not run since "
                     f"{_m.get('derivedAt')}) — HQ is rendering computed numbers from then")
    if _h_age is None:
        _msgs.append("meta.updated is missing or unparseable")
    elif _h_age > 45:
        _msgs.append(f"hand-maintained half is {_h_age} days old (meta.updated {_m.get('updated')}) "
                     f"— company/metrics/focus on Today are frozen at that date")
    if _msgs:
        drift.append("HQ data.json freshness — " + " | ".join(_msgs) +
                     ". Run `python3 dashboard/refresh.py` for the derived half; edit "
                     "dashboard/data.json meta.updated when you refresh the hand-written half.")
    else:
        ok.append(f"HQ data.json is fresh (derived {_d_age}d, hand-maintained {_h_age}d)")
except Exception as e:
    drift.append(f"could not verify HQ data.json freshness: {e}")


# ── every decisions/ citation in the repo resolves to a real file ──
# Added 2026-08-24. 113 decisions are cited from code comments, SOPs, site copy and other
# decisions, and nothing checked that a citation points at anything. crm/connector_statements.py
# cited the connector-console-v3 decision under an 08-11 date when it was filed on 08-13 —
# right slug, wrong date, file never existed. (Described, not quoted: writing the dead path here
# verbatim made this very check fire on its own comment.) A dead citation is worse than none:
# it reads as provenance, so the next
# reader trusts a reason they cannot actually open. Dated record folders are scanned too — a
# citation was accurate when written only if the file was there, so a break is a break.
try:
    _cited, _rx = {}, re.compile(r"decisions/(20\d\d-\d\d-\d\d_[a-z0-9-]+\.md)")
    for _root, _dirs, _files in os.walk(ROOT):
        _dirs[:] = [d for d in _dirs if d not in {".git", "__pycache__", "node_modules"}]
        for _f in _files:
            if not _f.endswith((".md", ".py", ".sh", ".html", ".json", ".txt")):
                continue
            _fp = os.path.join(_root, _f)
            for _m in _rx.findall(read(_fp)):
                _cited.setdefault(_m, set()).add(os.path.relpath(_fp, ROOT))
    _dead = {c: v for c, v in _cited.items()
             if not os.path.exists(os.path.join(ROOT, "decisions", c))}
    if _dead:
        _lines = [f"{c} (cited by {', '.join(sorted(v)[:3])})" for c, v in sorted(_dead.items())]
        drift.append("dead decision citation(s) — " + " | ".join(_lines) +
                     ". Find the real file (usually the same slug on a different date) and fix the "
                     "citing line; never delete the citation, which loses the reason.")
    else:
        ok.append(f"every decisions/ citation resolves ({len(_cited)} distinct file(s) cited)")
except Exception as e:
    drift.append(f"could not verify decision citations: {e}")


# ── the learnings store stays retrievable ──
# Added 2026-08-24. learnings/ is the feed-forward half of the closed loop, and it has a good
# self-audit (`learning_triggers.py --check`) that NOTHING ran — so on the day this was written it
# was quietly reporting five unresolved links (all of which pointed at files that existed; the
# checker's own index was too strict) and one entry with "no triggers" that in fact had them,
# written bold, invisible to every run for five days. Both are fixed; this is what stops the next
# one sitting unread. Coverage is checked as a FLOOR, not an exact number — the store grows.
try:
    _lt = subprocess.run([sys.executable, os.path.join(ROOT, "runtime/learning_triggers.py"),
                          "--check", "--json"],
                         capture_output=True, text=True, timeout=60)
    _h = json.loads(_lt.stdout)
    _msgs = []
    if _h.get("links_unresolved"):
        _msgs.append("dead [[links]]: " + ", ".join(
            f"[[{u['link']}]] in {os.path.basename(u['in'])}" for u in _h["links_unresolved"][:4]))
    if _h.get("unreadable"):
        _msgs.append(f"{len(_h['unreadable'])} unreadable entr(y/ies)")
    # unknown_trigger_kinds is ADVISORY and stays out of drift. A trigger like `file://` has a colon
    # without a typed kind and is flagged by --check as "check it isn't a typo" — it isn't; it is the
    # literal thing that entry is about. Firing drift on a maybe is how a drift list gets ignored.
    _advisory = len(_h.get("unknown_trigger_kinds") or [])
    # A domain a prompt names but that does not exist retrieves NOTHING, silently. Two prompts
    # pointed at learnings/outbound/ and learnings/sales/ — neither ever existed.
    _named = set()
    for _p in glob.glob(os.path.join(ROOT, "runtime/prompts/*.md")):
        _named |= set(re.findall(r"learnings/([a-z_-]+)/", read(_p)))
    _ghost = sorted(d for d in _named
                    if not os.path.isdir(os.path.join(ROOT, "learnings", d)))
    if _ghost:
        _msgs.append("prompt(s) name a learnings domain that does not exist: "
                     + ", ".join(f"learnings/{d}/" for d in _ghost))
    if _h.get("coverage_pct", 0) < 90:
        _nt = _h.get("without_triggers") or []
        _nt = len(_nt) if isinstance(_nt, list) else _nt
        _msgs.append(f"trigger coverage {_h['coverage_pct']}% is below the 90% floor "
                     f"({_nt} entr(y/ies) reachable only by domain fallback)")
    if _msgs:
        drift.append("learnings store — " + " | ".join(_msgs) +
                     ". Run `python3 runtime/learning_triggers.py --check` for the full report.")
    else:
        _tail = f", {_advisory} advisory trigger note(s)" if _advisory else ""
        ok.append(f"learnings store retrievable ({_h['live']} live, {_h['coverage_pct']}% triggered, "
                  f"{_h['links_total']} links all resolving{_tail})")
except Exception as e:
    drift.append(f"could not verify the learnings store: {e}")


# ── an offerings/ entry that runs has crossed the line and should move ──
# Added 2026-08-24. `offerings/` means DESCRIBED-not-built; `Pre Build Ideas/` means built-not-sold,
# and its own README sets the test: "can you launch it from .claude/launch.json?" That line drifted
# quietly — property-os reached 81 files and ~8,460 lines of a running app while sitting in the
# folder whose README says nothing there runs, and two smaller prototypes did the same. It moved on
# 2026-08-24; this is what makes the NEXT crossing announce itself instead of waiting to be noticed
# during a folder review. Reported, never auto-moved: whether a prototype has outgrown its spec is a
# judgement, and the two remaining crossings are deliberate and named in offerings/_README.md.
_CROSSED_OK = {"trust-ledger", "autonomy-standard"}   # named in offerings/_README.md; move when next touched
try:
    _cfgs = json.load(open(os.path.join(ROOT, ".claude/launch.json"), encoding="utf-8"))["configurations"]
    _runs = set()
    for _c in _cfgs:
        for _a in _c.get("runtimeArgs") or []:
            _m = re.match(r"offerings/([^/]+)/", str(_a))
            if _m:
                _runs.add(_m.group(1))
    _new = sorted(_runs - _CROSSED_OK)
    _gone = sorted(d for d in _CROSSED_OK
                   if not os.path.isdir(os.path.join(ROOT, "offerings", d)))
    _msgs = []
    if _new:
        _msgs.append("offerings entr(y/ies) now serving from launch.json: " + ", ".join(_new) +
                     " — a spec that runs belongs in Pre Build Ideas/")
    if _gone:
        _msgs.append("allow-listed crossing(s) no longer in offerings/: " + ", ".join(_gone) +
                     " — they moved; drop them from _CROSSED_OK here")
    if _msgs:
        drift.append("offerings/ crossings — " + " | ".join(_msgs) +
                     ". The line and the two accepted exceptions are in offerings/_README.md.")
    else:
        ok.append(f"offerings/ line holds ({len(_runs)} runnable, all {len(_CROSSED_OK)} accepted "
                  f"and named in _README)")
except Exception as e:
    drift.append(f"could not verify offerings/ crossings: {e}")


# ── the playground cannot write to live ──
# Added 2026-08-24. `playground/check_isolation.py` is the best-scarred check in this repo: it
# exists because on 2026-08-07 the seeder wrote synthetic connectors into the REAL crm/data.json —
# reads came from the sandbox, writes went to production, which is strictly worse than no sandbox.
# ELEVEN modules across crm/ and dashboard/ carry the comment "Enforced by
# playground/check_isolation.py", and until today nothing ran it: no suite, no timer, no watchdog.
# A developer reading crm/connector_writes.py saw a guarantee that was a script someone had to
# remember to type. It costs 0.3s and is read-only (its seed writes only into gitignored
# playground/data/), so there is no reason for it not to run every Monday.
try:
    _iso = subprocess.run([sys.executable, os.path.join(ROOT, "playground/check_isolation.py")],
                          capture_output=True, text=True, timeout=120, cwd=ROOT)
    _claims = len([f for f in glob.glob(os.path.join(ROOT, "crm", "*.py"))
                   + glob.glob(os.path.join(ROOT, "dashboard", "*.py"))
                   if "Enforced by playground/check_isolation.py" in read(f)])
    if _iso.returncode != 0:
        _why = " ".join((_iso.stdout + " " + _iso.stderr).split())[:400] or "no output"
        drift.append(f"playground isolation FAILED — {_why}. {_claims} module(s) carry an 'Enforced "
                     f"by playground/check_isolation.py' comment; a failure here means the sandbox "
                     f"can reach live data. Run `python3 playground/check_isolation.py`.")
    else:
        ok.append(f"playground cannot write to live ({_claims} modules assert this check enforces "
                  f"them, and it now runs)")
except Exception as e:
    drift.append(f"could not run the playground isolation check: {e}")


# ── the pre-build index describes the pre-builds ──
# Added 2026-08-24. 76 industry builds, ~1,250 files, and a hand-maintained index table in
# `Pre Build Ideas/_README.md` carrying a row per build with its launch name, port and assertion
# count. Moving property-management in from offerings/ the same morning left the table at 75 rows,
# the headline at 5,371 assertions (actual 5,856) and the counter-argument saying "seventy-five
# demos" — three stale numbers from one move, none of which any check would have caught. This is
# structure only: every build has a row, every row's launch name is real, and no port is claimed
# twice. Assertion counts are NOT checked — running 77 suites to verify a doc is the wrong trade.
try:
    _pb = os.path.join(ROOT, "Pre Build Ideas")
    _dirs = {os.path.basename(d) for d in glob.glob(os.path.join(_pb, "*"))
             if os.path.isdir(d) and os.path.basename(d) != "_kit"}
    _idx = read(os.path.join(_pb, "_README.md"))
    _rows = re.findall(r"^\| \d+ \| `([^`/]+)/?` \| [^|]*\| `([^`]+)` \u00b7 (\d+)", _idx, re.M)
    _tabled = {r[0] for r in _rows}
    _names = {c["name"]: c for c in json.load(
        open(os.path.join(ROOT, ".claude/launch.json"), encoding="utf-8"))["configurations"]}
    _msgs = []
    _absent = sorted(_dirs - _tabled)
    _ghost = sorted(_tabled - _dirs)
    if _absent:
        _msgs.append(f"build(s) with no row in the index: {', '.join(_absent)}")
    if _ghost:
        _msgs.append(f"index row(s) naming no build folder: {', '.join(_ghost)}")
    _badname = [f"{d} -> {ln}" for d, ln, _pt in _rows if ln not in _names]
    if _badname:
        _msgs.append("row(s) naming a launch entry that does not exist: " + ", ".join(_badname[:4]))
    _badport = [f"{d} says {pt}, launch.json says {_names[ln]['port']}"
                for d, ln, pt in _rows if ln in _names and int(pt) != _names[ln]["port"]]
    if _badport:
        _msgs.append("row(s) with the wrong port: " + ", ".join(_badport[:4]))
    if _msgs:
        drift.append("Pre Build Ideas index — " + " | ".join(_msgs) +
                     ". The table in Pre Build Ideas/_README.md is the index to 76 builds; a build "
                     "missing from it is a build nobody can find.")
    else:
        ok.append(f"pre-build index complete ({len(_dirs)} builds, all tabled, launch names and "
                  f"ports match)")
except Exception as e:
    drift.append(f"could not verify the pre-build index: {e}")


# ── the OS ladder is quoted identically wherever it is quoted ──
# Added 2026-08-24. pricing/v0/os-tiers.md is the source; pricing/README.md and 06_business-plan.md
# \u00a74 each restate the four tiers so a reader can orient without opening three files. That is a
# COPIED FACT — the single most common failure in this repo — and the README's rewrite on 2026-08-24
# hand-typed the table, so it needs a machine behind it rather than care. §8 of the plan is already
# checked against the financial model separately; this checks the ladder itself.
try:
    _NUM = r"\$([\d,]+\u2013[\d,]+)"
    def _ladder(_path):
        _txt = read(os.path.join(ROOT, _path))
        _out = {}
        for _t in ("Core", "Suite", "Operation", "Command"):
            _row = re.search(rf"^\|\s*\*\*{_t}\*\*\s*\|.*$", _txt, re.M)
            if not _row:
                continue
            _n = [x.replace(",", "") for x in re.findall(_NUM, _row.group(0))]
            if len(_n) >= 2:
                _out[_t] = tuple(_n[-2:])
        return _out
    _src = _ladder("pricing/v0/os-tiers.md")
    _bad, _thin = [], []
    if len(_src) != 4:
        _thin.append(f"pricing/v0/os-tiers.md parsed only {len(_src)}/4 tiers — the source row format changed")
    for _f in ("pricing/README.md",):
        _c = _ladder(_f)
        if not _c:
            _thin.append(f"{_f} restates no tier rows (fine if it stopped copying them — drop it here)")
            continue
        for _t, _v in _c.items():
            if _t in _src and _v != _src[_t]:
                _bad.append(f"{_f} {_t} {_v[0]}/{_v[1]} vs os-tiers {_src[_t][0]}/{_src[_t][1]}")
    if _bad:
        drift.append("OS ladder quoted inconsistently — " + " | ".join(_bad) +
                     ". pricing/v0/os-tiers.md is the source; fix the copy, not the source.")
    elif _thin:
        drift.append("OS ladder check degraded — " + " | ".join(_thin))
    else:
        ok.append(f"OS ladder consistent ({len(_src)} tiers, matching everywhere it is restated)")
except Exception as e:
    drift.append(f"could not verify the OS ladder: {e}")


# ── processes/_README counts describe processes/ ──
# Added 2026-08-24. That page is a structural map rather than a file index — the right shape for 170+
# files — which makes its per-folder counts the only thing it actually asserts. They were hand-typed
# when it was rewritten on 2026-08-23 and were wrong four days later: 134 files had become 171 and
# partnerships/ had DOUBLED from 33 to 66. Dotfiles are excluded on purpose (.DS_Store is gitignored
# and would make the count drift with whichever machine last opened Finder).
try:
    def _nfiles(_rel):
        _base = os.path.join(ROOT, _rel)
        return sum(1 for _r, _d, _f in os.walk(_base)
                   for _x in _f if not _x.startswith("."))
    _pr = read(os.path.join(ROOT, "processes/_README.md"))
    _want = {
        "total":        (_nfiles("processes"),      r"\*\*(\d+) files\*\*"),
        "loops/":       (_nfiles("processes/loops"), r"\| `loops/` \| (\d+) \|"),
        "partnerships/": (_nfiles("processes/partnerships"), r"\| `partnerships/` \| (\d+) \|"),
        "outbound/":    (_nfiles("processes/outbound"), r"\| `outbound/` \| (\d+) \|"),
        "contracts/":   (_nfiles("processes/contracts"), r"\| `contracts/` \| (\d+) \|"),
        "root":         (len([f for f in os.listdir(os.path.join(ROOT, "processes"))
                              if f.endswith(".md")]), r"\| \*\(root\)\* \| (\d+) \|"),
    }
    _bad, _nf = [], []
    for _label, (_actual, _rx) in _want.items():
        _m = re.search(_rx, _pr)
        if not _m:
            _nf.append(_label); continue
        if int(_m.group(1)) != _actual:
            _bad.append(f"{_label} says {_m.group(1)}, actual {_actual}")
    if _bad or _nf:
        _msg = " | ".join(_bad + ([f"no count found for {', '.join(_nf)}"] if _nf else []))
        drift.append("processes/_README counts — " + _msg +
                     ". That page's counts are the only claim it makes; refresh them or fix the "
                     "regex here if a row was deliberately reworded.")
    else:
        ok.append(f"processes/_README counts match ({_want['total'][0]} files across 6 folders)")
except Exception as e:
    drift.append(f"could not verify processes/_README counts: {e}")


# ── the master launch gate reports its own age honestly ──
# Added 2026-08-24. processes/launch-gate.md is, by CLAUDE.md, the ONLY place gate state lives —
# and it is the thing blocking every external surface yourco has built. On the day this was written
# four of its six fields still read "the Founder to fill", its update log held one entry (2026-07-05,
# "no recorded update since"), and its Expected-timeline row said "now 3+ weeks past that estimate"
# when the estimate was 2026-06-12 — 73 days, about ten weeks. A tracker that under-reports its own
# staleness by 3x is worse than an empty one, because it reads as maintained.
#
# This does NOT judge whether the gate should be cleared — that is the Founder's, and no check can know it.
# It only refuses to let the page's own arithmetic go quietly wrong.
try:
    _g = read(os.path.join(ROOT, "processes/launch-gate.md"))
    _today = datetime.date.today()
    _msgs = []
    # Counts BOTH markers. The 2026-08-25 rewrite replaced "*the Founder to fill" with a louder
    # "UNRECORDED — the Founder only", and in doing so made this counter read 0 while two fields were
    # still genuinely blank — a checker blinded by a reword of the thing it watches, which is the
    # exact failure class the rest of this file exists to catch. Match on either.
    _fills = (len(re.findall(r"\*the Founder to fill", _g))
              + len(re.findall(r"UNRECORDED\s*[\u2014-]\s*the Founder only", _g)))
    _log = sorted(re.findall(r"^- (\d{4}-\d{2}-\d{2}) \u2014", _g, re.M), reverse=True)
    if _log:
        _age = (_today - datetime.date.fromisoformat(_log[0])).days
        if _age > 30:
            _msgs.append(f"no update logged for {_age} days (newest entry {_log[0]})")
    else:
        _msgs.append("the update log has no dated entries")
    # the page states an estimate date and a weeks-past claim; make the claim keep up with the calendar
    _est = re.search(r"as of (\d{4}-\d{2}-\d{2})", _g)
    _claim = re.search(r"now (\d+)\+? weeks past", _g)
    if _est and _claim:
        _real = (_today - datetime.date.fromisoformat(_est.group(1))).days // 7
        if _real > int(_claim.group(1)) + 1:
            _msgs.append(f"it says '{_claim.group(1)}+ weeks past' the {_est.group(1)} estimate; "
                         f"the calendar says {_real}")
    if _msgs:
        drift.append(f"launch-gate tracker — " + " | ".join(_msgs) +
                     (f" | {_fills} field(s) still unrecorded" if _fills else "") +
                     ". It is the only record of the gate blocking every external surface; "
                     "an unmaintained tracker reads as a maintained one.")
    elif _fills:
        # A fresh log with a blank resolution condition still means nobody but the Founder can ever
        # declare the gate cleared. That is worth saying every week, not just when the log rots.
        drift.append(f"launch-gate tracker — log is fresh, but {_fills} field(s) are still "
                     f"unrecorded (what the gate IS, and what would clear it). Until the "
                     f"resolution condition exists, 'cleared' is not a testable state and the "
                     f"external half of the company depends on one person remembering to say so.")
    else:
        ok.append("launch-gate tracker current (every field recorded, log fresh)")
except Exception as e:
    drift.append(f"could not verify the launch-gate tracker: {e}")


# ── the anti-library stays checkable ──
# Added 2026-08-24. rejections/ is small and healthy, and this is what keeps it that way. Two things
# it asserts about itself: every entry names the condition that would reopen it (rejections.py calls
# a missing one `unconditional` — "a permanent veto with no stated reopening condition is a red
# flag, not a clean file"), and a check that cannot be evaluated is an `error`, never a quiet
# "did not fire". Reopened entries are NOT drift here — they now land on The Board as needs-you
# (dashboard/board.py rejection_items), which is where a human decision belongs.
try:
    import importlib.util as _ilu
    _rj_path = os.path.join(ROOT, "runtime", "rejections.py")
    _spec = _ilu.spec_from_file_location("_rej_check", _rj_path)
    _rj = _ilu.module_from_spec(_spec)
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    _spec.loader.exec_module(_rj)
    _st = _rj.status_all()
    _c = _st.get("counts", {})
    _msgs = []
    if _c.get("unconditional"):
        _bad = [r["file"] for r in _st["rejections"] if r.get("verdict") == "unconditional"]
        _msgs.append(f"{_c['unconditional']} rejection(s) with NO reopen condition: "
                     + ", ".join(_bad[:4]))
    if _c.get("error"):
        _bad = [r["file"] for r in _st["rejections"] if r.get("verdict") == "error"]
        _msgs.append(f"{_c['error']} rejection check(s) could not be evaluated: " + ", ".join(_bad[:4]))
    if _st.get("unreadable"):
        _msgs.append(f"{len(_st['unreadable'])} unreadable entr(y/ies)")
    if _st.get("facts_error"):
        _msgs.append(f"the shared fact map failed to build: {_st['facts_error']}")
    if _msgs:
        drift.append("anti-library — " + " | ".join(_msgs) +
                     ". Every rejection must name what would reopen it; run "
                     "`python3 runtime/rejections.py --list`.")
    else:
        _re = _c.get("reopened", 0) + _c.get("due", 0)
        _tail = f", {_re} reopened (on The Board)" if _re else ""
        ok.append(f"anti-library checkable ({_c.get('standing', 0)} standing, all with reopen "
                  f"conditions{_tail})")
except Exception as e:
    drift.append(f"could not verify the anti-library: {e}")


# ── sendable material cannot silently outlive the positioning it describes ──
# Added 2026-08-24. send-package/ is the one folder built to LEAVE the building — a self-contained
# bundle to AirDrop or email someone. It sat untouched for 72 days while the company changed
# underneath it: it led with a single AI employee as "what we sell" (now the entry rung, offered
# LAST), never mentioned the Audit (the mandatory front door since 2026-06-16), and its embedded
# CRM screenshot showed internal agent names and a retired $750/mo price — breaking two of the six
# external-surface rules in CLAUDE.md.
#
# The check is deliberately AGE-RELATIVE, not absolute: sendable material is stale when the things
# it describes have moved since it was written, which is what "older than its sources" means. While
# it carries a DO-NOT-SEND marker this passes — a marked-superseded asset is handled, not rotten.
try:
    _sp = os.path.join(ROOT, "send-package")
    _SOURCES = ["CLAUDE.md", "01_company.md", "pricing/v0/os-tiers.md"]
    def _gitdate(_rel):
        try:
            _o = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%at", "--", _rel],
                                capture_output=True, text=True, timeout=30).stdout.strip()
            return int(_o) if _o else None
        except Exception:
            return None
    _assets = [os.path.relpath(os.path.join(_r, _f), ROOT)
               for _r, _d, _fs in os.walk(_sp) for _f in _fs if not _f.startswith(".")]
    _marked = [a for a in _assets
               if a.endswith((".html", ".txt", ".md")) and "DO NOT SEND" in read(os.path.join(ROOT, a)).upper()]
    _newest_src = max((_gitdate(x) or 0) for x in _SOURCES)
    _oldest_asset = min((_gitdate(a) or 0) for a in _assets) if _assets else 0
    _lag = (_newest_src - _oldest_asset) // 86400 if _oldest_asset else 0
    if _marked:
        ok.append(f"send-package handled ({len(_marked)} of {len(_assets)} file(s) carry a "
                  f"DO-NOT-SEND marker; content lags its sources by {_lag}d)")
    elif _lag > 30:
        drift.append(f"send-package is {_lag} days behind its own sources (CLAUDE.md / 01_company.md "
                     f"/ pricing) and carries NO do-not-send marker. It is the one folder built to be "
                     f"emailed to someone — rebuild it, or mark it superseded. Check any screenshot "
                     f"against the six external-surface rules before embedding it.")
    else:
        ok.append(f"send-package current (within {_lag}d of its sources)")
except Exception as e:
    drift.append(f"could not verify send-package freshness: {e}")


# ── show.sh's header counts the servers it actually starts ──
# Added 2026-08-24. The header said "bring up the cockpits (website + HQ + CRM) … all three servers
# and open the website" — true until the app gateway shipped on 08-23, after which it starts FIVE
# and opens the gateway, not the site. The body was updated; the comment a human reads first was
# not. This is a two-line check on a two-line claim, and it is here because that comment is the
# only documentation `./show.sh` has.
try:
    _sh = read(os.path.join(ROOT, "show.sh"))
    _entries = len(re.findall(r'^\s+"yourco-[a-z-]+:', _sh, re.M))
    _WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
    _m = re.search(r"all (\w+) servers", _sh, re.I)
    _msgs = []
    if not _m:
        _msgs.append("the header no longer states how many servers it starts")
    else:
        _said = _WORDS.get(_m.group(1).lower()) if not _m.group(1).isdigit() else int(_m.group(1))
        if _said != _entries:
            _msgs.append(f"header says '{_m.group(1)}' servers, the COCKPITS array has {_entries}")
    if not _entries:
        _msgs.append("the COCKPITS array could not be parsed — the check cannot see the real count")
    if _msgs:
        drift.append("show.sh header — " + " | ".join(_msgs) +
                     ". That comment is the only documentation ./show.sh has.")
    else:
        ok.append(f"show.sh header matches what it starts ({_entries} servers)")
except Exception as e:
    drift.append(f"could not verify the show.sh header: {e}")


# ── the AI-OS formula says the same thing on every surface it appears ──
# Added 2026-08-24, the day the formula shipped. It is the answer to "what is an AI OS?" — the most
# repeated question on every call — and it now exists in TWO places: the site's #what section and
# Pickle's battlecard. That is the exact duplicated-fact shape that has drifted before (commission
# %s, tier names, cadences), and a formula that reads differently on the site than in the Founder's hand on
# a call is worse than having no formula. The six terms are the fact; order matters because it is
# recited aloud.
try:
    _TERMS = ["answering service", "CRM", "email marketing", "scheduler", "bookkeeper", "SOP binder"]
    _site = read(os.path.join(ROOT, "agents/webb/pages/yourco-site-v2/index.html"))
    _card = read(os.path.join(ROOT, "agents/pickle/collateral/battlecard.md"))
    _msgs = []
    _sm = re.search(r'<section class="tile" id="what">(.*?)</section>', _site, re.S)
    if not _sm:
        _msgs.append("the site's #what section is gone — the site no longer answers the question")
    else:
        _got = re.findall(r'<div class="term">your ([^<]+)</div>', _sm.group(1))
        if _got != _TERMS:
            _msgs.append(f"site terms are {_got}, expected {_TERMS}")
    _cm = re.search(r"^## The one-liner(.*?)^## ", _card, re.S | re.M)
    if not _cm:
        _msgs.append("the battlecard has no '## The one-liner' section")
    else:
        _body = _cm.group(1)
        _missing = [t for t in _TERMS if t.lower() not in _body.lower()]
        if _missing:
            _msgs.append(f"battlecard one-liner is missing term(s): {_missing}")
        if "they do the work" not in _body:
            _msgs.append("the battlecard dropped the 'they do the work' clause — the formula's punch")
        if "moat" not in _body.lower():
            _msgs.append("the battlecard lost the 'formula opens, moat closes' warning, which is the "
                         "guard against reciting a line a no-code operator could also recite")
    if _msgs:
        drift.append("AI-OS formula — " + " | ".join(_msgs) +
                     ". the Founder adopted this wording 2026-08-24; see decisions/2026-07-05_tool-triage.md.")
    else:
        ok.append(f"AI-OS formula consistent ({len(_TERMS)} terms, site + battlecard, punch and moat-guard intact)")
except Exception as e:
    drift.append(f"could not verify the AI-OS formula: {e}")


# ── the Audit's control map survives end to end ──
# Added 2026-08-24, the day it shipped. It spans FOUR surfaces — the SOP's questions, the SOP's mapping
# to rungs, the report template's config, and the render that deletes the section when unanswered. The
# fragile one is the LAST: a governance section that silently falls back to the template's sample
# answers would put words in a client's mouth about what they agreed an agent may do. That is the one
# failure here with a real-world cost, so it is checked as a property, not as prose.
try:
    _sop = read(os.path.join(ROOT, "processes/audit-sop.md"))
    _rep = read(os.path.join(ROOT, "clients/_yourco-template/audit-report/index.html"))
    _msgs = []
    if "**E. The control map**" not in _sop:
        _msgs.append("SOP Step 2 lost Block E — the Audit no longer asks what the client will allow")
    else:
        _qs = re.search(r"\*\*E\. The control map\*\*(.*?)^## ", _sop, re.S | re.M)
        _n = len(re.findall(r"^\d+\. ", _qs.group(1), re.M)) if _qs else 0
        if _n < 8:
            _msgs.append(f"Block E is down to {_n} questions (was 8) — check what was dropped")
    if "## Step 4b" not in _sop:
        _msgs.append("SOP lost Step 4b — Block E's answers no longer map to rungs, so it is a "
                     "questionnaire that goes nowhere")
    elif "promotion criterion" not in _sop:
        _msgs.append("Step 4b no longer names Q21 as the promotion criterion, which is the answer "
                     "that converts 'trust us' into a condition the client set")
    # The question guide exists TWICE by design: processes/audit-sop.md is the shared SOP and
    # agents/bella/02_build.md is Bella's runbook, which deliberately carries proposed deltas. Deltas
    # are fine; a whole BLOCK present in one and missing from the other is not — that is how Block E
    # spent an hour existing only in the SOP on the day it was written. Compare block letters only,
    # so intentional wording differences stay allowed.
    _bella = read(os.path.join(ROOT, "agents/bella/02_build.md"))
    _blocks = lambda t: sorted(set(re.findall(r"\*\*([A-Z])\. [A-Z][a-z]", t)))
    _sb, _bb = _blocks(_sop), _blocks(_bella)
    if _sb != _bb:
        _msgs.append(f"the question guide has diverged — SOP has blocks {_sb}, Bella's runbook has "
                     f"{_bb}; a block in one and not the other means the call and the SOP disagree")
    if "governance:" not in _rep:
        _msgs.append("the audit-report template lost its governance config")
    # the honesty property: the render must remove the section when there is no config
    _has_guard = re.search(r"if\(!g \|\| !g\.rows \|\| !g\.rows\.length\)", _rep) and ".remove()" in _rep
    if not _has_guard:
        _msgs.append("the report no longer DELETES the control map when the client did not answer "
                     "Block E — an unanswered section would render the template's sample answers as "
                     "if the client had agreed to them")
    if _msgs:
        drift.append("Audit control map — " + " | ".join(_msgs) +
                     ". Built 2026-08-24; see agents/bella/01_discovery.md.")
    else:
        ok.append("Audit control map intact (Block E asked, Step 4b maps it to rungs, report renders "
                  "it and deletes it when unanswered)")
except Exception as e:
    drift.append(f"could not verify the Audit control map: {e}")


# ── the inbox has not become a graveyard with a nicer name ──
# Added 2026-08-24 with inbox/ itself. The whole point of an inbox is that capture stops requiring a
# routing decision — which works right up until nothing is ever routed, at which point it is strictly
# worse than no inbox, because things now LOOK captured. 14 days is not a nag threshold: an item that
# will not route in two weeks is usually a thing that needs a DECISION rather than a folder, and that
# is worth surfacing. The triage itself (runtime/inbox_triage.py) proposes and never files, so nothing
# here can be resolved by the machine — only reported.
try:
    _ib = os.path.join(ROOT, "inbox")
    if not os.path.isdir(_ib):
        drift.append("inbox/ is gone — capture again requires choosing among 20 destinations up front "
                     "(see inbox/_README.md for why that suppressed capture)")
    else:
        import time as _t
        _now = _t.time()
        _items = [f for f in os.listdir(_ib) if not f.startswith(".") and f != "_README.md"
                  and os.path.isfile(os.path.join(_ib, f))]
        _stale = [(f, int((_now - os.stat(os.path.join(_ib, f)).st_mtime) // 86400)) for f in _items]
        _stale = sorted([x for x in _stale if x[1] >= 14], key=lambda x: -x[1])
        if _stale:
            _names = ", ".join(f"{f} ({d}d)" for f, d in _stale[:4])
            drift.append(f"inbox — {len(_stale)} item(s) past 14 days: {_names}"
                         + (" …" if len(_stale) > 4 else "") +
                         ". An item that will not route usually needs a decision, not a folder. "
                         "`python3 runtime/inbox_triage.py`")
        else:
            ok.append(f"inbox clear ({len(_items)} item(s) waiting, none past 14 days)")
except Exception as e:
    drift.append(f"could not verify the inbox: {e}")


# ── every skill is registered in HQ, not just on disk ──
# Added 2026-08-24. Adding a skill touches two registries: .claude/skills/_README.md and
# dashboard/skills.py §TRACE. Miss the second and HQ still LISTS the skill — with a blank trigger and
# verdict "unmeasurable" — so it reads as a skill nobody can measure rather than one nobody
# registered. That is the failure mode worth catching: the panel exists because the Founder said "I feel like
# I just forget to use the skills," and a blank trigger is the one state that guarantees he still will.
# A deliberate `None` glob is fine and common; an ABSENT key is the bug.
try:
    _sk_dir = os.path.join(ROOT, ".claude", "skills")
    _on_disk = {d for d in os.listdir(_sk_dir)
                if os.path.isdir(os.path.join(_sk_dir, d)) and not d.startswith("_")}
    _panel = read(os.path.join(ROOT, "dashboard/skills.py"))
    _traced = set(re.findall(r'^\s*"([a-z][a-z0-9-]+)":\s*\(', _panel, re.M))
    _readme = read(os.path.join(ROOT, ".claude/skills/_README.md"))
    _missing_trace = sorted(_on_disk - _traced)
    _missing_index = sorted(d for d in _on_disk if f"`{d}`" not in _readme)
    _ghost = sorted(_traced - _on_disk)
    _msgs = []
    if _missing_trace:
        _msgs.append(f"not in dashboard/skills.py TRACE: {', '.join(_missing_trace)} "
                     "(HQ will show a blank trigger and read 'unmeasurable')")
    if _missing_index:
        _msgs.append(f"not listed in .claude/skills/_README.md: {', '.join(_missing_index)}")
    if _ghost:
        _msgs.append(f"TRACE names skill(s) that no longer exist: {', '.join(_ghost)}")
    if _msgs:
        drift.append("skill registration — " + " | ".join(_msgs) +
                     ". See .claude/skills/create-skill/ step 4.")
    else:
        ok.append(f"skills registered ({len(_on_disk)} on disk, all in HQ's TRACE and the index)")
except Exception as e:
    drift.append(f"could not verify skill registration: {e}")


# ── the role coach stays grounded, and keeps refusing the role it cannot ground ──
# Added 2026-08-24 with crm/coach.py. Two properties matter and neither is visible by reading output.
# (1) Every drill must map to a lesson that EXISTS — a drill whose lesson was renamed or deleted is a
#     trick question, tested on material the curriculum no longer teaches.
# (2) Partner must stay NOT coachable while partner duties are undefined. That refusal is not
#     squeamishness: the OA's own open gap #8 says "'substantially full time' against no written
#     duties means Service Failure never fires", and its fix is Schedule C-1 lane definitions. A
#     partner curriculum would author that schedule by the back door, without counsel, against a live
#     question about when Service Failure fires. If someone flips `coachable` on without D5 being
#     answered, that has to be loud.
try:
    sys.path.insert(0, os.path.join(ROOT, "crm"))
    import coach as _co
    _msgs = []
    if _co.ROLES["partner"]["coachable"]:
        _oa_early = read(os.path.join(ROOT, "finance/legal-docs/operating-agreement-DRAFT.md"))
        if "The undefined lane" in _oa_early:
            _msgs.append("partner is marked COACHABLE while the OA still lists gap #8 'The undefined "
                         "lane' — a partner curriculum would author Schedule C-1 without counsel")
    for _role, _cfg in _co.ROLES.items():
        if not _cfg["coachable"]:
            continue
        _slugs = {l["slug"] for l in _co._load(_role)}
        # Compare the RAW keys of _drills.json, not the resolved drills: drills() only ever yields
        # entries whose lesson it already found, so checking its output for orphans is tautological.
        # An earlier version of this check did exactly that and passed a deliberately broken file.
        _orphans = sorted(set(_co._drills_file(_role)) - _slugs)
        if _orphans:
            _msgs.append(f"{_role}: drill(s) point at missing lesson(s) {_orphans}")
        if not _slugs:
            _msgs.append(f"{_role}: curriculum directory is empty — the coach has nothing to teach")
    for _r in ("growth", "session"):
        _out = getattr(_co, _r)("advisor", "__probe__")
        if not _out.get("cannotSee"):
            _msgs.append(f"coach.{_r}() no longer states what it cannot see — at n=0 clients that "
                         "disclaimer is the only thing separating coaching from invention")
    if _msgs:
        drift.append("role coach — " + " | ".join(_msgs) + ". See crm/coach.py.")
    else:
        _n = sum(len(_co.drills(r)) for r, c in _co.ROLES.items() if c["coachable"])
        ok.append(f"role coach grounded ({_n} drills, all mapped to real lessons; partner correctly "
                  "refused while its duties are undefined)")
except Exception as e:
    drift.append(f"could not verify the role coach: {e}")


# ── every CSS custom property a surface uses is actually defined ──
# Added 2026-08-24. `var(--ink)` was used twice in the Connector Console and defined nowhere. An
# undefined var() with no fallback makes the whole declaration invalid at computed-value time, so
# `color` silently falls back to INHERIT — which meant `.staged strong` inherited the muted colour
# from `.staged` and rendered emphasis at exactly the weight of the text it was meant to stand out
# from. Nothing errors, nothing logs, and the page looks *almost* right, which is why it survived.
# HQ had two more of the same shape (`--bg2`, `--muted`) — both introduced the same day by the
# freshness strip and the Search door. This is a whole class of bug and it is cheap to close.
try:
    _surfaces = [
        "processes/partnerships/connector-console/index.html",
        "dashboard/index.html",
        "crm/index.html",
        "clients/_yourco-template/client-console.html",
        "clients/_yourco-template/audit-report/index.html",
    ]
    _msgs = []
    for _sf in _surfaces:
        _fp = os.path.join(ROOT, _sf)
        if not os.path.exists(_fp):
            continue
        _css = read(_fp)
        # A var() may carry its own fallback — `var(--x, #fff)` is legitimate and self-healing, so
        # only bare uses count.
        _used = set(re.findall(r"var\(\s*(--[a-z0-9-]+)\s*\)", _css))
        _defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", _css))
        _missing = sorted(_used - _defined)
        if _missing:
            _msgs.append(f"{_sf}: {', '.join(_missing)}")
    if _msgs:
        drift.append("undefined CSS tokens — " + " | ".join(_msgs) +
                     ". An undefined var() with no fallback makes the declaration invalid and the "
                     "property falls back to inherit; the page looks almost right and nothing errors.")
    else:
        ok.append(f"CSS tokens all resolve ({len(_surfaces)} surfaces checked)")
except Exception as e:
    drift.append(f"could not verify CSS tokens: {e}")


# ── no interactive control wears a DIVIDER token as its border ──
# Added 2026-08-24 after a sweep of all 12 HQ doors: 8 control types failed WCAG's 3:1 for UI
# components, every one because a control had been given --line / --line-soft / --hairline. Those are
# divider tokens — correctly faint for a hairline between rows, and 1.2–1.6:1 against their own
# grounds, so a control wearing one does not read as operable. Strengthening the tokens would darken
# every decorative rule on the page, so controls use --control-edge instead (--pewter: 3.21:1 on the
# dark ground, 4.23:1 on the cream panel).
#
# Real contrast needs a browser — backdrops, alpha compositing, scoped token overrides. This checks
# the PATTERN that produced every failure instead, which is static and cheap. It is a proxy, and it
# says so: passing here is not proof of 3:1, it is absence of the known cause.
try:
    _css = read(os.path.join(ROOT, "dashboard/index.html"))
    _DIVIDERS = ("var(--line)", "var(--line-soft)", "var(--hairline)")
    _CONTROL = re.compile(r"^\.?[a-zA-Z][\w .:>()\[\]=\"'-]*\b(input|select|textarea|button|\.btn|\.bd-chip|\.bd-tile|\.bd-own|\.chip)\b[^{]*\{([^}]*)\}", re.M)
    _bad = []
    for _m in _CONTROL.finditer(_css):
        _sel = _m.group(0).split("{")[0].strip()
        _body = _m.group(2)
        if not re.search(r"border(-top)?\s*:\s*[^;]*solid", _body):
            continue
        for _d in _DIVIDERS:
            if re.search(r"border(-top)?\s*:\s*[^;]*solid\s*" + re.escape(_d), _body):
                _bad.append(f"{_sel[:44]} -> {_d}")
    if _bad:
        drift.append("HQ control borders — divider token used as a control edge: "
                     + " | ".join(sorted(set(_bad))[:6])
                     + ". Dividers measure ~1.2-1.6:1; UI components need 3:1. Use --control-edge.")
    else:
        ok.append("HQ control borders use --control-edge, not divider tokens "
                  "(proxy for the 3:1 sweep; 201 controls measured clean 2026-08-24)")
except Exception as e:
    drift.append(f"could not verify HQ control borders: {e}")


# ── the Florida annual report, which carries an automatic $400 penalty ──
# Added 2026-08-25 while writing SETUP/01. Florida's LLC annual report is due 1 Jan – 1 May every
# year at $138.75, and missing 1 May triggers an automatic, non-negotiable $400 penalty. yourco was
# formed 22 April 2026, so its FIRST report is due by 1 May 2027 — and nothing reminded anyone.
#
# A knowable date with a fixed four-hundred-dollar downside is exactly what a watchdog is for. This
# warns from 1 January until a record exists for that year, then goes quiet. It records nothing and
# files nothing: filing is the Founder's, and the check only refuses to let the date pass unnoticed.
try:
    import datetime as _dt
    _today = _dt.date.today()
    _year = _today.year
    if _year >= 2027:                     # first obligation year; nothing is due before this
        _biz = os.path.join(ROOT, "finance/legal-docs/business-info.md")
        _txt = read(_biz) if os.path.exists(_biz) else ""
        _filed = re.search(rf"annual report.{{0,40}}{_year}.{{0,40}}(filed|paid|confirmed)", _txt, re.I) \
                 or os.path.exists(os.path.join(ROOT, f"finance/legal-docs/annual-report-{_year}.pdf"))
        _due = _dt.date(_year, 5, 1)
        _left = (_due - _today).days
        if not _filed and _today <= _due:
            drift.append(f"FL annual report {_year} — due 1 May, {_left} day(s) left, $138.75. "
                         f"No record of filing in finance/legal-docs/. **Missing 1 May is an "
                         f"automatic $400 penalty** ($538.75 total), non-negotiable. File at "
                         f"sunbiz.org, then note it in business-info.md so this goes quiet.")
        elif not _filed and _today > _due:
            drift.append(f"FL annual report {_year} — **PAST DUE** since 1 May and no record of "
                         f"filing. The $400 penalty is automatic; the entity can eventually be "
                         f"administratively dissolved. Resolve today.")
        else:
            ok.append(f"FL annual report {_year} recorded as filed")
    else:
        ok.append(f"FL annual report — nothing due yet (formed 2026; first report is due by "
                  f"1 May 2027)")
except Exception as e:
    drift.append(f"could not verify the FL annual report deadline: {e}")


# ── standing obligations: insurance in force, and 10DLC not silently stalled ──
# Added 2026-08-25, extending the FL annual-report check. the Founder asked for "renewal dates"; neither of
# these HAS one yet, and inventing a date to watch would be worse than watching nothing. What they
# actually have is a STATE, and the state is the risk:
#
#   insurance — nothing is bound (insurance-plan.md, 2026-07-08). Meanwhile
#               processes/contracts/engagement-agreement.md §13 ALREADY REPRESENTS that yourco
#               "will maintain" GL + E&O + Cyber, softened only by a bracketed [[Once obtained]].
#               Signing a client on that language with no policy behind it is the exposure, so the
#               trigger is a client reaching signed/live — not a calendar date.
#   10DLC     — a critical path with 2-4 week lead time, last status 2026-06-16, blocked on needing
#               Privacy Policy + T&C URLs. A blocked runbook nobody has touched in months reads
#               exactly like a finished one.
#
# Both go quiet the moment the underlying fact changes: bind a policy, or update the status line.
try:
    import datetime as _dt, json as _json
    _msgs, _oks = [], []

    # --- insurance -------------------------------------------------------------------------
    _ins = read(os.path.join(ROOT, "finance/legal-docs/insurance-plan.md"))
    _bound = bool(re.search(r"\b(bound|binder in hand|policy in force|in force)\b", _ins, re.I)) \
             and not re.search(r"nothing bound yet", _ins, re.I)
    _live = []
    try:
        _crm = _json.load(open(os.path.join(ROOT, "crm/data.json"), encoding="utf-8"))
        for _c in (_crm.get("companies") or []):
            _st = str(_c.get("stage", "")).lower()
            if _st in ("live", "signed", "won", "closed-won", "active"):
                _live.append(_c.get("name", "?"))
    except Exception:
        _live = None                      # unreadable CRM is not the same as no live clients
    if not _bound:
        if _live is None:
            _msgs.append("insurance is unbound and the CRM could not be read to check for a live "
                         "client — treat as unverified, not as safe")
        elif _live:
            _msgs.append(f"**insurance is UNBOUND and {len(_live)} client(s) are signed/live "
                         f"({', '.join(_live[:3])}). engagement-agreement.md §13 represents GL + E&O "
                         f"+ Cyber coverage. That representation currently has no policy behind it.**")
        else:
            _oks.append("insurance unbound — no signed/live client yet, so the go-live trigger has "
                        "not fired (engagement-agreement.md §13 still reads [[Once obtained]])")
    else:
        _oks.append("insurance recorded as bound")

    # --- 10DLC -----------------------------------------------------------------------------
    _p10 = os.path.join(ROOT, "processes/10dlc-sending-infra-setup.md")
    _t10 = read(_p10)
    _dates = re.findall(r"Status[^(]{0,30}\((\d{4}-\d{2}-\d{2})", _t10)
    if not _dates:
        _msgs.append("10DLC runbook carries no dated Status line — cannot tell live from abandoned")
    else:
        _newest = max(_dates)
        _age = (_dt.date.today() - _dt.date.fromisoformat(_newest)).days
        # Completion is read ONLY from the newest dated Status line, never from prose elsewhere in
        # the file. The first version of this check searched the whole document and matched
        # "- [x] 10DLC brand approved" out of the "After all this" section — which is a FUTURE
        # checklist ("you're cleared when these are true"), not a record that they are. It reported
        # 10DLC complete while the runbook was blocked on Privacy Policy + T&C URLs. A target state
        # read as a current state is the worst failure a check like this can have, because it is
        # silent and it says "safe".
        _line = next((l for l in _t10.splitlines() if _newest in l and re.search(r"Status", l)), "")
        _done = bool(re.search(r"\b(approved|complete|done|live)\b", _line, re.I)) \
                and not re.search(r"\b(blocked|pending|requires|waiting|needs)\b", _line, re.I)
        if _done:
            _oks.append(f"10DLC recorded complete (status {_newest})")
        elif _age > 30:
            _msgs.append(f"10DLC stalled — newest status {_newest}, **{_age} days** ago, and not "
                         f"recorded complete. Lead time is 2-4 weeks, so this is on the critical "
                         f"path for any texting client. Update the status line or close it out.")
        else:
            _oks.append(f"10DLC in progress (status {_newest}, {_age}d)")

    for _o in _oks:
        ok.append(_o)
    if _msgs:
        drift.append("standing obligations — " + " | ".join(_msgs))
except Exception as e:
    drift.append(f"could not verify standing obligations: {e}")


# ── documents that declare their own checks ──
# Added 2026-08-24. Two whole classes of drift, closed generically rather than one instance at a
# time — see runtime/doc_claims.py for the reasoning.
#
#   COUNTS      a number in a doc carries `<!--#count: ...-->` and is verified against the thing it
#               describes. Guarding a new number is now one comment on the line you were already
#               typing, not a Python edit here — which is the difference between coverage that
#               grows and coverage that waits for someone to notice drift by eye.
#   CITATIONS   every repo-rooted `path/to/file.ext` in backticks must resolve. 2,748 of them exist;
#               49 pointed at nothing. A doc may cite something not built yet — it says so with
#               `<!--#planned-->` rather than the checker guessing.
#
# The hardcoded _claims table above still holds the few that cannot be expressed as an annotation
# (bullets inside a named section). Everything else migrated.
try:
    _dc_spec = _ilu.spec_from_file_location("_doc_claims", os.path.join(ROOT, "runtime/doc_claims.py"))
    _dc = _ilu.module_from_spec(_dc_spec); _dc_spec.loader.exec_module(_dc)
    _rows = _dc.scan()
    _rep = _dc.report(_rows)
    _cites = _dc.citations()
    _msgs = []
    if _rep["problems"]:
        _msgs.append("self-declared count(s) wrong: " + " | ".join(
            f"{p['file']}:{p['line']} {p['why']}" for p in _rep["problems"][:4]))
    if _cites:
        _by = {}
        for _c in _cites:
            _by.setdefault(_c["cited"], []).append(_c["file"])
        _msgs.append(f"{len(_by)} dead citation(s): " + " | ".join(
            f"{k} (in {v[0]})" for k, v in list(_by.items())[:4]))
    if _msgs:
        drift.append("doc claims — " + " | ".join(_msgs) +
                     ". Run `python3 runtime/doc_claims.py --list`. A number that is wrong is fixed "
                     "in the doc, never here; a citation that is deliberately ahead of reality gets "
                     "`<!--#planned-->`.")
    else:
        ok.append(f"doc claims hold ({_rep['total']} self-declared counts verified, "
                  f"0 dead citations across the repo)")
except Exception as e:
    drift.append(f"could not verify doc claims: {e}")


# ── The one number, and the number each agent owns (added 2026-08-25) ──
# Three inputs on 2026-08-24 pointed at one gap: nine co-equal goals is zero goals, and 27 agents
# owned no numbers. Both halves are now declared — the apex in dashboard/goals.json (the Founder's), the
# per-agent definitions in runtime/agent-registry.json (Rafi's). These invariants exist so neither
# can rot: an agent added without a number, a metric claiming a source that does not compute, or an
# "unmeasured" entry with no named gap are all silent failures that read as coverage.
try:
    _reg = json.loads(read(os.path.join(ROOT, "runtime/agent-registry.json")) or "{}")
    _am = _reg.get("agent_metrics") or {}
    _agents_declared = _am.get("agents") or {}
    _sources = set((_am.get("sources") or {}).keys())
    _folders = {n for n in os.listdir(os.path.join(ROOT, "agents"))
                if os.path.isdir(os.path.join(ROOT, "agents", n)) and not n.startswith("_")}
    _miss = sorted(_folders - set(_agents_declared))
    _orph = sorted(set(_agents_declared) - _folders)
    if _miss:
        drift.append(f"agent(s) with no number assigned: {', '.join(_miss)} — every agent in agents/ "
                     f"must declare what it moves in agent-registry.json agent_metrics.agents.")
    if _orph:
        drift.append(f"agent_metrics names agent(s) that no longer exist: {', '.join(_orph)}.")

    # A metric may claim only a source that is declared AND implemented; and an unmeasured one must
    # say what is missing. Otherwise a blank cell reads as "fine" instead of "nobody wired this".
    _bad_src, _bad_gap, _bad_lad = [], [], []
    # northstar.py implements the CRM/finance metrics; loop_metrics.py implements the seven that
    # were prose and is merged into the same table at import. Both are read, or every metric the
    # second module owns reads as "claims a source nothing computes".
    _impl = set()
    for _f in ("dashboard/northstar.py", "dashboard/loop_metrics.py", "dashboard/crm_metrics.py",
               "dashboard/client_metrics.py", "dashboard/uptime.py",
               "dashboard/gate_metrics.py"):
        _m = re.search(r"^METRICS = \{(.*?)^\}", read(os.path.join(ROOT, _f)), re.S | re.M)
        if _m:
            _impl |= set(re.findall(r'"([A-Za-z]+)":', _m.group(1)))
    for _who, _spec in _agents_declared.items():
        _src = _spec.get("source")
        if _src not in _sources:
            _bad_src.append(f"{_who} → {_src!r} not in agent_metrics.sources")
        elif _src != "unmeasured" and _spec.get("owns") not in _impl:
            _bad_src.append(f"{_who} → claims {_src!r} but northstar.METRICS has no "
                            f"{_spec.get('owns')!r}")
        if _src == "unmeasured" and not (_spec.get("needs") and _spec.get("blockedBy")):
            _bad_gap.append(_who)
        if _spec.get("ladders") not in ("direct", "enabling"):
            _bad_lad.append(f"{_who} → {_spec.get('ladders')!r}")
    if _bad_src:
        drift.append("agent metric source(s) unusable: " + " | ".join(_bad_src[:4]))
    if _bad_gap:
        drift.append("unmeasured agent metric(s) with no named gap: " + ", ".join(_bad_gap[:6]) +
                     " — an unmeasured metric MUST carry needs + blockedBy, or the blank is a wish.")
    if _bad_lad:
        drift.append("agent metric(s) with an illegal `ladders` value: " + " | ".join(_bad_lad[:4]) +
                     " — direct or enabling only. An agent whose number does neither is a "
                     "retirement question, not a third category.")
    if not (_miss or _orph or _bad_src or _bad_gap or _bad_lad):
        ok.append(f"every agent owns a number ({len(_agents_declared)} declared, "
                  f"{sum(1 for v in _agents_declared.values() if v.get('source') != 'unmeasured')} "
                  f"computable, the rest carry a named gap)")

    # The apex itself: declared, singular, and one of the metrics HQ actually computes.
    _goals = json.loads(read(os.path.join(ROOT, "dashboard/goals.json")) or "{}")
    _ns = (_goals.get("northstar") or {}).get("metric")
    _gm = re.search(r"^GOAL_METRICS = \((.*?)\)", read(os.path.join(ROOT, "dashboard/server.py")),
                    re.S | re.M)
    _known = set(re.findall(r'"([A-Za-z]+)"', _gm.group(1))) if _gm else set()
    if not _ns:
        drift.append("no north star declared — dashboard/goals.json needs northstar.metric. Nine "
                     "co-equal goal metrics is the thing this replaced.")
    elif _known and _ns not in _known:
        drift.append(f"north star {_ns!r} is not one of server.GOAL_METRICS — nothing computes it.")
    else:
        _sup = set((_goals.get("northstar") or {}).get("supporting") or [])
        if _known and _sup and (_sup | {_ns}) != _known:
            drift.append("goals.json northstar.supporting + the north star do not cover "
                         "GOAL_METRICS exactly — a metric is either the apex or supporting, and a "
                         "metric in neither list is back to being a co-equal goal.")
        else:
            ok.append(f"north star declared and computable: {_ns}")
except Exception as e:
    drift.append(f"could not verify the north star / agent metrics: {e}")

# ── "In motion" means one thing (added 2026-08-25) ──
# HQ counted 3 deals in motion while the CRM's KPI band said 37, because `pre-convo` is a bench in
# dashboard/server.py and a working rung in crm/index.html. Both are defensible for their purpose —
# the board shows what you work, the metric counts what is actually moving — but they used the SAME
# WORDS for different sets, and that is how "37 deals in motion" ended up in a triage memo.
# The definitions may differ; the labels may not, and the CRM must carry the reconciliation.
try:
    _srv = read(os.path.join(ROOT, "dashboard/server.py"))
    _m = re.search(r'^BENCH_STAGES = \((.*?)\)', _srv, re.S | re.M)
    _hq_bench = set(re.findall(r'"([a-z\-]+)"', _m.group(1))) if _m else set()
    _crm = read(os.path.join(ROOT, "crm/index.html"))
    _m2 = re.search(r'^const _motion\s*=\s*d\s*=>.*$', _crm, re.M)
    _crm_excl = set(re.findall(r'x\.stage!=="([a-z\-]+)"', _m2.group(0))) if _m2 else set()
    _marker = 'HQ\'s \\"deals in motion\\" counts only past Pre Convo'
    _diff = sorted((_hq_bench - _crm_excl) - {"relationship", "prospect"})   # legacy names, unused
    if not _hq_bench or not _m2:
        drift.append("could not read the in-motion definitions from server.py / crm/index.html — "
                     "the shapes moved; re-point this invariant.")
    elif _diff:
        _bad_label = re.search(r'\{k:"In motion"', _crm)
        if _bad_label:
            drift.append(f'CRM labels a set "In motion" that includes {_diff} — stages HQ counts as '
                         f'bench. One word, two numbers is the drift class this repo exists to '
                         f'prevent. Rename the label or align the definitions.')
        elif _marker not in _crm:
            drift.append(f"CRM and HQ disagree about {_diff} and the CRM no longer carries the "
                         f"reconciliation note. Restore it, or align the two definitions.")
        else:
            ok.append(f'"in motion" is unambiguous (HQ excludes {_diff}; the CRM says so on the card)')
    else:
        if _marker in _crm:
            drift.append("the CRM still carries the in-motion reconciliation note, but HQ and the "
                         "CRM now agree — a note explaining a difference that no longer exists is "
                         "the next thing to mislead someone. Remove it.")
        else:
            ok.append('"in motion" means the same set in HQ and the CRM')
except Exception as e:
    drift.append(f"could not verify the in-motion definitions: {e}")


# ── The CRM's controlled vocabularies stay controlled (added 2026-08-25) ──
# `company.source` was free text and every intake path invented its own string, which is why no
# surface could ask which CHANNEL produced a company. `channel` is the controlled answer — and a
# controlled vocabulary that nothing checks becomes free text again within a month.
try:
    _crm = json.loads(read(os.path.join(ROOT, "crm/data.json")) or "{}")
    _meta = _crm.get("meta") or {}
    _chan = set(_meta.get("sourceChannels") or [])
    _cos = [c for c in (_crm.get("companies") or []) if not c.get("archived")]
    _bad = sorted({(c.get("channel") or "") for c in _cos
                   if (c.get("channel") or "").strip() and c.get("channel") not in _chan})
    _badsrc = sorted({(c.get("channelSource") or "") for c in _cos
                      if (c.get("channelSource") or "") not in ("", "recorded", "restated", "inferred")})
    _msgs = []
    if not _chan:
        _msgs.append("crm/data.json meta.sourceChannels is missing — company.channel has no vocabulary")
    if _bad:
        _msgs.append(f"company.channel value(s) outside meta.sourceChannels: {_bad}")
    if _badsrc:
        _msgs.append(f"company.channelSource must be recorded/restated/inferred, found: {_badsrc}")
    # Every intake path must stamp the channel, or coverage decays silently as new rows arrive.
    _unstamped = [f for f in ("runtime/promote.py", "runtime/promote_intent.py",
                              "runtime/site_intake.py", "runtime/snapshot_intake.py")
                  if '"channel"' not in read(os.path.join(ROOT, f))]
    if _unstamped:
        _msgs.append("intake path(s) create a company without stamping `channel`: "
                     + ", ".join(_unstamped) + " — coverage decays with every new row and the "
                     "channel metrics refuse below 80%")
    # The Audit is the front door of the whole motion; losing the activity type makes its
    # conversion unknowable again, which is the exact state 2026-08-25 fixed.
    if "Audit delivered" not in (_meta.get("activityTypes") or []):
        _msgs.append("crm/data.json meta.activityTypes lost 'Audit delivered' — Bella's conversion "
                     "goes back to being unknowable rather than merely unknown")
    if "collateral" not in (_meta.get("artifactTypes") or []):
        _msgs.append("crm/data.json meta.artifactTypes lost 'collateral' — a one-pager becomes "
                     "indistinguishable from a build again")
    if _msgs:
        drift.append("CRM vocabulary — " + " | ".join(_msgs))
    else:
        _cov = sum(1 for c in _cos if (c.get("channel") or "").strip())
        ok.append(f"CRM vocabularies hold (channel on {_cov}/{len(_cos)} companies, "
                  f"{len(_chan)} channels, all 4 intake paths stamping)")
except Exception as e:
    drift.append(f"could not verify the CRM vocabularies: {e}")


# ── The stage clock cannot go back to being overwritten (added 2026-08-25) ──
# deal.stageSince holds only the CURRENT stage's date, so before stageHistory existed the moment a
# deal advanced, the previous entry date was destroyed — and there were ZERO stage-change activities
# in the log. Days-to-go-live would have been unmeasurable even after client #1. This is the one gap
# on the whole metric sweep that could only be closed BEFORE the fact, so it gets a guard.
try:
    _crm = json.loads(read(os.path.join(ROOT, "crm/data.json")) or "{}")
    _deals = _crm.get("deals") or []
    _stagekeys = {s.get("key") for s in (_crm.get("stages") or [])}
    _msgs = []
    _nohist = [d.get("id") for d in _deals if not d.get("stageHistory")]
    if _nohist:
        _msgs.append(f"{len(_nohist)} deal(s) carry no stageHistory: {_nohist[:5]} — the go-live "
                     f"clock is not running on them")
    _badstage = sorted({h.get("stage") for d in _deals for h in (d.get("stageHistory") or [])
                        if h.get("stage") not in _stagekeys})
    if _badstage:
        _msgs.append(f"stageHistory names unknown stage(s): {_badstage}")
    _badsrc = sorted({(h.get("source") or "") for d in _deals for h in (d.get("stageHistory") or [])
                      if h.get("source") not in ("recorded", "restated")})
    if _badsrc:
        _msgs.append(f"stageHistory source must be recorded/restated, found: {_badsrc}")
    # One writer, and it must still be wired into the move path.
    _idx = read(os.path.join(ROOT, "crm/index.html"))
    if "function pushStage(" not in _idx or _idx.count("pushStage(d,") < 2:
        _msgs.append("crm/index.html no longer calls pushStage() on every stage move — the history "
                     "stops appending and the clock silently goes back to being overwritten")
    if re.search(r'type:\s*"stage"', _idx):
        _msgs.append("crm/index.html writes activity type \"stage\", which is not in "
                     "meta.activityTypes (the vocabulary says \"Stage change\")")
    if _msgs:
        drift.append("stage clock — " + " | ".join(_msgs))
    else:
        ok.append(f"the stage clock is running ({len(_deals)} deals carry stageHistory, one writer)")
except Exception as e:
    drift.append(f"could not verify the stage clock: {e}")

# ── The locked price bands must stay machine-readable (added 2026-08-25) ──
# Polo's number is "quoted prices inside a locked band". If the table in pricing/README.md stops
# parsing, the metric refuses — which is the designed behaviour and still means the only check on
# off-band pricing goes dark. An earlier version of the parser read "$3" out of "cap 3, then
# graduate" and passed the $1,000 brotherhood rate as in-band; that is the failure to guard.
try:
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import client_metrics as _cmet
    _bands = _cmet.locked_bands()
    if len(_bands) < 4:
        drift.append(f"pricing/README.md locked band table parsed {len(_bands)} band(s) — Polo's "
                     f"off-band check is dark. The table is the single source; do not copy it.")
    elif any(lo < _cmet.MIN_PLAUSIBLE_RETAINER or lo > hi for _n, lo, hi in _bands):
        drift.append(f"a locked band parsed implausibly: {_bands} — a floor below "
                     f"${_cmet.MIN_PLAUSIBLE_RETAINER} means the parser is reading prose as money, "
                     f"which is how an off-band price passes as in-band.")
    else:
        ok.append(f"locked price bands parse ({len(_bands)} bands; "
                  f"${min(lo for _n, lo, _h in _bands):,} floor)")
except Exception as e:
    drift.append(f"could not verify the locked price bands: {e}")


# ── The heartbeat's denominator (added 2026-08-25) ──
# Uptime is beats received over beats EXPECTED, and "expected" is derived from the interval. The
# interval is written in three places — the writer, the systemd timer and the reader — and if they
# ever disagree the percentage is silently wrong in whichever direction the mismatch runs.
try:
    _hb = read(os.path.join(ROOT, "runtime/heartbeat.sh"))
    _tm = read(os.path.join(ROOT, "runtime/systemd/yourco-heartbeat.timer"))
    _up = read(os.path.join(ROOT, "dashboard/uptime.py"))
    _msgs = []
    _w = re.search(r"^INTERVAL_MIN=(\d+)", _hb, re.M)
    _t = re.search(r"^OnCalendar=\*:0/(\d+)", _tm, re.M)
    _r = re.search(r"^INTERVAL_MIN = (\d+)", _up, re.M)
    _vals = {"heartbeat.sh": _w and _w.group(1), "timer": _t and _t.group(1), "uptime.py": _r and _r.group(1)}
    if None in _vals.values():
        _msgs.append(f"could not read the beat interval from all three: {_vals}")
    elif len(set(_vals.values())) != 1:
        _msgs.append(f"beat interval disagrees across writer/timer/reader: {_vals} — the uptime "
                     f"denominator is wrong in whichever direction the mismatch runs")
    # A persistent timer would fire catch-up runs after downtime and back-fill the exact gap this
    # instrument exists to expose: the outage would erase its own evidence.
    if "Persistent=false" not in _tm:
        _msgs.append("yourco-heartbeat.timer is not Persistent=false — catch-up beats would "
                     "back-fill the outage they are supposed to reveal")
    # It must survive a dead credit balance, which is how the runtime actually went dark twice.
    if re.search(r"^[^#]*\bclaude\b", _hb, re.M):
        _msgs.append("runtime/heartbeat.sh appears to invoke `claude` — the one instrument that "
                     "must keep working during an outage cannot depend on the thing that is out")
    # The store must be committed. loops/_runtime/ is gitignored and that is exactly why none of
    # this was ever visible from the Mac.
    _gi = read(os.path.join(ROOT, ".gitignore"))
    if "loops/_health/heartbeat.jsonl" in _gi or re.search(r"^loops/_health/\s*$", _gi, re.M):
        _msgs.append("loops/_health/ is gitignored — the beats never reach the repo and uptime is "
                     "unmeasurable from anywhere but the box")
    # Rafi's watchdog flags any unsanctioned unit, so an unsanctioned heartbeat would show up as
    # governance drift the moment it is installed.
    _reg = json.loads(read(os.path.join(ROOT, "runtime/agent-registry.json")) or "{}")
    for _k, _u in (("sanctioned_timers", "yourco-heartbeat.timer"),
                   ("sanctioned_services", "yourco-heartbeat.service")):
        if _u not in (_reg.get(_k) or []):
            _msgs.append(f"{_u} is not in {_k} — installing it would read as registry drift")
    if _msgs:
        drift.append("heartbeat — " + " | ".join(_msgs))
    else:
        ok.append(f"the heartbeat's denominator holds ({_vals['timer']}-minute beat in writer, "
                  f"timer and reader; non-persistent; store committed; units sanctioned)")
except Exception as e:
    drift.append(f"could not verify the heartbeat: {e}")


# ── No writer may create a row on a retired rung (added 2026-08-25) ──
# The README half of this was already checked. The CODE half was not, and three separate writers —
# promote.py, promote_intent.py and intent_server.py — still created deals on `prospect`, a rung
# retired in the 2026-08-07 ladder restructure. Every row they made would have landed off the board,
# and nothing would have noticed until someone went looking for the first outbound lead.
try:
    _crm = json.loads(read(os.path.join(ROOT, "crm/data.json")) or "{}")
    _live_stages = {s.get("key") for s in (_crm.get("stages") or [])}
    _meta = _crm.get("meta") or {}
    _writers = ["runtime/promote.py", "runtime/promote_intent.py", "runtime/intent_server.py",
                "runtime/site_intake.py", "runtime/snapshot_intake.py"]
    _msgs = []
    for _w in _writers:
        _src = read(os.path.join(ROOT, _w))
        if not _src:
            continue
        for _m in re.finditer(r'"stage":\s*"([a-z\-]+)"', _src):
            if _m.group(1) not in _live_stages:
                _msgs.append(f"{_w} creates a deal on retired stage {_m.group(1)!r}")
        # A deal created without stageHistory carries no clock, so the go-live durations are lost
        # for exactly the deals that path produces.
        if '"stage":' in _src and '"stageHistory"' not in _src:
            _msgs.append(f"{_w} creates a deal with no stageHistory — the go-live clock never starts "
                         f"on rows from that path")
    # Sequence status is a controlled vocabulary now; a value outside it is invisible to the rate.
    _seq = set(_meta.get("seqStatuses") or [])
    if not _seq:
        _msgs.append("crm/data.json meta.seqStatuses is missing — a reply's quality is unrecordable")
    else:
        _bad = sorted({(d.get("seqStatus") or "") for d in (_crm.get("deals") or [])
                       if (d.get("seqStatus") or "") and d.get("seqStatus") not in _seq | {"replied"}})
        if _bad:
            _msgs.append(f"deal.seqStatus value(s) outside meta.seqStatuses: {_bad}")
        if "replied-positive" not in _seq:
            _msgs.append("meta.seqStatuses lost `replied-positive` — 'positive reply rate' stops "
                         "being expressible and Michelle's number goes dark")
    if "Booking" not in (_meta.get("activityTypes") or []):
        _msgs.append("meta.activityTypes lost 'Booking' — contact.nextMeeting holds only the NEXT "
                     "one, so without the activity the second booking erases the first")
    if _msgs:
        drift.append("intake writers — " + " | ".join(_msgs[:5]))
    else:
        ok.append(f"every intake writer uses a live stage and starts the clock "
                  f"({len(_writers)} paths checked)")
except Exception as e:
    drift.append(f"could not verify the intake writers: {e}")

# ── A booking from the site has to be attributable to the site (added 2026-08-25) ──
# Every Calendly link on the staged site was bare, so a booking out of the site was indistinguishable
# from one out of an email, a connector, or a pasted URL. Webb's number depends on the parameter
# surviving to launch, and the launch is the moment nobody will be re-reading this file.
try:
    _pages = site_pages()          # SITE is already the staged-site path at the top of this file
    _bare, _tagged = [], 0
    for _p in _pages:
        _s = read(_p)
        for _m in re.finditer(r"calendly\.com/[^\"'\s]*", _s):
            if "utm_source=" in _m.group(0):
                _tagged += 1
            else:
                _bare.append(os.path.basename(_p))
    if _bare:
        drift.append(f"{len(set(_bare))} page(s) carry an untagged Calendly link "
                     f"({', '.join(sorted(set(_bare))[:4])}) — a booking from those is "
                     f"indistinguishable from one out of an email or a pasted URL, and Webb's "
                     f"number cannot see it.")
    elif _tagged:
        ok.append(f"every Calendly link on the site is attributable ({_tagged} links tagged)")
except Exception as e:
    drift.append(f"could not verify the site's booking links: {e}")


# ── The recording step lives where the doing is described (added 2026-08-25) ──
# Three agents' numbers depend on a human logging one thing at the moment a real event happens. The
# prose-cluster lesson was that a loop which produces a number and writes it into a memo is the same
# as not producing it — this is the human version. If the SOP that governs the DOING stops naming
# the RECORDING, the first audit gets delivered and never counted, exactly as before.
try:
    _sop = read(os.path.join(ROOT, "processes/audit-sop.md"))
    _kl = read(os.path.join(ROOT, "agents/Reed/02_build.md"))
    _pk = read(os.path.join(ROOT, "agents/pickle/_README.md"))
    _msgs = []
    if "Audit delivered" not in _sop:
        _msgs.append("processes/audit-sop.md no longer tells anyone to log an `Audit delivered` "
                     "activity — the Audit is the front door of the whole motion and its conversion "
                     "goes back to unknowable")
    if "type: video" not in _kl:
        _msgs.append("agents/Reed/02_build.md lost its definition-of-done: register a shown asset "
                     "on the deal (`type: video`), or reach stops being countable")
    if "type: collateral" not in _pk:
        _msgs.append("agents/pickle/_README.md lost its definition-of-done: register used collateral "
                     "on the deal (`type: collateral`)")
    # And the Board must still be able to SAY that nothing has been shown — a metric reading blank
    # is invisible in exactly the way absence-is-invisible describes.
    if "def unshown_assets" not in read(os.path.join(ROOT, "dashboard/board.py")):
        _msgs.append("dashboard/board.py no longer surfaces produced-but-never-shown assets, so "
                     "'nobody has put collateral in front of anyone' becomes a fact no surface states")
    if _msgs:
        drift.append("recording steps — " + " | ".join(_msgs))
    else:
        ok.append("the three first-event recording steps are named in the SOPs that govern them")
except Exception as e:
    drift.append(f"could not verify the recording steps: {e}")


# ── The nine KPIs: the doc and the engine cannot drift (added 2026-08-25) ──
try:
    _k = read(os.path.join(ROOT, "dashboard/kpis.py"))
    _names = re.findall(r'^\s*"([a-zA-Z]+)", "([^"]+)",$', _k, re.M)
    _doc = read(os.path.join(ROOT, "finance/kpi-definitions.md"))
    if len(_names) != 9:
        drift.append(f"dashboard/kpis.py defines {len(_names)} KPIs, not 9 — if a KPI was added or "
                     f"removed, finance/kpi-definitions.md changes in the same commit.")
    _absent = [n for _key, n in _names
               if re.sub(r"\s*\(.*?\)", "", n).lower() not in _doc.lower()]
    if _absent:
        drift.append("KPI(s) computed but not defined in finance/kpi-definitions.md: " +
                     ", ".join(_absent) + " — a number with no written refusal condition is exactly "
                     "the thing that page exists to prevent.")
    if len(_names) == 9 and not _absent:
        ok.append("the nine KPIs match between dashboard/kpis.py and finance/kpi-definitions.md")

    # The machine copy of the actuals may not drift from the narrative one it was taken from.
    _act = json.loads(read(os.path.join(ROOT, "finance/actuals.json")) or "{}")
    _run = read(os.path.join(ROOT, "finance/runway.md"))
    _pairs = [("cash.onHand", (_act.get("cash") or {}).get("onHand")),
              ("burn.monthlyFixed", (_act.get("burn") or {}).get("monthlyFixed"))]
    _gone = []
    for _label, _v in _pairs:
        if _v is None:
            continue
        _txt = f"{_v:,.2f}".rstrip("0").rstrip(".") if isinstance(_v, float) else f"{_v:,}"
        if _txt not in _run and f"{_v:,.2f}" not in _run:
            _gone.append(f"{_label}={_v}")
    if _gone:
        drift.append("finance/actuals.json no longer matches finance/runway.md: " +
                     ", ".join(_gone) + ". runway.md is the narrative record; actuals.json is the "
                     "machine copy of figures it has already confirmed — update both at the close.")
    else:
        ok.append("finance/actuals.json agrees with finance/runway.md")
except Exception as e:
    drift.append(f"could not verify the KPI definitions: {e}")


# ── report ──
today = datetime.date.today().isoformat()
outdir = os.path.join(ROOT, "loops/_consistency"); os.makedirs(outdir, exist_ok=True)
lines = [f"# Consistency check — {today}", "",
         f"**{'DRIFT FOUND' if drift else 'ALL ALIGNED'}** — {len(ok)} invariants pass, {len(drift)} drift item(s).", ""]
if drift:
    lines += ["## Drift (fix each in ONE commit that sweeps every surface)", *[f"- ⚠️ {d}" for d in drift], ""]
lines += ["## Passing", *[f"- ✅ {o}" for o in ok], "",
          "*Invariants live in `runtime/consistency-check.py` — add one every time a human catches drift by eye.*"]
with open(os.path.join(outdir, f"{today}.md"), "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
if "--quiet" not in sys.argv:
    print("\n".join(lines))
sys.exit(1 if drift else 0)
