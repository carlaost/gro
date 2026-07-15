#!/usr/bin/env python3
"""Build the metric with GPT instead of Claude: GPT types each paper's contributions
(same closed taxonomy the Claude compiler used), so we get a GPT-authored contrib metric.
Enables the 2x2: {metric model} x {panel model} -> cleanly separates shared-method bias
from real transferable signal."""
import json, subprocess, os
HERE=os.path.dirname(os.path.abspath(__file__))
SCHEMA=os.path.join(HERE,"typing_schema.json")
open(SCHEMA,"w").write(json.dumps({"type":"object","additionalProperties":False,"required":["contributions"],
 "properties":{"contributions":{"type":"array","items":{"type":"object","additionalProperties":False,
   "required":["type","confidence"],
   "properties":{"type":{"type":"string","enum":["new_paradigm","new_method","new_finding","refutation","synthesis","incremental_improvement","replication"]},
                 "confidence":{"type":"number","minimum":0,"maximum":1}}}}}}))
payload=json.load(open("codex_panel_input.json"))
PROMPT="""You are compiling a research paper's CONTRIBUTIONS for a knowledge base. List each DISTINCT scientific contribution the paper makes, and classify each with its novelty TYPE from this closed taxonomy and a confidence in [0,1]:
new_paradigm (reframes the field) > new_method > new_finding > refutation > synthesis > incremental_improvement > replication.
Judge only from the paper's own text below; do not reward quantity. Output only the JSON.

TITLE: {title}
ABSTRACT: {abstract}
KEY CLAIMS: {claims}"""
out=json.load(open("gpt_typing.json")) if os.path.exists("gpt_typing.json") else {}
for i,p in enumerate(payload):
    if p["slug"] in out: continue
    pr=PROMPT.format(title=p["title"],abstract=p["abstract"] or "(title only)",claims="; ".join(p["claims"]) or "(none)")
    try:
        r=subprocess.run(["codex","exec","-s","read-only","--skip-git-repo-check","--ephemeral","--output-schema",SCHEMA,"-"],
                         input=pr,capture_output=True,text=True,timeout=120)
        obj=None
        for line in reversed(r.stdout.strip().splitlines()):
            line=line.strip()
            if line.startswith("{") and "contributions" in line: obj=json.loads(line); break
        out[p["slug"]]=obj.get("contributions") if obj else None
        print(i+1,p["slug"][:32],"->",len(out[p["slug"]]) if out[p["slug"]] else "ERR","contribs",flush=True)
    except Exception as e:
        out[p["slug"]]=None; print(i+1,"ERR",str(e)[:40],flush=True)
    json.dump(out,open("gpt_typing.json","w"),indent=1)
print("done")
