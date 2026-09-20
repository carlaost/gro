#!/usr/bin/env python3
"""Cross-model expert panel: re-judge all 66 papers with GPT (codex exec, gpt-5.5) using the
SAME SOTA-grounded metascientist protocol as the Claude panel. Tests whether the metric's
agreement with experts survives a DIFFERENT model family (shared-LLM-bias check)."""
import json, subprocess, os
HERE=os.path.dirname(os.path.abspath(__file__))
SCHEMA=os.path.join(HERE,"score_schema.json")
open(SCHEMA,"w").write(json.dumps({"type":"object","additionalProperties":False,
  "required":["breakthrough_score","tier"],
  "properties":{"breakthrough_score":{"type":"integer","minimum":0,"maximum":100},
                "tier":{"type":"string","enum":["landmark","significant","solid","incremental","non_contribution"]}}}))
payload=json.load(open("codex_panel_input.json"))

PROMPT="""You are a hard-nosed metascience / research-impact analyst. Rate how much of a scientific BREAKTHROUGH the following Alzheimer's-disease paper is — its potential to reshape the field — on 0-100, RELATIVE TO THE STATE OF THE ART shown.

Anchor the scale:
- 90-100 landmark: redefines diagnosis/therapy/mechanism beyond all shown prior art.
- 65-89 significant: a real new finding/method clearly beyond the prior art.
- 40-64 solid: competent advance, close to existing work.
- 15-39 incremental: derivative of the prior art shown.
- 0-14 non-contribution: an annual statistics/facts report, burden re-estimate, or generic review.
Be skeptical: a heavily-cited annual report or burden re-estimate is NOT a breakthrough. Judge advance BEYOND the prior art, not how impressive it sounds alone. Output only the JSON.

PAPER TITLE: {title}
ABSTRACT: {abstract}
KEY CLAIMS: {claims}

PRIOR-ART LANDSCAPE (what existed before; judge advance beyond THIS):
{prior_art}
"""
out={}
existing=json.load(open("codex_panel_scores.json")) if os.path.exists("codex_panel_scores.json") else {}
out.update(existing)
for i,p in enumerate(payload):
    if p["slug"] in out: continue
    prompt=PROMPT.format(title=p["title"],abstract=p["abstract"] or "(title only)",
                         claims="; ".join(p["claims"]) or "(none)", prior_art=p["prior_art"] or "(no prior-art brief)")
    try:
        r=subprocess.run(["codex","exec","-s","read-only","--skip-git-repo-check","--ephemeral",
                          "--output-schema",SCHEMA,"-"],input=prompt,capture_output=True,text=True,timeout=120)
        # last JSON line
        sc=None
        for line in reversed(r.stdout.strip().splitlines()):
            line=line.strip()
            if line.startswith("{") and "breakthrough_score" in line:
                sc=json.loads(line); break
        out[p["slug"]]=sc.get("breakthrough_score") if sc else None
        print(i+1,p["slug"][:34],"->",out[p["slug"]],flush=True)
    except Exception as e:
        out[p["slug"]]=None; print(i+1,p["slug"][:34],"ERR",str(e)[:50],flush=True)
    json.dump(out,open("codex_panel_scores.json","w"),indent=1)
print("done; scored",sum(1 for v in out.values() if v is not None),"/",len(payload))
