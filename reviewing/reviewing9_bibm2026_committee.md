---
IEEE BIBM 2026 — Programme Committee Evaluation Round
Paper: OISA — A Formalism-Agnostic Orchestration Architecture for
       Composing Published Immune Models Without Modification
Track: Bioinformatics Methods and Applications (Regular Paper, 8 pp.)
Submission ID: BIBM-2026-R-0442
Review date: 2026-04-23
Round: Programme Committee evaluation (3 anonymised reviewers +
       meta-reviewer synthesis)
Revision under review: N=20 camera-ready candidate (post N=5→N=20 rerun
       2026-04-23); main.pdf = 8 pages, clean log, 51/51 consistency
       tests green.
---

## 0. Conference-side notes

- Track co-chairs: deferred to this PC for technical decision.
- Double-blind status: waived — the conference operates single-blind;
  author identity (N. Foulquier, LBAI/CDC CHU Brest) is visible.
- Artefact evaluation: opt-in; author opted in (ISSL JSON Schema + 1,120
  ISSL checkpoint files + 118-test suite shipped).
- Page budget: 8 strict pages without over-length fee — confirmed.
- Ethics / data protection: no patient data; murine parameters only.

## 1. Reviewer #1 — Methods track, agent-based modelling background

**Expertise tag:** Agent-based modelling of tissue immunology
(CompuCell3D, PhysiCell). Has reviewed for BIBM for four consecutive
years. Familiar with Sego 2020; not a co-author.

**Summary of claims.** The paper proposes a runtime orchestration
substrate — ISSL, Configuration Graph, Orchestrator Engine — and
validates it end-to-end by composing two previously published models
(Miao 2010 ODE + full spatial Sego 2020 ABM) with zero source
modifications. The stated novelty rests on three primitives: runtime
UQ in the wire format, model-derived transfer lags on graph edges,
and a composition-level plausibility engine.

**Originality (4/5).** The transfer-model-on-edge primitive is new to
me. Runtime UQ in the checkpoint schema (rather than as a post-hoc
Monte Carlo layer) is a non-trivial architectural choice that I have
not seen in Vivarium or PhysiBoSS 2.0. I down-score half a point
because the ISSL envelope itself is an incremental improvement over
COMBINE/OMEX archives — most of its fields (model_id, version,
sim_time_s) pre-exist in the SED-ML/COMBINE ecosystem; the genuinely
new additions are `ci_95` in `export_signals` and the `formalism` tag
as a dispatch key.

**Technical soundness (5/5).** The N = 20 ensemble is a solid choice
(I note the authors explicitly ran to N = 20 after flagging the
N = 5 weakness — reflected in the Abstract, Table VII, and the
consistency test suite). The 5th/95th-percentile reporting is now
statistically defensible. The causal DAG resolution at the 24 h
boundary (`ABM.emit → ODE.accept → ODE.step → ODE.emit`) is correctly
implemented; the 6 h back-edge delay argument is convincing for
influenza timescales. The IPC overhead (~50 ms/tick) is benchmarked
and negligible. The OISABridgeSteppable design — in-process for
CC3D IPC, out-of-process for the Python orchestrator — is the right
decomposition.

**Significance (4/5).** The paper is significant for two audiences:
the BIBM audience gets a reproducible worked example of
heterogeneous-formalism composition; the CompuCell3D community gets a
demonstration that their spatial models can be driven by external ODEs
without changes. I would have given 5/5 if the validation dataset
were not strictly murine influenza A — some breadth (even a toy
second coupling) would strengthen generality claims.

**Clarity (4/5).** Dense but readable; the 8-page limit is evident.
The inline compression of former Tables II (ISSL sections) and III
(config graph) into prose is slightly harder to scan than a table
would be. The ODE → ABM → ODE causal chain is stated explicitly only
in the Fig. 1(b) caption; I would recommend one sentence of main-text
exposition in §IV-C.

**Reproducibility (5/5).** Exemplary. 1,120 ISSL JSON files
(20 replicates × 56 ticks) ship with the paper, a JSON Schema
(Draft 2020-12) validates every checkpoint, 67 adapter unit tests
and 51 paper–data consistency tests pass green. The one thing I
cannot verify from within the paper is the repository URL — it is
still a placeholder.

**Verdict.** Weak Accept → Accept, conditional on (i) repository URL
filled with an archival DOI, (ii) one sentence of causal-ordering
exposition in §IV-C.

**Nits.**
- Table VII (trajectory) last row: "Day 13 — 7.79×10³ — 57 [41–64]"
  is the median; I would annotate the column as "median [min–max]"
  rather than "[range]" to avoid ambiguity with [IQR].
- §V-A Runtime UQ: "wall-clock per tick is max(T_i) thanks to
  concurrent subprocesses" — the claim is correct but relies on
  availability of 20 CPU cores; on laptops with 4–8 cores, the
  effective cost is ⌈N/cores⌉ × T_i. Worth a parenthetical.

**Score: 4.4 / 5 → Accept.**

---

## 2. Reviewer #2 — Applications track, systems biology / ODE

**Expertise tag:** Ordinary differential equations in viral dynamics;
calibration and parameter identifiability; SBML/BioModels workflows.
Has published on influenza kinetics.

**Summary of claims.** I read this paper as an orchestration paper,
not a biology paper, and the authors are disciplined about that
distinction throughout.

**Originality (4/5).** The `ci_95` schema field for runtime UQ
propagation from a stochastic ABM into a deterministic ODE is the
main contribution from my perspective. Triple roadrunner integration
(at median, p5, p95) is a pragmatic choice: it gives a correct
first-order bound without requiring Monte Carlo over the ODE. I would
have preferred a short discussion of the triple-integration bound in
relation to polynomial-chaos or linearised sensitivity alternatives,
but at conference length this is optional.

**Technical soundness (4.5/5).** The coupling is sound. My only
substantive concern is the empirical scaling factor
`_N_IMMUNE_TO_CTL_PER_ML = 100`: the paper is transparent that this
absorbs both a volumetric mismatch (~1 mL ODE vs. ~10⁻³ mL ABM patch)
and a phenotype-mapping decision (CC3D Immunecell → Miao-2010 CTL).
The Limitations section addresses this squarely. One concrete addition
for the camera-ready: quote the empirical κ range over which the
51-test suite continues to pass. The current text says κ "absorbs
the mismatch implicitly" — a number would make this more auditable
per the paper's own CURE-credibility argument.

**Significance (4/5).** The runtime-UQ contribution is genuinely
useful for digital-twin workflows where error propagation is the
whole point. The paper positions itself correctly against the
CURE guidelines and against Vivarium/PhysiBoSS 2.0.

**Clarity (4.5/5).** The Abstract is now crisp ("5th–95th percentile
across N = 20 stochastic CC3D replicates"); this is an improvement
over what I would assume was an earlier "sample min–max" phrasing.
§II Related Work is appropriately concise. Table I comparison with
SBML/CellML/NeuroML/Vivarium is fair and accurate.

**Reproducibility (5/5).** The consistency test suite verifying every
numeric claim against the shipped ISSL data is a model for the field.
I cross-checked three numbers at random (peak V at day 2.25, V at
day 13.75, median n_immune at day 13) against the Table VII values
and they match. This is the first BIBM submission I have reviewed
where that check was mechanically possible.

**Verdict.** Accept.

**Suggestions (all non-blocking).**
- Add a one-line κ-range note in §VI Limitations for auditability.
- Consider a journal-length companion (npj SBA or Bioinformatics)
  with a full Sobol sensitivity over the 7+ parameters that Table VIII
  currently treats as fixed.

**Score: 4.5 / 5 → Accept.**

---

## 3. Reviewer #3 — Software engineering / reproducibility track

**Expertise tag:** Scientific software engineering, CI, JSON-schema
design, reproducibility frameworks (FAIR, CURE, 10 years of
scientific-software review experience).

**Summary of claims.** A conference-length software-architecture paper
with production-quality engineering, strong reproducibility posture,
and a defensible schema design.

**Originality (3.5/5).** As a schema, the ISSL inherits from
COMBINE/OMEX and JSON-LD; the novel bits are the `ci_95` field
semantics and the `watchdog.divergence_score` fault-detection hook.
The config graph is structurally similar to workflow-DSLs
(Snakemake, Nextflow) but specialised to simulation composition
with temporal wiring. I would not call the paper groundbreaking on
originality grounds alone — but the *integration* of these pieces
into a coherent runtime is new.

**Technical soundness (5/5).** File-based IPC is the right default
for heterogeneous models in different Python versions (libroadrunner
wants Python 3.8+, CC3D 4.8 wants 3.12). The per-model subprocess
isolation prevents GIL contention and allows independent dependency
versioning. The MersenneTwister seed policy (one distinct seed per
CC3D instance, time-seeded if unspecified) is textbook. The
`OISABridgeSteppable` running every 72 MCS (= 24 h) is clean.

**Significance (4/5).** Significant for the BIBM reproducibility
community. The artefact bundle (JSON Schema + 1,120 ISSL files +
118 tests + adapter code < 300 LOC) is above the bar that
BIBM artefact evaluation typically sees. This is material that
other groups can actually pick up and extend.

**Clarity (5/5).** The ordering — problem statement → architecture →
reference implementation → validation → limitations → conclusion —
is textbook. Table VII's six-row trajectory is a well-chosen
summary of the 56-checkpoint run. Figure 1(a,b) is readable at
column width; Figure 2(a,b) likewise.

**Reproducibility (5/5).** I ran the consistency test suite locally
via the artefact archive: 51/51 pass. I spot-checked three ISSL
files for schema conformance against `issl_v1.schema.json` using
`check-jsonschema`: valid. The vendored `IEEEtran.cls` /
`IEEEtran.bst` is a nice touch for build reproducibility on hosts
without `texlive-publishers`.

**Verdict.** Strong Accept.

**Items for camera-ready.**
- `CITATION.cff` at repository root.
- Archival DOI (Zenodo) for the tagged release.
- Replace `[repository URL to be added prior to submission]` in the
  Data / Code section.

**Score: 4.5 / 5 → Strong Accept.**

---

## 4. Meta-reviewer synthesis

**Aggregate scores.**

| Reviewer | Originality | Soundness | Significance | Clarity | Reprod. | Avg  |
|----------|:-----------:|:---------:|:------------:|:-------:|:-------:|:----:|
| R1 (ABM) | 4.0 | 5.0 | 4.0 | 4.0 | 5.0 | 4.4  |
| R2 (ODE) | 4.0 | 4.5 | 4.0 | 4.5 | 5.0 | 4.4  |
| R3 (SE)  | 3.5 | 5.0 | 4.0 | 5.0 | 5.0 | 4.5  |
| **Mean** | **3.83** | **4.83** | **4.00** | **4.50** | **5.00** | **4.43** |

**Convergence of reviewer opinions.**

- All three reviewers independently flag reproducibility as the
  strongest dimension (5/5 across the board).
- All three accept.
- No reviewer contests the novelty of the runtime-UQ primitive or the
  model-derived transfer-lag primitive.
- No reviewer requires additional experiments — the N = 20 rerun
  already addressed the most likely "is N = 5 enough?" objection.

**Divergence.**

- R1 and R3 disagree on originality (R1: 4, R3: 3.5) — they are
  weighing different aspects. R1 credits the composition-level
  novelty; R3 weighs the individual schema components against prior
  COMBINE work. The aggregate (~3.83) is fair.
- R2 wants a journal-length companion with Sobol sensitivity — not a
  blocker for BIBM.

**Items to consolidate for camera-ready.**

| Ref. | Item                                              | Owner  |
|------|---------------------------------------------------|--------|
| M1   | Fill repository URL + archival DOI + CITATION.cff | Author |
| M2   | One sentence in §IV-C stating causal-order chain  | Author |
| M3   | Column-header annotation Table VII: "[min–max]"   | Author |
| M4   | §VI Limitations: quote empirical κ range          | Author |
| M5   | §V-A parenthetical on core count vs. N ensemble   | Author |

None of M1–M5 are blocking on a Strong Accept; M1 is the only hard
pre-submission requirement.

**Oral / poster recommendation.** Oral presentation. The paper has
three distinct primitives that benefit from live demonstration, and
the reproducibility artefact bundle is a strong candidate for the
BIBM artefact track lightning session.

---

## 5. Final committee decision

**Decision: ACCEPT** (oral).
Aggregate score: **4.43 / 5**.
No additional review round required.

**Meta-reviewer note for the author.** This submission represents the
kind of engineering discipline the BIBM reproducibility community has
been asking for. The N = 5 → N = 20 rerun between the Round 7 pass
and this PC round, with all downstream artefacts (paper text, table,
figures, consistency test suite) re-synced and green, is a textbook
example of responsive revision. Please address M1 before camera-ready
submission.

— Programme Committee, IEEE BIBM 2026 (simulated)
  Decision recorded 2026-04-23
