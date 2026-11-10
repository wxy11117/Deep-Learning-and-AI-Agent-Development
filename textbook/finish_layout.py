"""Apply textbook running heads, folios, PDF page labels and stable TOC locations.

Always starts from Chromium's unstamped output, so repeated builds do not stack marks.
"""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
import pymupdf as fitz

def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
doc=fitz.open(ROOT/'_review_revised/book_unstamped.pdf')
entries=load('toc_entries.json');outline=doc.get_toc();locations={};chapter_starts=[];section_starts=[];parts=[]
for level,title,physical in outline:
    if level==2 and title=='版权与作者信息':locations['copyright']={'physical':physical}
    elif level==2 and title=='参考文献与资料':locations['bibliography']={'physical':physical}
    elif level==2 and title=='阅读说明':locations['reading-guide']={'physical':physical}
    elif level==2 and re.sub(r'\s','',title)=='详细目录':locations['contents']={'physical':physical}
    elif level==2 and title=='简明总目录':locations['overview']={'physical':physical}
    elif level==2 and title in ['深度学习原理与项目','大语言模型与检索','AI Agent 开发实战']:
        parts.append((physical,title));locations[f'part-{len(parts):02}']={'physical':physical}
    elif level==3 and (m:=re.match(r'第\s*(\d+)\s*章\s*(.*)',title)):
        n=int(m[1]);locations[f'chapter-{n:02}']={'physical':physical};chapter_starts.append((physical,n,title))
    elif level==4 and (m:=re.match(r'(\d+)\.(\d+)\s*(.*)',title)):
        id=f'section-{int(m[1]):02}-{int(m[2]):02}'
        locations[id]={'physical':physical};section_starts.append((physical,int(m[1]),title))
assert len(chapter_starts)==44,(len(chapter_starts),outline[:15])
assert len(parts)==3,parts
missing=[e['id'] for e in entries if e['id'] not in locations]
assert not missing,missing
body_start=parts[0][0]
reading_start=locations['reading-guide']['physical']
front_start=locations['copyright']['physical']
back_start=locations['bibliography']['physical']
author_info=load('author_page.json')
assert front_start==3 and reading_start==4 and all(name in doc[1].get_text() for name in author_info['authors']), 'Preserve cover and author page; follow with copyright and reading guide'
locations['author-page']={'physical':2,'label':'作者扉页'}
def roman(n):
    result=''
    for value,symbol in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=value:result+=symbol;n-=value
    return result
def label(physical):return '作者扉页' if physical==2 else str(physical-body_start+1) if physical>=body_start else roman(physical-front_start+1)
for value in locations.values():value['label']=label(value['physical'])
palette={'blue':'315e7a','teal':'3a756c','violet':'70618a','berry':'925b70','orange':'9a6b3f'}
themes=load('book_structure.json')['chapterThemes']
def color(hex):return tuple(int(hex[k:k+2],16)/255 for k in (0,2,4))
song_path=Path(r'C:\Windows\Fonts\simsun.ttc')
song=fitz.Font(fontfile=str(song_path));latin=fitz.Font('tiro')
left=24*72/25.4;right=doc[0].rect.width-22*72/25.4
for index,page in enumerate(doc):
    physical=index+1
    if physical in (1,2):continue
    page.insert_font(fontname='BookRunningSong',fontfile=str(song_path))
    accent=color('315e7a');head='阅读说明' if physical<locations['overview']['physical'] else '简明总目录' if physical<locations['contents']['physical'] else '详细目录'
    current=[x for x in chapter_starts if x[0]<=physical]
    is_part=physical in [x[0] for x in parts]
    if current and not is_part:
        cp,n,title=current[-1];accent=color(palette[themes[n-1][0]])
        sections=[x for x in section_starts if x[0]<=physical and x[1]==n]
        head=(sections[-1][2] if physical%2 and sections and physical!=cp else title)
    elif physical>=body_start:
        head=next(t for p,t in parts if p==physical)
    # The title page carries no running head; part openers retain a folio only.
    if physical==front_start:head='版权与作者信息'
    elif physical>=back_start:head='参考文献与资料'
    if not is_part:
        size=8.3
        while song.text_length(head,fontsize=size)>right-left and size>6.8:size-=.2
        x=left if physical%2==0 else right-song.text_length(head,fontsize=size)
        page.insert_text((x,46),head,fontname='BookRunningSong',fontsize=size,color=color('687378'))
        page.draw_line((left,53),(right,53),color=color('cbd2d4'),width=.45)
    page.insert_text((left,811),'深度学习与 AI Agent 开发：原理、实战与应用',fontname='BookRunningSong',fontsize=7.5,color=color('58666d'))
    folio=label(physical);width=latin.text_length(folio,fontsize=10.5)
    page.draw_line((right-width-17,806),(right-width-9,806),color=accent,width=2)
    page.insert_text((right-width,811),folio,fontname='tiro',fontsize=10.5,color=color('253e4d'))
doc.set_page_labels([{'startpage':0,'prefix':'封面'},{'startpage':1,'prefix':'作者扉页'},{'startpage':front_start-1,'style':'r','firstpagenum':1},{'startpage':body_start-1,'style':'D','firstpagenum':1}])
outline.insert(1,[2,'作者扉页',2]);doc.set_toc(outline)
metadata=doc.metadata;metadata.update({'title':'深度学习与 AI Agent 开发：原理、实战与应用','author':author_info['author'],'subject':f"修订版；44 章、{load('layout_check.json')['figures']} 组图示、8 个项目与真实模型综合案例",'keywords':'深度学习,机器学习,AI Agent,教材,项目实践'})
doc.set_metadata(metadata)
doc.subset_fonts()
doc.save(ROOT/'深度学习与AI_Agent开发_精排版.pdf',garbage=4,deflate=True)
result={'pages':len(doc),'author_pages':1,'copyright_pages':reading_start-front_start,'body_start_physical':body_start,'front_pages':body_start-front_start,'body_pages':back_start-body_start,'reference_pages':len(doc)-back_start+1,'locations':locations}
(ROOT/'page_locations.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'chapter_pages.json').write_text(json.dumps({str(n):p for p,n,_ in chapter_starts},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='locations'},ensure_ascii=False))
