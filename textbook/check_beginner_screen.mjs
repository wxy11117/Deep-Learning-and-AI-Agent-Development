import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const MODULES=process.env.BOOK_NODE_MODULES||(fs.existsSync(path.join(ROOT,'node_modules','playwright'))?path.join(ROOT,'node_modules'):'C:/Users/Lenovo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {chromium}=require(path.join(MODULES,'playwright'));
let browser;try{browser=await chromium.launch({channel:'msedge',headless:true});}catch{browser=await chromium.launch({headless:true});}
const page=await browser.newPage();
await page.goto(pathToFileURL(path.join(ROOT,'深度学习与AI_Agent开发_阅读版.html')).href);
await page.evaluate(()=>document.fonts.ready);
const reports=[];
for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  const result=await page.evaluate(()=>{
    const author=document.querySelector('.author-page');const box=author.getBoundingClientRect();
    return {width:innerWidth,scroll:document.documentElement.scrollWidth,
      titleFont:getComputedStyle(document.querySelector('.author-title')).fontFamily,
      latinFont:getComputedStyle(document.querySelector('.author-latin')).fontFamily,
      authorFont:getComputedStyle(document.querySelector('.author-name')).fontFamily,
      authorFontPx:getComputedStyle(document.querySelector('.author-name')).fontSize,
      authors:[...document.querySelectorAll('.author-name')].map(e=>e.textContent),
      clipped:[...author.querySelectorAll('.author-title,.author-name,.author-quote')].filter(e=>{const r=e.getBoundingClientRect();return r.right>box.right+1||r.bottom>box.bottom+1||r.left<box.left-1;}).map(e=>e.className),
      order:[...document.querySelector('main').children].slice(0,3).map(e=>e.id),
      applicationCount:document.querySelectorAll('aside.application').length,
      figureCount:document.querySelectorAll('figure').length,
      brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length};
  });
  if(result.width!==result.scroll||result.clipped.length||result.brokenImages||result.applicationCount!==7||result.figureCount!==68||result.authors.join(',')!=='Violet,Star,Sapphire')throw new Error(JSON.stringify(result));
  reports.push(result);
}
fs.writeFileSync(path.join(ROOT,'author_screen_check.json'),JSON.stringify(reports,null,2));
await browser.close();console.log(JSON.stringify(reports,null,2));
