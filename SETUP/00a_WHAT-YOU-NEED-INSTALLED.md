# 00a — What you need on your laptop

> Do this before step 01. It takes about fifteen minutes and everything after it assumes it is done.

## Required

| Tool | Why | Check it |
|---|---|---|
| **Python 3.10 or newer** | Everything here — the runtime, the checks, the CRM, the dashboards, all 76 prototypes — is Python and **stdlib-only**. No framework, no build step. | `python3 --version` |
| **git** | The repo *is* the company. Every artifact is versioned. | `git --version` |
| **Claude Code CLI** | The agents. Loops run as `claude -p`; without it the runtime has nothing to call. Install: [claude.com/claude-code](https://claude.com/claude-code) | `claude --version` |
| **A terminal** | Everything is command-line. No GUI is required at any point. | — |

**3.10 is a hard floor, not a suggestion** — parts of this use `match` statements and `X | None` type
syntax, which are syntax errors on 3.9. If `python3 --version` says 3.9 or lower, upgrade first;
everything will fail in confusing ways otherwise.

## Needed only when you get there

| Tool | Needed for | Step |
|---|---|---|
| **Node.js 18+** (gives you `npx`) | MCP connectors — Slack, Gmail, Calendar are `npx` stdio servers | 04 |
| **A VPS** (any Ubuntu box, ~$8/mo) | the always-on runtime. Nothing before step 05 needs one. | 05 |
| **`gh`** (GitHub CLI) | only if you want your repo on GitHub | optional |

## Python packages

**The core needs none.** Install per feature, not up front:

```bash
pip install openpyxl        # only to read/write the financial model
pip install slack_sdk       # only once you wire Slack (step 04)
```

Full list with reasons: `requirements.txt`. One package (`pygrib`) is needed by exactly one prototype
and requires system libraries — skip it unless you are working on that prototype.

## ⚠️ Platform note

**This was built on macOS and a few commands are macOS-specific.** On Linux or WSL they need small
changes — none of them deep, but they will bite the first time:

| Command | macOS | Linux |
|---|---|---|
| in-place edit | `sed -i '' 's/a/b/'` | `sed -i 's/a/b/'` |
| open a browser | `open <url>` | `xdg-open <url>` |
| what is on a port | `lsof -ti tcp:8790` | `ss -ltnp` or install `lsof` |

`show.sh` uses `lsof` and `open`. **Windows is untested** — use WSL rather than native PowerShell.

## Confirm you are ready

```bash
python3 --version     # 3.10 or higher
git --version
claude --version
python3 runtime/consistency-check.py    # should print checks, not a traceback
```

## Done when

**All four commands above run without error, and the consistency check prints a list of checks.**

If the last one throws a traceback rather than reporting warnings, stop and fix that first — it is the
tool you will use to verify every later step.
