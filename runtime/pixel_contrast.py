#!/usr/bin/env python3
"""yourco — does the text on a rendered page actually paint? Measured in pixels, not in the DOM.

WHY THIS EXISTS. Four times in two days the Connector Console shipped text that was *present and
correctly worded and completely invisible* — a cream figure on a cream panel, an on-dark notice on a
light tile, a muted cell on a dark table, and finally the approval gate's A0/A1/A2 rung labels
computing to `rgb(22,27,51)` on an `rgb(22,27,51)` tile: identical values, so the ladder rendered
with no rung names at all. Every one was invisible to every check we had, because the markup was
right, the copy was right, the tests passed, and the consistency watchdog reads text not pixels.
And every time, the sentence that vanished was the one saying a number is NOT real.

WHY THE OBVIOUS FIX DOESN'T WORK. The first attempt was a DOM audit: walk the tree, compare each
element's computed colour against the nearest painted background. It reported six failures, all
false — it read `rgba(255,255,255,.05)` as pure white because it never composited alpha, so every
element inside a translucent card looked like black-on-white. A check that is wrong in both
directions is worse than no check, so it was thrown away rather than committed.

HOW THIS ONE WORKS. It renders the page twice in headless Chrome:

  pass A — the page exactly as a connector sees it
  pass B — the same page with every glyph made transparent

Any pixel that DIFFERS between the two is a pixel where text actually painted. That is the ground
truth: it composites alpha, blend modes, shadows, overlaps and antialiasing for free, because it is
the browser's own renderer doing the compositing rather than us modelling it. Then, for every
element that contains text, we ask two questions of the rendered image:

  1. Did any of its pixels change?   No  → the text painted NOTHING. Invisible. Hard failure.
  2. What is the contrast between the pixels that changed (the ink) and the ones that didn't
     (the surface behind it)?        Low → legible-but-faint. Reported separately.

PNG decoding is stdlib `zlib` + the five PNG filter types — no Pillow, no numpy, consistent with the
"a wrench, not a workshop" posture. Chrome is already a dependency of this repo (it renders
`rep-packet.pdf`).

Usage:
  python3 runtime/pixel_contrast.py                       # the console's fixture pages
  python3 runtime/pixel_contrast.py <file.html> [...]     # any local page
  python3 runtime/pixel_contrast.py --width 390           # check a phone layout
Exit 0 = every text element paints · exit 1 = something is invisible.
"""
import os, re, sys, json, zlib, struct, shutil, subprocess, tempfile, argparse, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSOLE_OUT = os.path.join(ROOT, "processes/partnerships/connector-console/_out")
DEFAULT_PAGES = ["_SAMPLE-populated.html", "_SAMPLE-unlocked.html", "_SAMPLE-gate.html",
                 "_SAMPLE-verify-queue.html"]
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]
# WCAG: 4.5:1 for body text, 3:1 for large. Below FAINT we report it; below INVISIBLE we fail.
# INVISIBLE is keyed off the measured RATIO, not the pixel count — the first version failed only when
# zero pixels changed, and a planted indigo-on-indigo bug slipped through as merely "faint" because
# subpixel antialiasing still nudges a handful of pixels. 1.0:1 is not faint. It is gone.
FAINT = 3.0
INVISIBLE = 1.4
MIN_BOX = 5          # ignore slivers — a 3px box is a rule or a spacer, not a sentence
MAX_TEXT = 70
MIN_INK = 6          # fewer changed pixels than this is a sub-pixel artefact, not a legible glyph


def find_chrome():
    for c in CHROME_CANDIDATES:
        p = shutil.which(c) if not os.path.isabs(c) else (c if os.path.exists(c) else None)
        if p:
            return p
    return None


# ---- PNG → RGB rows (stdlib only) ---------------------------------------------------------
def png_rgb(path):
    """Decode a non-interlaced 8-bit PNG to (w, h, bytearray of RGB triples)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    pos, idat, w = 8, bytearray(), None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, color, _c, _f, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or interlace or color not in (2, 6):
                raise ValueError(f"unsupported PNG: depth={depth} color={color} interlace={interlace}")
            chans = 3 if color == 2 else 4
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(bytes(idat))
    stride = w * chans
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        # The five PNG filters, applied per byte against the left (a) and upper (b) neighbours.
        if ft == 1:
            for i in range(chans, stride):
                line[i] = (line[i] + line[i - chans]) & 255
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                b = prev[i]
                c = prev[i - chans] if i >= chans else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif ft != 0:
            raise ValueError(f"bad PNG filter {ft}")
        o = y * w * 3
        for x in range(w):
            s = x * chans
            out[o + x * 3:o + x * 3 + 3] = line[s:s + 3]
        prev = line
    return w, h, out


def lum(r, g, b):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---- the two renders ----------------------------------------------------------------------
# Injected into BOTH passes. Without it the audit measures a page that is still moving: `.reveal`
# animates translateY(18px)→0 over 0.7s, so geometry read the moment the class is added is ~18px
# above where the glyphs eventually paint — which made every element deep in the page look like it
# painted nothing. A screenshot is a still of a settled page; the measurement has to be one too.
FREEZE_CSS = """
<style id="__freeze">*,*::before,*::after{transition:none!important;animation:none!important}
  html{scroll-behavior:auto!important}</style>
"""

AUDIT_JS = """
<script>
window.addEventListener("load", function(){
  // Every room at once, and no reveal animation mid-flight — we are auditing the settled page.
  document.querySelectorAll(".room").forEach(r=>r.classList.add("on"));
  document.querySelectorAll(".reveal").forEach(e=>e.classList.add("in"));
  document.querySelectorAll("details").forEach(d=>d.open=true);
  var boxes=[];
  document.querySelectorAll("body *").forEach(function(el){
    var own=[].slice.call(el.childNodes).filter(n=>n.nodeType===3)
              .map(n=>n.textContent).join("").trim();
    if(!own) return;                                  // only elements holding their OWN text
    var cs=getComputedStyle(el);
    if(cs.display==="none"||cs.visibility==="hidden"||parseFloat(cs.opacity)===0) return;
    var r=el.getBoundingClientRect();
    if(r.width<%(min)d||r.height<%(min)d) return;
    boxes.push({x:Math.round(r.left+scrollX),y:Math.round(r.top+scrollY),
                w:Math.round(r.width),h:Math.round(r.height),
                t:own.slice(0,%(max)d),
                sel:(el.tagName.toLowerCase()+"."+(el.className||"").toString().trim()
                     .split(/\\s+/).join(".")).slice(0,54)});
  });
  // Chrome dropped --dump-dom, so the page POSTs its own layout back to the harness. Served over
  // http:// (not file://) precisely so this is same-origin and needs no CORS relaxation.
  // A SYNCHRONOUS XHR on purpose: sendBeacon silently returns false above ~64KB, and the populated
  // console's geometry is comfortably larger than that — so the two biggest pages, the ones most
  // worth checking, reported "no layout" and were skipped while the small ones passed.
  var payload=JSON.stringify({h:document.body.scrollHeight,
                              w:document.documentElement.scrollWidth, boxes:boxes});
  try{ var xhr=new XMLHttpRequest(); xhr.open("POST","/__boxes",false); xhr.send(payload); }
  catch(e){ fetch("/__boxes",{method:"POST",body:payload}); }
});
</script>
""" % {"min": MIN_BOX, "max": MAX_TEXT}

# Pass B. `-webkit-text-fill-color` is the one that actually wins on a lot of elements, and
# text-shadow has to go too or a shadowed glyph still paints something.
HIDE_TEXT_CSS = """
<style id="__hide">*,*::before,*::after{color:transparent!important;
  -webkit-text-fill-color:transparent!important;text-shadow:none!important;
  text-decoration-color:transparent!important;caret-color:transparent!important}</style>
"""


def _build(src, tmp, hide):
    html = open(src, encoding="utf-8").read()
    inject = FREEZE_CSS + AUDIT_JS + (HIDE_TEXT_CSS if hide else "")
    html = (html.replace("</body>", inject + "</body>", 1) if "</body>" in html
            else html + inject)
    out = os.path.join(tmp, ("b" if hide else "a") + ".html")
    open(out, "w", encoding="utf-8").write(html)
    return out


class _Harness(HTTPServer):
    """Serves the two audit pages and catches the layout the page posts back.

    `--headless=new` HANGS in this environment (verified: both --screenshot and --dump-dom never
    return, while the old mode completes in seconds), so the old flag is used deliberately. If a
    future Chrome removes it, the fix is the DevTools protocol, not a return to DOM guessing.
    """
    boxes = None


class _Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            self.server.boxes = json.loads(self.rfile.read(n).decode("utf-8"))
        except ValueError:
            self.server.boxes = None
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


def _serve(directory):
    srv = _Harness(("127.0.0.1", 0),
                   lambda *a, **k: _Handler(*a, directory=directory, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _chrome_run(chrome, url, args):
    cmd = [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--virtual-time-budget=5000"] + args + [url]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None


def audit(src, chrome, width=1280, keep=None):
    """Render `src` twice and report every text element whose pixels never changed."""
    with tempfile.TemporaryDirectory(prefix="pxc") as tmp:
        a_html, b_html = _build(src, tmp, False), _build(src, tmp, True)
        # Assets (there are none today — the console inlines everything) resolve relative to the
        # ORIGINAL folder, so serve that and drop the two audit pages into it.
        srv, base = _serve(tmp)
        try:
            # 1. Pass A: the page as a connector sees it. It posts its layout back on load.
            srv.boxes = None
            r = _chrome_run(chrome, f"{base}/a.html",
                            [f"--screenshot={os.path.join(tmp, 'a.png')}",
                             f"--window-size={width},1200"])
            if r is None:
                return None, "Chrome did not return (headless render timed out)"
            probe = srv.boxes
            if not probe or not probe.get("boxes"):
                return None, "the page posted no layout back — nothing to attribute pixels to"
            height = max(400, min(int(probe["h"]) + 40, 16000))
            # 2. Re-render BOTH passes at the full page height — and take the geometry from the
            #    full-height pass A, never from the probe. Viewport height changes layout (the probe
            #    sat ~15px off, which made every element look like it painted nothing and produced a
            #    page full of confident false failures). Geometry and pixels must come from the same
            #    render or the check is measuring two different pages.
            shots = {}
            meta = None
            for tag, page in (("a", "a.html"), ("b", "b.html")):
                png = os.path.join(tmp, f"{tag}-full.png")
                srv.boxes = None
                if _chrome_run(chrome, f"{base}/{page}",
                               [f"--screenshot={png}", f"--window-size={width},{height}"]) is None:
                    return None, "Chrome did not return on the full-height render"
                if tag == "a":
                    meta = srv.boxes or probe
                if not os.path.exists(png):
                    return None, f"Chrome produced no screenshot for {os.path.basename(src)}"
                shots[tag] = png
            if keep:
                for t, pth in shots.items():
                    shutil.copy(pth, os.path.join(keep, f"{os.path.basename(src)}.{t}.png"))
            wa, ha, A = png_rgb(shots["a"])
            wb, hb, B = png_rgb(shots["b"])
        finally:
            srv.shutdown()
    if (wa, ha) != (wb, hb):
        return None, f"the two renders differ in size ({wa}x{ha} vs {wb}x{hb}) — layout is not stable"

    findings = []
    for box in meta["boxes"]:
        x0, y0 = max(0, box["x"]), max(0, box["y"])
        x1, y1 = min(wa, x0 + box["w"]), min(ha, y0 + box["h"])
        if x1 <= x0 or y1 <= y0:
            continue                                    # outside the captured area
        ink, bg_l, bg_n = [], 0.0, 0
        for y in range(y0, y1):
            row = y * wa * 3
            for x in range(x0, x1):
                i = row + x * 3
                if A[i] != B[i] or A[i + 1] != B[i + 1] or A[i + 2] != B[i + 2]:
                    ink.append(lum(A[i], A[i + 1], A[i + 2]))
                else:
                    bg_l += lum(A[i], A[i + 1], A[i + 2]); bg_n += 1
        if len(ink) < MIN_INK:
            findings.append({"kind": "invisible", "box": box, "ink": len(ink),
                             "why": ("no pixel in this element changed when its text was hidden — "
                                     "the glyphs painted nothing at all") if not ink else
                                    f"only {len(ink)} pixel(s) changed — the glyphs left no readable mark"})
            continue
        if bg_n == 0:
            continue
        surface = bg_l / bg_n
        # Measure the glyph CORE, not the average of every changed pixel. Antialiasing surrounds
        # each letter with half-tones, and averaging them drags the measurement toward the surface —
        # the first version of this scored ordinary black-on-cream body copy at ~1.8:1 and called it
        # faint. The core is the changed pixel furthest from the surface, which is the darkness (or
        # lightness) a reader actually perceives as the letterform.
        core = max(ink, key=lambda v: abs(v - surface))
        cr = ratio(core, surface)
        if cr < INVISIBLE:
            findings.append({"kind": "invisible", "ratio": round(cr, 2), "box": box,
                             "why": f"glyph-to-surface contrast is ~{cr:.2f}:1 — the text is there and "
                                    f"cannot be seen"})
        elif cr < FAINT:
            findings.append({"kind": "faint", "ratio": round(cr, 2), "box": box,
                             "why": f"glyph-to-surface contrast is ~{cr:.1f}:1 in the render"})
    return findings, None


def main():
    ap = argparse.ArgumentParser(description="rendered-pixel contrast check")
    ap.add_argument("pages", nargs="*", help="HTML files (default: the console fixtures)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--keep", metavar="DIR", help="save the two renders for eyeballing")
    a = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("No Chrome/Chromium found — this check needs a real renderer, and refuses to\n"
              "approximate one in the DOM (that is the check that was wrong in both directions).")
        return 2
    pages = a.pages or [os.path.join(CONSOLE_OUT, p) for p in DEFAULT_PAGES]
    pages = [p for p in pages if os.path.exists(p)]
    if not pages:
        print("Nothing to check — render the fixtures first:\n"
              "  python3 processes/partnerships/connector-console/server.py --sample")
        return 2
    if a.keep:
        os.makedirs(a.keep, exist_ok=True)

    print(f"# Rendered-pixel contrast — {len(pages)} page(s) at {a.width}px\n")
    bad = faint = checked = errors = 0
    for src in pages:
        findings, err = audit(src, chrome, a.width, a.keep)
        name = os.path.basename(src)
        if err:
            # Counted separately from findings on purpose: "could not check" and "found invisible
            # text" are different states, and the first reported as the second would be a checker
            # that lies in the same direction as the bugs it exists to catch.
            print(f"  ⚠️  COULD NOT CHECK  {name}: {err}")
            errors += 1
            continue
        inv = [f for f in findings if f["kind"] == "invisible"]
        fnt = [f for f in findings if f["kind"] == "faint"]
        bad += len(inv); faint += len(fnt); checked += 1
        status = "INVISIBLE TEXT" if inv else ("faint" if fnt else "ok")
        print(f"  {status:<15} {name}")
        for f in inv + fnt:
            b = f["box"]
            print(f"      {'✖' if f['kind'] == 'invisible' else '·'} {b['sel']}")
            print(f"        “{b['t']}”")
            print(f"        {f['why']}")
    print(f"\n{checked} page(s) checked · {bad} invisible · {faint} faint"
          + (f" · {errors} COULD NOT BE CHECKED" if errors else ""))
    if not bad and not errors:
        print("Every text element on every page actually paints.")
    return 1 if (bad or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
