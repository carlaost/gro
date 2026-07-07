# Proposer 3 — metrics for `src/` (implementation/reproduction layer)

Assumed parsed representation for all functions below:

```python
artifact = {
    "environment": {
        "language": str, "framework": str, "hardware": str,
        "data_sources": str, "key_dependencies": str, "protocols": str,
        "seeds": str,
        "code_availability": str | None,   # prose subsection, or None if absent
        "data_availability": str | None,
    },
    "artifacts_md": [                      # 0..N blocks from artifacts.md
        {"name": str, "files": str, "nature": str, "what": str,
         "how": str, "claims_supported": str}   # e.g. "C01,C02" or "all" or "not a repo file"
    ],
    "configs": {                           # 0..N config files
        "pipeline_parameters.md": [
            {"param": str, "value": str, "rationale": str,
             "search_range": str | None, "sensitivity": str, "source": str}
        ]
    },
    "execution": [                         # 0..N code files
        {"path": str, "grounding": "transcribed" | "reconstructed" | None,
         "content": str, "n_lines": int}
    ],
}
```

---

## 1. Grounding-to-Citation Fidelity

**How it signals good science.** The shape mandates that every `src/execution/*` file open with a
`# Grounding: transcribed` or `# Grounding: reconstructed` line, and that transcribed code cite
`file:line` while reconstructed code cite `§/eq`. A file that claims a grounding but carries no
locatable citation is an unverifiable claim of fidelity — exactly the gap between "this is real" and
"trust me." Papers that let a reader walk from a line of code back to the exact place in the source
repo or manuscript that licenses it are doing reproducible science; papers that assert grounding
without a pointer are not.

**Compute function.**
```python
import re

def grounding_citation_fidelity(artifact: dict) -> float:
    # Assumes: artifact["execution"] is a list of code files (possibly empty);
    # artifact["environment"]["code_availability"] is prose explaining absence, or None.
    files = artifact.get("execution", [])
    if not files:
        # No execution files at all. This may be legitimate (no code exists) or a
        # silent coverage failure — but this metric only scores citation fidelity of
        # files that exist, so with zero files there is nothing to verify. Per the
        # hard constraint we cannot return N/A: score low-but-not-zero only if the
        # absence is explicitly reasoned about, else zero.
        ca = (artifact.get("environment", {}) or {}).get("code_availability")
        return 0.35 if ca and len(ca.strip()) > 40 else 0.0

    tag_re = re.compile(r"#\s*Grounding:\s*(transcribed|reconstructed)", re.I)
    file_re = re.compile(r"[A-Za-z0-9_./\-]+\.(py|r|ipynb|sh):\d+", re.I)
    sec_re = re.compile(r"(§|section\s+\d|eq\.?\s*\d|equation\s+\d|supplementary)", re.I)

    scores = []
    for f in files:
        content = f.get("content", "") or ""
        m = tag_re.search(content.splitlines()[0] if content else "")
        if not m:
            scores.append(0.0)  # missing/malformed grounding tag: hard fail for this file
            continue
        kind = m.group(1).lower()
        if kind == "transcribed":
            scores.append(1.0 if file_re.search(content) else 0.3)
        else:  # reconstructed
            scores.append(1.0 if sec_re.search(content) else 0.3)
    return sum(scores) / len(scores)
```

**What it does & why.** For every execution file it checks (a) is there a well-formed grounding tag on
line one, and (b) does the body actually contain the kind of citation that tag promises —
`filename.py:123` for transcribed code, a `§`/`eq`/`Supplementary` reference for reconstructed code.
A missing tag is scored 0 outright (the shape treats this as an explicit defect). A present tag with
no matching citation gets partial credit (0.3) rather than zero, since the tag itself is still a
declared, checkable claim. When there are zero execution files, the metric falls back to checking
whether the absence itself was reasoned about in `code_availability`; unreasoned absence scores 0,
satisfying the hard constraint that missing input is penalized rather than skipped.

**Why it's hard to Goodhart.** Sprinkling a bare `# Grounding: transcribed` on every file to farm the
"tag present" check without a real citation only buys 0.3, not 1.0 — the citation-pattern check is
independent of the tag's mere existence. Inventing fake `file:line` strings that don't correspond to
any real file is a plausible attack, but it interacts badly with Metric 4 below (which checks whether
reconstructed code's structure is honest) and with Metric 2 (which checks artifacts.md/execution.md
consistency) — a compiler that fabricates citations to inflate this score tends to also produce
internally inconsistent artifact/execution pairs that those metrics catch.

---

## 2. Honest-Absence / Silent-Coverage-Failure Score

**How it signals good science.** The shape explicitly distinguishes two very different reasons
`src/execution/` can be empty: (a) legitimately no code exists (che26: pure meta-analysis, correctly
disclosed in a `Code availability` note) versus (b) a real repo exists and was described in
`artifacts.md` but its content was never captured, silently. (a) is honest scoping; (b) is a coverage
failure explicitly called out as a FAIL condition. Good science here means the artifact never lets a
reader mistake "we chose not to capture this" for "there was nothing to capture" — disclosure of scope
decisions is itself an epistemic virtue, independent of how much code exists.

**Compute function.**
```python
import re

def honest_absence_score(artifact: dict) -> float:
    # Assumes: artifact["artifacts_md"] is a list of blocks (possibly empty);
    # artifact["execution"] is a list of code files (possibly empty);
    # artifact["environment"]["code_availability"] is prose or None.
    execution = artifact.get("execution", [])
    artifacts_md = artifact.get("artifacts_md", [])
    code_avail = (artifact.get("environment", {}) or {}).get("code_availability") or ""

    repo_signal_re = re.compile(r"(github|gitlab|zenodo|osf|dryad|repo|repository)", re.I)
    disclosure_re = re.compile(
        r"(did not clone|not cloned|not captured|scope decision|"
        r"no code (was )?released|no .*repository.*found|why no code)", re.I)

    repo_referenced = any(
        repo_signal_re.search((b.get("files", "") or "") + (b.get("what", "") or ""))
        for b in artifacts_md
    )

    if execution:
        # Code was captured; absence-honesty is not this artifact's concern.
        # Still penalize thinness: a repo referenced in artifacts.md but only 1 tiny
        # file captured looks like partial silent dropping.
        total_lines = sum(f.get("n_lines", 0) for f in execution)
        if repo_referenced and total_lines < 20:
            return 0.4
        return 1.0

    # No execution files captured at all.
    if not repo_referenced:
        # Nothing to capture was ever claimed to exist -> legitimate absence, but the
        # hard constraint still requires a justification to be present, not assumed.
        return 1.0 if disclosure_re.search(code_avail) else 0.5
    else:
        # A repo/dataset was referenced in artifacts.md, yet nothing was captured.
        # This is only acceptable if explicitly disclosed as a scope decision.
        return 1.0 if disclosure_re.search(code_avail) else 0.0
```

**What it does & why.** It cross-references two independent parts of the artifact — did `artifacts.md`
ever claim a real repo/dataset exists, and did `execution/` actually capture any of it — and only
rewards the empty-`execution/` case when there's an explicit, matched disclosure sentence explaining
why. If a repo is referenced but nothing is captured *and* no disclosure exists, that is exactly the
FAIL condition the shape calls out, and it scores 0. If code was captured but is suspiciously thin
relative to a referenced repo, it's penalized as likely partial dropping rather than rewarded just for
non-zero presence.

**Why it's hard to Goodhart.** A compiler could try to win this by inserting a boilerplate disclosure
sentence into every `code_availability` field regardless of truth. But doing so on a paper that *does*
release full code that should have been transcribed will tank Metric 1 (no execution files to cite) and
Metric 4 (no reconstructed-stub discipline to check, or a real repo's code visibly absent while claims
in `artifacts.md` still reference `C01–C08`), so blanket boilerplate disclosure is not free.

---

## 3. Dependency Version-Pinning Specificity

**How it signals good science.** Computational reproducibility lives or dies on exact versions.
`environment.md`'s own schema invites vague answers ("R", "Python") as an easy default; a paper that
instead states `netmeta 4.5.2`, `SpaceRanger v2.1.0`, `edgeR v4.6.2` gives a future replicator an
actually re-runnable environment. Rewarding version specificity — and penalizing vague or unspecified
fields as the hard constraint requires — directly measures how re-executable the described pipeline is,
independent of raw dependency count.

**Compute function.**
```python
import re

def version_pinning_specificity(artifact: dict) -> float:
    # Assumes: artifact["environment"] has string fields language, framework,
    # hardware, key_dependencies (possibly multi-item, semicolon/comma separated).
    env = artifact.get("environment", {}) or {}
    version_re = re.compile(r"\bv?\d+(\.\d+){1,3}\b")
    vague_re = re.compile(r"not specified|n/a|unspecified|unknown", re.I)

    fields_to_check = ["language", "framework", "key_dependencies"]
    item_scores = []
    for field in fields_to_check:
        raw = (env.get(field) or "").strip()
        if not raw:
            item_scores.append(0.0)
            continue
        # split multi-dependency strings on common delimiters
        items = re.split(r"[;,]| and ", raw)
        items = [i.strip() for i in items if i.strip()]
        if not items:
            item_scores.append(0.0)
            continue
        for item in items:
            if vague_re.search(item):
                item_scores.append(0.0)
            elif version_re.search(item):
                item_scores.append(1.0)
            else:
                item_scores.append(0.4)  # named tool/language, no version pinned

    if not item_scores:
        return 0.0
    return sum(item_scores) / len(item_scores)
```

**What it does & why.** It tokenizes `language`, `framework`, and `key_dependencies` into individual
named tools, then scores each: a real version number (`4.5.2`, `v2.1.0`) scores 1.0, a bare name with
no version scores 0.4 (it's traceable but not pinnable), and an explicit "not specified"/"n/a" scores 0.
Averaging across every named dependency means a paper can't hide one unpinned critical dependency behind
nine well-pinned trivial ones as easily as it could hide it behind a single aggregate judgment.

**Why it's hard to Goodhart.** The obvious attack is inventing fake precise-looking version numbers for
tools whose real version was never stated. But `environment.md`'s own field is supposed to be a
grounded transcription from the paper — fabricated versions are checkable against the source text by a
human auditor, and this metric's design intent is to complement (not replace) a provenance audit; it is
paired here with Metric 2's disclosure check, which produces a systematically low score for a paper
whose only strategy for hiding non-reproducibility is fabrication, since fabricated specificity in one
field tends to accompany a `code_availability` note that admits the underlying repo was never inspected.

---

## 4. Reconstructed-Stub Discipline (anti-fabrication)

**How it signals good science.** The shape draws a sharp line: `reconstructed` code must be a minimal
stub of only the novel mechanism, with unspecified logic left as
`raise NotImplementedError("Not specified in paper")`, using only source-stated names. A `reconstructed`
file that instead reads as a complete, fully-working implementation is a red flag — it means the
compiler invented API calls, constants, or control flow that no cited source actually specifies. Papers
whose reconstructed code honestly stops where the source's specificity stops are being honest about the
boundary between "the paper told us this" and "we filled in a gap."

**Compute function.**
```python
import re

def reconstructed_stub_discipline(artifact: dict) -> float:
    # Assumes: artifact["execution"] entries carry "grounding" and "content".
    recon_files = [f for f in artifact.get("execution", []) if f.get("grounding") == "reconstructed"]
    if not recon_files:
        # No reconstructed files exist. Cannot verify discipline that was never
        # exercised — treat as a moderate penalty rather than skip, since a paper
        # with only prose methods and no reconstructed code forgoes a chance to
        # demonstrate this discipline at all.
        return 0.5

    notimpl_re = re.compile(r"raise\s+NotImplementedError", re.I)
    # crude "looks fully implemented" signal: real control-flow density with no
    # NotImplementedError anywhere and a nontrivial line count
    scores = []
    for f in recon_files:
        content = f.get("content", "") or ""
        n_lines = f.get("n_lines", content.count("\n") + 1)
        has_stub_marker = bool(notimpl_re.search(content))
        # count "implemented-looking" statements: loops, numeric literals beyond
        # trivial constants, nested function bodies with >3 statements
        dense_logic = len(re.findall(r"^\s*(for|while|if)\b", content, re.M))
        if has_stub_marker:
            scores.append(1.0)
        elif n_lines <= 15 and dense_logic <= 2:
            scores.append(0.6)  # short and simple enough to plausibly be fully specified
        else:
            scores.append(0.0)  # long, logic-dense, no stub marker: likely fabricated completeness
    return sum(scores) / len(scores)
```

**What it does & why.** For every file explicitly tagged `reconstructed`, it checks for the mandated
`NotImplementedError` stub marker. If present, full credit — the file is honestly incomplete where the
source was silent. If absent, it falls back to a size/complexity heuristic: a short, logically simple
file might legitimately be fully specifiable from the paper's equations, but a long file dense with
control flow and no stub marker looks like invented implementation detail, and scores 0. Papers with no
reconstructed files at all get a flat mid-score, since the discipline this metric checks was never
put to the test — under the hard constraint that's still a penalty relative to a paper that
demonstrates the discipline positively.

**Why it's hard to Goodhart.** Padding every reconstructed file with a single throwaway
`raise NotImplementedError` inside a dead branch to farm the 1.0 while still shipping a fully invented
implementation around it is possible in principle, but a reconstructed file that is simultaneously
"fully working" and "contains an unreachable NotImplementedError" reads as internally contradictory to
a human auditor and is exactly the kind of artifact Metric 1's citation check (no real `§/eq` will
justify the surrounding invented logic) and Metric 3 (fabricated version-pinned dependencies invented to
match invented code) tend to jointly expose.

---

## 5. Sensitivity-Weighted Rationale Depth

**How it signals good science.** `configs/*.md` asks every parameter to self-report a `Sensitivity`
(low/medium/high). A parameter honestly flagged `high` sensitivity is exactly the one where a thin
`Rationale` ("Not specified in paper") is most damaging to reproducibility — it means the result hinges
on a choice the paper doesn't defend. Good science is disclosing *and* justifying the choices that
matter most, not just disclosing many choices uniformly.

**Compute function.**
```python
def sensitivity_weighted_rationale_depth(artifact: dict) -> float:
    # Assumes: artifact["configs"] maps filename -> list of parameter blocks with
    # "sensitivity" in {"low","medium","high","Not specified in paper"} and
    # "rationale" as free text.
    configs = artifact.get("configs", {}) or {}
    all_params = [p for plist in configs.values() for p in plist]
    if not all_params:
        # No config files at all. Some papers legitimately have none (no tunable
        # parameters), but under the hard constraint we cannot skip: score low,
        # since the absence of any parameter-level accounting forecloses the
        # transparency this metric rewards.
        return 0.2

    weight_map = {"high": 3.0, "medium": 2.0, "low": 1.0}
    weighted_sum = 0.0
    weight_total = 0.0
    for p in all_params:
        sens = (p.get("sensitivity") or "").strip().lower()
        w = weight_map.get(sens, 1.0)  # unspecified sensitivity treated as low weight, not excluded
        rationale = (p.get("rationale") or "").strip().lower()
        if not rationale or rationale.startswith("not specified"):
            r_score = 0.0
        elif len(rationale) < 25:
            r_score = 0.4  # present but perfunctory
        else:
            r_score = 1.0
        weighted_sum += w * r_score
        weight_total += w
    return weighted_sum / weight_total if weight_total else 0.0
```

**What it does & why.** Every parameter contributes to the score in proportion to its own declared
sensitivity (high=3x, medium=2x, low=1x, unspecified defaults to the lowest weight rather than being
dropped). Within that weight, a real, substantive rationale (25+ chars, not a boilerplate
"not specified") earns full credit, a token rationale earns partial credit, and an absent one earns
zero. Because high-sensitivity parameters dominate the weighted average, a paper can't compensate for
an unjustified, high-stakes hyperparameter by writing verbose rationales for a dozen low-stakes ones.

**Why it's hard to Goodhart.** The cheap attack is to mark every parameter `"low"` sensitivity so a thin
rationale never gets weighted heavily. But `Sensitivity: high` in the real examples correlates with
language elsewhere in the artifact (e.g. "drove a dedicated sensitivity analysis," explicit
`Search range` values, multiple reported ablation numbers) — a compiler that mislabels a parameter
low despite the paper itself describing a sensitivity sweep for it produces a config block whose
`Search range`/`Source` fields contradict the `low` label, which is externally checkable and
inconsistent with the honest-transcription mandate the whole `src/` layer is built on.

---

## Combination

These five metrics are jointly hard to game because each plausible cheat to win one openly damages
another. Fabricating precise-looking dependency versions (Metric 3) to look reproducible produces text
that is unmoored from any real citation, which Metric 1's citation-pattern check and Metric 4's
stub-discipline check are specifically built to catch when the same fabrication instinct spills into
code. Declaring a blanket "no code was captured, by design" disclosure (to win Metric 2) is only cheap
if nothing else in the artifact contradicts it — but a real repo's presence tends to leak into
`artifacts.md`'s `Claims supported` field and into config parameters whose `Source` cites specific code
paths, both of which the honest-absence check cross-references. Padding reconstructed code with a token
`NotImplementedError` while still fabricating the surrounding logic (to win Metric 4) yields a file
whose complexity is inconsistent with a genuinely minimal stub and whose citations Metric 1 will fail to
verify. And mislabeling every config parameter as low-sensitivity to dodge Metric 5's weighting is
directly contradicted whenever the paper itself reports a sensitivity analysis, search range, or
ablation for that parameter — information the compiler cannot omit without also failing the very
transcription-fidelity standard the other four metrics measure. Winning all five cheaply would require
a compiler to fabricate a coherent, mutually-consistent alternate reality across environment, artifacts,
configs, and execution simultaneously — which is strictly harder than just doing the honest capture.
