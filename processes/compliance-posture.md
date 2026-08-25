# Compliance Posture & Control Register

> **Owner: Rafi** (Compliance — see `agents/rafi/`). The living record of YourCo's regulatory + security controls, their status, and open gaps. Flags only — **remediation is the Founder's call.** Framework backbone: NIST CSF (Identify → Protect → Detect → Respond → Recover); privacy stance: Privacy by Design (Cavoukian). Last reviewed: 2026-06-11.

## Status legend
✅ in place · 🟡 partial / needs work · 🔴 not done · ⏳ blocked on an external gate (counsel, vendor, first client)

## 1. Security controls (Protect / Detect)
| Control | Status | Notes |
|---|---|---|
| **Approval gate** (always-on ≠ auto-send) | ✅ | Host `~/.claude/settings.json`: deny external `gmail.send` / `delete` / `Bash`; allow drafts / reads / internal Slack. Proven in production. |
| **Secrets management** | ✅ | Tokens/keys in `~/.yourco/env` + `~/.gmail-mcp` / `~/.calendar-mcp` on the host; **gitignored, never committed.** |
| **Private source repo** | ✅ | `founder22/yourco-os` private; write-enabled deploy key on host. |
| **Access / auth** | 🟢 mostly | **ufw firewall active + key-only SSH** — password auth disabled + confirmed refused, 2026-06-10. Hosted CRM + dashboard reachable **only over Tailscale** (private WireGuard mesh; never the public internet), 2026-06-11. Left: **2FA sweep** across accounts (the Founder, per-account). |
| **Least privilege (connectors)** | 🟡 | Slack bot-token scopes, Gmail (draft/read), Calendar (read-only set), Instantly (`all:read`). Left: periodic scope review — grant only what each loop needs. |
| **Monitoring** | ✅ | Atlas (ops) + the watchdog loop observe the fleet; Kolby grades output quality. |
| **Agent registry + drift watchdog** (Detect) | ✅ v0 | Sanctioned-agent baseline `runtime/agent-registry.json` + `runtime/agent-registry-check.py` — diffs live runtime (prompts, systemd units, connector scopes, commit authors) against it and flags any unsanctioned addition. Weekly (`yourco-agent-registry.timer`, Mon 07:45 ET); surfaces in the Monday briefing. Detect-only; the Founder alone sanctions (by editing the registry). The "Vanta for our own agents." Decision: `decisions/2026-06-22_agent-registry-governance-watchdog.md`. Next: client-tenant attestation at first signed engagement. |
| **Incident response (Respond / Recover)** | ✅ | **Security Incident Runbook** (`agents/rafi/security-incident-runbook.md`) — implements the DPA §10 72-hour breach-notification duty; detect → contain → notify → remediate → review, with a wall card for under-stress use. Reviewed periodically. |

## 2. Data handling & privacy (Privacy by Design)
| Item | Status | Notes |
|---|---|---|
| Data inventory | 🟡 | Pre-client: only YourCo's own Gmail/Slack/Calendar. No client data yet. Build a real inventory when the first engagement lands. |
| Client data in the client's tenant | ✅ (by design) | The named employee runs in the *client's* tenant; YourCo accesses via scoped connectors, doesn't custody client data centrally. |
| **Privacy policy (public)** | 🔴 | The site/landing collect data (Calendly, forms). **Needs a published privacy policy before go-live** — coordinate with Ray + counsel. |
| **DPA (data processing addendum)** | 🟡 drafted | `processes/contracts/dpa.md` — **reconciled 2026-06-11** to full depth (state Privacy Laws, 72-hr breach clause, current sub-processor stack, security annex). Left: counsel finalize before first client data. |
| Data minimization + retention | 🟡 | Principle adopted; write explicit retention rules at first engagement. |

## 3. Outreach legality (before any send)
| Regulation | Status | Notes |
|---|---|---|
| **CAN-SPAM** (commercial email) | 🟡 | Needs: working unsubscribe, valid physical mailing address, no deceptive headers in every Reilly campaign. Verify in `copy-structure.md` before first send. |
| **TCPA** (SMS consent) | ⏳ | 10DLC registration in progress (`processes/10dlc-sending-infra-setup.md`); no SMS until approved + consent posture confirmed. |
| **FTSA** (Florida Telephone Solicitation Act) | ⏳ | Flagged for counsel review (stricter than TCPA on auto-dialed/texted solicitations). **Counsel sign-off required before SMS outreach.** |
| Suppression / DNC | 🟡 | `agents/reilly/_suppression.md` exists; confirm replied/unsubscribed/DNC honored automatically. |

> **Go-live gate:** no outreach sends until CAN-SPAM verified, and no SMS until 10DLC approved + FTSA/TCPA counsel sign-off. Rafi + Ray + the Founder clear this together.

## 4. Procurement readiness (enterprise asks)
| Item | Status | Notes |
|---|---|---|
| SOC 2 / ISO 27001 | 🔴 | None yet (pre-revenue, SMB-focused). Build only when a prospect's procurement requires it; until then, answer questionnaires with the honest current posture. |
| Security questionnaire response | 🟡 | Rafi drafts answers from this register on demand; the Founder approves before sending. |

## Open items (Rafi's flag list → the Founder remediates)
*Drafts built 2026-06-10 — remaining action is counsel review or the Founder execution.*
1. **Privacy policy** — ✅ drafted (`processes/contracts/privacy-policy.md`). Left: counsel review → Webb publishes at `/privacy` before the site collects data at go-live.
2. **DPA** — ✅ drafted + **reconciled 2026-06-11** to full depth (`processes/contracts/dpa.md`; merged the mature `dpa-v3-prior.md`). Left: counsel review before any client data.
3. **Outreach legality** — ✅ CAN-SPAM checklist + FTSA/TCPA brief built (`agents/rafi/outreach-compliance.md`); **email-first recommended**. Left: verify CAN-SPAM items (footer address + working unsubscribe) before first send; **FTSA/TCPA counsel sign-off** before any SMS.
4. **Account hardening** — ✅ runbook built; **VPS firewall + key-only SSH done 2026-06-10**, Tailscale-only hosting added 2026-06-11. Left: **2FA sweep** (the Founder, per-account) — the one remaining hardening item.
5. **Security Incident Runbook** — ✅ adopted 2026-06-11 (`agents/rafi/security-incident-runbook.md`); satisfies the DPA's 72-hr notification duty. Left: counsel spot-review alongside the DPA.
6. **HIPAA BAA + vertical-compliance map** — ✅ drafted 2026-06-12 (`processes/contracts/baa.md` + `agents/rafi/vertical-compliance-map.md`). Discovery flags the vertical's gate (healthcare→BAA, etc.); BAA signs before any PHI flows. Left: counsel review of the BAA. *(Surfaced by the Northside dental dry-run.)*
7. **Sandbox test-tenant** — spec'd 2026-06-12 (`processes/sandbox-test-tenant.md`) to run the live-integration eval on synthetic data before a client's real tenant — strengthens the eval/autonomy gate. Left: Kemba/the Founder provision it.
8. Build a real **data inventory + retention policy** at the first engagement (unchanged).

## Review cadence
On-demand (any "are we clear?" check) + a quarterly posture review (can be wired as a runtime loop like Polo's). Each review: re-check every control above, update status, refresh the open-items list.
