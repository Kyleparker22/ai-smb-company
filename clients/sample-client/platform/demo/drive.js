// Live-driven demo recording: acts out a full test run on the real platform with a
// visible cursor, human-speed typing and clicking, recorded via Chrome screencast.
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const VO = JSON.parse(fs.readFileSync('vo-durations.json', 'utf8'));
const ASSETS = '/Users/you/Documents/Claude/Projects/YourCo LLC - AI/clients/sample-client/platform/assets';
const DEMO = '/Users/you/Documents/Claude/Projects/YourCo LLC - AI/clients/sample-client/platform/demo';
const scenes = [];
let t0;

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new',
    args: ['--window-size=1600,1000', '--hide-scrollbars'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });

  // visible fake cursor that follows the real mouse
  await page.evaluateOnNewDocument(() => {
    addEventListener('DOMContentLoaded', () => {
      const c = document.createElement('div');
      c.id = 'democursor';
      c.style.cssText = 'position:fixed;width:22px;height:22px;border-radius:50%;background:rgba(224,168,104,.45);border:2.5px solid #E0A868;z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:width .12s,height .12s;box-shadow:0 0 14px rgba(224,168,104,.6)';
      document.body.appendChild(c);
      addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; });
      addEventListener('mousedown', () => { c.style.width = '15px'; c.style.height = '15px'; });
      addEventListener('mouseup', () => { c.style.width = '22px'; c.style.height = '22px'; });
    });
  });

  let mx = 800, my = 500;
  async function glide(x, y, steps = 22) {
    for (let i = 1; i <= steps; i++) {
      const e = i / steps, ease = e < .5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2;
      await page.mouse.move(mx + (x - mx) * ease, my + (y - my) * ease);
      await sleep(9);
    }
    mx = x; my = y;
  }
  async function clickSel(sel) {
    const el = await page.$(sel);
    if (!el) throw new Error('missing ' + sel);
    await el.evaluate(e => e.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await sleep(250);
    const b = await el.boundingBox();
    if (!b) throw new Error('nobox ' + sel);
    await glide(b.x + b.width / 2, b.y + b.height / 2);
    await sleep(120);
    await page.mouse.click(mx, my);
    await sleep(220);
  }
  async function clickText(txt) {
    const h = await page.evaluateHandle(t => [...document.querySelectorAll('button')].find(b => b.textContent.includes(t)), txt);
    const el = h.asElement();
    if (!el) throw new Error('no button ' + txt);
    await el.evaluate(e => e.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await sleep(250);
    const b = await el.boundingBox();
    await glide(b.x + b.width / 2, b.y + b.height / 2);
    await sleep(120);
    await page.mouse.click(mx, my);
    await sleep(220);
  }
  async function typeIn(sel, text, delay = 34) {
    await clickSel(sel);
    await page.type(sel, text, { delay });
  }
  function mark(i) { scenes.push({ scene: i, t: +((Date.now() - t0) / 1000).toFixed(2) }); console.log('scene', i, scenes[scenes.length - 1].t); }
  const scenePad = i => VO[i] * 1000 + 900;

  // ---------- record ----------
  await page.goto('file://' + DEMO + '/title.html');
  const recorder = await page.screencast({ path: DEMO + '/raw.webm' });
  t0 = Date.now();

  // S0 title
  mark(0); await sleep(scenePad(0));

  // S1 intake — new project, type everything
  await page.goto('http://localhost:8804/');
  await sleep(1800);
  mark(1);
  await clickText('+ New');
  await sleep(700);
  await typeIn('#p_client', 'The Hendersons');
  await typeIn('#p_address', '412 Maple Grove Ln, Yourtown');
  await clickSel('#p_budget'); await page.type('#p_budget', '$35–50k', { delay: 40 });
  await clickSel('#p_timeline'); await page.type('#p_timeline', 'before Thanksgiving', { delay: 40 });
  await typeIn('#p_notes', 'Bluestone patio with a pergola and lights, fire pit, privacy planting along the back fence.', 18);
  const s1left = scenePad(1) - (Date.now() - t0 - scenes[1].t * 1000);
  if (s1left > 0) await sleep(s1left);

  // S2 site — photos, moasure paste, trace, grade, access
  mark(2);
  await clickText('2 · Site');
  await sleep(400);
  const photo = await page.$('#p_photos');
  await photo.uploadFile(ASSETS + '/before.jpg');
  await sleep(1400);
  await typeIn('#moasurePaste', 'back patio width, 21.5\npatio depth, 14\nfence run, 62', 12);
  await clickText('Import as Moasure');
  await sleep(400);
  const TRACE = '# boundary\n2,2\n96,2\n96,58\n2,58\n# house\n24,4\n72,4\n72,26\n24,26\n# feature Oak tree\n84,40\n# feature Gate (36in)\n2,44';
  await page.evaluate(t => { document.getElementById('tracePaste').value = t; }, TRACE);
  await clickText('Import trace');
  await sleep(600);
  if (!await page.evaluate(() => !!S.trace)) throw new Error('ASSERT: trace did not import');
  await typeIn('#q_gradeft', '2.5', 80);
  const slider = await page.$('#q_access');
  const sb = await slider.boundingBox();
  await glide(sb.x + sb.width * 0.15, sb.y + sb.height / 2); await page.mouse.click(mx, my);
  await page.evaluate(() => { const s = document.getElementById('q_access'); s.value = 4; s.dispatchEvent(new Event('input')); });
  const s2left = scenePad(2) - (Date.now() - t0 - scenes[2].t * 1000);
  if (s2left > 0) await sleep(s2left);

  // S3 board — auto-drawn from trace
  mark(3);
  await clickText('3 · 2D Board');
  await glide(700, 620, 30); await glide(1100, 500, 30);
  const s3left = scenePad(3) - (Date.now() - t0 - scenes[3].t * 1000);
  if (s3left > 0) await sleep(s3left);

  // S4 layouts — propose, browse, pick
  mark(4);
  await clickText('Propose layouts');
  await sleep(900);
  const v0 = await page.$('.variant');
  if (v0) {
    const vb = await v0.boundingBox();
    await glide(vb.x + vb.width / 2, vb.y + 60); await sleep(1100);
    page.once('dialog', d => d.accept());
    await page.mouse.click(mx, my);
    await sleep(700);
  }
  if (!await page.evaluate(() => S.elements.length > 0)) throw new Error('ASSERT: layout not applied');
  // small drag of the patio for life
  const drag = await page.evaluate(() => {
    const svg = document.getElementById('boardsvg').getBoundingClientRect();
    const e = S.elements.find(x => x.type === 'patio');
    if (!e) return null;
    const sc = svg.width / 800;
    return { x: svg.x + (e.x + e.w / 2) * 8 * sc, y: svg.y + (e.y + e.d / 2) * 8 * sc };
  });
  if (drag) {
    await glide(drag.x, drag.y); await page.mouse.down();
    await glide(drag.x - 60, drag.y + 25, 18); await page.mouse.up();
  }
  const s4left = scenePad(4) - (Date.now() - t0 - scenes[4].t * 1000);
  if (s4left > 0) await sleep(s4left);

  // S5 quote — numbers + package flip
  mark(5);
  await clickText('7 · Quote');
  await sleep(600);
  if (!await page.evaluate(() => computeQuote().price > 0)) throw new Error('ASSERT: quote is zero');
  const tiers = await page.$$('#tierstrip .tier');
  if (tiers[1]) { const tb = await tiers[1].boundingBox(); await glide(tb.x + tb.width / 2, tb.y + tb.height / 2); await sleep(300); await page.mouse.click(mx, my); }
  await sleep(600);
  if (tiers[0]) { const tb = await (await page.$$('#tierstrip .tier'))[0].boundingBox(); await glide(tb.x + tb.width / 2, tb.y + tb.height / 2); await sleep(250); await page.mouse.click(mx, my); }
  await glide(500, 700, 26);
  const s5left = scenePad(5) - (Date.now() - t0 - scenes[5].t * 1000);
  if (s5left > 0) await sleep(s5left);

  // S6 client view day — upload the day render live, then browse
  mark(6);
  await clickText('4 · Design Studio');
  await sleep(500);
  const rend = await page.$('#p_renders');
  await rend.uploadFile(ASSETS + '/design1.png');
  await sleep(1800);
  if (!await page.evaluate(() => S.project.renders.length > 0)) throw new Error('ASSERT: day render not uploaded');
  await page.evaluate(() => showTab('client'));
  await sleep(300);
  await page.evaluate(() => window.scrollTo({ top: 900, behavior: 'smooth' }));
  await sleep(1200);
  // click Premium package card
  const pk = await page.$$('#clientView .cv-tier');
  if (pk[1]) { const b = await pk[1].boundingBox(); if (b) { await glide(b.x + b.width / 2, b.y + b.height / 2); await page.mouse.click(mx, my); await sleep(600); } }
  const s6left = scenePad(6) - (Date.now() - t0 - scenes[6].t * 1000);
  if (s6left > 0) await sleep(s6left);

  // S7 night — upload night render tagged night, flip the state pill
  mark(7);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(500);
  await page.select('#renderState', 'night');
  const rend2 = await page.$('#p_renders');
  await rend2.uploadFile(ASSETS + '/night1.png');
  await sleep(1800);
  if (!await page.evaluate(() => S.project.renders.some(r => r.state === 'night'))) throw new Error('ASSERT: night render not uploaded');
  await page.evaluate(() => showTab('client'));
  await sleep(300);
  await page.evaluate(() => window.scrollTo({ top: 900, behavior: 'smooth' }));
  await sleep(800);
  const nightBtn = await page.evaluateHandle(() => [...document.querySelectorAll('#clientView .statetabs button')].find(b => b.textContent.startsWith('Night')));
  const nEl = nightBtn.asElement();
  if (nEl) { const b = await nEl.boundingBox(); if (b) { await glide(b.x + b.width / 2, b.y + b.height / 2); await sleep(250); await page.mouse.click(mx, my); await sleep(600); } }
  await page.evaluate(() => window.scrollTo({ top: 1250, behavior: 'smooth' }));
  const s7left = scenePad(7) - (Date.now() - t0 - scenes[7].t * 1000);
  if (s7left > 0) await sleep(s7left);

  // S8 approvals — check the gates green, then a peek at subs
  mark(8);
  await clickText('8 · Approvals');
  await sleep(500);
  for (let i = 0; i < 6; i++) {
    const boxes = await page.$$('#flagList input[type=checkbox]');
    const un = [];
    for (const bx of boxes) { if (!(await (await bx.getProperty('checked')).jsonValue())) un.push(bx); }
    if (!un.length) break;
    const b = await un[0].boundingBox();
    if (!b) break;
    await glide(b.x + b.width / 2, b.y + b.height / 2); await sleep(260); await page.mouse.click(mx, my); await sleep(420);
  }
  const s8left = scenePad(8) - (Date.now() - t0 - scenes[8].t * 1000);
  if (s8left > 0) await sleep(s8left);

  // S9 end card
  mark(9);
  await page.goto('file://' + DEMO + '/end.html');
  await sleep(scenePad(9) + 600);

  await recorder.stop();
  fs.writeFileSync('scenes.json', JSON.stringify(scenes, null, 1));
  await browser.close();
  console.log('DONE', JSON.stringify(scenes));
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
