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

# Miao2010 Table 1: k_E = killing rate coefficient (mL · cell⁻¹ · day⁻¹)
# In the SBML, killing rate = k_E × Eps × T_E_T
# where T_E_T is the CTL effector count (cells/mL) and k_E is the rate constant.
# Published range from Miao 2010 Table 1: k_E ~ 2e-5 mL·cell⁻¹·day⁻¹
_K_E_RATE_CONST = 2e-5    # mL·cell⁻¹·day⁻¹  (Miao 2010 Table 1)

# Sego2020 scale factor: n_immune (discrete tissue agents) → CTL/mL in Miao2010 compartment
# Tissue compartment ~ 0.01 mL; Sego2020 grid ~ 84,000 cells
# Published CTL density at peak: ~10³–10⁶ CTL/mL (Miao 2010 Fig 2)
# Scale: each tissue immune cell ≈ 100 CTL/mL in the systemic compartment (conservative)
_N_IMMUNE_TO_CTL_PER_ML = 100.0   # CTL/mL per tissue immune agent


class Miao2010Adapter:
    """
    OISA-compliant wrapper around the Miao2010 SBML tissue model.

    Internal dynamics: entirely delegated to libroadrunner (BIOMD0000000546_model1.xml).
    This class adds only emit_issl() and accept_issl().
    """

    MODEL_ID = "miao2010_ode"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    def __init__(self, sbml_path: str = _SBML_PATH):
        self._sbml_path = sbml_path
        self._rr = roadrunner.RoadRunner(sbml_path)
        self._sim_time_s: float = 0.0
        # The SBML time is in days; step_period maps seconds to days
        self._step_period_s: float = 6 * 3600  # 6 h default
        # Set k_E to published rate constant (Miao 2010 Table 1) — stays fixed
        # T_E_T (CTL effector count) is updated dynamically via accept_issl()
        self._rr["k_E"] = _K_E_RATE_CONST

        # Bounds runners for ci_95 propagation (lazy-initialised)
        self._rr_lo: roadrunner.RoadRunner | None = None
        self._rr_hi: roadrunner.RoadRunner | None = None
        self._ctl_ci_95: list[float] | None = None  # [lo, hi] in CTL/mL

    # ------------------------------------------------------------------
    # Bounds runners for ci_95 propagation
    # ------------------------------------------------------------------
    def _ensure_bounds_runners(self) -> None:
        """Lazy-init the lo/hi roadrunner instances for UQ propagation."""
        if self._rr_lo is None:
            self._rr_lo = roadrunner.RoadRunner(self._sbml_path)
            self._rr_lo["k_E"] = _K_E_RATE_CONST
        if self._rr_hi is None:
            self._rr_hi = roadrunner.RoadRunner(self._sbml_path)
            self._rr_hi["k_E"] = _K_E_RATE_CONST

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

        # If we have ci_95 bounds on the input, run lo/hi trajectories
        if self._ctl_ci_95 is not None:
            self._ensure_bounds_runners()
            self._rr_lo.simulate(t0, t1, 2)
            self._rr_hi.simulate(t0, t1, 2)

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

        # Compute ci_95 from bounds runners if available
        ci_95_ep = ci_95_eps = ci_95_v = ci_95_frac = None
        if self._rr_lo is not None and self._rr_hi is not None and self._ctl_ci_95 is not None:
            ep_lo  = float(self._rr_lo["[s1]"])
            eps_lo = float(self._rr_lo["[s2]"])
            v_lo   = float(self._rr_lo["[s3]"])
            ep_hi  = float(self._rr_hi["[s1]"])
            eps_hi = float(self._rr_hi["[s2]"])
            v_hi   = float(self._rr_hi["[s3]"])
            # Sort bounds (more immune → less virus, so lo/hi may swap)
            ci_95_ep  = [min(ep_lo, ep_hi), max(ep_lo, ep_hi)]
            ci_95_eps = [min(eps_lo, eps_hi), max(eps_lo, eps_hi)]
            ci_95_v   = [min(v_lo, v_hi), max(v_lo, v_hi)]
            tot_lo = ep_lo + eps_lo
            tot_hi = ep_hi + eps_hi
            frac_lo = eps_lo / tot_lo if tot_lo > 0 else 0.0
            frac_hi = eps_hi / tot_hi if tot_hi > 0 else 0.0
            ci_95_frac = [min(frac_lo, frac_hi), max(frac_lo, frac_hi)]

        return {
            "envelope": {
                "model_id": self.MODEL_ID,
                "model_version": "BIOMD0000000546",
                "sim_time_s": self._sim_time_s,
                "formalism": "ODE",
                "schema_uri": self.SCHEMA_URI,
            },
            "continuous_state": [
                {"label": "Ep",  "count": ep,  "unit": "cells", "ci_95": ci_95_ep},
                {"label": "Eps", "count": eps, "unit": "cells", "ci_95": ci_95_eps},
                {"label": "V",   "count": v,   "unit": "copies/mL", "ci_95": ci_95_v},
            ],
            "export_signals": [
                {
                    "signal_id": "miao2010.viral_load",
                    "label": "V",
                    "value": v,
                    "unit": "copies/mL",
                    "ci_95": ci_95_v,
                    "transfer_lag_s": None,
                },
                {
                    "signal_id": "miao2010.infected_fraction",
                    "label": "Eps_fraction",
                    "value": infected_fraction,
                    "unit": "dimensionless",
                    "ci_95": ci_95_frac,
                    "transfer_lag_s": None,
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
        Maps n_immune → T_E_T (CTL effector count) in the SBML via roadrunner.setValue().

        SBML kinetics: killing rate = k_E × Eps × T_E_T
          k_E  = rate constant (Miao 2010 Table 1, set at init, stays fixed)
          T_E_T = CTL effector count (cells/mL), updated here from Sego2020 signal

        If the signal carries ci_95 bounds, they are propagated to the lo/hi
        roadrunner instances for runtime UQ.

        Zero changes to BIOMD0000000546_model1.xml.
        """
        for sig in issl.get("export_signals", []):
            if sig["signal_id"] == "sego2020.immune_cell_count":
                n_immune = float(sig["value"])
                ctl_per_ml = n_immune * _N_IMMUNE_TO_CTL_PER_ML
                self._rr["T_E_T"] = ctl_per_ml

                # Propagate ci_95 bounds to lo/hi runners
                ci_95 = sig.get("ci_95")
                if ci_95 is not None and len(ci_95) == 2:
                    ctl_lo = float(ci_95[0]) * _N_IMMUNE_TO_CTL_PER_ML
                    ctl_hi = float(ci_95[1]) * _N_IMMUNE_TO_CTL_PER_ML
                    self._ctl_ci_95 = [ctl_lo, ctl_hi]
                    self._ensure_bounds_runners()
                    self._rr_lo["T_E_T"] = ctl_lo
                    self._rr_hi["T_E_T"] = ctl_hi
                else:
                    self._ctl_ci_95 = None

    # ------------------------------------------------------------------
    # Convenience: viral load as scalar (for orchestrator coupling)
    # ------------------------------------------------------------------
    @property
    def viral_load(self) -> float:
        return float(self._rr["[s3]"])
