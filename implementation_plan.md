# Plan d'implémentation : Modèles publiés OISA-compliant dans SASSy

## Contexte

Le dépôt SASSy (`~/workspace/SASSy`) est le codebase de simulation OISA existant.
Il contient déjà 4 modèles (BM ODE → Blood transit → Thymus ABM → PLN ODE) avec
une infrastructure complète : `ModelBase`, ISSL schema, orchestrateur ZMQ, configs YAML.

**Objectif :** Ajouter un second use case (paire Miao2010 ODE + Viral Tissue ABM) en
suivant exactement les patterns existants. Démonstration : ajouter uniquement
`_step()` + `emit_issl()` rend n'importe quel modèle OISA-compliant.

**La méthode `emit_issl()` = l'`emit()` du papier.** L'orchestrateur ZMQ
envoie `{"cmd": "emit", "sim_time_s": t}` → le modèle retourne l'ISSL validé.

---

## Paire de modèles choisie

| | ODE | ABM |
|---|---|---|
| **Modèle** | Miao et al. 2010 | Sego et al. 2020 (simplifié) |
| **Référence** | BIOMD0000000546 | CompuCell3D covid-tissue-models |
| **Δt** | 21 600 s (6 h) | 86 400 s (24 h) |
| **Port ZMQ** | 5014 | 5015 |
| **Biologie** | Cinétique virale systémique (CTL, IgG, IgM) | Tissu épithélial : infection cellule-par-cellule |

**Couplage :**
```
viral_tissue_abm   ──viral_shedding_flux──►  miao_influenza_ode
miao_influenza_ode ──ctl_recruitment_rate──► viral_tissue_abm
```

---

## Fichiers à créer (dans `~/workspace/SASSy`)

```
models/
├── miao_influenza_ode/
│   ├── __init__.py
│   ├── model.py           # ODE subclass de ModelBase
│   ├── parameters.yaml    # paramètres Miao2010 avec ci_95 + source
│   └── tests/
│       ├── __init__.py
│       └── test_miao.py   # 3 tests minimum (step, emit, biologique)
└── viral_tissue_abm/
    ├── __init__.py
    ├── model.py           # ABM subclass de ModelBase (pattern thymus)
    ├── parameters.yaml
    └── tests/
        ├── __init__.py
        └── test_viral.py

configs/
└── run_VIRALCOMP1_miao_tissue.yaml   # config graph ODE + ABM, 14 jours
```

---

## Étape 1 — `miao_influenza_ode/parameters.yaml`

Format identique à `bm_haematopoiesis/parameters.yaml`.
State variables du modèle ODE Miao2010 (5 compartiments) :

| Variable | Signification | CI (initiale) | Unité |
|---|---|---|---|
| V | Titer viral | 0.001 | TCID50/mL |
| E | Effecteurs CTL CD8+ | 0.0 | 10^5 cells/mL |
| A_G | Anticorps IgG | 0.0 | AU/mL |
| A_M | Anticorps IgM | 0.0 | AU/mL |
| T | Cellules cibles (épithéliales) | 7.5 | 10^6 cells |

Paramètres clés (Miao et al. 2010, J Theor Biol 264:179, Table 2, BIOMD0000000546)
avec `value`, `unit`, `ci_95`, `source` pour chaque entrée.

---

## Étape 2 — `miao_influenza_ode/model.py`

Subclasse `ModelBase`, même pattern que `BMHaematopoiesis` :

```python
class MiaoInfluenzaODE(ModelBase):
    MODEL_ID      = "miao_influenza_ode"
    MODEL_VERSION = "1"
    DELTA_T_S     = 21_600.0   # 6 h

    def _step(self, sim_time_s: float, signals: list[dict]) -> None:
        # 1. Parser viral_shedding_flux depuis signals (émis par l'ABM)
        #    → injecter comme forcing dans dV/dt
        # 2. solve_ivp(self._ode, ...) — même pattern que BMHaematopoiesis._step()

    def emit_issl(self, sim_time_s: float) -> dict:
        # Retourner dict conforme à schemas/issl_v1.schema.json
        # export_signals[0] :
        #   signal_id : "miao_influenza_ode.ctl_recruitment_rate"
        #   entity_id : "CL:0000910"   # CD8+ effector T cell (OBO)
        #   flux      : E(t) × conversion_factor   # cells/day
        #   unit      : "cells·day^-1"
        # export_signals[1] :
        #   signal_id : "miao_influenza_ode.antibody_level"
        #   entity_id : "GO:0003823"
        #   flux      : A_G(t) + A_M(t)
        #   unit      : "AU/mL"
```

Watchdog : `ood_flag = True` si V > 10^8 ou E < 0.

---

## Étape 3 — `viral_tissue_abm/model.py`

Pattern identique à `thymus_selection/model.py` (N réalisations, CI-95 empirique).

**Agents :** `EpithelialCell` avec états `healthy | infected | dead`

**Règles par sous-step :**
- Cellule saine → infectée avec prob `β × V_local`
- `V_local` augmente de `p × n_infected` par step (shedding viral)
- Cellule infectée → morte après `τ_inf` steps
- CTL agents recrutés selon `ctl_recruitment_rate` reçu via signals
- CTL tue une cellule infectée voisine avec prob `k_ctl`

**Scaling :** `scale_factor = 20 000` (500 agents → 10^7 cellules pulmonaires)

```python
class ViralTissueABM(ModelBase):
    MODEL_ID      = "viral_tissue_abm"
    MODEL_VERSION = "1"
    DELTA_T_S     = 86_400.0   # 24 h

    def _step(self, sim_time_s: float, signals: list[dict]) -> None:
        # Parser ctl_recruitment_rate et antibody_level depuis signals
        # Lancer N réalisations × substep_h sous-steps
        # Stocker résultats moyens + ci_95 empirique

    def emit_issl(self, sim_time_s: float) -> dict:
        # export_signals[0] :
        #   signal_id            : "viral_tissue_abm.viral_shedding_flux"
        #   entity_id            : "NCBITaxon:11520"   # Influenza A virus
        #   flux                 : V_tissue_mean × scale_factor
        #   unit                 : "copies·mL^-1·day^-1"
        #   scaling_factor       : 20000
        #   biological_flux_per_day : (idem flux)
```

---

## Étape 4 — `configs/run_VIRALCOMP1_miao_tissue.yaml`

```yaml
oisa_version: "1.0"

models:
  - id: miao_influenza_ode
    formalism: ODE
    executable: models/miao_influenza_ode/model.py
    issl_port: "tcp://localhost:5014"
    delta_t_s: 21600

  - id: viral_tissue_abm
    formalism: ABM
    executable: models/viral_tissue_abm/model.py
    issl_port: "tcp://localhost:5015"
    delta_t_s: 86400

edges:
  - source: viral_tissue_abm
    signal_id: viral_tissue_abm.viral_shedding_flux
    target: miao_influenza_ode
    lag: "constant:0"
    activation_threshold: 0.0

  - source: miao_influenza_ode
    signal_id: miao_influenza_ode.ctl_recruitment_rate
    target: viral_tissue_abm
    lag: "constant:0"
    activation_threshold: 0.0

global_clock:
  start_s: 0
  end_s: 1209600          # 14 jours (infection aiguë influenza)
  checkpoint_interval_s: 86400

renderer:
  format: "OISA-render-v1"
  target: "file:logs/VIRALCOMP1/render_stream.ndjson"
  emit_interval_s: 86400
  scene_schema_uri: "schemas/scene_schemas/immune_ontogeny_v1.json"
```

---

## Étape 5 — Tests

Pattern : `models/bm_haematopoiesis/tests/test_bm.py`

**3 tests minimum par modèle :**

1. `test_step_no_crash` — step sans signals → état non-négatif
2. `test_emit_issl_validates` — ISSL retourné valide contre `schemas/issl_v1.schema.json`
3. Assertion biologique :
   - ODE : après 7 jours, `E(t) > E(0)` (expansion CTL attendue)
   - ABM : après 5 jours avec `V_initial > 0`, `n_infected > 0`

---

## Fichiers de référence SASSy à suivre

| Fichier existant | Sert de template pour |
|---|---|
| `models/_base/model_base.py` | Base class, méthodes abstraites, ZMQ loop |
| `models/bm_haematopoiesis/model.py` | Pattern ODE (`solve_ivp`, `emit_issl`, watchdog) |
| `models/thymus_selection/model.py` | Pattern ABM (réalisations, `scaling_factor`, `discrete_events`) |
| `models/bm_haematopoiesis/parameters.yaml` | Format YAML (`value`, `unit`, `ci_95`, `source`) |
| `configs/run_COMP3_full_graph.yaml` | Format config YAML (`models`, `edges`, `global_clock`) |
| `schemas/issl_v1.schema.json` | Schéma ISSL exact à respecter |

---

## Vérification end-to-end

```bash
cd ~/workspace/SASSy

# Tests unitaires
pytest models/miao_influenza_ode/tests/ -v
pytest models/viral_tissue_abm/tests/ -v

# Simulation couplée 14 jours
python orchestrator/main.py --config configs/run_VIRALCOMP1_miao_tissue.yaml

# Résultats attendus :
# - logs/VIRALCOMP1/render_stream.ndjson : 14 lignes NDJSON
# - Aucun watchdog health_status "failed"
# - viral_shedding_flux peak autour du jour 3–5 (biologie influenza)
# - ctl_recruitment_rate croissant entre jour 5–10 (réponse adaptative)
```
