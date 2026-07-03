"""
Run N replicate 14-day OISA simulations IN PARALLEL across CPU cores.

This is the parallel companion to run_replicates.py (which is sequential).
Each replicate is an independent stochastic CC3D realisation with its own
IPC directory and output subfolder, so there are zero file conflicts and the
replicates can run concurrently. On a 24-core machine, N=50 replicates at
~270 s each complete in roughly ceil(50/W)*270 s wall-clock for W workers
(e.g. W=20 -> ~15 min, versus ~3.7 h sequential).

Requirements (user's machine only -- CompuCell3D 4.8 is NOT available in the
sandbox where this script was authored):
    conda activate cc3d48-env     # must provide cc3d 4.8 + roadrunner + maboss

Usage (from repo root):
    python models/orchestrator/run_replicates_parallel.py \
        --days 14 --n 50 --workers 20 --output results/issl_14d_n50

Then regenerate the paper's Table 2 / ensemble CIs from results/issl_14d_n50
exactly as for the N=20 set (the ISSL schema is identical).

Notes
-----
* Each replicate runs in its own subprocess (ProcessPoolExecutor), so a
  crash in one CC3D run cannot take down the others; failures are reported
  at the end and the surviving replicates are still usable.
* CC3D seeds its MersenneTwister from wall-clock time by default. To make a
  parallel batch reproducible we pass an explicit per-replicate seed through
  the OISA_CC3D_SEED environment variable IF the orchestrator/adapter honour
  it; if they do not, replicates remain independent time-seeded draws (still
  valid, just not bit-reproducible).
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

sys.path.insert(0, str(Path(__file__).parent.parent))


def _run_one(replicate: int, n_days: int, output_base: str,
             n_ensemble: int, seed: int | None) -> dict:
    """Worker: run a single replicate in an isolated subprocess."""
    # Imports happen inside the worker so each process initialises CC3D cleanly.
    from orchestrator.orchestrator import OISAOrchestrator

    if seed is not None:
        os.environ["OISA_CC3D_SEED"] = str(seed)

    out_dir = Path(output_base) / f"r{replicate:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    ipc_dir = Path(tempfile.mkdtemp(prefix=f"oisa_ipc_r{replicate:02d}_"))

    t0 = time.monotonic()
    orch = OISAOrchestrator(output_dir=out_dir, ipc_dir=ipc_dir,
                            n_abm_instances=n_ensemble)
    orch.run(n_days=n_days)
    orch.abm.close()
    elapsed = time.monotonic() - t0

    cps = sorted(out_dir.glob("issl_t*.json"))
    expected = n_days * 4
    ok = (len(cps) == expected)

    # Light summary for the console; full data is in the ISSL files.
    peak_v = v_final = 0.0
    max_imm = 0
    for cp_path in cps:
        d = json.loads(cp_path.read_text())
        for sig in d["ode"]["export_signals"]:
            if sig["signal_id"] == "miao2010.viral_load":
                v = sig["value"]
                peak_v = max(peak_v, v)
                v_final = v
        if d.get("abm"):
            for cs in d["abm"]["continuous_state"]:
                if cs["label"] == "n_immune":
                    max_imm = max(max_imm, cs["count"])

    return {
        "replicate": replicate, "out_dir": str(out_dir), "elapsed_s": elapsed,
        "n_checkpoints": len(cps), "expected": expected, "ok": ok,
        "peak_V": peak_v, "V_final": v_final, "max_n_immune": max_imm,
        "clearance_ok": v_final < 0.1 * peak_v if peak_v else False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--n", type=int, default=50,
                        help="Number of independent replicates")
    parser.add_argument("--workers", type=int, default=min(20, os.cpu_count() or 4),
                        help="Concurrent CC3D processes (<= physical cores)")
    parser.add_argument("--ensemble", type=int, default=1,
                        help="ABM ensemble size per replicate (>1 enables per-tick UQ)")
    parser.add_argument("--seed-base", type=int, default=None,
                        help="If set, replicate i uses seed = seed_base + i "
                             "(bit-reproducible only if adapter honours OISA_CC3D_SEED)")
    parser.add_argument("--output", type=Path, default=Path("results/issl_14d_n50"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    print(f"Launching {args.n} replicates on {args.workers} workers "
          f"({args.days} days, ensemble={args.ensemble}) -> {args.output}")

    t_total = time.monotonic()
    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(
                _run_one, i, args.days, str(args.output), args.ensemble,
                (args.seed_base + i) if args.seed_base is not None else None,
            ): i
            for i in range(1, args.n + 1)
        }
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                r = fut.result()
                results.append(r)
                tag = "OK " if r["ok"] and r["clearance_ok"] else "CHK"
                print(f"  [{tag}] r{i:02d}  {r['elapsed_s']:.0f}s  "
                      f"peak V={r['peak_V']:.2e}  max n_immune={r['max_n_immune']}  "
                      f"({len(results)}/{args.n} done)")
            except Exception as e:  # noqa: BLE001 -- report, keep going
                print(f"  [ERR] r{i:02d} FAILED: {e!r}")

    elapsed = time.monotonic() - t_total
    n_ok = sum(1 for r in results if r["ok"])
    (args.output / "run_summary.json").write_text(json.dumps(
        {"n_requested": args.n, "n_completed": len(results), "n_ok": n_ok,
         "workers": args.workers, "wall_clock_min": elapsed / 60,
         "results": sorted(results, key=lambda r: r["replicate"])}, indent=2))
    print(f"\n{'='*60}")
    print(f"  {len(results)}/{args.n} replicates finished, {n_ok} with full "
          f"{args.days*4} checkpoints, in {elapsed/60:.1f} min wall-clock")
    print(f"  Summary: {args.output/'run_summary.json'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
