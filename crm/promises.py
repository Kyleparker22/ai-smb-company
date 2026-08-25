#!/usr/bin/env python3
"""The promise ledger — sold-vs-delivered drift, made visible.

Every CRM on earth is blind to this, for a structural reason: the CRM and the
delivery system are different products from different vendors, so the sentence
"we'll have the supplier drafts working by the second week" is captured in one
system and owed in another. Nothing reconciles them.

Here they are the same repo. So a commitment becomes a tracked object at the
moment it is made, rides the deal through the stages into `clients/<slug>/`, and
surfaces on the client's own console as **promise debt** — the count and value of
what we said and haven't yet delivered.

That is the moat artifact: provable reliability is exactly what yourco sells, and
this is the instrument that proves it.

Design rule: the extractor PROPOSES, a human CONFIRMS. Candidates are never
silently promoted into the ledger — a fabricated promise is worse than a missed one.

Run:
    python3 crm/promises.py                 # the ledger + debt
    python3 crm/promises.py --scan          # propose candidates from activities + client docs
    python3 crm/promises.py --export        # write clients/<slug>/promises.json for the console
    python3 crm/promises.py --json
"""
import json, os, re, sys, datetime, fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
DATA_JS = os.path.join(DATA_DIR, "data.js")
CLIENTS = os.path.join(REPO, "clients")
CANDIDATES = os.path.join(DATA_DIR, "_promise-candidates.json")
LOCK = os.path.join(REPO, "runtime", ".repo.lock")
TODAY = datetime.date.today()

STATUSES = ("open", "delivered", "broken", "renegotiated")
SEVERITY = {"low": 1, "normal": 2, "high": 3}

# Commitment language. Deliberately narrow: a first-person future-tense promise with an
# object. Broad patterns produce noise, and noise is what makes a ledger get ignored.
PATTERNS = [
    (r"\bwe(?:'| a)?ll\s+(?!see\b|talk\b|be in touch\b)([a-z][^.;\n]{8,120})", "we'll"),
    (r"\bwe will\s+(?!see\b|be in touch\b)([a-z][^.;\n]{8,120})", "we will"),
    (r"\bi(?:'| wi)?ll\s+(?!see\b|talk\b|be in touch\b|let you know\b)([a-z][^.;\n]{8,120})", "I'll"),
    (r"\byourco (?:will|commits to)\s+([a-z][^.;\n]{8,120})", "yourco will"),
    (r"\b(?:we|i) (?:committed|promised|guaranteed) (?:to\s+)?([a-z][^.;\n]{8,120})", "committed"),
    (r"\byou(?:'| wi)?ll have\s+([a-z][^.;\n]{8,120})", "you'll have"),
    (r"\bdeliver(?:ed|y)? by\s+([^.;\n]{4,60})", "delivery date"),
]
DATE_HINT = re.compile(r"\b(by|before|on)\s+((?:mon|tue|wed|thu|fri|sat|sun)\w*|next week|next month|"
                       r"\d{4}-\d{2}-\d{2}|[A-Z][a-z]{2,8}\s+\d{1,2})", re.I)


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")


def client_dir(company_name):
    s = slug(company_name)
    for cand in (s, s.replace("-llc", "").strip("-"), s.split("-")[0]):
        p = os.path.join(CLIENTS, cand)
        if cand and os.path.isdir(p):
            return p
    return None


def holders(data):
    """Deals and closed deals both carry promises — a promise outlives the pipeline row."""
    for d in data.get("deals", []) or []:
        yield d, False
    for c in data.get("closed", []) or []:
        yield c, True


def ledger(data):
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    rows = []
    for h, closed in holders(data):
        co = cos.get(h.get("companyId"), {})
        for p in h.get("promises") or []:
            due = _d(p.get("due"))
            status = p.get("status") or "open"
            overdue = bool(due and due < TODAY and status == "open")
            rows.append({
                "id": p.get("id"), "dealId": h.get("id"), "companyId": h.get("companyId"),
                "company": co.get("name") or h.get("name"),
                "text": p.get("text") or "", "madeOn": p.get("madeOn"), "due": p.get("due"),
                "source": p.get("source") or "", "owner": p.get("owner") or "the Founder",
                "status": status, "severity": p.get("severity") or "normal",
                "deliveredOn": p.get("deliveredOn"), "evidence": p.get("evidence") or "",
                "overdue": overdue,
                "daysLate": (TODAY - due).days if overdue else None,
                "stage": h.get("stage"), "closed": closed,
            })
    return rows


def debt(rows):
    """Promise debt: what is owed and unpaid, per company. Severity-weighted, never money-valued —
    a promise is not a dollar figure and pretending otherwise would be an invented number."""
    by = {}
    for r in rows:
        if r["status"] != "open":
            continue
        b = by.setdefault(r["company"], {"company": r["company"], "open": 0, "overdue": 0,
                                         "weight": 0, "worstDaysLate": 0, "items": []})
        b["open"] += 1
        b["weight"] += SEVERITY.get(r["severity"], 2)
        if r["overdue"]:
            b["overdue"] += 1
            b["worstDaysLate"] = max(b["worstDaysLate"], r["daysLate"] or 0)
        b["items"].append(r)
    out = sorted(by.values(), key=lambda b: (-b["overdue"], -b["weight"]))
    for b in out:
        b["state"] = "clear" if not b["open"] else ("in debt" if b["overdue"] else "carrying")
    return out


# ---------------------------------------------------------------- extraction

def _clean(t):
    t = re.sub(r"\s+", " ", t).strip(" -–—*|`")
    return t[:180]


def scan_text(text, source, data_date=None):
    found = []
    for pat, kind in PATTERNS:
        for m in re.finditer(pat, text, re.I):
            body = _clean(m.group(1))
            if len(body.split()) < 3:
                continue
            ctx = text[max(0, m.start() - 90): m.end() + 90]
            dh = DATE_HINT.search(ctx)
            found.append({"text": _clean(m.group(0)), "cue": kind, "source": source,
                          "dueHint": dh.group(0) if dh else None, "madeOn": data_date})
    return found


def scan(data, max_files=60):
    """Propose promise candidates from the CRM activity log and the client folders."""
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    out = []
    seen = set()

    def push(company_id, company, cand):
        key = (company_id, cand["text"].lower()[:90])
        if key in seen:
            return
        seen.add(key)
        cand.update({"companyId": company_id, "company": company, "status": "candidate"})
        out.append(cand)

    for a in data.get("activities", []) or []:
        co = cos.get(a.get("companyId"))
        if not co:
            continue
        for c in scan_text(str(a.get("summary") or ""), f"activity {a.get('date')} ({a.get('type')})",
                           a.get("date")):
            push(co["id"], co.get("name"), c)

    for co in cos.values():
        cd = client_dir(co.get("name"))
        if not cd:
            continue
        n = 0
        for root, _, files in os.walk(cd):
            if any(p in root for p in ("/node_modules", "/.git", "/_archive")):
                continue
            for fn in sorted(files):
                if not fn.endswith((".md", ".txt")) or n >= max_files:
                    continue
                n += 1
                path = os.path.join(root, fn)
                try:
                    with open(path, errors="ignore") as f:
                        txt = f.read()[:120000]
                except Exception:
                    continue
                rel = os.path.relpath(path, REPO)
                mdate = None
                m = re.search(r"(\d{4}-\d{2}-\d{2})", fn)
                if m:
                    mdate = m.group(1)
                for c in scan_text(txt, rel, mdate):
                    push(co["id"], co.get("name"), c)
    return out


def export(data, rows):
    """Write the per-client feed the client console reads. One file per real client folder."""
    written = []
    by_co = {}
    for r in rows:
        by_co.setdefault(r["company"], []).append(r)
    for company, items in by_co.items():
        cd = client_dir(company)
        if not cd:
            continue
        open_items = [i for i in items if i["status"] == "open"]
        payload = {
            "company": company, "generated": TODAY.isoformat(),
            "open": len(open_items), "overdue": sum(1 for i in open_items if i["overdue"]),
            "delivered": sum(1 for i in items if i["status"] == "delivered"),
            "renegotiated": sum(1 for i in items if i["status"] == "renegotiated"),
            "broken": sum(1 for i in items if i["status"] == "broken"),
            "promises": [{"text": i["text"], "madeOn": i["madeOn"], "due": i["due"],
                          "status": i["status"], "deliveredOn": i["deliveredOn"],
                          "daysLate": i["daysLate"], "source": i["source"]} for i in items],
            "note": ("Everything yourco said it would do for you, and where each one stands. "
                     "Shown to you on purpose — an unmet commitment you can see is a commitment we can be held to."),
        }
        p = os.path.join(cd, "promises.json")
        tmp = p + ".tmp"
        with open(tmp, "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
        written.append(os.path.relpath(p, REPO))
    return written


def save_candidates(cands):
    tmp = CANDIDATES + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"generated": TODAY.isoformat(), "candidates": cands,
                   "note": "Proposed, not accepted. Confirm in the CRM dossier to enter the ledger."},
                  f, indent=2, ensure_ascii=False)
    os.replace(tmp, CANDIDATES)


def compute(data):
    rows = ledger(data)
    d = debt(rows)
    return {"generated": TODAY.isoformat(), "promises": rows, "debt": d,
            "open": sum(1 for r in rows if r["status"] == "open"),
            "overdue": sum(1 for r in rows if r["overdue"]),
            "delivered": sum(1 for r in rows if r["status"] == "delivered"),
            "broken": sum(1 for r in rows if r["status"] == "broken"),
            "candidatesFile": os.path.basename(CANDIDATES),
            "honesty": ("Only confirmed promises are in this ledger. The scanner proposes candidates from "
                        "the activity log and the client folder; a human accepts them in the dossier. "
                        "Debt is counted and severity-weighted, never converted to dollars — there is no "
                        "defensible exchange rate between a missed commitment and money.")}


def main():
    with open(DATA) as f:
        data = json.load(f)
    if "--scan" in sys.argv:
        cands = scan(data)
        save_candidates(cands)
        print(f"{len(cands)} candidate promise(s) proposed → crm/{os.path.basename(CANDIDATES)}")
        for c in cands[:25]:
            print(f"  [{c['company']}] {c['text']}")
            print(f"      source: {c['source']}" + (f"  due-hint: {c['dueHint']}" if c["dueHint"] else ""))
        if len(cands) > 25:
            print(f"  … and {len(cands)-25} more")
        print("\nNothing entered the ledger — confirm each one in the CRM dossier.")
        return
    r = compute(data)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Promise ledger — {len(r['promises'])} tracked, {r['open']} open, {r['overdue']} overdue\n")
    if not r["promises"]:
        print("  Empty. Run --scan to propose candidates from what's already on record,")
        print("  or add one in the CRM dossier the moment it's made.")
    for b in r["debt"]:
        print(f"  {b['company'][:30]:<30} {b['state']:<9} open {b['open']}, overdue {b['overdue']}"
              + (f", worst {b['worstDaysLate']}d late" if b["worstDaysLate"] else ""))
        for i in b["items"][:5]:
            flag = f"  ⚠ {i['daysLate']}d late" if i["overdue"] else ""
            print(f"      · {i['text'][:100]}{flag}")
    if "--export" in sys.argv:
        w = export(data, r["promises"])
        print("\nexported: " + (", ".join(w) if w else "no client folder matched a company with promises"))
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
