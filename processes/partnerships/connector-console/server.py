#!/usr/bin/env python3
"""yourco — the Connector Console (Connector OS step 2, `processes/partnerships/connector-os.md` §2).

The connector-facing half of the glass ledger: one page per connector showing **their own** rung,
referrals, money-with-the-math, downline override (informational only), and every event in their own
history from the append-only attribution log.

v2 (2026-08-07) adds: their referrals as **working records** they can annotate · commission-tier
progress worth-on-today's-book · a **dark-by-default** phantom-share section · self-set **goals** with
CRM-computed currents · **reporting** built from the attribution log · and the **upline view** — a
connector who recruited others sees their downline's production, pipeline, goals and reporting, and
may help set their goals.

Rules this file exists to hold:

1. **One source of truth, never forked.** Every number here comes from `crm/connector_statements.books()`
   (the book math) and `crm/connector_ladder.compute()` (the rungs). The console's number, the CRM
   Referrals cockpit's number, and the money Charles pays are the same computation or it's a bug.
2. **A connector sees only their own data.** The render function takes ONE connector and never emits
   another connector's book, name, or earnings — the single exception being their own downline. No
   yourco margin, no client internals, no CRM-wide totals, no yourco service prices (a referred
   client's own retainer is the connector's commission basis and is theirs to see).
   **Downline scope (v2):** an upline sees a downline member's rung, production (client count + active
   MRR), pipeline **as stage counts**, goals, and referral counts — deliberately NOT that person's
   client names, retainers per client, or commission/payout figures. Production and pipeline are what
   the Founder asked an upline to be able to coach on; another person's client roster and pay are not.
3. **Writes are scoped, never forked into a second database.** There is ONE database, `crm/data.json`.
   Every write goes through `crm/connector_writes.py` → `can_write()` → `melanie.crm_lock()` +
   `_atomic_dump` + `write_mirror`, and appends an attribution-log event. A connector may write only
   their own goals, their downline's goals, and notes/next-action on their own referrals. Renders are
   still never logged — a page view is not an attribution event.
4. **Identity is the session, and only the session (v3, 2026-08-07).** The v2 server read the acting
   connector out of the URL path, which made a link a credential: editing `/c/alice` to `/c/bob` was
   a complete account takeover of Bob, read and write. That path is **gone** — not demoted to a
   fallback, removed. Every route resolves `session → identity` via `auth.py` and then asks
   `authorize()` what that identity may do with the *requested* name. The URL is a request; the
   session is the answer. A body field naming an actor is ignored outright: if a form posts
   `actor=bob` while the session is Alice, the write is attributed to — and scoped to — Alice.

Authorization, in one table (server-side, computed fresh per request, never from client input):

  | request                        | operator | self | ancestor of target | anyone else |
  |--------------------------------|----------|------|--------------------|-------------|
  | `GET /c/<name>` (full console) | allow    | allow| —                  | 403         |
  | `GET /c/<name>` (scoped view)  | —        | —    | allow (bounded)    | 403         |
  | `POST …/goal`                  | 403 (RO) | allow| allow (their goals)| 403         |
  | `POST …/referral`              | 403 (RO) | allow| 403                | 403         |
  | `POST …/training`              | 403 (RO) | allow| 403                | 403         |

**v4 (2026-08-07) — training gates everything.** A connector who has not completed their **R0
training** gets `render_gate()`: a single-purpose "start here" page carrying *only* Learnings. The
other sections are not hidden, they are **not assembled** — nothing can leak out of markup that was
never built. Past R0 the whole console appears, and thereafter the rung a connector *holds* is
`min(evidence rung, training ceiling)` (`crm/connector_training.py`), so `UNLOCKS` — still the single
gate — is asked about a rung whose training is done. The evidence rung and the held rung are both
rendered, never collapsed: "you've earned R2 on evidence — finish R1 training to claim it" is the
sentence the whole design exists to be able to say.

The "scoped view" an upline gets is deliberately NOT the target's console: it is the same bounded
card the upline already sees on their own page (rung, production, pipeline as stage counts, goals) —
no client names, no per-client retainers, no earnings. Being someone's upline earns coaching data,
not their book. A 403 is byte-identical whether the requested connector exists or not.

Usage:
  python3 processes/partnerships/connector-console/server.py --render "Sample Contact"
  python3 processes/partnerships/connector-console/server.py --all
  python3 processes/partnerships/connector-console/server.py --serve [port]     # default 8807
  python3 processes/partnerships/connector-console/server.py --list
  python3 processes/partnerships/connector-console/server.py --issue-setup-token "Sample Contact"
  python3 processes/partnerships/connector-console/server.py --auth-list
  python3 processes/partnerships/connector-console/server.py --auth-revoke "Sample Contact"

STAGED: the connector program is counsel- + launch-gated. Every rendered page says so on its face.
The server binds 127.0.0.1 and speaks HTTP; authentication is real, transport is not. What must change
before this faces the public internet is written down in `_README.md` §Identity — read it before
serving this anywhere but a laptop.
"""
import os, sys, re, json, html, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
# Playground switch (2026-08-07). Same contract as the CRM and HQ: the template and all code
# stay at HERE; only DATA moves. Rendered consoles (OUT) and the auth store move too — a login
# in the sandbox must not be a real login, and a practice console must not land in the repo.
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO
CRM_DIR = os.path.join(ROOT, "crm")
OUT = os.path.join(ROOT, "_connector-consoles") if PLAYGROUND else os.path.join(HERE, "_out")
if PLAYGROUND:
    os.makedirs(OUT, exist_ok=True)
    os.environ.setdefault("YOURCO_CONNECTOR_AUTH_DIR", ROOT)
TEMPLATE = os.path.join(HERE, "index.html")
DEFAULT_PORT = 8807

# Import from the CODE dir, never CRM_DIR — in the playground CRM_DIR is a data tree with no
# .py files in it. Those two roles were the same path until 2026-08-07 and separating them is
# the whole point: code stays in the repo, data moves.
sys.path.insert(0, os.path.join(REPO, "crm"))
import connector_ladder as ladder                      # rungs + attribution log
import connector_writes as writes                      # the ONE scoped write path onto crm/data.json
import connector_training as training                  # the training gate + its own scoped write
import coach                                          # practice drills (self-marked here; see coach.record's `by`)
from connector_statements import books, _tier          # THE book math — never re-derived here
import connector_statements as stmts_mod               # bounty ledger + its constants, same rule
import connector_ghost as cghost                       # v3: yourco graded against its own median
import connector_approvals as capr                     # v3: the connector's gate on our first message
import connector_calibration as ccal                   # v3: their judgment, measured
import connector_escrow as cesc                        # v3: our bond against our own conduct
import connector_perks as cperk                        # v3: the own-OS grant

sys.path.insert(0, HERE)
import auth                                            # the ONLY source of identity (v3)

auth.set_logger(ladder.log_event)                      # auth.* events land on the attribution log

STAGED_NOTE = ("This console is a <strong>staged preview — not yet live</strong>. yourco's connector "
               "program is in counsel review; nothing on this page is an offer, an agreement, or a "
               "promise of income, and no payout is owed or payable until the program launches.")
CONTACT = "founder@yourco.example.com"

# Readable labels for the machine-readable gates in connector_ladder.UNLOCKS. Agent names never appear
# on a connector-facing surface (CLAUDE.md §External-surface rules), so "Polo-locked prices" is written
# as yourco's locked prices.
UNLOCK_LABELS = {
    "warm_intros": "Make warm introductions on yourco's behalf",
    "submit_contacts": "Hand yourco a business owner's details and let yourco make the approach — "
                       "you don't have to make the introduction yourself",
    "console": "This console — your ledger, live",
    "referral_spotter": "The referral-spotter — an agent that notices referral-shaped moments in your "
                        "world (with your permission) and drafts the intro in your voice. It never sends.",
    "demo_generation": "Generate a real, working demo for a business you just met — give first, never pitch",
    "own_digital_employee": "Your own digital employee — built and operated for you, free while you're active",
    "quote_locked_prices": "Quote yourco's locked prices directly",
    "co_brand": "Co-branded materials",
    "recruit_connectors": "Recruit other connectors (your own downline)",
    "run_audit_with_oversight": "Run the audit conversation yourself, with yourco supporting and reviewing",
    "deep_co_brand": "Deeper co-branding",
    "own_book_yourco_delivers": "Carry your own book, with yourco delivering underneath",
}

# The attribution log is append-only and may carry internal fields. The console renders a WHITELIST —
# a field not on this list is never shown to a connector.
EVENT_LABELS = {
    "referral.registered": "Referral registered",
    "referral.tagged": "Referral tagged to you",
    "stage.moved": "Referral moved stage",
    "conversation.held": "Real conversation held",
    "payment.collected": "First payment collected",
    "payout.computed": "Payout computed",
    "payout.paid": "Payout paid",
    "rung.changed": "Rung changed",
    "demo.generated": "Demo generated",
    "agreement.signed": "Agreement signed",
    "correction": "Correction",
    "note": "Note",
    "goal.set": "Goal target set",
    "referral.noted": "You updated a referral",
    "submission.received": "Contact submitted",
    "submission.verified": "Submission reviewed",
}
EVENT_FIELDS = [("company", "company"), ("stage", "stage"), ("month", "month"),
                ("amount", "amount"), ("note", "note")]

# The phantom-share bands — thresholds carry over unchanged from
# `decisions/2026-06-30_rep-equity-track.md`; the instrument is phantom units per
# `decisions/2026-08-07_phantom-shares-supersede-equity-track.md`. Measured on trailing-12-month
# NET-RETAINED referred revenue (revenue from referred clients still active at measurement).
#
# ⚠️ This section is DARK BY DEFAULT and renders only for connectors named in `meta.phantomTrack`
# (the Founder-set, per-connector, never computed and never auto-enabled). Never render a projected payout,
# a valuation, or a dollar value for the units — that is the binding display rule of the decision.
PHANTOM_BANDS = [(500_000, "0.5%"), (750_000, "1.0%"), (1_000_000, "1.5%")]
TRAILING_MONTHS = 12
DAYS_PER_MONTH = 30.44

# Connector-facing CONTENT lives outside this file, as an index the console renders — so a lesson or a
# resource is added by writing content, never by editing the renderer.
CONTENT_DIR = os.path.join(ROOT, "processes", "partnerships", "connector-training")
RESOURCES = os.path.join(CONTENT_DIR, "_resources.json")
DEMO_ROOT = os.path.join(ROOT, "agents", "bird", "connector-demos")
RUNG_N = {r["key"]: r["n"] for r in ladder.RUNGS}
RUNG_NAME = {r["key"]: r["name"] for r in ladder.RUNGS}


# ---- helpers -------------------------------------------------------------------------
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "unknown"


def esc(s):
    return html.escape(str(s if s is not None else ""))


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


def pct(v):
    """10.0 → '10%', 12.5 → '12.5%' — rates read as written in the agreement, never as floats."""
    return f"{v:g}%"


def _days_since(iso):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat((iso or "")[:10])).days
    except ValueError:
        return None


def stage_labels(d):
    return {s.get("key"): s.get("label") or s.get("key") for s in d.get("stages", [])}


# ---- the data one connector may see --------------------------------------------------
# ---- connector-facing content (lessons + resources) ----------------------------------
def _frontmatter(text):
    """Minimal `--- key: value ---` frontmatter. No YAML dependency; unknown keys pass through."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, text[end + 4:].lstrip("\n")


def md_to_html(md):
    """A deliberately small markdown subset — headings, lists, quotes, bold/italic/code, paragraphs.

    Everything is HTML-escaped FIRST, so lesson content can never inject markup into the console.
    """
    out, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            mode = None
            return
        if mode == "ul":
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in buf) + "</ul>")
        elif mode == "ol":
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in buf) + "</ol>")
        elif mode == "quote":
            # soft-wrapped source lines rejoin as prose — a wrapped sentence is one sentence
            out.append("<blockquote>" + " ".join(buf) + "</blockquote>")
        else:
            out.append("<p>" + " ".join(buf) + "</p>")
        buf, mode = [], None

    def inline(s):
        s = esc(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"`([^`]+?)`", r'<span class="mono">\1</span>', s)
        return s

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", line)
        if h:
            flush()
            lvl = min(len(h.group(1)) + 2, 4)     # a lesson's "#" is an h3 inside the console
            out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>")
            continue
        if line.lstrip().startswith(("- ", "* ")):
            if mode != "ul":
                flush()
                mode = "ul"
            buf.append(inline(line.lstrip()[2:]))
            continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            if mode != "ol":
                flush()
                mode = "ol"
            buf.append(inline(m.group(2)))
            continue
        if line.lstrip().startswith(">"):
            if mode != "quote":
                flush()
                mode = "quote"
            buf.append(inline(line.lstrip()[1:].strip()))
            continue
        if mode in ("ul", "ol", "quote"):
            buf[-1] += " " + inline(line.strip())   # continuation of the previous item
            continue
        if mode != "p":
            flush()
            mode = "p"
        buf.append(inline(line.strip()))
    flush()
    return "".join(out)


def load_lessons():
    """Every lesson in the content directory, ordered. Missing directory → no lessons, honestly."""
    out = []
    if not os.path.isdir(CONTENT_DIR):
        return out
    for fn in sorted(os.listdir(CONTENT_DIR)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        meta, body = _frontmatter(open(os.path.join(CONTENT_DIR, fn), encoding="utf-8").read())
        meta.update(slug=fn[:-3], body=body)
        try:
            meta["order"] = int(meta.get("order") or 999)
        except ValueError:
            meta["order"] = 999
        out.append(meta)
    out.sort(key=lambda m: (m["order"], m["slug"]))
    return out


def lessons_for(me):
    """Rung-aware lesson list. A locked lesson is SHOWN (title, length, what unlocks it) — never hidden.

    Which rung a lesson belongs to reads `connector_ladder.UNLOCKS` whenever the lesson names a
    capability, so the curriculum can never drift from the policy the rest of the OS enforces.

    **Visibility runs off the EVIDENCE rung, not the held one — deliberately.** A connector whose
    evidence has outrun their training must be able to read the very lesson that unblocks them; gating
    the lesson on the held rung would be a deadlock (you would need the rung to read the lesson that
    grants the rung). What the *held* rung still governs is whether the capability the lesson teaches
    is actually usable yet — carried separately as `capabilityHeld` and said out loud on the card.
    """
    ev = me.get("evidenceRungN", me["rungN"])
    by_rung = ((me.get("training") or {}).get("byRung") or {})
    out = []
    for L in load_lessons():
        cap, rung = L.get("unlocks"), L.get("rung") or "R0"
        if cap:
            # the rung that actually grants it, per UNLOCKS — not a number typed into the lesson
            rung = next((k for k, v in ladder.UNLOCKS.items() if cap in v), rung)
        need = RUNG_N.get(rung, 0)
        marks = {x["slug"]: x for x in (by_rung.get(rung) or {}).get("lessons", [])}
        m = marks.get(L["slug"], {})
        out.append({**L, "open": ev >= need, "rung": rung, "needRung": need,
                    "rungName": RUNG_NAME.get(rung, ""),
                    "capability": cap,
                    "capabilityHeld": (ladder.can_for(me, cap) if cap else me["rungN"] >= need),
                    "done": bool(m.get("done")), "doneAt": m.get("doneAt"),
                    # R2+ is operator-confirmed: a connector's mark is a SUBMISSION, not completion.
                    "status": m.get("status") or "open",
                    "needsConfirmation": bool(m.get("needsConfirmation")),
                    "confirmedBy": m.get("confirmedBy"),
                    "acknowledge": L.get("acknowledge"),
                    "stub": (L.get("status") or "").lower() == "stub"})
    return out


def training_for(me, lessons):
    """The training block the console renders: per-rung progress, the gate state, and the next act.

    Reads `connector_ladder.compute()`'s own numbers — this function derives presentation, never
    policy. The gate itself lives in `crm/connector_training.py`.
    """
    t = (me.get("training") or {})
    by_rung = t.get("byRung") or {}
    ev = me.get("evidenceRungN", me["rungN"])
    rows = []
    for r in ladder.RUNGS:
        b = dict(by_rung.get(r["key"]) or {"rung": r["key"], "rungName": r["name"], "lessons": [],
                                           "total": 0, "done": 0, "complete": False, "exists": False,
                                           "completedAt": None})
        b["visible"] = ev >= r["n"]              # you see a rung's training once you have earned it
        b["current"] = (t.get("blockingRung") == r["key"])
        rows.append(b)
    r0 = by_rung.get("R0") or {}
    return {"rungs": rows, "byRung": by_rung,
            "r0Complete": bool(r0.get("complete")),
            "r0": rows[0],
            "blockingRung": t.get("blockingRung"),
            "ceiling": me.get("trainingCeiling"), "ceilingN": me.get("trainingCeilingN"),
            "blocked": bool(me.get("blockedByTraining")),
            "needed": me.get("trainingNeeded"),
            "lessons": lessons}


def demo_kits_for(name, evs):
    """The connector's OWN generated demo kits — their folder only, plus their own log events."""
    kits = []
    folder = os.path.join(DEMO_ROOT, slug(name))
    if os.path.isdir(folder):
        for fn in sorted(os.listdir(folder)):
            p = os.path.join(folder, fn)
            if os.path.isdir(p):
                kits.append({"name": fn, "path": os.path.relpath(p, ROOT)})
    logged = sum(1 for e in evs if e.get("event") == "demo.generated")
    return {"kits": kits, "logged": logged}


def drills_for(name, me, lessons):
    """Practice scenarios, visible only for lessons this connector has ALREADY completed.

    Two deliberate constraints:

    * **Completed lessons only.** A drill is practice of a thing you were taught; showing it before
      the lesson turns it into a quiz on material the console has not given you yet, and the whole
      curriculum is built the other way round (`connector_training.py` gates what you may even see).
    * **`looks_like` / `fails_if` are NOT sent until the attempt is marked.** The rubric is the answer
      key. Shipping it with the prompt would let the page reveal it early — so the browser never holds
      it, and `reveal` is fetched only after a verdict exists. That is why this returns two shapes.

    Nothing here moves a rung. Rungs move on lessons plus CRM evidence; practice is practice, and the
    page says so.
    """
    done = {l["slug"] for l in lessons if l.get("done")}
    hist = {}
    for r in coach._history("connector", name):
        hist.setdefault(r["drill"], []).append(r)
    out = []
    for d in coach.drills("connector"):
        if d["lesson"] not in done:
            continue
        rows = hist.get(d["id"], [])
        last = rows[-1] if rows else None
        item = {"id": d["id"], "lesson": d["lesson"], "rung": d["rung"], "prompt": d["prompt"],
                "attempts": len(rows),
                "lastVerdict": last["verdict"] if last else None,
                "lastBy": last.get("by", "agent") if last else None}
        if last:                       # only now may the rubric travel to the browser
            item["reveal"] = {"looksLike": d["looks_like"], "failsIf": d["fails_if"]}
        out.append(item)
    return {"items": out,
            "done": sum(1 for i in out if i["lastVerdict"]),
            "note": "Practice only — nothing here changes your rung. Rungs move on lessons and on "
                    "what your referrals actually do."}


def resources_for(name, me, d, evs, lessons=None):
    """The resource index, resolved per connector. A document is LINKED only when its manifest entry
    says it is cleared for external eyes AND it is available now — otherwise it is listed and marked."""
    try:
        man = json.load(open(RESOURCES, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    contact = next((c for c in d.get("contacts", []) if c.get("id") == me.get("contactId")), {}) or {}
    demos = demo_kits_for(name, evs)
    # a lesson-backed resource inherits that lesson's rung gate — one gate, never two that can disagree
    lesson_open = {L["slug"]: L for L in (lessons if lessons is not None else lessons_for(me))}
    out = []
    for r in man.get("resources", []):
        av, state, detail, link = r.get("availability"), "", "", None
        if r.get("id") == "w9":
            on = contact.get("w9OnFile")
            state = "on file" if on else "not on file"
            detail = ("Recorded on your contact record." if on else
                      "yourco has no W-9 recorded for you. It is collected at join, alongside the "
                      "agreement — no payout can be computed without it.")
        elif r.get("id") == "referral-link":
            code = contact.get("referralCode")
            state = "issued" if code else "not issued yet"
            detail = (f"Your code: {code}" if code else
                      "Issued when you join. You do not need it to refer — a warm intro is tagged to "
                      "you by hand at first contact either way.")
        elif r.get("id") == "training-record":
            t = (me.get("training") or {}).get("byRung") or {}
            done = [k for k, v in t.items() if v.get("complete")]
            state = (f"{len(done)} rung(s) complete" if done else "nothing recorded yet")
            nxt = (me.get("training") or {}).get("blockingRung")
            detail = ((", ".join(sorted(done)) + ". " if done else "")
                      + (f"{nxt} training is the one in front of you. " if nxt else
                         "Every rung's training on the ladder is complete. ")
                      + (r.get("note") or ""))
        elif r.get("kind") == "generated":
            cap = r.get("unlocks")
            ok = ladder.can(me["rungN"], cap) if cap else True
            if not ok:
                grant = next((k for k, v in ladder.UNLOCKS.items() if cap in v), "R1")
                state = f"unlocks at {grant}"
                detail = f"Demo generation is earned at {grant} · {RUNG_NAME.get(grant, '')}."
            elif demos["kits"]:
                state = f"{len(demos['kits'])} kit(s)"
                detail = "; ".join(k["name"] for k in demos["kits"])
            else:
                state = "none yet"
                detail = ("You have generated no demos yet. Nothing is listed here that you did not "
                          "make.")
        elif r.get("lesson"):
            L = lesson_open.get(r["lesson"])
            if L and not L["open"]:
                state = f'unlocks at {L["rung"]}'
                detail = f'Opens at {L["rung"]} · {L["rungName"]}, with the lesson itself.'
            elif L:
                state, link = "available", r["lesson"]
                detail = r.get("note") or ""
            else:
                state = "not available yet"
                detail = "The lesson this points at is not in the library."
        elif av == "now" and r.get("clearedExternally"):
            state = "available"
            detail = r.get("note") or ""
        elif av == "counsel":
            state = "not available — in counsel review"
            detail = r.get("why") or ""
        elif av == "launch":
            state = "available at launch"
            detail = r.get("why") or ""
        else:
            state = "not available yet"
            detail = r.get("why") or r.get("note") or ""
        out.append({"title": r.get("title"), "what": r.get("what"), "kind": r.get("kind"),
                    "state": state, "detail": detail, "lesson": link})
    return out


def _refs_for(name, d, connectors, labels, rate, notes=None):
    """One connector's referrals as working records. `rate` is theirs; nobody else's book is touched."""
    book = connectors.get(name, {"active": [], "inactive": []})
    by_id = {c["id"]: c for c in d.get("companies", [])}
    contacts = d.get("contacts", [])
    notes = notes if notes is not None else ((d.get("meta") or {}).get("connectorNotes") or {})
    acts = d.get("activities", [])
    # Referral MODE is per referral, never per person (`decisions/2026-08-11_connector-program-v2.md`):
    # the same connector introduces one owner and sources another, and both are normal. yourco sets it,
    # so it renders read-only alongside stage and retainer. Default is `introducer` — every referral
    # that predates the modes was a warm intro.
    modes = (d.get("meta") or {}).get("referralMode") or {}

    refs = []
    for r in book["active"] + book["inactive"]:
        live = r in book["active"]
        cid = r["companyId"]
        co = by_id.get(cid) or {}
        # the person at the business they introduced — name + role only, never yourco's internal notes
        who = next((c for c in contacts
                    if c.get("companyId") == cid and c.get("kind") != "internal"), None)
        touches = [a.get("date") for a in acts if a.get("companyId") == cid and a.get("date")]
        n = notes.get(str(cid)) or {}
        refs.append({
            "company": r["company"],
            "companyId": cid,
            "vertical": co.get("vertical") or "",
            "contact": (who or {}).get("name") or "",
            "contactRole": (who or {}).get("role") or "",
            "stageKey": r["stage"],
            "stage": labels.get(r["stage"], (r["stage"] or "—").title()),
            "mode": "sourcer" if (modes.get(str(cid)) or "introducer") == "sourcer" else "introducer",
            "live": live,
            "mrr": r["mrr"],
            "commission": round(r["mrr"] * rate / 100, 2) if live else 0.0,
            "days": _days_since(r.get("stageSince")),
            "lastTouch": max(touches) if touches else "",
            "note": n.get("note") or "",
            "nextAction": n.get("nextAction") or "",
        })
    refs.sort(key=lambda r: (not r["live"], -r["mrr"], r["company"]))
    return refs


def goal_currents(me, refs):
    """The live value of every goal metric — computed from the CRM, never self-reported."""
    ev = me["evidence"]
    return {"referrals": len(refs),
            "conversations": ev["conversations"],
            "liveClients": ev["live"],
            "referredMRR": sum(r["mrr"] for r in refs if r["live"])}


def goals_block(name, d, me, refs, period=None):
    """Targets the connector set + currents the CRM proves + pace against the quarter."""
    period = period or writes.quarter_of()
    rec = writes.goals_for(name, d=d, period=period)
    start, end = writes.quarter_bounds(period)
    today = datetime.date.today()
    span = (end - start).days + 1
    elapsed = max(0, min(span, (today - start).days + 1))
    return {"period": period,
            "label": f"{period[:4]} Q{period[-1]}",
            "targets": rec.get("targets") or {},
            "updated": rec.get("updated") or "", "updatedBy": rec.get("updatedBy") or "",
            "currents": goal_currents(me, refs),
            "pctElapsed": int(round(100 * elapsed / span)) if span else None}


def tier_progress(me, tiers, refs):
    """Current tier, what earns the next one, and what it is worth ON TODAY'S BOOK (never a projection).

    Bands come from `connector_statements` — this used to keep its own copy of the count thresholds
    and went stale the moment the basis moved to MRR (2026-08-13), rendering "6–10 active" on a page
    whose actual rate was computed from revenue. Ask the money module; never restate the bands here.
    """
    rates = tiers.get("rates", [10, 12.5, 15])
    basis = stmts_mod._tier_basis(tiers)
    lo, hi = ((tiers.get("thresholds") or [6, 11])[:2] if basis == "count"
              else (tiers.get("mrrThresholds") or stmts_mod.MRR_THRESHOLDS)[:2])
    n = me["book"]["active"]
    mrr = sum(r["mrr"] for r in refs if r["live"])
    cur = n if basis == "count" else mrr                 # the number the bands are actually about
    rate = me["book"]["rate"]
    names = ["Referrer", "Senior", "Partner"]

    def band(a, b):
        if basis == "count":
            return f"{a}–{b} active" if b else f"{a}+ active"
        eq = lambda v: max(1, int(round(v / stmts_mod.CORE_FLOOR)))
        return (f"{money(a)}–{money(b)}/mo" if b else f"{money(a)}+/mo") + \
               (f" · ≈{eq(a)}+ clients" if not b else f" · ≈{eq(a)}–{eq(b + 1)} clients")

    steps = [{"tier": 1, "name": names[0], "rate": rates[0], "from": 0, "to": lo - 1,
              "band": band(0, lo - 1)},
             {"tier": 2, "name": names[1], "rate": rates[1], "from": lo, "to": hi - 1,
              "band": band(lo, hi - 1)},
             {"tier": 3, "name": names[2], "rate": rates[2], "from": hi, "to": None,
              "band": band(hi, None)}]
    nxt = next((s for s in steps if s["tier"] == me["book"]["tier"] + 1), None)
    _nrate, gap_text = stmts_mod.tier_progress_note({"active": [{"mrr": r["mrr"]} for r in refs if r["live"]]},
                                                    tiers)
    uplift = round(mrr * (nxt["rate"] - rate) / 100, 2) if nxt else 0.0
    return {"tier": me["book"]["tier"], "name": names[me["book"]["tier"] - 1], "rate": rate,
            "active": n, "mrr": mrr, "steps": steps, "next": nxt,
            "need": max((nxt["from"] - cur) if nxt else 0, 0), "gapText": gap_text, "basis": basis,
            "uplift": uplift,
            "pct": None if not nxt else min(100, int(round(100 * cur / max(nxt["from"], 1))))}


def phantom_block(name, d, refs):
    """DARK BY DEFAULT. Returns None unless `meta.phantomTrack` names this connector.

    Never computed into existence, never auto-enabled — the Founder sets `meta.phantomTrack` by hand
    (`decisions/2026-08-07_phantom-shares-supersede-equity-track.md` §The display risk, rule 1).
    """
    track = (d.get("meta") or {}).get("phantomTrack")
    if not track:
        return None
    enabled = set(track) if isinstance(track, (list, tuple, set)) else {
        k for k, v in dict(track).items() if v}
    if name not in enabled:
        return None

    # Measured trailing-12-month NET-RETAINED referred revenue: for each referred client STILL ACTIVE
    # today, the months it has been live within the trailing 12. Real numbers only — no forecast.
    measured, lines = 0.0, []
    for r in refs:
        if not r["live"]:
            continue
        months = min(TRAILING_MONTHS, int((r["days"] or 0) // DAYS_PER_MONTH))
        amt = round(r["mrr"] * months, 2)
        measured += amt
        lines.append({"company": r["company"], "mrr": r["mrr"], "months": months, "amount": amt})
    first = PHANTOM_BANDS[0][0]
    return {"measured": round(measured, 2), "lines": lines, "bands": PHANTOM_BANDS,
            "reached": [b for b in PHANTOM_BANDS if measured >= b[0]],
            "pctFirst": min(100, int(round(100 * measured / first))) if first else 0}


def reporting_block(me, refs, evs, override):
    """Their own performance over time — the attribution log IS the history, so it is the source."""
    months = {}

    def bucket(m):
        return months.setdefault(m, {"referrals": 0, "moves": 0, "commission": 0.0, "override": 0.0})

    for e in evs:
        m = (e.get("month") or (e.get("ts") or "")[:7]) or ""
        if not m:
            continue
        ev = e.get("event")
        if ev in ("referral.registered", "referral.tagged"):
            bucket(m)["referrals"] += 1
        elif ev == "stage.moved":
            bucket(m)["moves"] += 1
        elif ev in ("payout.computed", "payout.paid"):
            try:
                amt = float(e.get("amount") or 0)
            except (TypeError, ValueError):
                amt = 0.0
            key = "override" if (e.get("kind") == "override") else "commission"
            bucket(m)[key] += amt

    R = ladder.RETENTION_DAYS
    n_conv = sum(1 for r in refs if r["stageKey"] in ladder.CONVERSATION_STAGES)
    n_live = sum(1 for r in refs if r["live"])
    n_ret = sum(1 for r in refs if r["live"] and (r["days"] or 0) >= R)
    funnel = [("Referrals registered", len(refs)),
              ("Reached a real conversation", n_conv),
              ("Went live", n_live),
              (f"Retained past {R} days", n_ret)]
    return {"months": dict(sorted(months.items())), "funnel": funnel,
            "hasMoney": any(v["commission"] or v["override"] for v in months.values()),
            "hasReferralHistory": any(v["referrals"] or v["moves"] for v in months.values()),
            "downlineNow": override}


def downline_view(actor, me, d, connectors, labels, tiers, evs_all=None):
    """The upline view: for each downline member — production, pipeline, goals, reporting.

    Deliberately NOT their client names, per-client retainers, or commission/payout figures
    (see module docstring rule 2). Recursive per the uncapped-depth decision; the cycle guard is
    `books()`' own `downline()`.
    """
    state = ladder.compute(d)
    recruiters = (d.get("meta") or {}).get("repRecruiters") or {}
    all_events = evs_all if evs_all is not None else ladder.read_events()
    out = []
    for k in me["downline"]:
        s = state.get(k)
        if not s:
            continue
        krefs = _refs_for(k, d, connectors, labels, s["book"]["rate"])
        pipeline = {}
        for r in krefs:
            if not r["live"]:
                pipeline[r["stage"]] = pipeline.get(r["stage"], 0) + 1
        kevs = [e for e in all_events if (e.get("connector") or "") == k]
        by_month = {}
        for e in kevs:
            if e.get("event") in ("referral.registered", "referral.tagged"):
                m = (e.get("ts") or "")[:7]
                by_month[m] = by_month.get(m, 0) + 1
        out.append({
            "name": k,
            "via": recruiters.get(k) or "",
            "rung": s["rung"], "rungName": s["rungName"],
            "clients": s["book"]["active"], "mrr": s["book"]["activeMRR"],
            "referrals": s["evidence"]["referrals"],
            "conversations": s["evidence"]["conversations"],
            "live": s["evidence"]["live"],
            "pipeline": sorted(pipeline.items(), key=lambda kv: -kv[1]),
            "goals": goals_block(k, d, s, krefs),
            "referralsByMonth": dict(sorted(by_month.items())),
        })
    out.sort(key=lambda x: (-x["mrr"], x["name"]))
    return out


def console_data(name, d=None, events=None, ghost_data=None):
    """Everything one connector's page renders — and nothing else. Pure read.

    `d` / `events` are injectable so the console can be exercised against a fixture without
    touching crm/data.json or the attribution log.
    """
    d = d if d is not None else json.load(open(os.path.join(CRM_DIR, "data.json")))
    state = ladder.compute(d)
    me = state.get(name)
    if me is None:
        return None

    tiers = (d.get("meta") or {}).get("referralTiers") or {}
    connectors, _credits, _dl = books(d)                 # one source of truth
    labels = stage_labels(d)
    rate = me["book"]["rate"]

    refs = _refs_for(name, d, connectors, labels, rate)
    active_mrr = sum(r["mrr"] for r in refs if r["live"])
    direct = round(active_mrr * rate / 100, 2)           # identical expression to connector_statements

    # downline: names + the MRR the override math needs. Nothing deeper about those people.
    ov_pct = float(tiers.get("override") or 0)
    dl = []
    for k in me["downline"]:
        kb = connectors.get(k, {"active": []})
        dl.append({"name": k, "clients": len(kb["active"]), "mrr": sum(a["mrr"] for a in kb["active"])})
    dl_mrr = sum(x["mrr"] for x in dl)
    override = {"pct": ov_pct, "people": dl, "mrr": dl_mrr,
                "amount": round(dl_mrr * ov_pct / 100, 2)}

    all_events = events if events is not None else ladder.read_events()
    evs = [e for e in all_events if (e.get("connector") or "") == name]  # never someone else's
    _lessons = lessons_for(me)

    # Sourcer submissions + the bounty they accrue. Imported from connector_statements for the same
    # reason the commission is: there is one computation of what yourco owes, and this is not a
    # second one. `cap` is the Founder's open number — unset renders as unset, never as a guessed default.
    cap, cap_used, cap_left = writes.cap_state(name, d)
    subs = {"rows": stmts_mod.submissions(d, name),
            "ledger": stmts_mod.bounties(d, name).get(name),
            "verifiedAmount": stmts_mod.BOUNTY_VERIFIED, "bookedAmount": stmts_mod.BOUNTY_BOOKED,
            "payable": stmts_mod.BOUNTY_PAYABLE,
            "cap": cap, "capUsed": cap_used, "capLeft": cap_left,
            "can": ladder.can_for(me, "submit_contacts")}

    return {"me": me, "refs": refs, "rate": rate, "activeMRR": active_mrr, "direct": direct,
            "tiers": tiers, "stageLabels": labels, "override": override, "events": evs,
            "tierProgress": tier_progress(me, tiers, refs),
            "goals": goals_block(name, d, me, refs),
            "phantom": phantom_block(name, d, refs),
            "reporting": reporting_block(me, refs, evs, override),
            "downline": downline_view(name, me, d, connectors, labels, tiers, all_events),
            "lessons": _lessons,
            "training": training_for(me, _lessons),
            "drills": drills_for(name, me, _lessons),
            "resources": resources_for(name, me, d, evs, _lessons),
            "submissions": subs,
            # v3 (2026-08-13). Each of these five is a computation that REFUSES rather than guesses,
            # and each is imported, never re-derived here — the console renders judgements it did not
            # make, which is the only way the number on this page can be the same as the number in
            # the statement and the money Charles pays.
            "ghost": cghost.compute(name, d, ghost_data=ghost_data),
            "approvals": capr.compute(name, d),
            "calibration": ccal.compute(name, d),
            "escrow": cesc.compute(name, d).get(name),
            "perk": cperk.compute(name, d),
            "slug": slug(name)}


def next_rung_progress(data):
    """What earns the next rung, with live progress from the connector's own evidence."""
    me, ev, refs = data["me"], data["me"]["evidence"], data["refs"]
    n = me["rungN"]
    R = ladder.RETENTION_DAYS
    # Training first: if the evidence has already earned a rung the training has not released, the
    # honest "next step" is the lesson, not another referral. Saying anything else would send somebody
    # to do work they have already done.
    if me.get("blockedByTraining"):
        blk = (data["training"]["byRung"].get(me["trainingNeeded"]) or {})
        rows = blk.get("lessons") or []
        checks = [(x["title"], x["done"],
                   None if x["done"] else
                   ("submitted — waiting on yourco to confirm" if x.get("status") == "submitted"
                    else "not marked complete yet"))
                  for x in rows]
        return {"target": f'{me["evidenceRung"]} · {me["evidenceRungName"]}',
                "earn": (f'You have earned {me["evidenceRung"]} on evidence. What is left is '
                         f'{me["trainingNeeded"]} training — finish it and the rung is yours.'),
                "have": blk.get("done", 0), "need": max(blk.get("total", 0), 1),
                "checks": checks or [(f'{me["trainingNeeded"]} training', False,
                                      "yourco has not published this training yet — that is yourco's "
                                      "gap, not yours. Say so and it gets written.")]}
    if n < 0:
        return {"target": "R0 · Joined", "earn": "signed agreement + W-9 on file",
                "have": 0, "need": 1,
                "checks": [("Partner agreement signed and W-9 on file", False,
                            "The program is in counsel review — nothing is signable yet.")]}
    if n == 0:
        # "a real conversation" is ladder.CONVERSATION_STAGES — read, never re-defined here
        detail = [(f"{r['company']} — {r['stage']}", r["stageKey"] in ladder.CONVERSATION_STAGES, None)
                  for r in refs]
        return {"target": "R1 · Proven", "earn": me["nextRungEarn"],
                "have": ev["conversations"], "need": 1,
                "checks": detail or [("One referral reaching a sit-down, audit, or beyond", False,
                                      "No referrals registered yet.")]}
    if n == 1:
        checks = []
        for r in refs:
            if r["live"]:
                dd = r["days"]
                ok = dd is not None and dd >= R
                checks.append((f"{r['company']} — live",
                               ok, None if ok else (f"{dd} of {R} days retained — {R - dd} to go"
                                                    if dd is not None else "retention clock starts at go-live")))
        return {"target": "R2 · Producing", "earn": me["nextRungEarn"],
                "have": ev[f"retained{R}d"], "need": 1,
                "checks": checks or [(f"First referred client live and retained {R} days", False,
                                      "No referred client is live yet.")]}
    if n == 2:
        held = ev[f"retained{R}d"]
        return {"target": "R3 · Trusted", "earn": me["nextRungEarn"],
                "have": ev["live"], "need": 3,
                "checks": [(f"{ev['live']} of 3 live referred clients", ev["live"] >= 3, None),
                           (f"Retention holding — {held} of {ev['live']} live past {R} days",
                            held == ev["live"] and ev["live"] > 0, None),
                           ("Zero conduct flags", not ev["conductFlag"], None)]}
    if n == 3:
        return {"target": "R4 · Advisor track", "earn": me["nextRungEarn"], "have": 0, "need": 0,
                "checks": [("Sustained book + the Founder's judgment", False,
                            "R4 is granted by the Founder, not computed — there is no counter to game.")]}
    return None


# ---- rendering -----------------------------------------------------------------------
_FINE_RUN = re.compile(r'(?:\s*<p class="fine"[^>]*>.*?</p>)+\s*$', re.S)


def _section(inner, cls="", why_label=None):
    """One section. Trailing fine-print is folded into a disclosure, everywhere, automatically.

    The console carried 34 blocks of small grey caveat text — the honesty rules each build refuses
    on. Individually they are the most important sentences on the page; stacked, they became
    wallpaper and made every section the same shape. Folding them is done HERE rather than at 34
    call sites so a new section cannot forget to, and the text itself is untouched: one click, still
    verbatim, still on the page for anyone auditing it. Nothing is deleted — only closed by default.
    """
    # Brass earns presence through scarcity (DESIGN.md §4.1). The page carried 16 ticks — one per
    # section — so brass signalled nothing. Stripped here rather than at 16 call sites: only the
    # section carrying a room's headline figure keeps it.
    if "head" not in cls:
        inner = inner.replace('<div class="tick"></div>', "")
    m = _FINE_RUN.search(inner)
    if m and m.group(0).count('class="fine"') >= 1:
        label = why_label or "Why this says what it says"
        inner = (inner[:m.start()]
                 + f'<details class="why"><summary>{esc(label)}</summary>{m.group(0)}</details>')
    return f'<section class="tile {cls}"><div class="wrap reveal">{inner}</div></section>'


def _figure(label, value, sub="", kind=""):
    """A number that matters, set as a number (DESIGN.md §4.10) — or a refusal, set as a sentence.

    `kind="none"` is the important one: a refusal must never be typeset like a total, or "No figure"
    reads as a balance of zero, which is the one thing every honesty rule in v3 exists to prevent.
    """
    cls = "val" + (f" {kind}" if kind else "")
    return (f'<div class="figure"><div class="lbl">{esc(label)}</div>'
            f'<div class="{cls}">{value}</div>'
            + (f'<div class="sub">{esc(sub)}</div>' if sub else "") + '</div>')


def _hero(data):
    me = data["me"]
    rung = f'{esc(me["rung"])} · {esc(me["rungName"])}' if me["rung"] else "Not joined"
    sub = ("You have not joined the connector program — this is a preview of the console you would get, "
           "rendered from real data (which, for you, is currently none)."
           if not me["rung"] else
           "Every number on this page is computed from yourco's records, with the math shown. "
           "Nothing here is estimated, rounded in yourco's favour, or editable after the fact.")
    return _section(
        f'<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console</div>'
        f'<h1 style="margin-top:12px">{esc(me["connector"])}</h1>'
        f'<p class="lede">{sub}</p>'
        f'<p class="muted mono" style="margin-top:18px">{rung}</p>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark")


def _rung_section(data):
    me = data["me"]
    strip = ""
    for r in ladder.RUNGS:
        on = "on" if me["rungN"] >= r["n"] else ""
        # a rung the evidence has earned but training has not released reads as earned-not-claimed —
        # visibly different from both "held" and "not yet".
        earned = (me.get("evidenceRungN", -1) >= r["n"] > me["rungN"])
        mark = ' <span class="tag">earned</span>' if earned else ""
        strip += (f'<div class="step {on}">{r["key"]}{mark}'
                  f'<span class="s-name">{esc(r["name"])}</span></div>')

    gap = ""
    if me.get("blockedByTraining"):
        gap = (f'<div class="gated"><div class="flag">held back by training</div>'
               f'<h3>You have earned {esc(me["evidenceRung"])} · {esc(me["evidenceRungName"])} on '
               f'evidence — you are holding {esc(me["rung"])} · {esc(me["rungName"])}.</h3>'
               f'<p>Your referrals did the work; nothing is being questioned and nothing is lost. '
               f'Every rung on this ladder has its own training, and a rung is only <em>held</em> once '
               f'the training below it is finished. Yours stops at '
               f'<strong>{esc(me["trainingNeeded"])}</strong> — complete it in Learnings below and the '
               f'rung you already earned becomes yours, along with what it unlocks.</p>'
               f'<p class="mono">holding = the lesser of what you have produced and what you have '
               f'been trained for</p></div>')

    unlocked = me["unlocks"]
    if unlocked:
        ul = "".join(f'<li>{UNLOCK_LABELS.get(u, esc(u))}</li>' for u in unlocked)
        unl = f'<h3>What your rung unlocks</h3><ul>{ul}</ul>'
    else:
        unl = ('<h3>What your rung unlocks</h3>'
               '<p>Nothing yet — the ladder starts when you join. Rungs are computed from evidence in '
               'yourco\'s records, never granted by mood, and they can move down as well as up.</p>')

    p = next_rung_progress(data)
    if p:
        pct = 100 if p["need"] == 0 else min(100, int(100 * p["have"] / max(p["need"], 1)))
        checks = "".join(
            f'<li><span class="box {"" if ok else "off"}">{"✓" if ok else "○"}</span>'
            f'<span>{esc(label)}{f"<br><span class=mono>{esc(note)}</span>" if note else ""}</span></li>'
            for label, ok, note in p["checks"])
        nxt = (f'<h3>Next rung — {esc(p["target"])}</h3>'
               f'<p>Earned by: {esc(p["earn"])}</p>'
               f'<div class="bar"><span style="width:{pct}%"></span></div>'
               f'<div class="barnote">{p["have"]} of {p["need"]} — evidence, not vibes.</div>'
               f'<ul class="checks">{checks}</ul>')
    else:
        nxt = ('<h3>Next rung</h3><p>You are at the top of the ladder. Beyond this, the conversation is '
               'with the Founder directly.</p>')

    key = (f'<span class="rung-key">{esc(me["rung"])}</span>' if me["rung"] else "")
    head = f'<div class="rung-head">{key}<span class="rung-name">{esc(me["rungName"])}</span></div>'
    return _section(f'<div class="tick"></div><h2>Your rung</h2>{head}'
                    f'<div class="ladder">{strip}</div>{gap}'
                    f'<div class="cols"><div class="card">{unl}</div><div class="card">{nxt}</div></div>', "head")


def _referrals_section(data):
    """v2: the referrals as WORKING RECORDS — yourco's fields read-only, the connector's editable."""
    refs = data["refs"]
    if not refs:
        return _section(
            '<div class="tick"></div><h2>Your referrals</h2>'
            '<div class="empty"><h3>No referrals yet</h3>'
            '<p>Nothing on this page is sample data. The moment you introduce a business and it is tagged '
            'to you, it appears here as a working record — its real stage, when it was last touched, and '
            'a place for your own next action and notes. Every move it makes after that is recorded on '
            'the log below, permanently.</p></div>', "parchment")

    cards = ""
    for r in refs:
        tag = ('<span class="tag live">Active</span>' if r["live"]
               else '<span class="tag">In progress</span>')
        # The mode says who is doing the talking on this referral — the single most useful thing for a
        # connector to know at a glance, because it tells them whether the ball is theirs.
        tag += ('<span class="tag mode">yourco is calling</span>' if r["mode"] == "sourcer"
                else '<span class="tag mode">Your introduction</span>')
        facts = [("Stage", r["stage"]),
                 ("Contact", (f'{r["contact"]}' + (f' · {r["contactRole"]}' if r["contactRole"] else ""))
                  if r["contact"] else "—"),
                 ("Last touch", (f'{r["lastTouch"]}' if r["lastTouch"] else "—")),
                 ("Their retainer", f'{money(r["mrr"])}/mo' if r["live"] else "—"),
                 ("Your commission", f'{money(r["commission"], True)}/mo' if r["live"] else "—")]
        kv = "".join(f'<div class="kv"><span class="k">{esc(k)}</span>'
                     f'<span class="v">{esc(v)}</span></div>' for k, v in facts)
        cards += (
            f'<div class="rec" data-company="{esc(r["companyId"])}">'
            f'<div class="rechead"><h3>{esc(r["company"])}</h3>{tag}</div>'
            f'<div class="kvs">{kv}</div>'
            f'<div class="editrow">'
            f'<label>Your next action<input type="text" data-f="nextAction" maxlength="300" '
            f'value="{esc(r["nextAction"])}" placeholder="e.g. call Client Owner Thursday"></label>'
            f'<label>Your notes<textarea data-f="note" maxlength="2000" rows="3" '
            f'placeholder="What you know that yourco doesn\'t.">{esc(r["note"])}</textarea></label>'
            f'<div class="saveline"><button class="btn" data-save="referral">Save</button>'
            f'<span class="status"></span></div></div></div>')

    n_live = sum(1 for r in refs if r["live"])
    return _section(
        f'<div class="tick"></div><h2>Your referrals</h2>'
        f'<p class="lede">{len(refs)} referral{"s" if len(refs) != 1 else ""} · '
        f'{n_live} active. "Active" means the client is live and paying — that is what commission is '
        f'computed on. The next action and notes on each record are <strong>yours</strong>: you write '
        f'them, they save straight into yourco\'s records, and yourco sees them there. There is no '
        f'separate system to keep in step.</p>'
        f'<div class="recs">{cards}</div>'
        f'<p class="fine">Stages are yourco\'s real pipeline stages, shown to you exactly as yourco sees '
        f'them. Stage, retainer, and ownership are <strong>read-only</strong> to you — they are set from '
        f'yourco\'s own records, which is precisely why the money on this page can be trusted. A referral '
        f'that never goes live is shown honestly as in progress — it is never quietly dropped from this '
        f'list.</p>', "parchment")


SUB_STATUS = {
    "pending":  ("Awaiting review", "We are checking this one. yourco reviews every submission within "
                                    "24–48 hours."),
    "verified": ("Verified", "Real business, reachable owner. The first step of the bounty is earned."),
    "booked":   ("Call booked", "A real conversation is on the calendar. Both steps are earned."),
    "client":   ("Now a client", "This one became a paying client — commission applies from here."),
    "rejected": ("Not verified", "We could not verify this contact. Nothing is earned on it, and it "
                                 "does not count against you."),
}


def _submissions_section(data):
    """Sourcer mode: hand yourco a name, yourco does the calling. The bounty ledger lives here.

    The honesty rules this section holds, all three load-bearing:
      • it never shows a payable balance while `BOUNTY_PAYABLE` is False — it says ACCRUED and why;
      • it asks for provenance and consent as REQUIRED fields, because yourco becomes the caller and
        has to be able to say where a contact came from (counsel checklist 17a);
      • an unset cap renders as unset. It does not invent a number the Founder has not set.
    """
    s = data["submissions"]
    if not s["can"]:
        return ""
    led = s["ledger"] or {"rows": [], "verified": 0, "booked": 0, "pending": 0, "rejected": 0,
                          "earned": 0.0}
    v_amt, b_amt = s["verifiedAmount"], s["bookedAmount"]

    rows = ""
    for r in s["rows"]:
        label, blurb = SUB_STATUS.get(r.get("status") or "pending", SUB_STATUS["pending"])
        earned = r.get("earned") or 0
        rows += (
            f'<tr><td><strong>{esc(r.get("business") or "—")}</strong>'
            f'<div class="sub">{esc(r.get("contact") or "")}</div></td>'
            f'<td>{esc((r.get("submittedAt") or "")[:10])}</td>'
            f'<td>{esc(label)}<div class="sub">{esc(blurb)}</div></td>'
            f'<td class="num">{money(earned, True) if earned else "—"}</td></tr>')
    table = (f'<table class="tbl"><thead><tr><th>Business</th><th>Submitted</th><th>Status</th>'
             f'<th class="num">Accrued</th></tr></thead><tbody>{rows}</tbody></table>'
             if rows else
             '<div class="empty"><h3>Nothing submitted yet</h3><p>Everything you submit shows here with '
             'its real status — including the ones that do not work out. A submission is never quietly '
             'dropped from this list.</p></div>')

    total = (f'<p class="big">{money(led["earned"], True)} accrued</p>'
             f'<p class="muted">{led["verified"]} verified × {money(v_amt)} + '
             f'{led["booked"]} booked call{"s" if led["booked"] != 1 else ""} × {money(b_amt)}'
             + (f' · {led["pending"]} awaiting review' if led["pending"] else "")
             + (f' · {led["rejected"]} not verified' if led["rejected"] else "") + '</p>')

    # The single most important sentence in this section.
    staged = ('<div class="staged"><strong>Accrued, not payable.</strong> The submission bounty is '
              'staged with the rest of the connector program. Nothing here is owed or payable until '
              'the program launches and its legal review clears — this figure is a running record of '
              'what you have done, not a balance.</div>') if not s["payable"] else ""

    if s["cap"] is None:
        capline = ('There is no submission limit set right now. If one is introduced, it will appear '
                   'here before it applies to you — never after.')
    else:
        capline = (f'{s["capUsed"]} of {s["cap"]} submissions used this month · '
                   f'{s["capLeft"]} left.')

    form = (
        f'<div class="rec" data-submission="1">'
        f'<div class="rechead"><h3>Submit a contact</h3></div>'
        f'<div class="editrow">'
        f'<label>Business name<input type="text" data-s="business" maxlength="200" '
        f'placeholder="Northside Dental"></label>'
        f'<label>Owner\'s name<input type="text" data-s="contact" maxlength="120" '
        f'placeholder="Dana Reyes"></label>'
        f'<label>Email<input type="email" data-s="email" maxlength="200" '
        f'placeholder="dana@northsidedental.com"></label>'
        f'<label>Phone<input type="tel" data-s="phone" maxlength="40" placeholder="(555) 010-0100"></label>'
        f'<label>How you know them <span class="req">required</span>'
        f'<input type="text" data-s="provenance" maxlength="500" '
        f'placeholder="my dentist for six years"></label>'
        f'<label>Do they know you are passing their details on?'
        f'<select data-s="consent">'
        f'<option value="unknown">Not sure</option>'
        f'<option value="yes">Yes — I told them</option>'
        f'<option value="no">No — not yet</option></select></label>'
        f'<label>Anything useful<textarea data-s="note" maxlength="1000" rows="3" '
        f'placeholder="What is going on in their business that made you think of this."></textarea></label>'
        f'<div class="saveline"><button class="btn" data-save="submission">Submit</button>'
        f'<span class="status"></span></div></div></div>')

    return _section(
        f'<div class="tick"></div><h2>Submit a contact</h2>'
        f'<p class="lede">You do not have to make the introduction yourself. Hand yourco an owner\'s '
        f'details and <strong>yourco makes the approach</strong> — you stay out of it entirely. '
        f'{money(v_amt)} once we verify the contact is real and reachable, another {money(b_amt)} if it '
        f'turns into a real conversation, and the normal commission on top if they become a client.</p>'
        f'{staged}'
        f'<div class="totalbox">{total}</div>'
        f'{table}'
        f'{form}'
        f'<p class="fine"><strong>Why we ask how you know them.</strong> On a submitted contact yourco '
        f'is the one making the call, so yourco has to be able to say where the contact came from and '
        f'whether they were expecting to hear from anyone. That is a real legal obligation on us, not '
        f'paperwork — it is why those two questions are required and why a submission without them '
        f'cannot be verified. Never submit a list you bought, scraped, or copied from somewhere; those '
        f'are rejected, and they are the one thing that could put this program at risk.</p>'
        f'<p class="fine">One referrer per business, ever — if someone already submitted a business, '
        f'the first logged submission holds it. {esc(capline)}</p>', "parchment")


ROOMS = [("overview", "Overview"), ("book", "Your book"), ("money", "Your money"),
         ("us", "How we're doing"), ("account", "Your account")]


def _needs_you(data):
    """The only list on the page that is a to-do. Empty is a real, good answer and says so."""
    out = []
    a = data.get("approvals") or {}
    for p in a.get("pending", []):
        out.append(("A message to " + (p.get("business") or "someone you referred"),
                    "waiting for you to approve, edit or stop it", "book"))
    t = data["training"]
    if t.get("blocking") and not t["blocking"].get("complete", True):
        out.append((f'{t["blocking"]["rungName"]} training',
                    "your results have run ahead of it", "account"))
    for r in data["refs"]:
        if r.get("nextAction"):
            out.append((r["company"], f'your note says: {r["nextAction"]}', "book"))
    return out[:6]


def _overview_section(data):
    """The front page. Four figures, then what is waiting on you — and nothing else.

    Every figure here is imported from the computation that owns it; the overview never derives a
    number, so it cannot disagree with the section it summarises. Where a section refuses to state a
    figure, the tile refuses in the same words rather than showing a zero.
    """
    me = data["me"]
    g, e, a = data.get("ghost"), data.get("escrow"), data.get("approvals") or {}
    sub = data.get("submissions") or {}
    led = sub.get("ledger") or {}

    owed = money(data["direct"], True) if data["direct"] else money(0, True)
    figs = _figure("What you're owed", owed,
                   f'{pct(data["rate"])} of {money(data["activeMRR"])}/mo, paid the 2nd Friday'
                   if data["activeMRR"] else "no active referred clients yet")
    pend = len(a.get("pending", []))
    figs += _figure("Waiting on you",
                    f'{pend}' if pend else "Nothing",
                    "first-contact drafts to approve" if pend else "nothing needs your sign-off",
                    kind="" if pend else "none")
    figs += _figure("Your rung", esc(me.get("rung") or "—"),
                    esc((me.get("rungName") or "not joined")), kind="sm")
    if e and e.get("breaches"):
        figs += _figure("What we owe you", money(e["owed"], True),
                        f'{len(e["breaches"])} time(s) we cost you something')
    elif g and not g.get("enough"):
        figs += _figure("How fast we moved", "No figure", "not enough of our own history yet",
                        kind="none")
    elif g:
        figs += _figure("How fast we moved", money(g["commissionGap"], True),
                        "what your book would be worth at our own normal pace")
    else:
        figs += _figure("What we owe you", "Nothing", "we've handled everything on time", kind="none")

    todo = _needs_you(data)
    if todo:
        items = "".join(
            f'<li><button class="lnk" data-goto="{esc(room)}"><strong>{esc(what)}</strong>'
            f'<span> — {esc(why)}</span></button></li>' for what, why, room in todo)
        need = (f'<h3 style="margin-top:34px">Waiting on you</h3><ul class="todo">{items}</ul>')
    else:
        need = ('<h3 style="margin-top:34px">Nothing is waiting on you</h3>'
                '<p class="lede">No drafts to approve, no training open, no notes outstanding. '
                'This is the normal state — the console is a record, not a queue you have to work.</p>')

    bounty = ""
    if led.get("earned"):
        bounty = (f'<p class="fine" style="border-top:0;padding-top:0;margin-top:22px">'
                  f'Plus <strong>{money(led["earned"], True)}</strong> of submission bounty accrued '
                  f'— staged with the rest of the program and not payable until it launches.</p>')

    return _section(
        f'<div class="tick"></div><h2>{esc(data["me"]["connector"].split(" (")[0])}, here is where you stand</h2>'
        f'<p class="lede">Every figure below is computed from yourco\'s own records, and every one of '
        f'them links to the arithmetic behind it. Where we cannot defend a number, this page says so '
        f'instead of showing you a zero.</p>'
        f'<div class="figures">{figs}</div>'
        f'{need}{bounty}', "head")


def _us_placeholder(data):
    """Shown when yourco has nothing to be graded on yet. Deliberately NOT hidden.

    The three sections in this room each self-hide with no data, which left a rail item that opened
    a blank page. Hiding the room instead would be worse: this is the half of the console where
    yourco is the one being measured, and quietly removing it whenever there is nothing to answer
    for is exactly the move the section exists to rule out.
    """
    n = len(data["refs"])
    return _section(
        '<div class="tick"></div><h2>How we\'re doing</h2>'
        '<p class="lede">This room is where <strong>yourco</strong> gets measured — how fast we moved '
        'your referrals against our own normal pace, what we owe you when we mishandle a contact, and '
        'how good your own read turns out to be.</p>'
        f'<div class="figures">{_figure("Nothing to report yet", "No figure", (
            "you have no referrals on the board, so there is nothing for us to be graded on"
            if not n else
            "we have not handled enough of your referrals yet to say anything we could defend"),
            kind="none")}</div>'
        '<p class="fine">It stays here, empty, rather than disappearing. A page that hides the section '
        'where the vendor is the one being judged — precisely when there is nothing good to show — '
        'would be the opposite of the point.</p>', "head")


def _rail(data, rooms=None):
    """Five rooms. The only count that is coloured is the one that means something needs doing.

    `rooms` is the built content, so the rail can never offer a room that opens on nothing.
    """
    a = data.get("approvals") or {}
    counts = {"book": len(a.get("pending", [])),
              "money": len([r for r in data["refs"] if r["live"]]) or None,
              "us": None, "account": None, "overview": None}
    due = {"book"}
    items = ""
    live = [r for r in ROOMS if rooms is None or (rooms.get(r[0]) or "").strip()]
    for i, (key, label) in enumerate(live, 1):
        c = counts.get(key)
        ct = (f'<span class="ct{" due" if (key in due and c) else ""}">{c}</span>'
              if c else "")
        items += (f'<button class="rnav{" active" if i == 1 else ""}" data-room="{key}">'
                  f'<span class="n">{i}</span><span>{esc(label)}</span>{ct}</button>')
    return (f'<aside class="rail"><div class="rail-lbl">Sections</div>'
            f'<nav class="rail-nav">{items}</nav></aside>')


ROOM_JS = """
<script>
(function(){
  const rooms = document.querySelectorAll(".room");
  const navs  = document.querySelectorAll(".rnav");
  function go(key, push){
    rooms.forEach(r => r.classList.toggle("on", r.dataset.room === key));
    // A room that was display:none never tripped the scroll-reveal observer, so its content would
    // switch in at opacity 0 and stay there. Showing a room reveals it outright.
    document.querySelectorAll(".room.on .reveal").forEach(el => el.classList.add("in"));
    navs.forEach(n => n.classList.toggle("active", n.dataset.room === key));
    if(push !== false && location.hash.slice(1) !== key) history.replaceState(null,"","#"+key);
    window.scrollTo({top:0, behavior:"instant"});
  }
  navs.forEach(n => n.addEventListener("click", () => go(n.dataset.room)));
  document.querySelectorAll("[data-goto]").forEach(b =>
    b.addEventListener("click", () => go(b.dataset.goto)));
  // A deep link has to survive a reload — a connector sent to their approvals should land there.
  const want = location.hash.slice(1);
  go([...navs].some(n => n.dataset.room === want) ? want : "overview", false);
})();
</script>
"""


def _ghost_section(data):
    """yourco graded against its own median pace — the one section on this page that is about US.

    The hardest thing to render honestly here is the refusal: when there is no defensible figure the
    section must NOT quietly print $0, because zero and "we won't say" mean opposite things and the
    flattering one is the wrong default.
    """
    g = data.get("ghost")
    if not g or not g["rows"]:
        return ""
    if g["enough"]:
        head = _figure("The difference to you", money(g["commissionGap"], True),
                       "what your book would be worth today if we had moved every one of your "
                       "referrals at our own normal speed")
    else:
        head = _figure("The difference to you", "No figure", g["why"], kind="none")
    head += _figure("Behind our own pace", str(g["behind"]) if g["behind"] else "None",
                    "referrals we have been slower on than usual", kind="sm" if g["behind"] else "none")
    head += _figure("Ahead of it", str(g["ahead"]) if g["ahead"] else "None",
                    "we moved these faster than we normally do", kind="sm" if g["ahead"] else "none")

    rows = ""
    for r in g["rows"]:
        if r["commissionGap"] is not None:
            gap = money(r["commissionGap"], True)
        else:
            gap = ('<span class="muted">no figure — we haven\'t run enough deals through '
                   f'{esc(", ".join(r["unpricedRungs"]))} to know our own pace</span>')
        where = (f'{esc(r["real"])} → should be <strong>{esc(r["ghost"])}</strong>'
                 if r["rungsBehind"] else
                 (f'{esc(r["real"])} — <strong>ahead of our own pace</strong>' if r["rungsAhead"]
                  else f'{esc(r["real"])} — on pace'))
        rows += (f'<tr><td><strong>{esc(r["company"])}</strong><div class="sub">{where}</div></td>'
                 f'<td class="num">{gap}</td></tr>')

    return _section(
        f'<div class="tick"></div><h2>How fast we moved your referrals</h2>'
        f'<p class="lede">This section grades <strong>yourco</strong>, not you. We reconstruct where '
        f'each of your referrals would be today if we had moved it at the speed we normally move our '
        f'own deals — and show you the difference in your commission. If we sat on one of your '
        f'introductions, this is where you find out.</p>'
        f'<div class="figures">{head}</div>'
        f'<table class="tbl" style="margin-top:30px"><thead><tr><th>Your referral</th>'
        f'<th class="num">Difference to you</th></tr></thead><tbody>{rows}</tbody></table>'
        f'<p class="fine"><strong>This is not money you are owed.</strong> It is what your book would '
        f'be worth on our own averages — an estimate of pace, not a bill, and a referral can be behind '
        f'pace for reasons that are nobody\'s fault. We show it because you have no other way of '
        f'telling the difference between a business that went quiet and a vendor that dropped it.</p>'
        f'<p class="fine">Where we have not run enough deals through a stage to know our own median, '
        f'you get the position and <strong>no dollar figure</strong> — we would rather leave it '
        f'unclaimed than invent it. Today {esc(str(g.get("measuredRungs")))} of '
        f'{esc(str(g.get("totalRungs")))} stages are measured.</p>', "head")


def _approvals_section(data):
    """The connector's gate on yourco's first message — and the rung they earn their way up."""
    a = data.get("approvals")
    if not a:
        return ""
    r = a["rung"]
    steps = ""
    for rung in capr.RUNGS:
        on = "on" if rung["n"] <= r["n"] else ""
        steps += (f'<div class="step {on}">{esc(rung["key"])}'
                  f'<span class="s-name">{esc(rung["name"])}</span></div>')

    pend = ""
    for p in a["pending"]:
        pend += (
            f'<div class="rec" data-approval="{esc(p["id"])}">'
            f'<div class="rechead"><h3>{esc(p["business"])}</h3>'
            + (f'<span class="tag live">goes out {esc((p.get("releaseAfter") or "")[:16])} '
               f'unless you stop it</span>' if p.get("releaseAfter") else
               '<span class="tag">waiting on you</span>')
            + f'</div>'
            f'<div class="editrow">'
            f'<label>What we plan to send<textarea data-a="draft" rows="5">{esc(p["draft"])}</textarea></label>'
            f'<div class="saveline">'
            f'<button class="btn" data-approve="approved">Send it as written</button> '
            f'<button class="btn" data-approve="edited">Save my edits and send that</button> '
            f'<button class="btn" data-approve="declined">Don\'t contact them</button>'
            f'<span class="status"></span></div></div></div>')
    if not pend:
        pend = ('<div class="empty"><h3>Nothing waiting on you</h3><p>When we are ready to reach out '
                'to someone you sent us, the exact message appears here first.</p></div>')

    hist = "".join(
        f'<tr><td>{esc(h["business"])}</td><td>{esc(h["status"])}</td>'
        f'<td>{esc((h.get("decidedAt") or "")[:10])}</td></tr>' for h in a["history"][:8])
    hist = (f'<table class="tbl"><thead><tr><th>Business</th><th>You said</th><th>When</th></tr>'
            f'</thead><tbody>{hist}</tbody></table>') if hist else ""

    nxt = ""
    if r["next"] and not r["held"]:
        nxt = (f'<p class="muted">{r["needed"]} more approved without edits and you move to '
               f'<strong>{esc(r["next"]["key"])} · {esc(r["next"]["name"])}</strong> — '
               f'{esc(r["next"]["what"])}</p>')
    elif r["held"]:
        nxt = ('<p class="muted">You have asked to review every message. That stands until you say '
               'otherwise — we will not move you off it.</p>')

    return _section(
        f'<div class="tick"></div><h2>What we say to the people you send us</h2>'
        f'<p class="lede">When you hand us a contact, we are about to use <strong>your name</strong> '
        f'with somebody who trusts you. So you see the first message before they do — and you can '
        f'change it, or stop it.</p>'
        f'<div class="ladder">{steps}</div>'
        f'<p class="lede" style="margin-top:14px"><strong>{esc(r["key"])} · {esc(r["name"])}</strong> — '
        f'{esc(r["what"])}</p>{nxt}'
        f'{pend}{hist}'
        f'<p class="fine">You earn your way off this gate the same way our own agents do: on evidence. '
        f'Approvals with no edits move you up; <strong>a complaint from anyone you referred puts you '
        f'straight back to reviewing every message</strong>, and one click puts you back there any '
        f'time you want. Editing a draft is not a mark against you — it tells us we got the tone wrong '
        f'about someone you actually know, which is the most useful thing you can send us.</p>', "head")


def _calibration_section(data):
    """Their judgment, measured. The refusal below the sample floor is the whole credibility of it."""
    c = data.get("calibration")
    if not c or (not c["resolved"] and not c["open"]):
        return ""
    if not c["enough"]:
        body = f'<div class="totalbox"><p class="big">Not yet</p><p class="muted">{esc(c["why"])}</p></div>'
    else:
        band_rows = "".join(
            f'<tr><td>You said {b["lo"]}–{b["hi"]}%</td><td class="num">{b["n"]}</td>'
            f'<td class="num">{b["hits"]}</td>'
            f'<td class="num">{b["actual"]:.0f}%</td></tr>'
            for b in c["bands"] if b["n"])
        # `why` already carries the bias sentence; the muted line adds the numbers behind it and must
        # not repeat it back.
        body = (f'<div class="totalbox"><p class="big">{esc(c["why"])}</p>'
                f'<p class="muted">{c["resolved"]} resolved · {c["open"]} still open · '
                f'{c["baseRate"]:.0f}% of them became clients · Brier score {c["brier"]} '
                f'(0 is perfect, 0.25 is what saying "50%" every time gets you)</p></div>'
                f'<table class="tbl"><thead><tr><th>When you said</th><th class="num">Times</th>'
                f'<th class="num">Became clients</th><th class="num">Actually</th></tr></thead>'
                f'<tbody>{band_rows}</tbody></table>')

    pri = ""
    if c.get("priority", 1.0) > 1.0:
        pri = (f'<p class="fine"><strong>Your read is earning you priority.</strong> Because your '
               f'calls have been good, the ones you flag as strong move up our queue '
               f'(×{c["priority"]}). That is earned on being right — there is no way to move it by '
               f'sending more names.</p>')

    return _section(
        f'<div class="tick"></div><h2>How good your read is</h2>'
        f'<p class="lede">Every time you send us someone you tell us how likely you think it is to '
        f'land. We keep score — not to grade you, but because nobody has ever told a referrer whether '
        f'their instincts are actually any good, and yours are the most valuable thing you bring.</p>'
        f'{body}{pri}'
        f'<p class="fine">Below {ccal.MIN_RESOLVED} resolved referrals there is <strong>no score at '
        f'all</strong> — not a provisional one. A number off three data points would be noise dressed '
        f'up as a verdict, and this one is about your judgment. You also cannot change a call after '
        f'you have made it; a prediction you can revise once you see how it is going is not a '
        f'prediction.</p>', "parchment")


def _escrow_section(data):
    """yourco's bond against its own conduct. Renders even at zero, because zero is the good news."""
    e = data.get("escrow")
    if not e or not e.get("submissions"):
        return ""
    if not e["breaches"]:
        body = ('<div class="totalbox"><p class="big">Nothing owed</p><p class="muted">We have '
                'handled every contact you sent us inside the time we promised.</p></div>')
    else:
        rows = "".join(
            f'<tr><td><strong>{esc(cesc.BREACHES.get(b["kind"], (b["kind"],))[0])}</strong>'
            f'<div class="sub">{esc(b.get("business") or "")} — {esc(b.get("detail") or "")}</div></td>'
            f'<td class="num">{money(cesc.ESCROW_PER_BREACH)}</td></tr>' for b in e["breaches"])
        body = (f'<div class="totalbox"><p class="big">{money(e["owed"], True)}</p>'
                f'<p class="muted">{len(e["breaches"])} time(s) we cost you something — '
                f'{e["computedCount"]} we caught ourselves, {e["loggedCount"]} logged by hand</p></div>'
                f'<table class="tbl"><thead><tr><th>What we did</th><th class="num">To you</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>')

    staged = ('<div class="staged"><strong>Accrued, not payable.</strong> Like everything else in this '
              'program, nothing is owed or payable until it launches.</div>') if not e["payable"] else ""

    return _section(
        f'<div class="tick"></div><h2>When we let you down</h2>'
        f'<p class="lede">When you send us someone you know, you are spending a relationship you may '
        f'need again. If we waste it — sit on the contact, never call, open badly — that costs you '
        f'something real, and no referral program on earth records it. We do, against ourselves.</p>'
        f'{staged}{body}'
        f'<p class="fine"><strong>This is not a guarantee that referrals close.</strong> Sample Company 46 say '
        f'no; that is normal and nothing is owed for it. This is only for the times the problem was '
        f'<em>us</em>.</p>'
        f'<p class="fine">Two of these we catch automatically — the same timestamps that prove we hit '
        f'the {cesc.SLA_VERIFY_HOURS}-hour promise also prove when we missed it, so we cannot quietly '
        f'not notice. For a bad conversation we depend on you telling us, and that asymmetry is worth '
        f'saying out loud rather than hiding.</p>', "parchment")


def _perk_section(data):
    """The own-OS grant. Renders the distance when short, and the commitment when earned."""
    p = data.get("perk")
    if not p:
        return ""
    if p["status"] == "not_yet" and p["liveClients"] == 0:
        return ""                                   # nothing to dangle at someone with no book yet
    if p["status"] == "not_yet":
        box = (f'<div class="totalbox"><p class="big">{p["liveClients"]} of {p["threshold"]}</p>'
               f'<p class="muted">{esc(p["why"])}</p></div>')
    else:
        state = {"earned": "Earned — not started yet", "scoped": "Being scoped now",
                 "live": "Running", "ended": "Ended"}.get(p["status"], p["status"])
        box = (f'<div class="totalbox"><p class="big">{esc(state)}</p>'
               f'<p class="muted">{esc(p["why"])}</p></div>')
    return _section(
        f'<div class="tick"></div><h2>Your own AI OS</h2>'
        f'<p class="lede">At <strong>{p["threshold"]} live referred clients</strong>, yourco builds and '
        f'operates an AI OS for <strong>your</strong> business — the same thing we sell, running your '
        f'pipeline, your follow-ups and your admin, free while you are active with us.</p>'
        f'{box}'
        f'<p class="fine">Why we can afford to: {p["threshold"]} live clients is at least '
        f'{money(p["bookAtThreshold"])}/mo of revenue you brought us. The system costs us less than '
        f'that, and you become someone who can say <em>"I run my business on this"</em> — which is '
        f'worth more to us than any commission rate.</p>'
        f'<p class="fine">Once you have earned it, it stays while you are an active connector — if a '
        f'client of yours churns we do not switch your business off. Building it is people, not a '
        f'switch, so "earned" and "running" are shown separately and the gap is a commitment we owe '
        f'you.</p>', "parchment")


def _tier_section(data):
    """Commission tier progress — and what the next tier is worth ON TODAY'S BOOK. Never a projection."""
    t = data["tierProgress"]
    strip = ""
    for s in t["steps"]:
        on = "on" if s["tier"] <= t["tier"] else ""
        strip += (f'<div class="step {on}">{pct(s["rate"])}'
                  f'<span class="s-name">{esc(s["name"])} · {esc(s["band"])}</span></div>')

    if not t["next"]:
        nxt = ('<h3>You are at the top rate</h3>'
               '<p>Tier 3 is the highest commission rate in the program. Beyond rate, what grows is '
               'agency — that is the rung ladder above, not this table.</p>')
    elif t["mrr"] <= 0:
        nxt = (f'<h3>Next tier — {esc(t["next"]["name"])} at {pct(t["next"]["rate"])}</h3>'
               f'<p>{esc(t["gapText"])} moves your whole book '
               f'to {pct(t["next"]["rate"])} — every client, not just the new ones. You have no active '
               f'book yet, so there is no "what it would be worth" figure to show you, and yourco will '
               f'not invent one.</p>')
    else:
        nxt = (f'<h3>Next tier — {esc(t["next"]["name"])} at {pct(t["next"]["rate"])}</h3>'
               f'<p>{esc(t["gapText"])} moves your '
               f'<strong>whole book</strong> to {pct(t["next"]["rate"])} — every client you already have, '
               f'not just the new ones.</p>'
               f'<div class="bar"><span style="width:{t["pct"]}%"></span></div>'
               f'<div class="barnote">{money(t["mrr"])} of {money(t["next"]["from"])} a month</div>'
               f'<p class="math" style="margin-top:14px">{money(t["mrr"])} × '
               f'({pct(t["next"]["rate"])} − {pct(t["rate"])}) = '
               f'<strong>{money(t["uplift"], True)}/mo more</strong> on today\'s book</p>'
               f'<p class="fine" style="border-top:0;padding-top:8px;margin-top:8px">That figure is the '
               f'rate change applied to the book you have <em>today</em>. It deliberately excludes what '
               f'the new clients themselves would pay — yourco does not know that number, so it will not '
               f'show you one.</p>')

    return _section(
        f'<div class="tick"></div><h2>Your commission tier</h2>'
        f'<p class="lede">Tier {t["tier"]} · <strong>{esc(t["name"])}</strong> · {pct(t["rate"])} · '
        f'{money(t["mrr"])}/mo across {t["active"]} active referred '
        f'client{"s" if t["active"] != 1 else ""}. The tier is set by <strong>how much live, paying '
        f'revenue</strong> you have referred — not how many logos — and the rate applies to your '
        f'entire book, not just the client that crossed the threshold.</p>'
        f'<div class="ladder">{strip}</div>'
        f'<div class="cols"><div class="card">{nxt}</div>'
        f'<div class="card"><h3>How the tier is decided</h3>'
        f'<p>Computed from yourco\'s records: a referred client counts once it is <strong>live and '
        f'paying</strong>, and your tier is the total monthly revenue of those clients — not how many '
        f'of them there are. Two clients at {money(15000)} each earn the same rate as ten at '
        f'{money(3000)}.</p>'
        f'<p style="margin-top:10px">It moves down as well as up. If a client churns your book falls '
        f'and the tier recalculates honestly — this page will show you that the same day it '
        f'happens.</p></div></div>')


def _goals_section(data):
    """Targets the connector sets; currents the CRM proves. Mirrors HQ's Goals tab honesty."""
    g = data["goals"]
    rows = ""
    for k, meta in writes.GOAL_METRICS.items():
        cur = g["currents"].get(k)
        tgt = g["targets"].get(k)
        fmt = (lambda v: "—" if v is None else (money(v) + "/mo" if meta["kind"] == "money"
                                                else f"{v:g}"))
        p = None if not tgt else min(100, int(round(100 * (cur or 0) / tgt)))
        if tgt is None:
            pace = "no target set"
            cls = ""
        elif g["pctElapsed"] is None:
            pace, cls = f"{p}% of target", ""
        else:
            ahead = p >= g["pctElapsed"]
            pace = f'{p}% of target · {"ahead of" if ahead else "behind"} pace ({g["pctElapsed"]}% of the quarter gone)'
            cls = "ahead" if ahead else "behind"
        rows += (f'<div class="grow"><span class="gm">{esc(meta["label"])}</span>'
                 f'<span class="gc">{fmt(cur)}</span>'
                 f'<span class="gt"><input type="number" step="any" min="0" data-goal="{esc(k)}" '
                 f'value="{"" if tgt is None else f"{tgt:g}"}" placeholder="set target"></span>'
                 f'<span class="gpb{"" if tgt else " unset"}"><i style="width:{p or 0}%"></i></span>'
                 f'<span class="gpace {cls}">{esc(pace)}</span></div>')

    set_note = (f'Last set {esc(g["updated"][:10])} by {esc(g["updatedBy"])}.'
                if g["updated"] else
                'You have not set any targets yet. Nothing is pre-filled and nothing is suggested — '
                'a target you did not choose is not a goal.')
    return _section(
        f'<div class="tick"></div><h2>Your goals</h2>'
        f'<p class="lede">Targets are yours to set for <strong>{esc(g["label"])}</strong>. The current '
        f'column is not self-reported — it is computed from yourco\'s records on every load, which is '
        f'why a goal here cannot be fudged. {set_note}</p>'
        f'<div class="goalgrid" data-goals-for="{esc(data["me"]["connector"])}">'
        f'<div class="grow ghead"><span class="gm">Metric</span><span class="gc">Now</span>'
        f'<span class="gt">Target</span><span class="gpb"></span><span class="gpace">Pace</span></div>'
        f'{rows}</div>'
        f'<div class="saveline"><button class="btn" data-save="goals">Save targets</button>'
        f'<span class="status"></span></div>'
        f'<p class="fine">Leave a target blank to clear it. "Now" is your live book as it stands today, '
        f'not a quarter-to-date count — yourco\'s attribution log starts recording movement the moment '
        f'your first referral is registered, and until then there is no in-quarter history to slice. '
        f'Every target you set is written to yourco\'s records and appears on your history below, so a '
        f'goal cannot be quietly rewritten after the fact.</p>')


def _bars(rows, fmt=None):
    """A simple by-month bar list. `rows` = [(label, value)]. Empty in → empty out (never faked)."""
    if not rows:
        return ""
    mx = max(v for _l, v in rows) or 1
    fmt = fmt or (lambda v: f"{v:g}")
    return "".join(f'<div class="mrow"><span class="ml">{esc(l)}</span>'
                   f'<span class="mb"><i style="width:{max(2, int(100 * v / mx))}%"></i></span>'
                   f'<span class="mv">{esc(fmt(v))}</span></div>' for l, v in rows)


def _reporting_section(data):
    """Performance over time, built from the attribution log — the log IS the history."""
    rep = data["reporting"]
    months = rep["months"]

    total = rep["funnel"][0][1]
    if total:
        fn = ""
        prev = None
        for label, v in rep["funnel"]:
            w = int(round(100 * v / total)) if total else 0
            conv = "" if prev is None else (f' · {int(round(100 * v / prev))}% of the step before'
                                            if prev else " · —")
            fn += (f'<div class="frow"><span class="fl">{esc(label)}</span>'
                   f'<span class="fb"><i style="width:{max(w, 2)}%"></i></span>'
                   f'<span class="fv">{v}{conv}</span></div>')
            prev = v
        funnel = f'<h3>Where your referrals got to</h3><div class="funnel">{fn}</div>'
    else:
        funnel = ('<h3>Where your referrals got to</h3>'
                  '<p>No referrals yet, so there is no funnel to draw. This chart fills itself in from '
                  'your real records — it will never show a shape you did not produce.</p>')

    if rep["hasReferralHistory"]:
        by_month = ('<h3>Referrals by month</h3>'
                    + f'<div class="months">{_bars([(m, v["referrals"]) for m, v in months.items()])}</div>')
    else:
        by_month = ('<h3>Referrals by month</h3>'
                    '<p>Your attribution log has no referral events yet. The first bar appears the month '
                    'your first referral is registered — yourco does not backfill or estimate this.</p>')

    if rep["hasMoney"]:
        earned = ('<h3>Commission by month</h3>'
                  + f'<div class="months">{_bars([(m, v["commission"]) for m, v in months.items()], lambda v: money(v, True))}</div>')
    else:
        earned = ('<h3>Commission by month</h3>'
                  '<p>No payout has ever been computed on your account — the connector program has not '
                  'launched, so there is nothing to chart. When it does, every month lands here from the '
                  'same log that records the payment itself.</p>')

    o = rep["downlineNow"]
    if o["people"]:
        dl = (f'<h3>Downline contribution</h3>'
              f'<p>Your downline currently carries {money(o["mrr"])}/mo of active client revenue across '
              f'{len(o["people"])} connector{"s" if len(o["people"]) != 1 else ""}. There is no '
              f'month-by-month history because no override has ever been computed — the override is '
              f'<strong>counsel-gated and not payable</strong>, and this figure is informational only.</p>')
    else:
        dl = ('<h3>Downline contribution</h3>'
              '<p>You have no downline, so there is nothing to report here.</p>')

    return _section(
        f'<div class="tick"></div><h2>Your reporting</h2>'
        f'<p class="lede">Your own performance over time, assembled from the append-only attribution '
        f'log below — the same immutable record yourco pays from. Where the log is empty, this section '
        f'says so rather than filling the space.</p>'
        f'<div class="cols"><div class="card">{funnel}</div><div class="card">{by_month}</div></div>'
        f'<div class="cols"><div class="card">{earned}</div><div class="card">{dl}</div></div>',
        "parchment")


def _phantom_section(data):
    """DARK BY DEFAULT — returns '' unless meta.phantomTrack names this connector.

    Binding display rules (`decisions/2026-08-07_phantom-shares-supersede-equity-track.md`):
    factual progress only; no projected payout, no valuation, no dollar value for the units; explicit
    statements that it is discretionary, that no units exist until a definitive plan document is
    executed, and that nothing shown is a grant, an offer, or a guarantee.
    """
    p = data.get("phantom")
    if not p:
        return ""
    bands = "".join(
        f'<tr><td>{money(t)}</td><td class="num">{esc(units)}</td>'
        f'<td class="num">{"reached" if p["measured"] >= t else "not reached"}</td></tr>'
        for t, units in p["bands"])
    if p["lines"]:
        detail = "".join(f'<tr><td>{esc(l["company"])}</td><td class="num">{money(l["mrr"])}/mo</td>'
                         f'<td class="num math">× {l["months"]} mo</td>'
                         f'<td class="num">{money(l["amount"])}</td></tr>' for l in p["lines"])
        math = (f'<table><tr><th>Active referred client</th><th class="num">Retainer</th>'
                f'<th class="num">Months in the last 12</th><th class="num">Counted</th></tr>{detail}'
                f'<tr class="total"><td>Measured</td><td></td><td></td>'
                f'<td class="num">{money(p["measured"])}</td></tr></table>')
    else:
        math = ('<p>Your measured figure is <strong>$0</strong> — you have no referred client that is '
                'still active today. This is a measurement, not a judgement, and it moves the moment '
                'that changes.</p>')

    return _section(
        f'<div class="gated"><div class="flag">Discretionary · not a grant · not an offer</div>'
        f'<h3>Phantom share track</h3>'
        f'<p>yourco maintains a discretionary phantom-share track for connectors who build a durable '
        f'book. It is shown to you because the Founder turned it on for your account specifically. Read all of '
        f'this before you read the numbers.</p>'
        f'<p style="margin-top:12px"><strong>What this is not:</strong> <strong>no units exist</strong>. '
        f'There is no plan document in force, and none of this is a grant, an offer, a promise, or a '
        f'guarantee of anything. Nothing here entitles you to anything. The track is entirely '
        f'discretionary; it is subject to counsel, and it may be changed or withdrawn at any time before '
        f'a definitive plan document is executed. <strong>Until such a document is executed and signed, '
        f'you have nothing.</strong></p>'
        f'<p style="margin-top:12px">What is shown below is <strong>one factual measurement</strong>: '
        f'your net-retained referred revenue over the trailing {TRAILING_MONTHS} months — revenue from '
        f'clients you referred that are <em>still active today</em> — against the thresholds the track '
        f'uses. yourco will not show you a projected payout, a company valuation, or a dollar value for '
        f'any unit, because no honest number of that kind exists.</p>'
        f'<h3 style="margin-top:22px">Your measured figure — {money(p["measured"])}</h3>'
        f'{math}'
        f'<div class="bar" style="margin-top:16px"><span style="width:{p["pctFirst"]}%"></span></div>'
        f'<div class="barnote">{money(p["measured"])} of {money(p["bands"][0][0])} — the first threshold</div>'
        f'<h3 style="margin-top:22px">The thresholds</h3>'
        f'<table><tr><th>Trailing-12-month net-retained referred revenue</th>'
        f'<th class="num">Band</th><th class="num">Your status</th></tr>{bands}</table>'
        f'<p style="margin-top:14px">Reaching a threshold does not create anything. It is a level of '
        f'production the track measures, nothing more — the decision to grant, and the terms of any '
        f'grant, sit entirely with yourco and its counsel.</p></div>')


def _downline_section(data):
    """The upline view — production, pipeline, goals (editable) and reporting for each downline member."""
    dl = data["downline"]
    if not dl:
        return ""
    cards = ""
    for m in dl:
        pipe = ("".join(f'<span class="pill">{esc(s)} · {n}</span>' for s, n in m["pipeline"])
                or '<span class="pill muted">nothing in progress</span>')
        g = m["goals"]
        grows = ""
        for k, meta in writes.GOAL_METRICS.items():
            cur = g["currents"].get(k)
            tgt = g["targets"].get(k)
            fmt = (lambda v: "—" if v is None else (money(v) + "/mo" if meta["kind"] == "money"
                                                    else f"{v:g}"))
            p = None if not tgt else min(100, int(round(100 * (cur or 0) / tgt)))
            grows += (f'<div class="grow"><span class="gm">{esc(meta["label"])}</span>'
                      f'<span class="gc">{fmt(cur)}</span>'
                      f'<span class="gt"><input type="number" step="any" min="0" data-goal="{esc(k)}" '
                      f'value="{"" if tgt is None else f"{tgt:g}"}" placeholder="set target"></span>'
                      f'<span class="gpb{"" if tgt else " unset"}"><i style="width:{p or 0}%"></i></span>'
                      f'<span class="gpace">{"" if p is None else f"{p}% of target"}</span></div>')
        hist = m["referralsByMonth"]
        rep = (f'<div class="months">{_bars(sorted(hist.items()))}</div>' if hist else
               '<p class="fine" style="border-top:0;padding-top:0">No referral events on their log yet.</p>')
        if m["via"] == data["me"]["connector"]:
            via = "Recruited by you."
        elif m["via"]:
            via = "Recruited by " + esc(m["via"]) + "."   # always someone else in your own downline
        else:
            via = ""
        cards += (
            f'<div class="dl" data-goals-for="{esc(m["name"])}">'
            f'<div class="rechead"><h3>{esc(m["name"])}</h3>'
            f'<span class="tag">{esc(m["rung"] or "—")} · {esc(m["rungName"])}</span></div>'
            f'<p class="fine" style="border-top:0;padding-top:0;margin-top:4px">{via}</p>'
            f'<div class="kvs">'
            f'<div class="kv"><span class="k">Active clients</span><span class="v">{m["clients"]}</span></div>'
            f'<div class="kv"><span class="k">Active revenue</span><span class="v">{money(m["mrr"])}/mo</span></div>'
            f'<div class="kv"><span class="k">Referrals</span><span class="v">{m["referrals"]}</span></div>'
            f'<div class="kv"><span class="k">Conversations</span><span class="v">{m["conversations"]}</span></div>'
            f'</div>'
            f'<h4>Pipeline</h4><div class="pills">{pipe}</div>'
            f'<h4>Their goals — {esc(g["label"])}</h4><div class="goalgrid">{grows}</div>'
            f'<div class="saveline"><button class="btn" data-save="goals">Save their targets</button>'
            f'<span class="status"></span></div>'
            f'<h4>Their referrals by month</h4>{rep}'
            f'</div>')

    return _section(
        f'<div class="tick"></div><h2>Your downline</h2>'
        f'<p class="lede">{len(dl)} connector{"s" if len(dl) != 1 else ""} in your downline, at every '
        f'depth. You can see what they are producing, what is in their pipeline, and how they are '
        f'tracking against their goals — and you can help set those goals. Every target you set for '
        f'someone else is written to their history with your name on it, so nobody is ever surprised by '
        f'a goal they did not choose.</p>'
        f'<div class="dls">{cards}</div>'
        f'<p class="fine">What you see here is deliberately bounded: their rung, their production, their '
        f'pipeline as stage counts, and their goals. You do <strong>not</strong> see their clients by '
        f'name, what any individual client pays them, or what they earn — that is theirs, exactly as '
        f'your book is yours and no upline of yours sees it either.</p>')


def _earnings_section(data):
    me, rate = data["me"], data["rate"]
    tiers = data["tiers"]
    n = me["book"]["active"]
    # Same source as the tier section and the statement — this used to keep its own count thresholds
    # and went stale when the basis moved to MRR on 2026-08-13.
    _nrate, _gap = stmts_mod.tier_progress_note(
        {"active": [{"mrr": r["mrr"]} for r in data["refs"] if r["live"]]}, tiers)
    nudge = f"{_gap} → {pct(_nrate)}" if _nrate else _gap

    if not any(r["live"] for r in data["refs"]):
        body = ('<div class="empty"><h3>Nothing owed yet — $0.00</h3>'
                f'<p>Commission is computed on retainers yourco has actually collected from clients you '
                f'referred. You have no active referred clients, so the number is zero. When that changes, '
                f'this page will show the arithmetic line by line: your rate ({pct(rate)}) × each client\'s '
                f'monthly retainer.</p></div>')
    else:
        rows = ""
        for r in data["refs"]:
            if not r["live"]:
                continue
            rows += (f'<tr><td>{esc(r["company"])}</td><td class="num">{money(r["mrr"])}/mo</td>'
                     f'<td class="num math">× {pct(rate)}</td>'
                     f'<td class="num">{money(r["commission"], True)}</td></tr>')
        rows += (f'<tr class="total"><td>Direct commission</td>'
                 f'<td class="num">{money(data["activeMRR"])}/mo</td>'
                 f'<td class="num math">× {pct(rate)}</td>'
                 f'<td class="num">{money(data["direct"], True)}/mo</td></tr>')
        body = (f'<table><tr><th>Active referred client</th><th class="num">Their retainer</th>'
                f'<th class="num">Your rate</th><th class="num">Your commission</th></tr>{rows}</table>'
                f'<p class="math" style="margin-top:14px">{money(data["activeMRR"])} × {pct(rate)} = '
                f'{money(data["direct"], True)} per month</p>')

    _figs = (_figure("Per month", money(data["direct"], True),
                     f'{pct(rate)} of {money(data["activeMRR"])} collected')
             + _figure("Active referred clients", str(n), "live and paying", kind="sm")
             + _figure("Next payday", "2nd Friday", "on revenue collected by then", kind="sm"))
    return _section(
        f'<div class="tick"></div><h2>What you\'re owed</h2>'
        f'<div class="figures">{_figs}</div>'
        f'<p class="lede" style="margin-top:26px">Tier {me["book"]["tier"]} · <strong>{rate}%</strong> · '
        f'{money(data["activeMRR"])}/mo across {n} active referred '
        f'client{"s" if n != 1 else ""} · next tier: {esc(nudge)}. Your rate is set by the live, paying '
        f'revenue you have referred — not the number of clients — and applies to your whole book.</p>'
        f'{body}'
        f'<p class="fine">Paid the second Friday of the month, on revenue yourco has collected — clients '
        f'pay on the 1st, a three-day collection window closes the books, and anything collecting late '
        f'rolls to the next payday. This is the same computation that produces your monthly statement and '
        f'the payment itself; there is no second set of books.</p>', "head")


def _override_section(data):
    o = data["override"]
    if not o["people"]:
        inner = ('<p>You have not recruited any connectors. Recruiting unlocks at <strong>R2 · Producing</strong> '
                 '— once you have a referred client live and retained. Until then there is no downline and '
                 'nothing to show here.</p>')
    else:
        rows = "".join(f'<tr><td>{esc(p["name"])}</td><td class="num">{p["clients"]}</td>'
                       f'<td class="num">{money(p["mrr"])}/mo</td></tr>' for p in o["people"])
        inner = (f'<p>These are the connectors in your downline and the active client revenue their books '
                 f'carry — the only figures the override arithmetic needs. You do not see their commissions, '
                 f'their clients, or anything else about them.</p>'
                 f'<table><tr><th>Connector</th><th class="num">Active clients</th>'
                 f'<th class="num">Their active revenue</th></tr>{rows}'
                 f'<tr class="total"><td>Downline total</td><td class="num">'
                 f'{sum(p["clients"] for p in o["people"])}</td>'
                 f'<td class="num">{money(o["mrr"])}/mo</td></tr></table>'
                 f'<p class="math" style="margin-top:12px">{money(o["mrr"])} × {pct(o["pct"])} = '
                 f'{money(o["amount"], True)} per month</p>')
    return _section(
        f'<div class="gated"><div class="flag">Informational · counsel-gated · not payable</div>'
        f'<h3>Downline override — {pct(o["pct"])}</h3>'
        f'{inner}'
        f'<p style="margin-top:14px"><strong>Read this part carefully:</strong> the downline override is '
        f'<strong>counsel-gated and not payable</strong> until it is cleared. It is shown here for '
        f'information only. It is not owed to you, it is not included in any total on this page, and it '
        f'may change or be withdrawn before the program launches.</p></div>', "quiet")


def _training_ladder(data):
    """The rung-by-rung training progress strip — what is done, what is next, what is still ahead."""
    rows = ""
    for b in data["training"]["rungs"]:
        if b["complete"]:
            state, cls = "complete", "live"
        elif not b["visible"]:
            state, cls = f'opens at {b["rung"]}', ""
        elif not b["exists"]:
            state, cls = "not written yet", ""
        else:
            state, cls = f'{b["done"]} of {b["total"]} done', ""
        when = (f' · {esc((b.get("completedAt") or "")[:10])}' if b["complete"] and b.get("completedAt")
                else "")
        pctv = 100 if b["complete"] else (int(100 * b["done"] / b["total"]) if b["total"] else 0)
        rows += (f'<div class="mrow"><div><strong>{esc(b["rung"])}</strong> · {esc(b["rungName"])}</div>'
                 f'<div class="mb"><i style="width:{pctv}%"></i></div>'
                 f'<div class="mv"><span class="tag {cls}">{esc(state)}</span>{when}</div></div>')
    return f'<div class="months">{rows}</div>'


def _learnings_section(data):
    """Training content — an index rendered from `connector-training/`, rung-aware, nothing hardcoded.

    v3: the curriculum is now a GATE, not a library. Completion is recorded here, per lesson, by the
    connector themselves, and the page says exactly what that does and does not prove.
    """
    lessons = data["lessons"]
    t = data["training"]
    if not lessons:
        return _section(
            '<div class="tick"></div><h2>Learnings</h2>'
            '<div class="empty"><h3>No lessons published yet</h3>'
            '<p>yourco\'s connector training lives in a content library this page reads. There is nothing '
            'in it right now, and this page will not invent a curriculum to look busy. Because training '
            'gates the ladder, that also means nobody can advance — which is yourco\'s problem to fix, '
            'not yours.</p></div>')

    open_n = sum(1 for L in lessons if L["open"])
    done_n = sum(1 for L in lessons if L["done"])
    items = ""
    for L in lessons:
        mins = f'{esc(L.get("minutes"))} min read' if L.get("minutes") else ""
        stub = ('<span class="tag">stub</span>' if L["stub"] else "")
        if L["open"]:
            done = ('<span class="tag live">completed</span>' if L["done"] else
                    '<span class="tag">not completed</span>')
            badge = f'{done}{stub}'
            body = f'<div class="lesson">{md_to_html(L["body"])}</div>'
            # `source:` stays in the lesson's frontmatter for internal traceability but is NEVER
            # rendered — a connector-facing page has no business showing yourco's internal file paths.
            src = ('<p class="fine">Written from yourco\'s own program documents. If anything here '
                   'contradicts your partner agreement, the agreement wins.</p>')
            # A lesson can teach a capability the HELD rung does not permit yet — say so on its face
            # rather than letting somebody read it as permission.
            notyet = ""
            if L.get("capability") and not L.get("capabilityHeld"):
                notyet = (f'<p class="fine"><strong>Reading this is not permission to do it yet.</strong> '
                          f'{UNLOCK_LABELS.get(L["capability"], esc(L["capability"]))} opens when you '
                          f'<em>hold</em> {esc(L["rung"])} — which is what completing this training does.</p>')
            if L["done"]:
                mark = (f'<div class="editrow"><p class="muted" style="font-size:14px">Completed '
                        f'{esc((L.get("doneAt") or "").replace("T", " ").replace("+00:00", " UTC"))} — '
                        f'recorded on your history. Re-read it any time; it stays open.</p></div>')
            else:
                ack = ""
                if L.get("acknowledge"):
                    ack = (f'<label style="text-transform:none;letter-spacing:normal;font-weight:400;'
                           f'font-size:14.5px;color:var(--ink-muted);margin-bottom:10px">'
                           f'<input type="checkbox" data-ack style="width:auto;display:inline-block;'
                           f'margin:0 9px 0 0;vertical-align:middle"> {esc(L["acknowledge"])}</label>')
                mark = (f'<div class="editrow" data-training="{esc(L["slug"])}">{ack}'
                        f'<div class="saveline">'
                        f'<button class="btn" data-save="training">Mark this complete</button>'
                        f'<span class="status"></span></div></div>')
            inner = (f'<details><summary>Read it{" · " + mins if mins else ""}</summary>'
                     f'{body}{notyet}{src}</details>{mark}')
        else:
            badge = (f'<span class="tag">unlocks at {esc(L["rung"])} · {esc(L["rungName"])}</span>{stub}')
            inner = (f'<p class="muted">You can see this is coming — that is deliberate. It opens when you '
                     f'reach <strong>{esc(L["rung"])} · {esc(L["rungName"])}</strong>, because it teaches '
                     f'something you cannot do before then.{" · " + mins if mins else ""}</p>')
        items += (f'<div class="rec" id="lesson-{esc(L["slug"])}">'
                  f'<div class="rechead"><h3>{esc(L.get("title") or L["slug"])}</h3>'
                  f'<span class="badges">{badge}</span></div>'
                  f'<p class="muted" style="font-size:14.5px;margin-top:8px">{esc(L.get("summary"))}</p>'
                  f'{inner}</div>')

    nudge = ""
    if t["blocked"]:
        nudge = (f'<div class="gated"><div class="flag">this is what is holding your rung</div>'
                 f'<h3>{esc(t["needed"])} training is the last thing between you and '
                 f'{esc(data["me"]["evidenceRung"])}.</h3>'
                 f'<p>Finish the {esc(t["needed"])} lessons below and the rung your referrals already '
                 f'earned becomes the rung you hold.</p></div>')

    return _section(
        f'<div class="tick"></div><h2>Learnings</h2>'
        f'<p class="lede">Every rung on the ladder has its own training, and a rung is only held once '
        f'the training below it is finished — evidence opens the lesson, the lesson releases the rung. '
        f'{open_n} of {len(lessons)} lessons are open to you; you have completed {done_n}. Locked '
        f'lessons are shown rather than hidden: you should be able to see what is ahead of you and what '
        f'it takes to get there. A lesson marked <strong>stub</strong> is short on purpose — yourco '
        f'would rather give you a true short lesson than an invented long one.</p>'
        f'{_training_ladder(data)}{nudge}'
        f'<div class="recs">{items}</div>'
        f'<p class="fine">You mark your own lessons complete, and yourco takes you at your word — every '
        f'completion is timestamped onto your permanent history along with whatever you agreed to. Being '
        f'straight about what that proves: it proves you were <em>shown</em> the material, not that you '
        f'absorbed it. It is recorded that way, and nobody will later claim it was a test.</p>', "quiet")


def _practice_section(data):
    """Practice — the half that Learnings deliberately cannot claim.

    The Learnings section ends by saying a completion proves you were *shown* the material, not that
    you absorbed it. This is where that gap gets closed, and the honesty carries over: a self-marked
    drill proves you read the rubric and formed a view, not that an outside judge agreed. The page
    says which kind each attempt was, because `crm/coach.py` records it and never merges them.
    """
    dr = data.get("drills") or {}
    items = dr.get("items") or []
    if not items:
        return ""
    rows = ""
    for it in items:
        v = it["lastVerdict"]
        tag = ""
        if v:
            by = "you marked" if it["lastBy"] == "self" else "judged"
            cls = {"solid": "live", "shaky": "", "missed": "warn"}.get(v, "")
            tag = f'<span class="tag {cls}">{esc(by)}: {esc(v)}</span>'
        rev = ""
        if it.get("reveal"):
            rev = (f'<details class="rev"><summary>what a good answer does</summary>'
                   f'<p><strong>Looks like:</strong> {esc(it["reveal"]["looksLike"])}</p>'
                   + (f'<p><strong>Fails if:</strong> {esc(it["reveal"]["failsIf"])}</p>'
                      if it["reveal"]["failsIf"] else "") + '</details>')
        rows += (f'<div class="rec drill" data-drill="{esc(it["id"])}">'
                 f'<div class="rechead"><strong>{esc(it["lesson"])}</strong> {tag}</div>'
                 f'<p>{esc(it["prompt"])}</p>'
                 f'<div class="drillmark">'
                 f'<button data-save="drill" data-v="solid">I nailed it</button>'
                 f'<button data-save="drill" data-v="shaky">Shaky</button>'
                 f'<button data-save="drill" data-v="missed">I missed it</button>'
                 f'</div>{rev}</div>')
    return _section(
        f'<div class="tick"></div><h2>Practice</h2>'
        f'<p class="lede">Finishing a lesson proves you were shown something. This is where you find '
        f'out whether you can actually do it. Say your answer out loud first — really out loud — then '
        f'mark yourself, and only then read what a good answer does. Reading the answer before you '
        f'try is the one way to waste this. {esc(dr.get("note", ""))}</p>'
        f'<div class="recs">{rows}</div>'
        f'<p class="fine">You mark your own practice, and yourco records it as exactly that: '
        f'<em>self-marked</em>. It sits separately from anything an yourco coach judges, and a '
        f'self-mark never overwrites a coach\'s finding — that separation is the only reason either '
        f'number means anything. Drills appear here once you have completed the lesson they belong '
        f'to; nothing on this page moves your rung.</p>', "quiet")


def _resources_section(data):
    """Documents and assets — availability resolved per connector; nothing uncleared is ever linked."""
    res = data["resources"]
    if not res:
        return _section(
            '<div class="tick"></div><h2>Resources</h2>'
            '<div class="empty"><h3>Nothing to list yet</h3>'
            '<p>The resource index is empty.</p></div>')
    rows = ""
    for r in res:
        avail = (r["state"] or "").lower()
        cls = "live" if avail in ("available", "on file", "issued") or avail.endswith("kit(s)") else ""
        link = (f'<a href="#lesson-{esc(r["lesson"])}">read it in this console</a>'
                if r.get("lesson") else "")
        rows += (f'<tr><td><strong>{esc(r["title"])}</strong><br>'
                 f'<span class="muted" style="font-size:13.5px">{esc(r["what"])}</span></td>'
                 f'<td><span class="tag {cls}">{esc(r["state"])}</span></td>'
                 f'<td><span class="muted" style="font-size:13.5px">{esc(r["detail"])} {link}</span></td>'
                 f'</tr>')
    return _section(
        f'<div class="tick"></div><h2>Resources</h2>'
        f'<p class="lede">Every document and asset attached to your account, and exactly where each one '
        f'stands. Anything not yet cleared is listed and marked rather than linked — yourco will not hand '
        f'you a draft agreement or an uncleared disclosure and let you treat it as the real terms.</p>'
        f'<table><tr><th>Item</th><th>Status</th><th>Detail</th></tr>{rows}</table>'
        f'<p class="fine">"Available at launch" and "in counsel review" mean the document exists but is '
        f'not cleared to be sent — the connector program is in counsel review and has not launched. When '
        f'that changes, these rows change with it; there is no separate list to keep in step.</p>', "quiet")


def _timeline_section(data):
    evs = data["events"]
    if not evs:
        inner = ('<div class="empty"><h3>Your history is empty</h3>'
                 '<p>Nothing has happened on your account yet, so there is nothing to show — and yourco '
                 'will not invent anything to fill the space. Your first entry is written the moment your '
                 'first referral is registered.</p></div>')
    else:
        items = ""
        for e in reversed(evs):
            label = EVENT_LABELS.get(e.get("event"), (e.get("event") or "event").replace(".", " ").capitalize())
            detail = []
            if e.get("event") == "rung.changed":
                detail.append(f'{esc(e.get("from") or "—")} → {esc(e.get("to") or "—")}')
            for key, cap in EVENT_FIELDS:
                if e.get(key) not in (None, ""):
                    v = e[key]
                    if key == "stage":                       # show the pipeline stage as a human reads it
                        v = data["stageLabels"].get(v, v)
                    detail.append(f'{cap}: {esc(v)}')
            if e.get("corrects"):
                detail.append(f'corrects event {esc(e["corrects"])}')
            ts = esc((e.get("ts") or "").replace("T", " ").replace("+00:00", " UTC"))
            dl_html = '<div class="detail">' + " · ".join(detail) + "</div>" if detail else ""
            items += (f'<div class="tl"><div class="when">{ts}</div>'
                      f'<div class="what">{esc(label)}</div>{dl_html}'
                      f'<div class="ref">entry #{esc(e.get("seq"))} · id {esc(e.get("id"))}</div></div>')
        inner = f'<div class="timeline">{items}</div>'
    return _section(
        f'<div class="tick"></div><h2>Your history</h2>'
        f'<p class="lede">Every event on your account, in order, from yourco\'s append-only attribution '
        f'log. Entries are never edited and never deleted — a mistake is corrected by a new entry that '
        f'cites the old one, so the correction is part of the record too. This is the whole point: a '
        f'referral program you can audit.</p>{inner}', "quiet")


def _footer(data):
    return _section(
        f'<p class="fine" style="border-top:0;padding-top:0">{STAGED_NOTE}</p>'
        f'<p class="fine">This page shows only your own account. It contains no other connector\'s book, '
        f'no client\'s internal information, and no part of yourco\'s internal system of record. '
        f'Rendered {datetime.date.today().isoformat()} from yourco\'s records. '
        f'Questions, or something here that does not match what you believe happened → '
        f'<a href="mailto:{CONTACT}">{CONTACT}</a>. Program rules: your partner agreement governs.</p>',
        "foot")


# Client-side saving. The acting connector is NOT in this payload and cannot be — the server takes it
# from the session cookie and re-checks scope with `connector_writes.can_write()` before touching
# anything, so the page cannot grant itself permission by editing a field or by naming someone else.
# The CSRF token is a per-session synchroniser (belt to SameSite=Strict's braces). On a static export
# (file://, or a page opened out of _out/) the fetch fails and the page says so honestly instead of
# pretending to have saved.
SAVE_JS = """
<script>
(function(){
  const BASE = window.CONSOLE_BASE || "";
  const CSRF = window.CONSOLE_CSRF || "";
  function setStatus(el, msg, cls){ el.textContent = msg; el.className = "status " + (cls||""); }
  async function post(path, body){
    const r = await fetch(BASE + path, {method:"POST", credentials:"same-origin",
                                        headers:{"Content-Type":"application/json",
                                                 "X-CSRF-Token": CSRF},
                                        body: JSON.stringify(body)});
    let j = {}; try { j = await r.json(); } catch(e) {}
    if(!r.ok || !j.ok) throw new Error(j.error || ("Save failed (" + r.status + ")."));
    return j;
  }
  // The connector's call on a first-contact draft. Its own handler because the decision is on the
  // BUTTON, not the box — "approve" and "save my edits" post different things from the same card.
  document.querySelectorAll("[data-approve]").forEach(function(btn){
    btn.addEventListener("click", async function(){
      const card = btn.closest("[data-approval]");
      const status = card.querySelector(".status");
      const box = card.querySelector("[data-a='draft']");
      const decision = btn.dataset.approve;
      btn.disabled = true; setStatus(status, "Saving…");
      try{
        await post("/approval", {id: card.dataset.approval, decision: decision,
                                 edited: decision === "edited" ? box.value : undefined});
        setStatus(status, "Recorded · reloading", "ok");
        window.location.reload();
      }catch(e){
        const off = (e instanceof TypeError);
        setStatus(status, off ? "This needs the console server — this is an exported copy." : e.message, "err");
        btn.disabled = false;
      }
    });
  });
  document.querySelectorAll("[data-save]").forEach(function(btn){
    btn.addEventListener("click", async function(){
      const kind = btn.dataset.save;
      const status = btn.parentElement.querySelector(".status");
      btn.disabled = true; setStatus(status, "Saving…");
      try{
        if(kind === "drill"){
          // The drill id and the verdict are all that is sent. WHO practised is the session, and the
          // provenance is fixed server-side to by="self" — the page cannot claim a coach judged it.
          const box = btn.closest("[data-drill]");
          await post("/drill", {drill: box.dataset.drill, verdict: btn.dataset.v});
          setStatus(status, "Marked · reloading so the answer opens", "ok");
          window.location.reload();
          return;
        }
        if(kind === "training"){
          // The lesson slug is the ONLY thing sent. Who completed it is the session, and what they
          // agreed to is the lesson's own sentence read server-side — the page cannot author either.
          const box = btn.closest("[data-training]");
          const ack = box.querySelector("[data-ack]");
          if(ack && !ack.checked){
            setStatus(status, "Tick the box first — it is what gets recorded.", "err");
            btn.disabled = false; return;
          }
          await post("/training", {lesson: box.dataset.training});
          setStatus(status, "Recorded · reloading", "ok");
          window.location.reload();
          return;
        } else if(kind === "submission"){
          const box = btn.closest("[data-submission]"), fields = {};
          box.querySelectorAll("[data-s]").forEach(function(i){ fields[i.dataset.s] = i.value; });
          await post("/submission", {fields: fields});
          setStatus(status, "Submitted · yourco reviews it within 24–48h", "ok");
          window.location.reload();
          return;
        } else if(kind === "referral"){
          const rec = btn.closest(".rec"), fields = {};
          rec.querySelectorAll("[data-f]").forEach(function(i){ fields[i.dataset.f] = i.value; });
          await post("/referral", {companyId: rec.dataset.company, fields: fields});
        } else {
          const box = btn.closest("[data-goals-for]") || btn.parentElement.previousElementSibling;
          const subject = box.dataset.goalsFor;
          const targets = {};
          box.querySelectorAll("[data-goal]").forEach(function(i){
            targets[i.dataset.goal] = i.value.trim() === "" ? null : Number(i.value);
          });
          await post("/goal", {subject: subject, targets: targets});
        }
        setStatus(status, "Saved to yourco's records · on your log", "ok");
      }catch(e){
        const off = (e instanceof TypeError);
        setStatus(status, off ? "Saving needs the console server — this is an exported copy."
                              : e.message, "err");
      }
      btn.disabled = false;
    });
  });
})();
</script>
"""


def _page(title, body):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    return tpl.replace("{{TITLE}}", html.escape(title)).replace("{{BODY}}", body)


# ---- the authentication surfaces -----------------------------------------------------------
# Every one of these is deliberately incurious: no page here confirms that a given person has an
# account, is locked out, or exists in yourco's records. There is exactly one failure sentence.
def _session_bar(signed_in_as, csrf):
    """Who you are + the way out. Absent on a static export, which has no session to end."""
    if not signed_in_as:
        return ""
    return _section(
        f'<div class="saveline"><span class="status">Signed in as '
        f'<strong>{esc(signed_in_as)}</strong>.</span>'
        f'<form method="POST" action="/logout" style="margin:0">'
        f'<input type="hidden" name="csrf" value="{esc(csrf)}">'
        f'<button class="btn" type="submit">Sign out</button></form></div>', "parchment")


def render_login(message="", name=""):
    body = _section(
        f'<a class="mark" href="/login">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console</div>'
        f'<h1 style="margin-top:12px">Sign in</h1>'
        f'<p class="lede">Your console shows your own book, computed from yourco\'s records. It is '
        f'reached by signing in — never by holding a link.</p>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark") + _section(
        f'<div class="card" style="max-width:460px">'
        f'{f"<p class=status style=color:var(--oxblood)>{esc(message)}</p>" if message else ""}'
        f'<form method="POST" action="/login">'
        f'<label>Your name<input name="name" autocomplete="username" autofocus '
        f'value="{esc(name)}" required></label>'
        f'<label style="display:block;margin-top:14px">Passphrase'
        f'<input name="passphrase" type="password" autocomplete="current-password" required></label>'
        f'<div class="saveline" style="margin-top:16px">'
        f'<button class="btn" type="submit">Sign in</button></div></form></div>'
        f'<p class="fine">Setting up for the first time, or lost your passphrase? yourco cannot look it '
        f'up — it is not stored anywhere, by design. Ask for a new setup link: '
        f'<a href="mailto:{CONTACT}">{CONTACT}</a>.</p>')
    return _page("Sign in — connector console — yourco (staged)", body)


def render_setup(token, name="", message="", done=False):
    if done:
        inner = (f'<div class="card" style="max-width:460px"><h3>Passphrase set</h3>'
                 f'<p>yourco does not have a copy of it and cannot recover it. '
                 f'<a href="/login">Sign in</a>.</p></div>')
    elif not name:
        inner = (f'<div class="card" style="max-width:460px"><h3>This link cannot be used</h3>'
                 f'<p>{esc(message or auth.SETUP_FAIL_MSG)} Setup links are single-use and expire after '
                 f'{auth.SETUP_TOKEN_HOURS} hours. Ask for a new one: '
                 f'<a href="mailto:{CONTACT}">{CONTACT}</a>.</p></div>')
    else:
        inner = (
            f'<div class="card" style="max-width:460px">'
            f'{f"<p class=status style=color:var(--oxblood)>{esc(message)}</p>" if message else ""}'
            f'<p>Setting the passphrase for <strong>{esc(name)}</strong>.</p>'
            f'<form method="POST" action="/setup">'
            f'<input type="hidden" name="token" value="{esc(token)}">'
            f'<label style="display:block;margin-top:12px">Choose a passphrase'
            f'<input name="passphrase" type="password" autocomplete="new-password" required></label>'
            f'<label style="display:block;margin-top:14px">Type it again'
            f'<input name="confirm" type="password" autocomplete="new-password" required></label>'
            f'<div class="saveline" style="margin-top:16px">'
            f'<button class="btn" type="submit">Set my passphrase</button></div></form></div>'
            f'<p class="fine">At least {auth.MIN_PASSPHRASE} characters — a phrase you will remember beats '
            f'a short scramble you will not. <strong>yourco never sees it.</strong> Only a one-way hash '
            f'is stored, so nobody at yourco — including the Founder — can read it, and nobody can give it back '
            f'to you if you lose it. This link works once and then stops working.</p>')
    body = _section(
        f'<a class="mark" href="/login">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console</div>'
        f'<h1 style="margin-top:12px">Set your passphrase</h1>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark") + _section(inner)
    return _page("Set your passphrase — connector console — yourco (staged)", body)


def render_denied():
    """One body for every refusal. It must not differ by a byte between 'not yours' and 'no such
    person' — a 404-vs-403 split is itself an account-enumeration oracle."""
    return _page("Not available — yourco", _section(
        '<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        '<div class="eyebrow" style="margin-top:40px">connector console</div>'
        '<h1 style="margin-top:12px">Not available</h1>'
        '<p class="lede">This console is not available to your account. If you believe that is wrong, '
        f'write to <a href="mailto:{CONTACT}" style="color:inherit">{CONTACT}</a>.</p>'
        '<p class="muted mono" style="margin-top:18px"><a href="/" style="color:inherit">'
        'your own console</a></p>', "dark"))


def render_operator_index(names, csrf, who, role="operator"):
    rows = "".join(f'<li><a href="/c/{slug(n)}">{html.escape(n)}</a></li>' for n in names)
    accounts = "".join(
        f'<li>{esc(u["name"])} — {esc(u["role"])}, '
        f'{"passphrase set" if u["passphraseSet"] else "<strong>no passphrase yet</strong>"}'
        f'{" · LOCKED" if u["locked"] else ""}'
        f'{" · setup link pending" if u["setupPending"] else ""}</li>'
        for u in auth.list_users())
    body = _section(
        f'<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console · {esc(role)}</div>'
        f'<h1 style="margin-top:12px">Every connector</h1>'
        f'<p class="lede">Signed in as <strong>{esc(who)}</strong> ({esc(role)}). This index exists so '
        f'yourco can page through the staged consoles. It is not reachable by a connector session — '
        f'a connector who asks for it is sent to their own console.</p>', "dark") \
        + _session_bar(who, csrf) + _section(
        f'<div class="tick"></div><h2>Connectors in the CRM ({len(names)})</h2><ul>{rows}</ul>'
        f'<p style="margin-top:18px"><a href="/verify"><strong>Verification queue →</strong></a> '
        f'sourced contacts waiting on yourco, against the 24–48h we promised.</p>'
        f'<h2 style="margin-top:34px">Console accounts ({len(auth.list_users())})</h2>'
        f'<ul>{accounts or "<li>None yet — issue a setup token to create one.</li>"}</ul>'
        f'<p class="fine">Operator sessions are <strong>read-only</strong>: an operator can view a '
        f'console but cannot write a goal or a note as anyone. Writes are a connector\'s own act, on '
        f'their own record, under their own name.</p>')
    return _page("Every connector — connector console — yourco (staged)", body)


VERIFY_JS = """
<script>
(function(){
  const CSRF = window.CONSOLE_CSRF || "";
  document.querySelectorAll("[data-verify]").forEach(function(btn){
    btn.addEventListener("click", async function(){
      const card = btn.closest("[data-sub-id]");
      const status = card.querySelector(".status");
      const reason = card.querySelector("[data-reason]");
      btn.disabled = true; status.textContent = "Saving…"; status.className = "status";
      try{
        const r = await fetch("/verify", {method:"POST", credentials:"same-origin",
          headers:{"Content-Type":"application/json","X-CSRF-Token":CSRF},
          body: JSON.stringify({id: card.dataset.subId, status: btn.dataset.verify,
                                reason: reason ? reason.value : ""})});
        let j = {}; try { j = await r.json(); } catch(e) {}
        if(!r.ok || !j.ok) throw new Error(j.error || ("Failed (" + r.status + ")."));
        status.textContent = "Recorded · reloading"; status.className = "status ok";
        window.location.reload();
      }catch(e){
        status.textContent = e.message; status.className = "status err";
        btn.disabled = false;
      }
    });
  });
})();
</script>
"""


def render_verify_queue(pending, csrf, who):
    """The operator's submission queue. The 24–48h SLA in the decision is measured against this page.

    Every card shows the two compliance answers (how the connector knows them, whether the person is
    expecting contact) at the top — because those, not the business name, are what the operator is
    actually being asked to judge before yourco picks up the phone.
    """
    cards = ""
    now = datetime.datetime.now(datetime.timezone.utc)
    for r in pending:
        try:
            age_h = (now - datetime.datetime.fromisoformat(r.get("submittedAt"))).total_seconds() / 3600
        except Exception:
            age_h = 0
        late = age_h > 48
        age = (f'{int(age_h)}h ago' if age_h < 48 else f'<strong>{int(age_h // 24)}d ago — past the '
                                                       f'24–48h we promised</strong>')
        consent = {"yes": "Yes — the connector told them",
                   "no": "No — not yet", "unknown": "Not sure"}.get(r.get("consent") or "unknown",
                                                                    "Not sure")
        cards += (
            f'<div class="rec" data-sub-id="{esc(r.get("id"))}">'
            f'<div class="rechead"><h3>{esc(r.get("business") or "—")}</h3>'
            f'<span class="tag{" live" if late else ""}">{age}</span></div>'
            f'<div class="kvs">'
            f'<div class="kv"><span class="k">From</span><span class="v">{esc(r.get("connector"))}</span></div>'
            f'<div class="kv"><span class="k">Owner</span><span class="v">{esc(r.get("contact") or "—")}</span></div>'
            f'<div class="kv"><span class="k">Reach</span><span class="v">'
            f'{esc(r.get("email") or "")}{" · " if r.get("email") and r.get("phone") else ""}'
            f'{esc(r.get("phone") or "")}</span></div>'
            f'<div class="kv"><span class="k">How they know them</span>'
            f'<span class="v">{esc(r.get("provenance") or "—")}</span></div>'
            f'<div class="kv"><span class="k">Expecting contact?</span><span class="v">{esc(consent)}</span></div>'
            + (f'<div class="kv"><span class="k">Note</span><span class="v">{esc(r.get("note"))}</span></div>'
               if r.get("note") else "")
            + f'</div>'
            f'<div class="editrow">'
            f'<label>Reason (recorded either way)<input type="text" data-reason maxlength="300" '
            f'placeholder="e.g. confirmed on their website"></label>'
            f'<div class="saveline">'
            f'<button class="btn" data-verify="verified">Verify</button> '
            f'<button class="btn" data-verify="booked">Verify + call booked</button> '
            f'<button class="btn" data-verify="rejected">Reject</button>'
            f'<span class="status"></span></div></div></div>')

    empty = ('<div class="empty"><h3>Queue is clear</h3><p>Nothing is waiting on yourco. Every '
             'submission has been verified, booked, or rejected — and every one of those decisions '
             'is on the attribution log with the operator\'s name on it.</p></div>')
    return _page("Verification queue — connector console — yourco (staged)", _section(
        f'<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console · operator</div>'
        f'<h1 style="margin-top:12px">Verification queue</h1>'
        f'<p class="lede">Signed in as <strong>{esc(who)}</strong>. {len(pending)} submission'
        f'{"s" if len(pending) != 1 else ""} waiting. yourco promised a decision within '
        f'<strong>24–48 hours</strong>, and the person on the other end is waiting to be paid — this '
        f'page is where that promise is either kept or visibly broken.</p>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark") + _section(
        f'<div class="tick"></div><h2>Waiting on yourco</h2>'
        f'<p class="lede">Judge the two questions at the top of each card before the business itself: '
        f'yourco is the one making this call, so where the contact came from and whether they are '
        f'expecting it is what decides whether we may make it at all. Reject anything bought, '
        f'scraped, or copied from a list.</p>'
        f'{cards or empty}'
        f'<p class="fine">Verifying pays the connector a bounty step, so an operator can never verify '
        f'their own submission. Both the decision and the reason are appended to the attribution log '
        f'under your name, permanently.</p>'
        f'<p class="fine"><a href="/">← operator index</a></p>')
        + _wiring("", csrf) + VERIFY_JS)


def _wiring(base, csrf):
    """The two values the page's save JS needs. `csrf` is empty on a static export — which is correct:
    an exported page has no session, so it must not be able to save, and it says so."""
    return (f'<script>window.CONSOLE_BASE={json.dumps(base)};'
            f'window.CONSOLE_CSRF={json.dumps(csrf)};</script>')


def _gate_hero(data):
    me = data["me"]
    r0 = data["training"]["r0"]
    left = max(r0["total"] - r0["done"], 0)
    mins = sum(int(L.get("minutes") or 0) for L in data["lessons"]
               if L["rung"] == "R0" and not L["done"])
    if me["rungN"] < 0:
        # Not joined: even R0 training is closed, because R0 is "joined". The page shows the shape of
        # what is coming and refuses to pretend any of it is open.
        sub = ("You have not joined the connector program yet — the agreement and W-9 come first, and "
               "the program is still in counsel review. This is the page you would land on when you "
               "do: your first training, and nothing else until it is finished. It opens at R0.")
    elif not r0["exists"]:
        sub = ("yourco has not published your first training yet. That is yourco's gap, not yours — "
               "the rest of this console opens the moment it exists, and nobody is going to pretend "
               "otherwise in the meantime.")
    elif r0["done"]:
        sub = (f"{left} lesson(s) to go — about {mins} minutes. Finish them and your full console "
               f"opens on this same page.")
    else:
        sub = (f"{r0['total']} short lessons, about {mins} minutes in total. They are the whole job: "
               f"what a good introduction sounds like, who to look for, the rules you work under, and "
               f"how you get paid. Finish them and your full console opens on this same page.")
    return _section(
        f'<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console</div>'
        f'<h1 style="margin-top:12px">Start here, {esc(me["connector"].split(" ")[0])}.</h1>'
        f'<p class="lede">{sub}</p>'
        f'<p class="muted mono" style="margin-top:18px">'
        f'{esc(me["rung"] or "not joined")} · your first training</p>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark")


def render_gate(data, base="", csrf="", signed_in_as=None):
    """The pre-R0-training console: **only** Learnings, and nothing else on the page.

    the Founder's rule — training gates everything. A connector who has just been onboarded sees one thing to
    do, not a wall of locked boxes with their money behind them. There are no referrals, earnings,
    tier, goals, reporting, upline, history, phantom or Resources markup on this page at all: those
    sections are not rendered-and-hidden, they are **not built**, so nothing can leak out of a page
    that never contained it.
    """
    me = data["me"]
    only_r0 = dict(data, lessons=[L for L in data["lessons"] if L["rung"] == "R0"])
    ahead = _section(
        f'<div class="tick"></div><h2>What opens when you finish</h2>'
        f'<p class="lede">Not a teaser — a list, so you know exactly what is behind this and why it is '
        f'not being kept from you for its own sake.</p>'
        f'<ul><li>Every business you have introduced, as a working record you can annotate</li>'
        f'<li>What you are owed, with the arithmetic shown</li>'
        f'<li>Your commission tier and what the next one is worth on your actual book</li>'
        f'<li>Goals, and a report built from your own history</li>'
        f'<li>Every document and asset attached to your account</li>'
        f'<li>Your full event history, from yourco\'s append-only log</li></ul>'
        f'<p class="fine">Why the gate exists: everything on that list is either money or something '
        f'you would say to somebody else on yourco\'s behalf. The four lessons below are what makes '
        f'both of those safe to hand over — for the business you introduce as much as for you. It is '
        f'the same rule yourco applies to its own systems: nothing is trusted with an action before '
        f'there is evidence it should be.</p>')
    body = (_gate_hero(data) + _session_bar(signed_in_as, csrf)
            + _learnings_section(only_r0) + ahead + _footer(data)
            + _wiring(base, csrf) + SAVE_JS)
    return _page(f'{me["connector"]} — start here — yourco (staged)', body)


def render(name, d=None, events=None, base="", csrf="", signed_in_as=None, ghost_data=None):
    data = console_data(name, d=d, events=events, ghost_data=ghost_data)
    if data is None:
        return None
    # THE GATE. R0 training incomplete → the start-here page, and nothing else is even assembled.
    if not data["training"]["r0Complete"]:
        return render_gate(data, base=base, csrf=csrf, signed_in_as=signed_in_as)
    # Five rooms. Within each, weight descends deliberately — one `head` carrying the room's key
    # figure, then working surfaces, then `quiet` reference material. That descent IS the band
    # rhythm the old page only pretended to have (three parchment tiles in a row, then two plain).
    rooms = {
        "overview": _overview_section(data),
        "book": (_approvals_section(data) + _referrals_section(data) + _submissions_section(data)),
        "money": (_earnings_section(data) + _tier_section(data) + _perk_section(data)
                  + _reporting_section(data) + _override_section(data)),
        "us": (_ghost_section(data) + _escrow_section(data) + _calibration_section(data)),
        "account": (_rung_section(data) + _goals_section(data) + _downline_section(data)
                    + _phantom_section(data) + _learnings_section(data)
                    + _practice_section(data)
                    + _resources_section(data) + _timeline_section(data)),
    }
    if not rooms["us"].strip():
        rooms["us"] = _us_placeholder(data)
    rooms = {k: v for k, v in rooms.items() if v.strip()}
    panes = "".join(f'<div class="room{" on" if k == "overview" else ""}" data-room="{k}">{v}</div>'
                    for k, v in rooms.items())
    body = (_hero(data) + _session_bar(signed_in_as, csrf)
            + f'<div class="shell">{_rail(data, rooms)}<main class="main">{panes}</main></div>'
            + _footer(data) + _wiring(base, csrf) + SAVE_JS + ROOM_JS)
    return _page(f"{name} — connector console — yourco (staged)", body)


def render_downline(actor, target, d=None, events=None, base="", csrf="", signed_in_as=None):
    """The ONLY page an upline may load about a downline member — and it is not that person's console.

    It is the same bounded card `_downline_section` already puts on the upline's own page: rung,
    production, pipeline as stage counts, goals (editable, because `can_write` permits an upline to
    help set them). It carries no client names, no per-client retainer, and no earnings figure,
    because those are not an upline's to see (module docstring rule 2). Reusing that one renderer is
    the point — there is no second, looser code path that could drift.
    """
    data = console_data(actor, d=d, events=events)
    if data is None:
        return None
    # The gate applies to the upline too: somebody who has not finished their own R0 training does not
    # get a coaching view of another person's production first.
    if not data["training"]["r0Complete"]:
        return render_gate(data, base=base, csrf=csrf, signed_in_as=signed_in_as)
    entry = next((m for m in data["downline"] if m["name"] == target), None)
    if entry is None:
        return None
    scoped = dict(data, downline=[entry])
    hero = _section(
        f'<a class="mark" href="/">yourco<span class="dot">.</span></a>'
        f'<div class="eyebrow" style="margin-top:40px">connector console · downline view</div>'
        f'<h1 style="margin-top:12px">{esc(target)}</h1>'
        f'<p class="lede">You are seeing this because {esc(target)} is in your downline. This is not '
        f'their console — it is the bounded view an upline gets: their rung, what they are producing, '
        f'what is in their pipeline, and their goals, which you may help set. Their clients by name, '
        f'what any individual client pays, and what they earn are theirs, exactly as yours are yours.</p>'
        f'<p class="muted mono" style="margin-top:18px">signed in as {esc(actor)}</p>'
        f'<div class="staged">{STAGED_NOTE}</div>', "dark")
    foot = _section(
        f'<p class="fine" style="border-top:0;padding-top:0">Every target you set for someone else is '
        f'written to their history with your name on it. Questions → '
        f'<a href="mailto:{CONTACT}">{CONTACT}</a>.</p>'
        f'<p class="fine"><a href="/c/{slug(actor)}">← back to your own console</a></p>', "foot")
    body = (hero + _session_bar(signed_in_as, csrf) + _downline_section(scoped) + foot
            + _wiring(base, csrf) + SAVE_JS)
    return _page(f"{target} — downline view — yourco (staged)", body)


# ---- modes ---------------------------------------------------------------------------
def _connectors(d=None):
    d = d if d is not None else json.load(open(os.path.join(CRM_DIR, "data.json")))
    return sorted(ladder.compute(d).keys())


def render_to_file(name, d=None):
    page = render(name, d=d)
    if page is None:
        return None
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{slug(name)}.html")
    open(path, "w", encoding="utf-8").write(page)
    return path


# ---- authorization -------------------------------------------------------------------------
# The one function that answers "may this identity touch this name?". It takes the SESSION, never a
# path segment, never a body field, and it recomputes the downline from `connector_ladder.compute()`
# on every call — so a person removed from a downline in the CRM loses that access on their next
# request, with no cache to invalidate and no token to expire.
def authorize(session, target, d=None):
    """Returns 'operator' | 'self' | 'downline' | None. None means 403, and 403 means say nothing."""
    if not session or not target:
        return None
    if auth.is_console_admin(session.get("role")):
        return "operator"
    if session.get("name") == target:
        return "self"
    d = d if d is not None else json.load(open(os.path.join(CRM_DIR, "data.json")))
    me = ladder.compute(d).get(session.get("name"))
    if me and target in (me.get("downline") or []):   # `downline` is books()' cycle-guarded walk
        return "downline"
    return None


def serve(port, host="127.0.0.1"):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import unquote, urlsplit, parse_qs

    class H(BaseHTTPRequestHandler):
        server_version = "yourco-console"
        sys_version = ""

        # ---- plumbing ----------------------------------------------------------------
        def _send(self, body, code=200, ctype="text/html; charset=utf-8", headers=()):
            b = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            # A console page is one person's financial record: never cache it, never let it be
            # framed, never leak its URL (which contains a name) to another origin.
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                             "img-src data:; connect-src 'self'; form-action 'self'; base-uri 'none'; "
                             "frame-ancestors 'none'")
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(b)

        def _json(self, obj, code=200, headers=()):
            self._send(json.dumps(obj), code, "application/json; charset=utf-8", headers)

        def _redirect(self, where, headers=()):
            # No body at all on a redirect: an unauthenticated request must receive zero page content.
            self._send("", 303, "text/plain; charset=utf-8", tuple(headers) + (("Location", where),))

        def _ip(self):
            return self.client_address[0] if self.client_address else ""

        # ---- identity ----------------------------------------------------------------
        def _session(self):
            """The ONLY place an identity is established. There is no other assignment to `who`."""
            return auth.session_for(auth.cookie_from_header(self.headers.get("Cookie")))

        def _origin_ok(self):
            """Reject a cross-origin POST outright. SameSite=Strict already stops the cookie riding
            along in a modern browser; this is the second lock for an old one."""
            o = self.headers.get("Origin")
            if not o or o == "null":
                return True                       # same-origin form posts often omit Origin entirely
            return urlsplit(o).netloc == (self.headers.get("Host") or "")

        def _form(self):
            try:
                n = min(int(self.headers.get("Content-Length", 0) or 0), 16_000)
                raw = self.rfile.read(n).decode("utf-8", "replace")
            except Exception:
                return {}
            return {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}

        def _body_json(self):
            try:
                n = min(int(self.headers.get("Content-Length", 0) or 0), 64_000)
                return json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return None

        # ---- GET ---------------------------------------------------------------------
        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            parts = urlsplit(self.path)
            path = unquote(parts.path)
            q = parse_qs(parts.query)
            who = self._session()

            if path == "/login":
                if who:
                    return self._redirect("/")
                return self._send(render_login(), 200)

            if path == "/setup":
                token = (q.get("token") or [""])[0]
                name = self._setup_name(token)
                return self._send(render_setup(token, name=name), 200 if name else 400)

            if path == "/logout":
                # Sign-out is a state change → POST only. A GET here just shows the way out.
                return self._redirect("/" if who else "/login")

            if not who:
                # Unauthenticated: no page content of any kind, for any path.
                return self._redirect("/login")

            if path in ("/", "/index.html"):
                if auth.is_console_admin(who["role"]):
                    return self._send(render_operator_index(_connectors(), who["csrf"], who["name"], who.get("role") or "operator"))
                return self._redirect(f"/c/{slug(who['name'])}")

            if path == "/verify":
                # Operator-only. A connector asking for the verification queue is not told it exists.
                if not auth.is_console_admin(who["role"]):
                    return self._send(render_denied(), 403)
                d = json.load(open(os.path.join(CRM_DIR, "data.json")))
                return self._send(render_verify_queue(writes.pending_submissions(d), who["csrf"],
                                                      who["name"]))

            if path.startswith("/c/"):
                want = path[3:].removesuffix(".html").strip("/")
                if "/" in want:
                    return self._send(render_denied(), 403)
                # Resolve the slug to a name, then ask authorize(). Resolution is NOT permission —
                # the two steps are separate on purpose, and only the second one decides.
                d = json.load(open(os.path.join(CRM_DIR, "data.json")))
                target = next((n for n in _connectors(d) if slug(n) == want), None)
                scope = authorize(who, target, d) if target else None
                if scope in ("self", "operator"):
                    page = render(target, d=d, base=f"/c/{slug(target)}", csrf=who["csrf"],
                                  signed_in_as=who["name"])
                    return self._send(page, 200) if page else self._send(render_denied(), 403)
                if scope == "downline":
                    page = render_downline(who["name"], target, d=d, base=f"/c/{slug(who['name'])}",
                                           csrf=who["csrf"], signed_in_as=who["name"])
                    return self._send(page, 200) if page else self._send(render_denied(), 403)
                # Unrelated connector, or a connector who does not exist: identical response. The
                # requested name is never echoed back, in the body or in a header.
                return self._send(render_denied(), 403)

            return self._send(render_denied(), 404)

        def _setup_name(self, token):
            """Whose setup link is this? Returns "" for anything not currently redeemable — an invalid,
            spent, or expired token is indistinguishable from a made-up one."""
            if not token:
                return ""
            import time as _t
            d = auth._load_users()
            for u in d["users"].values():
                t = u.get("setupToken") or {}
                if not t.get("hash") or t.get("usedAt") or float(t.get("expiresAt") or 0) < _t.time():
                    continue
                import secrets as _s
                if _s.compare_digest(auth._token_hash(token, t["salt"]), t["hash"]):
                    return u["name"]
            return ""

        # ---- POST --------------------------------------------------------------------
        def do_POST(self):
            path = unquote(urlsplit(self.path).path)
            if not self._origin_ok():
                return self._json({"ok": False, "error": "Request refused."}, 403)

            if path == "/login":
                return self._post_login()
            if path == "/setup":
                return self._post_setup()
            if path == "/logout":
                return self._post_logout()
            if path == "/verify":
                return self._post_verify()
            return self._post_write(path)

        def _post_verify(self):
            """The ONE write an operator session may make — and it is their own act, under their name.

            This does not weaken "operator sessions are read-only", whose point is that an operator
            cannot write *as a connector*: no goal, no note, no training mark in someone else's name.
            Verifying a submission is yourco's own decision about yourco's own queue, and
            `verify_submission()` still refuses if the operator is the submitting connector.
            """
            who = self._session()
            if not who or not auth.is_console_admin(who["role"]):
                return self._json({"ok": False, "error": "Not available."}, 403)
            if not auth.check_csrf(who, self.headers.get("X-CSRF-Token")):
                return self._json({"ok": False, "error": "Request refused."}, 403)
            if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
                return self._json({"ok": False, "error": "Request refused."}, 415)
            body = self._body_json()
            if not isinstance(body, dict):
                return self._json({"ok": False, "error": "bad payload"}, 400)
            try:
                rec = writes.verify_submission(who["name"], (body.get("id") or "").strip(),
                                               (body.get("status") or "").strip(),
                                               reason=(body.get("reason") or "").strip())
                return self._json({"ok": True, "saved": rec})
            except writes.ScopeError as e:
                return self._json({"ok": False, "error": str(e)}, 403)
            except Exception as e:
                print("console verify error:", e, file=sys.stderr)
                return self._json({"ok": False, "error": "save failed"}, 500)

        def _post_login(self):
            f = self._form()
            name, passphrase = (f.get("name") or "").strip(), f.get("passphrase") or ""
            ok, user, _msg = auth.verify(name, passphrase, ip=self._ip())
            if not ok:
                # Same page, same sentence, same status for every failure mode.
                return self._send(render_login(auth.FAIL_MSG, name=name), 401)
            sid, _csrf = auth.create_session(user["name"], user["role"])
            cookie = auth.set_cookie(sid, self.headers.get("Host"))
            dest = "/" if auth.is_console_admin(user["role"]) else f"/c/{slug(user['name'])}"
            return self._redirect(dest, (("Set-Cookie", cookie),))

        def _post_setup(self):
            f = self._form()
            token = f.get("token") or ""
            ok, name, msg = auth.complete_setup(token, f.get("passphrase") or "",
                                                confirm=f.get("confirm"))
            if not ok:
                # If the token itself is dead, the form is gone too; if only the passphrase was weak,
                # keep the form so the person can try again.
                still = self._setup_name(token)
                return self._send(render_setup(token, name=still, message=msg), 400)
            return self._send(render_setup("", name=name, done=True), 200)

        def _post_logout(self):
            sid = auth.cookie_from_header(self.headers.get("Cookie"))
            who = auth.session_for(sid)
            if who and not auth.check_csrf(who, self._form().get("csrf")):
                return self._send(render_denied(), 403)
            auth.destroy_session(sid)
            return self._redirect("/login", (("Set-Cookie", auth.clear_cookie(self.headers.get("Host"))),))

        def _post_write(self, path):
            """Scoped writes. The ACTING connector is the SESSION — never the URL, never the body.

            Three independent gates, in order: (1) a session must exist; (2) `authorize()` must say
            this identity may act on the requested page; (3) `connector_writes.can_write()` must
            permit the specific field on the specific subject. Any refusal writes nothing at all.
            """
            m = re.match(r"^/c/([^/]+)/(goal|referral|training|submission|approval|drill)$", path)
            if not m:
                return self._json({"ok": False, "error": "unknown endpoint"}, 404)
            who = self._session()
            if not who:
                return self._json({"ok": False, "error": "Not signed in."}, 401)
            if not auth.check_csrf(who, self.headers.get("X-CSRF-Token")):
                return self._json({"ok": False, "error": "Request refused."}, 403)
            # A JSON endpoint must be asked in JSON — a form-encoded POST is how a cross-site page
            # would try, and it cannot set this header.
            if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
                return self._json({"ok": False, "error": "Request refused."}, 415)
            if auth.is_console_admin(who["role"]):
                return self._json({"ok": False, "error": "Operator sessions are read-only."}, 403)

            d = json.load(open(os.path.join(CRM_DIR, "data.json")))
            target = next((n for n in _connectors(d) if slug(n) == m.group(1)), None)
            scope = authorize(who, target, d) if target else None
            if scope not in ("self", "downline"):
                return self._json({"ok": False, "error": "Not available."}, 403)
            # A referral note, a training completion and a submission are acts only the person
            # themselves may make. An upline may help set a goal; nobody may complete somebody else's
            # training, and nobody submits a contact for somebody else — on a submission the bounty
            # would accrue to the wrong person.
            if m.group(2) in ("referral", "training", "submission", "approval", "drill") and scope != "self":
                return self._json({"ok": False, "error": "Not available."}, 403)

            body = self._body_json()
            if not isinstance(body, dict):
                return self._json({"ok": False, "error": "bad payload"}, 400)
            if body.get("actor") and str(body["actor"]).strip() != who["name"]:
                # Not an error — just ignored, loudly, so the operator log shows the attempt.
                print(f"[console] ignoring body actor={body['actor']!r}; session is {who['name']!r}",
                      file=sys.stderr)

            actor = who["name"]        # the ONLY assignment to actor in this file
            try:
                if m.group(2) == "training":
                    rec = training.mark_lesson(actor, (body.get("lesson") or "").strip())
                elif m.group(2) == "drill":
                    # A practice attempt the connector marked THEMSELVES. It is recorded as
                    # `by="self"` and can never become an outside judgement — crm/coach.py keeps the
                    # two apart, and a self-mark cannot clear a work-on item an agent flagged.
                    # Nothing here touches a rung: rungs move on lessons + CRM evidence, not practice.
                    rec = coach.record("connector", actor,
                                       (body.get("drill") or "").strip(),
                                       (body.get("verdict") or "").strip(),
                                       note=(body.get("note") or "").strip(), by="self")
                elif m.group(2) == "submission":
                    rec = writes.submit_contact(actor, body.get("fields") or {})
                elif m.group(2) == "approval":
                    rec = capr.decide(actor, (body.get("id") or "").strip(),
                                      (body.get("decision") or "").strip(),
                                      edited=body.get("edited"))
                elif m.group(2) == "goal":
                    rec = writes.set_goal_targets(actor, (body.get("subject") or "").strip(),
                                                  body.get("targets") or {})
                else:
                    rec = writes.set_referral_fields(actor, body.get("companyId"),
                                                     body.get("fields") or {})
                return self._json({"ok": True, "saved": rec})
            except ValueError as e:
                return self._json({"ok": False, "error": str(e)}, 400)
            except (writes.ScopeError, training.ScopeError, capr.ApprovalError) as e:
                return self._json({"ok": False, "error": str(e)}, 403)
            except Exception as e:
                print("console write error:", e, file=sys.stderr)
                return self._json({"ok": False, "error": "save failed"}, 500)

        def log_message(self, *a):
            pass

    srv = HTTPServer((host, port), H)
    accounts = auth.list_users()
    print(f"Connector Console (staged preview) → http://{host}:{port}/login")
    print(f"  auth: {len(accounts)} account(s); "
          f"{sum(1 for u in accounts if u['passphraseSet'])} with a passphrase set")
    if not accounts:
        print("  no accounts — nobody can sign in. Issue one:\n"
              '    python3 processes/partnerships/connector-console/server.py '
              '--issue-setup-token "<name>"')
    return srv


def sample_fixture():
    """A synthetic connector with a book, a downline, and submissions in every state.

    Exists because the live CRM cannot reach these states — the program is pre-launch and no connector
    has joined — so nothing on a real render exercises the populated page. Every name here is visibly
    a fixture ("Sample Connector (fixture — not a real person)", "(sample)") so an exported page can never be mistaken for a real
    person's ledger. Written 2026-08-11 when the `_SAMPLE-*.html` files in `_out/` turned out to have
    no generator behind them: a sample nobody can rebuild is a stale artifact, not a fixture.
    """
    today = datetime.date.today()
    old = (today - datetime.timedelta(days=120)).isoformat()
    r0 = {L["slug"]: {"at": old, "by": "Sample Connector (fixture — not a real person)"}
          for L in training.curriculum().get("R0", [])}
    r1 = {L["slug"]: {"at": old, "by": "Sample Connector (fixture — not a real person)",
                      **({"confirmedAt": old, "confirmedBy": "the Founder"}
                         if training.needs_confirmation(L, "R1") else {})}
          for L in training.curriculum().get("R1", [])}
    return {
        "companies": [
            {"id": "sc1", "name": "Northside Dental (sample)", "referrer": "Sample Connector (fixture — not a real person)",
             "vertical": "Dental"},
            {"id": "sc2", "name": "Harbor Landscaping (sample)", "referrer": "Sample Connector (fixture — not a real person)",
             "vertical": "Landscaping"},
            {"id": "sc3", "name": "Cedar Auto Body (sample)", "referrer": "Second Connector (fixture)"},
            {"id": "sc4", "name": "Lakeside Physio (sample)",
             "referrer": "Sample Connector (fixture — not a real person)"},
            {"id": "sc5", "name": "Bay Street Dental (sample)",
             "referrer": "Sample Connector (fixture — not a real person)"},
        ],
        "deals": [
            {"id": "sd1", "companyId": "sc1", "stage": "live", "retainer": 3000,
             "stageSince": (today - datetime.timedelta(days=140)).isoformat()},
            {"id": "sd2", "companyId": "sc2", "stage": "audit",
             "stageSince": (today - datetime.timedelta(days=9)).isoformat()},
            {"id": "sd3", "companyId": "sc3", "stage": "live", "retainer": 3000,
             "stageSince": (today - datetime.timedelta(days=40)).isoformat()},
            {"id": "sd4", "companyId": "sc4", "stage": "discovery",
             "stageSince": (today - datetime.timedelta(days=26)).isoformat()},
            {"id": "sd5", "companyId": "sc5", "stage": "proposal",
             "stageSince": (today - datetime.timedelta(days=5)).isoformat()},
        ],
        "contacts": [
            {"id": "sp1", "name": "Sample Connector (fixture — not a real person)", "kind": "internal", "teamRole": "connector",
             "teamStatus": "active"},
            {"id": "sp2", "name": "Second Connector (fixture)", "kind": "internal", "teamRole": "connector",
             "teamStatus": "active"},
            {"id": "sp3", "name": "Dana Reyes (sample)", "companyId": "sc1", "role": "Owner"},
        ],
        "activities": [{"date": (today - datetime.timedelta(days=4)).isoformat(),
                        "companyId": "sc1", "type": "call", "summary": "sample"}],
        "meta": {
            "referralTiers": {"rates": [10, 12.5, 15], "thresholds": [6, 11], "override": 1},
            "repRecruiters": {"Second Connector (fixture)": "Sample Connector (fixture — not a real person)"},
            "referralMode": {"sc2": "sourcer"},
            "connectorTraining": {"Sample Connector (fixture — not a real person)": {"R0": {"lessons": r0, "completedAt": old},
                                                       "R1": {"lessons": r1, "completedAt": old}},
                                  "Second Connector (fixture)": {"R0": {"lessons": dict(r0), "completedAt": old}}},
            # v3 fixture data — one of each state, so every new section renders something real.
            "connectorPredictions": [
                {"id": f"p{i}", "connector": "Sample Connector (fixture — not a real person)",
                 "subject": f"sc{i}", "confidence": conf, "at": old, "by": "x",
                 "resolved": True, "outcome": out, "resolvedAt": old}
                for i, (conf, out) in enumerate(
                    [(80, "client"), (75, "client"), (60, "dead"), (30, "dead"), (85, "client"),
                     (45, "dead")])],
            "connectorApprovals": [
                {"id": "apr-fixture-1", "submissionId": "sub-c",
                 "connector": "Sample Connector (fixture — not a real person)",
                 "business": "Lakeside Physio (sample)",
                 "draft": "Hi Tom — Sample Connector mentioned you'd been buried in after-hours "
                          "calls. We build the kind of system that answers them. Worth 15 minutes?",
                 "status": "pending", "createdAt": old, "createdBy": "the Founder", "rungAtDraft": "A0",
                 "releaseAfter": None}],
            "connectorIncidents": [],
            "connectorSubmissions": [
                {"id": "sub-a", "connector": "Sample Connector (fixture — not a real person)", "mode": "sourcer", "status": "booked",
                 "business": "Harbor Landscaping (sample)", "contact": "Ray Ellis (sample)",
                 "email": "ray@harbor.example", "phone": "", "provenance": "they do my mother's yard",
                 "consent": "yes", "note": "", "submittedAt": (today - datetime.timedelta(days=21)).isoformat(),
                 "verifiedAt": (today - datetime.timedelta(days=20)).isoformat(), "verifiedBy": "the Founder"},
                {"id": "sub-b", "connector": "Sample Connector (fixture — not a real person)", "mode": "sourcer", "status": "verified",
                 "business": "Cedar Auto Body (sample)", "contact": "Marta Cole (sample)",
                 "email": "", "phone": "555-0142", "provenance": "fixed my truck twice",
                 "consent": "unknown", "note": "", "submittedAt": (today - datetime.timedelta(days=6)).isoformat(),
                 "verifiedAt": (today - datetime.timedelta(days=5)).isoformat(), "verifiedBy": "the Founder"},
                {"id": "sub-c", "connector": "Sample Connector (fixture — not a real person)", "mode": "sourcer", "status": "pending",
                 "business": "Lakeside Physio (sample)", "contact": "Tom Vance (sample)",
                 "email": "tom@lakeside.example", "phone": "", "provenance": "my physio",
                 "consent": "no", "note": "just started asking about after-hours calls",
                 "submittedAt": (today - datetime.timedelta(days=1)).isoformat()},
                {"id": "sub-d", "connector": "Sample Connector (fixture — not a real person)", "mode": "sourcer", "status": "rejected",
                 "business": "Unreachable Co (sample)", "contact": "—", "email": "x@x.example",
                 "phone": "", "provenance": "met at an expo", "consent": "unknown", "note": "",
                 "submittedAt": (today - datetime.timedelta(days=30)).isoformat(),
                 "verifiedAt": (today - datetime.timedelta(days=29)).isoformat(),
                 "verifiedBy": "the Founder", "reason": "number disconnected, no web presence"},
            ],
        },
    }


def render_samples():
    d = sample_fixture()
    # The ghost read is normally derived from yourco's real git-reconstructed board, which knows
    # nothing about synthetic companies — so the section would render empty and the fixture could not
    # demonstrate it. Injected here, and ONLY here: `console_data` takes the real one by default.
    fixture_ghost = {"measuredRungs": 4, "totalRungs": 6, "ghost": [
        {"id": "sd1", "company": "Northside Dental (sample)", "real": "live", "ghost": "live",
         "rungsBehind": 0, "rungsAhead": 0, "daysBehind": -4, "priced": True, "evGap": 0,
         "unpricedRungs": [], "explain": "on pace"},
        {"id": "sd2", "company": "Harbor Landscaping (sample)", "real": "audit", "ghost": "proposal",
         "rungsBehind": 1, "rungsAhead": 0, "daysBehind": 12, "priced": True, "evGap": 1800,
         "unpricedRungs": [], "explain": "our own median reaches proposal in 9d; this has sat 21d"},
        {"id": "sd4", "company": "Lakeside Physio (sample)", "real": "discovery", "ghost": "audit",
         "rungsBehind": 1, "rungsAhead": 0, "daysBehind": 6, "priced": False, "evGap": None,
         "unpricedRungs": ["audit"], "explain": "we have not run enough deals through audit"},
        {"id": "sd5", "company": "Bay Street Dental (sample)", "real": "proposal", "ghost": "audit",
         "rungsBehind": 0, "rungsAhead": 1, "daysBehind": -7, "priced": True, "evGap": 0,
         "unpricedRungs": [], "explain": "moved faster than our own median"},
    ]}
    outs = {}
    # populated: a full console. gate: somebody who has not finished R0 training.
    outs["_SAMPLE-populated"] = render("Sample Connector (fixture — not a real person)", d=d, events=[],
                                       ghost_data=fixture_ghost)
    gated = json.loads(json.dumps(d))
    gated["meta"]["connectorTraining"]["Sample Connector (fixture — not a real person)"] = {}
    outs["_SAMPLE-gate"] = render("Sample Connector (fixture — not a real person)", d=gated, events=[])
    # unlocked: the downline member's own (smaller) console.
    outs["_SAMPLE-unlocked"] = render("Second Connector (fixture)", d=d, events=[])
    outs["_SAMPLE-verify-queue"] = render_verify_queue(writes.pending_submissions(d), "", "the Founder")
    os.makedirs(OUT, exist_ok=True)
    for name, page in outs.items():
        if page:
            open(os.path.join(OUT, f"{name}.html"), "w", encoding="utf-8").write(page)
    return [n for n, p in outs.items() if p]


def main():
    ap = argparse.ArgumentParser(description="yourco Connector Console — staged")
    ap.add_argument("--render", metavar="NAME", help="render one connector's console to _out/")
    ap.add_argument("--all", action="store_true", help="render every connector")
    ap.add_argument("--list", action="store_true", help="list connector contacts")
    ap.add_argument("--sample", action="store_true",
                    help="render the fixture consoles to _out/_SAMPLE-*.html (no CRM data touched)")
    ap.add_argument("--serve", nargs="?", const=DEFAULT_PORT, type=int, metavar="PORT")
    ap.add_argument("--issue-setup-token", metavar="NAME",
                    help="mint a single-use setup link so NAME can set their own passphrase")
    ap.add_argument("--role", default="connector", choices=auth.VALID_ROLES,
                    help="with --issue-setup-token: account role (default connector). "
                         "partner = HQ+CRM+console · advisor = CRM+console · connector = console only")
    ap.add_argument("--hours", type=float, default=auth.SETUP_TOKEN_HOURS,
                    help="with --issue-setup-token: how long the link is valid")
    ap.add_argument("--auth-list", action="store_true", help="list console accounts (no secrets)")
    ap.add_argument("--auth-revoke", metavar="NAME", help="delete an account and end its sessions")
    a = ap.parse_args()

    if a.issue_setup_token:
        name = a.issue_setup_token.strip()
        if a.role == "connector" and name not in _connectors():
            print(f"{name!r} is not a connector contact in the CRM. Add them to the CRM first "
                  f"(--list shows who exists), or pass --role operator.")
            return 1
        token, expires = auth.issue_setup_token(name, role=a.role, hours=a.hours)
        print(f"Setup link for {name} ({a.role}) — single use, expires {expires}:\n")
        print(f"  http://127.0.0.1:{DEFAULT_PORT}/setup?token={token}\n")
        print("Hand this to them over a channel you already trust. It works once. yourco never learns\n"
              "the passphrase they choose, and cannot recover it — a lost one is re-issued, not looked up.")
        return
    if a.auth_list:
        us = auth.list_users()
        print(f"# Connector Console accounts — {len(us)}\n")
        if not us:
            print("None. Nobody can sign in (the store fails closed, not open).")
        for u in us:
            bits = ["passphrase set" if u["passphraseSet"] else "NO PASSPHRASE"]
            if u["locked"]:
                bits.append(f"LOCKED until {u['lockedUntil']}")
            if u["setupPending"]:
                bits.append(f"setup link pending (expires {u['setupExpires']})")
            if u["lastLogin"]:
                bits.append(f"last login {u['lastLogin']}")
            print(f"  {u['role']:<9} {u['name']:<26} {' · '.join(bits)}")
        print(f"\nStore: {os.path.relpath(auth.STORE, ROOT)} (gitignored, 0600, hashes only)")
        return
    if a.auth_revoke:
        print(f"Revoked {a.auth_revoke!r} — account deleted, sessions ended."
              if auth.revoke(a.auth_revoke) else f"No account named {a.auth_revoke!r}.")
        return
    if a.list:
        for n in _connectors():
            print(n)
        return
    if a.sample:
        made = render_samples()
        print(f"Rendered {len(made)} fixture page(s) → {os.path.relpath(OUT, ROOT)}/")
        for n in made:
            print(f"  {n}.html")
        print("\nSynthetic data only — no CRM record was read or written.")
        return
    if a.render:
        p = render_to_file(a.render)
        print(p or f"No connector contact named {a.render!r} in the CRM "
                   f"(--list shows who exists).")
        return
    if a.all:
        names = _connectors()
        for n in names:
            render_to_file(n)
        print(f"Rendered {len(names)} console(s) → {os.path.relpath(OUT, ROOT)}/")
        return
    if a.serve is not None:
        return serve(a.serve).serve_forever()
    ap.print_help()


if __name__ == "__main__":
    main()
