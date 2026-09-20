#!/usr/bin/env python3
import json, os, subprocess, glob
S="jscore_schema.json"
open(S,"w").write(json.dumps({"type":"object","additionalProperties":False,"required":["breakthrough_score"],
 "properties":{"breakthrough_score":{"type":"integer","minimum":0,"maximum":100}}}))
P="""Rate how much of a scientific BREAKTHROUGH this paper is (potential to reshape its field) on 0-100, judging ONLY from the paper at publication time with NO hindsight about later citations/influence. Anchor: 90-100 field-redefining; 65-89 significant; 40-64 solid; 15-39 incremental; 0-14 non-contribution. Output only the JSON.

PAPER FULL TEXT:
"""
out=json.load(open("judge_ft_gpt.json")) if os.path.exists("judge_ft_gpt.json") else {}
for i,fp in enumerate(sorted(glob.glob("fulltext/*.txt"))):
    slug=os.path.splitext(os.path.basename(fp))[0]
    if slug in out: continue
    txt=open(fp,errors="ignore").read()[:14000]
    try:
        r=subprocess.run(["codex","exec","-s","read-only","--skip-git-repo-check","--ephemeral","--output-schema",S,"-"],
                         input=P+txt,capture_output=True,text=True,timeout=150)
        sc=None
        for line in reversed(r.stdout.strip().splitlines()):
            if line.strip().startswith("{") and "breakthrough_score" in line: sc=json.loads(line.strip())["breakthrough_score"]; break
        out[slug]=sc; print(i+1,slug,"->",sc,flush=True)
    except Exception as e: out[slug]=None; print(i+1,slug,"ERR",str(e)[:30],flush=True)
    json.dump(out,open("judge_ft_gpt.json","w"),indent=1)
print("done")
