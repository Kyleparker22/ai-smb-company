# Design & Development Tools

Pre-wired tools for design, frontend development, and automation. These are available now as git submodules, ready to integrate into the runtime and agent workflows when your business is live.

## Inventory

### 1. **Taste Skill** — Design system builder
- **Repo:** `taste-skill/`
- **Purpose:** Build and maintain visual design systems; generate brand-consistent UI components
- **When to use:** After your brand/DESIGN.md is locked in, use this to generate component libraries, design tokens, and brand asset systems
- **Agent integration:** Design-loop agents (e.g., the one that builds branded surfaces for clients)

### 2. **Impeccable** — UI design + hand-off tool
- **Repo:** `impeccable/`
- **Purpose:** Design UIs in code, generate comps, hand off to developers with zero rework
- **When to use:** For rapid iteration on client-facing surfaces (dashboards, consoles, internal platforms)
- **Agent integration:** Design-surface agents; pairs with visual-brand-qa skill for QA

### 3. **Playwright CLI** — Browser automation & testing
- **Repo:** `playwright-cli/`
- **Purpose:** Automate browser interactions, run end-to-end tests, capture screenshots of designs in live context
- **When to use:** For verifying designs work across browsers; testing agent-written HTML; capturing visual regression tests
- **Agent integration:** Quality-check loops; live-testing agents

### 4. **Awesome Design** — Design resource library
- **Repo:** `awesome-design/`
- **Purpose:** Curated collection of design patterns, tools, and resources
- **When to use:** Reference for design decisions, pattern inspiration, tool recommendations for new features
- **Agent integration:** Context for design-direction agents

### 5. **img2threejs** — Image to 3D converter
- **Repo:** `img2threejs/`
- **Purpose:** Convert 2D images/mockups to interactive 3D models
- **When to use:** For creating 3D product visualizations, interactive demos, immersive client presentations
- **Agent integration:** Creative/portfolio agents; client demo loops

## Installation

All are installed as git submodules. To initialize:

```bash
git submodule update --init --recursive
```

## Setup order

1. **Brand locked** → wire Taste Skill (Step 02 in SETUP)
2. **First surface design** → add Impeccable (Step 07 in SETUP)
3. **QA automation needed** → integrate Playwright (Step 08/09)
4. **Design reference needed** → import Awesome Design patterns (ongoing)
5. **3D demos** → activate img2threejs (when client asks for it)

## Pre-build checklist

Before adding these to your runtime:

- [ ] CLAUDE.md filled in with YOUR company details
- [ ] Brand/DESIGN.md locked (Taste Skill needs this)
- [ ] First client or internal surface designed (Impeccable needs a real use case)
- [ ] Local Claude Code environment working (SETUP/04)
- [ ] `.claude/launch.json` updated with any new dev servers these tools need

## Notes

- These are **not** dependencies in `requirements.txt` yet — add them as you integrate each
- Submodule updates are manual: `git submodule update --remote` periodically checks for upstream changes
- Each tool has its own README — start there when you're ready to use it
- Some require Node.js / npm (Playwright, Taste Skill); verify your local environment has them
