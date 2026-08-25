# `loops/_health/` — the runtime's own pulse

**Written by `runtime/heartbeat.sh` (systemd `yourco-heartbeat.timer`, every 15 minutes).
Read by `dashboard/uptime.py`. Owner: Kemba.**

## `heartbeat.jsonl`

One line per beat. Nothing else lives here.

The point is not what the lines say — it is **which lines are missing**. A log can only record what
happened while the box was working, so no log can ever record an outage. Availability is therefore

```
uptime = beats received ÷ beats expected     (expected = window ÷ 15 minutes)
```

and a gap in the file **is** the outage rather than a hole in the evidence. Same lesson as
`learnings/ops/2026-08-07_absence-is-invisible-to-this-os`, which cost the runtime three dark days.

| Field | What it is |
|---|---|
| `ts` | UTC, and the only ordering key — a shell writer cannot allocate a monotonic `seq` safely, so this store deliberately has none (unlike the `runtime/ledger.py` stores) |
| `interval_min` | the beat interval **as the writer understood it**, so a changed cadence is visible in the data rather than only in the timer |
| `boot`, `up_s` | host boot time and uptime — a reboot is then a recorded fact, not something inferred from a gap |
| `paused` | `runtime/.paused` present. **Paused is not down**: available and idle. Reported separately as `serving` |
| `timers`, `failed_units` | active and failed `yourco-*` units — the difference between *the box is down*, *the timers are gone* and *the loops are failing*, which every past outage post-mortem had to guess at |
| `disk_pct`, `load1`, `head` | disk, load, and the commit the box was on |
| `last_loop_min` | minutes since any loop last wrote a status line. `loops/_runtime/` is **gitignored and host-local**, so this number is the only way that evidence ever reaches the repo |

## Three things that would each break it silently

- **`Persistent=false` on the timer.** A persistent timer fires catch-up runs after downtime and
  would back-fill the exact gap this exists to expose — the outage would erase its own evidence.
- **This folder is committed.** The obvious home was `loops/_runtime/`, and that folder is
  gitignored, which is precisely why runtime health was never visible from anywhere but the box.
- **The interval lives in three files** — `runtime/heartbeat.sh`, the timer, and
  `dashboard/uptime.py`. If they disagree the denominator is wrong in whichever direction the
  mismatch runs. `runtime/consistency-check.py` fails when they do.

## Empty until the Founder installs it

The beat is a **host** action and nobody in a Cowork session can take it:

```bash
sudo cp runtime/systemd/yourco-heartbeat.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now yourco-heartbeat.timer
```

Until then `dashboard/uptime.py` reads **unmeasured** — never 100%. A monitor's first reading is the
easiest number in the business to fake, and *"100%, all-time"* is always false: nothing was watching.
