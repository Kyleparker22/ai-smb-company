# Crew OS — build 21

Pre-built vertical AI OS for commercial cleaning & janitorial companies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # 85 contracts, 36 crew, inspections, night reports
python3 test_crew_os.py    # 30 assertions
```

Launch name **`prebuild-crew-os`** (port 8841, 127.0.0.1 only).

## What it is

"Northstar Building Services" — $5.5M janitorial. Three modules: **night-report triage**,
**coverage board**, **inspection evidence**.

## The refusals it is organised around

**No access code, key, or combo ever moves through this system.** A "text me the lockbox combo"
request is refused with the rule stated — a supervisor handles it by voice, on the client's own
channel. One leaked thread is a breach. `share_access_info` is R0.

**A security incident is closed by a human or not at all.** Unlocked doors, alarms, strangers,
broken glass, missing valuables — each escalates at R2 immediately; software attempting to close
one is refused. Eval costly class = missed security incident (*HOW A JANITORIAL COMPANY LOSES A
CLIENT AND MEETS ITS INSURER*), recall 1.0.

**"Cleaned per spec" needs an inspection record inside 14 days.** With one, the complaint reply
cites it; without one, the honest reply *admits the gap and books an inspection* — arguing without
evidence is refused, structurally.

**Access is never improvised.** The coverage board proposes only crew with recorded access to the
building; the keyless are blocked with the reason named.

## 10-minute demo

Board → Night reports (unlocked door → escalated, try closing as software — refused; lockbox ask →
refused; complaint on the uninspected contract → the honest draft) → Coverage (keyed candidates
only) → ROI → Trust.

## What this does not do yet

- **No integrations.** Timekeeping (Swept/Connecteam-class), inspection apps, SMS are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the security and access stops exactly as they are.
- **Nothing is sent.**
