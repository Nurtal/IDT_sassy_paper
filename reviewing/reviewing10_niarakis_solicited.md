---
Solicited Expert Review
Reviewer:   Prof. Anna Niarakis
            Center for Integrative Biology of Toulouse (CBI Toulouse),
            Université de Toulouse / CNRS
            (profile: cbi-toulouse.fr/membre/niarakis-anna/)
            Co-coordinator, Immune Digital Twins EU initiative
            Co-author: Laubenbacher/Niarakis Forum Report (2024 npj SBA)
                       Niarakis et al. 2024 on IDT challenges (npj SBA 10:141)
Paper:      OISA — A Formalism-Agnostic Orchestration Architecture for
            Composing Published Immune Models Without Modification
Author:     Nathan Foulquier (LBAI, Inserm U1227, UBO; CDC CHU de Brest)
Solicited:  2026-04-21 — returned 2026-04-23
Round:      External expert review (independent, not part of the
            BIBM 2026 programme committee rotation). Reviews the N=20
            camera-ready candidate (main.pdf, 8 pages, 2026-04-23
            rebuild after N=5 → N=20 rerun).
---

## Foreword — positioning and scope

Since I moved to the CBI Toulouse group I have been coordinating work
on immune digital twins under the logical/Boolean-modelling thread,
in partnership with the groups of Laubenbacher, Helikar, Glazier, and
Flobak. Two of my recent papers ([13] Forum report, [14] npj SBA
2024 on IDT applications/limitations/challenges) are cited in this
manuscript as framing for the IDT roadmap. I confirm the citation
is accurate and non-controversial; I therefore do not recuse but I
flag the relationship here for transparency.

I read this manuscript specifically against three challenges I have
spent the last two years flagging in public talks and review articles:

  (i)   the shortage of *working, reproducible* heterogeneous-formalism
        IDT prototypes beyond PhysiBoSS 2.0 (cancer) and the
        Moreau-PhysiCell COVID-19 work;
  (ii)  the absence of a shared wire format for state exchange between
        ODE, ABM, and logical models — the "SBML for composition" gap;
  (iii) the fact that credibility, in the CURE sense, has to be
        instrumented at the *composition* level, not just inside each
        individual model.

OISA speaks directly to all three. My overall assessment is that this
is one of the most mature orchestration-substrate proposals I have
seen since Vivarium, and it is the first I am aware of that combines
(a) a published SBML ODE, (b) an unmodified published CC3D spatial
ABM, and (c) runtime UQ propagation in a single 8-page,
artefact-complete conference paper.

## 1. What the paper delivers (as I read it)

Three primitives, plus a reference implementation:

1. **ISSL (Internal Simulation State Log).** A JSON-LD checkpoint
   with six sections: envelope, continuous_state, discrete_events,
   export_signals, internal_parameters, watchdog. The `ci_95` field
   on every `export_signal` and `continuous_state` entry carries
   runtime uncertainty bounds as a first-class schema feature — not
   as a post-hoc wrapper. JSON Schema Draft 2020-12 is shipped and
   used to validate every checkpoint.

2. **Configuration graph.** YAML / JSON-LD specification of models,
   edges, transfer_models, global_clock, calibration, and
   wildcard_namespace. Edges carry either a `constant:N` lag or a
   `model:ID` lag (a genuinely new design primitive — the lag
   between compartments becomes itself a model output, not a free
   parameter).

3. **Orchestrator engine.** Nine components: ISSL ingestion, signal
   router, temporal scheduler (GSimT), causal DAG resolver,
   watchdog, biological-plausibility constraint engine, IPC manager,
   UQ aggregator, calibration bridge. The causal chain at the 24 h
   boundary (`ABM.emit → ODE.accept → ODE.step → ODE.emit`) is the
   soundness guarantee.

**Reference coupling.** Miao 2010 (BioModels BIOMD0000000546,
systemic ODE) + Sego 2020 (CC3D 4.8.0, 12 steppables, 90×90×2,
@5b7e42c, the *full* spatial model not a surrogate). Zero lines of
either published model are changed. Adapter code ≈ 300 LOC.

**Ensemble.** N = 20 parallel CC3D instances. The Abstract reports
the bounds as 5th/95th percentile, which is statistically defensible
at that sample size. (I note the manuscript under an earlier revision
reported sample min–max with N = 5 — the upgrade to N = 20 between
the first review pass and this one addresses the first concern a
reviewer in my position would raise. It is also visible in the
paper-data consistency suite, which now tests N = 20 against
widened immune ranges: n_immune(day 1) ∈ [2, 10] and n_immune(day 13)
median 57 ∈ [41, 64]. These are the right numbers.)

## 2. Assessment

### 2.1 Originality — **5 / 5**

In the context of IDT orchestration substrates specifically:

- **Runtime UQ in the wire format, not as a separate analysis layer.**
  I have not seen this in Vivarium (Agmon 2022), in PhysiBoSS 2.0
  (Ponce-de-Leon 2023), in BioModels/SED-ML, or in COMBINE/OMEX
  archives. The usual pattern is to carry point values, run an
  offline Monte Carlo, and staple error bars on post-hoc. OISA
  carries `(median, ci_95, unit, provenance)` as the minimum wire
  unit; this changes the ergonomics of credibility instrumentation.

- **Model-derived transfer lags (`lag: "model:ID"`).** This is a
  small but important idea that I want to emphasise. The lag between
  lung interstitium and draining lymph node is itself a biological
  quantity — flow, transit, residence time — that we should be
  modelling, not parameterising as a constant. OISA promotes this to
  a first-class graph-edge concept. For anyone building a human IDT
  with more than two compartments, this primitive is immediately
  useful.

- **Composition-level plausibility engine.** The
  `_N_IMMUNE_TO_CTL_PER_ML = 100` scaling factor as an *auditable,
  ISSL-recorded decision* is the right answer to a problem I have
  flagged repeatedly: two individually valid models can be composed
  into something biologically nonsensical if the bridge is silent
  about unit / scale / phenotype-mapping decisions. OISA forces
  those decisions into the record.

### 2.2 Technical soundness — **4.5 / 5**

The engineering is careful. Specific strengths:

- Causal DAG resolution at the GSimT 24 h boundary is formally
  correct and empirically confirmed by the causal-ordering checks
  in the consistency suite.
- The 6 h back-edge delay in the ODE → ABM → ODE cycle is justified
  on causality grounds; the timescale argument (hours-to-days being
  the relevant influenza window) is sound.
- The watchdog + divergence_score + PAUSE semantics are the right
  safety layer; the 0.15 threshold is reported with rationale.

Remaining concerns, none blocking:

**T1 — Spatial-scale mismatch.** The ODE represents a systemic
compartment (V_total ≈ 1 mL); the ABM is a single tissue patch
(~10⁻³ mL). κ absorbs this implicitly; the Limitations section is
honest about it and prescribes explicit
V_tissue = V_systemic × (V_patch / V_total) normalisation for
predictive deployment. I would like one extra sentence quoting the
empirical κ range over which the 51-test consistency suite continues
to pass; this would bound the "κ absorbs the mismatch" claim
quantitatively.

**T2 — Single-disease validation.** Murine influenza A only. I
understand the conference-length constraint; a journal extension
should add at least one second coupling to demonstrate generality.
PhysiBoSS/MaBoSS as a third formalism class (Boolean/logical) under
the ISSL envelope would be the natural next target — and would
directly engage my group's interests, which I acknowledge as a
positive bias.

**T3 — Sensitivity coverage.** The 3×3 coupling-parameter grid is
adequate at conference length. Internal parameters of Miao 2010 and
Sego 2020 are correctly excluded (they are calibrated upstream). A
full Sobol/Morris global sensitivity is deferred to future work,
which is acceptable for BIBM and necessary for a journal version.

### 2.3 Significance for the IDT community — **5 / 5**

I want to be emphatic here. The IDT community has a prototype gap.
We have excellent roadmaps (Laubenbacher 2022 npj DM, 2024 Nature
Computational Science; the 2024 Forum report; the 2024 Frontiers
Digital Health use-cases paper; the 2024 npj SBA challenges paper).
What we do not have, in sufficient numbers, is *working,
reproducible, formalism-agnostic compositions of two independently
published, independently calibrated immune models*. OISA is exactly
that, with artefacts that let the rest of us iterate on the
architecture rather than re-derive it.

For the Immune Digital Twins initiative specifically, the ISSL
envelope is a candidate for adoption as a reference wire format. I
would like to raise this at our next working-group meeting (with
the author's permission).

### 2.4 Clarity — **4.5 / 5**

The revision compiled to 8 pages is dense but readable. Figure 2
(trajectory) with N = 20 replicate shading is now clearly
interpretable. The Validation section separates three distinct
claims (viral kinetics, spatial immune recruitment, emergent
temporal lag) and quantifies each.

Two clarity items:

- **CL1 — Causal-ordering chain.** The sequence
  `ABM.emit → ODE.accept → ODE.step → ODE.emit` appears in the
  Fig. 1(b) caption but is not stated explicitly in §IV-C main text.
  Adding one sentence would help readers who skim the figure.

- **CL2 — ISSL schema table.** The six ISSL sections are described
  in inline prose. I understand this was done to fit 8 pages. If a
  compact 6-row table can be restored by trimming two sentences of
  §II related work, it would improve readability — the ISSL is the
  paper's central contribution and deserves tabular emphasis. This
  is a preference, not a requirement.

### 2.5 Reproducibility — **5 / 5**

Exemplary, and a model for BIBM submissions in this area.

- JSON Schema (Draft 2020-12) shipped — envelope is
  machine-checkable.
- 1,120 ISSL checkpoint files (20 replicates × 56 ticks) shipped,
  not a sanitised subset.
- Paper–data consistency suite (51 tests) verifies every numeric
  claim in the manuscript against the actual ISSL records;
  I spot-checked and the suite is green at N = 20.
- Adapter unit tests: 67 (ODE 23 + ABM 20 + BloodTransit 8 +
  integration 16).
- Pinned provenance: CompuCell3D 4.8.0, Miao 2010 from BioModels
  unmodified, Sego 2020 at commit @5b7e42c.

The only residual item is the `[repository URL to be added prior to
submission]` placeholder. I would also recommend a `CITATION.cff`
and an archival DOI (Zenodo) at the time the URL is filled in — not
blocking, but strongly encouraged.

---

## 3. Positioning against adjacent work

I concur with the Table I positioning against SBML, CellML, SED-ML,
Vivarium, PhysiBoSS 2.0, with two nuances worth adding in §II:

- **Vivarium.** Agmon *et al.* 2022 deliberately leaves checkpoint
  schemas and runtime UQ to the user; OISA's design decision —
  "standardise the wire format and bake UQ into it" — is a
  conceptual advance, not a reimplementation. One sentence in §II-A
  would make this explicit rather than implicit in the comparison
  table.

- **PhysiBoSS 2.0.** Ponce-de-Leon *et al.* 2023 couples PhysiCell
  (ABM) with MaBoSS (Boolean) inside a single executable binary.
  OISA's out-of-process design (separate subprocesses, file-based
  IPC) is the correct decomposition for IDT deployment where models
  come from different labs in different Python versions, but it
  trades latency for dependency isolation. Naming this tradeoff
  explicitly in §II-B would help readers coming from the PhysiBoSS
  community.

- **Adjacent logical/Boolean work.** The logical-modelling community
  (GINsim, MaBoSS, CellNOptR) is not yet coupled in via OISA. I
  would welcome a short forward-looking sentence in the Conclusion
  noting that the ISSL envelope, with its `formalism` dispatch tag,
  can accommodate logical models as a third formalism class — this
  is the natural extension and would signal the architecture's
  generality to the CBI Toulouse and IDT-EU audiences.

---

## 4. Itemised recommendations for camera-ready

Numbered for traceability. Only N1 is a hard pre-submission
requirement.

- **N1 (required).** Fill the repository URL placeholder in the
  Data / Code section. Archive a tagged release on Zenodo and cite
  the DOI.

- **N2 (recommended).** Add one sentence in §IV-C stating the causal-
  ordering chain `ABM.emit → ODE.accept → ODE.step → ODE.emit`
  explicitly in main text (it is currently only in the Fig. 1b
  caption).

- **N3 (recommended).** One sentence in §VI Limitations quoting the
  empirical κ range over which the 51-test consistency suite still
  passes — this bounds the "κ absorbs the volume mismatch" claim.

- **N4 (recommended).** One sentence in §II-A explicitly contrasting
  OISA with Vivarium on checkpoint schema and runtime UQ
  propagation.

- **N5 (optional).** Restore the six-row ISSL section inventory as
  a compact table if page budget allows, offset by trimming two
  sentences of §II related work.

- **N6 (optional, forward-looking).** One clause in the Conclusion
  signalling that ISSL accommodates a third formalism class
  (Boolean / logical, e.g., GINsim / MaBoSS), indicating the
  architecture's generality.

- **N7 (nit).** Define "GSimT" at first use; currently it appears
  in the Abstract without expansion.

- **N8 (nit).** Table VII column header — clarify "[range]" as
  "[min–max]" (or "[p5–p95]" depending on what is actually plotted)
  to distinguish from IQR which appears in the Abstract.

---

## 5. Scoring

| Axis                      | Score | Notes                                    |
|---------------------------|:----:|-------------------------------------------|
| Originality               | 5.0  | Three new primitives; runtime-UQ wire format is the standout. |
| Technical soundness       | 4.5  | κ range + single-disease scope caveats.   |
| Significance / relevance  | 5.0  | Fills a prototype gap in IDT work.        |
| Clarity                   | 4.5  | 8-page fit cost one useful table; causal chain buried in caption. |
| Reproducibility           | 5.0  | Schema + 1,120 ISSL files + 118 tests.    |
| **Aggregate**             | **4.8 / 5** |                                    |

## 6. Recommendation

**Strong Accept** for IEEE BIBM 2026.

Beyond the conference decision, three forward-looking points:

1. **Journal companion.** I strongly encourage a longer companion
   paper in *npj Systems Biology and Applications* (where the Forum
   Report and the 2024 challenges paper both appeared). §IV-C and
   §V-B would benefit from the space the conference format does not
   permit, and the IDT community would read it there.

2. **IDT-EU initiative engagement.** I would be pleased to introduce
   the OISA design to the IDT-EU working group (logical-modelling
   thread). The ISSL envelope is a candidate for a reference wire
   format in cross-lab IDT prototypes. This is a follow-up
   proposal, not a review condition.

3. **Third-formalism extension.** A demonstration coupling a
   logical/Boolean model (e.g., a MaBoSS cell-cycle or innate-
   signalling network) through ISSL into the Miao / Sego pipeline
   would close the current "ODE + ABM only" framing and would be
   natural for the BIBM/ISMB community. I would be delighted to
   collaborate on this.

— Prof. Anna Niarakis (simulated reviewer persona)
  CBI Toulouse / IDT-EU / Laubenbacher–Niarakis Forum
  Review returned: 2026-04-23
