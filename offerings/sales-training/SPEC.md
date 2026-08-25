# Sales-Training / Enablement OS — build + validation spec (v0, internal)

> **Status: pre-build, pre-pilot.** Catalog entry: `processes/new-offering-lines.md` B6. Internal only — not on the public site. Owners: Brett (strategy) · Reilly/Michelle (methodology + content) · Kimi (build) · Polo (price) · Kolby (eval). Operated by YourCo (we own the eval/reliability; the client gets faster-ramping reps).

## The one-line
Companies can't ramp reps fast or coach consistently — managers don't have time to role-play with every rep or review every call. An **operated AI sales coach** lets every rep practice against a realistic AI buyer on demand and get scored, methodology-specific feedback — then expands into a full enablement OS.

## Wedge first: the AI Sales Coach (a single employee)
Build and validate **only this** before the OS:
1. **Role-play sparring partner.** The rep starts a practice rep — cold open, discovery, objection-handling, or a full mock call — against an AI buyer tuned to *their* ICP, product, and common objections. Text first; **spoken (phone) role-play via Vapi** as the fast-follow (phone-pitch practice is the highest-value mode for most SMB sales teams).
2. **Scored feedback against a rubric.** Every rep is graded on a fixed methodology rubric (talk-ratio, discovery quality, objection handling, next-step secured, etc.) with specific, quotable feedback — not vibes.
3. **Reinforcement.** Weak spots become the next drill; the rep sees their own ramp curve over time.

That loop alone is a sellable employee ($1–5k setup + $1,500–2,500/mo). Land it, then expand.

## Expand → the enablement OS
- **Onboarding/ramp** to a named methodology (new-hire path: content → drills → certification gate).
- **Real-call scoring** (not just role-play) once call recordings are wired in.
- **Manager dashboard** — per-rep ramp curve, team-wide weak spots, where deals leak.
- **Scenario library fed by A3 (win/loss intelligence):** real lost-deal objections + reference-call language become the role-play scenarios and the rubric. *This is the moat join — the coach trains on the company's actual deals, not generic scripts.*

## Stack
Anthropic API (the buyer-persona + scoring brain) · Vapi + ElevenLabs (spoken role-play, the voice use case) · a scoring rubric (codified per methodology) · a simple rep/manager dashboard · CRM/recording connectors for real-call scoring (phase 2). No new platform pieces beyond what YourCo runs.

## Why YourCo wins (the moat, not the feature)
- **Methodology-specific + operated.** We encode *the client's* playbook into the rubric and own its reliability/eval — generic "AI sales coach" tools ship a one-size rubric you self-configure.
- **Real credibility.** YourCo runs on a real sales discipline (Reilly = *Predictable Revenue* + Josh Braun; David = *Winning by Design*) — the rubric isn't invented.
- **Eval is the product, not a footnote.** A coach that scores reps must itself be scored against human-grader agreement — exactly Kolby's muscle. That defensibility is what no-code can't match.

## Eval gates (Kolby) — higher bar than a Tier-1 employee
- Scoring agreement with a human grader on a held-out set (the coach's grades must track a real sales manager's).
- No fabricated feedback — every score cites the moment in the transcript.
- Persona realism check — the AI buyer behaves like the ICP, doesn't fold instantly or stonewall unfairly.
- Tone/safety — coaching is candid but never demeaning.

## Validation plan (pre-sell before heavy build — Kagan-style)
1. **Dogfood the methodology** internally: Reilly/Michelle codify the rubric + 5 starter scenarios from YourCo's own outbound playbook.
2. **One design-partner sales team** via warm network (an SMB with 3–10 reps and a real ramp problem). Free/cheap pilot in exchange for shaping it.
3. **MVP = the wedge only** (text role-play + scored feedback on 3 scenarios). Prove a rep improves measurably over ~2 weeks.
4. Then add voice, then the manager dashboard, then real-call scoring.

## Pricing (Polo, v0)
- **Wedge (AI Sales Coach):** $1–5k setup + $1,500–2,500/mo.
- **Full enablement OS:** $2–5k implementation + $3–10k/mo, **+ per-seat option** (value scales with rep count — the Tier-2 per-unit pattern).
- Audit credit applies (a sales org can enter via the Audit like any client).

## Risks / open decisions
- **Competitive:** Gong, Second Nature, Hyperbound-style tools exist. Win on operated + methodology-specific + AI-native role-play, not on being first. *(Brett: competitive-watch entry.)*
- **Voice complexity:** spoken role-play (Vapi) is the high-value mode but adds latency/cost — validate text first.
- **Design partner:** who? (No obvious one in the current CRM — the friend-leads are owner-operators, not sales orgs. Sourcing a pilot is the first real task.)
- **Real-call scoring = recording consent + data handling** (Rafi gate when we get to phase 2).
