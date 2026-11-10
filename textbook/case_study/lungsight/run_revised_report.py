"""Repair a provenance wording issue discovered in the integrated draft, preserving both runs."""
from pathlib import Path
import argparse,json
import run_experiment as experiment
from run_experiment import ROOT,run_case,summarize
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results');args=parser.parse_args()
    if not args.live:parser.error('--live is required')
    experiment.RESULTS=args.output_dir.resolve()
    case=json.loads((ROOT/'integrated_case.json').read_text(encoding='utf-8'))
    case={**case,'id':'REPORT02','question':case['question']+' 来源表达要求：正文开头明确本例概率由作者人工构造、按 LungSight 接口组织；公开仓库的 ResNet18 架构与权重版本作为参照信息单独说明。区分项目真实属性、本例构造数据和模拟待复核状态。'}
    record=run_case(case,'integrated_revised')
    if record['score']['passed']:
        a=record['score']['answer'];docs={d['id']:d for d in json.loads((ROOT/'documents.json').read_text(encoding='utf-8'))}
        lines=['# LungSight 综合教学报告：修订后的来源表达','',a['answer'],'','## 结构化结果','','```json',json.dumps(a['value'],ensure_ascii=False,indent=2),'```','','## 资料出处','']
        for c in a['citations']:
            d=docs[c['id']];lines.append(f"- [{c['id']} · {d['title']}]({d['url']})：{c['quote']}")
        (experiment.RESULTS/'integrated_report_revised.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    summarize()
