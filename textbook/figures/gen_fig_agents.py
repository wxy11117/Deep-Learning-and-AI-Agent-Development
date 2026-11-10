"""Analytic illustrations plus a plot of actually executed simulated-order data."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'_build_deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont(str(ROOT/'vendor/fonts/NotoSerifSC-Regular.ttf'))
plt.rcParams.update({'font.family':['Noto Serif SC','DejaVu Serif'],'font.size':11,'axes.titlesize':12,'axes.labelsize':10,'axes.unicode_minus':False,
 'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'legend.fontsize':9,'pdf.fonttype':42,'ps.fonttype':42,
 'axes.grid':True,'grid.alpha':.14,'text.color':'#243744','axes.labelcolor':'#243744','savefig.facecolor':'white'})
B,G,O,P='#0072B2','#009E73','#E69F00','#CC79A7'
def save(fig,name):
    for ext in ('png','pdf'):fig.savefig(ROOT/'figures'/f'{name}.{ext}',dpi=300,bbox_inches='tight',pad_inches=.16)
    plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained');n=np.arange(1,11)
for p,c,mark in [(.9,B,'o'),(.97,G,'s')]:axes[0].plot(n,p**n,color=c,marker=mark,label=f'单步成功率 {p:.0%}')
axes[0].set(xlabel='串行关键步骤数',ylabel='全部成功概率',title='假设各步骤独立');axes[0].legend()
for p,c,mark in [(.5,O,'^'),(.7,P,'D')]:axes[1].plot(np.arange(1,6),1-(1-p)**np.arange(1,6),color=c,marker=mark,label=f'单次成功率 {p:.0%}')
axes[1].set(xlabel='尝试次数上限',ylabel='至少成功一次的概率',title='假设尝试独立且可判定成功');axes[1].legend();save(fig,'fig_35_reliability')

fig,ax=plt.subplots(figsize=(9,2.35),layout='constrained');labels=['指令','历史/状态','证据','工具定义','输出预留'];colors=[B,G,P,O,'#7b8794']
values=np.array([[1200,4800,4000,1000,2000],[1200,1800,2500,1000,2000]])
left=np.zeros(2)
for j,label in enumerate(labels):
    bars=ax.barh([1,0],values[:,j],left=left,color=colors[j],label=label,edgecolor='white',hatch=['','//','','..',''][j]);
    for i,v in enumerate(values[:,j]):ax.text(left[i]+v/2,1-i,str(v),ha='center',va='center',fontsize=10,color='white' if j in (0,1,2) else '#253744',bbox=dict(facecolor=colors[j],edgecolor='none',pad=1))
    left+=values[:,j]
ax.set(yticks=[1,0],yticklabels=['直接累计历史','选择状态与证据'],title='同一任务的上下文组织（教学预算 / token）');ax.legend(ncol=5,loc='upper left',bbox_to_anchor=(0,-.21));ax.grid(axis='y',visible=False);save(fig,'fig_36_context_budget')

fig,ax=plt.subplots(figsize=(8,2.65),layout='constrained');z=1.96
for i,n in enumerate([20,100,500]):
    p=.8;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    ax.errorbar(p,i,xerr=[[p-(center-half)],[(center+half)-p]],fmt=['o','s','D'][i],color=[B,G,P][i],capsize=6,markersize=7)
    ax.text(.99,i,f'{center-half:.1%}–{center+half:.1%}',va='center',ha='right',fontsize=10)
ax.set(yticks=[0,1,2],yticklabels=['16 / 20','80 / 100','400 / 500'],xlabel='成功比例与 Wilson 95% 区间',xlim=(.54,1.02),ylim=(-.6,2.6),title='同为 80%，样本量改变抽样不确定性');ax.axvline(.8,color='#777',ls=':',alpha=.5);ax.invert_yaxis();save(fig,'fig_37_eval_uncertainty')

fig,axes=plt.subplots(1,2,figsize=(9,3.4),layout='constrained')
seq=[('模型规划',0,2,B),('查询 A',2,3,G),('查询 B',5,2,P),('汇总',7,1,O)]
par=[('模型规划',0,2,B),('查询 A',2,3,G),('查询 B',2,2,P),('汇总',5,1,O)]
for ax,data,title in zip(axes,[seq,par],['顺序：8 秒','独立查询并行：6 秒']):
    for i,(label,start,width,color) in enumerate(data):ax.barh(3-i,width,left=start,color=color);ax.text(start+width/2,3-i,f'{width}s',ha='center',va='center',color='white' if color!=O else '#283744')
    ax.set(yticks=[3,2,1,0],yticklabels=[d[0] for d in data],xlim=(0,8.7),xlabel='假设时间 / 秒',title=title);ax.grid(axis='y',visible=False)
save(fig,'fig_38_latency_budget')

result=json.loads((ROOT/'agent_projects/results/offline_results.json').read_text(encoding='utf-8'));rows=result['projects']['analysis']['tables']['region']['rows']
fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout='constrained');x=np.arange(3)
axes[0].bar(x-.18,[float(r['revenue']) for r in rows],.34,label='收入',color=B)
bars=axes[0].bar(x+.18,[float(r['profit']) for r in rows],.34,label='利润',color=G,hatch='//');axes[0].bar_label(bars,padding=3,fontsize=9)
axes[0].set(xticks=x,xticklabels=[r['group'] for r in rows],ylabel='教学货币单位',title='绝对金额');axes[0].legend()
bars=axes[1].bar(x,[100*r['margin'] for r in rows],color=[B,G,P]);axes[1].bar_label(bars,fmt='%.2f%%',padding=3)
axes[1].set(xticks=x,xticklabels=[r['group'] for r in rows],ylabel='利润率 / %',ylim=(0,47),title='总利润 / 总收入');save(fig,'fig_39_orders')

fig,ax=plt.subplots(figsize=(8,3.4),layout='constrained');workers=np.arange(1,9);compute=12/workers;overhead=.35*(workers-1)**1.5
ax.plot(workers,compute,label='理想可分计算',color=B,marker='o');ax.plot(workers,overhead,label='假设协调开销',color=O,marker='^',ls='--');ax.plot(workers,compute+overhead,label='合计',color=P,marker='s')
ax.set(xlabel='工作者数量',ylabel='假设时间 / 秒',title='任务可分也不代表工作者越多越快');ax.legend();save(fig,'fig_40_coordination')
print('Generated six Agent figure groups')


