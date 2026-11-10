"""Render the reviewed bibliography and publication page from structured records."""
from pathlib import Path
import json,html,re
ROOT=Path(__file__).resolve().parent
refs=json.loads((ROOT/'publication/references.json').read_text(encoding='utf-8'))
esc=lambda s:html.escape(str(s),quote=True)

def author_short(e):
    names=[]
    for name in e['authors'][:3]:
        if ', ' in name:
            family,given=name.split(', ',1)
            initials=' '.join(x[0].upper() for x in re.findall(r'[^\W\d_]+',given,re.U))
            names.append(family.upper()+' '+initials)
        else:names.append(name)
    return ', '.join(names)+(', et al.' if len(e['authors'])>3 else '')

def format_entry(e):
    tags={'article':'J','inproceedings':'C/OL','preprint':'EB/OL','online':'EB/OL','software':'CP/OL','dataset':'DS/OL'}
    head=author_short(e).rstrip('.')+'. '+e['title']+'['+tags[e['kind']]+'].'
    container=e['container']
    if e.get('series'):container+=' ('+e['series']+')'
    date=e.get('date') or e.get('year','')
    tail=container+(', '+date if date else '')
    if e.get('volume'):tail+=', '+e['volume']
    if e.get('issue'):tail+='('+e['issue']+')'
    if e.get('pages'):tail+=': '+e['pages']
    if e.get('arxiv') and e['kind']=='preprint':tail+='，arXiv:'+e['arxiv']
    text=esc(head)+' '+esc(tail)+'.'
    doi=e.get('doi')
    if doi:
        text+=' DOI: <a href="https://doi.org/'+esc(doi)+'">'+esc(doi)+'</a>.'
    else:
        text+=' <a class="reference-url" href="'+esc(e['url'])+'">'+esc(e['url'])+'</a>.'
    text+=' <span class="reference-access">[访问日期：'+e['accessed']+']</span>'
    places=('第 '+ '、'.join(str(x) for x in e['chapters'])+' 章') if e['chapters'] else e['location']
    return '<p class="reference-entry" id="ref-'+str(e['number']).zfill(3)+'"><span class="reference-label">['+str(e['number'])+']</span> '+text+'<span class="reference-locator">引用位置：'+esc(places)+'</span></p>'

intro='''本表按正文中资料首次出现的顺序编号，随后补列原始数据与题辞来源。文中方括号编号可跳转到相应条目。正式发表的论文优先记录会议或期刊信息；预印本与正式发表年份分别保留，正文介绍研究历史时仍可能使用预印本年份。在线资料的访问日期统一为 2026 年 11 月 11 日。

期刊条目列出卷期、页码或文章号和 DOI；电子会议论文采用官方提供的卷页信息与论文入口。软件文档按核对时的页面与版本著录，实验所用依赖版本见各项目说明。'''
md='## 参考文献与资料\n\n'+intro+'\n\n'+'\n\n'.join(format_entry(e) for e in refs['entries'])+'\n'
(ROOT/'参考文献.md').write_text(md,encoding='utf-8')

copyright='''## 版权与作者信息

<div class="publication-book-title">深度学习与 AI Agent 开发<br><span>原理 · 实战 · 应用</span></div>

<dl class="publication-facts">
<dt>作者署名</dt><dd>Violet · Star · Sapphire</dd>
<dt>版本</dt><dd>2026 年 11 月修订版</dd>
<dt>内容规模</dt><dd>44 章 · 68 组正文图示 · 8 个基础项目</dd>
<dt>资料形态</dt><dd>PDF、离线阅读版、源稿与项目资料包</dd>
</dl>

<p class="publication-copyright">© 2026 Violet、Star、Sapphire</p>

**正文与图表。** 本书正文、原创图表、封面与作者扉页保留版权。引用请标明书名、作者、版本与章节；转载、改编、再版及其他授权使用请取得权利人许可。

**配套代码。** 为本书编写的原创代码采用 MIT License，允许使用、修改、再分发及商用，并须保留版权与许可文本。完整条款见资料包中的 LICENSE-CODE.txt，文件范围见 LICENSE.md 及配套许可清单。

**第三方资料。** 软件、字体、公开数据与 LungSight 来源快照保持各自权利和许可。出处与分发方式见 THIRD_PARTY_NOTICES.md；正文引用集中收录于卷末参考文献。

**配套资料与仓库。** 本书相关配套资料与代码均已上传至公开仓库：
[github.com/wxy11117/Deep-Learning-and-AI-Agent-Development](https://github.com/wxy11117/Deep-Learning-and-AI-Agent-Development)。读者也可通过[在线阅读入口](https://wxy11117.github.io/Deep-Learning-and-AI-Agent-Development/)直接阅读本书。正文与图表保留版权，原创代码采用 MIT，第三方资料遵循各自许可；具体使用范围与本页及仓库中的许可文件一致。

'''
(ROOT/'版权页.md').write_text(copyright,encoding='utf-8')

# BibLaTeX-compatible .bib preserves full author names and online access dates.
def protect(s):return str(s).replace('\\','\\textbackslash{}').replace('&','\\&').replace('%','\\%').replace('_','\\_')
bib=[]
for e in refs['entries']:
    kind=e['kind'] if e['kind'] in ('article','inproceedings') else 'misc' if e['kind']=='preprint' else 'online'
    authors=['{'+a+'}' if a in e.get('corporate_authors',[]) else a for a in e['authors']]
    fields={'author':' and '.join(authors),'title':'{'+e['title']+'}','url':e['url'],'urldate':e['accessed']}
    if e.get('year'):fields['year']=e['year']
    if kind=='article':fields['journal']=e['container']
    elif kind=='inproceedings':fields['booktitle']=e['container']
    else:fields['howpublished']=e['container']
    for src,dest in [('volume','volume'),('issue','number'),('pages','pages'),('doi','doi')]:
        if e.get(src):fields[dest]=e[src].replace('-','--') if src=='pages' else e[src]
    notes=list(e['notes'])
    if e.get('preprint_year') and e['preprint_year']!=e.get('year'):
        notes.append('预印本首发年份：'+e['preprint_year']+'；正式发表年份：'+e['year']+'。')
    if notes:fields['note']=' '.join(notes)
    bib.append('@'+kind+'{'+e['key']+',\n'+',\n'.join('  '+k+' = {'+(v if k in ('url','doi') else protect(v))+'}' for k,v in fields.items())+'\n}\n')
(ROOT/'publication/references.bib').write_text('\n'.join(bib),encoding='utf-8')
print(json.dumps({'references':len(refs['entries']),'copyright_page':True,'authors':['Violet','Star','Sapphire'],'code_license':'MIT'},ensure_ascii=False))
