import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const DIR=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.dirname(DIR);
const MODULES=process.env.BOOK_NODE_MODULES ||
 (fs.existsSync(path.join(ROOT,'node_modules','playwright'))?path.join(ROOT,'node_modules'):
 'C:/Users/Lenovo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {chromium}=require(path.join(MODULES,'playwright'));
const source=fs.readFileSync(path.join(DIR,'structures.md'),'utf8')+'\n'+fs.readFileSync(path.join(DIR,'agent_structures.md'),'utf8');
const entries=[...source.matchAll(/<!-- FIG:(\w+) -->\s*~~~mermaid\n([\s\S]*?)\n~~~/g)];
let browser;
try{browser=await chromium.launch({channel:'msedge',headless:true});}
catch{browser=await chromium.launch({headless:true});}
const page=await browser.newPage({viewport:{width:1400,height:1200},deviceScaleFactor:2});
await page.setContent('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;padding:24px;background:white;font-family:"SimSun",serif}#diagram{display:inline-block}svg{display:block}</style></head><body><div id="diagram"></div></body></html>');
await page.addScriptTag({path:path.join(ROOT,'vendor/mermaid/mermaid.min.js')});
await page.evaluate(()=>mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'default',fontFamily:'SimSun, serif',flowchart:{htmlLabels:false,curve:'basis',nodeSpacing:28,rankSpacing:42},themeVariables:{fontSize:'17px'}}));
for(const [_,name,code] of entries){
    const svg=await page.evaluate(async ({name,code})=>{
        const {svg}=await mermaid.render(name,code);
        document.getElementById('diagram').innerHTML=svg;
        const el=document.querySelector('#diagram svg');
        const vb=el.viewBox.baseVal;
        el.style.maxWidth='none';el.setAttribute('width',String(vb.width));el.setAttribute('height',String(vb.height));
        return el.outerHTML;
    },{name,code});
    fs.writeFileSync(path.join(DIR,name+'.svg'),svg);
    await page.locator('#diagram').screenshot({path:path.join(DIR,name+'.png')});
    console.log(name);
}
await browser.close();
