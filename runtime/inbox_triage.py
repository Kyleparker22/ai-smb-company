#!/usr/bin/env python3
"""inbox_triage — inventory what is in ./inbox and PROPOSE where each item belongs.

    python3 runtime/inbox_triage.py           # write a dated proposal to loops/_inbox/
    python3 runtime/inbox_triage.py --dry     # print it, write nothing
    python3 runtime/inbox_triage.py --json

WHY THIS EXISTS
The repo has 20 top-level destinations and no place to put something before you know which one it is.
That means capture requires judgment, so things do not get captured. `inbox/_README.md` carries the
evidence, including a client PDF that has been sitting in ~/Downloads instead of the workspace.

WHY IT PROPOSES AND NEVER FILES
`decisions/`, `learnings/`, `rejections/` and `offerings/` mean genuinely different things, and
`00_README.md` opens by warning that confusing them is how you "treat a prototype as a product." An
auto-filer would manufacture that confusion at scale, silently. So this reports and suggests; a human
moves. Same posture as vacancies.py and the failure-trace skill patches: propose, never apply.

WHY THE SUGGESTIONS ARE DETERMINISTIC
Routing is judgment, but the SIGNALS are mechanical: a client's name in the filename, an extension, a
keyword that only appears in one domain. So this computes the signals and shows its work, and when the
signal is weak it prints `undetermined` rather than inventing a confident destination —
`learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md` is explicit that wrapping
deterministic work in a model call costs tokens and is less reliable. A wrong-but-confident route here
would be worse than no route, because the whole point is that the human is still deciding.
"""
import os, re, sys, json, time, hashlib, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(ROOT, "inbox")
OUT = os.path.join(ROOT, "loops", "_inbox")
TEXT_EXT = (".md", ".txt", ".markdown")
STALE_DAYS = 14
_HASHES = {}

# (destination, why, matcher). Order matters — first hit wins, most specific first.
def _clients():
    d = os.path.join(ROOT, "clients")
    return [c for c in os.listdir(d) if os.path.isdir(os.path.join(d, c)) and not c.startswith("_")] \
        if os.path.isdir(d) else []


def _repo_hashes():
    """md5 -> first repo path, for every file OUTSIDE inbox/. Built once per run.

    Added 2026-08-24 after the tool's first real use proposed `clients/sample-client/` for a PDF that was
    already filed there, byte-identical, under a better name. Proposing a move for a file that is
    already home is worse than saying nothing: acted on, it creates the duplicate it should prevent.
    Cheap to rule out — an md5 of every tracked file costs well under a second at this repo's size.
    """
    seen = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "node_modules", "__pycache__", "inbox", ".venv", "venv"}]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) > 60_000_000:
                    continue
                with open(fp, "rb") as fh:
                    h = hashlib.md5(fh.read()).hexdigest()
            except OSError:
                continue
            seen.setdefault(h, os.path.relpath(fp, ROOT))
    return seen


def suggest(name, body):
    """(destination, why) — or (None, why-it-is-undetermined). Never guesses."""
    low = (name + " " + body[:4000]).lower()
    # Normalise separators before comparing: a file arriving from a download or an export is as likely
    # to be `southern_cut_workflow.pdf` as `sample-client-workflow.pdf`, and treating those as different
    # names is how a CLIENT artifact — the highest-value thing in here — falls through to undetermined.
    def _norm(t):
        return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
    n_name, n_body = _norm(name), _norm(body[:4000])
    for c in _clients():
        stem = _norm(c)
        if stem and (stem in n_name or stem in n_body):
            where = "filename" if stem in n_name else "contents"
            return f"clients/{c}/", f"the {where} names the client '{c}'"
    pairs = [
        ("decisions/",  "reads as a settled call ('we decided/chose/locked')",
         r"\b(we decided|decision:|we chose|locked in|going with)\b"),
        ("rejections/", "reads as something ruled out, which is the anti-library's job",
         r"\b(we are not doing|ruled out|rejected|decided against|not pursuing)\b"),
        ("learnings/",  "reads as an observed pattern rather than a choice",
         r"\b(pattern:|we keep|every time we|lesson|kept happening|next time)\b"),
        ("offerings/",  "reads as a described-but-unbuilt offering",
         r"\b(spec|offering|vertical|productiz)\w*\b"),
        ("finance/",    "financial subject matter",
         r"\b(invoice|runway|revenue|p&l|tax|ein|expense)\b"),
    ]
    for dest, why, rx in pairs:
        if re.search(rx, low):
            return dest, why
    return None, "no distinctive signal in the filename or the first lines"


def scan():
    if not os.path.isdir(INBOX):
        return []
    now = time.time()
    global _HASHES
    _HASHES = _repo_hashes()
    items = []
    for fn in sorted(os.listdir(INBOX)):
        if fn.startswith(".") or fn == "_README.md":
            continue
        fp = os.path.join(INBOX, fn)
        if not os.path.isfile(fp):
            continue
        st = os.stat(fp)
        body, readable = "", fn.lower().endswith(TEXT_EXT)
        if readable:
            try:
                body = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                body = ""
        try:
            with open(fp, "rb") as fh:
                _h = hashlib.md5(fh.read()).hexdigest()
        except OSError:
            _h = None
        _dupe = _HASHES.get(_h) if _h else None
        if _dupe:
            dest, why = None, f"ALREADY IN THE REPO, byte-identical: `{_dupe}`"
        else:
            dest, why = suggest(fn, body)
        snippet = ""
        if body:
            for ln in body.splitlines():
                if len(ln.strip()) > 30:
                    snippet = re.sub(r"\s+", " ", ln.strip())[:180]
                    break
        items.append({
            "file": fn,
            "age_days": int((now - st.st_mtime) // 86400),
            "kb": max(1, st.st_size // 1024),
            "readable": readable,
            "snippet": snippet,
            "suggested": dest,
            "why": why,
            "stale": int((now - st.st_mtime) // 86400) >= STALE_DAYS,
            "dupe": bool(_dupe),
        })
    return items


def render(items):
    from datetime import date
    L = [f"# Inbox triage — {date.today().isoformat()}", ""]
    if not items:
        L += ["Inbox is empty. Nothing to route.", "",
              "*That is a real state, not a skipped run.*"]
        return "\n".join(L)
    stale = [i for i in items if i["stale"]]
    L += [f"**{len(items)} item(s) waiting.** "
          + (f"⚠️ **{len(stale)} past {STALE_DAYS} days** — an item that will not route usually needs a "
             "decision, not a folder." if stale else "None stale."), "",
          "Nothing below has been moved. These are proposals; you commit them.", ""]
    for i in items:
        head = f"## {i['file']}"
        if i["stale"]:
            head += "  ⚠️"
        L.append(head)
        L.append(f"- {i['age_days']}d old · {i['kb']} KB"
                 + ("" if i["readable"] else " · binary (not read — routed on filename only)"))
        if i["snippet"]:
            L.append(f"- > {i['snippet']}")
        if i["suggested"]:
            L.append(f"- **Proposed: `{i['suggested']}`** — {i['why']}")
        elif i.get("dupe"):
            L.append(f"- **Duplicate — already filed.** {i['why']}")
            L.append("  Nothing to route. Delete the inbox copy once you have confirmed the filed one "
                     "is the version you want to keep.")
        else:
            L.append(f"- **Undetermined** — {i['why']}. "
                     "Left here deliberately rather than filed somewhere plausible.")
        L.append("")
    L += ["---", "",
          "*Proposals only — `runtime/inbox_triage.py` never moves a file. "
          "Routing between `decisions/`, `learnings/`, `rejections/` and `offerings/` is judgment; "
          "see `inbox/_README.md`.*"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry", action="store_true", help="print, write nothing")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    items = scan()
    if a.json:
        print(json.dumps(items, indent=2)); return
    text = render(items)
    if a.dry:
        print(text); return
    os.makedirs(OUT, exist_ok=True)
    from datetime import date
    fp = os.path.join(OUT, f"{date.today().isoformat()}.md")
    open(fp, "w", encoding="utf-8").write(text + "\n")
    print(text)
    print(f"\n→ {os.path.relpath(fp, ROOT)}")


if __name__ == "__main__":
    main()
