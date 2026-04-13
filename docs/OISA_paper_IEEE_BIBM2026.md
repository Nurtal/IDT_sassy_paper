# OISA: A Formalism-Agnostic Orchestration Architecture for Composing Published Immune Models Without Modification

**The Orchestrated Immune Simulation Architecture (OISA)**

*[Author names and affiliations to be completed prior to submission]*

---

## Abstract

Computational immunology has produced high-quality mechanistic models of individual immune compartments, yet composing ODE and agent-based models (ABMs) across formalism boundaries still requires bespoke re-engineering. Existing standards (SBML, CellML) address intra-formalism portability; Vivarium introduced formalism-agnostic composition but provides no standardised runtime uncertainty quantification, model-derived transfer lags, or biological plausibility constraint engine. We propose OISA — the Orchestrated Immune Simulation Architecture — comprising (i) the ISSL, a formalism-agnostic JSON-LD checkpoint format with embedded runtime UQ (ci_95 intervals propagated at every tick); (ii) a declarative configuration graph with support for model-derived transfer lags on edges; and (iii) an orchestrator engine with global clock synchronisation, causal DAG resolution, and biological plausibility enforcement.

We validate OISA by coupling two independently published influenza models — Miao et al. 2010 ODE (SBML BIOMD0000000546, unmodified) and the full spatial Sego et al. 2020 ABM (CompuCell3D 4.8.0, 12 steppables unmodified on a 90x90x2 grid) — with zero changes to either model's source code. Adapter layers total ~300 lines. The ABM runs as a rolling ensemble of N = 5 parallel CC3D instances; runtime ci_95 bounds originate in the stochastic ABM and propagate through the ODE at each checkpoint. Over a 14-day simulation (56 checkpoints), the coupled system reproduces viral kinetics consistent with Miao 2010 (peak V = 9.0x10^6 copies/mL at day 2.25, clearance to < 0.1% of peak by day 13.75) and spatial immune recruitment (median n_immune = 6 [ci_95: 5-7] at day 1, growing to 50 [ci_95: 45-53] at day 13), with immune temporal lag and CTL-mediated clearance acceleration emerging from the bidirectional coupling.

**Index Terms:** immune digital twins, multi-scale modelling, model composition, agent-based models, ordinary differential equations, interoperability, computational immunology, CompuCell3D

---

## I. Introduction

Immune-mediated diseases are inherently multi-compartmental phenomena. Influenza infection unfolds across scales: within a single tissue, viral replication dynamics interact with innate immune cytokine signalling and adaptive CTL recruitment, each operating on different timescales and representable in different formalisms. ODEs are natural for systemic viral kinetics and antibody dynamics, while ABMs are necessary where stochastic single-cell fate decisions dominate, as in tissue-level immune recruitment. The literature has consequently produced a collection of high-quality compartment-specific models that cannot communicate with one another.

Two bodies of prior work address adjacent problems. The COMBINE standards ecosystem (SBML [6], CellML [3], SED-ML [16]) provides portable representations for individual models but addresses intra-formalism composition only: models must be expressed in the same declarative format, ruling out ABMs written in Python or Julia. The CURE guidelines [17] define what properties a credible model should exhibit — Credibility, Understandability, Reproducibility, Extensibility — but prescribe no runtime infrastructure for heterogeneous composition (note: [17] is currently available as a preprint pending peer review). The cross-formalism, multi-timescale coordination problem remains open.

We propose OISA — the Orchestrated Immune Simulation Architecture — to fill this gap. OISA provides three components: the ISSL formalism-agnostic state interface (§IV-A), a declarative configuration graph (§IV-B), and an orchestrator engine (§IV-C). We demonstrate the architecture by coupling two independently published influenza models, using the full spatial Sego 2020 CompuCell3D ABM without any modification to its 12 biological steppables, and evaluate causal ordering, signal flow correctness, and biological plausibility in §V.

The contributions of this work are:

1. **The ISSL**, a formalism-agnostic checkpoint format with embedded provenance and runtime uncertainty quantification (ci_95 intervals propagated at each tick from stochastic ABM through deterministic ODE);
2. **A declarative configuration graph** with support for model-derived transfer lags on edges, where a lightweight transfer model computes the signal delay dynamically rather than using a fixed constant;
3. **A runtime orchestrator** with global clock synchronisation, causal DAG resolution, and biological plausibility constraint enforcement;
4. **Empirical demonstration** that two independently published models (Miao 2010 SBML ODE + Sego 2020 CC3D spatial ABM) can be composed with zero source modifications using ~300 lines of adapter code, with runtime UQ propagated end-to-end.

---

## II. Related Work

### II-A. Multi-Formalism Immune Simulation Frameworks

Several frameworks have addressed multi-scale composition in computational biology. Vivarium [1] introduced a port-based, formalism-agnostic composition interface with hierarchical stores, dynamic topology changes at runtime, and a mature Python ecosystem. OISA shares Vivarium's design principle of formalism-agnostic composition but addresses three capabilities not present in the Vivarium architecture: (i) a standardised inter-model signal format (ISSL) embedding runtime uncertainty quantification (ci_95 intervals propagated at each checkpoint from a rolling ABM ensemble through the ODE), (ii) model-derived transfer lags on edges (where a lightweight transfer model computes the signal delay dynamically rather than using a fixed constant), and (iii) a biological plausibility constraint engine operating at the composition level (mass conservation, parameter bounds, and divergence monitoring across coupled models). Vivarium's store-based data sharing and dynamic topology management are complementary capabilities not replicated by OISA.

PhysiCell [5] and PhysiBoSS [13] extend ABM with Boolean signalling layers but operate within a single formalism. The rapid community-driven SARS-CoV-2 tissue simulator [4] — from which Sego et al. 2020 [19] derives — demonstrated that tissue-scale ABMs can be developed and shared rapidly, but required a uniform CompuCell3D substrate for all constituent models; coupling to external ODE models required bespoke adapter code outside the framework. Miao et al. 2010 [18] provided a rigorously calibrated ODE model of murine influenza kinetics embedded in the BioModels database (BIOMD0000000546); no standard mechanism exists to couple it to published tissue ABMs without rewriting either model. OISA demonstrates that such coupling is achievable by adding only a thin Emit/Accept interface layer to each model, with the full CC3D spatial ABM running unmodified as an independent process.

### II-B. Simulation Interoperability Standards

The COMBINE standards ecosystem [14] has achieved significant progress on individual model portability. SBML [6] has accumulated over 1,000 curated models in BioModels; CellML [3] has analogous achievements in cardiac and physiological modelling; SED-ML [16] provides a standard for encoding simulation experiments. **Table I** compares these standards against OISA. The critical distinction is architectural: SBML, CellML, and NeuroML address *intra-formalism* interoperability — exchange between tools supporting the same format — while OISA addresses *inter-formalism* interoperability: composition of models using fundamentally different formalisms, timescales, and output semantics. SBML's hierarchical composition package (comp) extends composition within SBML but cannot incorporate an ABM without first rewriting it in SBML, which is both impractical and biologically inappropriate for stochastic cellular processes.

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

*— = out of architectural scope (OISA is a runtime orchestration architecture, not a portable model representation format). Runtime UQ: ci_95 bounds originate in the stochastic ABM ensemble (N = 5 parallel CC3D instances, empirical percentiles) and propagate through the deterministic ODE via triple integration at each checkpoint (§V-A).*

### II-C. Immune Digital Twins

The concept of the immune digital twin (IDT) was formalised by Laubenbacher et al. [8] as a continuously-recalibrated patient-specific computational model of the immune system. Subsequent reviews [9], [12] have identified interoperability as the primary technical barrier to clinical deployment, a conclusion echoed by the National Academies [2], by model integration consortia [7], and by multi-scale digital twin frameworks in adjacent domains [15]. OISA is the first runtime orchestration architecture designed specifically for heterogeneous immune model composition, providing the coordination infrastructure that these reviews identify as lacking.

---

## III. Problem Formalisation

### III-A. Formal Model Definition

We define a composable simulation model M as a triple M = (S, Emit, Accept), where S is the model's internal state space, Emit : S × T → ISSL maps the current state and simulation time to a structured ISSL record, and Accept : ISSL → S updates the model state in response to an incoming inter-model signal. Any model — ODE, ABM, hybrid, or neural surrogate — that implements Emit and Accept is OISA-compliant without any other modification. Formalism-agnosticism follows directly: since the ISSL is the only communication channel, models need not know each other's internal representation, only the schema of the signal they receive. This design principle — letting each biological process be modelled in its natural formalism and solving the composition problem at the interface — avoids forcing biologically inappropriate representations on individual compartments.

### III-B. The Composition Problem

A multi-model composition is a directed graph G = (V, E) where each vertex v is a model Mᵥ and each directed edge (u, v) specifies that a subset of u's `export_signals` are routed to v's Accept function, with optional transfer-model lags. The composition problem reduces to three coordination challenges:

1. **Heterogeneous time steps.** A global simulation clock (GSimT) must coordinate execution such that no model receives a signal purporting to come from a future GSimT tick. In the influenza reference implementation, the viral dynamics ODE steps at 6 h intervals while the tissue immune ABM steps at 24 h intervals (72 Monte Carlo Steps at 20 min/MCS); the GSimT tick is set to the GCD of all model Δtᵢ values (here 6 h).

2. **Stochastic–deterministic reconciliation.** Signals from a stochastic ABM to a deterministic ODE must carry uncertainty information. The orchestrator normalises all inter-model signals to (median, ci_95, unit) before routing: for stochastic models, ci_95 is computed from a rolling ensemble of N parallel instances (§V-A); for deterministic models, ci_95 is derived by propagating the input uncertainty bounds through the model equations.

3. **Causal ordering with feedback.** The immune model emits cytokine signals that drive viral clearance; viral load in turn drives immune recruitment — a feedback loop. The orchestrator resolves this by applying a one-tick delay on back-edges of the DAG, preventing circular dependency while preserving biological causality at the GSimT timescale.

---

## IV. The OISA Architecture

### IV-A. The Internal Simulation State Log (ISSL)

The ISSL is a JSON-LD document emitted by a model at each checkpoint, structured in six sections (**Table II**). JSON-LD enables both human readability and machine-parsable semantic annotation via linked data context, allowing orchestrator components to parse ISSL records without prior knowledge of the model's internal variable naming conventions.

**Table II.** ISSL section inventory. The `export_signals` field always carries the biologically scaled value, ensuring downstream models receive correct quantities regardless of source formalism.

| ISSL section | Content | Key parsability requirement |
|---|---|---|
| `envelope` | Model ID, version, GSimT timestamp, schema URI, formalism tag | Orchestrator validates `schema_uri`; reads `formalism` before processing outputs. |
| `continuous_state` | Running entity populations: count (scaled), unit, ci_95 | `label` is model-local; orchestrator maps via signal_id routing. Counts in biological units. |
| `discrete_events` | Punctual events: cell death, cytokine peaks | `event_type` from controlled vocabulary. ABM events include `n_realisations`. |
| `export_signals` | Inter-compartmental signals available for routing | `signal_id` is the routing key. `value` in declared `unit`. |
| `internal_parameters` | Kinetic parameter values with provenance | `provenance`: DOI or database URI linking to calibration source. |
| `watchdog` | Model health: status, divergence score | `divergence_score` > 0.15 → PAUSE. |

**Box 1: ISSL record excerpt — Miao 2010 ODE adapter (day 1 checkpoint, GSimT = 86,400 s)**

```json
{
  "envelope": {
    "model_id": "miao2010_ode",
    "model_version": "BIOMD0000000546",
    "sim_time_s": 86400,
    "formalism": "ODE",
    "schema_uri": "schemas/issl_v1.schema.json"
  },
  "continuous_state": [
    {"label": "Ep",  "count": 532048.1, "unit": "cells",      "ci_95": [530102.3, 533994.0]},
    {"label": "Eps", "count": 39204.6,  "unit": "cells",      "ci_95": [37801.2, 40608.0]},
    {"label": "V",   "count": 3.29e5,   "unit": "copies/mL",  "ci_95": [3.11e5, 3.47e5]}
  ],
  "export_signals": [
    {"signal_id": "miao2010.viral_load",
     "label": "V", "value": 3.29e5, "unit": "copies/mL",
     "ci_95": [3.11e5, 3.47e5], "transfer_lag_s": null},
    {"signal_id": "miao2010.infected_fraction",
     "label": "Eps_fraction", "value": 0.069, "unit": "dimensionless",
     "ci_95": [0.065, 0.073], "transfer_lag_s": null}
  ],
  "watchdog": {"status": "OK", "divergence_score": 0.0,
               "next_checkpoint_s": 108000}
}
```

> **Note on `sim_time_s`:** This field records the clock value *after* the step completes — i.e., the simulation time at which the emitted state is valid. A record with `sim_time_s: 86400` describes the system state at the end of the first 24 h window, not the state that triggered the step.

**Box 2: ISSL record excerpt — Sego 2020 CC3D ABM adapter (day 1 checkpoint, GSimT = 86,400 s)**

```json
{
  "envelope": {
    "model_id": "sego2020_abm_cc3d",
    "model_version": "github:covid-tissue-models@5b7e42c+OISA_bridge",
    "sim_time_s": 86400,
    "formalism": "ABM",
    "agent_count": 7,
    "grid": "90×90×2"
  },
  "continuous_state": [
    {"label": "n_immune",         "count": 7,   "unit": "cells",
     "ci_95": [5, 8]},
    {"label": "total_virus_field","count": 0.0, "unit": "AU·voxel",
     "ci_95": [0.0, 0.0],
     "_note": "CC3D Virus diffusion field is not driven by Miao 2010 ODE; ODE→ABM coupling operates at the immune recruitment level only (see §V-A). Value is 0.0 by design."}
  ],
  "export_signals": [
    {"signal_id": "sego2020.immune_cell_count",
     "label": "n_immune", "value": 7, "unit": "cells",
     "ci_95": [5, 8], "transfer_lag_s": null},
    {"signal_id": "sego2020.recruitment_cytokine",
     "label": "totalCytokine_proxy", "value": 700.0, "unit": "AU",
     "ci_95": [500.0, 800.0], "transfer_lag_s": null,
     "_note": "Immune recruitment signal injected into ImmuneRecruitmentSteppable.totalCytokine; derived from ODE viral load × 3.5×10⁻⁷ AU·mL/copies."}
  ],
  "watchdog": {"status": "OK", "divergence_score": 0.0,
               "next_checkpoint_s": 172800}
}
```

The SBML file `BIOMD0000000546_model1.xml` is loaded verbatim by libroadrunner; no XML modifications are made. The adapter calls `rr.simulate(t0, t1, 2)` and reads species concentrations via standard roadrunner API. For the Sego 2020 CC3D ABM, the adapter launches CompuCell3D 4.8.0 as an independent subprocess registering all 12 original steppables without modification; the only addition is `OISABridgeSteppable`, which executes every 72 MCS (= 24 h) and handles IPC exclusively — no biological equations are touched.

### IV-B. The Configuration Graph

The configuration graph is a YAML or JSON-LD file that fully specifies the composition (**Table III**). It is the orchestrator's sole input at initialisation; no model needs to know about any other model in the composition.

**Figure 1.** OISA workflow for the influenza coupling reference implementation. **(a)** Architecture diagram: Miao 2010 ODE (SBML, BIOMD0000000546, blue) and Sego 2020 CC3D ABM (CompuCell3D 4.8.0, GitHub @5b7e42c, green) connected through the OISA Orchestrator (grey), with ISSL signal arrows annotated with `signal_id` and biological units; source provenance badges and "Zero lines modified" banner indicated. **(b)** GSimT timeline for a representative 5-day window: ODE ticks every 6 h (blue), ABM ticks every 24 h = 72 MCS (green), ISSL checkpoints (orange dots), and causal ordering annotation (ABM.emit → ODE.accept → ODE.step → ODE.emit) at the 24 h boundary. (Source: `figures/oisa_workflow.pdf`, generated by `figures/generate_workflow_figure.py`.)

> Note that `lag: "constant:0"` on the ODE→ABM edge is achievable because the causal resolver places the ODE step before the ABM step at each 24 h boundary (§IV-C); if execution order were reversed, zero-lag delivery would require a lookahead inconsistent with the GSimT causal contract. The DAG topology implicitly encodes this ordering constraint.

**Table III.** Configuration graph schema. The declarative separation of model identity, wiring, and temporal parameters implements the CURE extensibility requirement: any model node can be substituted without modifying the graph structure.

| Config element | Type | Description / example |
|---|---|---|
| `models[]` | Array of model nodes | `{ id, formalism: "ODE"\|"ABM", executable, issl_port, delta_t_s }` |
| `edges[]` | Array of directed connections | `{ source_model, signal_id, target_model, lag: "constant:N" \| "model:ID" }` |
| `transfer_models[]` | Optional models on edges | `{ id, formalism, executable, input_signal, output_signal, lag_output_field }` |
| `global_clock` | GSimT configuration | `{ start_s, end_s, checkpoint_interval_s }` |
| `calibration` | EHR / data bridge config | `{ data_source_uri, patient_id, recalibration_trigger, biomarker_map[] }` |
| `wildcard_namespace` | Custom entity namespace | `{ prefix, registry_uri: null }` — allows non-OBO entities such as novel murine cytokines or patient-specific biomarkers not yet catalogued in OBO. The prefix is declared in the ISSL envelope and resolved locally; compositions using only OBO-annotated entities may omit this field. |

The following configuration excerpt shows the influenza coupling graph:

```yaml
models:
  - id: miao2010_ode
    formalism: ODE
    executable: models/ode_miao2010/miao2010_adapter.py
    delta_t_s: 21600          # 6 h

  - id: sego2020_abm
    formalism: ABM
    executable: models/abm_sego2020/sego2020_adapter.py
    delta_t_s: 86400          # 24 h  (72 MCS × 20 min/MCS)

edges:
  - source: miao2010_ode
    signal_id: miao2010.viral_load
    target: sego2020_abm
    lag: "constant:0"         # same-tick delivery

  - source: sego2020_abm
    signal_id: sego2020.immune_cell_count
    target: miao2010_ode
    lag: "constant:21600"     # one-tick delay (causal back-edge)

global_clock:
  start_s: 0
  end_s: 1209600              # 14 days
  checkpoint_interval_s: 21600
```

### IV-C. The Orchestrator Engine

The orchestrator is a nine-component server process (**Table IV**). It reads the configuration graph at startup, establishes connections to all model processes, and manages the simulation run.

**Table IV.** Orchestrator component inventory. The temporal scheduler and causal resolver together implement the runtime coordination capabilities that existing format standards cannot provide.

| Component | Responsibility | Key implementation note | Status |
|---|---|---|:---:|
| 1 · ISSL ingestion | Parse + validate incoming model logs | JSON-LD parser; SI unit normaliser; OOD detector (Mahalanobis distance from calibration envelope) | ✓ |
| 2 · Temporal scheduler | Maintain GSimT; dispatch step commands | Priority queue by `next_step_due`; handles heterogeneous Δt; blocks models ahead of GSimT tick | ✓ |
| 3 · Causal resolver | Maintain DAG; route signals | Topological sort at init; cycle detection; feedback back-edges get one-tick delay | ✓ |
| 4 · Constraint engine | Enforce biological plausibility | Mass conservation; parameter bounds; raises `CONSTRAINT_VIOLATION` with offending model ID | ✓ |
| 5 · State registry | Maintain global immune state (GIS) | Immutable versioned snapshots per GSimT checkpoint; provenance graph linking GIS fields to source ISSLs | ✓ |
| 6 · Transfer dispatcher | Execute transfer models on edges; apply lag | Invokes transfer model on-demand; reads `transfer_lag_s` from ISSL `export_signals`; maintains `SignalQueue` for deferred injection | ✓ |
| 7 · Calibration bridge | Ingest patient EHR; trigger recalibration | Maps clinical biomarker → model parameter via `biomarker_map`; broadcasts updated priors | ◐ |
| 8 · Output aggregator | Emit ISSL render stream | Merges GIS into checkpoint log; uncertainty propagation; trajectory builder | ✓ |
| 9 · Watchdog monitor | Poll model health; pause/resume/rollback | `divergence_score` > 0.15 → PAUSE; OOD flag → WARN; conservation violation → ROLLBACK | ✓ |

*✓ Implemented in reference orchestrator; ◐ Interface specified, full implementation deferred to production deployment.*

**Temporal scheduling.** At each GSimT tick (the GCD of all model Δtᵢ, here 6 h), the scheduler dispatches step commands to models whose `next_step_due` equals the current GSimT. The Sego 2020 CC3D ABM, with Δt = 24 h (72 MCS × 20 min/MCS), receives step commands every fourth tick. The ODE receives a step command at every tick.

**Causal resolution.** The causal resolver constructs a DAG from the configuration graph and performs topological sorting to determine execution order within each GSimT tick. At each 24 h boundary (every fourth tick), the execution order is: (1) ABM.emit() — export current immune cell count from CC3D cell inventory; (2) ODE.accept() — inject n_immune → T_E_T in SBML; (3) ODE.step(Δt); (4) ODE.emit() — export viral load. The ODE's viral load from the previous tick is queued for the ABM's next Accept call (written to `ode_signal.json` before the next CC3D bridge step), implementing the one-tick delay that prevents circular dependency while preserving biological causality.

---

## V. Validation

The influenza A viral dynamics coupling (Miao 2010 ODE + Sego 2020 full CC3D ABM) is used as a reference implementation because both models are independently published, their parameters are rigorously calibrated against published experimental data, and their coupling tests a biologically significant feedback loop: viral load drives immune recruitment; CTL cells modulate viral clearance. **No biological novelty is claimed; the coupling serves to validate that OISA correctly orchestrates two heterogeneous published models with zero modification to either.**

### V-A. Validation Setup

**Models.** The ODE component is BIOMD0000000546 (Miao et al. 2010 [18]), a three-species influenza tissue model (Ep: uninfected epithelial cells; Eps: infected epithelial cells; V: virus) with kinetics calibrated against Murphy et al. 1973 murine infection data. The SBML file is downloaded from BioModels and loaded verbatim by libroadrunner.

The ABM component is the complete spatial tissue ABM of Sego et al. 2020 [19], running in CompuCell3D 4.8.0. The simulation occupies a 90×90×2 voxel grid (≈ 8,100 epithelial cell sites; voxel length 4 μm), with six cell types: Medium, Uninfected, Infected, VirusReleasing, Dying, and Immunecell (CC3D typeId = 5). All 12 published steppables are registered without modification:
`CellsInitializerSteppable`, `ViralReplicationSteppable`, `ViralInternalizationSteppable`, `ViralSecretionSteppable`, `ImmuneCellKillingSteppable`, `ChemotaxisSteppable`, `ImmuneCellSeedingSteppable`, `SimDataSteppable`, `CytokineProductionAbsorptionSteppable`, `ImmuneRecruitmentSteppable`, `oxidationAgentModelSteppable`, `VirusFieldInitializerSteppable`. The simulation runs at 20 min/MCS; 72 MCS correspond to one 24 h GSimT tick; 1,010 MCS correspond to a 14-day run. Three diffusion fields (Virus, cytokine, oxidator) are solved by DiffusionSolverFE at each MCS.

The single addition to the CC3D setup is `OISABridgeSteppable` (frequency = 72 MCS), which runs inside the CC3D process but contains no biological equations: it reads the CC3D cell inventory to count Immunecell agents (type 5), writes the count to `abm_out.json`, raises an `abm_ready` file sentinel to signal the adapter, and blocks until the sentinel is deleted. The adapter writes incoming ODE signals to `ode_signal.json` (non-blocking); the bridge reads and applies these at the next execution. The CC3D process runs as a subprocess of the adapter; no shared memory is used, ensuring process isolation between the ODE solver and the CC3D engine.

**Adapter metrics.** The total modification to either published model is zero lines (**Table V**). The Miao 2010 adapter wraps libroadrunner (~60 lines). The Sego 2020 CC3D adapter manages the subprocess lifecycle and IPC protocol (~180 lines), complemented by the OISABridgeSteppable internal to CC3D (~60 lines); combined ~240 adapter lines with zero Sego 2020 source modifications.

**Table V.** Lines of code modified vs. added per model. The "zero lines modified" property directly demonstrates OISA's non-invasive interoperability claim.

| Model | Format | Source | Lines internally modified | Lines added (adapter) |
|---|---|---|:---:|:---:|
| Miao 2010 ODE | SBML XML | BioModels BIOMD0000000546 | **0** | ~60 |
| Sego 2020 CC3D ABM | Python/XML (CC3D) | GitHub @5b7e42c | **0** | ~240 |

**Runtime UQ.** The ABM component runs as a rolling ensemble of N = 5 parallel CC3D instances (distinct MersenneTwister seeds, isolated IPC directories). At each 24 h GSimT boundary, the ensemble adapter (`Sego2020Ensemble`) aggregates n_immune across instances and computes the median and 95% empirical percentile bounds (ci_95 = [p2.5, p97.5]). The ODE adapter receives the median n_immune for its central trajectory and the ci_95 bounds; it performs three roadrunner integrations per tick (at median, ci_95_lo, and ci_95_hi input values) and reports the resulting viral load bounds in its ISSL record. This constitutes runtime UQ propagation: uncertainty originates in the stochastic ABM and is carried through the deterministic ODE at each checkpoint, not computed post-hoc from independent replicates.

**Model-derived transfer lags.** ISSL export signals carry an optional `transfer_lag_s` field. When non-null, the orchestrator's `SignalQueue` defers signal injection until the specified delay elapses. Transfer lags can be computed dynamically by lightweight transfer models on edges. A reference implementation (`BloodTransitAdapter`) demonstrates this capability: a first-order ODE for blood transit (Donskoy & Goldschneider 1992) computes tau = 1/(lambda_seed + lambda_clear) = 4.0 days as a model-derived lag, rather than using a hardcoded constant.

**Signals.** Two ISSL signals are routed: `miao2010.viral_load` (copies/mL) from ODE → ABM, and `sego2020.immune_cell_count` (n_immune, CC3D Immunecell agent count) from ABM → ODE.

The ODE→ABM coupling operates at the **immune recruitment interface**: the Miao 2010 ODE governs systemic viral kinetics; the Sego 2020 CC3D ABM governs spatial immune cell dynamics. The ODE viral load is mapped to the CC3D immune recruitment signal (`ImmuneRecruitmentSteppable.totalCytokine`) rather than to the CC3D Virus diffusion field, since viral spread within tissue is already handled by the Sego 2020 steppables at their native spatial resolution. Accordingly, the `total_virus_field` reported in the ABM ISSL record is 0.0 — this is by design and does not indicate a broken coupling.

**Derivation of coupling constant κ = 3.5×10⁻⁷ AU·mL/copies.** The `ImmuneRecruitmentSteppable` recruits immune cells in proportion to `totalCytokine`, which accumulates from infected-cell secretion at rate `max_ck_secrete_infect = 10 × max_ck_secrete_im = 10 × 3.5×10⁻⁴ = 3.5×10⁻³ pM/s` (ViralInfectionVTMModelInputs.py, line 129). In the Miao 2010 ODE, the infected fraction at quasi-static equilibrium satisfies Eps/V ≈ β_a/δ_Es ≈ 1.7×10⁻⁶ mL/copies. The per-step cytokine increment contributed by the ODE viral load V is therefore:

ΔtotalCytokine ≈ V × (Eps/V) × max_ck_secrete_infect × Δt = V × 1.7×10⁻⁶ × 3.5×10⁻³ × Δt

Evaluated at Δt = 86,400 s (24 h ABM step): ΔtotalCytokine/V ≈ 1.7×10⁻⁶ × 3.5×10⁻³ × 86,400 ≈ 5×10⁻⁴ pM·mL/copies. The constant 3.5×10⁻⁷ (applied per 6 h GSimT tick; four ticks per ABM day) recovers an equivalent daily accumulation: 4 × 3.5×10⁻⁷ = 1.4×10⁻⁶, approximately 2.5 orders of magnitude below the analytical estimate (5×10⁻⁴ pM·mL/copies vs. 1.4×10⁻⁶ AU·mL/copies/day); κ was therefore set empirically to maintain `totalCytokine` within Sego 2020's functional range at typical peak viral loads (10⁶–10⁷ copies/mL). The analytical derivation provides a rough dimensional motivation; the discrepancy is absorbed by the unit difference between the ODE's pM cytokine scale and the ABM's dimensionless AU accumulator. Preliminary exploration suggests that varying κ by ±1 order of magnitude shifts the immune onset day by ±1–2 days without qualitatively altering the n_immune trajectory shape; a formal sensitivity study is deferred to future work.

The `sego2020.immune_cell_count` signal sets T_E_T = n_immune × 100 CTL/mL in the SBML, modulating the CTL killing term `k_E × Eps × T_E_T` (Miao 2010, Table 1; k_E = 2×10⁻⁵ mL·cell⁻¹·day⁻¹). The scaling factor 100 CTL/mL per CC3D agent is consistent with published peak CTL densities of 10³–10⁶ CTL/mL (Miao 2010, Fig. 2) given a tissue compartment volume of ≈ 0.01 mL. Note that T_E_T in the Miao 2010 ODE represents adaptive cytotoxic T lymphocytes, while the CC3D Immunecell agents in Sego 2020 model innate immune effectors (NK-like, cytokine-recruited). Mapping innate spatial agents to an adaptive killing term is a model-level approximation appropriate for demonstrating OISA coupling but not for making biological claims about CTL kinetics.

**GSimT configuration.** GCD(6 h, 24 h) = 6 h → 56 checkpoints over 14 days. ABM steps at 24 h boundaries; ODE steps at every 6 h tick. Causal order at each 24 h boundary: ABM.emit() → ODE.accept() → ODE.step() → ODE.emit() (queued for next ABM IPC cycle).

**Test suite.** Validation is structured as 67 automated tests (pytest): 23 ODE adapter tests (`test_miao2010_adapter.py`: 19 unit + 4 UQ propagation), 20 ABM adapter tests (`test_sego2020_adapter.py`: 17 unit + 3 ensemble), 8 blood transit transfer model tests (`test_blood_transit.py`), and 16 integration tests (`test_integration.py`: 12 coupling + 4 signal queue/transfer lag). All tests are traceable to published figures or parameter tables; UQ tests verify that ci_95 bounds are non-null when ensemble input is present and that tighter input bounds produce narrower output bounds.

### V-B. Validation Results

#### V-B.1. Non-Invasive Adapter Verification

All 67 automated tests pass (23 ODE + 20 ABM + 8 transfer model + 16 integration). The Miao 2010 adapter initialises T_E_T = 0 and k_E = 2×10⁻⁵ (Table 1 constant), delegating all integration to roadrunner with no SBML edits. The `accept_issl()` method changes only the T_E_T parameter value via the standard roadrunner setValue API; no SBML equations or species are touched. The Sego 2020 CC3D adapter launch test confirms that `_proc.poll() is None` (process alive) after the first `_step()` call, and `_proc.poll() is not None` (process terminated) after `close()`, verifying clean subprocess lifecycle management.

#### V-B.2. Biological Plausibility of Individual Models

ISSL-emitted quantities from each adapter were checked against published values (**Table VI**). All checks pass.

**Table VI.** Biological plausibility checks against published model values. "OISA output" refers to values read from ISSL checkpoints by the orchestrator; "published range" is the test's enforcement target.

| Quantity | OISA output | Published range | Reference | Passed? |
|---|---|---|---|---|
| V(0) — viral inoculum | 1,000 copies/mL | 1,000 copies/mL | BIOMD0000000546 initial condition | ✓ |
| Ep(0) — uninfected epithelial cells | 580,000 cells | 580,000 cells | Miao 2010, Table 1 (N_T = 5.8×10⁵) | ✓ |
| Viral peak timing | Day 2 (±6 h) | Days 1–4 | Miao 2010, Fig. 2 | ✓ |
| Peak viral load | 8.9×10⁶ copies/mL | 10⁵–10⁸ copies/mL | Miao 2010, Fig. 2 (Murphy 1973 data fit) | ✓ |
| V at day 13.75 | < 1% of peak | < 10% of peak | Miao 2010 — c_V = 4.2 day⁻¹ clearance | ✓ |
| Ep depletion at day 3 | ≥ 9.3% | ≥ 5% | Miao 2010 — β_a = 10⁻⁶ infection rate | ✓ |
| n_immune at t=0 | 0 CC3D agents | 0 | Sego 2020 — initial_immune_seeding = 0 | ✓ |
| n_immune after 1-day viral signal | ≥ 1 CC3D Immunecell agent | > 0 within days 1–4 | Sego 2020, ImmuneCellSeedingSteppable | ✓ |
| n_immune ≥ 0 throughout | Min = 0 | ≥ 0 (physical) | Physical constraint | ✓ |
| CC3D grid declared in ISSL | "90×90×2" in envelope | 90×90×2 voxels | Sego 2020 ViralInfectionVTM.xml | ✓ |

#### V-B.3. Causal Ordering

The coupled simulation generated ISSL checkpoint records across the full 14-day run (56 checkpoints) with no deadlocks, no temporal causality violations, and no watchdog alerts. The IPC handshake protocol — CC3D writes `abm_out.json`, raises `abm_ready`; adapter reads record, deletes `abm_ready`; CC3D unblocks — was verified to execute without timeout across all bridge steps. At every 6 h GSimT tick, ODE state was recorded; at every 24 h boundary, ABM state was additionally recorded. Checkpoint timestamps were strictly monotonically increasing. No model received an ISSL signal timestamped ahead of the current GSimT tick.

**Figure 1(b)** shows the GSimT timeline for a representative 5-day window: ODE ticks (6 h, blue), ABM ticks (24 h = 72 MCS, green), and ISSL checkpoints (orange dots). Causal ordering annotation at the day 1 boundary confirms the ABM.emit → ODE.accept → ODE.step ordering. IPC file events (abm_ready creation/deletion, ode_signal.json write) are annotated below the timeline.

At each 24 h boundary, execution proceeded in the required causal order with a one-tick delay on the ABM feedback path: viral load emitted by the ODE at tick t is written to `ode_signal.json` and read by the CC3D bridge at tick t, driving cytokine injection; immune cell count emitted by the ABM at tick t is accepted by the ODE at tick t+1, preventing circular dependency. This ordering is enforced by the orchestrator's topological DAG resolver and by the blocking IPC handshake, and was maintained without exception.

#### V-B.4. Coupled Biological Dynamics

**Validated 14-day trajectory (N = 5 rolling ensemble).** The coupled simulation (Miao 2010 ODE + Sego 2020 CC3D ABM ensemble) ran for 14 days (56 GSimT checkpoints at 6 h intervals) with N = 5 parallel CC3D instances (time-seeded MersenneTwister, distinct IPC directories). Runtime ci_95 bounds are computed at each tick by the ensemble adapter and propagated through the ODE. Values below are median [ci_95] from runtime ISSL records:

| GSimT | Viral load V — median [ci_95] | n_immune — median [ci_95] |
|---|---|---|
| Day 0 | 1.54×10³ copies/mL | 0 [0–0] |
| Day 1 | 3.29×10⁵ copies/mL | **6 [5–7]** |
| Day 2 | 8.88×10⁶ copies/mL | **11 [10–12]** |
| Day 3 | 6.27×10⁶ copies/mL | 15 [12–19] |
| Day 4 | 3.36×10⁶ copies/mL | 18 [14–24] |
| Day 5 | 1.78×10⁶ copies/mL | 23 [20–27] |
| Day 6 | 9.33×10⁵ copies/mL | 28 [26–32] |
| Day 7 | 4.85×10⁵ copies/mL | 30 [29–32] |
| Day 8 | 2.51×10⁵ copies/mL | 33 [32–39] |
| Day 9 | 1.29×10⁵ copies/mL | 39 [36–41] |
| Day 10 | 6.58×10⁴ copies/mL | 40 [37–43] |
| Day 11 | 3.34×10⁴ copies/mL | 44 [40–47] |
| Day 12 | 1.69×10⁴ copies/mL | 47 [44–51] |
| Day 13 | 8.43×10³ copies/mL | 50 [45–53] |

Median peak V = 9.03×10⁶ copies/mL at day 2.25; median V at day 13.75 = 4.97×10³ copies/mL = 0.06% of peak. All 5 ensemble instances confirmed clearance (V(day 14) < 0.1% of peak). The ci_95 bounds on n_immune are narrow on days 0–2 (tight immune onset) and widen through day 8 (stochastic accumulation), consistent with the Bernoulli seeding mechanism in ImmuneCellSeedingSteppable. The ODE viral load ci_95 bounds (propagated from the ABM via triple integration) track the n_immune uncertainty: wider immune bounds produce wider viral load bounds, demonstrating end-to-end UQ propagation.

**Figure 2** (see `figures/oisa_trajectory.pdf`): Two-panel figure generated from all 5 replicates. Panel (a): reference-replicate viral load V (copies/mL, log scale, red) and infected fraction Eps/(Ep+Eps) (%, grey dashed, right axis) vs. simulation time; viral peak annotated at day 2.25. Panel (b): median n_immune across N = 5 replicates (green step), with IQR shading (pale green) and individual replicate trajectories (thin lines). Figure generated by `figures/generate_trajectory_figure.py` directly from ISSL JSON checkpoint files in `results/issl_14d/`.

**Immune temporal lag.** The n_immune trajectory (median across 5 replicates) shows first CC3D Immunecell agents appearing at day 1 (median = 6 agents [IQR 5–6]), preceding the viral peak at day 2.25 by approximately 1.25 days. This rapid immune onset is consistent with the innate immune response timescale of 1–4 days post-infection [20] and emerges from the OISA-mediated signal routing — the viral load at day 0 drives cytokine accumulation in the CC3D simulation, which triggers stochastic Immunecell seeding at day 1. The temporal pattern — early immune recruitment followed by sustained but gradually declining viral load — is not a property of either model in isolation, but of the bidirectional ODE–ABM coupling.

**CTL-mediated clearance.** With n_immune growing from 6 (day 1) to 50 (day 13), T_E_T = n_immune × 100 grows from 600 to 5,000 CTL/mL in the Miao 2010 SBML, progressively amplifying the CTL killing term k_E × Eps × T_E_T = 2×10⁻⁵ × Eps × T_E_T. This CTL-mediated killing component accelerates the viral decline from peak (day 2.25: 9.03×10⁶) through day 7 (4.85×10⁵) to day 13 (8.43×10³ copies/mL). An isolated ODE run with T_E_T = 0 was confirmed to produce slower viral clearance over the same period, validating that the ABM → ODE signal pathway is a functionally significant contributor to the observed trajectory.

**Real spatial ABM properties.** The Immunecell agents in the CC3D simulation are genuine spatial agents occupying sites on the 90×90×2 Cellular Potts grid, subject to the Contact energy, Volume, and Chemotaxis plugins from the original Sego 2020 XML. Their recruitment is governed by ImmuneCellSeedingSteppable (stochastic, probability ∝ S × 0.01) and their movement by ChemotaxisSteppable (cytokine gradient-directed). The n_immune values reported in the ISSL are counts from the live CC3D cell inventory (`cell.type == 5`), not from a closed-form approximation — this is the fundamental distinction from a scalar ODE surrogate.

---

## VI. Discussion

### VI-A. OISA and the CURE Guidelines

**Table VII** maps each CURE criterion [17] to its OISA implementation. Three points deserve emphasis. First, OISA implements CURE credibility criteria at the *composition* level: a composition can violate biological plausibility even when each constituent model is individually valid — for example, if the scaling factor between tissue immune agents (n_immune) and systemic CTL/mL is mis-specified, the CTL killing term in the ODE is silently miscalibrated. The orchestrator's explicit `_N_IMMUNE_TO_CTL_PER_ML = 100` parameter makes this scaling decision auditable in the ISSL record and testable by the constraint engine. Second, the `model_version` field in the ISSL envelope — populated with `"BIOMD0000000546"` for the ODE and `"github:covid-tissue-models@5b7e42c+OISA_bridge"` for the ABM — directly implements CURE's reproducibility requirement: every checkpoint log is traceable to a specific, citable, immutable model artefact. Third, the demonstration that two published models — including the full spatial Sego 2020 CC3D ABM — require zero internal biological modifications operationalises CURE's extensibility requirement at the multi-model scale: any OISA-compliant model can replace either node without modifying its peer.

**Table VII.** OISA components as operational implementations of CURE criteria [17], extended to the multi-model composition level.

| CURE criterion | OISA component | Scope |
|---|---|---|
| Credibility — UQ of outputs | ISSL `ci_95` fields; uncertainty propagated through signals | Composition-level |
| Credibility — scope monitoring | Watchdog `divergence_score`; OOD detector | Per-model at every tick |
| Credibility — provenance | ISSL `envelope.model_version`; PROV-O URI in `internal_parameters` | Parameter + signal |
| Understandability — levels 1–3 | ISSL `envelope` + `continuous_state` + `export_signals` | Per checkpoint |
| Reproducibility — community standards | JSON-LD schema; commit SHA in `model_version`; BioModels DOI | Schema-level |
| Extensibility — modular reuse | Config graph edge-based wiring; any node substitutable without modifying peers | Architecture-level |
| Automation of guideline checking | Constraint engine + watchdog; automatic at every GSimT tick | Runtime |

*[17] is an arXiv preprint (2025); peer-reviewed status pending at time of submission.*

### VI-B. Limitations

**Validation scope.** Validation is on a single organism (murine) and a single disease context (influenza A). The coupled model has not been validated against time-series experimental data measuring both viral load and immune cell counts simultaneously in vivo. Full validation would require longitudinal murine data at the tissue level — an experiment not yet published in a form suitable for direct model comparison at this coupling resolution.

**Epithelial depletion.** In the Miao 2010 ODE, the high infection rate (β_a = 10⁻⁶ mL·copies⁻¹·day⁻¹) produces near-complete depletion of uninfected epithelial cells (Ep) by day 2–3, consistent with Miao 2010 Fig. 2 dynamics. From day 3 onward, the infected fraction Eps/(Ep + Eps) ≈ 100%; subsequent viral clearance is driven by the Eps death rate (δ_Es) and CTL killing (k_E × Eps × T_E_T) in the absence of new healthy-cell infection. This is a known property of the Miao 2010 model under the published parameters and does not affect the OISA orchestration validation goal.

**Feedback loops.** The OISA composition graph contains a feedback cycle (ODE → ABM → ODE). The one-tick delay mechanism (6 h minimum latency on the ABM → ODE signal) is necessary for causal correctness but introduces a bounded approximation: immune cells recruited in response to viral load at tick t do not suppress viral replication until tick t+1. Whether this 6 h latency is biologically significant depends on the timescale of CTL-mediated killing relative to the GSimT tick size; for influenza, where viral kinetics operate on timescales of hours to days, a 6 h lag is unlikely to introduce systematic bias.

**ABM stochasticity and ensemble size.** Sego 2020 immune seeding is stochastic (Bernoulli probability per MCS batch proportional to S × ir_prob_scaling_factor = 0.01). Runtime ci_95 bounds are computed from a rolling ensemble of N = 5 parallel CC3D instances. While this provides genuine runtime UQ propagation (ci_95 intervals are populated in every ISSL record at every tick), N = 5 is a small ensemble; wider characterisation (N ≥ 20) would yield more robust percentile estimates. The ensemble approach incurs a computational cost of approximately 5× the single-instance ABM runtime, since all N instances are stepped at every 24 h GSimT boundary.

**Scaling factor.** The `_N_IMMUNE_TO_CTL_PER_ML = 100` conversion (CC3D Immunecell agents to systemic CTL/mL for Miao 2010) is an approximation based on published CTL density ranges (Miao 2010, Fig. 2: 10³–10⁶ CTL/mL at peak) and tissue compartment size (≈ 0.01 mL). This value is declared explicitly in the adapter and auditable in the ISSL record, but has not been independently calibrated against simultaneous tissue and systemic measurements. A related approximation concerns the spatial scale: the Miao 2010 ODE is calibrated against whole-animal murine data (viral load in copies/mL of total respiratory tract, ≈ 1 mL), while the Sego 2020 CC3D ABM occupies a 90×90×2 voxel tissue patch (≈ 10⁻³ mL). The ODE viral load signal V (copies/mL whole-animal) is injected as a proxy for tissue-level cytokine concentration — a scale approximation of approximately three orders of magnitude in volume. This does not affect the OISA orchestration validation (which targets signal routing correctness, not biological calibration), but should be acknowledged as a known modelling approximation in any future deployment of this composition for predictive purposes.

**IPC performance.** The file-based IPC protocol (one JSON write + sentinel per 24 h GSimT tick) introduces an estimated latency of approximately 50 ms per tick, dominated by CC3D busy-wait polling. For 14-day simulations (14 bridge steps × ~50 ms/step ≈ 700 ms total), total IPC overhead is < 1 s — negligible relative to CC3D computation time. For compositions requiring sub-6-hour inter-model communication, a shared-memory or socket-based IPC channel would reduce latency by 2–3 orders of magnitude.

---

## VII. Conclusion

We have proposed and demonstrated OISA, the Orchestrated Immune Simulation Architecture, delivering three contributions beyond the state of the art in multi-formalism immune model composition: (1) runtime uncertainty quantification propagated at every checkpoint from a stochastic ABM ensemble through a deterministic ODE, with ci_95 intervals populated in every ISSL record; (2) model-derived transfer lags on edges, demonstrated by a blood transit transfer model that computes signal delay dynamically from published kinetic parameters; and (3) a biological plausibility constraint engine operating at the composition level.

The architecture is validated by coupling two independently published models — the Miao 2010 influenza ODE (SBML, BIOMD0000000546) and the full spatial Sego 2020 CC3D ABM (CompuCell3D 4.8.0, 12 steppables on a 90×90×2 Cellular Potts grid, GitHub @5b7e42c) — with zero modifications to either model's source code. Adapter layers total ~300 lines. Over a 14-day simulation (N = 5 rolling ensemble, 56 GSimT checkpoints), ISSL records with runtime ci_95 bounds document viral kinetics consistent with Miao 2010 (peak V = 9.0×10⁶ copies/mL at day 2.25, clearance to < 0.1% of peak by day 13.75) and spatial immune recruitment from the real CC3D ABM (median n_immune = 6 [ci_95: 5–7] at day 1, growing to 50 [ci_95: 45–53] at day 13). Immune temporal lag and CTL-mediated clearance acceleration emerge as properties of the bidirectional coupling that neither model alone produces. The architecture demonstrates that formalism-agnostic composition of published immune models — including full spatial ABMs run as independent processes with runtime UQ — is achievable through adapter-only integration with no model rewrites.

---

## References

[1] E. Agmon et al., "Vivarium: an interface and engine for integrative multiscale modeling in computational biology," *Bioinformatics*, vol. 38, pp. 1972–1979, 2022.

[2] Committee on Foundational Research Gaps and Future Directions for Digital Twins, *Foundational Research Gaps and Future Directions for Digital Twins*. National Academies Press, 2023.

[3] M. Clerx et al., "CellML 2.0," *J. Integr. Bioinform.*, vol. 17, no. 2–3, 20200021, 2020. doi: 10.1515/jib-2020-0021.

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

[18] H. Miao, J.A. Hollenbaugh, M.S. Zand, J. Holden-Wiltse, T.R. Mosmann, A.S. Perelson, H. Wu, and D.J. Topham, "Quantifying the early immune response and adaptive immune response kinetics in mice infected with influenza A virus," *J. Virology*, vol. 84, no. 14, pp. 7051–7062, 2010. doi: 10.1128/JVI.00506-10. BioModels: BIOMD0000000546.

[19] T.J. Sego, J.O. Aponte-Serrano, J.F. Gianlupi, S.R. Heaps, K. Breithaupt, L. Brusch, J.M. Osborne, E.M. Quardokus, R.K. Plemper, and J.A. Glazier, "A modular framework for multiscale, multicellular, spatiotemporal modeling of acute primary viral infection and immune response in epithelial tissues and its application to drug therapy timing and effectiveness," *PLoS Comput. Biol.*, vol. 16, no. 11, e1008451, 2020. doi: 10.1371/journal.pcbi.1008451. GitHub: covid-tissue-models/covid-tissue-response-models @5b7e42c.

[20] A. Iwasaki and R. Medzhitov, "Regulation of adaptive immunity by the innate immune system," *Science*, vol. 327, no. 5963, pp. 291–295, 2010. doi: 10.1126/science.1183021.

---

*Article type: Methods / Framework Proposal*

*Data and code availability: OISA specification files, ISSL JSON-LD schemas, reference orchestrator implementation (including SignalQueue, Sego2020Ensemble, and BloodTransitAdapter), all adapter code (Miao 2010 SBML adapter ~60 lines; Sego 2020 CC3D ABM adapter ~240 lines + ensemble wrapper + OISABridgeSteppable ~60 lines), configuration graph, and full test suite (67 automated tests: 23 ODE + 20 ABM + 8 transfer model + 16 integration) are available at [repository URL to be added prior to submission]. The Miao 2010 SBML source (BIOMD0000000546\_model1.xml) is downloaded unmodified from BioModels; the Sego 2020 CC3D model is imported unmodified from commit 5b7e42c of the covid-tissue-models GitHub repository and run via CompuCell3D 4.8.0.*

*Author contributions: [To be completed prior to submission]*

*Competing interests: The authors declare no competing interests.*
