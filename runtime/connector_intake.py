#!/usr/bin/env python3
"""yourco — submit a contact by text or email. The console is the ledger; this is the doorway.

The research finding that drove this: partner portals are the thing partners don't use. A connector's
actual job happens on a job site, in a truck, thirty seconds after a conversation ends — and a
beautiful web console is the wrong shape for that moment. Activation is the only number that matters
at n=0 connectors, so the interaction has to live where they already are.

So: **text or email yourco a business owner's details and it becomes a submission.** The console keeps
doing what it is good at — the audit trail, the ledger, the arithmetic — and stops being the only door.

Three properties this holds, and the third is the one people get wrong:

1. **Identity comes from the channel, never the message.** The connector is resolved by matching the
   sender's phone/email against their CRM contact record. A message that *says* "this is from Alice"
   is treated as text, because a body claiming an identity is exactly how you would spoof a bounty
   into someone else's account.
2. **The scoped write path is unchanged.** Parsing produces fields; `connector_writes.submit_contact`
   still decides. Every rule — provenance required, duplicate detection, the cap, the ladder gate —
   applies identically whether the submission came from a form or a text, because there is one
   write path and this is not a second one.
3. **It drafts a reply; it never sends one.** `the Founder sends; agents draft` (CLAUDE.md) is not suspended
   because the channel is convenient. The reply comes back as a draft for the normal send path.

**Provenance in an unstructured message.** `provenance` is a required field and a legal one — yourco
becomes the caller on a sourced contact, so "how do you know them" has to be answerable per row. A
free-text message often won't contain it. This module does **not** invent one: if it cannot find a
provenance statement, the submission is not created and the drafted reply asks the one question.
An intake that guessed would put an unanswerable contact into a queue yourco then calls.

Channels:
  • **email** — parse the body. Wired: yourco already runs a Gmail connector.
  • **sms** — same parser, different transport. NEEDS A NUMBER + KEYS: see `_README` note below;
    `.claude/skills/wire-credentialed-connector/` is the procedure. Until those exist `--channel sms`
    parses and reports but has no transport, and says so rather than pretending.

Usage:
  python3 runtime/connector_intake.py --demo
  python3 runtime/connector_intake.py --from "alice@example.com" --text "..." [--commit]
"""
import os, re, sys, json, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRM_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") \
    else os.path.join(ROOT, "crm")
sys.path.insert(0, os.path.join(ROOT, "crm"))
import connector_writes as writes
import connector_ladder as ladder

CRM = os.path.join(CRM_DIR, "data.json")

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
# How a person actually writes provenance in a text message. Deliberately conservative: a miss costs
# one clarifying reply, a false positive puts a contact yourco cannot vouch for into the call queue.
PROVENANCE_RE = re.compile(
    r"\b(my|our)\s+(\w+\s+){0,3}(dentist|doctor|physio|barber|mechanic|accountant|plumber|"
    r"electrician|landscaper|contractor|vet|chiropractor|trainer|attorney|lawyer|realtor|agent|"
    r"neighbou?r|cousin|brother|sister|uncle|aunt|friend|client|customer|supplier|banker)\b"
    r"|\b(i|we)\s+(have\s+)?(know|known|met|worked|used|golf|play|go|went|train|bank)\w*\b"
    r"|\bknown\s+(him|her|them|the\s+owner)\b"
    r"|\b(he|she|they)\s+(does|did|do|has\s+done)\s+(my|our)\b",
    re.I)
LABELLED = {
    "business": re.compile(r"^\s*(?:business|company|biz)\s*[:\-]\s*(.+)$", re.I | re.M),
    "contact": re.compile(r"^\s*(?:owner|contact|name)\s*[:\-]\s*(.+)$", re.I | re.M),
    "provenance": re.compile(r"^\s*(?:how|how i know|know|via|source)\s*[:\-]\s*(.+)$", re.I | re.M),
    "note": re.compile(r"^\s*(?:note|notes|why)\s*[:\-]\s*(.+)$", re.I | re.M),
}
CONSENT_YES = re.compile(r"\b(they|he|she)\s+(know|knows|expect|expects|are expecting|is expecting)\b"
                         r"|\bi\s+(told|mentioned|warned|asked)\s+(them|him|her)\b", re.I)
CONSENT_NO = re.compile(r"\b(they|he|she)\s+(don'?t|does\s?n'?t|do\s+not)\s+know\b"
                        r"|\bhaven'?t\s+(told|mentioned|asked)\b|\bno\s+heads?[\s-]?up\b", re.I)


def resolve_connector(sender, d):
    """Sender → connector name, matched on their OWN contact record. The message body is never trusted."""
    sender = (sender or "").strip().lower()
    if not sender:
        return None
    digits = re.sub(r"\D", "", sender)
    for c in d.get("contacts", []):
        if c.get("kind") != "internal" or c.get("teamRole") != "connector":
            continue
        if (c.get("email") or "").strip().lower() == sender:
            return (c.get("name") or "").strip()
        cph = re.sub(r"\D", "", c.get("phone") or "")
        if digits and cph and len(digits) >= 10 and cph[-10:] == digits[-10:]:
            return (c.get("name") or "").strip()
    return None


def _segments(text):
    """First line → clean comma/dash-delimited segments, greeting and contact details removed.

    ONE definition, used by both the business and the owner-name extraction. They were written
    separately at first and immediately diverged — the greeting strip was applied to one and not the
    other, so "Hey yourco — Cedar Auto Body" filed the business name as the owner's name.
    """
    first = EMAIL_RE.sub("", PHONE_RE.sub("", (text.splitlines() or [""])[0]))
    # The dash class must include en/em dashes — "Hey yourco — Cedar…" is the most common opening
    # and a plain-hyphen class silently leaves the dash (and the greeting) behind.
    first = re.sub(r"^\s*(hey|hi|hello|yo|good\s+\w+)\b[\s,!.\-–—]*(yourco|team|guys|folks)?[\s,!.\-–—]*",
                   "", first.strip(), flags=re.I)
    return [s for s in (x.strip(" ,.-–—\t") for x in re.split(r"\s*[,;]\s*|\s+[–—]\s+", first)) if s]


def parse(text):
    """Free text → submission fields. Returns (fields, missing). Never invents a value.

    Labelled lines win over prose: someone who writes "Business: X" has told us exactly what they mean
    and guessing past that would be worse than useless.
    """
    text = (text or "").strip()
    fields, missing = {}, []
    for key, rx in LABELLED.items():
        m = rx.search(text)
        if m:
            fields[key] = m.group(1).strip()

    em = EMAIL_RE.search(text)
    if em:
        fields["email"] = em.group(0)
    ph = PHONE_RE.search(text)
    if ph:
        fields["phone"] = ph.group(0).strip()

    if "provenance" not in fields:
        m = PROVENANCE_RE.search(text)
        if m:
            # Keep the words they actually wrote — a normalised paraphrase would put language in the
            # connector's mouth on the one field that has to be defensible to a regulator later. But
            # bound it to the CLAUSE, not the whole message: cut at the nearest clause break on each
            # side, so "Cedar Auto Body 555-0142, my mechanic, fixed my truck twice" yields
            # "my mechanic, fixed my truck twice" and not the business name as well.
            start = max(text.rfind(c, 0, m.start()) for c in ".,;—–\n") + 1
            end = min((p for p in (text.find(c, m.end()) for c in ".;\n") if p != -1), default=-1)
            fields["provenance"] = text[start:(end if end != -1 else len(text))].strip(" ,-–—")

    segs = _segments(text)
    if "business" not in fields and segs and len(segs[0]) < 120:
        # People write "Northside Dental, Dana Reyes, dana@x.test — she's my dentist". The business is
        # the FIRST segment, not the whole line: taking the line gives you the entire anecdote as a
        # company name.
        fields["business"] = segs[0]

    if CONSENT_YES.search(text):
        fields["consent"] = "yes"
    elif CONSENT_NO.search(text):
        fields["consent"] = "no"
    else:
        fields["consent"] = "unknown"

    if "contact" not in fields and len(segs) > 1:
        # Positional: "Northside Dental, Dana Reyes, dana@…" — the second segment, but ONLY when it
        # looks like a person (2–3 capitalised words, no digits) AND is not just the business name
        # again. Anything less certain is asked for rather than guessed; a wrong owner name is worse
        # than an absent one, because yourco opens a call with it.
        cand = segs[1]
        # Leading tokens may be initials ("J. Smith", "A Person") — a single capital is a real name
        # shape and rejecting it silently drops the owner from perfectly ordinary messages. The LAST
        # token must still be a proper word, so "Cedar Auto B" doesn't read as a person.
        if (re.fullmatch(r"(?:[A-Z][\w'’.-]*\s+){1,2}[A-Z][\w'’-]{1,}", cand or "")
                and cand.lower() != (fields.get("business") or "").lower()):
            fields["contact"] = cand

    # Every field the scoped write path requires is checked HERE, so a message that cannot be logged
    # comes back as a question rather than as a refusal. A ScopeError from `submit_contact` should
    # mean a real refusal — a duplicate, the cap, the ladder gate — never a field we knew was blank.
    for req in ("business", "contact", "provenance"):
        if not (fields.get(req) or "").strip():
            missing.append(req)
    if not ((fields.get("email") or "").strip() or (fields.get("phone") or "").strip()):
        missing.append("reach")
    return fields, missing


ASK = {
    "business": "the business name",
    "provenance": "how you know them (we have to be able to say where the contact came from — "
                  "we're the ones making the call)",
    "reach": "an email or phone number for them",
    "contact": "the owner's name",
}


def draft_reply(connector, fields, missing, result=None, error=None):
    """The reply yourco would send. A DRAFT — this module never sends anything."""
    who = (connector or "there").split()[0]
    if error:
        return f"Thanks {who} — we couldn't log that one: {error} Reply with the fix and we'll add it."
    if missing:
        wants = " and ".join(ASK.get(m, m) for m in missing)
        got = fields.get("business") or "that one"
        return (f"Thanks {who} — got {got}. Before we can call them we need {wants}. "
                f"Reply with it and it's logged.")
    b = fields.get("business")
    return (f"Logged, {who} — {b} is in. We'll verify within 24–48 hours and you'll get $25 the moment "
            f"we do, plus $25 more if it turns into a real conversation. Nothing is payable until the "
            f"program launches. We'll show you our first message to them before it goes anywhere.")


def handle(sender, text, channel="email", d=None, commit=False, log=None):
    """One inbound message → a submission (or a question). Returns a report dict; never sends."""
    d0 = d if d is not None else json.load(open(CRM))
    who = resolve_connector(sender, d0)
    if not who:
        return {"ok": False, "connector": None, "channel": channel,
                "reason": "unknown-sender",
                "reply": None,   # deliberately no reply drafted to an unrecognised number/address
                "note": ("Sender does not match any connector's own contact record. No reply is "
                         "drafted and nothing is written — an unrecognised sender is not told what "
                         "this address is for.")}
    fields, missing = parse(text)
    if missing:
        return {"ok": False, "connector": who, "channel": channel, "reason": "incomplete",
                "fields": fields, "missing": missing,
                "reply": draft_reply(who, fields, missing)}
    try:
        rec = writes.submit_contact(who, fields, d=(None if commit else d0),
                                    commit=commit, log=log)
    except writes.ScopeError as e:
        return {"ok": False, "connector": who, "channel": channel, "reason": "refused",
                "fields": fields, "error": str(e),
                "reply": draft_reply(who, fields, [], error=str(e))}
    return {"ok": True, "connector": who, "channel": channel, "fields": fields,
            "submission": rec, "reply": draft_reply(who, fields, [], result=rec)}


DEMO = [
    ("alice@example.com",
     "Northside Dental, Dana Reyes, dana@northside.test — she's been my dentist for six years and "
     "she's drowning in missed calls. I told her someone might reach out."),
    ("555-111-2222", "Hey yourco — Cedar Auto Body 727-555-0142, my mechanic, fixed my truck twice."),
    ("alice@example.com", "Lakeside Physio, tom@lakeside.test"),          # no provenance → asks
    ("+15550000000", "Some Business, my barber, 555-1234"),               # unknown sender → silence
]


def main():
    ap = argparse.ArgumentParser(description="yourco connector intake — text/email → submission")
    ap.add_argument("--from", dest="sender", help="sender phone or email")
    ap.add_argument("--text", help="the message body")
    ap.add_argument("--channel", default="email", choices=("email", "sms"))
    ap.add_argument("--commit", action="store_true", help="actually write the submission")
    ap.add_argument("--demo", action="store_true", help="run the worked examples against the live CRM (dry)")
    a = ap.parse_args()

    if a.channel == "sms":
        print("NOTE: SMS has no transport wired yet — no number, no keys. Parsing works; delivery does\n"
              "      not. Procedure: .claude/skills/wire-credentialed-connector/\n")
    if a.demo:
        # A FIXTURE connector, not the live CRM: no real connector has joined (the program is
        # pre-launch), so running the demo against real data would only ever show "unknown sender"
        # and prove nothing about the parser. Synthetic, and labelled as such.
        d = {"companies": [], "deals": [], "activities": [],
             "contacts": [{"id": "demo1", "name": "Alice Demo (fixture)", "kind": "internal",
                           "teamRole": "connector", "teamStatus": "active",
                           "email": "alice@example.com", "phone": "555-111-2222"}],
             "meta": {"referralTiers": {"rates": [10, 12.5, 15]}, "connectorSubmissions": [],
                      "connectorTraining": {}}}
        print("(demo runs against a synthetic connector — no CRM record is read or written)")
    else:
        d = json.load(open(CRM))
    cases = DEMO if a.demo else [(a.sender, a.text)]
    if not a.demo and not (a.sender and a.text):
        ap.error("give --from and --text, or --demo")
    for sender, text in cases:
        r = handle(sender, text, channel=a.channel, d=d, commit=a.commit)
        print(f"\n─ from {sender}")
        print(f"  {text[:96]}")
        print(f"  → {'LOGGED' if r['ok'] else r['reason'].upper()}"
              + (f" as {r['connector']}" if r.get("connector") else ""))
        if r.get("missing"):
            print(f"    missing: {', '.join(r['missing'])}")
        if r.get("reply"):
            print(f"    draft reply: {r['reply'][:150]}")
        elif not r.get("connector"):
            print(f"    {r['note']}")
    if not a.commit:
        print("\n(dry run — nothing written. Add --commit to log real submissions.)")


if __name__ == "__main__":
    main()
