#!/usr/bin/env python3
"""Historical validation: publication-time metric vs mature disruption. Reproduces §10."""
import json, math
def spearman(x,y):
    def rank(v):
        o=sorted(range(len(v)),key=lambda i:v[i]);r=[0]*len(v);i=0
        while i<len(v):
            j=i
            while j+1<len(v) and v[o[j+1]]==v[o[i]]:j+=1
            a=(i+j)/2+1
            for k in range(i,j+1):r[o[k]]=a
            i=j+1
        return r
    rx,ry=rank(x),rank(y);n=len(x);mx=sum(rx)/n;my=sum(ry)/n
    c=sum((rx[i]-mx)*(ry[i]-my) for i in range(n));sx=math.sqrt(sum((v-mx)**2 for v in rx));sy=math.sqrt(sum((v-my)**2 for v in ry))
    return round(c/(sx*sy),3) if sx and sy else 0
metric=json.load(open('metric_pubtime.json'));disr=json.load(open('disruption.json'))
for mc in (10,30,50):
    R=[(metric[p]['metric'],disr[p]['mDI']) for p in metric
       if metric[p]['metric'] is not None and disr.get(p,{}).get('mDI') is not None and disr[p]['n_citers']>=mc]
    print('citers>=%d n=%d  metric~mDI rho=%+.3f'%(mc,len(R),spearman([r[0] for r in R],[r[1] for r in R])))
if __name__=='__main__': pass
