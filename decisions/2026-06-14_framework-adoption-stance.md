# Decision — framework / agent-runtime / library adoption stance ("borrow patterns, not dependencies")

**Date:** 2026-06-14 · **Owners:** the Founder + Kemba (platform) · **Status:** settled (standing default; revisit trigger below)

## Question
A steady stream of impressive open-source projects keeps surfacing — dev-orchestration setups (gstack), parallel-subagent frameworks (ruflo), scraping libraries (ScrapeGraph AI), full "AI agent operating systems" (AIOS / Cerebrum). Each looks adoptable. What's the default answer, and how do we decide fast instead of re-litigating every time?

## Decision
**Borrow the pattern, skip the dependency — by default.** Anything that adds a standing framework, an always-running agent runtime, a local model server, or a third-party automation/scraping substrate is **parked by default** because it cuts against the owned-and-auditable moat. We re-implement the *idea* natively (small, in-repo, on our own Claude key) only when it earns its place by the moat test below.

This is the sibling of the [no-code tooling stance](2026-06-11_no-code-tooling-stance.md) (Notion/n8n/Make). That one covers the no-code/automation layer; this one covers code frameworks, agent kernels, and libraries. Same north star: **the moat is reliability + eval + observability + approval + enterprise integration + executive trust — not tooling.**

## The moat test (apply to any "should we adopt X?")
1. **Does it add a runtime we don't already own?** (a framework process, a model server, redis, a marketplace, a kernel) → strong no. New surface area we must secure, observe, and keep alive is the opposite of what we sell.
2. **Does it duplicate something the OS already has?** Scheduler → systemd timers. Memory → `memory/` + `learnings/` + `CLAUDE.md`. Tool mgmt → MCP. LLM core → the Claude API. Orchestration → the Workflow tool + the loop fleet. If we already draw that box, adopting theirs subtracts clarity.
3. **Is it pre-1.0 / research code?** Our 48h go-lives and reliability promise can't ride a moving dependency.
4. **Supply-chain & autonomy risk?** Third-party agent runtimes that act on their own, or libraries that touch external sites/ToS (LinkedIn scraping, etc.), import risk that contradicts the compliance-led posture.
5. **What's the *idea* worth, stripped of the install?** Almost always the answer: re-implement it natively in a few hundred lines, on our key, under our eval/approval/observability umbrella.

If a tool adds a runtime (1), duplicates the OS (2), is pre-1.0 (3), or imports autonomy/ToS risk (4) — park it and borrow the pattern.

## The evaluated set (this is the precedent, not new policy)
- **gstack** (Garry Tan's Claude Code setup) → borrowed the *design-review pass* idea natively; skipped the install.
- **ruflo / parallel sub-agents** → borrowed the *fan-out review* pattern; ran it natively via the Workflow tool (and it found real production bugs). No framework.
- **ScrapeGraph AI** → borrowed *LLM-extraction-from-a-page*; built **native Enrich** instead (public pages only, own key, SSRF-guarded, no scraping framework / no LinkedIn-ToS exposure). See `crm/` Enrich + `dashboard/melanie.py`.
- **AIOS / Cerebrum** (the research "AI Agent OS") → declined. It's a multi-developer agent-marketplace kernel (scheduler, VM sandbox, agent hub, local model servers, redis) — solves scale we don't have, duplicates every box the OS already owns, is pre-1.0, and the name-collision ("AIOS") blurs the very distinction that makes ours defensible: ours is an *operating rhythm for a business*, not a *runtime kernel for arbitrary agents*. Borrow the kernel/scheduler/memory-manager **vocabulary** for explaining the OS to technical buyers; not the code.

## What we do instead
Keep the OS deliberately minimal and fully owned: git + markdown/JSON artifacts, systemd loop timers, the small Claude brain (`melanie.py`), the native CRM/dashboard, MCP for tools, and the Workflow tool for orchestration. Minimalism *is* the moat-supporting choice — a system small enough to understand completely is what lets us deliver eval, observability, and approval credibly. New capability gets added by writing it natively under that umbrella, not by importing a substrate.

## Revisit trigger
If a native re-implementation becomes a genuine bottleneck (e.g., hand-rolling a capability would threaten a 48h go-live), reach for the *narrowest, most ownable* option — self-hostable, git-versionable, code-extensible, sitting **under** YourCo's eval/approval/observability umbrella (the "a wrench, never the workshop" rule from the no-code stance) — never a framework that becomes the substrate the work lives in. The bar is "does it strengthen or dilute the moat?", not "is it useful?"
