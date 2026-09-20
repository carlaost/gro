#!/usr/bin/env python3
"""
V3 grounding — RC6 (grounding reclassified to the artifact-trust axis, with explicit trust classes)
and RC7 (semantic grounding: does the cited quote actually SUPPORT the number/claim).

`ctx` is the same read-only context described in detectors.py. Additionally useful here:
  ctx["base"]        Path to research/ara-library/<slug>/
  ctx["claims_md"]   raw claims.md (source bullets carry «quote» + a cited *.md path or a paper.pdf/§ ref)
  ctx["v1"]          the full V1 per-ARA result

Return schema (frozen):
  grounding_trust(ctx)     -> {"value": float|None, "trust_class": str, "self_contained_ratio": float|None,
                               "coverage": int, "detail": str}
      # RC6: this is an ARTIFACT-TRUST signal, NOT a paper ranker. `value` = verified ratio where checkable.
      # trust_class ∈ {"self_contained", "pdf_pointer", "no_parseable_quotes", "no_source", "mixed"}.
      # Replace the old None with an explicit class. `coverage` = number of checkable quotes.
  semantic_grounding(ctx)  -> {"value": float|"pending", "validity": <lattice>, "detail": str}
      # RC7: a PAPER ranker. If an LLM [sem] pass is available, emit a frozen per-(number,quote) support
      # score. If not available, return value="pending", validity="pending_sem" (degrade gracefully —
      # do NOT fabricate a score). Prefer reading a frozen logic/grounding_findings.yaml if present.

Normalization: apply NFKC + dash-fold + whitespace-collapse before string-presence checks, and route a
"quote exists in file but does not support the number" to ungrounded, while "quote string not found due
to extraction/format" routes to trust_class, not to semantic failure.

See research/metrics/v3/plan.md (RC6/RC7).
"""
from __future__ import annotations
import re
import unicodedata
from pathlib import Path

# ----------------------------- RC6: verified grounding -----------------------------
# Same shapes as V2's verified_grounding (research/metrics/v2/compute_metrics_v2.py), adapted to the
# frozen v3 ctx + trust_class schema, plus an optional PyMuPDF coverage booster (gated on availability).

QUOTE_RE = re.compile(r"«(.+?)»")
PATH_RE = re.compile(r"([\w./-]+\.md)")                       # in-repo evidence file (not paper.pdf / §refs)
CLAIM_BLOCK_RE = re.compile(r"(?m)^##\s+C\d+:")
SOURCES_BLOCK_RE = re.compile(r"-\s*\*\*Sources?\*\*:\s*(.*?)(?=\n-\s*\*\*Tags\*\*|\Z)", re.S)

# NFKC normalizes most compatibility forms already; fold the remaining dash/hyphen variants NFKC
# leaves alone (en/em dash, minus sign, non-breaking hyphen) so «AAPC: 3.18» matches across a
# transcription that swapped a hyphen style.
_DASH_FOLD = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-",
    "—": "-", "―": "-", "−": "-",
})


def _norm(s: str) -> str:
    """NFKC + dash-fold + whitespace-collapse, case-insensitive — the shared presence-check normalizer."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.translate(_DASH_FOLD)
    return re.sub(r"\s+", " ", s).strip().lower()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _resolve_cited(base: Path, data_lib_dir: Path, relpath: str) -> Path | None:
    """A cited *.md may live in the ARA dir or in the discovery record (data/lib/<slug>/)."""
    for root in (base, data_lib_dir):
        if root is None or not root.exists():
            continue
        cand = root / relpath
        if cand.exists():
            return cand
        hits = list(root.rglob(Path(relpath).name))     # fall back to basename anywhere under root
        if hits:
            return hits[0]
    return None


_PDF_TEXT_CACHE: dict[Path, str] = {}


def _find_pdf(base: Path, data_lib_dir: Path) -> Path | None:
    for root in (base, data_lib_dir):
        if root is None or not root.exists():
            continue
        cand = root / "paper.pdf"
        if cand.exists():
            return cand
        hits = list(root.glob("*.pdf"))
        if hits:
            return hits[0]
    return None


def _pdf_haystack(pdf_path: Path | None) -> str | None:
    """OPTIONAL coverage booster (RC6): try to resolve a paper.pdf/§ pointer against the actual PDF
    text via PyMuPDF. Gated behind (a) PyMuPDF being importable and (b) the PDF actually existing —
    never assumed corpus-wide. Returns None (booster off) rather than raising on any failure."""
    if pdf_path is None:
        return None
    if pdf_path in _PDF_TEXT_CACHE:
        return _PDF_TEXT_CACHE[pdf_path] or None
    text = ""
    try:
        import fitz  # PyMuPDF
        with fitz.open(pdf_path) as doc:
            text = "\n".join(page.get_text() for page in doc)
    except Exception:
        text = ""
    _PDF_TEXT_CACHE[pdf_path] = text
    return _norm(text) if text else None


def _quote_matches(quote: str, hay: str) -> bool:
    """Ellipsis-tolerant substring check: a «a ... b» quote matches if each non-empty segment is
    present (line-tolerant re-open, not a fragile exact-string match)."""
    parts = [p for p in re.split(r"\.\.\.|…", quote) if p.strip()]
    return bool(parts) and all(_norm(p) in hay for p in parts)


def grounding_trust(ctx):
    base: Path = ctx["base"]
    slug = ctx["slug"]
    claims_md = ctx.get("claims_md") or ""
    data_lib_dir = base.parent.parent / "data" / "lib" / slug   # research/data/lib/<slug>/

    has_sources_header = False
    present = unverifiable = checkable = verified = 0
    pdf_boosted = 0

    pdf_hay = _pdf_haystack(_find_pdf(base, data_lib_dir))

    for block in CLAIM_BLOCK_RE.split(claims_md)[1:]:
        src_m = SOURCES_BLOCK_RE.search(block)
        if not src_m:
            continue
        has_sources_header = True
        for line in src_m.group(1).splitlines():
            quotes = QUOTE_RE.findall(line)
            if not quotes:
                continue
            pm = PATH_RE.search(line)
            target = _resolve_cited(base, data_lib_dir, pm.group(1)) if pm else None
            for quote in quotes:
                present += 1
                if pm:
                    checkable += 1
                    if target is not None and _quote_matches(quote, _norm(_read(target))):
                        verified += 1
                    # else: cited *.md path given but file missing / quote not found after
                    # normalization -> "quote_not_found_extraction", still counted in `checkable`
                    # (it stays an in-repo pointer) but not in `verified`. This is NOT routed to
                    # no_source/no_parseable_quotes -- those describe the ABSENCE of any checkable
                    # pointer, not a per-quote match failure.
                    continue
                # no in-repo *.md path -> a paper.pdf/§ pointer; try the optional PDF booster first
                if pdf_hay is not None and _quote_matches(quote, pdf_hay):
                    checkable += 1
                    verified += 1
                    pdf_boosted += 1
                else:
                    unverifiable += 1

    quote_not_found_extraction = checkable - verified

    if not has_sources_header:
        trust_class = "no_source"                 # no Sources block at all (e.g. woj25)
    elif present == 0:
        trust_class = "no_parseable_quotes"        # Sources blocks exist, but no «quote» in any of them
    elif unverifiable == 0:
        trust_class = "self_contained"             # every quote resolves to an in-repo/PDF-resolved pointer
    elif checkable == 0:
        trust_class = "pdf_pointer"                # every quote is a bare paper.pdf/§ pointer, nothing checkable
    else:
        trust_class = "mixed"                      # some checkable, some bare pdf/§ pointers

    value = round(verified / checkable, 3) if checkable else None
    self_contained_ratio = round(checkable / present, 3) if present else None

    detail = (
        f"quotes_present={present}, checkable={checkable} (in-repo .md pointer"
        + (f" or PyMuPDF-resolved PDF, +{pdf_boosted} boosted" if pdf_boosted else "")
        + f"), unverifiable={unverifiable} (bare paper.pdf/§ pointer, no PDF resolution available/matched), "
        f"verified={verified}, quote_not_found_extraction={quote_not_found_extraction} "
        "(checkable but string-match failed even after NFKC+dash-fold+whitespace normalization -- "
        "an extraction/format issue, routed to trust_class/coverage, not scored as a semantic "
        f"grounding failure) -> trust_class={trust_class}."
    )

    return {
        "value": value,
        "trust_class": trust_class,
        "self_contained_ratio": self_contained_ratio,
        "coverage": checkable,
        "detail": detail,
    }


# ----------------------------- RC7: semantic grounding (paper ranker) -----------------------------
def semantic_grounding(ctx):
    base: Path = ctx["base"]
    findings_path = base / "logic" / "grounding_findings.yaml"

    if not findings_path.exists():
        return {
            "value": "pending",
            "validity": "pending_sem",
            "detail": (
                "no frozen logic/grounding_findings.yaml on this ARA and no LLM [sem] pass is wired "
                "into this run. RC7 asks whether the cited quote SUPPORTS the number (not just whether "
                "the string is present) -- that requires semantic judgment this deterministic module "
                "cannot fabricate, so it degrades to pending rather than guessing a score. Expected "
                "path on this well-compiled corpus (plan.md RC7): low yield here, guardrail for worse ARAs."
            ),
        }

    try:
        import yaml
        findings = yaml.safe_load(findings_path.read_text(encoding="utf-8")) or []
    except Exception as e:
        return {
            "value": "pending",
            "validity": "pending_sem",
            "detail": f"logic/grounding_findings.yaml present but unreadable ({e}); degrading to pending",
        }

    if not isinstance(findings, list) or not findings:
        return {
            "value": "pending",
            "validity": "pending_sem",
            "detail": "logic/grounding_findings.yaml present but empty/malformed; degrading to pending",
        }

    n = len(findings)
    grounded = 0
    for f in findings:
        if not isinstance(f, dict):
            continue
        verdict = str(f.get("verdict") or "").lower()
        value_match = str(f.get("value_match") or "").lower()
        polarity_ok = bool(f.get("polarity_ok"))
        context_match = bool(f.get("context_match"))
        string_present = bool(f.get("string_present"))
        if (string_present and verdict == "supports"
                and value_match in ("exact", "rounded", "derived")
                and polarity_ok and context_match):
            grounded += 1

    return {
        "value": round(grounded / n, 3),
        # Cycle-3: was "validated" — but this is scored from a frozen LLM-JUDGE pass (grounding_findings),
        # i.e. "an LLM ran", which is the exact P1 disease fixed in sem_metrics. It is `judge_scored`
        # (internally consistent, LLM-derived), NOT externally validated → correctly not `usable`.
        "validity": "judge_scored",
        "detail": (
            f"{grounded}/{n} (number,quote) findings pass string_present ∧ verdict==supports ∧ "
            "value_match∈{exact,rounded,derived} ∧ polarity_ok ∧ context_match, scored deterministically "
            "from the frozen logic/grounding_findings.yaml (a prior [sem] pass's output -- this module "
            "does not itself call an LLM, so self-grading is avoided by construction)."
        ),
    }
