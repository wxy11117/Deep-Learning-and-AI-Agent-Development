"""Draw the original, editable vector illustration for Violet's author page."""
from pathlib import Path
import sys, math
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '_build_deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Polygon, Ellipse
from matplotlib.font_manager import FontProperties

plt.rcParams.update({'svg.fonttype': 'path', 'pdf.fonttype': 42, 'mathtext.fontset': 'stix'})
song = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')
kai = FontProperties(fname=r'C:\Windows\Fonts\simkai.ttf')
navy, teal, violet, copper = '#315e7a', '#4c827b', '#857099', '#ad8253'
fig, ax = plt.subplots(figsize=(10, 5.7))
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax.set(xlim=(0, 1000), ylim=(570, 0)); ax.axis('off')

def text(x, y, value, size=15, color=navy, align='center', italic=False):
    return ax.text(x, y, value, fontsize=size, color=color, ha=align, va='center',
                   fontproperties=kai if italic else song, zorder=8)

def arrow(a, b, color=navy, rad=0, style='-|>', lw=1.15, alpha=1, zorder=4):
    patch = FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=12, linewidth=lw,
                            connectionstyle=f'arc3,rad={rad}', color=color, alpha=alpha, zorder=zorder)
    ax.add_patch(patch)

def node(x, y, r=7, color=navy, fill='white'):
    ax.add_patch(Circle((x,y), r, fc=fill, ec=color, lw=1.1, zorder=6))

# Three linked regions share a calm, faintly gridded field.
ax.add_patch(Ellipse((485, 325), 930, 310, facecolor='#f6f8f8', edgecolor='none', zorder=0))
for x in range(80, 970, 55):
    ax.plot([x, x-55], [440, 180], color='#d7e0e0', lw=.4, alpha=.32, zorder=0)
for y in range(210, 450, 45):
    ax.plot([60, 960], [y, y-12], color='#d7e0e0', lw=.4, alpha=.32, zorder=0)

text(210, 77, '学习表示', 18, navy)
text(492, 77, '建立关联', 18, violet)
text(804, 77, '组织行动', 18, teal)
for x, color in [(210,navy),(492,violet),(804,teal)]:
    ax.plot([x-27,x+27],[102,102],color=color,lw=1.25,alpha=.65)

# An input patch and a shared-weight feedforward network.
for layer in range(3):
    ox, oy = 25+layer*8, 234-layer*8
    ax.add_patch(Rectangle((ox,oy),49,61,fc='white',ec='#aac0cb',lw=.8,zorder=2+layer))
for row in range(4):
    for col in range(3):
        shade=['#d6e4eb','#aac6d4','#6f99ad','#eaf0f3'][(row+2*col)%4]
        ax.add_patch(Rectangle((45+col*12,218+row*13),9,10,fc=shade,ec='none',zorder=7))
text(64,322,'数据',12,navy)
layers=[[(133,y) for y in [222,269,316]],[(194,y) for y in [198,245,292,339]],
        [(255,y) for y in [210,257,304,351]],[(316,y) for y in [248,301]]]
for left,right in zip(layers,layers[1:]):
    for i,a in enumerate(left):
        for j,b in enumerate(right):
            ax.plot([a[0],b[0]],[a[1],b[1]],color=navy,lw=.65,
                    alpha=.18+.1*((i+j)%3),zorder=3)
for k,layer in enumerate(layers):
    for j,(x,y) in enumerate(layer):node(x,y,7.4,navy,'#f3f7fa' if (k+j)%2 else '#d9e6ed')
arrow((85,269),(119,269),navy,lw=1)
text(223,389,'神经网络',14,navy)
text(213,151,r'$h^{(l+1)}=\sigma(W^{(l)}h^{(l)}+b^{(l)})$',17,navy)

# A small loss landscape and a descending optimization path.
gx,gy=np.meshgrid(np.linspace(-2.3,2.3,100),np.linspace(-1.6,1.6,80))
loss=(gx+.35*gy)**2+1.7*gy**2
ax.contour(215+gx*39,465+gy*18,loss,levels=[.35,.9,1.8,3.1,4.8],
           colors=['#c9d5dc'],linewidths=.65,zorder=1)
trace=[(284,443),(263,450),(246,461),(231,460),(224,465),(216,465)]
for a,b in zip(trace,trace[1:]):arrow(a,b,copper,lw=1,style='->',zorder=5)
for x,y in trace[::2]:node(x,y,2.6,copper,'white')
text(213,521,r'$\theta\leftarrow\theta-\eta\nabla_{\theta}\mathcal{L}$',17,copper)

# Causal attention: rows are queries and columns are keys.
arrow((335,267),(392,267),navy,rad=-.08,lw=1.4)
text(376,230,'表示',12,navy)
startx,starty,cell,n=430,200,16,8
for row in range(n):
    scores=np.exp(-.6*np.arange(row,-1,-1)); weights=scores/scores.sum()
    for col in range(n):
        active=col<=row
        from matplotlib.colors import to_rgb
        base=np.array(to_rgb(violet)); strength=(.1+.65*weights[col]) if active else .025
        fill=tuple(1-(1-base)*strength)
        ax.add_patch(Rectangle((startx+col*cell,starty+row*cell),cell-2,cell-2,
                               fc=fill,ec='#dad5e0',lw=.4,zorder=3))
text(491,180,r'$K$',16,violet)
text(410,264,r'$Q$',16,violet)
text(495,359,'因果注意力',14,violet)
text(493,416,r'$A=\mathrm{softmax}\!\left(\frac{QK^{\mathsf{T}}}{\sqrt{d_k}}+M\right)$',19,violet)
text(495,467,'上下文 · 关联 · 选择',13,violet,italic=True)

# A compact model/action/observation loop. The tool boundary is explicit.
arrow((576,267),(648,267),violet,rad=.1,lw=1.4)
text(610,229,'上下文',12,violet)
center=(803,281)
ax.add_patch(Ellipse(center,248,250,fill=False,ec='#b4cbc7',lw=.8,zorder=2))
positions=[(803,156),(917,335),(689,335)]
names=[('模型',teal),('工具',copper),('观察',violet)]
for (x,y),(label,color) in zip(positions,names):
    ax.add_patch(Circle((x,y),30,fc='white',ec=color,lw=1.4,zorder=6))
    text(x,y,label,14,color)
arrow((831,169),(922,300),teal,rad=-.25,lw=1.5)
arrow((885,347),(721,347),copper,rad=-.27,lw=1.5)
arrow((687,302),(775,170),violet,rad=-.25,lw=1.5)
text(923,226,'行动',12,teal)
text(802,424,'结果',12,copper)
text(681,226,'反馈',12,violet)
ax.add_patch(Rectangle((759,258),88,46,fc='#eaf2ef',ec='#a6bfb8',lw=.8,zorder=5))
text(803,281,'任务状态',14,teal)
for p in positions:
    ax.plot([803,p[0]],[281,p[1]],color='#90aaa4',lw=.7,linestyle=(0,(3,4)),zorder=3)
text(805,465,'AI Agent',17,teal)
text(806,521,r'$s_{t+1}=F(s_t,a_t,o_{t+1})$',17,teal)

target=ROOT/'figures'/'author_learning_action.svg'
fig.savefig(target, transparent=True, metadata={'Title':'From learned representations to agent actions',
             'Description':'Original frontispiece illustration: neural network, causal attention and model-tool-observation loop.'})
fig.savefig(target.with_suffix('.pdf'), transparent=True)
fig.savefig(target.with_suffix('.png'), dpi=240, facecolor='white')
print(target)
