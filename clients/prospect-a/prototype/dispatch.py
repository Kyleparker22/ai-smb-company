#!/usr/bin/env python3
"""
yourco · Storm Dispatch (Twilio SMS) — Prospect A Roofing

The last mile: take an APPROVED, verified storm + a chosen action + a target
group, and text Nick's roofers. Goes from demo to a thing Nick can actually use.

SAFETY — this NEVER sends unless ALL of these are true:
  1. Twilio creds are present (env or .env), and
  2. DISPATCH_DRY_RUN=0, and
  3. you pass --send on the command line.
Otherwise it's a DRY RUN: it prints exactly what it *would* send, to whom, and
stops. That mirrors the yourco approval gate (nothing outbound without approval).

Setup:  cp .env.example .env         # fill Twilio creds
        cp roster.example.json roster.json   # fill real roofers (gitignored)

Usage:  python3 storm_poc.py                 # produce last_run.json first
        python3 dispatch.py                   # dry-run: top storm, its action, all crew
        python3 dispatch.py --to area:Jacksonville
        python3 dispatch.py --storm 2 --action standby --to team:A
        python3 dispatch.py --to area:Jacksonville --send    # real send (needs creds + DRY_RUN=0)
"""
import argparse, base64, json, os, sys, urllib.parse, urllib.request


# ---------- config / env ----------
def load_env():
    """Minimal .env loader (no dependency). Real env vars win over .env."""
    path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    return {
        "sid":     os.environ.get("TWILIO_ACCOUNT_SID", ""),
        "token":   os.environ.get("TWILIO_AUTH_TOKEN", ""),
        "msg_sid": os.environ.get("TWILIO_MESSAGING_SERVICE_SID", ""),
        "from":    os.environ.get("TWILIO_FROM", ""),
        "dry_env": os.environ.get("DISPATCH_DRY_RUN", "1") != "0",
    }


def here(name):
    return os.path.join(os.path.dirname(__file__), name)


def load_roster():
    for f in ("roster.json", "roster.example.json"):
        p = here(f)
        if os.path.exists(p):
            r = json.load(open(p))
            r["_source"] = f
            return r
    sys.exit("No roster found (roster.json / roster.example.json).")


def load_run():
    p = here("last_run.json")
    if not os.path.exists(p):
        sys.exit("No last_run.json — run `python3 storm_poc.py` first.")
    return json.load(open(p))


# ---------- message + targeting ----------
def hazard_str(v):
    bits = []
    if v.get("max_hail_in") is not None:  bits.append(f'HAIL to {v["max_hail_in"]:.2f}"')
    if v.get("max_wind_mph") is not None: bits.append(f'WIND {v["max_wind_mph"]:.0f}mph')
    elif v.get("wind_damage"):            bits.append("WIND damage")
    if v.get("tornado"):                  bits.append("TORNADO")
    return " + ".join(bits) or "storm reports"


def compose(storm, trigger, sig):
    msg = trigger["template"].format(county=storm["county"], md=storm["date"][5:],
                                     hazard=hazard_str(storm), conf=storm["confidence"])
    return msg if msg.rstrip().endswith(sig) else msg


def select(roster, target):
    roofers = roster.get("roofers", [])
    if not target or target == "all":
        return roofers
    if ":" not in target:
        sys.exit(f"Bad --to '{target}'. Use all | area:<X> | team:<X> | person:<name>.")
    key, val = target.split(":", 1)
    key, val = key.strip().lower(), val.strip().lower()
    field = {"area": "area", "team": "team", "person": "name"}.get(key)
    if not field:
        sys.exit(f"Unknown target '{key}'. Use area / team / person.")
    return [r for r in roofers if str(r.get(field, "")).lower() == val
            or (field == "name" and val in str(r.get("name", "")).lower())]


# ---------- Twilio send (raw HTTP, no SDK) ----------
def send_one(cfg, to, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{cfg['sid']}/Messages.json"
    data = {"To": to, "Body": body}
    if cfg["msg_sid"]:
        data["MessagingServiceSid"] = cfg["msg_sid"]
    else:
        data["From"] = cfg["from"]
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    req.add_header("Authorization", "Basic " + base64.b64encode(
        f"{cfg['sid']}:{cfg['token']}".encode()).decode())
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode()).get("sid")


def main():
    ap = argparse.ArgumentParser(description="Dispatch a verified storm alert to Nick's roofers.")
    ap.add_argument("--storm", type=int, default=0, help="index into roofing-relevant storms (default 0 = top)")
    ap.add_argument("--action", help="trigger key (default = the storm's recommended action)")
    ap.add_argument("--to", default="all", help="all | area:<X> | team:<X> | person:<name>")
    ap.add_argument("--send", action="store_true", help="actually send (needs creds + DISPATCH_DRY_RUN=0)")
    a = ap.parse_args()

    cfg = load_env()
    roster = load_roster()
    run = load_run()
    sig = roster.get("reply_signature", "Nick")

    rel = [v for v in run["verified"] if v["roofing_relevant"]]
    if not rel:
        sys.exit("No roofing-relevant storms in last_run.json.")
    if not (0 <= a.storm < len(rel)):
        sys.exit(f"--storm {a.storm} out of range (0..{len(rel)-1}).")
    storm = rel[a.storm]

    trig_by_key = {t["key"]: t for t in run["triggers"]}
    key = a.action or storm.get("trigger")
    if key not in trig_by_key:
        sys.exit(f"Unknown action '{key}'. Options: {', '.join(trig_by_key)}.")
    trigger = trig_by_key[key]

    body = compose(storm, trigger, sig)
    recipients = select(roster, a.to)

    # decide dry-run
    have_creds = bool(cfg["sid"] and cfg["token"] and (cfg["msg_sid"] or cfg["from"]))
    dry = (not a.send) or cfg["dry_env"] or (not have_creds)

    print("=" * 62)
    print(f"  DISPATCH  ·  {roster.get('business','')}   (roster: {roster['_source']})")
    print("=" * 62)
    print(f"  Storm   : {storm['county']} County · {storm['date']} · {hazard_str(storm)} · {storm['confidence']}")
    print(f"  Action  : {trigger['label']}  ({key})")
    print(f"  Target  : {a.to}   ->  {len(recipients)} roofer(s)")
    print(f"  Message : \"{body}\"  ({len(body)} chars)")
    print("  Recipients:")
    for r in recipients:
        print(f"    · {r.get('name','?'):12} {r.get('phone','?'):14} [{r.get('area','')}/{r.get('team','')}]")
    if not recipients:
        print("    (none matched — check --to)")
    print("-" * 62)

    if dry:
        why = []
        if not a.send:        why.append("no --send")
        if cfg["dry_env"]:    why.append("DISPATCH_DRY_RUN=1")
        if not have_creds:    why.append("no Twilio creds")
        print(f"  DRY RUN — nothing sent.  ({'; '.join(why)})")
        print("  To go live: fill .env (DRY_RUN=0) + roster.json, then add --send.")
        return

    print(f"  SENDING via Twilio to {len(recipients)} roofer(s)…")
    ok = 0
    for r in recipients:
        try:
            sid = send_one(cfg, r["phone"], body)
            print(f"    ✓ {r.get('name','?'):12} {r['phone']:14} sid={sid}")
            ok += 1
        except Exception as e:
            print(f"    ✗ {r.get('name','?'):12} {r.get('phone','?'):14} FAILED: {e}")
    print("-" * 62)
    print(f"  Sent {ok}/{len(recipients)}.")


if __name__ == "__main__":
    main()
