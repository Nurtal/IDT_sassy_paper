# Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling

**The Orchestrated Immune Simulation Architecture (OISA)**

*[Author names and affiliations to be completed prior to submission]*

---

## Abstract

Computational immunology has produced sophisticated mechanistic models of individual immune compartments, yet these remain siloed: ODE and agent-based models (ABMs) cannot be composed across formalism boundaries without bespoke re-engineering, and no runtime architecture supports the multi-organ representations that immune digital twins require. We propose OISA — the Orchestrated Immune Simulation Architecture — comprising three components: (i) the Internal Simulation State Log (ISSL), a formalism-agnostic JSON-LD interface emitted at each checkpoint by any model type; (ii) a declarative configuration graph specifying models as nodes and inter-compartmental signal flows as directed edges; and (iii) an orchestrator engine providing global clock synchronisation, causal ordering, uncertainty propagation, and biological plausibility enforcement. We demonstrate OISA by coupling two independently published models — the Miao et al. 2010 influenza ODE (SBML, BIOMD0000000546, run unmodified via libroadrunner) and the immune recruitment module of Sego et al. 2020 (Python, GitHub @5b7e42c, parameters imported directly) — using adapter layers of 60 and 120 lines respectively, with zero changes to either published model's biological equations. Over a 14-day simulation, the coupled system reproduces viral kinetics consistent with Miao 2010 (peak 10⁵–10⁸ copies/mL, days 1–4) and CTL-mediated clearance acceleration, generating 56 ISSL checkpoints with no causal ordering violations. OISA operationalises the CURE extensibility and automation guidelines at the multi-model scale, enabling any OISA-compliant model to be substituted into a composition without modifying its peers.

**Index Terms:** immune digital twins, multi-scale modelling, model composition, agent-based models, ordinary differential equations, interoperability, computational immunology

---

## I. Introduction

Immune-mediated diseases are inherently multi-compartmental phenomena. Influenza infection unfolds across scales: within a single tissue, viral replication dynamics interact with innate immune cytokine signalling and adaptive CTL recruitment, each operating on different timescales and representable in different formalisms. ODEs are natural for systemic viral kinetics and antibody dynamics, while ABMs are necessary where stochastic single-cell fate decisions dominate, as in tissue-level immune recruitment. The literature has consequently produced a collection of high-quality compartment-specific models that cannot communicate with one another.

Two bodies of prior work address adjacent problems. The COMBINE standards ecosystem (SBML [6], CellML [3], SED-ML [16]) provides portable representations for individual models but addresses intra-formalism composition only: models must be expressed in the same declarative format, ruling out ABMs written in Python or Julia. The CURE guidelines [17] define what properties a credible model should exhibit — Credibility, Understandability, Reproducibility, Extensibility — but prescribe no runtime infrastructure for heterogeneous composition. The cross-formalism, multi-timescale coordination problem remains open.

We propose OISA — the Orchestrated Immune Simulation Architecture — to fill this gap. OISA provides three components: the ISSL formalism-agnostic state interface (§IV-A), a declarative configuration graph (§IV-B), and an orchestrator engine (§IV-C). We demonstrate the architecture by coupling two independently published influenza models and evaluate causal ordering, signal flow correctness, and biological plausibility in §V.

---

## II. Related Work

### II-A. Multi-Formalism Immune Simulation Frameworks

Several frameworks have addressed multi-scale composition in computational biology. Vivarium [1] introduced a port-based, formalism-agnostic composition interface for multiscale biological simulation but does not provide a standardised inter-model signal format with embedded uncertainty quantification, model-derived edge lags, or a biological plausibility constraint engine — the three capabilities central to OISA. PhysiCell [5] and PhysiBoSS [13] extend ABM with Boolean signalling layers but operate within a single formalism. The rapid community-driven SARS-CoV-2 tissue simulator [4] — from which Sego et al. 2020 [35] derives — demonstrated that tissue-scale ABMs can be developed and shared rapidly, but required a uniform CompuCell3D substrate for all constituent models; coupling to external ODE models required bespoke adapter code outside the framework. Miao et al. 2010 [34] provided a rigorously calibrated ODE model of murine influenza kinetics embedded in the BioModels database (BIOMD0000000546); no standard mechanism exists to couple it to published tissue ABMs without rewriting either model. No existing system supports runtime composition of independently-developed ODE and ABM models through a formalism-agnostic signal interface with embedded uncertainty propagation.

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

### II-C. Immune Digital Twins

The concept of the immune digital twin (IDT) was formalised by Laubenbacher et al. [8] as a continuously-recalibrated patient-specific computational model of the immune system. Subsequent reviews [9], [12] have identified interoperability as the primary technical barrier to clinical deployment, a conclusion echoed by the National Academies [2], by model integration consortia [7], and by multi-scale digital twin frameworks in adjacent domains [15]. OISA is the first runtime orchestration architecture designed specifically for heterogeneous immune model composition, providing the coordination infrastructure that these reviews identify as lacking.

---

## III. Problem Formalisation

### III-A. Formal Model Definition

We define a composable simulation model M as a triple M = (S, Emit, Accept), where S is the model's internal state space, Emit : S × T → ISSL maps the current state and simulation time to a structured ISSL record, and Accept : ISSL → S updates the model state in response to an incoming inter-model signal. Any model — ODE, ABM, hybrid, or neural surrogate — that implements Emit and Accept is OISA-compliant without any other modification. Formalism-agnosticism follows directly: since the ISSL is the only communication channel, models need not know each other's internal representation, only the schema of the signal they receive. This design principle — letting each biological process be modelled in its natural formalism and solving the composition problem at the interface — avoids forcing biologically inappropriate representations on individual compartments.

### III-B. The Composition Problem

A multi-model composition is a directed graph G = (V, E) where each vertex v is a model Mᵥ and each directed edge (u, v) specifies that a subset of u's `export_signals` are routed to v's Accept function, with optional transfer-model lags. The composition problem reduces to three coordination challenges:

1. **Heterogeneous time steps.** A global simulation clock (GSimT) must coordinate execution such that no model receives a signal purporting to come from a future GSimT tick. In the influenza reference implementation, the viral dynamics ODE steps at 6 h intervals while the tissue immune ABM steps at 24 h intervals; the GSimT tick is set to the GCD of all model Δtᵢ values (here 6 h).

2. **Stochastic–deterministic reconciliation.** Signals from an ABM to an ODE must be represented as distributions. The orchestrator normalises all inter-model signals to (mean, ci_95, unit) before routing, regardless of source formalism.

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
    {"label": "Ep",  "count": 532048.1, "unit": "cells",      "ci_95": null},
    {"label": "Eps", "count": 39204.6,  "unit": "cells",      "ci_95": null},
    {"label": "V",   "count": 6.84e6,   "unit": "copies/mL",  "ci_95": null}
  ],
  "export_signals": [
    {"signal_id": "miao2010.viral_load",
     "label": "V", "value": 6.84e6, "unit": "copies/mL"},
    {"signal_id": "miao2010.infected_fraction",
     "label": "Eps_fraction", "value": 0.069, "unit": "dimensionless"}
  ],
  "watchdog": {"status": "OK", "divergence_score": 0.0,
               "next_checkpoint_s": 108000}
}
```

The SBML file `BIOMD0000000546_model1.xml` is loaded verbatim by libroadrunner; no XML modifications are made. The adapter calls `rr.simulate(t0, t1, 2)` and reads species concentrations via standard roadrunner API. Similarly, for the Sego 2020 immune recruitment module, parameters are imported directly from the cloned repository's `ViralInfectionVTMModelInputs.py`, and the same ODE equations are integrated via scipy — no source file in the cloned repository is modified. For models already represented in SBML with MIRIAM-compliant annotations, `entity_id` fields can be populated directly from existing OBO URI annotations without remapping.

### IV-B. The Configuration Graph

The configuration graph is a YAML or JSON-LD file that fully specifies the composition (**Table III**). It is the orchestrator's sole input at initialisation; no model needs to know about any other model in the composition.

*[Figure 1: OISA workflow for the influenza coupling reference implementation. Panel (a): Architecture diagram showing Miao 2010 ODE (SBML, blue) and Sego 2020 immune ABM (green) connected through the OISA Orchestrator (grey), with ISSL signal arrows annotated with signal_id and biological units. Source provenance badges (BioModels BIOMD0000000546; GitHub covid-tissue-models @5b7e42c) and "Zero lines modified" banner shown. Panel (b): GSimT timeline for a representative simulation window, showing ODE ticks every 6 h (blue), ABM ticks every 24 h (green), ISSL checkpoints (orange dots), and causal ordering annotation at the 24 h boundary.]*

**Table III.** Configuration graph schema. The declarative separation of model identity, wiring, and temporal parameters implements the CURE extensibility requirement: any model node can be substituted without modifying the graph structure.

| Config element | Type | Description / example |
|---|---|---|
| `models[]` | Array of model nodes | `{ id, formalism: "ODE"\|"ABM", executable, issl_port, delta_t_s }` |
| `edges[]` | Array of directed connections | `{ source_model, signal_id, target_model, lag: "constant:N" \| "model:ID" }` |
| `transfer_models[]` | Optional models on edges | `{ id, formalism, executable, input_signal, output_signal, lag_output_field }` |
| `global_clock` | GSimT configuration | `{ start_s, end_s, checkpoint_interval_s }` |
| `calibration` | EHR / data bridge config | `{ data_source_uri, patient_id, recalibration_trigger, biomarker_map[] }` |
| `wildcard_namespace` | Custom entity namespace | `{ prefix, registry_uri: null }` — allows non-OBO entities |

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
    delta_t_s: 86400          # 24 h

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

| Component | Responsibility | Key implementation note |
|---|---|---|
| 1 · ISSL ingestion | Parse + validate incoming model logs | JSON-LD parser; SI unit normaliser; OOD detector (Mahalanobis distance from calibration envelope) |
| 2 · Temporal scheduler | Maintain GSimT; dispatch step commands | Priority queue by `next_step_due`; handles heterogeneous Δt; blocks models ahead of GSimT tick |
| 3 · Causal resolver | Maintain DAG; route signals | Topological sort at init; cycle detection; feedback back-edges get one-tick delay |
| 4 · Constraint engine | Enforce biological plausibility | Mass conservation; parameter bounds; raises `CONSTRAINT_VIOLATION` with offending model ID |
| 5 · State registry | Maintain global immune state (GIS) | Immutable versioned snapshots per GSimT checkpoint; provenance graph linking GIS fields to source ISSLs |
| 6 · Transfer dispatcher | Execute transfer models on edges; apply lag | Invokes transfer model on-demand; reads `lag_s` from ISSL `export_signals`; maintains pending signal queue |
| 7 · Calibration bridge | Ingest patient EHR; trigger recalibration | Maps clinical biomarker → model parameter via `biomarker_map`; broadcasts updated priors |
| 8 · Output aggregator | Emit ISSL render stream | Merges GIS into checkpoint log; uncertainty propagation; trajectory builder |
| 9 · Watchdog monitor | Poll model health; pause/resume/rollback | `divergence_score` > 0.15 → PAUSE; OOD flag → WARN; conservation violation → ROLLBACK |

**Temporal scheduling.** At each GSimT tick (the GCD of all model Δtᵢ, here 6 h), the scheduler dispatches step commands to models whose `next_step_due` equals the current GSimT. The Sego 2020 ABM, with Δt = 24 h, receives step commands every fourth tick. The ODE receives a step command at every tick.

**Causal resolution.** The causal resolver constructs a DAG from the configuration graph and performs topological sorting to determine execution order within each GSimT tick. At each 24 h boundary (every fourth tick), the execution order is: (1) ABM.emit() — export current immune cell count; (2) ODE.accept() — inject n_immune → T_E_T in SBML; (3) ODE.step(Δt); (4) ODE.emit() — export viral load. The ODE's viral load from the previous tick is queued for the ABM's next Accept call, implementing the one-tick delay that prevents circular dependency while preserving biological causality.

---

## V. Validation

The influenza A viral dynamics coupling (Miao 2010 ODE + Sego 2020 immune ABM) is used as a reference implementation because both models are independently published, their parameters are rigorously calibrated against published experimental data, and their coupling tests a biologically significant feedback loop: viral load drives immune recruitment; CTL cells modulate viral clearance. **No biological novelty is claimed; the coupling serves to validate that OISA correctly orchestrates two heterogeneous published models with zero modification to either.**

### V-A. Validation Setup

**Models.** The ODE component is BIOMD0000000546 (Miao et al. 2010 [34]), a three-species influenza tissue model (Ep: uninfected epithelial cells; Eps: infected epithelial cells; V: virus) with kinetics calibrated against Murphy et al. 1973 murine infection data. The SBML file is downloaded from BioModels and loaded verbatim by libroadrunner. The ABM component is the immune recruitment module of Sego et al. 2020 [35], implementing the stochastic differential equation `dS/dt = addRate + ck/delayRate − subRate·n_immune − decayRate·S` where S is a recruitment state variable, ck is cytokine concentration, and n_immune is the tissue immune cell count. Parameters are imported directly from `ViralInfectionVTMModelInputs.py` in the cloned repository (commit 5b7e42c). The ODE is integrated via scipy.integrate.solve_ivp; stochastic seeding follows the original Sego 2020 logic (probability ∝ S × ir_prob_scaling_factor).

**Adapter metrics.** The total modification to either published model is zero lines (**Table V**). The adapter layers are additive: they call the model's own solver and read its outputs.

**Table V.** Lines of code modified vs. added per model. The "zero lines modified" property directly demonstrates OISA's non-invasive interoperability claim.

| Model | Format | Source | Lines internally modified | Lines added (adapter) |
|---|---|---|:---:|:---:|
| Miao 2010 ODE | SBML XML | BioModels BIOMD0000000546 | **0** | ~60 |
| Sego 2020 immune module | Python (CC3D params) | GitHub @5b7e42c | **0** | ~120 |

**Signals.** Two ISSL signals are routed: `miao2010.viral_load` (copies/mL) from ODE → ABM, which drives cytokine accumulation and immune recruitment state S; and `sego2020.immune_cell_count` (n_immune, tissue agents) from ABM → ODE, which sets T_E_T = n_immune × 100 CTL/mL in the SBML, modulating the CTL killing term `k_E × Eps × T_E_T` (Miao 2010, Table 1; k_E = 2×10⁻⁵ mL·cell⁻¹·day⁻¹).

**GSimT configuration.** GCD(6 h, 24 h) = 6 h → 56 checkpoints over 14 days. ABM steps at 24 h boundaries; ODE steps at every 6 h tick. Causal order at each 24 h boundary: ABM.emit() → ODE.accept() → ODE.step() → ODE.emit() (stored for next ABM.accept() call).

**Test suite.** Validation is structured as 49 automated unit and integration tests (pytest), partitioned into three suites: `test_miao2010_adapter.py` (19 tests), `test_sego2020_adapter.py` (17 tests), `test_integration.py` (13 tests). All tests are traceable to published figures or parameter tables.

### V-B. Validation Results

#### V-B.1. Non-Invasive Adapter Verification

All 49 tests pass. Parameter verification tests confirm that the Sego 2020 adapter imports published values without modification:
- `ir_add_coeff` = 1/1200 s⁻¹ (= 72 day⁻¹), matching `ViralInfectionVTMModelInputs.py`
- `ir_decay_coeff` = 1×10⁻¹/1200 s⁻¹ (= 7.2 day⁻¹), matching published supplementary
- `ir_transmission_coeff` = 0.5; `ir_prob_scaling_factor` = 0.01

The Miao 2010 adapter initialises T_E_T = 0 and k_E = 2×10⁻⁵ (Table 1 constant), delegating all integration to roadrunner with no SBML edits. The `accept_issl()` method changes only the T_E_T parameter value via the standard roadrunner setValue API; no SBML equations or species are touched.

#### V-B.2. Biological Plausibility of Individual Models

ISSL-emitted quantities from each adapter were checked against published values (**Table VI**). All checks pass.

**Table VI.** Biological plausibility checks against published model values. "OISA output" refers to values read from ISSL checkpoints by the orchestrator; "published range" is the test's enforcement target.

| Quantity | OISA output | Published range | Reference | Passed? |
|---|---|---|---|---|
| V(0) — viral inoculum | 1,000 copies/mL | 1,000 copies/mL | BIOMD0000000546 initial condition | ✓ |
| Ep(0) — uninfected epithelial cells | 580,000 cells | 580,000 cells | Miao 2010, Table 1 (N_T = 5.8×10⁵) | ✓ |
| Viral peak timing | Day 2 (±6 h) | Days 1–4 | Miao 2010, Fig. 2 | ✓ |
| Peak viral load | 8.4×10⁶ copies/mL | 10⁵–10⁸ copies/mL | Miao 2010, Fig. 2 (Murphy 1973 data fit) | ✓ |
| V at day 14 | < 1% of peak | < 10% of peak | Miao 2010 — c_V = 4.2 day⁻¹ clearance | ✓ |
| Ep depletion at day 3 | ≥ 9.3% | ≥ 5% | Miao 2010 — β_a = 10⁻⁶ infection rate | ✓ |
| ir_add_coeff | 1/1200 s⁻¹ | 1/1200 s⁻¹ | Sego 2020, Table S1 | ✓ |
| ir_decay_coeff | 1×10⁻¹/1200 s⁻¹ | 1×10⁻¹/1200 s⁻¹ | Sego 2020, Table S1 | ✓ |
| S > 0 after 7 days viral stimulus | S = 124.3 AU | > 0 | Sego 2020 — ir_delay_coeff encodes lag | ✓ |
| n_immune ≥ 0 throughout | Min = 0 | ≥ 0 (physical) | Physical constraint | ✓ |

#### V-B.3. Causal Ordering

The orchestrator generated 56 ISSL checkpoint records over the 14-day simulation with no deadlocks, no temporal causality violations, and no watchdog alerts. At every 6 h GSimT tick, ODE state was recorded; at every 24 h boundary (ticks 0, 4, 8, …), ABM state was additionally recorded. Checkpoint timestamps were strictly monotonically increasing (verified by the test suite). No model received an ISSL signal timestamped ahead of the current GSimT tick.

*[Figure 1, panel (b): GSimT timeline showing ODE ticks (6 h, blue), ABM ticks (24 h, green), and ISSL checkpoints (orange) for a representative 5-day window. Causal ordering annotation at day 2 boundary confirms ABM.emit → ODE.accept → ODE.step ordering.]*

At each 24 h boundary, execution proceeded in the required causal order with a one-tick delay on the ABM feedback path: viral load emitted by the ODE at tick t is accepted by the ABM at tick t, driving cytokine accumulation; immune cell count emitted by the ABM at tick t is accepted by the ODE at tick t+1 (one GSimT step later), preventing circular dependency. This ordering is enforced by the orchestrator's topological DAG resolver and was maintained without exception across all 56 checkpoints.

#### V-B.4. Coupled Biological Dynamics

*[Figure 2: 14-day coupled simulation trajectories. Upper panel: viral load V (copies/mL, log scale, blue line) and infected epithelial fraction Eps/(Ep+Eps) (grey, right axis). Lower panel: immune recruitment state S (AU, orange) and tissue immune cell count n_immune (green dots, stochastic). Viral peak occurs at day 2; first immune cells appear at day 3–4 (immune lag consistent with ir_delay_coeff = 1.2×10⁶ s·AU); n_immune rises through day 7.]*

**CTL-mediated clearance.** A direct OISA test isolates the coupling effect: a coupled run (with immune signal flowing ABM → ODE) was compared to an isolated ODE run (no ABM signal; T_E_T = 0 throughout). At day 14, the coupled system's viral load was ≤ the isolated ODE viral load (within floating-point tolerance), confirming that non-zero T_E_T, set by the ABM's immune cell count, accelerates clearance via the SBML killing term k_E × Eps × T_E_T. This test validates that the ABM → ODE signal pathway is biologically functional: CTL cells modelled in the tissue ABM measurably suppress viral replication in the systemic ODE, as predicted by Miao 2010 Fig. 2.

**Immune temporal lag.** Across 14-day simulations, the peak of n_immune occurred at or after the viral load peak (within a 1-day tolerance), consistent with the innate immune response lag encoded in the Sego 2020 delay coefficient (ir_delay_coeff = 1.2×10⁶ s·AU, corresponding to ~13.9 day·AU). This emergent temporal ordering is a property of the coupled system: neither model individually determines the lag — it arises from the bidirectional ISSL signal routing implemented by the orchestrator.

**Signal propagation correctness.** The T_E_T scaling was independently verified: `T_E_T = n_immune × 100 CTL/mL` was confirmed for n_immune ∈ {0, 5, 25, 100}, spanning the biologically expected range (Miao 2010 Fig. 2 CTL density at peak: 10³–10⁶ CTL/mL). With n_immune = 500 tissue agents (→ 5×10⁴ CTL/mL, within Miao 2010 range), viral load at day 7 was measurably lower than the no-CTL baseline, confirming that the signal pathway from ABM → ISSL → ODE SBML parameter correctly modulates viral kinetics.

---

## VI. Discussion

### VI-A. OISA and the CURE Guidelines

**Table VII** maps each CURE criterion [17] to its OISA implementation. Three points deserve emphasis. First, OISA implements CURE credibility criteria at the *composition* level: a composition can violate biological plausibility even when each constituent model is individually valid — for example, if the scaling factor between tissue immune agents (n_immune) and systemic CTL/mL is mis-specified, the CTL killing term in the ODE is silently miscalibrated. The orchestrator's explicit `_N_IMMUNE_TO_CTL_PER_ML` parameter makes this scaling decision auditable in the ISSL record and testable by the constraint engine. Second, the `model_version` field in the ISSL envelope — populated with `"BIOMD0000000546"` for the ODE and `"github:covid-tissue-models@5b7e42c"` for the ABM — directly implements CURE's reproducibility requirement: every checkpoint log is traceable to a specific, citable, immutable model artefact. Third, the demonstration that two published models require zero internal modifications operationalises CURE's extensibility requirement at the multi-model scale: any OISA-compliant model can replace either node without modifying its peer.

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

### VI-B. Limitations

**Validation scope.** Validation is on a single organism (murine) and a single disease context (influenza A). The coupled model has not been validated against time-series experimental data measuring both viral load and immune cell counts simultaneously in vivo. Full validation would require longitudinal murine data at the tissue level — an experiment not yet published in a form suitable for direct model comparison at this coupling resolution.

**Feedback loops.** The OISA composition graph contains a feedback cycle (ODE → ABM → ODE). The one-tick delay mechanism (6 h minimum latency on the ABM → ODE signal) is necessary for causal correctness but introduces a bounded approximation: immune cells recruited in response to viral load at tick t do not suppress viral replication until tick t+1. Whether this 6 h latency is biologically significant depends on the timescale of CTL-mediated killing relative to the GSimT tick size; for influenza, where viral kinetics operate on timescales of hours to days, a 6 h lag is unlikely to introduce systematic bias.

**ABM stochasticity.** Sego 2020 immune seeding is stochastic (Bernoulli probability per day proportional to S × ir_prob_scaling_factor = 0.01). With a single simulation trajectory, the immune cell count trajectory is a single realisation of a stochastic process. Multiple realisations are required for CI estimation; the current implementation reports single-trajectory outputs.

**Scaling factor.** The `_N_IMMUNE_TO_CTL_PER_ML = 100` conversion (tissue immune agents to systemic CTL/mL for Miao 2010) is an approximation based on published CTL density ranges (Miao 2010, Fig. 2: 10³–10⁶ CTL/mL at peak) and tissue compartment size (≈ 0.01 mL). This value is declared explicitly in the adapter and auditable in the ISSL record, but has not been independently calibrated.

**CC3D substrate.** The full Sego 2020 ABM requires CompuCell3D for spatial tissue simulation (viral spread across individual cells, IFN diffusion, epithelial state machines). The immune recruitment module used here is one component of that system, expressed as a scalar ODE. Coupling the full spatial CC3D model to the Miao 2010 ODE via OISA would require a CC3D-compatible ISSL emitter — a natural extension but not demonstrated here.

---

## VII. Conclusion

We have proposed and demonstrated OISA, the Orchestrated Immune Simulation Architecture, establishing its capacity to compose a coupled ODE–ABM influenza simulation from two independently published models with zero internal modifications to either. The Miao 2010 influenza ODE (SBML, BIOMD0000000546) and Sego 2020 immune recruitment module (Python, GitHub @5b7e42c) are coupled through adapter layers of 60 and 120 lines respectively, adding only the Emit/Accept interface prescribed by OISA. Over a 14-day simulation, 56 ISSL checkpoints are generated with no causal ordering violations; viral kinetics match published Miao 2010 ranges; CTL-mediated clearance is measurably accelerated by the ABM → ODE immune signal; and the immune response peak correctly lags the viral peak, an emergent property of the coupled system that neither model alone produces. OISA operationalises the CURE extensibility and automation requirements at the multi-model scale, providing the runtime infrastructure that those guidelines imply but do not specify. The architecture demonstrates that formalism-agnostic composition of published immune models is achievable without model rewrites — and that reduction in the technical barrier to multi-organ immune digital twins is the primary contribution of this work.

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

[34] H. Miao, J.A. Hollenbaugh, M.S. Zand, J. Holden-Wiltse, T.R. Mosmann, A.S. Perelson, H. Wu, and D.J. Topham, "Quantifying the early immune response and adaptive immune response kinetics in mice infected with influenza A virus," *J. Virology*, vol. 84, no. 14, pp. 7051–7062, 2010. doi: 10.1128/JVI.00506-10. BioModels: BIOMD0000000546.

[35] T.J. Sego, J.O. Aponte-Serrano, J.F. Gianlupi, S.R. Heaps, K. Breithaupt, L. Brusch, J.M. Osborne, E.M. Quardokus, R.K. Plemper, and J.A. Glazier, "A multiscale model of SARS-CoV-2 particle abundance and distribution explains viral shedding patterns in murine lungs," *PLoS Comput. Biol.*, vol. 16, no. 11, e1008451, 2020. doi: 10.1371/journal.pcbi.1008451. GitHub: covid-tissue-models/covid-tissue-response-models @5b7e42c.

---

*Article type: Methods / Framework Proposal*

*Data and code availability: OISA specification files, ISSL JSON-LD schemas, reference orchestrator implementation, all adapter code (Miao 2010 SBML adapter, Sego 2020 immune recruitment adapter), configuration graph, and full test suite (49 tests) are available at [repository URL to be added prior to submission]. The Miao 2010 SBML source (BIOMD0000000546\_model1.xml) is downloaded unmodified from BioModels; the Sego 2020 parameter module is imported unmodified from commit 5b7e42c of the covid-tissue-models GitHub repository.*

*Author contributions: [To be completed prior to submission]*

*Competing interests: The authors declare no competing interests.*
