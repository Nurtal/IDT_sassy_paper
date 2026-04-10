"""
Run N replicate 14-day OISA simulations sequentially.

Each replicate uses a distinct IPC directory so there are no file conflicts.
CC3D uses a time-seeded MersenneTwister by default, so each replicate is an
independent stochastic realisation.

Usage (from repo root, cc3d48-env activated):
    python models/orchestrator/run_replicates.py --days 14 --n 5 --output results/issl_14d
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from orchestrator.orchestrator import OISAOrchestrator


def run_one(replicate: int, n_days: int, output_base: Path) -> Path:
    out_dir = output_base / f"r{replicate:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    ipc_dir = Path(tempfile.mkdtemp(prefix=f"oisa_ipc_r{replicate:02d}_"))

    print(f"\n{'='*60}")
    print(f"  REPLICATE {replicate}  →  {out_dir}")
    print(f"{'='*60}")

    t0 = time.monotonic()
    orch = OISAOrchestrator(output_dir=out_dir, ipc_dir=ipc_dir)
    orch.run(n_days=n_days)
    orch.abm.close()
    elapsed = time.monotonic() - t0

    # Quick verification
    cps = sorted(out_dir.glob("issl_t*.json"))
    expected = n_days * 4
    assert len(cps) == expected, f"r{replicate}: got {len(cps)} checkpoints, expected {expected}"

    # Extract summary stats
    viral_loads, n_immune_vals = [], []
    for cp_path in cps:
        d = json.loads(cp_path.read_text())
        for sig in d["ode"]["export_signals"]:
            if sig["signal_id"] == "miao2010.viral_load":
                viral_loads.append(sig["value"])
        if d.get("abm"):
            for cs in d["abm"]["continuous_state"]:
                if cs["label"] == "n_immune":
                    n_immune_vals.append(cs["count"])

    peak_v   = max(viral_loads) if viral_loads else 0
    v_final  = viral_loads[-1] if viral_loads else 0
    max_imm  = max(n_immune_vals) if n_immune_vals else 0
    clr_ok   = v_final < 0.1 * peak_v

    print(f"\n  r{replicate} — {elapsed:.0f}s | peak V={peak_v:.2e} | "
          f"V(day{n_days})={v_final:.2e} | max n_immune={max_imm} | "
          f"clearance={'✓' if clr_ok else '✗'}")
    return out_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",   type=int,  default=14)
    parser.add_argument("--n",      type=int,  default=5,
                        help="Number of independent replicates")
    parser.add_argument("--output", type=Path, default=Path("results/issl_14d"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    t_total = time.monotonic()
    for i in range(1, args.n + 1):
        run_one(i, args.days, args.output)

    elapsed = time.monotonic() - t_total
    print(f"\n{'='*60}")
    print(f"  All {args.n} replicates complete in {elapsed/60:.1f} min")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
