#!/usr/bin/env python3
"""Trigger-scoped Step 0 — load the learnings that fit THIS run, not the ones filed nearby.

THE PROBLEM THIS FIXES.  `runtime/prompts/_loop-contract.md` Step 0 says: read the last ~5
entries in this loop's `learnings/` domain. Domain is a *filing* decision made when the entry
was written; relevance is a *retrieval* decision made when a run starts. They are not the same
thing, and the gap is the known failure — the right learning exists, in the wrong folder, and
the run that needed it never saw it. Three real examples in the current store:

  • `qa-eval/2026-06-21_write-flags-as-checklists.md` is about how to WRITE a learning. Every
    loop that writes one needs it; only Kolby's domain loads it.
  • `ops/2026-08-09_inference-only-where-judgment-is-needed.md` says "everything deterministic
    is code". It is addressed to "every agent authoring a new runtime loop" — who are filed
    under nine different domains.
  • `sales-copy/2026-08-09_name-the-number-...md` ends with "any agent authoring a loop prompt".

Devin's Knowledge Base solves this by attaching a TRIGGER to each knowledge item rather than a
folder. This is that, in our format, deterministic (no model call — see the inference-only
learning above), and additive: domain+recency still runs as the fallback.

THE FORMAT.  One optional line in an entry, alongside `Audience:`:

    Triggers: writing a learning, authoring a loop prompt, agent:kolby, loop:eval-review

  A trigger is either a **phrase** (all of its words must appear in the run's context) or a
  **typed** trigger — `agent:<name>`, `loop:<name>`, `skill:<name>`, `domain:<name>`,
  `path:<substring>`, or the literal `always`. Triggers are OR'd; words inside one phrase
  are AND'd. Deliberately dumb: substring and token matching, no embeddings, no model.

  A colon alone does **not** make a trigger typed — only one of the five `KINDS` prefixes does.
  `file://`, `https://`, `3:1` and `note: x` are phrases, and are matched as phrases. (Until
  2026-08-09 any colon meant "typed", so `file://` in the preview-URL entry parsed as kind
  `file` and never fired — a trigger that looked present and did nothing. `--check` still
  lists colon-bearing phrases so a genuine typo like `agnet:kemba` stays visible.)

FIVE HONESTY RULES (each is a test in runtime/test_agentops.py):

1. **An entry without triggers is never dropped.** It falls back to domain+recency exactly as
   today. The output states how many entries are running on fallback, so an incomplete backfill
   is *visible* rather than quietly shrinking what a run reads.
2. **Nothing is silently truncated.** Results are capped, and the count above the cap is
   reported as "below the line", with the cap that produced it.
3. **Stale is flagged, not hidden.** An entry past STALE_DAYS that is not marked `[absorbed]`
   is returned with `stale: true`. Memory staleness is the open problem in the agent-memory
   literature; the answer here is not deletion, it is labelling.
4. **A zero-match run says so.** Empty is a valid result and is reported as empty with the
   context that produced it — never padded with loosely-related entries to look useful.
5. **Link expansion is additive, labelled, and separately capped.** See below.

LINK EXPANSION (added 2026-08-09).  Triggers answer *what should load*. `[[wikilinks]]` answer a
different question — *what else is implied once something loads* — and the store already carries
them, because this repo is an Obsidian vault and the learnings format asks for them. Obsidian
traverses those links for the human (graph + backlinks); nothing traversed them for the agent.
This is that second half, and it is deliberately conservative:

  • **One hop.** `LINK_HOPS = 1`. Two hops pulls the neighbourhood, then the graph; a Step 0 that
    returns the graph is a Step 0 nobody reads.
  • **Never displaces a direct match.** Expansion runs *after* `matched` is scored and capped, and
    linked entries are returned under their own key with their own budget (`MAX_LINKED`). A link
    can add context; it can never push out a trigger hit.
  • **Always labelled.** Every linked entry carries `linked_from` — the entry that pulled it in —
    so a run can tell "this fired for me" from "this is adjacent to something that fired".
  • **A link that resolves to nothing is reported, never ignored.** That is live regression
    detection: on 2026-08-09, 8 of 13 links in the store were dangling because the format says
    link by slug while files are named `YYYY-MM-DD_slug.md`. Silence is how that lasted.

CLI
  python3 runtime/learning_triggers.py --loop content --agent katie --about "linkedin stat"
  python3 runtime/learning_triggers.py --loop eval-review --domain qa-eval --json
  python3 runtime/learning_triggers.py --check        # trigger-coverage + link health
  python3 runtime/learning_triggers.py --loop x --no-links   # expansion off
"""
import os, re, sys, json, argparse, datetime

ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEARNINGS = os.path.join(ROOT, "learnings")

MAX_RESULTS = 8      # a Step 0 that returns 30 entries is a Step 0 nobody reads
RECENT_DAYS = 30     # the fallback window the loop contract already specifies
FALLBACK_N = 5       # "last ~5 in the domain" — unchanged, so nothing regresses
STALE_DAYS = 120     # past this and not [absorbed] → flagged for review, never dropped
LINK_HOPS = 1        # one hop. Two pulls the neighbourhood; three pulls the graph.
MAX_LINKED = 4       # link expansion gets its own budget so it can't crowd out matches

KINDS = {"agent", "loop", "domain", "skill", "path"}   # the typed-trigger prefixes

STOP = {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "it", "that",
        "this", "with", "as", "at", "by", "be", "not", "from", "any", "when"}


def _tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP and len(w) > 1}


def _links(body):
    """Wikilink targets in an entry. `[[name|alias]]` and `[[name#heading]]` both resolve to
    `name` — the alias and the heading are display concerns, not the link target."""
    return [m.strip() for m in re.findall(r"\[\[([^\]|#]+)", body or "") if m.strip()]


def _parse_date(name, body):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(name))
    if not m:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", body[:200])
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _field(body, label):
    """Pull a `Label: ...` line, including its wrapped continuation lines."""
    # `**Label:**` is tolerated as well as `Label:`. One entry was written bold and its triggers
    # were invisible to every run for five days while --check reported it as simply "no triggers" —
    # a learning that exists but cannot be retrieved is worse than one nobody wrote, because the
    # coverage number says 98% and everyone relaxes.
    m = re.search(rf"^\*{{0,2}}{label}:\*{{0,2}}\s*(.+?)(?=\n\*{{0,2}}[A-Z][a-zA-Z-]+:|\n\n|\Z)",
                  body, re.M | re.S)
    return " ".join(m.group(1).split()) if m else ""


def _title(body):
    """First real line. Some entries are memory-style with YAML frontmatter, so the block is
    skipped — otherwise the title renders as 'name: <slug>', which is the filename twice."""
    lines = body.splitlines()
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                lines = lines[i + 1:]
                break
    for line in lines:
        line = line.strip().lstrip("#").strip()
        if line and line != "---":
            return line[:160]
    return ""


def load_entries(root=LEARNINGS):
    """Every learning on disk, parsed. Unreadable files are COUNTED, not skipped silently."""
    entries, unreadable = [], []
    if not os.path.isdir(root):
        return entries, unreadable
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith(".md") or fn.startswith("_") or fn == "REVIEW-LOG.md":
                continue
            path = os.path.join(dirpath, fn)
            try:
                body = open(path, encoding="utf-8").read()
            except OSError as e:
                unreadable.append({"path": os.path.relpath(path, ROOT), "error": str(e)})
                continue
            domain = os.path.relpath(dirpath, root).split(os.sep)[0]
            title = _title(body)
            trig_raw = _field(body, "Triggers")
            triggers = [t.strip().lower() for t in trig_raw.split(",") if t.strip()]
            entries.append({
                "path": os.path.relpath(path, ROOT),
                "stem": os.path.splitext(fn)[0],
                "links": _links(body),
                "domain": domain,
                "date": _parse_date(fn, body),
                "title": title,
                "absorbed": "[absorbed]" in title.lower(),
                "audience": _field(body, "Audience"),
                "triggers": triggers,
                "haystack": _tokens(title + " " + _field(body, "Pattern") + " " +
                                    _field(body, "Implication") + " " + _field(body, "Audience")),
            })
    return entries, unreadable


def _trigger_hit(trig, ctx):
    """Does one trigger fire against the run context? Typed triggers match their field;
    a bare phrase matches when EVERY one of its words is present in the context."""
    if trig == "always":
        return True
    kind, sep, val = trig.partition(":")
    if sep and kind.strip() in KINDS:
        kind, val = kind.strip(), val.strip()
        if kind == "agent":
            return val == (ctx.get("agent") or "").lower()
        if kind == "loop":
            return val == (ctx.get("loop") or "").lower()
        if kind == "domain":
            return val == (ctx.get("domain") or "").lower()
        if kind == "skill":
            return val in [s.lower() for s in ctx.get("skills", [])]
        if kind == "path":
            return any(val in p.lower() for p in ctx.get("paths", []))
    # A colon does NOT imply a typed trigger. `file://`, `https://`, `3:1` and `note: x` are
    # phrases an author meant literally; before 2026-08-09 they were parsed as typed triggers
    # with an unknown kind and silently never fired. Anything whose prefix isn't a real KIND
    # falls through to phrase matching, which is what was written and what was meant.
    words = _tokens(trig)
    return bool(words) and words <= ctx["_ctx_tokens"]


def select(loop=None, agent=None, domain=None, about="", paths=(), skills=(), today=None,
           max_results=MAX_RESULTS, root=LEARNINGS, follow_links=True, max_linked=MAX_LINKED):
    """The Step 0 read. Returns matches + everything a caller needs to report honestly."""
    today = today or datetime.date.today()
    entries, unreadable = load_entries(root)
    ctx = {"loop": loop, "agent": agent, "domain": domain, "paths": list(paths),
           "skills": list(skills)}
    ctx["_ctx_tokens"] = _tokens(" ".join(filter(None, [loop, agent, domain, about,
                                                        " ".join(paths), " ".join(skills)])))

    absorbed = sum(1 for e in entries if e["absorbed"])
    scored, no_triggers = [], 0
    for e in entries:
        if e["absorbed"]:
            continue
        if not e["triggers"]:
            no_triggers += 1
        age = (today - e["date"]).days if e["date"] else 9999
        hits = [t for t in e["triggers"] if _trigger_hit(t, ctx)]
        why, score = None, 0
        if hits:
            score, why = 100 + len(hits), "trigger: " + "; ".join(hits[:3])
        elif agent and agent.lower() in e["audience"].lower():
            score, why = 60, "audience names " + agent
        elif domain and e["domain"] == domain and age <= RECENT_DAYS:
            score, why = 30, f"fallback: {domain} domain, {age}d old"
        if score:
            scored.append({**{k: v for k, v in e.items() if k != "haystack"},
                           "score": score, "why": why, "age_days": age,
                           "stale": age > STALE_DAYS,
                           "date": e["date"].isoformat() if e["date"] else None})

    # Domain fallback floor: if triggers produced nothing, the contract's original behaviour
    # still runs, so this change can only ADD context, never remove it.
    if not scored and domain:
        pool = sorted([e for e in entries if e["domain"] == domain and not e["absorbed"]],
                      key=lambda e: e["date"] or datetime.date.min, reverse=True)[:FALLBACK_N]
        for e in pool:
            age = (today - e["date"]).days if e["date"] else 9999
            scored.append({**{k: v for k, v in e.items() if k != "haystack"},
                           "score": 10, "why": f"fallback floor: last {FALLBACK_N} in {domain}",
                           "age_days": age, "stale": age > STALE_DAYS,
                           "date": e["date"].isoformat() if e["date"] else None})

    scored.sort(key=lambda r: (-r["score"], r["age_days"]))
    shown, below = scored[:max_results], max(0, len(scored) - max_results)

    # Rule 5 — expansion runs AFTER the cap, into its own bucket. `matched` is untouched by it,
    # so every guarantee above still holds exactly as it did before links existed.
    linked, linked_below, unresolved = ([], 0, [])
    if follow_links and shown:
        linked, linked_below, unresolved = expand_links(shown, entries, max_linked, today)

    return {
        "context": {k: v for k, v in ctx.items() if not k.startswith("_")} | {"about": about},
        "matched": shown,
        "linked": linked,
        "linked_below_the_line": linked_below,
        "linked_cap": max_linked if follow_links else 0,
        "unresolved_links": unresolved,
        "below_the_line": below,
        "cap": max_results,
        "total_entries": len(entries),
        "without_triggers": no_triggers,
        "absorbed_excluded": absorbed,
        "unreadable": unreadable,
        "empty_reason": None if shown else
            "No learning matched this context, and no domain fallback applied. "
            "That is a real result — do not substitute loosely-related entries.",
    }


def link_index(live):
    """Resolve `[[wikilink]]` -> entry. Used by BOTH the retrieval hop and `--check`.

    Shared on purpose. The two paths each built their own stem set, so a fix to one silently left
    the other reporting the opposite — which is how five links that pointed at real files were
    reported as rot on 2026-08-24 while retrieval followed them fine.

    Indexes the full stem AND the slug after the date prefix, because a human writes
    `[[loop-liveness-blindspot]]`, not `[[2026-07-28_loop-liveness-blindspot]]` — and because a
    date-bearing link breaks on every re-date, which has already happened once (four entries moved
    08-09 -> 08-16). An ambiguous slug is deliberately left OUT: when two entries share one,
    reporting the link unresolved beats guessing which was meant.
    """
    idx = {e["stem"]: e for e in live}
    slugs = {}
    for e in live:
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", e["stem"])
        if slug != e["stem"]:
            slugs.setdefault(slug, []).append(e)
    for slug, es in slugs.items():
        if len(es) == 1 and slug not in idx:
            idx[slug] = es[0]
    return idx


def expand_links(shown, entries, max_linked=MAX_LINKED, today=None):
    """One hop out from the matched set. Returns (linked_rows, unresolved).

    Additive by construction: it reads `shown` and never modifies it, so the worst case is that
    it adds nothing. Order is deterministic — source order, then link order as written — because
    a Step 0 that returns different context on identical input is not a Step 0 you can debug.
    """
    today = today or datetime.date.today()
    by_stem = link_index([e for e in entries if not e["absorbed"]])
    already = {m["path"] for m in shown}
    linked, unresolved, seen = [], [], set()

    for src in shown:
        src_entry = by_stem.get(src.get("stem"))
        for target in (src_entry or {}).get("links", []):
            tgt = by_stem.get(target)
            if not tgt:
                # May point outside learnings/ (a decision, a process doc) — Obsidian resolves
                # those, this module only indexes learnings, so it is stated as such, not as an error.
                unresolved.append({"link": target, "in": src["path"]})
                continue
            if tgt["path"] in already or tgt["path"] in seen:
                continue
            seen.add(tgt["path"])
            age = (today - tgt["date"]).days if tgt["date"] else 9999
            linked.append({**{k: v for k, v in tgt.items() if k not in ("haystack", "links")},
                           "score": 0, "age_days": age, "stale": age > STALE_DAYS,
                           "date": tgt["date"].isoformat() if tgt["date"] else None,
                           "linked_from": src["path"],
                           "why": f"linked from {os.path.basename(src['path'])}"})

    return linked[:max_linked], max(0, len(linked) - max_linked), unresolved


def coverage(root=LEARNINGS, today=None):
    """--check: how much of the store is actually trigger-scoped, and what looks wrong."""
    today = today or datetime.date.today()
    entries, unreadable = load_entries(root)
    live = [e for e in entries if not e["absorbed"]]
    # Colon-bearing triggers that are NOT typed. These now work (as phrases) — they are listed
    # so a real typo (`agnet:kemba`) is still visible, not because they are broken.
    unknown = []
    for e in live:
        for t in e["triggers"]:
            if ":" in t and t.split(":", 1)[0].strip() not in KINDS:
                unknown.append({"path": e["path"], "trigger": t})
    stale = [{"path": e["path"], "age_days": (today - e["date"]).days}
             for e in live if e["date"] and (today - e["date"]).days > STALE_DAYS]
    with_t = [e for e in live if e["triggers"]]
    # Link health. All 13 links in the store resolved as of 2026-08-09; this is what keeps that
    # true — a link naming no learning is surfaced by name rather than failing silently.
    resolvable = link_index(live)
    unresolved = [{"link": t, "in": e["path"]}
                  for e in live for t in e["links"] if t not in resolvable]
    return {
        "links_total": sum(len(e["links"]) for e in live),
        "links_unresolved": unresolved,
        "entries_with_links": sum(1 for e in live if e["links"]),
        "total": len(entries), "live": len(live), "absorbed": len(entries) - len(live),
        "with_triggers": len(with_t),
        "without_triggers": [e["path"] for e in live if not e["triggers"]],
        "coverage_pct": round(100 * len(with_t) / len(live), 1) if live else None,
        "unknown_trigger_kinds": unknown,
        "stale_unabsorbed": sorted(stale, key=lambda s: -s["age_days"]),
        "unreadable": unreadable,
    }


def render(res):
    out = [f"Step 0 — learnings for {res['context'].get('loop') or 'this run'}"
           f"  (agent={res['context'].get('agent') or '—'}, domain={res['context'].get('domain') or '—'})", ""]
    if not res["matched"]:
        out += [res["empty_reason"], ""]
    for m in res["matched"]:
        flag = "  ⚠ STALE" if m["stale"] else ""
        out.append(f"  • {m['title']}{flag}")
        out.append(f"      {m['path']}  [{m['why']}]")
    for m in res.get("linked", []):
        flag = "  ⚠ STALE" if m["stale"] else ""
        out.append(f"  ↳ {m['title']}{flag}")
        out.append(f"      {m['path']}  [{m['why']}]")
    out.append("")
    if res.get("linked_below_the_line"):
        out.append(f"  {res['linked_below_the_line']} more linked entries sit below the link cap "
                   f"of {res['linked_cap']}.")
    if res.get("unresolved_links"):
        out.append("  unresolved links (no learning by that name — may point outside learnings/): "
                   + ", ".join(f"[[{u['link']}]] in {os.path.basename(u['in'])}"
                               for u in res["unresolved_links"][:5]))
    if res["below_the_line"]:
        out.append(f"  {res['below_the_line']} more matched but sit below the cap of {res['cap']}.")
    if res["without_triggers"]:
        out.append(f"  {res['without_triggers']} of {res['total_entries']} entries carry no Triggers: "
                   f"line and are reachable only by domain fallback.")
    if res["unreadable"]:
        out.append(f"  {len(res['unreadable'])} entries could not be read — not silently skipped: "
                   + ", ".join(u["path"] for u in res["unreadable"][:5]))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Trigger-scoped Step 0 retrieval for learnings.")
    ap.add_argument("--loop"); ap.add_argument("--agent"); ap.add_argument("--domain")
    ap.add_argument("--about", default="", help="free text: what this run is about")
    ap.add_argument("--path", action="append", default=[], help="file path this run touches")
    ap.add_argument("--skill", action="append", default=[], help="skill this run invokes")
    ap.add_argument("--max", type=int, default=MAX_RESULTS)
    ap.add_argument("--no-links", action="store_true", help="disable one-hop link expansion")
    ap.add_argument("--check", action="store_true", help="trigger-coverage + link health")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.check:
        c = coverage()
        if a.json:
            print(json.dumps(c, indent=2)); return
        print(f"Trigger coverage: {c['with_triggers']}/{c['live']} live entries "
              f"({c['coverage_pct']}%)   [{c['absorbed']} absorbed, excluded]")
        for p in c["without_triggers"]:
            print(f"  no triggers: {p}")
        for u in c["unknown_trigger_kinds"]:
            print(f"  note: '{u['trigger']}' has a colon but no typed kind — matched as a "
                  f"phrase. Check it isn't a typo.  ({u['path']})")
        for s in c["stale_unabsorbed"]:
            print(f"  stale {s['age_days']}d, not marked [absorbed]: {s['path']}")
        print(f"Links: {c['links_total']} across {c['entries_with_links']} entries, "
              f"{len(c['links_unresolved'])} unresolved")
        for u in c["links_unresolved"]:
            print(f"  UNRESOLVED [[{u['link']}]]  ({u['in']})")
        return

    res = select(loop=a.loop, agent=a.agent, domain=a.domain, about=a.about,
                 paths=a.path, skills=a.skill, max_results=a.max, follow_links=not a.no_links)
    print(json.dumps(res, indent=2) if a.json else render(res))


if __name__ == "__main__":
    main()
