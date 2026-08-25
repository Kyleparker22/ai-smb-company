#!/usr/bin/env python3
"""receipts/assemble.py — evidence-packet skeleton assembler (stub; stdlib only).

Walks this engagement's record locations (ledger/*.jsonl + audit-trail/),
selects records responsive to a date range (+ optional keyword), orders them
chronologically, and emits a packet SKELETON from receipts/packet-template.md.

Integrity posture (see receipts/README.md — the hard lines):
  * READ-ONLY over the record: this script never writes, edits, or deletes a
    source record. Append-only is enforced at capture; assembly only views.
  * NO curation: filtering is by responsiveness (dates/keyword) only — never
    by favorability. Every matching record lands in the exhibits table,
    including entries unhelpful to the client's position.
  * GAPS AS GAPS: months in range with no ledger file, unreadable files, and
    unparseable lines are REPORTED in the gap section, never papered over or
    reconstructed.
  * The narrative summary (§1) is left as a placeholder — a labeled
    human/LLM pass fills it AFTER assembly, from the exhibits only. This
    script never paraphrases a record.

Usage:
  python3 receipts/assemble.py --from 2026-09-01 --to 2026-09-30 \
      [--match "keyword"] [--out receipts/packets/]

Run from the engagement root (the folder containing ledger/ and receipts/).
"""

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# Record locations, relative to the engagement root. Extend per engagement
# overlay if a module writes its trail elsewhere — extend, never replace:
# dropping a location from assembly would be selective assembly.
RECORD_LOCATIONS = {
    "ledger": Path("ledger"),          # append-only JSONL, one file per month (ledger/_SCHEMA.md)
    "audit-trail": Path("audit-trail"),  # per-module audit trail exports, if present
}


def parse_args(argv):
    p = argparse.ArgumentParser(description="Assemble an evidence-packet skeleton.")
    p.add_argument("--from", dest="date_from", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--to", dest="date_to", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--match", default=None,
                   help="optional case-insensitive substring; applied to whole record text "
                        "(responsiveness filter only — never favorability)")
    p.add_argument("--out", default="receipts/packets", help="output directory")
    return p.parse_args(argv)


def record_ts(rec):
    """Best-effort ISO timestamp from a record; None if absent/unparseable."""
    ts = rec.get("ts") or rec.get("timestamp")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts))
    except ValueError:
        return None


def in_range(dt, d_from, d_to):
    return dt is not None and d_from <= dt.date() <= d_to


def months_in_range(d_from, d_to):
    y, m = d_from.year, d_from.month
    while (y, m) <= (d_to.year, d_to.month):
        yield f"{y:04d}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def collect(root, d_from, d_to, match):
    """Walk record locations. Returns (records, gaps). Read-only."""
    records, gaps = [], []

    # --- ledger/*.jsonl (monthly files) ---
    ledger_dir = root / RECORD_LOCATIONS["ledger"]
    for month in months_in_range(d_from, d_to):
        f = ledger_dir / f"{month}.jsonl"
        if not f.is_file():
            gaps.append((f"ledger file for {month}", "no ledger file present for this month", month))
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except OSError as e:
            gaps.append((f"ledger file for {month}", f"file unreadable ({e.__class__.__name__})", month))
            continue
        for n, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                gaps.append((f"{f.name} line {n}", "unparseable ledger line (reported, not repaired)", month))
                continue
            dt = record_ts(rec)
            if dt is None:
                gaps.append((f"{f.name} line {n}", "record lacks a parseable timestamp", month))
                continue
            if in_range(dt, d_from, d_to) and (not match or match.lower() in line.lower()):
                records.append({
                    "ts": dt,
                    "channel": rec.get("record_type", "ledger"),
                    "id": rec.get("id", f"{f.name}:{n}"),
                    "entry": line.strip(),   # verbatim — never paraphrased
                    "source": str(f.relative_to(root)),
                })

    # --- audit-trail/ (optional; any files, matched by mtime-agnostic content walk) ---
    trail_dir = root / RECORD_LOCATIONS["audit-trail"]
    if trail_dir.is_dir():
        for f in sorted(p for p in trail_dir.rglob("*") if p.is_file()):
            if f.suffix == ".jsonl":
                # same treatment as ledger files, without the monthly-gap check
                try:
                    lines = f.read_text(encoding="utf-8").splitlines()
                except OSError as e:
                    gaps.append((str(f.relative_to(root)), f"file unreadable ({e.__class__.__name__})", "-"))
                    continue
                for n, line in enumerate(lines, 1):
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        gaps.append((f"{f.name} line {n}", "unparseable audit-trail line", "-"))
                        continue
                    dt = record_ts(rec)
                    if dt and in_range(dt, d_from, d_to) and (not match or match.lower() in line.lower()):
                        records.append({
                            "ts": dt, "channel": rec.get("record_type", "audit-trail"),
                            "id": rec.get("id", f"{f.name}:{n}"), "entry": line.strip(),
                            "source": str(f.relative_to(root)),
                        })
            # non-JSONL artifacts are listed by reference for the human pass
    else:
        gaps.append(("audit-trail/", "no audit-trail directory in this engagement (ledger-only assembly)", "-"))

    records.sort(key=lambda r: r["ts"])
    return records, gaps


def md_escape(s, limit=400):
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= limit else s[:limit] + " …[truncated for table; full record at source]"


def render(records, gaps, args, now):
    lines = [
        "# [[CLIENT BRAND]] — Record of Interactions",
        f"**Packet assembled:** {now}",
        "**Concerning:** [[customer / job / dispute reference — fill from the request]]"
        + (f" (match filter: `{args.match}`)" if args.match else ""),
        f"**Period covered:** {args.date_from} – {args.date_to}",
        f"**Assembly ID:** pkt-{now.replace(':', '').replace('-', '')[:15]} · "
        f"**Records responsive:** {len(records)} · **Gaps identified:** {len(gaps)}",
        "",
        "> This packet presents the complete responsive record for the period and matter above, "
        "in chronological order, exactly as captured at the time of each event. Summary text is "
        "labeled as summary; record entries are verbatim. Gaps in the record are reported as gaps.",
        "",
        "---",
        "",
        "## 1. Chain of events (narrative summary)",
        "*Labeled summary — TO BE WRITTEN in the human/LLM pass, from and only from the exhibits "
        "in §2. Every sentence traceable to an exhibit number. No merit opinions.*",
        "",
        "[[NARRATIVE PLACEHOLDER — assembly stub does not paraphrase records]]",
        "",
        "## 2. The record (exhibits, chronological)",
        "*Each entry verbatim as captured. Includes ALL responsive entries — this packet does not curate.*",
        "",
        "| # | Timestamp (captured) | Channel / type | Record ID | Entry (verbatim) | Source |",
        "|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(records, 1):
        lines.append(f"| {i} | {r['ts'].isoformat()} | {md_escape(r['channel'])} | "
                     f"{md_escape(r['id'])} | {md_escape(r['entry'])} | {md_escape(r['source'])} |")
    if not records:
        lines.append("| – | – | – | – | *No responsive records in the system for this period "
                     "and filter.* | – |")

    lines += [
        "",
        "## 3. Gaps reported as gaps",
        "*Nothing in this section is reconstructed. Add here any interaction the requester "
        "references for which the system holds no record.*",
        "",
        "| Referenced interaction / location | Why no record | Period affected |",
        "|---|---|---|",
    ]
    for what, why, period in gaps:
        lines.append(f"| {md_escape(what)} | {md_escape(why)} | {period} |")
    if not gaps:
        lines.append("| – | No gaps identified — the record above is continuous for the "
                     "responsive period. | – |")

    lines += [
        "",
        "## 4. Integrity note (how these records are kept)",
        "Records in this packet were captured automatically at the time of each event by "
        "[[CLIENT BRAND]]'s operations system and are maintained append-only: entries are never "
        "edited or deleted within the retention window; corrections appear as new entries "
        "referencing the original. Timestamps are applied at capture. Records the system did not "
        "capture are reported in §3 as gaps and are never reconstructed. Retention window: "
        "[[per engagement agreement]]. These records belong to [[CLIENT LEGAL NAME]]. This packet "
        "organizes existing records; it makes no legal claims and contains no legal advice.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    args = parse_args(argv)
    try:
        d_from = date.fromisoformat(args.date_from)
        d_to = date.fromisoformat(args.date_to)
    except ValueError:
        sys.exit("error: --from/--to must be YYYY-MM-DD")
    if d_from > d_to:
        sys.exit("error: --from is after --to")

    root = Path.cwd()
    if not (root / "receipts").is_dir():
        sys.exit("error: run from the engagement root (the folder containing receipts/ and ledger/)")

    records, gaps = collect(root, d_from, d_to, args.match)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)  # only write outside the record locations
    out = out_dir / f"packet-skeleton_{args.date_from}_to_{args.date_to}_{now[:19].replace(':', '')}.md"
    out.write_text(render(records, gaps, args, now), encoding="utf-8")

    print(f"packet skeleton: {out}")
    print(f"  responsive records: {len(records)} · gaps reported: {len(gaps)}")
    print("next: human/LLM pass fills §1 narrative from the exhibits; Kolby evals; "
          "named approver reviews before anything leaves the tenant (R1).")


if __name__ == "__main__":
    main()
