"""
FULLY RE-SIMULATED sensitivity analysis for the two OISA coupling parameters.

This is the rigorous companion to run_sensitivity.py. The original script
approximates the effect of kappa by shifting a reference n_immune trajectory
(because re-running CC3D per cell was assumed prohibitive). This version
instead RE-SIMULATES the complete coupled OISA system (CC3D ABM + roadrunner
ODE + MaBoSS Boolean) at every grid cell, so both coupling parameters act
through the genuine dynamics rather than a proxy:

  - kappa   (ODE viral load -> ABM cytokine coupling)   via OISA_KAPPA
  - scaling (ABM n_immune -> CTL/mL conversion)         via OISA_CTL_SCALING

Both are read from the environment by the OISA bridge/adapter (they default
to the paper values 3.5e-7 and 100 when unset), so NO published-model or
adapter source is edited to run the sweep -- only OISA-layer env vars change.

Requirements (user's machine only -- CompuCell3D 4.8 is NOT in the sandbox):
    conda activate cc3d48-env

Usage (from repo root):
    python models/orchestrator/run_sensitivity_full.py \
        --days 14 --reps 3 --workers 9 \
        --output results/sensitivity_full.json

Cost: 3x3 grid x `reps` replicates x ~270 s each. With reps=3 that is 27
coupled runs; on 9 workers ~3 waves -> ~15 min. reps>1 gives a per-cell
ensemble so the reported peak_V / clearance carry a spread, not a single
draw (the main limitation of the original single-replicate grid).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).parent.parent))

_KAPPA_VALUES = [3.5e-8, 3.5e-7, 3.5e-6]      # +/- 1 OOM around the pinned value
_SCALING_VALUES = [10.0, 100.0, 1000.0]       # +/- 1 OOM around 100 CTL/mL/agent


def _run_cell(kappa: float, scaling: float, rep: int,
              n_days: int, output_base: str) -> dict:
    """Worker: one full coupled re-simulation at (kappa, scaling)."""
    os.environ["OISA_KAPPA"] = repr(kappa)
    os.environ["OISA_CTL_SCALING"] = repr(scaling)

    from orchestrator.orchestrator import OISAOrchestrator

    tag = f"k{kappa:.1e}_s{scaling:.0f}_r{rep:02d}"
    out_dir = Path(output_base).parent / "sensitivity_full_runs" / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    ipc_dir = Path(tempfile.mkdtemp(prefix=f"oisa_ipc_{tag}_"))

    t0 = time.monotonic()
    orch = OISAOrchestrator(output_dir=out_dir, ipc_dir=ipc_dir, n_abm_instances=1)
    orch.run(n_days=n_days)
    orch.abm.close()
    elapsed = time.monotonic() - t0

    viral, n_imm, times = [], [], []
    for cp in sorted(out_dir.glob("issl_t*.json")):
        d = json.loads(cp.read_text())
        t = d.get("gsim_time_days")
        for sig in d["ode"]["export_signals"]:
            if sig["signal_id"] == "miao2010.viral_load":
                viral.append(sig["value"]); times.append(t)
        if d.get("abm"):
            for cs in d["abm"]["continuous_state"]:
                if cs["label"] == "n_immune":
                    n_imm.append(cs["count"])

    peak_v = max(viral) if viral else 0.0
    peak_day = times[viral.index(peak_v)] if viral else None
    v_final = viral[-1] if viral else 0.0
    return {
        "kappa": kappa, "scaling": scaling, "rep": rep, "elapsed_s": elapsed,
        "peak_V": peak_v, "peak_day": peak_day, "V_final": v_final,
        "residual_frac": (v_final / peak_v) if peak_v else None,
        "max_n_immune": max(n_imm) if n_imm else 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--reps", type=int, default=3,
                        help="Stochastic replicates per grid cell")
    parser.add_argument("--workers", type=int, default=min(9, os.cpu_count() or 4))
    parser.add_argument("--output", type=Path,
                        default=Path("results/sensitivity_full.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    jobs = [(k, s, r) for k in _KAPPA_VALUES for s in _SCALING_VALUES
            for r in range(1, args.reps + 1)]
    print(f"Full sensitivity sweep: {len(_KAPPA_VALUES)}x{len(_SCALING_VALUES)} grid "
          f"x {args.reps} reps = {len(jobs)} coupled runs on {args.workers} workers")

    t_total = time.monotonic()
    raw: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_run_cell, k, s, r, args.days, str(args.output)): (k, s, r)
                for (k, s, r) in jobs}
        for fut in as_completed(futs):
            k, s, r = futs[fut]
            try:
                res = fut.result(); raw.append(res)
                print(f"  k={k:.1e} s={s:.0f} r{r}: peak V={res['peak_V']:.2e} "
                      f"resid={res['residual_frac']:.3%} ({len(raw)}/{len(jobs)})")
            except Exception as e:  # noqa: BLE001
                print(f"  k={k:.1e} s={s:.0f} r{r} FAILED: {e!r}")

    # Aggregate per grid cell (median across reps + spread).
    cells = {}
    for res in raw:
        cells.setdefault((res["kappa"], res["scaling"]), []).append(res)
    grid = []
    for (k, s), rs in sorted(cells.items()):
        pv = [x["peak_V"] for x in rs]
        rf = [x["residual_frac"] for x in rs if x["residual_frac"] is not None]
        grid.append({
            "kappa": k, "scaling": s, "n_reps": len(rs),
            "peak_V_median": median(pv) if pv else None,
            "peak_V_min": min(pv) if pv else None,
            "peak_V_max": max(pv) if pv else None,
            "residual_frac_median": median(rf) if rf else None,
            "max_n_immune_median": median(x["max_n_immune"] for x in rs),
        })

    elapsed = time.monotonic() - t_total
    args.output.write_text(json.dumps({
        "grid_kappa": _KAPPA_VALUES, "grid_scaling": _SCALING_VALUES,
        "reps_per_cell": args.reps, "n_days": args.days,
        "wall_clock_min": elapsed / 60,
        "method": "full coupled re-simulation (CC3D+ODE+Boolean) per cell",
        "cells": grid, "raw": raw,
    }, indent=2))
    print(f"\nDone: {len(raw)}/{len(jobs)} runs in {elapsed/60:.1f} min")
    print(f"Grid summary -> {args.output}")


if __name__ == "__main__":
    main()
