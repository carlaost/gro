# Stage 1 critique — `11_dataset`

Judge: metascientist + incentive designer. Artifact: `data/dataset.md` (+ `data/preprocessing.md`).

## One-line verdicts + rank

- **agent1 — RANK 1.** Full five-axis coverage (access, specificity, discrepancy, genre-scope, ethics)
  with the tournament's cleanest interlock; its **Genre-Scope Fidelity** ("generated in this study"
  must be backed by a real accession in the header) is a genuinely orthogonal Goodhart check no rival has.
- **agent2 — RANK 2.** Same five axes, but sharpened against *surface* gaming: **Provenance Specificity
  Density** is word-count-normalized (kills verbosity padding) and **Consent/Ethics Grounding** explicitly
  caps vague-boilerplate ("ethically approved") at 0.3. Most surface-resistant set.
- **agent3 — RANK 3.** Strong and distinctive — its **Preprocessing Traceability Proportional to
  Raw-Data Claims** is the single most science-aware metric proposed, and its discrepancy metric actually
  *sums the N column* — but it drops the ethics/consent axis entirely and leaves a 0.7 free-pass floor.
- **agent4 — RANK 4.** Has a unique axis (**External-Dataset Reference Specificity**) but is the weakest
  on soundness (claim-vs-code mismatch, scoping leak) and hard-constraint fidelity, and drops both ethics
  and preprocessing.

## WINNERS: agent1, agent2

---

## Per-winner critique + stage-2 directions

### agent1 (rank 1)

Strengths: five metrics that genuinely interlock (the Combination essay is not hand-waving — fabricating
specificity to win metric 2 creates the unreconciled totals metric 3 punishes; padding ethics buzzwords
to win metric 5 fails the identifier-shaped IRB regex and the genre check). **Genre-Scope Fidelity** is
the standout: tying a "generated in this study" claim to a verifiable accession ID in the block header
is a cheap-to-check, hard-to-fake honesty signal that directly targets hallucinated provenance.

Sharp critique + stage-2 directions:
1. **Access-Tier Honesty over-penalizes legitimate single-tier data.** The shape doc explicitly notes a
   genuinely all-open dataset is valid, yet metric 1 caps single-tier claims at 0.5 as "uncontrasted
   oversimplification." A truly-open dataset that *says so with a data-layer qualifier* ("processed matrix
   is open, no controlled component exists") should not be docked like a lazy blanket "available." Split
   the 0.5 bucket: reward single-tier + explicit data-layer qualifier higher than bare "available." Borrow
   agent2's qualifier-token idea (raw/processed/metadata/individual-level) to make this distinction.
2. **Discrepancy Self-Audit only counts table rows, never sums the N column.** che26's real, flagged
   mismatch ("12 cohorts don't sum to 18 studies / 24 datasets") is an *arithmetic* mismatch, not a
   row-count one. Metric 3 currently compares `len(included_cohorts_table)` to stated totals — it would
   miss the exact positive example the shape doc holds up. Add summed-`N`-column reconciliation (agent3
   and agent4 both do this) alongside the row-count check.
3. **No preprocessing-traceability axis.** Genre-Scope Fidelity checks only the *negative* (secondary
   reuse must not fabricate raw QC); it never rewards a primary-generation paper for *owing and supplying*
   a QC trail proportional to its raw-data claims. Add agent3's Metric 4 idea (QC-vocabulary specificity
   scaled to raw-data claims, deduped so keyword-stuffing one term is capped).

### agent2 (rank 2)

Strengths: the most deliberately anti-surface set. **Provenance Specificity Density** normalizes hits by
word count so a verbose-but-vague block cannot win by length — directly answering the brief's "verbosity
loses" warning. **Consent/Ethics Grounding** is the only proposal that actively detects and caps generic
assurance language ("appropriate approvals were obtained") at 0.3 while giving near-full credit to the
legitimate secondary-reuse deferral ("not applicable at the review level").

Sharp critique + stage-2 directions:
1. **The access-tier construct is ambiguous between two things.** Metric 1 rewards a clause that pairs an
   access word with a data-layer qualifier — so "raw reads are controlled access" scores 1.0 as a single
   qualified clause, even though it names only *one* tier. That conflates genuine open-vs-gated
   *differentiation* (agent1/agent4's target) with per-clause qualification. Decide which you measure, or
   score both: qualifier presence *and* whether the document as a whole contrasts an open component
   against a gated one. State the construct explicitly.
2. **Discrepancy Self-Audit uses row count only.** Same defect as agent1 — it compares `len(table)` to
   intro numbers and never sums the `N` column, so it would not catch che26's actual arithmetic mismatch.
   Add N-column summation.
3. **Preprocessing is under-measured.** Genre-Consistent Structural Completeness rewards mere *presence*
   of a preprocessing section/pointer for primary genre (binary 1.0/0.0) and never scores QC specificity.
   Upgrade to scale by distinct QC dimensions covered (agent3's approach), so "we did QC" scores below a
   real thresholds/normalization/batch-correction trail.
4. **Density saturation constant (1 identifier / 15 words) is asserted, not justified.** A short, dense,
   correct block could be unfairly capped or a padded one flattered. Calibrate against the two worked
   examples (huu25, che26) and report where each lands.

---

## Why the losers lost

**agent3 (rank 3).** The strongest loser, and its **Preprocessing Traceability Proportional to Raw-Data
Claims** is a metric both winners should steal — it is the most science-aware single metric in the pool,
targeting the exact steps (filtering thresholds, batch correction, exclusions) most likely to introduce
bias, and it dedups QC vocabulary so keyword-stuffing is capped. Its **Cross-Statement Consistency**
metric is also more rigorous than either winner's, actually summing the cohort table's `N` column rather
than just counting rows. It lost on coverage and calibration, not cleverness: it drops the ethics/consent
axis entirely, even though the shape doc names ethical provenance (IRB numbers, consent framework) as a
load-bearing fact for primary human-subjects data and gives che26's explicit "not applicable at the
review level" as a positive signal — a four-metric set with no ethics metric leaves that axis unscored.
Its Preprocessing metric also hands secondary-reuse work a flat 0.7 "genre-appropriate silence" score,
a generous floor that is closer to a free pass than the interlocking penalties the brief rewards.

**agent4 (rank 4).** Its **External-Dataset Reference Specificity (EDRS)** is a genuinely novel axis
nobody else covers — rewarding traceable identifiers for borrowed datasets. But it is the weakest set on
the axes the brief weights most. **Compute soundness:** the AFCD "Why it's hard to Goodhart" claims
boilerplate is filtered "by requiring the field text to reference an accession ID, a number, or an IRB
token," but `_is_substantive` implements only a length≥15 check plus a short placeholder blacklist — a
long empty sentence passes, so the stated defense is not in the code. Its ATDR appends
`intro_paragraph + raw_text` (the whole document) as one access blob for the secondary genre, defeating
the per-statement scoping it claims as its Goodhart defense. **Hard-constraint tension:** EDRS scores a
hard 0.0 when no external-datasets section exists, but the shape doc says external datasets are
warranted-only and self-contained work is legitimate — this penalizes good papers that simply used no
external data, exactly the "correctly absent must not be penalized" case. It also drops both the ethics
and preprocessing axes, leaving the thinnest genuine coverage of the four.
