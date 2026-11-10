"""Verify new CLI behavior, evidence checks, numeric exercises and saved real-model records."""
from pathlib import Path
import sys,json,subprocess,copy,hashlib,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'agent_projects'))
sys.path.insert(0,str(ROOT/'case_study/lungsight'))
from case_tools import CaseStore,score
from deepseek_provider import DeepSeekModel
from core import ContractError

checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def command(*args):
    p=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)

before=read('projects/results/metrics.json')
command('projects/run_projects.py','--project','retrieval')
after=read('projects/results/metrics.json')
check('single ML project preserves other project metrics',all(after[k]==before[k] for k in before if k!='retrieval'))
check('retrieval recomputation preserves Recall and MRR',all(after['retrieval'][k]==before['retrieval'][k] for k in ['recall_at_k','mrr']))
for project in ['knowledge','analysis','workflow']:
    before=read('agent_projects/results/offline_results.json')
    command('agent_projects/run_projects.py','--project',project)
    after=read('agent_projects/results/offline_results.json')
    check(project+' CLI preserves unselected results',all(after['projects'][k]==before['projects'][k] for k in before['projects'] if k!=project))
check('all Agent result entries retained',set(after['projects'])=={'knowledge','analysis','workflow'})

store=CaseStore();task=store.task('DEMO-001')
check('five-fold probabilities each sum to one',all(math.isclose(sum(row),1) for row in task['fold_probabilities']))
check('aggregate probabilities sum to one',math.isclose(sum(task['mean_probabilities'].values()),1))
check('B mean, agreement, spread and margin',task['mean_probabilities']['B']==.51 and task['fold_agreement']==.8 and task['class_spreads']['B']==.35 and task['top_two_margin']==.23)
try:store.task('DEMO-999');bad=False
except ContractError:bad=True
check('unknown task is an explicit tool error',bad)
try:store.read('LS01','wrong-version');bad=False
except ContractError:bad=True
check('wrong document version rejected',bad)
fault=CaseStore(inject_timeout=True,recover_timeout=True)
try:fault.search('ResNet18',3);bad=False
except ContractError as e:bad='TEMPORARY_TIMEOUT' in str(e)
check('temporary read fault becomes a structured error',bad)
check('same read succeeds after one injected fault',bool(fault.search('ResNet18',3)['matches']))
data=read('case_study/lungsight/evaluation_cases.json')
record=read('case_study/lungsight/results/evaluation/L01_r1.json')
for field,value in [('value','WrongNet'),('citations',[{'id':'LS99','version':'bad','quote':'fabricated'}])]:
    result=copy.deepcopy(record['result']);answer=json.loads(result['text']);answer[field]=value;result['text']=json.dumps(answer)
    check('grader rejects incorrect '+field,not score(data['cases'][0],result)['passed'])
bad=copy.deepcopy(record['result']);bad['history']=[]
check('grader rejects citations without actual reads',not score(data['cases'][0],bad)['passed'])
fixture={'choices':[{'finish_reason':'tool_calls','message':{'content':None,'tool_calls':[{'id':'x','function':{'name':'read_source','arguments':'{"doc_id":"LS01","version":"v"}'}}]}}],'usage':{'prompt_tokens':10,'completion_tokens':4}}
reply=DeepSeekModel.decode(fixture)
check('DeepSeek adapter retains call id and usage',reply.calls[0]['id']=='x' and reply.usage['prompt_tokens']==10)
fixture['choices'][0]['finish_reason']='length'
try:DeepSeekModel.decode(fixture);bad=False
except ContractError:bad=True
check('truncated provider result is a visible failure',bad)

for case in data['cases']:
    r=read(f"case_study/lungsight/results/evaluation/{case['id']}_r1.json")
    check('real record and recomputed grading '+case['id'],r['real_model_executed'] and score(case,r['result'])==r['score'])
manifest=read('case_study/lungsight/source_manifest.json')
for relative,digest in manifest['source_files_sha256'].items():
    check('frozen public source '+relative,hashlib.sha256((ROOT/'case_study/lungsight'/relative).read_bytes()).hexdigest()==digest)
check('frozen evaluation set unchanged',hashlib.sha256((ROOT/'case_study/lungsight/evaluation_cases.json').read_bytes()).hexdigest()==manifest['evaluation_sha256'])
check('gradient update numeric exercise',math.isclose((3-.1*6)**2,5.76))
check('attention transfer exercise',math.isclose(.3*2+.3*4+.4*10,5.8))
check('rank exercise',math.isclose((1+.5+.25)/3,7/12))
check('weather event comparison',sum(t>31 for t in [29,31,33,30,32])==2 and sum(t>=31 for t in [29,31,33,30,32])==3)
check('mask IoU and Dice exercise',math.isclose(4/(6+6-4),.5) and math.isclose(2*4/(6+6),2/3))
bridge=read('agent_projects/results/sensor_bridge.json')
check('sensor bridge waits with no business write',bridge['checkpoint_restored'] and bridge['ticket_still_open'] and bridge['business_write_events']==0)
report={'passed':len(checks),'failed':0,'checks':checks,'live_api_calls_in_this_check':0}
(ROOT/'final_project_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'failed':0}))
