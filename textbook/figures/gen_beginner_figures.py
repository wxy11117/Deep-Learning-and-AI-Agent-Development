"""Original, reproducible beginner illustrations; numerical examples are illustrative."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'_build_deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT=ROOT/'figures'
fm.fontManager.addfont('C:/Windows/Fonts/simsun.ttc')
plt.rcParams.update({'font.family':'SimSun','font.size':13,'axes.unicode_minus':False,
                     'svg.fonttype':'path','pdf.fonttype':42,'savefig.facecolor':'white'})
NAVY='#315e7a'; TEAL='#3a756c'; PURPLE='#70618a'; OCHRE='#9a6b3f'
INK='#263b47'; MUTED='#61747c'; LIGHT='#d3dde0'
BLUE='#edf3f7'; GREEN='#edf5f0'; LILAC='#f4eff7'; SAND='#faf3e8'

def canvas(h=3.4):
    fig,ax=plt.subplots(figsize=(8.6,h))
    fig.subplots_adjust(left=.015,right=.985,top=.97,bottom=.035)
    ax.set_xlim(0,10);ax.set_ylim(0,4);ax.axis('off')
    return fig,ax

def text(ax,x,y,s,sz=13,color=INK,ha='center',weight='normal',va='center'):
    return ax.text(x,y,s,ha=ha,va=va,fontsize=sz,color=color,fontweight=weight,linespacing=1.45)

def box(ax,x,y,w,h,title,detail='',color=NAVY,fill=BLUE):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.025,rounding_size=0.08',
                              fc=fill,ec=color,lw=1))
    text(ax,x+w/2,y+h*.66 if detail else y+h/2,title,14,color)
    if detail:text(ax,x+w/2,y+h*.27,detail,11.8)

def arrow(ax,a,b,color=MUTED,rad=0,style='-|>',lw=1.2):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=12,
                               lw=lw,color=color,connectionstyle=f'arc3,rad={rad}'))

def save(fig,name):
    for ext in ['svg','pdf','png']:
        fig.savefig(OUT/f'{name}.{ext}',dpi=300)
    plt.close(fig)

# 1. Same input, adjusted parameter, and smaller observed error.
fig,ax=canvas(3.1)
text(ax,.12,3.7,'同一条购买记录：重量 2 千克，实际总价 8 元',15,ha='left')
box(ax,.15,1.7,2.1,1.3,'输入','重量 2 千克')
box(ax,3,1.7,2.5,1.3,'单价参数','3 元／千克',TEAL,GREEN)
box(ax,6.25,1.7,3.25,1.3,'预测 6 元','与实际总价相差 2 元',PURPLE,LILAC)
arrow(ax,(2.3,2.35),(2.92,2.35));arrow(ax,(5.55,2.35),(6.17,2.35))
text(ax,3.35,1.15,'更新参数',12,TEAL);arrow(ax,(4.25,1.6),(4.25,.75),TEAL)
text(ax,4.25,.42,'3.4 元／千克',14,TEAL)
arrow(ax,(5.5,.42),(6.18,.42))
text(ax,7.85,.42,'预测 6.8 元；差距 1.2 元',14,PURPLE)
save(fig,'beginner_01_learning')

# 2. Values -> vector -> matrix -> stack, with explicit semantic axes.
fig,ax=canvas(3.2)
text(ax,1.2,3.65,'一个成绩',14,NAVY)
box(ax,.65,2.65,1.1,.65,'85',color=NAVY)
text(ax,1.2,2.25,'标量',12)
text(ax,4.35,3.65,'一个学生的成绩',14,TEAL)
for j,v in enumerate([85,78,92,88]):
    ax.add_patch(Rectangle((2.85+j*.76,2.65),.76,.65,fc=GREEN,ec=TEAL,lw=.7))
    text(ax,3.23+j*.76,2.98,str(v),12)
text(ax,4.35,2.25,'向量：4 门课',12)
text(ax,8.1,3.65,'5 个班的成绩表',14,PURPLE)
for k in [4,3,2,1,0]:
    ax.add_patch(Rectangle((7.05+k*.09,2.2+k*.1),2.05,.9,fc=LILAC,ec=PURPLE,lw=.8))
text(ax,8.08,2.67,'5 × 3 × 4',14,PURPLE)
text(ax,8.15,1.8,'班级 × 学生 × 课程',11.5)
text(ax,1.2,1.45,'一张成绩表',14,NAVY)
values=[[85,78,92,88],[76,90,81,84],[93,86,89,91]]
for i,row in enumerate(values):
    for j,v in enumerate(row):
        x=2.85+j*.76;y=1.33-i*.46
        ax.add_patch(Rectangle((x,y-.23),.76,.46,fc=BLUE,ec=LIGHT,lw=.6))
        text(ax,x+.38,y,str(v),11.5)
    text(ax,2.65,1.33-i*.46,f'学生 {i+1}',10.5,ha='right')
text(ax,4.35,.03,'矩阵：3 名学生 × 4 门课',11.5)
arrow(ax,(5.95,1.05),(7.02,2.05),PURPLE,rad=.1)
save(fig,'beginner_02_tensor')

# 3. Exact valid cross-correlation as used by most CNN implementations.
fig,ax=canvas(3.25)
X=np.tile([0,0,0,1,1],(4,1));K=np.tile([-1,0,1],(3,1))
Y=np.array([[np.sum(X[r:r+3,c:c+3]*K) for c in range(3)] for r in range(2)])
assert np.array_equal(Y,[[0,3,3],[0,3,3]])
def grid(ax,A,x,y,cell,color,fill):
    for i,row in enumerate(A):
        for j,v in enumerate(row):
            ax.add_patch(Rectangle((x+j*cell,y-i*cell),cell,cell,fc=fill,ec=LIGHT,lw=.7))
            text(ax,x+(j+.5)*cell,y+(.5-i)*cell,str(v),12,color)
text(ax,1.7,3.65,'输入 4 × 5',14,NAVY)
grid(ax,X,.35,2.75,.54,NAVY,BLUE)
ax.add_patch(Rectangle((.35,1.67),1.62,1.62,fc='none',ec=OCHRE,lw=2))
text(ax,1.7,.63,'首个窗口：全为 0',12,OCHRE)
text(ax,5,3.65,'共享模板 3 × 3',14,TEAL)
grid(ax,K,4.2,2.75,.54,TEAL,GREEN)
text(ax,5,.63,'各位置使用同一组数',12,TEAL)
text(ax,8.35,3.65,'输出 2 × 3',14,PURPLE)
grid(ax,Y,7.55,2.48,.54,PURPLE,LILAC)
text(ax,8.35,1.25,'首行：0、3、3',12,PURPLE)
arrow(ax,(3.2,2.2),(3.88,2.2));arrow(ax,(6.05,2.2),(7.2,2.2))
text(ax,5,.13,'步长 1，无补零；逐格相乘，再把窗口内结果相加',12,MUTED)
save(fig,'beginner_03_convolution')

# 4. Explicit sum and contributions; no claimed learned weights.
fig,ax=canvas(2.95)
xs=[.4,3.7,7];cols=[NAVY,TEAL,PURPLE];fills=[BLUE,GREEN,LILAC]
for x,v,w,c,f in zip(xs,[2,4,10],[.2,.3,.5],cols,fills):
    box(ax,x,2.1,2.5,1.1,f'信息值 {v}',f'示范权重 {w:.1f}',c,f)
    arrow(ax,(x+1.25,2.03),(x+1.25,1.47),c)
    text(ax,x+1.25,1.15,f'贡献 {v*w:.1f}',15,c)
text(ax,3.3,1.15,'＋',17);text(ax,6.6,1.15,'＋',17)
text(ax,5,.4,'加权汇总：0.4 + 1.2 + 5.0 = 6.6',16)
text(ax,5,3.72,'先看汇总怎样计算，再学习权重怎样产生',14,MUTED)
save(fig,'beginner_04_attention')

# 5. Retrieval with version and provenance kept visible.
fig,ax=canvas(2.95)
nodes=[(.15,NAVY,BLUE,'问题','R2 2.0 的日志\n保存多久？'),
       (2.68,TEAL,GREEN,'检索','先按型号与版本\n筛选候选资料'),
       (5.21,PURPLE,LILAC,'读原文','K01：本机日志\n保存 30 天'),
       (7.74,OCHRE,SAND,'组织回答','30 天\n注明来源 K01')]
for x,c,f,t,d in nodes:box(ax,x,1.65,2.1,1.6,t,d,c,f)
for a,b in [(2.29,2.62),(4.82,5.15),(7.35,7.68)]:arrow(ax,(a,2.45),(b,2.45))
text(ax,5,.93,'版本条件跟随资料，引用跟随结论',14,MUTED)
text(ax,5,.35,'教学虚构手册；完整工具与引用检查见第 40 章',11.5,MUTED)
save(fig,'beginner_05_rag')

# 6. Request, execution, observation and next selection are separate nodes.
fig,ax=canvas(3.5)
box(ax,.15,2.35,2.8,1.15,'提出调用','模型：读取设备状态',NAVY,BLUE)
box(ax,3.6,2.35,2.8,1.15,'执行工具','程序：查询状态接口',TEAL,GREEN)
box(ax,7.05,2.35,2.8,1.15,'得到观察','返回：连接中断',PURPLE,LILAC)
arrow(ax,(3,2.93),(3.54,2.93));arrow(ax,(6.45,2.93),(6.99,2.93))
box(ax,3.6,.35,2.8,1.15,'选择下一步','查询日志或完成任务',OCHRE,SAND)
arrow(ax,(8.45,2.3),(6.45,.95),PURPLE,rad=-.12)
arrow(ax,(3.55,.95),(1.55,2.3),OCHRE,rad=-.15)
text(ax,1.45,.8,'继续获取信息',11.5,OCHRE)
arrow(ax,(6.45,.6),(7.15,.6),TEAL)
text(ax,8.55,.6,'输出有依据的建议',12,TEAL)
text(ax,5,3.85,'后续动作取决于实际返回的结果',14,MUTED)
save(fig,'beginner_06_agent')
print('Created 6 original illustrations, each in SVG, PDF and 300 DPI PNG.')
