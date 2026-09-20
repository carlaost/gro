#!/usr/bin/env python3
"""Ground truth = mature disruption (Funk-Owen-Smith style) from OpenAlex, no LLM.
For focal F (refs R_F known), fetch its citers within a 5-yr window with their referenced_works
inline (select=referenced_works, paged). A citer that also cites >=1 of R_F = consolidating (i);
one that cites F but none of R_F = disrupting (j). mDI = (j - i)/(i + j) in [-1,1];
high = the field built on F while dropping its predecessors = a step-change."""
import json, subprocess, os, time
HERE=os.path.dirname(os.path.abspath(__file__)); MAILTO="carla@positron.vc"
def get(u):
    try: return json.loads(subprocess.run(["curl","-s",u],capture_output=True,text=True,timeout=60).stdout)
    except Exception: return None
corpus=json.load(open("corpus.json"))
out={}
for n,p in enumerate(corpus):
    fid=p["id"].split("/")[-1]; RF=set(p["referenced_works"]); yr=p["year"] or 2007
    if not RF:
        out[p["id"]]={"mDI":None,"n_citers":0,"note":"no refs"}; continue
    end=f"{yr+5}-12-31"
    i=j=0; page=1
    while page<=3:  # cap 600 citers
        d=get(f"https://api.openalex.org/works?filter=cites:{fid},to_publication_date:{end}"
              f"&select=referenced_works&per_page=200&page={page}&mailto={MAILTO}")
        if not d or not d.get("results"): break
        for c in d["results"]:
            cr=set(c.get("referenced_works") or [])
            if cr & RF: i+=1
            else: j+=1
        if len(d["results"])<200: break
        page+=1; time.sleep(0.15)
    tot=i+j
    out[p["id"]]={"mDI": round((j-i)/tot,4) if tot else None, "n_citers":tot,
                  "i_consolidating":i,"j_disrupting":j,"cited_total":p["cited_by_count"],
                  "title":p["title"],"year":yr}
    print(n+1,"%5d cit  mDI=%s  %s"%(tot,out[p['id']]['mDI'],(p['title'] or '')[:44]),flush=True)
    json.dump(out,open("disruption.json","w"),indent=1)
print("done")
