#!/usr/bin/env python3
"""Digest Claude Code session transcripts into compact, friction-focused markdown.

Used by the monthly session-friction-audit (processes/loops/session-friction-audit.md).
Reads this machine's transcripts for THIS project and emits one digest .md per session
containing: metadata, every real user message (truncated), permission denials, and deduped
tool errors — the raw material for the friction-clustering analysts.

  python3 runtime/session-digest.py [--since DAYS] [--out DIR]

Defaults: --since 35 (monthly cadence + overlap), --out ~/.yourco/session-digests/
Output goes OUTSIDE the repo on purpose: digests can contain secrets the Founder pasted into chat,
so they are never committed — and `~/Documents` on this Mac is iCloud-synced (Desktop &
Documents Folders sync is ON), so a gitignored path inside the repo still uploads to iCloud
and, on rapid rewrite, leaves " 2.md" conflict copies that silently double the corpus.
`~/.yourco/` is outside both. The audit run still deletes the digests when done.

Prints a one-line-per-session table to stdout so the caller sees the corpus at a glance.
"""
import json, os, re, sys, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Claude Code stores transcripts under ~/.claude/projects/<path-with-nonalnum->->->dashes>/
PROJECT_KEY = re.sub(r"[^a-zA-Z0-9]", "-", ROOT)
SRC = os.path.join(os.path.expanduser("~/.claude/projects"), PROJECT_KEY)

MAX_USER_MSG = 1500
MAX_ERR = 300


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def is_meta(t):
    if not t.strip():
        return True
    for marker in ("<command-name>", "<local-command-stdout>", "<system-reminder>",
                   "Caveat: The messages below", "[Request interrupted"):
        if t.strip().startswith(marker):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", type=int, default=35, help="only sessions modified within N days")
    ap.add_argument("--out", default=os.path.expanduser("~/.yourco/session-digests"))
    ap.add_argument("--exclude", default="", help="session id (basename, no .jsonl) to skip")
    args = ap.parse_args()

    if not os.path.isdir(SRC):
        print(f"no transcript dir for this project: {SRC}", file=sys.stderr)
        print("(this project has no Claude Code sessions on this machine yet)", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    # clear any stale digests from a prior run
    for old in glob.glob(os.path.join(args.out, "*.md")):
        os.remove(old)

    now = None
    try:
        import time
        now = time.time()
    except Exception:
        pass
    cutoff = (now - args.since * 86400) if now else 0

    summaries = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.jsonl"))):
        sid = os.path.basename(path)[:-6]
        if sid == args.exclude:
            continue
        if cutoff and os.path.getmtime(path) < cutoff:
            continue
        size = os.path.getsize(path)
        user_msgs, denials, errors = [], [], []
        n_asst = interrupts = 0
        first_ts = last_ts = None
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                ts = rec.get("timestamp")
                if ts:
                    first_ts = first_ts or ts
                    last_ts = ts
                rtype = rec.get("type")
                msg = rec.get("message") or {}
                if rtype == "assistant":
                    n_asst += 1
                    continue
                if rtype != "user":
                    continue
                content = msg.get("content")
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            raw = b.get("content")
                            txt = (raw if isinstance(raw, str) else text_of(raw) or "")[:MAX_ERR]
                            low = txt.lower()
                            if "doesn't want to proceed" in low or "user rejected" in low or (
                                    "permission" in low and "deni" in low):
                                denials.append(txt)
                            elif b.get("is_error"):
                                errors.append(txt)
                t = text_of(content)
                if is_meta(t):
                    if "[Request interrupted" in t:
                        interrupts += 1
                    continue
                if rec.get("isMeta"):
                    continue
                user_msgs.append(t[:MAX_USER_MSG])

        if not user_msgs and not denials:
            continue
        day = (first_ts or "")[:10]
        seen, uniq_errors = set(), []
        for e in errors:
            if e[:80] not in seen:
                seen.add(e[:80])
                uniq_errors.append(e)
        with open(os.path.join(args.out, f"{day}_{sid[:8]}.md"), "w") as w:
            w.write(f"# Session {sid[:8]} — {day} → {(last_ts or '')[:10]}\n")
            w.write(f"size={size//1024}KB user_msgs={len(user_msgs)} assistant_msgs={n_asst} "
                    f"denials={len(denials)} tool_errors={len(errors)} interrupts={interrupts}\n\n")
            w.write("## User messages (in order)\n\n")
            for i, m in enumerate(user_msgs, 1):
                w.write(f"### U{i}\n{m}\n\n")
            if denials:
                w.write("## Permission denials / rejections\n\n")
                for d in denials[:20]:
                    w.write(f"- {d}\n")
                w.write("\n")
            if uniq_errors:
                w.write("## Tool errors (deduped)\n\n")
                for e in uniq_errors[:30]:
                    w.write(f"- {e}\n")
                w.write("\n")
        summaries.append((day, sid[:8], size, len(user_msgs), len(denials), len(errors)))

    summaries.sort()
    print(f"{'date':<12}{'session':<10}{'KB':>8}{'user':>6}{'deny':>6}{'errs':>6}")
    for day, sid, size, u, d, e in summaries:
        print(f"{day:<12}{sid:<10}{size//1024:>8}{u:>6}{d:>6}{e:>6}")
    print(f"\n{len(summaries)} digests written to {args.out} (gitignored — delete after the audit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
