#!/usr/bin/env python3
"""yourco — audit → engagement scaffolder (the realistic "1-click build").

Takes the Audit findings and **scaffolds the engagement to ~80%** in one command: clones the golden
template into a client folder, pre-fills the discovery doc from the diagnosis, and seeds the demo-kit.
It does NOT 1-click a live agent — the reliability layer (integrating the client's tools/tenant, eval
against their criteria, the approval gate) is Kimi's human+build work, and that's the moat, on purpose.

Input: the AUDIT json (the same object Bella fills in `clients/_yourco-template/audit-report/index.html`),
or basic flags. Dry-run by default; --commit creates the folder.

Usage:
  python3 runtime/scaffold_engagement.py --audit audit.json                 # dry run — show the plan
  python3 runtime/scaffold_engagement.py --audit audit.json --commit        # create clients/<slug>/
  python3 runtime/scaffold_engagement.py --client "YourCo Landscaping" --vertical Landscaping \
      --first-build "AI Front Desk" --commit
"""
import os, sys, json, re, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(REPO, "clients", "_yourco-template")


def _slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def _arg(a, k, d=None):
    return a[a.index(k) + 1] if k in a else d


def load_audit(a):
    if "--audit" in a:
        d = json.load(open(_arg(a, "--audit")))
        return {"client": d.get("client", ""), "vertical": (d.get("vertical", "") or "").split("·")[0].strip(),
                "first_build": (d.get("firstBuild") or {}).get("name", ""),
                "first_desc": (d.get("firstBuild") or {}).get("desc", ""),
                "bottlenecks": [b.get("name", "") for b in d.get("bottlenecks", [])],
                "headline": d.get("headline", ""), "bigNum": d.get("bigNum", ""),
                "roadmap": d.get("roadmap", [])}
    return {"client": _arg(a, "--client", ""), "vertical": _arg(a, "--vertical", ""),
            "first_build": _arg(a, "--first-build", ""), "first_desc": "", "bottlenecks": [],
            "headline": "", "bigNum": "", "roadmap": []}


def discovery_seed(au):
    today = datetime.date.today().isoformat()
    rm = "\n".join(f"- **{r.get('phase','')}** — {r.get('emp','')}: {r.get('fixes','')}" for r in au["roadmap"])
    bl = "\n".join(f"- {b}" for b in au["bottlenecks"])
    return f"""# Discovery — {au['client']} / {au['first_build'] or '[[EMPLOYEE]]'}

> **Seeded from the AI Audit ({today}).** The Audit already diagnosed the bottleneck + the first build — this is the discovery doc, ~80% pre-filled. Complete the [[ ]] fields on the discovery/build call. Agenda: `processes/discovery-to-48h-build.md`.

## From the Audit (pre-filled)
- **Vertical:** {au['vertical'] or '[[ ]]'}
- **Diagnosed headline:** {au['headline'] or '[[ ]]'}
- **The leak (quantified):** {au['bigNum'] or '[[ ]]'}
- **Bottlenecks found:**
{bl or '- [[ ]]'}
- **First build (the 48-hour win):** **{au['first_build'] or '[[ ]]'}** — {au['first_desc'] or '[[ ]]'}
- **Roadmap after #1:**
{rm or '- [[ ]]'}

## 1. The job (what the employee does first)
{au['first_build'] or '[[The one job, precisely.]]'} — confirm scope on the call. · **Employee type:** [[voice / text-intake / scheduling / drafting / Q&A / data-ops / outbound]]

## 2. The trigger
[[What kicks the job off — inbound call, email/web-form, calendar time, CRM event.]]

## 3. The inputs + decision logic
- **Inputs the employee needs:** [[ ]]
- **The rules / fields / criteria it applies:** [[ ]]

## 4. The output / action
[[What it produces or does — book, draft, reply, log, route, escalate.]]

## 5. The gated actions (approval line)
[[Which outputs are human-approved vs. autonomous — the per-engagement gate.]]

## 6. The systems (read/write)
- Client tools it must touch (CRM/field software, calendar, phone, email): [[ confirm on the call ]]

## 7. Success criteria (what the eval measures)
[[The measurable outcome — e.g. % of calls answered, time-to-quote. Set with the client.]]
"""


SCAFFOLD_NOTES = """# Scaffold notes — what's done vs. what's left

This engagement was **scaffolded from the Audit** by `runtime/scaffold_engagement.py`. Roughly 80% of the setup is done; the remaining 20% is the part that *can't* be 1-clicked — and that part is the moat.

## ✅ Done by the scaffolder (the "1-click")
- Client folder cloned from `_yourco-template` (discovery/build/eval/go-live/cost docs, client-console, demo-kit).
- `01_discovery.md` pre-filled from the Audit diagnosis (bottlenecks, the first build, the roadmap).

## 🔧 Kimi finishes (human + build — NOT 1-clickable, by design)
- **Integration** into the client's actual tools/tenant (their CRM, calendar, phone, email) — every client is different.
- **Eval** against *their* success criteria — the harness that proves it works before it goes live.
- **The approval gate** — what's human-approved vs. autonomous, per this engagement.
- **The 48-hour build + go-live** — `processes/discovery-to-48h-build.md`.
- Provisioning (Janice): tenant access + the employee's mailbox.

> The scaffolder gets you to a running start; reliability is still earned per client. That's intentional — the part we *don't* automate is exactly what clients pay yourco to own.
"""


if __name__ == "__main__":
    a = sys.argv[1:]
    au = load_audit(a)
    if not au["client"]:
        print(__doc__); sys.exit(1)
    slug = _slug(au["client"])
    target = os.path.join(REPO, "clients", slug)
    commit = "--commit" in a
    print(f"Client: {au['client']}  → clients/{slug}/")
    print(f"First build: {au['first_build'] or '(none given)'} · vertical: {au['vertical'] or '(none)'}")
    if os.path.exists(target):
        print(f"✗ clients/{slug}/ already exists — refusing to overwrite. Pick a different name or remove it.")
        sys.exit(1)
    if not commit:
        print("\nDRY RUN — would:")
        print(f"  • clone clients/_yourco-template/ → clients/{slug}/")
        print(f"  • pre-fill {slug}/01_discovery.md from the Audit")
        print(f"  • write {slug}/SCAFFOLD-NOTES.md (what's left for Kimi)")
        print("\n(re-run with --commit to create it. Then Kimi finishes integration + eval + the build.)")
        sys.exit(0)
    shutil.copytree(TEMPLATE, target)
    open(os.path.join(target, "01_discovery.md"), "w").write(discovery_seed(au))
    open(os.path.join(target, "SCAFFOLD-NOTES.md"), "w").write(SCAFFOLD_NOTES)
    print(f"\n✓ Scaffolded clients/{slug}/ (discovery pre-filled). Next: Janice provisions → Kimi builds the first employee.")
    print("  Reliability (integration + eval + approval) is Kimi's human+build work — see SCAFFOLD-NOTES.md.")
