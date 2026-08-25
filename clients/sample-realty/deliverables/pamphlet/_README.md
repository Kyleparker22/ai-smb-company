# 2304 Highland Forest Drive — in-home pamphlet

Built to Kimi's spec (2026-08-19): cover with exterior + photos · features &
highlights · floor plan · property disclosure.

## Rebuild
```bash
# photos + floor plan must sit beside pamphlet.html as:
#   hero.jpg great.jpg kitchen.jpg primary.jpg deck.jpg floorplan.png
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --no-pdf-header-footer --print-to-pdf=front.pdf \
  --virtual-time-budget=9000 "file://$PWD/pamphlet.html"
# then append the disclosure, scaled to Letter (pypdf) — see the session notes
```

## Decisions worth keeping
- **Highlights take two pages, not one.** The features sheet holds ~60 bullets across
  ten groups. Forced onto one page it drops below 8pt and stops being readable in a
  home where people skim it standing up. Two pages is the honest fit.
- **6,070 sq ft is used**, matching the measured floor plan that appears two pages
  later. The earlier 6,049 figure would have contradicted a document inside the same
  pamphlet. ⚠️ Kimi must confirm which figure goes on the MLS.
- Photos are the photographer's stills, resized to 2200px — ample for placement at
  this size, and keeps the file emailable.
- Disclosure pages arrive at 32.9 x 42.4 in and are scaled to Letter on merge;
  aspect ratios are within 0.3% so nothing distorts.
