"""Reproducible mathematical illustrations; measured plots use experiment files."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_build_deps"))
sys.path.insert(0, str(ROOT))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from numpy_mlp_demo import forward

OUT = ROOT / "figures"
font_manager.fontManager.addfont(str(ROOT/"vendor/fonts/NotoSerifSC-Regular.ttf"))
plt.rcParams.update({
    "font.family": ["Noto Serif SC","DejaVu Serif"], "font.size": 10,
    "mathtext.fontset": "dejavuserif",
    "axes.titlesize": 12, "axes.titleweight": "normal",
    "axes.labelsize": 10, "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#94a3b8", "text.color": "#233744",
    "axes.labelcolor": "#233744", "xtick.color": "#536675",
    "ytick.color": "#536675", "axes.grid": True, "grid.alpha": .14,
    "legend.frameon": False, "legend.fontsize": 9,
    "lines.linewidth": 2.0, "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.facecolor": "white",
})
BLUE, ORANGE, GREEN, RED = "#0072B2", "#E69F00", "#009E73", "#D55E00"


def save(fig, name):
    fig.savefig(OUT / (name + ".png"), dpi=300, bbox_inches="tight", pad_inches=.18)
    fig.savefig(OUT / (name + ".pdf"), bbox_inches="tight", pad_inches=.18)
    plt.close(fig)


x = np.linspace(-4, 4, 400)
sig = 1 / (1 + np.exp(-x))
fig, axes = plt.subplots(1, 2, figsize=(9, 3.25), layout="constrained")
for y, label, color, style in [
    (sig, "Sigmoid", BLUE, "-"), (np.tanh(x), "Tanh", ORANGE, "--"),
    (np.maximum(x, 0), "ReLU", GREEN, "-.")]:
    axes[0].plot(x, y, label=label, color=color, ls=style)
for y, label, color, style in [
    (sig*(1-sig), "Sigmoid", BLUE, "-"),
    (1-np.tanh(x)**2, "Tanh", ORANGE, "--"),
    ((x>0).astype(float), "ReLU（零点外）", GREEN, "-.")]:
    axes[1].plot(x, y, label=label, color=color, ls=style)
axes[0].set(title="激活函数", xlabel="输入 z", ylabel="输出")
axes[1].set(title="局部导数", xlabel="输入 z", ylabel="导数")
for ax in axes: ax.legend(loc="upper left")
save(fig, "fig_01_activations")

fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), layout="constrained")
w = np.linspace(-.3, 4.3, 300)
axes[0].plot(w, 2*(w-2)**2, color=BLUE)
path = [0.]
for _ in range(8): path.append(path[-1] - .15*4*(path[-1]-2))
path = np.array(path)
axes[0].plot(path, 2*(path-2)**2, "o--", color=ORANGE, ms=5)
axes[0].set(title="参数沿负梯度接近最低点", xlabel="参数 w", ylabel="损失 L")
for rate, color, style in [(.03, BLUE, "-"), (.15, GREEN, "--"), (.52, RED, ":")]:
    pos, losses = 0., []
    for _ in range(15):
        losses.append(2*(pos-2)**2)
        pos -= rate*4*(pos-2)
    axes[1].plot(losses, color=color, ls=style, label=f"学习率 {rate}")
axes[1].set(title="步长改变训练行为", xlabel="更新次数", ylabel="损失（对数刻度）", yscale="log")
axes[1].legend()
save(fig, "fig_02_gradient")

rng = np.random.default_rng(11)
xx = np.linspace(-1, 1, 18)
yy = np.sin(3*xx) + rng.normal(0, .20, len(xx))
grid = np.linspace(-1, 1, 300)
fig, axes = plt.subplots(1, 3, figsize=(9, 3.0), layout="constrained")
for ax, degree, title in zip(axes, [1, 3, 14], ["低容量：欠拟合", "中等容量：较合理", "高容量：追随噪声"]):
    poly = np.polynomial.Polynomial.fit(xx, yy, degree)
    ax.plot(grid, np.sin(3*grid), "--", color="#82919a", label="真实规则")
    ax.plot(grid, poly(grid), color=BLUE, label="拟合")
    ax.scatter(xx, yy, color=ORANGE, s=20, zorder=3, label="含噪训练点")
    ax.set(title=title, xlabel="输入 x", ylim=(-1.8, 1.8))
axes[0].set_ylabel("输出 y")
axes[0].legend(fontsize=8)
save(fig, "fig_03_capacity")

fig, axes = plt.subplots(1, 3, figsize=(9, 3.1), layout="constrained")
image = np.zeros((7, 7)); image[:, 3:] = 1
kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
output = np.array([[np.sum(image[i:i+3,j:j+3]*kernel) for j in range(5)] for i in range(5)])
cmap = LinearSegmentedColormap.from_list("book", ["#f4f7f6", BLUE])
for ax, arr, title in zip(axes, [image,kernel,output], ["输入：垂直边缘", "3×3 边缘核", "有效区域的互相关输出"]):
    ax.imshow(arr, cmap=cmap)
    for (i,j), value in np.ndenumerate(arr):
        ax.text(j, i, f"{value:g}", ha="center", va="center",
                color="white" if value > (arr.max()+arr.min())/2 else "#233744", fontsize=9)
    ax.set(title=title, xlabel="列位置", ylabel="行位置")
    ax.grid(False); ax.set_xticks(range(arr.shape[1])); ax.set_yticks(range(arr.shape[0]))
save(fig, "fig_04_convolution")

fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.3), layout="constrained")
q = np.array([[1.,0.],[.5,.5],[0.,1.],[.8,.2]])
scores = q@q.T / np.sqrt(2)
for ax, causal, title in zip(axes,[False,True],["双向访问：每行均可看全部位置","因果访问：未来位置权重为零"]):
    s = scores.copy()
    if causal: s[np.triu_indices(4,1)] = -np.inf
    weight = np.exp(s-s.max(axis=1,keepdims=True)); weight /= weight.sum(axis=1,keepdims=True)
    ax.imshow(weight, cmap=cmap, vmin=0,vmax=1)
    for (i,j), value in np.ndenumerate(weight):
        ax.text(j,i,f"{value:.2f}",ha="center",va="center",color="white" if value>.6 else "#233744")
    ax.set(title=title,xlabel="被访问的位置（Key）",ylabel="当前位置（Query）",
           xticks=range(4),yticks=range(4))
    ax.grid(False)
save(fig,"fig_05_attention")

fig, axes = plt.subplots(1, 4, figsize=(9,2.7), layout="constrained")
g = np.linspace(-1,1,48); gx,gy=np.meshgrid(g,g)
original=((gx**2+gy**2<.55)&(gx**2+gy**2>.20)).astype(float)
noise=np.random.default_rng(5).normal(size=original.shape)
for ax,a,title in zip(axes,[1,.7,.3,0],["原始结构","较少噪声","较多噪声","高斯噪声"]):
    ax.imshow(np.sqrt(a)*original+np.sqrt(1-a)*noise,cmap="gray",vmin=-1.8,vmax=2)
    ax.set_title(title); ax.set_axis_off()
save(fig,"fig_06_diffusion")

arr = np.loadtxt(ROOT/"experiment"/"history.csv",delimiter=",",skiprows=1)
data = np.load(ROOT/"experiment"/"numpy_mlp.npz")
fig, axes=plt.subplots(1,2,figsize=(9,3.3),layout="constrained")
axes[0].plot(arr[:,0],arr[:,1],color=BLUE,label="训练损失")
axes[0].plot(arr[:,0],arr[:,2],color=ORANGE,ls="--",label="验证损失")
axes[0].set(title="实际实验：学习曲线",xlabel="Epoch",ylabel="交叉熵")
axes[0].legend()
coords=np.linspace(-1.5,1.5,160); a,b=np.meshgrid(coords,coords)
points=np.c_[a.ravel(),b.ravel()]
_,logp=forward((points-data["mean"])/data["std"],data)
prob=np.exp(logp[:,1]).reshape(a.shape)
axes[1].contourf(a,b,prob,levels=np.linspace(0,1,11),cmap=cmap,alpha=.8)
axes[1].contour(a,b,prob,levels=[.5],colors=[BLUE],linewidths=2)
test=data["x_test"]*data["std"]+data["mean"]
for cls,color,marker in [(0,ORANGE,"o"),(1,"#264653","x")]:
    sel=np.flatnonzero(data["y_test"]==cls)[:80]
    axes[1].scatter(test[sel,0],test[sel,1],c=color,marker=marker,s=13,label=f"测试类 {cls}")
axes[1].set(title="实际实验：决策边界",xlabel=r"原始特征 $x_1$",ylabel=r"原始特征 $x_2$",aspect="equal")
axes[1].legend(loc="upper right",fontsize=8)
save(fig,"fig_07_experiment")
print("Created 7 figure pairs (300-DPI PNG + vector PDF).")


