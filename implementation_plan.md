# Plan d'implémentation et de restructuration — OISA

> Document de planification pour IEEE BIBM 2026
> Derniere mise a jour : 2026-04-13

---

## Diagnostic

Le papier revendique trois differenciations avec Vivarium [1] :

| Claim | Etat actuel | Impact |
|-------|------------|--------|
| 1. Signal format avec UQ integre (ci_95) | **Non implemente** — ci_95: null partout | Claim non livree |
| 2. Lags model-derived sur les edges | **Non implemente** — transfer_models[] = interface specifiee | Claim non livree |
| 3. Biological plausibility constraint engine | **Implemente** (watchdog + divergence_score) | OK |

Les claims 1 et 2 ne sont pas delivrees dans le code. Un reviewer connaissant Vivarium peut legitimement juger que la contribution est insuffisante. En parallele, l'article souffre de problemes structurels (titre trompeur, abstract trop dense, pas de liste de contributions, formalisation decrivant un systeme inexistant).

Ce plan couvre les deux axes : **implementation code** (Partie A) et **restructuration article** (Partie B).

---

## PARTIE A — Implementation des features manquantes

### A1. Runtime UQ Propagation (ci_95)

**Objectif :** Les ISSL records doivent contenir de vraies valeurs ci_95 calculees en temps reel, pas null.

**Approche :** Rolling ensemble integre a l'orchestrateur. L'orchestrateur lance N instances ABM en parallele a chaque tick et agrege les signaux avant routage.

#### A1.1 — Classe `Sego2020Ensemble` (sego2020_adapter.py)

Nouvelle classe wrapper encapsulant N instances de `Sego2020Adapter` :

```
Sego2020Ensemble
    __init__(n_instances=5, ipc_base)    # Cree N adapters dans des IPC dirs isoles
    _step(dt_s)                          # Step les N instances
    emit_issl() -> dict                  # Agrege : median + percentiles [2.5, 97.5]
    accept_issl(issl)                    # Broadcast le signal ODE a toutes les instances
    close()                              # Ferme les N sous-processus CC3D
```

Points cles :
- N instances CC3D independantes (seeds distincts, IPC dirs distincts)
- Agregation via `numpy.percentile([n_immune_1, ..., n_immune_N], [2.5, 97.5])`
- L'ISSL emis contient `"ci_95": [lo, hi]` pour chaque continuous_state
- Pas de modification de `Sego2020Adapter` existante ni de `oisa_bridge_steppable.py`

**Fichier :** `models/abm_sego2020/sego2020_adapter.py` — ajouter ~60 lignes en fin de fichier

#### A1.2 — Propagation ci_95 dans l'ODE (miao2010_adapter.py)

L'ODE est deterministe : meme entree -> meme sortie. Mais elle recoit maintenant n_immune avec un ci_95. Propagation par triple integration :

```
accept_issl(issl):
    lire n_immune_median, n_immune_lo, n_immune_hi depuis ci_95

_step_with_bounds():
    run roadrunner 3 fois : avec median, lo, hi
    stocker V_median, V_lo, V_hi

emit_issl():
    "ci_95": [V_lo, V_hi]   # au lieu de null
```

**Fichier :** `models/ode_miao2010/miao2010_adapter.py` — modifier ~40 lignes

#### A1.3 — Utiliser l'ensemble dans l'orchestrateur

**Fichier :** `models/orchestrator/orchestrator.py`

Changement minimal :
- Ligne 40 : `Sego2020Adapter(ipc_dir)` -> `Sego2020Ensemble(n_instances=5, ipc_base=ipc_dir)`
- Ajouter parametre `n_abm_instances` au constructeur
- Le reste du code est inchange (meme interface)

#### A1.4 — Adapter run_replicates.py

**Fichier :** `models/orchestrator/run_replicates.py`

- La UQ est maintenant integree a l'orchestrateur, plus besoin de boucle de replicats pour la UQ
- Garder le script pour runs multi-scenarios (variation de kappa, etc.)
- Modifier l'extraction de stats pour lire ci_95 depuis les ISSL

#### A1.5 — Tests

| Fichier | Tests a ajouter | Nb |
|---------|----------------|:--:|
| `tests/test_miao2010_adapter.py` | ci_95 non-null quand signal avec ci_95 accepte | 3-4 |
| `tests/test_sego2020_adapter.py` | Sego2020Ensemble emit ci_95, broadcast accept | 2-3 |
| `tests/test_integration.py` | Propagation ci_95 end-to-end ODE <-> ABM | 2-3 |

**Total :** ~8 nouveaux tests -> 56 tests

---

### A2. Model-Derived Transfer Lags (transfer_models[])

**Objectif :** Permettre a un modele de calculer dynamiquement le lag d'un signal, et implementer un premier transfer model concret.

#### A2.1 — Etendre le schema ISSL

Ajouter `transfer_lag_s` aux `export_signals` dans les deux adapters :

```json
{
    "signal_id": "miao2010.viral_load",
    "value": 3.29e5,
    "unit": "copies/mL",
    "transfer_lag_s": null
}
```

**Fichiers :** `miao2010_adapter.py` + `sego2020_adapter.py` — ~5 lignes chacun

#### A2.2 — Classe `SignalQueue` (orchestrator.py)

```
SignalQueue
    __init__()
    enqueue(issl, delay_s, current_s)    # Met en file un signal pour injection differee
    dequeue_ready(current_s) -> [issl]   # Retourne les signaux prets a injecter
```

Modifier la boucle `run()` :
- Avant `accept_issl()`, verifier `transfer_lag_s`
- Si non-null, enqueuer au lieu d'injecter
- A chaque tick, drainer les signaux prets

**Fichier :** `models/orchestrator/orchestrator.py` — +30 lignes (classe) + ~15 lignes (boucle)

#### A2.3 — Blood Transit Transfer Model (nouveau fichier)

Base sur `docs/model_specifications.md` section 2 (Blood Transit ODE, Donskoy & Goldschneider 1992) :

```
BloodTransitAdapter
    LAMBDA_SEED  = 0.045  day-1
    LAMBDA_CLEAR = 0.205  day-1
    STOP_FRAC    = 0.18

    accept_issl(issl)       # Lit F_export (flux de progeniteurs BM)
    emit_issl() -> dict     # Calcule F_thymic et tau = 1/(lambda_seed + lambda_clear)
                            # Emet transfer_lag_s = tau * 86400 (secondes)
```

Ce transfer model :
- Accepte un flux de progeniteurs en entree
- Calcule dynamiquement le temps de transit (`tau`) selon ses parametres cinetiques
- Emet le flux thymique avec le lag model-derived

**Nouveau fichier :** `models/transfer_blood_transit/blood_transit_adapter.py` (~80 lignes)

#### A2.4 — Integration dans la demo influenza

**Recommandation :** Ne pas modifier la demo influenza (garder `lag: "constant:0"`). Ajouter un test d'integration dedie au Blood Transit qui montre le lag dynamique. Evite de changer les resultats valides tout en prouvant la feature.

Le YAML de configuration est etendu avec un edge de demonstration :

```yaml
# Edge de demonstration (test only, pas dans la demo influenza)
- source: bm_haematopoiesis
  signal_id: bm.progenitor_export
  target: thymus_abm
  lag: "model:blood_transit"
  transfer_model: blood_transit_ode
```

#### A2.5 — Tests

| Fichier | Tests | Nb |
|---------|-------|:--:|
| `transfer_blood_transit/tests/test_blood_transit.py` (nouveau) | Steady-state, tau computation, format ISSL | 6 |
| `tests/test_integration.py` | SignalQueue delay, model-derived lag routing | 2-3 |

**Total avec A1 :** ~18 nouveaux tests -> ~66 tests

---

### A3. Resume des fichiers

#### Fichiers a creer

| Fichier | Contenu | Lignes |
|---------|---------|:------:|
| `models/transfer_blood_transit/__init__.py` | (vide) | 1 |
| `models/transfer_blood_transit/blood_transit_adapter.py` | Transfer model ODE | ~80 |
| `models/transfer_blood_transit/tests/__init__.py` | (vide) | 1 |
| `models/transfer_blood_transit/tests/test_blood_transit.py` | Tests | ~80 |

#### Fichiers a modifier

| Fichier | Modification | Delta |
|---------|-------------|:-----:|
| `models/abm_sego2020/sego2020_adapter.py` | + Sego2020Ensemble + transfer_lag_s | +70 |
| `models/ode_miao2010/miao2010_adapter.py` | + ci_95 propagation + transfer_lag_s | +50 |
| `models/orchestrator/orchestrator.py` | + SignalQueue + utiliser ensemble | +50 |
| `models/orchestrator/run_replicates.py` | Adapter aux ci_95 runtime | +20 |
| `models/ode_miao2010/tests/test_miao2010_adapter.py` | + tests ci_95 | +30 |
| `models/abm_sego2020/tests/test_sego2020_adapter.py` | + tests ensemble | +25 |
| `models/orchestrator/tests/test_integration.py` | + tests UQ e2e + transfer lag | +40 |

---

## PARTIE B — Restructuration de l'article

**Fichier cible :** `docs/OISA_paper_IEEE_BIBM2026.md`

### B1. Titre

**Actuel :**
> Simulation as a Service: A Formalism-Agnostic Orchestration Framework for Modular Immune Disease Modelling

**Propose :**
> OISA: A Formalism-Agnostic Orchestration Architecture for Composing Published Immune Models Without Modification

**Justification :** "Simulation as a Service" importe une connotation SaaS/cloud absente du papier (pas d'API REST, pas de deploiement cloud, pas de multi-tenant). Le nouveau titre met en avant la contribution reelle.

### B2. Abstract

**Probleme :** ~500 mots, 1 bloc monolithique, chiffres detailles en premiere lecture. IEEE BIBM attend ~200 mots.

**Proposition :** 2 paragraphes, ~250 mots :

**Paragraphe 1 — Probleme + Solution (~100 mots) :**
- Constat : modeles immunitaires silotes, pas de composition cross-formalism
- Gap : COMBINE = intra-formalism ; Vivarium = pas de UQ integree ni constraint engine
- Proposition : OISA = ISSL + config graph + orchestrateur avec UQ runtime et plausibility checking

**Paragraphe 2 — Validation + Resultats (~150 mots) :**
- Demo : Miao 2010 ODE + Sego 2020 CC3D, zero lignes modifiees, ~300 lignes d'adapter
- Chiffres cles : 14 jours, N=5 ensemble runtime, clearance virale, temporal lag, ci_95 propage
- Conclusion : OISA operationalise CURE au niveau multi-modele

### B3. Liste de contributions (fin de section I)

Ajouter apres le dernier paragraphe de l'Introduction :

> The contributions of this work are:
>
> 1. **The ISSL**, a formalism-agnostic checkpoint format with embedded provenance and runtime uncertainty quantification (ci_95);
> 2. **A declarative configuration graph** with support for model-derived transfer lags on edges;
> 3. **A runtime orchestrator** with global clock synchronisation, causal DAG resolution, and biological plausibility constraint enforcement;
> 4. **Empirical demonstration** that two independently published models (Miao 2010 SBML ODE + Sego 2020 CC3D spatial ABM) can be composed with zero source modifications using ~300 lines of adapter code.

### B4. Reecriture section II-A (positionnement Vivarium)

**Probleme actuel :** Le texte dit que Vivarium "ne fournit pas nativement" UQ/lags/constraints, mais ne reconnait pas ce que Vivarium fournit deja (ports, stores hierarchiques, topologies dynamiques, ecosysteme Python). La comparaison est asymetrique et fragile.

**Proposition :**

> Vivarium [1] introduced a port-based, formalism-agnostic composition interface with hierarchical stores, dynamic topology changes at runtime, and a mature Python ecosystem. OISA shares Vivarium's design principle of formalism-agnostic composition but addresses three capabilities not present in the Vivarium architecture: (i) a standardised inter-model signal format (ISSL) embedding runtime uncertainty quantification (ci_95 intervals propagated at each checkpoint), (ii) model-derived transfer lags on edges (where a lightweight transfer model computes the signal delay dynamically rather than using a fixed constant), and (iii) a biological plausibility constraint engine operating at the composition level (mass conservation, parameter bounds, and divergence monitoring across coupled models). Vivarium's store-based data sharing and dynamic topology management are complementary capabilities not replicated by OISA.

### B5. Correction section III-B point 2

**Actuel :** "The orchestrator normalises all inter-model signals to (mean, ci_95, unit) before routing, regardless of source formalism."

Ce texte decrit un systeme qui, apres implementation A1, existera reellement. Preciser le mecanisme :

> The orchestrator normalises all inter-model signals to (median, ci_95, unit) before routing: for stochastic models, ci_95 is computed from a rolling ensemble of N parallel instances (section V-A); for deterministic models, ci_95 is derived by propagating the input uncertainty bounds through the model equations (section V-A).

### B6. Table I — mise a jour

| Ligne | Avant | Apres |
|-------|-------|-------|
| Runtime UQ propagation | restricted (note de bas) | check (implemente) |
| Model-derived transfer lag | check (mais non demontre) | check (demontre via BloodTransitAdapter) |

Supprimer la note "specified but not implemented" et la remplacer par :
> UQ runtime implemented via rolling ensemble (N = 5 CC3D instances, section V-A). Model-derived lag demonstrated with BloodTransitAdapter (section V-A).

Corriger egalement le placement de la note (actuellement entre deux rangees du tableau, ce qui casse le rendu Markdown).

### B7. Section V-A — ajouter paragraphe UQ

Nouveau paragraphe dans la section Validation Setup :

> **Runtime UQ.** The ABM component runs as an ensemble of N = 5 parallel CC3D instances (distinct MersenneTwister seeds, isolated IPC directories). At each 24 h GSimT boundary, the ensemble adapter aggregates n_immune across instances and computes median and 95% empirical percentile bounds (ci_95). The ODE adapter receives the median n_immune for its central trajectory and the ci_95 bounds; it performs three roadrunner integrations per tick (at median, ci_95_lo, and ci_95_hi input values) and reports the resulting viral load bounds in its ISSL record. This constitutes runtime UQ propagation: uncertainty originates in the stochastic ABM and is carried through the ODE at each checkpoint, not computed post-hoc.

### B8. Section V-B.4 — mettre a jour les resultats

Completer la table de trajectoire avec une colonne ci_95 (vraies valeurs au lieu de null).
Mettre a jour les Box 1 et Box 2 (exemples ISSL) pour montrer ci_95 non-null.

### B9. Section VI-B — Limitations

- **Supprimer** le caveat "ci_95: null throughout" (ce n'est plus vrai apres A1)
- **Garder** le caveat N=5 (taille d'ensemble petite) — recommander N >= 20
- **Ajouter** un paragraphe sur le cout computationnel de l'ensemble (5x plus lent pour l'ABM)
- **Garder** les paragraphes epithelial depletion, scale mismatch, IPC (deja ajoutes)

### B10. Conclusion

Remplacer "CURE extensibility and automation requirements" par mention explicite des trois contributions delivrees :
- UQ runtime propagation (ci_95 dans tous les ISSL records)
- Model-derived transfer lags (demontre avec BloodTransitAdapter)
- Constraint engine + composition sans modification

---

## PARTIE C — Ordre d'execution global

### Phase 1 : Implementation code

| Etape | Action | Fichier(s) | Priorite |
|:-----:|--------|-----------|:--------:|
| 1 | A2.1 — Ajouter transfer_lag_s au schema ISSL | miao2010_adapter, sego2020_adapter | Haute |
| 2 | A2.2 — Creer SignalQueue | orchestrator.py | Haute |
| 3 | A2.3 — Creer BloodTransitAdapter | nouveau fichier | Haute |
| 4 | A2.5 — Tests transfer model | nouveau fichier | Haute |
| 5 | A1.1 — Creer Sego2020Ensemble | sego2020_adapter.py | Haute |
| 6 | A1.2 — Propagation ci_95 dans ODE | miao2010_adapter.py | Haute |
| 7 | A1.3 — Utiliser ensemble dans orchestrateur | orchestrator.py | Haute |
| 8 | A1.5 — Tests UQ | 3 fichiers de tests | Haute |
| 9 | Run complet — relancer demo 14 jours avec ensemble | - | Haute |

### Phase 2 : Restructuration article

| Etape | Action | Section |
|:-----:|--------|---------|
| 10 | B1 — Changer le titre | Header |
| 11 | B2 — Reecrire l'abstract (2 paragraphes, ~250 mots) | Abstract |
| 12 | B3 — Ajouter liste de contributions | Section I |
| 13 | B4 — Reecrire positionnement Vivarium | Section II-A |
| 14 | B5 — Corriger formalisation UQ | Section III-B |
| 15 | B6 — Mettre a jour Table I | Section II-B |
| 16 | B7 — Ajouter paragraphe UQ dans setup | Section V-A |
| 17 | B8 — Mettre a jour resultats avec ci_95 | Section V-B.4 |
| 18 | B9 — Mettre a jour limitations | Section VI-B |
| 19 | B10 — Mettre a jour conclusion | Section VII |

### Phase 3 : Verification

| Etape | Action |
|:-----:|--------|
| 20 | Lancer pytest — ~66 tests attendus, tous verts |
| 21 | Verifier que les ISSL records contiennent ci_95 non-null |
| 22 | Verifier que BloodTransitAdapter emet transfer_lag_s |
| 23 | Relecture complete du papier pour coherence interne |
