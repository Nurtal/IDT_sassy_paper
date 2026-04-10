"""
Figure 2 — 14-day coupled OISA simulation trajectories.

Reads ISSL checkpoint directories from N independent stochastic replicates
and produces a two-panel figure:
  Panel (a): viral load V (copies/mL, log scale) + infected fraction Eps/(Ep+Eps)
  Panel (b): CC3D Immunecell agent count n_immune with median ± IQR band (N replicates)

Usage:
    python figures/generate_trajectory_figure.py \
        --results results/issl_14d \
        --output  figures/oisa_trajectory

Output:
    figures/oisa_trajectory.pdf
    figures/oisa_trajectory.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        9,
    "axes.labelsize":   9,
    "axes.titlesize":   9,
    "legend.fontsize":  8,
    "xtick.labelsize":  8,
    "ytick.labelsize":  8,
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "figure.dpi":       150,
})

_RED    = "#C0392B"
_GREY   = "#7F8C8D"
_GREEN  = "#27AE60"
_LGREY  = "#BDC3C7"


def load_replicate(rep_dir: Path) -> dict:
    """Load all checkpoint data from one replicate directory."""
    times, viral_loads, inf_frac, n_immune = [], [], [], []

    for cp in sorted(rep_dir.glob("issl_t*.json")):
        d = json.loads(cp.read_text())

        times.append(d["gsim_time_days"])

        # ODE state
        cs_ode = {c["label"]: c["count"]
                  for c in d["ode"].get("continuous_state", [])}
        V  = cs_ode.get("V",  0.0)
        Ep  = cs_ode.get("Ep",  1.0)
        Eps = cs_ode.get("Eps", 0.0)
        viral_loads.append(V)
        inf_frac.append(Eps / (Ep + Eps) if (Ep + Eps) > 0 else 0.0)

        # ABM state (present only at daily ticks)
        if d.get("abm"):
            cs_abm = {c["label"]: c["count"]
                      for c in d["abm"].get("continuous_state", [])}
            n_immune.append((d["gsim_time_days"], cs_abm.get("n_immune", 0)))

    return {
        "times":       np.array(times),
        "V":           np.array(viral_loads),
        "inf_frac":    np.array(inf_frac),
        "n_immune":    n_immune,   # list of (day, count)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path,
                        default=Path("results/issl_14d"))
    parser.add_argument("--output",  type=Path,
                        default=Path("figures/oisa_trajectory"))
    args = parser.parse_args()

    # ── Collect replicates ───────────────────────────────────────────────────
    rep_dirs = sorted(args.results.glob("r*/"))
    if not rep_dirs:
        # fallback: use the results dir itself (single run)
        rep_dirs = [args.results]

    print(f"Loading {len(rep_dirs)} replicate(s) from {args.results} …")
    reps = [load_replicate(d) for d in rep_dirs]

    # Use the first replicate for ODE curves (deterministic across replicates)
    ref = reps[0]
    times = ref["times"]
    V     = ref["V"]
    frac  = ref["inf_frac"]

    # Build n_immune matrix (days × replicates) at daily boundaries
    # Collect unique ABM day points
    abm_days = sorted({day for r in reps for day, _ in r["n_immune"]})
    n_mat = np.full((len(abm_days), len(reps)), np.nan)
    for j, rep in enumerate(reps):
        day_to_count = dict(rep["n_immune"])
        for i, day in enumerate(abm_days):
            n_mat[i, j] = day_to_count.get(day, np.nan)

    abm_days_arr = np.array(abm_days)
    med  = np.nanmedian(n_mat, axis=1)
    q25  = np.nanpercentile(n_mat, 25, axis=1)
    q75  = np.nanpercentile(n_mat, 75, axis=1)

    # ── Figure layout ────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.5), sharex=True,
                             gridspec_kw={"height_ratios": [1.6, 1]})
    fig.subplots_adjust(hspace=0.08, left=0.12, right=0.88, top=0.93, bottom=0.10)

    # ── Panel (a) — Viral load + infected fraction ───────────────────────────
    ax1 = axes[0]
    ax1r = ax1.twinx()

    l1, = ax1.semilogy(times, np.maximum(V, 1), color=_RED, lw=2,
                       label="Viral load V (ODE, copies/mL)")
    l2, = ax1r.plot(times, frac * 100, color=_GREY, lw=1.2, ls="--",
                    label="Infected fraction Eps/(Ep+Eps) (%)")

    # Annotate peak
    peak_idx = int(np.argmax(V))
    ax1.annotate(f"Peak\nday {times[peak_idx]:.1f}",
                 xy=(times[peak_idx], V[peak_idx]),
                 xytext=(times[peak_idx] + 0.8, V[peak_idx] * 0.5),
                 fontsize=7, color=_RED,
                 arrowprops=dict(arrowstyle="->", color=_RED, lw=0.8))

    ax1.set_ylabel("Viral load V (copies/mL)")
    ax1r.set_ylabel("Infected fraction (%)", color=_GREY)
    ax1r.tick_params(colors=_GREY)
    ax1r.yaxis.label.set_color(_GREY)
    ax1.set_ylim(bottom=1e2)
    ax1r.set_ylim(0, max(frac * 100) * 1.3 + 0.1)
    ax1.grid(True, alpha=0.25, which="both")
    ax1.set_title("(a)  Miao 2010 ODE — influenza tissue dynamics",
                  loc="left", pad=4, fontsize=9)

    # Combine legends
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", fontsize=7.5,
               framealpha=0.85, edgecolor="none")

    # ── Panel (b) — Immune agent count ──────────────────────────────────────
    ax2 = axes[1]

    if len(reps) > 1:
        ax2.fill_between(abm_days_arr, q25, q75, color=_GREEN, alpha=0.20,
                         label=f"IQR (N={len(reps)} replicates)")
    ax2.step(abm_days_arr, med, where="post", color=_GREEN, lw=2,
             label=f"Median n_immune (CC3D Immunecell agents)")

    # Individual trajectories (thin)
    if len(reps) > 1:
        for j in range(len(reps)):
            ax2.step(abm_days_arr, n_mat[:, j], where="post",
                     color=_GREEN, lw=0.5, alpha=0.35)

    # Annotate first immune cell appearance
    first_day = next((abm_days_arr[i] for i in range(len(abm_days_arr))
                      if med[i] >= 1), None)
    if first_day is not None:
        ax2.axvline(first_day, color=_GREEN, ls=":", lw=1.0, alpha=0.6)
        ax2.annotate(f"First agent\nday {first_day:.0f}",
                     xy=(first_day, 0.5), xytext=(first_day + 0.5, 2),
                     fontsize=7, color=_GREEN,
                     arrowprops=dict(arrowstyle="->", color=_GREEN, lw=0.8))

    ax2.set_ylabel("n_immune (CC3D agents)")
    ax2.set_xlabel("Simulation time (days)")
    ax2.set_xlim(0, times[-1] + 0.1)
    ax2.set_ylim(bottom=-0.5)
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="upper left", fontsize=7.5, framealpha=0.85, edgecolor="none")
    ax2.set_title("(b)  Sego 2020 CC3D ABM — spatial immune recruitment "
                  "(90×90×2 grid, 12 steppables unmodified)",
                  loc="left", pad=4, fontsize=9)

    # ── Save ─────────────────────────────────────────────────────────────────
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        p = args.output.with_suffix(f".{ext}")
        fig.savefig(p, dpi=150, bbox_inches="tight")
        print(f"Saved {p}")

    plt.close(fig)

    # ── Summary stats ────────────────────────────────────────────────────────
    peak_V = float(np.max(V))
    V_day14 = float(V[-1])
    print(f"\nSummary (ref replicate):")
    print(f"  Peak V         = {peak_V:.2e} copies/mL (day {times[peak_idx]:.2f})")
    print(f"  V at day 14    = {V_day14:.2e} copies/mL ({V_day14/peak_V*100:.1f}% of peak)")
    print(f"  Max n_immune   = {int(np.nanmax(n_mat))}")
    if len(reps) > 1:
        day7_idx = next((i for i, d in enumerate(abm_days_arr) if abs(d - 7.0) < 0.01), None)
        if day7_idx is not None:
            print(f"  n_immune day 7 = {np.nanmedian(n_mat[day7_idx]):.0f} [IQR "
                  f"{np.nanpercentile(n_mat[day7_idx], 25):.0f}–"
                  f"{np.nanpercentile(n_mat[day7_idx], 75):.0f}]"
                  f"  (N={len(reps)})")


if __name__ == "__main__":
    main()
