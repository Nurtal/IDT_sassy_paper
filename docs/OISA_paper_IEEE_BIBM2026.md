# Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling

**The Orchestrated Immune Simulation Architecture (OISA)**

*[Author names and affiliations to be completed prior to submission]*

---

## Abstract

Computational immunology has produced sophisticated mechanistic models of individual immune compartments, yet these remain siloed: ODE and agent-based models (ABMs) cannot be composed across formalism boundaries without bespoke re-engineering, and no runtime architecture supports the multi-organ representations that immune digital twins require. We propose OISA — the Orchestrated Immune Simulation Architecture — comprising three components: (i) the Internal Simulation State Log (ISSL), a formalism-agnostic JSON-LD interface emitted at each checkpoint by any model type; (ii) a declarative configuration graph specifying models as nodes and inter-compartmental signal flows as directed edges with optional transfer-model lags; and (iii) an orchestrator engine providing global clock synchronisation, causal ordering, uncertainty propagation, and biological plausibility enforcement. We demonstrate OISA on a four-compartment murine immune ontogeny pipeline (bone marrow → blood transit → thymus → peripheral lymph nodes), validating causal ordering, uncertainty propagation, and biological plausibility against published murine data. No biological novelty is claimed; the pipeline serves as a reference implementation for framework validation. OISA operationalises the CURE extensibility and automation guidelines at the multi-model scale, enabling any OISA-compliant model to be substituted into a composition without modifying its peers.

**Index Terms:** immune digital twins, multi-scale modelling, model composition, agent-based models, ordinary differential equations, interoperability, computational immunology

---

## I. Introduction

Immune-mediated diseases are inherently multi-compartmental phenomena. Rheumatoid arthritis traces to haematopoietic stem cell programming in the bone marrow before manifesting in the synovial joint; sepsis is a systemic dysregulation spanning blood, bone marrow, and multiple peripheral tissues; type 1 diabetes involves thymic selection failures and peripheral tolerance breakdown. No single model formalism can faithfully represent all these scales — ODEs are natural for large, well-mixed progenitor pool dynamics, while ABMs are necessary where stochastic single-cell fate decisions dominate, as in thymic TCR-mediated selection. The literature has consequently produced a collection of high-quality compartment-specific models that cannot communicate with one another.

Two bodies of prior work address adjacent problems. The COMBINE standards ecosystem (SBML [6], CellML [3], SED-ML [16]) provides portable representations for individual models but addresses intra-formalism composition only: models must be expressed in the same declarative format, ruling out ABMs written in Python or Julia. The CURE guidelines [17] define what properties a credible model should exhibit — Credibility, Understandability, Reproducibility, Extensibility — but prescribe no runtime infrastructure for heterogeneous composition. The cross-formalism, multi-timescale coordination problem remains open.

We propose OISA — the Orchestrated Immune Simulation Architecture — to fill this gap. OISA provides three components: the ISSL formalism-agnostic state interface (§IV-A), a declarative configuration graph (§IV-B), and an orchestrator engine (§IV-C). We demonstrate the architecture on a four-compartment murine immune ontogeny pipeline and evaluate causal ordering, uncertainty propagation, and biological plausibility in §V.

---

## II. Related Work

### II-A. Multi-Formalism Immune Simulation Frameworks

Several frameworks have addressed multi-scale composition in computational biology. Vivarium [1] introduced a port-based, formalism-agnostic composition interface for multiscale biological simulation but does not provide a standardised inter-model signal format with embedded uncertainty quantification, model-derived edge lags, or a biological plausibility constraint engine — the three capabilities central to OISA. PhysiCell [5] and PhysiBoSS [13] extend ABM with Boolean signalling layers but operate within a single formalism. The SARS-CoV-2 tissue simulator [4] demonstrated rapid community-driven ABM composition but required a uniform computational substrate. Within computational immunology specifically, Efroni et al. [28] demonstrated that thymocyte development and lineage determination can be modelled as emergent properties of single-cell gene regulatory dynamics — a published ABM reference for the thymic selection component of our pipeline — but did not address inter-model composition or coupling to ODE compartments. No existing system supports runtime composition of independently-developed ODE and ABM models through a formalism-agnostic signal interface with embedded uncertainty propagation.

### II-B. Simulation Interoperability Standards

The COMBINE standards ecosystem [14] has achieved significant progress on individual model portability. SBML [6] has accumulated over 1,000 curated models in BioModels; CellML [3] has analogous achievements in cardiac and physiological modelling; SED-ML [16] provides a standard for encoding simulation experiments. **Table I** compares these standards against OISA. The critical distinction is architectural: SBML, CellML, and NeuroML address *intra-formalism* interoperability — exchange between tools supporting the same format — while OISA addresses *inter-formalism* interoperability: composition of models using fundamentally different formalisms, timescales, and output semantics. SBML's hierarchical composition package (comp) extends composition within SBML but cannot incorporate an ABM without first rewriting it in SBML, which is both impractical and biologically inappropriate for stochastic cellular processes such as thymic selection.

**Table I.** Comparison of SBML, CellML, NeuroML/LEMS, and OISA across capabilities relevant to multi-organ immune simulation.

| Capability | SBML L3 | CellML 2.0 | NeuroML/LEMS | OISA (ISSL) |
|---|:---:|:---:|:---:|:---:|
| Portable model representation | ✓ | ✓ | ✓ | — |
| ODE / biochemical networks | ✓ | ✓ | neurons only | via Emit() |
| Agent-based models | ✗ | ✗ | ✗ | via Emit() |
| Heterogeneous Δt between models | ✗ | ✗ | ✗ | ✓ |
| Model-derived transfer lag on edges | ✗ | ✗ | ✗ | ✓ |
| Inter-formalism composition (ODE + ABM) | ✗ | ✗ | ✗ | ✓ |
| Runtime UQ propagation across models | ✗ | ✗ | ✗ | ✓ |
| OBO ontology annotation | ✓ | ✓ | ✓ | ✓ + wildcard |
| ABM scaling factor declaration | ✗ | ✗ | ✗ | ✓ |
| Requires model rewrite to adopt | ✓ | ✓ | ✓ | ✗ (add Emit only) |

### II-C. Immune Digital Twins

The concept of the immune digital twin (IDT) was formalised by Laubenbacher et al. [8] as a continuously-recalibrated patient-specific computational model of the immune system. Subsequent reviews [9], [12] have identified interoperability as the primary technical barrier to clinical deployment, a conclusion echoed by the National Academies [2], by model integration consortia [7], and by multi-scale digital twin frameworks in adjacent domains [15]. OISA is the first runtime orchestration architecture designed specifically for heterogeneous immune model composition, providing the coordination infrastructure that these reviews identify as lacking.

---

## III. Problem Formalisation

### III-A. Formal Model Definition

We define a composable simulation model M as a triple M = (S, Emit, Accept), where S is the model's internal state space, Emit : S × T → ISSL maps the current state and simulation time to a structured ISSL record, and Accept : ISSL → S updates the model state in response to an incoming inter-model signal. Any model — ODE, ABM, hybrid, or neural surrogate — that implements Emit and Accept is OISA-compliant without any other modification. Formalism-agnosticism follows directly: since the ISSL is the only communication channel, models need not know each other's internal representation, only the schema of the signal they receive. This design principle — letting each biological process be modelled in its natural formalism and solving the composition problem at the interface — avoids forcing biologically inappropriate representations on individual compartments.

### III-B. The Composition Problem

A multi-model composition is a directed graph G = (V, E) where each vertex v is a model Mᵥ and each directed edge (u, v) specifies that a subset of u's `export_signals` are routed to v's Accept function, with optional transfer model execution and lag application on the edge. The composition problem reduces to three coordination challenges:

1. **Heterogeneous time steps.** A global simulation clock (GSimT) must coordinate execution such that no model receives a signal purporting to come from a future GSimT tick. In the reference implementation, the bone marrow ODE steps at 6 h intervals while the thymus ABM steps at 24 h intervals; the GSimT tick is set to the GCD of all model Δtᵢ values (here 6 h).

2. **Stochastic–deterministic reconciliation.** Signals from an ABM to an ODE must be represented as distributions. The orchestrator normalises all inter-model signals to (mean, ci_95, unit) before routing, regardless of source formalism.

3. **Model-derived transfer lags.** The biological delay between bone marrow export and thymic arrival is itself a modelled quantity — it depends on the current export flux and transit ODE parameters and cannot be declared at configuration time. Transfer models as first-class edge properties address this.

---

## IV. The OISA Architecture

### IV-A. The Internal Simulation State Log (ISSL)

The ISSL is a JSON-LD document emitted by a model at each checkpoint, structured in six sections (**Table II**). JSON-LD enables both human readability and machine-parsable semantic annotation via linked data context, allowing orchestrator components to parse ISSL records without prior knowledge of the model's internal variable naming conventions.

**Table II.** ISSL section inventory. The `biological_flux_per_day` field in `export_signals` always carries the biologically scaled value, ensuring downstream ODE models receive correct quantities regardless of source formalism.

| ISSL section | Content | Key parsability requirement |
|---|---|---|
| `envelope` | Model ID, version, GSimT timestamp, schema URI, `agent_count`, `scale_factor` | Orchestrator validates `schema_uri`; reads `scale_factor` before processing ABM outputs. |
| `continuous_state` | Running entity populations: count (scaled), unit, fitness, surface markers, ci_95 | `entity_class`: "ontology" (OBO URI) \| "custom" (namespaced local ID). Counts in biological units after scaling. |
| `discrete_events` | Punctual events: selection events, cell death, cytokine peaks | `event_type` from controlled vocabulary. ABM events include `n_realisations` and variance. Counts are raw agent events (discrete by definition). |
| `export_signals` | Inter-compartmental fluxes available for routing | `biological_flux_per_day` carries the scaled value. `flux_raw_agents` available for traceability. `lag_s` present for transfer models only. |
| `internal_parameters` | Kinetic parameter values with posteriors and provenance | `identifiable`: bool; `provenance`: PROV-O pointer to calibration dataset URI. |
| `watchdog` | Model health: status, OOD flag, divergence score | `divergence_score` > 0.15 → PAUSE; OOD flag → WARN. |

**ABM scaling mechanism.** A murine thymus ABM simulating 300 agents must communicate a naïve T-cell export flux in biologically meaningful cells·day⁻¹, not in raw agent counts. The ISSL `envelope` therefore carries `agent_count` and `scale_factor` (real cells per simulated agent); `export_signals.biological_flux_per_day` is always computed as `flux_raw_agents × scale_factor` before emission. The scaling decision is documented in the ISSL record rather than hidden in model code, directly implementing CURE's understandability requirement at the composition level.

**Box 1: ISSL record excerpt — bone marrow ODE model (BM v7, day 1 checkpoint, GSimT = 86,400 s)**

```json
{
  "issl_version": "1.0",
  "model_id": "BM_haematopoiesis_v7", "formalism": "ODE",
  "sim_time_s": 86400,
  "continuous_state": [
    { "entity_class":"ontology", "entity_id":"CL:0000037", "label":"HSC",
      "count": 9075.0, "unit":"cells", "ci_95":[7820, 10401] },
    { "entity_class":"ontology", "entity_id":"CL:0002420", "label":"DN1/ETP",
      "count": 1191.1, "unit":"cells", "ci_95":[27, 1942] }
  ],
  "export_signals": [
    { "signal_id":"BM.progenitor_export", "entity_id":"CL:0002420",
      "biological_flux_per_day": 59.55, "unit":"cells·day⁻¹",
      "ci_95":[1.4, 90.9], "target_hint":"blood_transit" }
  ],
  "internal_parameters": [
    { "param_id":"r_HSC_renewal", "value":0.0045, "unit":"day⁻¹",
      "posterior_ci_95":[0.003, 0.007], "identifiable":true,
      "provenance":"doi:10.1038/nature14242" }
  ],
  "watchdog": { "status":"running", "ood_flag":false, "divergence_score":0.03 }
}
```

For models already represented in SBML with MIRIAM-compliant annotations, `entity_id` fields can be populated directly from existing OBO URI annotations without remapping. SBML models with `delta_t` specified in SED-ML can use that value as the `delta_t_s` field in the configuration graph.

### IV-B. The Configuration Graph

The configuration graph is a YAML or JSON-LD file that fully specifies the composition (**Table III**). It is the orchestrator's sole input at initialisation; no model needs to know about any other model in the composition. **Figure 1** shows the directed graph for the four-compartment reference implementation.

*[Figure 1: Configuration graph for the four-compartment murine immune ontogeny reference implementation. Nodes: BM ODE (6 h Δt), blood transit ODE (memoryless transfer model), thymus ABM (24 h Δt), peripheral LN ODE (12 h Δt). Edges annotated with signal IDs and lag types: model-derived lag on BM → Thymus (via blood transit), constant 2-day lag on Thymus → PLN.]*

**Table III.** Configuration graph schema. The declarative separation of model identity, wiring, temporal parameters, and renderer configuration implements the CURE extensibility requirement: any model node can be substituted without modifying the graph structure.

| Config element | Type | Description / example |
|---|---|---|
| `models[]` | Array of model nodes | `{ id, formalism: "ODE"\|"ABM", executable, issl_port, delta_t_s }` |
| `edges[]` | Array of directed connections | `{ source_model, signal_id, target_model, lag: "constant:N" \| "model:ID" }` |
| `transfer_models[]` | Optional models on edges | `{ id, formalism, executable, input_signal, output_signal, lag_output_field }` |
| `global_clock` | GSimT configuration | `{ start_s, end_s, checkpoint_interval_s }` |
| `calibration` | EHR / data bridge config | `{ data_source_uri, patient_id, recalibration_trigger, biomarker_map[] }` |
| `wildcard_namespace` | Custom entity namespace | `{ prefix, registry_uri: null }` — allows non-OBO entities |

The transfer model mechanism is OISA's most significant architectural contribution beyond existing composition frameworks: by allowing any edge to specify a transfer model, OISA enables runtime computation of biologically accurate delays from model outputs, rather than requiring delays to be estimated and hard-coded at design time. The following excerpt shows the key edge definitions:

```yaml
edges:
  - source: BM_haematopoiesis_v7
    signal_id: BM.progenitor_export
    target: Thymus_selection_v3
    lag: "model:blood_transit"     # transfer model computes lag dynamically

  - source: Thymus_selection_v3
    signal_id: THY.naive_T_export
    target: PeripheralLN_ODE
    lag: "constant:172800"         # 2-day homing lag (calibrated from [26])
```

### IV-C. The Orchestrator Engine

The orchestrator is a nine-component server process (**Table IV**). It reads the configuration graph at startup, establishes socket connections to all model processes, and manages the simulation run.

**Table IV.** Orchestrator component inventory. The transfer dispatcher and temporal scheduler together implement the runtime coordination capabilities that existing format standards cannot provide.

| Component | Responsibility | Key implementation note |
|---|---|---|
| 1 · ISSL ingestion | Parse + validate incoming model logs | JSON-LD parser; OBO URI resolver; SI unit normaliser; OOD detector (Mahalanobis distance from calibration envelope) |
| 2 · Temporal scheduler | Maintain GSimT; dispatch step commands | Priority queue by `next_step_due`; handles heterogeneous Δt; blocks models ahead of GSimT tick |
| 3 · Causal resolver | Maintain DAG; route signals | Topological sort at init; cycle detection; feedback back-edges get one-tick delay |
| 4 · Constraint engine | Enforce biological plausibility | Cell mass conservation; parameter bounds; raises `CONSTRAINT_VIOLATION` with offending model ID |
| 5 · State registry | Maintain global immune state (GIS) | Immutable versioned snapshots per GSimT checkpoint; PROV-O provenance graph linking GIS fields to source ISSLs |
| 6 · Transfer dispatcher | Execute transfer models on edges; apply lag | Invokes transfer model on-demand; reads `lag_s` from ISSL `export_signals`; maintains pending signal queue |
| 7 · Calibration bridge | Ingest patient EHR; trigger recalibration | Maps clinical biomarker → model parameter via `biomarker_map`; broadcasts updated priors |
| 8 · Output aggregator | Emit OISSL render stream | Merges GIS into checkpoint log; uncertainty propagation; trajectory builder |
| 9 · Watchdog monitor | Poll model health; pause/resume/rollback | `divergence_score` > 0.15 → PAUSE; OOD flag → WARN; conservation violation → ROLLBACK |

**Temporal scheduling.** At each GSimT tick (the GCD of all model Δtᵢ, here 6 h), the scheduler dispatches step commands to models whose `next_step_due` equals the current GSimT. Models with longer Δt (e.g., the thymus ABM at 24 h) receive step commands every fourth tick. The scheduler blocks any model that attempts to advance beyond the current tick until all models at that tick have emitted their ISSL records.

**Causal resolution.** The causal resolver constructs a DAG from the configuration graph and performs topological sorting to determine execution order within each GSimT tick. In the reference implementation — which is acyclic — the execution order at each applicable tick is: BM → blood_transit → Thymus → PLN. Feedback edges (e.g., peripheral Treg suppression of thymic output) receive a one-tick delay, preserving biological causality at the GSimT timescale without circular dependency.

---

## V. Validation

The murine immune ontogeny pipeline (bone marrow → blood transit → thymic T-cell selection → peripheral naïve T-cell homeostasis) is used as a reference implementation because all four compartments have well-characterised kinetic parameters in the published murine literature. **No biological novelty is claimed; the pipeline serves to validate that OISA correctly orchestrates heterogeneous models under increasing architectural complexity.**

### V-A. Validation Setup

Five experimental configurations are evaluated incrementally (**Table V**). Each activates one additional OISA capability, isolating framework mechanisms for independent validation.

**Table V.** Validation run matrix. Each configuration adds one OISA capability to the previous. "✓ (live)" denotes runtime computation by the orchestrator at each GSimT tick.

| Run | ODE model | ODE + ABM | Transfer lag | UQ propagation | Plausibility check |
|---|:---:|:---:|:---:|:---:|:---:|
| BM1 — BM haematopoiesis baseline | ✓ | — | — | ✓ | ✓ |
| THY1 — Thymus ABM baseline | — | ✓ | — | ✓ | ✓ |
| COMP1 — BM → Thymus direct coupling | ✓ | ✓ | — | ✓ | ✓ |
| COMP2 — BM → Blood Transit → Thymus | ✓ | ✓ | ✓ (live) | ✓ | ✓ |
| COMP3 — Full 4-model pipeline | ✓ | ✓ | ✓ (live) | ✓ | ✓ |

The four composed models are: (1) a five-compartment ODE cascade (HSC → MPP → LMPP → CLP → DN1) following the logistic niche-limited renewal formulation of Marciniak-Czochra et al. [29] with kinetic rates from Busch et al. [18], Adolfsson et al. [19], and Kondo et al. [20]; (2) a memoryless blood transit ODE whose stop fraction and transit time are calibrated from Goldschneider et al. [30] and Donskoy & Goldschneider [21]; (3) a 300-agent thymus ABM (scale_factor = 300,000 [22]) whose developmental stage machine follows Shortman & Wu [31] and whose TCR-affinity selection thresholds are calibrated from Starr et al. [23] and McCaughtry et al. [24] — the closest published ABM reference for the selection component is Efroni et al. [28]; and (4) a peripheral LN ODE implementing the canonical De Boer & Perelson [32] logistic homeostasis model, with turnover rates from Schluns & Lefrançois [33] and pool set points from Berzins et al. [27]. CI-95 is Monte Carlo (2,000 draws) for ODE models and empirical (12 ABM realisations) for the thymus ABM.

### V-B. Validation Results

#### V-B.1. Causal Ordering

The orchestrator generated 120 OISSL checkpoint records over the 30-day COMP3 simulation with no deadlocks, no temporal causality violations, and no watchdog alerts. At each 6 h GSimT tick, the topological execution order BM → blood_transit → Thymus → PLN was maintained without exception; no model received an ISSL signal timestamped ahead of the current GSimT. The transfer dispatcher correctly invoked the blood transit ODE on-demand for each BM emission event and queued the resulting progenitor delivery at GSimT + lag_s, producing a transit lag of 95.7 h (~4 days) consistent with Goldschneider et al. [30] and Donskoy & Goldschneider [21] estimates of 3–5 days.

*[Figure 2: Causal execution timeline across GSimT ticks for COMP3 days 1–5. Each row is one model (BM, blood_transit, Thymus, PLN); columns are 6 h GSimT ticks. Step-command dispatch (▶) and ISSL emission (●) events confirm BM → blood_transit → Thymus → PLN ordering at every applicable tick, with transfer-model invocation (⚡) annotated on the BM → blood_transit edge.]*

#### V-B.2. Biological Plausibility

ISSL-emitted quantities were checked against published murine ranges at day 30 (**Table VI**). All three primary framework-level outputs fall within their respective published intervals. At day 30, peripheral naïve CD4⁺ T cells reached 193,424 (homeostatic set point: 200,000; 96.7% maintenance) and CD8⁺ T cells reached 97,093 (set point: 100,000; 97.1% maintenance), with a CD4/CD8 ratio of ~2:1 [27], [32]. These checks validate that the constraint engine correctly enforces biological plausibility and that unit conversions and scale factor application across the ODE–ABM interface introduce no systematic bias.

**Table VI.** Biological plausibility checks at day 30 (COMP3). Values are OISA framework outputs; published ranges are the constraint engine's enforcement targets. All checks passed: no `CONSTRAINT_VIOLATION` event was raised during the 30-day simulation.

| Quantity | OISA output (day 30) | Published range | Reference | Passed? |
|---|---|---|---|---|
| BM DN1 export flux (cells·day⁻¹) | 59.6 [CI: 1.4–90.9] | 10–100 cells·day⁻¹ | Goldschneider et al. [30] | ✓ |
| Thymic naïve T export (cells·day⁻¹) | 1.0 × 10⁶ [CI: 84,000–2M] | 0.5–2 × 10⁶ cells·day⁻¹ | Scollay et al. [25] | ✓ |
| Peripheral CD4/CD8 ratio at steady state | ~2.0:1 | ~2:1 (murine) | De Boer & Perelson [32]; Berzins et al. [27] | ✓ |

#### V-B.3. Uncertainty Propagation

Confidence intervals compound correctly across the composition chain. In COMP1 (direct ODE → ABM coupling, no transfer lag), the BM ODE's Monte Carlo CI-95 ([1.4, 90.9] cells·day⁻¹) is normalised by the orchestrator to a distributional estimate before acceptance by the thymus ABM, yielding a thymic export CI-95 of [300,000–1.0 × 10⁶] cells·day⁻¹ across 12 ABM realisations. In COMP2 (with blood transit transfer model), the transit lag introduces an additional uncertainty contribution, widening the thymic export CI-95 to [84,000–2.0 × 10⁶] cells·day⁻¹ — correctly reflecting compounded transit ODE and ABM stochastic uncertainty. Uncertainty is neither lost nor artificially collapsed at any inter-model interface.

*[Figure 3: Uncertainty propagation across the five validation runs. X-axis: run configuration (BM1 → COMP3), ordered by number of active OISA composition features. Y-axis: thymic naïve T export CI-95 width (log scale). Width increases monotonically with composition complexity, confirming that the orchestrator correctly compounds rather than discards inter-model uncertainty.]*

---

## VI. Discussion

### VI-A. OISA and the CURE Guidelines

**Table VII** maps each CURE criterion [17] to its OISA implementation. Three points deserve emphasis. First, OISA implements CURE credibility criteria at the *composition* level: a composition can violate biological plausibility even when each constituent model is individually valid — for example, if cell mass is not conserved across an ODE→ABM interface due to a unit conversion error. The orchestrator constraint engine catches these composition-level failures at every GSimT tick, a check that individual model validators cannot perform. Second, the `scale_factor` declaration makes the ABM scaling assumption explicit and auditable — a direct implementation of CURE's understandability requirement at the multi-model scale. Third, OISA does not implement all CURE criteria: individual model validation against experimental data and governance of ontology adoption remain the responsibility of model developers.

**Table VII.** OISA components as operational implementations of CURE criteria [17], extended to the multi-model composition level.

| CURE criterion | OISA component | Scope |
|---|---|---|
| Credibility — UQ of outputs | ISSL `ci_95` fields; MC (ODE) and empirical (ABM) CI propagated through signals | Composition-level |
| Credibility — scope monitoring | Watchdog `ood_flag` + Mahalanobis OOD detector | Per-model at every tick |
| Credibility — provenance | ISSL `provenance` PROV-O URI; OISSL provenance graph | Parameter + signal |
| Understandability — levels 1–3 | ISSL `envelope` + `continuous_state` + `export_signals` | Per checkpoint |
| Reproducibility — community standards | JSON-LD schema; OBO URI annotations (CL:, GO:); SED-ML Δt compatibility | Schema-level |
| Extensibility — modular reuse | Config graph edge-based wiring; any node substitutable without modifying peers | Architecture-level |
| Automation of guideline checking | Constraint engine + watchdog; automatic at every GSimT tick | Runtime |

### VI-B. Limitations

**Validation scope.** Validation is on a single organism (murine) and a single biological process (immune ontogeny). No independent experimental dataset for the composed multi-compartment output exists; full validation would require longitudinal murine data capturing all four compartments simultaneously — an experiment not yet published.

**Feedback loops.** The COMP3 graph is acyclic. Biologically significant feedback loops (e.g., peripheral Treg suppression of thymic output) require the one-tick delay mechanism described in §IV-C, introducing a minimum latency of one GSimT tick (6 h). Whether this latency is biologically significant depends on the timescale of the feedback process relative to the GSimT tick size.

**ABM scaling.** With 300 agents and 12 realisations, the effective sample for CI-95 estimation is 3,600 agent-trajectories — sufficient for mean and CI estimates reported here, but potentially inadequate for tail-event statistics such as autoimmune escape rates.

**Species specificity.** All kinetic parameters are calibrated from murine data. Human immune ontogeny parameters — particularly thymic transit times, selection yields, and peripheral pool set points — differ substantially and require independent calibration from human data sources before OISA can be applied to human IDTs.

---

## VII. Conclusion

We have proposed and demonstrated OISA, the Orchestrated Immune Simulation Architecture, establishing its capacity to compose a four-compartment immune ontogeny simulation from heterogeneous ODE and ABM models with formalism-agnostic signal routing, model-derived transfer lags, and automated biological plausibility enforcement. Validation on the murine reference implementation confirms correct causal ordering across 120 checkpoint records, monotonically increasing uncertainty compounding across all five experimental configurations, and biological plausibility of framework outputs within published murine ranges. OISA operationalises the CURE extensibility and automation requirements at the multi-model scale, providing the runtime infrastructure that those guidelines imply but do not specify. The architecture demonstrates that formalism-agnostic composition is achievable without model rewrites — and that reduction in the technical barrier to multi-organ immune digital twins is the primary contribution of this work.

---

## References

[1] E. Agmon et al., "Vivarium: an interface and engine for integrative multiscale modeling in computational biology," *Bioinformatics*, vol. 38, pp. 1972–1979, 2022.

[2] Committee on Foundational Research Gaps and Future Directions for Digital Twins, *Foundational Research Gaps and Future Directions for Digital Twins*. National Academies Press, 2023.

[3] C.M. Lloyd et al., "The CellML Model Repository," *Bioinformatics*, vol. 24, pp. 2122–2123, 2008.

[4] M. Getz et al., "Rapid community-driven development of a SARS-CoV-2 tissue simulator," *iScience*, vol. 23, 101734, 2020.

[5] A. Ghaffarizadeh et al., "PhysiCell: An open source physics-based cell simulator for 3-D multicellular systems," *PLoS Comput. Biol.*, vol. 14, e1005991, 2018.

[6] M. Hucka et al., "The Systems Biology Markup Language (SBML): Language Specification for Level 3 Version 1 Core," *J. Integr. Bioinform.*, vol. 12, no. 266, 2015.

[7] J. Karr et al., "Model Integration in Computational Biology: The Role of Reproducibility, Credibility and Utility," *Front. Syst. Biol.*, vol. 2, 822606, 2022.

[8] R. Laubenbacher et al., "Building digital twins of the human immune system: toward a roadmap," *npj Digit. Med.*, vol. 5, p. 64, 2022.

[9] R. Laubenbacher et al., "Forum on immune digital twins: a meeting report," *npj Syst. Biol. Appl.*, vol. 10, p. 19, 2024.

[10] R. Laubenbacher, B. Mehrad, I. Shmulevich, and N. Trayanova, "Digital twins in medicine," *Nat. Comput. Sci.*, vol. 4, pp. 184–191, 2024.

[11] R. Laubenbacher et al., "Toward mechanistic medical digital twins: some use cases in immunology," *Front. Digit. Health*, vol. 6, 1349595, 2024.

[12] A. Niarakis et al., "Immune digital twins for complex human pathologies: applications, limitations, and challenges," *npj Syst. Biol. Appl.*, vol. 10, p. 141, 2024.

[13] M. Ponce-de-Leon et al., "PhysiBoSS 2.0: a sustainable integration of stochastic Boolean and agent-based modelling frameworks," *npj Syst. Biol. Appl.*, vol. 9, p. 54, 2023.

[14] F. Bergmann et al., "COMBINE archive and OMEX format: one file to share all information to reproduce a modeling project," *BMC Bioinformatics*, vol. 15, p. 369, 2014.

[15] M. Viceconti et al., "From the digital twins in healthcare to the Virtual Human Twin," *IEEE J. Biomed. Health Inform.*, vol. 28, pp. 491–501, 2024.

[16] D. Waltemath et al., "Reproducible computational biology experiments with SED-ML," *BMC Syst. Biol.*, vol. 5, p. 198, 2011.

[17] H.M. Sauro et al., "From FAIR to CURE: Guidelines for Computational Models of Biological Systems," *arXiv*:2502.15597, 2025.

[18] K. Busch et al., "Fundamental properties of unperturbed haematopoiesis from stem cells in vivo," *Nature*, vol. 518, pp. 542–546, 2015.

[19] J. Adolfsson et al., "Identification of Flt3+ lympho-myeloid stem cells lacking erythro-megakaryocytic potential: a revised road map for adult blood lineage commitment," *Cell*, vol. 121, pp. 295–306, 2005.

[20] M. Kondo, I.L. Weissman, and K. Akashi, "Identification of clonogenic common lymphoid progenitors in mouse bone marrow," *Cell*, vol. 91, pp. 661–672, 1997.

[21] E. Donskoy and I. Goldschneider, "Thymocytopoiesis is maintained by blood-borne precursors throughout postnatal life: a study in parabiotic mice," *J. Immunol.*, vol. 148, pp. 1604–1612, 1992.

[22] R. Scollay and D.I. Godfrey, "Thymic emigration: conveyor belts or lucky dips?" *Immunol. Today*, vol. 16, pp. 268–273, 1995.

[23] T.K. Starr, S.C. Jameson, and K.A. Hogquist, "Positive and negative selection of T cells," *Annu. Rev. Immunol.*, vol. 21, pp. 139–176, 2003.

[24] T.M. McCaughtry, M.S. Wilken, and K.A. Hogquist, "Thymic emigration revisited," *J. Exp. Med.*, vol. 204, pp. 2513–2520, 2007.

[25] R. Scollay, J. Smith, and V. Stauffer, "Dynamics of early T cells: prothymocyte migration and proliferation in the adult mouse thymus," *Immunol. Rev.*, vol. 53, pp. 89–106, 1980.

[26] C.R. Mackay, W.L. Marston, and L. Dudler, "Naive and memory T cells show distinct pathways of lymphocyte recirculation," *J. Exp. Med.*, vol. 171, pp. 801–817, 1990.

[27] S.P. Berzins, R.L. Boyd, and J.F.A.P. Miller, "The role of the thymus and recent thymic migrants in the maintenance of the adult peripheral lymphocyte pool," *J. Exp. Med.*, vol. 187, pp. 1839–1848, 1998.

[28] S. Efroni, R. Harel, and I.R. Cohen, "Emergent dynamics of thymocyte development and lineage determination," *PLoS Comput. Biol.*, vol. 3, e13, 2007. doi: 10.1371/journal.pcbi.0030013

[29] A. Marciniak-Czochra, T. Stiehl, A.D. Ho, W. Jäger, and W. Wagner, "Modeling of asymmetric cell division in hematopoietic stem cells — regulation of self-renewal is essential for efficient repopulation," *Stem Cells Dev.*, vol. 18, pp. 377–385, 2009. doi: 10.1089/scd.2008.0143

[30] I. Goldschneider, E.C. Komschlies, and D.L. Greiner, "Studies of thymocytopoiesis in rats and mice. I. Kinetics of appearance of thymocytes using a direct intrathymic adoptive transfer assay for thymocyte precursors," *J. Exp. Med.*, vol. 163, pp. 1–17, 1986. doi: 10.1084/jem.163.1.1

[31] K. Shortman and L. Wu, "Early T lymphocyte progenitors," *Annu. Rev. Immunol.*, vol. 14, pp. 29–47, 1996. doi: 10.1146/annurev.immunol.14.1.29

[32] R.J. De Boer and A.S. Perelson, "T cell repertoires and competitive exclusion," *J. Theor. Biol.*, vol. 169, pp. 201–222, 1994. doi: 10.1006/jtbi.1994.1143

[33] K.S. Schluns and L. Lefrançois, "Cytokine control of memory T-cell development and survival," *Nat. Rev. Immunol.*, vol. 3, pp. 269–279, 2003. doi: 10.1038/nri1052

---

*Article type: Methods / Framework Proposal*

*Data and code availability: OISA specification files, ISSL JSON-LD schemas, reference orchestrator implementation, all model code (BM ODE, blood transit ODE, thymus ABM, peripheral LN ODE), configuration graphs (COMP1–COMP3), and Supplementary Table S1 (full parameter listings with calibration sources and posterior CI estimates) are available at [repository URL to be added prior to submission].*

*Species note: All kinetic parameters are calibrated from published murine data. Human parameters can be substituted in `parameters.yaml` without architectural modification.*

*Author contributions: [To be completed prior to submission]*

*Competing interests: The authors declare no competing interests.*
