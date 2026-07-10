#!/usr/bin/env python3
"""Deterministic genre + structural metadata for all 66 papers from OpenAlex (by DOI).
No LLM — a reproducible fetch, the 'shared definition' a metric can condition on.
Emits openalex_meta.json: {slug: {type, n_referenced, cited_by, top_topic_score, genre}}.
genre heuristic (v0): review if OpenAlex type=='review'; surveillance_report if type=='article'
AND n_referenced very high (>=200, a compilation tell) OR top_topic_score>=0.97 (generic);
else primary_research.
"""
import glob, json, os, subprocess, yaml
ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"

def doi_of(slug):
    p = f"{ARALIB}/{slug}/PAPER.md"
    if os.path.exists(p):
        fm = open(p).read().split("---")
        if len(fm) > 1:
            d = yaml.safe_load(fm[1]) or {}
            if d.get("doi"): return d["doi"]
    t = f"{ARALIB}/{slug}/gro/temporal.yaml"
    if os.path.exists(t):
        return (yaml.safe_load(open(t)) or {}).get("doi")
    return None

def fetch(doi):
    try:
        out = subprocess.run(["curl","-s",f"https://api.openalex.org/works/doi:{doi}"],
                             capture_output=True,text=True,timeout=30).stdout
        return json.loads(out)
    except Exception:
        return None

def genre(typ, nref, topscore):
    if typ == "review": return "review"
    if typ in ("paratext","editorial","letter"): return "other"
    if typ == "article" and ((nref or 0) >= 200 or (topscore or 0) >= 0.97):
        return "surveillance_report"
    return "primary_research"

def main():
    out = {}
    for gro in sorted(glob.glob(f"{ARALIB}/*/gro")):
        slug = os.path.basename(os.path.dirname(gro))
        doi = doi_of(slug)
        if not doi:
            out[slug] = {"doi": None, "genre": None}; continue
        d = fetch(doi)
        if not d:
            out[slug] = {"doi": doi, "genre": None}; continue
        typ = d.get("type"); nref = len(d.get("referenced_works") or [])
        tops = d.get("topics") or []
        topscore = tops[0].get("score") if tops else None
        out[slug] = {"doi": doi, "type": typ, "n_referenced": nref,
                     "cited_by": d.get("cited_by_count"), "top_topic_score": topscore,
                     "genre": genre(typ, nref, topscore)}
    json.dump(out, open("openalex_meta.json","w"), indent=1)
    from collections import Counter
    print("fetched", len(out), "papers")
    print("genre distribution:", dict(Counter(v.get("genre") for v in out.values())))

if __name__ == "__main__":
    main()
