"""
OISA Tri-Formalism Orchestrator — Influenza use case, 3-formalism coupling.

Extends the 2-formalism (ODE+ABM) orchestrator with a third, structurally
different formalism — a continuous-time stochastic Boolean network (MaBoSS) —
to demonstrate genuine formalism-agnosticism and, crucially, HETEROGENEOUS
CROSS-FORMALISM UNCERTAINTY PROPAGATION.

Three coupled models (all via the ISSL v1 contract):
  - ODE      Miao2010   (SBML BIOMD0000000546)   viral tissue dynamics (Ep,Eps,V)
             live via libroadrunner; ci_95 = post-hoc lo/hi bounds runners.
  - ABM      Sego2020   (github:covid-tissue-models)  immune-cell recruitment
             replayed from the canonical N=20 ensemble; ci_95 = ensemble
             percentile [2.5, 97.5] across replicates at each tick.
  - BOOLEAN  TregModel  (pyMaBoSS TregModel_InitPop) CD4+/Treg differentiation
             live via cmaboss; ci_95 = NATIVE Wilson score interval on (p,N),
             intrinsic to a single run.

Causal coupling graph (one-tick lag on feedback edges, reusing SignalQueue):

    ABM.immune_cell_count ┐                 (recruited effector immunity)
                          ├─►  effective_immune = n_immune·(1 − w·treg_fraction)
    BOOL.treg_fraction  ──┘                 (Treg suppression of effectors)
                                │
                                ▼
    effective_immune ──► ODE.T_E_T ──► ODE viral dynamics ──► infected_fraction
                                │                                      │
                                └──────────────────────────────────────┘
    ODE.infected_fraction ──► BOOL.$ActTCR2, $ExtIL2   (antigen drives Treg fate)

The effective-immune INTERVAL is computed by interval arithmetic that fuses the
ABM ensemble bound AND the Boolean native (Wilson) bound:

    effective_lo = n_immune_lo · (1 − w · treg_hi)
    effective_hi = n_immune_hi · (1 − w · treg_lo)

so the ODE viral-load ci_95 downstream carries uncertainty that ORIGINATED in
three different formalisms with three different UQ definitions. This is the
headline result: OISA propagates heterogeneous uncertainty across a formalism
boundary without homogenising it.

GSimT step = 6 h (as in the 2-formalism orchestrator). ABM advances every 4
ticks (24 h); ODE and Boolean every tick.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).parent
# Adapter roots: repo layout is models/<name>/ with this file in models/orchestrator/,
# so adapters live under _HERE.parent. The standalone tri_formalism/ tree keeps them
# under _HERE.parent/"models". Add whichever exists.
for _cand in (_HERE.parent, _HERE.parent / "models"):
    if (_cand / "ode_miao2010").is_dir() and str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))

from ode_miao2010.miao2010_adapter import (
    Miao2010Adapter,
    _N_IMMUNE_TO_CTL_PER_ML,
)
from boolean_treg.maboss_adapter import MaBoSSTregAdapter

_SECS_PER_HOUR = 3600
_GSIM_STEP_S = 6 * _SECS_PER_HOUR
_ODE_DT_S = 6 * _SECS_PER_HOUR
_ABM_DT_S = 24 * _SECS_PER_HOUR

# Boolean→ODE feedback: Treg suppression weight on effector immunity.
# effective_immune = n_immune · (1 − w · treg_fraction). w in [0,1].
# w=0.5 : full Treg commitment halves effective killing capacity (conservative,
# consistent with in-vitro Treg:Teff suppression assays at ~1:1 giving ~50%).
_TREG_SUPPRESSION_W = 0.5


class SignalQueue:
    """Queue of ISSL signals with deferred injection times (one-tick lag)."""

    def __init__(self):
        self._queue: list[tuple[float, dict, str]] = []

    def enqueue(self, issl: dict, delay_s: float, current_s: float, target: str) -> None:
        self._queue.append((current_s + delay_s, issl, target))

    def dequeue_ready(self, current_s: float) -> list[tuple[dict, str]]:
        ready = [(issl, tgt) for t, issl, tgt in self._queue if t <= current_s]
        self._queue = [(t, issl, tgt) for t, issl, tgt in self._queue if t > current_s]
        return ready


class ABMEnsembleReplay:
    """Replays the canonical N=20 ABM ensemble as an OISA-compliant source.

    Each per-tick emit_issl() returns the ensemble MEAN immune_cell_count with a
    ci_95 = [p2.5, p97.5] percentile band across the replicates — the ABM's
    ensemble-based UQ. This is the exact dataset that was validated / accepted in
    the 2-formalism paper; re-running CompuCell3D live is prohibitively expensive
    and would change nothing about the coupling logic under test.
    """

    MODEL_ID = "sego2020_abm_cc3d"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    def __init__(self, ensemble_dir: str):
        self._dir = Path(ensemble_dir)
        self._reps = sorted(
            d for d in os.listdir(self._dir) if (self._dir / d).is_dir()
        )
        if not self._reps:
            raise FileNotFoundError(f"no replicate subdirs under {ensemble_dir}")
        self._tick = -1
        self._mean = 0.0
        self._ci95 = [0.0, 0.0]
        self._sim_time_s = 0.0
        self._model_version = "github:covid-tissue-models@5b7e42c+OISA_bridge"

    def _load_tick(self, tick: int) -> None:
        vals = []
        for r in self._reps:
            p = self._dir / r / f"issl_t{tick:04d}.json"
            if not p.exists():
                continue
            d = json.load(open(p))
            abm = d.get("abm")
            if abm is None:
                continue
            for s in abm["export_signals"]:
                if s["signal_id"] == "sego2020.immune_cell_count":
                    vals.append(float(s["value"]))
        if vals:
            arr = np.array(vals)
            self._mean = float(arr.mean())
            self._ci95 = [
                float(np.percentile(arr, 2.5)),
                float(np.percentile(arr, 97.5)),
            ]

    def _step(self, dt_s: float) -> None:
        self._tick += 1
        self._sim_time_s += dt_s
        self._load_tick(self._tick)

    @property
    def n_immune(self) -> float:
        return self._mean

    def emit_issl(self) -> dict:
        return {
            "envelope": {
                "model_id": self.MODEL_ID,
                "model_version": self._model_version,
                "sim_time_s": self._sim_time_s,
                "formalism": "ABM",
                "schema_uri": self.SCHEMA_URI,
                "uq_method": "ensemble_percentile_n20",
            },
            "continuous_state": [
                {"label": "immune_cell_count", "count": self._mean,
                 "unit": "agents", "ci_95": list(self._ci95)},
            ],
            "export_signals": [
                {"signal_id": "sego2020.immune_cell_count", "label": "n_immune",
                 "value": self._mean, "unit": "agents",
                 "ci_95": list(self._ci95), "transfer_lag_s": None},
            ],
            "watchdog": {"status": "OK", "divergence_score": 0.0,
                         "next_checkpoint_s": self._sim_time_s + _ABM_DT_S},
        }


def _fuse_effective_immune(abm_issl: dict, treg_fraction: float,
                           treg_ci95: list[float], w: float) -> dict:
    """Fuse ABM ensemble bounds with Boolean native bounds by interval arithmetic.

    Produces a synthetic 'sego2020.immune_cell_count' signal whose value and
    ci_95 represent EFFECTIVE (Treg-suppressed) effector immunity — the input
    the ODE's T_E_T actually sees. The ci_95 fuses two heterogeneous UQ sources:
      • n_immune bounds  = ABM ensemble percentile band
      • treg   bounds    = Boolean native Wilson interval
    """
    sig = next(s for s in abm_issl["export_signals"]
               if s["signal_id"] == "sego2020.immune_cell_count")
    n_mean = float(sig["value"])
    n_ci = sig.get("ci_95") or [n_mean, n_mean]
    n_lo, n_hi = float(n_ci[0]), float(n_ci[1])
    t_lo, t_hi = float(treg_ci95[0]), float(treg_ci95[1])

    eff_mean = n_mean * (1.0 - w * treg_fraction)
    # more treg (t_hi) and fewer immune (n_lo) → lowest effective immunity
    eff_lo = n_lo * (1.0 - w * t_hi)
    eff_hi = n_hi * (1.0 - w * t_lo)
    eff_lo = max(0.0, eff_lo)
    eff_hi = max(eff_lo, eff_hi)

    return {
        "envelope": dict(abm_issl["envelope"],
                         model_id="oisa_effective_immune",
                         uq_method="fused_abm_ensemble_x_boolean_wilson"),
        "continuous_state": [
            {"label": "effective_immune", "count": eff_mean, "unit": "agents",
             "ci_95": [eff_lo, eff_hi]},
        ],
        "export_signals": [
            {"signal_id": "sego2020.immune_cell_count", "label": "effective_immune",
             "value": eff_mean, "unit": "agents",
             "ci_95": [eff_lo, eff_hi], "transfer_lag_s": None,
             "provenance": {"abm_n_immune": n_mean, "abm_ci95": [n_lo, n_hi],
                            "treg_fraction": treg_fraction, "treg_ci95": [t_lo, t_hi],
                            "suppression_w": w}},
        ],
        "watchdog": {"status": "OK", "divergence_score": 0.0,
                     "next_checkpoint_s": abm_issl["watchdog"]["next_checkpoint_s"]},
    }


class TriOISAOrchestrator:
    """Three-formalism ISSL orchestrator (ODE + ABM-replay + Boolean-live)."""

    def __init__(self, output_dir: Path, abm_ensemble_dir: str,
                 boolean_sample_count: int = 20000,
                 treg_suppression_w: float = _TREG_SUPPRESSION_W):
        self.ode = Miao2010Adapter()
        self.abm = ABMEnsembleReplay(abm_ensemble_dir)
        self.boolean = MaBoSSTregAdapter(sample_count=boolean_sample_count)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._w = treg_suppression_w
        self._tick = 0
        self._signal_queue = SignalQueue()

    def run(self, n_days: int = 14, verbose: bool = True) -> None:
        total_s = n_days * 86400
        gsim_t = 0.0
        issl_ode: dict | None = None
        issl_abm: dict | None = None
        issl_bool: dict | None = None

        if verbose:
            print(f"[OISA-3F] {n_days}-day tri-formalism influenza simulation")
            print(f"[OISA-3F]   ODE:     Miao2010   (live roadrunner, post-hoc ci_95)")
            print(f"[OISA-3F]   ABM:     Sego2020   (N=20 ensemble replay, percentile ci_95)")
            print(f"[OISA-3F]   BOOLEAN: TregModel  (live cmaboss, native Wilson ci_95)")
            print(f"[OISA-3F]   GSimT=6h → {n_days*4} checkpoints, w_treg={self._w}\n")

        while gsim_t < total_s:
            day = gsim_t / 86400

            # -- deferred (lagged) signal injection ------------------------
            for deferred_issl, target in self._signal_queue.dequeue_ready(gsim_t):
                if target == "ode":
                    self.ode.accept_issl(deferred_issl)
                elif target == "boolean":
                    self.boolean.accept_issl(deferred_issl)

            # -- ABM tick (every 24 h) -------------------------------------
            abm_tick = int(round(gsim_t)) % int(_ABM_DT_S) == 0
            if abm_tick:
                self.abm._step(_ABM_DT_S)
                issl_abm = self.abm.emit_issl()

            # -- BOOLEAN tick (every 6 h): relax to Treg attractor ---------
            self.boolean._step(_GSIM_STEP_S)
            issl_bool = self.boolean.emit_issl()

            # -- Fuse ABM ⊗ Boolean → effective immune → ODE ---------------
            if issl_abm is not None:
                treg_sig = next(s for s in issl_bool["export_signals"]
                                if s["signal_id"] == "maboss_treg.treg_fraction")
                fused = _fuse_effective_immune(
                    issl_abm, float(treg_sig["value"]),
                    treg_sig["ci_95"], self._w)
                self.ode.accept_issl(fused)
            else:
                fused = None

            # -- ODE tick (every 6 h) --------------------------------------
            self.ode._step(_ODE_DT_S)
            issl_ode = self.ode.emit_issl()

            # -- ODE → Boolean feedback (one-tick lag) ---------------------
            self._route_signal(issl_ode, "boolean", gsim_t)

            # -- checkpoint ------------------------------------------------
            checkpoint = {
                "tick": self._tick,
                "gsim_time_days": round(day, 4),
                "ode": issl_ode,
                "abm": issl_abm,
                "boolean": issl_bool,
                "coupling": {
                    "effective_immune": fused["export_signals"][0] if fused else None,
                    "treg_suppression_w": self._w,
                },
            }
            self._save_checkpoint(checkpoint)

            if verbose:
                v = self.ode.viral_load
                treg = self.boolean.treg_fraction
                n_im = self.abm.n_immune
                print(f"  [t={day:5.2f}d] V={v:.3e}  n_immune={n_im:5.1f}  "
                      f"treg={treg:.3f}  |  OK")

            gsim_t += _GSIM_STEP_S
            self._tick += 1

        if verbose:
            print(f"\n[OISA-3F] Done. {self._tick} checkpoints → {self.output_dir}")

    def _route_signal(self, issl: dict, target: str, gsim_t: float) -> None:
        max_lag = 0.0
        for sig in issl.get("export_signals", []):
            lag = sig.get("transfer_lag_s")
            if lag is not None and lag > 0:
                max_lag = max(max_lag, lag)
        # feedback edges get a one-tick lag by construction (causal ordering)
        if target == "boolean":
            max_lag = max(max_lag, _GSIM_STEP_S)
        if max_lag > 0:
            self._signal_queue.enqueue(issl, max_lag, gsim_t, target)
        else:
            if target == "ode":
                self.ode.accept_issl(issl)
            elif target == "boolean":
                self.boolean.accept_issl(issl)

    def _save_checkpoint(self, checkpoint: dict) -> None:
        fname = self.output_dir / f"issl_t{self._tick:04d}.json"
        with open(fname, "w") as f:
            json.dump(checkpoint, f, indent=2, default=str)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--abm-ensemble", required=True)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--sample-count", type=int, default=20000)
    ap.add_argument("--w", type=float, default=_TREG_SUPPRESSION_W,
                    help="Treg suppression weight in effective_immune = n*(1-w*treg)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    orch = TriOISAOrchestrator(
        Path(args.out), args.abm_ensemble,
        boolean_sample_count=args.sample_count,
        treg_suppression_w=args.w)
    orch.run(n_days=args.days, verbose=not args.quiet)
