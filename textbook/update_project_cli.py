"""One-time mechanical refactor: select a project without changing its computation."""
from pathlib import Path
p=Path(__file__).parent/'agent_projects/run_projects.py'
s=p.read_text(encoding='utf-8')
assert 'def main(live=False):' in s
s=s.replace('def main(live=False):','def main(live=False,project="all"):')
old="    out=ROOT/'results';out.mkdir(exist_ok=True);prepare();summary={'mode':'live_api' if live else 'offline_replay','python':platform.python_version(),'projects':{}}"
new="""    out=ROOT/'results';out.mkdir(exist_ok=True)
    name='live_results.json' if live else 'offline_results.json'
    saved=out/name
    summary=json.loads(saved.read_text(encoding='utf-8')) if project!='all' and saved.exists() else {'projects':{}}
    summary.update({'mode':'live_api' if live else 'offline_replay','python':platform.python_version()})"""
assert old in s;s=s.replace(old,new)
start=s.index('    kb=KnowledgeBase()');analysis=s.index('    store=AnalysisStore()',start)
workflow=s.index('    with tempfile.TemporaryDirectory() as tmp:',analysis)
ending=s.index("    name='live_results.json' if live else 'offline_results.json'",workflow)
blocks=[s[start:analysis],s[analysis:workflow],s[workflow:ending]]
wrapped=''
for key,block in zip(['knowledge','analysis','workflow'],blocks):
    wrapped+=f"    if project in ('all','{key}'):\n"
    if key=='analysis':wrapped+='        prepare()\n'
    wrapped+=''.join('    '+line if line.strip() else line for line in block.splitlines(keepends=True))
s=s[:start]+wrapped+s[ending:]
s=s.replace("    main(parser.parse_args().live)","    parser.add_argument('--project',choices=['all','knowledge','analysis','workflow'],default='all',help='Run one project and retain other result entries.')\n    args=parser.parse_args()\n    main(args.live,args.project)")
p.write_text(s,encoding='utf-8')
print('Added independent Agent project selection.')
