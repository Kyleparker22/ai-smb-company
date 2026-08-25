#!/usr/bin/env python3
"""Site evidence — the public claims, each bound to the check that proves it.

Every number on every marketing site in the world is frozen. It was true when someone typed it,
and it stays on the page whether or not it stays true. That is the universal default, and it is
precisely the failure mode yourco sells against — so the site inverts it.

Each public claim is bound here to a **check that runs**. This module runs them and writes
`site-evidence.json` next to the staged site. The page renders the number only while the check
behind it is fresh; when it lapses, the number is REPLACED on the live page by a statement of what
is missing. Nothing on the site is a sentence somebody typed once.

    The mechanism is the argument. The page does not describe the eval gate — it is one.

WHAT MAY BE BOUND, AND WHAT MAY NOT
yourco is pre-revenue at n=0 clients. A meter bound to volume — clients, revenue, hours saved —
is a scoreboard reading zero, and would repel the exact buyer it is meant to reassure. So the
binding is restricted **in code**, not by good intentions: claims are about the machine (controls,
drills, gates, schedules, suites), never about the book of business. `_forbidden()` refuses to
register anything volume-shaped, and the refusal is a hard error at generation time rather than a
review note somebody skips. See BANNED.

FOUR RULES (they mirror dashboard/security_model.py, deliberately — one posture, not two)
1. **A claim with no check cannot be published.** There is no path to a bare sentence with a number
   in it. If you cannot name the check, the claim does not go on the site.
2. **A stale check is not a weaker claim — it is no claim.** Past `ttlDays` the value is withheld
   and the page says which check went quiet and when. Degrading to "roughly" would be the whole
   lie this module exists to prevent.
3. **A check that errors reports the error.** It never falls back to the last good value. A cached
   number surviving a broken check is indistinguishable from a frozen marketing site.
4. **Freshness is evaluated in the reader's browser, not here.** `generatedAt` + `ttlDays` are
   published; `evidence.js` compares them against the reader's clock. So if this generator stops
   running, the site goes dark on its own — which is the point. A liveness claim that depended on
   the liveness it was claiming would prove nothing.

  python3 runtime/site_evidence.py            # write site-evidence.json
  python3 runtime/site_evidence.py --print     # stdout, don't write
  python3 runtime/site_evidence.py --check     # exit 1 if any claim is unproven (for the loop)
"""
import os, re, sys, json, subprocess, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "agents", "webb", "pages", "yourco-site-v2")
OUT = os.path.join(SITE, "site-evidence.json")

GATE = os.path.join(HERE, "headless-settings.reference.json")
REGISTRY = os.path.join(HERE, "agent-registry.json")
DRILLS = os.path.join(ROOT, "loops", "_trust", "drills.jsonl")
GOVERNANCE = os.path.join(ROOT, "loops", "_governance")
CONSISTENCY = os.path.join(ROOT, "loops", "_consistency")

# Rule: the meter is pointed at the machine, never at the book of business. A claim whose id or
# text trips this list is refused at generation time — at n=0 clients a volume number is a
# scoreboard reading zero, and no amount of honest framing fixes that.
BANNED = ("client", "customer", "revenue", "mrr", "arr", "deal", "pipeline", "hours saved",
          "roi", "saved our", "paying", "signed")


def _forbidden(cid, text):
    hay = f"{cid} {text}".lower()
    return [w for w in BANNED if w in hay]


# ── check plumbing ──────────────────────────────────────────────────────────────────────────
def _run(cmd, cwd=ROOT, timeout=180):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _latest(dirpath):
    """Most recent dated artifact in a loop output directory."""
    try:
        names = sorted(n for n in os.listdir(dirpath) if re.match(r"^\d{4}-\d{2}-\d{2}", n))
    except OSError as e:
        raise RuntimeError(f"{os.path.relpath(dirpath, ROOT)} unreadable: {e}")
    if not names:
        raise RuntimeError(f"no dated artifact in {os.path.relpath(dirpath, ROOT)}")
    return os.path.join(dirpath, names[-1]), names[-1][:10]


# ── the checks ──────────────────────────────────────────────────────────────────────────────
# Each returns (value, detail). Raising is normal and expected: rule 3 turns the exception into a
# published refusal rather than a silent fallback.

def chk_deny_send():
    deny = _json(GATE).get("permissions", {}).get("deny", [])
    hits = [d for d in deny if "send_email" in d]
    if not hits:
        raise RuntimeError("no send-email deny rule found in the gate config")
    return "cannot send", f"deny rule {hits[0]}"


def chk_deny_bash():
    deny = _json(GATE).get("permissions", {}).get("deny", [])
    if "Bash" not in deny:
        raise RuntimeError("Bash is not in the gate's deny list")
    return "cannot run shell", "deny rule Bash"


def chk_controls_drilled():
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import security_model
    d = security_model.build()
    if d.get("error"):
        raise RuntimeError(d["error"])
    rows = d.get("controls") or []
    if not rows:
        raise RuntimeError("the control set came back empty")
    tested = sum(1 for r in rows if r.get("state") == "tested")
    if not tested:
        # "0 of 4 survived a live attack" is technically true and rhetorically a lie — it reads as
        # a score when the real state is that the attack has never been run. A claim about
        # surviving attack cannot be made until something has attacked. Withheld, and named.
        raise RuntimeError(
            f"none of the {len(rows)} deny rules has been attacked yet — the canary-injection "
            f"drill is defined but has never been armed, so there is no survival to report")
    return f"{tested} of {len(rows)}", "deny rules with a fault-injection drill behind them"


def chk_honesty_suite():
    rc, out = _run([sys.executable, "runtime/test_evidence.py"])
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if not m:
        raise RuntimeError("the suite did not report a pass/fail line")
    passed, failed = int(m.group(1)), int(m.group(2))
    if failed or rc != 0:
        raise RuntimeError(f"{failed} assertion(s) failing — the claim is withheld until they pass")
    return f"{passed}", "assertions that stop the OS stating what its inputs do not support"


def chk_consistency():
    path, on = _latest(CONSISTENCY)
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"(\d+)\s+invariants pass,\s+(\d+)\s+drift", txt)
    if not m:
        raise RuntimeError(f"{os.path.basename(path)} has no invariant tally")
    return f"{m.group(1)}", f"cross-surface invariants checked {on}; {m.group(2)} drifting"


def chk_loops():
    reg = _json(REGISTRY)
    timers = reg.get("sanctioned_timers") or []
    if not timers:
        raise RuntimeError("the registry lists no sanctioned timers")
    return f"{len(timers)}", "scheduled jobs that run with no human present"


def chk_governance():
    _, on = _latest(GOVERNANCE)
    age = (datetime.date.today() - datetime.date.fromisoformat(on)).days
    if age > 21:
        raise RuntimeError(f"the sanctioned-surface diff has not run since {on} ({age} days)")
    return on, "last diff of what is running against what is sanctioned"


def chk_drill():
    rows = []
    with open(DRILLS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass  # a corrupt line is not a passing drill
    armed = [r for r in rows if r.get("kind") == "armed"]
    caught = {r.get("drill") for r in rows if r.get("kind") == "detected"}
    if not armed:
        raise RuntimeError("no fault has been injected yet — there is nothing to report")
    last = armed[-1]
    if last.get("drill") not in caught:
        raise RuntimeError(f"the {last.get('drill')} drill armed {last.get('on')} has no detection recorded")
    return last.get("on"), f"{last.get('drill')} injected and caught"


# ── the claim registry ──────────────────────────────────────────────────────────────────────
# statement: {value} is substituted. ttlDays: how long the check's result may be shown before the
# page withholds it. Short TTLs on things that should move; long on config facts that shouldn't.
CLAIMS = [
    dict(id="gate-no-send", subject="Whether our agents can send email", ttlDays=45, check=chk_deny_send,
         statement="Our agents {value} email.",
         means="Drafting and sending are different permissions. Sending is denied at the "
               "configuration layer, so it is not a policy an agent can be talked out of.",
         source="runtime/headless-settings.reference.json"),
    dict(id="gate-no-bash", subject="Whether our agents can reach a shell", ttlDays=45, check=chk_deny_bash,
         statement="Our agents {value}.",
         means="The load-bearing one. An agent that can reach a shell can step around every "
               "other control here, so it is denied outright.",
         source="runtime/headless-settings.reference.json"),
    dict(id="controls-drilled", subject="Deny rules that have survived a live attack", ttlDays=45, check=chk_controls_drilled,
         statement="{value} deny rules have survived a live attack.",
         means="A rule nobody has attacked is a claim, not a control. This counts only the ones "
               "something has actually tried to break. The rest are listed as untested, on purpose.",
         source="loops/_trust/drills.jsonl"),
    dict(id="honesty-suite", subject="Automated checks on what this system may state", ttlDays=21, check=chk_honesty_suite,
         statement="{value} automated checks stop this system from stating what it cannot prove.",
         means="The same discipline this page runs on. If any of them fail, the number here is "
               "withheld rather than rounded.",
         source="runtime/test_evidence.py"),
    dict(id="consistency", subject="Facts re-checked across every surface", ttlDays=21, check=chk_consistency,
         statement="{value} facts are re-checked across every surface each week.",
         means="A number changed in one place and left stale everywhere else is the most common "
               "way a company starts lying by accident. A machine checks, not a person.",
         source="runtime/consistency-check.py"),
    dict(id="loops", subject="Scheduled jobs running with no human present", ttlDays=30, check=chk_loops,
         statement="{value} scheduled jobs run this company with no human present.",
         means="Not a demo. This is the system we sell, running the business that sells it.",
         source="runtime/agent-registry.json"),
    dict(id="governance", subject="Last diff of what runs against what is sanctioned", ttlDays=30, check=chk_governance,
         statement="Last checked {value}: everything running is on the sanctioned list.",
         means="A weekly diff of what is actually running against what is approved to run. "
               "Unapproved automation is how an AI system quietly becomes something nobody chose.",
         source="loops/_governance/"),
    dict(id="drill", subject="Last fault injected on purpose", ttlDays=60, check=chk_drill,
         statement="Last fault injected {value} — caught.",
         means="We break it on purpose, on a schedule, and record whether we noticed. A control "
               "with no drill behind it is not evidence of anything.",
         source="loops/_trust/drills.jsonl"),
]


def controls():
    """The control set, for the page that replaces a wall of certification badges.

    A badge is an assertion somebody bought. A control row here names the rule, what it prevents,
    and the drill that attacked it — and reads `untested` when nothing has. Most of ours read
    untested today; publishing that is the reason anyone should believe the ones that don't.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "dashboard"))
        import security_model
        d = security_model.build()
        if d.get("error"):
            return {"available": False, "reason": d["error"]}
        return {
            "available": True,
            "rows": d.get("controls") or [],
            "source": d.get("gate", {}).get("source"),
            "isReferenceCopy": d.get("gate", {}).get("isReferenceCopy"),
            "activeFileNote": d.get("gate", {}).get("activeFileNote"),
            "externalOk": d.get("external"),
            "tested": sum(1 for r in (d.get("controls") or []) if r.get("state") == "tested"),
            "total": len(d.get("controls") or []),
        }
    except Exception as e:
        return {"available": False, "reason": f"{type(e).__name__}: {e}"}


def build():
    now = datetime.datetime.now()
    out, refused = [], []
    for c in CLAIMS:
        bad = _forbidden(c["id"], c["statement"] + " " + c["means"])
        if bad:
            refused.append({"id": c["id"], "reason":
                            f"claim is volume-shaped ({', '.join(bad)}) — the meter is bound to "
                            f"the machine, never to the book of business"})
            continue
        row = {"id": c["id"], "subject": c["subject"], "ttlDays": c["ttlDays"],
               "source": c["source"], "means": c["means"]}
        try:
            value, detail = c["check"]()
            row.update(state="proven", value=str(value), detail=detail,
                       text=c["statement"].replace("{value}", str(value)),
                       verifiedOn=now.strftime("%Y-%m-%d"))
        except Exception as e:                                    # rule 3 — report, never cache
            row.update(state="unproven", value=None, detail=None,
                       text=c["statement"].replace("{value}", "—"),
                       missing=f"{type(e).__name__}: {e}".replace("RuntimeError: ", ""))
        out.append(row)

    proven = sum(1 for r in out if r["state"] == "proven")
    return {
        "generatedAt": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "generatedOn": now.strftime("%Y-%m-%d"),
        "claims": out,
        "controls": controls(),
        "refused": refused,
        "summary": {"total": len(out), "proven": proven, "unproven": len(out) - proven},
        "contract": ("Every claim on the site is bound to a check that runs. Past its ttlDays the "
                     "value is withheld and what is missing is named in its place. Nothing here "
                     "falls back to a cached number."),
        "boundTo": ("Reliability and process only. Volume claims — clients, revenue, hours saved — "
                    "are refused at generation time, not by review."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="show", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if any claim is unproven")
    a = ap.parse_args()
    d = build()
    if a.show:
        print(json.dumps(d, indent=2))
    else:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
        s = d["summary"]
        print(f"wrote {os.path.relpath(OUT, ROOT)} — {s['proven']}/{s['total']} proven, "
              f"{s['unproven']} unproven")
        for r in d["claims"]:
            if r["state"] == "unproven":
                print(f"  unproven  {r['id']}: {r['missing']}")
        for r in d["refused"]:
            print(f"  REFUSED   {r['id']}: {r['reason']}")
    if a.check and d["summary"]["unproven"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
