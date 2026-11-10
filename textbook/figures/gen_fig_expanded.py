"""Original analytic illustrations and plots from saved, actually executed experiments."""
from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"_build_deps"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
font_manager.fontManager.addfont(str(ROOT/"vendor/fonts/NotoSerifSC-Regular.ttf"))
plt.rcParams.update({
    "font.family":["Noto Serif SC","DejaVu Serif"],"font.size":11,"axes.titlesize":12,
    "mathtext.fontset":"dejavuserif",
    "axes.titleweight":"normal","axes.labelsize":10,"axes.unicode_minus":False,
    "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#9aaeb4",
    "text.color":"#183543","axes.labelcolor":"#183543","xtick.color":"#536675",
    "ytick.color":"#536675","axes.grid":True,"grid.alpha":.15,
    "legend.frameon":False,"legend.fontsize":9,"lines.linewidth":2,
    "pdf.fonttype":42,"ps.fonttype":42,"savefig.facecolor":"white",
})
OUT=ROOT/"figures"; RESULTS=ROOT/"projects/results"
B,O,G,R,P="#0072B2","#E69F00","#009E73","#D55E00","#CC79A7"
CM=LinearSegmentedColormap.from_list("book",["#f1f6f5","#9bd5c9","#0072B2"])
def save(fig,name):
    selected=os.environ.get("BOOK_FIGURES","")
    if selected and name not in selected.split(","):
        plt.close(fig)
        return
    fig.savefig(OUT/(name+".png"),dpi=300,bbox_inches="tight",pad_inches=.17)
    fig.savefig(OUT/(name+".pdf"),bbox_inches="tight",pad_inches=.17)
    plt.close(fig)
def grid_numbers(ax,m,title,fmt=".2f",vmin=None,vmax=None):
    ax.imshow(m,cmap=CM,vmin=vmin,vmax=vmax,aspect="auto")
    low=float(m.min()) if vmin is None else vmin
    high=float(m.max()) if vmax is None else vmax
    for (i,j),v in np.ndenumerate(m):
        fraction=(v-low)/max(high-low,1e-12)
        ax.text(j,i,format(v,fmt),ha="center",va="center",fontsize=11,
                color="white" if fraction>.68 else "#183543")
    ax.set_title(title,pad=12);ax.grid(False)
    ax.set_xticks(range(m.shape[1]));ax.set_yticks(range(m.shape[0]))

# Geometry: same direction is different from same distance.
fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout="constrained")
for v,label,c in [(np.array([1,2]),"a = (1, 2)",B),(np.array([2,4]),"b = (2, 4)",O),(np.array([2,1]),"c = (2, 1)",G)]:
    axes[0].quiver(0,0,*v,angles="xy",scale_units="xy",scale=1,color=c,width=.013)
    axes[0].text(v[0]+.07,v[1],label,color=c,fontsize=10)
axes[0].set(xlim=(-.2,3.5),ylim=(-.2,4.7),title="长度与方向是两种信息",xlabel="维度 1",ylabel="维度 2")
axes[0].set_aspect("equal")
values=[[np.sqrt(5),np.sqrt(2)],[1.,.8]]
axes[1].bar(np.arange(2)-.18,values[0],.34,label="欧氏距离",color=B)
axes[1].bar(np.arange(2)+.18,values[1],.34,label="余弦相似度",color=G,hatch="//")
axes[1].set(xticks=[0,1],xticklabels=["a 与 b","a 与 c"],title="数值小不总是表示更相似",ylabel="各自定义下的数值")
axes[1].legend()
save(fig,"fig_08_geometry")

# ReLU spline construction.
x=np.linspace(-1,3,500);relu=lambda z:np.maximum(z,0)
fig,axes=plt.subplots(1,2,figsize=(9,3.4),layout="constrained")
for y,label,c,ls in [(relu(x),"ReLU(x)",B,"-"),(-2*relu(x-1),"-2 ReLU(x−1)",O,"--"),(relu(x-2),"ReLU(x−2)",G,"-.")]:
    axes[0].plot(x,y,label=label,color=c,ls=ls)
axes[0].set(title="三个折线单元",xlabel="x",ylabel="分量");axes[0].legend()
axes[1].plot(x,relu(x)-2*relu(x-1)+relu(x-2),color=B)
axes[1].scatter([0,1,2],[0,1,0],color=R,zorder=3)
axes[1].set(title="线性组合得到三角形函数",xlabel="x",ylabel="输出",ylim=(-.12,1.25))
save(fig,"fig_09_relu_spline")

# Binary cross entropy and gradient.
z=np.linspace(-7,7,500);p=1/(1+np.exp(-z))
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
for y,c,ls in [(0,O,"--"),(1,B,"-")]:
    axes[0].plot(z,np.logaddexp(0,z)-y*z,label=f"真实标签 y={y}",color=c,ls=ls)
    axes[1].plot(z,p-y,label=f"y={y}：p−y",color=c,ls=ls)
for ax,title,yl in zip(axes,["错误且自信时损失增大","梯度给出纠正方向"],["二元交叉熵","对 logit 的导数"]):
    ax.set(title=title,xlabel="logit z",ylabel=yl);ax.legend()
save(fig,"fig_10_bce_gradient")

# Curvature and step size.
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout="constrained")
u=np.linspace(-2.5,2.5,180);v=np.linspace(-1.2,1.2,180);xx,yy=np.meshgrid(u,v)
axes[0].contour(xx,yy,.5*(xx**2+12*yy**2),levels=[.1,.3,.6,1,2,4,7,10],colors="#b7cfce")
for lr,c in [(.04,B),(.15,R)]:
    pt=np.array([2.,.8]);track=[pt.copy()]
    for _ in range(25):
        pt-=lr*np.array([pt[0],12*pt[1]]);track.append(pt.copy())
    a=np.array(track);axes[0].plot(a[:,0],a[:,1],".-",c=c,label=f"学习率 {lr}")
axes[0].set(title="陡峭方向限制全局步长",xlabel="参数 w₁",ylabel="参数 w₂");axes[0].legend()
for lr,c,ls in [(.05,B,"-"),(.15,G,"--"),(.18,R,":")]:
    a=np.array([2.,.8]);loss=[]
    for _ in range(35):
        loss.append(.5*(a[0]**2+12*a[1]**2));a-=lr*np.array([a[0],12*a[1]])
    axes[1].plot(loss,color=c,ls=ls,label=f"学习率 {lr}")
axes[1].set(title="超过 2/12 后不稳定",xlabel="更新步",ylabel="损失",yscale="log");axes[1].legend()
save(fig,"fig_11_curvature")

# Normalization axes.
a=np.array([[1.,2.,10.],[3.,4.,14.],[5.,6.,18.]])
bn=(a-a.mean(0))/np.sqrt(a.var(0)+1e-5)
ln=(a-a.mean(1,keepdims=True))/np.sqrt(a.var(1,keepdims=True)+1e-5)
fig,axes=plt.subplots(1,3,figsize=(9,3.1),layout="constrained")
for ax,m,t in zip(axes,[a,bn,ln],["原始：行是样本，列是特征","沿批维标准化（逐列）","沿特征维标准化（逐行）"]):
    grid_numbers(ax,m,t);ax.set_xlabel("特征");ax.set_ylabel("样本")
save(fig,"fig_12_normalization")

# Receptive field as literal input grids, two stride-one convolutions.
fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout="constrained")
for ax,side,title in zip(axes,[3,5],["一层 3×3 卷积：感受野 3×3","两层 3×3 卷积：感受野 5×5"]):
    m=np.zeros((7,7));start=(7-side)//2;m[start:start+side,start:start+side]=1
    ax.imshow(m,cmap=CM,vmin=0,vmax=1);ax.scatter([3],[3],c=O,s=90,marker="x")
    ax.set_xticks(np.arange(-.5,7,1),minor=True);ax.set_yticks(np.arange(-.5,7,1),minor=True)
    ax.grid(which="minor",color="white",lw=1.5);ax.grid(which="major",visible=False)
    ax.set_xticks([]);ax.set_yticks([]);ax.set_title(title)
save(fig,"fig_13_receptive_field")

# Fully specified Q=K=V attention.
X=np.array([[1.,0.],[0.,1.],[1.,1.]])
score=X@X.T/np.sqrt(2);A=np.exp(score-score.max(1,keepdims=True));A/=A.sum(1,keepdims=True)
fig,axes=plt.subplots(1,3,figsize=(9,3.2),layout="constrained")
for ax,m,t in zip(axes,[score,A,A@X],["QKᵀ / √2","逐行 Softmax 权重","AV：混合后的表示"]):
    grid_numbers(ax,m,t,".3f")
save(fig,"fig_14_attention_values")

# Rotation position encoding.
fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout="constrained")
theta=np.linspace(0,2*np.pi,250);axes[0].plot(np.cos(theta),np.sin(theta),c="#b7cfce")
for angle,c,label in [(0,B,"位置 0"),(.6,G,"位置 1"),(1.2,O,"位置 2")]:
    axes[0].quiver(0,0,np.cos(angle),np.sin(angle),angles="xy",scale_units="xy",scale=1,color=c,width=.012,label=label)
axes[0].set(xlim=(-1.2,1.2),ylim=(-1.2,1.2),title="二维向量随位置旋转")
axes[0].set_aspect("equal");axes[0].legend(loc="lower left")
d=np.arange(-10,11);axes[1].plot(d,np.cos(.6*d),"o-",color=B)
axes[1].set(title="同向量旋转后的点积",xlabel="相对位置 m−n",ylabel="cos[0.6(m−n)]")
save(fig,"fig_15_rotary")

# VAE distributions and transformation.
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
x=np.linspace(-4,5,500)
for mu,sd,c,lab in [(0,1,B,"先验 N(0, 1)"),(1.5,.7,O,"示例后验 N(1.5, 0.7²)")]:
    axes[0].plot(x,np.exp(-.5*((x-mu)/sd)**2)/(sd*np.sqrt(2*np.pi)),c=c,label=lab)
axes[0].set(title="分布可以同时改变中心与宽度",xlabel="潜变量 z",ylabel="概率密度");axes[0].legend()
eps=np.linspace(-2,2,100);axes[1].plot(eps,1.5+.7*eps,color=G)
axes[1].scatter([.4],[1.78],c=R,zorder=3)
axes[1].set(title="重参数化 z = 1.5 + 0.7 ε",xlabel="基础噪声 ε",ylabel="采样值 z")
save(fig,"fig_16_reparameterization")

# Forward diffusion signal/noise coefficients.
t=np.arange(1,1001);beta=np.linspace(1e-4,.02,1000);ab=np.cumprod(1-beta)
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
axes[0].plot(t,np.sqrt(ab),c=B,label="信号系数 √ᾱ")
axes[0].plot(t,np.sqrt(1-ab),c=O,label="噪声系数 √(1−ᾱ)",ls="--")
axes[0].set(title="线性 beta 日程下的系数",xlabel="加噪步 t",ylabel="系数");axes[0].legend()
axes[1].plot(t,ab/(1-ab),color=G)
axes[1].set(title="信噪比逐步降低",xlabel="加噪步 t",ylabel="ᾱ / (1−ᾱ)",yscale="log")
save(fig,"fig_17_diffusion_snr")

# Same predictions, multiple thresholds.
scores=np.array([.95,.85,.8,.7,.55,.4,.25,.1]);labels=np.array([1,0,1,1,0,1,0,0])
thr=np.linspace(0,1,101);precision=[];recall=[];fp=[]
for q in thr:
    pred=scores>=q;tp=np.sum(pred&(labels==1));f=np.sum(pred&(labels==0))
    precision.append(tp/(tp+f) if tp+f else np.nan);recall.append(tp/4);fp.append(f/4)
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
axes[0].step(thr,precision,where="post",color=B,label="精确率")
axes[0].step(thr,recall,where="post",color=O,label="召回率",ls="--")
axes[0].set(title="八个教学样本的阈值权衡",xlabel="分类阈值",ylabel="比例",ylim=(-.03,1.08));axes[0].legend()
axes[1].scatter(scores,labels,c=[B if y else O for y in labels],s=75,edgecolors="white")
axes[1].axvline(.6,color=G,ls="--");axes[1].set(title="阈值 0.6 的逐样本决策",xlabel="预测分数",ylabel="真实标签",yticks=[0,1],ylim=(-.2,1.2))
save(fig,"fig_18_threshold_metrics")

# Analytically specified calibration, no fake measured evidence.
conf=np.linspace(.1,.9,9)
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
axes[0].plot([0,1],[0,1],"--",color="#94a3b8",label="理想校准")
axes[0].plot(conf,conf**1.5,"o-",color=R,label="构造的过度自信关系")
axes[0].set(title="校准关心概率与频率是否一致",xlabel="报告的概率",ylabel="假设的真实发生率",xlim=(0,1),ylim=(0,1));axes[0].legend()
z=np.array([3.,1.,0.]);temps=[.5,1,2];probs=[]
for T in temps:
    q=np.exp(z/T-max(z/T));probs.append(q/q.sum())
for j,c in enumerate([B,O,G]):axes[1].bar(np.arange(3)+(j-1)*.24,np.array(probs)[:,j],.23,color=c,label=f"类别 {j}")
axes[1].set(xticks=range(3),xticklabels=["T=0.5","T=1","T=2"],title="温度改变置信度，保持排序",ylabel="Softmax 概率");axes[1].legend()
save(fig,"fig_19_calibration")

# Ridge and low rank geometry use a deterministic illustrative regression.
rng=np.random.default_rng(13);x=np.linspace(-1,1,22);y=np.sin(3*x)+rng.normal(0,.15,len(x))
xx=np.linspace(-1,1,300);A=np.stack([x**k for k in range(9)],axis=1);AA=np.stack([xx**k for k in range(9)],axis=1)
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
for alpha,c,ls in [(1e-7,R,":"),(.01,B,"-"),(3,G,"--")]:
    reg=np.eye(9)*alpha;reg[0,0]=0;w=np.linalg.solve(A.T@A+reg,A.T@y)
    axes[0].plot(xx,AA@w,c=c,ls=ls,label=f"α={alpha:g}")
    axes[1].plot(range(1,9),np.abs(w[1:]),"o"+ls,color=c,label=f"α={alpha:g}")
axes[0].scatter(x,y,c=O,s=23,zorder=3);axes[0].set(title="同一特征空间，不同收缩强度",xlabel="x",ylabel="预测");axes[0].legend()
axes[1].set(title="正则项改变系数大小",xlabel="多项式次数",ylabel="系数绝对值",yscale="log");axes[1].legend()
save(fig,"fig_20_ridge")

# Actual project results.
d=np.load(RESULTS/"bike.npz");fig,ax=plt.subplots(figsize=(9,3.4),layout="constrained")
yy=d["all_y"];ax.plot(np.arange(len(yy)),yy,c=B,lw=1.1)
for left,right,color,label in [(0,7,"#e9ebeb","历史准备"),(7,507,"#dbefe9","训练 500 天"),(507,607,"#fff0cd","验证 100 天"),(607,731,"#e0eaf5","测试 124 天")]:
    ax.axvspan(left,right,color=color,alpha=.65,zorder=0)
    if right-left>20:ax.text((left+right)/2,8500,label,ha="center",fontsize=10)
ax.set(title="公开数据：时间顺序决定评估边界",xlabel="从 2011-01-01 起的日序号",ylabel="日租借次数",ylim=(0,9500))
save(fig,"fig_21_bike_timeline")

fig,axes=plt.subplots(2,1,figsize=(9,6),layout="constrained")
for key,c,ls,lab in [("truth","#344b56","-","真实总量"),("ridge",G,"--","岭回归"),("pred",B,"-","MLP，种子42")]:
    axes[0].plot(d[key],color=c,ls=ls,lw=1.5,label=lab)
axes[0].set(title="测试区间逐日预测",xlabel="测试日序号",ylabel="日租借次数");axes[0].legend(ncol=3)
mae=[904.6774,1306.4355,859.8132,1049.6712];rmse=[1320.0166,1880.9024,1190.9144,1303.8019]
axes[1].bar(np.arange(4)-.18,mae,.35,color=B,label="MAE")
axes[1].bar(np.arange(4)+.18,rmse,.35,color=O,hatch="//",label="RMSE")
axes[1].set(xticks=range(4),xticklabels=["昨天总量","上周同日","岭回归","MLP / 42"],ylabel="日租借次数",title="网络复杂度没有转化为本次最佳误差")
axes[1].legend()
save(fig,"fig_22_bike_predictions")

d=np.load(RESULTS/"digits.npz")
fig,axes=plt.subplots(2,6,figsize=(9,3.7),layout="constrained")
for i,ax in enumerate(axes.flat):
    ax.imshow(d["images"][i],cmap="Greys",vmin=0,vmax=1);ax.set_title(f"真实：{d['truth'][i]}",fontsize=11);ax.axis("off")
save(fig,"fig_23_digits_gallery")

fig=plt.figure(figsize=(9,5),layout="constrained");gs=fig.add_gridspec(2,4,width_ratios=[1.2,1.2,1,1])
ax=fig.add_subplot(gs[:,:2]);cm=d["confusion"];ax.imshow(cm,cmap=CM,vmin=0,vmax=40)
for (i,j),v in np.ndenumerate(cm):
    if v:ax.text(j,i,str(v),ha="center",va="center",fontsize=9,color="white" if v>25 else "#183543")
ax.set(xticks=range(10),yticks=range(10),xlabel="预测类别",ylabel="真实类别",title="混淆矩阵 / 种子 42");ax.grid(False)
wrong=np.flatnonzero(d["truth"]!=d["pred"])
for n,(r,c) in enumerate([(0,2),(0,3),(1,2),(1,3)]):
    i=wrong[n];ax=fig.add_subplot(gs[r,c]);ax.imshow(d["images"][i],cmap="Greys",vmin=0,vmax=1)
    ax.set_title(f"{d['truth'][i]} → {d['pred'][i]}",color=R);ax.axis("off")
save(fig,"fig_24_digits_confusion")

fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout="constrained");h=d["history"]
axes[0].plot(h[:,0],h[:,1],c=B,label="训练");axes[0].plot(h[:,0],h[:,2],c=O,label="验证")
axes[0].axvline(28,c=G,ls="--",lw=1);axes[0].set(title="按验证损失选择第 28 轮",xlabel="epoch",ylabel="交叉熵");axes[0].legend()
p=np.exp(d["logits"]-d["logits"].max(1,keepdims=True));p/=p.sum(1,keepdims=True);correct=d["truth"]==d["pred"]
axes[1].hist(p.max(1)[correct],bins=np.linspace(.2,1,9),color=B,alpha=.7,label="正确")
axes[1].hist(p.max(1)[~correct],bins=np.linspace(.2,1,9),color=O,alpha=.8,label="错误",hatch="//")
axes[1].set(title="错误也可能带有较高置信度",xlabel="最大 Softmax 概率",ylabel="样本数（对称对数轴）",yscale="symlog");axes[1].legend()
save(fig,"fig_25_digits_learning")

d=np.load(RESULTS/"sensor.npz");fig,axes=plt.subplots(2,1,figsize=(9,5.8),layout="constrained")
for key,c,ls,lab in [("raw","#b9c1c5","-","含噪输入"),("truth","#183543","-","干净真值"),("median",O,"--","中值滤波"),("pred",B,"-","CNN估计")]:
    axes[0].plot(d[key][:81],c=c,ls=ls,lw=1.5,label=lab)
axes[0].set(title="模拟信号：第一段测试轨迹",xlabel="窗口末端采样步（相对）",ylabel="距离／厘米");axes[0].legend(ncol=4,fontsize=9)
mae=[2.1768,1.2997,1.2241];rmse=[4.4012,1.6109,1.6239]
axes[1].bar(np.arange(3)-.18,mae,.35,color=B,label="MAE");axes[1].bar(np.arange(3)+.18,rmse,.35,color=O,hatch="//",label="RMSE")
axes[1].set(xticks=range(3),xticklabels=["原始观测","五点因果中值","一维 CNN"],ylabel="误差／厘米",title="两种误差指标并未给出同一赢家");axes[1].legend()
save(fig,"fig_26_sensor_trace")

d=np.load(RESULTS/"segmentation.npz");ids=[0,1,int(np.flatnonzero(d["truth"].sum((1,2))==0)[0])]
fig,axes=plt.subplots(3,5,figsize=(9,5.8),layout="constrained")
for r,i in enumerate(ids):
    for c,(key,title) in enumerate([("images","输入"),("truth","真实掩膜"),("threshold_baseline","阈值法"),("prob","网络分数"),("pred","网络预测")]):
        axes[r,c].imshow(d[key][i],cmap="Greys" if key=="images" else CM,vmin=0,vmax=1)
        if r==0:axes[r,c].set_title(title,fontsize=11)
        axes[r,c].axis("off")
fig.colorbar(axes[0,3].images[0],ax=list(axes[:,3]),shrink=.72,ticks=[0,.5,1],fraction=.1,pad=.03)
save(fig,"fig_27_segmentation_examples")

d=np.load(RESULTS/"retrieval.npz");fig,ax=plt.subplots(figsize=(9,5.5),layout="constrained")
im=ax.imshow(d["scores"],cmap=CM,aspect="auto",vmin=0,vmax=max(.6,d["scores"].max()))
for row,col in enumerate(d["truth"]):ax.add_patch(Rectangle((col-.45,row-.45),.9,.9,fill=False,lw=1.8,edgecolor=O))
ax.set(xticks=range(12),xticklabels=[f"A{i:02}" for i in range(1,13)],yticks=range(15),yticklabels=[f"Q{i:02}" for i in range(1,16)],xlabel="虚构说明文档",ylabel="手写问题",title="词面相似度矩阵：金色框为相关目标")
ax.grid(False);fig.colorbar(im,ax=ax,pad=.02,label="余弦分数")
save(fig,"fig_28_retrieval_scores")
import json
lab=json.loads((RESULTS/"derivation_lab.json").read_text(encoding="utf-8"))
arr=np.array(lab["finite_difference"])
fig,ax=plt.subplots(figsize=(9,3.6),layout="constrained")
ax.loglog(arr[:,0],arr[:,1],"o-",color=B)
ax.set(title="全部 9 个参数的梯度核验",xlabel="中心差分步长 epsilon",ylabel="最大绝对误差")
ax.invert_xaxis()
save(fig,"fig_29_gradient_check")
d=np.load(RESULTS/"mini_transformer.npz")
fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout="constrained")
axes[0].plot(np.arange(1,len(d["losses"])+1),d["losses"],color=P)
axes[0].set(title="两条固定序列上的拟合",xlabel="优化器更新步",ylabel="交叉熵")
axes[1].bar(range(4),d["causal_difference"],color=[B,B,B,O])
axes[1].set(title="只改最后一个输入 token",xlabel="输出位置",ylabel="logits 最大绝对变化",xticks=range(4))
axes[1].text(1,0.3,"较早位置变化 = 0",ha="center",fontsize=10,color=B)
save(fig,"fig_30_transformer_lab")

fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
boxes=[(10,10,40,40,.93,B),(12,12,40,40,.88,R),(60,10,40,40,.76,G)]
for ax,selected,title in zip(axes,[[0,1,2],[0,2]],["抑制前：两个框高度重叠","NMS 后：保留两个候选"]):
    for j in selected:
        x,y,w,h,score,c=boxes[j];ax.add_patch(Rectangle((x,y),w,h,fill=False,ec=c,lw=2,ls="--" if j==1 else "-"))
        ax.text(x,y-4 if j!=1 else y+h+10,f"框{j+1} / {score:.2f}",color=c,fontsize=10)
    ax.set(xlim=(0,110),ylim=(75,-5),title=title,xlabel="x",ylabel="y");ax.set_aspect("equal")
save(fig,"fig_31_detection_nms")

x=np.linspace(-1.5,1.5,601);scale=.25;q=np.clip(np.rint(x/scale),-4,4);xh=scale*q
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout="constrained")
axes[0].plot(x,x,"--",c="#91a5b0",label="理想恒等映射")
axes[0].plot(x,xh,c=P,label="量化还原")
axes[0].set(title="步长 0.25，整数范围 −4 到 4",xlabel="原始值 x",ylabel="还原值");axes[0].legend()
axes[1].plot(x,xh-x,c=R)
axes[1].axvspan(-1.5,-1.125,color="#f6e2ec",zorder=0);axes[1].axvspan(1.125,1.5,color="#f6e2ec",zorder=0)
axes[1].set(title="格点舍入误差与范围截断",xlabel="原始值 x",ylabel="还原值 − 原始值")
save(fig,"fig_32_quantization")
adj=np.array([[1.,1,0],[1,1,1],[0,1,1]])
deg=adj.sum(1);norm=adj/np.sqrt(deg[:,None]*deg[None,:]);before=np.array([1.,2,0]);after=norm@before
fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout="constrained")
grid_numbers(axes[0],norm,"对称度归一化系数 S",".3f",0,1)
axes[0].set(xlabel="信息来源节点",ylabel="接收节点",xticklabels=[1,2,3],yticklabels=[1,2,3])
axes[1].bar(np.arange(3)-.18,before,.35,color=P,label="传播前")
axes[1].bar(np.arange(3)+.18,after,.35,color=G,hatch="//",label="传播后")
axes[1].set(xticks=range(3),xticklabels=["节点1","节点2","节点3"],ylabel="特征数值",title="一次图传播带来的变化")
axes[1].legend()
save(fig,"fig_33_graph_aggregation")

similarity=np.array([.8,.3,-.2]);temps=[1,.5,.1];ps=[]
for temp in temps:
    logits=similarity/temp;v=np.exp(logits-logits.max());ps.append(v/v.sum())
ps=np.array(ps)
fig,ax=plt.subplots(figsize=(9,3.6),layout="constrained")
for j,(label,c,hatch) in enumerate([("正样本 / 0.8",G,""),("负样本1 / 0.3",O,"//"),("负样本2 / −0.2",P,"..")]):
    bars=ax.bar(np.arange(3)+(j-1)*.24,ps[:,j],.23,color=c,label=label,hatch=hatch)
    ax.bar_label(bars,fmt="%.3f",fontsize=9,padding=3)
ax.set(xticks=range(3),xticklabels=["温度 1.0","温度 0.5","温度 0.1"],ylabel="归一化权重",ylim=(0,1.2),title="低温度使同一组相似度的分布更尖锐")
ax.legend(ncol=3,loc="upper left")
save(fig,"fig_34_contrastive_temperature")
print("Saved figure groups:",os.environ.get("BOOK_FIGURES") or "all 27 expanded-edition groups")


