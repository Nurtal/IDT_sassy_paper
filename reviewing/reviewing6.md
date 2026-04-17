---
IEEE BIBM 2026 — Simulated Peer Review — Round 5 (Post-Revision Committee Review)

Paper: OISA: A Formalism-Agnostic Orchestration Architecture for Composing Published Immune Models Without Modification
Track: Bioinformatics Methods and Applications
Submission type: Full paper (8 pages)
Round: Major Revision (Round 4) → Re-review by original reviewer + two additional committee members
Review date: 2026-04-16
---

## Programme Committee Statement

This manuscript was returned after Round 4 with a Major Revision recommendation from an external reviewer (area: multi-scale computational biology, digital twins). The reviewer raised four major concerns (C1–C4), three moderate concerns (C5–C7), and six minor comments (M1–M6). The revised manuscript has been evaluated by the original external reviewer (R1) and two additional programme committee members (R2: systems biology standards; R3: agent-based modelling / HPC).

**Overall assessment:** The revision is thorough and responsive. All four major concerns have been addressed substantively. The paper is significantly strengthened by the addition of the sensitivity analysis (Table VIII), the reframing of UQ bounds, the spatial scale mismatch discussion, and the abstract-level validation disclaimer. The committee recommends **Accept with Minor Revisions** (camera-ready corrections only).

**Overall score: 4.2 / 5 (Accept with Minor Revisions)**

---

## Reviewer R1 — Score: 4/5 (Accept)

*(Original external reviewer, Round 4)*

### Response to Major Concerns

**C1 (Abstract validation disclaimer) — RESOLVED.** The Abstract now contains the explicit sentence: "This validation targets orchestration correctness — signal routing, causal ordering, and runtime UQ propagation — not biological prediction of the coupled system, which has not been validated against simultaneous in-vivo measurements." This is exactly what was requested. The same qualifier appears in the Conclusion, ensuring that a reader scanning either section understands the validation scope. No further action needed.

**C2 (Sensitivity analysis) — RESOLVED.** The authors have added §V-B.5 "Parameter Sensitivity" with a 3×3 grid (Table VIII) sweeping κ ∈ {3.5×10⁻⁸, 3.5×10⁻⁷, 3.5×10⁻⁶} × scaling ∈ {10, 100, 1000}. The table is well-structured and includes the isolated ODE baseline. The finding that scaling dominates while κ has a secondary effect via immune onset timing is clearly stated and consistent with the model structure (scaling directly multiplies T_E_T; κ acts indirectly through cytokine-driven immune recruitment). The observation that peak V remains within one order of magnitude across the full grid is reassuring. One methodological note: the sensitivity script uses an approximate n_immune trajectory shift rather than re-running the CC3D ABM for each κ. The authors acknowledge this ("the n_immune trajectory was approximated by shifting the reference ensemble median… by the qualitatively observed ±1–2 day onset shift"). This approximation is reasonable for a framework paper but should be flagged as a limitation — see R1-N1 below.

**C3 (Spatial scale mismatch) — RESOLVED.** The §VI-B paragraph on spatial scale mismatch has been completely rewritten. The coupling is now explicitly framed as a "proof-of-concept" with two clear reasons for omitting volume normalisation: (i) the validation targets orchestration correctness, not biological prediction; (ii) the empirically tuned κ implicitly absorbs the volume mismatch (the analytical-to-empirical discrepancy of ~2.5 OOM is consistent with the volume ratio). The authors provide the principled normalisation formula (V_tissue = V_systemic × V_patch/V_total ≈ V × 10⁻³) for future production use. This is a satisfactory resolution — perhaps even stronger than the minimum requested, since it simultaneously justifies the current approach and provides a roadmap for biological deployment.

**C4 (ci_95 renaming) — RESOLVED.** All occurrences of ci_95 have been qualified: the Abstract, Table I footnote, §III-B, §V-A (with a dedicated "Statistical note"), the trajectory table headers (now "ens. range [N = 5]"), §VI-B, Table VII, and the Conclusion all consistently use "ensemble range [N = 5]" or "ensemble bounds" language. The field name ci_95 is retained in ISSL schema excerpts (Boxes 1–2) for schema consistency but is qualified as "sample min–max." The statistical note in §V-A is precise and honest. This is a model response to a statistical criticism.

### Response to Moderate and Minor Concerns

**C5 (CURE preprint acknowledgement) — RESOLVED.** §VI-A now opens with: "We note that the CURE guidelines [17] are currently available as an arXiv preprint (2025) and have not yet undergone peer review; we interpret OISA's design against the principles proposed therein, supplemented by alignment with the peer-reviewed FAIR principles where applicable." This is sufficient.

**C6 (Table IV component status) — RESOLVED.** Components 1, 4, 5, and 9 are now marked "✓ / ◐†" with a detailed footnote distinguishing core functionality (tested) from sub-capabilities (specified but untested: OOD detection, ROLLBACK, PROV-O). This is honest and informative. The footnote is long but necessary.

**C7 (Table I SED-ML footnote) — RESOLVED.** The table footnote now reads: "'SBML L3' refers to the format specification alone; SED-ML [16] provides co-simulation capabilities including heterogeneous time-stepping for SBML-compatible models but does not extend to ABM composition." This resolves the potential objection from the SBML community.

**M1 (Vivarium in §I) — RESOLVED.** The Introduction now reads "Three bodies of prior work" with Vivarium acknowledged as the third, including a forward reference to §II-A.

**M2 (BloodTransitAdapter clarification) — RESOLVED.** §V-A now includes: "The BloodTransitAdapter was validated independently (8 dedicated tests) but was not active during the 14-day coupled influenza simulation…" This eliminates the ambiguity.

**M3 (Box 2 n_immune consistency) — RESOLVED.** Box 2 now includes the note: "Values in Box 2 are from a single illustrative CC3D instance and may differ from the ensemble median (N = 5) reported in §V-B.4." Adequate.

**M4 (Day 0 V discrepancy) — RESOLVED.** The trajectory table now has a footnote: "*Day 0 corresponds to the state after the first GSimT tick (6 h of ODE integration from V₀ = 1,000 copies/mL)…" Clear.

**M5 (Author placeholders) — NOT YET ADDRESSED.** Author names, affiliations, and contributions remain placeholder text. This is expected at this stage and is a camera-ready requirement, not a scientific concern.

**M6 (Calibration bridge clarification) — RESOLVED.** A paragraph after Table IV clarifies the calibration bridge's limited implementation status.

### New Comments from R1

**R1-N1 (Minor).** The sensitivity analysis (§V-B.5) uses a heuristic trajectory shift to approximate the effect of varying κ on the ABM-side immune trajectory, rather than re-running the CC3D ABM. This is a reasonable computational shortcut and is acknowledged in the text ("the n_immune trajectory was approximated by shifting the reference ensemble median"). However, the description in the paper text could more explicitly state that this is a *single-model* (ODE-only) sensitivity analysis with *approximate* ABM inputs, not a full coupled re-simulation. Recommend adding "ODE-side" or "approximate single-model" qualifier to the table title or §V-B.5 opening sentence. **Severity: Minor — addressable in camera-ready.**

**R1-N2 (Minor).** The n_immune ranges in the Abstract ([4–7] at day 1, [40–53] at day 13) now match the trajectory table — confirmed. However, the Abstract does not specify that these are ensemble bounds from N = 5 instances; it says "ens. range" which is clear in the context of the full paper but may be opaque to a reader who only sees the Abstract. Recommend expanding to "ensemble range across N = 5 stochastic replicates" at least once in the Abstract. **Severity: Cosmetic.**

---

## Reviewer R2 — Score: 4/5 (Accept)

*(Programme committee member, area: systems biology standards and SBML/SED-ML ecosystem)*

### General Assessment

This is a technically solid framework paper that addresses a genuine gap in the computational biology infrastructure: inter-formalism composition of published models without modification. The "zero lines modified" demonstration — particularly with the full spatial Sego 2020 CC3D ABM, not a toy surrogate — is compelling evidence that the approach is practical.

The revised manuscript is substantially improved over the version described in the Round 4 review. The sensitivity analysis, the honest statistical reframing of the UQ bounds, and the spatial scale mismatch discussion elevate the paper from "interesting demonstration" to "credible framework proposal."

### Specific Comments

**R2-1. Table I comparison — now adequate.** The SED-ML footnote resolves my primary concern. The comparison is now technically accurate: SBML L3 (format) does not support ABM composition or runtime UQ; SED-ML (simulation description) supports heterogeneous time-stepping for compatible models but not ABM-ODE composition. The distinction is correctly drawn. The addition of "Runtime UQ" qualification (N = 5 min–max) in the footnote is also appropriate.

**R2-2. Reference [3] CellML version.** The reference [3] (Clerx et al. 2020) is now the CellML 2.0 specification (doi: 10.1515/jib-2020-0021), which is the correct citation for the language spec used in Table I. This addresses the concern raised in Round 3 (R3 in reviewing4.md). No further action needed.

**R2-3. ISSL as a potential standard (Observation, not a required change).** The ISSL JSON-LD format described in §IV-A and Table II could potentially be submitted to the COMBINE community as a proposed standard for inter-formalism signal exchange. The authors do not make this claim (appropriately), but a brief sentence in Future Work acknowledging this possibility would strengthen the paper's contribution framing. This is a suggestion, not a requirement.

**R2-4. Schema URI validation (Minor).** Box 1 references `schemas/issl_v1.schema.json` as the schema URI. Is this schema published in the repository? If so, it should be mentioned in the data availability statement. If not, the URI is a dangling reference. **Severity: Minor — camera-ready.**

---

## Reviewer R3 — Score: 4.5/5 (Strong Accept)

*(Programme committee member, area: agent-based modelling, HPC, computational immunology)*

### General Assessment

This is the strongest paper I have reviewed in this track. The problem — composing heterogeneous published immune models at runtime without rewriting either — is important, and the solution is elegant. The key technical insight (formalism-agnostic composition via thin Emit/Accept adapters + JSON-LD checkpoints + causal DAG resolution) is simple in concept but the implementation details (rolling ensemble UQ, file-based IPC for CC3D subprocess isolation, the SignalQueue deferred injection mechanism) demonstrate practical engineering maturity.

The use of the *full* Sego 2020 CC3D ABM — all 12 steppables, 3 diffusion fields, 90×90×2 Cellular Potts grid — is particularly noteworthy. Many multi-scale composition papers use simplified surrogates and claim generality; this paper uses the actual published model unmodified and demonstrates that the orchestration handles it. The adapter line count (~300 lines total) is credible and verifiable from the described codebase.

### Specific Comments

**R3-1. Sensitivity analysis is welcome but limited.** Table VIII provides useful quantitative evidence that the coupled dynamics are robust to ±1 OOM parameter variation. However, the analysis only varies the two coupling parameters (κ and scaling). It does not vary any model-internal parameters (e.g., Miao 2010 β_a or c_V, Sego 2020 ir_prob_scaling_factor). A reviewer familiar with global sensitivity analysis (Sobol indices, Morris method) might ask why a local one-at-a-time sweep was chosen. I don't think this is a major gap for a framework paper — the sensitivity analysis is about coupling parameters, not model parameters — but a sentence acknowledging that model-internal sensitivity is out of scope would preempt this critique. **Severity: Minor.**

**R3-2. CC3D ensemble scaling.** The paper states that the ensemble approach "incurs a computational cost of approximately N× the single-instance ABM runtime" (§VI-B). For N = 5 this is manageable, but for production N ≥ 20 on a full CC3D simulation this becomes a non-trivial HPC concern. The paper does not discuss parallelism strategy (e.g., are the 5 CC3D instances run concurrently on separate cores, or sequentially?). A brief note on the parallel execution model would be valuable. **Severity: Minor.**

**R3-3. Immunecell type semantics.** The paper honestly acknowledges that "Immunecell agents in Sego 2020 model innate immune effectors (NK-like, cytokine-recruited)" while "T_E_T in the Miao 2010 ODE represents adaptive cytotoxic T lymphocytes" and that "mapping innate spatial agents to an adaptive killing term is a model-level approximation" (§V-A). This is exactly the kind of transparency that makes a framework paper credible. No action needed — I am noting this as a strength.

**R3-4. Figures.** Both Figure 1 (architecture/GSimT timeline) and Figure 2 (trajectory plot) are now present and generated from actual data. Figure 1 is information-dense but readable; the "Zero lines modified" banner is a nice touch. Figure 2 effectively shows the viral peak/clearance dynamics and immune recruitment with IQR bands. The figures resolve the pre-submission blocker from Round 4 (C8/Fig. 1–3). The paper originally mentioned 3 figures; 2 are sufficient for the content. **No action needed.**

**R3-5. Test suite coverage.** The paper reports 67 automated tests with clear decomposition (23 ODE + 20 ABM + 8 transfer + 16 integration). The Table IV footnote honestly distinguishes tested vs. untested sub-capabilities. The 51 additional consistency tests mentioned in the data availability description (if published) would further strengthen reproducibility, but this is not required for acceptance. **Observation only.**

---

## Summary of Required Revisions

| ID | Reviewer | Severity | Action required |
|---|---|---|---|
| R1-N1 | R1 | Minor | Add "ODE-side" or "approximate" qualifier to §V-B.5 sensitivity description |
| R1-N2 | R1 | Cosmetic | Expand "ens. range" in Abstract to clarify N = 5 stochastic replicates |
| R2-4 | R2 | Minor | Confirm ISSL schema URI is published in repository; update data availability if needed |
| R3-1 | R3 | Minor | Add sentence in §V-B.5 noting model-internal sensitivity is out of scope |
| R3-2 | R3 | Minor | Add brief note on CC3D ensemble parallel execution model |
| M5 | All | Camera-ready | Complete author names, affiliations, and contributions |

**No major revisions required.** All items are addressable in the camera-ready version.

---

## Selection Committee Decision

### Score Summary

| Reviewer | Score | Recommendation |
|---|---|---|
| R1 (external, multi-scale biology) | 4.0 / 5 | Accept |
| R2 (standards / SBML ecosystem) | 4.0 / 5 | Accept |
| R3 (ABM / HPC / comp. immunology) | 4.5 / 5 | Strong Accept |
| **Aggregate** | **4.2 / 5** | **Accept with Minor Revisions** |

### Committee Deliberation Notes

The committee discussed the paper for approximately 15 minutes. Key points raised:

1. **Originality.** The "zero lines modified" principle applied to a full spatial CC3D ABM (not a simplified surrogate) is a genuine advance over prior multi-scale coupling demonstrations, which typically require model rewrites. All three reviewers agreed this is a publishable result.

2. **Completeness of revision.** The response to Round 4 is unusually thorough. All four major concerns (C1–C4) were addressed with substantive changes (not just textual patches). The sensitivity analysis (C2) and the §VI-B spatial scale discussion (C3) add real technical content, not just hedging language. R3 noted this as "one of the more responsive revisions I've seen in this track."

3. **Remaining weakness: single use case.** The architecture is demonstrated on exactly one model pair (Miao 2010 + Sego 2020). While the design is general, the empirical evidence for generality is limited. The committee noted that this is standard for a framework proposal paper and does not warrant rejection, but the authors should be aware that future work demonstrating OISA with a second disease context or a third formalism (e.g., PDE, neural surrogate) would substantially strengthen the contribution.

4. **Statistical honesty.** The reframing of ci_95 as "ensemble range [N = 5]" was cited by all three reviewers as an example of appropriate scientific communication. Many papers in the track would benefit from this level of statistical transparency.

5. **Figures.** The figure generation from actual experimental data (not schematic mockups) was noted positively. Figure 2 in particular — showing real ISSL checkpoint data with IQR bands — demonstrates that the pipeline produces analysable output, not just textual claims.

### Decision

**ACCEPT WITH MINOR REVISIONS.**

The paper makes a clear, well-validated contribution to the multi-scale computational immunology infrastructure. The "zero lines modified" composition of two independently published models (ODE + full spatial ABM) is a practical result that the community can build on. The remaining items (R1-N1, R1-N2, R2-4, R3-1, R3-2, M5) are all addressable in the camera-ready version without further review.

The authors are required to submit a camera-ready version addressing the six items in the revision table above. No second re-review is required.

---

*Programme Committee, IEEE BIBM 2026 — Bioinformatics Methods and Applications Track*
*Review conducted under double-blind guidelines. Reviewer identities not disclosed.*
