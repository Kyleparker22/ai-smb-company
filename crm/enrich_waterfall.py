#!/usr/bin/env python3
"""Waterfall enrichment — ranked providers, pay only on a match, verify before writing.

Clay's contribution to GTM tooling is not "enrichment" — everyone has that. It is the
**waterfall**: route each field to a ranked list of sources, stop at the first that returns
something usable, and only pay the ones that actually matched. Published coverage goes from
~20% on a single provider to 70–85% on a well-configured chain.

yourco had `/api/enrich`: one call, one source, take it or leave it. Two things were missing.

  1. RANKED FALLBACK. A single source that misses returns nothing, and the field stays empty
     forever because nobody re-runs it.
  2. A VERIFICATION GATE BEFORE WRITE. This is the half that matters more here, and the half
     Clay treats as a step rather than a principle. A CRM whose insight layer refuses to state
     what it cannot defend must not accept an unverified email into the same record — the
     moment enrichment can write a guess, every read downstream inherits the guess.

So the contract is: **propose → verify → gate → write**, and a value that fails verification
is recorded as a REFUSAL with the reason, not silently dropped. A dropped miss looks identical
to a field nobody tried; a recorded refusal tells you the chain ran and found nothing, which
is the difference between "unknown" and "unknowable from these sources".

COST. Providers are ordered cheapest-credible-first, and the chain stops on the first
verified hit — so the expensive source is only ever paid when the cheap ones genuinely failed.
Every attempt is logged with whether it was billable, because "we spent $40 on enrichment"
should be answerable per field.

REFUSAL RULES:
  · Nothing is written by this module. It returns a proposal; the caller writes.
  · A value that fails its verifier NEVER writes, however many providers agreed on it.
    Three sources returning the same malformed email is three sources being wrong together.
  · Confidence is the VERIFIER's, not the provider's. A provider's own confidence score is
    marketing.

Run:
    python3 crm/enrich_waterfall.py --company "Sample Client"
    python3 crm/enrich_waterfall.py --plan          # the chain, per field, with costs
    python3 crm/enrich_waterfall.py --json
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
LOG = os.path.join(DATA_DIR, "_enrich-log.jsonl")
TODAY = datetime.date.today()

# ---- verifiers: the gate. A provider proposes; these decide whether it may be written. ----
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[a-z]{2,}$", re.I)
ROLE_PREFIX = ("info@", "contact@", "sales@", "hello@", "admin@", "office@", "support@")
URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.I)


def verify_email(v, ctx=None):
    v = (v or "").strip().lower()
    if not EMAIL_RE.match(v):
        return False, "not a syntactically valid address"
    if v.startswith(ROLE_PREFIX):
        # Not invalid — but it is not a PERSON, and writing it into a contact's email field
        # makes the CRM believe we can reach a named human when we can only reach a mailbox.
        return False, "role mailbox, not a person — file it on the company, not the contact"
    dom = v.split("@")[-1]
    site = ((ctx or {}).get("website") or "").lower()
    if site and dom not in site and site.replace("www.", "").split("//")[-1].split("/")[0] not in dom:
        return False, f"domain {dom} does not match the company's own site"
    return True, "syntax + domain check passed"


def verify_url(v, ctx=None):
    v = (v or "").strip()
    return (True, "well-formed") if URL_RE.match(v) else (False, "not a well-formed URL")


def verify_size(v, ctx=None):
    try:
        n = int(str(v).strip())
    except Exception:
        return False, "not a whole number — size is an employee COUNT, never a band like '10-50'"
    if n <= 0 or n > 500000:
        return False, f"{n} is outside a believable employee count"
    return True, "plausible headcount"


def verify_text(v, ctx=None):
    v = (v or "").strip()
    return (True, "non-empty") if len(v) >= 2 else (False, "empty")


# ---- the chains. Cheapest-credible first; the chain stops at the first VERIFIED hit. ----
# `billable` is what we are charged when the provider RETURNS something, matched or not —
# which is why order matters and why a free source always leads where one exists.
CHAINS = {
    "website":  [("crm-self", 0.0), ("site-guess", 0.0), ("melanie-fetch", 0.01)],
    "email":    [("crm-self", 0.0), ("melanie-fetch", 0.01), ("vibe", 0.08)],
    "phone":    [("crm-self", 0.0), ("melanie-fetch", 0.01), ("vibe", 0.08)],
    "location": [("crm-self", 0.0), ("melanie-fetch", 0.01)],
    "size":     [("crm-self", 0.0), ("melanie-fetch", 0.01), ("vibe", 0.10)],
    "vertical": [("crm-self", 0.0), ("melanie-fetch", 0.01)],
}
VERIFIERS = {"email": verify_email, "website": verify_url, "size": verify_size,
             "phone": verify_text, "location": verify_text, "vertical": verify_text}


def _provider(name, field, company, ctx):
    """Ask ONE provider for ONE field. Returns (value|None, billable, note).

    Only `crm-self` and `site-guess` are implemented locally; the paid providers are declared
    but return None with a reason, because wiring a billable call behind a module that can be
    invoked from a loop is exactly how an enrichment bill arrives unannounced. They light up
    when someone deliberately wires them (`wire-credentialed-connector` skill)."""
    if name == "crm-self":
        v = (ctx or {}).get(field)
        return (v, False, "already on the record") if v else (None, False, "not on the record")
    if name == "site-guess" and field == "website":
        nm = re.sub(r"[^a-z0-9]", "", (company or "").lower())
        return (f"https://{nm}.com", False, "guessed from the company name — must still verify") if nm else (None, False, "no name")
    if name == "melanie-fetch":
        try:
            import melanie  # noqa: F401
        except Exception:
            return None, False, "brain not loaded — provider unavailable"
        return None, False, ("wired but not called from this module: melanie.enrich() writes to "
                             "the CRM, and this module is proposal-only by contract")
    return None, False, f"provider `{name}` declared but not wired (see wire-credentialed-connector)"


def enrich_field(field, company, ctx=None, chain=None):
    """Walk the chain for one field. Stops at the first value that PASSES verification."""
    chain = chain or CHAINS.get(field) or []
    verifier = VERIFIERS.get(field, verify_text)
    attempts, spent = [], 0.0
    for name, cost in chain:
        val, billable, note = _provider(name, field, company, ctx)
        if billable:
            spent += cost
        if val is None:
            attempts.append({"provider": name, "result": "no value", "note": note,
                             "billed": cost if billable else 0.0})
            continue
        ok, why = verifier(val, ctx)
        attempts.append({"provider": name, "result": "verified" if ok else "rejected",
                         "value": val, "why": why, "billed": cost if billable else 0.0})
        if ok:
            return {"field": field, "status": "verified", "value": val, "provider": name,
                    "verification": why, "attempts": attempts, "spent": round(spent, 4)}
        # A rejected value is NOT returned and NOT written — the chain continues.
    return {"field": field, "status": "refused", "value": None, "attempts": attempts,
            "spent": round(spent, 4),
            "why": (f"{len(attempts)} provider(s) tried, none returned a value that passed "
                    f"verification. Recorded as a refusal rather than dropped, so this reads as "
                    f"'the chain ran and found nothing' rather than 'nobody tried'.")}


def enrich_company(company_name, data=None, fields=None):
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    co = next((c for c in data.get("companies", [])
               if (c.get("name") or "").strip().lower() == (company_name or "").strip().lower()), None)
    if not co:
        return {"status": "unknown company", "company": company_name}
    want = fields or [f for f in CHAINS if not co.get(f)]
    out = [enrich_field(f, co.get("name"), co) for f in want]
    return {
        "generated": TODAY.isoformat(), "company": co.get("name"), "companyId": co.get("id"),
        "gaps": want, "results": out,
        "verified": [r for r in out if r["status"] == "verified"],
        "refused": [r for r in out if r["status"] == "refused"],
        "spent": round(sum(r["spent"] for r in out), 4),
        "honesty": ("Nothing here is written. Verified values are PROPOSALS the caller may apply; "
                    "refusals are recorded so an empty field can be told apart from an untried "
                    "one. A value that fails its verifier never writes, however many providers "
                    "agreed on it."),
    }


def compute(data=None):
    """Coverage across the book — which fields the chain could and could not fill."""
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    cos = [c for c in data.get("companies", []) if not c.get("archived") and not c.get("archivedOn")]
    cov = {}
    for f in CHAINS:
        have = sum(1 for c in cos if c.get(f))
        cov[f] = {"field": f, "have": have, "of": len(cos),
                  "pct": round(have / len(cos) * 100) if cos else 0,
                  "chain": [n for n, _ in CHAINS[f]]}
    wired = [n for n in {n for ch in CHAINS.values() for n, _ in ch}
             if n in ("crm-self", "site-guess")]
    return {
        "generated": TODAY.isoformat(), "companies": len(cos), "coverage": list(cov.values()),
        "chains": {k: v for k, v in CHAINS.items()},
        "wiredProviders": sorted(wired),
        "reading": (f"{len(cos)} companies. Coverage: "
                    + " · ".join(f"{c['field']} {c['pct']}%" for c in cov.values())),
        "honesty": ("Only the free local providers are wired. The paid rungs are declared with "
                    "their per-call cost but deliberately not callable from here — a billable "
                    "call reachable from a loop is how an enrichment invoice arrives unannounced. "
                    "Wire them via the wire-credentialed-connector skill when the spend is "
                    "intended."),
    }


def main():
    if "--plan" in sys.argv:
        print("Waterfall plan — cheapest credible first, stop at the first VERIFIED hit\n")
        for f, ch in CHAINS.items():
            print(f"  {f:<10} " + " → ".join(f"{n} (${c:.2f})" for n, c in ch))
        print("\n  Every value passes a verifier before it may be written:")
        for f, v in VERIFIERS.items():
            print(f"    {f:<10} {v.__doc__ or v.__name__}")
        return
    if "--company" in sys.argv:
        r = enrich_company(sys.argv[sys.argv.index("--company") + 1])
        print(json.dumps(r, indent=2)); return
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Enrichment coverage — {r['companies']} companies\n")
    for c in r["coverage"]:
        bar = "█" * (c["pct"] // 10) + "·" * (10 - c["pct"] // 10)
        print(f"  {c['field']:<10} {bar} {c['pct']:>3}%  ({c['have']}/{c['of']})  "
              f"chain: {' → '.join(c['chain'])}")
    print(f"\n  {r['honesty']}")


if __name__ == "__main__":
    main()
