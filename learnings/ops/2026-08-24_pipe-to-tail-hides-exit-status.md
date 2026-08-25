2026-08-24 — `cmd | tail` reports tail's exit status, so a failed check reads as a pass

Source: two failures in one session (2026-08-24), same shape both times.
Pattern: A shell pipeline exits with the status of its LAST stage. Every `python3 runtime/check.py | tail -4`
or `bash runtime/commit-scoped.sh ... | tail -5` therefore exits 0 whenever `tail` succeeds — which is
always — no matter what happened upstream. Both bites today:
  1. `consistency-check.py` hit a SyntaxError from an edit of mine and stopped writing its artifact. The
     command still exited 0, so I read the PREVIOUS run's artifact and believed the checks were green for
     several minutes.
  2. `commit-scoped.sh | tail -5` returned exit 0 while the two target files were still modified. I read
     that as a stuck commit and said so; in fact the exit code carried no information either way. The
     commit had landed.
Implication: The visible tail output and the exit code are independent. **Never conclude "it passed"
from an exit code on a piped command, and never conclude "it failed" either.** Two habits fix it:
  - Verify the EFFECT, not the invocation — `git log`/`git status` for a commit, the dated artifact's own
    pass/fail counts for a check, the file's content for a write.
  - When the status matters, drop the pipe (`python3 runtime/consistency-check.py; echo "rc=$?"`) or set
    `set -o pipefail` so the pipeline inherits the first failure.
Correction (same day, found while verifying): an earlier draft of this entry claimed
`consistency-check.py` "exits 0 on a failed run by design." **That is wrong.** Line 2340 is
`sys.exit(1 if drift else 0)`, and WARNINGS count as drift — so a run with 77/77 invariants passing and
3 standing ⚠️ advisories exits **1**. The exit code there is real; the pipe is what destroyed it. Note
the corollary, which is the more useful half: **rc=1 from that script does not mean your change broke
something** — it usually means the three long-standing advisories (Reddit key, `data.json` freshness,
OtherVenture tracker) are still open. Read the artifact's own pass/fail counts to tell those apart.
The artifact is the source of truth, not the command.
Audience: every agent that runs a verification command and reports the result to the Founder

Triggers: consistency-check, commit-scoped, verification, exit code, pipefail, tail, running tests, reporting green, git commit
