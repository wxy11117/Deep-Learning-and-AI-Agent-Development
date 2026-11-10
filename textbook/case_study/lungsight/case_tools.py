"""Three read-only tools exposing frozen public excerpts and labeled teaching data."""
from pathlib import Path
import sys,json,math
from collections import Counter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'agent_projects'))
from core import Tool,TEXT,object_schema,ContractError
from knowledge import grams

class CaseStore:
    def __init__(self,inject_timeout=False,recover_timeout=True):
        self.docs=json.loads((ROOT/'documents.json').read_text(encoding='utf-8'))
        self.tasks=json.loads((ROOT/'teaching_tasks.json').read_text(encoding='utf-8'))
        self.revision=json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8'))['commit']
        self.inject_timeout=inject_timeout;self.recover_timeout=recover_timeout;self.timeout_injected=False
        self.events=[]
    def search(self,query,top_k):
        if self.inject_timeout and not self.timeout_injected:
            self.timeout_injected=True;self.events.append({'event':'injected_timeout','tool':'search_project_docs'})
            if self.recover_timeout:raise ContractError('TEMPORARY_TIMEOUT: teaching fault injection; retry this read-only search once.')
            raise TimeoutError('Injected read-only search timeout; unhandled baseline adapter.')
        q=grams(query);qn=math.sqrt(sum(v*v for v in q.values())) or 1
        results=[]
        for d in self.docs:
            g=grams(d['title']+' '+d['text']);gn=math.sqrt(sum(v*v for v in g.values())) or 1
            score=sum(n*g[k] for k,n in q.items())/(qn*gn)
            if score>0:results.append({'id':d['id'],'version':d['version'],'title':d['title'],'score':round(score,6)})
        return {'revision':self.revision,'matches':sorted(results,key=lambda r:(-r['score'],r['id']))[:top_k]}
    def read(self,doc_id,version):
        for d in self.docs:
            if d['id']==doc_id and d['version']==version:return dict(d)
        raise ContractError('Document or requested version not available')
    def task(self,task_id):
        if task_id not in self.tasks:raise ContractError('TASK_NOT_FOUND: '+task_id)
        task=self.tasks[task_id];rows=task['fold_probabilities'];labels=task['class_labels']
        means=[round(sum(row[k] for row in rows)/len(rows),6) for k in range(len(labels))]
        winners=[labels[max(range(len(labels)),key=lambda k:r[k])] for r in rows]
        ordered=sorted(range(len(labels)),key=lambda k:means[k],reverse=True)
        return {**task,'id':task_id,'version':task['model_version'],
                'text':'教学构造数据，A/B/C/D 为抽象类别；以下数值由程序对五折概率计算。',
                'mean_probabilities':dict(zip(labels,means)),
                'fold_top_classes':winners,'top_class':labels[ordered[0]],
                'fold_agreement':max(Counter(winners).values())/len(winners),
                'top_two_margin':round(means[ordered[0]]-means[ordered[1]],6),
                'class_spreads':{label:round(max(r[k] for r in rows)-min(r[k] for r in rows),6) for k,label in enumerate(labels)}}
    def tools(self):
        return [
          Tool('search_project_docs','检索固定版本的 LungSight 公开资料，返回候选编号与标题；要引用正文再调用 read_source。',object_schema({'query':TEXT,'top_k':{'type':'integer','minimum':1,'maximum':4}}),self.search),
          Tool('read_source','按搜索得到的编号与 version 读取原文及 GitHub 出处；版本须使用搜索结果。',object_schema({'doc_id':TEXT,'version':TEXT}),self.read),
          Tool('get_task_summary','读取教学任务的五折概率、平均值、一致比例和模型版本；仅含人工构造的 A/B/C/D 示例。',object_schema({'task_id':TEXT}),self.task)]

def score(case,result):
    expected=case['expected'];checks={};reason=[]
    try:
        answer=json.loads(result['text'])
    except (KeyError,json.JSONDecodeError,TypeError):return {'passed':False,'checks':{'json':False},'reason':['final output is not the requested JSON']}
    checks['json']=isinstance(answer,dict)
    if not checks['json']:return {'passed':False,'checks':checks,'reason':['answer must be object']}
    checks['status']=answer.get('status')==expected['status']
    actual=answer.get('value');wanted=expected['value']
    checks['value']=(type(actual) in (int,float) and type(actual) is not bool and math.isfinite(actual) and math.isclose(actual,wanted,abs_tol=1e-6)) if type(wanted) in (int,float) else type(actual)==type(wanted) and actual==wanted
    evidence={};used_tools=[]
    for event in result.get('history',[]):
        if event['role']=='assistant':used_tools += [x['name'] for x in event.get('calls',[])]
        if event['role']=='tool':
            for item in event['results']:
                v=item.get('value')
                if item['ok'] and isinstance(v,dict) and 'text' in v and 'id' in v:evidence[v['id']]=v
    citations=answer.get('citations',[])
    checks['citations']=isinstance(citations,list)
    cited=set()
    if checks['citations']:
        for c in citations:
            if not isinstance(c,dict):checks['citations']=False;continue
            d=evidence.get(c.get('id'));quote=c.get('quote')
            if not d or c.get('version')!=d['version'] or not isinstance(quote,str) or not quote or quote not in d['text']:
                checks['citations']=False
            else:cited.add(c['id'])
    checks['required_sources']=set(expected['source_ids'])<=cited
    checks['task_read']=expected['task_id'] is None or expected['task_id'] in evidence
    checks['looked_up']='search_project_docs' in used_tools or 'get_task_summary' in used_tools
    checks['task_complete']=result.get('status')=='completed'
    return {'passed':all(checks.values()),'checks':checks,'answer':answer,
            'reason':[k for k,v in checks.items() if not v],
            'scope':'checks the requested fact value, source provenance and necessary reads; free prose quality is reviewed separately'}
