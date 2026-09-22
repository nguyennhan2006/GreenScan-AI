# ADR 0003 — Qualitative verification, bilingual extraction, legal layer wired in

Status: accepted — 2026-08-14

## Context

Measured against `data/real_cases` (four cases with a regulator's or court's
decision behind them), the pipeline scored **0/4** while the unit suite was
**162/162 green**. The two numbers did not contradict each other: nothing in the
suite ran the real pack, because the pack-to-pipeline mapping lived in an
untracked script outside the package.

```text
BNY-2022   expected CONTRADICTED  →  INSUFFICIENT_EVIDENCE
DWS-2023   expected CONTRADICTED  →  PARTIALLY_SUPPORTED     ← sign inverted
KDP-2024   expected CONTRADICTED  →  claim never extracted
KLM-2024   expected CONTRADICTED  →  INSUFFICIENT_EVIDENCE
```

## Decisions

### 1. Contradiction is not only arithmetic

The verifier could reach `CONTRADICTED` through a numeric relative-error test or
a giảm/tăng direction flip, and through nothing else. Every adjudicated case is
refuted qualitatively — by omission, a coverage gap, a control gap, or a court
holding a statement misleading — so none of them could ever be detected.

A cue lexicon (`configs/stance_cues.yaml`, bilingual) now decides a passage's
stance when arithmetic cannot. Order of authority, strongest first:

```text
1. numeric      two comparable figures agree or disagree
2. qualitative  a cue phrase refutes or confirms the claim
3. direction    the trend stated in the claim is reversed in evidence
4. similarity   nothing decided; fall back to how related the text is
```

Constraints the lexicon is built to hold:

- **Phrases, not bare negation.** "không"/"not" are too common to carry a
  refutation; "không thực hiện"/"did not" are not.
- **Silence is never refutation.** A cue fires only on text that is present.
- **A cue needs a connection to the claim** — lexical overlap, or the passage
  being an authority's finding. Without that guard any document containing
  "inadequate" would refute anything retrieved beside it.

### 2. Stance is computed before status, not after

Status used to be derived from retrieval scores alone, with per-passage stances
attached afterwards. That let the two disagree, which is how DWS-2023 came back
`PARTIALLY_SUPPORTED` on the strength of a passage saying the firm "lacked
formalized controls to verify use of the ESG Engine" — a refutation counted
towards support because nothing ever asked the passage which side it was on.

### 3. A language model may point, never decide

`verification.llm_stance: "off"` by default. Set to `on_ambiguous` it rules only
on passages the deterministic layers declined, always sets
`requires_llm_review`, and returns `None` on any provider failure so the
deterministic verdict stands. Arithmetic remains `deterministic/none` in
`configs/routing.yaml`.

### 4. The taxonomy is bilingual, and gains a type the corpus needed

`configs/taxonomy_vi.yaml` → `configs/taxonomy.yaml`, with `vi`/`en` term lists
kept separate so the extractor can report which lexicon fired. Scope and metric
lexicons moved out of `claim_extractor.py` into the same file; the scorer's
private copy of the vague-term list is gone, so there is one lexicon rather than
three drifting ones.

`esg_process_integration` is new. Two of the four adjudicated cases are claims
about *how a firm works* rather than about a physical outcome, and they route to
the `disclosure` legal issue rather than the green taxonomy — the question BNY
and DWS were actually charged under.

### 5. The retrieval threshold does not get to decide evidence does not exist

`minimum_score` conflated "nothing speaks to this claim" with "nothing *looked
like* this claim". KLM-2024 is the second: the claim shares no content word with
the court finding that held it misleading. A floor (`retrieval.floor_k`) keeps
the best candidates below the cut, marked `below_threshold`.

The asymmetry this creates is deliberate and matches the domain: **a weak
passage may carry a refutation from an authority; it may never establish
support.** Every SUPPORTED and PARTIALLY_SUPPORTED path still gates on the raw
score.

### 6. The legal layer runs inside the pipeline

`check_applicable_law` is now a step in `OrchestratorAgent.PLAN`, producing one
record per claim in `AnalysisResult.legal_checks` and gate **G7**. Scope limits
carried by adjudicated sources (settlement without admission, "do not generalize
this finding") travel from document metadata onto the evidence and into the
record — without them "a regulator found this statement incomplete, settled
without admission" degrades into "the company lied".

`CLAIM_TYPE_TO_ISSUE` was written against a vocabulary the extractor never
emits, so five of eight real claim types fell through to the `green_taxonomy`
default and were checked against the wrong instrument. It now keys on the
taxonomy's own types.

An inconclusive legal check does **not** block a release: the layer returns
`INSUFFICIENT_EVIDENCE` both when no instrument governs a claim and when one
governs it but its text was never extracted, and those are coverage gaps, not
findings about a company. Only `NOT_MATCH`/`PARTIAL_MATCH` — a rule that
actually ran and failed — holds a release for review.

### 7. One source of truth for severity

Three copies existed: the rubric's `severity:` block, `ReviewSettings`
thresholds, and a hardcoded ladder in the scorer. Only the hardcoded one had any
effect, so editing either documented copy silently changed nothing. Bands now
come from the rubric file and a rubric that cannot state its bands raises.

### 8. The real pack gates CI

`quantum_gw.evaluation.real_cases` puts the adjudicated pack on the same footing
as the synthetic golden set, with `quantum-agent evaluate-real` and
`tests/test_real_case_evaluation.py`. Status, per-evidence stance and risk band
are reported **separately** — they fail independently and one blended number
hides which moved. Control cases are listed and never scored: a Vietnamese
report with no adjudication has no right answer, and inventing one is exactly
what the pack forbids.

## Result

```text
                              before   after
verification status accuracy    0.00    1.00
evidence stance accuracy         n/a    1.00   (8/8, incl. the CONTEXT_ONLY negative)
legal check coverage             0.00    1.00
risk band accuracy               n/a    0.50
```

## Consequences

- The cue lexicon is a maintained asset. New refutation vocabulary means editing
  `configs/stance_cues.yaml`, and every addition risks false positives on the
  golden set — `tests/test_qualitative_stance.py` holds the guards.
- **Risk band is 0.50 and is deliberately not being tuned.** DWS-2023 scores 70
  against a gold CRITICAL (75+) and KDP-2024 scores 65. Closing a 5- and a
  10-point gap by adjusting weights against four frozen cases is overfitting the
  evaluation set, which `DATASET_AUDIT_V2.md` §5 and `TRAINING_READINESS.md`
  both rule out. The gap is a measurement, and it moves when the adjudicated
  corpus reaches the 100–200 claims those documents call for.
- Four adjudicated claims cannot support any statistical claim about accuracy.
  1.00 here means "the four known failure shapes are handled", not "the system
  is accurate".
