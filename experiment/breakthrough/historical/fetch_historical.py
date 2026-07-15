#!/usr/bin/env python3
"""Historical AD corpus (2004-2010), fixed: tight AD relevance + stratified across the
impact distribution (not top-cited-only). Ground truth (disruption) computed later."""
import json, subprocess, os, time
HERE=os.path.dirname(os.path.abspath(__file__)); MAILTO="carla@positron.vc"
def get(u):
    try: return json.loads(subprocess.run(["curl","-s",u],capture_output=True,text=True,timeout=60).stdout)
    except Exception: return None
def deinv(inv):
    if not inv: return ""
    n=max((i for idxs in inv.values() for i in idxs),default=-1)+1
    t=[""]*n
    for w,idxs in inv.items():
        for i in idxs:
            if i<n: t[i]=w
    return " ".join(t)
# TIGHT relevance: title/abstract must be about Alzheimer's; plus the AD concept.
base=("https://api.openalex.org/works?filter=title_and_abstract.search:alzheimer,"
      "concepts.id:C2779134260,from_publication_date:2004-01-01,to_publication_date:2010-12-31,"
      "type:article,has_abstract:true")
allw=[]
for page in range(1,16):  # up to 3000 ranked by citations
    d=get(f"{base}&per_page=200&page={page}&sort=cited_by_count:desc&mailto={MAILTO}")
    if not d or not d.get("results"): break
    allw+=d["results"]
    if len(d["results"])<200: break
    time.sleep(0.25)
print("relevant AD 2004-2010 papers ranked:",len(allw))
# stratified sample across the citation-rank distribution: every k-th => spans landmarks..ordinary
N=72
k=max(1,len(allw)//N)
samp=allw[::k][:N]
out=[]
for w in samp:
    out.append({"id":w["id"],"doi":w.get("doi"),"title":w.get("title"),
                "year":w.get("publication_year"),
                "abstract":deinv(w.get("abstract_inverted_index"))[:2500],
                "cited_by_count":w.get("cited_by_count"),
                "referenced_works":w.get("referenced_works") or []})
json.dump(out,open(os.path.join(HERE,"corpus.json"),"w"),indent=1)
cs=sorted(x["cited_by_count"] for x in out)
print("sampled %d | citation range %d..%d median %d"%(len(out),cs[0],cs[-1],cs[len(cs)//2]))
from collections import Counter
print("years:",dict(sorted(Counter(x['year'] for x in out).items())))
print("sample (spanning impact):")
for x in sorted(out,key=lambda z:-z['cited_by_count'])[::12]:
    print("  %6d  %s"%(x['cited_by_count'],(x['title'] or '')[:66]))
