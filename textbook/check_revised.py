"""Audit final typography, complete TOC, links, page geometry and source references."""
from pathlib import Path
import sys,json,re,ast
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'_build_deps'))
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
doc=fitz.open(ROOT/'深度学习与AI_Agent开发_精排版.pdf');out=ROOT/'_review_revised';out.mkdir(exist_ok=True)
locations=json.loads((ROOT/'page_locations.json').read_text(encoding='utf-8'))
entries=json.loads((ROOT/'toc_entries.json').read_text(encoding='utf-8'))
font=ImageFont.truetype(r'C:\Windows\Fonts\simsun.ttc',20)
info=[];fonts=set();bounds=[];labels=[]
for i,page in enumerate(doc):
    blocks=page.get_text('blocks');text=page.get_text()
    bad=[b[:4] for b in blocks if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1]
    spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    fonts.update(s['font'] for s in spans)
    body=[b for b in blocks if b[1]>60 and b[3]<790]
    info.append({'page':i+1,'label':page.get_label(),'characters':len(text),'outside_bounds':bad,'body_bottom':round(max([b[3] for b in body] or [0]),1),'body_characters':sum(len(b[4]) for b in body)})
    expected='封面' if i==0 else '作者扉页' if i==1 else str(i-locations['body_start_physical']+2) if i+1>=locations['body_start_physical'] else None
    if expected and page.get_label()!=expected:labels.append({'page':i+1,'label':page.get_label(),'expected':expected})
for start in range(0,len(doc),16):
    sheet=Image.new('RGB',(1200,1800),'#e9eeec');draw=ImageDraw.Draw(sheet)
    for j in range(start,min(start+16,len(doc))):
        pix=doc[j].get_pixmap(matrix=fitz.Matrix(.46,.46),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        x=(j-start)%4*300+13;y=(j-start)//4*450+32;sheet.paste(im,(x,y));draw.text((x,y-27),f'{j+1} / {doc[j].get_label()}',font=font,fill='#183543')
    sheet.save(out/f'contact_{start//16+1:02}.png')
selected={0,1,2,3,locations['body_start_physical']-1,len(doc)-1}
for n in [6,16,27,29,32,34,36,40,41,42,44]:
    p=locations['locations'][f'chapter-{n:02}']['physical']-1;selected.update([p,min(p+1,len(doc)-1)])
for i in sorted(selected):doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(out/f'page_{i+1:03}.png')
source=(ROOT/'深度学习与AI_Agent开发.md').read_text(encoding='utf-8')
headings=set(re.findall(r'^### (\d+\.\d+)\s',source,re.M));refs=re.findall(r'第\s*(\d+\.\d+)\s*节',source)
html=(ROOT/'深度学习与AI_Agent开发_阅读版.html').read_text(encoding='utf-8')
toc_html=re.search(r'<ol class="toc-list">(.*?)</ol>',html,re.S).group(1)
printed=dict(re.findall(r'href="#([^"]+)".*?<em>(.*?)</em>',toc_html,re.S))
overview_html=re.search(r'<ol class="overview-list toc-list">(.*?)</ol>',html,re.S).group(1)
overview_printed=dict(re.findall(r'href="#([^"]+)".*?<em>(.*?)</em>',overview_html,re.S))
overview_errors=[{'id':id,'printed':label,'actual':locations['locations'][id]['label']} for id,label in overview_printed.items() if label!=locations['locations'][id]['label']]
assert len(overview_printed)==47,'Overview must contain three parts and 44 chapters'
toc_page_mismatches=[{'id':e['id'],'printed':printed.get(e['id']),'actual':locations['locations'][e['id']]['label']} for e in entries if printed.get(e['id'])!=locations['locations'][e['id']]['label']]
toc_links=[l for p in list(doc)[locations['locations']['contents']['physical']-1:locations['body_start_physical']-1] for l in p.get_links() if l.get('page',-1)>=0 and l.get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED)]
link_errors=[]
for link in toc_links:
    id=link.get('nameddest','');expected=locations['locations'].get(id)
    if expected and link['page']+1!=expected['physical']:link_errors.append({'id':id,'actual':link['page']+1,'expected':expected['physical']})
# Compare text streams with the pre-stamp PDF: running heads must not alter main content.
raw=fitz.open(ROOT/'_review_revised/book_unstamped.pdf')
assert len(doc)==len(raw)
content_errors=[]
for i in range(len(doc)):
    original=re.sub(r'\s','',raw[i].get_text());stamped=re.sub(r'\s','',doc[i].get_text())
    if not stamped.startswith(original):content_errors.append(i+1)
result={'pages':len(doc),'chapters':44,'author_page_physical':2,'author_name':json.loads((ROOT/'author_page.json').read_text(encoding='utf-8'))['author'],'author_font_embedded':any('GreatVibes' in f for f in fonts),'author_title_font_embedded':any('BookTitleSerif' in f for f in fonts),'fonts':sorted(fonts),'songti_embedded':any('SimSun' in f for f in fonts),'heading_font_embedded':any('BookSans700' in f for f in fonts),'cover_font_embedded':any('BookSans900' in f for f in fonts),'kaiti_embedded':any('KaiTi' in f for f in fonts),
 'empty_pages':[p['page'] for p in info if p['characters']<50], 'outside_bounds':[p for p in info if p['outside_bounds']],
 'missing_section_references':sorted(set(refs)-headings),'page_label_errors':labels,'toc_entries':len(entries),'toc_page_mismatches':toc_page_mismatches,'toc_internal_links':len(toc_links),'toc_link_mismatches':link_errors,
 'overview_entries':len(overview_printed),'overview_page_mismatches':overview_errors,'stamp_content_mismatches':content_errors,
 'short_body_pages':[p['page'] for p in info if p['page']>=locations['body_start_physical'] and p['body_bottom']<250], 'page_info':info}
(ROOT/'pdf_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('page_info','fonts')},ensure_ascii=False))
print('Fonts:',', '.join(sorted(fonts)))
