# Proposer 4 (improved) — metrics for `src/` implementation/reproduction layer

## Changes from stage 1

1. **Killed the surface `NAMED_TOOL_RE` proxy in `environment_concreteness`.** Any capitalized word
   ("The", "Not") used to earn the +0.2 "named tool" bonus. Replaced with `_grounded_named_tool`,
   which only credits a token if it appears in a small known-tool/lexicon set *or* is corroborated
   by actually showing up in `execution/` file content (import/usage) — i.e. the name must be
   cross-referenceable against another layer, not just capitalized.
2. **Removed the length-only free passes.** `grounding_integrity`'s empty-`execution` fallback used
   to hand out 0.6 to any 21-character sentence; `config_calibration`'s empty-`configs` fallback used
   to hand out 0.3 to any 21-character dependency string. Both now require *specific* tokens (named
   registries searched, "not cloned"/"scope decision" language, or version/parameter-shaped text) —
   generic filler no longer clears the bar, and a present-but-unspecific justification is scored
   strictly below a present-and-specific one instead of being pooled together.
3. **Closed part of the `claim_traceability` fabrication gap.** The schema now carries an optional
   `claim_inventory` (the set of `C##` ids known to exist elsewhere in the ARA, e.g. from the claims
   layer). When available, cited ids are checked against it and unverifiable ids only earn partial
   credit proportional to the verified fraction, instead of blanket 1.0 for any `C\d{2,}`-shaped
   string. When unavailable, behavior degrades to the prior (documented) limitation rather than
   silently pretending to verify.
4. **Generalized the uniformity/variance discount** (previously only in `config_calibration`) to two
   more places: `claim_traceability` now discounts a block set where every single item is lazily
   marked `"all"`, and `grounding_integrity` now discounts the case where a repo is affirmatively
   claimed in `artifacts.md` yet *every* execution file is tagged `reconstructed` — a pattern
   consistent with relabeling real code as "reconstructed" to dodge the substantive-transcription
   bar rather than genuine paper-only re-derivation.

Metric 1 (`capture_proportionality`) is retained essentially as-is — the critique had no complaint
against it beyond noting it was the strongest metric in the pool — but its cited docstring is
updated to reflect that its `REPO_SIGNS` detector is now shared/reused by `grounding_integrity`.

---

**Assumed parsed representation** (used by every function below):

```python
artifact = {
    "environment": {
        "language_runtime": str | None,
        "framework": str | None,
        "hardware": str | None,
        "data_sources": str | None,
        "key_dependencies": str | None,
        "protocols": str | None,
        "random_seeds": str | None,
        "code_availability": str | None,   # prose subsection, may be absent
        "data_availability": str | None,
    },
    "artifacts_md": [                      # [] if artifacts.md absent entirely
        {"name": str, "files_in_repo": str, "nature": str,
         "description": str, "how_to_run": str, "claims_supported": str},
        ...
    ],
    "configs": {                           # {} if no configs/ files
        "<filename>.md": [
            {"name": str, "value": str, "rationale": str,
             "search_range": str | None, "sensitivity": str, "source": str},
            ...
        ],
        ...
    },
    "execution": [                         # [] if no execution/ files
        {"path": str, "grounding": "transcribed" | "reconstructed" | None,
         "source_note": str | None, "content": str, "line_count": int},
        ...
    ],
    "claim_inventory": set | None,         # NEW: C## ids known to exist elsewhere in the ARA
                                            # (e.g. from claims.md). None if this metric layer has
                                            # no cross-artifact visibility — degrades gracefully.
}
```

---

## 1. Capture Proportionality (repo-reality vs. `src/` coverage)

**How it signals good science.** The compiler's core epistemic duty in this layer is a faithful
*mapping*, not a maximization: capture every real artifact, manufacture none. A paper whose
underlying repo is large and substantive but whose `execution/` is empty, with no disclosure, is
hiding reproducibility material — a silent coverage failure. A paper whose `execution/` is
suspiciously polished and complete despite the source being prose-only has fabricated code. Both
are worse science than an honestly, explicitly justified absence. This metric rewards the
*honesty of the mapping*, not the raw volume of code.

**Compute function.**

```python
import re

REPO_SIGNS = re.compile(r"\b(github|gitlab|zenodo|osf|dryad|repo(sitory)?|\.git\b)\b", re.I)
DISCLOSURE_SIGNS = re.compile(
    r"\b(not clone|did not clone|not captured|scope decision|not released|"
    r"no code|no analysis code|not accessioned)\b", re.I)
FABRICATION_SIGNS = re.compile(r"\b(placeholder|invented|assumed|example only)\b", re.I)


def repo_claimed_in(artifact: dict) -> bool:
    """Shared detector, reused by grounding_integrity (see metric 2) so both metrics agree on
    what counts as 'a real repo was claimed to exist' rather than drifting independently."""
    art_blocks = artifact.get("artifacts_md", [])
    return any(
        REPO_SIGNS.search((b.get("files_in_repo", "") + " " + b.get("description", "")))
        for b in art_blocks
    )


def capture_proportionality(artifact: dict) -> float:
    """
    Assumes: artifact['artifacts_md'] is a list (possibly empty) of blocks with
    'files_in_repo'/'description' text; artifact['environment']['code_availability']
    is prose or None; artifact['execution'] is a list (possibly empty).
    Returns a 0.0-1.0 score. Never returns None/N-A.
    """
    art_blocks = artifact.get("artifacts_md", [])
    exec_files = artifact.get("execution", [])
    code_avail = artifact.get("environment", {}).get("code_availability") or ""

    repo_claimed = repo_claimed_in(artifact)
    disclosed = bool(DISCLOSURE_SIGNS.search(code_avail)) or any(
        DISCLOSURE_SIGNS.search(b.get("description", "")) for b in art_blocks
    )

    if repo_claimed and not exec_files:
        # A real repo is claimed but nothing was captured into execution/.
        return 0.9 if disclosed else 0.05          # honest scope decision vs silent failure

    if not repo_claimed and not exec_files and not art_blocks:
        # Nothing claimed, nothing captured: only defensible if code_availability
        # explicitly reasons about genre (e.g. meta-analysis, no primary data).
        return 0.7 if len(code_avail) > 40 and not FABRICATION_SIGNS.search(code_avail) else 0.1

    if exec_files and not repo_claimed and not art_blocks:
        # Code appeared from nowhere the metadata ever mentions a source for.
        return 0.15

    if exec_files:
        # Reward proportion of files carrying a real source citation
        cited = sum(1 for f in exec_files if f.get("source_note"))
        return 0.5 + 0.5 * (cited / len(exec_files))

    return 0.3  # residual: some artifacts_md, no execution, no clear repo claim either way
```

**What it does & why.** It cross-references the *claim* of code existing (in `artifacts.md` /
`code_availability` prose) against the *fact* of what landed in `execution/`. Four regimes are
scored differently: (a) claimed-but-absent-and-undisclosed → near-zero (the exact "silent
coverage failure" FAIL condition); (b) claimed-but-absent-and-disclosed → high (the legitimate
huu25-style scope decision); (c) nothing-claimed-nothing-captured → scored on whether the genre
justification is substantive (the che26-style correct absence); (d) code present → scored on how
much of it is actually source-cited rather than free-floating.

**Why it's hard to Goodhart.** You cannot inflate this by writing more code — an uncited pile of
`execution/` files with no `artifacts_md`/repo mention still scores low (regime b'/0.15). You
cannot inflate it by omitting mention of the repo either, since `repo_claimed` becomes false only
if you never say a repo exists, which itself is checked elsewhere (metric 5, claim traceability,
penalizes vague `artifacts.md`). Writing a fake disclosure sentence is cheap, but doing so while
still deleting real code hurts metric 2 (grounding integrity, since the resulting files/citations
won't reconcile) and metric 5 (path verifiability).

---

## 2. Grounding-Tag & Citation Integrity

**How it signals good science.** Every `execution/*` file must self-declare its evidentiary
status (`transcribed` vs `reconstructed`) and, if transcribed, must be traceable to a real
file/line in the source. This is the mechanism that keeps "real code" from silently sliding into
"plausible-looking code the compiler made up." A layer that gets this right lets a reader verify
provenance without re-deriving it; a layer that gets it wrong (or omits the tag) is asking to be
trusted rather than showing its work.

**Compute function.**

```python
import re

TAG_RE = re.compile(r"^#\s*Grounding:\s*(transcribed|reconstructed)\s*$", re.M)
SRC_CITE_RE = re.compile(r"(Source|cite)[:\s].{3,}", re.I)
NOTIMPL_RE = re.compile(r"NotImplementedError\(.*Not specified in paper.*\)")

# Specific, checkable absence language — NOT a length gate. A justification only counts as
# "honest disclosure" if it names a mechanism (a searched registry, a stated non-clone decision,
# or an explicit "duplicates prose method" reasoning), matching the vocabulary the shape doc's own
# worked examples (che26, huu25) actually use.
SPECIFIC_ABSENCE_RE = re.compile(
    r"\b(no code availability statement|no github|no gitlab|no zenodo|no osf|no dryad|"
    r"not clone|did not clone|scope decision|duplicat\w*\s+(the\s+)?(prose|methodology|"
    r"study_design)|summary-data|no analysis code was released|verified via)\b", re.I)


def grounding_integrity(artifact: dict) -> float:
    """
    Assumes each execution file dict has 'content' (full file text) and
    'grounding' (parsed first-line tag, or None if absent/malformed).
    If execution is empty, falls back to whether absence itself is *specifically* (not just
    lengthily) justified via environment['code_availability']. Never returns None.
    """
    files = artifact.get("execution", [])
    if not files:
        code_avail = artifact.get("environment", {}).get("code_availability") or ""
        if SPECIFIC_ABSENCE_RE.search(code_avail):
            return 0.6                      # named mechanism for the absence — genuinely honest
        if len(code_avail) > 20:
            return 0.15                     # something was written, but it's generic filler
        return 0.0                          # silent / blank

    scores = []
    tags = []
    for f in files:
        content = f.get("content", "")
        tag_match = TAG_RE.search(content)
        if not tag_match:
            tags.append(None)
            scores.append(0.0)          # missing/malformed tag = defect, per doc
            continue
        tag = tag_match.group(1)
        tags.append(tag)
        if tag == "transcribed":
            has_cite = bool(SRC_CITE_RE.search(content[:400]))
            substantive = f.get("line_count", 0) >= 15
            scores.append(0.4 + 0.3 * has_cite + 0.3 * substantive)
        else:  # reconstructed
            has_stub = bool(NOTIMPL_RE.search(content))
            scores.append(0.5 + 0.5 * has_stub)

    base = sum(scores) / len(scores)

    # Anti-gaming (generalized from metric 3's variance discount): if a real repo was
    # affirmatively claimed elsewhere in the ARA (repo_claimed_in, shared with metric 1), yet
    # *every* execution file is uniformly tagged 'reconstructed', that's the signature of
    # relabeling copyable real code as paper-derived reconstruction to dodge the substantive-body
    # bar transcribed files are held to. Discount it.
    if len(files) >= 2 and len(set(tags)) == 1 and tags[0] == "reconstructed" and repo_claimed_in(artifact):
        base *= 0.6

    return base
```

**What it does & why.** For each file it requires the literal `# Grounding:` tag as the doc
mandates; a missing tag is scored zero outright (the doc calls this "itself a defect"). For
`transcribed` files it rewards a nearby source citation and enough substance to be a real function
body rather than a stub (guarding against "stripped to signatures-only," an explicit FAIL
condition). For `reconstructed` files it rewards presence of the `NotImplementedError("Not
specified in paper")` idiom that marks honest incompleteness rather than invented logic. When no
execution files exist at all, it doesn't return N/A and it no longer rewards mere verbosity — it
requires the absence justification to name a specific, checkable mechanism, with a smaller partial
credit for present-but-generic text and zero for silence.

**Why it's hard to Goodhart.** Slapping `# Grounding: transcribed` on a stub without real content
only buys the 0.4 base — the substance and citation bonuses require actual line count and a
citation string, which in turn must be truthful to survive metric 1 (a fake citation to a repo
that was never claimed to exist looks inconsistent under capture-proportionality) and metric 5
(path verifiability). Marking everything `reconstructed` to dodge the "substantive body" bar
caps you at 0.5 per file (no higher without honest `NotImplementedError` stubs) and, if a repo was
claimed at all, now trips the uniformity discount on top — a wholesale "reconstructed" relabeling
of real code no longer quietly averages out to a moderate score. Writing a generic one-liner like
"code not available" to farm the old flat 0.6 fallback now only earns 0.15; only naming a real,
specific absence mechanism (a registry actually searched, an explicit non-clone decision) reaches
0.6, and that language is cheap to write but expensive to falsify without contradicting metric 1's
`disclosed` check on the same text.

---

## 3. Configuration Rationale–Sensitivity Calibration

**How it signals good science.** Good experimental science documents *why* a parameter takes the
value it does in proportion to how much that parameter matters. A config layer where
high-sensitivity parameters carry real rationale and search ranges, while low-sensitivity ones are
terse, reflects genuine methodological effort. A config layer where sensitivity labels are applied
uniformly and rationale is uniformly blank suggests the sensitivity field is decorative rather
than the product of an actual sensitivity analysis.

**Compute function.**

```python
import re

# Version numbers or parameter-shaped vocabulary — a *specific* signal that something
# quantitative was actually reported, not just "some text longer than N characters."
PARAM_LIKE_RE = re.compile(
    r"\b(v?\d+(\.\d+){1,3}|parameter|threshold|cutoff|dose|dosage|rate|epoch|"
    r"learning[- ]rate|seed|iteration)\b", re.I)


def config_calibration(artifact: dict) -> float:
    """
    Assumes artifact['configs'] maps filename -> list of param dicts with
    'rationale' and 'sensitivity' string fields (sensitivity in
    {'high','medium','low'} or a free-text/'Not specified' value).
    Empty configs is itself scored (not skipped), via environment fallback.
    """
    blocks = [p for plist in artifact.get("configs", {}).values() for p in plist]

    if not blocks:
        deps = artifact.get("environment", {}).get("key_dependencies") or ""
        protocols = artifact.get("environment", {}).get("protocols") or ""
        combined = f"{deps} {protocols}"
        # No configs captured at all: only partial credit, and only if the substitute text is
        # *specific* (a version number, a named parameter-shaped term) rather than merely long.
        return 0.3 if PARAM_LIKE_RE.search(combined) else 0.0

    weight = {"high": 3, "medium": 2, "low": 1}
    def is_specified(text):
        t = (text or "").strip().lower()
        return t not in ("", "not specified in paper", "n/a")

    weighted_num, weighted_den = 0.0, 0.0
    sens_values = []
    for p in blocks:
        sens = (p.get("sensitivity") or "").strip().lower()
        w = weight.get(sens, 1)
        sens_values.append(sens)
        weighted_den += w
        if is_specified(p.get("rationale")):
            weighted_num += w

    base = weighted_num / weighted_den if weighted_den else 0.0

    # Anti-gaming: if sensitivity is non-trivial (>=3 blocks) but shows zero
    # variance, treat the labeling as likely uninformative and discount it.
    if len(sens_values) >= 3 and len(set(sens_values)) == 1:
        base *= 0.6

    return base
```

**What it does & why.** It weights "is the rationale actually filled in" by the declared
sensitivity of the parameter, so a paper is rewarded most for justifying the parameters that
matter most, not for padding easy, low-stakes fields. If `configs/` is entirely absent, rather
than skipping, it falls back to a much smaller signal from `environment.md`'s dependency/protocol
fields — but that fallback now requires a genuinely parameter-shaped token (a version number, a
named quantity like "threshold"/"dose"/"seed"), not just 20+ characters of arbitrary prose. It then
discounts cases where the sensitivity field itself shows no variance, catching lazily-uniform
labeling.

**Why it's hard to Goodhart.** Marking every parameter "low sensitivity" to lower the bar for
required rationale triggers the variance penalty once there are ≥3 blocks. Marking everything
"high" with copy-pasted boilerplate rationale raises `is_specified` scores but produces
suspiciously long, repetitive rationale text that other proposers'/independent qualitative review
would flag; within this metric set, it also tends to reduce line-count-based substance elsewhere
if the same boilerplate leaks into `execution/` docstrings (metric 2). Simply not creating
`configs/` files to avoid scrutiny caps the score at 0.3 at best, and even that 0.3 now requires a
real parameter-shaped mention in `environment.md` — padding the dependency string with filler
prose no longer buys the fallback credit.

---

## 4. Environment Metadata Concreteness & Transparency

**How it signals good science.** Reproducibility is a function of how concrete and checkable the
`environment.md` fields are — versioned dependencies, named hardware, explicit seeds — vs. vague
prose. Crucially, an honest `"Not specified in paper"` is scientifically better than a field that
is simply missing/blank, because it distinguishes "the original paper didn't report this" (a fact
about the source) from "the compiler didn't bother" (a fact about the artifact). This metric
rewards concreteness first, and honest disclosure of absence second, while penalizing silent
blanks hardest.

**Compute function.**

```python
import re

VERSION_RE = re.compile(r"\b[vV]?\d+(\.\d+){1,3}\b")
HONEST_ABSENCE_RE = re.compile(r"not specified in paper|n/a\b", re.I)

# A real (if small) lexicon of tool/platform names that plausibly recur across environment.md and
# execution/ imports, replacing the old "any capitalized word" proxy that scored "The"/"Not".
KNOWN_TOOL_LEXICON = {
    "python", "r", "bioconductor", "pytorch", "tensorflow", "scanpy", "scvi", "seurat",
    "cellranger", "spaceranger", "netmeta", "limma", "edger", "bayesspace", "liana",
    "jhpce", "slurm", "docker", "conda", "cuda", "numpy", "pandas", "sklearn",
    "huggingface", "prism", "graphpad", "stata", "spss", "matlab",
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+.\-]{2,}")

FIELDS = ["language_runtime", "framework", "hardware", "data_sources",
          "key_dependencies", "protocols", "random_seeds"]


def _grounded_named_tool(val: str, exec_files: list) -> bool:
    """A named-tool bonus now requires the token to be independently corroborated: either it's a
    recognized tool/platform name, or it actually recurs inside execution/ file content (imports,
    CLI calls) — so an arbitrary capitalized word in prose can no longer buy the bonus on its own."""
    exec_blob = " ".join(f.get("content", "") for f in exec_files).lower()
    for tok in TOKEN_RE.findall(val):
        low = tok.lower()
        if low in KNOWN_TOOL_LEXICON:
            return True
        if len(low) >= 4 and low in exec_blob:
            return True
    return False


def environment_concreteness(artifact: dict) -> float:
    """
    Assumes artifact['environment'] is a dict possibly missing keys entirely
    (blank) vs. present with honest-absence text vs. present with concrete
    detail. Always returns a score; a fully blank environment scores 0.0.
    """
    env = artifact.get("environment", {})
    exec_files = artifact.get("execution", [])
    scores = []
    for field in FIELDS:
        val = env.get(field)
        if val is None or val.strip() == "":
            scores.append(0.0)                       # silently missing: worst case
            continue
        if HONEST_ABSENCE_RE.search(val):
            scores.append(0.4)                        # transparent but uninformative
            continue
        has_version = bool(VERSION_RE.search(val))
        has_named = _grounded_named_tool(val, exec_files)
        scores.append(0.6 + 0.2 * has_version + 0.2 * has_named)

    return sum(scores) / len(scores)
```

**What it does & why.** It walks the seven core `environment.md` fields and scores each on a
three-tier scale: silently absent (0.0, worst — undisclosed gap), honestly marked
"not specified in paper" (0.4 — transparent about a real limitation of the source), or populated
with concrete detail (0.6 base, up to 1.0 with version numbers and a corroborated named tool).
The named-tool bonus is now cross-referenced rather than a capitalization proxy: it fires only for
a recognized platform/tool name or a token that independently recurs in the captured
`execution/` content, so it cannot be earned by capitalizing an arbitrary word.

**Why it's hard to Goodhart.** Padding fields with invented version numbers to hit the 1.0 tier
is the obvious attack, but fabricated versions/tool names that don't correspond to anything real
in `artifacts_md`/`execution` citations will contradict metric 1 and metric 2 (a claimed
dependency with no corresponding execution import or artifact reference reads as inconsistent) —
and now, concretely, a fabricated tool name that never appears in `execution/` content and isn't in
the known lexicon simply fails `_grounded_named_tool` outright, rather than passing on
capitalization alone. Simply writing "not specified in paper" everywhere to seem "honest" caps
every field at 0.4, well below what real reporting would earn — so honesty-as-a-dodge is capped,
not free.

---

## 5. Claim-Traceability of Captured Artifacts

**How it signals good science.** The implementation layer only matters insofar as it is tied back
to the claims it supports — `artifacts.md`'s own schema requires a `Claims supported` field for
exactly this reason. An artifact block that names a real, verifiable file path and links to
specific claim IDs is doing epistemic work (a reader can check "does this artifact actually
substantiate C04?"). A block with a generic path and a vague or missing claims field is
decorative documentation that cannot be audited.

**Compute function.**

```python
import re

CLAIM_ID_RE = re.compile(r"\bC\d{2,}\b")
GENERIC_PATH_RE = re.compile(r"^(n/?a|not a repo file|unknown|tbd)?$", re.I)
VAGUE_CLAIMS_RE = re.compile(r"\b(several|various|some|many)\b", re.I)


def claim_traceability(artifact: dict) -> float:
    """
    Assumes each artifacts_md block has 'files_in_repo' and 'claims_supported'
    string fields. Empty artifacts_md is scored 0.0, not skipped.
    NEW: artifact['claim_inventory'] (set[str] | None) — the set of C## ids the ARA's claims
    layer actually contains, if visible to this metric. When present, cited ids are checked
    against it instead of being trusted at face value; when absent, behavior degrades to the
    prior (unverifiable-but-not-penalized) treatment.
    """
    blocks = artifact.get("artifacts_md", [])
    if not blocks:
        return 0.0

    inventory = artifact.get("claim_inventory")  # set[str] | None
    claims_norm = []  # for the uniformity check below
    scores = []
    for b in blocks:
        path = (b.get("files_in_repo") or "").strip()
        claims = (b.get("claims_supported") or "").strip()
        claims_norm.append(claims.lower())

        path_score = 0.0 if GENERIC_PATH_RE.match(path) and "not a repo file" not in path.lower() else \
                     0.6 if "not a repo file" in path.lower() else \
                     1.0 if len(path) > 8 else 0.3

        if claims.lower() == "all":
            claims_score = 0.7   # legitimate but coarse-grained
        elif claims.strip() == "":
            claims_score = 0.0
        else:
            ids = CLAIM_ID_RE.findall(claims)
            if ids and not VAGUE_CLAIMS_RE.search(claims):
                if inventory is not None:
                    # Verify against the real claim inventory rather than trusting any
                    # C\d{2,}-shaped string; unverifiable ids only earn partial credit,
                    # proportional to how many of the cited ids actually exist elsewhere.
                    verified = [i for i in ids if i in inventory]
                    claims_score = 0.4 + 0.6 * (len(verified) / len(ids))
                else:
                    claims_score = 1.0   # specific, enumerable ids; cannot cross-check here
            else:
                claims_score = 0.3   # present but vague ("several claims")

        scores.append(0.5 * path_score + 0.5 * claims_score)

    base = sum(scores) / len(scores)

    # Anti-gaming (generalized from metric 3's variance discount): a block set where every single
    # item is lazily marked "all" earns the coarse-grained credit on every block with zero
    # differentiation effort. Once there are enough blocks to make differentiation meaningful,
    # discount uniform "all"-everywhere labeling the same way metric 3 discounts uniform
    # sensitivity labeling.
    if len(blocks) >= 3 and all(c == "all" for c in claims_norm):
        base *= 0.6

    return base
```

**What it does & why.** For every `artifacts.md` block it scores the path field (real-looking
repo path > explicitly-justified non-repo item like a PROSPERO registration > blank/generic) and
the claims field (verified-specific `C##` ids > blanket `"all"` > vague hedge words > blank), then
averages the two per block. When the metric layer has visibility into the ARA's actual claim
inventory, cited ids are no longer taken on faith — an id that names something that doesn't exist
anywhere else in the artifact earns only partial credit, scaled to how much of the citation set is
real. This operationalizes the schema's own audit hook: a block only counts as epistemically useful
if a reader (or another layer) could go check it against a specific, real claim.

**Why it's hard to Goodhart.** Writing `"all"` for every block to guarantee credit only earns 0.7
per block, not 1.0 — and if a paper has ≥3 artifacts blocks *all* lazily marked `"all"`, the
uniformity discount now knocks the whole metric down by 40%, closing off "mark everything all" as
a costless default. Inventing specific-looking `C04, C07` ids is no longer free when
`claim_inventory` is available: an id fabricated out of thin air fails verification and only earns
partial credit proportional to the genuinely-real ids in the same block, so padding a claims field
with more invented ids to look thorough actively drags the block's score toward the 0.4 floor
rather than up. Even where `claim_inventory` isn't wired up, a fabricated dense web of claim ids
across many artifacts with thin `files_in_repo` paths still drags down the path-side of the same
per-block average, since path fidelity and claims fidelity are scored independently and averaged,
not each gameable to 1.0 on their own.

---

## Combination

These five metrics are built to interlock rather than reward the same behavior twice. Metric 1
(capture proportionality) and metric 2 (grounding integrity) both hinge on *citations existing and
being consistent*, and now also share a single `repo_claimed_in` detector — inflating one by adding
uncited code or undisclosed claims directly starves the other of the evidence it needs to score
well, and a uniform "everything is reconstructed" relabeling trips a discount in metric 2 the same
way a uniform sensitivity label trips one in metric 3. Metric 4 (environment concreteness) rewards
version-number-and-tool-name detail only when the tool name is independently corroborated (a known
lexicon entry or a token that actually recurs in cited `execution/` content), so padding metadata
with invented capitalized nouns no longer pays off in isolation. Metric 3 (config calibration),
metric 4's fallback, and metric 5 (claim traceability) all now share the same anti-length-padding
posture — fallback credit requires a *specific* token (a version number, a named parameter, a
verified claim id, a named absence mechanism), not merely enough characters to clear a threshold —
and metrics 3 and 5 both apply the same uniformity-as-laziness discount (identical sensitivity
labels; blanket "all" claims) so that maximizing apparent coverage by copy-pasting labels is capped
rather than maximized in either place. Overall, cheaply maximizing any one metric (write more code,
tag everything, cite everything, write a longer boilerplate sentence) now more reliably either
contradicts what another metric can verify (paths, claims, source notes, execution content) or
trips an explicit uniformity/specificity discount — so a paper cannot win the full set cheaply
without the underlying `src/` layer actually being honest, proportionate, and traceable.
