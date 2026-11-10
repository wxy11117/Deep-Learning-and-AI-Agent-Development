"""Audit final textual claims against frozen records and source files, without API requests."""
from pathlib import Path
import json,re,hashlib,collections,ast
ROOT=Path(__file__).resolve().parent;CASE=ROOT/'case_study/lungsight'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
chapters={n:(ROOT/f'新版章节/{n:02}.md').read_text(encoding='utf-8') for n in range(1,45)}
text='\n'.join(chapters.values());checks={}
def check(name,condition):
    checks[name]=bool(condition)
    assert condition,name
manifest=load(CASE/'source_manifest.json')
check('all_source_snapshots_match',all(sha(CASE/p)==h for p,h in manifest['source_files_sha256'].items()))
for key,name in [('documents_sha256','documents.json'),('evaluation_sha256','evaluation_cases.json'),('task_sha256','teaching_tasks.json')]:
    check(name+'_frozen',sha(CASE/name)==manifest[key])
summary=load(CASE/'results/summary.json');records=[]
for phase,stats in summary['groups'].items():
    group=[load(p) for p in sorted((CASE/'results'/phase).glob('*.json'))];records+=group
    check(phase+'_run_count',len(group)==stats['runs'])
    check(phase+'_usage',sum(r['usage']['input_tokens'] for r in group)==stats['input_tokens'] and sum(r['usage']['output_tokens'] for r in group)==stats['output_tokens'])
    check(phase+'_request_count',sum(len(r['requests']) for r in group)==stats['model_requests'])
check('total_run_count',len(records)==32)
totals={k:sum(r['usage'][k] for r in records) for k in ['input_tokens','output_tokens']}
check('book_token_totals',totals=={'input_tokens':120517,'output_tokens':9511})
check('total_model_calls',sum(len(r['requests']) for r in records)==89)
check('total_tool_calls',sum(r['result']['calls'] for r in records)==79)
check('real_responses_saved',all(r['real_model_executed'] and r['returned_models']==['deepseek-flash'] for r in records))
check('preserved_wrapper_snapshots',all((CASE/'execution_sources'/(r['implementation_sha256']['run_experiment.py']+'.py')).is_file() for r in records))
for name,path in [('case_tools.py',CASE/'case_tools.py'),('core.py',ROOT/'agent_projects/core.py'),('deepseek_provider.py',ROOT/'agent_projects/deepseek_provider.py')]:
    check(name+'_matches_executions',all(r['implementation_sha256'][name]==sha(path) for r in records))
review=load(CASE/'results/semantic_review.json')
check('editorial_review_evidence',all(sha(CASE/x['run'])==x['sha256'] for x in review['reviewed_evaluation_answers']+[review['finding'],review['revision']]))
check('review_covers_20',len(review['reviewed_evaluation_answers'])==20)
cases=load(CASE/'evaluation_cases.json')['cases']
check('question_categories',collections.Counter(c['category'] for c in cases)=={'source':12,'task':5,'missing':2,'version':1})
check('programming_intro_remains_21','21.1' in chapters[21] and 'print' in chapters[21])
check('advanced_reading_cues',all('进阶选读' in chapters[n] or '推导选读' in chapters[n] for n in [3,4,7]))
check('project_launch_paths',all('--project '+choice in chapters[n] for n,choice in [(22,'bike'),(23,'digits'),(24,'sensor'),(25,'segmentation'),(31,'retrieval'),(40,'knowledge'),(41,'analysis'),(42,'workflow')]))
check('new_case_sections',all('### '+s+' ' in text for s in ['38.10','38.11','40.10','40.11','40.12','40.13','40.14','42.9']))
check('corrected_crossreference','下一章之后的高效训练部分' not in chapters[30])
check('typo_fixed','尽可能可能' not in text)
check('exercise_numbers_separate','**项目一：' not in chapters[28] and '**拓展练习 A：' in chapters[28])
check('regularizer_symbol',r'+\lambda\Omega(\theta)' in chapters[1])
check('obsolete_live_status_removed','未执行付费评测' not in text and '本版没有执行真实模型调用' not in text)
check('author_page_config_preserved',sha(ROOT/'author_page.json')==load(ROOT/'final_revision_log.json')['author_config_sha256'])
check('three_authors_and_size',load(ROOT/'author_page.json')['authors']==['Violet','Star','Sapphire'] and load(ROOT/'author_page.json')['signature_size_pt']==28)
check('forty_four_chapters',len(re.findall(r'^## 第\s*\d+\s*章',text,re.M))==44)
check('new_figures_exist',all((ROOT/'figures'/f'{n}.{ext}').is_file() for n in ['fig_41_lungsight_runs','diagram_sensor_bridge','diagram_lungsight_trace'] for ext in ['svg','pdf','png']))
for folder in ['agent_projects','case_study/lungsight']:
    for p in (ROOT/folder).glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
check('python_syntax',True)
result={'passed':all(checks.values()),'checks':checks,'total_checks':len(checks),'real_model_totals':totals,
        'estimated_usd_peak_cache_miss':(totals['input_tokens']*.3+totals['output_tokens']*1.2)/1e6}
(ROOT/'final_content_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'real_model_totals':totals}))
