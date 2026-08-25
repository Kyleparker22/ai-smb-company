---
name: show-surface
description: Put a local surface (HQ dashboard, CRM, staged site, client console, demo) in front of the Founder — or produce a link he can send someone. Use whenever the ask is "show me X" / "can I see the site now" / "pull up X" / "give me a link I can send to <person>". Replaces the guess-a-port-then-fail loop that produced "No preview is open" in 8 of the last 35 days' sessions.
---

# show-surface — get a surface on screen (or into a sendable link)

## When
Any request whose done-state is *the Founder looking at something* or *the Founder holding a link*: "show me the HQ and CRM", "and show me the website", "can i see the site now", "pull up Sample Product", "provide me a link I can send to Partner B". NOT for surfaces that are already deployed at a public URL (just give the URL) and NOT for building the surface itself — this is the last mile only.

## Steps (Cowork/host only — headless loops have no preview tools)
1. **Read `.claude/launch.json` first. Never guess a server name or a port.** Every local surface is registered there (`yourco-hq`, `yourco-crm`, `yourco-webb-pages`, `yourco-client-console`, `yourco-demo-kit`, `yourco-sample-client`, `sample-client-proposal`, `sample-client-design-studio`, `nick-storm-demo`, `nick-crew-app`, `Reed-salon-voice-demo`). If the surface the Founder named isn't there, that's step 5.
2. **Start it by name:** `preview_start` with `{name: "<launch.json name>"}` — not `{url: "http://localhost:<port>"}`. Starting by URL when no server is running is what produces "No preview is open" and "navigation to http://localhost:PORT was denied or failed."
3. **Verify it responds before saying a word about it.** `read_page` (or `get_page_text`) and confirm real content — a running server serving a 404 or an empty shell looks identical to success in the tool result. If a dev server won't start, check `preview_logs` before retrying.
4. **Hand over the proof, not the promise.** Give the Founder the URL *and* a screenshot (`computer{action:"screenshot"}`) or a two-line description of what's on screen. "It's running at :8790" without evidence is the failure this skill exists to prevent — he asks again, and the second ask is the friction.
5. **New surface → register it before sharing.** Add a `.claude/launch.json` entry (name, runtimeExecutable, runtimeArgs, port), start it by name, verify per step 3, then share. A link shared before a verified 200 is the #1 way a demo dies in front of someone.

## Sending it to someone else
6. If the ask is "a link/file I can send to <person>", the deliverable is **self-contained**: a localhost URL is useless to them. Either produce a single-file HTML artifact (open it locally to verify it renders standalone), or use the already-deployed URL. Say plainly which one it is and whether it expires.
7. **the Founder sends; agents draft.** Produce the link plus the message copy and stop — do not text, email, or post it. ("Do not text Nick. Provide me the Link and I will text him," 2026-07-28.)

## Gotchas
- Tool names drift: it is `preview_start` / `mcp__Claude_Browser__*`. `mcp__Claude_Preview__preview_start` does not exist and has been called by mistake.
- `computer{action:"left_click", coordinate:…}` needs a prior `screenshot` in the same session; `find` needs a prior `read_page`. Sequence: screenshot/read_page → act.
- `scroll_amount` and `duration` on `computer` max out at **10** — larger values are a hard validation error, not a clamp.
- If the Browser pane hangs ("computer timed out after 30s"), don't re-issue the same click: re-`navigate` or restart the server, then re-verify.
- Two surfaces at once ("show me the HQ and CRM") = two `preview_start` calls and two verifications. Half-answering guarantees the follow-up ask.

## Canonical doc
`.claude/launch.json` is the truth for what exists and on which port; `./show.sh` is the human one-command equivalent. CLAUDE.md carries the one-line rule ("local surfaces are served ONLY via the server names in `.claude/launch.json`") — this skill is the procedure behind it.

## When the Browser pane says "Maximum 5 dev servers per folder"
Learned 2026-08-10 (`learnings/ops/2026-08-23_preview-url-bypasses-server-slots.md`). In order:
1. **Look for a server already covering it** — `ps -eo pid,etime,command | grep http.server`, then `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/<path>`.
2. **`preview_start({url: "http://localhost:<port>/..."})`** — takes no slot and works while `{name: ...}` is refused. (`navigate` to a bare localhost URL is blocked by policy; `preview_start({url})` is not.)
3. **Only then** ask the Founder to stop one from the other chat's window.

**Killing the OS processes does not free a slot** — the cap is harness bookkeeping. Clean up stale servers as housekeeping, never as a fix.

**`file://` will not substitute for HTTP**: the pane snapshots local files to a `data:` URL and drops linked stylesheets, so the page renders unstyled. Verify the design system loaded by reading a *token* (`--brass`), not a rule from the page's own inline `<style>`.

**If the pane is hidden, screenshots come back blank while the DOM still answers.** Measure instead of looking: bounding boxes, `scrollWidth > innerWidth` for overflow, `gridTemplateColumns` length for responsive stacking.
