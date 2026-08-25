# Status Report: Always-On Headless Runtime Migration — 2026-06-09
**Author:** the Founder (YourCo) · builder-operator, holding for Kemba | **Date:** 2026-06-09

> Snapshot of the always-on runtime build. Canonical tracker: `decisions/2026-06-09_always-on-runtime.md`. Step-by-step: `processes/claude-code-setup.md`.

### Executive Summary
The base runtime is **live**: YourCo's OS now runs headless on a cloud VPS with Claude Code, git-synced, and a passing end-to-end smoke test. We're now wiring the MCP connectors — and hit the expected hard part: 5 of 7 connectors need browser-based OAuth, which on a headless box requires an SSH-tunnel technique we've now got an authoritative playbook for. One strategic decision (the autonomy/approval line) was made and logged. No blockers are fatal; the remaining work is methodical.

### Overall Status: 🟡 At Risk — *on plan, but connector OAuth is the fiddly long-pole*

### Key Metrics
| Metric | Target | Actual | Trend | Status |
|--------|--------|--------|-------|--------|
| Runbook steps complete (of 9) | 9 | 4 (repo, host, runtime, smoke test) | ↑ | 🟢 |
| MCP connectors live (of 7) | 7 | 0 (1st in progress) | ↑ | 🟡 |
| Headless smoke test | pass | **pass** ($0.04, Opus 4.8) | — | 🟢 |
| Days desktop-dependent loops persist | 0 | still all (until cutover) | flat | 🔴 |

### Accomplishments This Period
- **OS → private GitHub repo** (`yourco-os`), `.gitignore`, git-sync SOP + script, **daily auto-backup** scheduled.
- **VPS stood up** (Hostinger Ubuntu 24.04): `claudeops` user, Node 24, Claude Code 2.1.170, API key secret, repo cloned via **write-enabled deploy key**, **smoke test passed** end-to-end.
- **Two verified playbooks** captured in the runbook (Appendix B: connector setup; headless-OAuth via SSH port-forward).
- **Approval posture decided + logged** — auto on safe actions, gate the irreversible few, ratchet open as eval earns it.
- **Anthropic org corrected** to YourCo (caught OtherVenture entanglement before go-live).

### In Progress
| Item | Owner | Status | ETA | Notes |
|------|-------|--------|-----|-------|
| MCP connector OAuth (Descript, Higgsfield, Gmail, Cal, Drive) | the Founder | Mid-flight | next session | Needs SSH-tunnel auth, one-time each |
| Interactive Claude Code login | the Founder | Completing now | minutes | One-time onboarding under YourCo org |
| Slack connector | the Founder | Pending | next | Token-based; channel unconfirmed |

### Risks and Issues
| Risk/Issue | Impact | Mitigation | Owner |
|------------|--------|------------|-------|
| Headless MCP OAuth is fiddly (5/7 connectors) | Slows Step 1 | Authoritative port-forward playbook in hand; do one at a time | the Founder |
| "Easy token tier" collapsed — most connectors are OAuth | More manual auth | Accepted; one-time per connector, then cached | the Founder |
| Anthropic org shared/renamed (OtherVenture→YourCo) | Possible billing co-mingling | Confirm OtherVenture isn't on same org | the Founder |
| Loops still desktop-dependent until cutover | Missed runs | Finish Steps 5–9; daily backup bridges | the Founder |

### Decisions Needed
| Decision | Context | Deadline | Recommended Action |
|----------|---------|----------|--------------------|
| Slack loop channel | Needed to wire Slack + briefing | Next session | Confirm `#all-yourco` |
| Separate YourCo Anthropic org? | Renamed shared org for now | Before scale | OK if OtherVenture doesn't use it; else split |

### Next Period Priorities
1. **Finish connector OAuth** (Descript → Higgsfield → Google trio) via the SSH tunnel; sort Slack token.
2. **Build loop scaffolding** — `run-loop.sh` wrapper + systemd service/timer per loop (Step 5).
3. **Approval gates (Step 6) → headless Monday-briefing dry-run (Step 7)** — verify artifact + Gmail *draft* + Slack post, and that nothing gated sent.
