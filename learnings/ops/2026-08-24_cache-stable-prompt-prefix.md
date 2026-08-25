2026-08-24 — Variable content goes at the END of a prompt, never the front

Source: Manus, "Context Engineering for AI Agents" (triaged in `decisions/2026-07-05_tool-triage.md`
§Addendum 2026-08-24), applied to `runtime/run-loop.sh` the same day it was written.
Pattern: A prompt's KV-cache is valid only up to the **first token that differs** from the previous
call. So anything that changes run-to-run — a timestamp, retrieved learnings, a rejections list, a
"today's date" line — invalidates the cache for **everything after it**. Put it at the front and the
whole prompt is uncached; cached input runs roughly a tenth the price of uncached on the same model.
yourco's own instance: `run-loop.sh` prepended Step 0 learnings + the anti-library to every loop
prompt. Both change whenever anyone writes a learning or a rejection, and they sat in front of ~20 loop
prompts a day. Reordered to append.
Implication: **When you inject anything into a prompt, append it.** Two reasons, and the second holds
even where caching does not apply: material near the end of the context sits in the model's recent
attention span, which is what you want for "read this before working." The named classic mistake is a
timestamp at the top of a system prompt — check for that first in any new prompt.
Caveat worth keeping: whether separate `claude -p` runs hit a cross-run cache at all is **unmeasured**
here, so do not claim a dollar saving from this. The ordering is correct on its own merits.
Audience: anyone editing `runtime/run-loop.sh`, a loop prompt, or an agent's system prompt

Triggers: run-loop, prompt assembly, loop prompt, system prompt, kv-cache, prompt caching, token cost, step 0 injection, context engineering
