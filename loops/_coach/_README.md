# _coach — practice records

One append-only JSONL per role (`connector.jsonl`, `advisor.jsonl`), written by `crm/coach.py record`.
Each line is one drill attempt: who, which drill, an agent's verdict (`solid|shaky|missed`), and one
line of why.

**These are individual performance records about named people, and they are committed to the repo.**
That is a deliberate choice, consistent with the CRM's own contact and deal data living here — but it
is worth knowing rather than discovering. Two consequences:

- Write the `note` as **what the answer did**, not as a judgement of the person. "Quoted a price"
  is a record; "doesn't listen" is not, and does not belong in a file that persists.
- If a role ever includes someone outside yourco whose practice record should not be in the company
  repo, that is a decision to make **before** the first `record`, not after.

**Read by** `crm/coach.py growth` and `session`. **Nothing else writes here.**

Growth areas are computed only from these records and from drill coverage — never from field results,
because at n=0 clients there are none. `coach.py` states that limit in every `growth` and `session`
response under `cannotSee`.
