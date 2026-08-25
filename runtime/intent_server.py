#!/usr/bin/env python3
"""yourco — interactive intent board (the 1-click push). the Founder clicks; the agent does the labor.

Serves a scored intent file (intent-<vertical>.json from intent_collect.py) as a clickable board with
two actions, both honoring the CONTACT-INFO GATE (decisions/2026-06-15_prospect-data-architecture.md):

  • Add to CRM  → only records that HAVE contact info (phone/email). David creates the lead. No-contact
                  signals are refused (they belong in the engagement/reply queue, not the CRM).
  • Enrich → stage to Instantly → records with an email are staged into the cold campaign (Reilly,
                  staging only, never sends); no-email records are reported as "needs enrichment first".

Pure stdlib http.server — no install. Local tool; the human triggers it, the agent runs the action.

Usage:
  python3 runtime/intent_server.py intent-landscaping.json --campaign "Intent — Landscaping"
  → open http://localhost:8799
"""
import os, sys, json, re, datetime, http.server, socketserver, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "dashboard"))
import intent_collect as ic  # scoring

PORT = int(os.environ.get("INTENT_PORT", "8799"))
RECORDS, CAMPAIGN = [], ""


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _has_contact(r):
    return bool(r.get("email") or r.get("phone"))


def _add_to_crm(records):
    """David: add contact-bearing records as 'lead to work'. Dedup by domain/email/name. Returns report."""
    crm = json.load(open(CRM))
    comps, conts, deals = crm.setdefault("companies", []), crm.setdefault("contacts", []), crm.setdefault("deals", [])
    dom = {(c.get("domain") or "").lower() for c in comps if c.get("domain")}
    nm = {_norm(c.get("name", "")) for c in comps}
    em = {(p.get("email") or "").lower() for p in conts if p.get("email")}

    def nid(p, items):
        n = max([int(re.sub(r"\D", "", x.get("id", "")) or 0) for x in items if x.get("id", "").startswith(p)] + [0])
        return f"{p}{n+1}"

    today = datetime.date.today().isoformat()
    added, skipped, dup = [], [], []
    for r in records:
        if not _has_contact(r):
            skipped.append(r.get("name") or r.get("intent", {}).get("signal", "")[:30]); continue
        namekey = _norm(r.get("name", "") or r.get("intent", {}).get("platform", ""))
        if (r.get("email", "").lower() in em and r.get("email")) or (namekey and namekey in nm):
            dup.append(r.get("name", "")); continue
        cid = nid("c", comps)
        comps.append({"id": cid, "name": r.get("name") or "(intent lead)", "vertical": r.get("vertical", ""),
                      "size": "", "location": "", "domain": r.get("domain", ""), "phone": r.get("phone", ""),
                      "source": "intent: " + r.get("intent", {}).get("platform", ""),
                      "status": "intent lead — to qualify", "owner": "Reilly"})
        if r.get("email") or r.get("phone"):
            conts.append({"id": nid("p", conts), "name": r.get("name", ""), "companyId": cid, "role": "",
                          "email": r.get("email", ""), "phone": r.get("phone", ""), "lastTouch": today,
                          "status": "intent — found"})
        deals.append({"id": nid("d", deals), "name": f"{r.get('name','intent')} — intent", "companyId": cid,
                      # `prospect` was retired from the ladder in the 2026-08-07 restructure;
                      # every row this created would have landed off the board. Fixed 2026-08-25.
                      "useCase": "TBD — qualify", "stage": "pre-convo", "value": 0,
                      "nextAction": "Qualify the intent signal: " + r.get("intent", {}).get("signal", "")[:80],
                      "nextDate": "", "lastTouch": "", "owner": "Reilly", "stageSince": today,
                      "stageHistory": [{"stage": "pre-convo", "at": today, "source": "recorded"}],
                      "intentUrl": r.get("intent", {}).get("url", "")})
        added.append(r.get("name", "")); nm.add(namekey)
    json.dump(crm, open(CRM, "w"), indent=2, ensure_ascii=False)
    try:
        import melanie; melanie.write_mirror(crm)
    except Exception:
        pass
    return {"added": added, "skipped_no_contact": skipped, "dup": dup}


def _stage_instantly(records):
    """Reilly: stage email-bearing records into the cold campaign (never sends). No email → needs enrichment."""
    if not CAMPAIGN:
        return {"error": "no --campaign set when the server started"}
    try:
        import sourcing
        return sourcing.stage_into_instantly(records, CAMPAIGN, dry_run=False)
    except Exception as e:
        return {"error": str(e)}


PRIO = ic._PRIO


def board_html():
    recs = RECORDS
    rows = []
    for i, r in enumerate(recs):
        it = r.get("intent", {})
        contact = (r.get("email") or r.get("phone") or "")
        url = it.get("url", "")
        link = f'<a href="{ic._esc(url)}" target=_blank>↗</a>' if url else ""
        contact_cell = ic._esc(contact) if contact else "<span class=no>—</span>"
        rows.append(
            f'<tr data-i="{i}" data-contact="{1 if contact else 0}" data-email="{1 if r.get("email") else 0}">'
            f'<td><input type=checkbox class=sel data-i="{i}"></td>'
            f'<td class=h>{r.get("heat",0)}</td><td class=k>{ic._esc(r.get("klass",""))}</td>'
            f'<td class=p>{ic._esc(it.get("platform",""))}</td><td class=nm>{ic._esc(r.get("name") or "—")}</td>'
            f'<td class=ct>{contact_cell}</td>'
            f'<td class=sig>{ic._esc(it.get("signal",""))[:140]}</td>'
            f'<td>{link}</td></tr>')
    body = "\n".join(rows)
    return f"""<!DOCTYPE html><html><head><meta charset=utf-8><title>Intent board — push</title><style>
body{{font:14px/1.5 -apple-system,Segoe UI,Inter,sans-serif;margin:0;background:#12162b;color:#1a1a1a}}
.wrap{{max-width:1100px;margin:0 auto;padding:18px}} header{{color:#F4EFE6;padding:6px 0 14px}}
h1{{margin:0;font-size:20px}} .sub{{color:#9aa;font-size:13px}}
.bar{{position:sticky;top:0;background:#161B33;padding:12px;border-radius:10px;margin-bottom:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.btn{{background:#B8965A;color:#1a1d2e;border:0;font-weight:700;padding:9px 16px;border-radius:8px;cursor:pointer}}
.btn.alt{{background:#4F6B4A;color:#fff}} .bar .n{{color:#F4EFE6;font-size:13px}}
.card{{background:#F4EFE6;border-radius:12px;padding:8px 14px}}
table{{width:100%;border-collapse:collapse}} td,th{{padding:7px 6px;border-bottom:1px solid #e7ddc9;font-size:13px;text-align:left;vertical-align:top}}
th{{font-size:11px;text-transform:uppercase;color:#888}} .h{{font-weight:700;color:#4F6B4A;text-align:center;width:32px}}
.k{{font-size:11px;color:#7a5}} .p{{font-size:11px;color:#789;white-space:nowrap}} .nm{{font-weight:600;max-width:130px}}
.ct{{font-size:12px;white-space:nowrap}} .no{{color:#c44}} .sig{{color:#333}} a{{color:#B8965A}}
#out{{background:#161B33;color:#cfe;border-radius:10px;padding:12px;margin-top:10px;white-space:pre-wrap;font-size:12.5px;display:none}}
</style></head><body><div class=wrap>
<header><h1>🛰️ Intent board — push</h1><div class=sub>{len(recs)} signals · campaign: <b>{ic._esc(CAMPAIGN) or "—"}</b> · contact-info gate enforced</div></header>
<div class=bar>
  <button class=btn onclick="pick('contact')">Select all w/ contact</button>
  <button class=btn onclick="pick('all')">All</button><button class=btn onclick="pick('none')">None</button>
  <span style="flex:1"></span>
  <button class="btn alt" onclick="act('add-crm')">→ Add selected to CRM</button>
  <button class=btn onclick="act('stage-instantly')">→ Enrich + stage to Instantly</button>
</div>
<div class=card><table>
<tr><th></th><th>heat</th><th>class</th><th>src</th><th>name</th><th>contact</th><th>signal</th><th></th></tr>
{body}
</table></div>
<div id=out></div></div>
<script>
function pick(m){{document.querySelectorAll('.sel').forEach(c=>{{const tr=c.closest('tr');
  c.checked = m==='all'?true : m==='none'?false : tr.dataset.contact==='1';}});}}
async function act(ep){{
  const ids=[...document.querySelectorAll('.sel:checked')].map(c=>+c.dataset.i);
  if(!ids.length){{alert('Select some rows first.');return;}}
  const out=document.getElementById('out'); out.style.display='block'; out.textContent='Working… the agent is on it.';
  const r=await fetch('/'+ep,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{indices:ids}})}});
  out.textContent=JSON.stringify(await r.json(),null,2);
}}
</script></body></html>"""


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.end_headers(); self.wfile.write(body.encode())

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, board_html(), "text/html")
        else:
            self._send(404, "{}")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            idx = json.loads(self.rfile.read(n) or "{}").get("indices", [])
            sel = [RECORDS[i] for i in idx if 0 <= i < len(RECORDS)]
        except Exception as e:
            return self._send(400, json.dumps({"error": str(e)}))
        if self.path == "/add-crm":
            self._send(200, json.dumps(_add_to_crm(sel)))
        elif self.path == "/stage-instantly":
            self._send(200, json.dumps(_stage_instantly(sel)))
        else:
            self._send(404, "{}")


if __name__ == "__main__":
    args = sys.argv[1:]
    path = next((a for a in args if a.endswith(".json")), None)
    if not path or not os.path.exists(path):
        print("usage: python3 runtime/intent_server.py intent-<vertical>.json [--campaign \"Intent — X\"]"); sys.exit(1)
    RECORDS = json.load(open(path))
    for r in RECORDS:
        ic.score_record(r)
    RECORDS.sort(key=lambda r: (PRIO.get(r.get("klass"), 9), -r.get("heat", 0)))
    CAMPAIGN = args[args.index("--campaign") + 1] if "--campaign" in args else ""
    print(f"Intent board: http://localhost:{PORT}  ({len(RECORDS)} signals, campaign: {CAMPAIGN or '—'})")
    print("Buttons run as the agent (David adds to CRM / Reilly stages to Instantly). Contact-info gate enforced. Ctrl-C to stop.")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), H) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
