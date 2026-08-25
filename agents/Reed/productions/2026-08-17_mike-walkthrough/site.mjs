import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--window-size=1600,900','--hide-scrollbars']});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});
await p.goto('http://localhost:8793/yourco-site-v2/index.html',{waitUntil:'networkidle2'});
await sleep(3000);
const rec=await p.screencast({path:'scenes/1d-site.webm'});
// Ride the home page, then the audit page — the priced front door the whole funnel leads to.
for(const y of [0,700,1500,2400,3300]){ await p.evaluate(t=>window.scrollTo({top:t,behavior:'smooth'}),y); await sleep(2200); }
await p.goto('http://localhost:8793/yourco-site-v2/audit.html',{waitUntil:'networkidle2'});
await sleep(2400);
for(const y of [0,750,1500]){ await p.evaluate(t=>window.scrollTo({top:t,behavior:'smooth'}),y); await sleep(2200); }
await sleep(500); await rec.stop(); await b.close(); console.log('site scene captured');
