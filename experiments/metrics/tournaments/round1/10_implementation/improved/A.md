# Proposer #2 — metrics for `src/` implementation/reproduction layer (revised)

## Changes from stage 1

- **Closed the `capture_to_claim_gap` free-pass exits (critique pt. 1).** The old `claimed_units == 0`
  branch handed out 0.7/1.0 to *any* artifact that produced zero enumerable claim-signals — including
  a compiler that deliberately writes vague `artifacts.md` prose about a repo it knows exists, to
  starve the denominator and dodge the ratio. The function now distinguishes "vague prose about a
  real, mentioned repo" (penalized, 0.15/0.3) from "no repo signal at all, i.e. plausibly a genuine
  non-code artifact" (0.7/1.0, unchanged) by reusing the `repo_mentioned` signal already computed for
  metric 3. Vagueness-as-evasion is now punished, not rewarded.
- **Made enumeration less brittle (critique pt. 2).** Claimed-unit counting no longer depends solely on
  the `\d{2}_\w+` zero-padded-stage format. Added a number-word / count-noun detector (`"fourteen
  stages"`, `"12 scripts"`, `"comprises 8 modules"`) so a pipeline described in prose rather than
  `01_foo`-style naming isn't scored as claiming zero units. To avoid the opposite failure —
  double-counting the same claimed scale because it's phrased two ways — the number-word signal is
  combined with the token-count signals via `max()`, not summed, so restating "14 stages" five times
  across a block cannot inflate the denominator past the true claim.
- **Dropped the length-based free pass in `disclosed_scope_honesty` (critique pt. 3).** The old
  `len(code_avail.strip()) > 60` OR-branch let any 61-character sentence of boilerplate ("We looked
  into it and decided not to include code here for this study.") count as a specific disclosure. That
  branch is removed entirely; disclosure quality is now judged only by whether the prose contains
  concrete, checkable tokens (named registries searched, explicit negation of a code-availability
  statement, or "duplicates prose method" reasoning) — length no longer buys credit.
- **Fixed the fragile `file_paths` stringification (critique pt. 4)** — `.__str__()` replaced with an
  explicit `" ".join(...)`, and `file_paths` are deduplicated before being counted so a block listing
  the same path twice can't pad its claimed-unit count.
- **Raised the `looks_full_bodied` line threshold from 15 to ~30 (critique pt. 4)**, aligning metric 1
  with the shape doc's own capture bar ("every real runnable file of substance (≥~30 lines or a named
  module/entrypoint) must be captured"). A 20-line file no longer gets free credit for looking
  "full-bodied" when the shape doc's own substance bar is twice that; a short file is now allowed to
  pass only if it clearly presents as a complete named entrypoint (has a `def main`/`if __name__`
  guard or an argparse/CLI block), not merely by hitting an arbitrary line count.
- **General Goodhart tightening:** wherever a fallback branch previously returned a flat, generous
  score for an "ambiguous/nothing to check" case, that branch now requires a positive signal
  (a mentioned repo, a specific token, a real captured file) before granting anything above a low
  score — consistent with the tournament's hard constraint that missing/ambiguous input is penalized,
  never treated as N/A.

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
        # substance bar raised to match the shape doc's own "~30 lines, or a named
        # module/entrypoint" capture threshold -- a short file only counts as "full-bodied"
        # if it is clearly a complete named entrypoint, not just moderately long.
        has_entrypoint = ("__main__" in content) or ("argparse" in content) or bool(
            re := __import__("re")
        ) and re.search(r"\bdef main\s*\(", content) is not None
        looks_full_bodied = (
            n_lines >= 30 and any(
                kw in content for kw in ("import ", "def ", "argparse", "logging", "library(")
            )
        ) or (has_entrypoint and n_lines >= 10)

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
matches what that tag promises: `transcribed` files should be long (now benchmarked against the
shape doc's own ~30-line substance bar, not an arbitrary lower threshold), import-laden, and cite a
real location; `reconstructed` files should be short, typed stubs that explicitly flag unimplemented
logic rather than quietly inventing it. Files with no execution content at all score 0 outright,
satisfying the hard constraint that absence is punished rather than skipped.

**Why it's hard to Goodhart.** You can't win by mass-labeling everything `transcribed` (thin files
get caught by the `looks_full_bodied` check, now calibrated to the shape doc's real substance bar
rather than a number a proposer picked) or everything `reconstructed` (fully-worked pipelines
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
    NOTE (revised): specificity is judged purely on the presence of concrete, checkable tokens.
    The previous version also granted a free pass to any code_availability prose over 60
    characters -- that length-based OR-branch is removed; a long-but-generic sentence now
    scores no differently than a short one.
    """
    exec_files = artifact.get("execution_files", [])
    blocks = artifact.get("artifacts_md_blocks", [])
    code_avail = ((artifact.get("environment", {}) or {}).get("code_availability") or "").lower()

    def block_text(b):
        return (b.get("what_it_contains", "") + " " + " ".join(b.get("file_paths", []))).lower()

    # signal that real underlying code/repo exists (from artifacts.md descriptions)
    repo_mentioned = any(
        any(kw in block_text(b) for kw in ("github", "gitlab", "repo", "zenodo", ".py", ".r", "pipeline"))
        for b in blocks
    )

    thin_capture = len(exec_files) == 0

    if not thin_capture:
        return 1.0  # substantial capture present -- no disclosure debt to pay

    if not repo_mentioned and not code_avail:
        # nothing to indicate whether code ever existed; can't distinguish
        # "correctly absent" from "silently dropped" -> hard constraint: penalize
        return 0.3

    # Specificity is now token-only: named registries actually searched, explicit negation
    # of a code-availability statement, or "duplicates prose method" reasoning. No length
    # shortcut -- a verbose-but-generic sentence gets the same (low) credit as a terse one.
    SPECIFIC_TOKENS = (
        "not clone", "not cloned", "did not clone", "no code availability statement",
        "no github", "no gitlab", "no repository", "no analysis code", "not released",
        "duplicate", "would only duplicate", "verified via", "web search", "sources.yaml",
        "zenodo", "prospero",
    )
    disclosure_is_specific = any(tok in code_avail for tok in SPECIFIC_TOKENS) or any(
        "not clone" in block_text(b) or "not cloned" in block_text(b)
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
why it wasn't captured, judged strictly by checkable tokens rather than prose length. Thin capture
with a mentioned repo and no such token is the worst case — exactly the silent-drop failure the
shape doc calls out — and scores lowest. Thin capture with a real, specific justification (che26's
meta-analysis case, huu25's "didn't clone" case) scores high.

**Why it's hard to Goodhart.** Bolting on a generic disclosure sentence ("scope was limited") to
farm credit is caught by the `disclosure_is_specific` keyword check, which demands concrete
language like "not cloned" — and, crucially, can no longer be won by simply writing a longer generic
sentence, since the length free pass has been removed. Fabricating a *specific-sounding* disclosure
for a repo that doesn't actually need one is self-defeating: if there's no real repo, `repo_mentioned`
is false and the metric already scores near-neutral without needing the disclosure at all — there's
no upside to inventing justifications where none are needed, and inventing them where they ARE
needed risks contradicting metric 1's grounding checks on any code that *is* present.

---

## 4. Parameter Provenance Density

**How it signals good science.** A config value without a rationale, sensitivity note, and source
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
import re

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}
COUNT_NOUN = r"(stages?|scripts?|modules?|steps?|files?|notebooks?|pipelines?|blocks?)"
WORDNUM_RE = re.compile(
    r"\b(\d{1,3}|" + "|".join(NUMBER_WORDS) + r")[\s-]*" + COUNT_NOUN, re.I
)


def capture_to_claim_gap(artifact: dict) -> float:
    """
    Assumes artifacts_md_blocks with 'what_it_contains' (str) and 'file_paths' (list[str]),
    and execution_files as above. Estimates 'claimed complexity' from language in
    what_it_contains that enumerates stages/files/modules -- via zero-padded stage tokens
    (e.g. "01_spaceranger"), inline code-file refs, declared paths, AND (new) number-word /
    digit + count-noun phrases like "fourteen stages" or "12 scripts" -- and compares it
    against actual captured execution files.

    Revised free-pass handling: a block that mentions a real underlying repo/pipeline but
    yields ZERO enumerable claimed units is now treated as a vagueness penalty (the compiler
    dodged the denominator), not a free pass. Only the case with NO repo signal at all
    (plausibly a genuinely non-code artifact -- dataset, registration, etc.) keeps the old
    lenient scoring.
    """
    blocks = artifact.get("artifacts_md_blocks", [])
    exec_files = artifact.get("execution_files", [])

    if not blocks and not exec_files:
        return 0.4  # nothing to compare -- plausibly a genuinely thin/abstract-only source;
                     # can't confirm honesty of that absence, so score modestly rather than skip

    def block_text(b):
        return b.get("what_it_contains", "") + " " + " ".join(b.get("file_paths", []))

    repo_mentioned = any(
        any(kw in block_text(b).lower() for kw in
            ("github", "gitlab", "repo", "zenodo", ".py", ".r", "pipeline"))
        for b in blocks
    )

    token_units = 0
    wordnum_max = 0
    seen_paths = set()
    for b in blocks:
        text = b.get("what_it_contains", "")
        # distinct numbered pipeline stages, e.g. "01_spaceranger", "14_MOFA"
        token_units += len(set(re.findall(r"\b\d{2}_\w+\b", text)))
        # distinct inline code-file references, e.g. `foo.py`
        token_units += len(set(re.findall(r"`[\w./]+\.(?:py|r|sh|ipynb)`", text, re.I)))
        for m in WORDNUM_RE.finditer(text):
            raw = m.group(1).lower()
            n = int(raw) if raw.isdigit() else NUMBER_WORDS.get(raw, 0)
            wordnum_max = max(wordnum_max, n)
        seen_paths.update(b.get("file_paths", []))
    token_units += len(seen_paths)

    # number-word phrasing states a total directly (e.g. "a 14-stage pipeline") -- take the
    # max against the token-based tally rather than summing, so restating the same scale in
    # prose and in a numbered-file-list can't double the claimed count.
    claimed_units = max(token_units, wordnum_max)

    captured_units = len(exec_files)

    if claimed_units == 0:
        if repo_mentioned:
            # a real repo/pipeline is referenced but described with NO enumerable specifics --
            # this is vagueness that starves the ratio's denominator, not an absence of claims.
            # Penalize it; a compiler cannot escape this metric by writing vaguer prose.
            return 0.3 if captured_units > 0 else 0.15
        # no repo signal at all -- plausibly a genuine non-code artifact (dataset, registration)
        return 0.7 if captured_units == 0 else 1.0

    ratio = min(captured_units / claimed_units, 1.0)
    return ratio
```

**What the function does & why.** It scans `artifacts.md` prose for enumerable signals of real
underlying complexity — numbered pipeline stages like `01_spaceranger`, inline code file
references, explicit file paths, and now number-word/digit phrases like "fourteen stages" or
"12 scripts" — and combines them into a "claimed unit" estimate, then divides the actually-captured
`execution/` file count by that claim. A block that describes a 15-stage pipeline but captures zero
files scores near zero; a block that describes three helper scripts and captures all three scores
1.0. Crucially, if a block clearly references a real repo/pipeline (`repo_mentioned`) but supplies
no enumerable specifics at all, that is now scored as evasive vagueness (0.15–0.3) rather than a
free pass — closing the loophole where a compiler could dodge this metric entirely just by writing
vaguer prose. Only genuinely non-code artifacts (no repo signal whatsoever) retain the lenient
0.7/1.0 scoring, matching the shape doc's own sanctioned "abstract-only" case.

**Why it's hard to Goodhart.** You cannot inflate this score by writing vaguer `artifacts.md` prose
about a real repo — that now routes into the penalized vagueness branch instead of the old free-pass
branch. You also cannot inflate it by dumping trivial filler files into `execution/` to raise the
numerator, because those files still have to pass metric 1's grounding-consistency check (tag/content
mismatch against the shape doc's real substance bar). And you cannot inflate the denominator's
number-word signal by restating the same scale claim in multiple phrasings, since the number-word and
token-based signals are combined with `max()`, not summed — repeating "14 stages" five times in one
block yields the same claimed-unit count as saying it once.

---

## Combination

These five metrics are built to interlock rather than stack independently. Metric 1 (grounding
consistency) and metric 5 (coverage gap) jointly punish the two opposite ways of cheating capture:
claiming rich code that isn't really there (caught by 1's shape check) and hiding real code behind
vague description (caught by 5's claim-vs-capture ratio, including the revised vagueness-penalty
branch for a mentioned-but-unenumerated repo) — padding one direction actively worsens the other.
Metric 2 (environment specificity) and metric 4 (parameter provenance) both reward *traceable*
concreteness rather than raw verbosity, so generic padding that might fool a naive length heuristic
in one gets flagged as uncited or unversioned in the other. Metric 3 (disclosed scope honesty) is the
connective tissue: it is the only metric that treats a low score on 1/4/5 as potentially *legitimate*
provided the artifact says so explicitly and specifically, using the same token-based specificity
test as metric 5's `repo_mentioned` signal (no length shortcuts in either) — but a fake or generic
disclosure statement doesn't help metric 3 much and does nothing for 1, 4, or 5, so there is no cheap
combined strategy that inflates all five at once. The only way to score well across the whole set is
to actually capture what exists, tag it honestly, cite it specifically, and say plainly — with
checkable specifics, not just length or repetition — what wasn't captured and why. That is precisely
the reproducibility behavior the artifact layer exists to reward.
