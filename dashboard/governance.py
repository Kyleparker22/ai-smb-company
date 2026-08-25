#!/usr/bin/env python3
"""Governance — the partner half of the Partners door: what's agreed, what's signed, what blocks.

The commercial half of a three-partner company is tracked everywhere. The governance half —
who owns what, on what terms, blocked by what, reversible until when — lived in five files
nobody opens together: the OA draft, Ray's review, the counsel-gate table, the split decision,
and the cash-structure decision. Reading them as a set is how you notice that the closest gate
to clearing became the furthest, and that the whole structure is still free to change.

EVERYTHING IS QUOTED, NOT RESTATED.  Equity splits, capital terms and gate status are facts with
consequences; a second copy of them in Python would be a liability the first time one changed.
So this module parses the canonical files and cites each one. Where a fact isn't recorded
anywhere, it says **unrecorded** and names what's missing — which is the most valuable output
here, because the open items in this domain are absences, not entries.

A NOTE ON THE WORD.  HQ says **Partner**. The operating agreement's own defined term is
**Principal** ("Founder Principal", "Partner Principal"), and that is left alone — renaming a
defined term inside a legal instrument to match a dashboard label would be a real error, not a
cosmetic one. The two words point at the same three people.

Sources
  decisions/2026-08-10_three-member-split.md ............ the split, and D10–D12
  decisions/2026-08-10_cash-structure-and-model-recalibration.md ... who funds what
  finance/legal-docs/operating-agreement-DRAFT.md ....... version, signature blocks
  finance/legal-docs/oa-review_ray_2026-08-05.md ........ counsel questions
  processes/counsel-gates.md ............................ gate #14 + counsel engagement
  crm/data.json ......................................... whether either partner is papered

Read-only. Exposed as GET /api/governance.
"""
import os, re, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SPLIT_DECISION = "decisions/2026-08-10_three-member-split.md"

# ---- percentages: WITHHELD FROM DISPLAY, not deleted (the Founder 2026-08-18) ------------------
# the Founder asked for the equity percentages off the CRM and HQ "for now". They are still parsed —
# the 100%-total validation and the OA cross-check depend on reading them — but they are not
# rendered. The distinction matters: the split EXISTS in the OA draft, so a panel that simply
# stopped showing numbers would read as "there is no split", which is false and is the more
# dangerous of the two errors. Everywhere a percentage would have appeared, the panel says
# instead that it is withheld and where the number actually lives.
SHOW_PCT = False
PCT_WITHHELD = ("percentages withheld from display at the Founder's request 2026-08-18 — they are "
                "unchanged in " + SPLIT_DECISION + " and in the OA draft, not deleted")
CASH_DECISION = "decisions/2026-08-10_cash-structure-and-model-recalibration.md"
OA = "finance/legal-docs/operating-agreement-DRAFT.md"
OA_REVIEW = "finance/legal-docs/oa-review_ray_2026-08-05.md"
GATES = "processes/counsel-gates.md"


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def _age(iso):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(iso)).days
    except (ValueError, TypeError):
        return None


def _clean(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s or "")
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


# ---- membership -------------------------------------------------------------
def membership():
    """The split, quoted from the decision that set it, cross-checked against the CRM."""
    txt = _read(SPLIT_DECISION)
    out = {"source": SPLIT_DECISION, "members": [], "papered": False, "note": None}
    if not txt:
        out["note"] = f"{SPLIT_DECISION} not found — the split is unrecorded"
        return out

    m = re.search(r"\*\*((?:[A-Z][\w.]*(?: [A-Z][\w.]*)*\s+\d+%\s*(?:·|and)?\s*)+)\*\*", txt)
    if m:
        for part in re.split(r"·|,| and ", m.group(1)):
            mm = re.match(r"\s*([A-Za-z][\w. ]*?)\s+(\d+)%\s*$", part)
            if mm:
                out["members"].append({"name": mm.group(1).strip(), "pct": int(mm.group(2))})
    total = sum(x["pct"] for x in out["members"])
    out["total"] = total
    if out["members"] and total != 100:
        out["note"] = f"the split parses to {total}%, not 100 — check {SPLIT_DECISION}"

    # Is any of it papered? The CRM is the register: teamRole partner + teamStatus.
    try:
        crm = json.loads(_read("crm/data.json") or "{}")
    except ValueError:
        crm = {}
    reg = []
    for c in crm.get("contacts", []) or []:
        if (c.get("teamRole") or "") == "partner":
            reg.append({"name": c.get("name"), "status": c.get("teamStatus") or "unset",
                        "relationship": c.get("relationship") or ""})
    out["crm"] = reg
    out["papered"] = bool(reg) and all(r["status"] == "active" for r in reg)
    out["crmNote"] = ("Every partner on the register sits at `prospect` — nothing is papered."
                      if reg and not out["papered"] else
                      "No partner records in the CRM." if not reg else
                      "CRM shows every partner active.")

    # A partner can exist in the CRM and NOT in the OA — Sample Contact, moved to partner
    # 2026-08-18, is the first. That gap is the most useful thing this panel can show, so it
    # is surfaced as a member with `inOA: False` rather than being dropped for failing to
    # appear in a decision written before he was considered.
    # EXPLICIT aliases, not fuzzy matching. The OA says "Partner C", the CRM record says
    # "Michael Partner C" — one human, two spellings, and without this the panel reported FIVE
    # partners. Surname matching is not an option here: the Founder and Partner B share a
    # surname, and first-initial matching collides on them too. Guessing at nicknames is the
    # same class of error that once mis-joined agents to humans on first name (CLAUDE.md), so
    # the map is hand-written and stays small.
    ALIASES = {"michael Partner C": "Partner C"}
    def _norm(n):
        k = (n or "").strip().lower()
        return ALIASES.get(k, k)
    known = {_norm(x["name"]) for x in out["members"]}
    known |= {_norm(x["name"]).split()[0] for x in out["members"] if _norm(x["name"])}
    for r in reg:
        nm = (r["name"] or "").strip()
        if nm and _norm(nm) not in known and _norm(nm).split()[0] not in known:
            out["members"].append({"name": nm, "pct": None, "inOA": False,
                                   "note": "in the CRM as a partner, NOT in the OA or the split "
                                           "decision — no allocation exists for them"})
    for x in out["members"]:
        x.setdefault("inOA", True)
        x["pctShown"] = (x["pct"] if SHOW_PCT else None)
    out["showPct"] = SHOW_PCT
    out["pctWithheld"] = None if SHOW_PCT else PCT_WITHHELD
    # the Founder is not a CRM contact; the decision is the register for the founder side.
    return out


# ---- the operating agreement ------------------------------------------------
SIG_RE = re.compile(r"^\[([^\]]+)\]\s*—\s*By:\s*([^,]+),\s*(\w+)\s+(_+|\S+)\s*·\s*Date\s+(_+|\S+)",
                    re.M)


def operating_agreement():
    txt = _read(OA)
    out = {"source": OA, "exists": bool(txt)}
    if not txt:
        out["note"] = "no operating-agreement draft found"
        return out
    v = re.search(r"DRAFT\s+(v\d+)", txt)
    d = re.search(r"DRAFT\s+v\d+\s*[—–-]\s*(\d{4}-\d{2}-\d{2})", txt)
    out["version"] = v.group(1) if v else "unversioned"
    out["dated"] = d.group(1) if d else None
    out["ageDays"] = _age(out["dated"])

    sigs = []
    for entity, who, _role, sig, date in SIG_RE.findall(txt):
        signed = not set(sig) <= set("_") or not set(date) <= set("_")
        sigs.append({"entity": entity.strip(), "who": who.strip(), "signed": bool(signed)})
    out["signatures"] = sigs
    out["signedCount"] = sum(1 for s in sigs if s["signed"])
    out["unsigned"] = len(sigs) - out["signedCount"]

    # Ray's in-house review — how many questions travel with it to counsel
    rev = _read(OA_REVIEW)
    # the review titles its list "Part IV — The 8 questions for counsel"; the gate table says
    # "8 sharpened counsel questions". Accept either phrasing rather than reporting "—".
    q = (re.search(r"(?:The\s+)?(\d+)\s+questions? for counsel", rev + txt, re.I)
         or re.search(r"(\d+)\s+(?:sharpened\s+)?counsel questions", rev + txt + _read(GATES), re.I))
    f = re.search(r"F1\s*[–—-]\s*F(\d+)", txt)
    out["review"] = {"source": OA_REVIEW, "exists": bool(rev),
                     "counselQuestions": int(q.group(1)) if q else None,
                     "findings": int(f.group(1)) if f else None}
    out["signedNote"] = ("Nothing is signed. Three signature blocks, all blank."
                         if not out["signedCount"] else
                         f"{out['signedCount']} of {len(sigs)} signature blocks filled.")
    return out


# ---- gate #14 and counsel engagement ---------------------------------------
def _gate_row(num):
    for line in _read(GATES).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].strip() == str(num):
            return cells
    return None


def gate14():
    cells = _gate_row(14)
    if not cells or len(cells) < 5:
        return {"found": False, "source": GATES,
                "note": "gate #14 row not found in the counsel-gate table"}
    status = cells[3]
    icon = next((c for c in "🔴🟠🔲✅🟢" if c in status), "")
    # the blocking decisions named inline, e.g. "**D10** voting threshold (…)"
    blockers = []
    for m in re.finditer(r"\*\*(D\d+)\*\*\s*([^,•]+?)(?=,\s*\*\*D\d+\*\*|\.\s|$)", status):
        blockers.append({"id": m.group(1), "what": _clean(m.group(2))[:160]})
    regressed = re.search(r"regressed\s+(\d{4}-\d{2}-\d{2})", status, re.I)
    return {
        "found": True, "source": GATES, "number": 14,
        "title": _clean(cells[1])[:220],
        "blocks": _clean(cells[2]),
        "icon": icon,
        "status": _clean(status)[:600],
        "blockers": blockers,
        "regressedOn": regressed.group(1) if regressed else None,
        "regressedDays": _age(regressed.group(1)) if regressed else None,
        "docs": _clean(cells[4]) if len(cells) > 4 else "",
    }


def counsel():
    """The engagement table. Its unfilled state is the headline, not a footnote."""
    txt = _read(GATES)
    sec = re.search(r"## Counsel engagement\s*\n((?:\|.*\n)+)", txt)
    fields, engaged = [], False
    if sec:
        for line in sec.group(1).splitlines()[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0]:
                val = _clean(cells[1])
                unfilled = bool(re.search(r"the Founder to fill|none engaged|^—?$", val, re.I))
                fields.append({"field": _clean(cells[0]), "value": val, "unfilled": unfilled})
        engaged = bool(fields) and not any(f["unfilled"] for f in fields)
    # gate rollup for context
    counts = {"blocked": 0, "awaiting": 0, "notStarted": 0, "cleared": 0, "total": 0}
    sec2 = re.search(r"## The gates.*?\n((?:\|.*\n)+)", txt, re.S)
    if sec2:
        for line in sec2.group(1).splitlines()[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or not cells[0].strip():
                continue
            counts["total"] += 1
            s = cells[3]
            if "🔴" in s: counts["blocked"] += 1
            elif "🟠" in s: counts["awaiting"] += 1
            elif "✅" in s: counts["cleared"] += 1
            else: counts["notStarted"] += 1
    return {"source": GATES, "fields": fields, "engaged": engaged, "gateCounts": counts,
            "note": ("No counsel is engaged as far as the workspace records — every 🔴 below "
                     "is waiting on a call that has not been made."
                     if not engaged else "Counsel engaged.")}


# ---- the blocking decisions D10–D12 ----------------------------------------
def open_decisions():
    txt = _read(SPLIT_DECISION)
    sec = re.search(r"## Three new blocking decisions.*?\n(.*?)(?=\n## )", txt, re.S)
    out = []
    if sec:
        for chunk in re.split(r"\n(?=- \*\*D\d+)", sec.group(1)):
            m = re.match(r"-\s*\*\*(D\d+)\s*[—–-]\s*(.+?)\*\*\s*(.*)", chunk.strip(), re.S)
            if m:
                out.append({"id": m.group(1), "title": _clean(m.group(2)),
                            "detail": _clean(m.group(3))[:600]})
    return {"source": SPLIT_DECISION, "decisions": out}


# ---- capital ----------------------------------------------------------------
def capital():
    """Quoted from the cash-structure decision — never re-derived. Money is exactly the kind
    of fact a second copy gets wrong."""
    txt = _read(CASH_DECISION)
    if not txt:
        return {"source": CASH_DECISION, "exists": False,
                "note": "no cash-structure decision found"}
    dec = re.search(r"## Decision\s*\n+(.+?)(?=\n\n|\n## )", txt, re.S)
    caveat = re.search(r"\*\*The caveat that matters more than the headline:\*\*(.+?)(?=\n\n|\n## )",
                       txt, re.S)
    return {
        "source": CASH_DECISION, "exists": True,
        "decision": _clean(dec.group(1))[:900] if dec else None,
        "caveat": _clean(caveat.group(1))[:700] if caveat else None,
        "note": "Quoted from the decision, not recomputed.",
    }


# ---- reversibility ----------------------------------------------------------
def reversibility():
    txt = _read(SPLIT_DECISION)
    sec = re.search(r"## Reversibility\s*\n+(.+?)(?=\n\n|\n## )", txt, re.S)
    body = _clean(sec.group(1)) if sec else None
    return {
        "source": SPLIT_DECISION,
        "text": body,
        "open": bool(body) and "reversible today" in body.lower(),
        "why": ("Nothing is signed, no entity is formed, no Units exist. This is the last moment "
                "the structure is free to change — which is the entire argument for answering "
                "D10–D12 now rather than after."),
    }


# ---- what nobody has written down ------------------------------------------
def unrecorded(counsel_engaged=False):
    """The open items in this domain are absences, so each one is CHECKED, not asserted.

    Each check looks for a STRUCTURED record — a decision file, a filled schedule field, a
    named firm — never a prose mention. That distinction is load-bearing: the first version of
    this function looked for the phrase "Mike's contribution" anywhere in decisions/, and the
    D12 trip-wire's own sentence *about the absence* ("overturn if Mike's contribution, once
    written down, …") satisfied it. A sentence describing a gap is not the gap being filled,
    and reading it as one hid a real blocker."""
    gaps = []

    def gap(label, recorded, why, where):
        if not recorded:
            gaps.append({"what": label, "why": why, "wouldLiveIn": where})

    # 1. Mike's lane and service standard (D12) — a decision file naming him is the record.
    #    Deliberately NOT a text search: the D12 trip-wire's own sentence about the absence
    #    would satisfy one, which is how the first version of this check hid the gap.
    dec_dir = os.path.join(ROOT, "decisions")
    dec_names = [f for f in (os.listdir(dec_dir) if os.path.isdir(dec_dir) else [])
                 if f.endswith(".md")]
    gap("Mike's contribution, lane and service standard",
        any(re.search(r"mike|Partner C", f, re.I) for f in dec_names),
        "D12 turns on it: if his commitment isn't substantially-full-time service, the 15% "
        "profits interest was priced on a wrong assumption, and §4.1, Schedule C-1, Schedule D "
        "and §10.1(i) each need a second version.",
        "a decision entry naming him, then Schedule C-1")

    # 2. Schedule B $ — the OA's own schedule, not the worksheet's worked example. The
    #    worksheet proposing a figure is not the same as the agreement carrying one.
    oa_txt = _read(OA)
    sb_sec = re.search(r"Schedule B\b(.{0,1200})", oa_txt, re.S)
    sb_in_oa = bool(sb_sec) and bool(re.search(r"\$\s?[\d,]{4,}", sb_sec.group(1)))
    sb_wk = _read("finance/legal-docs/schedule-b-valuation-worksheet.md")
    proposed = re.search(r"Distribution Threshold of \*{0,2}\$\s?([\d,]+)", sb_wk)
    gap("Schedule B dollar value (the Distribution Threshold)", sb_in_oa,
        "It is what the Founder side recovers first on liquidation or sale, and leaving it open "
        "re-exposes gate #11."
        + (f" The worksheet proposes ${proposed.group(1)}; the agreement does not carry it yet."
           if proposed else ""),
        "Schedule B in the OA (worksheet: finance/legal-docs/schedule-b-valuation-worksheet.md)")

    # 3. Counsel — reuse the engagement table's own verdict rather than grepping for a firm name
    gap("Counsel — a named firm", counsel_engaged,
        "Every 🔴 gate terminates in the same missing phone call.",
        "the counsel-engagement table in processes/counsel-gates.md")

    return {"gaps": gaps, "oaFills": oa_fills(),
            "note": "Each row is a live check for a STRUCTURED record — a decision file naming "
                    "the person, a figure inside the agreement itself, a named firm — never a "
                    "prose mention, because a sentence describing a gap is not the gap being "
                    "filled. Write the missing thing and the row disappears on the next poll."}


# The OA marks its own open fills with uppercase bracket placeholders. Reading THAT convention
# beats guessing at what's missing: fill the bracket and the row disappears by itself.
FILL_LABELS = {
    "LANE": "a Partner's Schedule C-1 lane — what they actually own",
    "DATE": "the agreement's effective date",
    "STATE": "state of formation for a Partner holdco",
    "STATE RELATIONSHIP": "the Referee's disclosed relationship to each Principal (§9.2A)",
    "AMOUNT": "key-person life insurance amount (§12.1)",
    "FOUNDER SPV LLC": "the Founder SPV — not yet formed",
    "KP HOLDCO LLC": "Partner B's holdco — not yet formed",
    "MT HOLDCO LLC": "Mike's holdco — not yet formed",
}


def oa_fills():
    """Every [UPPERCASE] placeholder still open in the operating agreement, with its meaning."""
    txt = _read(OA)
    found = {}
    for m in re.finditer(r"\[([A-Z][A-Z /_-]{2,40})\]", txt):
        tok = m.group(1).strip()
        d = found.setdefault(tok, {"token": tok, "n": 0,
                                   "means": FILL_LABELS.get(tok, "open fill"),
                                   "context": ""})
        d["n"] += 1
        if not d["context"]:
            d["context"] = _clean(txt[max(0, m.start() - 90):m.end() + 40])[:170]
    return {"source": OA, "fills": sorted(found.values(), key=lambda f: (-f["n"], f["token"])),
            "total": sum(f["n"] for f in found.values()),
            "note": "Parsed from the agreement's own placeholder convention — fill the bracket "
                    "and the row disappears."}


# ---- redaction ---------------------------------------------------------------------------
# The percentages also appear inside text QUOTED from the OA, the split decision and the gate
# log — and governance.py's whole premise is "EVERYTHING IS QUOTED, NOT RESTATED". Silently
# editing a quotation is a worse failure than showing the figure, so every redaction is MARKED.
# Applied to the final payload only: the parsers upstream still see the real numbers, which is
# what the 100%-total check and the OA cross-check depend on.
_PCT_SUBS = [
    (re.compile(r"\b50\s*/\s*35\s*/\s*15\b"), "[split withheld]"),
    (re.compile(r"\bat\s+50/35/15\b", re.I), "at the agreed split"),
    (re.compile(r"\bthe\s+15%\s+holder\b", re.I), "the minority holder"),
    (re.compile(r"\bthe\s+15%\s+profits interest\b", re.I), "the minority profits interest"),
    # These state a COMBINED HOLDING, which reveals the split by subtraction even though the
    # sentence is about a voting threshold. The threshold itself (>50%, >=66%) is governance
    # mechanics and stays — it exists independently of who holds what.
    (re.compile(r"the two Partners? together are exactly 50%", re.I),
     "the two Partners together are exactly half [withheld]"),
    (re.compile(r"the two partners at exactly 50%", re.I),
     "the two partners at exactly half [withheld]"),
]


def _redact(obj):
    """Walk the payload and mask equity percentages in prose. The connector escalator
    (10/12.5/15%) is a different number entirely and is deliberately untouched."""
    if SHOW_PCT:
        return obj
    if isinstance(obj, str):
        for rx, rep in _PCT_SUBS:
            obj = rx.sub(rep, obj)
        return obj
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    if isinstance(obj, dict):
        # `pct` stays intact in the data — consumers read `pctShown`, which is already None.
        return {k: (v if k == "pct" else _redact(v)) for k, v in obj.items()}
    return obj


def build():
    m = membership()
    o = operating_agreement()
    g = gate14()
    c = counsel()
    d = open_decisions()
    u = unrecorded(c["engaged"])
    r = reversibility()

    # the one-line state of play, assembled from the parts and never hand-written
    if not m["members"]:
        headline = "The split is not recorded anywhere the OS can read."
    elif m["papered"]:
        headline = "Membership is papered."
    else:
        n_oa = sum(1 for x in m["members"] if x.get("inOA"))
        n_out = len(m["members"]) - n_oa
        pieces = [f"{len(m['members'])} partners"
                  + (f" ({n_oa} in the OA, {n_out} not)" if n_out else "")
                  + (", split " + "/".join(str(x["pct"]) for x in m["members"] if x.get("pct") is not None)
                     if SHOW_PCT else ", percentages withheld")
                  + ", none papered"]
        if o.get("unsigned"):
            pieces.append(f"{o['unsigned']} unsigned signature blocks")
        if g.get("icon") == "🔴":
            pieces.append("gate #14 blocked-hard"
                          + (f" for {g['regressedDays']}d" if g.get("regressedDays") else ""))
        if not c["engaged"]:
            pieces.append("no counsel engaged")
        headline = " · ".join(pieces) + "."

    return _redact({
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "headline": headline,
        "membership": m,
        "oa": o,
        "gate": g,
        "counsel": c,
        "openDecisions": d,
        "capital": capital(),
        "reversibility": r,
        "unrecorded": u,
        "counts": {
            "openDecisions": len(d["decisions"]),
            "gaps": len(u["gaps"]),
            "unsigned": o.get("unsigned", 0),
            "gatesBlocked": c["gateCounts"]["blocked"],
        },
        "note": ("Every figure here is quoted from the file that owns it and cited back to it — "
                 "equity splits and capital terms are facts with consequences, and a second copy "
                 "in code would be wrong the first time one changed. Where nothing records a "
                 "fact, it reads 'unrecorded' and names where it would live. HQ says Partner; "
                 "the OA's defined term is Principal, and that is deliberately left alone."),
    })


if __name__ == "__main__":
    d = build()
    print("GOVERNANCE — " + d["headline"] + "\n")
    m = d["membership"]
    for x in m["members"]:
        if SHOW_PCT and x.get("pct") is not None:
            print(f"  {x['name']:<20} {x['pct']}%")
        else:
            print(f"  {x['name']:<20} {'— in the OA' if x.get('inOA') else '— NOT in the OA'}")
    print(f"  {m['crmNote']}")
    o = d["oa"]
    print(f"\n  OA {o.get('version')} dated {o.get('dated')} ({o.get('ageDays')}d ago) — "
          f"{o.get('signedNote')}")
    if o.get("review", {}).get("counselQuestions"):
        print(f"  Ray's review: {o['review']['counselQuestions']} counsel questions, "
              f"{o['review'].get('findings')} findings")
    g = d["gate"]
    if g.get("found"):
        print(f"\n  Gate #14 {g['icon']} — regressed {g.get('regressedOn')} "
              f"({g.get('regressedDays')}d ago)")
        print(f"    blocks: {g['blocks'][:100]}")
    print(f"\n  Open blocking decisions ({d['counts']['openDecisions']}):")
    for x in d["openDecisions"]["decisions"]:
        print(f"    {x['id']} — {x['title']}")
    print(f"\n  Unrecorded ({d['counts']['gaps']}):")
    for x in d["unrecorded"]["gaps"]:
        print(f"    · {x['what']}  -> {x['wouldLiveIn']}")
    print(f"\n  Counsel: {d['counsel']['note']}")
    print(f"  Reversibility: {'OPEN — ' if d['reversibility']['open'] else ''}"
          f"{(d['reversibility']['text'] or '')[:160]}")
