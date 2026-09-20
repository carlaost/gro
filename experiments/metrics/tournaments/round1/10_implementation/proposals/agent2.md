# Proposer #2 — metrics for `src/` implementation/reproduction layer

Assumed parsed shape (matches `10_implementation.md`):

```python
artifact = {
  "environment": {
    "language": str | None,
    "framework": str | None,
    "hardware": str | None,
    "data_sources": str | list | None,
    "dependencies": list[str] | None,      # e.g. ["edgeR v4.6.2", "limma v3.64.1"]
    "protocols": str | None,
    "seeds": str | None,                   # includes "Not specified in paper" / "n/a" as literal strings
    "code_availability": str | None,       # prose subsection, or None if absent
    "data_availability": str | None,       # verbatim quote subsection, or None if absent
  },
  "artifacts_md_blocks": [                 # [] if artifacts.md absent
    {"name": str, "file_paths": list[str], "nature": str,
     "what_it_contains": str, "how_to_run": str, "claims_supported": list[str] | "all"}
  ],
  "configs": {                             # {} if no configs/ dir
    "category_name": [
      {"param_name": str, "value": str, "rationale": str | None,
       "search_range": str | None, "sensitivity": str | None, "source": str | None}
    ]
  },
  "execution_files": [                     # [] if src/execution/ absent
    {"filename": str, "grounding": "transcribed" | "reconstructed" | None,
     "content": str, "line_count": int, "cited_source": str | None}
  ],
}
```

---

## 1. Grounding-Tag/Content Consistency

**How it signals good science.** The compiler's own rule is that `transcribed` code must be a
faithful, full-bodied copy of real source, while `reconstructed` code must be a minimal typed stub
with `NotImplementedError` on anything unstated. A file's *declared* provenance and its *actual*
shape either match or they don't — and a mismatch (e.g. a "transcribed" file that's actually a
5-line paraphrase, or a "reconstructed" file dense with fully-worked-out logic that reads like
invented internals) is direct textual evidence of either sloppiness or fabrication. Consistency
between claim and content is a cheap, checkable proxy for honest provenance tracking, which is a
precondition for reproducibility ever meaning anything.

**Compute function.**

```python
def grounding_consistency_score(artifact: dict) -> float:
    """
    Assumes: artifact["execution_files"] is a list of dicts with 'grounding', 'content',
    'line_count', 'cited_source' as described above. If execution_files is empty, we cannot
    assess grounding fidelity at all -- treat that as a maximal penalty per the hard constraint
    (missing input = low score, not N/A), UNLESS environment.md's code_availability subsection
    explicitly justifies the absence (see metric 3) -- that carve-out is handled by metric 3,
    not here, so this metric stays strict.
    """
    files = artifact.get("execution_files", [])
    if not files:
        return 0.0  # no execution files -> cannot verify grounding at all -> penalize

    scores = []
    for f in files:
        tag = f.get("grounding")
        content = f.get("content", "") or ""
        n_lines = f.get("line_count", 0)
        cited = bool(f.get("cited_source"))

        if tag not in ("transcribed", "reconstructed"):
            scores.append(0.0)  # missing/malformed tag is an explicit documented defect
            continue

        has_notimpl = "NotImplementedError" in content or "not specified" in content.lower()
        looks_full_bodied = n_lines >= 15 and any(
            kw in content for kw in ("import ", "def ", "argparse", "logging", "library(")
        )

        if tag == "transcribed":
            # must be full-bodied AND cite a real source location
            s = 0.0
            s += 0.5 if looks_full_bodied else 0.0
            s += 0.5 if cited else 0.0
            # transcribed files padded with NotImplementedError are suspicious -> penalize
            if has_notimpl:
                s *= 0.3
            scores.append(s)
        else:  # reconstructed
            # should be minimal/typed, should NOT look like a fully worked-out pipeline,
            # and unspecified logic should honestly say so
            s = 0.0
            s += 0.5 if has_notimpl else 0.0
            s += 0.5 if not looks_full_bodied else 0.1
            scores.append(s)

    return sum(scores) / len(scores)
```

**What the function does & why.** For every captured execution file, it checks whether the
declared grounding tag is actually present (untagged files score zero, matching the brief's
explicit "grounding tag missing is itself a defect" rule), then checks whether the file's shape
matches what that tag promises: `transcribed` files should be long, import-laden, and cite a real
location; `reconstructed` files should be short, typed stubs that explicitly flag unimplemented
logic rather than quietly inventing it. Files with no execution content at all score 0 outright,
satisfying the hard constraint that absence is punished rather than skipped.

**Why it's hard to Goodhart.** You can't win by mass-labeling everything `transcribed` (thin files
get caught by the `looks_full_bodied` check) or everything `reconstructed` (fully-worked pipelines
without `NotImplementedError` get caught too). Adding fake citations to fabricated code passes this
metric's `cited` check but produces content that a downstream fact-check (or metric 5, coverage
gap) would flag as unverifiable — the reward for gaming this metric transfers risk elsewhere in the
set.

---

## 2. Environment Specificity Index

**How it signals good science.** Reproducibility is not binary — "Python was used" and "Python
3.11.4 with pinned requirements.txt SHA" are both technically "language specified" but only one
lets someone actually rerun the work. Good science reports *exact*, falsifiable operational detail
(versions, seeds, hardware) rather than vague gestures. This metric rewards specificity per field
and treats vague-but-present values as only partial credit — while explicit, honest "n/a" for
fields that are genuinely inapplicable (e.g. hardware for a pure meta-analysis) is NOT penalized,
per the shape doc's own distinction between correct absence and negligent vagueness.

**Compute function.**

```python
import re

def environment_specificity_score(artifact: dict) -> float:
    """
    Assumes artifact["environment"] dict with string/None fields as in the shape above.
    Distinguishes: (a) a field with concrete detail -> full credit; (b) a field honestly
    marked n/a/not-applicable for a genre where it plausibly doesn't apply -> neutral credit
    (not a penalty, since the artifact is being honest, not evasive); (c) a field marked
    "Not specified in paper" for something that plausibly WAS knowable (e.g. software version,
    seeds) -> penalized; (d) a field entirely missing/empty -> maximal penalty (hard constraint).
    """
    env = artifact.get("environment") or {}
    fields = ["language", "framework", "hardware", "data_sources", "dependencies", "protocols", "seeds"]
    version_re = re.compile(r"\d+\.\d+(\.\d+)?")

    def score_field(name, val):
        if val is None or (isinstance(val, str) and val.strip() == ""):
            return 0.0  # missing entirely -> penalize, never skip
        text = val if isinstance(val, str) else " ".join(val)
        low = text.lower()
        if "n/a" in low or "not applicable" in low:
            # honest inapplicability -- only real credit for hardware/protocols/seeds
            # where non-computational genres legitimately have none
            return 0.6 if name in ("hardware", "protocols", "seeds") else 0.2
        if "not specified" in low:
            return 0.15  # honest but a real reproducibility gap
        # reward concrete versioned/dated/quantified detail
        if version_re.search(text) or len(text) > 40:
            return 1.0
        return 0.5  # present but thin (e.g. "Python" with no version)

    per_field = [score_field(f, env.get(f)) for f in fields]
    return sum(per_field) / len(fields)
```

**What the function does & why.** It walks the seven core `environment.md` fields, giving full
credit only to concrete, versioned, or richly-detailed values, partial credit to thin-but-present
values, small credit to honestly-flagged gaps ("Not specified in paper"), a bit more credit to
honest structural "n/a" (which reflects genre reality, not negligence), and zero to fields that are
simply absent from the parse. This operationalizes "more concrete detail = more reproducible" while
still being lenient to genuinely non-computational work.

**Why it's hard to Goodhart.** Padding fields with long but content-free prose to trigger the
`len(text) > 40` heuristic is possible in isolation, but that padding has no version numbers or
citable specifics, so it collides with metric 4 (provenance density) and metric 1 (grounding
consistency) which both reward *traceable* specificity, not verbosity — a compiler that inflates
prose without substance loses on those instead.

---

## 3. Disclosed-Scope Honesty Score

**How it signals good science.** The shape doc is explicit that the *hardest* failure mode here is
silent under-capture: a repo exists, has real code, and the artifact just doesn't mention it versus
a repo exists and the artifact says "we didn't clone it, here's why." Good science is defined
partly by calibrated self-report of its own limits. This metric directly rewards the presence of an
explicit, specific scope-limitation statement (in `code_availability`/`data_availability` or an
`artifacts.md` block) whenever the artifact's own capture is thin relative to what it describes —
and it penalizes thin capture that comes with NO such disclosure, treating silence as evidence of
either carelessness or concealment.

**Compute function.**

```python
def disclosed_scope_honesty(artifact: dict) -> float:
    """
    Assumes environment['code_availability'] (str|None) and artifacts_md_blocks list as above.
    Thin capture = few/no execution files. The question this asks: when capture is thin,
    is that thinness EXPLAINED in-artifact, specifically and checkably, or just left silent?
    """
    exec_files = artifact.get("execution_files", [])
    blocks = artifact.get("artifacts_md_blocks", [])
    code_avail = (artifact.get("environment", {}) or {}).get("code_availability") or ""

    # signal that real underlying code/repo exists (from artifacts.md descriptions)
    repo_mentioned = any(
        any(kw in (b.get("what_it_contains", "") + b.get("file_paths", []).__str__()).lower()
            for kw in ("github", "gitlab", "repo", "zenodo", ".py", ".r", "pipeline"))
        for b in blocks
    )

    thin_capture = len(exec_files) == 0

    if not thin_capture:
        return 1.0  # substantial capture present -- no disclosure debt to pay

    if not repo_mentioned and not code_avail:
        # nothing to indicate whether code ever existed; can't distinguish
        # "correctly absent" from "silently dropped" -> hard constraint: penalize
        return 0.3

    # thin/no execution AND something (repo mention or code_availability prose) exists to check
    disclosure_is_specific = len(code_avail.strip()) > 60 or any(
        len(b.get("what_it_contains", "")) > 40 and "not clone" in b.get("what_it_contains", "").lower()
        or "not cloned" in b.get("what_it_contains", "").lower()
        for b in blocks
    )

    if repo_mentioned and not disclosure_is_specific:
        return 0.1  # repo clearly exists, capture is thin, but no real explanation -> silent drop
    if disclosure_is_specific:
        return 0.9  # honestly, specifically flagged scope decision
    return 0.5  # some prose exists but genre plausibly has no code at all (e.g. pure meta-analysis)
```

**What the function does & why.** It first checks whether execution capture is thin. If capture is
substantial, there's nothing to disclose and the metric passes automatically. If capture is thin,
it looks for two things: (a) does `artifacts.md` itself mention an underlying repo/pipeline
(evidence that code plausibly exists), and (b) is there a specific, non-boilerplate explanation for
why it wasn't captured. Thin capture with a mentioned repo and no explanation is the worst case —
exactly the silent-drop failure the shape doc calls out — and scores lowest. Thin capture with a
real, specific justification (che26's meta-analysis case, huu25's "didn't clone" case) scores high.

**Why it's hard to Goodhart.** Bolting on a generic disclosure sentence ("scope was limited") to
farm credit is caught by the `disclosure_is_specific` length/keyword check, which demands concrete
language like "not cloned." And fabricating a *specific-sounding* disclosure for a repo that
doesn't actually need one is self-defeating: if there's no real repo, `repo_mentioned` is false and
the metric already scores near-neutral without needing the disclosure at all — there's no upside to
inventing justifications where none are needed, and inventing them where they ARE needed risks
contradicting metric 1's grounding checks on any code that *is* present.

---

## 4. Parameter Provenance Density

**How it signals good science. ** A config value without a rationale, sensitivity note, and source
citation is just a number someone chose — it's unfalsifiable and uninspectable. Good science shows
its work: *why* this cutoff, *how sensitive* the result is to it, and *where* in the paper it's
stated. Density of these three fields across all captured config blocks is a direct proxy for how
audit-able the paper's parameter choices are, and the shape doc explicitly carries a `Sensitivity`
field for exactly this reason.

**Compute function.**

```python
def parameter_provenance_density(artifact: dict) -> float:
    """
    Assumes artifact['configs'] is a dict of category -> list of per-parameter dicts with
    'rationale', 'sensitivity', 'source' (each str|None, or the literal "Not specified in paper").
    No configs at all is scored as a penalty per the hard constraint, since nearly all
    computational work has at least one tunable parameter worth recording; genuinely
    parameter-free analytical work should have said so in environment.md instead (that's
    scored by metric 2's honest-n/a path, not here).
    """
    configs = artifact.get("configs", {}) or {}
    all_params = [p for plist in configs.values() for p in plist]

    if not all_params:
        return 0.1  # no configs captured at all -> low score, not N/A

    def field_credit(val):
        if not val:
            return 0.0
        low = val.strip().lower()
        if "not specified" in low:
            return 0.2  # honestly flagged gap, still a gap
        return 1.0

    per_param_scores = []
    for p in all_params:
        rationale = field_credit(p.get("rationale"))
        sensitivity = field_credit(p.get("sensitivity"))
        source = field_credit(p.get("source"))
        # source is weighted highest: an uncited rationale is just an assertion
        per_param_scores.append(0.25 * rationale + 0.25 * sensitivity + 0.5 * source)

    return sum(per_param_scores) / len(per_param_scores)
```

**What the function does & why.** For every parameter block across every config file, it scores
the presence and quality of rationale, sensitivity, and source, weighting `source` (a checkable
pointer to a section/table/figure) higher than `rationale` (which can be asserted without
verification). "Not specified in paper" gets small partial credit for honesty over silence, but far
less than an actual citation. It averages across all parameters so a paper can't hide a few
well-documented showcase parameters among many undocumented ones.

**Why it's hard to Goodhart.** Filling every `source` field with a vague "Methods" citation to farm
credit is possible, but doing so at scale across dozens of parameters is itself checkable against
metric 2 (specificity) and produces a visibly repetitive, low-information pattern; more importantly
fabricating specific-sounding sources (page/table numbers) that don't correspond to real content
risks contradicting the transcribed-code citations checked in metric 1 if the same source strings
are cross-referenced. Padding rationale/sensitivity text without a real source only buys 50% of the
per-parameter score at most, since source is weighted highest.

---

## 5. Capture-to-Claim Coverage Gap

**How it signals good science.** `artifacts.md` blocks make *claims* about what exists (a pipeline
with 15 numbered stages, a repo of a given size, N processed-data objects). `execution/` and the
rest of `src/` are where those claims should cash out into physically present content, when the
compiler chose to capture rather than merely describe. A large gap between how much an
`artifacts.md` block *says* exists and how much is actually captured as real files is a direct,
computable measure of under-delivery — independent of whether that gap is disclosed (metric 3
already scores the disclosure quality; this metric scores the raw magnitude of the gap itself, so
a large, well-disclosed gap can still legitimately score low here — disclosure explains a gap, it
doesn't erase the reproducibility cost of it).

**Compute function.**

```python
def capture_to_claim_gap(artifact: dict) -> float:
    """
    Assumes artifacts_md_blocks with 'what_it_contains' (str) and 'file_paths' (list[str]),
    and execution_files as above. Estimates 'claimed complexity' from language in
    what_it_contains that enumerates stages/files/modules, and compares it against actual
    captured execution files. No artifacts.md and no execution at all is the ambiguous
    "abstract-only source" case -- scored neutral-low, not skipped.
    """
    blocks = artifact.get("artifacts_md_blocks", [])
    exec_files = artifact.get("execution_files", [])

    if not blocks and not exec_files:
        return 0.4  # nothing to compare -- plausibly a genuinely thin/abstract-only source;
                     # can't confirm honesty of that absence, so score modestly rather than skip

    import re
    claimed_units = 0
    for b in blocks:
        text = b.get("what_it_contains", "")
        # count enumerated pipeline stages / numbered scripts / named modules as claimed units
        claimed_units += len(re.findall(r"\b\d{2}_\w+", text))          # e.g. "01_spaceranger"
        claimed_units += len(re.findall(r"`[\w./]+\.(py|r|sh|ipynb)`", text, re.I))
        claimed_units += len(b.get("file_paths", []))

    captured_units = len(exec_files)

    if claimed_units == 0:
        # no enumerable claims -- capture of anything at all is a bonus, absence is neutral
        return 0.7 if captured_units == 0 else 1.0

    ratio = min(captured_units / claimed_units, 1.0)
    return ratio
```

**What the function does & why.** It scans `artifacts.md` prose for enumerable signals of real
underlying complexity (numbered pipeline stages like `01_spaceranger`, inline code file
references, explicit file paths) and sums them into a rough "claimed unit" count, then divides the
actually-captured `execution/` file count by that claim. A block that describes a 15-stage pipeline
but captures zero files scores near zero; a block that describes three helper scripts and captures
all three scores 1.0. This makes the "pointer instead of copy" failure mode numeric rather than
qualitative.

**Why it's hard to Goodhart.** You cannot inflate this score by writing vaguer `artifacts.md` prose
(fewer enumerable units lowers the denominator but also strips exactly the kind of concrete
grounded description the compiler's own `artifacts.md` template requires, which would independently
read as a defect under any qualitative check of that field). You also cannot inflate it by dumping
trivial filler files into `execution/` to raise the numerator, because those files still have to
pass metric 1's grounding-consistency check (tag/content mismatch) and metric 4 doesn't apply here
but a thin, contentless file dragged in purely to pad the count will fail `looks_full_bodied` in
metric 1.

---

## Combination

These five metrics are built to interlock rather than stack independently. Metric 1 (grounding
consistency) and metric 5 (coverage gap) jointly punish the two opposite ways of cheating capture:
claiming rich code that isn't really there (caught by 1's shape check) and hiding real code behind
vague description (caught by 5's claim-vs-capture ratio) — padding one direction actively worsens
the other. Metric 2 (environment specificity) and metric 4 (parameter provenance) both reward
*traceable* concreteness rather than raw verbosity, so generic padding that might fool a naive
length heuristic in one gets flagged as uncited or unversioned in the other. Metric 3 (disclosed
scope honesty) is the connective tissue: it is the only metric that treats a low score on 1/4/5 as
potentially *legitimate* provided the artifact says so explicitly and specifically — but a fake or
generic disclosure statement doesn't help metric 3 much (it demands specificity) and does nothing
for 1, 4, or 5, so there is no cheap combined strategy that inflates all five at once. The only way
to score well across the whole set is to actually capture what exists, tag it honestly, cite it
specifically, and say plainly what wasn't captured and why — which is precisely the reproducibility
behavior the artifact layer exists to reward.
