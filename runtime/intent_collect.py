#!/usr/bin/env python3
"""yourco — Sadie's intent collector (free + compliant sources only).

Pulls intent signals from sources that are FREE *and* allowed (per agents/rafi/social-platform-
scraping-assessment.md) and writes them in Sadie's hand-off schema for the cold pipeline
(processes/outbound/intent-outreach.md). It does NOT scrape ToS-prohibited platforms (X/Meta/LinkedIn) —
those go through paid official APIs / licensed data, not this tool.

Sources here (all free + ToS-clean):
  • YouTube Data API — official, free within quota (key in runtime/.youtube.env). Searches videos for
    intent phrases; `--comments` pulls matching top comments (prospect-level — real owners venting).
  • Google News RSS — Google's public news search feed. Auto-built from each vertical's phrases, NO
    setup/key. Company + event signal (a business in the news, a storm in a roofing market).
  • RSS / Atom feeds — any public feed: **Google Alerts RSS** (broadest free coverage — set up per
    runtime/intent-alerts-setup.md) + niche-forum feeds. No key, no scraping.
  (WebSearch is the assistant's in-session tool — Sadie runs it in Cowork and appends to the same JSON.)

Output schema (one object per signal):
  {name, domain?, email?, phone?, intent:{signal,url,platform}, source:["sadie","<src>"]}

Usage:
  python3 runtime/intent_collect.py --self-check
  python3 runtime/intent_collect.py --list-verticals
  # one vertical (YouTube COMMENTS = real owners venting, keyword-filtered, + any configured RSS):
  python3 runtime/intent_collect.py --vertical "Landscaping" --comments
  # sweep ALL configured verticals → one intent-<vertical>.json each:
  python3 runtime/intent_collect.py --all-verticals --comments
  # add --prospects-only to keep just owner-venting + low-rated-business signals (drop news/vendor/noise):
  python3 runtime/intent_collect.py --vertical "Landscaping" --comments --prospects-only

Every signal is auto-scored + ranked (klass: prospect / business-complaint / business / unknown / news /
vendor; prospects first by heat). --prospects-only filters to the high-value ones.
  # ad-hoc per source:
  python3 runtime/intent_collect.py --youtube "missing calls landscaping" --comments --keywords "missed call,voicemail"
  python3 runtime/intent_collect.py --bluesky "landscaping missing calls" --keywords "missed,voicemail"
  python3 runtime/intent_collect.py --mastodon "smallbusiness,landscaping" --instance mastodon.social --keywords "missed call"
  python3 runtime/intent_collect.py --yelp "landscaping" --location "Yourtown"
  python3 runtime/intent_collect.py --rss "https://www.google.com/alerts/feeds/XXXX,https://forum.example/feed" --keywords "missed calls"
  # then: python3 runtime/sourcing.py --sadie-json intent-landscaping.json --campaign "Intent — Landscaping" [--commit]

Verticals live in runtime/intent_verticals.json (14 seeded; add freely). --comments pulls prospect-level
signal (people in the comments); without it you get video-level topic/market radar.
"""
import os, sys, json, re, html, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_env():
    for fn in (".youtube.env", ".yelp.env", ".bluesky.env"):
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
YT_KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
YELP_KEY = os.environ.get("YELP_API_KEY", "").strip()
BSKY_HANDLE = os.environ.get("BSKY_HANDLE", "").strip()
BSKY_APP_PW = os.environ.get("BSKY_APP_PASSWORD", "").strip()
# Browser UA — many public feeds (XenForo forums, etc.) sit behind Cloudflare and 403 a non-browser UA.
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=int(os.environ.get("INTENT_HTTP_TIMEOUT", "30"))) as r:
        return r.read()


# ---- YouTube Data API (official, free quota) ------------------------------
def _yt(path, params):
    params["key"] = YT_KEY
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
    return json.loads(_get(url).decode())


def youtube(query, limit=15, comments=False, keywords=None, vertical=""):
    """Search YouTube for intent phrases via the official Data API.
    Default: video-level signals (topic/market radar). With comments=True: pull the top comments on
    those videos and keep the ones matching the pain keywords — that's where the actual prospects are
    (real owners venting in their own words). Returns intent records (+ vertical tag)."""
    if not YT_KEY:
        print("  (YouTube skipped — set YOUTUBE_API_KEY in runtime/.youtube.env)")
        return []
    try:
        data = _yt("search", {"part": "snippet", "q": query, "type": "video",
                              "maxResults": min(int(limit), 50)})
    except urllib.error.HTTPError as e:
        print(f"  (YouTube API error {e.code}: {e.read().decode()[:160]})")
        return []
    out, vids = [], []
    for it in data.get("items", []):
        sn = it.get("snippet", {})
        vid = (it.get("id") or {}).get("videoId")
        if not vid:
            continue
        vids.append(vid)
        if not comments:
            signal = (sn.get("title", "") + " — " + sn.get("description", "")).strip(" —")
            out.append({"name": sn.get("channelTitle", ""), "domain": "", "email": "", "phone": "",
                        "intent": {"signal": signal[:300], "url": f"https://www.youtube.com/watch?v={vid}",
                                   "platform": "youtube"}, "source": ["sadie", "youtube"], "vertical": vertical})
    if comments and vids:
        out += youtube_comments(vids, keywords, vertical)
    return out


def youtube_comments(video_ids, keywords=None, vertical="", per_video=25):
    """Pull top comments on each video and keep the ones expressing the pain (keyword match). Each is a
    real person in their own words — the prospect-level signal. Comments disabled → that video skips."""
    kws = [k.strip().lower() for k in (keywords or []) if k.strip()]
    out = []
    for vid in video_ids:
        try:
            d = _yt("commentThreads", {"part": "snippet", "videoId": vid, "maxResults": per_video,
                                       "order": "relevance", "textFormat": "plainText"})
        except urllib.error.HTTPError:
            continue  # comments off / not found — skip this video
        for it in d.get("items", []):
            c = (((it.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {})
            txt = (c.get("textDisplay") or "").strip()
            if not txt or (kws and not any(k in txt.lower() for k in kws)):
                continue
            out.append({"name": c.get("authorDisplayName", ""), "domain": "", "email": "", "phone": "",
                        "intent": {"signal": txt[:300],
                                   "url": f"https://www.youtube.com/watch?v={vid}&lc={it.get('id', '')}",
                                   "platform": "youtube-comment"},
                        "source": ["sadie", "youtube"], "vertical": vertical})
    return out


# ---- RSS / Atom (public feeds — Google Alerts, forums, blogs) --------------
def _text(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def _strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def rss(feed_urls, keywords=None, vertical=""):
    """Read public RSS/Atom feeds, keep items matching any keyword (if given). Returns intent records."""
    kws = [k.strip().lower() for k in (keywords or []) if k.strip()]
    out = []
    for url in feed_urls:
        url = url.strip()
        if not url:
            continue
        try:
            root = ET.fromstring(_get(url))
        except Exception as e:
            print(f"  (RSS skip {url[:50]}…: {e})")
            continue
        # RSS <item> and Atom <entry>
        items = root.iter("{http://www.w3.org/2005/Atom}entry") if root.tag.endswith("feed") \
            else root.iter("item")
        host = urllib.parse.urlparse(url).netloc.replace("www.", "")
        plat = ("google-alerts" if "google.com/alerts" in url else
                "google-news" if "news.google.com" in url else (host or "rss"))
        for it in items:
            title = _text(it.find("title")) or _text(it.find("{http://www.w3.org/2005/Atom}title"))
            # RSS: <link>url</link> (text). Atom: <link href="url"/> (attribute). Handle both.
            link = ""
            for tag in ("link", "{http://www.w3.org/2005/Atom}link"):
                le = it.find(tag)
                if le is not None:
                    link = le.get("href") or _text(le)
                    if link:
                        break
            summ = (_text(it.find("description"))
                    or _text(it.find("{http://www.w3.org/2005/Atom}summary"))
                    or _text(it.find("{http://www.w3.org/2005/Atom}content")))
            signal = _strip_html((title + " — " + summ)).strip(" —")
            if kws and not any(k in signal.lower() for k in kws):
                continue
            out.append({"name": "", "domain": "", "email": "", "phone": "",
                        "intent": {"signal": signal[:300], "url": link, "platform": plat},
                        "source": ["sadie", "rss"], "vertical": vertical})
    return out


# ---- Google News RSS (public feed, free, no setup) ------------------------
def google_news(phrases, vertical=""):
    """Google's public News RSS search — build a feed per phrase, no key/setup. Surfaces company +
    event signals (a business in the news, hiring, a storm in a roofing market). The phrase IS the
    filter, so no extra keyword filtering. Compliant: it's a published feed, not scraping."""
    urls = [f"https://news.google.com/rss/search?q={urllib.parse.quote(p)}&hl=en-US&gl=US&ceid=US:en"
            for p in phrases if p.strip()]
    return rss(urls, keywords=None, vertical=vertical)


# ---- Bluesky (open AT-Protocol — free; searchPosts needs an app-password login) -
_BSKY_TOK = None


def _bsky_token():
    """Log in once with the yourco Bluesky handle + APP PASSWORD (revocable, not the main password) and
    cache the access token. Free + compliant (official auth on an open protocol — the legit alt to X)."""
    global _BSKY_TOK
    if _BSKY_TOK is not None:
        return _BSKY_TOK
    if not (BSKY_HANDLE and BSKY_APP_PW):
        _BSKY_TOK = ""
        return ""
    body = json.dumps({"identifier": BSKY_HANDLE, "password": BSKY_APP_PW}).encode()
    req = urllib.request.Request("https://bsky.social/xrpc/com.atproto.server.createSession",
                                 data=body, method="POST",
                                 headers={**UA, "Content-Type": "application/json"})
    try:
        _BSKY_TOK = json.loads(urllib.request.urlopen(req, timeout=20).read().decode()).get("accessJwt", "")
    except Exception as e:
        print(f"  (Bluesky login failed: {e})")
        _BSKY_TOK = ""
    return _BSKY_TOK


def bluesky(query, limit=25, keywords=None, vertical=""):
    """Search Bluesky (app.bsky.feed.searchPosts) — the open, compliant alternative to X. Returns real
    people posting the pain in their own words. Needs the app-password login (runtime/.bluesky.env)."""
    kws = [k.strip().lower() for k in (keywords or []) if k.strip()]
    tok = _bsky_token()
    if not tok:
        print("  (Bluesky skipped — set BSKY_HANDLE + BSKY_APP_PASSWORD in runtime/.bluesky.env)")
        return []
    # NOTE: with an auth token, searchPosts must hit the entryway/AppView (bsky.social), NOT
    # public.api.bsky.app (that host is unauthenticated-only and 403s a bearer token).
    url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts?" + urllib.parse.urlencode(
        {"q": query, "limit": min(int(limit), 100)})
    try:
        req = urllib.request.Request(url, headers={**UA, "Accept": "application/json",
                                                   "Authorization": "Bearer " + tok})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    except urllib.error.HTTPError as e:
        print(f"  (Bluesky error {e.code})")
        return []
    out = []
    for p in data.get("posts", []):
        text = ((p.get("record") or {}).get("text") or "").strip()
        if not text or (kws and not any(k in text.lower() for k in kws)):
            continue
        au = p.get("author") or {}
        handle = au.get("handle", "")
        rkey = (p.get("uri", "") or "").split("/")[-1]
        out.append({"name": au.get("displayName") or handle, "domain": "", "email": "", "phone": "",
                    "intent": {"signal": text[:300],
                               "url": f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "",
                               "platform": "bluesky"}, "source": ["sadie", "bluesky"], "vertical": vertical})
    return out


# ---- Mastodon (public hashtag RSS — free, no key) -------------------------
def mastodon(tags, instance="mastodon.social", keywords=None, vertical=""):
    """Public hashtag RSS on a Mastodon instance (no auth). tags = ['Landscaping','SmallBusiness']."""
    urls = [f"https://{instance}/tags/{urllib.parse.quote(t.strip().lstrip('#'))}.rss" for t in tags if t.strip()]
    recs = rss(urls, keywords, vertical)
    for r in recs:
        r["source"] = ["sadie", "mastodon"]
        r["intent"]["platform"] = "mastodon"
    return recs


# ---- Yelp Fusion (official API, free tier — business + complaint signal) --
def yelp(term, location="United States", limit=25, vertical=""):
    """Yelp Fusion business search (official, free tier; key in runtime/.yelp.env). More sourcing than
    intent: finds businesses in a vertical + a rating/review signal (low rating = a complaint to act on).
    Gives name + phone (no email — enrich later)."""
    if not YELP_KEY:
        print("  (Yelp skipped — set YELP_API_KEY in runtime/.yelp.env)")
        return []
    url = "https://api.yelp.com/v3/businesses/search?" + urllib.parse.urlencode(
        {"term": term, "location": location, "limit": min(int(limit), 50), "sort_by": "review_count"})
    req = urllib.request.Request(url, headers={**UA, "Authorization": "Bearer " + YELP_KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  (Yelp error {e.code}: {e.read().decode()[:120]})")
        return []
    out = []
    for b in data.get("businesses", []):
        cats = ", ".join(c.get("title", "") for c in b.get("categories", []))
        out.append({"name": b.get("name", ""), "domain": "", "email": "", "phone": b.get("phone", ""),
                    "intent": {"signal": f"{b.get('rating', '?')}★ / {b.get('review_count', 0)} reviews"
                                         f"{' — ' + cats if cats else ''}",
                               "url": b.get("url", ""), "platform": "yelp"},
                    "source": ["sadie", "yelp"], "vertical": vertical})
    return out


# ---- vertical config (drives many industries from one place) --------------
VERTICALS = os.path.join(HERE, "intent_verticals.json")


def load_verticals():
    try:
        return {v["vertical"]: v for v in json.load(open(VERTICALS)).get("verticals", [])}
    except Exception:
        return {}


def collect_vertical(name, comments=True):
    """Run every configured YouTube query for one vertical (with comment-level prospect signal) + any
    configured RSS feeds, all keyword-filtered to that vertical's pain phrases. Returns tagged records."""
    cfg = load_verticals().get(name)
    if not cfg:
        print(f"  (no config for vertical '{name}' — see runtime/intent_verticals.json)")
        return []
    kws = cfg.get("keywords", [])
    recs = []
    for q in cfg.get("youtube_queries", []):
        recs += youtube(q, cfg.get("limit", 8), comments=comments, keywords=kws, vertical=name)
    if cfg.get("alert_phrases"):                       # Google News RSS — auto, no setup needed
        recs += google_news(cfg["alert_phrases"], vertical=name)
    for q in cfg.get("bluesky_queries", cfg.get("youtube_queries", [])):  # Bluesky — free, no key
        recs += bluesky(q, keywords=kws, vertical=name)
    if cfg.get("mastodon_tags"):                       # Mastodon hashtag RSS — free, no key
        recs += mastodon(cfg["mastodon_tags"], cfg.get("mastodon_instance", "mastodon.social"),
                         keywords=kws, vertical=name)
    if cfg.get("yelp_term") and YELP_KEY:              # Yelp Fusion — needs key (business + rating signal)
        recs += yelp(cfg["yelp_term"], cfg.get("yelp_location", "United States"), vertical=name)
    if cfg.get("rss_feeds"):                           # feeds the Founder pasted (Google Alerts, forums)
        recs += rss(cfg["rss_feeds"], kws, vertical=name)
    return recs


def _dedupe(records):
    seen, out = set(), []
    for r in records:
        u = (r.get("intent") or {}).get("url", "")
        if u and u in seen:
            continue
        seen.add(u)
        out.append(r)
    return out


# ---- scoring / ranking (separate "owner venting" from vendor/news/marketer) -
# A signal is only valuable if it's a PROSPECT in pain, not a competitor selling the same fix or a news
# article about the topic. Heuristic v1 (free, fast); v2 could escalate ambiguous ones to Melanie/Claude.
SHARED_PAIN = ["missed call", "missed calls", "voicemail", "losing jobs", "lost a customer", "can't keep up",
               "cant keep up", "after hours", "too many leads", "booked solid", "no time to", "phone rings"]
VENDOR_MARKERS = ["we help", "we offer", "we provide", "our service", "our team", "our software", "our app",
                  "book a demo", "free trial", "dm me", "check out our", "sign up", "grow your", "get more leads",
                  "link in bio", "follow us", "subscribe", "% off", "limited time", "we specialize", "try our",
                  "schedule a call", "calendly.com", "let us help", "we build", "our platform"]
PROSPECT_MARKERS = ["i keep", "i can't", "i cant", "i'm losing", "im losing", "my voicemail", "my phone",
                    "we keep missing", "we lose", "we're losing", "were losing", "anyone else", "how do i",
                    "how do you", "struggling", "frustrated", "overwhelmed", "need help", "any advice",
                    "i lost", "drowning in", "tired of", "sick of", "help me", "what do you all do"]


def score_record(r):
    """Tag each record with klass (prospect / business-complaint / business / unknown / news / vendor),
    a heat score, and a numeric score. Mutates + returns r."""
    txt = ((r.get("intent") or {}).get("signal") or "").lower()
    plat = (r.get("intent") or {}).get("platform", "")
    vend = sum(1 for m in VENDOR_MARKERS if m in txt)
    pros = sum(1 for m in PROSPECT_MARKERS if m in txt)
    pain = sum(1 for k in SHARED_PAIN if k in txt)
    heat = pros * 2 + pain + (1 if "?" in txt else 0)
    if plat == "yelp":
        try:
            rating = float(txt.split("★")[0].strip().split()[-1])
        except Exception:
            rating = 5.0
        klass = "business-complaint" if rating < 3.7 else "business"
        if rating < 3.7:
            heat += 2
    elif plat in ("google-news", "google-alerts"):
        # published web content = market radar, NEVER a first-person prospect (a headline with
        # "overwhelmed"/"tired of" is an article, not an owner). A Google Alert occasionally catches
        # a real forum/Reddit post → only then (2+ first-person markers) treat it as a prospect.
        klass = "prospect" if (plat == "google-alerts" and pros >= 2) else "news"
    elif vend >= 1 and pros == 0:
        klass = "vendor"
    elif pros >= 1 or pain >= 1:
        klass = "prospect"
    else:
        klass = "unknown"
    r["klass"], r["heat"], r["score"] = klass, heat, pros * 2 + pain - vend * 3
    return r


_PRIO = {"prospect": 0, "business-complaint": 1, "business": 2, "unknown": 3, "news": 4, "vendor": 5}


# ---- cli ------------------------------------------------------------------
def _self_check():
    print("yourco intent collector — config check")
    print(f"  YouTube Data API key set: {bool(YT_KEY)}")
    print(f"  Yelp Fusion API key set:  {bool(YELP_KEY)}  (business + rating signal)")
    print(f"  Bluesky login set:        {bool(BSKY_HANDLE and BSKY_APP_PW)}  (handle + app password)")
    print("  No-key sources: Google News RSS · Mastodon (hashtag RSS) · Google Alerts/forum RSS")
    print("  scope: FREE + COMPLIANT sources only. No X/Meta/LinkedIn scraping (paid API / licensed data).")
    print("  out → Sadie schema → runtime/sourcing.py --sadie-json (cold pipeline, never sends).")
    return 0


def _slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _html_report(full, path, title, mix):
    """A scannable 'intent board' — full stack grouped by class, prospects first, clickable links."""
    CHIP = {"prospect": "#4F6B4A", "business-complaint": "#B8965A", "business": "#5b617a",
            "unknown": "#8a8fa3", "news": "#aab", "vendor": "#c98"}
    chips = " ".join(f'<span class=chip style="background:{CHIP.get(k,"#999")}">{k}: {v}</span>'
                     for k, v in sorted(mix.items(), key=lambda kv: _PRIO.get(kv[0], 9)))
    def rows(klass):
        out = []
        for r in [x for x in full if x.get("klass") == klass]:
            it = r.get("intent", {})
            nm = _esc(r.get("name") or "—")
            url = _esc(it.get("url", ""))
            link = f'<a href="{url}" target="_blank">view ↗</a>' if url else ""
            out.append(f'<tr><td class=heat>{r.get("heat",0)}</td><td class=plat>{_esc(it.get("platform",""))}</td>'
                       f'<td class=nm>{nm}</td><td class=sig>{_esc(it.get("signal",""))[:200]}</td><td>{link}</td></tr>')
        return "\n".join(out)
    def section(klass, label):
        body = rows(klass)
        if not body:
            return ""
        return f'<h2>{label} <span class=ct>{mix.get(klass,0)}</span></h2><table>{body}</table>'
    html = f"""<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Intent board — {_esc(title)}</title><style>
body{{margin:0;font:15px/1.5 -apple-system,Segoe UI,Inter,sans-serif;background:#12162b;color:#1a1a1a}}
.wrap{{max-width:1040px;margin:0 auto;padding:24px}}
header{{color:#F4EFE6;padding:8px 0 18px}} header h1{{margin:0;font-size:22px}} .sub{{color:#9aa;font-size:13px;margin-top:4px}}
.chips{{margin:12px 0}} .chip{{color:#fff;border-radius:999px;padding:3px 10px;font-size:12px;margin-right:6px;display:inline-block}}
.card{{background:#F4EFE6;border-radius:14px;padding:8px 20px 20px}}
h2{{font-size:16px;color:#161B33;margin:22px 0 8px;border-bottom:1px solid #ddd6c8;padding-bottom:6px}} .ct{{color:#B8965A;font-weight:700}}
table{{width:100%;border-collapse:collapse}} td{{padding:7px 8px;border-bottom:1px solid #eee4d4;vertical-align:top;font-size:13.5px}}
.heat{{font-weight:700;color:#4F6B4A;width:34px;text-align:center}} .plat{{color:#7a7f93;white-space:nowrap;font-size:12px;width:120px}}
.nm{{font-weight:600;width:150px}} .sig{{color:#333}} a{{color:#B8965A;white-space:nowrap}}
</style></head><body><div class=wrap>
<header><h1>🛰️ Intent board — {_esc(title)}</h1><div class=sub>Sadie · ranked prospects-first · click "view" to open the source · drafts/approval gated</div>
<div class=chips>{chips}</div></header>
<div class=card>
{section('prospect','🔥 Prospects (owners in pain)')}
{section('business-complaint','⭐ Sample Company 46 with complaints (low-rated)')}
{section('business','🏢 Sample Company 46 (to enrich)')}
{section('unknown','❓ Unclassified')}
<h2 style="color:#999">Filtered out</h2><p style="color:#888;font-size:13px">news: {mix.get('news',0)} · vendor: {mix.get('vendor',0)} — hidden as noise (competitors / articles).</p>
</div></div></body></html>"""
    open(path, "w").write(html)


def _emit(recs, out_path, campaign_hint="<vertical>", prospects_only=False, html_path=None):
    full = _dedupe(recs)
    for r in full:
        score_record(r)
    full.sort(key=lambda r: (_PRIO.get(r.get("klass"), 9), -r.get("heat", 0)))
    mix = {}
    for r in full:
        mix[r["klass"]] = mix.get(r["klass"], 0) + 1
    recs = [r for r in full if r.get("klass") in ("prospect", "business-complaint")] if prospects_only else full
    print(f"Collected {len(recs)} signal(s)" + (" — prospects only" if prospects_only else "")
          + f" · mix: {mix}")
    if html_path:
        _html_report(full, html_path, campaign_hint, mix)
        print(f"→ intent board: {html_path} (open in a browser to scan)")
    if out_path:
        json.dump(recs, open(out_path, "w"), indent=2, ensure_ascii=False)
        print(f"→ wrote {out_path} (ranked: prospects first). Next: python3 runtime/sourcing.py "
              f"--sadie-json {out_path} --campaign \"Intent — {campaign_hint}\"")
    elif not html_path:
        print(json.dumps(recs, indent=2, ensure_ascii=False))
    return recs


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-check" in a:
        sys.exit(_self_check())
    if "--list-verticals" in a:
        v = load_verticals()
        print(f"{len(v)} verticals configured (runtime/intent_verticals.json):")
        for name in v:
            print(f"  • {name}  ({len(v[name].get('youtube_queries', []))} YT queries, "
                  f"{len(v[name].get('keywords', []))} keywords)")
        sys.exit(0)
    comments = "--comments" in a
    ponly = "--prospects-only" in a
    want_html = "--html" in a

    if "--all-verticals" in a:
        verts = load_verticals()
        print(f"Sweeping {len(verts)} verticals (YouTube comments={comments}, prospects_only={ponly})…\n")
        total = 0
        for name in verts:
            print(f"— {name} —")
            recs = collect_vertical(name, comments=comments)
            recs = _emit(recs, f"intent-{_slug(name)}.json", campaign_hint=name, prospects_only=ponly,
                         html_path=f"intent-{_slug(name)}.html" if want_html else None)
            total += len(recs)
            print()
        print(f"Done. {total} kept across {len(verts)} verticals → one intent-<vertical>.json (+ .html) each.")
        sys.exit(0)

    if "--vertical" in a:
        name = a[a.index("--vertical") + 1]
        out = a[a.index("--out") + 1] if "--out" in a else f"intent-{_slug(name)}.json"
        _emit(collect_vertical(name, comments=comments), out, campaign_hint=name, prospects_only=ponly,
              html_path=(out.rsplit(".", 1)[0] + ".html") if want_html else None)
        sys.exit(0)

    recs = []
    kws = a[a.index("--keywords") + 1].split(",") if "--keywords" in a else None
    if "--youtube" in a:
        lim = int(a[a.index("--limit") + 1]) if "--limit" in a else 15
        recs += youtube(a[a.index("--youtube") + 1], lim, comments=comments, keywords=kws)
    if "--bluesky" in a:
        recs += bluesky(a[a.index("--bluesky") + 1], keywords=kws)
    if "--mastodon" in a:
        inst = a[a.index("--instance") + 1] if "--instance" in a else "mastodon.social"
        recs += mastodon(a[a.index("--mastodon") + 1].split(","), inst, keywords=kws)
    if "--yelp" in a:
        loc = a[a.index("--location") + 1] if "--location" in a else "United States"
        recs += yelp(a[a.index("--yelp") + 1], loc)
    if "--rss" in a:
        recs += rss(a[a.index("--rss") + 1].split(","), kws)
    if not any(f in a for f in ("--youtube", "--bluesky", "--mastodon", "--yelp", "--rss")):
        print(__doc__); sys.exit(0)
    _emit(recs, a[a.index("--out") + 1] if "--out" in a else None, prospects_only=ponly)
