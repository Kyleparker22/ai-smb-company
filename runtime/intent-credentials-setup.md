# Intent sources — credentials, in one sitting

> **Status: PARTLY DONE — YouTube, Yelp and Bluesky are keyed; REDDIT IS NOT.** §3 is the outstanding one, and `runtime/consistency-check.py` flags `sadie-intent` until it is done. Only the Founder can complete it (it needs an account).

> Knock out every key/login for Sadie's intent collectors here. All go into **gitignored** `*.env` files in `runtime/` — paste the value after the `=`, save, done. The assistant never enters these; they stay on your machine. Verify any of them with `python3 runtime/intent_collect.py --self-check`.
>
> **Already free + working, no credential:** Google News RSS, Mastodon, forum RSS, WebSearch. **Done:** YouTube. **This doc:** Bluesky, Yelp, **Reddit**. **Separate doc:** Google Alerts (`runtime/intent-alerts-setup.md`).

## 1. Bluesky (handle + app password) → `runtime/.bluesky.env`
Bluesky's post-search now needs a login. Use an **app password** (a revocable, app-specific password — *not* your main one).
1. If you don't have a Bluesky account for yourco, create one at **bsky.app** (use `contact@yourco.example.com` once that mailbox exists — see §4 — or any email for now; you can rename later).
2. In the app: **Settings → Privacy and security → App passwords → Add App Password.** Name it "yourco-intent." Copy the generated password (looks like `xxxx-xxxx-xxxx-xxxx`).
3. Open the file and fill both lines:
   ```
   open -e "/Users/you/Documents/Claude/Projects/YourCo LLC - AI/runtime/.bluesky.env"
   ```
   ```
   BSKY_HANDLE=yourco.bsky.social        # your actual handle
   BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx # the APP password, not your login password
   ```
4. Verify: `python3 runtime/intent_collect.py --self-check` → **`Bluesky login set: True`**.

## 2. Yelp Fusion API key → `runtime/.yelp.env`
Official, free tier (~500 calls/day). Surfaces businesses in a vertical + their rating/review (a low rating = a complaint to act on).
1. Go to **yelp.com/developers** → **Create App** (sign in / create a Yelp account). Fill the short form (app name "yourco", industry, contact email).
2. On the app page, copy the **API Key** (the long key, not the Client ID).
3. Open the file and paste it:
   ```
   open -e "/Users/you/Documents/Claude/Projects/YourCo LLC - AI/runtime/.yelp.env"
   ```
   ```
   YELP_API_KEY=your-long-yelp-key
   ```
4. Verify: `python3 runtime/intent_collect.py --self-check` → **`Yelp Fusion API key set: True`**.

## 3. Reddit (client ID + secret) → `~/.yourco/reddit.env`
**This is the one the consistency checker is currently flagging.** Sadie's intent board reports
`Reddit ⛔ unkeyed`, and a zero from an unkeyed source is plumbing, not a market read — which is exactly
why it is flagged rather than quietly reported as "no signals." Reddit is where the intent conversations
actually are: `smallbusiness`, `Entrepreneur`, `sweatystartup`, `landscaping`, `lawncare`, `HVAC`,
`Plumbing`, `Contractor`, `HomeImprovement`, `msp`, `AskMarketing`.

Free, no paid tier needed — read-only API access via a **script app**.

1. Sign in to Reddit with the account you want to own this (a plain personal account is fine; it is only
   used to authenticate reads, and nothing is ever posted).
2. Go to **reddit.com/prefs/apps** → scroll to the bottom → **create another app...**
3. Fill the form:
   - **name:** `yourco-sadie`
   - **type:** select **script** ← must be `script`; the other types use a different OAuth flow that
     `agents/sadie/listen.py` does not implement
   - **description:** `intent listening, read-only`
   - **about url:** leave blank
   - **redirect uri:** `http://localhost:8080` (required by the form, never used by a script app)
4. Press **create app**. On the resulting card:
   - the **client ID** is the short string directly *under* the app name, top-left (~14 chars) — it is not labelled
   - the **secret** is the value on the line labelled `secret`
5. The file lives outside the repo, in your home directory. Create it and paste both values:
   ```
   mkdir -p ~/.yourco && open -e ~/.yourco/reddit.env
   ```
   ```
   REDDIT_CLIENT_ID=your-14-char-id
   REDDIT_CLIENT_SECRET=your-secret
   ```
6. Lock it down: `chmod 600 ~/.yourco/reddit.env`
7. Verify: `python3 agents/sadie/listen.py` → it should return posts instead of the
   "set REDDIT_CLIENT_ID/SECRET" message. The next intent sweep will then read `Reddit ✅` and the
   consistency checker's `sadie-intent` item will clear.

> **Why this file is not in `runtime/` like the others:** `~/.yourco/` is outside the repo entirely, so it
> cannot be committed even by accident. `agents/sadie/listen.py` reads `~/.yourco/reddit.env` (or the
> `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` environment variables) and nothing else.
>
> **The VPS needs its own copy.** Credentials do not sync — the runtime box is a separate clone with a
> separate home directory. If the intent loop is meant to run headless, repeat step 5 there over SSH.

## 4. Do you need a contact@yourco.example.com email?
**For Google Alerts and Yelp: no** — your `founder@yourco.example.com` account is fine. Don't block on this.

**For Bluesky and the agent-identity model: recommended, eventually.** YourCo's convention is that each agent gets its own `@yourco.com` mailbox (it's part of the executive-trust layer), and Sadie will want her *own* identity for any social account she posts from — not yours. So set up `sadie@` when you're ready for Sadie to have her own social presence.

**How to set it up (you do this — I can't create accounts):**
- **Real mailbox (recommended, ~$6/mo):** Google Workspace **admin.google.com → Directory → Users → Add new user** → first name "Sadie", email `contact@yourco.example.com`. That's a paid seat (Business Starter) but gives Sadie a real, independent login for Bluesky/social + a mailbox.
- **Free interim:** create an **alias** (`admin.google.com → the the Founder@ user → Add alternate email → contact@yourco.example.com`) that just forwards to your inbox. Good enough for receiving, but it can't independently log into Bluesky/Google as "Sadie" — so for social accounts you'd still want the real seat.

**Recommendation:** use `the Founder@` for Alerts/Yelp now (don't wait); spin up the real `sadie@` Workspace user before you create Sadie's Bluesky/social accounts so they belong to her identity, not yours.

## Reminder
- Never paste a key into chat — only into these files. They're gitignored (`*.env`), so they never get committed.
- After any change, `--self-check` confirms what's set. Nothing sends or posts regardless of keys — collection is read-only and the send/post gate stays in place.
