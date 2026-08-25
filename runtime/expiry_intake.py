#!/usr/bin/env python3
"""Expiry — the belief check that comes back.

Every lead tool on the internet is one-shot: answer, get scored, receive a PDF, done. The visitor
learns something for four minutes and the vendor learns an email address. This is the opposite
shape. A business owner writes down three things their business runs on and how they'd know if each
stopped being true; the page sorts them into checkable and **unmeasured** on the spot, free and
ungated. This module is the half that makes it worth doing: it remembers, and on the schedule they
chose it comes back and asks whether their own sentence is still true.

That recurring, welcome, entirely non-salesy reason to be in a founder's inbox is the thing every
outbound sequence is trying and failing to buy — and it works precisely because the email contains
nothing except their words and one question.

THE ENGINE IS NOT NEW; THE TARGET IS. `runtime/client_tripwires.py` already watches a *client's*
own decisions for expiry and reports `unmeasured` for a fact nobody measures. This points the same
instrument at somebody who isn't a client, which is the part nobody ships.

FOUR RULES
1. **It drafts; it never sends.** `the Founder sends; agents draft` (CLAUDE.md) is not suspended because
   the email is friendly and the person opted in. `--due` writes copy to `loops/_expiry/` for the
   normal send path. There is no transport in this file, deliberately.
2. **Their words, never ours.** The email quotes the belief verbatim. We do not paraphrase a
   stranger's sentence back at them, and we never re-state what we think they meant.
3. **No judgement is stored.** We keep the belief, how they said they'd know, the email, and the
   interval. We do not score the business, infer its size, or enrich the record — the promise on
   the page is that this isn't used to build a profile, and the schema is where that is kept.
4. **Unsubscribe is a field, not a negotiation.** `active: false` ends it permanently; a suppressed
   row is never re-armed by a later submission from the same address.

STAGED: nothing serves until launch (`processes/launch-gate.md`). At launch, `--serve` runs behind
the site host's reverse proxy alongside `runtime/site_intake.py`, and the unit gets registered in
`runtime/agent-registry.json` the same day it is enabled.

  python3 runtime/expiry_intake.py --self-check          # dry-run a sample submission
  python3 runtime/expiry_intake.py --self-check --commit # write the sample to the store
  python3 runtime/expiry_intake.py --due                 # draft check-backs that are due
  python3 runtime/expiry_intake.py --serve [port]        # launch-gated HTTP mode (default 8808)
"""
import os, re, sys, json, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUTDIR = os.path.join(REPO, "loops", "_expiry")
STORE = os.path.join(OUTDIR, "beliefs.jsonl")

MAXLEN = 200
MAX_BELIEFS = 5
VALID_HOW = {"number", "told", "notice", "no"}
VALID_INTERVALS = {30, 90, 180}

# How they said they'd know -> whether that counts as measurement. Only a number someone actually
# looks at does. "Someone would tell me" and "I'd notice" feel like verification and are not; that
# distinction is the entire product and it is not softened here to be polite.
MEASURED = {"number"}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]+$")


def _s(v, n=MAXLEN):
    return re.sub(r"\s+", " ", str(v or "")).strip()[:n]


def _now():
    return datetime.datetime.now()


# ── store ───────────────────────────────────────────────────────────────────────────────────
def _read_all():
    rows, bad = [], 0
    if not os.path.exists(STORE):
        return rows, bad
    with open(STORE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                bad += 1          # counted, never silently dropped
    return rows, bad


def _append(row):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(STORE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _suppressed():
    rows, _ = _read_all()
    return {r["email"] for r in rows if r.get("kind") == "unsubscribe"}


def latest_by_email():
    """The live subscription per address — last write wins, suppressions removed."""
    rows, _ = _read_all()
    supp = _suppressed()
    out = {}
    for r in rows:
        if r.get("kind") != "belief-set":
            continue
        if r["email"] in supp:
            out.pop(r["email"], None)
            continue
        out[r["email"]] = r
    return out


# ── intake ──────────────────────────────────────────────────────────────────────────────────
def handle(payload, commit=False):
    email = _s(payload.get("email"), 254).lower()
    if not EMAIL_RE.match(email):
        return {"ok": False, "error": "that doesn't look like an email address"}
    if email in _suppressed():
        # Rule 4: a suppressed address stays suppressed. Accepting this silently would be worse —
        # the person would expect mail that will never come.
        return {"ok": False, "error": "this address previously unsubscribed and will not be re-armed"}

    try:
        interval = int(payload.get("interval_days") or 90)
    except (TypeError, ValueError):
        interval = 90
    if interval not in VALID_INTERVALS:
        interval = 90

    beliefs = []
    for b in (payload.get("beliefs") or [])[:MAX_BELIEFS]:
        text, how = _s((b or {}).get("text")), _s((b or {}).get("how"), 12)
        if not text or how not in VALID_HOW:
            continue                      # a belief with no stated check is not a belief we can ask about
        beliefs.append({"text": text, "how": how, "measured": how in MEASURED})
    if not beliefs:
        return {"ok": False, "error": "no belief carried both a sentence and a stated way of knowing"}

    now = _now()
    row = {
        "kind": "belief-set",
        "email": email,
        "capturedAt": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "capturedOn": now.strftime("%Y-%m-%d"),
        "intervalDays": interval,
        "dueOn": (now.date() + datetime.timedelta(days=interval)).isoformat(),
        "beliefs": beliefs,
        "unmeasured": sum(1 for b in beliefs if not b["measured"]),
        "source": _s(payload.get("source"), 60) or "expiry page",
        "lastAskedOn": None,
        # Rule 3: nothing is stored beyond this. No score, no inferred industry, no enrichment.
    }
    if commit:
        _append(row)
    return {"ok": True, "stored": commit, "row": row}


def unsubscribe(email, commit=False):
    email = _s(email, 254).lower()
    row = {"kind": "unsubscribe", "email": email,
           "at": _now().strftime("%Y-%m-%dT%H:%M:%S")}
    if commit:
        _append(row)
    return {"ok": True, "stored": commit, "row": row}


# ── the check-back (drafts only — rule 1) ───────────────────────────────────────────────────
def draft(row, today=None):
    """One email. Their sentences, one question, an unsubscribe line. Nothing else."""
    today = today or datetime.date.today()
    since = (today - datetime.date.fromisoformat(row["capturedOn"])).days
    lines = [f"Subject: Still true?", "",
             f"You wrote these down {since} days ago. One question each: are they still true?", ""]
    for b in row["beliefs"]:
        lines.append(f'  "{b["text"]}"')                       # rule 2 — verbatim
        if not b["measured"]:
            lines.append("   (you said nothing would tell you if this changed)")
        lines.append("")
    unmeasured = [b for b in row["beliefs"] if not b["measured"]]
    if unmeasured:
        lines.append(f"{len(unmeasured)} of these you couldn't check then. If that's still the case, "
                     f"the honest answer to the question above is \"I don't know\" — which is its own "
                     f"answer, and the useful one.")
    else:
        lines.append("You could check all of these. Worth two minutes to actually look.")
    lines += ["", "Reply if you want to talk about it. Otherwise we'll ask again in "
              f"{row['intervalDays']} days.", "", "— the Founder, yourco",
              "Stop these any time: reply STOP and it ends permanently."]
    return "\n".join(lines)


def due(today=None, commit=False):
    """Everything whose check-back has come around. Writes drafts; sends nothing."""
    today = today or datetime.date.today()
    live = latest_by_email()
    out = []
    for email, row in sorted(live.items()):
        anchor = row.get("lastAskedOn") or row["capturedOn"]
        due_on = datetime.date.fromisoformat(anchor) + datetime.timedelta(days=row["intervalDays"])
        if due_on > today:
            continue
        out.append({"email": email, "dueOn": due_on.isoformat(), "draft": draft(row, today)})

    if commit and out:
        os.makedirs(OUTDIR, exist_ok=True)
        path = os.path.join(OUTDIR, f"{today.isoformat()}_check-backs.md")
        body = [f"# Expiry check-backs due {today.isoformat()}", "",
                f"{len(out)} draft(s). **Drafts only — nothing here has been sent.** "
                f"the Founder sends; agents draft.", ""]
        for d in out:
            body += [f"## {d['email']}", "", "```", d["draft"], "```", ""]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(body))
        return out, path
    return out, None


# ── http (launch-gated) ─────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/expiry-intake":
            return self._json(404, {"ok": False, "error": "no such endpoint"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 8192:
                return self._json(413, {"ok": False, "error": "payload too large"})
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"ok": False, "error": "unreadable payload"})
        res = handle(payload, commit=True)
        self._json(200 if res.get("ok") else 400, res)

    def log_message(self, *a):
        pass


SAMPLE = {"email": "sample.owner@example.com", "interval_days": 90, "source": "expiry page",
          "beliefs": [{"text": "We get back to every quote within a day.", "how": "notice"},
                      {"text": "We follow up twice before we drop a lead.", "how": "no"},
                      {"text": "No job goes out without a deposit.", "how": "number"}]}


def main():
    argv = sys.argv[1:]
    commit = "--commit" in argv

    if "--serve" in argv:
        i = argv.index("--serve")
        port = int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 8808
        print(f"expiry intake on :{port} (POST /api/expiry-intake) — launch-gated")
        ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
        return 0

    if "--due" in argv:
        rows, path = due(commit=commit)
        print(f"{len(rows)} check-back(s) due" + (f" — drafted to {os.path.relpath(path, REPO)}"
                                                  if path else " (nothing written; pass --commit)"))
        for r in rows:
            print(f"  {r['email']} (due {r['dueOn']})")
        if rows and not commit:
            print("\n--- first draft ---\n" + rows[0]["draft"])
        return 0

    if "--self-check" in argv:
        res = handle(SAMPLE, commit=commit)
        print(json.dumps(res, indent=2))
        if res["ok"]:
            print("\n--- the check-back it would draft 90 days on ---\n")
            print(draft(res["row"], datetime.date.today() + datetime.timedelta(days=90)))
        return 0 if res["ok"] else 1

    print(__doc__.strip().split("\n\n")[-1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
