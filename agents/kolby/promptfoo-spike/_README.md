# promptfoo spike — working artifacts (NOT yet adopted)

Proven configs from the 2026-07-22 spike (`../promptfoo-spike.md` has the writeup + go/no-go). Kept in-repo so the next step is one command, not a rebuild. **Nothing here is wired into the runtime** — this is a spike, pending the judge-half decision.

## Files
- `promptfooconfig.deterministic.yaml` — the copy-content checks that run with **no API key** (leaked merge var · internal agent name · price · brand-case · opt-out). Self-contained (inline fixtures).
- `promptfooconfig.full.yaml` — adds the six LLM-judge dimensions as `llm-rubric`. **Needs an inference key.**
- `fixtures/touch1.txt` — a clean rendered Touch 1 sample.

## Run
```bash
cd agents/kolby/promptfoo-spike
# deterministic layer (no key) — should be 1 PASS, 2 FAIL (Touch 2 catches 'Reese'):
PROMPTFOO_DISABLE_TELEMETRY=1 npx promptfoo@0.121.19 eval -c promptfooconfig.deterministic.yaml --no-cache

# judge layer (needs a real inference key, NOT the repo's admin key):
export ANTHROPIC_API_KEY=sk-ant-api...   # via runtime/.promptfoo.env per wire-credentialed-connector
PROMPTFOO_DISABLE_TELEMETRY=1 npx promptfoo@0.121.19 eval -c promptfooconfig.full.yaml --no-cache
```

## Gotchas (cost real iterations — see writeup Finding #2)
- promptfoo renders assertion `value` strings through nunjucks too → a literal `{{` crashes the row. Use regex `/\{\{/`, never `output.includes('{{')`.
- Test copy that intentionally contains a leaked `{{var}}` must be wrapped `{% raw %}...{% endraw %}`.
- javascript asserts must return a boolean / number / GradingResult object — `cond || 'msg'` silently errors.
