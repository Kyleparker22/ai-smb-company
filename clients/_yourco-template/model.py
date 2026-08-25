#!/usr/bin/env python3
"""yourco — the model seam. One place a client OS decides which model runs which task.

WHY THIS EXISTS
    CLAUDE.md promises a **model-upgrade dividend**: "every model/tooling improvement flows
    to the client as a free upgrade — the offering appreciates as AI advances." That is only
    true if models can actually be swapped. Before this file, every client build called a
    provider directly with the model ID inline, so "upgrade the client" meant grepping for
    string literals — and in practice it didn't happen (the first shipped client agent sat
    pinned to a superseded model for months). One seam, one config file, one edit.

    It also buys two things the inline pattern can't:
      • FAILOVER — a single-vendor outage otherwise takes a client's OS down, and yourco owns
        the reliability promise. Candidates are tried in order.
      • COST ROUTING — cheap models for mechanical work. This lands directly on margin,
        because yourco absorbs 100% of the token spend (CLAUDE.md §Token economics).

WHAT IT IS NOT
    Not a framework, not an AI gateway product, not a second agent runtime. A wrench, not a
    workshop (`decisions/2026-06-14_framework-adoption-stance.md`). No third-party deps: the
    official `anthropic` SDK is used when it happens to be installed, otherwise raw HTTPS, so
    a client box runs the moment keys are present with no `pip install` step.

USE
    from model import ask
    text, meta = ask("draft", "Write the follow-up email.", system="You are ...")
    # meta -> {"provider": "anthropic", "model": "claude-opus-5", "attempts": [...],
    #          "input_tokens": 812, "output_tokens": 240}

    Callers name a TASK, never a model. Adding a task or changing which model serves it is an
    edit to model-routing.json — no code change, no grep.

KEYS (env, or the gitignored env file named in the config; never in the browser, never in git)
    ANTHROPIC_API_KEY   Claude
    GEMINI_API_KEY      Gemini (already used for Design Studio image generation)

HONESTY RULE (house standard)
    With no key, or when every candidate fails, this RAISES. It never returns invented text
    and never silently degrades to a stub — a client surface that fabricates on failure is
    worse than one that reports it. Callers decide what the human sees.
"""
import os
import json
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "model-routing.json")
ANTHROPIC_VERSION = "2023-06-01"


class ModelError(RuntimeError):
    """Every candidate for a task failed, or none was configured. Carries per-attempt detail."""


# ---- config + keys ---------------------------------------------------------
def _config():
    with open(CONFIG) as f:
        return json.load(f)


def _load_env_file(cfg):
    """Read KEY=value lines from the gitignored env file, without overriding real env vars."""
    path = cfg.get("env_file")
    if not path:
        return
    path = path if os.path.isabs(path) else os.path.join(HERE, path)
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _key(name, cfg):
    _load_env_file(cfg)
    return (os.environ.get(name) or "").strip()


def candidates_for(task, cfg=None):
    """The ordered candidate list for a task, falling back to the config's default task."""
    cfg = cfg or _config()
    routes = cfg.get("routes", {})
    if task in routes:
        return routes[task]
    default = cfg.get("default_task")
    if default and default in routes:
        return routes[default]
    raise ModelError(
        f"task {task!r} is not in {os.path.basename(CONFIG)} and no usable default_task is set. "
        f"Known tasks: {', '.join(sorted(routes)) or '(none)'}"
    )


# ---- providers -------------------------------------------------------------
def _post(url, body, headers, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _anthropic(cand, prompt, system, max_tokens, timeout, cfg):
    """Claude. Prefers the official SDK when installed; raw HTTPS otherwise (same request)."""
    api_key = _key("ANTHROPIC_API_KEY", cfg)
    if not api_key:
        raise ModelError("ANTHROPIC_API_KEY is not set")

    body = {"model": cand["model"], "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    # effort is how depth/cost is controlled on current models. Do NOT send temperature,
    # top_p, top_k or thinking.budget_tokens — all are rejected (400) on the current
    # Claude models, and effort replaces the old thinking-budget concept.
    if cand.get("effort"):
        body["output_config"] = {"effort": cand["effort"]}

    try:
        import anthropic  # optional; used when the box happens to have it
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(**body)
        text = "".join(b.text for b in msg.content if b.type == "text")
        usage = msg.usage
        return text, getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0)
    except ImportError:
        pass

    data = _post(
        "https://api.anthropic.com/v1/messages", body,
        {"content-type": "application/json", "x-api-key": api_key,
         "anthropic-version": ANTHROPIC_VERSION},
        timeout,
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    u = data.get("usage", {}) or {}
    return text, u.get("input_tokens", 0), u.get("output_tokens", 0)


def _gemini(cand, prompt, system, max_tokens, timeout, cfg):
    """Gemini. Already in use for Design Studio image generation — same key, same posture."""
    api_key = _key("GEMINI_API_KEY", cfg)
    if not api_key:
        raise ModelError("GEMINI_API_KEY is not set")

    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    data = _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{cand['model']}:generateContent",
        body, {"content-type": "application/json", "x-goog-api-key": api_key}, timeout,
    )
    parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", []) or []
    text = "".join(p.get("text", "") for p in parts)
    u = data.get("usageMetadata", {}) or {}
    return text, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0)


PROVIDERS = {"anthropic": _anthropic, "gemini": _gemini}


# ---- the seam --------------------------------------------------------------
def ask(task, prompt, system=None, max_tokens=None, cfg=None):
    """Run `task` against its configured candidates in order. Returns (text, meta).

    Raises ModelError if every candidate fails — with each attempt's error, so a failure is
    diagnosable rather than mysterious. Never returns fabricated text.
    """
    cfg = cfg or _config()
    cands = candidates_for(task, cfg)
    timeout = cfg.get("timeout_seconds", 120)
    attempts = []

    for cand in cands:
        provider = PROVIDERS.get(cand.get("provider"))
        if not provider:
            attempts.append({"model": cand.get("model"), "error": f"unknown provider {cand.get('provider')!r}"})
            continue
        started = time.time()
        try:
            text, tin, tout = provider(
                cand, prompt, system, max_tokens or cand.get("max_tokens", 4096), timeout, cfg
            )
        except Exception as e:  # noqa: BLE001 — any candidate failure falls through to the next
            attempts.append({"provider": cand.get("provider"), "model": cand.get("model"),
                             "error": f"{type(e).__name__}: {e}"[:300],
                             "seconds": round(time.time() - started, 1)})
            continue
        if not (text or "").strip():
            attempts.append({"provider": cand.get("provider"), "model": cand.get("model"),
                             "error": "empty response"})
            continue
        return text, {"provider": cand["provider"], "model": cand["model"], "task": task,
                      "input_tokens": tin, "output_tokens": tout,
                      "seconds": round(time.time() - started, 1),
                      "attempts": attempts, "fell_back": bool(attempts)}

    raise ModelError(
        f"every candidate for task {task!r} failed: "
        + " | ".join(f"{a.get('model')}: {a.get('error')}" for a in attempts)
    )


def preflight(cfg=None):
    """Which tasks could actually run right now. Prints a table; returns rows.

    Run this at client go-live and after any key rotation — it answers "is the OS wired?"
    without spending a token.
    """
    cfg = cfg or _config()
    rows = []
    for task, cands in sorted(cfg.get("routes", {}).items()):
        usable = []
        for c in cands:
            keyname = {"anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}.get(c.get("provider"))
            if keyname and _key(keyname, cfg):
                usable.append(c["model"])
        rows.append({"task": task, "candidates": [c["model"] for c in cands], "usable": usable})
        state = "ok" if usable else "NO KEY"
        print(f"  {task:<18} {state:<7} {' → '.join(c['model'] for c in cands)}")
    if not any(r["usable"] for r in rows):
        print("\n  No usable candidate for any task — set the keys named in the module docstring.")
    return rows


if __name__ == "__main__":
    import sys
    if "--preflight" in sys.argv:
        print(f"model seam — {CONFIG}\n")
        preflight()
    else:
        print(__doc__)
        print("Run with --preflight to check which tasks can run with the keys present.")
