import os, math, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from rpn import Calc
os.makedirs("assets", exist_ok=True)
INK="#1f2933"; GRID="#d9dee3"; BLUE="#2563eb"; ORANGE="#e8702a"; GREEN="#2f9e44"; GREY="#8a949e"; PURPLE="#7048e8"; GOLD="#f2a900"; RED="#c92a2a"
plt.rcParams.update({"font.size":11,"axes.edgecolor":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
 "text.color":INK,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":GRID,"grid.linewidth":0.8,
 "figure.facecolor":"white","axes.facecolor":"white","svg.fonttype":"path","axes.titleweight":"bold","axes.titlesize":13})
PREVIEW=os.environ.get("PREVIEW")
def save(fig,name):
    fig.savefig(f"assets/{name}.svg",bbox_inches="tight",facecolor="white",dpi=200)
    if PREVIEW: fig.savefig(f"/tmp/lg_{name}.png",bbox_inches="tight",facecolor="white",dpi=70)
    plt.close(fig)
def box(ax,x,y,w,h,c,lw=1.8,fc="white"): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=.08",fc=fc,ec=c,lw=lw))
def orbit(r,x0,n,prec=34):
    """Runs LBL L with Flag 0 set; the PSE values are the iterates x1..xN."""
    c=Calc(prec=prec,flags={0},inputs=dict(R=r,X=x0,N=n)); c.run('L'); return [x0]+[float(v) for v in c.pses]
def lyap(r,x0,n):
    c=Calc(inputs=dict(R=r,X=x0,N=n)); c.run('E'); return float(c.st[0])

# 1 Program map
fig,ax=plt.subplots(figsize=(10,3.4)); ax.axis("off"); ax.set_xlim(0,10.2); ax.set_ylim(0,3.3)
ax.text(.1,3.15,"Program Map",fontsize=13,fontweight="bold",va="center")
items=[("L","Iterate the map","X: xₙ",BLUE,.1),("E","Lyapunov exponent","X: λ",ORANGE,3.5),("A","Both","VIEW λ, then X: xₙ",GREEN,6.9)]
for k,t,o,c,x0 in items:
    box(ax,x0,1.25,3.1,1.45,c)
    ax.text(x0+1.55,2.3,f"LBL {k}",ha="center",fontsize=13,fontweight="bold",color=c)
    ax.text(x0+1.55,1.88,t,ha="center",fontsize=10.5)
    ax.text(x0+1.55,1.5,o,ha="center",fontsize=10,color=GREY)
ax.text(.1,.75,"Prompts: R? growth rate r   X? initial value x₀   N? iterations.   Internal: Z (iteration loop), Y and X (Lyapunov loop)",fontsize=9.5,color=GREY)
ax.text(.1,.3,"Flag 0: set = pause and show every iterate during LBL Z (cleared automatically at the end of the run)",fontsize=9.5,color=GREY)
save(fig,"program_map")

# 2 Cobweb diagrams
fig,axs=plt.subplots(1,3,figsize=(12,4.3))
for ax,(r,x0,n,lab,c) in zip(axs,[(2.5,0.2,20,"r = 2.5: fixed point",BLUE),(3.2,0.5,40,"r = 3.2: period 2",GREEN),(4,0.2,60,"r = 4: chaos",RED)]):
    xs=np.linspace(0,1,300); ax.plot(xs,r*xs*(1-xs),color=INK,lw=2); ax.plot([0,1],[0,1],color=GREY,lw=1.2,ls="--")
    o=orbit(r,x0,n); px=[o[0]]; py=[0]
    for a,b in zip(o[:-1],o[1:]): px+= [a,b]; py+=[b,b]
    ax.plot(px,py,color=c,lw=1.1,alpha=.85); ax.plot(o[0],0,"o",color=c,ms=7)
    ax.set_xlim(0,1); ax.set_ylim(0,1.02); ax.set_aspect("equal"); ax.set_title(lab,loc="left",fontsize=12)
    ax.set_xlabel("xₙ")
axs[0].set_ylabel("xₙ₊₁")
fig.suptitle("Cobweb Diagrams from LBL L",x=0.02,ha="left",fontweight="bold",fontsize=13); fig.tight_layout()
save(fig,"cobweb")

# 3 Time series
fig,axs=plt.subplots(4,1,figsize=(10,6.4),sharex=True)
for ax,(r,lab,c) in zip(axs,[(2.8,"r = 2.8  fixed point 1 − 1/r",BLUE),(3.2,"r = 3.2  period 2",GREEN),(3.5,"r = 3.5  period 4",PURPLE),(3.9,"r = 3.9  chaos",RED)]):
    o=orbit(r,0.2,50); ax.plot(range(51),o,"-o",color=c,ms=3.2,lw=1.2)
    ax.set_ylim(0,1.05); ax.set_yticks([0,.5,1]); ax.set_title(lab,loc="right",fontsize=10.5,color=c,pad=3)
axs[-1].set_xlabel("Iteration n"); fig.suptitle("Iterates xₙ from x₀ = 0.2",x=0.02,ha="left",fontweight="bold",fontsize=13); fig.tight_layout()
save(fig,"time_series")

# 4 Bifurcation diagram and Lyapunov exponent
rs=np.linspace(2.5,4.0,1500); x=np.full_like(rs,0.5)
for _ in range(600): x=rs*x*(1-x)
R_=[];X_=[]
for _ in range(200): x=rs*x*(1-x); R_.append(rs.copy()); X_.append(x.copy())
rl=np.linspace(2.5,4.0,301); ly=[lyap(r,0.5,300) for r in rl]
fig,(a1,a2)=plt.subplots(2,1,figsize=(10,7),sharex=True,gridspec_kw=dict(height_ratios=[1.35,1]))
a1.plot(np.concatenate(R_),np.concatenate(X_),",",color=INK,alpha=.35,rasterized=True); a1.set_ylim(0,1); a1.set_ylabel("Long-run xₙ")
for rv,t in ((3.0,"3.0"),(1+math.sqrt(6),"3.449"),(3.5699,"3.570"),(1+math.sqrt(8),"3.828")):
    for a in (a1,a2): a.axvline(rv,color=GREY,lw=.9,ls=":")
    a1.text(rv,1.01,t,ha="center",fontsize=9,color=GREY)
a1.set_title("Bifurcation Diagram and Lyapunov Exponent",loc="left",pad=16)
ly=np.array(ly); a2.axhline(0,color=INK,lw=1)
a2.fill_between(rl,ly,0,where=ly>0,color=RED,alpha=.25,lw=0); a2.fill_between(rl,ly,0,where=ly<=0,color=BLUE,alpha=.18,lw=0)
a2.plot(rl,ly,color=INK,lw=1.2,label="LBL E, x₀ = 0.5, N = 300")
a2.set_ylim(-1.6,0.8); a2.set_ylabel("λ"); a2.set_xlabel("Growth rate r"); a2.legend(frameon=False,loc="lower left",fontsize=9.5)
a2.text(2.55,0.45,"λ > 0: chaos",color=RED,fontsize=10,fontweight="bold"); a2.text(2.55,-0.35,"λ < 0: stable",color=BLUE,fontsize=10,fontweight="bold")
a2.set_xlim(2.5,4.0); fig.tight_layout(); save(fig,"bifurcation")

# 5 Lyapunov convergence (running mean of the LBL E sum)
fig,ax=plt.subplots(figsize=(10,4.3))
for r,x0,th,c,lab in ((2.5,0.2,math.log(.5),BLUE,"r = 2.5"),(3.2,0.5,0.5*math.log(.16),GREEN,"r = 3.2"),(3.5,0.5,-0.872507,PURPLE,"r = 3.5"),(4.0,0.2,math.log(2),RED,"r = 4")):
    o=orbit(r,x0,1000); s=0; run=[]
    for k,v in enumerate(o[:-1]):
        d=abs(r*(1-2*v)); s+=math.log(d) if d else 0; run.append(s/(k+1))
    ax.plot(range(1,1001),run,color=c,lw=1.8,label=lab); ax.axhline(th,color=c,lw=1,ls="--")
ax.set_xscale("log"); ax.set_xlim(1,1000); ax.set_ylim(-1.6,1.4); ax.set_xlabel("Iterations N"); ax.set_ylabel("λ after N terms")
ax.legend(frameon=False,ncol=4,loc="lower right",bbox_to_anchor=(1,1.0),fontsize=9.5); ax.text(1.2,-1.5,"Dashed: exact value for each r",fontsize=9.5,color=GREY)
ax.set_title("The Lyapunov Exponent Settles as N Grows",loc="left",pad=26); save(fig,"lyapunov_convergence")

# 6 Sensitivity and precision
fig,(a1,a2)=plt.subplots(2,1,figsize=(10,6),sharex=True)
o1=orbit(4,0.2,60); o2=orbit(4,0.200001,60)
a1.plot(o1,"-o",color=BLUE,ms=3,lw=1.3,label="x₀ = 0.2"); a1.plot(o2,"-o",color=ORANGE,ms=3,lw=1.3,label="x₀ = 0.200001")
a1.set_ylim(0,1.05); a1.legend(frameon=False,ncol=2,loc="lower right",bbox_to_anchor=(1,1.0),fontsize=9.5); a1.set_title("Sensitive Dependence, r = 4",loc="left",pad=22)
p34=orbit(4,0.2,60,34); p12=orbit(4,0.2,60,12)
a2.plot(p34,"-o",color=BLUE,ms=3,lw=1.3,label="34-digit arithmetic (DM32)"); a2.plot(p12,"-o",color=GREY,ms=3,lw=1.3,label="12-digit arithmetic (HP-32SII precision)")
a2.set_ylim(0,1.05); a2.legend(frameon=False,ncol=2,loc="lower right",bbox_to_anchor=(1,1.0),fontsize=9.5); a2.set_xlabel("Iteration n")
a2.set_title("Same Start, Different Precision, r = 4, x₀ = 0.2",loc="left",pad=22); fig.tight_layout(); save(fig,"sensitivity")
