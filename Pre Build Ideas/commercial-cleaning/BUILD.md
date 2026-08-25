# Crew OS — commercial cleaning & janitorial (build 21)

**Working name:** Crew OS · **Launch:** `prebuild-crew-os` · **Port:** 8841

## The idea

A janitorial company is the trade that holds keys, codes and alarm credentials to every client's
building — at 2am, unsupervised. Its risks are a security incident handled casually, an access
credential leaked in a text thread, and a quality dispute with no evidence behind either side.
Crew OS triages the night reports with a security bias, makes access information unspeakable by
software, and turns "we cleaned it" into a claim with an inspection record behind it.

**Buyer:** the owner / ops manager. Thinks in contracts, complaints, and night-crew coverage.

## The bleeding neck

- The 2am "back door was unlocked when we got here" report buried in a group chat until Monday.
- Alarm codes and lockbox combos living in text threads — one compromised phone from a breach.
- "The restrooms weren't done" vs "yes they were": nobody has evidence, the client wins, the
  contract shrinks.
- Night no-shows discovered when the client calls in the morning.

## Modules

1. **Night-report triage** (Intake) — security incidents (unlocked doors, alarms, propped doors,
   strangers, damage) route to a human **immediately** and can never be closed by software.
   Complaints draft responses citing the last inspection — or admitting there is none. Supply
   requests draft. **Any request for access information is refused** — codes and keys move through
   humans and the client's own channel, never through this system.
2. **Coverage board** (Operations) — tonight's contracts vs assigned crew; a crew member without
   recorded access to a building is never proposed for it (the blocker named).
3. **Inspection evidence** (Customer) — "cleaned per spec" is assertable only with an inspection
   record inside the window; otherwise **"cannot assert — no inspection on file."**

## Guardrails (load-bearing)

- `share_access_info` — **R0.** Codes, keys, lockbox combos: never in a message from this system.
- `close_security_incident` — **R0** for software; a human closes after follow-up.
- `assert_cleaned_without_inspection` — **R0**, structural.
- The eval's costly class is a missed security incident.

## ROI model

Complaint-driven contract shrinkage avoided → scenario · inspection-backed disputes won → their
number · dispatch/relay hours → time saved · coverage misses caught → revenue (their contract value).

## Build prompt (§8)

Build `Pre Build Ideas/commercial-cleaning/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8841,
launch `prebuild-crew-os`. Seed "Northstar Building Services": ~85 contracts, night crews with
per-building access flags, reports incl. every security type, inspections on some contracts only.
Eval costly class = missed security incident. Tests pin the access refusal, the software-close
refusal, the no-inspection refusal, the access-blocked coverage, ROI blanks, counted automation.
