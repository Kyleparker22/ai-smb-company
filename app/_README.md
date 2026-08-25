# /app/ — the yourco app: one login, one address, three surfaces

**Reality level: 🟢 REAL, but 🔒 private.** Built 2026-08-23. Runs on loopback/Tailscale only —
public exposure is an launch-gate decision (`processes/launch-gate.md`), not a flag.

Start it: `python3 app/server.py` (or the `yourco-app` entry in `.claude/launch.json`, port **8820**).
It needs HQ, the CRM and the console already running — `./show.sh` plus the console on 8807.

## Why it exists

HQ and the CRM have **no authentication of their own.** Verified 2026-08-23: an unauthenticated
`GET :8790/api/data` returns the whole CRM — every prospect's name, email and phone. They are safe
today only because they bind to `127.0.0.1` and are reached over Tailscale. **Network position is
the entire security model**, and "the team can log in" is incompatible with that.

So one gateway owns identity and the three apps stay exactly as they are.

## Roles

`auth.ROLE_AREAS` is the authority; the gateway only enforces it. Matches yourco's own people
taxonomy (`decisions/2026-07-06_advisors-connectors-taxonomy.md`).

| Role | HQ | CRM | Console | Who |
|---|:--:|:--:|:--:|---|
| **partner** | ✅ | ✅ | ✅ | The 50/35/15 members — the Founder, Partner B, Mike |
| **advisor** | — | ✅ | ✅ | yourco salespeople |
| **connector** | — | — | ✅ | External referral partners |

Advisors are kept out of HQ deliberately: it carries runway, the OA, partner splits and the
finance model. `operator` is the pre-2026-08-23 name for `partner`, still honoured because the Founder's
live account carries it — an auth change must never lock out the only person who can grant access.

Verified over HTTP, not by reading the code:

```
ROLE         /hq/   /crm/  /connector/
partner      200    200    200
advisor      403    200    200
connector    403    403    200
```

## How it works, and what it deliberately does not do

**It does not rewrite the apps.** HQ and the CRM are ~7,500 lines of working UI; adding auth to
both would be the riskiest change in this repo. The gateway reverse-proxies them instead.

That is only possible because a measurement said so: both UIs reach their APIs **only** through
`fetch()` with absolute paths — no XMLHttpRequest, no EventSource, no absolute `href`/`src`. So a
three-line `fetch` shim injected before `</head>` makes an app mounted at `/crm` behave as if it
were at the root. The console additionally emits ~10 absolute `href`/`action` attributes, rewritten
on the way out.

**Single sign-on is free.** The gateway and the console share `auth.py` *and its session store*, so
the gateway sets the same `yourco_console` cookie the console already understands. No token
passing, no second identity system.

## Security posture — read before exposing this

- **Cross-origin POSTs are refused at the gateway** before auth and before any proxying. This matters
  more than it looks: the proxy *rewrites* `Origin` to match the backend (without it every HQ write
  403'd), which means HQ's own CSRF check can no longer fail. The first version shipped without a
  gateway-side check and its commit called that "correct, not a bypass" — it was a bypass. What had
  actually been preventing exploitation was `SameSite=Strict` on the session cookie, a control in
  another module that was not verified at the time. One unverified control is not a posture.
- The three backends **must stay bound to `127.0.0.1`**. The gateway is the only process that may
  ever listen on a public interface.
- That makes the gateway a **single point of failure**: a routing bug here is full exposure. It is
  an accepted trade against bolting auth onto three codebases, and it is why the role check happens
  *before* the proxy call, not inside it.
- Binding to anything other than loopback prints a loud warning naming the launch-gate.
- The service worker caches **only** the static shell. Pages and every `/api/` call are
  network-only — a cached pipeline number, or one person's view surviving a sign-out, would be
  worse than no offline support.

## Adding a person

```bash
python3 processes/partnerships/connector-console/server.py --issue-setup-token "Partner B" --role partner
```

Send them the one-time link; they set their own passphrase. Roles: `partner`, `advisor`, `connector`.

## Tests

`python3 app/test_gateway.py` — **78 assertions**, all guarding an ACCESS rule rather than a feature.

Written 2026-08-23, and honestly: they should have come first. The repo had 207 assertions on HQ's
honesty rules and 75 on agentops, and **zero** on the 559-line auth module or the 403-line gateway —
the only components deciding who can read the CRM and HQ. The role matrix had been verified once, by
hand, with curl, and the test accounts deleted afterwards.

They cover: the full role matrix (both as a predicate and over real HTTP), deny-by-default for unknown
roles, the auth lifecycle (single-use setup tokens, replay refusal, passphrase policy, session
teardown), unauthenticated access to every path, cross-origin POST refusal, and that the shell omits
doors a role cannot reach from the DOM entirely.

**Everything runs against a throwaway store in a temp dir**, and the first three assertions verify that
— the tests fail loudly if the environment override protecting the real `_auth.json` is missing.

**They were proven by sabotage, not by passing.** A suite that goes green on its first run has not
demonstrated anything. Three deliberate breakages were introduced and each was caught: granting
advisors HQ access (3 failures), disabling the gateway's CSRF check (1), and moving the role check
below the proxy call (3).

## Known-unverified

**PWA install is untested on a real device.** The manifest, icon and service worker are served
correctly (200, right MIME, secure context), but registration fails inside the embedded preview
browser, which commonly blocks service workers. Confirm on an actual phone before believing the
home-screen install works.
