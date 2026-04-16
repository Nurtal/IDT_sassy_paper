"""
Sensitivity analysis for OISA coupling parameters.

Sweeps a 3×3 grid over:
  - κ (kappa): ODE viral load → ABM cytokine coupling constant
    Values: {3.5e-8, 3.5e-7, 3.5e-6}
  - scaling: n_immune → CTL/mL conversion factor
    Values: {10, 100, 1000}

For each combination, runs a 14-day ODE simulation with a synthetic
n_immune trajectory derived from the reference ensemble median (Table in
§V-B.4 of the paper). The ABM side is not re-run; instead, we inject the
reference n_immune trajectory and vary only the ODE-side parameters to
measure their effect on viral kinetics.

The scaling factor directly affects ODE-side dynamics (T_E_T = n_immune × scaling).
κ affects ABM-side dynamics (cytokine accumulation rate → immune recruitment speed).
Since re-running the CC3D ABM for each κ is computationally prohibitive,
we approximate the effect of varying κ on the n_immune trajectory by
shifting the immune onset and growth rate proportionally:
  - κ × 10 → immune onset ~1 day earlier, faster accumulation
  - κ / 10 → immune onset ~2 days later, slower accumulation
These approximations are consistent with the qualitative observation in
§V-A that "varying κ by ±1 order of magnitude shifts the immune onset
day by ±1–2 days."

Output: a summary table printed to stdout and saved as JSON.

Usage:
    python models/orchestrator/run_sensitivity.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from ode_miao2010.miao2010_adapter import Miao2010Adapter

# Reference n_immune trajectory (ensemble median from §V-B.4)
# Index = day (0..13), value = median n_immune at that day boundary
_REF_N_IMMUNE = [0, 6, 11, 15, 18, 23, 28, 30, 33, 39, 40, 44, 47, 50]

_DT_6H = 6 * 3600  # 6 h in seconds
_TICKS_PER_DAY = 4
_N_DAYS = 14

# Parameter grid
_KAPPA_VALUES = [3.5e-8, 3.5e-7, 3.5e-6]
_SCALING_VALUES = [10, 100, 1000]


def _shifted_n_immune(kappa: float) -> list[int]:
    """Approximate n_immune trajectory for a given κ.

    κ = 3.5e-7 (reference): use reference trajectory as-is.
    κ = 3.5e-6 (10× higher): immune onset ~1 day earlier, ~20% higher peak.
    κ = 3.5e-8 (10× lower):  immune onset ~2 days later, ~30% lower peak.

    These shifts are consistent with the qualitative observation that
    varying κ by ±1 OOM shifts immune onset by ±1–2 days.
    """
    ref_kappa = 3.5e-7
    if abs(kappa - ref_kappa) / ref_kappa < 0.1:
        return list(_REF_N_IMMUNE)

    if kappa > ref_kappa:
        # Higher κ → earlier onset, faster recruitment
        # Shift trajectory left by 1 day, scale up by 1.2
        shifted = [0] * _N_DAYS
        for d in range(_N_DAYS):
            src = d + 1  # look 1 day ahead in reference
            if src < len(_REF_N_IMMUNE):
                shifted[d] = min(int(_REF_N_IMMUNE[src] * 1.2), 70)
            else:
                shifted[d] = min(int(_REF_N_IMMUNE[-1] * 1.2), 70)
        return shifted
    else:
        # Lower κ → later onset, slower recruitment
        # Shift trajectory right by 2 days, scale down by 0.7
        shifted = [0] * _N_DAYS
        for d in range(_N_DAYS):
            src = d - 2  # look 2 days back in reference
            if src < 0:
                shifted[d] = 0
            elif src < len(_REF_N_IMMUNE):
                shifted[d] = int(_REF_N_IMMUNE[src] * 0.7)
            else:
                shifted[d] = int(_REF_N_IMMUNE[-1] * 0.7)
        return shifted


def run_one(kappa: float, scaling: float) -> dict:
    """Run a 14-day ODE simulation with given coupling parameters.

    Returns dict with peak_V, peak_day, immune_onset_day, V_day14.
    """
    ode = Miao2010Adapter()
    n_immune_traj = _shifted_n_immune(kappa)

    viral_loads = []

    for tick in range(_N_DAYS * _TICKS_PER_DAY):
        day = tick / _TICKS_PER_DAY

        # At each day boundary, inject n_immune signal
        if tick % _TICKS_PER_DAY == 0:
            current_day = int(tick / _TICKS_PER_DAY)
            if current_day < len(n_immune_traj):
                n_immune = n_immune_traj[current_day]
            else:
                n_immune = n_immune_traj[-1]

            # Apply scaling factor: n_immune → CTL/mL
            ctl_per_ml = n_immune * scaling
            ode._rr["T_E_T"] = ctl_per_ml

        # Step ODE
        ode._step(_DT_6H)
        v = ode.viral_load
        viral_loads.append((day + 0.25, v))  # +0.25 because step completes 6h later

    # Extract metrics
    peak_v = max(viral_loads, key=lambda x: x[1])
    v_final = viral_loads[-1][1]

    # Immune onset: first day where n_immune >= 1
    immune_onset = None
    for d, n in enumerate(n_immune_traj):
        if n >= 1:
            immune_onset = d
            break

    return {
        "kappa": kappa,
        "scaling": scaling,
        "peak_V": peak_v[1],
        "peak_day": peak_v[0],
        "V_day14": v_final,
        "clearance_pct": (v_final / peak_v[1]) * 100 if peak_v[1] > 0 else 0,
        "immune_onset_day": immune_onset,
        "n_immune_trajectory": n_immune_traj,
    }


def main():
    results = []

    print(f"{'κ':>12s} | {'scaling':>8s} | {'peak V (cop/mL)':>16s} | "
          f"{'peak day':>9s} | {'V(day14)':>14s} | {'V14/Vpeak %':>11s}")
    print("-" * 85)

    for kappa in _KAPPA_VALUES:
        for scaling in _SCALING_VALUES:
            r = run_one(kappa, scaling)
            results.append(r)
            print(f"{kappa:12.1e} | {scaling:8.0f} | {r['peak_V']:16.2e} | "
                  f"{r['peak_day']:9.2f} | {r['V_day14']:14.2e} | "
                  f"{r['clearance_pct']:10.4f}%")

    # Also run isolated ODE (no immune signal) as baseline
    ode_iso = Miao2010Adapter()
    for _ in range(_N_DAYS * _TICKS_PER_DAY):
        ode_iso._step(_DT_6H)
    v_iso = ode_iso.viral_load
    iso_peak_v = 0
    ode_iso2 = Miao2010Adapter()
    v_series = []
    for tick in range(_N_DAYS * _TICKS_PER_DAY):
        ode_iso2._step(_DT_6H)
        v_series.append(ode_iso2.viral_load)
    iso_peak_v = max(v_series)

    print("-" * 85)
    print(f"{'Isolated':>12s} | {'(T_E_T=0)':>8s} | {iso_peak_v:16.2e} | "
          f"{'—':>9s} | {v_iso:14.2e} | "
          f"{(v_iso / iso_peak_v) * 100 if iso_peak_v > 0 else 0:10.4f}%")

    # Save JSON
    out_path = Path(__file__).parent.parent.parent / "results" / "sensitivity_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "grid": results,
            "isolated_baseline": {
                "peak_V": iso_peak_v,
                "V_day14": v_iso,
            },
            "reference_n_immune": _REF_N_IMMUNE,
        }, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
