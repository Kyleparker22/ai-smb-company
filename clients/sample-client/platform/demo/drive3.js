// v3 live-driven demo: the four-option Design Studio, recorded as a real run on the real platform.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const VO = JSON.parse(fs.readFileSync('vo-durations.json', 'utf8'));
const PLAT = '/Users/you/Documents/Claude/Projects/YourCo LLC - AI/clients/sample-client/platform';
const ASSETS = PLAT + '/assets', DEMO = PLAT + '/demo';
const scenes = []; let t0;
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--window-size=1600,1000', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });
  page.on('dialog', d => d.accept());
  await page.evaluateOnNewDocument(() => {
    addEventListener('DOMContentLoaded', () => {
      const c = document.createElement('div'); c.id = 'democursor';
      c.style.cssText = 'position:fixed;width:22px;height:22px;border-radius:50%;background:rgba(224,168,104,.45);border:2.5px solid #E0A868;z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:width .12s,height .12s;box-shadow:0 0 14px rgba(224,168,104,.6)';
      document.body.appendChild(c);
      addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; });
      addEventListener('mousedown', () => { c.style.width = '15px'; c.style.height = '15px'; });
      addEventListener('mouseup', () => { c.style.width = '22px'; c.style.height = '22px'; });
    });
  });
  let mx = 800, my = 500;
  async function glide(x, y, steps = 22) { for (let i = 1; i <= steps; i++) { const e = i / steps, ease = e < .5 ? 2*e*e : 1 - Math.pow(-2*e+2, 2)/2; await page.mouse.move(mx + (x-mx)*ease, my + (y-my)*ease); await sleep(9); } mx = x; my = y; }
  async function clickEl(el, label) { if (!el) throw new Error('missing ' + label); await el.evaluate(e => e.scrollIntoView({ block: 'center', behavior: 'instant' })); await sleep(260); const b = await el.boundingBox(); if (!b) throw new Error('nobox ' + label); await glide(b.x + b.width/2, b.y + b.height/2); await sleep(130); await page.mouse.click(mx, my); await sleep(240); }
  async function clickSel(sel) { await clickEl(await page.$(sel), sel); }
  async function clickText(txt, tag = 'button') { const h = await page.evaluateHandle((t, tg) => [...document.querySelectorAll(tg)].find(b => b.textContent.includes(t)), txt, tag); await clickEl(h.asElement(), txt); }
  async function typeIn(sel, text, delay = 28) { await clickSel(sel); await page.type(sel, text, { delay }); }
  async function scrollTo(sel, idx = 0) { await page.evaluate((s, i) => { const el = document.querySelectorAll(s)[i]; if (el) el.scrollIntoView({ block: 'start', behavior: 'smooth' }); }, sel, idx); await sleep(900); }
  function mark(i) { scenes.push({ scene: i, t: +((Date.now() - t0) / 1000).toFixed(2) }); console.log('scene', i, scenes[scenes.length-1].t); }
  const pad = i => VO[i] * 1000 + 900;
  async function restPad(i) { const left = pad(i) - (Date.now() - t0 - scenes[i].t * 1000); if (left > 0) await sleep(left); }

  await page.goto('file://' + DEMO + '/title.html'); await sleep(500);
  const recorder = await page.screencast({ path: 'raw.webm' });
  t0 = Date.now();
  mark(0); await sleep(pad(0));

  // S1 — Visit Mode: who's here + the four want-levels, typed live
  await page.goto('http://localhost:8804/'); await sleep(1600);
  mark(1);
  await clickText('+ New'); await sleep(900);
  await clickText('2 · Visit'); await sleep(600);
  await typeIn('#v_client', 'The Millers'); await typeIn('#v_address', '2140 Ridgecrest Dr, Davidson');
  await clickSel('#v_repchips .repchip:nth-child(1)'); await clickSel('#v_repchips .repchip:nth-child(2)');
  await typeIn('#v_budget', '$60–80k', 36);
  await typeIn('#v_notes', 'Bluestone patio with a fire pit in the middle, pergola over the dining end, privacy planting along the back fence.', 16);
  await typeIn('#v_nice', 'seating wall around the patio', 20);
  await typeIn('#v_dream', 'an outdoor kitchen with a built-in grill', 20);
  await typeIn('#v_sc', 'low-voltage lighting along the walkway and beds', 20);
  await restPad(1);

  // S2 — capture the site: photo, tape dims, grade, access + why
  mark(2);
  const ph = await page.$('#v_photos'); await ph.uploadFile(ASSETS + '/before.jpg'); await sleep(1500);
  if (!await page.evaluate(() => S.project.photos.length > 0)) throw new Error('ASSERT photo');
  await typeIn('#v_yw', '70', 60); await typeIn('#v_yd', '45', 60);
  await typeIn('#v_gradeft', '2', 80);
  const sl = await page.$('#v_access'); const sb = await sl.boundingBox(); await sl.evaluate(e => e.scrollIntoView({block:'center'})); await sleep(200);
  const sb2 = await sl.boundingBox(); await glide(sb2.x + sb2.width*0.4, sb2.y + sb2.height/2); await page.mouse.click(mx, my);
  await page.evaluate(() => { const s = document.getElementById('v_access'); s.value = 5; s.dispatchEvent(new Event('input')); });
  await typeIn('#v_accesswhy', '36-inch side gate, wheelbarrow only', 22);
  await restPad(2);

  // S3 — auto-design + four options fire
  mark(3);
  await clickText('✦ Auto-design');
  for (let i = 0; i < 40; i++) { await sleep(700); const m = await page.$eval('#visitMsg', e => e.textContent); if (/rendering|already running/i.test(m)) break; }
  const vm = await page.$eval('#visitMsg', e => e.textContent);
  if (!/option/i.test(vm)) throw new Error('ASSERT options did not fire: ' + vm);
  await page.evaluate(() => document.getElementById('visitMsg').scrollIntoView({block:'center', behavior:'smooth'}));
  await restPad(3);

  // S4 — Design Studio on a finished project: four options, descriptions, prices, choose
  mark(4);
  await page.select('#projSelect', 'pbf0aa221'); await sleep(1400);
  await clickText('3 · Design Studio'); await sleep(1800);
  const nCards = await page.evaluate(() => document.querySelectorAll('#clientView .cv-option').length);
  if (nCards < 4) throw new Error('ASSERT option cards: ' + nCards);
  for (let i = 0; i < 4; i++) { await scrollTo('#clientView .cv-option', i); await glide(500 + i*40, 420, 26); await sleep(i === 0 ? 4200 : 3200); }
  await scrollTo('#clientView .cv-option', 0);
  await clickText('Go with this one'); await sleep(900);
  await restPad(4);

  // S5 — Build it together: toggle, live price, budget line
  mark(5);
  await scrollTo('#clientView .addons', 0); await sleep(800);
  const boxes = await page.$$('#clientView .addons input[type=checkbox]');
  const target = boxes[boxes.length - 1];
  if (target) { await clickEl(target, 'addon'); await sleep(1600); await clickEl((await page.$$('#clientView .addons input[type=checkbox]')).slice(-1)[0], 'addon'); }
  await restPad(5);

  // S6 — approve the studio step → board locks → subs RFQs
  mark(6);
  await page.evaluate(() => window.scrollTo({top:0, behavior:'smooth'})); await sleep(600);
  await clickSel('#step-client input'); await sleep(600);
  await clickText('5 · 2D Board'); await sleep(1200);
  const lock = await page.$eval('#boardLockNote', e => e.textContent);
  if (!/Option/.test(lock)) throw new Error('ASSERT board lock: ' + lock);
  await glide(700, 600, 30); await sleep(1600);
  await clickText('7 · Subs'); await sleep(900);
  await glide(600, 700, 30);
  await restPad(6);

  // S7 — quote from their own jobs → approvals → proposal unlocks
  mark(7);
  await clickText('8 · Quote'); await sleep(900); await glide(500, 760, 30); await sleep(2200);
  await clickText('9 · Approvals'); await sleep(800);
  for (let i = 0; i < 3; i++) { const un = []; for (const bx of await page.$$('#flagList input[type=checkbox]')) { if (!(await (await bx.getProperty('checked')).jsonValue())) un.push(bx); } if (!un.length) break; await clickEl(un[0], 'flag'); await sleep(350); }
  await scrollTo('#proposalBox', 0);
  await restPad(7);

  // S8 — Present mode
  mark(8);
  await clickText('3 · Design Studio'); await sleep(1400);
  await clickText('Present full screen'); await sleep(600);
  if (!await page.evaluate(() => document.body.classList.contains('presenting'))) { await clickText('Present full screen'); await sleep(600); }
  if (!await page.evaluate(() => document.body.classList.contains('presenting'))) throw new Error('ASSERT present mode did not engage');
  await sleep(2200);
  await page.evaluate(() => document.getElementById('clientView').scrollTo({top: 900, behavior:'smooth'})); await sleep(1600);
  await page.keyboard.press('Escape'); await sleep(400);
  await restPad(8);

  // S9 — end card
  mark(9);
  await page.goto('file://' + DEMO + '/end.html'); await sleep(pad(9) + 600);
  await recorder.stop();
  fs.writeFileSync('scenes.json', JSON.stringify(scenes, null, 1));

  // leave the Founder-Test exactly as we found it
  await page.goto('http://localhost:8804/?project=pbf0aa221&tab=client&v=restore'); await sleep(1800);
  await page.evaluate(() => { delete S.steps.client; S.project.chosenOption = null; S.approvals = {}; save(); });
  await sleep(1500);
  await browser.close();
  console.log('DONE', JSON.stringify(scenes));
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
