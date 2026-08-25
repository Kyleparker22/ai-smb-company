# Rename this first

> **`YourCo` is not a real company — it is the blank where your name goes.** It appears in every
> casing (`YourCo`, `yourco`, `YOURCO`), in the domain (`yourco.example.com`), in the legal name
> (`YOURCO LLC`), in file paths, and in systemd unit names. That is deliberate: one word to replace,
> and the check below tells you when you have got all of it.

| Placeholder | Replace with |
|---|---|
| `YourCo LLC` / `YOURCO LLC` | your registered legal name |
| `YourCo` / `yourco` / `YOURCO` | your brand, same casing |
| `yourco.example.com` | your domain |
| `founder@yourco.example.com` | your work email |
| `the Founder` / `FOUNDER_` | your name / your identifier prefix |
| `Partner B` / `Partner C` | co-founders, if any |
| `123 Example St, Your City, ST 00000` | your business address |
| `10.0.0.1` / `user@your-vps` | your server and its user |
| `Sample Client` / `Sample Realty` / `Prospect A` | your own clients |
| `Yourtown` / `Your State` | your location |
| `Riverton` | your city (synthetic data) |
| `launch-gate` | your own name for "not public yet" |

```bash
grep -ril "yourco" . | xargs sed -i '' 's/YourCo/YourCo/g; s/yourco/yourco/g; s/YOURCO/YOURCO/g'
```

⚠️ **Check `.claude/launch.json` and `runtime/systemd/` afterwards** — they carry paths, and a
renamed path with a stale unit is the failure that looks like "the runtime just stopped working."

## Then

1. Read `SETUP/00_START-HERE.md`.
2. Set `git config user.email` **before your first commit**.
3. Credentials go in `runtime/.<service>.env` — **never** `runtime/.env.<service>` (`.gitignore`
   matches `*.env`; the reversed form commits your key). Verify: `git check-ignore -v <path>`.
4. Delete agents you will not use, per `runtime/agent-wiring-checklist.md`. A half-wired agent is
   invisible to the governance watchdog.
5. Replace the three worked client engagements in `clients/` with your own once you have them.

## Confirm the rename took

```bash
grep -ril "yourco" . --exclude-dir=.git | wc -l     # should print 0 when you are done
```

If that returns anything, the remaining files still carry the placeholder — most often
`.claude/launch.json`, `runtime/systemd/*`, or a path rather than file contents.
