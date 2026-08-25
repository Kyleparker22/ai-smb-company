#!/usr/bin/env python3
"""Sample Product — verified-alert sender (runs on the VPS, which has internet).

The Worker does all the MATCHING (it has subscribers + the verified feed + the
sent-ledger in D1, no egress needed) and exposes the result at /api/alert-queue.
This script only SENDS: pull the queue, text (Twilio) / email (SMTP) each
subscriber the verified storms they haven't gotten, then POST the keys back to
/api/alert-sent so nobody gets the same storm twice.

"We verify a storm is good before it sends" = the queue only contains storms the
engine graded and the AI marked GO; this sender never decides — it just delivers.

Env (in /home/claudeops/.config/storm-verified.env, same file as the publisher):
  INGEST_URL          e.g. https://sweet-opal-720.higgsfield.app/api/ingest
  INGEST_SECRET       shared secret (same one the Worker holds)
  TWILIO_ACCOUNT_SID  } all three present -> SMS turns on
  TWILIO_AUTH_TOKEN   }
  TWILIO_FROM         } the sending number, e.g. +18135550142
  SMTP_HOST/PORT/USER/PASS/FROM  } all present -> email turns on (optional)

Until Twilio creds are set the script is a DRY RUN: it logs exactly what it WOULD
send and does NOT mark anything sent, so the moment the number is connected the
backlog flushes. Stdlib only (urllib/smtplib) — no pip install on the VPS.
"""
import base64
import json
import os
import smtplib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15"

# Durable local record of delivered (subscriber,storm,channel) pairs that have NOT yet been
# confirmed to the Worker's sent-ledger. Every delivered pair is appended here BEFORE the batch
# POST, so a failed/interrupted POST can't lose the record and re-blast the whole queue next run
# (the original single-point-of-failure). Gitignored. Replayed at startup, cleared on POST success.
JOURNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sent_journal.jsonl")


def _base_url() -> str:
    ingest = os.environ.get("INGEST_URL", "").strip()
    if not ingest:
        sys.exit("INGEST_URL not set")
    # strip the trailing /api/ingest to get the app origin
    return ingest.rsplit("/api/ingest", 1)[0].rstrip("/")


def _get_queue(base: str, secret: str):
    url = f"{base}/api/alert-queue?secret={urllib.parse.quote(secret)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "x-ingest-secret": secret})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("queue", [])


def _post_sent(base: str, secret: str, sent: list) -> bool:
    """POST delivered pairs to the Worker's sent-ledger, with retries. Returns True on confirmed
    success. The Worker dedups by (subscriber,storm,channel), so re-POSTing a pair is a safe no-op."""
    if not sent:
        return True
    data = json.dumps({"sent": sent}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                f"{base}/api/alert-sent",
                data=data,
                headers={"User-Agent": UA, "x-ingest-secret": secret, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                print("  alert-sent ->", r.status, r.read().decode()[:120])
            return True
        except Exception as e:  # noqa: BLE001 — network/HTTP; retry then give up (records stay journaled)
            print(f"    ! alert-sent attempt {attempt + 1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    return False


def _journal_append(records: list):
    if not records:
        return
    with open(JOURNAL, "a") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
        f.flush()
        os.fsync(f.fileno())  # survive a power/process kill between send and next run


def _journal_read() -> list:
    if not os.path.exists(JOURNAL):
        return []
    out = []
    with open(JOURNAL) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def _journal_clear():
    try:
        os.remove(JOURNAL)
    except OSError:
        pass


def _twilio_ready() -> bool:
    return all(os.environ.get(k) for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"))


def _smtp_ready() -> bool:
    return all(os.environ.get(k) for k in ("SMTP_HOST", "SMTP_FROM"))


def _send_sms(to: str, body: str) -> bool:
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    token = os.environ["TWILIO_AUTH_TOKEN"]
    frm = os.environ["TWILIO_FROM"]
    data = urllib.parse.urlencode({"From": frm, "To": to, "Body": body}).encode()
    req = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        data=data,
        headers={"Authorization": "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode()},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"    ! twilio {e.code}: {e.read().decode()[:160]}")
        return False
    except (urllib.error.URLError, OSError) as e:
        # A network timeout / connection failure used to propagate out of the per-item loop and
        # kill the run before the ledger POST — re-blasting everyone already sent. Treat as a
        # non-delivery for this subscriber and move on.
        print(f"    ! twilio network error: {e}")
        return False


def _send_email(to: str, subject: str, body: str) -> bool:
    msg = EmailMessage()
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        host = os.environ["SMTP_HOST"]
        port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            if os.environ.get("SMTP_USER"):
                s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASS", ""))
            s.send_message(msg)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"    ! smtp error: {e}")
        return False


def _compose(name: str, storms: list, base: str) -> str:
    lines = [f"⚡ Sample Product — {len(storms)} confirmed storm{'s' if len(storms) != 1 else ''} in your area:"]
    for s in storms[:5]:
        bits = [f"{s['county']} {s['date']} (grade {s['grade']})"]
        if s.get("max_hail_in"):
            bits.append(f"{s['max_hail_in']}\" hail")
        if s.get("max_wind_mph"):
            bits.append(f"{s['max_wind_mph']} mph")
        if s.get("tornado"):
            bits.append("tornado")
        lines.append("• " + " · ".join(bits))
    if len(storms) > 5:
        lines.append(f"…+{len(storms) - 5} more")
    lines.append(f"Details: {base}/feed")
    return "\n".join(lines)


def main():
    base = _base_url()
    secret = os.environ.get("INGEST_SECRET", "")
    if not secret:
        sys.exit("INGEST_SECRET not set")

    sms_on = _twilio_ready()
    email_on = _smtp_ready()
    print(f"alert sender: sms={'on' if sms_on else 'DRY'} email={'on' if email_on else 'DRY'}")

    # Replay any records stranded by a prior failed/interrupted POST BEFORE pulling the queue, so
    # the Worker records them and doesn't re-queue (and thus re-send) those pairs this run.
    pending = _journal_read()
    if pending:
        print(f"replaying {len(pending)} journaled (subscriber,storm) record(s) from a prior run…")
        if _post_sent(base, secret, pending):
            _journal_clear()
        else:
            print("  replay POST failed — leaving journal; will retry next run")

    queue = _get_queue(base, secret)
    if not queue:
        print("queue empty — nothing to send")
        return

    sent = []
    for item in queue:
        # Isolate each subscriber: a malformed queue item or a send exception must skip forward,
        # never abort the run (which would leave earlier deliveries unrecorded → duplicated).
        try:
            sub = item["subscriber"]
            storms = item["storms"]
            chan = sub.get("channel", "sms")
            body = _compose(sub["name"], storms, base)
            keys = [s["key"] for s in storms]
            print(f"→ {sub['name']} ({chan}) — {len(storms)} storm(s)")

            delivered = False
            want_sms = chan in ("sms", "both") and sub.get("phone")
            want_email = chan in ("email", "both") and sub.get("email")

            if want_sms:
                if sms_on:
                    delivered = _send_sms(sub["phone"], body) or delivered
                else:
                    print(f"    [DRY] SMS to {sub['phone']}:\n      " + body.replace("\n", "\n      "))
            if want_email:
                if email_on:
                    delivered = _send_email(sub["email"], "Verified storm in your area", body) or delivered
                else:
                    print(f"    [DRY] EMAIL to {sub['email']} (subject: Verified storm in your area)")

            # Only record as sent when something actually went out. In dry-run nothing is marked,
            # so the backlog flushes the moment Twilio/SMTP is connected.
            if delivered:
                recs = [{"subscriber_id": sub["id"], "storm_key": k, "channel": chan} for k in keys]
                _journal_append(recs)   # durable BEFORE the batch POST — the anti-re-blast guard
                sent.extend(recs)
        except Exception as e:  # noqa: BLE001 — one bad item never kills the whole send
            print(f"    ! skipped a queue item ({e})")
            continue

    # Batch-confirm to the Worker; only drop the journal once the ledger is confirmed written.
    if _post_sent(base, secret, sent):
        _journal_clear()
        print(f"done — delivered alerts recorded for {len(sent)} (subscriber,storm) pair(s)")
    else:
        print(f"done — {len(sent)} pair(s) delivered but ledger POST failed; journaled for replay next run")


if __name__ == "__main__":
    main()
