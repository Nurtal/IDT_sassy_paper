---
  IEEE BIBM 2026 — Simulated Peer Review — Round 3 (Selection Committee Final Pass)

  Paper: Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling (OISA)
  Track: Bioinformatics Methods and Applications
  Submission type: Full paper (8 pages)
  Round: Final selection committee review prior to conditional acceptance / camera-ready

---

## Programme Chair Statement

This paper has been reviewed over two prior rounds. The Round 2 meta-review (Weak Accept, conditional on three blocking items) identified Figure 1 rendering, κ derivation correctness, and Table I UQ qualification as mandatory pre-camera-ready fixes. The present selection committee pass confirms that **none of the three blocking items from Round 2 have been addressed in the current manuscript version**. In addition, this round identifies reference coherence failures and main-message clarity issues that must be resolved before the paper can be accepted.

The underlying contribution is sound and original. The demonstration that two independently published models can be composed without source modifications is a meaningful result. The committee recommends **Conditional Accept** — not rejection — but the camera-ready version must satisfy all items enumerated in this report.

---

## Reference Coherence Audit

A full cross-reference check was performed between the body text and the bibliography ([1]–[19]). Results:

| ID  | Issue                                                                                                                                | Location            | Severity        |
|-----|--------------------------------------------------------------------------------------------------------------------------------------|---------------------|-----------------|
| R1  | **Missing bibliography entry**: §V-B.4 cites "Iwasaki & Pillai 2014" by name in the text ("consistent with the innate immune response timescale of 1–4 days post-infection (Iwasaki & Pillai 2014)") but no corresponding numbered reference [20] or equivalent exists in the bibliography. | §V-B.4 + References | **Blocking**    |
| R2  | **[17] CURE guidelines is an arXiv preprint** (arXiv:2502.15597, 2025). For IEEE BIBM 2026, this may lack peer-reviewed status at submission time. §VI-A builds the CURE-alignment argument on this source; Table VII maps OISA to CURE criteria. If [17] is not peer-reviewed by camera-ready deadline, authors should either (a) substitute a peer-reviewed credibility-framework reference, or (b) add an explicit note that [17] is a preprint. | §I, §VI-A, Table VII | High             |
| R3  | **[3] CellML reference is the Model Repository, not the language spec**: Lloyd et al. 2008 describes the CellML Model Repository infrastructure. Table I compares "CellML 2.0" capabilities, but CellML 2.0 is specified in a separate document (Hedley et al. / Cuellar et al.). The cited source does not establish the CellML 2.0 capabilities listed in the comparison. | Table I             | Moderate         |
| R4  | **Table VI label "V at day 14"**: The paper states the simulation has 56 GSimT checkpoints at 6 h intervals starting at t = 0, meaning the last checkpoint falls at tick 55 × 6 h = 330 h = 13.75 days. The row label "V at day 14 \| < 1% of peak" is factually wrong by 6 h. Should read "V at day 13.75" or the simulation must be extended by one tick. | Table VI            | Minor            |
| R5  | **Data availability footer inconsistency**: The footer states "full test suite (36 unit tests + integration tests)" without specifying the count of integration tests. §V-A correctly states "48 automated tests: 36 unit + 12 integration." The footer creates ambiguity about whether the 12 integration tests are published with the repository. | Footer              | Minor            |
| R6  | **Author fields incomplete**: The manuscript header reads "*[Author names and affiliations to be completed prior to submission]*" and the footer reads "*[Author contributions: To be completed prior to submission]*". These are submission blockers. | Header + Footer     | **Blocking** (camera-ready) |
| R7  | **Repository URL missing**: Data availability reads "[repository URL to be added prior to submission]". No URL is provided. | Footer              | **Blocking** (camera-ready) |

**Summary**: 2 blocking (content), 3 blocking (camera-ready), 1 high, 1 moderate, 1 minor. R1 (missing citation) is the most urgent content-blocking reference issue.

---

## Main Message Clarity Report

### Overall Assessment

The paper's core message — that OISA enables formalism-agnostic composition of published immune simulation models through a thin adapter-only interface, without modifying either model's biological equations — is **scientifically sound and genuinely novel**. The three-component architecture (ISSL + config graph + orchestrator) is well-specified. However, several presentation choices obscure the contribution or risk misleading the reader.

### Per-Section Assessment

**Title**
"Simulation as a Service" is a phrase strongly associated with cloud computing (SaaS). A reader encountering this title in the proceedings index will expect a cloud/microservices contribution, not a scientific middleware architecture for immune model composition. The subtitle ("A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling") accurately describes the work, but the main title creates a mismatch. Recommend either (a) inverting title/subtitle, or (b) replacing "Simulation as a Service" with a phrase that does not import the SaaS connotation — e.g., "Formalism-Agnostic Runtime Composition for Modular Immune Disease Modelling."

**Abstract**
The abstract is a single paragraph of approximately 500 words. IEEE BIBM does not mandate structured abstracts, but the density of this block makes the core claim difficult to extract at a glance. The main contribution (zero-modification inter-formalism composition) does not appear until sentence 3; the abstract front-loads motivation before stating the actual result. Recommend restructuring as two paragraphs: (1) motivation + gap + proposed solution (3–4 sentences), (2) validation results + key numbers (4–5 sentences). The quantitative results (peak V, n_immune, N=5 replicates, 56 checkpoints, adapter line counts) are appropriately concrete.

**§I — Introduction**
The introduction correctly situates OISA relative to COMBINE standards and CURE guidelines. However, it lacks a **contributions list** — a standard feature of methods papers that helps reviewers and readers rapidly confirm the paper's scope. The implicit contributions (ISSL schema, config graph, orchestrator engine, reference implementation) are recoverable from the text but should be enumerated explicitly as a bullet list at the end of §I.

**§II-A — Related Work: Multi-Formalism Frameworks**
The comparison with Vivarium [1] is fair and has been appropriately softened from Round 1. The statement that Vivarium "does not natively provide as a standardised interface an inter-model signal format with embedded uncertainty quantification, model-derived edge lags, or a biological plausibility constraint engine" is accurate and specific. No change required here.

**§II-B — Interoperability Standards**
The paper correctly distinguishes intra- vs. inter-formalism interoperability, and Table I is a clear and useful comparison. However, the paper implies that OISA is comparable to SBML/CellML/NeuroML in the "portable model representation" row by leaving that cell "—" (dash). This dash could be misread as "missing" rather than "not applicable" (OISA is a runtime architecture, not a portable representation format). A footnote clarifying that "—" means architectural scope mismatch rather than absence of the feature would prevent misreading.

**§III — Problem Formalisation**
The formal definition M = (S, Emit, Accept) is clean and minimal. The claim that "Formalism-agnosticism follows directly" (§III-A) is asserted without proof or argument. The reader needs one sentence explaining *why* the ISSL acts as a formalism firewall — i.e., because Emit maps any formalism's state to a common JSON-LD schema, and Accept only consumes that schema, so the source formalism is invisible to the receiver. This is implicit but should be made explicit.

**§IV — Architecture**
The architecture is clearly described. Table IV with Status column (✓ / ◐) is exemplary. The config graph YAML excerpt is concrete and reproducible. The only gap here is the execution-order dependency of `lag: "constant:0"` on the ODE→ABM edge (config, line 187 of paper): zero-lag delivery is only possible because the ODE executes before the ABM at each 24 h boundary — if this ordering were reversed, the signal would require a lookahead. This dependency on implicit DAG topology is not acknowledged in the prose describing lag semantics.

**§V — Validation**
The validation design is appropriate for the stated goal (demonstrating OISA orchestration correctness, not biological novelty). The non-invasive adapter verification, biological plausibility table (Table VI), causal ordering section, and 14-day coupled dynamics are each necessary validation components and are clearly presented. The following sub-issues affect clarity or correctness:

- §V-A κ derivation still claims "within one order of magnitude" for a factor-357 discrepancy (see Referee B below).
- §V-A sensitivity analysis is stated as a result without supporting data (see Referee C below).
- §V-B.1 states "All 36 unit tests pass" — does not confirm integration tests.
- §V-B.4 does not discuss the biological implication of Eps/(Ep+Eps) = 100% from day 2–3 onwards.

**§VI — Discussion**
The CURE mapping (Table VII) and the limitations paragraph are well-written and appropriately honest. The 6 h one-tick delay justification in §VI-B is correct. However, three Reviewer 2/3 concerns from Round 2 — Eps saturation, scale mismatch, and sensitivity data — remain entirely unaddressed in the current text.

**§VII — Conclusion**
The conclusion correctly summarises the architectural contribution and the validated result. It does not overstate biological novelty. The sentence about CURE operationalisation is appropriate but should reference [17] as a preprint pending peer review.

---

## Referee A — Computational Biology / Immunology (Score: 4/5 — Weak Accept)

### Summary

A technically solid and well-structured paper demonstrating inter-formalism composition of two independently published influenza models. The core engineering contribution is clear: zero source-code modifications to either model, adapter-only coupling, 14-day validated trajectory. The immunological framing is appropriate — no new biology is claimed. My concerns are concentrated on (1) the missing Iwasaki & Pillai reference, (2) the biological interpretation of 100% epithelial infection, and (3) the CTL/innate approximation.

### Strengths

- The paper correctly avoids claiming biological novelty; the validation goal is stated explicitly: "No biological novelty is claimed; the coupling serves to validate that OISA correctly orchestrates two heterogeneous published models with zero modification to either." (§V preamble)
- The ODE→ABM coupling at the immune recruitment interface (not the viral diffusion field) is the correct biological choice and is explained clearly in §V-A. The _note field in Box 2 documenting `total_virus_field: 0.0` by design is an excellent transparency device.
- The CTL-mediated clearance comparison (coupled vs. isolated ODE with T_E_T = 0) is the appropriate validation of the ABM→ODE feedback pathway.
- The immune temporal lag result (Immunecell agents appear at day 1, preceding viral peak at day 2.25) is an emergent property of the coupling not producible by either model alone — this is the central biological validation finding and is clearly articulated.

### Concerns

**A1 — Missing reference: Iwasaki & Pillai 2014 [Blocking].**
§V-B.4 cites "Iwasaki & Pillai 2014" to support the claim that innate immune onset within 1–4 days is consistent with published data. This citation appears in the text but has no bibliography entry. The reference is almost certainly: A. Iwasaki and R. Medzhitov, "Regulation of adaptive immunity by the innate immune system," *Science*, vol. 327, pp. 291–295, 2010 — or possibly Iwasaki & Pillai 2014 in *Nat. Rev. Immunol.* The authors must add the full citation. Until this is fixed, the supporting claim for immune onset timing is unsupported.

**A2 — Eps/(Ep+Eps) = 100% from day 2–3: biological interpretation absent [Significant].**
The trajectory table in §V-B.4 shows viral load and n_immune but not the infected fraction. However, the Miao 2010 ODE with V peaking at 9×10⁶ copies/mL and β_a = 10⁻⁶ mL·copies⁻¹·day⁻¹ produces near-complete depletion of uninfected epithelial cells (Ep) by day 3, as noted by Reviewer 2 in Round 2. The current text in §V-B.1 reports "Ep depletion at day 3: ≥ 9.3%" in Table VI — but this check verifies only that depletion has *begun*, not that it reaches saturation. After day 3, all Ep cells are infected (Eps = Ep_total), and subsequent viral dynamics are driven solely by the Eps → V secretion and clearance rates with no healthy cells left to infect. This is a known property of the Miao 2010 model and does not invalidate the OISA validation, but it should be acknowledged in one sentence in §VI-B. The current text does not mention this.

**A3 — CTL ↔ Immunecell approximation: not noted in abstract or §V [Minor].**
The abstract states "CTL-mediated viral clearance acceleration" as a key result. However, T_E_T in the Miao 2010 ODE represents adaptive CTL (cytotoxic T lymphocytes), while the CC3D Immunecell agents in Sego 2020 represent innate-like immune cells (natural killer-like, recruited stochastically by cytokine gradient). The paper maps innate ABM agents onto an adaptive ODE killing term. This is a model-level approximation that is biologically meaningful in the context of demonstrating OISA coupling but should be flagged in §V-A or in the abstract where "CTL-mediated" is used. Reviewer 3 flagged this in Round 2; the current text does not address it.

---

## Referee B — Software Architecture / Interoperability (Score: 3/5 — Borderline)

### Summary

The software architecture is well-designed and the OISA component decomposition (ISSL, config graph, orchestrator) is appropriate. However, three critical issues from Round 2 remain unaddressed: the κ derivation mathematical error, the Table I UQ claim mismatch, and Figure 1 rendering. I cannot recommend acceptance while these issues persist.

### Strengths

- The IPC protocol (sentinel-file handshake) is pragmatic and correct for this use case. Process isolation between ODE solver and CC3D engine is architecturally sound.
- The config graph YAML excerpt is concrete enough to reproduce. The declarative wiring (models know nothing about peers) correctly implements the CURE extensibility requirement.
- Table IV with ✓ / ◐ Status column is an effective and honest way to communicate implementation completeness.
- The one-tick delay mechanism for causal ordering is correctly explained and verified (§V-B.3).

### Concerns

**B1 — Figure 1 is still a prose placeholder [Blocking, Round 2 carry-over].**
The paper still contains the text (§IV-B): "*[Figure 1: OISA workflow for the influenza coupling reference implementation. Panel (a): Architecture diagram showing Miao 2010 ODE (SBML, blue) and Sego 2020 CC3D ABM (green) connected through the OISA Orchestrator (grey)...]*". This is italic bracketed prose, not a rendered figure. The repository contains `figures/oisa_workflow.pdf` (82 KB) and `figures/oisa_workflow.png` (418 KB) — the figure file exists but is not embedded in the manuscript. For a systems architecture paper, Figure 1 (the workflow diagram) is the primary visual communication of the contribution. This is a hard blocking issue.

**B2 — κ derivation error still present [Blocking, Round 2 carry-over].**
§V-A still states: "The constant 3.5×10⁻⁷ ... recovers an equivalent daily accumulation: 4 × 3.5×10⁻⁷ = 1.4×10⁻⁶, within one order of magnitude of the analytical estimate." The analytical estimate is 5×10⁻⁴ pM·mL/copies. The ratio 5×10⁻⁴ / 1.4×10⁻⁶ = 357, which is 2.5 orders of magnitude — not one. This error was identified by Reviewer 2 in Round 2 (M1) and remains uncorrected. The fix is straightforward: replace "within one order of magnitude" with "within approximately 2.5 orders of magnitude, calibrated empirically to maintain totalCytokine within Sego 2020's functional range." Option (b) from Reviewer 2's Round 2 comment is scientifically acceptable and requires only a two-line edit.

**B3 — Table I UQ checkmark unqualified [Significant, Round 2 carry-over].**
Table I (§II-B) marks OISA with ✓ for "Runtime UQ propagation across models." However, §VI-B explicitly states: "Individual ISSL records report single-trajectory n_immune values with ci_95: null; ensemble statistics are computed post-hoc from the checkpoint archive." Post-hoc ensemble statistics are not runtime UQ propagation. The ✓ should be changed to ◐ with a footnote: "ci_95 fields declared in ISSL schema; runtime population planned — not implemented in reference version." This was flagged by Reviewer 2 (M2) in Round 2 and remains unfixed.

**B4 — lag: "constant:0" execution-order dependency undisclosed [Minor, new].**
The config graph (§IV-B) specifies `lag: "constant:0"` on the ODE→ABM edge. Zero-lag delivery is only achievable because the causal resolver places the ODE step before the ABM step at each 24 h boundary (as described in §IV-C: "ABM.emit() → ODE.accept() → ODE.step() → ODE.emit()"). If execution order were reversed, zero-lag delivery would require an ODE lookahead that violates causality. The paper should add one sentence noting that `lag: "constant:0"` is order-dependent and that the config graph's DAG topology implicitly encodes this constraint. Reviewer 3 (W4) flagged this in Round 2; the current text does not acknowledge it.

**B5 — §V-B.1 test count inconsistency [Minor, Round 2 carry-over].**
§V-A correctly states "48 automated tests: 36 unit + 12 integration." §V-B.1 states "All 36 unit tests pass." The integration tests (12) are not confirmed as passing in the results section. Either update to "All 48 automated tests pass" or explicitly state the integration test status.

---

## Referee C — Statistical / Validation Methods (Score: 4/5 — Weak Accept)

### Summary

The validation methodology is appropriate for the stated goal. The 14-day, N=5 ensemble with median [IQR] reporting is the correct choice. My concerns are: (1) the unsupported sensitivity analysis claim, (2) the undiscussed scale mismatch between models, and (3) the IPC latency measurement gap.

### Strengths

- Median [IQR] across N=5 is correctly used as the central tendency measure for a stochastic ABM. The choice of IQR (robust to outliers) over confidence intervals is appropriate for N=5 where Gaussian assumptions fail.
- The replicate methodology is sound: time-seeded MersenneTwister, distinct IPC directories, independently confirmed V < 0.1% of peak across all 5 replicates. The clearance criterion is clearly defined and uniformly met.
- The biological plausibility table (Table VI) is structured as a proper verification table: observable, expected range, reference, pass/fail. This is the correct way to validate a simulation.
- The CTL-mediated clearance validation (coupled vs. T_E_T = 0 isolated ODE) is the right counterfactual experiment.

### Concerns

**C1 — Sensitivity analysis claim unsupported by data [Significant, Round 2 carry-over].**
§V-A states: "A sensitivity analysis shows that varying κ by ±1 order of magnitude shifts the immune onset day by ±1–2 days but does not qualitatively alter the n_immune trajectory shape." This is presented as a finding, not an expectation. No figure, table, or supplementary result is provided. Reviewer 2 (M4) flagged this in Round 2. The fix is either: (a) provide the data (run 3 additional κ values, report immune onset day shift in a supplementary table or inline), or (b) rephrase as "preliminary exploration suggests" to remove the assertion of a completed analysis. The current text misleads the reader into believing a sensitivity study was conducted.

**C2 — Scale mismatch not acknowledged [Significant, Round 2 carry-over].**
The Miao 2010 ODE is calibrated against whole-animal murine respiratory tract data (V in copies/mL of total respiratory tract, estimated volume ≈ 1 mL; Miao 2010, Materials and Methods). The Sego 2020 CC3D ABM occupies a 90×90×2 voxel tissue patch at 4 μm voxel length = 360 μm × 360 μm × 8 μm ≈ 10⁻³ cm³ ≈ 10⁻³ mL. The ODE signal V (copies/mL whole-animal) is injected as a proxy for local cytokine concentration in a tissue patch that is approximately 3 orders of magnitude smaller in volume. This scale mismatch is not discussed anywhere in the paper. It does not invalidate the OISA validation (which targets orchestration correctness, not biological calibration), but it should be explicitly acknowledged as a known approximation in §VI-B Limitations. Reviewer 3 (W2) flagged this in Round 2; the current text remains silent.

**C3 — N=5 IQR zero-width at day 2 [Minor, Round 2 carry-over].**
The trajectory table shows n_immune = 11 [11–11] at day 2, i.e., zero IQR width. With N=5, a zero-width IQR may reflect genuine deterministic onset or small-sample artifact. One sentence in §VI-B (ABM stochasticity paragraph) should acknowledge that N=5 is adequate for demonstration but that characterising the 25th–75th percentile reliably requires N≥20 (Harrell & Davis 1982; bootstrap confidence intervals for small N). The current text ("The n_immune IQR is narrow on days 1–2 (tight immune onset)") attributes the zero-width IQR to biology without acknowledging the sample-size caveat.

**C4 — IPC latency: estimate not measurement [Minor].**
§VI-B states: "For 14-day simulations (14 bridge steps), total IPC overhead is < 1 s." The calculation 14 steps × ~50 ms/step = ~700 ms is provided in the prior review context. The paper should state whether 50 ms/step is a measured value (with measurement method) or an estimate. 700 ms is close to the 1 s bound, so the claim "< 1 s" is plausible but tight. Replacing "approximately 50 ms per tick" with "measured at N ms per tick (mean over M runs)" would satisfy this concern with minimal effort.

---

## Decision Scorecard

| Criterion              | Referee A | Referee B | Referee C | Mean |
|------------------------|:---------:|:---------:|:---------:|:----:|
| Originality            |     4     |     3     |     4     | 3.7  |
| Technical soundness    |     4     |     3     |     4     | 3.7  |
| Significance           |     4     |     3     |     4     | 3.7  |
| Presentation           |     3     |     3     |     4     | 3.3  |
| Overall                |     4     |     3     |     4     | 3.7  |

**Decision: Conditional Accept** — camera-ready requires resolution of the following items.

---

## Consolidated Action List for Camera-Ready

### Blocking (must fix before acceptance)

| ID  | Item                                                                                       | Action                                                                                                  |
|-----|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| B1  | Figure 1 is prose placeholder                                                              | Embed `figures/oisa_workflow.pdf` as rendered Figure 1; remove bracketed prose description              |
| B2  | κ "within one order of magnitude" — factor is ~357 (2.5 orders)                          | Replace with "within approximately 2.5 orders of magnitude, calibrated empirically to functional range" |
| B3  | Table I ✓ for Runtime UQ propagation — ci_95: null throughout                            | Change to ◐; add footnote: "declared in schema; runtime population is a planned extension"              |
| R1  | Iwasaki & Pillai 2014 missing from bibliography                                            | Add full reference entry [20]; confirm author/title/journal                                             |
| R6  | Author names, affiliations, contributions fields are placeholders                         | Complete all author metadata before submission                                                          |
| R7  | Repository URL missing from data availability statement                                    | Add GitHub/Zenodo URL                                                                                   |

### High Priority (strongly recommended)

| ID  | Item                                                                                       | Action                                                                                                  |
|-----|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| B4  | §V-B.1: "All 36 unit tests pass" — integration tests status unclear                       | State whether all 48 pass, or explain why 12 integration tests are excluded from the status claim       |
| N3  | Eps/(Ep+Eps) = 100% from day 2–3 not discussed                                            | Add 2 sentences in §VI-B acknowledging complete epithelial depletion as a known Miao 2010 model property|
| N4  | Sensitivity analysis claimed without data                                                  | Provide supporting table or rephrase as "preliminary exploration suggests"                               |
| N5  | Scale mismatch ODE (whole-animal ~1 mL) vs. ABM (tissue patch ~0.01 mL) not discussed     | Add 2 sentences in §VI-B Limitations acknowledging the volume-scale approximation                       |
| R2  | CURE [17] is arXiv preprint                                                                | Note preprint status in §I or §VI-A; substitute peer-reviewed reference if available by camera-ready    |

### Minor (recommended)

| ID  | Item                                                                                       | Action                                                                                                  |
|-----|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| N1  | `lag: "constant:0"` is execution-order dependent — not disclosed                          | Add one sentence in §IV-B noting DAG topology implicitly encodes ODE-before-ABM ordering                |
| N2  | IPC latency "< 1 s" is estimate, not measurement                                          | State measured value (N ms mean over M runs) or label clearly as an estimate                            |
| N6  | CTL (adaptive) ↔ Immunecell (innate) approximation not noted in abstract or §V-A          | Add one sentence in §V-A flagging this as a model-level approximation; revise abstract claim            |
| R3  | Data availability footer says "36 unit tests + integration tests" — inconsistent with §V-A | Replace with "48 automated tests (36 unit + 12 integration)"                                            |
| R4  | [3] CellML reference is Repository, not spec                                               | Replace with CellML 2.0 specification reference for Table I comparison                                  |
| R5  | Table VI: "V at day 14" — last checkpoint is day 13.75                                    | Correct label to "V at day 13.75" or extend simulation by one tick                                      |
| C3  | N=5 zero-width IQR at day 2 — sample-size caveat absent                                   | Add sentence in §VI-B: N=5 adequate for demonstration; N≥20 recommended for reliable IQR estimation     |
| C4  | IPC latency 50 ms/step — estimate or measurement not specified                             | State "measured at X ms/step" or "estimated at ~50 ms/step"                                             |

---

## Reviewer Consensus Note on Main Contribution

All three referees agree: the core architectural contribution (OISA enables zero-modification inter-formalism composition via ISSL + config graph + orchestrator) is valid, original, and meaningful for the field of computational immunology. The demonstration coupling (Miao 2010 SBML ODE + Sego 2020 full CC3D ABM) is a convincing and reproducible proof of concept. The paper's honest framing — no biological novelty claimed, coupling as an orchestration validation — is scientifically appropriate.

The blocking items are presentation and precision failures, not fundamental scientific flaws. The committee is confident that a focused camera-ready revision can resolve them.
