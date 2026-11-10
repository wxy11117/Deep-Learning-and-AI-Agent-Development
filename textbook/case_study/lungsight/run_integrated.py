"""Generate one real-model, source-linked research explanation draft."""
import argparse,json
from pathlib import Path
import run_experiment as experiment
from run_experiment import ROOT,run_case,summarize
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=parser.parse_args();experiment.RESULTS=args.output_dir.resolve()
    if not args.live:parser.error('--live is required')
    case=json.loads((ROOT/'integrated_case.json').read_text(encoding='utf-8'))
    record=run_case(case,'integrated')
    if record['score']['passed']:
        answer=record['score']['answer']
        docs={d['id']:d for d in json.loads((ROOT/'documents.json').read_text(encoding='utf-8'))}
        lines=['# LungSight 教学任务科研结果说明草稿','',
               '数据：人工构造的 A/B/C/D 五折概率；公开仓库资料按固定提交保存。',
               '生成方式：DeepSeek 实际选择并调用教材只读工具。','',answer['answer'],'',
               '## 结构化结果','', '```json',json.dumps(answer['value'],ensure_ascii=False,indent=2),'```','', '## 引用','']
        for c in answer['citations']:
            d=docs[c['id']];lines.extend([f"- [{c['id']} · {d['title']}]({d['url']})：{c['quote']}"])
        (experiment.RESULTS/'integrated_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    summarize()
