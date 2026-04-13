"""
Tests for the Blood Transit transfer model adapter.

Reference: Donskoy & Goldschneider 1992, J. Immunol. 148:1604–1612.
Parameters: lambda_seed=0.045 day⁻¹, lambda_clear=0.205 day⁻¹, stop_frac=0.18.
Transit lag tau = 1/(0.045+0.205) = 4.0 days.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from models.transfer_blood_transit.blood_transit_adapter import BloodTransitAdapter


@pytest.fixture()
def model():
    return BloodTransitAdapter()


# -----------------------------------------------------------------------
# 1. Parameter values
# -----------------------------------------------------------------------

class TestParameters:

    def test_tau_is_4_days(self, model):
        """Transit lag tau = 1/(0.045+0.205) = 4.0 days.
        Ref: Donskoy & Goldschneider 1992 — parabiosis experiment.
        """
        assert abs(model._tau_days - 4.0) < 0.01

    def test_tau_s_is_4_days_in_seconds(self, model):
        assert abs(model.tau_s - 4.0 * 86400) < 1.0

    def test_stop_fraction_is_018(self, model):
        """Stop fraction = lambda_seed / (lambda_seed + lambda_clear) = 0.18.
        Ref: Donskoy & Goldschneider 1992.
        """
        assert abs(model.stop_fraction - 0.18) < 0.001


# -----------------------------------------------------------------------
# 2. Steady-state computation
# -----------------------------------------------------------------------

class TestSteadyState:

    def test_thymic_delivery_at_steady_state(self, model):
        """F_thymic = stop_fraction * F_export at steady-state."""
        f_export = 1000.0  # cells/day
        model.accept_issl({
            "export_signals": [
                {"signal_id": "bm.progenitor_export", "value": f_export}
            ]
        })
        model._step(86400)
        assert abs(model._f_thymic - 0.18 * f_export) < 0.1

    def test_zero_input_gives_zero_output(self, model):
        """No BM export → no thymic delivery."""
        model._step(86400)
        assert model._f_thymic == 0.0


# -----------------------------------------------------------------------
# 3. ISSL format
# -----------------------------------------------------------------------

class TestISSLFormat:

    def test_transfer_lag_s_present_and_positive(self, model):
        """ISSL export_signals must contain transfer_lag_s > 0."""
        model.accept_issl({
            "export_signals": [
                {"signal_id": "bm.progenitor_export", "value": 500.0}
            ]
        })
        model._step(86400)
        issl = model.emit_issl()
        sig = issl["export_signals"][0]
        assert "transfer_lag_s" in sig
        assert sig["transfer_lag_s"] > 0
        assert abs(sig["transfer_lag_s"] - 4.0 * 86400) < 1.0

    def test_envelope_model_id(self, model):
        issl = model.emit_issl()
        assert issl["envelope"]["model_id"] == "blood_transit_ode"

    def test_signal_id_is_thymic_delivery(self, model):
        model._step(86400)
        issl = model.emit_issl()
        assert issl["export_signals"][0]["signal_id"] == "transit.thymic_delivery"
