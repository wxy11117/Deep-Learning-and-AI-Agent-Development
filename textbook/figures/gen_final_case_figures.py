"""Draw original vector case diagrams and the observed repeated-run timing plot."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_build_deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib import font_manager as fm
fm.fontManager.addfont('C:/Windows/Fonts/simsun.ttc')
plt.rcParams.update({'font.family':'SimSun','font.size':14,'axes.unicode_minus':False,
                     'svg.fonttype':'path','pdf.fonttype':42,'savefig.facecolor':'white'})
BLUE='#315e7a';TEAL='#397b73';VIOLET='#73618c';OCHRE='#a26b3e';INK='#263b47';MUTED='#62767e'
def canvas(h):
    f,a=plt.subplots(figsize=(8.6,h));f.subplots_adjust(left=.02,right=.98,bottom=.03,top=.97)
    a.set(xlim=(0,10),ylim=(0,6));a.axis('off');return f,a
def label(a,x,y,t,size=14,color=INK):
    a.text(x,y,t,ha='center',va='center',fontsize=size,color=color,linespacing=1.55)
def box(a,x,y,w,h,title,detail,color,fill):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.03,rounding_size=.10',fc=fill,ec=color,lw=1.1))
    label(a,x+w/2,y+h*.72,title,15,color);label(a,x+w/2,y+h*.31,detail,12)
def arrow(a,p,q,color=MUTED):
    a.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=13,lw=1.3,color=color))
def save(f,name):
    for ext in ['svg','pdf','png']:f.savefig(ROOT/'figures'/f'{name}.{ext}',dpi=300)
    plt.close(f)

f,a=canvas(3.7)
box(a,.15,3.5,3,1.55,'数值模型','模拟轨迹 → CNN 估计\n测量 51.947；估计 81.417 cm',BLUE,'#edf3f7')
box(a,3.65,3.5,2.7,1.55,'复核规则','差异 29.470 cm\n教学阈值 10 cm',OCHRE,'#faf2e8')
box(a,6.85,3.5,2.95,1.55,'资料工具','搜索并读取 S01／2.0\n取得检查步骤和出处',TEAL,'#edf6f2')
arrow(a,(3.2,4.27),(3.6,4.27));arrow(a,(6.4,4.27),(6.8,4.27))
box(a,3.65,.65,6.15,1.55,'保存待审阅提案','关闭连接 → 重新打开 → 恢复 awaiting_approval',VIOLET,'#f3eff7')
arrow(a,(8.32,3.4),(8.32,2.3),TEAL)
label(a,1.7,1.47,'模型回答“估计多少”\n规则回答“是否入队”\n工具回答“依据什么”',12.5)
label(a,6.73,.15,'工单仍为 open；业务变更事件为 0',12,MUTED)
label(a,5,5.63,'从预测数值到可恢复的任务状态',17,BLUE)
save(f,'diagram_sensor_bridge')

f,a=canvas(4.3)
box(a,.25,4.45,4.15,1.15,'公开资料快照','Git 提交固定 · 架构／权重标识／项目定位',BLUE,'#edf3f7')
box(a,5.6,4.45,4.15,1.15,'人工构造教学任务','DEMO-001 · 五折概率／模拟复核状态',OCHRE,'#faf2e8')
box(a,.45,2.2,3.7,1.35,'搜索 → 读取','search_project_docs\nread_source',TEAL,'#edf6f2')
box(a,5.85,2.2,3.7,1.35,'确定性数值工具','get_task_summary\n均值、分歧与版本字段',TEAL,'#edf6f2')
arrow(a,(2.3,4.36),(2.3,3.65));arrow(a,(7.7,4.36),(7.7,3.65))
box(a,2.9,.15,4.2,1.25,'DeepSeek 工具循环','按需要请求工具 → 接收结果 → 生成草稿',VIOLET,'#f3eff7')
arrow(a,(4.12,2.21),(4.12,1.51),BLUE);arrow(a,(5.88,2.21),(5.88,1.51),OCHRE)
arrow(a,(2.82,.8),(1.1,.8),VIOLET);arrow(a,(1.1,.8),(1.1,2.1),VIOLET)
label(a,1.12,.22,'下一步请求',11,VIOLET)
label(a,8.55,.78,'分别注明\n原文事实与构造数值',12)
save(f,'diagram_lungsight_trace')

case=ROOT/'case_study/lungsight/results'
rows=[]
for id in ['L06','L14','L19']:
    rows.append([json.loads((case/phase/f'{id}_r{rep}.json').read_text(encoding='utf-8'))['elapsed_seconds']
                 for phase,rep in [('evaluation',1),('repeat',2),('repeat',3)]])
f,a=plt.subplots(figsize=(8.6,3.75));f.subplots_adjust(left=.23,right=.96,bottom=.23,top=.85)
colors=[BLUE,TEAL,VIOLET];offsets=[-.20,0,.20]
for i,(color,off) in enumerate(zip(colors,offsets)):
    a.scatter([r[i] for r in rows],[j+off for j in range(3)],s=65,c=color,label=['原始运行','重复 1','重复 2'][i],zorder=3)
    for j,row in enumerate(rows):a.annotate(f'{row[i]:.3f}',(row[i],j+off),xytext=(5,0),textcoords='offset points',fontsize=11,color=color,va='center')
a.set_yticks([0,1,2],['L06 · 模式字段','L14 · B 类均值','L19 · 信息缺失'])
a.set_xlim(0,15);a.set_ylim(-.5,2.5);a.set_xlabel('端到端耗时／秒',fontsize=13)
a.grid(axis='x',color='#dce4e7',linewidth=.7);a.set_axisbelow(True)
a.spines[['top','right','left']].set_visible(False);a.spines['bottom'].set_color('#b7c5ca');a.tick_params(axis='y',length=0)
a.legend(loc='upper center',bbox_to_anchor=(.5,1.28),ncol=3,frameon=False,fontsize=12)
save(f,'fig_41_lungsight_runs')
print('Generated 3 final-case figures in SVG, PDF and 300 DPI PNG.')
