# Client trip-wires — the client's own decisions, watched for expiry

> Engine: `runtime/client_tripwires.py`. Facts: this folder's `facts.json`, written by the
> client's own OS. Every CRM reports what happened; this reports **which of the client's own past
> decisions reality has just contradicted.** Added 2026-08-13.

## How this works

During discovery the client states operating decisions in **their own words**, and each one gets
the condition that would make it wrong. Their OS already measures the numbers, so it can tell them
the month a decision expires — with their own sentence quoted back.

```markdown
## <short name for the decision>
- **They decided:** <the client's own words, quoted — never our paraphrase>
- **Decided on:** YYYY-MM-DD
- **Overturn if:** <the plain-language condition that makes it wrong>
- **Check:** `quotesPerWeek > 20`      ← a fact from facts.json, or `_none — <why>_`
- **Say:** <the exact sentence to show them when it fires>
```

**The rules that keep this from embarrassing us at a client:**

- **Their words, not ours.** yourco never invents a client's reasoning. If they didn't say it,
  it doesn't go in — the same rule that stops agents writing yourco's own trip-wires.
- **A check naming a fact nobody measures reads `unmeasured` and never fires.** Telling a client
  their decision expired on the strength of a number that isn't being measured is the worst
  failure this feature has.
- **One grammar.** Checks are evaluated by `dashboard/tripwires.py` — the same tiny language, the
  same refusals. Mixing `and` with `or` is refused rather than guessed.
- **`Say:` is written in advance, calmly, while nobody is under pressure.** A trip-wire firing is
  a good moment for the client and a bad moment to be drafting a sentence.
- **Expiry is an invitation, not an upsell trigger.** The output is "your model of your business
  changed", not "buy the next module". If every trip-wire conveniently expires into a purchase,
  the client will notice, and the feature dies with the trust.

---

## Example — manual quoting

*(EXAMPLE. Illustrates the format. Replace at discovery with decisions the client actually stated;
the engine flags a client whose file is examples-only so this can never be mistaken for live.)*

- **They decided:** "We write every quote by hand. It's twenty minutes and I'd rather be sure."
- **Decided on:** 2026-03-01
- **Overturn if:** quote volume passes what one person can hand-write in a working day without the
  backlog growing.
- **Check:** `quotesPerWeek > 20`
- **Say:** In March you decided hand-writing every quote was worth the twenty minutes. You were at
  12 a week then. You're at {quotesPerWeek} now — that's over {quoteHoursPerWeek} hours a week on
  quoting alone. Worth a look, not a decision you have to make today.

## Example — no Saturday crew

*(EXAMPLE — replace at discovery.)*

- **They decided:** "Saturdays aren't worth staffing. The calls don't come in."
- **Decided on:** 2026-03-01
- **Overturn if:** weekend inbound is no longer negligible.
- **Check:** `saturdayLeadsPerMonth >= 8`
- **Say:** You decided Saturdays weren't worth staffing when weekend enquiries were rare. Last
  month there were {saturdayLeadsPerMonth}. Not a recommendation — just the number that changed.

## Example — one crew is enough

*(EXAMPLE — replace at discovery. Deliberately shows a check whose fact is NOT in facts.json, so
the engine renders `unmeasured` instead of firing. That state is the feature working, not a gap.)*

- **They decided:** "One crew. A second one is more management than it's worth."
- **Decided on:** 2026-03-01
- **Overturn if:** jobs are being turned away or scheduled out past the point customers accept.
- **Check:** `jobsDeclinedPerMonth >= 4`
- **Say:** You decided a second crew was more management than it was worth. Last month
  {jobsDeclinedPerMonth} jobs were turned down for capacity.
