# Learning — interface-first + seed→live: the build standard that makes engagement #2 cheap

**Date:** 2026-06-18 · **Type:** pattern / standard · **Surfaced by:** the Founder reviewing a Verdent build writeup (niche-radar one-shot)

## The observation
A competitor's writeup nailed why their v1→v2 upgrade (local demo → live data + phone delivery) was a one-line prompt instead of a rewrite: **v1 was built behind two seams** — every data source behind a shared `Connector` interface, every output behind a `deliver()` interface. The seed-file reader and file-writer were just the *first implementations* of those seams. Swapping in live fetch + a messaging channel was a drop-in, not a refactor.

That's not their insight to own — it's craft we already do in pieces and should make a **standard** the scaffolder/Kimi apply by default on every engagement:
- `recraft.py` — dry-run default, gated behind `--commit`
- runtime Gmail — **draft-only** behind the approval gate
- `snapshot_intake.py` — staged handler, swap-ready for live send
- the Slack listener — `--self-check` offline mode before going live

## The standard (apply to every client OS build)
1. **Contract first.** Define the shared types and interfaces *before* any implementation. One file (`types.ts`/`schema`) the parallel workstreams agree on. This is what lets independent pieces — connectors, scorer, renderer, delivery — be built concurrently without colliding (and what makes a Workflow fan-out actually parallelizable).
2. **Every external touch behind an interface.** Each data source implements one `Connector`-shaped contract; each output (file, Slack, email, SMS, client console) implements one `deliver()`-shaped contract. The pipeline in the middle never knows which implementation it's talking to.
3. **Seed → live ladder.** Ship v1 as deterministic + local: seed/fixture data in, file out, no keys, no network. It *works the first time* and demos with zero setup. Live fetch and real delivery are later implementations of the same seams, gated behind a flag (`LIVE=1`) — never a rewrite.
4. **Fail-soft, always ships.** A live source that errors or rate-limits falls back to its seed/last-good; a delivery channel that's down falls back to file. The run never hard-crashes — it degrades. (Mirrors the connectors' "missing seed → log + return [], don't crash the run.")
5. **Offline self-check before live.** Every connector/delivery gets a `--self-check` that validates config + contract with no network, the way the VPS daemons do. Catches the dumb stuff before burning a connect cycle.

## Why it matters for yourco specifically
This *is* the moat in code form. The reason a client OS can go live in 48h and then iterate weekly without breaking is that account expansion = adding another implementation behind an existing seam (a new source, a new approval-gated action, a new channel), not re-opening the build. Interface-first is what turns "custom per client" from a cost into a compounding asset.

## Read this at Step 0
The scaffolder, Kimi, and Janice on any **build** turn; Webb on any connector/output work. Fold the seam + seed→live + self-check checklist into `clients/_yourco-template/02_build.md` as the default build shape. Related: `learnings/ops/2026-06-14_vps-daemon-deploy-pattern.md` (the self-check / fail-soft discipline), `decisions/2026-06-15_no-n8n-stance.md` (why we own the code, not a no-code graph).

Triggers: agent:kimi, agent:kemba, client build, scaffolder, build standard, skill:scaffold-engagement, loop:demo-prep
