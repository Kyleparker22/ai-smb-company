#!/usr/bin/env python3
"""Sample Client agent — test suite (the proposal's "ships with a test suite" promise, made real).

Tests the parts that MUST be right and must never depend on AI: the deposit math, the duplicate guard,
the Installation filter, material routing, and graceful handling of missing data. No network, no Claude.

Run:  python3 clients/sample-client/prototype/test_agent.py
"""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent

# Force the deterministic, no-network path for the whole suite (the docstring's "no Claude" promise).
# With no key, parse_proposal uses _regex_parse and draft() returns its template string.
agent._KEY = ""


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a)


def capture(fn, *a):
    """Run fn, returning the text it printed (so tests can assert on the flow, not just side effects)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*a)
    return buf.getvalue()


PASS, FAIL = 0, 0


def check(name, got, want):
    global PASS, FAIL
    ok = got == want
    PASS += ok; FAIL += (not ok)
    print(f"  {'✅' if ok else '❌'} {name}" + ("" if ok else f"   got {got!r}, want {want!r}"))


print("Sample Client agent — test suite\n" + "-" * 60)

# 1–3 · deposit tiers (the money math)
check("small tier: $8,000 → 50% = $4,000", agent.deposit_for(8000)[0], 4000.0)
check("mid tier: $48,500 → 35% = $16,975", agent.deposit_for(48500)[0], 16975.0)
check("large tier: $200,000 → 25% = $50,000", agent.deposit_for(200000)[0], 50000.0)

# 4–5 · tier boundaries (off-by-one safety)
check("boundary: exactly $10,000 is small (50%)", agent.deposit_for(10000)[1], 0.50)
check("boundary: $10,000.01 is mid (35%)", agent.deposit_for(10000.01)[1], 0.35)

# 6–7 · material routing
check("pallets route to job site", agent.route_material("Belgard Holland pavers (pallets)"), "job site")
check("boxed fixtures route to shop", agent.route_material("Low-voltage lighting fixtures (boxed)"), "shop")

# 8 · Installation filter (non-installation actually STOPs — assert the flow, not just _SEEN,
#     which run() sets unconditionally before the filter and so can't prove the filter worked).
agent._SEEN.clear()
out = capture(agent.run, "Division: Maintenance\nProposal total: $2,000\n", "MNT-1")
check("non-installation proposal STOPs before drafting", ("STOP" in out) and ("CLIENT DEPOSIT" not in out), True)

# 8b · regression guard for the no-key fallback: division comes from the INPUT, not a hardcoded
#      'Installation' (which used to make the filter a no-op and every proposal parse as Chen).
check("fallback parses division from the proposal text",
      agent._regex_parse("Division: Maintenance\nProposal total: $2,000\n")["division"].lower(), "maintenance")
check("fallback parses the real client, not hardcoded Chen",
      agent._regex_parse("Division: Installation\nClient: Jane Doe\nProposal total: $9,000\n")["client"], "Jane Doe")

# 9 · duplicate guard (one signed proposal never double-sends)
agent._SEEN.clear(); agent._SEEN.add("SC-2026-0488")
before = len(agent._SEEN)
quiet(agent.run, "Division: Installation\n", "SC-2026-0488")  # already seen
check("duplicate proposal is ignored (no double-send)", len(agent._SEEN), before)

# 10 · missing calendar dates don't crash — the parse returns the window keys (possibly empty),
#      and a real window line is parsed into start/end.
p = agent._regex_parse("Division: Installation\nProposal total: $12,000\n")
check("missing-window parse doesn't crash and keeps the keys", "window_start" in p and "window_end" in p, True)
p2 = agent._regex_parse("Division: Installation\nProject window: 2026-07-06 to 2026-07-17\nProposal total: $1\n")
check("a real window line parses into start → end", (p2["window_start"], p2["window_end"]), ("2026-07-06", "2026-07-17"))

print("-" * 60)
print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
