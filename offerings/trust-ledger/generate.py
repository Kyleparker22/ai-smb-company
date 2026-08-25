#!/usr/bin/env python3
"""yourco — Trust Ledger generator (Frontier #1).

WHY: the Trust Ledger page (prototype/index.html) is the public record of what yourco's AI is
trusted to do and how it earned it. Its truth lives in runtime/autonomy-matrix.md — the rungs
table (current rung + ceiling per action) and the streak ledger (Kolby's weekly counts). The v0
data.json was hand-seeded and drifted within a month; this generator makes the page a *derived*
surface so it can never drift again.

RUNS: at each weekly eval-review (Kolby's Sunday loop) — after the streak ledger is updated in
runtime/autonomy-matrix.md, run `python3 offerings/trust-ledger/generate.py` and the page follows.
Deterministic, stdlib-only, idempotent (no-op when nothing changed; asOf only bumps on real change).

WHAT IT DOES:
  - parses runtime/autonomy-matrix.md: the "Current rungs" table (rung + ceiling per action) and
    the "Streak ledger" table (clean-weeks · real-uses counts per climbing action)
  - translates internal action names to the public phrasing via PUBLIC below — external-surface
    rules apply (no agent names, no internal tool/vendor names on a public page), so the public
    wording is maintained HERE, while rungs/ceilings/streak counts always come from the matrix
  - preserves the hand-curated incident log: prototype/incidents.json is the incidents source of
    record (edit incidents there, never in data.json — regeneration overwrites data.json)
  - writes prototype/data.json in the exact schema index.html reads

USAGE:
  python3 offerings/trust-ledger/generate.py            # regenerate prototype/data.json
  python3 offerings/trust-ledger/generate.py --check    # diff against current file, write nothing
                                                        # exit 0 = in sync · exit 1 = drift/error

FAIL-LOUD RULE: a matrix action with no PUBLIC mapping is an error, not a skip — a public surface
must never auto-receive internal names. Add the mapping, then rerun.
"""
import json, os, re, sys, datetime, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MATRIX = os.path.join(ROOT, "runtime", "autonomy-matrix.md")
PROTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prototype")
DATA = os.path.join(PROTO, "data.json")
INCIDENTS = os.path.join(PROTO, "incidents.json")

# ── Public phrasing (internal → external). Keys = normalized matrix action (text before any
# paren, lowercased). Rung/ceiling/streak counts are parsed from the matrix; wording lives here.
PUBLIC = [
    ("read / glob / grep / websearch", "Read / search (files, web)",
     "Inherently safe — autonomous by design", None),
    ("file write / edit", "File write / edit (version-controlled)",
     "Every change reversible via git", None),
    ("slack post", "Internal channel posts (Slack)",
     "Internal-only surface, reversible", None),
    ("gmail read / search", "Email read / search", "Read-only", None),
    ("calendar read", "Calendar read", "Read-only", None),
    ("calendar create/update", "Calendar create/update (own holds)",
     "Advances on 4 clean weeks · ≥10 real uses",
     "ledger opened {opened}, counting honestly from zero"),
    ("gmail label / archive / mark-read", "Email label / archive / mark-read",
     "Advances on 4 clean weeks · ≥10 real uses",
     "ledger opened {opened}, counting honestly from zero"),
    ("gmail send", "Email send (external)",
     "Drafts only today; climbs on 8 clean weeks · ≥20 clean drafts (draft-vs-outcome record)",
     "counting from ledger open ({opened})"),
    ("instantly batch send", "Outbound campaign send (batch)",
     "Every batch requires a dated PASS from the pre-send eval gate + human click; "
     "climbs on 6 consecutive PASS-gated clean sends",
     "counting starts at launch; nothing sends before it"),
    ("delete / destroy", "Delete / destroy data",
     "Stays gated by design — never advances, regardless of evidence", None),
    ("bash", "Shell / system access (runtime)",
     "Denied by configuration — the load-bearing control; an agent that can shell can bypass "
     "every other control", None),
]

# ── Static editorial copy (page framing, not matrix data) ──
PRINCIPLE = ("Autonomy is earned per action, on eval evidence — never granted. Every action "
             "starts gated (R1) and climbs only on a clean, real-use streak. Any incident holds "
             "or resets the climb. This page is the record.")
RUNGS = {
    "R1": "Gated — a human approves every instance",
    "R2": "Supervised — acts alone, notifies, reversible window",
    "R3": "Autonomous — earned; watchdogs and kill switch remain",
}
NEVER = ("Two action classes never climb, no matter how clean the record: destructive operations "
         "(delete/destroy) and shell access. Evidence can earn autonomy; it cannot earn the right "
         "to be unrecoverable.")
HONESTY = ("This ledger currently records yourco's own operating system — the company runs on its "
           "own agents, and this is their real record, resets and unresolved incidents included. "
           "Client engagements get their own private ledger from day one. Nothing on this page is "
           "a projection, and the streaks start at zero because counting honestly beats "
           "reconstructing a flattering past.")
SOURCE = ("runtime/autonomy-matrix.md (rungs + streak ledger), regenerated by "
          "offerings/trust-ledger/generate.py at each weekly eval-review; incident log "
          "hand-curated in incidents.json")


def norm(action):
    """Normalize a matrix action name to its PUBLIC key: text before any paren, unbolded, lowered."""
    a = action.replace("**", "").split("(")[0]
    return re.sub(r"\s+", " ", a).strip().lower().rstrip(" /")


def table_rows(md, heading):
    """Return the cell-lists of the first pipe table under the given ## heading."""
    m = re.search(rf"^##\s+{re.escape(heading)}.*?$", md, re.M)
    if not m:
        sys.exit(f"ERROR: section '## {heading}…' not found in {MATRIX}")
    rows = []
    for line in md[m.end():].splitlines():
        line = line.strip()
        if rows and not line.startswith("|"):
            break
        if line.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:]  # drop header row


def rung_of(cell):
    m = re.search(r"R([1-3])", cell)
    return f"R{m.group(1)}" if m else None


def parse_streaks(md):
    """Streak ledger → {normalized action: (weeks:int, uses:str)}; uses may carry '≥'."""
    out = {}
    for cells in table_rows(md, "Streak ledger"):
        if len(cells) < 4:
            continue
        raw = cells[3].replace("**", "")
        m = re.match(r"\s*(\d+)\s*·\s*(≥?\s*\d+)", raw)
        if not m:
            sys.exit(f"ERROR: unparseable streak cell for '{cells[0]}': {raw!r}")
        out[norm(cells[0])] = (int(m.group(1)), m.group(2).replace(" ", ""))
    return out


def streak_text(weeks, uses, suffix, opened):
    wk = "wk" if weeks == 1 else "wks"
    use = "use" if uses == "1" else "uses"
    return f"{weeks} clean {wk} · {uses} real {use} — {suffix.format(opened=opened)}"


def build():
    with open(MATRIX, encoding="utf-8") as f:
        md = f.read()
    opened_m = re.search(r"Ledger opened at zero on (\d{4}-\d{2}-\d{2})", md)
    opened = opened_m.group(1) if opened_m else "2026-07-05"
    streaks = parse_streaks(md)
    pub = {k: (name, note, sfx) for k, name, note, sfx in PUBLIC}

    actions, unmapped = [], []
    for cells in table_rows(md, "Current rungs"):
        if len(cells) < 3:
            continue
        key = norm(cells[0])
        if key not in pub:
            unmapped.append(cells[0])
            continue
        name, note, sfx = pub[key]
        streak = None
        if sfx is not None:
            w, u = streaks.get(key, (0, "0"))
            streak = streak_text(w, u, sfx, opened)
        actions.append({"action": name, "rung": rung_of(cells[1]), "ceiling": rung_of(cells[2]),
                        "note": note, "streak": streak})
    if unmapped:
        sys.exit("ERROR: matrix actions with no PUBLIC mapping (add them to generate.py — a "
                 f"public surface must never auto-receive internal names): {unmapped}")
    if not actions:
        sys.exit("ERROR: no actions parsed from the rungs table")

    try:
        with open(INCIDENTS, encoding="utf-8") as f:
            incidents = json.load(f)
    except OSError:
        sys.exit(f"ERROR: {INCIDENTS} missing — the hand-curated incident log is required")

    return {
        "asOf": datetime.date.today().isoformat(),
        "source": SOURCE,
        "principle": PRINCIPLE,
        "rungs": RUNGS,
        "actions": actions,
        "incidents": incidents,
        "neverAdvances": NEVER,
        "honesty": HONESTY,
    }


def main():
    check = "--check" in sys.argv[1:]
    new = build()
    old = None
    if os.path.exists(DATA):
        with open(DATA, encoding="utf-8") as f:
            old = json.load(f)

    # asOf is generation metadata — ignore it when deciding whether anything really changed,
    # so reruns with an unchanged matrix are no-ops and asOf reflects the data's real vintage.
    same = old is not None and {k: v for k, v in old.items() if k != "asOf"} == \
                               {k: v for k, v in new.items() if k != "asOf"}
    if same:
        print(f"in sync — {os.path.relpath(DATA, ROOT)} already matches the matrix (asOf {old['asOf']})")
        return 0

    if check:
        a = json.dumps(old, ensure_ascii=False, indent=2).splitlines() if old else []
        b = json.dumps(new, ensure_ascii=False, indent=2).splitlines()
        print("\n".join(difflib.unified_diff(a, b, "data.json (current)", "data.json (from matrix)", lineterm="")))
        print("\nDRIFT: data.json does not match runtime/autonomy-matrix.md — run without --check to fix")
        return 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {os.path.relpath(DATA, ROOT)} — {len(new['actions'])} actions, "
          f"{len(new['incidents'])} incidents (asOf {new['asOf']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
