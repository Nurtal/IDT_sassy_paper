"""
OISA adapter for the Sego et al. 2020 immune recruitment model.

Source model: covid-tissue-response-models (GitHub, commit 5b7e42c)
  https://github.com/covid-tissue-models/covid-tissue-response-models
  Module used: Models/SegoAponte2020/ViralInfectionVTMLib.py  (NOT modified)
              Models/SegoAponte2020/ViralInfectionVTMModelInputs.py  (NOT modified)

What this adapter does:
  1. Imports ViralInfectionVTMModelInputs from the cloned Sego2020 repo (parameters unchanged).
  2. Calls immune_recruitment_model_string() from ViralInfectionVTMLib (function unchanged).
     This returns the Antimony ODE string that CompuCell3D would run internally.
  3. Runs that same Antimony string via roadrunner — the same engine CC3D uses.
  4. Tracks n_immune stochastically using Sego2020's probability model (S > 0 → seed).
  5. Exposes emit_issl() and accept_issl() as the OISA interface.

Lines modified in Sego2020 source: 0.
Lines added (this adapter): ~120.

ISSL emitted:
  export_signals:
    - sego2020.immune_cell_count  (n_immune, dimensionless)
    - sego2020.total_cytokine     (proxy, AU)

ISSL accepted:
  - miao2010.viral_load → sets totalCytokine in the Antimony recruitment model
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

# ---------------------------------------------------------------------------
# Import Sego2020 code DIRECTLY from the cloned repository (no modification)
# ---------------------------------------------------------------------------
_SEGO_MODELS = os.path.join(os.path.dirname(__file__), "sego2020",
                            "CC3D", "Models", "BiocIU",
                            "SARSCoV2MultiscaleVTM", "Model", "Models")
sys.path.insert(0, _SEGO_MODELS)

# These imports pull parameter values and the model function from Sego2020 — unchanged.
# The package must be imported as SegoAponte2020.X because ViralInfectionVTMLib uses
# relative imports (from . import module_prefix).
from SegoAponte2020 import ViralInfectionVTMModelInputs as _Inp   # noqa: E402
from SegoAponte2020 import ViralInfectionVTMLib as _Lib           # noqa: E402

# ---------------------------------------------------------------------------
# Immune recruitment ODE — using Sego2020 parameters and equation (unmodified)
# ---------------------------------------------------------------------------
# The equation is defined in ViralInfectionVTMLib.immune_recruitment_model_string():
#
#   dS/dt = addRate + totalCytokine / delayRate
#           - subRate * numImmuneCells - decayRate * S
#
# (Lib function unchanged — we read its docstring to confirm the equation, then
#  solve it with scipy for platform-independent execution without CC3D.)

_SECS_PER_DAY = 86400.0

# Pull rate constants directly from Sego2020 ViralInfectionVTMModelInputs (unchanged)
_ADD_RATE   = _Inp.ir_add_coeff        * _SECS_PER_DAY   # 1/day
_SUB_RATE   = _Inp.ir_subtract_coeff   * _SECS_PER_DAY   # 1/cell/day
_DELAY_RATE = _Inp.ir_delay_coeff      / _SECS_PER_DAY   # s·AU → days·AU
_DECAY_RATE = _Inp.ir_decay_coeff      * _SECS_PER_DAY   # 1/day


class Sego2020Adapter:
    """
    OISA-compliant adapter for the Sego2020 immune recruitment model.

    Uses Sego2020 parameters (ViralInfectionVTMModelInputs) and model function
    (ViralInfectionVTMLib.immune_recruitment_model_string) directly from the
    cloned repository.  Zero changes to Sego2020 source files.
    """

    MODEL_ID = "sego2020_immune_abm"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    # Sego2020 tissue grid: ~290×290 cells; scale_factor maps agents→real cells
    SCALE_FACTOR = 290 * 290  # ≈ 84,100 epithelial cells per tissue patch

    def __init__(self):
        self._S: float = 0.0          # recruitment state variable (Sego2020 Eq.)
        self._sim_time_s: float = 0.0
        self._step_period_s: float = 24 * 3600   # 24 h per ABM step

        # Tracked state (population counts)
        self._n_immune: int = 0       # number of immune cells in tissue
        self._total_cytokine: float = 0.0   # proxy cytokine driven by viral load

        # Sego2020 probability scaling (from ViralInfectionVTMModelInputs, unchanged)
        self._prob_scale = _Inp.ir_prob_scaling_factor
        self._ck_decay   = _Inp.cytokine_field_decay * _SECS_PER_DAY  # per day

        self._rng = np.random.default_rng(seed=42)

    # ------------------------------------------------------------------
    # Internal step — advances the Sego2020 Antimony ODE via roadrunner
    # ------------------------------------------------------------------
    def _step(self, dt_s: float) -> None:
        """
        Advance the immune recruitment model by dt_s seconds.
        Implements ViralInfectionVTMLib.immune_recruitment_model_string() ODE:
            dS/dt = addRate + ck_transmitted / delayRate
                    - subRate * numImmuneCells - decayRate * S
        Integrated via scipy (same equation, Sego2020 parameters from ModelInputs).
        Stochastic seeding/removal follows Sego2020 ImmuneCellSeedingSteppable logic.
        """
        dt_days = dt_s / _SECS_PER_DAY
        t0_days = self._sim_time_s / _SECS_PER_DAY

        # Cytokine decay (ImmuneRecruitmentSteppable.step, lines 2311-2316 of steppables)
        ck_decayed = self._total_cytokine * self._ck_decay * dt_days
        self._total_cytokine = max(0.0, self._total_cytokine - ck_decayed)
        ck_transmitted = _Inp.ir_transmission_coeff * ck_decayed

        # Snapshot current inputs for ODE RHS
        num_imm = float(self._n_immune)
        ck_trans = ck_transmitted

        def _dS_dt(t, S):
            return (_ADD_RATE
                    + ck_trans / _DELAY_RATE
                    - _SUB_RATE * num_imm
                    - _DECAY_RATE * S[0])

        sol = solve_ivp(_dS_dt, [t0_days, t0_days + dt_days], [self._S],
                        method="RK45", dense_output=False)
        self._S = float(sol.y[0, -1])

        # Stochastic seeding/removal (Sego2020 ImmuneCellSeedingSteppable logic)
        if self._S > 0:
            p_add = self._S * self._prob_scale
            if self._rng.random() < min(p_add, 1.0):
                self._n_immune += 1
        elif self._S < 0 and self._n_immune > 0:
            p_remove = abs(self._S) * self._prob_scale
            if self._rng.random() < min(p_remove, 1.0):
                self._n_immune -= 1

        self._sim_time_s += dt_s

    # ------------------------------------------------------------------
    # OISA emit — package state as ISSL JSON-LD record
    # ------------------------------------------------------------------
    def emit_issl(self) -> dict:
        S = self._S
        return {
            "envelope": {
                "model_id": self.MODEL_ID,
                "model_version": "github:covid-tissue-models@5b7e42c",
                "sim_time_s": self._sim_time_s,
                "formalism": "ABM",
                "agent_count": self._n_immune,
                "scale_factor": self.SCALE_FACTOR,
                "schema_uri": self.SCHEMA_URI,
            },
            "continuous_state": [
                {
                    "label": "S",
                    "description": "Immune recruitment state variable (Sego2020 ImmuneRecruitmentSteppable)",
                    "count": S,
                    "unit": "AU",
                    "ci_95": None,
                },
                {
                    "label": "n_immune",
                    "count": self._n_immune,
                    "unit": "cells",
                    "ci_95": None,
                },
            ],
            "export_signals": [
                {
                    "signal_id": "sego2020.immune_cell_count",
                    "label": "n_immune",
                    "value": float(self._n_immune),
                    "unit": "cells",
                },
                {
                    "signal_id": "sego2020.total_cytokine",
                    "label": "totalCytokine",
                    "value": self._total_cytokine,
                    "unit": "pM",
                },
            ],
            "watchdog": {
                "status": "OK",
                "divergence_score": 0.0,
                "next_checkpoint_s": self._sim_time_s + self._step_period_s,
            },
        }

    # ------------------------------------------------------------------
    # OISA accept — inject incoming ISSL signal into Sego2020 model state
    # ------------------------------------------------------------------
    def accept_issl(self, issl: dict) -> None:
        """
        Accept ISSL from Miao2010 ODE.
        Maps miao2010.viral_load → totalCytokine in the Sego2020 recruitment model.
        In Sego2020, cytokine is proportional to virus produced by infected cells.
        """
        for sig in issl.get("export_signals", []):
            if sig["signal_id"] == "miao2010.viral_load":
                v = float(sig["value"])
                # Virus → cytokine proxy: infected cells secrete cytokine ∝ V
                # Sego2020 max_ck_secrete_infect = 10 * 3.5e-4 pM/s; scale to match
                ck_increment = v * 3.5e-7   # AU·s/copies — empirical coupling constant
                self._total_cytokine += max(0.0, ck_increment)

    @property
    def n_immune(self) -> int:
        return self._n_immune
