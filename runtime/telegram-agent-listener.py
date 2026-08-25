#!/usr/bin/env python3
"""yourco — Telegram per-agent command transport (phone sibling of the Slack control surface).

the Founder DMs the bot from his phone; this listener runs the chosen agent against his instruction
(under the host approval gate) and replies in the same DM. Same gate, same allowlist, same
injection hardening, same "listener commits because the gate-bound agent can't push" model as
runtime/slack-agent-listener.py — only the transport differs (Telegram Bot API long-poll).

Design + rationale: runtime/telegram-control-setup.md
Security model (shared): decisions/2026-06-14_slack-agent-control-surface.md
  • Only the Founder's numeric Telegram id (FOUNDER_TELEGRAM_USER_ID) may command. Everyone else is silently
    ignored — no reply, no acknowledgement the bot even exists. A bot token is not workspace-secret,
    so this allowlist is the WHOLE gate at the transport layer and is checked before anything else.
  • The agent runs under ~/.claude/settings.json: read/edit + Slack-post + Gmail-DRAFT allowed;
    send / delete / Bash DENIED. A Telegram command cannot escalate past a scheduled loop.
  • the Founder's literal message is the ONLY instruction; forwarded/quoted text and links are untrusted DATA.
  • Long-poll dials OUT to Telegram — no inbound port is opened (never switch to webhooks).

The moat-critical internals — invoke_agent (gated headless run), git_sync (trusted-daemon persistence),
_git, AGENT_ROLE, the 8/min rate limiter — are IMPORTED from the Slack listener so the two stay in lockstep.

Deploy: runtime/telegram-control-setup.md   (stdlib only — no pip install needed)
Offline config check (no connection):  python3 runtime/telegram-agent-listener.py --self-check
"""
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Import the Slack listener's shared internals by path (its filename has hyphens → can't `import`).
# Executing it only DEFINES functions/reads env — it does not connect to Slack.
_spec = importlib.util.spec_from_file_location(
    "yourco_slack_listener", os.path.join(HERE, "slack-agent-listener.py"))
shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shared)

invoke_agent = shared.invoke_agent      # gated headless run of an agent
git_sync = shared.git_sync              # trusted-daemon commit+push of what the agent wrote
_git = shared._git                      # thin git runner (cwd=REPO)
_rate_ok = shared._rate_ok              # 8/min rolling limiter (shared module state)
AGENT_ROLE = shared.AGENT_ROLE          # slug -> role (canonical map lives in the Slack listener)

# Unicode emoji per agent (Telegram renders these; the Slack listener's `:shortcode:` form does not).
AGENT_EMOJI = {
    "katie": "✍️", "david": "\U0001f4c7", "atlas": "\U0001f6f0️",
    "charles": "\U0001f4b0", "polo": "\U0001f3f7️", "kolby": "✅",
    "kortney": "\U0001f91d", "jim": "\U0001f4c5", "luka": "\U0001f3a8",
    "brett": "\U0001f9ed", "reilly": "\U0001f3af", "mario": "\U0001f50d",
    "michelle": "✏️", "Reed": "\U0001f3ac", "bella": "\U0001f52c",
    "webb": "\U0001f310", "janice": "\U0001f4cb", "kimi": "\U0001f6e0️",
    "bird": "\U0001f4c8", "harry": "\U0001f9fe", "kori": "\U0001f465",
    "sadie": "\U0001f442", "ray": "⚖️", "rafi": "\U0001f6e1️",
    "kemba": "\U0001f3d7️", "pickle": "\U0001f4c4",
}
AGENTS = set(AGENT_ROLE)                 # valid slugs, sourced from the shared role map
DEFAULT_AGENT = "atlas"                  # sticky agent for a chat until the Founder names one
ROBOT = "\U0001f916"                     # fallback emoji (kept out of f-strings for <3.12 portability)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOW_USER = os.environ.get("FOUNDER_TELEGRAM_USER_ID", "").strip()
API = f"https://api.telegram.org/bot{TOKEN}"

_sticky = {}                             # chat_id -> agent slug (in-memory; resets on restart to DEFAULT_AGENT)


# ── Telegram Bot API (stdlib only) ────────────────────────────────────────────
def _api(method, params=None, timeout=60):
    """POST to the Bot API; return the `result` payload or None on any error."""
    data = json.dumps(params or {}).encode()
    req = urllib.request.Request(f"{API}/{method}", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode())
            return body.get("result") if body.get("ok") else None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None


def send(chat_id, text):
    """Send PLAIN text (no parse_mode — agent output has code/underscores/brackets that would 400 a
    Markdown/HTML send). Truncate to Telegram's safe length."""
    _api("sendMessage", {"chat_id": chat_id, "text": (text or "")[:3500],
                         "disable_web_page_preview": True}, timeout=20)


def label(agent):
    return f"{AGENT_EMOJI.get(agent, ROBOT)} {agent.capitalize()}"


# ── Routing: prefix + sticky ──────────────────────────────────────────────────
def route(chat_id, text):
    """Return (agent, instruction). First word matching a slug selects + sticks that agent;
    otherwise the chat's sticky agent (default atlas) handles it."""
    first, _, rest = text.partition(" ")
    slug = first.rstrip(":").lower()
    if slug in AGENTS:
        _sticky[chat_id] = slug
        return slug, rest.strip()
    return _sticky.get(chat_id, DEFAULT_AGENT), text.strip()


def handle_command(chat_id, text):
    """Handle /commands. Return True if the message was a command (and was handled)."""
    cmd, _, arg = text.partition(" ")
    cmd, arg = cmd.lower().lstrip("/"), arg.strip().lower()
    if cmd in ("start", "help"):
        cur = _sticky.get(chat_id, DEFAULT_AGENT)
        send(chat_id,
             "yourco command line.\n"
             "• `agent: your instruction` — e.g. `katie: draft a post on eval gates`\n"
             "• bare messages go to your current agent (sticky).\n"
             "• /agents — list · /agent <name> — switch · /whoami — current\n"
             f"Current agent: {label(cur)}. Gate holds: I can draft/post but never send, delete, or run Bash.")
        return True
    if cmd == "agents":
        send(chat_id, "Agents:\n" + "\n".join(
            f"{label(a)} — {AGENT_ROLE[a]}" for a in sorted(AGENTS)))
        return True
    if cmd == "whoami":
        send(chat_id, f"Current agent: {label(_sticky.get(chat_id, DEFAULT_AGENT))}.")
        return True
    if cmd == "agent":
        if arg in AGENTS:
            _sticky[chat_id] = arg
            send(chat_id, f"Switched to {label(arg)} — {AGENT_ROLE[arg]}.")
        elif arg:
            send(chat_id, f"Don't know '{arg}'. Try /agents.")
        else:
            send(chat_id, f"Current agent: {label(_sticky.get(chat_id, DEFAULT_AGENT))}. "
                          f"Set with `/agent <name>`.")
        return True
    return False


# ── Message handling ──────────────────────────────────────────────────────────
def handle_message(msg):
    frm = str((msg.get("from") or {}).get("id", ""))
    if not frm or frm != ALLOW_USER:                 # the Founder only — silent for everyone else
        return
    chat_id = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").strip()
    if chat_id is None or not text:
        return
    if text.startswith("/") and handle_command(chat_id, text):
        return
    if not _rate_ok():
        send(chat_id, "Easy now, sugar — give me a sec between commands.")
        return

    agent, instruction = route(chat_id, text)
    if not instruction:                              # e.g. "katie:" with nothing after it
        send(chat_id, f"{label(agent)} is listening — what do you need?")
        return
    send(chat_id, f"_On it — {label(agent)} is working…_")
    _git(["pull", "--rebase", "--autostash"])        # give the agent the latest repo state
    send(chat_id, f"{label(agent)}:\n{invoke_agent(agent, instruction)}")
    changed = git_sync(agent)                         # persist what the gate-bound agent can't push itself
    if changed:
        send(chat_id, "Committed + pushed: " + ", ".join(changed))


def run():
    missing = [k for k, v in (("TELEGRAM_BOT_TOKEN", TOKEN),
                              ("FOUNDER_TELEGRAM_USER_ID", ALLOW_USER)) if not v]
    if missing:
        print("[telegram-listener] missing env: " + ", ".join(missing))
        return 2
    me = _api("getMe", timeout=15)
    if not me:
        print("[telegram-listener] getMe failed — check TELEGRAM_BOT_TOKEN / network")
        return 2

    # Drain any backlog WITHOUT processing it: a command queued while the service was down should not
    # fire on restart (a day-old ask acting now is a footgun). Advance the offset past everything pending.
    offset = None
    drained = _api("getUpdates", {"timeout": 0, "allowed_updates": ["message"]}, timeout=15) or []
    if drained:
        offset = drained[-1]["update_id"] + 1
    print(f"[telegram-listener] connected as @{me.get('username')} · "
          f"commanding user={ALLOW_USER} · {len(AGENTS)} agents · skipped {len(drained)} backlog msg(s)")

    while True:
        updates = _api("getUpdates",
                       {"timeout": 50, "offset": offset, "allowed_updates": ["message"]},
                       timeout=60)
        if updates is None:                          # network hiccup — back off and retry
            time.sleep(3)
            continue
        for u in updates:
            offset = u["update_id"] + 1
            if "message" in u:                       # ignore edited_message/other update types
                try:
                    handle_message(u["message"])
                except Exception as e:               # one bad message must not kill the daemon
                    print(f"[telegram-listener] handler error: {e}")


def self_check():
    print(f"yourco Telegram agent listener — config check ({len(AGENTS)} agents)")
    print(f"bot token set: {bool(TOKEN)} | allow-user set: {bool(ALLOW_USER)} | default agent: {DEFAULT_AGENT}")
    print(f"claude bin: {shared.CLAUDE_BIN} | timeout: {shared.TIMEOUT}s | rate: {shared.RATE_MAX}/min")
    print("routing: `agent: …` selects+sticks; bare msg → sticky. Commands: /agents /agent /whoami /help")
    print("gate reminder: agent runs under ~/.claude/settings.json — send/delete/Bash stay denied.")
    return 0


if __name__ == "__main__":
    sys.exit(self_check() if "--self-check" in sys.argv else run())
