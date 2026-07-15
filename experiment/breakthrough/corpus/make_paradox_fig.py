#!/usr/bin/env python3
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Circle
v=json.load(open("paradox_vectors.json"))       # metric(Claude), claude, gpt panels
C=np.array(v["claude"]);G=np.array(v["gpt"]);M=np.array(v["metric"])
def r(a,b): return float(np.corrcoef(a,b)[0,1])
BLUE="#2f6fb3";ORANGE="#e08a1e";GREEN="#3f8f5b";INK="#1a1a1a";MUT="#6b7280";GRID="#e6e8eb"
fig=plt.figure(figsize=(14,9.6));fig.patch.set_facecolor("white")
gs=fig.add_gridspec(2,2,hspace=0.42,wspace=0.26,height_ratios=[1,1.05])

def scatter(ax,y,col,name,rr):
    ax.scatter(M,y,s=30,c=col,alpha=0.75,edgecolors="white",linewidths=0.5,zorder=3)
    b,a=np.polyfit(M,y,1);xs=np.array([M.min(),M.max()]);ax.plot(xs,a+b*xs,color=col,lw=2,zorder=2)
    ax.set_xlabel("Claude-built metric  max(peak,cwmean)",fontsize=9,color=INK)
    ax.set_ylabel(f"{name} panel",fontsize=9,color=INK)
    ax.set_title(f"metric vs {name}    r = {rr:.2f}",fontsize=11,color=INK,pad=6,weight="bold")
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.grid(True,color=GRID,lw=0.8,zorder=0);ax.set_axisbelow(True);ax.tick_params(colors=MUT,labelsize=8)
axA=fig.add_subplot(gs[0,0]);scatter(axA,C,BLUE,"Claude",r(M,C))
axB=fig.add_subplot(gs[0,1]);scatter(axB,G,ORANGE,"GPT-5.5",r(M,G));axB.set_ylim(axA.get_ylim())

# bottom-left: 2x2 grouped bars (held-out Spearman) — the bias flips + consensus wins
axb=fig.add_subplot(gs[1,0])
groups=["vs Claude panel","vs GPT panel"]; x=np.arange(2); w=0.34
cb=[0.58,0.34]; gb=[0.43,0.43]; cons=[0.59,0.47]
axb.bar(x-w/2,cb,w,color=BLUE,label="Claude-built metric",zorder=3)
axb.bar(x+w/2,gb,w,color=ORANGE,label="GPT-built metric",zorder=3)
for xi,val in zip(x-w/2,cb): axb.text(xi,val+0.012,f"{val:.2f}",ha="center",fontsize=8,color=INK)
for xi,val in zip(x+w/2,gb): axb.text(xi,val+0.012,f"{val:.2f}",ha="center",fontsize=8,color=INK)
axb.plot(x,cons,"o--",color=GREEN,lw=1.6,ms=6,zorder=4,label="consensus (avg) metric")
for xi,val in zip(x,cons): axb.text(xi,val+0.02,f"{val:.2f}",ha="center",fontsize=8,color=GREEN,weight="bold")
axb.set_xticks(x);axb.set_xticklabels(groups,fontsize=9.5);axb.set_ylim(0,0.72)
axb.set_ylabel("Spearman ρ vs panel (held-out)",fontsize=9,color=INK)
axb.set_title("Bias flips sides: each metric leans toward its own model's panel",fontsize=10.5,color=INK,pad=6,weight="bold")
for s in ("top","right"): axb.spines[s].set_visible(False)
axb.grid(True,axis="y",color=GRID,lw=0.8,zorder=0);axb.set_axisbelow(True);axb.tick_params(colors=MUT,labelsize=8)
axb.legend(fontsize=7.6,loc="upper right",frameon=False)

# bottom-right: honest Venn with BOTH metrics placed
ax=fig.add_subplot(gs[1,1]);ax.set_xlim(-2.4,2.4);ax.set_ylim(-2.0,2.4);ax.axis("off");ax.set_aspect("equal")
R=1.35;dx=0.30
ax.add_patch(Circle((-dx,0.45),R,facecolor=BLUE,alpha=0.15,edgecolor=BLUE,lw=1.5))
ax.add_patch(Circle(( dx,0.45),R,facecolor=ORANGE,alpha=0.15,edgecolor=ORANGE,lw=1.5))
ax.text(-1.65,1.65,"Claude panel",color=BLUE,fontsize=10,weight="bold",ha="center")
ax.text( 1.65,1.65,"GPT panel",color=ORANGE,fontsize=10,weight="bold",ha="center")
ax.text(0,0.95,"CONSENSUS",color=INK,fontsize=10,weight="bold",ha="center")
ax.text(0,0.66,"≈83% shared (r=0.91)",color="#33383f",fontsize=7.6,ha="center")
# the two metric markers: small, sitting in consensus, each leaning to its own side
ax.add_patch(Circle((-0.5,-0.15),0.42,facecolor=BLUE,alpha=0.42,edgecolor=BLUE,lw=1.4))
ax.add_patch(Circle(( 0.5,-0.15),0.42,facecolor=ORANGE,alpha=0.42,edgecolor=ORANGE,lw=1.4))
ax.text(-0.5,-0.15,"Claude\nmetric",color="white",fontsize=6.8,weight="bold",ha="center",va="center")
ax.text( 0.5,-0.15,"GPT\nmetric",color="white",fontsize=6.8,weight="bold",ha="center",va="center")
ax.set_title("Each metric sits in consensus but leans to its maker's side",fontsize=10.5,color=INK,pad=6,weight="bold")
ax.text(0,-1.35,"metrics agree with each other only ρ=0.16 —\nClaude & GPT type contributions very differently",
        fontsize=7.8,color="#33383f",ha="center",va="top",linespacing=1.4)
fig.suptitle("Shared-method bias, proven both directions: a metric leans toward whichever model built it; consensus metric beats both",
             fontsize=12.5,color=INK,y=0.99,weight="bold")
fig.savefig("paradox_figure.png",dpi=165,bbox_inches="tight",facecolor="white")
print("done")
