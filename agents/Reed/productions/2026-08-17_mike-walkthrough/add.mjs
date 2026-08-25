import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const HIDE=`(()=>{const s=document.createElement('style');s.textContent='#mel,.mel{display:none!important}';document.head.appendChild(s);})();`;
const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--window-size=1600,900','--hide-scrollbars']});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});

// 7b — Connector Console (the SAMPLE fixture, never a real connector's ledger)
await p.goto('http://localhost:8808/_SAMPLE-populated.html',{waitUntil:'networkidle2'});
await sleep(2200);
let rec=await p.screencast({path:'scenes/7b-console.webm'});
for(const y of [0,650,1300,1950]){ await p.evaluate(t=>window.scrollTo({top:t,behavior:'smooth'}),y); await sleep(2600); }
await sleep(500); await rec.stop(); console.log('  7b console ok');

// 7c — HQ System: the loops, real state
await p.goto('http://localhost:8791/',{waitUntil:'networkidle2'});
await p.evaluate(HIDE); await sleep(2200);
rec=await p.screencast({path:'scenes/7c-loops.webm'});
await p.evaluate(()=>{const el=[...document.querySelectorAll('button')].find(e=>(e.textContent||'').trim().startsWith('System')); if(el) el.click();});
await sleep(3200);
for(const y of [0,600,1200]){ await p.evaluate(t=>window.scrollTo({top:t,behavior:'smooth'}),y); await sleep(2600); }
await sleep(500); await rec.stop(); console.log('  7c loops ok');
await b.close();
