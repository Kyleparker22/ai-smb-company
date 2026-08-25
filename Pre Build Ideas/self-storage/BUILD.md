# Gate OS — self-storage (build 23)

**Working name:** Gate OS · **Launch:** `prebuild-gate-os` · **Port:** 8843

## The idea

Self-storage is a delinquency-management business with a legal minefield at the end of it: the
lien-and-auction process is state-law-specific, unforgiving, and — the part operators learn in
court — **federally stopped for servicemembers (SCRA)**. Gate OS runs the ladder gently, computes
the lien calendar as date alerts under replaceable rules, and structurally refuses any lien step
against a tenant whose military status is flagged or unverified.

**Buyer:** the owner/operator. Thinks in occupancy, delinquency %, and auctions they never
wanted to run.

## The bleeding neck

- An auction run against a deployed servicemember is a federal violation with statutory damages —
  and the signal was usually sitting in a text: "I'm deployed until March."
- Lien timelines missed → restart the clock → months more non-payment.
- Threatening dunning texts → complaints, chargebacks, reviews.

## Modules

1. **Delinquency ladder** (Back Office) — bounded, never-threatening reminders; then the **lien
   calendar**: per-state steps (notice, advertise, earliest sale) computed from the delinquency
   date, every one a DATE ALERT under rules that name themselves a default.
2. **The SCRA stop** (Company Brain) — any lien step against a tenant flagged military, or whose
   status is **unverified**, is refused with the federal stake named. Military signals in messages
   ("deployed", "PCS orders", "active duty") are the eval's costly class.
3. **Message triage** (Intake) — military signals, payment promises, move-outs, gate problems.
4. **Occupancy board** (Operations) — counted per facility, refusing where unit counts are missing.

## Guardrails (load-bearing)

- `initiate_auction` / `cut_lock` / `sell_contents` — **R0.** A human runs a sale off a
  counsel-reviewed checklist; software alerts dates.
- Lien steps refuse on `military_flag` OR unverified SCRA status — verification is a human task.
- Dunning is bounded and structurally cannot threaten.

## ROI model

Delinquency days shortened → cash timing · auctions avoided via earlier contact → scenario ·
manual ladder hours → time saved · SCRA discipline → scenario (never a saving).

## Build prompt (§8)

Build `Pre Build Ideas/self-storage/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8843,
launch `prebuild-gate-os`. Seed "Summit Ridge Storage": 3 facilities, ~1,900 units, tenants at
every delinquency stage incl. military-flagged and unverified, messages incl. deployment signals.
Eval costly class = missed military signal. Tests pin the SCRA refusal (flagged AND unverified),
the R0s, the non-threatening ladder, the date-alert calendar, occupancy refusals, ROI blanks.
