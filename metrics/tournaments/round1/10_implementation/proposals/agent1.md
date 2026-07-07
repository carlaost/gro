# Proposer 1 — metrics for the `src/` implementation/reproduction layer

Assumed parsed representation (a dict) for one artifact instance:

```python
artifact = {
    "environment": {
        "language": str, "framework": str, "hardware": str,
        "data_sources": str, "key_dependencies": str, "protocols": str,
        "random_seeds": str,
        "code_availability_text": str | None,   # prose under "## Code availability"
        "data_availability_text": str | None,
    },
    "artifacts_blocks": [   # from src/artifacts.md, 0+
        {"name": str, "files_in_repo": str, "nature": str,
         "what_it_does": str, "how_to_use": str, "claims_supported": list[str] | str}
    ],
    "configs": [   # from src/configs/*.md, 0+ files
        {"file": str, "parameters": [
            {"name": str, "value": str, "rationale": str,
             "search_range": str | None, "sensitivity": str, "source": str}
        ]}
    ],
    "execution": [   # from src/execution/*, 0+ files
        {"path": str, "grounding": "transcribed" | "reconstructed" | None,
         "source_comment": str | None,  # the "# Source: ..." line, if any
         "body": str, "line_count": int}
    ],
}
```

Boilerplate-absence phrases (used throughout): `{"not specified in paper", "n/a", "none", "not applicable", "unknown", ""}` (case-insensitive, whitespace-stripped).

---

## 1. Grounding Provenance Completeness

**How it signals good science.** Code presented as evidence is only as trustworthy as its chain of custody. The shape requires every `execution/` file to open with a `# Grounding: transcribed|reconstructed` tag plus a traceable pointer (a real file:line for transcribed, a §/equation for reconstructed). This is the code-layer equivalent of a citation: it lets a reader distinguish "this is the author's real code" from "this is our best guess at unstated logic." A layer that either omits code entirely without saying why, or includes code without declaring/citing its provenance, is hiding the evidentiary status of its strongest claims.

**Compute function.**
```python
def grounding_provenance_completeness(artifact: dict) -> float:
    # Assumes: artifact["execution"] is the full list of captured files (possibly empty);
    # artifact["environment"]["code_availability_text"] holds prose justifying absence, if any.
    exe = artifact["execution"]
    env = artifact["environment"]

    def is_boilerplate(s):
        return (s or "").strip().lower() in {"not specified in paper", "n/a", "none", "not applicable", "unknown", ""}

    if not exe:
        # Missing input case: absence of code is only good science if explicitly,
        # specifically justified — not silently skipped.
        text = env.get("code_availability_text") or ""
        if is_boilerplate(text):
            return 0.05
        # Reward specificity: named repositories checked, named search actions taken,
        # or explicit "duplicates prose method" reasoning — not just an assertion.
        specificity_markers = ["github", "gitlab", "zenodo", "osf", "dryad", "verified",
                                "searched", "no repository", "duplicat"]
        hits = sum(1 for m in specificity_markers if m in text.lower())
        return min(1.0, 0.35 + 0.15 * hits)

    scores = []
    for f in exe:
        s = 0.0
        if f["grounding"] in ("transcribed", "reconstructed"):
            s += 0.5
        else:
            scores.append(0.0)  # missing tag entirely is an explicit defect per the shape doc
            continue
        cite = f.get("source_comment") or ""
        # a real citation names a file, a line/§/eq marker, or a specific source artifact
        has_pointer = any(tok in cite.lower() for tok in [".py", ".ipynb", ".r", "§", "eq", "line", "figure", "table", "notebook", "repo"])
        if has_pointer:
            s += 0.5
        scores.append(s)
    return sum(scores) / len(scores)
```

**What it does and why.** If no execution files exist, the function checks whether their absence is defended with specific, checkable language (named registries searched, explicit reasoning about duplication) rather than a bare assertion — silence is penalized, evidenced absence is rewarded. If execution files do exist, each is scored on two independent bits: does it declare a valid grounding tag at all, and does that declaration carry an actual locatable pointer rather than a vague "adapted from the paper." The artifact score is the mean across files, so one well-cited file cannot hide many uncited ones.

**Why it's hard to Goodhart.** Slapping `# Grounding: transcribed` on every file without a real pointer only buys the 0.5 tag-presence credit, not the full score — and a fake pointer (a made-up file:line) is checkable by anyone diffing against the actual source repo, which other reviewers/metrics (see Metric 2 and 4) are specifically built to catch. Padding the "code availability" prose with buzzwords like "GitHub" without an actual verification trail is a shallow win capped at 1.0 but easily contradicted if artifacts.md or the real record disagrees.

---

## 2. Reconstruction Fidelity (Fabrication Resistance)

**How it signals good science.** The shape draws a sharp epistemic line: `transcribed` code must be a faithful, uncut copy of real code; `reconstructed` code must be a minimal stub of only the explicitly-stated mechanism, with every unstated detail marked `raise NotImplementedError("Not specified in paper")`. A reconstructed file that reads as a complete, runnable implementation is very likely inventing API names, constants, or control flow the paper never stated — exactly the fabrication the shape doc calls out as a FAIL condition. Rewarding stub-honesty over stub-completeness is rewarding the layer for not pretending to know more than the source said.

**Compute function.**
```python
import re

def reconstruction_fidelity(artifact: dict) -> float:
    # Assumes: each execution file's "body" is the literal file text.
    exe = [f for f in artifact["execution"] if f["grounding"] is not None]
    if not exe:
        return 0.1  # no execution files to assess fidelity on; treat as thin per hard constraint

    scores = []
    for f in exe:
        body = f["body"]
        n_defs = len(re.findall(r"^\s*def\s+\w+\(", body, re.M))
        n_notimpl = len(re.findall(r"NotImplementedError", body))
        n_lines = f["line_count"]

        if f["grounding"] == "reconstructed":
            if n_defs == 0:
                scores.append(0.2)  # can't assess a stub with no functions; suspicious
                continue
            # A faithful reconstruction should show unstated logic as explicit stubs.
            # Zero NotImplementedError in a nontrivial reconstructed file is a fabrication red flag.
            if n_notimpl == 0 and n_lines > 15:
                scores.append(0.0)
            else:
                coverage = min(1.0, n_notimpl / max(1, n_defs))
                scores.append(0.4 + 0.6 * coverage)
        else:  # transcribed
            # Faithful transcription retains real scaffolding: imports, and is not
            # suspiciously stripped to bare signatures (shape doc explicitly forbids this).
            has_imports = bool(re.search(r"^\s*(import|from)\s+\w+", body, re.M))
            stripped_to_signatures = n_defs > 0 and (n_lines / max(1, n_defs)) < 3
            s = 0.5 if has_imports else 0.1
            s += 0.5 if not stripped_to_signatures else 0.0
            scores.append(s)
    return sum(scores) / len(scores)
```

**What it does and why.** For `reconstructed` files it checks the ratio of `NotImplementedError` markers to function definitions — a reconstruction that never admits "not specified" while still being long and def-heavy is treated as likely-fabricated and scored zero. For `transcribed` files it checks for real import statements and for a lines-per-function ratio that rules out "stripped to signature only" — both explicit failure modes named in the shape doc. The per-file scores are averaged.

**Why it's hard to Goodhart.** You cannot simultaneously inflate this metric and Metric 1's citation-quality: adding fake `NotImplementedError` calls to a truly fabricated block to farm this score would shrink the file to something closer to a real stub, which lowers the "completeness" a gamer might otherwise want to show off elsewhere (e.g., in Metric 3's config-rigor story, where an implementation with real substance is expected to correlate with populated configs). And keeping full scaffolding in a transcribed file while inventing its content is only detectable by ground truth, which is exactly what Metric 1's pointer-check and Metric 4's repo cross-check are designed to expose.

---

## 3. Parameter Rigor Density

**How it signals good science.** `configs/*.md` exists specifically to capture *why* an analytical choice was made and *how sensitive* the result is to it — rationale, search range, sensitivity. A methods section that lists parameter values but never says why, or never characterizes sensitivity, is weaker science than one that does, independent of whether the underlying paper is "reproducible" in the code sense. This metric rewards density of real justification over boilerplate placeholders, and treats total absence of any config capture — when execution/artifacts indicate a tunable pipeline exists — as a coverage gap rather than a free pass.

**Compute function.**
```python
def parameter_rigor_density(artifact: dict) -> float:
    # Assumes: artifact["configs"] is the list of config files/blocks (possibly empty);
    # artifact["execution"] used only to detect "a tunable pipeline clearly exists".
    def is_boilerplate(s):
        return (s or "").strip().lower() in {"not specified in paper", "n/a", "none", "not applicable", "unknown", ""}

    params = [p for c in artifact["configs"] for p in c["parameters"]]

    if not params:
        # Is there evidence (in execution/) that tunable parameters exist but were never
        # captured as configs? A pipeline with epochs/thresholds/cutoffs in code but no
        # configs/ file is a thin-capture penalty, not a free "n/a".
        exe_text = " ".join(f["body"] for f in artifact["execution"])
        tunable_signals = ["epoch", "threshold", "cutoff", "learning_rate", "n_samples", "seed", "alpha="]
        if any(sig in exe_text.lower() for sig in tunable_signals):
            return 0.1
        return 0.4  # plausibly a genuinely non-parametric / analytical work; moderate, not zero

    scored = []
    for p in params:
        s = 0.0
        if not is_boilerplate(p["rationale"]):
            s += 0.4
        if p.get("search_range") and not is_boilerplate(p["search_range"]):
            s += 0.2
        if not is_boilerplate(p.get("sensitivity", "")):
            s += 0.3
        if not is_boilerplate(p.get("source", "")):
            s += 0.1
        scored.append(s)
    return sum(scored) / len(scored)
```

**What it does and why.** Each parameter block earns credit for a concrete (non-templated) rationale, a stated search range, a stated sensitivity level, and a located source — weighted toward rationale and sensitivity since those carry the most epistemic content. If no config files exist at all, the function looks inside captured execution code for signs that tunable parameters were actually used (hyperparameter-shaped tokens); finding them without a corresponding config file is scored low (a coverage gap), while true absence of any tunable machinery is scored as a moderate — not maximal — default, consistent with never handing out a free pass for missing input.

**Why it's hard to Goodhart.** Writing verbose but generic rationale ("chosen based on prior literature") without an actual sensitivity value still forfeits the 0.3 sensitivity weight, so score-farming with prose bulk alone caps out well below 1.0. Fabricating a fake `sensitivity: high` for a parameter with no accompanying execution-layer evidence a sensitivity analysis was ever run is exposed by cross-referencing execution/ content (an artifact claiming "high sensitivity, dedicated sensitivity analysis" with zero supporting code or narrative elsewhere is inconsistent with Metric 4's repo/claim coherence check).

---

## 4. Repo-Capture Honesty

**How it signals good science.** The shape doc names an explicit FAIL condition: a provided repository's real code reduced to a pointer in `artifacts.md` instead of being copied into `execution/`, done *silently* — versus the legitimate, disclosed case (huu25) where a real repo exists but wasn't cloned, and that scope decision is stated in-artifact. Good science documentation is honest about what it did and did not capture; silent under-capture misrepresents the evidentiary depth of the layer to anyone downstream who trusts it.

**Compute function.**
```python
def repo_capture_honesty(artifact: dict) -> float:
    # Assumes: artifacts_blocks entries with "Nature" indicating code/pipeline/tool are the
    # ones that could plausibly have execution/ counterparts.
    code_like_blocks = [
        b for b in artifact["artifacts_blocks"]
        if any(k in (b.get("nature") or "").lower() for k in ["tool", "pipeline", "library", "system", "code"])
    ]
    if not code_like_blocks:
        return 0.5  # nothing to check; neutral, not a free top score

    disclosure_markers = ["not cloned", "did not clone", "not captured", "scope", "verified via",
                           "not accessioned into", "pointer only", "size", "not reproduced here"]

    scores = []
    for b in code_like_blocks:
        has_real_repo_evidence = any(k in (b.get("files_in_repo") or "").lower()
                                      for k in ["github", "gitlab", "zenodo", "http", "/"])
        if not has_real_repo_evidence:
            scores.append(0.6)  # nothing concrete claimed to exist, so no capture obligation
            continue
        exe_nonempty = len(artifact["execution"]) > 0
        text_blob = (b.get("what_it_does") or "") + " " + (b.get("how_to_use") or "")
        disclosed = any(m in text_blob.lower() for m in disclosure_markers)
        if exe_nonempty:
            scores.append(1.0)          # captured — best outcome
        elif disclosed:
            scores.append(0.75)         # honestly disclosed non-capture
        else:
            scores.append(0.0)          # silent pointer-only drop — the named FAIL condition
    return sum(scores) / len(scores)
```

**What it does and why.** For every `artifacts.md` block that describes something code-shaped and backed by a real, locatable repository, the function checks whether `execution/` actually contains captured code. If it does, that's the strongest outcome. If it doesn't, the function looks for explicit disclosure language explaining the scope decision (mirroring the huu25 pattern in the shape doc) — present, it's scored as an honest, still-imperfect outcome; absent, it's scored zero, matching the shape doc's explicit FAIL condition for silent drops.

**Why it's hard to Goodhart.** A compiler could try to farm the "disclosed" credit by sprinkling scope-decision language onto every block regardless of truth, but doing so on a block that in fact *does* have matching execution/ content wastes no points (the 1.0 branch already dominates), and doing so when no real repo is claimed at all is capped at the neutral 0.5/0.6 bands — so the only place the disclosure language pays off is exactly where it's supposed to (real repo, deliberately not captured). Inflating captured execution/ with irrelevant boilerplate files to trigger the `exe_nonempty` branch is caught by Metric 2's fidelity check on those same files.

---

## 5. Environment Specificity-Weighted Provenance

**How it signals good science.** `environment.md` is the one always-present file, and its fields vary enormously in how load-bearing they are for reproducibility: a versioned dependency list and a stated random seed matter far more than a generic hardware note. Good underlying science reports these with real specificity (version numbers, actual seed values or explicit "seed not set" honesty); an ARA that reduces every field to "not specified" either reflects a genuinely under-reported paper (itself a science-quality signal worth penalizing) or a lazy compilation. Either way, low specificity should score low.

**Compute function.**
```python
import re

def environment_specificity_score(artifact: dict) -> float:
    # Assumes: artifact["environment"] has the six-plus string/prose fields from the shape.
    env = artifact["environment"]

    def is_boilerplate(s):
        return (s or "").strip().lower() in {"not specified in paper", "n/a", "none", "not applicable", "unknown", ""}

    def has_version_number(s):
        return bool(re.search(r"\d+\.\d+", s or ""))

    weights = {
        "language": 1.0, "framework": 1.0, "hardware": 0.5,
        "data_sources": 1.0, "key_dependencies": 1.5, "protocols": 0.5,
        "random_seeds": 1.5,
    }
    total_w, total_s = 0.0, 0.0
    for field, w in weights.items():
        val = env.get(field, "")
        total_w += w
        if is_boilerplate(val):
            # "n/a" is legitimate for hardware/protocols in analytical work; other boilerplate
            # fields (esp. random_seeds, key_dependencies) reflect a real reproducibility gap.
            total_s += 0.35 * w if field in ("hardware", "protocols") else 0.0
            continue
        s = 0.6  # credit for a concrete, non-boilerplate statement
        if field in ("framework", "key_dependencies") and has_version_number(val):
            s += 0.4
        elif field == "random_seeds" and re.search(r"\bseed\b.*\d", val.lower()):
            s += 0.4
        else:
            s += 0.2
        total_s += min(1.0, s) * w
    return total_s / total_w
```

**What it does and why.** Each environment field gets a reproducibility-importance weight (dependencies and seeds weighted highest, hardware/protocols lowest since "n/a" is often a true and acceptable answer there). Boilerplate absence on the high-weight fields is scored near zero (a real documentation/reproducibility gap), while "n/a" on the low-weight fields gets partial, not zero, credit since it can be a legitimate answer. Concrete values earn a base credit, with a bonus for fields that additionally carry a real version number or an actual seed value rather than just a qualitative sentence.

**Why it's hard to Goodhart.** Fabricating a fake version number or seed value to trigger the bonus is directly checkable against the same repo evidence Metric 4 and Metric 1 use (a `key_dependencies` version that doesn't match anything in a captured `execution/` file's imports, or a `random_seeds` value with no corresponding constant anywhere in transcribed code, is an internal inconsistency across this same artifact). Padding every field with wordy-but-vague prose to dodge the boilerplate check only earns the base 0.6xW credit, not the version/seed bonus, capping the payoff of that strategy well below actually reporting the paper's real specificity.

---

## Combination

These five metrics are built to check each other. Metric 1 (grounding provenance) and Metric 2 (reconstruction fidelity) both look *inside* the same `execution/` files but for different signals — a file can't fake a citation (Metric 1) without either being caught by fake-pointer inconsistency or paying the "stripped-to-signature" / "zero-NotImplementedError" cost in Metric 2. Metric 4 (repo-capture honesty) cross-checks the *coverage* claim implied by `artifacts.md` against what actually landed in `execution/`, so a compiler that games Metric 1/2 by writing beautifully-cited, well-stubbed *fake* files for a repo it never actually captured is simultaneously failing Metric 4's silent-drop check the moment `artifacts.md` describes a real, locatable repo. Metric 3 (parameter rigor) and Metric 5 (environment specificity) both reward concrete, checkable detail over prose bulk, and both are cross-referenced against `execution/` content (tunable-parameter tokens, version numbers, seed constants) — so inventing rich-sounding config rationale or environment specificity that has no corresponding trace in the transcribed code is an internal contradiction inside the same artifact, not just an isolated score to pad. Winning all five cheaply would require fabricating a fully internally-consistent fake repo, complete with matching versions, seeds, parameters, and citations — at which point the fabrication is large enough in scope that it stops being "gaming a metric" and starts being "writing a second, fictitious paper's worth of implementation detail," which is precisely the effort the shape doc's grounding rules are designed to make not worth it.
