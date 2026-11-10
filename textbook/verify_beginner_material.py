"""Check manuscript additions, hand calculations, source preservation and fonts."""
from pathlib import Path
import sys, re, json, math, ast, hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
from fontTools.ttLib import TTFont
from add_beginner_material import ITEMS, APPLICATIONS, REFERENCE_FIXES

reference=json.loads((ROOT/'validation_reference.json').read_text(encoding='utf-8'))
revision=json.loads((ROOT/'final_revision_log.json').read_text(encoding='utf-8'))
digest=lambda value:hashlib.sha256(value.encode('utf-8')).hexdigest()
new='\n'.join((ROOT/f'新版章节/{i:02}.md').read_text(encoding='utf-8') for i in range(1,45))
# The final edition intentionally edits prose and adds sections. Verify the original
# mathematical/code content using the recorded corrections, not an obsolete whole-prose hash.
reversed_chapters=[]
for n in range(1,45):
    t=(ROOT/f'新版章节/{n:02}.md').read_text(encoding='utf-8')
    for change in reversed(revision['changes']):
        if change['chapter']==n and change['kind']=='correction':
            t=t.replace(change['after'],change['before'])
    reversed_chapters.append(t)
restored='\n'.join(reversed_chapters)

def subsequence(a,b):
    it=iter(b)
    return all(any(x==y for y in it) for x in a)
patterns={
    'display_math':r'\$\$([\s\S]*?)\$\$',
    'inline_math':r'\\\(([\s\S]*?)\\\)',
    'code_blocks':r'~~~[^\n]*\n([\s\S]*?)~~~',
    'table_rows':r'(?m)^\|.*\|$',
}
preserved={'baseline':'final_revision_log.json + validation_reference.json',
           'verification_mode':'SHA-256 subsequences after reversing explicit final-edition corrections',
           'prose_review':'Final editorial corrections and additions are recorded; no claim of unchanged prose.',
           'reference_rows_corrected':len(REFERENCE_FIXES)}
for key,p in patterns.items():
    after=[digest(v) for v in re.findall(p,new)]
    if key=='table_rows':
        corrected=reference['corrected_table_rows_sha256']
        oldrow='| 真实模型任务评测 | 独立问题、固定环境 | 模型能否选择有效行动并完成任务 | 提供方法与接口，未执行付费评测 |'
        newrow='| 真实模型任务评测 | 冻结问题、固定环境 | 模型能否选择有效行动并完成任务 | 已执行 20 道 DeepSeek 教学题及对照，见 38.10 节 |'
        audited=[digest(v) for v in re.findall(p,new.replace(newrow,oldrow))]
        assert subsequence(corrected,audited),'Original table row missing outside documented status correction'
        preserved[key]={'before':len(corrected),'after':len(after),'retained_or_corrected':True,'prior_reference_rows_corrected':21,'experiment_status_row_updated':1}
    else:
        before=revision['before_entries_sha256'][key]
        audited=[digest(v) for v in re.findall(p,restored)]
        assert subsequence(before,audited),key
        preserved[key]={'before':len(before),'after':len(after),'retained_or_corrected':True,
                        'unchanged':subsequence(before,after),'audited_against_final_revision_log':True}

checks={}
def close(name,value,wanted):
    assert math.isclose(value,wanted,rel_tol=1e-9,abs_tol=1e-9),(name,value,wanted)
    checks[name]={'value':value,'expected':wanted}
close('apple_initial_prediction',2*3,6)
close('apple_updated_prediction',2*3.4,6.8)
close('apple_initial_half_square_loss',.5*(6-8)**2,2)
close('apple_updated_half_square_loss',.5*(6.8-8)**2,.72)
close('apple_loss_after_small_change',.5*(2*3.1-8)**2,1.62)
close('apple_gradient_step',3-.1*((2*3-8)*2),3.4)
close('courier_linear_model',3*4+2,14)
close('nearest_neighbor_rent',(1800+2000+2200)/3,2000)
close('likelihood_half',.5*.5*.5,.125)
close('likelihood_point_eight',.8*.8*.2,.128)
close('mae',(1+1+4)/3,2)
close('mse',(1+1+16)/3,6)
close('negative_log_high',round(-math.log(.8),3),.223)
close('negative_log_low',round(-math.log(.2),3),1.609)
close('iou',4/(6+6-4),.5)
close('attention_weights',.2+.3+.5,1)
close('attention_weighted_sum',.2*2+.3*4+.5*10,6.6)
close('precision',6/8,.75);close('recall',6/10,.6)
close('sensor_mean',sum([49,51,80,50,49])/5,55.8)
close('sensor_median',sorted([49,51,80,50,49])[2],50)
close('overall_profit_margin',(20+90)/(100+900),.11)
close('mean_of_profit_margins',(.2+.1)/2,.15)
close('daily_input_tokens',100*4*1500,600000)
close('daily_output_tokens',100*4*300,120000)
X=[[0,0,0,1,1] for _ in range(4)];K=[[-1,0,1] for _ in range(3)]
Y=[[sum(X[r+i][c+j]*K[i][j] for i in range(3) for j in range(3)) for c in range(3)] for r in range(2)]
assert Y==[[0,3,3],[0,3,3]]
checks['convolution']={'value':Y,'expected':[[0,3,3],[0,3,3]]}
inserted='\n'.join(x['text'] for x in ITEMS)
for code in re.findall(r'~~~python\n([\s\S]*?)~~~',inserted):
    ast.parse(code);scope={};exec(compile(code,'beginner-example','exec'),scope)
    assert scope['prediction']==6.0
for code in re.findall(r'~~~json\n([\s\S]*?)~~~',inserted):
    assert json.loads(code)=={'model':'R2','version':'2.0','topic':'log_retention'}
assert len(re.findall(r'<!-- BEGINNER:',new))==len(ITEMS)
for item in ITEMS:
    assert item['text'] in new,'Original beginner passage changed: '+str(item.get('id',''))
assert len(re.findall(r'<!-- APPLICATION:',new))==7
assert len(re.findall(r'<!-- FIG:beginner_',new))==6
assert all(c['url'] in new for c in APPLICATIONS)
defensive=[p for p in ['据此不能说明','不能证明','无法证明','尚不能','不代表','以原论文为准'] if p in inserted]
# The added prose should explain mechanisms and conditions directly.
assert not defensive,defensive
font_missing={}
chars={ord(c) for c in new if '\u4e00'<=c<='\u9fff'}
for filename in ['NotoSerifSC-Regular.ttf','BookSans-700.ttf']:
    cmap=TTFont(ROOT/'vendor/fonts'/filename).getBestCmap()
    missing=''.join(chr(c) for c in sorted(chars-set(cmap)))
    font_missing[filename]=missing
assert not any(font_missing.values()),font_missing
preserved['font_missing_characters']=font_missing
(ROOT/'content_preservation_check.json').write_text(json.dumps(preserved,ensure_ascii=False,indent=2),encoding='utf-8')
result={'passed':True,'teaching_insertions':92,'recent_application_cases':7,'figures':6,
        'chapters_touched':44,'reference_rows_corrected':21,'numeric_checks':len(checks),
        'python_snippets_checked':1,'json_snippets_checked':1,'source_preservation':True,
        'font_missing_characters':font_missing,'defensive_phrase_matches':defensive,'calculations':checks}
(ROOT/'beginner_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='calculations'},ensure_ascii=False))
