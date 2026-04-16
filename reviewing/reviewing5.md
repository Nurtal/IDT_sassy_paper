---
IEEE BIBM 2026 — Simulated Peer Review — Round 4 (Independent External Reviewer)

Paper: OISA: A Formalism-Agnostic Orchestration Architecture for Composing Published Immune Models Without Modification
Track: Bioinformatics Methods and Applications
Review date: 2026-04-14
Reviewer: External reviewer (area: multi-scale computational biology, digital twins)
Recommendation: Major Revision
---

## Summary

The paper proposes OISA (Orchestrated Immune Simulation Architecture), a runtime orchestration framework designed to compose heterogeneous immune simulation models — specifically ODE and agent-based models (ABMs) — without modifying their source code. The core contributions are: (i) ISSL, a JSON-LD inter-model signal format with embedded runtime uncertainty quantification; (ii) a declarative configuration graph; and (iii) an orchestrator engine with causal DAG resolution, temporal scheduling, and biological plausibility enforcement. The architecture is demonstrated by coupling the Miao 2010 influenza ODE (SBML BIOMD0000000546) with the Sego 2020 CompuCell3D spatial ABM using only thin adapter layers (~300 lines), with zero modifications to either source model.

The problem addressed — formalism-agnostic, non-invasive multi-model composition for immune digital twins — is important and timely. The paper is well-written, technically detailed, and appropriately scoped as a framework proposal. However, several substantive issues must be addressed before acceptance.

---

## Detailed Comments

### C1 — Validation is architectural, not biological: this must be stated more prominently in the Abstract

The Abstract currently reads as though coupled biological dynamics are being validated ("reproduces viral kinetics consistent with Miao 2010… spatial immune recruitment"). The actual validation goal — stated correctly in §V ("No biological novelty is claimed; the coupling serves to validate that OISA correctly orchestrates two heterogeneous published models with zero modification") — is architectural: signal routing correctness, causal ordering, and UQ propagation. The Abstract gives the biological numbers (peak V, n_immune trajectory) without the critical disclaimer that these are not validated against experimental data. A reader scanning only the Abstract may conclude that the coupled model has been biologically validated, which it has not (acknowledged in §VI-B). **The Abstract must include an explicit sentence stating that validation is of the orchestration framework, not of the biological output of the coupled model.**

### C2 — The coupling constant κ = 3.5×10⁻⁷ is empirically set and underconstrained; sensitivity analysis is absent

Section V-A provides a derivation of the ODE→ABM coupling constant κ but concedes that it "was set empirically to maintain totalCytokine within Sego 2020's functional range at typical peak viral loads." The derivation gives a rough dimensional motivation but acknowledges a ~2.5 order-of-magnitude discrepancy between the analytical estimate and the value used. Furthermore, only a qualitative sensitivity statement is given ("varying κ by ±1 order of magnitude shifts the immune onset day by ±1–2 days") without quantitative data. Similarly, the scaling factor `_N_IMMUNE_TO_CTL_PER_ML = 100` is acknowledged as an approximation not independently calibrated. These two empirically chosen parameters are the primary biological coupling mechanisms; their sensitivity is precisely what determines whether the coupled trajectory is interpretable. **A quantitative sensitivity table or figure showing n_immune and V trajectories for κ ∈ {3.5×10⁻⁸, 3.5×10⁻⁷, 3.5×10⁻⁶} and for the scaling factor ∈ {10, 100, 1000} is required.** This can be compact (a 3×3 summary table of peak V and immune onset day) and would substantially strengthen the validation section.

### C3 — The spatial scale mismatch (ODE whole-animal vs. ABM tissue patch ~10⁻³ mL) is serious and inadequately addressed

Section VI-B acknowledges that "the Miao 2010 ODE is calibrated against whole-animal murine data… while the Sego 2020 CC3D ABM occupies a 90×90×2 voxel tissue patch (≈ 10⁻³ mL)… a scale approximation of approximately three orders of magnitude in volume." The paper then states "this does not affect the OISA orchestration validation goal." While this is true for demonstrating signal routing, the three-orders-of-magnitude mismatch means the ODE viral load in copies/mL whole-animal is injected into a sub-millilitre tissue compartment without rescaling. This is not merely a modelling approximation — it risks making the coupled system physically incoherent. **The paper must either: (a) provide a principled volume-normalisation of the ODE→ABM signal (dividing by the compartment volume ratio), or (b) more explicitly frame the coupling as a proof-of-concept that deliberately defers volume-scaling to future work, and explain why the results remain interpretable as a framework demonstration despite this mismatch.** Currently the discussion is too brief for the severity of the issue.

### C4 — N = 5 ensemble is insufficiently justified for the UQ propagation claim

The paper claims runtime UQ propagation as a primary contribution, with ci_95 bounds propagated from the stochastic ABM through the deterministic ODE at each checkpoint. However, the ensemble size N = 5 is acknowledged to be small (§VI-B: "wider characterisation N ≥ 20 would yield more robust percentile estimates"). Empirical percentiles from N = 5 are very unstable: the p2.5 and p97.5 estimates from 5 samples are essentially the sample minimum and maximum, with a 95% CI on the percentile estimate itself spanning nearly the full sample range. As presented, the "ci_95" label is misleading — these are sample extremes, not robust 95th-percentile estimates. **Either: (a) rename the bounds to "min–max" or "ensemble range [N=5]" to accurately reflect their statistical content, or (b) include results for at least N = 10–20 to demonstrate that the bounds are stable.** If computational constraints preclude larger N, this must be stated explicitly with a runtime estimate.

### C5 — The CURE reference [17] is an arXiv preprint; this creates a fragility in the CURE-alignment framing

A non-trivial portion of the Discussion (§VI-A, Table VII) frames OISA's contributions in terms of the CURE guidelines [17], which is footnoted as "an arXiv preprint (2025); peer-reviewed status pending." IEEE BIBM requires that primary cited works be traceable. If [17] is not peer-reviewed by submission, the CURE framing should either be presented as "we interpret OISA's design against the principles of [17]" (with a caveat that the guidelines themselves are preprint), or supplemented by alignment against the FAIR principles (which are peer-reviewed) or the COMBINE standards documentation. **The paper should explicitly acknowledge the preprint status of [17] in the body text of §VI-A, not only in a footnote to Table VII.**

### C6 — The orchestrator component table (Table IV) mixes design claims with implementation status; "Implemented" claims are untestable from the paper

Table IV lists 9 orchestrator components, 8 marked ✓ (implemented) and 1 marked ◐ (interface specified). The test suite (67 pytest tests) covers adapter and signal-level behaviour but does not appear to test orchestrator-level components such as the OOD detector (Mahalanobis distance), the PROV-O URI generation in `internal_parameters`, the `ROLLBACK` watchdog path, or the `divergence_score` computation. Without these tests, the ✓ claims for components 1 (OOD detector), 4 (constraint engine ROLLBACK path), and 5 (PROV-O provenance graph) are unverifiable. **Either add test coverage for these components (even minimal smoke tests) to the described test suite, or downgrade the unverified components to ◐ and note that they are specified but not yet covered by the published test suite.**

### C7 — The comparison in Table I uses "✗" for SBML hierarchical composition (SBML comp) without full nuance

Table I marks SBML L3 as "✗" for "Inter-formalism composition (ODE + ABM)." This is correct for ABM composition. However, the cell "✗" for "Heterogeneous Δt between models" for SBML may be debated by SBML community reviewers, since SED-ML (listed separately as [16]) does support heterogeneous time-stepping for co-simulation scenarios. The distinction between the SBML format and the COMBINE simulation ecosystem should be clearer. **The table caption or a table footnote should note that "SBML L3" in this comparison refers to the format specification alone, and that SED-ML co-simulation capabilities are addressed separately (listed as [16] in the paper).** This avoids a technically incorrect comparison that may provoke reviewer pushback from the standards community.

### C8 — Figure placeholders are still present; figures must be complete for final submission

Three figures (Fig. 1 architecture workflow, Fig. 2 trajectory plot, Fig. 3 UQ propagation) are described as placeholders in the paper text ("Source: figures/oisa_workflow.pdf, generated by figures/generate_workflow_figure.py"). IEEE BIBM requires complete figures for final submission. This is flagged as a pre-submission blocker, not a scientific concern, but the absence of actual figures means the paper cannot be fully evaluated on its visual presentation of the 14-day trajectory data (Table V data) or the causal ordering timeline. **All three figures must be finalised before submission.**

---

## Minor Comments

- **M1.** §I states "Two bodies of prior work address adjacent problems" — this framing is slightly narrow given that Vivarium is introduced in §II-A as a substantially related work. The Introduction should acknowledge Vivarium earlier and frame OISA's relationship to it more precisely.

- **M2.** The blood transit transfer model (BloodTransitAdapter, §V-A) is described but its output — a computed lag of tau = 4.0 days — is never used in the 14-day coupled simulation reported in §V-B.4. If model-derived transfer lags are listed as a primary contribution (contribution #2 in §I), they should appear in the reported results. Clarify whether the BloodTransitAdapter was active during the 14-day run or was validated separately.

- **M3.** Box 1 and Box 2 show two ISSL records at the same sim_time_s = 86,400 (day 1), but the ABM ISSL shows n_immune = 7 while the V-B.4 trajectory table shows n_immune = 6 at day 1. These should be consistent; if Box 2 is an illustrative excerpt and not from the validated run, this should be noted.

- **M4.** The 14-day trajectory table (§V-B.4) shows V at day 0 = 1.54×10³ copies/mL but the initial condition is stated as 1,000 copies/mL (Table VI row 1). The discrepancy (1540 vs. 1000) should be explained — is this after one GSimT tick of ODE integration from the initial condition?

- **M5.** Author names, affiliations, and repository URL are placeholder text. These must be complete for final submission.

- **M6.** §IV-C states the orchestrator is a "nine-component server process" but Table IV lists only 9 rows numbered 1–9, and component 7 (calibration bridge) is partially implemented (◐). Whether the calibration bridge is considered "implemented" in any form for this demonstration should be clarified.

---

## Summary of Required Revisions

| ID | Severity | Action required |
|---|---|---|
| C1 | Major | Add explicit disclaimer to Abstract: validation is of orchestration, not of coupled biological output |
| C2 | Major | Add quantitative sensitivity table for κ and scaling factor |
| C3 | Major | Provide principled volume normalisation or explicit framing of the spatial scale mismatch |
| C4 | Major | Rename ci_95 to "ensemble range [N=5]" or increase N to support the UQ claim |
| C5 | Moderate | Acknowledge CURE preprint status in body text of §VI-A |
| C6 | Moderate | Add test coverage or downgrade ✓ status for OOD detector, ROLLBACK path, and PROV-O provenance |
| C7 | Minor | Add footnote to Table I clarifying that SED-ML co-simulation is addressed separately |
| M1–M6 | Minor | See minor comments above |
| Fig. 1–3 | Pre-submission blocker | Replace all figure placeholders with actual generated figures |

---

## Recommendation

**Major Revision.** The paper addresses a genuine problem in computational immunology and proposes a technically coherent architecture. The non-invasive composition demonstration with zero model modifications is a solid empirical result. However, the four major comments — particularly the abstract-level misrepresentation of validation scope (C1), the underconstrained coupling parameters without sensitivity analysis (C2), the spatial scale mismatch (C3), and the statistical inadequacy of the UQ ensemble (C4) — must be resolved before the paper can be accepted. A revised version addressing these points would be a strong candidate for acceptance.

---
*Reviewed under IEEE BIBM 2026 double-blind review guidelines. Reviewer identity not disclosed.*
