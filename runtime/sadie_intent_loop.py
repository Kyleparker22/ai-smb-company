#!/usr/bin/env python3
"""Sadie's scheduled intent loop — surfaces REAL prospect signal (owners venting in their own words).

Runs on a systemd timer (yourco-sadie-intent), NOT via `claude -p`: deterministic, needs network +
the Slack bot token, and the agent gate denies Bash. For the configured verticals it pulls the
high-signal FIRST-PERSON sources — **YouTube comments, Bluesky, and Reddit** (where real owners say
"I keep missing calls and losing jobs") — ranks prospects-first (reusing intent_collect's engine +
listen.py's Reddit engine), writes a board to loops/sadie/, and posts a digest to #yourco-sadie.

Google News / Alerts are deliberately NOT used here — they index published articles (news/vendor/SEO),
not people in pain (they produced ~97% noise). Wrong fishing hole for prospecting.

Autonomy: collection only (R3 — read/surface). Drafts/sends NOTHING externally; turning a signal into
cold outreach stays Reilly's gated (R1) step.

Keys (the real sources need auth — the loop skips + prints which are missing; setup:
runtime/intent-credentials-setup.md):
  • YouTube comments → YOUTUBE_API_KEY in runtime/.youtube.env
  • Bluesky         → BSKY_HANDLE + BSKY_APP_PASSWORD in runtime/.bluesky.env
  • Reddit          → REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in ~/.yourco/reddit.env
  • Slack post      → SLACK_BOT_TOKEN (from ~/.yourco/env, sourced by sadie-intent.sh)

Scope: SADIE_VERTICALS (default "Landscaping,Hardscaping" — the beachhead; YouTube has a daily quota,
so keep this focused). SADIE_TOP_N (default 12) caps the digest.
"""
import os, sys, json, datetime, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))     # runtime/
REPO = os.path.dirname(HERE)                            # repo root
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "clients", "sadie"))
import intent_collect as ic                             # YouTube/Bluesky/scoring engine
try:
    import listen as reddit_engine                      # agents/sadie/listen.py — Reddit search
except Exception:
    reddit_engine = None

BOT = os.environ.get("SLACK_BOT_TOKEN", "").strip()
CHANNEL = os.environ.get("SADIE_SLACK_CHANNEL", "#yourco-sadie")
TOP_N = int(os.environ.get("SADIE_TOP_N", "12"))
os.environ.setdefault("INTENT_HTTP_TIMEOUT", "12")     # keep each fetch snappy


def reddit_signals():
    """Reddit — owners asking for help (Sadie's listen.py engine). Needs ~/.yourco/reddit.env."""
    if reddit_engine is None:
        return []
    cid, sec = reddit_engine.load_creds()
    if not (cid and sec):
        print("  (Reddit skipped — set REDDIT_CLIENT_ID/SECRET in ~/.yourco/reddit.env)")
        return []
    try:
        token = reddit_engine.get_token(cid, sec)
    except Exception as e:
        print(f"  (Reddit auth failed: {e})")
        return []
    out, seen = [], set()
    for sub in reddit_engine.SUBREDDITS:
        for c in reddit_engine.search(token, sub):
            p = c.get("data", {})
            pid = p.get("id")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            text = (p.get("title", "") + " " + (p.get("selftext", "") or "")).replace("\n", " ")[:300]
            out.append({"name": p.get("author", ""), "domain": "", "email": "", "phone": "",
                        "intent": {"signal": text, "url": "https://reddit.com" + p.get("permalink", ""),
                                   "platform": "reddit"}, "source": ["sadie", "reddit"], "vertical": f"r/{sub}"})
    return out


def source_status():
    """Which sources can actually run this sweep — written into the board so a zero from an unkeyed
    source is never mistaken for a quiet market (learnings/ops/2026-07-20_keyless-source-loop-silent-zero.md)."""
    rd = False
    if reddit_engine is not None:
        cid, sec = reddit_engine.load_creds()
        rd = bool(cid and sec)
    return [("YouTube", bool(ic.YT_KEY)), ("Bluesky", bool(ic.BSKY_HANDLE and ic.BSKY_APP_PW)), ("Reddit", rd)]


def collect():
    verts = ic.load_verticals()
    sel = os.environ.get("SADIE_VERTICALS", "Landscaping,Hardscaping")
    names = [n.strip() for n in sel.split(",") if n.strip()]
    recs = []
    for name in names:
        cfg = verts.get(name)
        if not cfg:
            continue
        kws = cfg.get("keywords", [])
        try:
            for q in cfg.get("youtube_queries", []):       # YouTube COMMENTS = real owners venting
                recs += ic.youtube(q, cfg.get("limit", 8), comments=True, keywords=kws, vertical=name)
            for q in cfg.get("bluesky_queries", cfg.get("youtube_queries", [])):  # Bluesky = real posts
                recs += ic.bluesky(q, keywords=kws, vertical=name)
        except Exception as e:
            print(f"  (vertical {name} skipped: {e})")
    recs += reddit_signals()                               # Reddit = owners asking for help
    recs = ic._dedupe(recs)
    for r in recs:
        ic.score_record(r)
    recs.sort(key=lambda r: (ic._PRIO.get(r.get("klass"), 9), -r.get("heat", 0)))
    return names, recs


def _mix(recs):
    m = {}
    for r in recs:
        m[r["klass"]] = m.get(r["klass"], 0) + 1
    return m


def write_board(date, names, recs, srcs):
    mix = _mix(recs)
    src_line = "Sources: " + " · ".join(f"{n} {'✅' if ok else '⛔ unkeyed'}" for n, ok in srcs) + "."
    if not all(ok for _, ok in srcs):
        src_line += " ⚠️ A zero from an unkeyed source is plumbing, not a market read."
    out = [f"# Sadie intent sweep — {date}", "",
           f"{len(recs)} signal(s) from YouTube comments + Bluesky + Reddit across {len(names)} verticals. "
           f"Mix: {', '.join(f'{k} {v}' for k, v in sorted(mix.items())) or '—'}.",
           src_line,
           "Read-only — Sadie surfaces; turning a signal into outreach stays Reilly's gated step.", ""]
    for r in recs:
        it = r.get("intent", {})
        out.append(f"- **[{(it.get('signal') or '—')[:160]}]({it.get('url','')})** · "
                   f"{r.get('vertical','')} · {it.get('platform','')} · {r.get('klass')} (heat {r.get('heat',0)})")
    rel = f"loops/sadie/{date}_intent-sweep.md"
    os.makedirs(os.path.join(REPO, "loops", "sadie"), exist_ok=True)
    open(os.path.join(REPO, rel), "w").write("\n".join(out) + "\n")
    return rel, mix


def digest_text(date, names, recs, mix, board_rel, srcs):
    top = [r for r in recs if r.get("klass") in ("prospect", "business-complaint")][:TOP_N]
    lines = [f"🛰️ *Sadie intent sweep* — {date}",
             f"{len(recs)} signals (YouTube comments · Bluesky · Reddit) across {len(names)} verticals. "
             f"Mix: {', '.join(f'{k} {v}' for k, v in sorted(mix.items())) or '—'}"]
    down = [n for n, ok in srcs if not ok]
    if down:
        lines.append(f"⚠️ *Unkeyed sources this run: {', '.join(down)}* — zeros from these are plumbing, not market. "
                     f"Wire per `runtime/intent-credentials-setup.md`.")
    if top:
        lines += ["", "*Top prospects (owners in their own words):*"]
        for r in top:
            it = r.get("intent", {})
            sig = (it.get("signal") or "—")[:140]
            url = it.get("url", "")
            lines.append(f"• <{url}|{sig}> — {r.get('vertical','')} · {it.get('platform','')}")
    else:
        lines.append("_No prospect-grade signals this run. If the sources are unkeyed, add the YouTube/"
                     "Bluesky/Reddit creds (see the loop header / intent-credentials-setup.md). Board committed._")
    lines += ["", f"Full board: `{board_rel}` · _read-only; outreach stays gated (the Founder approves)._"]
    return "\n".join(lines)


def post_slack(text):
    if not BOT:
        print("(no SLACK_BOT_TOKEN — skipping Slack post; board still written)")
        return
    data = urllib.parse.urlencode({
        "channel": CHANNEL, "text": text, "username": "Sadie", "icon_emoji": ":ear:",
        "unfurl_links": "false", "unfurl_media": "false",
    }).encode()
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=data,
                                 headers={"Authorization": f"Bearer {BOT}"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        print("Slack post:", "ok" if resp.get("ok") else resp.get("error"))
    except Exception as e:
        print("Slack post failed:", e)


def attach_to_crm():
    """Lane 1 of promote_intent: signals matching companies ALREADY in the CRM attach to their
    signals[] (Hot List pills). Enrichment only — row creation stays the gated promote lane."""
    try:
        import promote_intent
        return promote_intent.attach_matched(dry_run=False)
    except Exception as e:
        print(f"  (CRM attach skipped: {e})")
        return []


def main():
    date = datetime.date.today().isoformat()
    srcs = source_status()
    names, recs = collect()
    board_rel, mix = write_board(date, names, recs, srcs)
    print(f"Wrote {board_rel} — {len(recs)} signals, mix {mix}, sources {dict(srcs)}")
    attached = attach_to_crm()
    text = digest_text(date, names, recs, mix, board_rel, srcs)
    if attached:
        text += ("\n🔗 *Hot List:* attached " + ", ".join(sorted({n for n, _ in attached}))
                 + " — signal pill(s) added in the CRM.")
    post_slack(text)


if __name__ == "__main__":
    main()
