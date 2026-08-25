# Kolby spike — Promptfoo as the eval-harness backbone

> **Status: adopt-CANDIDATE, not adopted.** One time-boxed spike, then a go/no-go. Owner: **Kolby** (the Founder runs it until Kolby is built). Source: `decisions/2026-07-05_tool-triage.md` §Addendum 07-20 (11-repo batch). Not scheduled ahead of the beachhead — do this when eval work is already on the bench, not as a detour from Sample Client.

## Why this is worth a spike (and why it's not a stance violation)
yourco's whole pitch is **reliability + eval + observability**, but Kolby's eval harnesses are **bespoke scripts** today. [Promptfoo](https://github.com/promptfoo/promptfoo) (MIT) is the industry-standard OSS eval + red-team runner: declarative test cases, assertions, LLM-as-judge, red-teaming, CI integration.

It **passes the framework-adoption stance** (`decisions/2026-06-14_framework-adoption-stance.md`) because it is a **test harness, not an agent brain** — the pytest-for-LLMs shape. Config lives in git, runs locally/CI, fully inspectable and ownable. That is *exactly* the "real version control + real evals in git" property the no-n8n decision (`decisions/2026-06-15_no-n8n-stance.md`) named as our advantage over no-code. Promptfoo is the tool that makes "we do real evals" literally true instead of aspirational.

**The one guardrail:** promptfoo is the **runner**; the moat is our **rubrics + judgment**. Adopting the runner must not become "the eval is whatever promptfoo's defaults score." The rubrics stay ours.

## The spike (time-box: ~half a day)
1. Pick **one existing bespoke harness** Kolby already runs (e.g. an outbound-copy eval, or the Bella audit-report eval).
2. Re-express it in promptfoo: test cases + assertions (deterministic + LLM-as-judge) as a git-tracked config.
3. Run both the bespoke version and the promptfoo version on the **same** set of real outputs.
4. Compare on the axes below.

## Go / no-go criteria
**Adopt if** promptfoo, vs the bespoke script:
- expresses the same rubric with **less code + clearer diffs** (a reviewer can read the config and see what's tested);
- gives **equal or better signal** (no important check we can't express as an assertion);
- runs in **CI headless** on the VPS with no new always-on service (config + runner only — no server to babysit, or the moat-test-#1 "adds a runtime we must own" cost outweighs it);
- keeps our rubrics **authoritative** (LLM-judge prompts are ours, versioned, not opaque defaults).

**Skip if** it forces our rubrics into shapes that lose signal, needs a hosted service, or the migration cost exceeds the bespoke maintenance cost.

## Guardrails if adopted
- **Self-hosted / library only** — no promptfoo SaaS, no telemetry to their cloud (verify the sharing/telemetry flags are off; secret-hygiene per `.claude/skills/wire-credentialed-connector/`).
- **Configs live in git** next to the agent they test; the runner is invoked by Kolby's loop, not a new daemon.
- **Rubrics are the asset** — promptfoo executes them; it never defines "good."
- If it becomes core, log a proper decision (`log-decision`) recording it as the eval backbone + the boundary above.

## Beachhead note
This is the *only* item from the 07-20 batch that asks for near-term effort, and it's load-bearing for the exact thing yourco sells. Still: it's a spike behind the first signed client, not ahead of it.

---

## Results — run 2026-07-22 (spike executed)

**Target chosen:** the outbound **pre-send eval gate** (`processes/outbound/pre-send-eval-gate.md`) — the most concrete existing harness (real copy, a real six-dimension rubric, and a coded pre-pass in `runtime/instantly.py --eval-batch`). promptfoo **0.121.19** was already cached; node 26 present.

**What was run:** the **deterministic layer** as a promptfoo config (`echo` provider + javascript assertions) against 3 real fixtures — a clean rendered Touch 1, the **actual canonical Touch 2** from `sequence-copy.md`, and a deliberately-broken preview. Config + fixtures in scratchpad (`scratchpad/promptfoo-spike/`), not committed (throwaway until the go/no-go).

**Result — it works and it discriminates** (table below reflects the corrected run after the blocklist fix):
| Fixture | Verdict | Note |
|---|---|---|
| Touch 1 (clean, rendered) | ✅ PASS | all checks green |
| Touch 2 (REAL canonical copy, uses "Reese") | ✅ PASS | Reese = sanctioned demo persona, correctly NOT flagged |
| Prospect named "David" in greeting | ✅ PASS | roster-collision handled (greeting stripped) |
| "Reilly" (real internal agent) in body | ❌ FAIL | scoped blocklist still fires |
| Broken preview | ❌ FAIL | leaked `{{merge var}}`, `$` price, capitalized `YourCo`, missing opt-out — 4/4 |

### Finding #1 — CORRECTED: the "Reese" flag was a false positive, and that's the useful result
The first run flagged "Reese" in canonical Touch 2/3 as an internal-agent-name violation. **That was wrong.** Reese is the **sanctioned landscaping demo persona** (`prospect-demo.html`, `proposal.html`, `sequence-copy.md`), not a roster agent (absent from `04_agent_roster.md`) — and dimension 4 *explicitly allows* the locked demo persona. My blocklist was too blunt: it lumped "Reese" in with internal agents (Reilly/Kolby/…). **the Founder ruled the persona split deliberate** (`decisions/2026-07-22_persona-on-1to1-surfaces.md`): named persona on 1:1 surfaces (outbound/demo/proposal), role-generic on the website.

**Why this is the spike's best result, not a wasted flag:** it pinpoints the exact boundary between the two layers. A deterministic regex *cannot* tell "Reese" (allowed persona) from "Reilly" (banned agent) from "David" (a real prospect's first name) — all three are just capitalized words. So the deterministic check was **scoped**: internal roster only, demo personas excluded, greeting line stripped (prospect first-names collide with the roster — David/Jim/Ray/Harry/Katie/Mario/Brett…). Genuinely ambiguous name calls belong to the **LLM judge**, not the regex — a concrete argument for why the judge layer earns its keep.

### Finding #2 — promptfoo's ergonomic tax (Kolby must know this)
promptfoo renders **both the copy AND the assertion `value` strings through nunjucks.** Any literal `{{` crashes the whole row with an opaque `expected variable end` — and `{{` is *exactly* what a leaked-merge-var check contains. Cost 3 debug iterations. Mitigations, now known:
- brace-checks must be regex `/\{\{/`, never literal `output.includes('{{')`;
- test copy containing a real leaked var must be wrapped `{% raw %}...{% endraw %}`;
- js asserts must return a **boolean / number / GradingResult object** — the `cond || 'message'` idiom silently errors ("must return a boolean…").

None are blockers, but they're sharp edges — a `_README` in the eval config dir would save the next person the same 3 iterations.

### The scope correction (important, changes the framing)
`instantly.py`'s M1–M5 are **Instantly/CRM *state* checks** (campaign paused? leads have demo_urls? HTTP 200? CRM dedupe?) — those need API access and **stay in `instantly.py`**; promptfoo can't and shouldn't do them. What promptfoo cleanly owns is the **copy-content layer**: the rendered-copy checks above **+ the six LLM-judge dimensions** — which today live **entirely in Kolby's prompt, unversioned**. So promptfoo doesn't replace the coded pre-pass; it **systematizes the half that is currently just judgment-in-a-prompt**. That's the higher-value half to make into config-in-git.

### Not run: the LLM-judge half
The six dimensions were written as `llm-rubric` assertions (`promptfooconfig.full.yaml`) but **not executed** — the repo holds only an **admin key** (`sk-ant-admin`, Admin API, no inference); llm-rubric needs an inference key (`sk-ant-api`). Honest gap, not a pass.

## Revised go / no-go
- **Deterministic copy-content layer → provisional GO.** Fully expressible as config-in-git, greppable, no new runtime (`npx promptfoo eval` in CI), and it caught a real issue on first run. Strong fit to replace the "Kolby eyeballs the rendered copy for banned words / agent names / prices / raw vars" step with a versioned check.
- **LLM-judge layer → PENDING one key-enabled run.** Decision blocked on: `export ANTHROPIC_API_KEY=sk-ant-api…` → run `promptfooconfig.full.yaml` on the same fixtures → compare the model's dimension scores against a Kolby hand-score on the identical copy. If they agree, adopt; if the rubric needs heavy coaxing to match the Founder's taste, the bespoke judgment prompt may stay.
- **Unchanged either way:** rubrics are the asset (promptfoo just executes them); self-host/library only, no promptfoo SaaS/telemetry; configs live in git next to the agent they test.

**Next action (the Founder, ~10 min):** drop an inference key in `runtime/.promptfoo.env` (per `wire-credentialed-connector`), re-run `full.yaml`, paste the judge scores here. Then this converts from provisional to a logged decision via `log-decision`. Until then: **deterministic layer is a GO to build into the gate; judge layer is a maybe.**
