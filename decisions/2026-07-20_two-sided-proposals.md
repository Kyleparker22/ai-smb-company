# 2026-07-20 — Two-sided proposals standard

**Decision** — Every outgoing proposal is two-sided: the return side (the audit's quantified bottleneck, in the client's own numbers, math shown, plus projected payback) appears alongside the investment. The cost number never travels alone. Baked into the canonical template `processes/contracts/proposal-sow.md` ("What this is worth vs. what it costs" section, immediately before Investment).

**Context** — the Founder asked whether to build a two-sided proposal dashboard for prospects/clients. Review of the first real proposal (Sample Client, `clients/sample-client/02_proposal.md`) showed it leads with scope and goes straight to the pricing table — no quantified return anywhere, and the deal has stalled at Proposal (top commercial gap in the 2026-07-04 full OS audit). Meanwhile the Audit SOP (Step 3, `processes/audit-sop.md`) already produces exactly the needed number — "quantify the dollar cost in their numbers … that number is the whole pitch" — it just never landed on the proposal surface.

**Options considered**
- **New agent/tool that generates a proposal dashboard** — rejected for now: the pieces exist (audit quantification upstream, demo kit + client console downstream); a new agent adds roster surface without new capability.
- **Interactive HTML proposal page in the demo kit** (`proposal.html`, config-driven) — deferred, not rejected: build it after the two-sided format proves itself on a real deal; template what worked, don't generalize pre-signal.
- **Retrofit Sample Client first** — explicitly declined by the Founder 2026-07-20; the standard applies to outgoing proposals going forward.
- **Template rule (chosen)** — add the two-sided section + fill-source + gate ("a one-sided proposal doesn't go out") to the one canonical template every proposal is filled from.

**Why** — Audit-first is the motion: Bella's quantified bottleneck is the whole pitch, so the proposal is where that number must land — outcome framing is the house rule and the return side is the outcome in dollars. One canonical template means zero drift surface (all other docs reference `proposal-sow.md`, they don't duplicate it). Credibility gate holds: return figures are projections from the client's own audit inputs with assumptions stated — never guarantees, never third-party benchmarks dressed as theirs (honesty footer updated to say so).

**Reversibility** — Cheap to reverse (delete the template section). Revisit if (a) the return side measurably spooks rather than converts — e.g. prospects dispute the math instead of signing — or (b) an engagement class emerges where the bottleneck genuinely can't be quantified pre-signing; the escape hatch today is "go get the numbers," not "send one-sided." The deferred demo-kit `proposal.html` becomes worth building once ≥1 deal closes on the two-sided format.

**Owners** — Pickle (packaging) + Polo (price side) + Bella (return side feeds from the Audit) · the Founder locks per existing gate.
