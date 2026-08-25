#!/usr/bin/env python3
"""The Finance view — the financial model, mirrored into HQ.

HQ does not compute the model and does not edit it. `finance/yourco-financial-model.xlsx`
holds ~6,800 formulas and only a spreadsheet engine can evaluate them; this view renders
what `runtime/finance_model_sync.py` extracted.

The load-bearing part is `stale`. HQ knows the sha256 of the workbook it was synced from
and re-hashes the live file on every request, so it can always say whether what it is
showing still matches reality — and it says so loudly rather than serving old numbers as
if they were current. Same principle as the Board's freshness strip: a stale source is
shown, never silently trusted.
"""
import json, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
SNAP = os.path.join(ROOT, "dashboard", "finance_model.json")
XLSX = os.path.join(ROOT, "finance", "yourco-financial-model.xlsx")


def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    if not os.path.exists(SNAP):
        return {"error": "never synced",
                "fix": "python3 runtime/finance_model_sync.py",
                "note": ("HQ mirrors the workbook and has no copy of its own. Until the sync runs "
                         "there is nothing to show — which is the correct state, not a bug.")}
    data = json.load(open(SNAP))
    src = data.get("source") or {}

    stale, why = False, None
    if not os.path.exists(XLSX):
        stale, why = True, "the workbook is missing from the repo"
    else:
        live = _digest(XLSX)
        if live != src.get("sha256"):
            stale = True
            why = ("the workbook has changed since HQ was last synced — these figures are from the "
                   "previous version")
    data["stale"] = stale
    data["staleReason"] = why
    data["fix"] = "python3 runtime/finance_model_sync.py" if stale else None
    data["editNote"] = ("Assumptions can be edited here. HQ writes the value into the workbook and marks "
                        "the model PENDING RECALCULATION — it does not compute the consequences, because "
                        "the machine serving HQ has no spreadsheet engine for the other ~6,800 formulas. "
                        "Until the recalculation runs, every figure below predates the pending edits and "
                        "says so.")

    # Pending edits: values already written into the workbook whose consequences have
    # NOT been computed. While any exist, every figure on this page is pre-edit — which
    # the UI must say, or the edit box becomes a lie.
    try:
        import sys as _s
        _s.path.insert(0, os.path.join(ROOT, "runtime"))
        import finance_model_edit as fme
        pend = fme.load_pending()
        data["pending"] = pend.get("edits", [])
        data["pendingSince"] = pend.get("since")
        data["pendingFix"] = "python3 runtime/finance_model_recalc.py"
        cur = fme.read_current()          # one workbook read, not one per field
        data["editable"] = [
            {"key": k, "label": human, "kind": kind, "min": lo, "max": hi, "value": cur.get(k)}
            for k, (label, col, kind, lo, hi, human) in fme.EDITABLE.items()]
    except Exception as e:
        data["pending"], data["editable"] = [], []
        data["editError"] = f"editing unavailable: {e}"
    return data


if __name__ == "__main__":
    print(json.dumps(build(), indent=2)[:1500])
