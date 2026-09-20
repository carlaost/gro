#!/usr/bin/env python3
"""Prediction framing: from publication-time text alone (downstream HELD OUT), predict a paper's
eventual BREAKTHROUGH (disruption) or CONVERGENCE (consolidation) effect. Rank skill (Spearman+CI)
and classification skill (AUC for top-tercile vs rest)."""
import json, math, random
random.seed(7)
def spearman(x,y):
    def rk(v):
        o=sorted(range(len(v)),key=lambda i:v[i]);r=[0]*len(v);i=0
        while i<len(v):
            j=i
            while j+1<len(v) and v[o[j+1]]==v[o[i]]:j+=1
            a=(i+j)/2+1
            for k in range(i,j+1):r[o[k]]=a
            i=j+1
        return r
    rx,ry=rk(x),rk(y);n=len(x);mx=sum(rx)/n;my=sum(ry)/n
    c=sum((rx[i]-mx)*(ry[i]-my) for i in range(n));sx=math.sqrt(sum((v-mx)**2 for v in rx));sy=math.sqrt(sum((v-my)**2 for v in ry))
    return c/(sx*sy) if sx and sy else 0
def ci(x,y,B=3000):
    bs=sorted(spearman([x[i] for i in idx],[y[i] for i in idx]) for idx in ([random.randrange(len(x)) for _ in range(len(x))] for _ in range(B)))
    return bs[int(.025*B)],bs[int(.975*B)]
def auc(scores,labels):  # P(score of positive > score of negative)
    pos=[s for s,l in zip(scores,labels) if l]; neg=[s for s,l in zip(scores,labels) if not l]
    if not pos or not neg: return None
    w=sum((1 if a>b else 0.5 if a==b else 0) for a in pos for b in neg)
    return w/(len(pos)*len(neg))
cl={k:v['metric'] for k,v in json.load(open('metric_pubtime_ft_claude.json')).items()}
gp={k:v.get('metric') for k,v in json.load(open('metric_pubtime_ft_gpt.json')).items()}
disr=json.load(open('disruption.json')); id2s={p['id']:p['id'].split('/')[-1] for p in json.load(open('corpus.json'))}
mdi={id2s[k]:(v.get('mDI') if v.get('n_citers',0)>=10 else None) for k,v in disr.items()}
rows=[]
for s in cl:
    if cl[s] is None or gp.get(s) is None or mdi.get(s) is None: continue
    rows.append((s,(cl[s]+gp[s])/2, cl[s], gp[s], mdi[s]))
M=[r[1] for r in rows]; MC=[r[2] for r in rows]; MG=[r[3] for r in rows]; D=[r[4] for r in rows]
n=len(rows); print("n =",n,"(full-text dual-model, >=10 citers)")
Dsorted=sorted(D); t_hi=Dsorted[int(2*n/3)]; t_lo=Dsorted[int(n/3)]
print()
print("=== TASK 1 — predict BREAKTHROUGH (disruption) ===")
lo,hi=ci(M,D)
print("  consensus metric: Spearman=%+.3f  95%% CI [%+.2f,%+.2f]"%(spearman(M,D),lo,hi))
print("  Claude=%+.3f  GPT=%+.3f"%(spearman(MC,D),spearman(MG,D)))
lab_hi=[d>=t_hi for d in D]
print("  classify top-tercile-disruptive: AUC=%.2f (0.5=chance)"%(auc(M,lab_hi) or 0))
print()
print("=== TASK 2 — predict CONVERGENCE (consolidation = -disruption) ===")
negD=[-d for d in D]; lo2,hi2=ci(M,negD)
print("  consensus metric: Spearman=%+.3f  95%% CI [%+.2f,%+.2f]"%(spearman(M,negD),lo2,hi2))
lab_conv=[d<=t_lo for d in D]  # most consolidating
print("  classify top-tercile-consolidating: AUC=%.2f"%(auc(M,lab_conv) or 0))
print()
print("Reading: AUC~0.5 and CI spanning 0 => the publication-time metric cannot predict either")
print("the breakthrough or the convergence effect from the paper alone.")
json.dump({"n":n,"breakthrough_rho":round(spearman(M,D),3),"breakthrough_ci":[round(lo,3),round(hi,3)],
           "breakthrough_auc":round(auc(M,lab_hi) or 0,3),
           "convergence_rho":round(spearman(M,negD),3),"convergence_auc":round(auc(M,lab_conv) or 0,3)},
          open('predict_result.json','w'),indent=1)
