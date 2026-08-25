# Account Hardening Runbook

> **Owner: Rafi (flags) → the Founder (executes).** Concrete steps to harden yourco's accounts + the VPS before go-live. Rafi can't enable 2FA for you (that's your per-account action) — this is the checklist; you run it.

## 1. Two-factor authentication (enable on every account)
Enable 2FA (authenticator app preferred over SMS) and **save the backup codes in a password manager**. Accounts:
- ☐ **GitHub** (`founder22`) — holds the OS repo + deploy key
- ☐ **Google** — the YourCo Workspace + the ops account behind Gmail/Calendar connectors (no 2FA here = the whole connector stack is exposed)
- ☐ **Vercel** — web deploys
- ☐ **Hostinger** — the VPS host (root access)
- ☐ **Vapi** + **Twilio** — voice/telephony (client-facing infra)
- ☐ **Instantly** — outbound sending
- ☐ **Anthropic Console** — API keys / billing
- ☐ **Higgsfield**, **Descript** — media tools (billing attached)

## 2. VPS hardening (run these on the server — `claudeops@srv1745256`)
```bash
# Firewall: allow SSH only, deny the rest
sudo apt-get update && sudo apt-get install -y ufw
sudo ufw allow OpenSSH
sudo ufw --force enable
sudo ufw status

# Disable password SSH (keys only) — confirm your SSH key works FIRST
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Optional: brute-force protection
sudo apt-get install -y fail2ban

# Lock down secrets file perms
chmod 600 ~/.yourco/env ~/.gmail-mcp/credentials.json ~/.calendar-mcp/gcp-oauth.keys.json 2>/dev/null
ls -la ~/.yourco/env
```
> ⚠️ Confirm your SSH **key** login works before disabling password auth, or you can lock yourself out. (The keepalive is already in your Mac's `~/.ssh/config`.)

## 3. Recovery posture
- ☐ Store all 2FA backup codes in a password manager (not a text file).
- ☐ Set recovery email/phone on the critical accounts (Google, GitHub, Hostinger).
- ☐ Confirm the GitHub deploy key on the VPS is **deploy-scoped** (not a full account key).

## Status
- ✅ **VPS hardening done 2026-06-10** — ufw firewall active (SSH only); **key-only SSH** (password auth disabled in `sshd_config.d/50-cloud-init.conf`, restart applied, refusal confirmed). the Founder's `~/.ssh/id_ed25519` is the access key.
- ✅ **Auto-updates + secrets chmod done 2026-06-10** — `unattended-upgrades` installed + actively running (confirmed via the login banner's auto-update log); `~/.yourco/env` now `-rw-------` (600). (fail2ban skipped — no password login to brute-force.)
- ⬜ **2FA sweep** across accounts — the remaining high-value item; the Founder's per-account action (§1 above).

Tracked in `processes/compliance-posture.md` §1.
