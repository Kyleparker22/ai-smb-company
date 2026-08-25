# Context audit — the CLAUDE.md + skills diet

> **One time-boxed working session (2h), the Founder at the keyboard.** Applies Anthropic's Claude-5-generation context-engineering rules (they cut **80%+ of Claude Code's own system prompt with no eval loss**) to yourco's OS. Triage + verdict: `decisions/2026-07-05_tool-triage.md` §Addendum 2026-07-29 (Anthropic). Source: [claude.com/blog — The New Rules of Context Engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models).
>
> **Why this is not prompt-gardening:** every Cowork session and every headless loop run re-reads this context. Trimming it cuts weekly token cost, cuts the contradiction surface the model burns attention on, and — via `yourco-template` — cuts run cost on every future client OS. That last one is COGS (`CLAUDE.md` §Token economics).

## Prerequisites (HARD GATE — do not run the session until both are green)
1. **The runtime is actually executing.** Discovered 2026-07-29: Claude-powered loops went dark between **07-12 and 07-15** (staggered last artifacts), deterministic python timers ran until ~07-22, and the VPS itself was offline until 07-29. **The watchdog is itself a Claude loop, so it died with them and reported nothing** — ~2 weeks of silent darkness. Optimizing context for loops that aren't running is meaningless, so: confirm fresh artifacts are landing (source-watch Fri 07:30, the Mon briefing set, eval-review Sun 17:00) before proceeding.
2. **A pre-trim Kolby baseline exists.** The stop/go for this whole exercise is a before/after eval — and `loops/eval-review/` has no artifact since **2026-07-12**. The first successful Sunday eval-review after the runtime is healthy IS the baseline; do not trim before it lands.

## Prep analysis (done 2026-07-29 — the session starts here, not from a blank page)
| Finding | Number | So what |
|---|---|---|
| `CLAUDE.md` size | **~3,357 words / ~4,500 tokens** | Paid on every session + every loop run |
| `01_company.md` size | ~1,040 words | **The boot context is 3.2× the full company doc it's supposed to point at** — the warehouse anti-pattern, quantified |
| Skills library | ~5,609 words / 15 skills | Healthy — already progressive disclosure; only `advisory-panel` (836w) is a split candidate |
| Self-documented drift | CLAUDE.md's own loop-count parenthetical ("*Loop counts here drift — `runtime/agent-registry.json` is the canonical list*") | A fact the file **knows** it can't keep current, kept anyway, with an apology attached. Textbook: the fact has a canonical home; the boot context should hold the pointer, not the copy |
| Duplication compensations | change-one-sweep-all + `runtime/consistency-check.py` | Precise claim: these exist because facts are duplicated. The audit reduces **internal doc** duplication; it does **not** retire the watchdog, which polices genuinely separate external surfaces (site · packets · CRM meta) that must legitimately restate the same fact |

## The six rules, as they apply here
1. **Rules → judgment.** Style/behavior prohibitions become outcome descriptions. *(Not compliance rules — see below.)*
2. **Examples → interface design.** Guidance about a tool belongs in that tool's description.
3. **Upfront → progressive disclosure.** CLAUDE.md holds identity + moat + current state + genuine gotchas + **pointers**; detail lives in `01_company.md`, `decisions/`, `processes/`, per-agent docs, skills.
4. **Repetition → one home per fact.**
5. **Manual memory → automatic.** No change needed (harness-side; the artifact discipline is a different, load-bearing thing).
6. **Simple specs → rich references.** Already ours: Kolby's rubrics ARE the "encode your taste so Claude can verify its own work" pattern.

## Steps
0. **Confirm both prerequisites.** If either is red, stop and fix the runtime first — that IS the higher-priority work.
1. **Run `/doctor`** in an interactive `claude` terminal (a terminal-dialog command — it cannot run in Cowork). It audits skills + CLAUDE.md and says what to cut. Capture the output into the session artifact.
2. **Contradiction scan.** Read CLAUDE.md and the skills side by side and list every clash (the classic: one doc demanding thorough documentation while another bans comments). Every clash is work the model does instead of the task.
3. **Classify every CLAUDE.md line** into exactly one bucket:
   - **KEEP** — identity, moat, current state, and *genuine gotchas nobody could infer from the repo* (the launch-gate, the OtherVenture/OtherVenture2 email separation, the shared-clone commit rule, launch.json-only serving).
   - **POINT** — true but detailed → move to its canonical home, leave one line + a link.
   - **CUT** — duplicated, stale, or inferable from the repo itself.
4. **Apply incrementally**, committing in slices via `runtime/commit-scoped.sh` so any regression is bisectable.
5. **Verify.** Next Sunday's eval-review is the "after." Compare against the baseline on the rubric's dimensions.

## What does NOT get trimmed (non-negotiable)
- **Compliance, brand, and security invariants stay hard rules** — no-send/no-delete, the approval gate, licensed-access-not-scraping, no fabricated stats/endorsements, white-label, no public prices. Rule 1 converts *style* prohibitions to judgment; it does not soften guardrails that exist because violating them has consequences.
- **Enforcement stays in the harness, not in prose** — the deny-list in `~/.claude/settings.json` is the real gate and is unaffected by any prose trim. (This split — enforcement in the harness, judgment in the prompt — is what the post recommends and what yourco already does correctly.)
- The consistency-check watchdog keeps running, and runs *hot* during the refactor: it is more valuable mid-migration, not less.

## Stop / go
**Kolby's before/after on the same rubric dimensions is the decision.** Degradation on grounding, honesty, or completeness → revert the slice that caused it (that's why step 4 commits incrementally) and log the failure mode. This is the prove-it-on-our-own-OS-first discipline: we test the 80%-no-eval-drop claim on *our* workload rather than taking a vendor benchmark on faith.

## Follow-through (the margin half — schedule separately, do not extend the 2h)
Fold the six rules into **`yourco-template` + the scaffolder's build practice** (Kimi/Kemba) so every future client OS ships lean context by default: lower run cost per operated engagement = margin. This is also the **model-upgrade dividend performed** — Anthropic deleted 80% of its own scaffolding on the new generation; yourco harvesting the same across its OS and every client build is the standing pitch, demonstrated rather than asserted.

## Notes
- **Time-box is real.** One session. If it wants a second, that's a signal to stop and re-check against the beachhead (0 signed clients) — this is the rare internal item that clears the 60-day filter, and also textbook rabbit-hole bait.
- **Graduate to a skill** if this runs a second time (next model generation, or per-client-template application) — per `.claude/skills/create-skill/`, a procedure re-run is a skill. First run stays an SOP because it carries one-time specifics.
