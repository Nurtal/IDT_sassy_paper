---
  OISA vs. SBML Qualitative Models — Différences clés

  1. Nature fondamentale

  ┌───────────┬───────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────┐
  │ Dimension │                             SBML qual                             │                                OISA                                 │
  ├───────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ Quoi ?    │ Format d'échange de modèles (XML)                                 │ Architecture d'orchestration à l'exécution                          │
  ├───────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ Rôle      │ Représenter un modèle unique dans un format portable              │ Coordonner plusieurs modèles hétérogènes qui tournent simultanément │
  ├───────────┼───────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ Runtime ? │ Non — les outils lisent/écrivent le fichier, exécutent séparément │ Oui — orchestrateur actif avec horloge globale (GSimT)              │
  └───────────┴───────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘

  2. Formalisme

  SBML qual est conçu exclusivement pour les modèles qualitatifs : réseaux de régulation Booléens ou multi-valués (Thomas formalism, logical regulatory graphs). Les espèces prennent des valeurs discrètes
  (0/1 ou 0/1/2…), les transitions sont des règles logiques.

  OISA est explicitement formalism-agnostic : ODE, ABM, hybrides, surrogates neuronaux. Le papier choisit justement l'ODE + ABM parce que ce sont des formalisms incommensurables — là où SBML qual reste
  dans un seul paradigme.

  3. Composition : intra vs. inter-formalisme

  C'est la divergence centrale.

  - SBML qual : interopérabilité intra-formalisme — plusieurs outils (GINsim, BoolNet, CellNetAnalyzer) peuvent lire le même modèle. Mais le modèle doit être réécrit dans le format XML SBML qual.
  Inapplicable à un ABM Python ou à un ODE Julia.
  - OISA : interopérabilité inter-formalisme — les modèles ne sont pas réécrits, ils implémentent seulement Emit() / Accept(). Un ABM thymique à 300 agents et un ODE haematopoïétique communiquent via ISSL
   sans rien savoir l'un de l'autre.

  4. Gestion du temps

  - SBML qual : les modèles logiques sont souvent event-driven ou synchrones discrets, sans notion de pas de temps hétérogènes. La gestion temporelle est déléguée aux outils.
  - OISA : problème de coordination temporelle hétérogène explicitement résolu — le BM ODE tourne à Δt = 6 h, le thymus ABM à Δt = 24 h, le GSimT est le GCD (6 h). Lags de transfert calculés dynamiquement
   (modèle blood transit).

  5. Incertitude (UQ)

  - SBML qual : pas de notion d'incertitude — les variables sont discrètes, pas de distributions.
  - OISA/ISSL : chaque signal inter-modèles transporte (mean, ci_95, unit). Les sorties stochastiques de l'ABM sont normalisées en distributions avant routage vers les ODEs. La propagation d'incertitude
  est une primitive de l'architecture.

  6. Quantitatif vs. qualitatif

  - SBML qual : fondamentalement qualitatif — activé / inhibé, haut / bas. Idéal pour explorer la logique d'un réseau de régulation (attracteurs, états stables) sans paramètres cinétiques.
  - OISA : fondamentalement quantitatif — flux en cellules·jour⁻¹, pools en nombre de cellules, paramètres cinétiques avec postérieurs. Nécessaire pour un digital twin qui doit prédire des quantités
  mesurables.

  7. Ce qu'ils partagent (peu de choses)

  - Les deux ciblent l'interopérabilité entre outils/modèles en biologie des systèmes.
  - Les deux utilisent des annotations ontologiques (OBO/MIRIAM dans SBML qual, OBO URIs dans ISSL).
  - Les deux s'appuient sur des formats lisibles par machine (XML vs. JSON-LD).

  ---
  En résumé

  SBML qual répond à la question : "Comment partager un modèle logique entre outils qualitatifs ?"
  OISA répond à la question : "Comment faire tourner ensemble des modèles ODEs et ABMs sans les réécrire, avec synchronisation temporelle et propagation d'incertitude ?"

  Les deux sont complémentaires plutôt que concurrents — un modèle Boolean de régulation génique (représentable en SBML qual) pourrait en théorie devenir un nœud OISA-compliant s'il implémente Emit() /   
  Accept(), et ses sorties booléennes seraient normalisées en distributions par l'orchestrateur avant routage.

