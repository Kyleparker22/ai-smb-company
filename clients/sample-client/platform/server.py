#!/usr/bin/env python3
"""Sample Client Design Studio platform server.

Serves the static platform AND a tiny JSON API for shared persistence:
  GET    /api/projects            -> [{id,name,client,updated}]
  POST   /api/projects            -> create {name, state?} -> {id}
  GET    /api/projects/<id>       -> full state JSON
  PUT    /api/projects/<id>       -> save state JSON
  DELETE /api/projects/<id>       -> remove
  GET    /api/actuals             -> shared completed-job entries (list)
  POST   /api/actuals             -> append one entry
  GET    /api/render-queue        -> pending render-generation requests
  POST   /api/render-queue        -> append request {projectId,state,prompt}

Storage: JSON files under data/projects/ + data/shared/ next to this file.
Stdlib only. Frontend degrades to localStorage-only mode if this API is absent
(i.e. when served by plain http.server).
"""
import json, re, sys, threading, time, urllib.request, urllib.error, uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
import shepherds_reader

ROOT = Path(__file__).resolve().parent

# ---- credentials (.env, gitignored — see .env.example) ----
ENV = {}
_envf = ROOT / ".env"
if _envf.exists():
    for line in _envf.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            if v.strip():
                ENV[k.strip()] = v.strip()

INTEGRATIONS = {
    "hubspot":   {"keys": ["HUBSPOT_TOKEN"], "kind": "api"},
    "aspire":    {"keys": ["ASPIRE_CLIENT_ID", "ASPIRE_CLIENT_SECRET"], "kind": "api"},
    "siteone":   {"keys": ["SITEONE_USER", "SITEONE_PASS"], "kind": "portal"},
    "ewing":     {"keys": ["EWING_ACCOUNT", "EWING_OTP_PHONE"], "kind": "portal-otp"},
    "latham":    {"keys": ["LATHAM_PASSWORD"], "kind": "password-gate"},
    "kirkdavis": {"keys": ["KIRKDAVIS_USER", "KIRKDAVIS_PASS"], "kind": "email-report"},
    "shepherds": {"keys": [], "kind": "public-site"},
}

SHEP = {"running": False}


def shepherds_pull(limit):
    try:
        shepherds_reader.run(limit=limit, delay=1.0)
    finally:
        SHEP["running"] = False


def shepherds_summary():
    f = SHARED / "availability-shepherds.json"
    if not f.exists():
        return {"pulled": None, "running": SHEP["running"]}
    d = read_json(f, {})
    return {"pulled": d.get("pulled"), "site_total": d.get("site_total"),
            "parsed": d.get("parsed"), "in_stock": d.get("in_stock"),
            "out_of_stock": d.get("out_of_stock"), "running": SHEP["running"]}


def integration_status():
    out = {}
    for name, spec in INTEGRATIONS.items():
        out[name] = {"kind": spec["kind"],
                     "credentials": all(k in ENV for k in spec["keys"]),
                     "missing": [k for k in spec["keys"] if k not in ENV]}
    out["availability_email"] = bool(ENV.get("AVAILABILITY_REPORT_EMAIL"))
    return out


def http_json(req):
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


def test_integration(name):
    """Live, read-only credential check. Never returns secret values."""
    if name == "hubspot":
        tok = ENV.get("HUBSPOT_TOKEN")
        if not tok:
            return {"ok": False, "detail": "HUBSPOT_TOKEN missing from .env"}
        req = urllib.request.Request(
            "https://api.hubapi.com/crm/v3/objects/deals?limit=1",
            headers={"Authorization": "Bearer " + tok})
        code, body = http_json(req)
        if code == 200:
            return {"ok": True, "detail": "Connected — deals endpoint readable (read scopes OK)."}
        if code in (401, 403):
            return {"ok": False, "detail": f"HTTP {code} — token invalid or missing crm.objects.deals scopes ({body.get('message','')[:120]})"}
        return {"ok": False, "detail": f"HTTP {code} {str(body)[:120]}"}
    if name == "aspire":
        cid, sec = ENV.get("ASPIRE_CLIENT_ID"), ENV.get("ASPIRE_CLIENT_SECRET")
        if not (cid and sec):
            return {"ok": False, "detail": "ASPIRE_CLIENT_ID / ASPIRE_CLIENT_SECRET missing from .env"}
        req = urllib.request.Request(
            "https://cloud-api.youraspire.com/Authorization",
            data=json.dumps({"ClientId": cid, "Secret": sec}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        code, body = http_json(req)
        if code == 200 and (body.get("Token") or body.get("token")):
            return {"ok": True, "detail": "Connected — Aspire API token issued."}
        if code == 404:  # Aspire returns 404 for bad credentials, not 401
            return {"ok": False, "detail": "Aspire rejected the Client ID + Secret pair. Verify the Client ID against the API page (screenshot is safe — secret isn't shown there), regenerate + re-copy the secret, or ask AspireCare to confirm API access is enabled for the account."}
        return {"ok": False, "detail": f"HTTP {code} ({str(body)[:120]})"}
    if name == "shepherds":
        try:
            n = len(shepherds_reader.product_urls())
            return {"ok": True, "detail": f"Connected — public product sitemap readable, {n} products listed (robots.txt allows; no credentials involved)."}
        except Exception as e:
            return {"ok": False, "detail": f"Sitemap fetch failed: {e}"}
    if name in INTEGRATIONS:
        st = integration_status()[name]
        if not st["credentials"]:
            return {"ok": False, "detail": "Credentials missing from .env: " + ", ".join(st["missing"])}
        if st["kind"] == "portal-otp":
            return {"ok": True, "detail": "Account on file. Login is SMS one-time code (no stored secret, by design) — human logs in, exports, CSV imports here."}
        if st["kind"] == "password-gate":
            return {"ok": True, "detail": "Wholesale-page password on file (lathamsnursery.com/wholesale) — human unlocks the page, grabs the list, CSV imports here."}
        return {"ok": True, "detail": "Portal credentials on file (no public API — used for exports; automated portal pulls are ToS-gated, Ray reviews)."}
    return {"ok": False, "detail": "unknown integration"}
PROJ = ROOT / "data" / "projects"
SHARED = ROOT / "data" / "shared"
PROJ.mkdir(parents=True, exist_ok=True)
SHARED.mkdir(parents=True, exist_ok=True)
PORT = 8804
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path, obj):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    tmp.replace(path)


# ---- Aspire live data (read-only credential; Select-All-GET scopes) ----
ASPIRE_BASE = "https://cloud-api.youraspire.com"
_aspire_tok = {"token": None, "ts": 0}


def aspire_token():
    if _aspire_tok["token"] and time.time() - _aspire_tok["ts"] < 3000:
        return _aspire_tok["token"]
    req = urllib.request.Request(ASPIRE_BASE + "/Authorization",
        data=json.dumps({"ClientId": ENV.get("ASPIRE_CLIENT_ID", ""),
                         "Secret": ENV.get("ASPIRE_CLIENT_SECRET", "")}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    code, body = http_json(req)
    tok = body.get("Token") or body.get("token")
    if code == 200 and tok:
        _aspire_tok.update(token=tok, ts=time.time())
        return tok
    raise RuntimeError(f"Aspire auth failed HTTP {code}")


def aspire_get(path, query=""):
    req = urllib.request.Request(ASPIRE_BASE + path + (("?" + query) if query else ""),
        headers={"Authorization": "Bearer " + aspire_token(), "Accept": "application/json"})
    code, body = http_json(req)
    if code != 200:
        raise RuntimeError(f"Aspire GET {path} HTTP {code}: {str(body)[:150]}")
    return body


def aspire_pull_actuals():
    """Completed work tickets -> est-vs-actual entries for the self-tuning engine."""
    def unwrap(x):
        return x if isinstance(x, list) else (x.get("value", []) if isinstance(x, dict) else [])
    tickets = unwrap(aspire_get("/WorkTickets", "$top=500&$orderby=CompleteDate%20desc"))
    times = []
    for page in range(10):  # $top caps at 1000 — paginate, newest first so they overlap recent tickets
        batch = unwrap(aspire_get("/WorkTicketTimes", f"$top=1000&$skip={page * 1000}&$orderby=WorkTicketTimeDate%20desc"))
        times.extend(batch)
        if len(batch) < 1000:
            break
    hours_by_ticket = {}
    for t in times:
        wid = t.get("WorkTicketID")
        hours_by_ticket[wid] = hours_by_ticket.get(wid, 0) + (t.get("Hours") or 0) + (t.get("OTHours") or 0)
    # Their reality (checked live 2026-08-18): InvoicedAmount lags (batch invoicing), and most
    # tickets are small maintenance stops. The install-quoting engine learns from install-scale
    # work: HoursEst >= 4. Price-accuracy uses final only where invoicing exists (final=0 rows
    # feed labor calibration but are excluded from the accuracy stat by the frontend).
    entries, small, no_time = [], 0, 0
    for w in tickets:
        if not w.get("CompleteDate"):
            continue
        est_h = w.get("HoursEst") or 0
        act_h = hours_by_ticket.get(w.get("WorkTicketID"), 0)
        quoted = w.get("Price") or w.get("TMCalcAmount") or 0
        final = w.get("InvoicedAmount") or w.get("TMCalcAmount") or 0
        if est_h > 0 and est_h < 4:
            small += 1
            continue
        if est_h >= 4 and act_h > 0 and quoted > 0:
            entries.append({"id": "A" + str(w.get("WorkTicketID")),
                            "name": f"WT {w.get('WorkTicketNumber')} ({w.get('WorkTicketStatusName', '')})",
                            "quotedMid": round(quoted, 2), "final": round(final, 2),
                            "estDays": round(est_h / 8, 2), "actDays": round(act_h / 8, 2),
                            "closed": str(w.get("CompleteDate"))[:10], "source": "aspire"})
        elif est_h >= 4:
            no_time += 1
    out = {"pulled": time.strftime("%Y-%m-%dT%H:%M:%S"), "tickets_seen": len(tickets),
           "time_entries_seen": len(times), "usable": len(entries),
           "small_maintenance_excluded": small, "install_scale_missing_time_data": no_time,
           "entries": entries}
    write_json(SHARED / "actuals-aspire.json", out)
    return out


def _paginate(path, pages=5, extra="", top=1000):
    out = []
    for page in range(pages):
        q = f"$top={top}&$skip={page * top}" + (("&" + extra) if extra else "")
        batch = aspire_get(path, q)
        batch = batch if isinstance(batch, list) else (batch.get("value", []) if isinstance(batch, dict) else [])
        out.extend(batch)
        if len(batch) < top:
            break
    return out


def aspire_deep_pull():
    """Study-grade job records: ticket -> service -> opportunity -> property, plus actual
    materials (item allocations), per-person crew hours, and sold line items. Read-only."""
    tickets = [t for t in _paginate("/WorkTickets", 1, "$orderby=CompleteDate%20desc", top=500) if t.get("CompleteDate")]
    times = _paginate("/WorkTicketTimes", 10, "$orderby=WorkTicketTimeDate%20desc")

    def fetch_by_ids(path, id_field, ids, batch=40):
        out = {}
        ids = [i for i in set(ids) if i is not None]
        for i in range(0, len(ids), batch):
            chunk = ",".join(str(x) for x in ids[i:i + batch])
            for row in _paginate(path, 1, f"$filter={id_field}%20in%20({chunk})"):
                out[row[id_field]] = row
        return out

    services = fetch_by_ids("/OpportunityServices", "OpportunityServiceID",
                            [t.get("OpportunityServiceID") for t in tickets])
    opps = fetch_by_ids("/Opportunities", "OpportunityID",
                        [s.get("OpportunityID") for s in services.values()])
    props = fetch_by_ids("/Properties", "PropertyID",
                         [o.get("PropertyID") for o in opps.values()])
    allocs = _paginate("/ItemAllocations", 5, "$orderby=CreatedDateTime%20desc")
    svc_items = []
    svc_ids = [s for s in services.keys()]
    for i in range(0, len(svc_ids), 40):
        chunk = ",".join(str(x) for x in svc_ids[i:i + 40])
        svc_items.extend(_paginate("/OpportunityServiceItems", 1, f"$filter=OpportunityServiceID%20in%20({chunk})"))

    crew_by_ticket, items_by_ticket, sold_by_service = {}, {}, {}
    for t in times:
        crew_by_ticket.setdefault(t.get("WorkTicketID"), {})
        nm = t.get("ContactName") or "?"
        crew_by_ticket[t["WorkTicketID"]][nm] = round(crew_by_ticket[t["WorkTicketID"]].get(nm, 0) + (t.get("Hours") or 0) + (t.get("OTHours") or 0), 2)
    for a in allocs:
        items_by_ticket.setdefault(a.get("WorkTicketID"), []).append(
            {"item": a.get("ItemName") or a.get("CatalogItemName"), "qty": a.get("ItemQuantity"),
             "cost": a.get("ItemTotalCost"), "type": a.get("ItemType")})
    for si in svc_items:
        sold_by_service.setdefault(si.get("OpportunityServiceID"), []).append(
            {"item": si.get("ItemName"), "qty": si.get("ItemQuantity"), "type": si.get("ItemType"),
             "price": si.get("ExtendedPrice"), "hours": si.get("ExtendedHours"),
             "category": si.get("CatalogItemCategoryName")})

    jobs = []
    for w in tickets:
        svc = services.get(w.get("OpportunityServiceID"), {})
        opp = opps.get(svc.get("OpportunityID"), {})
        prop = props.get(opp.get("PropertyID"), {})
        crew = crew_by_ticket.get(w.get("WorkTicketID"), {})
        mat = items_by_ticket.get(w.get("WorkTicketID"), [])
        jobs.append({
            "ticket": w.get("WorkTicketNumber"), "completed": str(w.get("CompleteDate"))[:10],
            "division": opp.get("DivisionName"), "opportunity": opp.get("OpportunityName"),
            "oppStatus": opp.get("OpportunityStatusName"), "salesRep": opp.get("SalesRepContactName"),
            "service": svc.get("DisplayName"), "complexityPercent": svc.get("ComplexityPercent"),
            "property": {"city": prop.get("PropertyAddressCity"), "industry": prop.get("IndustryName"),
                         "status": prop.get("PropertyStatusName")},
            "est": {"hours": w.get("HoursEst"), "laborCost": w.get("HourCostEst"),
                    "material": w.get("MaterialCostEst"), "equip": w.get("EquipCostEst"),
                    "sub": w.get("SubCostEst"), "other": w.get("OtherCostEst")},
            "price": w.get("Price"), "invoiced": w.get("InvoicedAmount"),
            "actual": {"hours": round(sum(crew.values()), 2), "crew": crew, "crewSize": len(crew),
                       "materialCost": round(sum((m.get("cost") or 0) for m in mat), 2),
                       "materials": mat[:20]},
            "sold": sold_by_service.get(w.get("OpportunityServiceID"), [])[:20]})
    divisions = {}
    for j in jobs:
        divisions[j["division"] or "?"] = divisions.get(j["division"] or "?", 0) + 1
    out = {"pulled": time.strftime("%Y-%m-%dT%H:%M:%S"), "jobs": len(jobs), "divisions": divisions,
           "with_crew": sum(1 for j in jobs if j["actual"]["crewSize"]),
           "with_material_actuals": sum(1 for j in jobs if j["actual"]["materialCost"]),
           "with_sold_items": sum(1 for j in jobs if j["sold"]),
           "records": jobs}
    write_json(SHARED / "aspire-jobs.json", out)

    # regenerate the engine's actuals off the REAL division field (heuristic retired where possible)
    entries = []
    for j in jobs:
        div = (j["division"] or "").lower()
        est_h, act_h = j["est"]["hours"] or 0, j["actual"]["hours"]
        # quoting engine learns ONLY from install-scope divisions (their real org: Installation #N,
        # Fencing) — Maintenance/Service/Admin/Designs tickets are different work and would skew it
        if not ("install" in div or "fenc" in div):
            continue
        # AND a real estimate: live data showed nominal 1-hour placeholder estimates on some
        # tickets (Fence Install est 0.12d vs 2-11d actual) — placeholders poison calibration
        if est_h < 4 or act_h <= 0 or not (j["price"] or 0) > 0:
            continue
        entries.append({"id": "A" + str(j["ticket"]),
                        "name": f"{j['service'] or 'WT ' + str(j['ticket'])} — {j['division'] or '?'}",
                        "quotedMid": round(j["price"], 2), "final": round(j["invoiced"] or 0, 2),
                        "estDays": round(est_h / 8, 2), "actDays": round(act_h / 8, 2),
                        "closed": j["completed"], "source": "aspire"})
    if entries:
        write_json(SHARED / "actuals-aspire.json",
                   {"pulled": out["pulled"], "tickets_seen": len(tickets), "usable": len(entries),
                    "basis": "division-filtered (real DivisionName, maintenance excluded)", "entries": entries})
    return out


def aspire_pull_catalog():
    items = aspire_get("/CatalogItems", "$top=1000")
    if not isinstance(items, list):
        items = items.get("value", []) if isinstance(items, dict) else []
    slim = [{"name": i.get("ItemName"), "code": i.get("ItemCode"), "type": i.get("ItemType"),
             "cost": i.get("ItemCost"), "unit": i.get("PurchaseUnitTypeName"),
             "active": i.get("Active")} for i in items]
    out = {"pulled": time.strftime("%Y-%m-%dT%H:%M:%S"), "count": len(slim),
           "active": sum(1 for i in slim if i.get("active")), "items": slim}
    write_json(SHARED / "aspire-catalog.json", out)
    return out


def hubspot_pull():
    tok = ENV.get("HUBSPOT_TOKEN")
    if not tok:
        raise RuntimeError("HUBSPOT_TOKEN missing")
    def hs(path):
        req = urllib.request.Request("https://api.hubapi.com" + path,
            headers={"Authorization": "Bearer " + tok})
        code, body = http_json(req)
        if code != 200:
            raise RuntimeError(f"HubSpot GET {path} HTTP {code}: {str(body)[:120]}")
        return body
    deals = hs("/crm/v3/objects/deals?limit=100&properties=dealname,amount,dealstage,closedate,pipeline")
    def hs_opt(path):
        try:
            return hs(path)
        except RuntimeError:
            return {}  # scope not granted on the private app — tolerated, deals are the core
    contacts = hs_opt("/crm/v3/objects/contacts?limit=1")
    companies = hs_opt("/crm/v3/objects/companies?limit=1")
    stage_counts = {}
    for dl in deals.get("results", []):
        st = dl.get("properties", {}).get("dealstage", "?")
        stage_counts[st] = stage_counts.get(st, 0) + 1
    out = {"pulled": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "deals_fetched": len(deals.get("results", [])),
           "has_more_deals": bool(deals.get("paging")),
           "stages": stage_counts,
           "total_contacts_hint": contacts.get("total", None),
           "total_companies_hint": companies.get("total", None),
           "deals": [{"name": dl["properties"].get("dealname"), "amount": dl["properties"].get("amount"),
                      "stage": dl["properties"].get("dealstage"), "close": dl["properties"].get("closedate")}
                     for dl in deals.get("results", [])]}
    write_json(SHARED / "hubspot-snapshot.json", out)
    return out


# ---- survey reader: extract PRINTED dimensions from the uploaded plan (propose-only) ----
def survey_extract(pid):
    p = PROJ / f"{pid}.json"
    st = read_json(p, {})
    img = (st.get("plan", {}) or {}).get("img") or ""
    if not img.startswith("data:"):
        raise RuntimeError("no survey/plan image on this project — upload it on the Site tab first")
    head, _, data = img.partition(",")
    mime = head.split(":")[1].split(";")[0]
    key = ENV.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing")
    model = ENV.get("GEMINI_TEXT_MODEL") or "gemini-3.5-flash"
    prompt = ("You are reading a land survey / site plan image for a landscaping estimate. "
              "Extract ONLY dimensions explicitly printed as text on the document (property lines, "
              "setbacks, building walls, existing features). Convert each to decimal feet. "
              "Do NOT estimate, scale off the drawing, or infer anything that is not printed. "
              'Return STRICT JSON only: {"dimensions":[{"label":"what it measures","feet":<number>,'
              '"confidence":"high|medium|low"}]} — empty list if nothing is printed.')
    body = {"contents": [{"parts": [{"text": prompt},
                                    {"inline_data": {"mime_type": mime, "data": data}}]}],
            "generationConfig": {"response_mime_type": "application/json"}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    code, resp = http_json(req)
    if code != 200:
        raise RuntimeError(f"survey read HTTP {code}: {str(resp)[:150]}")
    txt = ""
    for c in resp.get("candidates", []):
        for part in c.get("content", {}).get("parts", []):
            txt += part.get("text") or ""
    txt = txt.strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        if txt.startswith("json"):
            txt = txt[4:]
    dims = json.loads(txt).get("dimensions", [])
    out = []
    for d in dims[:40]:
        try:
            ft = float(d.get("feet"))
        except (TypeError, ValueError):
            continue
        if ft > 0:
            out.append({"label": str(d.get("label", ""))[:80], "feet": round(ft, 2),
                        "confidence": d.get("confidence", "medium")})
    return out


# ---- design coverage: consult text vs designed elements — the "nothing vanishes" net ----
def design_coverage(text, elements):
    key = ENV.get("GEMINI_API_KEY")
    if not key:
        return []
    model = ENV.get("GEMINI_TEXT_MODEL") or "gemini-3.5-flash"
    prompt = ("Consult notes for a backyard design, and the list of elements already on the design board. "
              "List each PHYSICAL BUILT FEATURE (a structure, surface, or installed amenity) requested in the "
              "notes that is NOT represented by any listed element. Ignore: plant/material/color/finish choices, "
              "lighting, anything already covered by a listed element. Estimate a footprint in feet only if the "
              "notes imply one, else use 10x8. Also give a TYPICAL professionally-installed cost range in USD for "
              "the feature at that size in the southeastern US (conservative, round numbers) — it is shown as an "
              "allowance pending a real contractor quote, never as a final price. "
              'STRICT JSON: {"missing":[{"name":"...","width_ft":<n>,"depth_ft":<n>,"typical_low_usd":<n>,"typical_high_usd":<n>}]} — empty list if fully covered.\n\n'
              f"NOTES: {text[:2000]}\n\nELEMENTS ON THE BOARD: {', '.join(elements)[:1000] or '(none)'}")
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    code, resp = http_json(req)
    if code != 200:
        return []
    txt = "".join(part.get("text") or "" for c in resp.get("candidates", [])
                  for part in c.get("content", {}).get("parts", []))
    try:
        return [m for m in json.loads(txt).get("missing", [])[:8] if m.get("name")]
    except Exception:
        return []


# ---- allowance from Sample Client's own history: real prices for similar past work ----
def allowance_history(name):
    toks = [t for t in re.sub(r"[^a-z0-9 ]", " ", name.lower()).split() if len(t) > 3]
    if not toks:
        return None
    data = read_json(SHARED / "aspire-jobs.json", {})
    prices = []
    for r in data.get("records", []):
        hay = ((r.get("service") or "") + " " + (r.get("opportunity") or "")).lower()
        if any(t in hay for t in toks) and (r.get("price") or 0) > 500:
            prices.append(float(r["price"]))
    if len(prices) < 3:
        return None
    prices.sort()
    lo, hi = prices[len(prices) // 4], prices[(3 * len(prices)) // 4]
    return {"src": "history", "n": len(prices), "lo": round(lo), "hi": round(hi)}


# ---- HubSpot deal search: pull intake info the office already entered ----
def hubspot_search(q):
    tok = ENV.get("HUBSPOT_TOKEN")
    if not tok:
        raise RuntimeError("HUBSPOT_TOKEN missing")
    body = {"query": q, "limit": 5,
            "properties": ["dealname", "amount", "dealstage", "closedate", "pipeline", "description"]}
    req = urllib.request.Request("https://api.hubapi.com/crm/v3/objects/deals/search",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"}, method="POST")
    code, resp = http_json(req)
    if code != 200:
        raise RuntimeError(f"HubSpot search HTTP {code}: {str(resp)[:120]}")
    out = []
    for d in resp.get("results", []):
        p = d.get("properties", {})
        out.append({"id": d.get("id"), "dealname": p.get("dealname"), "amount": p.get("amount"),
                    "dealstage": p.get("dealstage"), "closedate": p.get("closedate"),
                    "description": (p.get("description") or "")[:500]})
    return out


# ---- self-serve render regeneration (on-site "update the render") ----
import base64


def project_image_b64(state_dict, render_state):
    """Pick the base image: newest render of the same state -> newest render -> first site photo."""
    proj = state_dict.get("project", {})
    renders = proj.get("renders", [])
    candidates = ([r for r in renders if r.get("state") == render_state] or renders)
    sources = [r.get("src", "") for r in candidates] + [p.get("src", "") for p in proj.get("photos", [])]
    for src in sources:
        if src.startswith("data:"):
            head, _, data = src.partition(",")
            mime = head.split(":")[1].split(";")[0]
            return mime, data, ("render" if src in [r.get("src") for r in candidates] else "photo")
        if src.startswith("assets/"):
            f = ROOT / src
            if f.exists():
                mime = "image/png" if f.suffix == ".png" else "image/jpeg"
                return mime, base64.b64encode(f.read_bytes()).decode(), "render"
    return None, None, None


def project_inspiration_b64(state_dict):
    """First client-supplied inspiration image, if any — used as a style reference (second input image)."""
    for i in state_dict.get("project", {}).get("inspiration", []) or []:
        src = i.get("src", "")
        if src.startswith("data:"):
            head, _, data = src.partition(",")
            return head.split(":")[1].split(";")[0], data
    return None, None


def project_photo_b64(state_dict):
    """The site PHOTO — the only honest base for a new design set. (Chaining off an older render
    leaked a koi pond from a previous option into 'Your Vision', 2026-08-19.)"""
    for p in state_dict.get("project", {}).get("photos", []) or []:
        src = p.get("src", "")
        if src.startswith("data:"):
            head, _, data = src.partition(",")
            return head.split(":")[1].split(";")[0], data
    return None, None


def generate_render_google(prompt, mime, img_b64, style=None):
    key = ENV.get("GEMINI_API_KEY")
    if not key:
        return None, "GEMINI_API_KEY missing from .env — self-serve regeneration not armed yet"
    model = ENV.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image"  # 2.5-image is closed to new projects (checked 2026-08-18)
    parts = [{"text": prompt}, {"inline_data": {"mime_type": mime, "data": img_b64}}]
    if style and style[1]:
        parts.append({"inline_data": {"mime_type": style[0], "data": style[1]}})
    body = {"contents": [{"parts": parts}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message", "")[:200]
        except Exception:
            msg = ""
        return None, f"image API HTTP {e.code}: {msg}"
    except Exception as e:
        return None, f"image API error: {e}"
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inline_data") or part.get("inlineData")
            if blob and blob.get("data"):
                return {"mime": blob.get("mime_type") or blob.get("mimeType") or "image/png",
                        "data": blob["data"]}, None
    return None, "image API returned no image (model may have refused — adjust the prompt)"


# ---- render SET generation: Day1 x2 angles + Year3 + Night, one button ----
SETGEN = {"running": False, "done": 0, "total": 0, "error": None}


def render_set_worker(pid, jobs):
    try:
        p = PROJ / f"{pid}.json"
        st0 = read_json(p, {})
        init_mime, init_b64 = project_photo_b64(st0)  # a SET always starts from the site photo, never an old render
        if not init_b64:
            init_mime, init_b64, _ = project_image_b64(st0, "day1")  # no photo at all → last resort
        style = project_inspiration_b64(st0)  # client vision reference, if dropped in
        chains = {}  # per-SET day1 result — each option's angle-B/year3/night chain from ITS OWN day1
        first_day1 = None  # the run's anchor: option 1 angle A — later options are add-only EDITS of it
        for job in jobs:
            sid = job.get("setId") or "_"
            if job.get("base") == "chain" and chains.get(sid):
                mime, img_b64 = chains[sid]
            elif job.get("base") == "first" and first_day1:
                mime, img_b64 = first_day1
            else:
                mime, img_b64 = init_mime, init_b64
            if not img_b64:
                SETGEN["error"] = "no base image"
                break
            result, err = generate_render_google(job["prompt"], mime, img_b64, style)
            if err and ("timed out" in err or "HTTP 5" in err):
                result, err = generate_render_google(job["prompt"], mime, img_b64, style)  # one retry on transient
            if err:
                SETGEN["error"] = err[:150]
                continue  # skip this image, keep the rest of the set
            if job.get("state") == "day1" and sid not in chains:
                chains[sid] = (result["mime"], result["data"])  # this option's later states share its layout
                if first_day1 is None:
                    first_day1 = chains[sid]
            st = read_json(p, {})
            st.setdefault("project", {}).setdefault("renders", []).insert(0, {
                "id": "g" + uuid.uuid4().hex[:8],
                "src": f"data:{result['mime']};base64,{result['data']}",
                "label": f"render set {time.strftime('%Y-%m-%d %H:%M')} — {job.get('angle','')}",
                "state": job.get("state", "day1"), "package": job.get("package") or "standard",
                "setId": job.get("setId"), "generated": True})
            st["_updated"] = time.time()
            write_json(p, st)
            SETGEN["done"] += 1
    finally:
        SETGEN["running"] = False


# ---- install calendar: scheduled WorkTickets grouped by week -> lightest upcoming week ----
def aspire_pull_schedule():
    import datetime as _dt
    today = _dt.date.today()
    horizon = today + _dt.timedelta(days=56)
    filt = f"ScheduledStartDate ge {today.isoformat()} and ScheduledStartDate le {horizon.isoformat()}".replace(" ", "%20")
    rows = _paginate("/WorkTickets", pages=3, extra=f"$filter={filt}")
    weeks = {}
    for t in rows:
        d = (t.get("ScheduledStartDate") or "")[:10]
        if not d:
            continue
        day = _dt.date.fromisoformat(d)
        monday = day - _dt.timedelta(days=day.weekday())
        w = weeks.setdefault(monday.isoformat(), {"tickets": 0, "hours": 0.0})
        w["tickets"] += 1
        w["hours"] += float(t.get("HoursEst") or 0)
    # lightest week by estimated hours, next 8 weeks including empty ones
    light, light_load = None, None
    for i in range(8):
        monday = (today - _dt.timedelta(days=today.weekday())) + _dt.timedelta(days=7 * (i + 1))
        load = weeks.get(monday.isoformat(), {}).get("hours", 0.0)
        if light_load is None or load < light_load:
            light, light_load = monday, load
    out = {"pulled": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "tickets_seen": len(rows), "weeks": weeks,
           "next_light_week": light.strftime("%b %-d") if light else None,
           "next_light_week_iso": light.isoformat() if light else None,
           "next_light_week_hours": round(light_load or 0, 1)}
    write_json(SHARED / "aspire-schedule.json", out)
    return out


# ---- cinematic tour: 8s Veo 3.1 video from the newest day-1 render (client's own key/billing) ----
TOURGEN = {"running": False, "error": None, "last": None}


def tour_worker(pid, prompt, set_id=None):
    try:
        p = PROJ / f"{pid}.json"
        st = read_json(p, {})
        mime = img_b64 = None
        if set_id:  # animate THIS option's own day-1 render
            for r in st.get("project", {}).get("renders", []):
                if r.get("setId") == set_id and r.get("state") == "day1" and r.get("src", "").startswith("data:"):
                    head, _, data = r["src"].partition(",")
                    mime, img_b64 = head.split(":")[1].split(";")[0], data
                    break
        if not img_b64:
            mime, img_b64, _ = project_image_b64(st, "day1")
        if not img_b64:
            TOURGEN["error"] = "no render or photo to animate"
            return
        key = ENV.get("GEMINI_API_KEY")
        model = ENV.get("VEO_MODEL") or "veo-3.1-fast-generate-preview"
        body = {"instances": [{"prompt": prompt,
                               "image": {"bytesBase64Encoded": img_b64, "mimeType": mime}}],
                "parameters": {"aspectRatio": "16:9"}}
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
        code, resp = http_json(req)
        if code != 200:
            TOURGEN["error"] = f"tour start HTTP {code}: {str(resp)[:200]}"
            return
        op = resp.get("name")
        video_uri = None
        for _ in range(60):  # up to ~5 min
            time.sleep(5)
            pr = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/{op}",
                headers={"x-goog-api-key": key})
            code, opr = http_json(pr)
            if code != 200:
                TOURGEN["error"] = f"tour poll HTTP {code}: {str(opr)[:150]}"
                return
            if opr.get("done"):
                err = opr.get("error")
                if err:
                    TOURGEN["error"] = f"tour failed: {str(err)[:200]}"
                    return
                samples = (opr.get("response", {}).get("generateVideoResponse", {})
                           .get("generatedSamples", []))
                if samples:
                    video_uri = samples[0].get("video", {}).get("uri")
                break
        if not video_uri:
            TOURGEN["error"] = TOURGEN["error"] or "tour timed out or returned no video"
            return
        dl = urllib.request.Request(video_uri, headers={"x-goog-api-key": key})
        with urllib.request.urlopen(dl, timeout=120) as r:
            data = r.read()
        tours_dir = SHARED / "tours"
        tours_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{pid}-{int(time.time())}.mp4"
        (tours_dir / fname).write_bytes(data)
        st = read_json(p, {})
        st.setdefault("project", {}).setdefault("tours", []).insert(0, {
            "id": "t" + uuid.uuid4().hex[:8],
            "src": f"data/shared/tours/{fname}", "setId": set_id,
            "label": f"cinematic tour {time.strftime('%Y-%m-%d %H:%M')}"})
        st["_updated"] = time.time()
        write_json(p, st)
        TOURGEN["last"] = fname
    except Exception as e:
        TOURGEN["error"] = str(e)[:200]
    finally:
        TOURGEN["running"] = False


# ---- shared sub contacts (email per sub, editable from the platform) ----
def sub_contacts():
    return read_json(SHARED / "sub-contacts.json", {})


# ---- render-queue drain: with a live image key, queued requests process themselves ----
DRAIN = {"running": False}


def drain_render_queue():
    try:
        qp = SHARED / "render-queue.json"
        q = read_json(qp, [])
        for entry in q:
            if entry.get("status") != "pending":
                continue
            pid = entry.get("projectId", "")
            p = (PROJ / f"{pid}.json") if ID_RE.match(pid or "") else None
            if not (p and p.exists() and entry.get("prompt")):
                entry["status"] = "error"
                entry["result"] = "project missing or empty prompt"
                continue
            st = read_json(p, {})
            mime, img_b64, basis = project_image_b64(st, entry.get("state", "day1"))
            if not img_b64:
                entry["status"] = "error"
                entry["result"] = "no base image in project"
                continue
            result, err = generate_render_google(entry["prompt"], mime, img_b64, project_inspiration_b64(st))
            if err:
                entry["status"] = "error" if "missing" not in err else "pending"
                entry["result"] = err[:150]
                if "missing" in err:
                    break  # no key — stop draining, stay queued
                continue
            rid = "g" + uuid.uuid4().hex[:8]
            st.setdefault("project", {}).setdefault("renders", []).insert(0, {
                "id": rid, "src": f"data:{result['mime']};base64,{result['data']}",
                "label": f"queue-drained generation {time.strftime('%Y-%m-%d %H:%M')} (from {basis})",
                "state": entry.get("state", "day1"), "package": entry.get("package") or "standard",
                "generated": True})
            st["_updated"] = time.time()
            write_json(p, st)
            entry["status"] = "done"
            entry["completed"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            entry["result"] = rid + " in project"
        write_json(qp, q)
    finally:
        DRAIN["running"] = False


def kick_drain():
    if not DRAIN["running"] and ENV.get("GEMINI_API_KEY"):
        DRAIN["running"] = True
        threading.Thread(target=drain_render_queue, daemon=True).start()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    # ---- helpers ----
    def send_api(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 50 * 1024 * 1024:
            return None
        try:
            return json.loads(self.rfile.read(n))
        except Exception:
            return None

    def project_path(self, pid):
        return (PROJ / f"{pid}.json") if ID_RE.match(pid or "") else None

    # ---- routes ----
    def end_headers(self):
        # html/js/data-json must never be cached — stale UI/config bit four times (missing buttons, old
        # pills, missing porch allowance, and deep-linked pages: ?query strings dodged this check entirely)
        p = self.path.split("?")[0]
        if p.endswith((".html", ".json", "/")) or p.count(".") == 0:
            self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/projects":
            out = []
            for f in sorted(PROJ.glob("*.json")):
                s = read_json(f, {})
                p = s.get("project", {})
                out.append({"id": f.stem, "name": p.get("client") or f.stem,
                            "address": p.get("address", ""), "stage": p.get("stage", "pitch"),
                            "updated": s.get("_updated", 0)})
            out.sort(key=lambda r: -r["updated"])
            return self.send_api(out)
        m = re.match(r"^/api/projects/([a-z0-9-]+)$", self.path)
        if m:
            p = self.project_path(m.group(1))
            if p and p.exists():
                return self.send_api(read_json(p, {}))
            return self.send_api({"error": "not found"}, 404)
        if self.path == "/api/actuals":
            manual = read_json(SHARED / "actuals.json", [])
            aspire = read_json(SHARED / "actuals-aspire.json", {}).get("entries", [])
            return self.send_api(aspire + manual)
        if self.path == "/api/aspire/summary":
            a = read_json(SHARED / "actuals-aspire.json", {})
            c = read_json(SHARED / "aspire-catalog.json", {})
            return self.send_api({"actuals": {k: a.get(k) for k in ("pulled", "tickets_seen", "usable")},
                                  "catalog": {k: c.get(k) for k in ("pulled", "count", "active")}})
        if self.path == "/api/hubspot/summary":
            h = read_json(SHARED / "hubspot-snapshot.json", {})
            return self.send_api({k: h.get(k) for k in ("pulled", "deals_fetched", "stages")})
        if self.path == "/api/render-queue":
            return self.send_api(read_json(SHARED / "render-queue.json", []))
        if self.path == "/api/aspire/schedule":
            return self.send_api(read_json(SHARED / "aspire-schedule.json", {}))
        if self.path == "/api/portfolio":
            return self.send_api(read_json(SHARED / "portfolio.json", []))
        if self.path == "/api/render/set/status":
            return self.send_api(dict(SETGEN))
        if self.path == "/api/render/tour/status":
            return self.send_api(dict(TOURGEN))
        if self.path == "/api/subs-contacts":
            return self.send_api(sub_contacts())
        if self.path == "/api/integrations/status":
            st = integration_status()
            st["shepherds"] = {"kind": "public-site", "credentials": True, "missing": [], **shepherds_summary()}
            return self.send_api(st)
        if self.path == "/api/availability/shepherds":
            return self.send_api(read_json(SHARED / "availability-shepherds.json", {"items": []}))
        m = re.match(r"^/api/integrations/test/([a-z]+)$", self.path)
        if m:
            return self.send_api(test_integration(m.group(1)))
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/projects":
            data = self.body_json() or {}
            pid = "p" + uuid.uuid4().hex[:8]
            state = data.get("state") or {}
            state["_updated"] = time.time()
            write_json(PROJ / f"{pid}.json", state)
            return self.send_api({"id": pid})
        if self.path == "/api/actuals":
            entry = self.body_json()
            if not isinstance(entry, dict):
                return self.send_api({"error": "bad entry"}, 400)
            arr = read_json(SHARED / "actuals.json", [])
            arr.append(entry)
            write_json(SHARED / "actuals.json", arr)
            return self.send_api({"ok": True, "n": len(arr)})
        if self.path == "/api/aspire/pull":
            try:
                r = aspire_pull_actuals()
                return self.send_api({"ok": True, **{k: r[k] for k in ("tickets_seen", "time_entries_seen", "usable", "small_maintenance_excluded", "install_scale_missing_time_data")}})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/aspire/deep-pull":
            try:
                r = aspire_deep_pull()
                return self.send_api({"ok": True, **{k: r[k] for k in ("jobs", "divisions", "with_crew", "with_material_actuals", "with_sold_items")}})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/aspire/catalog-pull":
            try:
                r = aspire_pull_catalog()
                return self.send_api({"ok": True, "count": r["count"], "active": r["active"]})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/aspire/schedule-pull":
            try:
                r = aspire_pull_schedule()
                return self.send_api({"ok": True, **{k: r[k] for k in ("tickets_seen", "next_light_week", "next_light_week_hours")}})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/hubspot/pull":
            try:
                r = hubspot_pull()
                return self.send_api({"ok": True, "deals_fetched": r["deals_fetched"], "stages": r["stages"]})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/render/set":
            body = self.body_json() or {}
            pid, jobs = body.get("projectId"), body.get("jobs", [])
            p = self.project_path(pid or "")
            if not (p and p.exists() and jobs):
                return self.send_api({"error": "need projectId + jobs"}, 400)
            if SETGEN["running"]:
                return self.send_api({"error": "a render set is already running"}, 409)
            if not ENV.get("GEMINI_API_KEY"):
                return self.send_api({"error": "GEMINI_API_KEY missing — set not armed"}, 503)
            SETGEN.update(running=True, done=0, total=len(jobs), error=None)
            threading.Thread(target=render_set_worker, args=(pid, jobs), daemon=True).start()
            return self.send_api({"ok": True, "total": len(jobs)})
        if self.path == "/api/subs-contacts":
            body = self.body_json() or {}
            c = sub_contacts()
            c.update({k: str(v)[:200] for k, v in body.items()})
            write_json(SHARED / "sub-contacts.json", c)
            return self.send_api({"ok": True})
        if self.path == "/api/allowance/history":
            body = self.body_json() or {}
            return self.send_api({"match": allowance_history(body.get("name") or "")})
        if self.path == "/api/design/coverage":
            body = self.body_json() or {}
            return self.send_api({"missing": design_coverage(body.get("text") or "", body.get("elements") or [])})
        if self.path == "/api/portfolio":
            entry = self.body_json()
            if not isinstance(entry, dict) or not entry.get("title"):
                return self.send_api({"error": "bad entry"}, 400)
            arr = read_json(SHARED / "portfolio.json", [])
            entry["id"] = "pf" + uuid.uuid4().hex[:8]
            entry["ts"] = time.time()
            arr.insert(0, entry)
            write_json(SHARED / "portfolio.json", arr)
            return self.send_api({"ok": True, "id": entry["id"], "count": len(arr)})
        if self.path == "/api/survey/extract":
            body = self.body_json() or {}
            p = self.project_path(body.get("projectId") or "")
            if not (p and p.exists()):
                return self.send_api({"error": "bad projectId"}, 400)
            try:
                return self.send_api({"ok": True, "dimensions": survey_extract(body["projectId"])})
            except Exception as e:
                return self.send_api({"error": str(e)[:200]}, 502)
        if self.path == "/api/hubspot/search":
            body = self.body_json() or {}
            q = (body.get("q") or "").strip()
            if not q:
                return self.send_api({"error": "empty query"}, 400)
            try:
                return self.send_api({"ok": True, "results": hubspot_search(q)})
            except Exception as e:
                return self.send_api({"ok": False, "error": str(e)[:200]}, 502)
        if self.path == "/api/render/tour":
            body = self.body_json() or {}
            pid = body.get("projectId")
            p = self.project_path(pid or "")
            if not (p and p.exists()):
                return self.send_api({"error": "bad projectId"}, 400)
            if TOURGEN["running"]:
                return self.send_api({"error": "a tour is already rendering"}, 409)
            if not ENV.get("GEMINI_API_KEY"):
                return self.send_api({"error": "GEMINI_API_KEY missing"}, 503)
            prompt = body.get("prompt") or ("Slow cinematic camera glide through this finished backyard design, "
                "golden-hour light, gentle breeze in the plants, photoreal, no people, no text.")
            TOURGEN.update(running=True, error=None)
            threading.Thread(target=tour_worker, args=(pid, prompt, body.get("setId")), daemon=True).start()
            return self.send_api({"ok": True})
        if self.path == "/api/render/generate":
            body = self.body_json() or {}
            pid, state, prompt = body.get("projectId"), body.get("state", "day1"), body.get("prompt", "")
            p = self.project_path(pid or "")
            if not (p and p.exists() and prompt):
                return self.send_api({"error": "need projectId + prompt"}, 400)
            st = read_json(p, {})
            mime, img_b64, basis = project_image_b64(st, state)
            if not img_b64:
                return self.send_api({"error": "project has no site photo or render to work from — upload a photo first"}, 400)
            result, err = generate_render_google(prompt, mime, img_b64, project_inspiration_b64(st))
            if err:
                code = 503 if "missing" in err else 502
                return self.send_api({"error": err}, code)
            entry = {"id": "g" + uuid.uuid4().hex[:8],
                     "src": f"data:{result['mime']};base64,{result['data']}",
                     "label": f"self-serve regeneration {time.strftime('%Y-%m-%d %H:%M')} (from {basis})",
                     "state": state, "package": body.get("package") or "standard", "generated": True}
            st.setdefault("project", {}).setdefault("renders", []).insert(0, entry)
            st["_updated"] = time.time()
            write_json(p, st)
            return self.send_api({"ok": True, "id": entry["id"], "basis": basis})
        if self.path == "/api/integrations/pull/shepherds":
            if SHEP["running"]:
                return self.send_api({"ok": False, "detail": "pull already running"})
            body = self.body_json() or {}
            limit = body.get("limit")
            SHEP["running"] = True
            threading.Thread(target=shepherds_pull, args=(limit,), daemon=True).start()
            return self.send_api({"ok": True, "detail": f"pull started ({'first '+str(limit) if limit else 'all'} products, 1 req/sec — polite)"})
        if self.path == "/api/render-queue":
            req = self.body_json()
            if not isinstance(req, dict):
                return self.send_api({"error": "bad request"}, 400)
            req["queued"] = time.time()
            req["status"] = "pending"
            arr = read_json(SHARED / "render-queue.json", [])
            arr.append(req)
            write_json(SHARED / "render-queue.json", arr)
            kick_drain()  # with a live key the queue drains itself
            return self.send_api({"ok": True, "position": len(arr)})
        return self.send_api({"error": "no route"}, 404)

    def do_PUT(self):
        m = re.match(r"^/api/projects/([a-z0-9-]+)$", self.path)
        if m:
            p = self.project_path(m.group(1))
            state = self.body_json()
            if p is None or not isinstance(state, dict):
                return self.send_api({"error": "bad request"}, 400)
            if not p.exists():
                # projects are born via POST only — a stale tab's debounced save must not
                # resurrect a deleted project (bit us 2026-08-19: QA projects came back from the dead)
                return self.send_api({"error": "project deleted"}, 404)
            # A browser tab holds a full copy of the state, so a save from a stale tab would
            # silently erase renders/tours the set worker wrote in the meantime (bit us
            # 2026-08-19: two Day-1 angles lost mid-set). Server-written media is therefore
            # merge-protected: only an explicit tombstone (client delete) removes it.
            if p.exists():
                old = read_json(p, {})
                tomb = set(state.get("tombstones") or [])
                for key in ("renders", "tours"):
                    oldm = old.get("project", {}).get(key, [])
                    cur = state.setdefault("project", {}).setdefault(key, [])
                    have = {r.get("id") for r in cur}
                    rescued = [r for r in oldm
                               if (r.get("generated") or key == "tours")
                               and r.get("id") not in have and r.get("id") not in tomb]
                    cur[:0] = rescued
            state["_updated"] = time.time()
            write_json(p, state)
            return self.send_api({"ok": True})
        return self.send_api({"error": "no route"}, 404)

    def do_DELETE(self):
        m = re.match(r"^/api/projects/([a-z0-9-]+)$", self.path)
        if m:
            p = self.project_path(m.group(1))
            if p and p.exists():
                p.unlink()
                return self.send_api({"ok": True})
            return self.send_api({"error": "not found"}, 404)
        return self.send_api({"error": "no route"}, 404)

    def log_message(self, fmt, *args):
        pass  # keep preview logs quiet


if __name__ == "__main__":
    print(f"Sample Client platform server on :{PORT} (static + /api)")
    kick_drain()  # process any renders queued while the key was absent
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
