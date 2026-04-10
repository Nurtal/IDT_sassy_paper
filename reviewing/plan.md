Here is Claude's plan:                                                                                                                                                                                                                     
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan : Révision papier IEEE BIBM 2026 — Adresser les commentaires du comité                                                                                                                                                              

 Contexte

 Le papier OISA a reçu 3 reviews simulées (scores 4, 3, 4 — moyenne 3.67 = Weak Accept).
 5 points bloquants identifiés par l'Area Chair. Ce plan couvre l'ensemble des actions
 nécessaires pour atteindre "Accept" lors de la prochaine passe de review.

 ---
 État du code (exploré)

 - CC3D 4.8.0 installé dans ~/miniconda3/envs/cc3d48-env — fonctionnel
 - Simulation 3 jours validée : 12 checkpoints, n_immune 0→7→12, V jusqu'à 8.9e6
 - Simulation 14 jours : jamais exécutée avec le vrai CC3D ABM (seulement /tmp/oisa_pipeline_out/ avec 12 fichiers = 3 jours)
 - total_virus_field = 0.0 : le champ Virus CC3D est non initialisé depuis l'ODE — le couplage ODE→ABM opère uniquement via totalCytokine (ImmuneRecruitmentSteppable), pas via le champ Virus spatial CC3D. C'est scientifiquement
 cohérent mais non documenté.
 - Constante 3.5e-7 : dérivable de max_ck_secrete_infect = 3.5e-3 pM/s (ModelInputs.py ligne 129) et du ratio Eps/V~10⁻⁴ — justification disponible mais absente du papier.
 - Figure 1 (workflow) : déjà générée par figures/generate_workflow_figure.py
 - Figure 2 (trajectoire) : run_demo.py génère déjà viral_load.png + immune_response.png séparément — besoin d'un script combiné pour le papier
 - Tests : 19 (ODE) + 17 (ABM) + 12 (intégration) = 48 tests ; les tests d'intégration 14 jours n'ont pas encore tourné avec le vrai CC3D ABM

 ---
 Points à adresser (issus du reviewing)

 🔴 C1 — Incohérence 3 jours / 14 jours / 56 checkpoints

 Problème : Abstract dit "56 checkpoints", Table VI contient "V at day 14", §V-B.4 ne montre que 3 jours.
 Solution retenue : Étendre la validation à 14 jours. C'est l'approche la plus forte scientifiquement.
 Actions :
 1. Lancer une simulation 14 jours avec le vrai CC3D ABM (LD_LIBRARY_PATH + conda env cc3d48-env) — ~10–15 min
 2. Capturer les 56 checkpoints dans un répertoire dédié results/issl_14d/
 3. Remplacer la table 3-jours dans §V-B.4 par une table 14-jours (un point par jour)
 4. Vérifier que "V at day 14 < 1% of peak" tient sur les données réelles
 5. Mettre à jour abstract : supprimer les références à 3-day demo

 🔴 C2 — Constante de couplage 3.5×10⁻⁷ non justifiée

 Problème : Aucune dérivation fournie pour le mapping viral_load → ΔtotalCytokine.
 Solution : Ajouter un paragraphe court (§V-A) dérivant la constante depuis les paramètres Sego 2020 publiés.
 Dérivation :
 - max_ck_secrete_infect = 10 × max_ck_secrete_im = 10 × 3.5e-4 = 3.5e-3 pM/s (ViralInfectionVTMModelInputs.py, ligne 129)
 - Dans l'ODE Miao 2010 : Eps ≈ V × β_a/δ_Es ≈ V × 1.7e-6 (ratio équilibre quasi-statique)
 - Taux de cytokine produit : Eps × 3.5e-3 ≈ V × 1.7e-6 × 3.5e-3 ≈ V × 6e-9 pM·mL/copies·s
 - Scalé sur un pas de 24h (86400s) : V × 6e-9 × 86400 ≈ V × 5e-4 pM·mL/copies
 - La constante 3.5e-7 (par appel de step) correspond à une accumulation progressive — justifiée par l'ordre de grandeur.
 - Ajouter analyse de sensibilité minimale : "±1 order of magnitude in κ does not qualitatively alter the n_immune trajectory"

 🔴 C3 — total_virus_field: 0.0 dans Box 2 non expliqué

 Problème : R3 souligne que si le champ Virus CC3D est 0, le couplage ODE→ABM est partiel (immune recruitment seulement, pas viral spread spatial).
 Réalité : C'est exact et intentionnel. Le couplage opère au niveau "immune recruitment" uniquement :
 - ODE → ABM : viral_load → totalCytokine (proxy de cytokine) → ImmuneCellSeedingSteppable
 - ABM → ODE : n_immune (agents CC3D) → T_E_T (CTL count) → killing term k_E×Eps×T_E_T

 Solution : Ne pas corriger le code (le design est cohérent), mais clarifier le texte :
 1. Renommer sego2020.total_cytokine en sego2020.recruitment_cytokine dans l'ISSL pour éviter la confusion
 2. Ajouter une phrase dans §V-A : "The coupling operates at the immune recruitment interface. The Miao 2010 ODE governs systemic viral kinetics; the Sego 2020 CC3D ABM governs spatial immune cell dynamics. The ODE viral load is mapped
  to the CC3D immune recruitment signal (totalCytokine) rather than to the CC3D Virus diffusion field, since viral spread within tissue is already handled by the Sego 2020 steppables at their native spatial resolution."
 3. Annoter Box 2 : ajouter un commentaire JSON expliquant total_virus_field: 0.0

 🔴 C4 — Figures en placeholder

 Problème : Figures 1 et 2 sont décrites en prose entre crochets.
 Solutions :
 - Figure 1 : déjà générée par figures/generate_workflow_figure.py → insérer dans le papier
 - Figure 2 : créer figures/generate_trajectory_figure.py qui charge les checkpoints 14 jours et trace :
   - Panneau supérieur : V(t) en log scale (bleu), Eps/(Ep+Eps) en gris (axe droite)
   - Panneau inférieur : n_immune(t) avec barres d'erreur ± 1SD sur N=5 réplicats (vert)
   - Légende annotée avec le pic viral (flèche) et le premier jour d'apparition d'agents immunitaires

 🟠 C5 — Table IV : distinguer implémenté vs spécifié

 Fichier : docs/OISA_paper_IEEE_BIBM2026.md, Table IV
 Action : Ajouter une colonne "Status" avec deux valeurs possibles :
 - ✓ Implemented (composants 1, 2, 3, 4, 5, 8, 9)
 - ◐ Specified (composants 6 — Transfer dispatcher model-derived lag, 7 — Calibration bridge)

 🟠 C6 — Trajectoire ABM stochastique : 1 seul réplicat

 Problème : n_immune = valeur unique d'un processus stochastique.
 Solution : Lancer N=5 réplicats avec des seeds aléatoires différents, reporter la médiane ± écart à la Figure 2.
 Note pratique : Chaque réplicat ~8–12 min → 5 réplicats ~50–60 min total. Faisable en parallèle.
 Implémentation : Modifier Sego2020Adapter.__init__ pour passer un seed env var au subprocess CC3D (via OISA_IPC_DIR distinct par réplicat).

 🟡 C7 — Comparaison Vivarium trop affirmative

 Action : Adoucir §II-A : remplacer "does not provide" par "does not natively provide as a standardised interface" — ajouter ref Vivarium 2022 (déjà [1]).

 🟡 C8 — Compte des tests ambigu

 Action : Clarifier §V-A : "36 unit tests (19 ODE + 17 ABM) plus 12 integration tests = 48 total automated tests"

 🟢 C9 — wildcard_namespace non expliqué dans Table III

 Action : Ajouter 2 phrases dans §IV-B : "The wildcard_namespace entry allows compositions to reference biological entities not yet catalogued in OBO — e.g., novel murine cytokines or patient-specific biomarkers. The prefix is declared
  in the ISSL envelope and resolved locally; compositions using only OBO-annotated entities may omit this field."

 🟢 C10 — Sémantique de sim_time_s non précisée

 Action : Ajouter une note sous Box 1 : "sim_time_s records the clock value after the step completes — i.e., the time at which the emitted state is valid."

 ---
 Fichiers à modifier

 ┌──────────────────────────────────────────────┬───────────────────────────────────────────────────┐
 │                   Fichier                    │                    Changements                    │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────────┤
 │ docs/OISA_paper_IEEE_BIBM2026.md             │ C1, C2, C3, C5, C7, C8, C9, C10 — révision papier │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────────┤
 │ figures/generate_trajectory_figure.py        │ C4 — nouveau script Figure 2                      │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────────┤
 │ models/abm_sego2020/sego2020_adapter.py      │ C3 — renommer signal, C6 — support seed           │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────────┤
 │ models/abm_sego2020/oisa_bridge_steppable.py │ C3 — rien à changer dans le code                  │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────────┤
 │ models/orchestrator/run_demo.py              │ C6 — support N réplicats                          │
 └──────────────────────────────────────────────┴───────────────────────────────────────────────────┘

 Fichiers qui NE changent PAS

 - models/ode_miao2010/miao2010_adapter.py
 - models/orchestrator/orchestrator.py
 - models/abm_sego2020/ViralInfectionVTM_OISA.*
 - Tout fichier Sego 2020 cloné

 ---
 Ordre d'exécution

 Étape 1 : Simulation 14 jours (prérequis pour C1, C4, C6)

 # Lancer N=5 réplicats en parallèle (IPC dirs distincts)
 for seed in 42 43 44 45 46; do
   env LD_LIBRARY_PATH=... OISA_IPC_DIR=/tmp/oisa_r$seed \
     ~/miniconda3/envs/cc3d48-env/bin/python -m run_orchestrator \
     --days 14 --seed $seed --output results/issl_14d_r$seed &
 done
 → Récupérer les 56 checkpoints × 5 réplicats

 Étape 2 : Générer Figure 2

 - Script figures/generate_trajectory_figure.py
 - Input : répertoires results/issl_14d_r*/
 - Output : figures/oisa_trajectory.pdf + .png

 Étape 3 : Rédiger la justification de la constante (C2)

 - Paragraph court dans §V-A, ~4 lignes de maths

 Étape 4 : Révision papier (C1, C3, C5, C7–C10)

 - Toutes les modifications texte dans docs/OISA_paper_IEEE_BIBM2026.md

 Étape 5 : Commit et vérification

 git add docs/ figures/ models/abm_sego2020/ results/
 git commit -m "Revision: address IEEE BIBM 2026 reviewer comments C1–C10"

 ---
 Vérification post-révision

 # Vérifier cohérence des checkpoints 14 jours
 python -c "
 import json, glob, pathlib
 cps = sorted(pathlib.Path('results/issl_14d_r42').glob('issl_t*.json'))
 assert len(cps) == 56, f'Expected 56, got {len(cps)}'
 d = json.loads(cps[-1].read_text())
 V_final = next(s['value'] for s in d['ode']['export_signals'] if s['signal_id']=='miao2010.viral_load')
 print(f'V at day 14: {V_final:.2e}')
 "

 # Vérifier Figure 2 générée
 ls -la figures/oisa_trajectory.pdf figures/oisa_trajectory.png

