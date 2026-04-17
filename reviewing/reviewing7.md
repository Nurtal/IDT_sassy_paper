---
IEEE BIBM 2026 — Simulated Selection Pass (Final Committee Decision)

Paper: OISA: A Formalism-Agnostic Orchestration Architecture for Composing
       Published Immune Models Without Modification
Track: Bioinformatics Methods and Applications (Regular Paper)
Submission type: Full paper (target length 8 pages, IEEE two-column)
Review date: 2026-04-17
Round: Selection / camera-ready verification (follow-up to Round 5)
---

## 0. Purpose of this review

The paper was previously evaluated in Round 5 (see `reviewing6.md`,
2026-04-16) and received *Accept with Minor Revisions* (aggregate 4.2/5).
Six camera-ready items were raised: R1-N1, R1-N2, R2-4, R3-1, R3-2, M5.

This pass has two goals:

  1. **Data / paper consistency audit.** Re-run the published consistency
     test suite against the current manuscript and the data shipped in
     the repository (`results/issl_14d/`, `results/sensitivity_analysis.json`).
  2. **Selection simulation.** Apply the IEEE BIBM 2026 track criteria
     (originality, technical soundness, significance, clarity, relevance,
     reproducibility) and issue a final selection decision, treating this
     as the last committee pass before camera-ready submission.

---

## 1. Data consistency audit

### 1.1 Method

The repository ships `tests/test_paper_consistency.py` — a pytest suite
that loads pre-computed ISSL checkpoints (5 replicates × 56 ticks =
280 JSON files under `results/issl_14d/`) plus the sensitivity grid in
`results/sensitivity_analysis.json`, and asserts that every quantitative
claim in the paper matches the data within the declared tolerance. The
suite covers 8 thematic groups (checkpoint structure, viral kinetics,
immune dynamics, causal ordering, paper claims, sensitivity grid,
adapter line count, paper structure).

### 1.2 Result

```
pytest tests/test_paper_consistency.py -v
============================== 51 passed in 0.06s ==============================
```

All **51 / 51** consistency checks pass. Specifically:

| Check class                    | Tests | Status |
|--------------------------------|:----:|:------:|
| Checkpoint structure           |   8  |   ✓    |
| Viral kinetics (§V-B.4)        |   6  |   ✓    |
| Immune dynamics (§V-B.4)       |   7  |   ✓    |
| Causal ordering                |   2  |   ✓    |
| Paper numerical claims         |  11  |   ✓    |
| Sensitivity consistency        |   7  |   ✓    |
| Adapter line count (§V-A)      |   4  |   ✓    |
| Paper structure                |   6  |   ✓    |

Every numeric statement in the Abstract, the §V-B.4 trajectory table,
the §V-B.5 sensitivity table (Table VIII), and the Table V adapter-line
claims matches the shipped data. In particular:

  - V(tick 0) ≈ 1.54×10³ copies/mL across all 5 replicates (paper §V-B.4
    footnote) — verified.
  - Median peak V ≈ 9.0×10⁶ copies/mL at day ~2.25 (paper §V-B.4,
    Abstract) — verified, relative error < 10 %.
  - V(day 13.75) < 0.1 % of peak in every replicate — verified.
  - n_immune(day 1) ensemble range within [4, 7] (paper §V-B.4 table) —
    verified.
  - n_immune(day 13) ensemble range within [40, 53] (paper §V-B.4 table
    and Abstract) — verified.
  - Sensitivity reference row (κ = 3.5×10⁻⁷, scaling = 100) peak V
    within 10 % of stochastic-replicate median peak — verified.
  - Sensitivity monotonicity: V(day 14) strictly decreases as scaling
    increases at fixed κ — verified.
  - Isolated-ODE baseline V(day 14) ≥ every coupled V(day 14) (CTL can
    only reduce viral load) — verified.

**Conclusion:** the paper's quantitative content is internally
consistent with the data artefacts shipped in the repository. No
Round-6 "data does not match paper" concern is raised.

---

## 2. Status of Round 5 minor-revision items

The Round 5 committee closed with six camera-ready items. Verification
against the current manuscript (`docs/OISA_paper_IEEE_BIBM2026.md`,
478 lines) and repository state gives:

| ID     | Item                                                                                                | Status                     |
|--------|-----------------------------------------------------------------------------------------------------|----------------------------|
| R1-N1  | Add "ODE-side" / "approximate single-model" qualifier to §V-B.5 title or opening sentence           | **NOT APPLIED**            |
| R1-N2  | Expand "ens. range" in Abstract so a stand-alone reader sees it = N = 5 stochastic replicates        | **NOT APPLIED**            |
| R2-4   | Confirm `schemas/issl_v1.schema.json` (Box 1) is published in the repository; else fix dangling URI | **NOT APPLIED**            |
| R3-1   | Add one sentence in §V-B.5 noting that *model-internal* parameter sensitivity is out of scope        | **NOT APPLIED**            |
| R3-2   | Brief note on CC3D ensemble parallel-execution model (concurrent vs. sequential on N cores)          | **NOT APPLIED**            |
| M5     | Complete author names, affiliations, contributions                                                   | **NOT APPLIED**            |

Grep evidence:

  - `grep -n "ODE-side\|model-internal\|out of scope\|concurrent" docs/OISA_paper_IEEE_BIBM2026.md`
    returns zero matches.
  - `docs/OISA_paper_IEEE_BIBM2026.md:5` still reads
    `*[Author names and affiliations to be completed prior to submission]*`.
  - `find . -name "issl_v1*" -not -path "*/venv/*"` returns nothing —
    the schema file referenced in Box 1 (`schemas/issl_v1.schema.json`)
    is not present in the repository tree. The data-availability
    statement at the end of the paper does not list it either.

None of the Round 5 minor items are blockers for scientific acceptance;
they are all camera-ready fixes. However, they **must** be cleared
before final submission, as R2-4 (dangling schema URI) and M5 (missing
authorship) are hard IEEE BIBM conference requirements.

---

## 3. Selection simulation against IEEE BIBM 2026 criteria

IEEE BIBM 2026 (per the track call and prior-edition reviewer guidance)
scores regular papers on six axes, each on 1–5:

  1. **Originality / novelty of contribution**
  2. **Technical soundness and rigour**
  3. **Significance / potential impact on bioinformatics & biomedicine**
  4. **Clarity and quality of presentation**
  5. **Relevance to the conference scope (esp. "Computational Systems
     Biology" and "Health Informatics / Digital Twins" tracks)**
  6. **Reproducibility (data + code availability, test coverage)**

Acceptance threshold at BIBM is typically ≥ 3.5 average with no 1-score
on any axis and no unresolved "Major Revision" flag.

### 3.1 Per-axis scoring

| # | Axis                     | Score | Rationale                                                                                                                                                                                                                                                                                                                                                                                   |
|:-:|--------------------------|:-----:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Originality              | **4** | "Zero lines modified" composition of a full spatial CC3D ABM (12 steppables, 90×90×2 grid) with an SBML ODE, plus runtime UQ propagation through a deterministic ODE from a stochastic ABM ensemble, is a genuinely new concrete demonstration for immune digital twins. The architectural ideas (JSON-LD checkpoint, causal DAG, model-derived transfer lag) extend but do not replace Vivarium / SBML-comp; this is honestly scoped. |
| 2 | Technical soundness      | **4** | All 51 consistency tests pass; causal-ordering, monotonicity and clearance assertions verified on ensemble data. Sensitivity grid (Table VIII) is consistent with `sensitivity_analysis.json`. Two residual concerns: (i) §V-B.5 sensitivity uses an ODE-only re-run with *approximate* shifted n_immune — legitimate but insufficiently qualified (R1-N1 not yet applied); (ii) Box 1 ISSL schema URI is still a dangling reference (R2-4). |
| 3 | Significance / impact    | **4** | The cross-formalism composition gap is explicitly identified as the primary barrier to clinical IDT deployment in Laubenbacher 2022/2024 and Niarakis 2024 — three peer-reviewed references the paper correctly cites. A practical, reproducible runtime that lets independently published immune models be composed without rewrite is precisely the infrastructure those reviews call for. Impact is limited by the single use-case (influenza / murine). |
| 4 | Clarity                  | **4** | Well-structured, 7-section IEEE layout, correct use of "Index Terms". §V-B is dense but navigable; disclaimers (validation scope, ensemble-range statistics, spatial-scale mismatch) are placed exactly where a careful reader looks. Minor deductions: Abstract is long (~330 words — BIBM soft cap ~250); "N = 5" acronym in Abstract lacks the "stochastic replicates" gloss (R1-N2). |
| 5 | Relevance                | **5** | Perfect fit for BIBM — paper sits at the intersection of Computational Systems Biology, Biomedical Informatics / Digital Twins, and Methods & Algorithms for Biological Data Analysis. All three 2026 track descriptions list "multi-scale modelling" and "model interoperability" explicitly.                                                                                             |
| 6 | Reproducibility          | **4** | SBML artefact immutable (BIOMD0000000546), ABM artefact pinned to commit 5b7e42c, 67 automated tests in the adapter suite + 51 paper-consistency tests shipped, figures regenerable from ISSL JSON (`figures/generate_trajectory_figure.py`). Gaps: (i) repository URL still placeholder, (ii) schema file `schemas/issl_v1.schema.json` referenced in Box 1 but not shipped, (iii) author-contribution section empty. |

**Aggregate: (4+4+4+4+5+4) / 6 = 4.17 / 5**

### 3.2 Compliance with BIBM hard requirements

| Requirement                                                      | Status                           |
|------------------------------------------------------------------|----------------------------------|
| Regular paper length (≤ 8 pages IEEE two-column)                 | Likely OK (markdown source is within the target once typeset with IEEEtran; recommend a dry compile before submission to confirm). |
| IEEE two-column template (IEEEtran)                              | PENDING — source is Markdown; camera-ready must be produced in IEEEtran LaTeX. |
| Index Terms (not "Keywords")                                     | ✓                                |
| Numbered references [N]                                          | ✓ (20 references)                |
| Author names / affiliations                                      | ✗ (placeholder — M5)             |
| Data and code availability statement                             | ✓ (present, but repository URL placeholder; schema file referenced but missing) |
| Competing-interests statement                                    | ✓                                |
| Double-blind compliance (no author-identifying info in body)     | ✓ (verified: no author name, institution, grant ID, or unique-identifier GitHub handle in body text or figure metadata) |
| Figures submitted at publication resolution                      | ✓ (PDF + PNG present in `figures/`) |
| Ethical statement (N/A for this paper — no human/animal data)    | N/A                              |

### 3.3 Remaining scientific concerns (none blocking)

  - **S1.** The coupled biological trajectory was not re-validated
    *against* the Miao 2010 or Sego 2020 published trajectories (only
    against their own published parameter ranges / numerical bounds).
    This is consistent with the paper's explicit framing
    ("orchestration correctness, not biological prediction") and was
    accepted by the Round 5 committee. Noted for completeness, not
    flagged.
  - **S2.** §V-B.5 sensitivity uses an *ODE-only* re-run with a
    trajectory-shift heuristic for n_immune. Honest enough for a
    framework paper, but R1-N1 fix is required to prevent a
    camera-ready reader from mis-reading the table as a full coupled
    re-simulation.
  - **S3.** Feedback-cycle one-tick delay is discussed (§VI-B) but the
    6 h latency is not itself stress-tested (e.g., by running the same
    composition with GSimT tick = 1 h and comparing). Noted as a
    natural extension, not a blocker.

---

## 4. Committee deliberation (simulated)

Three notional committee members — PC1 (multi-scale computational
biology), PC2 (systems biology standards / SBML-COMBINE), PC3 (ABM /
HPC / computational immunology) — revisit the paper after the Round 5
decision and the consistency audit of §1.

  - **PC1.** "Data audit is clean — 51/51. The Round 5 accept still
    holds. None of the Round 5 minor items are scientific, so the
    paper is ready *scientifically*. What it is not ready for is
    camera-ready submission. I would send it back with a *Conditional
    Accept* tied to the six items, but I would not re-review."
  - **PC2.** "My main Round 5 point (R2-4) remains open: Box 1 cites
    `schemas/issl_v1.schema.json` and it's not in the repo. That
    single fix — ship the JSON Schema file and add it to the data
    availability statement — turns a dangling reference into a
    genuine COMBINE-style contribution. I would not let this through
    unconditional accept without it."
  - **PC3.** "R3-2 — parallel execution model for the N = 5 CC3D
    ensemble — is a one-sentence fix but the kind of thing an HPC
    reviewer flags immediately. Subprocess-level parallelism should
    be stated explicitly (concurrent on separate cores, or sequential
    in a loop). Also confirms that the reported ~50 ms IPC overhead
    per tick is per instance, not per ensemble."

**Consensus:** No scientific regression since Round 5. Data
consistency is fully verified. The six Round 5 camera-ready items
remain the *sole* open issues.

---

## 5. Final selection decision

### 5.1 Score

| Reviewer             | Score | Recommendation        |
|----------------------|:-----:|-----------------------|
| PC1 (multi-scale)    | 4.0   | Accept (conditional)  |
| PC2 (standards)      | 4.0   | Accept (conditional)  |
| PC3 (ABM / HPC)      | 4.5   | Accept                |
| **Aggregate**        | **4.17** | **ACCEPT — camera-ready conditional on the six Round 5 items** |

### 5.2 Decision

**ACCEPT — conditional camera-ready.**

The paper is scientifically ready for IEEE BIBM 2026 publication in
the Bioinformatics Methods and Applications track. The 51-test
consistency suite passes end-to-end; the Round 5 major-revision items
(C1–C4) have been resolved to the committee's satisfaction and have
not regressed. The aggregate score of 4.17 / 5 is comfortably above
the acceptance threshold.

Camera-ready submission is **conditional** on clearing the six items
carried forward from Round 5. These are not sent back for a further
review round; they are camera-ready deliverables verified by the
programme chair before the proceedings cut-off.

### 5.3 Required camera-ready actions

| ID     | Priority  | Action                                                                                                                                                            | Effort |
|--------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----:|
| M5     | Mandatory | Fill author block (names, affiliations, corresponding author, contributions).                                                                                     | 10 min |
| R2-4   | Mandatory | Ship `schemas/issl_v1.schema.json` in the repository and add it to the data-availability statement. If the file will not be shipped, remove the URI from Box 1.    | 30 min |
| R1-N1  | Required  | §V-B.5 opening sentence: add "ODE-side" or "approximate single-model" qualifier; clarify that the n_immune trajectory was *shifted* (not re-simulated).            | 5 min  |
| R1-N2  | Required  | Abstract: expand first occurrence of "ens. range" / "N = 5" to "ensemble range across N = 5 stochastic CC3D replicates".                                           | 2 min  |
| R3-1   | Required  | §V-B.5: add one sentence stating that Miao 2010 / Sego 2020 model-internal parameters (β_a, c_V, ir_prob_scaling_factor) are out of scope for this sensitivity.    | 3 min  |
| R3-2   | Required  | §V-A or §VI-B: add one sentence on the ensemble execution model (e.g., "the N = 5 CC3D instances are launched as concurrent subprocesses on separate CPU cores"). | 3 min  |
| Extra  | Recommended | Fill the repository URL placeholder in the data-availability paragraph. Dry-compile the Markdown source into IEEEtran LaTeX to confirm the 8-page limit.          | 30 min |

Total effort for camera-ready compliance: **≈ 1.5 hours**.

### 5.4 Not required

  - No new experiments.
  - No new figures.
  - No additional review round.
  - No reference-list changes.

---

## 6. One-line summary

**IEEE BIBM 2026 — Bioinformatics Methods and Applications Track —
*ACCEPT* (4.17 / 5), camera-ready conditional on the six Round 5
minor items; data-consistency suite 51 / 51 pass.**

---

*Programme Committee, IEEE BIBM 2026 — Bioinformatics Methods and
Applications Track. Selection pass conducted under double-blind
guidelines; reviewer identities not disclosed. This review
supersedes `reviewing6.md` (Round 5) for camera-ready purposes; no
further re-review is scheduled.*

---

## 7. Camera-ready closure (post-review, 2026-04-17)

All six items listed in §5.3 have been applied to the manuscript
after this review. Status:

| ID     | Action                                                                                       | Applied | Location                                                                                                                      |
|--------|----------------------------------------------------------------------------------------------|:-------:|-------------------------------------------------------------------------------------------------------------------------------|
| M5     | Fill author block and author-contribution section.                                           |   ✓     | Header: "Nathan Foulquier — LBAI (Inserm U1227), Centre de Données Cliniques du CHU de Brest." Author contributions paragraph updated. |
| R2-4   | Ship `schemas/issl_v1.schema.json` and reference it from the data-availability statement.    |   ✓     | `schemas/issl_v1.schema.json` created (Draft 2020-12, covers envelope / continuous_state / discrete_events / export_signals / internal_parameters / watchdog). Listed in data-availability paragraph. |
| R1-N1  | Add "ODE-side" / "approximate single-model" qualifier to §V-B.5.                             |   ✓     | §V-B.5 heading now reads "Parameter Sensitivity (ODE-side, coupling parameters only)"; opening sentence reframed.            |
| R1-N2  | Clarify N = 5 stochastic replicates in Abstract.                                             |   ✓     | Abstract rewording: "reported as *ensemble range across N = 5 stochastic CC3D replicates* (sample min–max, see §V-A)".       |
| R3-1   | State that model-internal parameters are out of scope for the sensitivity analysis.          |   ✓     | New sentence in §V-B.5 explicitly excluding β_a, c_V, δ_Es, ir_prob_scaling_factor, chemotaxis coefficients, max_ck_secrete_infect. |
| R3-2   | Describe the ensemble parallel-execution model.                                              |   ✓     | §V-A "Runtime UQ" paragraph: "N instances are launched by `Sego2020Ensemble` as concurrent OS subprocesses on separate CPU cores … wall-clock cost per tick is max(T_i) rather than Σ T_i". |

### 7.1 Post-edit re-verification

The paper–data consistency suite was re-run after the edits:

```
pytest tests/test_paper_consistency.py -v
============================== 51 passed in 0.05s ==============================
```

No regression. All 51 tests still pass, including the seven
§V-B.5 / Abstract-structure / spatial-scale checks that touch
edited passages.

### 7.2 Residual items

  - The repository URL in the data-availability paragraph remains
    placeholder text (`[repository URL to be added prior to
    submission]`) — to be filled at submission time when the
    double-blind obfuscated URL or the final public repository is
    decided.
  - The manuscript is still in Markdown; camera-ready IEEEtran LaTeX
    typesetting is pending.

All other Round 5 / Round 6 selection-committee items are cleared.
The paper is now ready for IEEEtran camera-ready typesetting and
submission.
