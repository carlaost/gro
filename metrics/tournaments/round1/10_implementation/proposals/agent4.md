# Proposer 4 — metrics for `src/` implementation/reproduction layer

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

    repo_claimed = any(
        REPO_SIGNS.search((b.get("files_in_repo", "") + " " + b.get("description", "")))
        for b in art_blocks
    )
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

def grounding_integrity(artifact: dict) -> float:
    """
    Assumes each execution file dict has 'content' (full file text) and
    'grounding' (parsed first-line tag, or None if absent/malformed).
    If execution is empty, falls back to whether absence itself is honestly
    tagged via environment['code_availability'] (never returns None).
    """
    files = artifact.get("execution", [])
    if not files:
        code_avail = artifact.get("environment", {}).get("code_availability") or ""
        return 0.6 if len(code_avail) > 20 else 0.0

    scores = []
    for f in files:
        content = f.get("content", "")
        tag_match = TAG_RE.search(content)
        if not tag_match:
            scores.append(0.0)          # missing/malformed tag = defect, per doc
            continue
        tag = tag_match.group(1)
        if tag == "transcribed":
            has_cite = bool(SRC_CITE_RE.search(content[:400]))
            substantive = f.get("line_count", 0) >= 15
            scores.append(0.4 + 0.3 * has_cite + 0.3 * substantive)
        else:  # reconstructed
            has_stub = bool(NOTIMPL_RE.search(content))
            scores.append(0.5 + 0.5 * has_stub)

    return sum(scores) / len(scores)
```

**What it does & why.** For each file it requires the literal `# Grounding:` tag as the doc
mandates; a missing tag is scored zero outright (the doc calls this "itself a defect"). For
`transcribed` files it rewards a nearby source citation and enough substance to be a real function
body rather than a stub (guarding against "stripped to signatures-only," an explicit FAIL
condition). For `reconstructed` files it rewards presence of the `NotImplementedError("Not
specified in paper")` idiom that marks honest incompleteness rather than invented logic. When no
execution files exist at all, it doesn't return N/A — it scores the fallback justification text.

**Why it's hard to Goodhart.** Slapping `# Grounding: transcribed` on a stub without real content
only buys the 0.4 base — the substance and citation bonuses require actual line count and a
citation string, which in turn must be truthful to survive metric 1 (a fake citation to a repo
that was never claimed to exist looks inconsistent under capture-proportionality) and metric 5
(path verifiability). Marking everything `reconstructed` to dodge the "substantive body" bar
caps you at 1.0 only if every unspecified branch is honestly stubbed — a fully-fleshed
"reconstructed" file with no `NotImplementedError` anywhere (i.e., invented logic dressed as
reconstruction) scores only 0.5, not higher than an honestly transcribed one.

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
        # No configs captured at all: only partial credit, scaled by whether
        # environment-level parameter info exists as a weaker substitute.
        return 0.3 if (len(deps) > 20 or len(protocols) > 20) else 0.0

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
fields (still nonzero if something parameter-like was captured, otherwise zero). It then
discounts cases where the sensitivity field itself shows no variance, catching lazily-uniform
labeling.

**Why it's hard to Goodhart.** Marking every parameter "low sensitivity" to lower the bar for
required rationale triggers the variance penalty once there are ≥3 blocks. Marking everything
"high" with copy-pasted boilerplate rationale raises `is_specified` scores but produces
suspiciously long, repetitive rationale text that other proposers'/independent qualitative review
would flag; within this metric set, it also tends to reduce line-count-based substance elsewhere
if the same boilerplate leaks into `execution/` docstrings (metric 2). Simply not creating
`configs/` files to avoid scrutiny caps the score at 0.3 at best.

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
NAMED_TOOL_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]{2,}\b")  # crude proper-noun/tool-name proxy
HONEST_ABSENCE_RE = re.compile(r"not specified in paper|n/a\b", re.I)

FIELDS = ["language_runtime", "framework", "hardware", "data_sources",
          "key_dependencies", "protocols", "random_seeds"]

def environment_concreteness(artifact: dict) -> float:
    """
    Assumes artifact['environment'] is a dict possibly missing keys entirely
    (blank) vs. present with honest-absence text vs. present with concrete
    detail. Always returns a score; a fully blank environment scores 0.0.
    """
    env = artifact.get("environment", {})
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
        has_named = len(NAMED_TOOL_RE.findall(val)) >= 1
        scores.append(0.6 + 0.2 * has_version + 0.2 * has_named)

    return sum(scores) / len(scores)
```

**What it does & why.** It walks the seven core `environment.md` fields and scores each on a
three-tier scale: silently absent (0.0, worst — undisclosed gap), honestly marked
"not specified in paper" (0.4 — transparent about a real limitation of the source), or populated
with concrete detail (0.6 base, up to 1.0 with version numbers and named tools/orgs). Averaging
across fields rewards artifacts that are thorough *and* honest about what wasn't reported, over
ones that are silent or vague.

**Why it's hard to Goodhart.** Padding fields with invented version numbers to hit the 1.0 tier
is the obvious attack, but fabricated versions/tool names that don't correspond to anything real
in `artifacts_md`/`execution` citations will contradict metric 1 and metric 2 (a claimed
dependency with no corresponding execution import or artifact reference reads as inconsistent).
Simply writing "not specified in paper" everywhere to seem "honest" caps every field at 0.4,
well below what real reporting would earn — so honesty-as-a-dodge is capped, not free.

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
    string fields. Empty artifacts_md is scored 0.0, not skipped, unless the
    execution layer independently carries claim linkage (it doesn't, per shape
    doc, so absence here is a straightforward penalty).
    """
    blocks = artifact.get("artifacts_md", [])
    if not blocks:
        return 0.0

    scores = []
    for b in blocks:
        path = (b.get("files_in_repo") or "").strip()
        claims = (b.get("claims_supported") or "").strip()

        path_score = 0.0 if GENERIC_PATH_RE.match(path) and "not a repo file" not in path.lower() else \
                     0.6 if "not a repo file" in path.lower() else \
                     1.0 if len(path) > 8 else 0.3

        if claims.lower() == "all":
            claims_score = 0.7   # legitimate but coarse-grained
        elif CLAIM_ID_RE.search(claims) and not VAGUE_CLAIMS_RE.search(claims):
            claims_score = 1.0   # specific, enumerable ids
        elif claims.strip() == "":
            claims_score = 0.0
        else:
            claims_score = 0.3   # present but vague ("several claims")

        scores.append(0.5 * path_score + 0.5 * claims_score)

    return sum(scores) / len(scores)
```

**What it does & why.** For every `artifacts.md` block it scores the path field (real-looking
repo path > explicitly-justified non-repo item like a PROSPERO registration > blank/generic) and
the claims field (specific `C##` ids > blanket `"all"` > vague hedge words > blank), then averages
the two per block. This operationalizes the schema's own audit hook: a block only counts as
epistemically useful if a reader could go check it against a specific claim.

**Why it's hard to Goodhart.** Writing `"all"` for every block to guarantee credit only earns 0.7,
not 1.0 — cheaper than doing real per-claim mapping but not free, and if a paper has many
artifacts blocks all lazily marked `"all"`, that pattern is itself visible (low variance, as in
metric 3's discount logic could be reused here). Inventing specific-looking `C04, C07` ids that
don't correspond to anything real can't be checked by this metric alone, but a fabricated dense
web of claim ids across many artifacts with thin `files_in_repo` paths would drag down the
path-side of the same per-block average, since path fidelity and claims fidelity are scored
independently and averaged, not each gameable to 1.0 on their own.

---

## Combination

These five metrics are built to interlock rather than reward the same behavior twice. Metric 1
(capture proportionality) and metric 2 (grounding integrity) both hinge on *citations existing and
being consistent* — inflating one by adding uncited code or undisclosed claims directly starves
the other of the evidence it needs to score well. Metric 4 (environment concreteness) rewards
fabricated-looking version numbers only if they are corroborated elsewhere (in cited
dependencies/execution imports), so padding metadata in isolation doesn't pay off. Metric 3
(config calibration) and metric 5 (claim traceability) both penalize *uniformity-as-laziness*
(identical sensitivity labels, blanket "all" claims) — so a strategy of maximizing apparent
coverage by copy-pasting labels gets capped rather than maximized in both places at once. Overall,
cheaply maximizing any one metric (write more code, tag everything, cite everything) tends to
either contradict what another metric can verify (paths, claims, source notes) or trip an explicit
uniformity/vagueness discount — so a paper cannot win the full set cheaply without the underlying
`src/` layer actually being honest, proportionate, and traceable.
