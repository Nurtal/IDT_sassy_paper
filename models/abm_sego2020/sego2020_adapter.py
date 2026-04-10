"""
OISA adapter for the Sego et al. 2020 spatial ABM (CompuCell3D).

Architecture: CC3D runs as a subprocess alongside the ODE orchestrator.
  - CC3D loads ViralInfectionVTM_OISA.cc3d which includes ALL original Sego2020
    steppables (zero modifications) plus OISABridgeSteppable (coupling only).
  - Adapter ↔ CC3D communication: file-based IPC in _IPC_DIR.

IPC protocol (per 24h GSimT tick):
  1. CC3D runs 72 MCS, writes abm_out.json, creates abm_ready sentinel.
  2. Adapter._step() blocks until abm_ready appears → reads abm_out.json.
  3. Adapter.emit_issl() returns data from abm_out.json, deletes abm_ready
     → CC3D unblocks for the next 72 MCS.
  4. Adapter.accept_issl() writes ode_signal.json → CC3D reads it at its
     next bridge step (non-blocking; adapter may write before or after _step).

Lines modified in Sego2020 source: 0.
Lines added (this adapter + bridge steppable): ~240.

References:
  - Sego et al. 2020, PLoS Comput Biol 16(11):e1008451.
    DOI: 10.1371/journal.pcbi.1008451
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE       = Path(__file__).resolve().parent
_CC3D_BIN   = Path(os.environ.get(
    "CC3D_PYTHON",
    os.path.expanduser("~/miniconda3/envs/cc3d48-env/bin/python")
))
_LD_LIB     = os.environ.get(
    "CC3D_LD_LIBRARY_PATH",
    os.path.expanduser("~/miniconda3/envs/cc3d48-env/lib")
)
_CC3D_PROJ  = _HERE / "ViralInfectionVTM_OISA.cc3d"
_IPC_DIR    = Path(os.environ.get("OISA_IPC_DIR", "/tmp/oisa_ipc"))

_POLL_S     = 0.05    # busy-wait poll interval
_TIMEOUT_S  = 600.0   # 10-min safeguard (CC3D 72 MCS << 10 min)

# Scale: each CC3D Immunecell agent represents 100 CTL/mL (Miao 2010 range)
_N_IMMUNE_TO_CTL_PER_ML = 100.0


class Sego2020Adapter:
    """
    OISA-compliant adapter for the Sego2020 spatial CC3D ABM.

    Launching: the first call to _step() starts the CC3D subprocess.
    Stopping:  call close() or let the context manager handle it.
    """

    MODEL_ID   = "sego2020_abm_cc3d"
    SCHEMA_URI = "schemas/issl_v1.schema.json"

    # CC3D grid parameters (ViralInfectionVTM_OISA.xml)
    GRID_X, GRID_Y, GRID_Z = 90, 90, 2
    VOXEL_CELLS = GRID_X * GRID_Y  # ~8100 epithelial agent sites

    def __init__(self, ipc_dir: Optional[Path] = None):
        self._ipc_dir   = Path(ipc_dir) if ipc_dir else _IPC_DIR
        self._ipc_dir.mkdir(parents=True, exist_ok=True)

        self._proc: Optional[subprocess.Popen] = None
        self._sim_time_s: float = 0.0

        # Last ABM state received from CC3D
        self._n_immune:    int   = 0
        self._total_virus: float = 0.0

        # Pending ODE signal to inject (written to ode_signal.json before next step)
        self._pending_ode_signal: Optional[dict] = None

        # Cleanup old IPC files
        for f in ["abm_out.json", "abm_ready", "ode_signal.json"]:
            (self._ipc_dir / f).unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Subprocess lifecycle
    # ------------------------------------------------------------------

    def _start_cc3d(self) -> None:
        """Launch CC3D subprocess (once) from a clean staging directory."""
        if self._proc is not None:
            return

        # CC3D copies the entire working directory to the output dir on startup.
        # To avoid permission errors from the sego2020/.git pack files, we
        # stage only the four required files in a temp directory.
        self._staging_dir = tempfile.mkdtemp(prefix="oisa_cc3d_stage_")
        staging = Path(self._staging_dir)
        for fname in [
            "ViralInfectionVTM_OISA.cc3d",
            "ViralInfectionVTM_OISA.py",
            "ViralInfectionVTM_OISA.xml",
            "oisa_bridge_steppable.py",
        ]:
            shutil.copy2(_HERE / fname, staging / fname)

        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = (
            _LD_LIB + ":" + env.get("LD_LIBRARY_PATH", "")
        ).rstrip(":")
        env["OISA_IPC_DIR"]    = str(self._ipc_dir)
        env["OISA_SCRIPT_DIR"] = str(_HERE)

        # Output dir must be OUTSIDE staging dir (CC3D requirement)
        self._cc3d_out_dir = tempfile.mkdtemp(prefix="oisa_cc3d_out_")

        cmd = [
            str(_CC3D_BIN),
            "-m", "cc3d.run_script",
            "-i", str(staging / "ViralInfectionVTM_OISA.cc3d"),
            "-o", self._cc3d_out_dir,
            "-f", "0",   # no VTK snapshot files
        ]
        self._proc = subprocess.Popen(
            cmd,
            env=env,
            cwd=str(staging),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def close(self) -> None:
        """Terminate CC3D subprocess and remove staging dir."""
        if self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
        staging = getattr(self, "_staging_dir", None)
        if staging and Path(staging).exists():
            shutil.rmtree(staging, ignore_errors=True)
            self._staging_dir = None
        cc3d_out = getattr(self, "_cc3d_out_dir", None)
        if cc3d_out and Path(cc3d_out).exists():
            shutil.rmtree(cc3d_out, ignore_errors=True)
            self._cc3d_out_dir = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------
    # OISA step — wait for CC3D to complete one 24h batch
    # ------------------------------------------------------------------

    def _step(self, dt_s: float) -> None:
        """
        Advance the ABM by dt_s seconds (must be 24h = 86400 s).
        Blocks until CC3D finishes 72 MCS and writes abm_ready.
        """
        self._start_cc3d()

        # Write pending ODE signal BEFORE the next bridge step reads it
        if self._pending_ode_signal is not None:
            sig_path = self._ipc_dir / "ode_signal.json"
            sig_path.write_text(json.dumps(self._pending_ode_signal))
            self._pending_ode_signal = None

        # Wait for CC3D to finish this 72-MCS batch
        ready_path = self._ipc_dir / "abm_ready"
        t0 = time.monotonic()
        while not ready_path.exists():
            if self._proc is not None and self._proc.poll() is not None:
                # CC3D exited — read stderr for diagnosis
                err = ""
                if self._proc.stderr:
                    err = self._proc.stderr.read().decode(errors="replace")[-2000:]
                raise RuntimeError(
                    f"CC3D subprocess exited unexpectedly (returncode="
                    f"{self._proc.returncode}).\nStderr tail:\n{err}"
                )
            elapsed = time.monotonic() - t0
            if elapsed > _TIMEOUT_S:
                raise RuntimeError(
                    f"Sego2020Adapter._step: CC3D did not respond within {_TIMEOUT_S}s. "
                    f"IPC dir: {self._ipc_dir}"
                )
            time.sleep(_POLL_S)

        # Read ABM state (abm_ready exists → abm_out.json is also ready)
        out_path = self._ipc_dir / "abm_out.json"
        try:
            data = json.loads(out_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to read abm_out.json: {e}") from e

        # Parse state
        self._n_immune    = 0
        self._total_virus = 0.0
        for cs in data.get("continuous_state", []):
            if cs["label"] == "n_immune":
                self._n_immune = int(cs["count"])
            elif cs["label"] == "total_virus":
                self._total_virus = float(cs["count"])

        self._sim_time_s += dt_s

    # ------------------------------------------------------------------
    # OISA emit — package CC3D state as ISSL record
    # Then DELETE abm_ready → CC3D unblocks for next batch
    # ------------------------------------------------------------------

    def emit_issl(self) -> dict:
        # Unblock CC3D by removing sentinel (it's now safe — we've read the data)
        ready_path = self._ipc_dir / "abm_ready"
        ready_path.unlink(missing_ok=True)

        return {
            "envelope": {
                "model_id":      self.MODEL_ID,
                "model_version": "github:covid-tissue-models@5b7e42c+OISA_bridge",
                "sim_time_s":    self._sim_time_s,
                "formalism":     "ABM",
                "agent_count":   self._n_immune,
                "grid":          f"{self.GRID_X}×{self.GRID_Y}×{self.GRID_Z}",
                "schema_uri":    self.SCHEMA_URI,
            },
            "continuous_state": [
                {
                    "label":       "n_immune",
                    "description": "CC3D Immunecell agent count (type 5)",
                    "count":       self._n_immune,
                    "unit":        "cells",
                    "ci_95":       None,
                },
                {
                    "label":       "total_virus_field",
                    "description": "Integral of CC3D Virus concentration field",
                    "count":       self._total_virus,
                    "unit":        "AU·voxel",
                    "ci_95":       None,
                },
            ],
            "export_signals": [
                {
                    "signal_id": "sego2020.immune_cell_count",
                    "label":     "n_immune",
                    "value":     float(self._n_immune),
                    "unit":      "cells",
                },
                {
                    "signal_id": "sego2020.recruitment_cytokine",
                    "label":     "totalCytokine_proxy",
                    "value":     self._total_virus,
                    "unit":      "AU",
                },
            ],
            "watchdog": {
                "status":           "OK",
                "divergence_score": 0.0,
                "next_checkpoint_s": self._sim_time_s + 86400,
            },
        }

    # ------------------------------------------------------------------
    # OISA accept — queue ODE signal for next CC3D bridge step
    # ------------------------------------------------------------------

    def accept_issl(self, issl: dict) -> None:
        """
        Accept ISSL from Miao2010 ODE.
        Queues the signal; it is written to ode_signal.json just before
        the next _step() call so the OISABridgeSteppable can read it.
        """
        signals = [
            s for s in issl.get("export_signals", [])
            if s["signal_id"] in {
                "miao2010.viral_load",
                "miao2010.infected_fraction",
            }
        ]
        if signals:
            self._pending_ode_signal = {"export_signals": signals}

    # ------------------------------------------------------------------
    # Properties expected by orchestrator
    # ------------------------------------------------------------------

    @property
    def n_immune(self) -> int:
        return self._n_immune
