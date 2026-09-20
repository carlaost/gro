#!/usr/bin/env python3
"""Rebuild the prior-art neighborhood for each paper DIRECTLY from OpenAlex (not from the
paper's sparse cited refs), then compute the standardized `overlap` per SPEC L8.

Method (fully deterministic, no LLM):
  1. Resolve the paper in OpenAlex by DOI -> id, publication_year, concept-score vector,
     and related_works (OpenAlex-precomputed concept neighbors).
  2. Neighborhood = related_works published <= the paper's year (PRIOR art only).
  3. overlap(P, N) = cosine of concept-score vectors (fraction of the paper's conceptual
     content shared with that prior work). Fallback to topics if concepts absent.
  4. Emit min/mean/max overlap + resolvability (= prior neighbors resolved / related_works).

Writes overlap_neighborhood.json {slug: {min,mean,max,n_prior,n_related,resolvability}}.
"""
import glob, json, math, os, subprocess, yaml

ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"
HERE = os.path.dirname(os.path.abspath(__file__))
MAILTO = "carla@positron.vc"
_cache = {}

def fetch(wid_or_doi, select):
    key = (wid_or_doi, select)
    if key in _cache:
        return _cache[key]
    if wid_or_doi.startswith("W") or wid_or_doi.startswith("http"):
        w = wid_or_doi.split("/")[-1]
        url = f"https://api.openalex.org/works/{w}?select={select}&mailto={MAILTO}"
    else:
        url = f"https://api.openalex.org/works/doi:{wid_or_doi}?select={select}&mailto={MAILTO}"
    try:
        out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30).stdout
        d = json.loads(out)
    except Exception:
        d = None
    _cache[key] = d
    return d

def cvec(work):
    """concept_id -> score vector; fall back to topics."""
    v = {}
    for c in (work.get("concepts") or []):
        if c.get("id") and c.get("score"):
            v[c["id"]] = float(c["score"])
    if not v:
        for t in (work.get("topics") or []):
            if t.get("id") and t.get("score"):
                v[t["id"]] = float(t["score"])
    return v

def cosine(a, b):
    if not a or not b:
        return None
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(x * x for x in a.values())); nb = math.sqrt(sum(x * x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0

def paper_doi(slug):
    p = f"{ARALIB}/{slug}/PAPER.md"
    if os.path.exists(p):
        fm = open(p).read().split("---")
        if len(fm) > 1:
            d = yaml.safe_load(fm[1]) or {}
            if isinstance(d, dict) and d.get("doi"):
                return d["doi"]
    t = f"{ARALIB}/{slug}/gro/temporal.yaml"
    return (yaml.safe_load(open(t)) or {}).get("doi") if os.path.exists(t) else None

def main():
    out = {}
    for gro in sorted(glob.glob(f"{ARALIB}/*/gro")):
        slug = os.path.basename(os.path.dirname(gro))
        doi = paper_doi(slug)
        if not doi:
            out[slug] = {"min": None, "mean": None, "max": None, "n_prior": 0, "n_related": 0, "resolvability": None}
            continue
        P = fetch(doi, "id,publication_year,concepts,topics,related_works")
        if not P:
            out[slug] = {"min": None, "mean": None, "max": None, "n_prior": 0, "n_related": 0, "resolvability": None}
            continue
        pyear = P.get("publication_year") or 9999
        pv = cvec(P)
        related = P.get("related_works") or []
        ovs = []
        for wid in related:
            N = fetch(wid, "id,publication_year,concepts,topics")
            if not N:
                continue
            if (N.get("publication_year") or 9999) > pyear:
                continue  # prior art only
            c = cosine(pv, cvec(N))
            if c is not None:
                ovs.append(round(c, 4))
        out[slug] = {
            "min": round(min(ovs), 4) if ovs else None,
            "mean": round(sum(ovs) / len(ovs), 4) if ovs else None,
            "max": round(max(ovs), 4) if ovs else None,
            "n_prior": len(ovs), "n_related": len(related),
            "resolvability": round(len(ovs) / len(related), 4) if related else None,
        }
        print(f"{slug[:36]:36s} prior={len(ovs)}/{len(related)} min={out[slug]['min']} mean={out[slug]['mean']} max={out[slug]['max']}", flush=True)
    json.dump(out, open(os.path.join(HERE, "overlap_neighborhood.json"), "w"), indent=1)
    have = sum(1 for v in out.values() if v["mean"] is not None)
    print(f"\nwrote overlap_neighborhood.json — {have}/{len(out)} papers with a standardized overlap")

if __name__ == "__main__":
    main()
