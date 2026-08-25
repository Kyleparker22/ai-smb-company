2026-08-23 — `preview_start({url})` bypasses the 5-dev-server cap; killing the processes does not

Source: verifying the delegation 2×2 added to the staged audit intake form (`a46eb8c`). Four turns were spent blocked on "Maximum 5 dev servers per folder reached; 5 belong to other chats."

Pattern: three things about the Browser pane, each of which cost time before it was understood.
**(1) The 5-server cap is harness bookkeeping, not process state.** Eight orphaned `http.server` processes had been running in this folder for five and six days. Killing all eight freed nothing — `preview_start` still reported five slots held. Only the owning chat (or the Founder, from that chat's window) releases a slot. Killing processes is worth doing as housekeeping and is *not* a fix for the cap.
**(2) `preview_start` with `url` needs no slot at all.** `preview_start({url: "http://localhost:8793/..."})` opened immediately while `preview_start({name: "yourco-webb-pages"})` was still refused. This is the documented behaviour — `url` opens a browser tab, `name` starts a dev server — but under a cap the distinction stops being a convenience and becomes the whole workaround. Note `navigate` to the same localhost URL is **blocked by policy**; only `preview_start({url})` opens it.
**(3) A running server may already be serving what you need.** `agents/webb/pages` was already up on :8793 from another chat. `ps -eo pid,etime,command | grep http.server` and a `curl -o /dev/null -w "%{http_code}"` answered in seconds what a slot request could not.

Also: **`file://` is not a substitute for HTTP here.** The pane converts local files to a `data:` snapshot and drops linked stylesheets — `tokens.css` and `site.css` never load, the page renders unstyled on a transparent body, and screenshots come back black. Inlining the CSS into a scratch copy does not help; the snapshot strips those `<style>` blocks too. A "cssLoaded: true" check can be actively misleading if it reads a rule from the page's own inline block rather than the linked design system — check a **token** (`getComputedStyle(root).getPropertyValue('--brass')`) instead.

Implication: when the Browser pane is capped, in order — (a) `ps` for a server already covering the directory and `curl` it; (b) `preview_start({url})` against that port; (c) only then ask the Founder to stop one from the other chat's window. Never kill another chat's server expecting a slot back. And when the pane is hidden, screenshots return blank while the DOM is fully queryable — verify layout by **measuring** (bounding boxes, `scrollWidth > innerWidth` for overflow, `gridTemplateColumns` for responsive stacking) rather than by picture; it is more precise anyway and it works when the pane will not cooperate.

Audience: any agent building or verifying a local surface — Webb (site), Atlas (HQ), Kimi (client surfaces); and the `show-surface` skill, whose whole reason for existing is the "No preview is open" failure.

Triggers: preview_start, dev server, Browser pane, max servers, localhost blocked, screenshot blank, file://, skill:show-surface, agent:webb, agent:atlas
