---                                                                                                                                                                                                                                       
  IEEE BIBM 2026 — Simulated Program Committee Review                                                                                                                                                                                       
                                                                                                                                                                                                                                            
  Paper ID: BIBM2026-0847                                                                                                                                                                                                                   
  Title: Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling                                                                                                                         
  Track: Computational Systems Biology and Multiscale Modelling                                                                                                                                                                             
  Page limit: 8 pages (full paper)                                                                                                                                                                                                          
  Review deadline: 2026-06-15                                                                                                                                                                                                               
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 1 — Senior Reviewer, Computational Immunology / Multi-scale Modelling                                                                                                                                                            
                                                                                                                                                                                                                                            
  Overall score: 4 — Weak Accept                                                                                                                                                                                                            
  Confidence: 4 (Expert)                                                                                                                                                                                                                    
                                                                                                                                                                                                                                            
  Summary                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                            
  The paper proposes OISA, a runtime orchestration architecture for composing heterogeneous immune simulation models across formalism boundaries. The core contribution is a formalism-agnostic inter-model signal format (ISSL, JSON-LD)   
  combined with a declarative configuration graph and an orchestrator engine. The authors demonstrate the architecture by coupling the Miao 2010 influenza ODE (SBML, BioModels BIOMD0000000546) and the full Sego 2020 CompuCell3D spatial 
  ABM (90×90×2 Cellular Potts grid, 12 steppables unmodified), with zero modifications to either source model. A 3-day coupled simulation is validated and ISSL checkpoints are examined.                                                   
                                                                                                                                                                                                                                            
  Strengths                                                                                                                                                                                                                                 

  1. The "zero lines modified" property is non-trivial and well-evidenced. Coupling a live CC3D subprocess to an SBML ODE via a file-based IPC layer, without touching either model's equations, is a genuine engineering contribution. The 
  separation of the OISABridgeSteppable (IPC only) from the 12 biological steppables (unmodified) is cleanly explained.
  2. Table I is a useful contribution in itself. The capability comparison of SBML/CellML/NeuroML vs. OISA is precise and non-trivial; the distinction between intra-formalism and inter-formalism interoperability is the clearest         
  articulation of the gap I have seen.                                                                                                                                                                                                      
  3. The ISSL design is sound. The six-section structure (envelope, continuous_state, discrete_events, export_signals, internal_parameters, watchdog) addresses practical needs: the formalism tag in the envelope allows the orchestrator
  to apply appropriate normalisation before routing; the divergence_score watchdog is a useful feature for long-running simulations.                                                                                                        
  4. Box 1 and Box 2 are excellent. Showing actual JSON records from both models with real values (V=3.29×10⁵, n_immune=7) makes the architecture concrete.
                                                                                                                                                                                                                                            
  Weaknesses                                                
                                                                                                                                                                                                                                            
  W1 — Internal inconsistency between abstract and validation section (major).                                                                                                                                                              
  The abstract claims "56 ISSL checkpoints with no causal ordering violations" (implying a 14-day run), while §V-B.4 presents a 3-day trajectory table and §V-A states "3-day demonstration." Table VI includes checks that require 14 days
  (e.g. "V at day 14 < 1% of peak"), but the validated run is explicitly 3 days. This inconsistency will confuse reviewers and could be flagged as an inflation of claims. The authors must resolve this: either extend the validated run to
   14 days, or remove the 14-day claims from the abstract and Table VI, or make explicit that the 14-day checks are from a separate (undescribed) run.
                                                                                                                                                                                                                                            
  W2 — The coupling constant 3.5×10⁻⁷ AU·mL/copies is ungrounded (major).                                                                                                                                                                   
  The ODE → ABM signal mapping (viral_load → totalCytokine proxy via coupling constant 3.5×10⁻⁷) is described as "calibrated to maintain cytokine within Sego 2020's physiological range." No derivation, sensitivity analysis, or
  calibration protocol is provided. This is a free parameter that could dominate the coupled dynamics. The immune cell count trajectory (0→7→12) could be almost entirely explained by this constant. Without at least a one-paragraph      
  justification and a sensitivity test (e.g. ±1 order of magnitude), this is a significant scientific gap.
                                                                                                                                                                                                                                            
  W3 — Validation is limited to a single stochastic realisation (moderate).                                                                                                                                                                 
  The n_immune trajectory (0, 7, 12 agents) is one sample from a stochastic process. With ir_prob_scaling_factor = 0.01, even a null model (S growing without viral signal) can produce sporadic agents. At minimum, the authors should
  report ensemble statistics (n=10–20 replicates) to distinguish signal-driven recruitment from spontaneous baseline. The ci_95: null fields in the ISSL are noted in the limitations, but a conference submission without any uncertainty  
  quantification on the key result is weak.                 
                                                                                                                                                                                                                                            
  W4 — Figure placeholders are unacceptable for final submission.                                                                                                                                                                           
  Figures 1 and 2 are described in bracketed text ([Figure 1: ...]) but not provided. IEEE BIBM requires camera-ready figures. The workflow figure and the 3-day trajectory figure are central to the paper's claims; their absence makes it
   impossible to assess visual presentation.                                                                                                                                                                                                
                                                            
  Minor Comments                                                                                                                                                                                                                            
                                                            
  - §IV-C, temporal scheduling paragraph: "72 MCS × 20 min/MCS" — this should be verified against the Sego 2020 supplementary. The XML uses <Steps>1010</Steps> but no MCS-to-real-time conversion factor is specified in the XML itself; it
   is defined in the steppable (step_period = 20×60 s). Worth a footnote.
  - The "wildcard_namespace" in Table III is mentioned but never discussed in the text. Either elaborate (1–2 sentences) or remove.                                                                                                         
  - Reference [17] (Sauro et al. 2025) is an arXiv preprint. Verify that it will be formally published before BIBM submission deadline.                                                                                                     
                                                                                                                                                                                                                                            
  Recommendation                                                                                                                                                                                                                            
                                                                                                                                                                                                                                            
  The paper addresses a real gap and the core implementation is sound. The abstract–validation inconsistency and the unjustified coupling constant are fixable. Conditional accept if W1–W3 are addressed and figures are provided.         
                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 2 — Program Committee Member, Bioinformatics / Interoperability Standards
                                                                                                                                                                                                                                            
  Overall score: 3 — Borderline / Weak Reject
  Confidence: 3 (Knowledgeable)                                                                                                                                                                                                             
                                                            
  Summary                                                                                                                                                                                                                                   
                                                            
  The authors propose OISA, a JSON-LD based inter-model signal layer for composing ODE and ABM models of immune processes, demonstrated on a coupled influenza simulation. The implementation is technically competent and the              
  zero-modification claim is well-supported. However, I have significant concerns about novelty positioning, validation rigour, and completeness that prevent me from recommending acceptance without substantial revision.
                                                                                                                                                                                                                                            
  Strengths                                                 

  1. The idea of a formalism-agnostic interface record (ISSL) is useful and cleanly specified.                                                                                                                                              
  2. Running the full CC3D ABM as a subprocess rather than reimplementing it is the right engineering choice; the IPC handshake design is simple and reproducible.
  3. The mapping to CURE guidelines (Table VII) is well-argued.                                                                                                                                                                             
                                                                                                                                                                                                                                            
  Weaknesses                                                                                                                                                                                                                                
                                                                                                                                                                                                                                            
  W1 — Novelty not sufficiently distinguished from Vivarium (major).                                                                                                                                                                        
  The authors claim Vivarium "does not provide a standardised inter-model signal format with embedded UQ, model-derived edge lags, or a biological plausibility constraint engine." This is partially correct but overstated. Vivarium's
  Store / Process interface does support heterogeneous time steps and stochastic-deterministic coupling; several Vivarium publications demonstrate ODE–ABM composition. The paper would be stronger if it demonstrated a concrete failure   
  case of Vivarium on the influenza coupling problem, rather than asserting Vivarium's limitations. Similarly, COPASI's task scheduling and BioNetGen's agent-based extensions are not discussed.
                                                                                                                                                                                                                                            
  W2 — The "full spatial ABM" claim requires more spatial evidence (major).                                                                                                                                                                 
  The paper's claim that the Sego 2020 CC3D model runs "unmodified" and that coupling is demonstrated at the spatial level is undermined by the validation evidence. The ISSL records report only n_immune (scalar count) and
  total_virus_field (scalar integral). There is no evidence that spatial properties — viral spread gradient, immune cell chemotaxis, contact killing by individual agents — are actually exercised. A figure showing the CC3D grid state at 
  days 0 and 2 (e.g. cell type map, cytokine field heatmap) would substantiate the "true spatial ABM" claim. As written, the validation could equally have been produced by the scalar ODE surrogate the authors replaced.
                                                                                                                                                                                                                                            
  W3 — No comparison to uncoupled baselines for the ABM side (major).                                                                                                                                                                       
  The authors compare coupled vs. isolated ODE trajectories to demonstrate CTL-mediated clearance. But there is no analogous test for the ABM side: does the Sego 2020 CC3D model produce different immune recruitment dynamics when driven
  by the Miao 2010 ODE signal versus a synthetic or null signal? Without this, it is unclear whether the ODE → ABM signal pathway is actually affecting CC3D dynamics, or whether the immune cell count would have been similar regardless. 
                                                            
  W4 — The coupling constant has no biological justification (moderate).                                                                                                                                                                    
  The choice of 3.5×10⁻⁷ AU·mL/copies to convert viral_load to totalCytokine is described as "empirical." For a Methods paper proposing a reusable architecture, an unjustified free parameter in the demonstration is a serious concern. If
   the architecture claims to enable non-invasive model coupling, the coupling constants on edges should be derivable from the models' documented units — or at minimum, the sensitivity of the key results to this parameter should be     
  shown.
                                                                                                                                                                                                                                            
  W5 — Test count inconsistency (minor).                                                                                                                                                                                                    
  §V-A states "36 automated unit and integration tests" but the abstract says "36 unit tests + integration tests." Are the integration tests included in the 36 or additional? The previous version of this paper mentioned 49 tests; the
  current version appears to have reduced this without explanation.                                                                                                                                                                         
                                                            
  Questions for Authors                                                                                                                                                                                                                     
                                                            
  1. Can you provide a CC3D grid visualisation at day 2 showing Immunecell agent positions and the cytokine field, to substantiate the spatial coupling claim?                                                                              
  2. What is the range of n_immune values across 20 stochastic replicates at day 2? Is the range consistent with Sego 2020 Fig. S3?
  3. How does the Miao 2010 ODE trajectory change if you provide a synthetic viral load signal to a standalone Sego 2020 CC3D run (without the ODE coupled)? Does the CC3D immune response differ?                                          
                                                                                                                                                                                                                                            
  Recommendation                                                                                                                                                                                                                            
                                                                                                                                                                                                                                            
  Borderline. The architecture is sound but the validation does not currently demonstrate spatial ABM coupling convincingly. The coupling constant issue and the Vivarium comparison weakness need addressing. I would reconsider with a    
  major revision.                                           
                                                                                                                                                                                                                                            
  ---                                                       
  Reviewer 3 — Program Committee Member, Systems Software / Simulation Middleware

  Overall score: 4 — Weak Accept
  Confidence: 3 (Knowledgeable)
                                                                                                                                                                                                                                            
  Summary
                                                                                                                                                                                                                                            
  This paper proposes a middleware architecture for coupling heterogeneous biological simulation models. I will focus on the technical and software architecture aspects. The overall design is reasonable; my concerns are mostly about    
  robustness claims, scalability, and presentation clarity.
                                                                                                                                                                                                                                            
  Strengths                                                 

  1. The subprocess + file-based IPC design is pragmatic. It avoids shared-memory race conditions between the CC3D Cellular Potts engine and the Python ODE integrator — an important correctness property that the authors do not          
  explicitly mention but implicitly achieve.
  2. The blocking handshake (abm_ready sentinel) guarantees synchronisation without busy-wait starvation, assuming OS-level inotify semantics (which the paper does not use but could). The current poll-sleep(0.05s) is sufficient for the 
  timescales involved.                                                                                                                                                                                                                      
  3. ISSL as JSON-LD is a good choice: it is human-readable, schema-validatable, and semantically annotated without requiring a separate ontology tool.
                                                                                                                                                                                                                                            
  Weaknesses                                                
                                                                                                                                                                                                                                            
  W1 — The file-based IPC is described as a limitation but its implications are understated (moderate).                                                                                                                                     
  The paper notes "~50 ms/tick IPC overhead, negligible at 14 days" (VI-B). However, the more important concern is reliability: file-based IPC under filesystem pressure (NFS mounts, slow disks, simultaneous jobs) can silently fail —
  e.g., abm_out.json partially written when the sentinel is raised, or sentinel persistence after an adapter crash. The paper describes a _TIMEOUT_S = 600 s safeguard in the bridge steppable, but does not discuss what happens after a   
  timeout — does CC3D terminate cleanly? Is the simulation restartable? These are engineering completeness questions, not theoretical ones, and they matter for the architecture's claimed robustness.
                                                                                                                                                                                                                                            
  W2 — The nine-component orchestrator (Table IV) is architecturally specified but not all implemented (moderate).                                                                                                                          
  Components 7 (Calibration bridge) and 6 (Transfer dispatcher, with model-derived lag) are described but appear absent from the reference implementation based on the configuration graph and test suite. The paper should distinguish
  clearly between the OISA specification (design) and the OISA reference implementation (current code). A reviewer cannot currently determine which claims are architectural proposals vs. demonstrated functionality.                      
                                                            
  W3 — Configuration graph is not validated (minor).                                                                                                                                                                                        
  The paper states the configuration graph is "the orchestrator's sole input at initialisation." Is there a JSON Schema or formal grammar for it? Is cyclic dependency detected at parse time? The text describes cycle detection as a
  feature of the causal resolver (§IV-C), but this implies cycles are detected only at simulation start, not at configuration load. A static analyser that validates the graph before any model is launched would be a straightforward and  
  important robustness addition.                            
                                                                                                                                                                                                                                            
  W4 — Scalability to N>2 models not discussed (minor).                                                                                                                                                                                     
  The architecture supports N-model compositions by design (directed graph), but the current implementation and test suite only exercise N=2. The GSimT GCD computation is trivial for two models; with N=8 models having incommensurable Δt
   values, the scheduler complexity and the number of IPC channels grow non-trivially. At minimum a paragraph on N>2 scalability would strengthen the architecture section.                                                                 
                                                            
  Minor Comments                                                                                                                                                                                                                            
                                                            
  - §IV-C: "blocks models ahead of GSimT tick" — should read "holds models whose next_step_due is beyond the current tick." As written it is ambiguous (blocking a model that is ahead of the tick means blocking a fast model, which is    
  correct, but the phrasing could mean blocking a model behind the tick, which would be wrong).
  - Box 1 and Box 2 differ in sim_time_s interpretation: Box 1 shows 86400 for what is described as a "day 1" record. Is this after the step (t=1 day elapsed) or before (t=0 day, about to step to 1 day)? This is critical for causality  
  correctness and should be stated explicitly.                                                                                                                                                                                              
  - The total_virus_field: 0.0 in Box 2 at day 1 is surprising given V=3.29×10⁵ copies/mL in the ODE. If the CC3D Virus field is not being driven by the ODE viral load, the ODE→ABM coupling is incomplete. The paper should explain why
  the CC3D Virus field is zero while the ODE reports significant viral load.                                                                                                                                                                
                                                            
  Recommendation                                                                                                                                                                                                                            
                                                            
  Weak accept. The architecture has genuine merit. The implementation completeness gap (Table IV claims vs. actual code) and the total_virus_field: 0.0 anomaly in Box 2 need addressing.                                                   
  
  ---                                                                                                                                                                                                                                       
  Area Chair Meta-Review                                    
                        
  Recommendation: Major Revision — Resubmit to next cycle
  (IEEE BIBM 2026 allows one major revision round before final accept/reject decision)                                                                                                                                                      
                                                                                                                                                                                                                                            
  Summary of Reviewer Consensus                                                                                                                                                                                                             
                                                                                                                                                                                                                                            
  Three reviewers assessed this paper. Scores: 4, 3, 4 (average 3.67). The reviewers agree on the following:                                                                                                                                
                                                            
  Shared strengths: The zero-modification coupling of a full CC3D spatial ABM to an SBML ODE is a genuine and non-trivial contribution. The ISSL design is sound. The paper is well-motivated and addresses a real gap in computational     
  immunology infrastructure.                                
                                                                                                                                                                                                                                            
  Shared concerns requiring revision before acceptance:                                                                                                                                                                                     
  
  C1 — Critical internal inconsistency: abstract claims 56 checkpoints / 14 days; validation shows 3 days (raised by R1). This is the single most urgent fix. The abstract must accurately describe the validated results. Either run and   
  report the 14-day simulation with ensemble statistics, or revise all 14-day claims to 3-day claims and remove Table VI rows that require 14 days of data (notably "V at day 14 < 1% of peak").
                                                                                                                                                                                                                                            
  C2 — The ODE→ABM coupling constant 3.5×10⁻⁷ is unjustified (R1, R2). This is a free parameter controlling the central claim. A sensitivity analysis (at minimum ±1 order of magnitude, showing whether n_immune dynamics change           
  qualitatively) is required.
                                                                                                                                                                                                                                            
  C3 — total_virus_field: 0.0 in Box 2 demands an explanation (R3). If the CC3D Virus diffusion field is not receiving the ODE viral load, then the ODE→ABM coupling pathway is injecting only into the totalCytokine shared variable — not 
  into the actual CC3D spatial fields. This means the spatial virus dynamics in CC3D are not actually driven by the Miao 2010 ODE. This may be architecturally acceptable (OISA couples at the immune recruitment level, not the viral
  spread level) but it must be stated explicitly, and the "full spatial ABM" claim must be scoped accordingly. This is also R2's concern (W2): is the spatial simulation actually exercised?                                                
                                                            
  C4 — Figure placeholders must be replaced with actual figures (R1). No exceptions for camera-ready submission.                                                                                                                            
  
  C5 — Clarify which of the nine orchestrator components (Table IV) are implemented vs. specified (R3). This is a CURE understandability requirement that the paper ironically applies to others but violates itself.                       
                                                            
  Items That Need Not Block Acceptance                                                                                                                                                                                                      
                                                            
  - N>2 scalability discussion (R3-W4): can be addressed with 1 paragraph                                                                                                                                                                   
  - Vivarium comparison (R2-W1): can be addressed by adding a concrete failure scenario or softening the claim
  - Test count inconsistency (R2-W5): minor, resolve with one sentence                                                                                                                                                                      
                                                                                                                                                                                                                                            
  Verdict                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                            
  This paper makes a real contribution to the immune digital twin infrastructure problem. The architecture is sound; the CC3D coupling is technically impressive. However, the abstract-validation gap (C1) and the unexplained coupling    
  parameter (C2) and zero virus field (C3) together represent a level of incompleteness that cannot be accepted at IEEE BIBM without revision. The paper is conditionally fundable for major revision.
                                                                                                                                                                                                                                            
  Action: Request major revision. Authors must submit a point-by-point response addressing C1–C5.                                                                                                                                           
  
  ---                                                                                                                                                                                                                                       
  Synthèse des points à corriger en priorité                
                                                                                                                                                                                                                                            
  ┌─────────────┬───────────────────────────────────────────────────────────────┬─────────────────────┬───────────────────────────────────────────────────────────────────────────────┐
  │  Priorité   │                           Problème                            │  Section concernée  │                                Action requise                                 │                                                     
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤
  │ 🔴 Bloquant │ Incohérence 3 jours vs 14 jours / 56 checkpoints              │ Abstract, Table VI  │ Choisir : étendre à 14 jours OU purger toutes les références à 14 jours       │                                                     
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤
  │ 🔴 Bloquant │ Constante de couplage 3.5×10⁻⁷ non justifiée                  │ §V-A, §VI-B         │ Ajouter dérivation ou analyse de sensibilité (±1 OOM)                         │                                                     
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🔴 Bloquant │ total_virus_field: 0.0 dans Box 2 inexpliqué                  │ Box 2, §V-B.4       │ Expliquer pourquoi le champ Virus CC3D est 0 (couplage partiel intentionnel?) │                                                     
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🔴 Bloquant │ Figures en placeholder                                        │ §IV-B, §V-B.4       │ Générer et insérer Figure 1 (workflow) + Figure 2 (trajectoire)               │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟠 Majeur   │ N_immune = valeur unique, pas d'ensemble stochastique         │ §V-B.4, limitations │ Reporter N=10–20 réplicats ou justifier pourquoi une seule trajectoire suffit │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟠 Majeur   │ Distinction implémenté vs. spécifié (Table IV components 6,7) │ §IV-C, Table IV     │ Ajouter colonne "Status: implemented / specified" dans Table IV               │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟡 Modéré   │ Vivarium comparaison trop affirmative                         │ §II-A               │ Adoucir OU fournir scénario d'échec concret de Vivarium                       │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟡 Modéré   │ Test count ambigu (36 inclut intégration ou pas?)             │ §V-A                │ Clarifier : "19+17 unit tests + X integration tests"                          │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟢 Mineur   │ wildcard_namespace mentionné mais non expliqué                │ §IV-B, Table III    │ 1–2 phrases ou supprimer la ligne                                             │
  ├─────────────┼───────────────────────────────────────────────────────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────────────┤                                                     
  │ 🟢 Mineur   │ sim_time_s sémantique (avant ou après le step?)               │ Box 1 & 2           │ Préciser "sim_time_s is the clock value after the step completes"             │
  └─────────────┴───────────────────────────────────────────────────────────────┴─────────────────────┴───────────────────────────────────────────────────────────────────────────────┘    
