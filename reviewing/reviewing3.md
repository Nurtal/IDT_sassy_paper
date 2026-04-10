---                                                                                                                                                                                                                                       
  IEEE BIBM 2026 — Simulated Peer Review — 2nd Round
                                                                                                                                                                                                                                            
  Paper: Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling (OISA)                                                                                                                  
  Track: Bioinformatics Methods and Applications                                                                                                                                                                                            
  Submission type: Full paper (8 pages)                                                                                                                                                                                                     
  Round: Major Revision → Re-review                                                                                                                                                                                                         
                                                                                                                                                                                                                                            
  ---                                                       
  Meta-Review — Area Chair                                                                                                                                                                                                                  
                                                            
  The revised manuscript addresses the majority of the concerns raised in Round 1. The extension to a 14-day, 5-replicate ensemble (C1, C6) is a substantial improvement, the coupling constant derivation (C2) is a meaningful addition,
  and the clarifications to the signal semantics (C3, C9, C10) strengthen the paper's technical precision. The Status column in Table IV (C5) is particularly welcome. The softened Vivarium comparison (C7) and test count clarification   
  (C8) are adequate.
                                                                                                                                                                                                                                            
  However, three new or persisting issues require attention before acceptance can be recommended:                                                                                                                                           
  
  1. Figure 1 remains a prose placeholder. Only Figure 2 was produced from real data. For a systems architecture paper, the workflow diagram (Figure 1) is load-bearing; its absence as a rendered figure is not acceptable at camera-ready.
  2. A mathematical inconsistency in the κ derivation (§V-A) is of sufficient severity that it may mislead future implementers. The claimed "within one order of magnitude" agreement should be verified.
  3. The runtime UQ claim in Table I (checkmark for "Runtime UQ propagation across models") is not supported by the implementation (ci_95: null throughout). This claim must be qualified.                                                  
                                                                                                                                                                                                                                            
  Recommendation: Weak Accept — conditional on resolving items 1–3 above. Reviewers R1 and R3 are broadly positive; R2 raises a sharp technical concern on the derivation.                                                                  
                                                                                                                                                                                                                                            
  Overall score: 3.7 / 5 (Weak Accept, conditional)                                                                                                                                                                                         
                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 1 — Score: 4/5 (Weak Accept)                     
                                       
  Summary
                                                                                                                                                                                                                                            
  The authors have addressed the Round 1 concerns effectively. The 14-day, 5-replicate validation is now the core empirical contribution, and the data in §V-B.4 (Table, Figure 2) are convincing. The ensemble statistics (median ± IQR    
  across N=5 CC3D replicates) are appropriately reported. The coupling constant derivation in §V-A is a welcome addition. OISA's positioning relative to COMBINE standards and Vivarium is now more precise.                                
                                                                                                                                                                                                                                            
  Strengths                                                 

  - The 56-checkpoint, 14-day simulation with viral clearance confirmed across all 5 replicates is a solid empirical result. The n_immune trajectory (0 → 6 → 50 over 14 days, IQR tightening then widening appropriately) is biologically  
  plausible and demonstrates the stochastic CC3D dynamics.
  - The ISSL signal renaming (total_cytokine → recruitment_cytokine) and the annotation of total_virus_field: 0.0 in Box 2 are exemplary in terms of transparency.                                                                          
  - The Status column (✓ / ◐) in Table IV is appreciated. It is now clear which components are implemented vs. specified.                                                                                                                   
  - The sim_time_s note under Box 1 resolves an ambiguity that is common in checkpoint-based simulation frameworks.                                                                                                                         
                                                                                                                                                                                                                                            
  Concerns                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                            
  W1 — Figure 1 is still a prose placeholder [Blocking]. The paper writes: "[Figure 1: OISA workflow... Panel (a): Architecture diagram...]". Figure 2 has been generated from real data and is described as a real file                    
  (figures/oisa_trajectory.pdf). Figure 1 has not been generated. For a conference proceeding, all figures must be rendered prior to submission. The textual description of Figure 1 is detailed enough to generate it (or at least a
  schematic); this must be done.                                                                                                                                                                                                            
                                                            
  W2 — §V-B.1 test count inconsistency. The paper now correctly states in §V-A that there are "48 automated tests: 36 unit + 12 integration." However, §V-B.1 reads: "All 36 unit tests pass." This creates ambiguity: do the 12 integration
   tests also pass? The statement should either be updated to "All 48 automated tests pass" or explicitly distinguish which suite results are being reported and why the integration tests are not separately confirmed here.
                                                                                                                                                                                                                                            
  W3 — Table VI: "V at day 14" vs. last checkpoint at day 13.75. The simulation's last tick is at day 13.75 (56th checkpoint: ticks 0–55 at 6 h intervals starting from t=0). Table VI lists "V at day 14 | < 1% of peak" but the actual    
  check is at day 13.75. The label should read "V at day 13.75" or the simulation should be extended by one tick to day 14.0. Minor but precise.
                                                                                                                                                                                                                                            
  W4 — N=5 and IQR width on days 1–2. The IQR for n_immune at day 2 is [11–11], i.e., zero width. With N=5, a zero-width IQR may reflect genuine consensus or a small sample artifact. The paper should acknowledge that N=5 is sufficient  
  for demonstration but that wider ensemble characterisation (N ≥ 20) would be needed to reliably estimate the 25th–75th percentile range. One sentence in §VI-B (ABM stochasticity paragraph) would suffice.
                                                                                                                                                                                                                                            
  Minor                                                     

  - The _note field used inside Box 2 JSON is non-standard JSON-LD and would fail schema validation if _note is not declared as an allowed extension field. Suggest using a comment or a declared oisa:annotation property instead.         
  - Reference [17] (CURE guidelines, arXiv 2502.15597) is a 2025 preprint. For IEEE BIBM 2026, this paper may not yet have a peer-reviewed status. Consider noting this or substituting a peer-reviewed credibility-framework reference if
  one becomes available before submission.                                                                                                                                                                                                  
                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 2 — Score: 3/5 (Borderline / Weak Reject)        
                                                                                                                                                                                                                                            
  Summary
                                                                                                                                                                                                                                            
  The revision is substantially improved over Round 1. However, I have identified a significant mathematical error in the coupling constant derivation (§V-A) that undermines one of the key technical additions of this revision.          
  Additionally, the runtime UQ claim in Table I appears unsupported by the implementation, which I consider a credibility issue. I support acceptance conditional on these being corrected; I am not prepared to recommend acceptance in the
   current state.                                                                                                                                                                                                                           
                                                            
  Strengths

  - The 14-day ensemble result (§V-B.4) is appropriate and the data are internally consistent. The fact that V falls to < 0.1% of peak across all 5 replicates is a meaningful clearance validation.                                        
  - The clarification that ODE→ABM coupling operates at the immune recruitment interface (not the viral diffusion field) was necessary and is now present. The _note fields in Box 2 are pragmatic, if not schema-perfect.
  - The Table IV Status column is a good addition.                                                                                                                                                                                          
                                                                                                                                                                                                                                            
  Concerns                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                            
  M1 — Mathematical inconsistency in κ derivation [Blocking]. §V-A derives the coupling constant κ as follows: ΔtotalCytokine/V ≈ 1.7×10⁻⁶ × 3.5×10⁻³ × 86,400 s ≈ 5×10⁻⁴ pM·mL/copies (per 24 h ABM step). The paper then states that the  
  used constant κ = 3.5×10⁻⁷ per 6 h tick, giving 4 × 3.5×10⁻⁷ = 1.4×10⁻⁶ AU·mL/copies per day, and claims this is "within one order of magnitude" of the analytical estimate 5×10⁻⁴.
                                                                                                                                                                                                                                            
  The ratio is 5×10⁻⁴ / 1.4×10⁻⁶ ≈ 357, i.e., approximately 2.5 orders of magnitude — not one. This is not a rounding difference; it is a discrepancy that will be noticed by readers attempting to reproduce the coupling. The authors must
   either:
  (a) correct the derivation (identify where the factor of ~360 is absorbed — perhaps in the units of totalCytokine vs. pM, or in the normalization of the ImmuneRecruitmentSteppable), or                                                  
  (b) state clearly that κ was set empirically to produce physiologically plausible immune recruitment, and that the derivation provides only a rough order-of-magnitude motivation.                                                        
                                                                                                                                                                                                                                            
  Option (b) is scientifically acceptable but requires removing the claim of "within one order of magnitude."                                                                                                                               
                                                                                                                                                                                                                                            
  M2 — Runtime UQ claim vs. implementation [Significant]. Table I marks OISA with ✓ for "Runtime UQ propagation across models." However, §VI-B (ABM stochasticity) explicitly states that ci_95: null in all ISSL records and that ensemble 
  statistics are "computed post-hoc from the checkpoint archive." Post-hoc computation is not runtime UQ propagation. The ISSL specification may support ci_95 fields, but the implementation does not populate them. The checkmark in Table
   I should be changed to ◐ (specified/partial) or accompanied by a footnote clarifying "planned; ci_95 fields declared in schema but not computed at runtime in the reference implementation."                                             
                                                            
  M3 — Eps/(Ep+Eps) = 100% from day 2 onward, not discussed. The data in Table §V-B.4 show that the infected fraction reaches 97.7% by day 2 and 100% from day 3 onward (14 consecutive days with all epithelial cells infected). This is a 
  biologically extreme outcome: complete depletion of uninfected epithelial cells by day 2–3. The Miao 2010 model does predict rapid infection spread (β_a = 10⁻⁶ mL·copies⁻¹·day⁻¹), but 100% infected fraction for 11 of 14 days raises a
  question: in a biological context, the ODE's Ep equation has a natural replenishment term? If not, the model irreversibly loses all healthy tissue by day 3, and the subsequent viral dynamics are driven by Eps death rate alone (δ_Es   
  term), with no healthy cells left to infect. This is consistent with the 11-day post-peak viral decay, but should be discussed — either to confirm it matches Miao 2010's intended usage or to flag it as a known model limitation that
  does not affect the OISA validation goal.

  M4 — Sensitivity analysis claim is unsupported. §V-A states: "A sensitivity analysis shows that varying κ by ±1 order of magnitude shifts the immune onset day by ±1–2 days but does not qualitatively alter the n_immune trajectory      
  shape." This is stated as a finding but no data, figure, or supplementary result is provided to support it. It should either be backed by evidence or rephrased as "we expect" / "preliminary exploration suggests."
                                                                                                                                                                                                                                            
  ---                                                       
  Reviewer 3 — Score: 4/5 (Weak Accept)

  Summary

  A well-revised paper. The core claims are now backed by 14-day ensemble data, the architecture is clearly described, and the limitations are honestly stated. My concerns are mostly about precision and completeness rather than         
  fundamental issues.
                                                                                                                                                                                                                                            
  Strengths                                                 

  - The ISSL formalism is clearly specified, and the two boxes (ODE and ABM ISSL records) are informative and concrete. The _note field approach for total_virus_field = 0.0 is a pragmatic engineering solution — it communicates the      
  intent even if it is not valid JSON-LD.
  - The CTL-mediated clearance comparison (coupled vs. isolated ODE with T_E_T = 0) is a correct and necessary validation step. This directly supports the claim that the ABM→ODE feedback pathway is functionally significant.             
  - The Discussion (§VI) is balanced. The limitations (validation scope, scaling factor, IPC performance, stochasticity) are clearly and honestly stated.                                                                                   
                                                                                                                                                                                                                                            
  Concerns                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                            
  W1 — Figure 1 [Blocking]. As noted by R1, Figure 1 is described in prose only. For a methods paper proposing a framework, the workflow diagram is arguably more important than the trajectory plot. Its absence as an actual figure is a  
  significant gap.
                                                                                                                                                                                                                                            
  W2 — Scale mismatch between models not addressed. The Miao 2010 ODE is a whole-animal murine model (viral load in copies/mL of total respiratory tract volume ≈ 1 mL). The Sego 2020 CC3D ABM is a 90×90×2 voxel tissue patch (≈ 0.01 mL).
   The ODE's viral load signal (V, copies/mL) is injected into the ABM as a proxy for cytokine concentration — but the physical scale of V in the ODE (whole-animal) and the tissue patch are different. The paper acknowledges a scaling
  factor (_N_IMMUNE_TO_CTL_PER_ML = 100) for the ABM→ODE direction, but the ODE→ABM direction (V → totalCytokine) maps a whole-animal quantity to a tissue-level quantity. This scale mismatch is not discussed. In the context of a        
  validation paper (not a biological claims paper), it should at minimum be acknowledged as a known approximation.

  W3 — IPC busy-wait latency underestimated? §VI-B states: "IPC overhead is < 1 s" for a 14-day run. The five-replicate run took 23.4 min total (≈ 4.7 min per replicate). If CC3D computation accounts for most of this, then IPC overhead 
  is indeed negligible. But the claim should be supported: what is the actual measured per-tick IPC latency, and what fraction does it represent of total per-tick compute time? "< 1 s" over 14 bridge steps (14 × ~50 ms ≈ 700 ms) is
  plausible but should be stated explicitly as a measured value.                                                                                                                                                                            
                                                            
  W4 — The lag: "constant:0" for ODE→ABM edge is semantically unusual. A lag of zero on a feed-forward edge means the ABM receives the ODE signal at the same tick it was emitted, which is possible only because the ODE runs before the   
  ABM at each 24 h boundary. If the execution order were reversed, this would require a lookahead. The paper should either note that zero-lag delivery is order-dependent, or clarify that the configuration graph encodes execution order
  implicitly via the DAG topology.                                                                                                                                                                                                          
                                                            
  Minor

  - The abstract uses "CTL-mediated viral clearance acceleration" but the ODE species T_E_T represents cytotoxic T lymphocytes in the adaptive response, while Sego 2020's Immunecell agents represent innate immune cells (natural         
  killer-like). This formalism mapping should be flagged explicitly — the paper couples an adaptive ODE killing term to an innate-like spatial ABM, which is a model-level approximation worth one sentence.
  - The reference list would benefit from a reference to Iwasaki & Pillai (2014) cited in §V-B.4 — currently referenced by name but no bibliography entry [20] is provided.                                                                 
                                                                                                                                                                                                                                            
  ---
  Summary Scorecard                                                                                                                                                                                                                         
                                                                                                                                                                                                                                            
  ┌─────────────────────┬─────┬─────┬─────┬──────┐
  │                     │ R1  │ R2  │ R3  │ Mean │                                                                                                                                                                                          
  ├─────────────────────┼─────┼─────┼─────┼──────┤                                                                                                                                                                                          
  │ Originality         │  4  │  3  │  4  │ 3.7  │
  ├─────────────────────┼─────┼─────┼─────┼──────┤                                                                                                                                                                                          
  │ Technical soundness │  4  │  3  │  4  │ 3.7  │          
  ├─────────────────────┼─────┼─────┼─────┼──────┤                                                                                                                                                                                          
  │ Significance        │  4  │  4  │  4  │ 4.0  │
  ├─────────────────────┼─────┼─────┼─────┼──────┤                                                                                                                                                                                          
  │ Presentation        │  4  │  3  │  4  │ 3.7  │          
  ├─────────────────────┼─────┼─────┼─────┼──────┤                                                                                                                                                                                          
  │ Overall             │  4  │  3  │  4  │ 3.7  │
  └─────────────────────┴─────┴─────┴─────┴──────┘                                                                                                                                                                                          
                                                            
  ---                                                                                                                                                                                                                                       
  Points bloquants identifiés — résumé opérationnel         
                                                   
  ┌──────────┬─────┬─────────────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
  │ Priorité │ ID  │                                          Problème                                           │                        Action requise                        │                                                           
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ 🔴       │ B1  │ Figure 1 toujours en placeholder prose                                                      │ Générer le diagramme d'architecture (workflow figure)        │                                                           
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ 🔴       │ B2  │ Erreur mathématique κ : 1.4×10⁻⁶ ≠ "within one order of magnitude" de 5×10⁻⁴ (facteur ~360) │ Corriger la dérivation ou reformuler la claim                │                                                           
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🔴       │ B3  │ Table I : ✓ "Runtime UQ propagation" non implémenté (ci_95 = null partout)                  │ Changer en ◐ ou ajouter note de bas de tableau               │                                                           
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟠       │ B4  │ §V-B.1 : "36 unit tests pass" incohérent avec "48 total tests"                              │ Clarifier : tous les 48 tests passent-ils ?                  │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟠       │ B5  │ Sensitivity analysis κ affirmée sans données                                                │ Supprimer la claim ou ajouter figure/table en supplémentaire │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟠       │ B6  │ Eps=100% pendant 11 jours non discuté (dépletion totale épithéliale)                        │ Ajouter 2 phrases en §VI-B ou §V-B.4                         │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟡       │ B7  │ Scale mismatch ODE (whole-animal) vs. CC3D (tissue patch) non discuté                       │ 2 phrases en §VI-B (Limitations)                             │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟡       │ B8  │ Table VI : "V at day 14" mais dernier checkpoint = day 13.75                                │ Corriger le label                                            │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟡       │ B9  │ Référence Iwasaki & Pillai 2014 manquante dans la bibliographie                             │ Ajouter [20]                                                 │
  ├──────────┼─────┼─────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤                                                           
  │ 🟢       │ B10 │ N=5 IQR à zéro-width au jour 2 — reconnaître la petite taille d'échantillon                 │ 1 phrase en §VI-B                                            │
  └──────────┴─────┴─────────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
