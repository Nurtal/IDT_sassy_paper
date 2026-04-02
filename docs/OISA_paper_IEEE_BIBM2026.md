# Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling

**The Orchestrated Immune Simulation Architecture (OISA)**

*[Author names and affiliations to be completed prior to submission]*

---

## Abstract

Computational immunology has produced mechanistic models of individual immune compartments of considerable sophistication, yet these models remain siloed: ODE and agent-based models (ABMs) cannot be composed without bespoke re-engineering, temporal coupling between organ-scale models is not standardised, and no runtime architecture supports the multi-organ representation that translational medicine demands. We propose OISA — the Orchestrated Immune Simulation Architecture — which addresses this gap through three components: (i) the Internal Simulation State Log (ISSL), a formalism-agnostic JSON-LD log format emitted at each checkpoint by any model regardless of whether it is an ODE, ABM, or hybrid; (ii) a declarative configuration graph specifying models as nodes and inter-compartmental signal flows as directed edges with optional transfer model lags; and (iii) an orchestrator engine providing global clock synchronisation, causal ordering, uncertainty quantification propagation, and biological plausibility enforcement. We validate OISA through five simulation runs of increasing complexity using a four-compartment murine immune ontogeny pipeline (bone marrow haematopoiesis → blood transit → thymic T-cell selection → peripheral lymph node homeostasis). All composition scenarios produce results consistent with published murine biology, and the orchestrator generates 120 checkpoint records over the 30-day full simulation with no causality violations. OISA operationalises the CURE (Credibility, Understandability, Reproducibility, Extensibility) guidelines at the multi-model scale, enabling any OISA-compliant model to be substituted into a composition without modifying its peers.

**Keywords:** immune digital twins, multi-scale modelling, model composition, agent-based models, ordinary differential equations, interoperability, computational immunology

---

## I. Introduction

Immune-mediated diseases are inherently multi-compartmental phenomena. Rheumatoid arthritis traces to haematopoietic stem cell programming in the bone marrow before manifesting in the synovial joint. Sepsis is a systemic dysregulation spanning blood, bone marrow, and multiple peripheral tissues simultaneously. Type 1 diabetes involves thymic selection failures, peripheral tolerance breakdown, and pancreatic tissue destruction. No single model formalism can faithfully represent all of these scales; the literature has instead produced a collection of high-quality compartment-specific models that cannot communicate with one another.

Two prior frameworks address adjacent problems. The CURE guidelines (Sauro et al. 2025) [29] define what properties a computational model should exhibit: Credibility, Understandability, Reproducibility, and Extensibility — but they describe properties of individual models, not the runtime infrastructure required to compose heterogeneous models. The COMBINE standards ecosystem (SBML [12], CellML [7], NeuroML, SED-ML [27]) provides portable representations for individual models but was designed for intra-formalism composition, combining models written in the same declarative language. Neither framework addresses the cross-formalism, multi-organ, multi-timescale composition problem.

This gap has a precise technical manifestation. SBML, CellML, and NeuroML cannot accommodate models that are not expressed in their own format, cannot compute edge-level transfer lags at runtime from a third model's output, and cannot propagate uncertainty distributions across formalism boundaries. The SBML hierarchical composition package (comp) extends composition within SBML but cannot incorporate an ABM written in Python or Julia without first rewriting it in SBML, which is both impractical and biologically inappropriate for stochastic cellular processes.

A further challenge is specific to ABM-ODE composition: the formalism mismatch in output semantics. An ODE model produces a deterministic state snapshot at each step; an ABM produces a stochastic realisation over a population of discrete agents. Routing an ABM's output to an ODE's input requires a reconciliation layer that normalises the stochastic count into a distributional estimate. No existing composition framework provides this reconciliation.

We propose OISA — the Orchestrated Immune Simulation Architecture — as a solution to these coordination problems. OISA does not replace SBML, CellML, or NeuroML, nor does it supplant the CURE guidelines. Instead, it adds the runtime orchestration layer that those standards and guidelines assume but do not specify: a coordination engine that enables formalism-agnostic composition of independently developed models into coherent multi-organ simulations.

---

## II. Background and Related Work

### II-A. From Mechanistic Models to Immune Digital Twins

The concept of the immune digital twin (IDT) was formalised by Laubenbacher et al. [17] as a computational model of an individual patient's immune system continuously recalibrated by clinical data. Subsequent reviews [18], [22] have articulated the gap between this vision and current capabilities: existing mechanistic models cover individual compartments well but cannot be composed into patient-scale representations without bespoke re-engineering for each new combination. The National Academies report on digital twins [6] identified interoperability as the primary technical barrier to clinical deployment.

The specific scale of the composition challenge is illustrated by the immune ontogeny pathway used throughout this paper: bone marrow haematopoiesis → blood transit → thymic T-cell education → peripheral naïve T-cell pool homeostasis. Each compartment has been modelled independently in the literature with calibrated kinetic parameters. No published work has composed all four into a single simulation that propagates uncertainty across compartments and enforces biological plausibility at every inter-model interface.

### II-B. Existing Standards: Achievements and Limitations

The COMBINE standards ecosystem has achieved significant progress on individual model portability. SBML [12] has accumulated over 1,000 curated models in BioModels, and reproducibility has been demonstrated across SBML-supporting tools. CellML [7] has analogous achievements in cardiac and physiological modelling. NeuroML/LEMS extends this to neural circuits. SED-ML [27] provides a standard for encoding simulation experiments. The COMBINE archive [24] bundles all artefacts for reproducibility.

**Table I** compares these standards against OISA across capabilities relevant to multi-organ immune simulation.

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
| Renderer-ready structured output | ✗ | ✗ | ✗ | ✓ |
| Requires model rewrite to adopt | ✓ | ✓ | ✓ | ✗ (add Emit only) |

The critical distinction is architectural: SBML, CellML, and NeuroML address intra-formalism interoperability — the ability to exchange models between tools supporting the same format. OISA addresses inter-formalism interoperability — the ability to compose models that use fundamentally different formalisms, timescales, and output semantics.

### II-C. The ODE–ABM Coupling Problem and the Scaling Challenge

ODEs are natural for processes where population-level mean-field approximations are valid: haematopoietic progenitor pool dynamics, systemic cytokine kinetics, PK/PD relationships. ABMs are natural where individual cell identity, spatial organisation, or stochastic fate decisions matter: thymic selection (where a cell's TCR affinity determines its fate), germinal centre reactions, and tumour-immune interactions. Composing these two formalisms requires solving two distinct problems.

The first is the output semantics mismatch: an ODE produces a deterministic flux rate, while an ABM produces a stochastic count. OISA's ISSL reconciliation layer normalises both to a (mean, ci_95, unit) representation before routing across formalism boundaries.

The second is the scale mismatch. A murine thymus contains ~10⁸ thymocytes; simulating each individually is computationally infeasible. The established solution in the ABM literature (PhysiCell [9], GlaziABM) is to simulate a representative sample and declare a scale factor. OISA makes this scale factor a first-class ISSL field, ensuring that downstream ODE models receive biologically scaled quantities rather than raw agent counts.

### II-D. The CURE Guidelines and the Automation Gap

The CURE guidelines [29] identify extensibility and automation as foundational requirements. Under extensibility, CURE observes that combining models written in different languages requires runtime infrastructure that the guidelines themselves do not specify. Under automation, CURE calls for tools that check guideline compliance without human intervention. OISA's orchestrator constraint engine implements exactly this automation — checking biological plausibility, parameter bounds, and provenance linkage at every simulation checkpoint.

The closest existing system to OISA in architectural philosophy is Vivarium [1], with its port-based formalism-agnostic composition interface. Vivarium's limitations in the immunological context are three-fold: it does not provide a standardised inter-model signal format (ISSL), it does not implement model-derived edge lags (transfer models), and it does not include a biological plausibility constraint engine. OISA addresses all three.

---

## III. Problem Formalisation

### III-A. Formal Model Definition

We define a composable simulation model M as a triple M = (S, Emit, Accept), where S is the model's internal state space, Emit : S × T → ISSL maps the current state and simulation time to a structured ISSL record, and Accept : ISSL → S updates the model state in response to an incoming inter-model signal. Any model — ODE, ABM, hybrid, or neural surrogate — that implements Emit and Accept is OISA-compliant without any other modification.

### III-B. The Composition Problem

A multi-model composition is a directed graph G = (V, E) where each vertex v is a model Mᵥ and each directed edge (u, v) specifies that a subset of u's export_signals are routed to v's Accept function, with optional transfer model execution and lag application on the edge. The composition problem reduces to three coordination challenges:

1. **Heterogeneous time steps.** A global simulation clock (GSimT) must coordinate execution such that no model receives a signal purporting to come from a future GSimT tick. In the COMP3 implementation, the bone marrow ODE steps at 6h intervals while the thymus ABM steps at 24h intervals and the peripheral LN ODE steps at 12h intervals. The GSimT tick is set to the GCD of all model Δt values (here 6h).

2. **Stochastic–deterministic reconciliation.** Signals from an ABM to an ODE must be represented as distributions. The orchestrator normalises all inter-model signals to (mean, ci_95, unit) before routing, regardless of the source formalism. ODE outputs carry Monte Carlo CI-95; ABM outputs carry empirical CI-95 across realisations.

3. **Model-derived transfer lags.** The biological delay between bone marrow export and thymic arrival is itself a modelled quantity computed by the blood transit ODE at runtime — it cannot be declared at model-description time because it depends on the current export flux, transit ODE parameters, and the stop_fraction. This requires transfer models as first-class edge properties.

### III-C. Why Formalism-Agnosticism is the Correct Design Principle

Requiring all models to be expressed in a common format — the approach of SBML comp or CellML — would produce less accurate models by forcing biologically inappropriate formalisms on individual processes. Haematopoietic progenitor dynamics are well-approximated by ODEs precisely because the population is large and well-mixed; forcing this process into an ABM adds computational cost without biological gain. Thymic selection is poorly approximated by ODEs precisely because individual cell fate depends on stochastic TCR affinity draws from a distribution; forcing this into an ODE loses the selection variance that is the biologically meaningful quantity. The correct principle is to let each process be modelled in its natural formalism and to solve the composition problem at the interface.

---

## IV. The OISA Architecture

### IV-A. The Internal Simulation State Log (ISSL)

The ISSL is a JSON-LD document emitted by a model at each checkpoint, structured in six sections (**Table II**). JSON-LD enables both human readability and machine-parsable semantic annotation via linked data context, allowing orchestrator components to parse ISSL records without prior knowledge of the model's internal variable naming conventions.

**Table II.** ISSL section inventory. The envelope section includes `agent_count` and `scale_factor` fields specific to ABM models; these are absent in ODE model ISSLs. The `biological_flux_per_day` field in `export_signals` always carries the biologically scaled value, ensuring downstream ODE models receive correct quantities regardless of source formalism.

| ISSL section | Content | Key parsability requirement |
|---|---|---|
| `envelope` | Model ID, version, GSimT timestamp, schema URI, `agent_count`, `scale_factor` | Orchestrator validates `schema_uri` and reads `scale_factor` before processing. For ABM models, `scale_factor` encodes the number of real cells per simulated agent. |
| `continuous_state` | Running entity populations: count (scaled), unit, fitness, surface markers, ci_95 | `entity_class`: "ontology" (OBO URI) \| "custom" (namespaced local ID). Counts in biological units after scaling. `count_raw_agents` available for traceability. |
| `discrete_events` | Punctual events: selection events, cell death, cytokine peaks | `event_type` from controlled vocabulary. ABM events include `n_realisations` and variance. Counts are raw agent events, not scaled (events are discrete by definition). |
| `export_signals` | Inter-compartmental fluxes available for routing | `biological_flux_per_day` field carries the scaled value. `flux_raw_agents` available for traceability. `lag_s` field present for transfer models only. |
| `internal_parameters` | Kinetic parameter values with posteriors and provenance | `identifiable`: bool; `provenance`: PROV-O pointer to calibration dataset URI. CI computed by MC (ODE) or empirical (ABM). |
| `watchdog` | Model health: status, OOD flag, divergence score | Orchestrator polls at every GSimT tick. `divergence_score` > 0.15 → PAUSE. |

**The ABM scaling mechanism.** A critical design decision in OISA's ISSL concerns how ABM outputs are communicated to downstream models. A murine thymus ABM simulating 300 agents must communicate a naïve T-cell export flux in biologically meaningful cells·day⁻¹, not in raw agent counts (which would be ~3.33 agents·day⁻¹). The ISSL `envelope` section therefore carries `agent_count` (agents simulated) and `scale_factor` (real cells per agent). The `export_signals.biological_flux_per_day` field is always computed as `flux_raw_agents × scale_factor` before emission. This ensures that the ODE receiving this signal operates on biologically plausible quantities and that the scaling decision is documented in the ISSL record rather than hidden in model code.

For models already represented in SBML with MIRIAM-compliant annotations, the `entity_id` fields in ISSL `continuous_state` can be populated directly from existing OBO URI annotations without remapping. SBML models with `delta_t` specified in SED-ML can use that value as the `delta_t_s` field in the configuration graph.

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

**Box 2: ISSL record excerpt — thymus ABM (v3, day 10 checkpoint, scale_factor = 300,000)**

```json
{
  "issl_version": "1.0",
  "model_id": "Thymus_selection_v3", "formalism": "ABM",
  "sim_time_s": 864000,
  "agent_count": 300, "scale_factor": 300000,
  "scale_factor_source": "doi:10.1146/annurev.iy.13.040195.001501",
  "n_realisations": 12,
  "continuous_state": [
    { "entity_class":"ontology", "entity_id":"CL:0000893", "label":"DP thymocyte",
      "count": 1300000, "count_raw_agents": 4,
      "unit":"cells (scaled)", "ci_95":[381000, 3000000] }
  ],
  "discrete_events": [
    { "event_type":"positive_selection", "ontology_ref":"GO:0045058",
      "count_raw_agents": 2, "n_realisations":12, "variance":0.8 },
    { "event_type":"neglect_death", "ontology_ref":"GO:0070242",
      "count_raw_agents":95, "n_realisations":12, "variance":3.1 }
  ],
  "export_signals": [
    { "signal_id":"THY.naive_T_export", "entity_id":"CL:0000898",
      "biological_flux_per_day": 1000000, "flux_raw_agents": 3.33,
      "unit":"cells·day⁻¹ (scaled)", "ci_95":[84000, 2000000],
      "target_hint":"peripheral_LN" }
  ],
  "watchdog": { "status":"running", "ood_flag":false, "divergence_score":0.07 }
}
```

### IV-B. The Configuration Graph

The configuration graph is a YAML or JSON-LD file that fully specifies the composition (**Table III**). The graph is the orchestrator's sole input at initialisation; no model needs to know about any other model in the composition.

**Table III.** Configuration graph schema. The declarative separation of model identity (`models[]`), wiring (`edges[]`), temporal parameters (`global_clock`), and renderer configuration (`renderer`) implements the CURE extensibility requirement: any model node can be substituted without modifying the graph structure.

| Config element | Type | Description / example |
|---|---|---|
| `models[]` | Array of model nodes | Each node: `{ id, formalism: "ODE"\|"ABM", executable, issl_port, delta_t_s }` |
| `edges[]` | Array of directed connections | `{ source_model, signal_id, target_model, lag: "constant:N" \| "model:ID", activation_threshold }` |
| `transfer_models[]` | Optional models on edges | `{ id, formalism, executable, input_signal, output_signal, lag_output_field }` |
| `global_clock` | GSimT configuration | `{ start_s, end_s, checkpoint_interval_s }` |
| `calibration` | EHR / data bridge config | `{ data_source_uri, patient_id, recalibration_trigger, biomarker_map[] }` |
| `renderer` | Output log → renderer config | `{ format: "OISA-render-v1", target, emit_interval_s, scene_schema_uri }` |
| `wildcard_namespace` | Custom entity namespace | `{ prefix, registry_uri: null }` — allows non-OBO entities |

**Transfer models as first-class edge properties.** The transfer model mechanism is OISA's most significant architectural contribution beyond existing composition frameworks. It encodes the insight that biological signal transmission is itself a modelled process: progenitors exported from the bone marrow undergo a blood transit journey whose duration is not a constant but a function of the current transit ODE state. By allowing any edge in the configuration graph to specify a transfer model, OISA enables runtime computation of biologically accurate delays from model outputs, rather than requiring these delays to be estimated and hard-coded at simulation design time.

**Box 3: Configuration graph — COMP3: four-model immune ontogeny simulation**

```yaml
oisa_version: "1.0"
models:
  - id: BM_haematopoiesis_v7
    formalism: ODE
    executable: "./models/bm_haematopoiesis/model.py"
    issl_port: "tcp://localhost:5001"
    delta_t_s: 21600          # 6-hour ODE steps

  - id: blood_transit
    formalism: ODE
    executable: "./models/blood_transit/model.py"
    issl_port: "tcp://localhost:5002"
    delta_t_s: 0              # stateless — invoked on-demand

  - id: Thymus_selection_v3
    formalism: ABM
    executable: "./models/thymus_selection/model.py"
    issl_port: "tcp://localhost:5003"
    delta_t_s: 86400          # 24-hour ABM checkpoints

  - id: PeripheralLN_ODE
    formalism: ODE
    executable: "./models/peripheral_ln/model.py"
    issl_port: "tcp://localhost:5004"
    delta_t_s: 43200          # 12-hour ODE steps

edges:
  - source: BM_haematopoiesis_v7
    signal_id: BM.progenitor_export
    target: Thymus_selection_v3
    lag: "model:blood_transit"     # transfer model computes lag dynamically

  - source: Thymus_selection_v3
    signal_id: THY.naive_T_export
    target: PeripheralLN_ODE
    lag: "constant:172800"         # 2-day homing lag

global_clock:
  start_s: 0
  end_s: 2592000                   # 30-day simulation
  checkpoint_interval_s: 21600     # GSimT tick = GCD(21600, 86400, 43200)
```

### IV-C. The Orchestrator Engine

The orchestrator is a nine-component server process (**Table IV**). It reads the configuration graph at startup, establishes socket connections to all model processes, and manages the simulation run.

**Table IV.** Orchestrator component inventory. The transfer dispatcher and temporal scheduler together implement the runtime coordination capabilities that existing format standards cannot provide.

| Component | Responsibility | Key implementation note |
|---|---|---|
| 1 · ISSL ingestion | Parse + validate incoming model logs | JSON-LD parser; OBO URI resolver; SI unit normaliser; OOD detector (Mahalanobis distance from calibration envelope) |
| 2 · Temporal scheduler | Maintain GSimT; dispatch step commands | Priority queue by `next_step_due`; handles heterogeneous Δt (BM: 6h, Thymus: 24h, PLN: 12h); blocks models ahead of GSimT |
| 3 · Causal resolver | Maintain DAG; route signals | Topological sort at init; cycle detection; feedback back-edges get one-tick delay |
| 4 · Constraint engine | Enforce biological plausibility | Cell mass conservation; parameter bounds; raises `CONSTRAINT_VIOLATION` with offending model ID |
| 5 · State registry | Maintain global immune state (GIS) | Immutable versioned snapshots per GSimT checkpoint; PROV-O provenance graph linking GIS fields to source ISSLs |
| 6 · Transfer dispatcher | Execute transfer models on edges; apply lag | Invokes transfer model on-demand; reads `lag_s` from ISSL `export_signals`; schedules signal delivery at GSimT + lag_s; maintains pending signal queue |
| 7 · Calibration bridge | Ingest patient EHR; trigger recalibration | Maps clinical biomarker → model parameter via `biomarker_map`; broadcasts updated priors |
| 8 · Output aggregator | Emit OISSL render stream | Merges GIS into checkpoint log; uncertainty propagation; trajectory builder; dashboard emitter |
| 9 · Watchdog monitor | Poll model health; pause/resume/rollback | `divergence_score` > 0.15 → PAUSE; OOD flag → WARN; conservation violation → ROLLBACK |

#### IV-C.1. Global Simulation Clock and Temporal Scheduling

The Global Simulation Time (GSimT) is the authoritative time reference for the composition. At each tick (here 21,600 s = 6 h, the GCD of all model Δtᵢ), the scheduler dispatches step commands to models whose `next_step_due` equals the current GSimT. Models with a longer Δt (e.g., the thymus ABM at 24 h) receive step commands every fourth GSimT tick. The scheduler maintains a priority queue sorted by `next_step_due` and blocks any model that attempts to advance beyond the current GSimT tick until all models at the current tick have emitted their ISSL records.

#### IV-C.2. Causal Resolution

The causal resolver constructs a DAG from the configuration graph and performs topological sorting to determine execution order within each GSimT tick. In the COMP3 graph — which is acyclic — the execution order at each applicable tick is: BM → blood_transit → Thymus → PLN. Feedback edges (e.g., peripheral Treg suppression of thymic output) would require a one-tick delay, making them available at the next GSimT tick rather than within the current tick, which avoids circular dependency while preserving biological causality at the timescale of the GSimT tick.

#### IV-C.3. Orchestrator Output Log and Renderer Interface

At each GSimT checkpoint, the output aggregator merges all model state snapshots into a single Orchestrator-ISSL (OISSL) document containing the `global_immune_state`, a `composition_events` log (signal routing, transfer model invocations, constraint checks), and a `provenance_graph` tracing each OISSL field to its source ISSL record. The OISSL is emitted to a configurable renderer that can produce dashboard visualisations, trajectory plots, or structured exports for downstream analysis.

---

## V. Results

We evaluated OISA through five simulation runs of increasing architectural complexity (**Table V**). All model parameters are drawn from published murine literature (Supplementary Table S1). Confidence intervals (CI-95) are reported throughout: Monte Carlo over 2,000 parameter draws for ODE models, and empirical across 12 ABM realisations for the thymus model.

**Table V.** Key simulation metrics at day 30 across all five scenarios. Thymus values are reported in scaled biological units (scale_factor = 300,000 per Scollay & Godfrey 1995 [35]). BM CI-95 is Monte Carlo (2,000 draws); Thymus CI-95 is empirical (12 realisations).

| Scenario | BM flux (cells·day⁻¹) | Thymus export (M cells·day⁻¹) | Transit lag (h) | CD4 pool / set point |
|---|---|---|---|---|
| BM1 baseline | 59.6 [1.4–90.9] | — | — | — |
| THY1 baseline | — | 1.00 | — | — |
| COMP1 direct | 59.6 | 0.80 [0.30–1.0M] | — | — |
| COMP2 transfer | 59.6 | 0.73 [0.08–2.0M] | 95.7 | — |
| COMP3 full graph | 59.6 | 0.73 [0.08–2.0M] | 95.7 | 193,424 / 200,000 |

### V-A. Simulation 1 — Bone Marrow Haematopoiesis Baseline (BM1)

The BM model implements a five-compartment ODE cascade HSC → MPP → LMPP → CLP → DN1, with logistic HSC renewal (K_niche = 11,000 cells, calibrated from Busch et al. 2015 [30]), near-balanced MPP proliferation, and linear downstream rates calibrated from the murine literature [31]–[33]. At day 30, the HSC pool reached 9,075 [7,820–10,401] cells, consistent with published murine bone marrow HSC estimates [30]. The DN1/ETP export flux stabilised at 59.6 [1.4–90.9] cells·day⁻¹, consistent with the Bhandoola et al. 2007 [33] range of 10–100 cells·day⁻¹.

**Table VI.** BM1 key metrics at day 30. CI-95 by Monte Carlo over 2,000 parameter draws.

| Compartment | Day 30 (cells) | CI-95 (MC) | Reference |
|---|---|---|---|
| HSC | 9,075 | [7,820–10,401] | Busch et al. 2015 [30] |
| MPP | 27,225 | [587–39,308] | Busch et al. 2015 [30] |
| LMPP | 11,911 | [288–17,428] | Adolfsson et al. 2005 [31] |
| CLP | 29,777 | [713–44,207] | Kondo et al. 1997 [32] |
| DN1 / ETP | 1,191 | [27–1,942] | Bhandoola et al. 2007 [33] |
| DN1 export flux (cells·day⁻¹) | 59.6 | [1.4–90.9] | Bhandoola et al. 2007 [33] |

*[Figure 1: BM1 — Bone marrow haematopoiesis baseline (ODE, v7, 30 days). Progenitor pool dynamics on log scale with CI-95 bands. Inset: DN1 export flux with expected equilibrium line at 59.6 cells/day.]*

### V-B. Simulation 2 — Thymus Selection Baseline (THY1)

The thymus model is an agent-based simulation of thymocyte development and TCR-mediated selection. The simulation uses 300 agents with scale_factor = 300,000 (based on Scollay & Godfrey 1995 [35]), yielding a simulated thymus of ~10⁸ cells. Agents progress through: DN1 import → DN→DP transition (~20 substeps at 1 h each, total ~20 h) → cortical positive selection (TCR affinity threshold, calibrated from Starr et al. 2003 [39]) → medullary negative selection → SP maturation → export (medullary dwell time ~4–5 days [40]). After an initial maturation lag of 4–5 days (corresponding to the DN→DP→SP transit time), the model exported ~1.0×10⁶ [84,000–2.0×10⁶] cells·day⁻¹ (scaled), consistent with published murine thymic output estimates of 0.5–2×10⁶ naïve T cells·day⁻¹ [34].

**Table VII.** THY1 key metrics at day 30. Values in scaled biological units (scale_factor = 300,000). CI-95 is empirical across 12 ABM realisations.

| Population | Day 30 (cells, scaled) | CI-95 | Reference |
|---|---|---|---|
| DN1 / ETP | 7.2 × 10⁶ | [5M–10M] | Scollay & Godfrey 1995 [35] |
| DP thymocyte | 1.3 × 10⁶ | [381,000–3M] | Egerton et al. 1990 [36] |
| CD4⁺ SP | 1.8 × 10⁶ | [600,000–3M] | Scollay & Godfrey 1995 [35] |
| CD8⁺ SP | 1.1 × 10⁶ | [300,000–2M] | Scollay & Godfrey 1995 [35] |
| Naïve T export (cells·day⁻¹) | 1.0 × 10⁶ | [84,000–2M] | Scollay et al. [34] |

*[Figure 2: THY1 — Thymus T-cell selection baseline (ABM v3, scale_factor = 300,000, 30 days). Stage population dynamics and naïve T export flux across 12 realisations.]*

### V-C. Simulation 3 — BM → Thymus Direct Coupling (COMP1)

COMP1 is the critical architectural test for formalism-agnostic composition: an ODE model wired directly to an ABM with no transfer model and no lag. The thymus `baseline_import` override is set to zero; all progenitor input is provided by the BM ISSL `export_signals.BM.progenitor_export`. The orchestrator's reconciliation layer normalises the ODE flux (deterministic) to the (mean, ci_95) form expected by the ABM's Accept function. Thymic export reached 0.80×10⁶ [300,000–1.0×10⁶] cells·day⁻¹ at day 30. The marginal reduction relative to the THY1 baseline (1.0×10⁶) reflects the slightly lower BM-calibrated import (59.6 vs. the synthetic 75 cells·day⁻¹ used in THY1 standalone).

*[Figure 3: COMP1 — BM → Thymus direct coupling (zero lag). BM progenitor export flux (CI-95) and thymus naïve T export flux (scaled cells/day, CI-95 across 12 realisations).]*

### V-D. Simulation 4 — BM → Blood Transit → Thymus (COMP2)

COMP2 introduced the blood transit ODE as a transfer model on the BM→Thymus edge, providing the first demonstration of model-derived lag computation in OISA. The transit ODE is stateless and invoked on-demand by the transfer dispatcher each time the BM emits a progenitor export signal. Given the BM export flux of 59.6 cells·day⁻¹ and a stop_fraction of 0.82 (representing progenitors that extravasate into non-thymic tissues), the transit ODE computed an effective delivery of 39.75 [37–43] cells·day⁻¹ to the thymus with a lag of 95.7 h (~4 days), consistent with Donskoy & Goldschneider 1992 [37] estimates of 3–5 days transit time. This lag reduced thymic export to 0.73×10⁶ cells·day⁻¹ — a 10% reduction relative to COMP1 — reflecting the delayed progenitor availability at the thymic entry gate.

*[Figure 4: COMP2 — BM → Blood Transit → Thymus. Transit lag annotated at ~day 4. Compare onset with COMP1 to illustrate the additive effect of transit lag on top of intra-thymic maturation lag.]*

### V-E. Simulation 5 — Full Immune Ontogeny Pipeline (COMP3)

COMP3 assembled all four models into a 30-day immune ontogeny simulation. Naïve T cells exported by the thymus are routed to the peripheral LN ODE with a 2-day homing lag (constant, declared in the configuration graph), consistent with Mackay et al. 1990 [41] estimates of 1–3 days for naïve T-cell recirculation. The orchestrator generated 120 OISSL checkpoint records over the 30-day simulation with no watchdog alerts, no constraint violations, and no temporal causality errors.

At day 30, peripheral naïve CD4⁺ T cells reached 193,424 (set point: 200,000; 96.7% maintenance) and CD8⁺ T cells reached 97,093 (set point: 100,000; 97.1% maintenance). The CD4/CD8 ratio evolved from 1.2:1 at day 5 (before substantial thymic export) to 2.0:1 by day 30 — matching the expected murine peripheral ratio [42], [43]. The full ontogeny pipeline demonstrated that upstream architectural choices (transfer model vs. direct coupling) propagate to downstream compartments: COMP3 peripheral CD4⁺ accumulation followed a sigmoid curve with inflection at day 10–12, corresponding to the combined transit lag (~4 days) and intra-thymic maturation lag (~5 days) before meaningful peripheral input began.

*[Figure 5: COMP3 — Full immune ontogeny pipeline (BM → Blood Transit → Thymus → Peripheral LN, 30 days). BM compartments, thymus compartments with selection events, and peripheral LN naïve T-cell pools with CD4/CD8 ratio trajectory.]*

*[Figure 6: Comparative summary across all five runs. Left: BM DN1 export flux across COMP1, COMP2, COMP3. Right: Thymic naïve T export flux — COMP1 (earliest onset), COMP2 (delayed by transit lag ~4 days), COMP3 (identical to COMP2, thymic dynamics unaffected by downstream PLN addition).]*

---

## VI. Discussion

### VI-A. OISA as an Operational Implementation of the CURE Guidelines

The CURE guidelines [29] conclude with an explicit call to action: "given the non-trivial effort required to implement the guidelines, the community moves to automate as many of the guidelines as possible." **Table VIII** maps each CURE criterion to its OISA implementation.

**Table VIII.** OISA components as operational implementations of CURE criteria (Sauro et al. 2025 [29]), extended to the multi-model composition level.

| CURE criterion | OISA component | Implementation |
|---|---|---|
| Credibility — UQ of model outputs | ISSL `internal_parameters` + `ci_95` fields | BM: Monte Carlo over 2,000 parameter draws. Thymus ABM: empirical CI-95 across 12 realisations. Both propagated through inter-model signals. |
| Credibility — scope monitoring | Orchestrator watchdog (`ood_flag`, `divergence_score`) | OOD detector flags models operating outside their calibration envelope at runtime. |
| Credibility — provenance | ISSL `internal_parameters.provenance` + OISSL PROV-O trace | Each parameter posterior linked to calibration dataset via PROV-O URI. Full signal provenance in OISSL. |
| Understandability — levels 1–3 | ISSL envelope + `continuous_state` + `export_signals` | Inputs/outputs (level 1), model components (level 2), and inter-compartmental interactions (level 3) encoded in every ISSL record. |
| Reproducibility — community standards | ISSL schema (JSON-LD) + SED-ML compatibility | OBO ontology URIs (CL:, GO:, PRO:) map directly from existing MIRIAM annotations. SED-ML delta_t values inform config graph. |
| Extensibility — modular reuse | OISA config graph (edge-based wiring) | Any OISA-compliant model substitutable without modifying others. Scaling factor declared in ISSL envelope, not orchestrator. |
| Automation of guideline checking | Orchestrator constraint engine + watchdog | Biological plausibility checks (cell mass conservation, parameter bounds) executed automatically at every GSimT tick. |

Three specific points deserve elaboration. First, OISA implements CURE credibility criteria at the *composition* level rather than the individual model level. A composition can violate biological plausibility even when each constituent model is individually valid — for example, if cell mass is not conserved across an ODE→ABM interface due to unit conversion error. The orchestrator constraint engine checks this at every GSimT tick, catching composition-level failures that individual model validators cannot detect.

Second, the ABM scaling mechanism addresses CURE's understandability requirement at the multi-model scale. The `scale_factor` declaration in the ISSL envelope makes the scaling decision explicit, auditable, and propagated to downstream models — a direct implementation of CURE's requirement that model assumptions be understandable at the composition level.

Third, OISA does not implement all CURE criteria. Individual model validation against experimental data, documentation of internal model assumptions, and governance of ontology adoption remain the responsibility of individual model developers. OISA's constraint engine checks *plausibility* (cell counts within expected ranges, parameters within posterior bounds) but not *validity* against new experimental data.

### VI-B. Why SBML comp and CellML Are Not Sufficient

A natural question is whether SBML's hierarchical composition package (comp) could be extended to handle ABMs, avoiding a new architecture. The answer is architectural: SBML comp and CellML composition require all composed models to be expressed in the same declarative format. An ABM written in Python, Julia, or C++ cannot be represented in SBML without fundamental reimplementation, which would lose the stochastic agent semantics that make ABMs appropriate for thymic selection modelling in the first place.

Vivarium [1] is the closest existing system to OISA in architectural philosophy, with its port-based formalism-agnostic composition interface. Vivarium's limitations in the immunological context are three-fold: it does not provide a standardised inter-model signal format with embedded uncertainty quantification (the ISSL), it does not implement model-derived edge lags (transfer models), and it does not include a biological plausibility constraint engine. OISA addresses all three limitations while maintaining Vivarium's core insight that composition should be formalism-agnostic.

### VI-C. The Transit Lag as a Non-Trivial Simulation Parameter

The 10% reduction in thymic export between COMP1 (direct coupling, 0.80×10⁶ cells·day⁻¹) and COMP2 (transit model, 0.72×10⁶ cells·day⁻¹) deserves interpretation beyond the architectural demonstration. In the murine system, progenitor transit time affects thymic output through two mechanisms: the lag delays the availability of progenitors at the thymic gate, and the stop_fraction reduces the number of progenitors that actually arrive. Both of these are biological parameters that should be modelled explicitly rather than estimated and embedded as constants in a composition framework. The OISA transfer model mechanism makes both parameters visible, adjustable, and linked to their calibration sources — enabling sensitivity analysis and, eventually, patient-specific calibration from clinical blood count data.

### VI-D. Limitations and Open Problems

**Validation scope.** The model parameters are calibrated from published murine data; no independent experimental validation of the composed simulation output has been performed. Full validation requires longitudinal murine data capturing all four compartments simultaneously — an experiment that, to our knowledge, has not been published.

**Feedback loops.** The COMP3 graph is acyclic. Biologically significant feedback loops (e.g., peripheral Treg suppression of thymic output) require the one-tick delay mechanism described in §IV-C.2, which introduces a minimum latency of one GSimT tick (6 h here). Whether this latency is biologically significant depends on the timescale of the feedback process relative to the GSimT tick.

**ABM scaling limitations.** The scale factor approach assumes that 300 agents provide an adequate Monte Carlo estimate of the thymic selection process. With 12 realisations and 300 agents, the effective sample for CI-95 estimation is 3,600 agent-trajectories — sufficient for the mean and CI estimates reported here, but potentially inadequate for tail-event statistics such as autoimmune escape rates.

**Species specificity.** All kinetic parameters are calibrated from murine data. Human immune ontogeny parameters — particularly thymic transit times, selection yields, and peripheral pool set points — differ substantially from murine values and require independent calibration from human data sources before OISA can be applied to human IDTs.

---

## VII. Conclusion

We have proposed and evaluated OISA, the Orchestrated Immune Simulation Architecture, demonstrating its capacity to compose a four-compartment immune ontogeny simulation from heterogeneous ODE and ABM models with formalism-agnostic signal routing, model-derived transfer lags, and automated biological plausibility enforcement. The simulation results are consistent with published murine biology across all five scenarios: BM export at 59.6 cells·day⁻¹ (Bhandoola et al. 2007 [33] range: 10–100), thymic output at ~1.0×10⁶ cells·day⁻¹ (Scollay et al. [34] range: 0.5–2×10⁶), and peripheral CD4/CD8 ratio of ~2:1 at steady state [42], [43].

OISA operationalises the CURE extensibility and automation requirements at the multi-model scale, providing the runtime infrastructure that those guidelines imply but do not specify. It demonstrates that formalism-agnostic composition is achievable without requiring model rewrites, and that the ODE–ABM coupling problem is tractable when output semantics are normalised through a standard log format (ISSL) and scaling decisions are made explicit.

The path from OISA to a clinically deployed immune digital twin remains long. But it no longer requires solving the composition problem from scratch for each new multi-organ modelling project — and that reduction in technical barrier is the contribution this paper aims to establish.

---

## References

[1] E. Agmon et al., "Vivarium: an interface and engine for integrative multiscale modeling in computational biology," *Bioinformatics*, vol. 38, pp. 1972–1979, 2022.

[2] M. Benson, "Digital Twins for Predictive, Preventive, Personalized, and Participatory Treatment of Immune-Mediated Diseases," *Arterioscler. Thromb. Vasc. Biol.*, vol. 43, pp. 410–416, 2023.

[3] X. Li et al., "Digital twins as global learning health and disease models for preventive and personalized medicine," *Genome Med.*, vol. 17, p. 11, 2025.

[4] A. Cappuccio, P. Tieri, and F. Castiglione, "Multiscale modelling in immunology: a review," *Brief. Bioinform.*, vol. 17, pp. 408–418, 2016.

[5] F. Castiglione et al., "Computational Immunology Meets Bioinformatics: the Use of Prediction Tools for Molecular Binding in the Simulation of the Immune System," *PLoS One*, vol. 5, e9862, 2010.

[6] Committee on Foundational Research Gaps and Future Directions for Digital Twins, *Foundational Research Gaps and Future Directions for Digital Twins*. National Academies Press, 2023.

[7] C.M. Lloyd et al., "The CellML Model Repository," *Bioinformatics*, vol. 24, pp. 2122–2123, 2008.

[8] M. Getz et al., "Rapid community-driven development of a SARS-CoV-2 tissue simulator," *iScience*, vol. 23, 101734, 2020.

[9] A. Ghaffarizadeh et al., "PhysiCell: An open source physics-based cell simulator for 3-D multicellular systems," *PLoS Comput. Biol.*, vol. 14, e1005991, 2018.

[10] R. Heiland et al., "PhysiCell Studio: a graphical tool to make agent-based modeling more accessible," *Gigabyte*, 2024, doi: 10.46471/gigabyte.128.

[11] T. Hernandez-Boussard et al., "Digital twins for predictive oncology will be a paradigm shift for precision cancer care," *Nat. Med.*, vol. 27, pp. 2065–2066, 2021.

[12] M. Hucka et al., "The Systems Biology Markup Language (SBML): Language Specification for Level 3 Version 1 Core," *J. Integr. Bioinform.*, vol. 12, pp. 382–549, 2015.

[13] J. Karr et al., "Model Integration in Computational Biology: The Role of Reproducibility, Credibility and Utility," *Front. Syst. Biol.*, vol. 2, 822606, 2022.

[14] H.T. Kaya, E. Surer, and A.C. Acar, "3D Simulation and Comparative Analysis of Immune System Cell Micro-Level Responses in VR and MR Environments," *GOODTECHS 2023*, LNICST 556, pp. 62–78, 2024.

[15] V. Sarpe and F. Jacob, "Simulating the decentralized processes of the human immune system in a virtual anatomy model," *BMC Bioinformatics*, vol. 14 (Suppl. 6), S2, 2013.

[16] M. Liberman et al., "Cell Studio: A platform for interactive, 3D graphical simulation of immunological processes," *APL Bioeng.*, vol. 2, 026107, 2018.

[17] R. Laubenbacher et al., "Building digital twins of the human immune system: toward a roadmap," *npj Digit. Med.*, vol. 5, p. 64, 2022.

[18] R. Laubenbacher et al., "Forum on immune digital twins: a meeting report," *npj Syst. Biol. Appl.*, vol. 10, p. 19, 2024.

[19] R. Laubenbacher, B. Mehrad, I. Shmulevich, and N. Trayanova, "Digital twins in medicine," *Nat. Comput. Sci.*, vol. 4, pp. 184–191, 2024.

[20] R. Laubenbacher et al., "Toward mechanistic medical digital twins: some use cases in immunology," *Front. Digit. Health*, vol. 6, 1349595, 2024.

[21] A. Montagud et al., "Systems biology at the giga-scale: large multi-scale models of complex, heterogeneous multicellular systems," *Curr. Opin. Syst. Biol.*, vol. 28, 100385, 2021.

[22] A. Niarakis et al., "Immune digital twins for complex human pathologies: applications, limitations, and challenges," *npj Syst. Biol. Appl.*, vol. 10, p. 141, 2024.

[23] M. Ponce-de-Leon et al., "PhysiBoSS 2.0: a sustainable integration of stochastic Boolean and agent-based modelling frameworks," *npj Syst. Biol. Appl.*, vol. 9, p. 54, 2023.

[24] F. Bergmann et al., "COMBINE archive and OMEX format: one file to share all information to reproduce a modeling project," *BMC Bioinformatics*, vol. 15, p. 369, 2014.

[25] N.A. Smith et al., "Computational biology of the cardiac myocyte: Proposed standards for the physiome," *J. Exp. Biol.*, vol. 210, pp. 1576–1583, 2007.

[26] M. Viceconti et al., "From the digital twins in healthcare to the Virtual Human Twin," *IEEE J. Biomed. Health Inform.*, vol. 28, pp. 491–501, 2024.

[27] D. Waltemath et al., "Reproducible computational biology experiments with SED-ML," *BMC Syst. Biol.*, vol. 5, p. 198, 2011.

[28] H. Wang et al., "From virtual patients to digital twins in immuno-oncology: lessons from mechanistic QSP modeling," *npj Digit. Med.*, vol. 7, p. 189, 2024.

[29] H.M. Sauro et al., "From FAIR to CURE: Guidelines for Computational Models of Biological Systems," *arXiv*:2502.15597, 2025.

[30] K. Busch et al., "Fundamental properties of unperturbed haematopoiesis from stem cells in vivo," *Nature*, vol. 518, pp. 542–546, 2015.

[31] J. Adolfsson et al., "Identification of Flt3+ lympho-myeloid stem cells lacking erythro-megakaryocytic potential: a revised road map for adult blood lineage commitment," *Cell*, vol. 121, pp. 295–306, 2005.

[32] M. Kondo, I.L. Weissman, and K. Akashi, "Identification of clonogenic common lymphoid progenitors in mouse bone marrow," *Cell*, vol. 91, pp. 661–672, 1997.

[33] A. Bhandoola et al., "Multipotent progenitors can give rise to all major innate immune cells," *Science*, vol. 316, pp. 901–906, 2007.

[34] R. Scollay, J. Smith, and V. Stauffer, "Dynamics of early T cells: prothymocyte migration and proliferation in the adult mouse thymus," *Immunol. Rev.*, vol. 53, pp. 89–106, 1980.

[35] R. Scollay and D.I. Godfrey, "Thymic emigration: conveyor belts or lucky dips?" *Immunol. Today*, vol. 16, pp. 268–273, 1995.

[36] M. Egerton, R. Scollay, and K. Shortman, "Kinetics of mature T-cell development in the thymus," *Proc. Natl. Acad. Sci. USA*, vol. 87, pp. 2579–2582, 1990.

[37] E. Donskoy and I. Goldschneider, "Thymocytopoiesis is maintained by blood-borne precursors throughout postnatal life: a study in parabiotic mice," *J. Immunol.*, vol. 148, pp. 1604–1612, 1992.

[38] C. Benz and C.C. Bleul, "A multipotent precursor in the thymus maps to the branching point of the T versus B lineage decision," *J. Exp. Med.*, vol. 202, pp. 21–31, 2005.

[39] T.K. Starr, S.C. Jameson, and K.A. Hogquist, "Positive and negative selection of T cells," *Annu. Rev. Immunol.*, vol. 21, pp. 139–176, 2003.

[40] T.M. McCaughtry, M.S. Wilken, and K.A. Hogquist, "Thymic emigration revisited," *J. Exp. Med.*, vol. 204, pp. 2513–2520, 2007.

[41] C.R. Mackay, W.L. Marston, and L. Dudler, "Naive and memory T cells show distinct pathways of lymphocyte recirculation," *J. Exp. Med.*, vol. 171, pp. 801–817, 1990.

[42] J.A.M. Borghans and R.J. De Boer, "Interpreting T-cell immunosenescence: it is not all about the size of the haystack," *Immunol. Lett.*, vol. 92, pp. 265–270, 2004.

[43] S.P. Berzins, R.L. Boyd, and J.F.A.P. Miller, "The role of the thymus and recent thymic migrants in the maintenance of the adult peripheral lymphocyte pool," *J. Exp. Med.*, vol. 187, pp. 1839–1848, 1998.

---

*Article type: Methods Proposal / Original Research*

*Data and code availability: OISA specification files, ISSL JSON schemas, reference orchestrator implementation, all model code, configuration graphs, and supplementary parameter tables are available at [repository URL to be added prior to submission]. All model parameters are fully specified in Supplementary Table S1.*

*Species note: All kinetic parameters are calibrated from published murine data. Human parameters can be substituted in `parameters.yaml` without architectural modification.*

*Author contributions: [To be completed prior to submission]*

*Competing interests: The authors declare no competing interests.*
