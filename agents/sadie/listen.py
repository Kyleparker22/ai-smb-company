#!/usr/bin/env python3
"""Sadie's Reddit listening tool — read-only intent search.

Searches target subreddits for people expressing the pain yourco solves
(missed calls, lost leads, drowning in manual work, wanting to automate, asking about
AI agents). Returns a ranked list of intent posts → Sadie drafts help-first replies →
the Founder approves + posts. READ ONLY — no posting (that stays human-approved).

Credentials (you create these once, never paste them into chat):
  Register a Reddit app at https://www.reddit.com/prefs/apps  → "create app" → type "script".
  Then save the two values to ~/.yourco/reddit.env (gitignored), one per line:
      REDDIT_CLIENT_ID=your_client_id
      REDDIT_CLIENT_SECRET=your_client_secret
  (App-only OAuth — no Reddit username/password needed for public reads.)

Run:  python3 agents/sadie/listen.py
Writes a ranked sweep to loops/sadie/<date>_reddit-sweep.md and prints the top hits.
"""
import os, sys, json, base64, urllib.request, urllib.parse, datetime

ENV_FILE = os.path.expanduser("~/.yourco/reddit.env")
UA = "yourco-sadie/0.1 (intent listening; contact founder@yourco.example.com)"

# Where the intent conversations live (home services + SMB + AI-curious owners)
SUBREDDITS = [
    "smallbusiness", "Entrepreneur", "sweatystartup", "landscaping", "lawncare",
    "HVAC", "Plumbing", "Contractor", "HomeImprovement", "msp", "AskMarketing",
]
# One combined query per sub (Reddit supports OR). Tuned to yourco's pain points.
QUERY = ('"missed calls" OR "answering service" OR "can\'t keep up" OR "losing leads" '
         'OR "automate" OR "AI receptionist" OR "AI agent" OR "virtual assistant" '
         'OR "drowning in" OR "automate customer service"')
# Intent keywords for ranking
INTENT = ["missed call", "answering service", "losing lead", "lost lead", "can't keep up",
          "automate", "ai receptionist", "ai agent", "virtual assistant", "drowning",
          "no time", "behind on", "voicemail", "book more", "follow up"]


def load_creds():
    creds = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    cid = creds.get("REDDIT_CLIENT_ID") or os.environ.get("REDDIT_CLIENT_ID")
    sec = creds.get("REDDIT_CLIENT_SECRET") or os.environ.get("REDDIT_CLIENT_SECRET")
    return cid, sec


def get_token(cid, sec):
    auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request("https://www.reddit.com/api/v1/access_token", data=data,
                                 headers={"Authorization": f"Basic {auth}", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["access_token"]


def search(token, sub):
    q = urllib.parse.urlencode({"q": QUERY, "restrict_sr": "1", "sort": "new",
                                "limit": "12", "t": "month", "type": "link"})
    req = urllib.request.Request(f"https://oauth.reddit.com/r/{sub}/search?{q}",
                                 headers={"Authorization": f"bearer {token}", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("data", {}).get("children", [])
    except Exception as e:
        print(f"  · {sub}: {e}", file=sys.stderr)
        return []


def score(post):
    text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
    hits = [k for k in INTENT if k in text]
    # questions + recency boost intent
    q = "?" in post.get("title", "")
    return len(hits) + (1 if q else 0), hits


def main():
    cid, sec = load_creds()
    if not cid or not sec:
        print(f"No Reddit credentials. Create them at https://www.reddit.com/prefs/apps\n"
              f"then save to {ENV_FILE}:\n  REDDIT_CLIENT_ID=...\n  REDDIT_CLIENT_SECRET=...")
        sys.exit(1)
    token = get_token(cid, sec)
    seen, rows = set(), []
    for sub in SUBREDDITS:
        for c in search(token, sub):
            p = c.get("data", {})
            if p.get("id") in seen:
                continue
            seen.add(p.get("id"))
            s, hits = score(p)
            if s == 0:
                continue
            rows.append({"score": s, "hits": hits, "sub": sub, "title": p.get("title", ""),
                         "url": "https://reddit.com" + p.get("permalink", ""),
                         "snippet": (p.get("selftext", "") or "")[:240].replace("\n", " ")})
    rows.sort(key=lambda r: r["score"], reverse=True)
    top = rows[:25]

    date = datetime.date.today().isoformat()
    out = [f"# Sadie Reddit sweep — {date}", "",
           f"Searched {len(SUBREDDITS)} subreddits for intent. {len(rows)} matches, top {len(top)} below.",
           "Read-only — Sadie drafts help-first replies; **the Founder approves + posts.**", ""]
    for r in top:
        out.append(f"- **[{r['title']}]({r['url']})** · r/{r['sub']} · intent: {', '.join(r['hits']) or '—'}")
        if r["snippet"]:
            out.append(f"  > {r['snippet']}")
    path = f"loops/sadie/{date}_reddit-sweep.md"
    os.makedirs("loops/sadie", exist_ok=True)
    open(path, "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"\n→ wrote {path}")


if __name__ == "__main__":
    main()
