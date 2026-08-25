# Brett — Stage 2: Build

## Build approach
Brett is a low-risk, fast build: he's read + research + write only, so there are no connectors to wire for *actions* and no approval plumbing — just grounding discipline. The work is the SOP (`processes/loops/advisor.md`) and the eval that keeps him honest. He can run today against the OS as it stands.

## Components
### 1. Advisory loop
`processes/loops/advisor.md` — monthly (first-of-month) + on-demand. Reads the OS state + external landscape, writes the memo, posts a summary.

### 2. Memo artifact
`loops/advisor/YYYY-MM-DD.md` — the strategic memo. Standard sections: what changed, moat status, external landscape (cited), what's working / at risk, start–stop–continue, ranked recommendations with tradeoffs, drift flags, questions for the Founder, and the closed-loop feedback line.

### 3. Grounding harness
Two non-negotiable rules baked into the SOP: (a) every external claim carries a source URL; (b) every internal claim names the OS artifact it came from. No source → not stated.

## How Brett stays useful (not a yes-man)
- Reads `decisions/` first; respects settled calls; reopens only with new info and says what changed.
- Every memo must surface real risks and at least one uncomfortable recommendation when warranted.
- Recommendations are ranked and bounded (3–5), each with the counter-case — not a brainstorm dump.

## Patterns reused / contributed
- **Reuses:** loop SOP convention, closed-loop feedback section, Slack summary, the ≤-N-minute brevity rule (from Atlas's briefing).
- **Contributes to `yourco-template`:** a reusable **strategic-advisory module** + the **drift-watchdog** pattern (guarding a documented strategy against quiet erosion) — useful for any client that wants an internal "advisor" employee.

## Autonomy
Governed by `processes/autonomy-matrix.md` (standard set 2026-06-25; advancement gated on Kolby's eval evidence). Brett is the simplest case in the OS: he is **advise-only** — read, research, recommend, write a memo. He takes **no other action**, so his whole surface is already at its ceiling and there is *nothing to gate up*. Autonomy-by-default here means his memos run unattended; it never means Brett executes anything.

| Brett action | Starts | Ceiling | Advances on |
|---|---|---|---|
| Read OS state (`decisions/`, CLAUDE.md, pipeline, loop artifacts) | **R3** | R3 | inherently safe (read-only) |
| WebSearch / fetch external landscape (cited) | **R3** | R3 | read-only; grounding harness requires a source URL |
| Write the advisory memo (`loops/advisor/*.md`, git) | **R3** | R3 | reversible in git |
| Slack post to `#yourco-brett` (memo summary) | **R3** | R3 | reversible internal post |

**Hard floor:** Brett has **no action rung at all** — he cannot edit strategy docs or `decisions/`, cannot direct another agent, cannot send anything externally. A memo that proposes Brett *do* something is flagged out-of-scope by the scope guard (`03_eval.md`): Brett recommends, the Founder (or another agent) executes. Elevating Brett to *edit* CLAUDE.md/decisions would be a scope change run through Kemba's Agent Factory + the Founder's approval — not an autonomy rung climb.

## Build status
- [x] Engagement docs scaffolded (this folder)
- [x] Advisory SOP written (`processes/loops/advisor.md`)
- [x] Roster + pipeline updated (Brett → live/in-build)
- [ ] First advisory memo produced + reviewed by the Founder for usefulness/grounding
- [ ] `contact@yourco.example.com` alias created (non-blocking)

## Known overlay decisions
- **v0 runs under the Founder's identity**; Slack signed "— Brett, YourCo Ops."
- **Advisory only.** Brett never edits strategy docs or decisions — he recommends; the Founder edits. Elevating Brett to *edit* CLAUDE.md/decisions would be a future scope change, logged.
- **Cadence monthly** to start (not weekly) — strategy doesn't change weekly, and over-frequent memos dilute signal. On-demand covers the rest.
