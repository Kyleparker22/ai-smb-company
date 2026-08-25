import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--window-size=1600,660','--hide-scrollbars','--force-device-scale-factor=1']});
const p=await b.newPage();
// Short viewport: the "Needs the Founder" panel (which carries an operating-agreement line) sits below it
// entirely, so nothing needs hiding and the layout stays intact.
await p.setViewport({width:1600,height:660,deviceScaleFactor:2});
await p.goto('http://localhost:8791/',{waitUntil:'networkidle2'});
await p.evaluate(()=>{const s=document.createElement('style');s.textContent='#mel,.mel{display:none!important}';document.head.appendChild(s);});
await sleep(2800);
const rec=await p.screencast({path:'scenes/02-hq-today.webm'});
await sleep(5200);
await p.evaluate(()=>window.scrollTo({top:150,behavior:'smooth'}));
await sleep(4200);
await p.evaluate(()=>window.scrollTo({top:0,behavior:'smooth'}));
await sleep(2600);
await rec.stop(); await sleep(1500); await b.close();
console.log('today shot (short viewport)');
