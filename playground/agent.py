#!/usr/bin/env python3
"""Run a real yourco agent against playground data.

    python3 playground/agent.py --list                 every runnable agent + its cadence
    python3 playground/agent.py --show open-loops      the prompt + what it will read (no API call)
    python3 playground/agent.py --run  open-loops      RUN IT for real against synthetic data
    python3 playground/agent.py --run  sales --model claude-sonnet-5

the Founder chose live agent runs (2026-08-07) over a dry-run simulator. This is that: the actual
`claude -p` invocation the VPS uses, with three things changed.

  1. YOURCO_DATA_ROOT points at playground/data, so the agent reads synthetic clients, a
     synthetic CRM, synthetic loop history — and writes its artifact into the sandbox.
  2. `cwd` is the playground data root, so any relative path the agent writes lands there.
  3. Tools that reach the outside world are DENIED, not merely discouraged. An agent in a
     sandbox that can email a real prospect is not in a sandbox.

PRECONDITION, STATED HONESTLY: as of 2026-08-07 the org's Anthropic API balance is exhausted
(spend fell to $0.83 across 08-01..08-06 and every model loop has been dark since ~08-04).
`--run` will fail until that is funded. It fails LOUDLY with the reason and the fix rather
than pretending, and `--show` works regardless — that is the whole design of this file.
"""
import os, sys, json, glob, shutil, argparse, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
PROMPTS = os.path.join(REPO, "runtime", "prompts")

# Every outward-facing capability, denied. The live approval gate already blocks send/delete;
# the playground blocks the whole category, because synthetic input must never produce a real
# side effect. Belt and braces: the agent also runs with cwd inside the sandbox.
DENY = [
    "Bash", "WebFetch", "WebSearch",
    "mcp__gmail__send_email", "mcp__gmail__draft_email", "mcp__gmail__delete_email",
    "mcp__gmail__batch_delete_emails", "mcp__gmail__modify_email",
    "mcp__4261ac1e-c219-4b15-aaa7-a44ae863e5de__create_draft",
    "mcp__4ff43158-c78d-4d49-89b0-36813cf0466b__slack_send_message",
    "mcp__4ff43158-c78d-4d49-89b0-36813cf0466b__slack_send_message_draft",
    "mcp__4ff43158-c78d-4d49-89b0-36813cf0466b__slack_schedule_message",
    "mcp__calendar__create-event", "mcp__calendar__update-event",
    "mcp__dfbfac5c-82b0-4ee0-be05-d5ad60064357__create_event",
]

SANDBOX_PREAMBLE = """\
[PLAYGROUND RUN — READ THIS FIRST]
You are running inside yourco's PLAYGROUND against SYNTHETIC data. Every company, person,
deal, dollar and ledger record you will read is invented by playground/seed.py. None of it
is real, and no one is waiting on the output.

Rules for this run:
- Treat the synthetic data as if it were real and do the actual job of your prompt. The point
  of this run is to see how your loop BEHAVES at this scale, so do not shortcut it.
- Write your artifact to the sandbox loops/ directory exactly as you normally would.
- Do NOT send, post, email, message, or publish anything. Those tools are denied.
- Do NOT touch the real repo, commit, or push. You are not in it.
- If the synthetic data is missing something your prompt needs, SAY SO in the artifact and
  name what was missing — that gap is a finding about the seeder or the prompt, and it is
  one of the most useful things this run can produce.

Your normal prompt follows.
--------------------------------------------------------------------------------
"""


def agents():
    out = []
    for p in sorted(glob.glob(os.path.join(PROMPTS, "*.md"))):
        n = os.path.basename(p)[:-3]
        if n.startswith("_"):
            continue
        timer = os.path.join(REPO, "runtime", "systemd", f"yourco-{n}.timer")
        cadence = ""
        if os.path.exists(timer):
            for ln in open(timer):
                if ln.strip().startswith("OnCalendar="):
                    cadence = ln.split("=", 1)[1].strip()
                    break
        out.append({"name": n, "path": p, "timer": os.path.exists(timer), "cadence": cadence})
    return out


def cmd_list():
    a = agents()
    print(f"{len(a)} runnable agent prompts (runtime/prompts/)\n")
    for x in a:
        flag = "" if x["timer"] else "   [no timer — cannot run on the VPS]"
        print(f"  {x['name']:<24} {x['cadence'] or '—':<28}{flag}")
    print("\n  --show <name>   the prompt + its inputs, no API call")
    print("  --run  <name>   run it for real against playground data")


def cmd_show(name):
    a = {x["name"]: x for x in agents()}.get(name)
    if not a:
        sys.exit(f"no prompt '{name}'. try --list")
    body = open(a["path"]).read()
    print(f"=== {name} ===")
    print(f"prompt   runtime/prompts/{name}.md ({len(body):,} chars)")
    print(f"timer    {a['cadence'] or 'NONE — this prompt can never fire on the VPS'}")
    print(f"data     {DATA}")
    if os.path.isdir(DATA):
        for sub in ("crm/data.json", "clients", "loops", "finance"):
            p = os.path.join(DATA, sub)
            if os.path.isdir(p):
                print(f"           {sub}/ — {len(os.listdir(p))} entries")
            elif os.path.exists(p):
                print(f"           {sub} — {os.path.getsize(p):,} bytes")
    else:
        print("           (not seeded — run playground/seed.py)")
    print(f"denied   {len(DENY)} outward-facing tools\n")
    print(body[:1800] + ("\n… (truncated)" if len(body) > 1800 else ""))


def cmd_run(name, model, timeout):
    if not shutil.which("claude"):
        sys.exit("`claude` CLI not on PATH — cannot run an agent.")
    if not os.path.isdir(DATA):
        sys.exit("playground not seeded. run: python3 playground/seed.py")
    a = {x["name"]: x for x in agents()}.get(name)
    if not a:
        sys.exit(f"no prompt '{name}'. try --list")

    prompt = SANDBOX_PREAMBLE + open(a["path"]).read()
    env = dict(os.environ, YOURCO_DATA_ROOT=DATA, YOURCO_PLAYGROUND="1")
    cmd = ["claude", "-p", prompt, "--disallowedTools", ",".join(DENY)]
    if model:
        cmd += ["--model", model]

    started = datetime.datetime.now()
    print(f"running '{name}' against {DATA}")
    print(f"  model     {model or 'session default'}")
    print(f"  denied    {len(DENY)} outward tools · cwd is the sandbox · git unreachable")
    print(f"  started   {started:%H:%M:%S}\n")
    try:
        r = subprocess.run(cmd, cwd=DATA, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        sys.exit(f"timed out after {timeout}s")
    out, err = r.stdout or "", r.stderr or ""
    blob = (out + err).lower()

    if r.returncode != 0 or "credit balance" in blob or "usage credits" in blob:
        print("RUN FAILED\n")
        print((err or out).strip()[:1200] or f"exit {r.returncode}, no output")
        print("\n--------------------------------------------------------------")
        if "credit balance" in blob or "usage credits" in blob:
            # The predicted blocker.
            print("Cause: the Anthropic ORG API balance is exhausted — not a playground bug.")
            print("Every model loop has been dark since ~2026-08-04 (API spend $0.83 across")
            print("08-01..08-06 vs an ~$8/day baseline).")
            print("Fix: top up + enable auto-reload at console.anthropic.com, then re-run.")
        elif "not logged in" in blob or "/login" in blob:
            # The blocker actually hit on this Mac, 2026-08-07. Different from the one above
            # and worth distinguishing: nothing is wrong with the account, the headless CLI
            # just has no credentials of its own here.
            print("Cause: the headless `claude` CLI is not authenticated on THIS machine.")
            print("Cowork sessions run on the Founder's subscription, but `claude -p` spawned as a")
            print("subprocess has no session of its own — the VPS has one, this Mac may not.")
            print("Fix: run `claude` once in a terminal and complete /login, then re-run here.")
            print("(Note this is separate from the dead org API balance; you may hit that next.)")
        else:
            print("Unrecognised failure. The command that ran was:")
            print("  claude -p <prompt> --disallowedTools <15 tools>   (cwd = playground/data)")
        print("Meanwhile `--show <agent>` works with no API call and no auth.")
        sys.exit(1)

    took = (datetime.datetime.now() - started).seconds
    print(out.strip()[:4000])
    print(f"\ndone in {took}s. artifacts written under {DATA}/loops/")
    new = sorted(glob.glob(os.path.join(DATA, "loops", "*", "*.md")), key=os.path.getmtime)[-3:]
    for p in new:
        print(f"  {os.path.relpath(p, DATA)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run an yourco agent against playground data.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--show", metavar="AGENT")
    g.add_argument("--run", metavar="AGENT")
    ap.add_argument("--model", default=None, help="e.g. claude-sonnet-5 (cheaper for a sandbox run)")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    if a.list:
        cmd_list()
    elif a.show:
        cmd_show(a.show)
    else:
        cmd_run(a.run, a.model, a.timeout)
