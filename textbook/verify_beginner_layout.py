"""Locate each new passage in the PDF and export representative revision previews."""
from pathlib import Path
import sys,json,re,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
from add_beginner_material import ITEMS,APPLICATIONS

path=ROOT/'深度学习与AI_Agent开发_精排版.pdf'
doc=fitz.open(path)
reference=json.loads((ROOT/'validation_reference.json').read_text(encoding='utf-8'))
author_info=json.loads((ROOT/'author_page.json').read_text(encoding='utf-8'))
texts=[p.get_text() for p in doc]
cjk=lambda s:re.sub(r'[^\u4e00-\u9fff]','',s)
flat=[cjk(t) for t in texts]
located=[]
for i,item in enumerate(ITEMS,1):
    clean=re.sub(r'<!--[\s\S]*?-->','',item['text']).strip()
    clean=re.sub(r'^小例子[：:]','',clean)
    probe=cjk(clean)[:14]
    pages=[p+1 for p,t in enumerate(flat) if probe in t]
    assert pages,(i,item['section'],probe)
    located.append({'id':i,'section':item['section'],'kind':item['kind'],'pages':pages})
links={l.get('uri') for p in doc for l in p.get_links() if l.get('uri')}
for case in APPLICATIONS:assert case['url'] in links,case['name']
author_spans=[s for b in doc[1].get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
signature=[s for s in author_spans if s['text'].strip() in author_info['authors']]
assert [s['text'].strip() for s in signature]==author_info['authors']
assert all(abs(s['size']-author_info['signature_size_pt'])<.3 for s in signature)
assert all('GreatVibes' in s['font'] for s in signature)
author_unchanged=hashlib.sha256(doc[1].get_text().encode('utf-8')).hexdigest()==reference['author_page_text_sha256']
assert author_unchanged
author={
    'pages':len(doc),'author_page_physical':2,'author_name':author_info['author'],'authors':author_info['authors'],
    'author_css_size_pt':author_info['signature_size_pt'],'author_rendered_size_pt':round(signature[0]['size'],2),
    'author_font':signature[0]['font'],'author_page_text_matches_approved_reference':author_unchanged,
    'first_page_labels':[p.get_label() for p in list(doc)[:4]],
    'source_links':[l['uri'] for l in doc[1].get_links() if 'uri' in l],
    'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
}
(ROOT/'author_page_check.json').write_text(json.dumps(author,ensure_ascii=False,indent=2),encoding='utf-8')

# Find readable sample pages after front matter, by prose or figure caption.
samples=[('参数与训练','从一次苹果计价理解学习'),('张量与形状','从成绩到张量'),
         ('卷积小方格','一个可手算的边缘模板'),('注意力手算','三项权重相加为'),
         ('近年应用','多种可能的天气'),('Agent 工具循环','一次只读排障循环')]
font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',25)
small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',19)
sheet=Image.new('RGB',(1600,1745),'#edf1ef');draw=ImageDraw.Draw(sheet)
draw.text((36,24),'深度学习与 AI Agent 开发 · 零基础讲解与应用增补',font=font,fill='#263f50')
draw.text((36,67),f'{len(doc)} 页 · 新增 92 处讲解与小例子 · 6 组原创图解 · 7 个近年应用案例',font=small,fill='#61747c')
preview=[]
out=ROOT/'_review_revised'
for i,(label,probe) in enumerate(samples):
    candidates=[j for j in range(18,len(doc)) if cjk(probe) in flat[j]]
    assert candidates,(label,probe)
    j=candidates[0]
    pix=doc[j].get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False)
    pix.save(out/f'beginner_{i+1:02}_page_{j+1:03}.png')
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    im.thumbnail((475,680),Image.Resampling.LANCZOS)
    x=35+(i%3)*520;y=157+(i//3)*780
    draw.text((x,y-34),f'{label} · 正文 {doc[j].get_label()} 页',font=small,fill='#315e7a')
    draw.rectangle((x-2,y-2,x+im.width+2,y+im.height+2),fill='#d0dadd');sheet.paste(im,(x,y))
    preview.append({'label':label,'physical':j+1,'folio':doc[j].get_label()})
sheet.save(ROOT/'零基础增补预览.png')
result={'pdf_pages':len(doc),'insertions_located':len(located),'application_links_checked':len(APPLICATIONS),
        'author_page_preserved':author_unchanged,'author_size_pt':round(signature[0]['size'],2),
        'preview_pages':preview,'passages':located}
(ROOT/'beginner_layout_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='passages'},ensure_ascii=False))
