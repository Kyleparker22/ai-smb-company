# Insurance — plan and status

> Not licensed advice. A broker who specialises in tech / professional services confirms limits.

| # | Policy | Why it matters here | Status |
|---|---|---|---|
| 1 | Technology E&O / Professional Liability (often bundled with Cyber) | Your agents *act*. This is the core policy. | ☐ not bound |
| 2 | General Liability | Standard, cheap, often demanded by clients | ☐ not bound |
| 3 | Cyber | You hold client data | ☐ not bound |
| 4 | Workers' comp | Required in most states once you have employees | ☐ n/a |

⚠️ **Coverage must be in force before your first client goes live** if your engagement agreement
represents that you carry it. Check §13 of `processes/contracts/engagement-agreement.md` *before* you
sign anyone — a representation with no policy behind it is the exposure.

A watchdog in `runtime/consistency-check.py` warns if a client reaches signed/live while this file
still says nothing is bound. Record renewal dates here once you bind; premiums go to `finance/`.
