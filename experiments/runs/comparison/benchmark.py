#!/usr/bin/env python3
"""Substrate benchmark: the SAME metric logic computed over two data shapes —
the raw ARA prose (parsed) vs the GRO typed sidecars (read) — on the four
constructs that are expressible on both. Plus a performance benchmark
(coverage, agreement, fidelity-to-external-truth, compute time)."""
import json, os, re, time, glob
import yaml

LIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"
V4 = "/Users/carlaostmann/code/dasmodel/research/metrics/v4-gro"
SLUGS = ["che26-diagnostic-performance-of-plasma-p-tau217","val25-blood-biomarkers-of-alzheimer-s-disease",
 "han26-tau-pathological-activity-in-plasma-before","zim25-donanemab-in-early-symptomatic-alzheimer-s",
 "jes26-efficacy-and-safety-of-donanemab-in","tit26-automated-high-throughput-quantification-of-plasma",
 "gau25-single-nucleus-and-spatial-transcriptomic-profiling","zho25-microglia-networks-within-the-tapestry-of",
 "aki26-molecular-signatures-of-resilience-to-alzheimer","cum26-alzheimer-s-disease-drug-development-pipeline",
 "xu25-epidemiological-and-sociodemographic-transitions-in-the","ard25-response-of-spatially-defined-microglia-states"]

NUM = re.compile(r"[-−–]?\d+(?:[.,]\d+)?")
def nums(s):
    return [x.replace("−","-").replace("–","-").replace(",","") for x in NUM.findall(s or "")]
def num_in_quote(value_str, quote):
    """rounding-aware: does the claim's stated number appear in its quote?"""
    vs = nums(value_str); qs = set(nums(quote))
    if not vs: return None  # no numeric to check
    for v in vs:
        if v in qs: return True
        try:
            fv = float(v)
            for q in qs:
                try:
                    if abs(float(q)-fv) <= 0.5*10**(-(len(v.split('.')[1]) if '.' in v else 0)): return True
                except: pass
        except: pass
    return False

# ---------- PROSE parsers (raw ARA shape) ----------
def parse_claims_prose(slug):
    p = f"{LIB}/{slug}/logic/claims.md"
    if not os.path.exists(p): return None
    txt = open(p).read()
    blocks = re.split(r"^##\s+C\d+", txt, flags=re.M)[1:]
    ids = re.findall(r"^##\s+(C\d+)", txt, flags=re.M)
    claims = []
    for cid, b in zip(ids, blocks):
        proof = re.search(r"\*\*Proof\*\*:\s*\[([^\]]*)\]", b)
        eids = re.findall(r"E\d+", proof.group(1)) if proof else []
        srcs = []
        for m in re.finditer(r"^\s*-\s+(.*?)\s*←\s*(.*?)(?:«(.*?)»)?\s*(?:\[(input|result)\])?\s*$", b, flags=re.M):
            val, ref, quote, role = m.group(1), m.group(2), m.group(3) or "", m.group(4) or ""
            if "←" in (val or ""):  # guard
                continue
            srcs.append({"value": val.strip("` "), "quote": quote, "role": role})
        claims.append({"id": cid, "proof_eids": eids, "sources": srcs})
    return claims

def parse_experiments_eids(slug):
    p = f"{LIB}/{slug}/logic/experiments.md"
    if not os.path.exists(p): return None
    return set(re.findall(r"^##\s+(E\d+)", open(p).read(), flags=re.M))

def parse_refs_prose(slug):
    p = f"{LIB}/{slug}/logic/related_work.md"
    if not os.path.exists(p): return None
    txt = open(p).read()
    blocks = re.split(r"^##\s+RW\d+", txt, flags=re.M)[1:]
    if not blocks:  # some ARAs list refs differently; fall back to counting DOI-bearing bullets
        dois = re.findall(r"10\.\d{4,}/\S+", txt)
        return {"n": max(len(dois), len(re.findall(r"^##\s", txt, flags=re.M))), "resolvable": len(set(dois))}
    n = len(blocks); res = 0
    for b in blocks:
        if re.search(r"10\.\d{4,}/\S+|PMID[:\s]*\d+|\bNCT\d{8}\b", b): res += 1
    return {"n": n, "resolvable": res}

# ---------- TYPED parsers (GRO sidecar shape) ----------
def load_yaml(p):
    return yaml.safe_load(open(p)) if os.path.exists(p) else None
def typed(slug):
    g = f"{LIB}/{slug}/gro"
    if not os.path.isdir(g): return None
    q = load_yaml(f"{g}/quantities.yaml") or {}
    c = load_yaml(f"{g}/claims_typed.yaml") or {}
    r = load_yaml(f"{g}/refs.yaml") or {}
    return {"quantities": q.get("quantities",[]), "claims": c.get("claims",[]), "refs": r.get("refs",[])}

# ---------- the four constructs, computed identically per shape ----------
def m_quote_consistency_prose(cl):
    tot=ok=0
    for c in cl:
        for s in c["sources"]:
            r = num_in_quote(s["value"], s["quote"])
            if r is None: continue
            tot+=1; ok+= 1 if r else 0
    return (ok/tot) if tot else None, tot
def m_quote_consistency_typed(t):
    tot=ok=0
    for q in t["quantities"]:
        r = num_in_quote(str(q.get("value","")), str(q.get("quote","")))
        if r is None: continue
        tot+=1; ok+= 1 if r else 0
    return (ok/tot) if tot else None, tot

def m_entail_prose(cl):
    if not cl: return None,0
    ok=0
    for c in cl:
        has_proof = len(c["proof_eids"])>0
        has_result = any(s["role"]=="result" for s in c["sources"])
        ok+= 1 if (has_proof and has_result) else 0
    return ok/len(cl), len(cl)
def m_entail_typed(t):
    cl=t["claims"]
    if not cl: return None,0
    qrole={q.get("id"):q.get("role") for q in t["quantities"]}
    ok=0
    for c in cl:
        has_proof=len(c.get("proof_refs") or [])>0
        has_result=any(qrole.get(qid)=="result" for qid in (c.get("quantity_refs") or []))
        ok+= 1 if (has_proof and has_result) else 0
    return ok/len(cl), len(cl)

def m_refres_prose(slug):
    r=parse_refs_prose(slug)
    if not r or not r["n"]: return None,0
    return r["resolvable"]/r["n"], r["n"]
def m_refres_typed(t):
    refs=t["refs"]
    if not refs: return None,0
    ok=sum(1 for x in refs if x.get("resolvable") is True)
    return ok/len(refs), len(refs)

def m_brokenref_prose(cl, eids):
    if cl is None or eids is None: return None,0
    broken=0; total=0
    for c in cl:
        for e in c["proof_eids"]:
            total+=1; broken+= 0 if e in eids else 1
    return broken, total
def m_brokenref_typed(t, eids):
    if eids is None: return None,0
    broken=0; total=0
    for c in t["claims"]:
        for e in (c.get("proof_refs") or []):
            total+=1; broken+= 0 if e in eids else 1
    return broken, total

# ---------- run + time ----------
truth={}
for f in glob.glob(f"{V4}/external/*.json"):
    d=json.load(open(f)); rr=d.get("reference_resolution") or {}
    truth[d.get("slug")] = rr.get("observed_rate")

rows=[]; timing={"prose":{}, "typed":{}}
CONSTRUCTS=["quote_consistency","entailment_precondition","reference_resolvability","broken_ref_rate"]
for c in CONSTRUCTS: timing["prose"][c]=0.0; timing["typed"][c]=0.0

for slug in SLUGS:
    cl=parse_claims_prose(slug); eids=parse_experiments_eids(slug); t=typed(slug)
    row={"slug":slug.split("-")[0],"prose":{},"typed":{},"truth":{}}
    # quote consistency
    t0=time.perf_counter(); vp=m_quote_consistency_prose(cl) if cl else (None,0); timing["prose"]["quote_consistency"]+=time.perf_counter()-t0
    t0=time.perf_counter(); vt=m_quote_consistency_typed(t) if t else (None,0); timing["typed"]["quote_consistency"]+=time.perf_counter()-t0
    row["prose"]["quote_consistency"]={"value":vp[0],"n":vp[1]}; row["typed"]["quote_consistency"]={"value":vt[0],"n":vt[1]}
    # entailment
    t0=time.perf_counter(); vp=m_entail_prose(cl) if cl else (None,0); timing["prose"]["entailment_precondition"]+=time.perf_counter()-t0
    t0=time.perf_counter(); vt=m_entail_typed(t) if t else (None,0); timing["typed"]["entailment_precondition"]+=time.perf_counter()-t0
    row["prose"]["entailment_precondition"]={"value":vp[0],"n":vp[1]}; row["typed"]["entailment_precondition"]={"value":vt[0],"n":vt[1]}
    # ref resolvability
    t0=time.perf_counter(); vp=m_refres_prose(slug); timing["prose"]["reference_resolvability"]+=time.perf_counter()-t0
    t0=time.perf_counter(); vt=m_refres_typed(t) if t else (None,0); timing["typed"]["reference_resolvability"]+=time.perf_counter()-t0
    row["prose"]["reference_resolvability"]={"value":vp[0],"n":vp[1]}; row["typed"]["reference_resolvability"]={"value":vt[0],"n":vt[1]}
    row["truth"]["reference_resolvability"]=truth.get(slug)
    # broken ref
    t0=time.perf_counter(); vp=m_brokenref_prose(cl,eids); timing["prose"]["broken_ref_rate"]+=time.perf_counter()-t0
    t0=time.perf_counter(); vt=m_brokenref_typed(t,eids) if t else (None,0); timing["typed"]["broken_ref_rate"]+=time.perf_counter()-t0
    row["prose"]["broken_ref_rate"]={"broken":vp[0],"n":vp[1]}; row["typed"]["broken_ref_rate"]={"broken":vt[0],"n":vt[1]}
    rows.append(row)

# ---------- aggregate performance benchmark ----------
def coverage(shape, con, key="value"):
    return sum(1 for r in rows if r[shape][con].get(key) is not None)/len(rows)
bench={"constructs":{}, "timing_ms":{"prose":{k:round(v*1000,2) for k,v in timing["prose"].items()},
                                     "typed":{k:round(v*1000,2) for k,v in timing["typed"].items()}}}
for con in ["quote_consistency","entailment_precondition","reference_resolvability"]:
    prose_cov=coverage("prose",con); typed_cov=coverage("typed",con)
    # agreement where both computed
    diffs=[abs(r["prose"][con]["value"]-r["typed"][con]["value"]) for r in rows
           if r["prose"][con]["value"] is not None and r["typed"][con]["value"] is not None]
    bench["constructs"][con]={"prose_coverage":round(prose_cov,3),"typed_coverage":round(typed_cov,3),
        "mean_abs_prose_vs_typed": round(sum(diffs)/len(diffs),3) if diffs else None, "n_both": len(diffs)}
# ref resolvability fidelity to truth
for shape in ["prose","typed"]:
    errs=[abs(r[shape]["reference_resolvability"]["value"]-r["truth"]["reference_resolvability"])
          for r in rows if r[shape]["reference_resolvability"]["value"] is not None and r["truth"]["reference_resolvability"] is not None]
    bench.setdefault("reference_resolvability_fidelity",{})[shape+"_MAE_vs_pubmed"]=round(sum(errs)/len(errs),3) if errs else None
    bench["reference_resolvability_fidelity"]["n"]=len(errs)
# broken-ref
for shape in ["prose","typed"]:
    bench.setdefault("broken_ref_total",{})[shape]=sum(r[shape]["broken_ref_rate"]["broken"] for r in rows if r[shape]["broken_ref_rate"]["broken"] is not None)

out={"per_ara":rows,"benchmark":bench,"note":"Same metric logic over two shapes: prose = parsed from raw ARA (claims.md/related_work.md/experiments.md); typed = read from gro/*.yaml sidecars. Reference-resolvability fidelity is measured against the live-PubMed observed rate (6 ARAs)."}
json.dump(out, open(f"{V4}/benchmark.json","w"), indent=1)
print("== SUBSTRATE BENCHMARK ==")
print("coverage (fraction of 12 ARAs computable):")
for con,d in bench["constructs"].items(): print(f"  {con:28s} prose={d['prose_coverage']:.2f}  typed={d['typed_coverage']:.2f}  |prose-typed| mean={d['mean_abs_prose_vs_typed']} (n={d['n_both']})")
print("ref-resolvability MAE vs PubMed truth:", bench["reference_resolvability_fidelity"])
print("broken-ref total:", bench["broken_ref_total"])
print("compute time (ms, all 12 ARAs):")
for con in CONSTRUCTS: print(f"  {con:28s} prose={bench['timing_ms']['prose'][con]:8.2f}  typed={bench['timing_ms']['typed'][con]:8.2f}")
