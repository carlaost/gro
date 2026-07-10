#!/usr/bin/env python3
"""Standardized `overlap` per the SPEC L8 shared definition: computed the SAME way for every
paper by a deterministic OpenAlex measure (bibliographic-coupling Jaccard), NOT per-agent LLM.

For each paper P with resolved neighbors N (from sota_anchor.yaml -> refs.yaml DOIs):
  overlap(P,N) = |refs(P) ∩ refs(N)| / |refs(P) ∪ refs(N)|   (Jaccard of OpenAlex referenced_works)
Emit min/mean/max overlap + resolvability (= fraction of neighbors that resolved in OpenAlex).
Writes overlap_openalex.json {slug: {min,mean,max,n_neighbors,resolvability}} + adds fields to a
copy the metric harness can read.
"""
import glob, json, os, subprocess, time, yaml

ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"
HERE = os.path.dirname(os.path.abspath(__file__))
MAILTO = "carla@positron.vc"   # OpenAlex polite pool
_cache = {}

def oa_refs(oaid_or_doi):
    """Return set of referenced_works OpenAlex ids for a work, cached."""
    key = oaid_or_doi
    if key in _cache:
        return _cache[key]
    sel = "select=referenced_works"
    if oaid_or_doi.startswith("http") or oaid_or_doi.startswith("W"):
        wid = oaid_or_doi.split("/")[-1]
        url = f"https://api.openalex.org/works/{wid}?{sel}&mailto={MAILTO}"
    else:
        url = f"https://api.openalex.org/works/doi:{oaid_or_doi}?{sel}&mailto={MAILTO}"
    try:
        out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30).stdout
        d = json.loads(out)
        refs = set(d.get("referenced_works") or [])
    except Exception:
        refs = set()
    _cache[key] = refs
    return refs

def paper_doi(slug):
    p = f"{ARALIB}/{slug}/PAPER.md"
    if os.path.exists(p):
        fm = open(p).read().split("---")
        if len(fm) > 1:
            d = yaml.safe_load(fm[1]) or {}
            if isinstance(d, dict) and d.get("doi"):
                return d["doi"]
    t = f"{ARALIB}/{slug}/gro/temporal.yaml"
    if os.path.exists(t):
        return (yaml.safe_load(open(t)) or {}).get("doi")
    return None

def ref_doi_map(gro):
    r = yaml.safe_load(open(os.path.join(gro, "refs.yaml")))
    rl = r.get("refs") if isinstance(r, dict) else r
    m = {}
    for x in (rl or []):
        if isinstance(x, dict) and x.get("external_id"):
            eid = str(x["external_id"])
            if eid.startswith("10."):
                m[x["id"]] = eid
    return m

def jaccard(a, b):
    if not a or not b:
        return None
    return len(a & b) / len(a | b)

def main():
    out = {}
    for gro in sorted(glob.glob(f"{ARALIB}/*/gro")):
        slug = os.path.basename(os.path.dirname(gro))
        doi = paper_doi(slug)
        anchorp = os.path.join(gro, "sota_anchor.yaml")
        if not doi or not os.path.exists(anchorp):
            out[slug] = {"min": None, "mean": None, "max": None, "n_neighbors": 0, "resolvability": None}
            continue
        prefs = oa_refs(doi)
        neigh = (yaml.safe_load(open(anchorp)) or {}).get("neighborhood") or []
        rmap = ref_doi_map(gro)
        ovs = []
        n_tried = n_res = 0
        for nb in neigh:
            rid = nb.get("ref")
            ndoi = rmap.get(rid)
            if not ndoi:
                n_tried += 1
                continue
            n_tried += 1
            nrefs = oa_refs(ndoi)
            if nrefs:
                n_res += 1
                j = jaccard(prefs, nrefs)
                if j is not None:
                    ovs.append(round(j, 4))
        resolvability = round(n_res / n_tried, 4) if n_tried else None
        out[slug] = {
            "min": round(min(ovs), 4) if ovs else None,
            "mean": round(sum(ovs) / len(ovs), 4) if ovs else None,
            "max": round(max(ovs), 4) if ovs else None,
            "n_neighbors": len(ovs), "resolvability": resolvability,
        }
        print(f"{slug[:38]:38s} n={len(ovs)} min={out[slug]['min']} mean={out[slug]['mean']} max={out[slug]['max']} resv={resolvability}")
    json.dump(out, open(os.path.join(HERE, "overlap_openalex.json"), "w"), indent=1)
    have = sum(1 for v in out.values() if v["mean"] is not None)
    print(f"\nwrote overlap_openalex.json — {have}/{len(out)} papers with a standardized overlap")

if __name__ == "__main__":
    main()
