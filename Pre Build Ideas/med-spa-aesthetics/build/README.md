# Consult OS — build 2 of 10

Pre-built vertical AI OS for med spas and aesthetic clinics.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # a two-location practice, 12 months
python3 test_consult_os.py           # 65 assertions, every one a refusal
```

Launch name **`prebuild-consult-os`** (port 8822, 127.0.0.1 only).

## What it is

"Verrine Aesthetics" — two locations, $2.1M, three injectors and a laser tech, ~2,100 inquiries
across Instagram DM, TikTok, web form, text and phone. All synthetic: invented names, 555 numbers,
no real patient records, no network calls.

Four modules covering the corridor from inquiry to repeat treatment: **instant concierge**,
**show-up ladder** (deposit → frame → confirm → morning-of, plus ranked cancellation refill),
**decision chaser** (bounded, driven by the injector's *captured objection*), **cadence engine**.

## The clinical stop is the product

`core.clinical_read()` is a rule, not a prompt string, and it has three tiers:

- **urgent_clinical** — vision change, blanching, drooping, spreading swelling, breathing. Pages an
  injector, tells the patient to call the clinic and to go to urgent care or 911 first, and
  **answers nothing**.
- **clinical** — units, dosing, candidacy, safety, medications, pregnancy, autoimmune, bruising,
  lumps. Routed unanswered.
- **commercial** — hours, parking, payment, the published consult fee, price *bands*. Answerable.

Hedged wording ("not sure if I can, I have a condition") routes. An empty or unreadable message
routes. On the eval set: 18 cases, clinical recall **1.0**, 0 missed, 0 false alarms — and urgent
complications are checked **again, separately**, because an average is not safety.

The refusal is visible in three places at once: the agent's own reply carries a `refused:` line, the
autonomy matrix declares `clinical_answer` at **R0 / never promotes** so a buyer can see the
prohibition rather than take it on faith, and a test asserts no streak on earth can promote it.

## Other places it refuses

- **Prices are bands.** A firm number is `quote_firm_price`, R1, never promotes. The agent may state
  the published consult fee and a band, nothing else.
- **Deposits.** Every ask is R1 and the agent never touches card data — it sends a link after a human
  approves.
- **The cadence engine never guesses at a clock that doesn't exist.** A patient with no treatment
  history is not flagged; a treatment with no reorder interval reports `no_clock`. Roughly a third of
  the seeded patients fall into this and stay out of the list on purpose.
- **Cost per booked consult is blank where ad spend isn't connected** — the funnel shows
  `unmeasured — ad spend not connected` per channel rather than modelling a number the owner would
  check against their own ad account in ten seconds.
- **Response time is a median, not a mean**, and says why on its face.

## 10-minute demo

1. **Today** — unanswered count, median response time, no-show rate, undecided plan value, and the
   drift list's annual value at stake.
2. **Inbox** — handle the 9:40pm "how much is lip filler" DM: band quoted, consult booked at R2,
   deposit held at R1.
3. Handle **"how many units would I need"** — routed unanswered, with the refusal shown.
4. Handle **"my lip is going white and it really hurts"** — injector paged, 911 language, no booking
   attempted. Then the **hedged** one, and the one that **names no treatment** (it asks).
5. **Consults** — simulate a cancellation and watch the ranked refill (undecided plan value first,
   then travel time), in waves rather than a blast.
6. **Undecided plans** — the $4,800 laser plan at day 11, its drafted-not-sent touches, and the copy
   that speaks to *this* patient's recorded objection.
7. **Cadence** — 79 drifting, ranked by their own annual value; then "Not flagged" and why.
8. **Funnel** — the blank cost-per-booked column.
9. **Trust & audit** — the queue, the eval, the urgent recall panel, the matrix with `clinical_answer`
   sitting at R0, the append-only log.

## What this does not do yet

- **No integrations.** Boulevard/Zenoti/Aesthetic Record, Meta/TikTok lead surfaces, SMS and
  payments are adapter seams. Nothing has spoken to an external service.
- **Classification is deterministic pattern-matching.** Correct for the clinical stop (auditable,
  testable, biased on purpose); a real deployment puts a model behind `qualify()` and leaves
  `clinical_read()` alone.
- **No HIPAA infrastructure.** Minimum-necessary shape only. Live deployment needs counsel review and
  a signed BAA — this prototype sidesteps it by using synthetic records.
- **The consult itself is out of scope.** The build handles the corridor around it, not the room.
- **Nothing is sent.** Every patient-facing message is a draft behind the gate.
