# Phone / remote access — the OS in your pocket

> **Status: LIVE REFERENCE** — Tailscale access to the VPS and its surfaces. Verified working 2026-08-23.

> Reach the whole OS from anywhere, privately, over **Tailscale** (a WireGuard mesh — nothing is exposed to the public internet; only your signed-in devices can connect). Set up 2026-06-11 (Group C).

> **↳ SSH in (the one command):** with the **Tailscale** app ON, run `ssh user@your-vps` from any signed-in device — **keyless** (Tailscale authenticates you; no password or key). Already at a `claudeops@srv1745256:~$` prompt? You're **already in** — skip SSH and run commands directly. Most common task → restart the Slack command listener: `cd ~/yourco-os && git pull && sudo systemctl restart yourco-slack-listener`.

## The pieces
- **Tailnet identity:** founder@yourco.example.com (use the same login on every device).
- **VPS Tailscale address:** `10.0.0.1` (stable; `tailscale ip -4` on the host to re-check).
- **Hosted apps** (systemd services on the VPS, bound to the Tailscale IP only, auto-restart):
  - **CRM** → `http://10.0.0.1:8790` — fully editable; edits git-commit + push, so phone ⇄ agents stay in sync.
  - **Dashboard** → `http://10.0.0.1:8791` — live, read-only.
- **SSH** (Tailscale SSH, keyless — Tailscale authenticates you): `user@your-vps`.

## One-time device setup
1. Install the **Tailscale** app, sign in as founder@yourco.example.com, toggle ON.
2. For app access: open the two URLs above in the browser → **Add to Home Screen** for one-tap launch.
3. For control: install an SSH app (**Termius**, free) → host `10.0.0.1`, user `claudeops` (no key/password — Tailscale handles auth).

## Phone cheat-sheet (after SSH in)
```bash
cd ~/yourco-os && git pull          # get the latest before doing anything
claude                              # interactive session with the whole OS (gated: drafts/posts/reads; no send/delete)

# Trigger an agent on demand:
sudo systemctl start yourco-pipeline-report.service   # David — pipeline report
sudo systemctl start yourco-eval-review.service       # Kolby — eval
sudo systemctl start yourco-monday-briefing.service   # Atlas — briefing
sudo systemctl start yourco-inbox-triage.service      # Jim — inbox
sudo systemctl start yourco-sales.service             # sales loop
sudo systemctl start yourco-finance.service           # Charles — finance

# See what happened:
tail -40 loops/_runtime/<loop>.log                    # a loop's run log
systemctl list-timers | grep yourco                   # all scheduled agents + next run
systemctl is-active yourco-crm yourco-dashboard       # are the hosted apps up
```

## Security posture
- Apps bind to the Tailscale IP only — **never the public internet.** No public URL, no public port.
- SSH is Tailscale-authenticated (your identity), no exposed key.
- A Claude session on the VPS runs under the host approval gate (`~/.claude/settings.json`): file R/W, Slack post, Gmail draft allowed; **send / delete / Bash denied.** The Mac (Cowork) remains the full-capability surface.
- To revoke a lost device: remove it in the Tailscale admin console — it instantly loses all access.
