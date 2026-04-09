---                                                                                                                                                                                                                                       
  REVIEW COMPLET — OISA paper, IEEE BIBM 2026                                                                                                                                                                                               
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  PARTIE 1 — ERREURS FACTUELLES ET DE FORME                                                                                                                                                                                                 
                                                                                                                                                                                                                                            
  1.1 Erreur critique : numérotation des références
                                                                                                                                                                                                                                            
  Bug sévère. La liste de références saute de [17] à [34]-[35]. Les références [18]–[33] ont été supprimées du corps du texte (elles appartenaient à la version précédente sur l'ontogénie immunitaire) mais les nouveaux indices [34] et   
  [35] n'ont pas été renormalisés. Un reviewer IEEE arrêtera sa lecture ici.
                                                                                                                                                                                                                                            
  Correction requise : Renommer [34] → [18] et [35] → [19] dans tout le document.                                                                                                                                                           
   
  ---                                                                                                                                                                                                                                       
  1.2 Référence manquante : Murphy et al. 1973              
                                                                                                                                                                                                                                            
  Section V-A : "calibrated against Murphy et al. 1973 murine infection data" — ce papier est cité en texte mais absent de la liste de références. Miao 2010 (maintenant [18]) le cite lui-même, donc la formulation correcte serait :
  "calibrated against murine infection data (Murphy et al. 1973, as cited in [18])" ou ajouter la référence complète :                                                                                                                      
                                                            
  ▎ [19-candidat] W.J. Murphy, "Influenza A virus infection of mice: II.", Infect. Immun., 1973. (à vérifier — le DOI exact est dans Miao 2010 Table 1 footnotes)                                                                           
                                                            
  ---                                                                                                                                                                                                                                       
  1.3 Terminologie incorrecte : "stochastic differential equation"
                                                                  
  Section V-A : "implementing the stochastic differential equation dS/dt = addRate + ck/delayRate − subRate·n_immune − decayRate·S"
                                                                                                                                                                                                                                            
  L'équation de Sego 2020 est une ODE déterministe. La partie stochastique est l'ensemencement de Bernoulli des cellules immunitaires basé sur S, pas l'équation différentielle elle-même. Le terme "stochastic differential equation" (SDE)
   a un sens mathématique précis (terme de bruit de Wiener) qui ne s'applique pas ici.                                                                                                                                                      
                                                                                                                                                                                                                                            
  Correction : "implementing an immune recruitment ODE dS/dt = ..., with stochastic immune cell seeding (Bernoulli probability ∝ S × ir_prob_scaling_factor)"                                                                               
   
  ---                                                                                                                                                                                                                                       
  1.4 Confusion du label "ABM" pour le composant Sego 2020  
                                                          
  Le composant Sego 2020 utilisé est un module scalaire ODE + Bernoulli sampling, pas un ABM spatial CompuCell3D. Le papier appelle ce composant "ABM" tout au long, y compris dans l'abstract et le titre de section ("ODE–ABM coupling").
  C'est une surreprésentation :                                                                                                                                                                                                             
   
  - Le vrai ABM Sego 2020 = 84 000 agents spatiaux sur grille CC3D (non utilisé)                                                                                                                                                            
  - Ce qui est utilisé = dS/dt avec n_immune comme variable d'état discrète
                                                                                                                                                                                                                                            
  Le papier le reconnaît en Limitations (§VI-B) mais trop tardivement. Cette distinction doit apparaître dès l'abstract.                                                                                                                    
                                                                                                                                                                                                                                            
  Correction suggérée pour l'abstract : "and the immune recruitment steppable of Sego et al. 2020 (a stochastic ODE module originally designed for a CompuCell3D ABM; Python, GitHub @5b7e42c)"                                             
                                                            
  ---                                                                                                                                                                                                                                       
  1.5 Affirmation "first" sans support                      
                                      
  §II-C : "OISA is the first runtime orchestration architecture designed specifically for heterogeneous immune model composition"
                                                                                                                                                                                                                                            
  Cette affirmation de priorité absolue ("first") est non défendable devant un programme committee IEEE sans preuve par revue systématique. Vivarium [1], MultiCellDS (Macklin 2015), le framework de Cherian et al. (2023, npj Syst. Biol.)
   ont des prétentions adjacentes.                                                                                                                                                                                                          
                                                                                                                                                                                                                                            
  Correction : Adoucir en : "To the best of our knowledge, OISA is the first runtime orchestration architecture..."                                                                                                                         
   
  ---                                                                                                                                                                                                                                       
  1.6 Claim UQ vs implémentation (incohérence interne)      
                                                                                                                                                                                                                                            
  Le papier revendique dans Table II et Table VII que OISA propage l'incertitude ("ISSL ci_95 fields; uncertainty propagated through signals"). Mais Box 1 montre "ci_95": null pour tous les champs. La validation (§V-B) ne démontre
  aucune propagation d'intervalles de confiance entre modèles.                                                                                                                                                                              
                                                            
  Deux options :                                                                                                                                                                                                                            
  - (A) Retirer la claim UQ du tableau comparatif Table I (ligne "Runtime UQ propagation across models ✓") et de Table VII, en la marquant comme "architecture-level provision, not demonstrated in this implementation"
  - (B) Implémenter la propagation Monte Carlo pour l'ODE et l'inclure dans les résultats                                                                                                                                                   
                                                                                         
  L'option (A) est suffisante pour la soumission mais fragilise la proposition comparative avec SBML.                                                                                                                                       
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  1.7 Valeurs numériques dans Table VI sans source de simulation                                                                                                                                                                            
                                                                                                                                                                                                                                            
  Table VI contient : "Day 2 (±6 h)", "8.4×10⁶ copies/mL", "≥ 9.3%", "S = 124.3 AU". Ces valeurs précises doivent venir d'une simulation réelle enregistrée. Elles ne correspondent pas à ce que les tests vérifient (les tests ne vérifient
   que des bornes, pas des valeurs exactes). Un reviewer demandera d'où viennent ces chiffres.                                                                                                                                              
                                                            
  Action requise : Lancer python models/orchestrator/run_demo.py et utiliser les valeurs réelles de sortie, ou reformuler les valeurs comme des bornes testées plutôt que comme des résultats ponctuels.                                    
                                                            
  ---                                                                                                                                                                                                                                       
  1.8 Figure 2 manquante                                    
                                                                                                                                                                                                                                            
  Le papier référence "[Figure 2: 14-day coupled simulation trajectories...]" mais cette figure n'existe pas (figures/ ne contient que oisa_workflow.pdf/png). Pour la soumission, soit cette figure est générée, soit la référence est
  supprimée du texte.                                                                                                                                                                                                                       
                                                            
  ---                                                                                                                                                                                                                                       
  1.9 Table I : libellé de ligne ambigu                     
                                                                                                                                                                                                                                            
  Ligne "Requires model rewrite to adopt" : ✓ pour SBML, CellML, NeuroML. Un modèle déjà en SBML ne nécessite pas de réécriture pour être utilisé dans un outil SBML. Le libellé est ambigu.
                                                                                                                                                                                                                                            
  Reformulation : "Requires model source modification to adopt the framework" — ce qui clarifie que la ✓ signifie "yes if your model is not already in this format".                                                                        
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  1.10 Incohérence checkpoint count/texte                   
                                                                                                                                                                                                                                            
  §IV-B : config YAML déclare checkpoint_interval_s: 21600 (6h). §V-B.3 dit "56 ISSL checkpoint records". 14 jours × 4 checkpoints/jour = 56. ✓ Correct. Mais §V-B.3 dit aussi "ABM steps at 24 h boundaries" produisant des records
  supplémentaires. L'orchestrateur produit 56 records JSON (un par tick), chacun contenant soit ODE seul, soit ODE+ABM. Ce point mériterait une phrase de clarification.                                                                    
                                                            
  ---                                                                                                                                                                                                                                       
  PARTIE 2 — ANALYSE SCIENTIFIQUE                           
                                                                                                                                                                                                                                            
  2.1 Forces du papier
                                                                                                                                                                                                                                            
  ┌───────────────────────────────────┬─────────────────────────────────────────────────────────────────┐                                                                                                                                   
  │             Dimension             │                           Évaluation                            │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                                                                                                                                   
  │ Clarté du problème                │ Excellente — le gap "ODE+ABM sans réécriture" est bien posé     │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Originalité de l'architecture     │ Solide — ISSL + DAG causal + GSimT est un design cohérent       │                                                                                                                                   
  ├───────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                                                                                                                                   
  │ Justification de l'implémentation │ Très bonne — zéro ligne modifiée est vérifiable et citable      │                                                                                                                                   
  ├───────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                                                                                                                                   
  │ Test suite traceable              │ Fort — 49 tests avec traceabilité aux figures publiées          │
  ├───────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                                                                                                                                   
  │ Limitation acknowledgment         │ Honnête — CC3D, scaling factor, single trajectory tous reconnus │
  └───────────────────────────────────┴─────────────────────────────────────────────────────────────────┘                                                                                                                                   
                                                            
  ---                                                                                                                                                                                                                                       
  2.2 Faiblesses scientifiques majeures                     
                                                                                                                                                                                                                                            
  W1 — Couplage cross-disease injustifié
                                                                                                                                                                                                                                            
  Le module Sego 2020 est développé pour SARS-CoV-2 et couplé ici à un modèle influenza A. Les équations de recrutement immunitaire sont bien disease-agnostic, mais cette justification est absente du texte. Un reviewer bioinformatique  
  posera cette question immédiatement.                                                                                                                                                                                                      
                                                                                                                                                                                                                                            
  Action : Ajouter une phrase en V-A justifiant que l'ODE de recrutement de Sego 2020 (§ImmuneRecruitmentSteppable) est paramétrisée sur des comportements cellulaires génériques (cytokine-driven, innate immune delay) indépendants du    
  pathogène.
                                                                                                                                                                                                                                            
  ---                                                       
  W2 — Faible démonstration de l'effet couplage
                                               
  La claim principale sur le couplage biologique est : "V_coupled ≤ V_isolated at day 14". Mais le papier dit "within floating-point tolerance" — ce qui suggère que l'effet est négligeable (le n_immune stochastique reste faible jusqu'à
  la fin, donc T_E_T ≈ 0 pendant l'essentiel de la simulation). Si l'effet CTL est invisible à l'échelle de la figure, la démonstration du couplage biologique est creuse.                                                                  
   
  Action : Quantifier la différence en pourcentage. Ou présenter la comparaison avec n_immune=500 injecté manuellement (qui montre un effet mesurable selon le test suite) plutôt que la trajectoire stochastique faible.                   
                                                            
  ---                                                                                                                                                                                                                                       
  W3 — Généralité de l'architecture non démontrée           
                                                                                                                                                                                                                                            
  Le papier affirme que "any OISA-compliant model can be substituted without modifying its peers" mais ne démontre qu'un seul couplage à 2 modèles. La généralité architecturale n'est pas testée. Les reviewers compareront à Vivarium, qui
   a démontré sa généralité sur 5+ modèles différents.                                                                                                                                                                                      
                                                            
  Réponse possible : Soit ajouter une discussion des extensions naturelles (CC3D complet, SBML antibody model), soit limiter la claim à "the adapter pattern is demonstrated to be non-invasive for two independently published models of   
  different formalisms".                                    
                                                                                                                                                                                                                                            
  ---                                                       
  W4 — Composants orchestrateur non implémentés
                                               
  Table IV liste 9 composants. La calibration bridge (7), le transfer dispatcher avec lag dynamique (6), et le Mahalanobis OOD detector (1) ne sont pas présents dans la validation. Soit les retirer de Table IV (marquer "future work"),
  soit les présenter clairement comme spécification architecturale vs implémentation démontrée.                                                                                                                                             
   
  ---                                                                                                                                                                                                                                       
  2.3 Comparaison avec Vivarium [1]                         
                                   
  Le papier écrit : "Vivarium does not provide a standardised inter-model signal format with embedded uncertainty quantification, model-derived edge lags, or a biological plausibility constraint engine". Ces trois points méritent
  vérification :                                                                                                                                                                                                                            
  - UQ : Vivarium ports ne portent pas de ci_95 natifs. ✓ Correct.
  - Lags dynamiques : Vivarium peut implémenter des lags via des processus intermédiaires. La distinction est que OISA les rend déclaratifs. Nuance à préciser.                                                                             
  - Constraint engine : Vivarium n'a pas de constraint engine intégré. ✓ Correct.                                                                              
                                                                                                                                                                                                                                            
  La comparaison est défendable mais devrait être plus précise : "unlike Vivarium, OISA provides..." plutôt que d'affirmer des manques absolus.                                                                                             
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  PARTIE 3 — SIMULATION D'ÉVALUATION IEEE BIBM 2026                                                                                                                                                                                         
                                                            
  IEEE BIBM utilise une échelle 1-5 : 1=Strong Reject, 2=Reject, 3=Weak Accept, 4=Accept, 5=Strong Accept. Seuil d'acceptation typique ≥ 3.5 avec consensus.
                                                                                                                                                                                                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 1 (Methods / Frameworks specialist)                                                                                                                                                                                              
                                                                                                                                                                                                                                            
  Score : 3 — Weak Accept                                   
                                                                                                                                                                                                                                            
  ▎ The paper addresses a genuine gap in computational immunology: the lack of a runtime coordination layer for heterogeneous ODE+ABM models. The ISSL design is clean and the "zero modification" demonstration is concrete and verifiable.
   The 49-test suite traceable to published figures is a notable strength.                                                                                                                                                                  
                                                                                                                                                                                                                                            
  ▎ However, several issues limit my enthusiasm. The reference numbering has a conspicuous gap ([17] → [34],[35]) suggesting incomplete revision from a prior version. The claimed UQ propagation is not demonstrated: ci_95 fields are null
   throughout Box 1 and no CI compounding is shown in §V. The paper labels the Sego 2020 scalar ODE component an "ABM", which is an overstatement — CompuCell3D agents are not used. The coupling biological effect (CTL clearance 
  acceleration) appears negligible with stochastic seeding: "within floating-point tolerance" is not a satisfying quantitative result. I would accept a revised version addressing these points.                                            
                                                            
  ---
  Reviewer 2 (Computational Immunology / Bioinformatics)
                                                        
  Score : 2 — Reject (major revision)
                                                                                                                                                                                                                                            
  ▎ The biological motivation is clear and the framework design is principled. My primary concern is the cross-disease coupling: the Sego 2020 model is for SARS-CoV-2 and is coupled here to an influenza ODE. No biological justification 
  is provided for why the immune recruitment dynamics from one pathogen context apply to another. This is not necessarily wrong — the recruitment ODE may be disease-agnostic — but the paper must argue this explicitly.                   
                                                                                                                                                                                                                                            
  ▎ Second, the "ABM" component used is a one-dimensional ODE with Bernoulli sampling. The paper's core claim — formalism-agnostic ODE+ABM composition — would be more convincing with a true spatially-explicit ABM (e.g., the full Sego   
  CC3D model with an ISSL emitter). The current coupling is ODE+ODE with stochastic noise, which is a much weaker demonstration.
                                                                                                                                                                                                                                            
  ▎ Murphy 1973 is cited in text but absent from references. The "first" claim in §II-C is unsubstantiated.                                                                                                                                 
   
  ▎ Minor: "stochastic differential equation" is terminologically incorrect.                                                                                                                                                                
                                                            
  ---                                                                                                                                                                                                                                       
  Reviewer 3 (Systems Biology / Software Architecture)      
                                                                                                                                                                                                                                            
  Score : 4 — Accept
                                                                                                                                                                                                                                            
  ▎ This paper makes a clear and valuable contribution: demonstrating that an inter-model protocol (ISSL) can couple two independently published models with adapter code only, without touching biological source files. The approach is   
  pragmatic and directly addresses the reproducibility and interoperability concerns raised by [2], [7], [9], [12]. The architecture is well-specified and the configuration graph design is elegant.
                                                                                                                                                                                                                                            
  ▎ I note the reference numbering gap (fix required before final submission) and the missing Murphy 1973 citation. The distinction between ODE and ABM in the validation case could be clearer. The orchestrator component table (Table IV)
   lists capabilities not demonstrated in this paper; a clearer notation of "proposed" vs "implemented and tested" would be appropriate. Nevertheless, the core framework contribution is sound and the influenza coupling provides a 
  concrete, reproducible demonstration.                                                                                                                                                                                                     
                                                            
  ▎ I recommend accept with minor revisions.                                                                                                                                                                                                
   
  ---                                                                                                                                                                                                                                       
  Score agrégé et recommandation de programme               
                                             
  ┌─────────────────────┬───────┬───────────────────────────────────────┐
  │      Reviewer       │ Score │                Verdict                │                                                                                                                                                                   
  ├─────────────────────┼───────┼───────────────────────────────────────┤
  │ R1 (Methods)        │ 3     │ Weak Accept                           │                                                                                                                                                                   
  ├─────────────────────┼───────┼───────────────────────────────────────┤
  │ R2 (Bioinformatics) │ 2     │ Reject (major)                        │
  ├─────────────────────┼───────┼───────────────────────────────────────┤                                                                                                                                                                   
  │ R3 (Architecture)   │ 4     │ Accept                                │
  ├─────────────────────┼───────┼───────────────────────────────────────┤                                                                                                                                                                   
  │ Méta-revieweur      │ 3.0   │ Borderline — révision majeure requise │
  └─────────────────────┴───────┴───────────────────────────────────────┘                                                                                                                                                                   
   
  Décision simulée : Major Revision Required                                                                                                                                                                                                
                                                            
  ---                                                                                                                                                                                                                                       
  PARTIE 4 — LISTE DE CORRECTIONS PRIORITAIRES (ordre décroissant d'urgence)
                                                                                                                                                                                                                                            
  ┌─────┬───────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  #  │ Priorité  │                                             Action                                             │                                                                                                                      
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 1   │ Bloquante │ Renommer [34]→[18], [35]→[19] dans tout le document                                            │                                                                                                                      
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 2   │ Bloquante │ Ajouter ou citer Murphy 1973 correctement                                                      │                                                                                                                      
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 3   │ Majeure   │ Clarifier "ABM" → "stochastic ODE recruitment module (from Sego 2020 CC3D ABM)" dès l'abstract │                                                                                                                      
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 4   │ Majeure   │ Justifier le couplage cross-disease (SARS-CoV-2 module → influenza ODE) en V-A                 │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 5   │ Majeure   │ Quantifier l'effet CTL numérique (pas "within floating-point tolerance")                       │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 6   │ Majeure   │ Marquer UQ comme "architecture provision, not demonstrated" dans Table I et Table VII          │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 7   │ Modérée   │ Corriger "stochastic differential equation" → "deterministic ODE with stochastic seeding"      │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 8   │ Modérée   │ Softener "first" → "to the best of our knowledge, first" en §II-C                              │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 9   │ Modérée   │ Distinguer components implémentés vs spécifiés dans Table IV                                   │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 10  │ Modérée   │ Générer Figure 2 (trajectoires 14j) ou retirer la référence du texte                           │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 11  │ Mineure   │ Reformuler libellé ligne Table I ("Requires model source modification to adopt")               │
  ├─────┼───────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤                                                                                                                      
  │ 12  │ Mineure   │ Sourcer les valeurs précises de Table VI depuis une simulation enregistrée                     │
  └─────┴───────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘         
