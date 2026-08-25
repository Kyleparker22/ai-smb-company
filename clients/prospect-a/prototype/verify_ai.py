#!/usr/bin/env python3
"""
yourco · AI Verification layer — Prospect A Roofing

The moat. The rule-based engine (storm_poc.py) checks that sources agree and
magnitudes clear a threshold. This layer has the AI actually READ the report
text — spotter remarks, measured-vs-estimated, who reported it — and judge:

  1. Is this real enough to send roofers?  (don't waste their time)
  2. Is it claim-grade?  (will the storm hold up when the homeowner files?)

Why it matters, proven on real data: the rule engine flags "Palm Beach 1.00\"
hail HIGH", but the only hail report is one PUBLIC estimate that says "pea to
quarter size" — the 1.00" number overstates it. An AI reading the remark catches
that; a threshold check doesn't. Insurance uses MEASURED airport (ASOS/AWOS)
data — this layer separates that from "someone posted hail on social media."

SAFETY / cost: off unless ANTHROPIC_API_KEY is set (like the other adapters).
The engine never depends on it — this enriches, it doesn't gate the pull.
Uses the official Anthropic SDK. Default model claude-opus-5; for production
volume set VERIFY_MODEL=claude-sonnet-5 (or claude-haiku-4-5) — plenty for
reading a few report remarks, and far cheaper (see cost.md).

    pip install anthropic
    export ANTHROPIC_API_KEY=...           # or add to .env
    python3 storm_poc.py && python3 verify_ai.py

Alternatively this same rubric runs as a runtime `claude -p` step (the yourco
loop pattern) with no API key — the runtime agent reads last_run.json directly.
"""
import json, os, sys

MODEL = os.environ.get("VERIFY_MODEL", "claude-opus-5")

RUBRIC = """You are yourco's storm-verification analyst for a Florida roofing company (Nick's).
You read the raw weather reports behind a candidate storm and decide two things:
 (1) DISPATCH — is this real and strong enough to send door-knocking crews? (don't waste their time on thin/false reports)
 (2) CLAIM-GRADE — would this storm hold up as documentation when a homeowner files an insurance claim?

How to weigh the evidence (this is the whole job — read the remarks, don't just trust the numbers):
- MEASURED beats ESTIMATED. Airport/mesonet instruments (ASOS, AWOS, Mesonet, Buoy) are the insurance gold standard. "Public"/"Broadcast Media"/"social media" reports are estimates — treat as weak on their own.
- Read the remark against the number. If a report is logged as 1.00" hail but the remark says "pea to quarter size", the number OVERSTATES it — downgrade.
- Corroboration raises confidence: multiple independent measured reports, or a ground report + an official NWS warning.
- Contradiction lowers it: one report says 1", another says pea-sized → flag it.
- Nick's thresholds: hail > 0.75", wind >= 55 mph, or any tornado. A single estimated report barely at threshold is NOT a confident dispatch.

Return your verdict. Be skeptical — a wasted crew trip and a bad claim both cost Nick more than a missed marginal storm."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "dispatch": {"type": "string", "enum": ["GO", "HOLD", "REJECT"],
                     "description": "GO = send crews; HOLD = wait for more reports; REJECT = not worth it / likely overstated"},
        "confidence": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
        "claim_grade": {"type": "boolean", "description": "true only if there is MEASURED official data that would support an insurance claim"},
        "verified_hazard": {"type": "string", "description": "the hazard actually supported by evidence, e.g. 'WIND 60mph (measured, ASOS)' — may differ from the flagged hazard"},
        "reasoning": {"type": "string", "description": "1-2 sentences, plain English, citing the evidence"},
        "red_flags": {"type": "array", "items": {"type": "string"}},
        "claim_packet": {"type": "string", "description": "if claim_grade, an insurance-ready evidence summary: date, county, peak measured value, the named official stations/reports; else empty string"},
    },
    "required": ["dispatch", "confidence", "claim_grade", "verified_hazard", "reasoning", "red_flags", "claim_packet"],
}


def evidence_text(v):
    lines = [f"Candidate: {v['county']} County, FL · {v['date']} · flagged {'/'.join(filter(None,[('HAIL %.2f\"'%v['max_hail_in']) if v.get('max_hail_in') else '', ('WIND %.0fmph'%v['max_wind_mph']) if v.get('max_wind_mph') else '', 'TORNADO' if v.get('tornado') else '']))} · rule-engine confidence {v['confidence']} · sources: {', '.join(v.get('sources_hit',[]))}",
             "Raw reports:"]
    for e in v.get("evidence", []):
        q = {"M": "MEASURED", "E": "ESTIMATED"}.get((e.get("qualifier") or "").upper(), e.get("qualifier") or "unspecified")
        mag = f"{e['value']}" if e.get("value") is not None else "no measured value"
        lines.append(f"  - [{e.get('src')}] {(e.get('time') or '')[11:16]} {e['hazard']} {mag} | {q} | reporter: {e.get('reporter')} | remark: {e.get('remark') or '(none)'}")
    return "\n".join(lines)


def main():
    try:
        import anthropic
    except ImportError:
        sys.exit("AI verification is OFF — `pip install anthropic` and set ANTHROPIC_API_KEY to enable. (The engine runs fine without it.)")
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.path.exists(".env")):
        sys.exit("AI verification is OFF — set ANTHROPIC_API_KEY (or add to .env). The engine runs fine without it.")

    run = json.load(open("last_run.json"))
    rel = [v for v in run["verified"] if v["roofing_relevant"]]
    if not rel:
        sys.exit("No roofing-relevant storms in last_run.json.")

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    out = []
    print(f"AI-verifying {len(rel)} storms with {MODEL} …\n")
    for v in rel:
        resp = client.messages.parse(
            model=MODEL, max_tokens=1200,
            thinking={"type": "adaptive"},
            system=RUBRIC,
            output_format={"type": "json_schema", "schema": SCHEMA},
            messages=[{"role": "user", "content": evidence_text(v)}],
        )
        verdict = resp.parsed_output
        out.append({"county": v["county"], "date": v["date"], **verdict})
        flags = ("  ⚠ " + "; ".join(verdict["red_flags"])) if verdict["red_flags"] else ""
        print(f"{verdict['dispatch']:6} {verdict['confidence']:6} claim={'Y' if verdict['claim_grade'] else 'n'}  "
              f"{v['county']} {v['date']} — {verdict['verified_hazard']}\n   {verdict['reasoning']}{flags}\n")

    json.dump(out, open("verified_ai.json", "w"), indent=2)
    go = sum(1 for x in out if x["dispatch"] == "GO")
    print(f"→ {go}/{len(out)} cleared for dispatch. Full verdicts + claim packets -> verified_ai.json")


if __name__ == "__main__":
    main()
