"""
OISA transfer model — Blood Transit ODE (memoryless).

Biological basis: DN1/ETP progenitors exported from bone marrow circulate
in blood for 3–5 days before a fraction (stop fraction ~18%) extravasates
into the thymic parenchyma. The remainder is cleared to non-thymic tissues.

ODE:
    dB/dt = F_export - (lambda_seed + lambda_clear) * B

Output signal:
    F_thymic = lambda_seed * B   [cells/day]

Transit lag (model-derived, emitted in ISSL):
    tau = 1 / (lambda_seed + lambda_clear)   [days]

This is a memoryless transfer model: B is initialised to zero at each
invocation and integrated to steady-state, so the output depends only on
the current F_export value.

References:
    - Goldschneider et al. 1986, J. Exp. Med. 163:1–17.
    - Donskoy & Goldschneider 1992, J. Immunol. 148:1604–1612.
"""

from __future__ import annotations


class BloodTransitAdapter:
    """OISA transfer model for BM → thymus blood transit."""

    MODEL_ID = "blood_transit_ode"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    # Parameters from Donskoy & Goldschneider 1992
    LAMBDA_SEED: float = 0.045     # day⁻¹ — thymic seeding rate
    LAMBDA_CLEAR: float = 0.205    # day⁻¹ — clearance to non-thymic tissues
    STOP_FRAC: float = 0.18        # fraction reaching thymus at steady-state

    def __init__(self):
        self._f_export: float = 0.0    # current BM export flux [cells/day]
        self._f_thymic: float = 0.0    # computed thymic delivery [cells/day]
        self._tau_days: float = self._compute_tau()
        self._sim_time_s: float = 0.0

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    def _compute_tau(self) -> float:
        """Transit lag tau = 1 / (lambda_seed + lambda_clear) [days]."""
        return 1.0 / (self.LAMBDA_SEED + self.LAMBDA_CLEAR)

    @property
    def tau_s(self) -> float:
        """Transit lag in seconds."""
        return self._tau_days * 86400.0

    @property
    def stop_fraction(self) -> float:
        """Fraction of exported progenitors reaching thymus."""
        return self.LAMBDA_SEED / (self.LAMBDA_SEED + self.LAMBDA_CLEAR)

    # ------------------------------------------------------------------
    # OISA interface
    # ------------------------------------------------------------------

    def accept_issl(self, issl: dict) -> None:
        """Accept BM progenitor export flux from upstream model."""
        for sig in issl.get("export_signals", []):
            if sig["signal_id"] == "bm.progenitor_export":
                self._f_export = float(sig["value"])

    def _step(self, dt_s: float) -> None:
        """Compute steady-state thymic delivery (memoryless: no persistent state)."""
        # At steady-state: B_ss = F_export / (lambda_seed + lambda_clear)
        # F_thymic = lambda_seed * B_ss = stop_fraction * F_export
        self._f_thymic = self.stop_fraction * self._f_export
        self._sim_time_s += dt_s

    def emit_issl(self) -> dict:
        """Emit ISSL with thymic delivery flux and model-derived transfer lag."""
        return {
            "envelope": {
                "model_id": self.MODEL_ID,
                "model_version": "oisa_transfer_v1",
                "sim_time_s": self._sim_time_s,
                "formalism": "ODE",
                "schema_uri": self.SCHEMA_URI,
            },
            "continuous_state": [
                {
                    "label": "B_blood",
                    "count": self._f_export / (self.LAMBDA_SEED + self.LAMBDA_CLEAR)
                            if (self.LAMBDA_SEED + self.LAMBDA_CLEAR) > 0 else 0.0,
                    "unit": "cells",
                    "ci_95": None,
                },
            ],
            "export_signals": [
                {
                    "signal_id": "transit.thymic_delivery",
                    "label": "F_thymic",
                    "value": self._f_thymic,
                    "unit": "cells/day",
                    "transfer_lag_s": self.tau_s,
                },
            ],
            "watchdog": {
                "status": "OK",
                "divergence_score": 0.0,
                "next_checkpoint_s": self._sim_time_s + 86400,
            },
        }
