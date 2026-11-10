import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url), ROOT=path.dirname(fileURLToPath(import.meta.url));
const MODULES=process.env.BOOK_NODE_MODULES||(fs.existsSync(path.join(ROOT,'node_modules','marked'))?path.join(ROOT,'node_modules'):'C:/Users/Lenovo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {marked}=await import(pathToFileURL(path.join(MODULES,'marked/lib/marked.esm.js')));
const {chromium}=require(path.join(MODULES,'playwright'));
const KATEX=path.join(ROOT,'vendor/katex/package/dist'),katex=require(path.join(KATEX,'katex.js'));
const read=n=>fs.readFileSync(path.join(ROOT,n),'utf8').replace(/^\uFEFF/,'');
const source=read('深度学习与AI_Agent开发.md').replaceAll('\r\n','\n');
const {chapterThemes,partPages}=JSON.parse(read('book_structure.json'));
const annotations=JSON.parse(read('layout_annotations.json'));
const authorInfo=JSON.parse(read('author_page.json'));
const referenceInfo=JSON.parse(read('publication/references.json'));
const referenceNumbers=new Map(referenceInfo.entries.flatMap(e=>[e.source_url,e.url].map(url=>[url,e.number])));
function addCitationNumbers(html){return html.replace(/<a href="([^"]+)"([^>]*)>([\s\S]*?)<\/a>/g,(all,url)=>{const number=referenceNumbers.get(url.replaceAll('&amp;','&'));return number?all+'<sup class="citation-ref"><a href="#ref-'+String(number).padStart(3,'0')+'" aria-label="参考文献 '+number+'">['+number+']</a></sup>':all;});}
const pageMap=fs.existsSync(path.join(ROOT,'page_locations.json'))?JSON.parse(read('page_locations.json')).locations:{};
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const embed=(n,mime)=>'data:'+mime+';base64,'+fs.readFileSync(path.join(ROOT,n)).toString('base64');
let mathCount=0,figureCount=0,currentChapter=0,chapterFigure=0,equation=0,example=0;
const semanticCounts={examples:0,worked:0,notes:0,counterexamples:0,answers:0,beginnerExamples:0,applications:0};
const tocEntries=[],chapters=[],titles=[];
// Keep print headings at phrase boundaries; navigation retains the full title.
const twoLineTitles=new Set([2,14,18,24,26,27,30,32,33,34,35,36,37,38,39,40,42,43,44]);
function chapterTitleHTML(number,title){
 if(!twoLineTitles.has(number))return escape(title);
 const split=number===44?title.indexOf('、')+1:title.indexOf('：')+1;
 if(split<1)throw new Error('Missing title phrase boundary: '+number);
 return escape(title.slice(0,split))+'<br class="chapter-title-break">'+escape(title.slice(split));
}
function mathRender(text){
 const stash=[];
 function token(expr,display){
  const rendered=katex.renderToString(expr.trim(),{displayMode:display,throwOnError:true,strict:'ignore',output:'html'});
  mathCount++;
  const id='BOOKMATHTOKEN'+stash.length+'END';
  const number=display&&currentChapter?'<span class="eq-number">('+currentChapter+'.'+(++equation)+')</span>':'';
  stash.push({id,html:display?'<div class="math-display">'+rendered+number+'</div>':'<span class="math-inline">'+rendered+'</span>'});
  return display?'\n\n'+id+'\n\n':id;
 }
 text=text.replace(/\$\$([\s\S]*?)\$\$/g,(_,m)=>token(m,true)).replace(/\\\(([\s\S]*?)\\\)/g,(_,m)=>token(m,false));
 let html=marked.parse(text);
 for(const {id,html:fragment} of stash)html=html.replace('<p>'+id+'</p>',fragment).replaceAll(id,fragment);
 return html;
}
function figureHTML(name,caption){
 const ext=fs.existsSync(path.join(ROOT,'figures',name+'.svg'))?'svg':'png';
 const img=embed('figures/'+name+'.'+ext,ext==='svg'?'image/svg+xml':'image/png');
 caption=caption.replace(/^图 \d+ · /,'');figureCount++;chapterFigure++;
 return '<figure class="'+(name.startsWith('diagram_')||name.startsWith('beginner_')?'structural':'quantitative')+'" data-figure="'+figureCount+'"><img alt="'+escape(caption)+'" src="'+img+'"><figcaption><strong>图 '+currentChapter+'.'+chapterFigure+'</strong>　'+caption+'</figcaption></figure>\n\n';
}
function styleParagraphs(html){
 return html.replace(/<p>([\s\S]*?)<\/p>/g,(all,content)=>{
  const plain=content.replace(/<[^>]*>/g,'');
  if(/^小例子[：:]/.test(plain)){semanticCounts.beginnerExamples++;return '<p class="example beginner-example"><strong class="example-label">从小例子理解</strong>'+content.replace(/^小例子[：:]\s*/,'')+'</p>';}
  if(/^例[：:]/.test(plain)){semanticCounts.examples++;return '<p class="example"><strong class="example-label">算例 '+currentChapter+'.'+(++example)+'</strong>'+content.replace(/^例[：:]\s*/,'')+'</p>';}
  if(/^参考解答[：:]/.test(plain)){semanticCounts.answers++;return '<p class="answer"><strong class="answer-label">参考解答</strong>'+content.replace(/^参考解答[：:]\s*/,'')+'</p>';}
  if(annotations.notes.some(x=>plain.startsWith(x))){semanticCounts.notes++;return '<p class="note"><strong class="note-label">注</strong>'+content+'</p>';}
  if(annotations.counterexamples.some(x=>plain.startsWith(x))){semanticCounts.counterexamples++;return '<p class="counterexample"><strong class="example-label">反例与辨析</strong>'+content+'</p>';}
  return all;
 });
}
const chunks=source.split('<a id="book-references"></a>')[0].split(/<a id="chapter-\d+"><\/a>\s*\n/).slice(1);
if(chunks.length!==44)throw new Error('Expected 44 chapters');
for(let i=0;i<chunks.length;i++){
 currentChapter=i+1;chapterFigure=0;equation=0;example=0;
 let chunk=chunks[i].replace(/\n---\s*$/,'');
 const match=chunk.match(/^## 第 (\d+) 章　([^\n]+)\n/);if(!match)throw new Error('Chapter '+i);
 const n=String(i+1).padStart(2,'0'),title=match[2],[theme,topic]=chapterThemes[i];titles.push(title);chunk=chunk.slice(match[0].length);
 let part='';
 if(partPages[i]){
  const pnum=String(Object.keys(partPages).indexOf(String(i))+1).padStart(2,'0');
  part=partPages[i].replace('<section class=', '<section id="part-'+pnum+'" class=');
  const pt=part.match(/<div class="part-title">([^<]+)<\/div>/)[1];
  part=part.replace(/<div class="part-title">([^<]+)<\/div>/,'<h2>$1</h2>').replace(/<div class="part-navigation">.*?<\/div>/,'');
  tocEntries.push({id:'part-'+pnum,type:'part',theme,title:'第 '+Number(pnum)+' 篇　'+pt});
 }
 tocEntries.push({id:'chapter-'+n,type:'chapter',theme,title:'第 '+(i+1)+' 章　'+title});
 const sectionParts=chunk.split(/(?=^### \d+\.\d+\s)/m);
 let html='';
 for(let block of sectionParts){
  const heading=block.match(/^### (\d+\.\d+)\s+([^\n]+)\n/);
  let head='',worked=false;
  if(heading){
   const id='section-'+heading[1].split('.').map(x=>x.padStart(2,'0')).join('-');
   tocEntries.push({id,type:'section',theme,title:heading[1]+'　'+heading[2]});
   head='<h4 id="'+id+'">'+escape(heading[1]+'　'+heading[2])+'</h4>';
   worked=annotations.worked_sections.includes(heading[1]);
   block=block.slice(heading[0].length);
  }
  block=block.replace(/<!-- FIG:([\w]+)\|([\s\S]*?) -->/g,(_,name,caption)=>figureHTML(name,caption.trim()));
  let body=addCitationNumbers(styleParagraphs(mathRender(block))).replaceAll('<h4>','<h5>').replaceAll('</h4>','</h5>');
  body=body.replace(/<!-- APPLICATION:([^>]+) -->([\s\S]*?)<!-- \/APPLICATION -->/g,(_,title,content)=>{semanticCounts.applications++;return '<aside class="application"><div class="application-kicker">近年应用 · 原理在现场</div><div class="application-title">'+escape(title)+'</div>'+content+'</aside>';});
  if(worked){semanticCounts.worked++;body='<div class="worked-example"><div class="worked-title">推演与计算</div>'+body+'</div>';}
  html+=head+body;
 }
 chapters.push(part+'<section class="chapter theme-'+theme+'" id="chapter-'+n+'"><header class="chapter-head"><div class="chapter-label">CHAPTER '+n+'</div><h3>第 '+(i+1)+' 章　'+chapterTitleHTML(i+1,title)+'</h3><div class="chapter-topic">'+escape(topic)+'</div></header>'+html+'</section>');
}
currentChapter=0;
const copyrightPage='<section class="copyright-page theme-blue" id="copyright">'+marked.parse(read('版权页.md'))+'</section>';
const downloadIcon='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 3v12m-5-5 5 5 5-5M5 16v4h14v-4"/></svg>';
const readerDownloads='<div class="reader-downloads" id="downloads" role="group" aria-label="下载本书与配套资料"><div class="reader-download-actions"><a class="reader-download-link reader-download-pdf" href="https://wxy11117.github.io/Deep-Learning-and-AI-Agent-Development/book.pdf" download="深度学习与AI_Agent开发_精排版.pdf">'+downloadIcon+'<span>下载 PDF 版</span></a><a class="reader-download-link reader-download-bundle" href="https://github.com/wxy11117/Deep-Learning-and-AI-Agent-Development/releases/download/v2026.11/Deep-Learning-and-AI-Agent-Development-materials-v2026.11.zip" download="深度学习与AI_Agent开发_完整资料.zip">'+downloadIcon+'<span>下载完整资料包</span></a></div><p class="reader-download-note">PDF 适合阅读与打印；资料包包含离线阅读版、源稿、代码和实验记录。</p></div>';
const bibliography='<section class="bibliography theme-blue" id="bibliography">'+marked.parse(read('参考文献.md'))+readerDownloads+'</section>';
const introduction=source.split('## 阅读说明\n')[1].split('## 目录')[0];
const front='<section class="front" id="reading-guide"><h2>阅读说明</h2><p class="lead">理解模型怎样学习，也理解系统怎样行动。</p>'+mathRender(introduction)+'<p class="edition-note">修订版 · 2026 年 11 月<br>正文宋体；标题黑体；注记楷体。章节、公式与图示均可按编号回查。</p></section>';
function tocRow(item){return '<li class="toc-'+item.type+' theme-'+(item.theme||'blue')+'"><a href="#'+item.id+'"><span class="toc-title">'+escape(item.title)+'</span><span class="dots"></span><em>'+escape(String(pageMap[item.id]?.label||'—'))+'</em></a></li>';}
const overview='<section class="contents overview" id="overview"><h2>简明总目录</h2><p class="toc-note">先看三篇主线与章名；逐节查找请使用后面的详细目录或 PDF 书签。编程入门保留在第 21 章。</p><ol class="overview-list toc-list">'+tocEntries.filter(e=>e.type!=='section').map(tocRow).join('')+'</ol></section>';
const contents='<section class="contents" id="contents"><h2>详细目录</h2><p class="toc-note">前置部分使用罗马页码，正文与卷末参考文献连续使用阿拉伯页码。点击条目可跳转到章或节。</p><ol class="toc-list">'+tocRow({id:'copyright',type:'front',title:'版权与作者信息'})+tocRow({id:'reading-guide',type:'front',title:'阅读说明'})+tocRow({id:'overview',type:'front',title:'简明总目录'})+tocEntries.map(tocRow).join('')+tocRow({id:'bibliography',type:'front',title:'参考文献与资料'})+'</ol></section>';
const cover='<section class="cover" id="cover"><div class="cover-top">从神经网络到智能体系统</div><h1 aria-label="深度学习与 AI Agent 开发"><span class="title-a">深度学习</span><span class="title-b"><span class="cover-and">与</span>AI Agent 开发</span></h1><p class="cover-subtitle">原理 · 实战 · 应用</p><div class="cover-english">DEEP LEARNING &amp; AI AGENT DEVELOPMENT<br>PRINCIPLES, PRACTICE AND APPLICATIONS</div><img class="cover-art" alt="原创的信号交织与激活点阵" src="'+embed('figures/cover_signal_weave.svg','image/svg+xml')+'"><div class="cover-bottom"><div class="cover-tagline">数学 · 模型 · 工具 · 状态<br>从计算原理走向完整项目</div><div class="cover-meta">44 章 · '+figureCount+' 组图示 · 8 个项目<br>附推导、源代码与实际运行记录<br>2026 年 11 月 · 修订版</div></div></section>';
const nav='<a href="#copyright">版权与作者信息</a>'+titles.map((t,i)=>'<a href="#chapter-'+String(i+1).padStart(2,'0')+'"><span>'+String(i+1).padStart(2,'0')+'</span>'+escape(t)+'</a>').join('')+'<a href="#bibliography">参考文献与资料</a>';
const authorPage='<section class="author-page" id="author-page" aria-label="作者扉页"><div class="author-book"><div class="author-title">深度学习<span class="author-second">与 <span class="author-latin">AI Agent</span> 开发</span></div><div class="author-subtitle">原理 · 实战 · 应用</div><div class="author-english">DEEP LEARNING &amp; AI AGENT DEVELOPMENT</div><div class="author-rule"></div></div><img class="author-art" alt="原创图示：数据经神经网络学习表示，通过因果注意力建立关联，连接模型、工具与观察组成的 Agent 工作循环" src="'+embed(authorInfo.artwork,'image/svg+xml')+'"><div class="author-signature"><span class="author-label">作　者</span><span class="author-names">'+authorInfo.authors.map(name=>'<span class="author-name">'+escape(name)+'</span>').join('')+'</span></div><blockquote class="author-quote"><p>'+authorInfo.quote.map(escape).join('<br>')+'</p><cite>—— '+escape(authorInfo.attribution)+'</cite><a class="quote-source" href="'+escape(authorInfo.source_url)+'">'+escape(authorInfo.source_note)+'</a></blockquote></section>';
let katexCSS=read('vendor/katex/package/dist/katex.min.css').replace(/url\(([^)]+)\)/g,(_,value)=>{const rel=value.replace(/["']/g,'');return 'url(data:font/'+path.extname(rel).slice(1)+';base64,'+fs.readFileSync(path.join(KATEX,rel)).toString('base64')+')';});
let css=read('book.css').replace(/url\('([^']+\.ttf)'\)/g,(_,n)=>'url('+embed(n,'font/ttf')+')');
const html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="'+escape(authorInfo.author)+'"><meta name="copyright" content="2026 Violet, Star, Sapphire; original companion code MIT; book text and figures rights reserved"><title>深度学习与 AI Agent 开发：原理、实战与应用</title><style>'+katexCSS+'\n'+css+'</style></head><body><nav class="sidebar" aria-label="章节导航"><div class="brand">深度学习与<br>AI Agent 开发</div><div class="edition">PRINCIPLES · PRACTICE · APPLICATIONS</div>'+nav+'</nav><main>'+cover+authorPage+copyrightPage+front+overview+contents+chapters.join('\n')+bibliography+'</main></body></html>';
const htmlPath=path.join(ROOT,'深度学习与AI_Agent开发_阅读版.html');fs.writeFileSync(htmlPath,html);
fs.writeFileSync(path.join(ROOT,'toc_entries.json'),JSON.stringify([{id:'copyright',type:'front',title:'版权与作者信息'},{id:'reading-guide',type:'front',title:'阅读说明'},{id:'overview',type:'front',title:'简明总目录'},...tocEntries,{id:'bibliography',type:'back',title:'参考文献与资料'}],null,2));
let browser;try{browser=await chromium.launch({channel:'msedge',headless:true});}catch{browser=await chromium.launch({headless:true});}
const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
await page.goto(pathToFileURL(htmlPath).href);await page.evaluate(()=>document.fonts.ready);
await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
const check=await page.evaluate(()=>({chapters:document.querySelectorAll('.chapter').length,bodyFont:getComputedStyle(document.querySelector('.chapter p')).fontFamily,songtiAvailable:document.fonts.check('16px SimSun'),headingFont:getComputedStyle(document.querySelector('.chapter h4')).fontFamily,coverFont:getComputedStyle(document.querySelector('.cover h1')).fontFamily,figures:document.querySelectorAll('figure').length,math:document.querySelectorAll('.math-display,.math-inline').length,katexErrors:document.querySelectorAll('.katex-error').length,overflows:[...document.querySelectorAll('table,pre')].filter(e=>e.scrollWidth>e.clientWidth+3).length}));
await page.emulateMedia({media:'print'});
const widthStyle=await page.addStyleTag({content:'body{width:619.8425px!important}'});
// Fit only long display equations; minimum size and report make the change reviewable.
const fitted=await page.evaluate(()=>{
 const results=[];
 for(const box of document.querySelectorAll('.math-display')){
  const equation=box.querySelector('.katex-display>.katex');if(!equation)continue;
  const styles=getComputedStyle(box),available=box.clientWidth-parseFloat(styles.paddingLeft)-parseFloat(styles.paddingRight);
  const natural=equation.getBoundingClientRect().width;
  if(natural>available){const before=parseFloat(styles.fontSize),after=before*available/natural*.98;box.style.fontSize=after+'px';results.push({number:box.querySelector('.eq-number')?.textContent,pt:after*.75});}
 }
 return results;
});
const printCheck=await page.evaluate(()=>({overflows:[...document.querySelectorAll('.math-display,table,pre')].filter(e=>e.scrollWidth>e.clientWidth+3).map(e=>({tag:e.tagName,width:e.clientWidth,scroll:e.scrollWidth,text:e.textContent.slice(0,70)})),oversizedFigures:[...document.querySelectorAll('figure')].filter(e=>e.getBoundingClientRect().height>950).map(e=>e.dataset.figure)}));
await widthStyle.evaluate(e=>e.remove());
if(check.katexErrors||check.overflows||printCheck.overflows.length||printCheck.oversizedFigures.length)throw new Error(JSON.stringify({check,printCheck}));
fs.mkdirSync(path.join(ROOT,'_review_revised'),{recursive:true});
if(!process.argv.includes('--html-only'))await page.pdf({path:path.join(ROOT,'_review_revised/book_unstamped.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,outline:true,tagged:true});
await page.emulateMedia({media:'screen'});await page.setViewportSize({width:390,height:844});
const mobile=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
await browser.close();
const result={...check,mathCount,mobile,printCheck,fittedEquations:fitted,semanticCounts,tocEntries:tocEntries.length+4,references:referenceInfo.entries.length};
fs.writeFileSync(path.join(ROOT,'layout_check.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
