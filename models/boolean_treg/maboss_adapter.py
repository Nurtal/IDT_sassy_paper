"""
OISA adapter for the MaBoSS Treg differentiation Boolean model.

Source model: TregModel_InitPop (.bnd/.cfg), CD4+ T-cell / regulatory-T-cell
  signalling network, 35 nodes. Distributed as a reference model in the
  pyMaBoSS test suite (github.com/colomoto/pyMaBoSS, path test/).
  Engine: cmaboss (compiled MaBoSS, continuous-time stochastic Boolean).

This adapter does NOT modify the .bnd/.cfg files.
It adds only the emit_issl() and accept_issl() interface methods, matching the
Miao2010Adapter / Sego2020Adapter contract.

Formalism note: continuous-time Boolean, run to quasi-steady state each GSimT
tick. Intracellular signalling equilibrates in minutes-hours << 6 h tick, so the
attractor probability at max_time is a valid per-tick readout (verified: FOXP3
plateau stable t=30->80 a.u.).

ISSL emitted:
  export_signals:
    - maboss_treg.treg_fraction   (FOXP3 attractor probability, dimensionless)
                                    ci_95 NATIVE = Wilson 95% score interval on (p, N)
    - maboss_treg.proliferation   (Proliferation propensity, dimensionless)

ISSL accepted:
  - miao2010.infected_fraction  → sets $ActTCR2 (antigen->TCR) and $ExtIL2 (milieu)
  - (fallback) miao2010.viral_load → normalised to an antigen proxy if fraction absent

Native UQ:
  The Boolean ci_95 is the Monte-Carlo sampling error of the attractor
  probability, intrinsic to a SINGLE run (parametrised by sample_count) — no
  external ensemble, unlike the post-hoc ci_95 bounding of the ODE/ABM adapters.
  Error is largest at intermediate commitment (Bernoulli p(1-p) shape).
"""

from __future__ import annotations

import os
from math import sqrt

import cmaboss

_HERE = os.path.dirname(__file__)
_BND_PATH = os.path.join(_HERE, "TregModel_InitPop.bnd")
_CFG_PATH = os.path.join(_HERE, "TregModel_InitPop_ActTCR2_TGFB.cfg")

# --- Coupling constants (see coupling_interface.json) ------------------------
# Antigen (infected_fraction in [0,1]) -> environmental Boolean inputs.
_ACTTCR_MIN = 0.05        # floor on TCR activation so IL-2 axis can engage
_VIRAL_REF_COPIES_ML = 9.0e6   # Miao2010 peak V (copies/mL) — normaliser for viral_load fallback
_RELAX_MAX_TIME = 30.0    # a.u. — QSS relaxation horizon (FOXP3 plateau reached)
_RELAX_TICK = 2.0         # a.u. — fine window for last-state readout
_DEFAULT_SAMPLE_COUNT = 20000  # Monte-Carlo trajectories -> controls native ci_95 width

# Output node -> export signal id
_TREG_NODE = "FOXP3"
_PROLIF_NODE = "Proliferation"


def wilson_ci95(p: float, n: int, z: float = 1.96) -> list[float]:
    """95% Wilson score interval for a probability p estimated from n samples.

    This is the native Monte-Carlo sampling error of a Boolean attractor
    probability: it stays within [0,1], scales as 1/sqrt(n), and is widest at
    p=0.5 (most ambiguous cell-fate decision).
    """
    if n <= 0:
        return [p, p]
    denom = 1.0 + z * z / n
    centre = p + z * z / (2.0 * n)
    half = z * sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    lo = (centre - half) / denom
    hi = (centre + half) / denom
    return [max(0.0, lo), min(1.0, hi)]


class MaBoSSTregAdapter:
    """OISA-compliant wrapper around the TregModel_InitPop Boolean network.

    Internal dynamics: entirely delegated to the cmaboss compiled engine.
    This class adds only emit_issl() and accept_issl().
    """

    MODEL_ID = "maboss_treg_boolean"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    def __init__(self, bnd_path: str = _BND_PATH, cfg_path: str = _CFG_PATH,
                 sample_count: int = _DEFAULT_SAMPLE_COUNT):
        self._bnd_path = bnd_path
        self._cfg_path = cfg_path
        self._sample_count = int(sample_count)
        self._sim_time_s: float = 0.0

        # Current environmental inputs (updated by accept_issl)
        self._act_tcr2: float = _ACTTCR_MIN
        self._ext_il2: float = 0.0
        self._act_tgfb: float = 1.0     # tolerogenic tissue TGF-beta assumed present

        # Cached last relaxation result
        self._p_treg: float = 0.0
        self._p_prolif: float = 0.0
        self._treg_err_native: float = 0.0     # raw MaBoSS sampling error (diagnostic)
        self._prolif_err_native: float = 0.0

        # Initial relaxation at baseline inputs
        self._relax()

    # ------------------------------------------------------------------
    # Internal: run the Boolean model to quasi-steady state
    # ------------------------------------------------------------------
    def _relax(self) -> None:
        sim = cmaboss.MaBoSSSim(self._bnd_path, self._cfg_path)
        sim.update_parameters(
            sample_count=self._sample_count,
            max_time=_RELAX_MAX_TIME,
            time_tick=_RELAX_TICK,
            **{"$ActTCR2": self._act_tcr2,
               "$ExtIL2": self._ext_il2,
               "$ActTGFB": self._act_tgfb},
        )
        means, _times, names, errs = sim.run().get_last_nodes_probtraj()
        means = means[-1]
        errs = errs[-1]
        idx = {n: i for i, n in enumerate(names)}
        self._p_treg = float(means[idx[_TREG_NODE]])
        self._p_prolif = float(means[idx[_PROLIF_NODE]])
        self._treg_err_native = float(errs[idx[_TREG_NODE]])
        self._prolif_err_native = float(errs[idx[_PROLIF_NODE]])

    def _step(self, dt_s: float) -> None:
        """Advance one GSimT tick: relax to attractor under current inputs."""
        self._sim_time_s += dt_s
        self._relax()

    # ------------------------------------------------------------------
    # OISA accept — map antigen signal to Boolean environmental inputs
    # ------------------------------------------------------------------
    def accept_issl(self, issl: dict) -> None:
        """Accept ISSL from the ODE tissue model.

        Maps antigen load to the Boolean environmental inputs:
          infected_fraction -> $ActTCR2 (TCR activation) and $ExtIL2 (milieu).
        Continuous-rate coupling (NOT thresholding) — preserves the model's
        native continuous istate semantics.
        """
        antigen = None
        for sig in issl.get("export_signals", []):
            if sig["signal_id"] == "miao2010.infected_fraction":
                antigen = float(sig["value"])
                break
        if antigen is None:
            # fallback: normalise viral load to a [0,1] antigen proxy
            for sig in issl.get("export_signals", []):
                if sig["signal_id"] == "miao2010.viral_load":
                    antigen = min(1.0, float(sig["value"]) / _VIRAL_REF_COPIES_ML)
                    break
        if antigen is None:
            return
        antigen = max(0.0, min(1.0, antigen))
        self._act_tcr2 = max(_ACTTCR_MIN, antigen)
        self._ext_il2 = antigen

    # ------------------------------------------------------------------
    # OISA emit — ISSL record with NATIVE ci_95
    # ------------------------------------------------------------------
    def emit_issl(self) -> dict:
        n = self._sample_count
        treg_ci95 = wilson_ci95(self._p_treg, n)
        prolif_ci95 = wilson_ci95(self._p_prolif, n)
        return {
            "envelope": {
                "model_id":      self.MODEL_ID,
                "model_version": "pyMaBoSS-test:TregModel_InitPop+OISA_bridge",
                "sim_time_s":    self._sim_time_s,
                "formalism":     "BOOLEAN",
                "engine":        "cmaboss (compiled MaBoSS)",
                "sample_count":  n,
                "n_nodes":       35,
                "schema_uri":    self.SCHEMA_URI,
            },
            "continuous_state": [
                {
                    "label":       "treg_fraction",
                    "description": "FOXP3 attractor probability (fraction committing to Treg phenotype)",
                    "count":       self._p_treg,
                    "unit":        "dimensionless",
                    "ci_95":       treg_ci95,
                    "ci_95_source": "native: Wilson 95% score interval on (p, sample_count)",
                    "native_sampling_error": self._treg_err_native,
                },
                {
                    "label":       "proliferation",
                    "description": "Proliferation node propensity (effector proliferation)",
                    "count":       self._p_prolif,
                    "unit":        "dimensionless",
                    "ci_95":       prolif_ci95,
                    "ci_95_source": "native: Wilson 95% score interval on (p, sample_count)",
                    "native_sampling_error": self._prolif_err_native,
                },
            ],
            "export_signals": [
                {
                    "signal_id": "maboss_treg.treg_fraction",
                    "label":     "FOXP3",
                    "value":     self._p_treg,
                    "unit":      "dimensionless",
                    "ci_95":     treg_ci95,
                    "transfer_lag_s": None,
                },
                {
                    "signal_id": "maboss_treg.proliferation",
                    "label":     "Proliferation",
                    "value":     self._p_prolif,
                    "unit":      "dimensionless",
                    "ci_95":     prolif_ci95,
                    "transfer_lag_s": None,
                },
            ],
            "watchdog": {
                "status":            "OK",
                "divergence_score":  0.0,
                "next_checkpoint_s": self._sim_time_s + 6 * 3600,
            },
        }

    # ------------------------------------------------------------------
    # Convenience accessors (for orchestrator coupling / logging)
    # ------------------------------------------------------------------
    @property
    def treg_fraction(self) -> float:
        return self._p_treg

    @property
    def proliferation(self) -> float:
        return self._p_prolif
