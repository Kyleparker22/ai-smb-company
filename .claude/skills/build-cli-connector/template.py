#!/usr/bin/env python3
"""<service>_cli — <one line: what this reaches and why it exists>.

DELIVERY PATH: <artifact | wrapper-injection | mcp>   <- state it, see SKILL.md
    artifact          a timer runs this, it writes loops/_<service>/<date>.md, a loop READS that file
    wrapper-injection run-loop.sh runs this before `claude -p` and injects stdout (must fail soft)
    mcp               only if an agent must choose calls interactively

WHY NOT AN MCP: <one line — no server exists / the only one is remote-OAuth and can't run on the VPS>
TERMS CHECKED:  <clause + date read>  <- commercial use AND LLM ingestion. Auto-skip if either forbids.

The agent cannot run this in a headless loop — the approval gate denies Bash, by design. Whatever this
prints has to reach the agent by one of the three paths above.
"""
import os, sys, json, argparse

ENV_FILE = "runtime/.<service>.env"          # NOTE the shape: dot-prefix, .env SUFFIX.
#   .gitignore matches `*.env`, so `runtime/.stripe.env` is ignored and `runtime/.env.stripe`
#   is NOT — the second form would commit the credential. Match the existing files
#   (.slack.env, .twilio.env, .yelp.env). See skills/wire-credentialed-connector.
REQUIRED = ["<SERVICE>_TOKEN"]


def _creds():
    """Fail loudly and usefully. Never fall back to a default or an empty call."""
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        sys.exit(f"missing {', '.join(missing)} — set it in {ENV_FILE} "
                 f"(never in source, never pasted into chat: a secret that reaches a transcript "
                 f"gets rotated)")
    return {k: os.environ[k] for k in REQUIRED}


def fetch(dry=False):
    """Read-only. Returns data, or None — and None means NO DATA, never an invented empty result."""
    if dry:
        return {"dry": True, "note": "no call made"}
    # ... the actual request ...
    raise NotImplementedError


def push(payload, commit=False):
    """Anything that sends / posts / deletes / spends. Default is the SAFE verb: without --commit this
    only shows what it would do. Mirrors the house rule that the Founder sends and agents draft."""
    if not commit:
        return {"would_do": payload, "committed": False}
    raise NotImplementedError


def render(data):
    """Human-readable artifact. If a number cannot be supported by what came back, NAME WHAT IS
    MISSING instead of printing a plausible one — the posture every HQ panel takes."""
    if data is None:
        return "No data returned. That is the finding, not a failed run — nothing was invented."
    return json.dumps(data, indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get");  g.add_argument("--dry", action="store_true")
    p = sub.add_parser("send"); p.add_argument("--commit", action="store_true",
                                               help="actually do it; without this, prints the intent only")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    _creds()
    if a.cmd == "get":
        data = fetch(dry=a.dry)
        print(json.dumps(data, indent=2) if a.json else render(data))
        # No data is a real answer AND a non-zero exit, so a caller that checks status can tell.
        # Remember: `cmd | tail` reports tail's status, so verify the ARTIFACT, not the invocation.
        sys.exit(0 if data else 2)
    if a.cmd == "send":
        out = push({}, commit=a.commit)
        print(json.dumps(out, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
