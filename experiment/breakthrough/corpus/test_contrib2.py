#!/usr/bin/env python3
import glob, json, os, yaml
from apply_formula import spearman, load_split
ARALIB="/Users/carlaostmann/code/dasmodel/research/ara-library"
NOVW={"new_paradigm":1.0,"new_method":0.8,"new_finding":0.7,"refutation":0.6,
      "synthesis":0.35,"incremental_improvement":0.15,"replication":0.1}
def contribs(gro):
    fp=os.path.join(gro,"contributions.yaml")
    if not os.path.exists(fp): return []
    doc=yaml.safe_load(open(fp)) or {}
    out=[]
    for c in (doc.get("contributions") or []):
        cat=(c.get("compiler_assessed_type") or {}); w=NOVW.get(cat.get("primary"),0.10)
        conf=cat.get("confidence"); conf=float(conf) if isinstance(conf,(int,float)) else 0.3
        if not (c.get("realized_in") or []): w=0.0
        out.append((w,conf))
    return out
def feats(cs):
    if not cs: return {}
    wc=sorted(((w*conf,w,conf) for w,conf in cs),reverse=True)
    peak=wc[0][0]
    # confidence-weighted mean (matches stored contrib_wmean)
    cwmean=sum(w*conf for _,w,conf in [(x[0],x[1],x[2]) for x in wc])/ (sum(c for _,_,c in wc) or 1)
    # top-2 confidence-weighted mean
    t2=wc[:2]; top2_cw=sum(w*conf for _,w,conf in t2)/(sum(c for _,_,c in t2) or 1)
    t3=wc[:3]; top3_cw=sum(w*conf for _,w,conf in t3)/(sum(c for _,_,c in t3) or 1)
    return {"peak":peak,"cwmean":round(cwmean,4),"top2_cw":round(top2_cw,4),
            "top3_cw":round(top3_cw,4),
            "peak+cwmean":round(0.5*peak+0.5*cwmean,4),
            "peak+top2":round(0.5*peak+0.5*top2_cw,4),
            "max(peak,cwmean)":round(max(peak,cwmean),4)}
rows={}
for gro in glob.glob(f"{ARALIB}/*/gro"):
    rows[os.path.basename(os.path.dirname(gro))]=feats(contribs(gro))
exp=json.load(open("expert_scores.json")); test=load_split("test")
def rho(k,slugs):
    xs=[];ys=[]
    for s in slugs:
        if s in exp and rows.get(s,{}).get(k) is not None: xs.append(rows[s][k]); ys.append(exp[s])
    return spearman(xs,ys),len(xs)
tests=[s for s in rows if s in test]
print("%-18s %12s %12s"%("candidate","all66","TEST"))
for k in ["peak","cwmean","top2_cw","top3_cw","peak+cwmean","peak+top2","max(peak,cwmean)"]:
    a,_=rho(k,list(rows)); t,nt=rho(k,tests)
    print("%-18s %8.3f %8.3f (n=%d)"%(k,a,t,nt))
