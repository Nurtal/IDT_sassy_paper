Here is Claude's plan:                                                                                                                                                                                     
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan d'implémentation : Modèles publiés + emit() OISA-compliant                                                                                                                                            
                                                                                                                                                                                                          
 Context

 Le papier IDT/OISA (docs/OISA_paper_IEEE_BIBM2026.md) définit OISA comme une architecture d'orchestration où tout modèle implémentant Emit() et Accept() est OISA-compliant "without other modification".
 Le cas de validation actuel utilise une pipeline hématopoïèse custom (BM ODE → Thymus ABM → PLN ODE).

 Objectif de ce plan : Ajouter un second use case utilisant des modèles PUBLIÉS ET EXISTANTS (ODE + ABM) auxquels on ajoute uniquement emit() et accept(), démontrant que l'interopérabilité OISA ne
 nécessite pas de réécrire les modèles — juste d'implémenter l'interface ISSL.

 Paire choisie :
 - ODE : Miao et al. 2010, BIOMD0000000546 (SBML) — influenza systémique (CTL, IgG, IgM)
 - ABM : Sego et al. 2020 — tissu épithélial viral (CompuCell3D), GitHub covid-tissue-models

 Message clé renforcé : "Two independently published models — one ODE, one ABM — become interoperable by adding only the Emit()/Accept() interface, requiring zero changes to their internal dynamics."

 ---
 Architecture de couplage biologique

 ABM (Sego2020 — epithelial tissue, CompuCell3D)
     Local viral load V_tissue(t)   →  [emit() → ISSL → accept()]
     Local IFN signal IFN_tissue(t) →  ODE (Miao2010 — systemic)
                                         ↓ CTL(t), Ab(t) [emit() → ISSL]
                                     → [accept()] ABM: immune cell recruitment rate

 Variables couplées (inter-model signals dans ISSL) :

 ┌─────────────────────────┬────────────────┬───────────────┬────────────────────────────────┐
 │         Signal          │ Source → Cible │  Unité ISSL   │         Transformation         │
 ├─────────────────────────┼────────────────┼───────────────┼────────────────────────────────┤
 │ viral_shedding_flux     │ ABM → ODE      │ copies/mL/day │ flux_raw × scale_factor        │
 ├─────────────────────────┼────────────────┼───────────────┼────────────────────────────────┤
 │ ifn_concentration       │ ABM → ODE      │ IU/mL         │ spatial average                │
 ├─────────────────────────┼────────────────┼───────────────┼────────────────────────────────┤
 │ ctl_recruitment_rate    │ ODE → ABM      │ cells/day     │ distribué aux agents ABM       │
 ├─────────────────────────┼────────────────┼───────────────┼────────────────────────────────┤
 │ antibody_neutralization │ ODE → ABM      │ AU/mL         │ modifie p_infection des agents │
 └─────────────────────────┴────────────────┴───────────────┴────────────────────────────────┘

 ---
 Fichiers à créer

 IDT_sassy_paper/
 ├── models/
 │   ├── ode_miao2010/
 │   │   ├── miao2010.xml          # SBML téléchargé depuis BioModels
 │   │   ├── ode_model.py          # Wrapper Python avec emit() et accept()
 │   │   └── issl_schema.json      # Schéma ISSL pour ce modèle
 │   ├── abm_viral_tissue/
 │   │   ├── abm_model.py          # ABM simplifié (mesa ou custom) avec emit/accept
 │   │   └── issl_schema.json
 │   └── orchestrator/
 │       ├── orchestrator.py       # Moteur OISA minimal
 │       ├── config.yaml           # Configuration graph (nodes + edges)
 │       └── run_demo.py           # Script de démonstration
 └── results/
     └── issl_checkpoints/         # Fichiers ISSL générés à chaque GSimT tick

 ---
 Étapes d'implémentation

 Étape 1 — Setup environnement Python

 source venv/bin/activate
 pip install libroadrunner mesa scipy numpy jsonschema pyyaml

 - libroadrunner : exécution native du SBML (BIOMD0000000546)
 - mesa : framework Python ABM pour le modèle viral tissue simplifié

 Étape 2 — ODE Model : Wrapper Miao2010

 Fichier : models/ode_miao2010/ode_model.py

 Fonctionnement :
 1. Charger miao2010.xml (SBML) via roadrunner.RoadRunner(path)
 2. step(dt) : avancer la simulation de dt jours
 3. emit() : lire l'état interne et produire l'ISSL JSON-LD
 4. accept(issl) : extraire viral_shedding_flux et ifn_concentration depuis le signal ISSL entrant, les injecter comme paramètres/forcing du modèle SBML

 Structure de l'ISSL émis par l'ODE :
 {
   "envelope": {"model_id": "miao2010_ode", "GSimT": "T+6h", "scale_factor": 1},
   "continuous_state": {
     "CTL": {"value": 1234.5, "unit": "cells/mL", "ci_95": [900, 1600]},
     "IgG": {"value": 0.45, "unit": "AU/mL", "ci_95": [0.3, 0.6]}
   },
   "export_signals": {
     "ctl_recruitment_rate": {"biological_flux_per_day": 500, "unit": "cells/day"},
     "antibody_neutralization": {"value": 0.45, "unit": "AU/mL"}
   },
   "watchdog": {"status": "OK", "divergence_score": 0.03}
 }

 Étape 3 — ABM Model : Viral Tissue (mesa simplifié)

 Fichier : models/abm_viral_tissue/abm_model.py

 Agents : cellules épithéliales (saines / infectées / mortes), cellules immunes innées
 Règles :
 - Propagation virale : cellule infectée → infecte voisins avec probabilité p_infection
 - p_infection modifié par antibody_neutralization reçu via accept()
 - Cellules immunes recrutées selon ctl_recruitment_rate reçu via accept()
 - scale_factor dans l'envelope ISSL : N_agents × scale_factor = cellules réelles

 emit() produit :
 {
   "envelope": {"model_id": "sego_viral_tissue_abm", "agent_count": 500, "scale_factor": 20000},
   "continuous_state": {
     "epithelial_healthy": {"value": 350, "unit": "agents"},
     "epithelial_infected": {"value": 120, "unit": "agents"}
   },
   "export_signals": {
     "viral_shedding_flux": {"biological_flux_per_day": 2.4e8, "unit": "copies/mL/day"},
     "ifn_concentration": {"value": 12.5, "unit": "IU/mL"}
   },
   "watchdog": {"status": "OK", "divergence_score": 0.07}
 }

 Étape 4 — Orchestrateur OISA minimal

 Fichier : models/orchestrator/orchestrator.py

 Algorithme :
 GSimT = 0
 Δt_ODE = 6h, Δt_ABM = 24h, GSimT_step = 6h (GCD)

 while GSimT < T_final:
     # Causal ordering: ABM → ODE → ABM
     if GSimT % Δt_ABM == 0:
         abm.step(Δt_ABM)
         issl_abm = abm.emit()
         ode.accept(issl_abm)          # inject viral_shedding_flux, IFN

     ode.step(Δt_ODE)
     issl_ode = ode.emit()
     abm.accept(issl_ode)              # inject ctl_recruitment_rate, Ab

     save_checkpoint(GSimT, issl_abm, issl_ode)
     GSimT += GSimT_step

 Config YAML :
 models:
   - id: miao2010_ode
     type: ODE
     sbml: models/ode_miao2010/miao2010.xml
     dt: 6h
   - id: sego_viral_tissue_abm
     type: ABM
     module: models.abm_viral_tissue.abm_model
     dt: 24h
     agents: 500
     scale_factor: 20000

 edges:
   - from: sego_viral_tissue_abm
     to: miao2010_ode
     signals: [viral_shedding_flux, ifn_concentration]
   - from: miao2010_ode
     to: sego_viral_tissue_abm
     signals: [ctl_recruitment_rate, antibody_neutralization]

 Étape 5 — Script de démonstration

 Fichier : models/orchestrator/run_demo.py

 - Lancer simulation 14 jours (infection aiguë influenza)
 - Générer 56 checkpoints ISSL (14 jours × 4 ticks/jour)
 - Produire figures : viral load (ABM) + CTL/Ab (ODE) sur même axe temporel
 - Vérifier : pas de violation causale, divergence_score < 0.15 à chaque tick

 ---
 Résultats attendus pour le papier

 1. Table "OISA compliance" : Miao2010 ODE + Sego ABM → 2 fonctions ajoutées (emit/accept), 0 ligne interne modifiée
 2. Figure couplage : viral load tissue (ABM) corrélée avec CTL systémique (ODE) sur 14 jours
 3. 56 checkpoints ISSL générés sans deadlock ni violation causale
 4. Message fort : modèles publiés indépendamment → interopérables via OISA sans réécriture

 ---
 Fichiers critiques existants

 - docs/OISA_paper_IEEE_BIBM2026.md — papier principal (à mettre à jour avec ce use case)
 - docs/model_specifications.md — specs mathématiques (référence pour les équations ODE)
 - smbl_qual.md — comparaison OISA vs SBML (contexte du message interopérabilité)

 ---
 Vérification end-to-end

 source venv/bin/activate
 cd models/orchestrator
 python run_demo.py --days 14 --output ../../results/issl_checkpoints/
 # Vérifier : 56 fichiers ISSL générés
 # Vérifier : figures viral_load.png et ctl_ab.png produites
 # Vérifier : aucun message WARN/PAUSE dans les watchdog

