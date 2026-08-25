// yourco — walkthrough capture for Mike.
// Drives the REAL surfaces headlessly and screencasts each scene. Every frame is the actual
// software running on real data; nothing here is a mockup. Same method as the Property OS demo.
import puppeteer from 'puppeteer-core';
import { mkdirSync } from 'fs';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const OUT = 'scenes';
mkdirSync(OUT, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));

// The Melanie chat panel (#mel) is a fixed 360×430 overlay that covers the right column of every
// HQ door — found on a QA frame, not by eye. Hide it for capture; it is a live control, not content.
// Also hide the orb launcher that sits under it.
const HIDE_OVERLAYS = `
(() => {
  const css = document.createElement('style');
  css.textContent = '#mel,#melorb,.mel,.melorb{display:none !important}';
  document.head.appendChild(css);
})();`;

// A soft brass cursor so the viewer's eye follows the action.
const CURSOR = `
(() => {
  if (window.__dot) return;
  const d = document.createElement('div');
  d.id = '__cursordot';
  Object.assign(d.style, {
    position:'fixed', width:'14px', height:'14px', borderRadius:'50%',
    background:'rgba(212,178,122,.92)', boxShadow:'0 0 0 6px rgba(212,178,122,.22)',
    pointerEvents:'none', zIndex:2147483647, transform:'translate(-50%,-50%)',
    transition:'left .28s cubic-bezier(.4,0,.2,1), top .28s cubic-bezier(.4,0,.2,1)',
    left:'-100px', top:'-100px',
  });
  document.body.appendChild(d);
  window.__dot = d;
})();`;

async function moveTo(page, sel) {
  const box = await page.evaluate(s => {
    const el = [...document.querySelectorAll('button,a')]
      .find(e => (e.textContent || '').trim().startsWith(s));
    if (!el) return null;
    el.scrollIntoView({ block: 'center' });
    const r = el.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  }, sel);
  if (!box) return null;
  await page.evaluate(({ x, y }) => {
    if (window.__dot) { window.__dot.style.left = x + 'px'; window.__dot.style.top = y + 'px'; }
  }, box);
  await sleep(420);
  return box;
}

async function clickLabel(page, label) {
  const box = await moveTo(page, label);
  if (!box) { console.log(`    ! no control starting with "${label}"`); return false; }
  await page.mouse.click(box.x, box.y);
  // Coordinate clicks landed on the CRM's nav row without activating the tab (QA frame showed the
  // cursor on "Pipeline" while the pane still read "1. Today"). Fire the element's own click too —
  // the dot has already moved there, so the motion still reads true.
  await page.evaluate(s => {
    const el = [...document.querySelectorAll('button,a')]
      .find(e => (e.textContent || '').trim().startsWith(s));
    if (el) el.click();
  }, label);
  await sleep(1100);
  return true;
}

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--window-size=1600,900', '--hide-scrollbars', '--force-device-scale-factor=1'],
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 2 });

// Scene list: [file, url, secs, driver]
const scenes = [
  ['02-hq-today', 'http://localhost:8791/', 13, async p => {
    await sleep(3000);
    await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await sleep(4500);
    await p.evaluate(() => window.scrollTo({ top: 520, behavior: 'smooth' }));
    await sleep(4000);
  }],
  ['03-hq-board', 'http://localhost:8791/', 11, async p => {
    await sleep(2200); await clickLabel(p, 'The Board'); await sleep(6500);
  }],
  ['04-hq-partners', 'http://localhost:8791/', 12, async p => {
    await sleep(2200); await clickLabel(p, 'Partners'); await sleep(7500);
  }],
  ['05-hq-agents', 'http://localhost:8791/', 10, async p => {
    await sleep(2200); await clickLabel(p, 'Agents'); await sleep(6000);
  }],
  ['06-crm-pipeline', 'http://localhost:8790/', 12, async p => {
    await sleep(2600); await clickLabel(p, '2Pipeline'); await sleep(7000);
  }],
  ['07-crm-evidence', 'http://localhost:8790/', 11, async p => {
    await sleep(2600); await clickLabel(p, '11Evidence'); await sleep(6500);
  }],
];

for (const [name, url, secs, drive] of scenes) {
  process.stdout.write(`  ${name} … `);
  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 40000 });
    await page.evaluate(HIDE_OVERLAYS);
    await page.evaluate(CURSOR);
    await sleep(600);
    const rec = await page.screencast({ path: `${OUT}/${name}.webm` });
    await drive(page);
    await sleep(500);
    await rec.stop();
    console.log(`ok (${secs}s target)`);
  } catch (e) {
    console.log(`FAILED: ${e.message}`);
  }
}

await browser.close();
console.log('capture complete');
