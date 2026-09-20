#!/usr/bin/env python3
"""gro_compile.py — compile a GRO-extended artifact from a structured *facts* JSON
extracted from a paper's full text (e.g. via Undermind `read_pdfs`).

This is the paper-based analogue of `research/paper2gro.py`. paper2gro scaffolds the
GRO sidecars from an ALREADY-compiled ARA directory and marks the semantic parts
`NEEDS_LLM`. This tool instead BUILDS the ARA front-matter + all GRO L8 sidecars
directly from a facts JSON that an LLM produced in a single full-text pass, so the
semantic judgements (claim typing, contribution novelty typing) are already FILLED.

Two-stage loop (mirrors the published `compiler` skill: LLM front, deterministic build):
  1. EXTRACT  (LLM / agent): run `extraction_prompt.md` over the PDF via read_pdfs;
     the model returns a facts JSON conforming to `schema.json`.
  2. COMPILE  (this script, deterministic): wire IDs, cross-refs, delta arithmetic,
     and emit PAPER.md + gro/*.yaml. Honest NEEDS_* markers remain ONLY where even the
     full text cannot supply the value:
       - external prior-work baselines the paper does not report  -> NEEDS_FETCH
       - the SOTA precedence neighborhood (needs a citation graph) -> NEEDS_RESOLVER

Grounding model: every claim wires to quantities (quantity_refs); every quantity carries
a verbatim `quote` + `source_ref`. That quote IS the evidence anchor — this facts-based
compiler does not build a separate /evidence layer, so `proof_refs` stays empty by design.

Usage:
  python3 gro_compile.py facts/daw20.json --lib ../inner-experience-library
  python3 gro_compile.py --batch facts --lib ../inner-experience-library
  python3 gro_compile.py facts/daw20.json --lib ../inner-experience-library --validate
"""
import argparse, datetime, json, os, re, sys

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml:  python3 -m pip install pyyaml")

ARA_VERSION = "1.0"

# closed contribution taxonomy the significance metric reads (must match research/paper2gro.py
# CONTRIB_TAXONOMY / compute_significance.py NOVELTY_W). The extraction must map its judgement
# onto one of these; anything else is rejected so the artifact stays metric-compatible.
CONTRIB_TAXONOMY = ["new_paradigm", "new_method", "new_finding", "refutation",
                    "synthesis", "incremental_improvement", "replication"]

# map common loose extraction labels onto the closed taxonomy so JSON-mode extraction
# (read_pdfs emitting facts directly) stays metric-compatible without hand-fixing.
CONTRIB_NORMALIZE = {
    "theory": "synthesis", "new_measure": "new_method", "measurement": "new_method",
    "conceptual_distinction": "synthesis", "distinction": "synthesis",
    "first_person_report": "new_finding", "case_report": "new_finding",
    "observation": "new_finding", "definition": "synthesis", "framework": "new_method",
    "review": "synthesis", "meta_analysis": "synthesis", "refute": "refutation",
    "improvement": "incremental_improvement", "extension": "incremental_improvement",
}


def slugify(s, n=6):
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")[:40] or "x"


def dump(path, obj, header=None):
    with open(path, "w") as f:
        if header:
            f.write(header.rstrip() + "\n")
        yaml.safe_dump(obj, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)


def compile_facts(facts, lib_dir, fetch_ts):
    meta = facts["meta"]
    slug = meta["slug"]
    out = os.path.join(lib_dir, slug)
    gro = os.path.join(out, "gro")
    os.makedirs(gro, exist_ok=True)

    # ---- assign deterministic IDs by declaration order ----
    claim_id = {c["key"]: f"C{i+1:02d}" for i, c in enumerate(facts.get("claims", []))}
    q_id = {q["key"]: f"Q{i+1:02d}" for i, q in enumerate(facts.get("quantities", []))}
    ent_id = {}
    for e in facts.get("entities", []):
        ent_id[e["key"]] = e.get("id") or f"EN-{e.get('kind','concept')}-{slugify(e['term'])}"
    xq_id = {x["key"]: f"XQ{i+1:02d}" for i, x in enumerate(facts.get("external_baselines", []))}
    ref_id = {r["key"]: f"R{i+1:02d}" for i, r in enumerate(facts.get("refs", []))}

    # ---- quantities.yaml + reverse map claim->quantities ----
    claim_qrefs = {k: [] for k in claim_id}
    quantities = []
    for q in facts.get("quantities", []):
        crefs = [claim_id[k] for k in q.get("claim_keys", []) if k in claim_id]
        for k in q.get("claim_keys", []):
            if k in claim_qrefs:
                claim_qrefs[k].append(q_id[q["key"]])
        quantities.append({
            "id": q_id[q["key"]], "value": q["value"], "unit": q.get("unit", "none"),
            "comparator": q.get("comparator", "none"),
            "ci_low": q.get("ci_low", "not_specified"), "ci_high": q.get("ci_high", "not_specified"),
            "role": q.get("role", "result"), "source_ref": q.get("source_ref", "not_specified"),
            "quote": q.get("quote", ""), "claim_refs": crefs,
        })
    dump(os.path.join(gro, "quantities.yaml"), {"quantities": quantities})

    # ---- entities.yaml ----
    entities = [{"id": ent_id[e["key"]], "term": e["term"], "kind": e.get("kind", "concept"),
                 "xref": e.get("xref", "not_specified")} for e in facts.get("entities", [])]
    dump(os.path.join(gro, "entities.yaml"), {"entities": entities})

    # ---- claims_typed.yaml ----
    claims = []
    for c in facts.get("claims", []):
        claims.append({
            "id": claim_id[c["key"]], "claim_type": c["claim_type"], "polarity": c.get("polarity", "positive"),
            "logical_form": c.get("logical_form", c.get("statement", "")),
            "population_n": c.get("population_n", "not_specified"),
            "population_scope": c.get("population_scope", "sample"),
            "quantity_refs": claim_qrefs.get(c["key"], []),
            "concept_refs": [ent_id[k] for k in c.get("concept_keys", []) if k in ent_id],
            "proof_refs": [],  # grounding is via quantity quotes; no separate /evidence layer
            "depends_on": [claim_id[k] for k in c.get("depends_on_keys", []) if k in claim_id],
        })
    dump(os.path.join(gro, "claims_typed.yaml"), {"claims": claims})

    # ---- contributions.yaml (CT##, realized_in wired -> anti-puffery lock) ----
    contribs = []
    for i, ct in enumerate(facts.get("contributions", [])):
        realized = [claim_id[k] for k in ct.get("realized_in", []) if k in claim_id]
        atype = ct.get("assessed_type", "new_finding")
        atype = CONTRIB_NORMALIZE.get(atype, atype)  # map loose labels -> taxonomy
        contribs.append({
            "id": f"CT{i+1:02d}", "author_framed_type": ct.get("author_framed_type", "not_specified"),
            "compiler_assessed_type": {"primary": atype,
                                        "confidence": ct.get("confidence", 0.6)},
            "typing_rationale": ct.get("typing_rationale", ""),
            "typing_divergence": ct.get("typing_divergence", "none"),
            "adjudication": "not_triggered",
            "realized_in": realized or "NEEDS_LLM: no realizing claim wired",
        })
    dump(os.path.join(gro, "contributions.yaml"), {"contributions": contribs})

    # ---- external_quantities.yaml (Tier B; NEEDS_FETCH if none reported) ----
    xqs = []
    for x in facts.get("external_baselines", []):
        xqs.append({
            "id": xq_id[x["key"]], "value": x["value"], "unit": x.get("unit", "none"),
            "description": x.get("description", ""),
            "source_anchor": {"external_id": x.get("external_id", "NEEDS_FETCH"),
                              "fetch_timestamp": x.get("fetch_timestamp", fetch_ts)},
            "baseline_verification": x.get("verification", "self_reported"),
        })
    xq_header = None if xqs else ("# NEEDS_FETCH: no off-paper prior-work baselines were reported in the\n"
                                  "# full text. Populate via an external fetch (Tier B) to enable deltas.")
    dump(os.path.join(gro, "external_quantities.yaml"), {"external_quantities": xqs}, header=xq_header)

    # ---- delta_ledger.yaml (deterministic arithmetic when a baseline is paired) ----
    deltas = []
    for i, d in enumerate(facts.get("deltas", [])):
        cq = q_id.get(d.get("claimed"))
        bx = xq_id.get(d.get("baseline")) if d.get("baseline") else None
        rec = {"id": f"D{i+1:02d}", "claimed_value": cq or "not_specified",
               "baseline_value": bx or "not_specified"}
        if cq and bx:
            cv = next(q["value"] for q in facts["quantities"] if q_id[q["key"]] == cq)
            bv = next(x["value"] for x in facts["external_baselines"] if xq_id[x["key"]] == bx)
            try:
                rec["delta_status"] = "quantified"
                rec["absolute_delta"] = round(cv - bv, 3)
                rec["relative_delta"] = round((cv - bv) / bv, 3) if bv else "undefined"
                rec["baseline_verification"] = "source_verified"
            except TypeError:
                rec["delta_status"] = "claimed_unresolved"
        else:
            rec["delta_status"] = "claimed_unresolved"
            rec["absolute_delta"] = "not_specified"
            rec["relative_delta"] = "not_specified"
            rec["baseline_verification"] = "self_reported"
        rec["note"] = d.get("note", "")
        deltas.append(rec)
    d_header = None if deltas else "# No claimed-vs-external-baseline deltas declared (many first-report / phenomenological papers have none)."
    dump(os.path.join(gro, "delta_ledger.yaml"), {"deltas": deltas}, header=d_header)

    # ---- refs.yaml ----
    refs = [{"id": ref_id[r["key"]], "raw": r["raw"], "external_id": r.get("external_id", "not_specified"),
             "resolvable": bool(r.get("external_id"))} for r in facts.get("refs", [])]
    dump(os.path.join(gro, "refs.yaml"), {"refs": refs})

    # ---- sota_anchor.yaml (undermind_resolved if a neighborhood is supplied, else NEEDS_RESOLVER) ----
    sota = facts.get("sota", {})
    year = int(meta["year"])
    nbhd = []
    for n in sota.get("neighborhood", []):
        ref = n.get("ref")
        nbhd.append({**n, "ref": ref_id.get(ref, ref)})  # map facts ref-key -> R##
    default_prov = "undermind_resolved" if nbhd else "compiler_estimated"
    sota_obj = {
        "precedence_date": sota.get("precedence_date", f"{year}-01-01"),
        "cutoff_date": f"{year}-01-01",
        "provenance": sota.get("provenance", default_prov),
        "neighborhood": nbhd,
        "used_undermind": sota.get("used_undermind", bool(nbhd)),
        "resolver_notes": sota.get("resolver_notes",
            ("Precedence neighborhood resolved via Undermind reference/citation search: the paper's "
             "key priors were scored for finding-level overlap against its core contribution.") if nbhd else
            ("NEEDS_RESOLVER: precedence neighborhood not resolved. Requires a citation-graph pass "
             "(Undermind reference/citation search or OpenAlex) to score overlap vs. topical prior art. "
             "The significance metric correctly penalizes this unresolved state.")),
    }
    dump(os.path.join(gro, "sota_anchor.yaml"), sota_obj)

    # ---- genre.yaml ----
    g = facts.get("genre", {})
    dump(os.path.join(gro, "genre.yaml"), {
        "paper_type": g.get("paper_type", "not_specified"),
        "expected_slots": g.get("expected_slots", ["claims", "quantities", "entities"]),
        "present_slots": g.get("present_slots", ["claims", "quantities", "entities"]),
        "absent_declared": g.get("absent_declared", []),
    })

    # ---- temporal.yaml ----
    dump(os.path.join(gro, "temporal.yaml"), {
        "pub_date": f"{year}-01-01", "doi": meta.get("doi", "not_specified"),
        "fetch_timestamp": fetch_ts, "note": "pub_date seeds the corpus temporal spine",
    })

    # ---- PAPER.md ----
    fm = {
        "title": meta["title"], "authors": meta.get("authors", []), "year": year,
        "venue": meta.get("venue", ""), "doi": meta.get("doi", ""), "ara_version": ARA_VERSION,
        "domain": meta.get("domain", ""), "keywords": meta.get("keywords", []),
        "grounding": meta.get("grounding", "full-text"),
        "claims_summary": [c.get("statement", "") for c in facts.get("claims", [])],
        "abstract": meta.get("abstract", ""),
    }
    with open(os.path.join(out, "PAPER.md"), "w") as f:
        f.write("---\n")
        yaml.safe_dump(fm, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
        f.write("---\n\n")
        f.write(f"# {meta['title']}\n\n## Overview\n\n{meta.get('overview','')}\n\n")
        f.write("## Compiled by\n\n`gro-compiler` (facts-based GRO compilation from Undermind read_pdfs full-text extraction).\n")

    return {"slug": slug, "out": out, "claims": len(claims), "quantities": len(quantities),
            "contributions": len(contribs), "external": len(xqs), "deltas": len(deltas)}


REQUIRED_SIDECARS = ["genre", "claims_typed", "quantities", "entities", "contributions",
                     "external_quantities", "delta_ledger", "sota_anchor", "temporal", "refs"]


def validate(out):
    gro = os.path.join(out, "gro")
    problems = []
    if not os.path.exists(os.path.join(out, "PAPER.md")):
        problems.append("missing PAPER.md")
    for s in REQUIRED_SIDECARS:
        p = os.path.join(gro, f"{s}.yaml")
        if not os.path.exists(p):
            problems.append(f"missing gro/{s}.yaml"); continue
        yaml.safe_load(open(p))  # parses?
    # anti-puffery: every contribution must realize >=1 claim
    contribs = yaml.safe_load(open(os.path.join(gro, "contributions.yaml")))["contributions"] or []
    for ct in contribs:
        if not isinstance(ct.get("realized_in"), list) or not ct["realized_in"]:
            problems.append(f"{ct['id']} realizes no claim (anti-puffery lock failed)")
        prim = (ct.get("compiler_assessed_type") or {}).get("primary")
        if prim not in CONTRIB_TAXONOMY:
            problems.append(f"{ct['id']} type '{prim}' not in metric taxonomy ({'/'.join(CONTRIB_TAXONOMY)})")
    # every claim quantity_ref resolves
    qs = {q["id"] for q in (yaml.safe_load(open(os.path.join(gro, "quantities.yaml")))["quantities"] or [])}
    for c in (yaml.safe_load(open(os.path.join(gro, "claims_typed.yaml")))["claims"] or []):
        for qr in c.get("quantity_refs", []):
            if qr not in qs:
                problems.append(f"{c['id']} references missing {qr}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facts", nargs="?", help="facts JSON file")
    ap.add_argument("--batch", help="directory of facts JSON files")
    ap.add_argument("--lib", required=True, help="output library dir")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--fetch-date", default=datetime.date.today().isoformat())
    args = ap.parse_args()
    fetch_ts = f"{args.fetch_date}T00:00:00Z"

    files = []
    if args.batch:
        files = [os.path.join(args.batch, f) for f in sorted(os.listdir(args.batch)) if f.endswith(".json")]
    elif args.facts:
        files = [args.facts]
    else:
        ap.error("pass a facts file or --batch DIR")

    for fp in files:
        facts = json.load(open(fp))
        r = compile_facts(facts, args.lib, fetch_ts)
        line = (f"compiled {r['slug']}: {r['claims']} claims, {r['quantities']} quantities, "
                f"{r['contributions']} contributions, {r['external']} external, {r['deltas']} deltas")
        if args.validate:
            probs = validate(r["out"])
            line += "  [VALID]" if not probs else "  [INVALID: " + "; ".join(probs) + "]"
        print(line)


if __name__ == "__main__":
    main()
