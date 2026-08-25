#!/usr/bin/env python3
"""yourco — agent-registry reconciliation watchdog ("Vanta for our own agents").

Diffs the LIVE runtime against the sanctioned baseline in runtime/agent-registry.json and
reports drift: a new/removed prompt, timer, or service; a widened/loosened connector scope;
an unknown commit author. Read-only — it DETECTS and ALERTS; the Founder alone sanctions (by editing
the registry). Owned by Rafi (NIST Detect). Decision: decisions/2026-06-22_agent-registry-governance-watchdog.md.

Modes:
  (default)      repo-declared check — diffs runtime/prompts, runtime/systemd, the settings
                 reference, and recent git authors against the registry. Runs anywhere (incl. Cowork).
  --live         ALSO check host state: installed systemd units, the ACTIVE ~/.claude/settings.json,
                 and crontab. Skips gracefully whatever isn't available (e.g. off-host).
  --self-check   print registry summary and exit (no diff).
  --quiet        only print on drift (for the scheduled job).

Exit code: 0 = clean, 1 = drift found, 2 = config error. Writes a dated report to loops/_governance/.
This is NOT the runtime health-watchdog (runtime/prompts/watchdog.md, 'did loops fire') — that's Atlas.
"""
import os, sys, json, glob, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REGISTRY = os.path.join(HERE, "agent-registry.json")
SETTINGS_REF = os.path.join(HERE, "headless-settings.reference.json")


def _load(path):
    with open(path) as f:
        return json.load(f)


def _basenames(pattern):
    return {os.path.basename(p) for p in glob.glob(pattern)}


def _run(cmd):
    """Best-effort subprocess; returns stdout or None (never raises)."""
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def _delta(label, live, sanctioned, kind):
    """Return list of drift findings for a set comparison. kind: 'new' findings are the security
    signal (unsanctioned thing appeared); 'missing' means a sanctioned thing vanished."""
    findings = []
    for x in sorted(live - sanctioned):
        findings.append(("DRIFT", f"unsanctioned {label}: {x}"))
    for x in sorted(sanctioned - live):
        findings.append(("MISSING", f"sanctioned {label} not found: {x}"))
    return findings


def check(reg, live=False):
    findings = []

    # 1. prompts (repo-declared agent loops)
    findings += _delta("prompt", _basenames(os.path.join(HERE, "prompts", "*.md")),
                       set(reg["sanctioned_prompts"]), "prompt")
    # 2. systemd unit FILES in the repo (declared)
    findings += _delta("timer (repo)", _basenames(os.path.join(HERE, "systemd", "*.timer")),
                       set(reg["sanctioned_timers"]), "timer")
    findings += _delta("service (repo)", _basenames(os.path.join(HERE, "systemd", "*.service")),
                       set(reg["sanctioned_services"]), "service")
    # 3. connector scopes in the settings reference (widened scope = the high-value signal)
    try:
        perms = _load(SETTINGS_REF)["permissions"]
        findings += _delta("connector ALLOW (reference)", set(perms.get("allow", [])),
                           set(reg["sanctioned_connectors_allow"]), "allow")
        # a removed deny is a loosening of the gate — flag it
        for x in sorted(set(reg["sanctioned_connectors_deny"]) - set(perms.get("deny", []))):
            findings.append(("DRIFT", f"gate deny REMOVED from reference: {x}"))
    except Exception as e:
        findings.append(("SKIP", f"settings reference unreadable: {e}"))
    # 4. recent commit authors
    authors = _run(["git", "log", "-n", "200", "--format=%an"])
    if authors is not None:
        live_authors = {a.strip() for a in authors.splitlines() if a.strip()}
        for a in sorted(live_authors - set(reg["sanctioned_commit_authors"])):
            findings.append(("DRIFT", f"unsanctioned commit author: {a}"))
    else:
        findings.append(("SKIP", "git author check unavailable"))

    # 5. LIVE host checks (only with --live; skip gracefully off-host)
    if live:
        sanctioned_units = set(reg["sanctioned_timers"]) | set(reg["sanctioned_services"])
        # Known-good non-yourco admin units on this host (tailscaled, etc.) — sanctioned once by the Founder.
        allow_system = set(reg.get("sanctioned_system_units", []))
        # (a) the yourco-* installed units (matches the naming convention)
        units = _run(["systemctl", "list-unit-files", "yourco-*", "--no-legend"])
        if units is not None:
            live_units = {ln.split()[0] for ln in units.splitlines() if ln.split()}
            for u in sorted(live_units - sanctioned_units):
                findings.append(("DRIFT", f"unsanctioned installed unit (host): {u}"))
        else:
            findings.append(("SKIP", "host systemd check unavailable (not on the VPS?)"))
        # (b) ANY admin-installed unit dropped into /etc/systemd/system — the earlier check only
        # matched yourco-*, so a differently-named rogue unit (stormverified-alerts.service, a
        # capital-I variant, backup-sync.timer) was invisible. Scan the dir directly; enable-symlinks
        # live in *.wants/ subdirs so the top-level glob catches real admin-installed units.
        etc = "/etc/systemd/system"
        if os.path.isdir(etc):
            try:
                admin_units = {f for f in os.listdir(etc) if f.endswith((".service", ".timer"))}
            except OSError:
                admin_units = set()
            for u in sorted(admin_units - sanctioned_units - allow_system):
                findings.append(("DRIFT", f"unsanctioned admin unit in {etc}: {u} "
                                          f"(sanction in agent-registry.json or remove)"))
        else:
            findings.append(("SKIP", f"{etc} not present (off-host)"))
        active = os.path.expanduser("~/.claude/settings.json")
        if os.path.exists(active):
            try:
                p = _load(active)["permissions"]
                for x in sorted(set(p.get("allow", [])) - set(reg["sanctioned_connectors_allow"])):
                    findings.append(("DRIFT", f"ACTIVE gate allows unsanctioned scope: {x}"))
                for x in sorted(set(reg["sanctioned_connectors_deny"]) - set(p.get("deny", []))):
                    findings.append(("DRIFT", f"ACTIVE gate deny REMOVED: {x}"))
            except Exception as e:
                findings.append(("SKIP", f"active settings.json unreadable: {e}"))
        else:
            findings.append(("SKIP", "active ~/.claude/settings.json not present (off-host)"))
        cron = _run(["crontab", "-l"])
        if cron:
            bad = [ln for ln in cron.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            if bad:
                findings.append(("DRIFT", f"unexpected crontab entries: {len(bad)} (review `crontab -l`)"))
    return findings


def write_report(findings, drift):
    day = datetime.date.today().isoformat()
    outdir = os.path.join(REPO, "loops", "_governance")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{day}.md")
    lines = [f"# Agent-registry drift check — {day}", "",
             f"**Result:** {'⚠️ DRIFT' if drift else '✅ clean'} · owned by Rafi · "
             f"baseline: `runtime/agent-registry.json`", ""]
    if findings:
        lines.append("| level | finding |"); lines.append("| --- | --- |")
        for lvl, msg in findings:
            lines.append(f"| {lvl} | {msg} |")
    else:
        lines.append("No drift. Live runtime matches the sanctioned registry.")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def self_check(reg):
    print("yourco agent-registry watchdog — registry summary")
    for k in ("sanctioned_prompts", "sanctioned_timers", "sanctioned_services",
              "sanctioned_slack_agent_channels", "sanctioned_connectors_allow",
              "sanctioned_connectors_deny", "sanctioned_commit_authors"):
        print(f"  {k:32} {len(reg.get(k, []))}")
    print(f"  registry updated: {reg.get('updated')} · owner: {reg.get('owner')}")
    return 0


def main(argv):
    if not os.path.exists(REGISTRY):
        print(f"[agent-registry] missing {REGISTRY}", file=sys.stderr); return 2
    try:
        reg = _load(REGISTRY)
    except (json.JSONDecodeError, OSError) as e:
        # Config error must be exit 2 (documented), not exit 1 (drift) — a corrupt registry is
        # not "drift found", and crashing uncaught would also write no report.
        print(f"[agent-registry] registry unreadable/malformed: {e}", file=sys.stderr); return 2
    if "--self-check" in argv:
        return self_check(reg)
    try:
        findings = check(reg, live="--live" in argv)
    except KeyError as e:
        print(f"[agent-registry] registry missing required key: {e}", file=sys.stderr); return 2
    # MISSING (a sanctioned prompt/timer/service/unit vanished) is drift too — otherwise deleting
    # the governance timer or the health watchdog itself would exit 0 and report "✅ clean".
    drift = any(lvl in ("DRIFT", "MISSING") for lvl, _ in findings)
    path = write_report(findings, drift)
    quiet = "--quiet" in argv
    if drift or not quiet:
        print(f"agent-registry drift check → {'⚠️ DRIFT' if drift else '✅ clean'}  ({path})")
        for lvl, msg in findings:
            print(f"  [{lvl}] {msg}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
