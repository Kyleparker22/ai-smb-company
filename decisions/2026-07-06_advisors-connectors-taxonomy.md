# 2026-07-06 — People taxonomy: Advisors + Connectors (CRM split, name locked everywhere)

## Decision
yourco's people are organized in the CRM as **Clients** vs **Internal Team**, and internal team has two
roles: **Advisors** (full-time yourco salespeople — run the audit-shaped sales conversation, scope the OS,
close) and **Connectors** (referral partners — make the intro, earn the recurring commission; this renames
the referral program's "sales reps" **everywhere**, external surfaces included). A person who is both a
client/prospect AND a connector gets **two cross-linked CRM profiles** — never one blended record.

## Context
the Founder asked for the contacts view to separate clients from yourco's own people, with a toggle between the
two internal roles. Four contacts (Prospect A, Sample Contact, Sample Contact, Partner B) were carrying
blended "client + connector" free-text statuses — unqueryable and drift-prone. The referral program had
also been calling connectors "sales reps," which collides with hiring actual full-time salespeople later.

## Options considered
- Full-time name: **Advisors** (chosen) · Solutions Architects · Consultants · Strategists · Closers ·
  Account Executives · Deal Leads · keep "Sales Reps".
- Connector scope: everywhere (chosen) vs CRM-internal-only (rejected — two names for one role is the
  exact cross-session drift class we keep fighting).
- Dual-role: two linked profiles (chosen) vs one record with multiple kinds (rejected — the Founder explicit).

## Why
"Advisors" matches the audit-first, trust-led sell — an SMB owner hears expert, not salesperson — and
pairs cleanly: Connectors introduce → Advisors advise → yourco builds. One name on every surface
(packet, careers, CRM, program spec) per change-one-sweep-all.

## Mechanics
- CRM schema (additive): contact `kind` = "client" (default) | "internal"; internal adds `teamRole` =
  "advisor" | "connector" and optional `linkedContactId` (set on both profiles of a dual-role person).
- Commission **tier names are unchanged** (Referrer / Senior / Partner — they name tiers, not roles).
- Internal keys/paths unchanged for compat: `repApplicants`, `repRecruiters`, `rep-intake`,
  `rep-packet.md` filenames — display labels only say Connector.
- Careers page + Connector Packet + program spec + one-pager + counsel checklist + site_intake all swept
  same-commit; consistency-check invariant guards against "sales rep" reappearing on live surfaces.

## Reversibility
Label-level: renaming again is one sweep + the invariant update. Schema-level: `kind`/`teamRole` are
additive fields; removing them degrades to the old blended view without data loss.
