#!/usr/bin/env python3
"""yourco — rep-intake handler (the Careers / "become a Sales Rep" form).

A prospective sales rep submits the form on agents/webb/pages/yourco-site-v2/careers.html, which
POSTs {name, email, phone, note, source:"rep-intake"} to /api/rep-intake. This module records the
applicant in the CRM (a `repApplicants` entry — NOT a client deal) and returns a Slack + email
summary for the (draft-only, approval-gated) connectors to deliver.

STAGED, same gate as the rest of the site: nothing sends until the site is deployed + the runtime
connectors are live. `handle()` writes the CRM only when commit=True. Owner: Bird (referral program)
+ the Founder. Mirrors runtime/snapshot_intake.py. Program: decisions/2026-06-30_referral-program-v1.md
(reminder: the rep economics + the multi-level override are counsel-gated before any offer).

Usage:
  python3 runtime/rep_intake.py --self-check           # sample payload, dry run (no writes)
  python3 runtime/rep_intake.py --self-check --commit  # write the sample applicant into the CRM
"""
import os, sys, json, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
CRM_JS = os.path.join(REPO, "crm", "data.js")
OWNER = "Bird"
FOUNDER = "founder@yourco.example.com"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean(s, n=2000):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def validate(p):
    name = _clean(p.get("name"), 200)
    email = _clean(p.get("email"), 200).lower()
    if not name or not EMAIL_RE.match(email):
        return None, "need a name + a valid email"
    return {
        "name": name, "email": email,
        "phone": _clean(p.get("phone"), 50),
        "note": _clean(p.get("note") or p.get("about") or p.get("message"), 2000),
        "source": "rep-intake",
        "date": datetime.date.today().isoformat(),
        "status": "new — follow up",
        "owner": OWNER,
    }, None


def _write_crm(a):
    d = json.load(open(CRM))
    apps = d.setdefault("repApplicants", [])
    if any((x.get("email") or "").lower() == a["email"] for x in apps):
        return False  # dedupe by email
    apps.append(a)
    d.setdefault("meta", {})["updated"] = datetime.date.today().isoformat()
    json.dump(d, open(CRM, "w"), indent=2)
    with open(CRM_JS, "w") as f:
        f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
        f.write("window.CRM_DATA = " + json.dumps(d, indent=2) + ";\n")
    return True


def _slack(a):
    return (f":raised_hand: *New sales-rep applicant* — {a['name']}\n"
            f"• {a['email']}" + (f" · {a['phone']}" if a['phone'] else "") + "\n"
            + (f"• “{a['note']}”\n" if a['note'] else "")
            + "Referral program is counsel-gated — qualify the fit, don't offer terms yet. — Bird")


def _email(a):
    return (f"Subject: New yourco rep applicant — {a['name']}\n\n"
            f"{a['name']} applied to become an yourco sales rep.\n"
            f"Email: {a['email']}\nPhone: {a['phone'] or '—'}\n"
            f"Why / network: {a['note'] or '—'}\n\n"
            f"Logged to the CRM (repApplicants). Reminder: the rep economics + the multi-level "
            f"override are counsel-gated before any offer (decisions/2026-06-30_referral-program-v1.md).\n")


def handle(payload, commit=False):
    a, err = validate(payload)
    if err:
        return {"ok": False, "error": err}
    written = _write_crm(a) if commit else None
    return {"ok": True, "applicant": a, "written": written, "slack": _slack(a), "email": _email(a)}


def _self_check(commit):
    sample = {"name": "Jordan Rep", "email": "jordan@example.com", "phone": "704-555-0102",
              "note": "Fractional CFO with 30+ SMB-owner relationships in Yourtown.", "source": "rep-intake"}
    r = handle(sample, commit=commit)
    print(json.dumps({k: v for k, v in r.items() if k not in ("email", "slack")}, indent=2, ensure_ascii=False))
    print("\n--- slack body ---\n" + (r.get("slack") or ""))
    if commit:
        print("\nwritten to CRM repApplicants:", r.get("written"))
    return 0


if __name__ == "__main__":
    sys.exit(_self_check("--commit" in sys.argv))
