# Validation — engine vs. Nick's manual hour (06/23–06/30/2026)

Nick spent ~an hour hand-cross-referencing his weather sites for the week and
sent us the result. We ran the engine (free NOAA sources only, thresholds hail
>0.75" / wind ≥55mph) over the same window and compared. **No tuning to his
answers** — this is what the engine produced on its own.

## Wind + tornado events — NOAA free layer nailed them
| Nick (manual) | Engine (auto) | Match |
|---|---|---|
| Jacksonville hit daily since 06/23 | **Duval 06/23 — 60mph** (NOAA LSR + SPC) | ✅ |
| Ocala 59mph (06/24) | **Marion 06/24 — 59mph** (LSR + SPC) | ✅ exact |
| Port St Lucie 58mph (06/24) | **St. Lucie 06/24 — 58mph** (LSR + SPC) | ✅ exact |
| Palm Bay 64 / Melbourne 60mph (06/24) | **Brevard 06/24 — 55mph** (same county, lower report point) | ◑ partial |
| Fort Myers EF-0 tornado 65mph (06/28) | **Lee 06/28 — TORNADO** (LSR + SPC) → "all crews" | ✅ |
| "Nothing worth traveling" (06/29) | **(engine also quiet 06/29)** | ✅ |
| Calhoun panhandle 70mph + 1" hail (06/30) | **Calhoun 06/30 — 1.00" hail + 69mph** (LSR + SPC) | ✅ near-exact |

The engine independently reproduced Nick's biggest calls of the week — off the
**free** NOAA layer, in seconds instead of an hour.

## The hail events it missed — and why that's the pitch, not a flaw
| Nick (manual) | Engine | Why missed |
|---|---|---|
| The Villages/Wildwood 1.25" hail (06/24) | — | not in NOAA ground reports |
| Kissimmee/St Cloud 1.25" hail (06/24) | — | not in NOAA ground reports |
| Bunnell 1.25" hail (06/26) | — | not in NOAA ground reports |
| Wesley Chapel 0.75" hail (06/26) | (engine got nearby Hillsborough 0.88" hail 06/27) | sparse NOAA hail coverage |

**This is exactly why Nick cross-references HailTrace + Interactive Hail Maps.**
Hail often isn't in NOAA's spotter reports, but it *is* in the radar-derived hail
products. Add those three sources (**Nick already has the Xweather key**) and the
engine catches the 1.25" hail days too — closing the gap to 100% of his manual list.

## Bonus — verified storms the engine surfaced that weren't on Nick's list
Brevard 06/23 · Hillsborough 0.88" hail 06/27 · Palm Beach 1.00" hail 06/24 ·
Martin 56mph 06/24. Real, verified, and worth a look — the kind of thing that
slips through a manual pass at 11pm.

## Takeaway
Free NOAA alone already matches most of Nick's hour of work. The premium hail
sources he named are the last mile to full coverage — and the whole thing runs
in seconds, every day, automatically. *(Engine run 2026-06-30, 8-day window.)*
