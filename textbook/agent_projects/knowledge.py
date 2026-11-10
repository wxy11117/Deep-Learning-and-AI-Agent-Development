"""Small version-aware evidence store. All manuals are fictional teaching material."""
from pathlib import Path
import json,re,math
from collections import Counter
from core import Tool,TEXT,object_schema,ContractError
ROOT=Path(__file__).resolve().parent
DOCUMENTS=[
 {'id':'K01','version':'2.0','title':'日志保存','text':'教学设备 R2 的日志在本机保存 30 天；导出文件的保留期由用户自行设置。'},
 {'id':'K02','version':'1.0','title':'旧版日志保存','text':'教学设备 R1 的日志在本机保存 7 天。该说明不适用于 R2。'},
 {'id':'K03','version':'2.0','title':'E07 故障','text':'E07 表示采样模块未就绪。先检查采样连接，再重新启动采样模块；持续出现时转交人工维护。'},
 {'id':'K04','version':'2.0','title':'导出操作','text':'日志可在设置页导出为 CSV；导出不会清除本机已有日志。'},
 {'id':'K05','version':'2.0','title':'连接条件','text':'采样模块需要保持供电，连接断开时会停止上传；重连后只补传本机仍保留的数据。'},
 {'id':'K06','version':'2.0','title':'温度说明','text':'本教学手册没有规定温度报警阈值；需要向设备维护方核实。'}]
def grams(text):
    s=''.join(re.findall(r'[\w\u4e00-\u9fff]',text.lower()))
    return Counter(s[i:i+2] for i in range(max(0,len(s)-1)))
class KnowledgeBase:
    def __init__(self,docs=None):self.docs=DOCUMENTS if docs is None else docs
    def search(self,query,version,top_k):
        q=grams(query);qn=math.sqrt(sum(v*v for v in q.values())) or 1
        out=[]
        for d in self.docs:
            if d['version']!=version:continue
            v=grams(d['title']+d['text']);vn=math.sqrt(sum(x*x for x in v.values())) or 1
            score=sum(n*v[g] for g,n in q.items())/(qn*vn)
            if score>0:out.append({'id':d['id'],'version':d['version'],'title':d['title'],'score':round(score,6)})
        return sorted(out,key=lambda x:(-x['score'],x['id']))[:top_k]
    def read(self,doc_id,version):
        for d in self.docs:
            if d['id']==doc_id and d['version']==version:return dict(d)
        raise ContractError('document not found for this version')
    def tools(self):return [
        Tool('search_manual','检索虚构教学手册，必须指定设备文档版本；返回编号和排序分数，不返回最终答案。',object_schema({'query':TEXT,'version':{'type':'string','enum':['1.0','2.0']},'top_k':{'type':'integer','minimum':1,'maximum':3}}),self.search),
        Tool('read_manual','按编号与版本读取手册原文；引用之前必须读取。',object_schema({'doc_id':TEXT,'version':{'type':'string','enum':['1.0','2.0']}}),self.read)]
def check_answer(answer,history):
    """Checks citation existence and exact supporting quotes, not semantic entailment."""
    evidence={}
    for h in history:
        if h['role']=='tool':
            for r in h['results']:
                d=r.get('value')
                if r['ok'] and isinstance(d,dict) and 'text' in d:evidence[d['id']]=d
    if not isinstance(answer,dict) or not isinstance(answer.get('answer'),str) or not answer['answer'].strip() or type(answer.get('abstain')) is not bool:raise ContractError('bad answer envelope')
    citations=answer.get('citations')
    if not isinstance(citations,list):raise ContractError('citations must be an array')
    if not answer['abstain'] and not citations:raise ContractError('answer needs evidence')
    for c in citations:
        if not isinstance(c,dict):raise ContractError('citation must be an object')
        d=evidence.get(c.get('id'));quote=c.get('quote')
        if not d or c.get('version')!=d['version'] or not isinstance(quote,str) or not quote or quote not in d['text']:raise ContractError('invalid quote or evidence not read')
    return True
