#!/usr/bin/env python3
"""
gro_extend.py — the material GRO compiler engine (self-contained).

This compiles the MATERIAL layers of a GRO artifact from an ARA. It is pure material
compilation: it structures what is actually present in the research. It makes NO judgments
and computes NO metrics — no novelty typing, no comparison against prior work, no scoring.
Metrics (breakthrough / significance / novelty) are a separate concern and are NOT built here.

`compile_gro.py` imports this module.

Material layers written into <ara>/gro/:
    temporal.yaml       dates present in the material (pub_date / doi / fetch_timestamp)
    refs.yaml           R##   the reference spine (references present)
    quantities.yaml     Q##   load-bearing numbers, each verbatim-quoted from source
    entities.yaml       EN-   terms / concepts / methods / measures / datasets named
    claims_typed.yaml   C##   claims with their structural form (not their merit)
    genre.yaml                paper type + which expected sections are present / absent
    contributions.yaml  CT##  the contributions the authors state, linked to realizing claims

The deterministic parts (temporal, claim-id seeding, file structure, referential-integrity
validation) are done here. Reading the material to fill the structural fields is compilation
too, done by the per-turn skill — it is transcription of what the source says, never an
evaluative judgment.

`pending_extraction` marks a structural slot whose value has not yet been compiled FROM THE
MATERIAL. It is a "not yet read" marker, not a judgment deferral.

Public surface used by compile_gro.py:
    MATERIAL_LAYERS
    load_ara(ara_dir)
    scaffold(ara_dir, out_dir=None, force=False)
    validate(gro_dir)
    _load_yaml(path)
"""
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML required: pip install pyyaml")

MATERIAL_LAYERS = [
    "temporal.yaml",
    "refs.yaml",
    "quantities.yaml",
    "entities.yaml",
    "claims_typed.yaml",
    "genre.yaml",
    "contributions.yaml",
]

PENDING = "pending_extraction"  # material not yet compiled from source (NOT a judgment)


# ---------------------------------------------------------------------------
# ARA parsing (the material we compile from)
# ---------------------------------------------------------------------------
def _now_utc():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def parse_frontmatter(paper_md_path):
    """Pull title / year / doi out of PAPER.md YAML frontmatter (best-effort)."""
    out = {"title": None, "year": None, "doi": None}
    if not os.path.isfile(paper_md_path):
        return out
    text = open(paper_md_path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
            out["title"] = fm.get("title")
            out["year"] = fm.get("year")
            out["doi"] = fm.get("doi")
        except yaml.YAMLError:
            pass
    if out["year"] is None:
        y = re.search(r"^year:\s*(\d{4})", text, re.MULTILINE)
        if y:
            out["year"] = int(y.group(1))
    if out["doi"] is None:
        d = re.search(r'^doi:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if d:
            out["doi"] = d.group(1).strip()
    return out


def parse_claims(claims_md_path):
    """Return [(C##, header_text), ...] from logic/claims.md."""
    claims = []
    if not os.path.isfile(claims_md_path):
        return claims
    for line in open(claims_md_path, encoding="utf-8"):
        m = re.match(r"^#+\s*(C\d{2,})\s*[:\-]\s*(.+?)\s*$", line)
        if m:
            claims.append((m.group(1), m.group(2)))
    return claims


def load_ara(ara_dir):
    return {
        "front": parse_frontmatter(os.path.join(ara_dir, "PAPER.md")),
        "claims": parse_claims(os.path.join(ara_dir, "logic", "claims.md")),
    }


# ---------------------------------------------------------------------------
# Material-layer scaffolds
# ---------------------------------------------------------------------------
HEADER = "# GRO material layer, compiled by gro-compiler. Pure material compilation; no metrics/judgments. "


def gen_temporal(ara):
    """Fully deterministic — dates present in the material."""
    year = ara["front"]["year"]
    doc = {
        "pub_date": (f"{year}-01-01" if year else PENDING),
        "doi": ara["front"]["doi"] or PENDING,
        "fetch_timestamp": _now_utc(),
        "note": "Dates present in the material. pub_date from PAPER.md year; "
                "fetch_timestamp is compile time. No precedence/cutoff windows are set here — "
                "those are metric concerns, out of scope for material compilation.",
    }
    return doc, HEADER + "temporal.yaml — dates present in the material (deterministic)."


def gen_claims_typed(ara):
    """One row per REAL claim id (deterministic). Structural fields are compiled from the
    claim text by the per-turn skill — the STRUCTURE of the claim, never its merit."""
    rows = []
    for cid, header in ara["claims"]:
        rows.append({
            "id": cid,  # DETERMINISTIC: a real logic/claims.md id
            "claim_type": f"{PENDING}  # generalization | prediction | existence | comparison | mechanism | definition",
            "polarity": f"{PENDING}  # positive | negative",
            "logical_form": f"{PENDING}  # a formal restatement of what the claim asserts",
            "population_scope": f"{PENDING}  # claimed_universal | sample | single_case",
            "quantity_refs": [],   # Q## this claim's numbers map to
            "concept_refs": [],    # EN- ids the claim names
            "proof_refs": [],      # evidence / experiment ids
            "depends_on": [],      # other C## ids
            "_seed_claim": header,  # source header, for the compile pass
        })
    return {"claims": rows}, HEADER + ("claims_typed.yaml — one row per real claim; "
            "structural form compiled from the claim text (not an evaluation).")


def gen_refs(ara):
    return {"refs": []}, HEADER + ("refs.yaml — the reference spine (references present in "
            "the material). Compile one R## per source cited.")


def gen_quantities(ara):
    return {"quantities": []}, HEADER + ("quantities.yaml — one Q## per load-bearing number, "
            "each with a verbatim `quote` copied from the source line (grounding).")


def gen_entities(ara):
    return {"entities": []}, HEADER + ("entities.yaml — EN- terms/concepts/methods/measures/"
            "datasets named in the material.")


def gen_genre(ara):
    doc = {
        "paper_type": f"{PENDING}  # e.g. empirical results | format/architecture spec | review | methods",
        "expected_slots": [],   # sections this genre would be expected to contain
        "present_slots": [],    # of those, the ones actually present in the material
        "absent_declared": [],  # expected slots honestly declared absent
    }
    return doc, HEADER + ("genre.yaml — paper type + which expected sections are present/"
            "absent (material, not a quality judgment).")


def gen_contributions(ara):
    """The contributions the AUTHORS state, linked to the claims that realize them. No
    assessment of novelty/type/significance — that is metric construction, out of scope."""
    return {"contributions": []}, HEADER + ("contributions.yaml — the contributions the "
            "authors state, each linked via realized_in to the real C## that realize it. "
            "No novelty typing / assessment (that is a metric, not compiled here).")


GENERATORS = {
    "temporal.yaml": gen_temporal,
    "refs.yaml": gen_refs,
    "quantities.yaml": gen_quantities,
    "entities.yaml": gen_entities,
    "claims_typed.yaml": gen_claims_typed,
    "genre.yaml": gen_genre,
    "contributions.yaml": gen_contributions,
}


def _dump(path, doc, header_comment):
    hc = header_comment.strip()
    hc = hc if hc.startswith("#") else "# " + hc
    with open(path, "w", encoding="utf-8") as f:
        f.write(hc + "\n")
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, default_flow_style=False)


def scaffold(ara_dir, out_dir=None, force=False):
    """Ensure <ara>/gro/ exists and every material layer is present. Non-destructive:
    existing files are preserved (compiled content is never clobbered) unless force=True."""
    if not os.path.isfile(os.path.join(ara_dir, "PAPER.md")):
        return {"dir": ara_dir, "ok": False, "reason": "no PAPER.md (not an ARA dir)"}
    ara = load_ara(ara_dir)
    gro_dir = os.path.join(out_dir or ara_dir, "gro")
    os.makedirs(gro_dir, exist_ok=True)
    written, skipped = [], []
    for name in MATERIAL_LAYERS:
        path = os.path.join(gro_dir, name)
        if os.path.exists(path) and not force:
            skipped.append(name)
            continue
        doc, header = GENERATORS[name](ara)
        _dump(path, doc, header)
        written.append(name)
    return {"dir": ara_dir, "gro_dir": gro_dir, "ok": True,
            "n_claims": len(ara["claims"]), "year": ara["front"]["year"],
            "written": written, "skipped": skipped}


# ---------------------------------------------------------------------------
# Validation — material integrity (grounding + referential integrity). No metrics.
# ---------------------------------------------------------------------------
def _load_yaml(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _is_pending(v):
    return isinstance(v, str) and v.strip().startswith(PENDING)


def validate(gro_dir, ara_dir=None):
    """Check the compiled material for integrity, not merit:
      - every claims_typed row is a real claim; every real claim has a row
      - every quantity carries a verbatim quote and links to a claim (grounding)
      - every contribution links to real claims that realize it (referential integrity)
      - every ref has an id
    Reports pending (not-yet-compiled) slots separately from integrity issues."""
    issues, pending = [], []
    for name in MATERIAL_LAYERS:
        if not os.path.isfile(os.path.join(gro_dir, name)):
            issues.append(f"MISSING {name}")

    real_claim_ids = set()
    if ara_dir:
        real_claim_ids = {c for c, _ in parse_claims(os.path.join(ara_dir, "logic", "claims.md"))}

    # claims_typed
    ct = _load_yaml(os.path.join(gro_dir, "claims_typed.yaml")) or {}
    typed_ids = set()
    for row in (ct.get("claims") or []):
        cid = row.get("id")
        typed_ids.add(cid)
        if real_claim_ids and cid not in real_claim_ids:
            issues.append(f"claims_typed {cid}: no such claim in logic/claims.md (orphan row)")
        for field in ("claim_type", "polarity", "logical_form", "population_scope"):
            if _is_pending(row.get(field)):
                pending.append(f"claims_typed {cid}.{field}")
    for cid in sorted(real_claim_ids - typed_ids):
        issues.append(f"claim {cid} present in logic but not yet compiled into claims_typed")

    # quantities — grounding
    q = _load_yaml(os.path.join(gro_dir, "quantities.yaml")) or {}
    for row in (q.get("quantities") or []):
        qid = row.get("id")
        if not (row.get("quote") or "").strip():
            issues.append(f"quantity {qid}: no verbatim quote (ungrounded)")
        if not (row.get("claim_refs") or []):
            issues.append(f"quantity {qid}: not linked to any claim")

    # contributions — referential integrity
    c = _load_yaml(os.path.join(gro_dir, "contributions.yaml")) or {}
    for row in (c.get("contributions") or []):
        ctid = row.get("id")
        realized = row.get("realized_in") or []
        if not realized:
            issues.append(f"contribution {ctid}: realized_in empty (not linked to any claim)")
        elif real_claim_ids:
            bad = [r for r in realized if r not in real_claim_ids]
            if bad:
                issues.append(f"contribution {ctid}: realized_in points at non-claims {bad}")

    # refs
    r = _load_yaml(os.path.join(gro_dir, "refs.yaml")) or {}
    for i, row in enumerate(r.get("refs") or []):
        if not row.get("id"):
            issues.append(f"ref #{i}: missing id")

    return {
        "gro_dir": gro_dir,
        "pending": pending,
        "issues": issues,
        "material_complete": len(issues) == 0 and len(pending) == 0,
    }
