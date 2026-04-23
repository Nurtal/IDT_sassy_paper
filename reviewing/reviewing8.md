---
IEEE BIBM 2026 — External Expert Review
Reviewer persona: Prof. Anna Niarakis
                  (Sorbonne Université / GenHotel — EA 3808, Univ. Évry;
                  Immune Digital Twins initiative; co-author of
                  Laubenbacher/Niarakis 2024 Forum Report and Niarakis
                  2024 npj SBA review of IDTs)
Paper: OISA — A Formalism-Agnostic Orchestration Architecture for
       Composing Published Immune Models Without Modification
       (single-author: N. Foulquier, LBAI/CDC CHU Brest)
Review date: 2026-04-23
Round: External expert solicited review (independent of committee passes
       3–7). Revision reviewed: 8-page IEEEtran camera-ready candidate.
---

## Preamble — conflict of interest and perspective

I declare a conflict-relevant prior engagement: the author cites two of
my recent papers ([13] Forum report, [14] Niarakis *et al.* 2024 on
IDT limitations and challenges) as framing for the IDT roadmap. That
framing is accurate and non-controversial, so I do not recuse; but the
reader should know that my review is therefore informed by the
challenges I spelled out in those papers — specifically: (i) the
scarcity of truly *coupled* heterogeneous-formalism IDT prototypes
beyond PhysiBoSS; (ii) the lack of interoperability standards for
state exchange between ODEs, ABMs, and logical/Boolean models; and
(iii) the absence of credibility instrumentation at the composition
level, not just at the single-model level. I read this paper primarily
to evaluate whether it advances these three fronts.

Short answer: **yes, on (i) and (ii); partially on (iii); and it does
so with a level of engineering discipline that the field has been
sorely missing.**

---

## 1. Summary of what the paper actually delivers

OISA is a three-part architecture for composing published immune
models without rewriting them:

1. **ISSL** — a JSON-LD checkpoint format that wraps any model's state
   in a formalism-tagged envelope with six sections (envelope,
   continuous_state, discrete_events, export_signals,
   internal_parameters, watchdog). Crucially, every `export_signal`
   carries a `ci_95` pair alongside the point value, so runtime
   uncertainty is a first-class citizen, not a post-hoc add-on.

2. **Configuration graph** — a YAML/JSON-LD declarative wiring file
   (models, edges, transfer_models, global_clock, calibration,
   wildcard_namespace). Edges carry either `constant:N` or `model:ID`
   transfer lags — the second being a *lightweight transfer model*
   that computes delay dynamically from upstream ISSL signals. This is
   a genuinely novel design primitive.

3. **Orchestrator** — nine components (signal router, temporal
   scheduler with GSimT, causal DAG resolver, watchdog, constraint
   engine, IPC manager, UQ aggregator, calibration bridge, ISSL
   ingestion). Runtime UQ is implemented via a rolling ensemble of
   N=5 parallel CompuCell3D subprocesses.

The reference implementation couples Miao 2010 (SBML BIOMD0000000546,
systemic influenza ODE) with the *full* Sego 2020 CompuCell3D spatial
ABM (12 steppables, 90×90×2 grid, commit @5b7e42c). Zero lines of
either published model are changed. Adapter code is ~300 LOC. The
14-day coupled run is reproduced from 280 ISSL checkpoint files in
`results/issl_14d/` and is accompanied by a 51-test paper–data
consistency suite that, per the repository log, passes.

The emergent behaviours — immune temporal lag preceding viral peak by
~1.25 days and CTL-mediated clearance acceleration — are reported as
*validation of orchestration correctness*, explicitly not as
biological predictions. The author is disciplined about this
distinction throughout.

---

## 2. Assessment against IEEE BIBM evaluation axes

### 2.1 Originality (5/5)

I have read and co-authored roughly the same set of IDT reviews that
frame this paper, and I can confirm the novelty claim is defensible.
Three specific points raise this above the baseline:

- **Runtime UQ propagated at every checkpoint through a cross-
  formalism boundary.** To my knowledge, no existing composition
  framework — not Vivarium, not PhysiBoSS 2.0 — does this as a
  standard schema field. Error bars on a coupled ODE+ABM trajectory
  are usually a post-hoc offline Monte Carlo artefact. Here they are
  in the wire format.

- **Model-derived transfer lags on edges.** The blood transit transfer
  model is a small but conceptually important idea. It acknowledges
  that the lag between compartments is itself a biological quantity,
  not a free parameter, and that a composition framework should
  therefore support it declaratively. I have not seen this done
  elsewhere at the orchestration layer.

- **Composition-level plausibility engine.** The `_N_IMMUNE_TO_CTL_
  PER_ML = 100` scaling factor as an auditable, ISSL-recorded
  decision is the right answer to a problem I flagged in the 2024
  npj SBA paper: two individually valid models can be composed into
  something biologically nonsensical if the bridge is silent about
  unit and scale mismatches. OISA makes those decisions visible.

### 2.2 Technical soundness (4.5/5)

The engineering is careful. Specific strengths:

- Causal DAG resolution at the GSimT boundary (ABM.emit → ODE.accept
  → ODE.step → ODE.emit) is formally correct and empirically
  confirmed by the causal-ordering checks in the consistency suite.
- The one-tick back-edge delay in the ODE→ABM→ODE cycle is justified
  on causality grounds, with the 6 h figure placed in context
  (hours-to-days being the relevant influenza timescale).
- Watchdog + divergence_score + PAUSE semantics are defensible as a
  runtime safety layer; the 0.15 threshold is reported with its
  rationale.

Concerns that a reviewer should raise:

**C1 — Ensemble size N = 5 is too small to call it uncertainty
quantification.** The paper is honest about this (the Limitations
section explicitly flags sample min–max vs. [2.5, 97.5]-percentile),
but the terminology "UQ" throughout the manuscript overstates what
N = 5 delivers. I would prefer either (a) consistent use of
"ensemble-range bounds" language in the Abstract and Contributions,
or (b) a brief note in §IV that the UQ component is architectural
and the reference implementation is a sample of convenience. Budget-
permitting, a single N = 20 confirmatory run would lay the concern
to rest.

**C2 — Volume mismatch between compartments (ODE ~1 mL systemic,
ABM ~10⁻³ mL tissue patch) is acknowledged but not quantitatively
bounded.** The paper states κ "absorbs the mismatch implicitly".
That is fine for an orchestration-correctness paper, but a reader
from the IDT community will want to know: at what magnitude of
mismatch does the absorption assumption break? A single sentence
quoting the observed κ range over which the 51-test consistency
suite still passes would help.

**C3 — Sensitivity sweep is a 3×3 grid over two coupling parameters
only.** The paper is transparent that internal parameters of Miao
2010 and Sego 2020 are out of scope (they are calibrated upstream),
and defers full Sobol to future work. Acceptable at conference
length; would be a required expansion for a journal version.

### 2.3 Significance and relevance to IDT community (5/5)

This is where I want to be emphatic. The IDT community has a
*prototype gap*: we have roadmaps (Laubenbacher 2022, 2024 Forum),
taxonomies, and application papers (PhysiBoSS 2.0 for cancer immune
response, ABM-ODE hybrids for COVID-19), but very few papers
demonstrate a *working, reproducible, formalism-agnostic composition
of two published, independently calibrated models*. OISA does
exactly that, and the artefacts (JSON Schema, ISSL records,
consistency suite) are the kind of deliverables that let the rest of
the community iterate on the architecture rather than re-derive it.

For the BIBM audience specifically, the paper's relevance is broader
than immunology: the ISSL envelope, the configuration graph, and the
transfer-model primitive are all portable to any
multi-compartment/multi-formalism bioinformatics application.

### 2.4 Clarity (4.5/5)

The revision compiled to 8 pages is dense but readable. The
Validation section (§V-B.4) does a good job separating three
distinct claims — viral kinetics agreement, spatial immune
recruitment, and emergent temporal lag — and quantifies each.
Fig. 2 effectively shows both the deterministic trajectory and the
ensemble spread.

Two minor clarity issues:

**CL1 — The compressed inline descriptions of the ISSL six sections
and the configuration graph six elements (now prose after the
revision) are harder to scan than the original tables.** I understand
they were inlined to meet the 8-page limit. I would suggest *one*
small table (the ISSL six-section inventory) be restored if a single
paragraph of prose can be dropped elsewhere — the ISSL schema is the
paper's central contribution and deserves tabular emphasis.

**CL2 — The causal ordering note `ABM.emit → ODE.accept → ODE.step →
ODE.emit` appears only in Fig. 1(b) caption.** I would add one
sentence in §IV-C stating this explicitly in-text, since it is the
property that makes the whole architecture sound.

### 2.5 Reproducibility (5/5)

Outstanding. The repository ships:

- the ISSL JSON Schema (Draft 2020-12), so the envelope is machine-
  checkable;
- 280 ISSL checkpoint files from the actual run, not a sanitised
  subset;
- a 51-test paper–data consistency suite that verifies every numeric
  claim against the shipped data;
- 67 adapter unit tests (ODE + ABM + BloodTransit + integration);
- pinned versions: CompuCell3D 4.8.0, Miao model from BioModels
  unchanged, Sego model pinned to commit @5b7e42c.

The only residual item — the placeholder `[repository URL to be
added prior to submission]` in the Data/Code section — is a
pre-camera-ready fix and does not affect the review. I would also
ask the author to include a `CITATION.cff` and an archival DOI
(Zenodo) at the time the URL is filled in.

---

## 3. Positioning against the state of the art

The author's Table I positions OISA against SBML, CellML, SED-ML,
Vivarium, and PhysiBoSS 2.0. I concur with that positioning with one
nuance the reviewers may want to see elaborated in §II:

**Vivarium comparison.** Agmon *et al.* 2022 deliberately leaves
checkpoint schemas and runtime UQ to the user. The OISA answer —
*"we standardise the wire format and we bake UQ into it"* — is a
conceptual advance over Vivarium, not a reimplementation of it. The
paper should state this contrast in one sentence rather than leaving
it implicit in the comparison table.

**PhysiBoSS 2.0 comparison.** Ponce-de-Leon *et al.* 2023 couples
PhysiCell (ABM) with MaBoSS (Boolean) inside a single executable.
OISA's design deliberately keeps models in separate subprocesses,
exchanging state through the file system. The tradeoff — higher
latency, much lower coupling — should be named explicitly. For IDT
deployment, where models come from different labs in different
languages, OISA's out-of-process design is the right call.

**Missing reference (minor).** The Heiland *et al.* papers on
PhysiCell/PhysiBoSS OpenMP scaling are adjacent work on ABM
performance, not composition, and can reasonably be omitted at
conference length. No action required.

---

## 4. Itemised comments for camera-ready

Numbered for traceability; not all are blocking.

- **N1 (minor, recommended).** In the Abstract, replace "runtime
  uncertainty bounds" on first use with "ensemble-range bounds
  (N = 5 rolling CompuCell3D replicates)" to avoid overstating the
  UQ claim. The Limitations section already concedes this; the
  Abstract should match.

- **N2 (minor, recommended).** Add one sentence in §IV-C making the
  causal-ordering chain `ABM.emit → ODE.accept → ODE.step → ODE.emit`
  explicit in-text rather than only in the Fig. 1(b) caption.

- **N3 (minor, optional).** Restore the six-row ISSL section
  inventory as a compact table (the shortest of the dropped tables,
  and the one that earns its space). Can be offset by trimming two
  sentences from §III-related-work.

- **N4 (minor, non-blocking).** In §VI Limitations, quote the
  empirical κ range over which the 51-test consistency suite
  continues to pass, so readers have a bound on the "κ absorbs the
  volume mismatch" statement.

- **N5 (pre-submission, required).** Fill the repository URL
  placeholder in the Data / Code section. Archive a tagged release
  on Zenodo and cite the DOI.

- **N6 (minor, optional).** In §II-A, add one sentence explicitly
  contrasting OISA with Vivarium on checkpoint schema and runtime UQ
  propagation. The distinction is currently implicit in Table I.

- **N7 (nit).** The acronym "GSimT" (Global Simulation Time) appears
  many times; I suggest defining it once in Abstract if it must be
  used there, or moving the first use to §IV to keep the Abstract
  legible to non-specialists.

- **N8 (nit).** The Conclusion still ends with "adapter-only
  integration." Consider a single forward-looking clause — e.g.,
  "…opening the door to integrating logical/Boolean regulatory
  models (GINsim, MaBoSS) as a third formalism class under the same
  ISSL envelope." This is a minor framing gesture that signals the
  architecture's generality to the IDT audience.

---

## 5. Scoring (BIBM rubric, 1–5)

| Axis                      | Score | Notes                                  |
|---------------------------|:----:|-----------------------------------------|
| Originality               | 5.0  | Three genuinely new primitives.         |
| Technical soundness       | 4.5  | N = 5, volume normalisation caveats.    |
| Significance / relevance  | 5.0  | Fills a prototype gap in the IDT field. |
| Clarity                   | 4.5  | 8-page fit cost two useful tables.      |
| Reproducibility           | 5.0  | Schema + 280 ISSL files + 51 tests.     |
| **Aggregate**             | **4.8 / 5** |                                  |

---

## 6. Recommendation

**Strong Accept** — with the N1–N8 items above treated as camera-ready
recommendations (N5 is the only hard pre-submission requirement).
This is, in my opinion, the most convincing reproducible demonstration
of heterogeneous-formalism immune model composition that the BIBM
2026 programme is likely to receive. It does not solve the immune
digital twin problem — no paper will — but it puts a well-engineered
orchestration substrate into the hands of the community, with the
schemas, data, and tests needed for others to build on it.

I would be pleased to see this presented at BIBM 2026, and I would
encourage the author to prepare a journal-length companion (npj
Systems Biology and Applications would be a natural fit) in which
Sections IV-C and V-B could be given the space the conference format
does not permit.

— Anna Niarakis (simulated)
  Immune Digital Twins initiative, Laubenbacher/Niarakis Forum
  2026-04-23
