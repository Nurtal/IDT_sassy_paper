"""
OISABridgeSteppable — runs INSIDE CompuCell3D alongside the Sego2020 steppables.

This steppable is the only addition to the Sego2020 model.
All biological equations remain EXACTLY as published in Sego et al. 2020.

Frequency: every 72 MCS (= 72 × 20 min = 24 h of simulated time).

IPC protocol (file-based, no network):
  IPC_DIR / abm_out.json   — written by this steppable (ABM → ODE signal)
  IPC_DIR / abm_ready      — sentinel: created after abm_out.json is written
                              CC3D blocks here until the adapter DELETES it
  IPC_DIR / ode_signal.json — written by adapter (ODE → ABM signal), if present
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from cc3d.core.PySteppables import SteppableBasePy


# IPC directory — must match sego2020_adapter.py
_IPC_DIR = Path(os.environ.get("OISA_IPC_DIR", "/tmp/oisa_ipc"))

_POLL_INTERVAL_S = 0.05   # busy-wait resolution
_TIMEOUT_S       = 300.0  # 5-minute safeguard against hung adapter


class OISABridgeSteppable(SteppableBasePy):
    """
    Minimal OISA bridge steppable.

    Inherits from SteppableBasePy (CC3D standard base class).
    Reads CC3D state after each 24h batch → writes abm_out.json.
    Blocks until adapter acknowledges (deletes abm_ready).
    Reads ode_signal.json if present and injects viral load into CC3D.
    """

    def __init__(self, frequency: int = 72):
        super().__init__(frequency=frequency)
        self._ipc_dir = Path(os.environ.get("OISA_IPC_DIR", "/tmp/oisa_ipc"))
        self._ipc_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        pass

    def step(self, mcs: int):
        """Called by CC3D every `frequency` MCS."""
        # --- 1. Read current ABM state from CC3D ---
        n_immune    = self._count_immune_cells()
        total_virus = self._integrate_virus_field()
        sim_time_s  = mcs * 20 * 60   # 20 min/MCS → seconds

        abm_out = {
            "sim_time_s": sim_time_s,
            "mcs": mcs,
            "export_signals": [
                {
                    "signal_id": "sego2020.immune_cell_count",
                    "value": n_immune,
                    "unit": "cells",
                },
                {
                    "signal_id": "sego2020.total_virus_field",
                    "value": total_virus,
                    "unit": "AU",
                },
            ],
            "continuous_state": [
                {"label": "n_immune",    "count": n_immune,    "unit": "cells"},
                {"label": "total_virus", "count": total_virus, "unit": "AU"},
            ],
        }

        # --- 2. Publish state + signal readiness ---
        out_path   = self._ipc_dir / "abm_out.json"
        ready_path = self._ipc_dir / "abm_ready"

        out_path.write_text(json.dumps(abm_out, indent=2))
        ready_path.touch()   # adapter is waiting for this

        # --- 3. Block until adapter has consumed the record ---
        t0 = time.monotonic()
        while ready_path.exists():
            elapsed = time.monotonic() - t0
            if elapsed > _TIMEOUT_S:
                ready_path.unlink(missing_ok=True)   # release deadlock
                raise RuntimeError(
                    f"OISABridgeSteppable: adapter did not acknowledge within {_TIMEOUT_S}s "
                    f"(mcs={mcs}). Possible adapter crash."
                )
            time.sleep(_POLL_INTERVAL_S)

        # --- 4. Inject ODE signal into CC3D if adapter wrote one ---
        sig_path = self._ipc_dir / "ode_signal.json"
        if sig_path.exists():
            try:
                sig = json.loads(sig_path.read_text())
                sig_path.unlink(missing_ok=True)
                self._inject_ode_signals(sig)
            except (json.JSONDecodeError, OSError):
                pass   # malformed file — ignore and continue

    def finish(self):
        """Called by CC3D at end of simulation — write a terminal record."""
        terminal = {"status": "finished", "mcs": -1, "export_signals": []}
        (self._ipc_dir / "abm_out.json").write_text(json.dumps(terminal))
        (self._ipc_dir / "abm_ready").touch()

    # ------------------------------------------------------------------
    # Helpers — read CC3D state
    # ------------------------------------------------------------------

    def _count_immune_cells(self) -> int:
        """Count live CC3D agents of type Immunecell (typeId=5)."""
        try:
            return sum(1 for cell in self.cell_list if cell.type == 5)
        except Exception:
            return 0

    def _integrate_virus_field(self) -> float:
        """Sum the Virus concentration field over all voxels."""
        try:
            field = self.get_concentration_field("Virus")
            if field is None:
                return 0.0
            total = 0.0
            for x in range(90):
                for y in range(90):
                    for z in range(2):
                        v = field[x, y, z]
                        if v > 0:
                            total += v
            return total
        except Exception:
            return 0.0

    def _inject_ode_signals(self, sig: dict) -> None:
        """
        Inject ODE-derived viral load into CC3D.

        Mapping: miao2010.viral_load (copies/mL) → Virus field boost
        in the CC3D Virus diffusion field via the shared-state variable
        in ImmuneRecruitmentSteppable (totalCytokine proxy).
        """
        for s in sig.get("export_signals", []):
            if s["signal_id"] == "miao2010.viral_load":
                v_load = float(s["value"])
                self._set_total_cytokine_proxy(v_load)
            elif s["signal_id"] == "miao2010.infected_fraction":
                pass   # informational — no direct injection needed

    def _set_total_cytokine_proxy(self, viral_load: float) -> None:
        """
        Inject viral load into the ImmuneRecruitmentSteppable shared state.

        Sego2020 ImmuneRecruitmentSteppable reads shared_steppable_vars[
        'vivtm_ir_steppable']['totalCytokine'].  We write to that dict
        so the next MCS of ImmuneRecruitmentSteppable sees the ODE-driven
        cytokine level.

        Coupling constant: 3.5e-7 AU·mL/copies  (same as original scalar adapter,
        keeps the signal within Sego2020's cytokine range ~10⁻²–10² pM).
        """
        try:
            svars = self.shared_steppable_vars
            # Key used by Sego2020 ImmuneRecruitmentSteppable (vivtm_ir_steppable)
            key = "vivtm_ir_steppable"
            if key not in svars:
                svars[key] = {}
            current_ck = svars[key].get("totalCytokine", 0.0)
            svars[key]["totalCytokine"] = current_ck + viral_load * 3.5e-7
        except Exception:
            pass   # degrade gracefully if shared_steppable_vars not available
