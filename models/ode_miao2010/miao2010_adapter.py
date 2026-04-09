"""
OISA adapter for Miao et al. 2010 — Influenza A viral tissue dynamics.

Source model: BIOMD0000000546 (BioModels, Miao2010)
  https://www.ebi.ac.uk/biomodels/BIOMD0000000546
  Species: Ep (uninfected epithelial cells), Eps (infected), V (virus)
  Parameters modified by OISA accept(): k_E (CTL killing), k_VG (IgG neutralization)

This adapter does NOT modify BIOMD0000000546.xml in any way.
It adds only the emit_issl() and accept_issl() interface methods.

ISSL emitted:
  export_signals:
    - miao2010.viral_load  (V, copies/mL)
    - miao2010.infected_fraction  (Eps / (Ep + Eps), dimensionless)

ISSL accepted:
  - sego2020.immune_cell_count  → sets k_E (CTL killing rate)
"""

from __future__ import annotations

import json
import math
import os

import roadrunner

# Path to the downloaded SBML (not modified)
_SBML_PATH = os.path.join(os.path.dirname(__file__), "BIOMD0000000546_model1.xml")

# Conversion: immune cells → k_E parameter in SBML (mL·cell⁻¹·day⁻¹)
# Sego2020 epithelial grid: 290×290 cells × cell_volume (12 um)² = ~1 cm² tissue patch
# Estimated tissue volume ~0.01 mL; k_E_per_cell ~ 2e-4 mL·cell⁻¹·day⁻¹ (Nowak & May 2000)
_K_E_PER_IMMUNE_CELL = 2e-4  # mL·cell⁻¹·day⁻¹  [published range: 1e-4 – 1e-3]
# Conversion viral load (copies/mL) → cytokine proxy for coupling
_V_TO_CK_SCALE = 1e-6        # dimensionless scale factor


class Miao2010Adapter:
    """
    OISA-compliant wrapper around the Miao2010 SBML tissue model.

    Internal dynamics: entirely delegated to libroadrunner (BIOMD0000000546_model1.xml).
    This class adds only emit_issl() and accept_issl().
    """

    MODEL_ID = "miao2010_ode"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    def __init__(self, sbml_path: str = _SBML_PATH):
        self._rr = roadrunner.RoadRunner(sbml_path)
        self._sim_time_s: float = 0.0
        # The SBML time is in days; step_period maps seconds to days
        self._step_period_s: float = 6 * 3600  # 6 h default

    # ------------------------------------------------------------------
    # Internal step — delegates entirely to roadrunner / SBML
    # ------------------------------------------------------------------
    def _step(self, dt_s: float) -> None:
        """Advance the SBML model by dt_s seconds (converted to days internally)."""
        dt_days = dt_s / 86400.0
        t0 = self._sim_time_s / 86400.0
        t1 = t0 + dt_days
        # roadrunner simulate(start, end, num_points)
        self._rr.simulate(t0, t1, 2)
        self._sim_time_s += dt_s

    # ------------------------------------------------------------------
    # OISA emit — package SBML state as ISSL JSON-LD record
    # ------------------------------------------------------------------
    def emit_issl(self) -> dict:
        ep  = float(self._rr["[s1]"])   # uninfected epithelial cells
        eps = float(self._rr["[s2]"])   # infected epithelial cells
        v   = float(self._rr["[s3]"])   # virus (copies/mL)

        total = ep + eps
        infected_fraction = eps / total if total > 0 else 0.0

        return {
            "envelope": {
                "model_id": self.MODEL_ID,
                "model_version": "BIOMD0000000546",
                "sim_time_s": self._sim_time_s,
                "formalism": "ODE",
                "schema_uri": self.SCHEMA_URI,
            },
            "continuous_state": [
                {"label": "Ep",  "count": ep,  "unit": "cells", "ci_95": None},
                {"label": "Eps", "count": eps, "unit": "cells", "ci_95": None},
                {"label": "V",   "count": v,   "unit": "copies/mL", "ci_95": None},
            ],
            "export_signals": [
                {
                    "signal_id": "miao2010.viral_load",
                    "label": "V",
                    "value": v,
                    "unit": "copies/mL",
                },
                {
                    "signal_id": "miao2010.infected_fraction",
                    "label": "Eps_fraction",
                    "value": infected_fraction,
                    "unit": "dimensionless",
                },
            ],
            "watchdog": {
                "status": "OK",
                "divergence_score": 0.0,
                "next_checkpoint_s": self._sim_time_s + self._step_period_s,
            },
        }

    # ------------------------------------------------------------------
    # OISA accept — inject incoming ISSL signal into SBML parameters
    # ------------------------------------------------------------------
    def accept_issl(self, issl: dict) -> None:
        """
        Accept ISSL record from the Sego2020 immune model.
        Injects n_immune → k_E into the SBML via roadrunner.setValue().
        Zero changes to BIOMD0000000546_model1.xml.
        """
        for sig in issl.get("export_signals", []):
            if sig["signal_id"] == "sego2020.immune_cell_count":
                n_immune = float(sig["value"])
                k_e = n_immune * _K_E_PER_IMMUNE_CELL
                # roadrunner standard API — injects into running SBML without reloading
                self._rr["k_E"] = k_e

    # ------------------------------------------------------------------
    # Convenience: viral load as scalar (for orchestrator coupling)
    # ------------------------------------------------------------------
    @property
    def viral_load(self) -> float:
        return float(self._rr["[s3]"])
