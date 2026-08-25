"""
Seed Property OS from a real manager's trust-account journal.

The synthetic seed (seed.py) invents a 220-unit portfolio. This one imports an
actual book of business from the spreadsheet the manager already keeps, so a
prospect sees THEIR doors, THEIR tenants and THEIR trust ledger rather than
someone else's demo.

    python3 seed_parker.py "/path/to/Rent Account Journal 2026.xlsx"

No names, addresses or figures live in this file — everything comes from the
workbook at run time, and data/ is gitignored, so importing real books leaves
nothing in the repo.
"""
import sys, os, re, hashlib, datetime as dt
from collections import OrderedDict, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

try:
    import openpyxl
except ImportError:
    sys.exit("needs openpyxl:  python3 -m pip install openpyxl")

JOURNAL_SHEET_HINT = "journal"
UTC = dt.timezone.utc


def sid(prefix, *parts):
    """Stable id from content, so re-running the import doesn't churn ids."""
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:10]
    return f"{prefix}_{h}"


def isot(d):
    if isinstance(d, dt.datetime):
        return d.replace(tzinfo=UTC).isoformat()
    return core.iso()


# ── property-name canonicalisation ────────────────────────────────────────────
# The same house is written several ways: "1010 Bexton", "1010 bexton st",
# "Bexton". Some houses are never numbered in the journal at all. Some rows name
# several properties at once, and a few name none. Each of those is a different
# problem and only the last two are unresolvable, so they become findings rather
# than silently landing on the wrong ledger.
import difflib

SUFFIXES = {"st", "street", "rd", "road", "ct", "court", "dr", "drive", "ln",
            "lane", "way", "ave", "avenue", "pl", "place", "blvd", "trail", "tr"}
NOT_A_PROPERTY = re.compile(r"incidental|misc|test |account|acct|^\(")


def canon_key(raw):
    s = re.sub(r"\s+", " ", str(raw or "").strip().lower())
    return s.strip(" .,-")


def street_of(k):
    """Street words only: no number, no suffix — the part that identifies a house."""
    words = [w for w in re.sub(r"[^a-z0-9 ]", " ", k).split() if not w.isdigit()]
    while words and words[-1] in SUFFIXES:
        words.pop()
    return " ".join(words)


def is_multi(k):
    return ("," in k) or ("(" in k) or bool(re.search(r"\ball\b.*propert", k))


def build_property_index(rows):
    """Canonical properties = every distinct street that carries real money."""
    streets = {}                       # street -> best display key
    for r in rows:
        k = canon_key(r["property"])
        if not k or is_multi(k) or NOT_A_PROPERTY.search(k):
            continue
        if classify(r["desc"]) not in ("rent", "fee", "disbursement", "maintenance", "deposit"):
            continue
        st = street_of(k)
        if not st:
            continue
        num = re.match(r"^(\d+)", k)
        # a numbered spelling is the better display name; keep the first one seen
        if st not in streets or (num and not re.match(r"^\d", streets[st])):
            streets[st] = k
    # Fold misspellings into the spelling that appears most often, BEFORE building
    # the index — otherwise "Kalispel" becomes a ninth house that doesn't exist.
    freq = defaultdict(int)
    for r in rows:
        k = canon_key(r["property"])
        if k and not is_multi(k) and not NOT_A_PROPERTY.search(k):
            st = street_of(k)
            if st:
                freq[st] += 1
    alias = {}
    for st in sorted(freq, key=lambda x: freq[x]):
        better = [o for o in freq if o != st and freq[o] > freq[st]
                  and difflib.SequenceMatcher(None, st, o).ratio() >= 0.88]
        if better:
            alias[st] = max(better, key=lambda o: freq[o])
    for bad, good in alias.items():
        streets.pop(bad, None)
    globals()["_STREET_ALIAS"] = alias

    # houses sharing a street are distinct only when numbered — group by (street, number)
    canon = OrderedDict()
    for r in rows:
        k = canon_key(r["property"])
        if not k or is_multi(k) or NOT_A_PROPERTY.search(k):
            continue
        if classify(r["desc"]) not in ("rent", "fee", "disbursement", "maintenance", "deposit"):
            continue
        st, num = street_of(k), (re.match(r"^(\d+)", k) or [None, None])[1]
        st = alias.get(st, st)
        if not st:
            continue
        canon.setdefault((st, num), k if num else streets.get(st, k))
    # A bare mention of a street that also appears numbered is the SAME house,
    # not another one — otherwise every unnumbered row invents a phantom property
    # and makes its own street look ambiguous.
    numbered_streets = {st for (st, num) in canon if num}
    for key in [k for k in canon if k[1] is None and k[0] in numbered_streets]:
        canon.pop(key)
    return canon, streets


def resolve_property(raw, canon, streets):
    k = canon_key(raw)
    if not k:
        return None, "no property named"
    if NOT_A_PROPERTY.search(k):
        return None, None                       # not a property row at all
    if is_multi(k):
        return None, f'"{raw}" names more than one property — it cannot post to any single ledger'
    st, num = street_of(k), (re.match(r"^(\d+)", k) or [None, None])[1]
    st = globals().get("_STREET_ALIAS", {}).get(st, st)
    if not st:
        return None, f'"{raw}" not recognised'
    if st not in streets:                       # tolerate a typo: kalispel -> kalispell
        near = difflib.get_close_matches(st, list(streets), n=1, cutoff=0.85)
        if not near:
            return None, f'"{raw}" not recognised'
        st = near[0]
    same = [key for (s2, n2), key in canon.items() if s2 == st]
    if num is not None:
        exact = [key for (s2, n2), key in canon.items() if s2 == st and n2 == num]
        if exact:
            return exact[0], None
    if len(same) == 1:
        return same[0], None
    return None, f'"{raw}" could be any of {len(same)} houses on that street'


def title(k):
    return " ".join(w.capitalize() for w in k.split())


# ── classifying a journal line ────────────────────────────────────────────────
def classify(desc, item=""):
    t = f"{desc} {item}".lower()
    if re.search(r"\bpm fee|property mgmt|management fee|mgmt fee", t):
        return "fee"
    if re.search(r"disburse?ment|disbust|to landlord|to owner", t):
        return "disbursement"
    if re.search(r"maint|repair|hvac|furnace|dishwasher|plumb|roof|paint|lawn|appliance", t):
        return "maintenance"
    if re.search(r"security deposit|\bsd\b|deposit held", t):
        return "deposit"
    if re.search(r"\brent\b|rental", t):
        return "rent"
    if re.search(r"incidental|misc fund|carryover|balance from", t):
        return "misc"
    return "other"


def read_journal(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = next((s for s in wb.worksheets if JOURNAL_SHEET_HINT in s.title.lower()), wb.worksheets[0])
    rows, header_at = [], None
    for i, r in enumerate(ws.iter_rows(values_only=True), start=1):
        vals = [("" if c is None else c) for c in r]
        low = [str(v).strip().lower() for v in vals]
        if header_at is None:
            if "date" in low and ("deposits" in low or "parties" in low):
                header_at = {name: idx for idx, name in enumerate(low) if name}
            continue
        def col(*names):
            for n in names:
                if n in header_at:
                    return vals[header_at[n]]
            return ""
        date, party = col("date"), col("parties")
        desc, prop = col("description/purpose", "description"), col("property")
        dep, chk = col("deposits"), col("checks pd", "checks")
        cleared = str(col("cleared bank", "cleared")).strip().lower().startswith("y")
        num = col("number")
        if not any([date, party, desc, dep, chk]):
            continue
        def money(v):
            try:
                return round(float(v), 2)
            except (TypeError, ValueError):
                return 0.0
        rows.append({
            "row": i, "date": date if isinstance(date, dt.datetime) else None,
            "raw_date": date, "party": str(party).strip(), "desc": str(desc).strip(),
            "property": str(prop).strip(), "deposit": money(dep), "check": money(chk),
            "cleared": cleared, "number": num,
        })
    return rows


def build(path):
    rows = read_journal(path)
    canon, streets = build_property_index(rows)
    findings = []

    # ── properties + units (single-family: one unit each) ────────────────────
    props, units, prop_by_key = [], [], {}
    seen_keys = list(OrderedDict.fromkeys(canon.values()))
    for k in seen_keys:
        pid = sid("prop", k)
        prop_by_key[k] = pid
        props.append({"id": pid, "name": title(k), "address": title(k),
                      "city": "Yourtown", "state": "NC", "year_built": None,
                      "owner_id": None})
        num = (re.match(r"^(\d+)", k) or [None, ""])[1] or "—"
        units.append({"id": sid("unit", k), "property_id": pid, "label": num,
                      "beds": None, "baths": None, "sqft": None, "rent": 0,
                      "tenant_id": None,
                      "lease": {"start": None, "end": None, "term_months": None,
                                "status": "active", "renewal_status": "not_started"}})
    unit_by_key = {k: sid("unit", k) for k in seen_keys}

    # ── tenants: whoever pays the rent on a property ─────────────────────────
    rent_by_prop = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if classify(r["desc"]) != "rent" or r["deposit"] <= 0:
            continue
        key, err = resolve_property(r["property"], canon, streets)
        if not key:
            findings.append({"row": r["row"], "issue": err, "amount": r["deposit"]})
            continue
        if r["party"]:
            rent_by_prop[key][r["party"]].append(r)

    tenants, tenant_by = [], {}
    for key, parties in rent_by_prop.items():
        # most recent payer is the sitting tenant; earlier ones are prior tenancies
        ordered = sorted(parties.items(),
                         key=lambda kv: max([x["date"] or dt.datetime.min for x in kv[1]]),
                         reverse=True)
        for idx, (name, txns) in enumerate(ordered):
            tid = sid("ten", key, name)
            first = min([t["date"] for t in txns if t["date"]] or [None])
            tenants.append({"id": tid, "name": name, "unit_id": unit_by_key[key],
                            "email": "", "phone": "", "move_in": isot(first),
                            "language": "en", "comms_pref": "sms",
                            "vulnerable_occupant": False,
                            "rent_on_time_streak": 0,
                            "status": "current" if idx == 0 else "past"})
            if idx == 0:
                tenant_by[key] = tid
                # We know when they STARTED paying. We do not know the lease term —
                # that is the one thing these books cannot supply, so it stays null
                # rather than being invented; the empty renewal radar is the finding.
                for u in units:
                    if u["id"] == unit_by_key[key] and first:
                        u["lease"]["start"] = isot(first)
                        u["lease"]["status"] = "active"
                        u["lease"]["term_unconfirmed"] = True
                amounts = [t["deposit"] for t in txns]
                rent = max(set(amounts), key=amounts.count)
                for u in units:
                    if u["id"] == unit_by_key[key]:
                        u["tenant_id"] = tid
                        u["rent"] = rent
                if len(set(amounts)) > 2:
                    findings.append({"row": None,
                                     "issue": f"{title(key)}: rent varies {min(amounts):.0f}–{max(amounts):.0f} — lease terms needed",
                                     "amount": None})

    # ── owners: inferred per property from the fee rate actually charged ─────
    owners, fee_pct = [], {}
    for key in seen_keys:
        rents = [r["deposit"] for r in rows
                 if classify(r["desc"]) == "rent" and r["deposit"] > 0
                 and resolve_property(r["property"], canon, streets)[0] == key]
        fees = [r["check"] for r in rows
                if classify(r["desc"]) == "fee" and r["check"] > 0
                and resolve_property(r["property"], canon, streets)[0] == key]
        if rents and fees:
            fee_pct[key] = round(sum(fees) / sum(rents), 4)
    # one owner record per property until the real owner map is confirmed
    for key in seen_keys:
        oid = sid("own", key)
        owners.append({"id": oid, "name": f"Owner — {title(key)}", "email": "",
                       "properties": [prop_by_key[key]], "spend_approval_limit": 400,
                       "emergency_spend_limit": 2000,
                       "reserve_policy": "Confirm with the manager at onboarding.",
                       "mgmt_fee_pct": fee_pct.get(key, 0.08), "reserve_floor": 0,
                       "unconfirmed": True})
        for p in props:
            if p["id"] == prop_by_key[key]:
                p["owner_id"] = oid

    # ── money: charges, payments, maintenance, and the trust ledger ──────────
    charges, payments, ledger, requests = [], [], [], []
    for r in rows:
        kind = classify(r["desc"])
        key, err = resolve_property(r["property"], canon, streets)
        amt = r["deposit"] or r["check"]
        if amt <= 0 and kind != "misc":
            continue
        if not key:
            if kind in ("rent", "fee", "disbursement", "maintenance"):
                findings.append({"row": r["row"], "issue": err or "unattributable", "amount": amt})
            continue
        at = isot(r["date"])
        if not r["date"]:
            findings.append({"row": r["row"], "issue": "no date — invisible to any monthly report", "amount": amt})
        uid, tid = unit_by_key[key], tenant_by.get(key)

        if kind == "rent" and r["deposit"] > 0:
            month = (r["date"] or dt.datetime.now()).strftime("%Y-%m")
            charges.append({"id": sid("chg", key, month), "unit_id": uid, "tenant_id": tid,
                            "month": month, "amount": r["deposit"],
                            "due": at, "kind": "rent"})
            payments.append({"id": sid("pay", r["row"]), "tenant_id": tid, "unit_id": uid,
                             "amount": r["deposit"], "method": "bank", "at": at,
                             "recorded_by": "import:journal"})
        if kind == "maintenance" and r["check"] > 0:
            requests.append({"id": sid("req", r["row"]), "unit_id": uid,
                             "property_id": prop_by_key[key], "tenant_id": tid,
                             "title": r["desc"] or "Maintenance", "description": r["desc"],
                             "category": "other", "priority": "P3", "status": "resolved",
                             "submitted_at": at, "channel": "import",
                             "photos": [], "cost": r["check"],
                             "vendor_id": None, "imported": True})

        acct = {"rent": "rent_income", "fee": "mgmt_fee", "disbursement": "owner_payout",
                "maintenance": "maintenance_expense", "deposit": f"deposits:{tid}",
                "misc": "misc_fund"}.get(kind, "unclassified")
        if r["deposit"] > 0:
            entries = [{"account": "trust_cash", "debit": r["deposit"], "credit": 0},
                       {"account": acct, "debit": 0, "credit": r["deposit"]}]
        else:
            entries = [{"account": acct, "debit": r["check"], "credit": 0},
                       {"account": "trust_cash", "debit": 0, "credit": r["check"]}]
        ledger.append({"id": sid("txn", r["row"]), "at": at,
                       "memo": f'{r["desc"]} — {title(key)}'.strip(" —"),
                       "actor": "import:journal", "kind": kind,
                       "subject": tid or prop_by_key[key], "entries": entries,
                       "cleared": r["cleared"], "source_row": r["row"]})

    # ── per-property balance: the finding hand-kept books can't surface ──────
    bal = defaultdict(float)
    for r in rows:
        key, _ = resolve_property(r["property"], canon, streets)
        if key:
            bal[key] += r["deposit"] - r["check"]
    for key, v in bal.items():
        if v < -1:
            findings.append({"row": None,
                             "issue": f"{title(key)} ends at {v:,.2f} — its costs exceeded its rents, "
                                      f"so other owners' funds are covering it",
                             "amount": round(v, 2)})

    uncleared = [r for r in rows if not r["cleared"] and (r["deposit"] or r["check"])]
    if uncleared:
        findings.append({"row": None,
                         "issue": f"{len(uncleared)} entries never marked cleared against the bank",
                         "amount": None})

    cfg = core.load("config", {}) or {}
    cfg.update({"org": "Imported portfolio", "unit_count": len(units),
                "seeded_at": core.iso(), "source": os.path.basename(path),
                "import": {"rows_read": len(rows), "properties": len(props),
                           "tenants": len(tenants), "ledger_entries": len(ledger),
                           "findings": len(findings)},
                "seed_params": {"imported": True}})
    cfg.pop("auth", None)          # demo login codes must not survive real data

    core.save("properties", props);   core.save("units", units)
    core.save("owners", owners);      core.save("tenants", tenants)
    core.save("charges", charges);    core.save("payments", payments)
    core.save("ledger", ledger);      core.save("requests", requests)
    core.save("config", cfg)
    for empty in ("vendors", "components", "events", "surveys", "messages",
                  "approvals", "batches", "turnovers", "referrals",
                  "inquiries", "prospects"):
        core.save(empty, [])
    core.save("findings", findings)
    return props, units, tenants, ledger, findings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    p, u, t, l, f = build(sys.argv[1])
    print(f"properties {len(p)} · units {len(u)} · tenants {len(t)} · ledger {len(l)}")
    print(f"findings   {len(f)}")
    for x in f[:12]:
        print("  -", x["issue"])
