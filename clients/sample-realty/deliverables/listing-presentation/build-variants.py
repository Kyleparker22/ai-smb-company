#!/usr/bin/env python3
"""Render the Coleman listing presentation in four brand-palette variants x two formats.

Content is identical within a format (single-source HTML); each variant only
overrides the :root palette vars before rendering. All palettes stay inside
Sample Realty's brand family (black/white/red/cream, site-sampled #EF0004).
Run from this directory: python3 build-variants.py
"""
import os, subprocess, sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))

# format label -> source file ("" = full 7pp edition)
SOURCES = {
    "": "coleman-listing-presentation.html",
    "Compact-": "coleman-listing-presentation-3pp.html",
}

VARIANTS = {
    # A — her site brand, base palette: black fields, cream paper, #EF0004 red.
    "A-Signature-Red": None,

    # B — same brand, red-undertoned dark: near-black-crimson fields, red accents.
    "B-Deep-Crimson": {
        "--field": "#24090B",
        "--warm": "#F5EFEC",
        "--on-dark": "#FFFFFF",
        "--on-dark-soft": "rgba(255,255,255,.93)",
        "--line-dark": "rgba(255,255,255,.3)",
    },

    # C — same brand, light throughout: warm-white fields, black type, red accents.
    "C-Light-Red": {
        "--field": "#F3EFE7",
        "--paper": "#FDFCFA",
        "--on-dark": "#131318",
        "--on-dark-soft": "rgba(19,19,24,.62)",
        "--line-dark": "rgba(19,19,24,.3)",
    },

    # D — same brand, pure white everywhere: white pages, black type, red accents.
    "D-White": {
        "--field": "#FFFFFF",
        "--paper": "#FFFFFF",
        "--warm": "#F6F5F2",
        "--on-dark": "#131318",
        "--on-dark-soft": "rgba(19,19,24,.62)",
        "--line-dark": "rgba(19,19,24,.32)",
    },
}

def main():
    has_photo = os.path.exists(os.path.join(HERE, "cover-house.jpg"))
    for fmt, srcfile in SOURCES.items():
        src = open(os.path.join(HERE, srcfile), encoding="utf-8").read()
        if has_photo:  # rights-clean house photo present -> covers gain the framed photo plate
            src = src.replace("<body>", '<body class="has-photo">')
        for name, palette in VARIANTS.items():
            html = src
            if palette:
                override = ":root{" + ";".join(f"{k}:{v}" for k, v in palette.items()) + "}"
                html = html.replace("</head>", f"<style>{override}</style>\n</head>")
            tmp = os.path.join(HERE, f"_variant-{fmt}{name}.html")
            out = os.path.join(HERE, f"Coleman-Listing-Presentation-{fmt}{name}.pdf")
            open(tmp, "w", encoding="utf-8").write(html)
            r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                                f"--print-to-pdf={out}", f"file://{tmp}"],
                               capture_output=True, text=True)
            os.remove(tmp)
            size = os.path.getsize(out) if os.path.exists(out) else 0
            if size == 0:
                print(f"FAILED {fmt}{name}: {r.stderr[-300:]}"); sys.exit(1)
            print(f"{fmt}{name}: {size//1024}KB")

if __name__ == "__main__":
    main()
