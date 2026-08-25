# Prospect A / Sample Product — Stage 1: Discovery

> **Reconstructed 2026-08-23, not captured live.** This engagement was built product-first: the system
> exists and operates in preview, but no discovery doc was ever written. What follows is assembled from
> `_README.md`, `BUILD-JOURNAL.md` and `prototype/`, and **every field that was never captured says so
> rather than being filled in.** A reconstructed record with named gaps is a record; an invented one is
> worse than the blank it replaced.

## 1. The job
Aggregate free and paid storm-data sources (NOAA/NWS, Xweather, Visual Crossing) into one verified
alert feed for a Florida roofing / storm-restoration operator: cross-reference and average wind and
hail readings, grade severity, and turn "was this address actually hit" from a manual week of work
into a one-tap answer.

## 2. The trigger
A storm event in the covered geography. The engine runs on the VPS
(`yourco-storm-alerts` / `yourco-storm-publish` timers) and publishes to the hosted app.

## 3. Inputs and decision logic
- **Inputs:** NOAA/NWS (free, live), Xweather (Nick's key), Visual Crossing (wind gusts, no hail size).
- **Logic:** cross-reference sources, average the readings, grade severity A–F, verify per address.
- ⚠️ **Never captured:** the acceptance thresholds. The verdict self-scoring loop exists and Kolby
  evaluates accuracy, but the *number* that separates "alert" from "don't" was never written down here.

## 4. Output / action
A verified alert feed plus a per-address history report; SMS to roofers on Nick's approval.

## 5. Gated actions — the approval line
**No auto-send. Nick one-taps every SMS.** Rafi holds SMS compliance (A2P 10DLC).
⚠️ **Open bug since the 2026-07-05 audit: duplicate SMS.** Still unresolved.

## 6. Systems
Twilio (SMS) · the hosted Cloudflare Worker app · the VPS runtime (engine + auto-publisher).
Operating cost ~$15–40/mo — see `cost.md`; the value is the verification layer, not compute.

## 7. Success criteria
⚠️ **Never agreed.** Kolby evaluates alert precision/recall against Nick's manual weeks, which is the
closest thing to a measure — but no threshold was ever set with Nick, so there is nothing to pass or
fail against. **This is the most consequential gap on the page.**

## 8. The commercial shape
⚠️ **Unpapered.** The partnership has no agreement — Ray's gate, and the blocker for public launch.
Nothing has been signed and nothing has been invoiced. What Nick pays is undecided (Polo prices it);
`cost.md` models yourco's operating cost only.

## What this reconstruction means
The product works and is in preview. What is missing is not code — it is **the agreed definition of
done**: no success criteria, no thresholds, no paper. Those are discovery outputs, and skipping them is
why an engagement can be simultaneously "built and operating" and still at `discovery` in the CRM.
