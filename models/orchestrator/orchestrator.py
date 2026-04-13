"""
OISA Orchestrator — Influenza use case.

Couples two published models via ISSL:
  - Miao2010 ODE (SBML BIOMD0000000546) — viral tissue dynamics (Ep, Eps, V)
  - Sego2020 ABM (github:covid-tissue-models) — immune cell recruitment

Causal ordering (one-tick delay for feedback loops):
  tick N: ABM.step() → ABM.emit() → ODE.accept()   [V drives cytokine → immune]
           ODE.step() → ODE.emit() → ABM.accept()   [immune drives k_E]

Global simulation time (GSimT) step = 6 h (GCD of 6 h ODE, 24 h ABM).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add model roots to path
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

from ode_miao2010.miao2010_adapter import Miao2010Adapter
from abm_sego2020.sego2020_adapter import Sego2020Adapter, Sego2020Ensemble

_SECS_PER_HOUR = 3600


class SignalQueue:
    """Queue of ISSL signals with deferred injection times."""

    def __init__(self):
        self._queue: list[tuple[float, dict, str]] = []  # (inject_at_s, issl, target)

    def enqueue(self, issl: dict, delay_s: float, current_s: float, target: str) -> None:
        self._queue.append((current_s + delay_s, issl, target))

    def dequeue_ready(self, current_s: float) -> list[tuple[dict, str]]:
        ready = [(issl, tgt) for t, issl, tgt in self._queue if t <= current_s]
        self._queue = [(t, issl, tgt) for t, issl, tgt in self._queue if t > current_s]
        return ready
_GSIM_STEP_S   = 6 * _SECS_PER_HOUR    # 6 h GSimT tick
_ODE_DT_S      = 6 * _SECS_PER_HOUR    # 6 h — ODE advances every tick
_ABM_DT_S      = 24 * _SECS_PER_HOUR   # 24 h — ABM advances every 4 ticks


class OISAOrchestrator:

    def __init__(self, output_dir: Path, ipc_dir: Path | None = None,
                 n_abm_instances: int = 1):
        self.ode = Miao2010Adapter()
        if n_abm_instances > 1 and ipc_dir:
            self.abm = Sego2020Ensemble(n_instances=n_abm_instances, ipc_base=ipc_dir)
        elif ipc_dir:
            self.abm = Sego2020Adapter(ipc_dir=ipc_dir)
        else:
            self.abm = Sego2020Adapter()
        self.output_dir = output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        self._tick = 0
        self._signal_queue = SignalQueue()

    def run(self, n_days: int = 14) -> None:
        total_s = n_days * 86400
        gsim_t  = 0.0
        issl_abm: dict | None = None
        issl_ode: dict | None = None

        print(f"[OISA] Starting {n_days}-day influenza simulation")
        print(f"[OISA]   ODE:  Miao2010  (BIOMD0000000546, Δt=6h)")
        print(f"[OISA]   ABM:  Sego2020  (github@5b7e42c,  Δt=24h)")
        print(f"[OISA]   GSimT step: 6h  →  {n_days * 4} checkpoints\n")

        while gsim_t < total_s:
            day = gsim_t / 86400

            # -- Inject any deferred signals ready at this tick ----------------
            for deferred_issl, target in self._signal_queue.dequeue_ready(gsim_t):
                if target == "abm":
                    self.abm.accept_issl(deferred_issl)
                elif target == "ode":
                    self.ode.accept_issl(deferred_issl)

            # -- ABM tick (every 24 h = every 4 GSimT ticks) ----------------
            abm_tick = int(round(gsim_t)) % int(_ABM_DT_S) == 0
            if abm_tick:
                # Inject previous ODE signal before ABM steps
                if issl_ode is not None:
                    self._route_signal(issl_ode, "abm", gsim_t)
                self.abm._step(_ABM_DT_S)
                issl_abm = self.abm.emit_issl()
                # Inject ABM signal into ODE
                self._route_signal(issl_abm, "ode", gsim_t)

            # -- ODE tick (every 6 h) ----------------------------------------
            self.ode._step(_ODE_DT_S)
            issl_ode = self.ode.emit_issl()

            # -- Checkpoint --------------------------------------------------
            checkpoint = {
                "tick": self._tick,
                "gsim_time_days": round(day, 4),
                "ode": issl_ode,
                "abm": issl_abm,
            }
            self._save_checkpoint(checkpoint)

            # -- Watchdog check ----------------------------------------------
            v = self.ode.viral_load
            n_im = self.abm.n_immune
            status = "WARN" if v > 1e9 else "OK"
            print(f"  [t={day:5.2f}d] V={v:.3e} copies/mL  |  "
                  f"n_immune={n_im:4d}  |  {status}")

            gsim_t += _GSIM_STEP_S
            self._tick += 1

        print(f"\n[OISA] Done. {self._tick} checkpoints in {self.output_dir}")

    def _route_signal(self, issl: dict, target: str, gsim_t: float) -> None:
        """Route an ISSL signal: immediate injection or deferred via SignalQueue."""
        max_lag = 0.0
        for sig in issl.get("export_signals", []):
            lag = sig.get("transfer_lag_s")
            if lag is not None and lag > 0:
                max_lag = max(max_lag, lag)
        if max_lag > 0:
            self._signal_queue.enqueue(issl, max_lag, gsim_t, target)
        else:
            if target == "abm":
                self.abm.accept_issl(issl)
            elif target == "ode":
                self.ode.accept_issl(issl)

    def _save_checkpoint(self, checkpoint: dict) -> None:
        fname = self.output_dir / f"issl_t{self._tick:04d}.json"
        with open(fname, "w") as f:
            json.dump(checkpoint, f, indent=2, default=str)
