#!/usr/bin/env python3
"""yourco — Twilio messaging connector (RCS Business Messaging / SMS) — SCAFFOLD, staged.

For the WARM / consented use case ONLY (reminders, confirmations, review asks to opted-in contacts) — NOT
cold outreach (cold stays email + SMS via Instantly). RCS to a number requires recorded opt-in; this connector
**refuses to send to any number without a consent record** (the `sms_consent` captured on the CRM contact from
the website forms).

Status: STAGED. No Twilio account / brand verification yet (see processes/rcs-messaging-setup.md — ~4–6 wk).
Creds (when they exist) come from runtime/.twilio.env (gitignored, empty scaffold today). Pure stdlib (urllib).

Guards (defense in depth):
  1. No creds  -> can't send (self-checks only).
  2. No recorded consent for the number -> REFUSED (hard stop).
  3. dry_run is the DEFAULT -> nothing leaves without an explicit --commit.
  4. On the headless runtime the approval gate also denies send/Bash — so a send is always a human action.

Usage:
  python3 runtime/twilio.py --self-check
  python3 runtime/twilio.py --send "+15551234567" "Your appt is confirmed for Tue 2pm. Reply STOP to opt out."          # dry-run
  python3 runtime/twilio.py --send "+15551234567" "..." --commit          # would send (only if creds + consent on file)
"""
import os, sys, json, base64, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
API_BASE = "https://api.twilio.com/2010-04-01"


def _load_env():
    p = os.path.join(HERE, ".twilio.env")
    if not os.path.exists(p):
        return
    for line in open(p):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
SID = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
MSG_SVC = os.environ.get("TWILIO_MESSAGING_SERVICE_SID", "").strip()
RCS_AGENT = os.environ.get("TWILIO_RCS_AGENT_ID", "").strip()


def _digits(s):
    return "".join(ch for ch in (s or "") if ch.isdigit())


def consent_for(phone):
    """Look up a recorded opt-in for this number in the CRM (the `sms_consent` + `consent` captured on the
    contact from the website forms). Returns the consent record dict, or None if no consent on file."""
    want = _digits(phone)[-10:]
    if not want or not os.path.exists(CRM):
        return None
    crm = json.load(open(CRM))
    for c in crm.get("contacts", []):
        if _digits(c.get("phone", ""))[-10:] == want and c.get("sms_consent"):
            return c.get("consent") or {"sms_consent": True}
    return None


def _req(path, form):
    if not (SID and TOKEN):
        raise RuntimeError("no Twilio creds (set TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN in runtime/.twilio.env)")
    data = urllib.parse.urlencode(form).encode()
    auth = base64.b64encode(f"{SID}:{TOKEN}".encode()).decode()
    r = urllib.request.Request(f"{API_BASE}/Accounts/{SID}/{path}", data=data, method="POST",
                               headers={"Authorization": "Basic " + auth,
                                        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Twilio POST {path} -> {e.code}: {e.read().decode()[:300]}")


def send(to, body, consent=None, dry_run=True):
    """Send a message to a CONSENTED number. Refuses without a consent record. dry_run=True by default —
    nothing sends without an explicit commit. Baseline = SMS-shape (Twilio Messages API); RCS rich content
    (cards/buttons via the Messaging Service + Content API) is the post-verification extension (TODO below).
    Verify the exact RCS/Content endpoint against current Twilio docs before binding reliance."""
    rec = consent if consent is not None else consent_for(to)
    if not rec:
        return {"refused": True, "reason": "no recorded SMS/RCS consent for this number — never message without opt-in",
                "to": to}
    if not (SID and TOKEN):
        return {"staged": True, "reason": "no Twilio creds yet (pre-verification) — would send once wired", "to": to,
                "body": body, "consent": rec}
    if dry_run:
        return {"dry_run": True, "to": to, "body": body, "via": (MSG_SVC or "from-number"), "consent": rec}
    # --- live send (post-verification) ---
    form = {"To": to, "Body": body}
    if MSG_SVC:
        form["MessagingServiceSid"] = MSG_SVC   # routes RCS-capable; falls back to SMS automatically
    else:
        form["From"] = os.environ.get("TWILIO_FROM", "")
    # TODO (when the RCS Agent is verified): send rich RCS content (cards/suggested replies) via the
    # Messaging Service tied to TWILIO_RCS_AGENT_ID using Twilio's Content API templates; SMS body is the fallback.
    return _req("Messages.json", form)


def _self_check():
    print("yourco Twilio connector — config check (SCAFFOLD / staged)")
    print(f"  creds set:        SID={bool(SID)} TOKEN={bool(TOKEN)}  (empty until the Founder wires runtime/.twilio.env)")
    print(f"  messaging svc:    {MSG_SVC or '—'}   rcs agent: {RCS_AGENT or '—'}")
    print(f"  CRM (consent src):{CRM} ({'found' if os.path.exists(CRM) else 'MISSING'})")
    print("  guard 1: refuses to send to any number without a recorded sms_consent (CRM).")
    print("  guard 2: dry_run is the default — nothing sends without --commit.")
    print("  use:     WARM/consented only (reminders/confirmations/review-asks); cold stays Instantly email+SMS.")
    print("  status:  STAGED — awaiting Twilio account + Google RCS brand verification (~4–6 wk).")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-check" in a or not a:
        sys.exit(_self_check())
    if "--send" in a:
        i = a.index("--send")
        to, body = a[i + 1], a[i + 2]
        commit = "--commit" in a
        res = send(to, body, dry_run=not commit)
        print(json.dumps(res, indent=2))
        if res.get("refused"):
            print("\nREFUSED — no opt-in on file for this number. Capture consent first (website forms).")
        elif res.get("staged") or res.get("dry_run"):
            print("\n(staged/dry-run — no message sent. Real send needs creds + verification + --commit + consent.)")
        sys.exit(0)
    print(__doc__)
