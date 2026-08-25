#!/usr/bin/env python3
"""Client trip-wires — the OS tells the client which of THEIR OWN decisions reality just broke.

Every CRM reports what happened. None reports *which of your past decisions is now wrong.* yourco
already does this for itself (`dashboard/tripwires.py`: a settled decision carries the evidence
that would overturn it, checked against live data on every poll). Pointing that at the customer is
the part nobody ships.

The shape: during discovery the client states operating decisions in their own words — "we quote
by hand", "we don't need a second crew", "Saturdays aren't worth staffing". Each gets the
condition that would make it wrong. Their OS already measures the numbers. So the OS can say, in
the month it becomes true:

    In March you decided manual quoting was fine at 12 quotes a week. You are at 31.

ONE CHECK LANGUAGE, NOT TWO. Checks are evaluated by `dashboard.tripwires.evaluate` — the same
tiny grammar, the same refusals (mixed and/or is refused rather than guessed; an unevaluable check
is an ERROR, never silently "did not fire"). A second dialect for clients would drift within a
month and would be the thing that eventually mis-fires at a customer.

FACTS COME FROM THE CLIENT, NOT FROM US. `clients/<name>/facts.json` is the client's own measured
numbers, written by their OS. A trip-wire referencing a fact that isn't there does **not** fire —
it reports an unknown fact, because telling a client their decision expired based on a number
nobody measured is the worst possible failure of this feature.

WHOSE WORDS. The decision text is quoted from the client. yourco never invents a client's
reasoning — the same rule that keeps agents from inventing yourco's own trip-wires.

  python3 runtime/client_tripwires.py --client sample-client
  python3 runtime/client_tripwires.py --all
"""
import os, re, sys, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIENTS = os.path.join(ROOT, "clients")
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

FILE = "client-tripwires.md"
FACTS = "facts.json"

def _field(label):
    """A bullet field that may WRAP onto continuation lines.

    `(.+)$` under re.M stops at the newline, which silently truncated every `Say:` longer than one
    line — the client-facing sentence was being cut mid-clause. Capture runs to the next bullet,
    the next blank line, or the end of the block."""
    return re.compile(r"^[ \t]*[-*][ \t]*\*\*" + label + r":?\*\*[ \t]*(.+?)"
                      r"(?=\n[ \t]*[-*][ \t]*\*\*|\n[ \t]*\n|\Z)", re.M | re.I | re.S)


FIELDS = {
    "decided": _field("They decided"),
    "on": _field("Decided on"),
    "overturn": _field("Overturn if"),
    "check": _field("Check"),
    "says": _field("Say"),
}
ISO = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _clean(s):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", s or "")).strip()


def facts_for(client):
    p = os.path.join(CLIENTS, client, FACTS)
    if not os.path.exists(p):
        return {}, f"no {FACTS} — the client's OS is not yet writing measured numbers"
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except ValueError as e:
        return {}, f"{FACTS} is not valid JSON ({e})"
    out = {k: v for k, v in (d.get("facts") or d).items()
           if isinstance(v, (int, float)) and not isinstance(v, bool)}
    return out, None


def parse(client):
    """-> (rows, error). Each row is one client decision with its overturn condition."""
    p = os.path.join(CLIENTS, client, FILE)
    txt = _read(p)
    if not txt:
        return [], f"no {FILE} in clients/{client}/"
    # Strip fenced blocks first: the "How this works" section documents the format inside a fence,
    # and its illustrative `## <short name>` heading was being parsed as a real client decision.
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    rows = []
    for block in re.split(r"\n(?=##\s)", txt):
        m = re.match(r"##\s+(.+)", block.strip())
        if not m:
            continue
        title = _clean(m.group(1))
        if title.lower().startswith(("how this works", "format", "example format")):
            continue
        f = {k: (rx.search(block).group(1).strip() if rx.search(block) else None)
             for k, rx in FIELDS.items()}
        if not f["decided"] and not f["overturn"]:
            continue
        rows.append({"title": title, **{k: _clean(v) if v else None for k, v in f.items()},
                     "isExample": bool(re.search(r"\bexample\b", block[:400], re.I))})
    return rows, None


def evaluate_client(client, today=None):
    today = today or datetime.date.today()
    rows, err = parse(client)
    if err:
        return {"client": client, "covered": False, "reason": err, "rows": []}
    facts, fact_err = facts_for(client)

    try:
        from tripwires import evaluate as _eval        # one grammar, shared
    except Exception as e:
        return {"client": client, "covered": True, "rows": [],
                "error": f"check engine unavailable: {type(e).__name__}: {e}"}

    out, fired = [], 0
    for r in rows:
        age = None
        if r.get("on") and ISO.search(r["on"]):
            try:
                age = (today - datetime.date.fromisoformat(ISO.search(r["on"]).group(1))).days
            except ValueError:
                pass
        result, error = (None, None)
        if r.get("check") and not re.match(r"^_?\s*none\b", r["check"], re.I):
            result, error = _eval(r["check"], facts, age)
        # An unknown fact must never read as "did not fire" — the client would be told their
        # decision is fine on the strength of a number nobody measured.
        if error and "unknown fact" in error:
            state = "unmeasured"
        elif error:
            state = "check-error"
        elif result is True:
            state, fired = "expired", fired + 1
        elif result is False:
            state = "holding"
        else:
            state = "no check"
        # {factName} placeholders in `Say:` are filled from the client's measured numbers. A
        # placeholder with no fact stays visibly unfilled rather than resolving to a blank —
        # an unfilled slot is obvious in review; a silently-blank one ships to a client.
        msg = r.get("says")
        if msg:
            msg = re.sub(r"\{([A-Za-z][A-Za-z0-9_]*)\}",
                         lambda m: (str(facts[m.group(1)]) if m.group(1) in facts
                                    else "{" + m.group(1) + " — UNMEASURED}"), msg)
        elif state == "expired":
            msg = f"{r['title']} — the condition you set has been met."
        out.append({**r, "ageDays": age, "state": state, "error": error, "message": msg})
    order = {"expired": 0, "unmeasured": 1, "check-error": 2, "no check": 3, "holding": 4}
    out.sort(key=lambda r: order.get(r["state"], 9))
    return {
        "client": client, "covered": True, "rows": out, "facts": facts,
        "factsError": fact_err,
        "counts": {k: sum(1 for r in out if r["state"] == k) for k in order},
        "fired": fired,
        "examplesOnly": bool(out) and all(r["isExample"] for r in out),
        "note": ("Checks run on the client's own measured numbers (facts.json), through the same "
                 "grammar yourco's own trip-wires use. A check naming a fact nobody measures "
                 "reads `unmeasured` and never fires — telling a client their decision expired on "
                 "the strength of an unmeasured number is the worst failure this feature has."),
    }


def build():
    res = []
    for name in sorted(os.listdir(CLIENTS)) if os.path.isdir(CLIENTS) else []:
        if not os.path.isdir(os.path.join(CLIENTS, name)) or name == "_yourco-template":
            continue
        r = evaluate_client(name)
        if r["covered"]:
            res.append(r)
    tmpl = evaluate_client("_yourco-template")
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "clients": res,
        "fired": sum(r.get("fired", 0) for r in res),
        "covered": len(res),
        "template": {"rows": len(tmpl.get("rows") or []), "examplesOnly": tmpl.get("examplesOnly")},
        "zeroState": ("No client carries trip-wires yet — the format and engine exist and the "
                      "template ships worked examples, but nothing here has ever run against a "
                      "real client's numbers. Unexercised, and said plainly.") if not res else None,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--client"); ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    targets = [a.client] if a.client else [
        n for n in sorted(os.listdir(CLIENTS)) if os.path.isdir(os.path.join(CLIENTS, n))]
    any_cov = False
    for c in targets:
        r = evaluate_client(c)
        if not r["covered"]:
            continue
        any_cov = True
        print(f"\n{c}: {len(r['rows'])} client decision(s) watched · {r['fired']} expired"
              + ("   [EXAMPLES ONLY — not real client decisions]" if r["examplesOnly"] else ""))
        if r.get("factsError"):
            print(f"   facts: {r['factsError']}")
        for row in r["rows"]:
            print(f"   [{row['state']:<12}] {row['title']}")
            if row["state"] == "expired":
                print(f"        -> {row['message']}")
            if row.get("error"):
                print(f"        ! {row['error']}")
    if not any_cov:
        print("no client carries client-tripwires.md")
