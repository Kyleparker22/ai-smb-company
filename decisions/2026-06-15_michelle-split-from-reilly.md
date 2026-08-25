# 2026-06-15 — Split Reilly → spin up Michelle (outbound copy/messaging)

## Decision
Execute the Reilly split that the same-day scope review (`2026-06-15_agent-scope-review.md`) had documented as a *future* move. the Founder called it now. The outbound function divides into two agents along its two eval bars:

- **Reilly = the machine (Sales / Outbound Ops, SDR).** Sourcing (Outscraper/Vibe/SuperSearch → `runtime/sourcing.py`), enrichment, ICP/dedup/deliverability, campaign create + stage (`runtime/instantly.py`), reply/bounce feedback, CRM promotion (`runtime/promote.py`), the suppression list. Eval bar: list quality + deliverability.
- **Michelle = the message (Outbound Copy / Messaging).** The multi-touch sequence copy, subject + angle variants, the demo-led narrative, applying `brand/writing-rules.md`. Owns the copy methodology (`agents/reilly/copy-structure.md`), `processes/outbound/sequence-copy.md`, and the messaging in `industry-campaigns.md` / `proof-led-outbound-engine.md`. Eval bar: positive-reply rate + brand/claims.

**The seam:** Reilly hands Michelle the vertical + target research → **Michelle writes** → Reilly stages it **paused** in Instantly → the Founder approves → launch. Michelle never sends.

## Why now (vs. the documented "wait")
The scope review said split when *multiple verticals run concurrently and one eval bar strains the other*. the Founder chose to do it ahead of that trigger — defensible because the two crafts are genuinely distinct (a list-builder/deliverability engineer is not a cold-email copywriter), the artifacts to hand over already exist cleanly, and establishing the boundary *before* volume is cheaper than untangling it after. The risk the review flagged (splitting an unproven agent) is mitigated: nothing about Reilly's proof is undone — the machine is unchanged, only the copy responsibility moved to a named owner.

## Lineage
Reilly keeps **Aaron Ross (*Predictable Revenue*)** — the outbound machine + role specialization (which is itself the argument *for* this split). Michelle gets **Josh Braun** (anti-pitch outbound: lead with the prospect's world) + **Eddie Shleyner / *VeryGoodCopy*** (persuasive microcopy).

## Boundaries (added to the roster)
- **Reilly vs Michelle:** machine vs. message (above).
- **Michelle vs Katie:** both write, different surfaces/crafts — Michelle = cold outbound (1:1 copy that earns a reply); Katie = owned/social (authority that compounds). Distinct eval bars.

## What changed
- `04_agent_roster.md` — Reilly row narrowed; Michelle row added (Current/in-build); lineage + naming + boundaries + org chart updated.
- `agents/michelle/_README.md` — charter (scope, lineage, eval bar, gate, playbook pointers).
- Ownership moved to Michelle in: `processes/outbound/sequence-copy.md`, `industry-campaigns.md`, `proof-led-outbound-engine.md`, `agents/reilly/copy-structure.md` (header), `agents/reilly/02_build.md` (step 3), `agents/reilly/_README.md`.
- `runtime/slack-agent-listener.py` + `slack-channels.md` — `#yourco-michelle` mapped (role + identity).
- `CLAUDE.md` roster list — Michelle added.

## the Founder's to-dos (can't be done from here)
- Create **contact@yourco.example.com** (each agent gets a mailbox — executive-trust layer).
- Create the **#yourco-michelle** Slack channel + invite the control bot (the listener is already mapped; redeploy `yourco-slack-listener` on the VPS to pick up the new mapping).

## Hard gate (unchanged)
Drafts only. Luka (brand) + Polo (claims/pricing) + the Founder (approval) before staging; nothing sends until the launch gate (OtherVenture + Rafi + warmup + batch approval).
