"""Shared kit for the pre-build verticals.

Seventy-five industry builds, one implementation of the honesty rules, the
autonomy matrix, the approval gate, the eval harness and the ROI panel. Each
vertical supplies only its domain rules. (It said "ten" until 2026-08-24, which
was true when written and had been wrong for sixty-five builds.)

The 76th, `property-management/`, does NOT use this kit: it was built inside
`offerings/` before the kit existed and carries its own honesty layer, money
rail and human queue. That is a real fork of the moat layer — worth folding in
if anyone touches either side, and worth knowing about if you change a rule here
and expect it to reach every build.

Deliberate deviation from each BUILD.md's "self-contained" instruction: seventy-five
copies of the honesty engine would drift, which is the exact failure that
`CLAUDE.md` §change-one-sweep-all exists to stop. Self-containment here means
"the vertical's folder plus this kit" — still stdlib only, still no network.
"""
from . import store, moat, serve  # noqa: F401
