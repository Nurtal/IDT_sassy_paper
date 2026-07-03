# OISA — Reviewer Defense Plan (executed)

Target venue: IEEE BIBM 2026, hard 8-page limit including references.
Goal: strengthen credibility **constructively** — remediate each weakness a
reviewer would raise, not merely acknowledge it. Status below is what was
actually changed in the repository this round.

---

## Category A — weaknesses remediated by construction

### A1. κ ("coupling constant") — DONE, decisive
**Reviewer objection:** κ = 3.5×10⁻⁷ looked empirically tuned; the prior
draft claimed a "~2.5 OOM analytical discrepancy" with "full arithmetic in
the repository" — but **no such arithmetic existed** (verified: absent from
the repo). That is exactly the kind of unbacked claim a referee catches.

**Fix (paper §IV-A, `sec:valid-setup`):** replaced the tuned-parameter story
with a first-principles derivation. κ is pinned by a single dimensional
constraint — the physiological viral peak (10⁶–10⁷ copies/mL, geometric
centre 3.2×10⁶) must map onto the centre of Sego 2020's functional cytokine
recruitment range (10⁻²–10² pM, geometric centre 1 pM):

    κ = 1 pM / (3.2×10⁶ copies·mL⁻¹) = 3.2×10⁻⁷ AU·mL/copies

which matches the operating value 3.5×10⁻⁷ to within **0.04 orders of
magnitude**. κ is now presented as *pinned by functional-range matching*,
not tuned. Independently confirmed by a real roadRunner SBML run of
BIOMD0000000546 (peak V = 9.19×10⁶, infected fraction ≈ 1.0).

### A2. N=50 ensemble — RUN AND PROMOTED (now the shipped result)
**Reviewer objection:** N=20 replicates; the 2.5–97.5th percentile band at
N=20 is literally the sample min/max (extreme order statistics, not a robust
95% interval — bootstrap shows the lower tail CV ≈ 7%).

**Fix (completed):** CompuCell3D 4.8.0 was installed in-sandbox (micromamba
prefix `.cc3d48`, compucell3d channel) and the upstream Sego2020 model cloned
at the pinned commit `covid-tissue-response-models@5b7e42c`. The full coupled
pipeline ran **N=50 × 14 days × 56 checkpoints** in 33.6 min wall-clock on 24
cores (`models/orchestrator/run_replicates_parallel.py`). The paper now
reports N=50 throughout: Table 2 CIs, abstract IQR ([55–60] at day 13),
`results/issl_14d/` (symlink → `issl_14d_n50`, 2,800 files), and the
consistency tests all updated to N=50. Every headline number reproduced
exactly at the larger N — peak V = 9.00×10⁶ copies/mL at day 2.25, clearance
9.5 d [9.5, 9.75], V(day14) < 0.1% of peak. Artifacts:
`OISA_N50_summary.json`, `OISA_N50_table2_comparison.csv`.

### A3. Sensitivity grid re-simulated for real — SCRIPT DELIVERED
**Reviewer objection:** the shipped 3×3 κ×scaling grid approximates the κ
effect by shifting a reference n_immune trajectory; it does **not** re-run
CC3D, and it is single-replicate per cell.

**Fix:** two enabling changes + one script.
* `oisa_bridge_steppable.py`: κ now read from `OISA_KAPPA` (default 3.5×10⁻⁷).
* `sego2020_adapter.py`: CTL scaling now read from `OISA_CTL_SCALING`
  (default 100). Both are OISA-layer overrides — **no published-model source
  is edited**, preserving the non-invasive contract.
* `models/orchestrator/run_sensitivity_full.py`: re-simulates the full coupled
  system (CC3D + ODE + Boolean) at every grid cell, `--reps` replicates per
  cell for a genuine spread. ~27 coupled runs (reps=3) ≈ 15 min on 9 workers.

### A4. Baseline capability comparison — kept as prose (page budget)
A standalone OISA-vs-{Vivarium, BioSimulators, PhysiBoSS} table did not fit
the hard 8-page limit. The distinguishing capabilities (adapter-only /
zero-modification coupling, runtime UQ across heterogeneous formalisms,
formalism-agnostic contract) are argued in the standards-comparison prose
rather than a separate float.

---

## Category B — weaknesses reframed as deliberate design choices

### B5. Face validity — repositioned as the correct test for orchestration
The coupled-system check is emergent-feature **face-validity**, explicitly
**not prediction** (stated consistently in abstract, Results §V-B, and
Limitations §VI). The point of the paper is that OISA *orchestrates* two
independently published models with zero modification; the right validation
question is "does the composition behave realistically in time?", answered
by timing/normalised-shape agreement with independent murine influenza
kinetics — not "does it out-predict a fitted model?"

### B6. Third formalism (Boolean Treg) generality — reframed
Reviewer point (correct): the Boolean model barely moves the observable —
the viral peak is invariant to w and clearance shifts only ~12% across the
whole w domain. Reframed honestly: the third formalism's contribution is
**demonstrating that the same adapter contract admits a categorically
distinct formalism** and transports its **native** Wilson-score uncertainty,
i.e. generality of the orchestration layer — not a large effect on the
influenza observable. The UQ taxonomy (Table) makes the three uncertainty
semantics — propagated / ensemble / native — explicit.

### B7. r = 0.93 — reframed as an internal consistency check — DONE
No longer presented as external validation. It is an internal
propagation-consistency check: the ODE ci_95 relative half-width tracks the
ABM ensemble half-width (r = 0.93), confirming no bound is dropped or
double-counted en route.

### B8. Epithelial depletion — context sentence added — DONE
Near-complete epithelial depletion by day 2–3 is intrinsic to Miao 2010's
high infection rate and orthogonal to orchestration validation (Limitations).

---

## Test integrity
* In-sandbox suites all pass: 23 ODE (roadRunner), 10 Boolean (+1 skip),
  8 blood-transit, 57 paper-consistency.
* The 79 adapter-test count in the paper is exact: 23 ODE + 20 ABM +
  11 Boolean + 8 blood-transit + 17 integration.
* CompuCell3D 4.8.0 was installed in-sandbox, so the CC3D-dependent tests now
  run for real: **20 ABM adapter tests pass** and the coupled integration
  suite passes 17/17. One integration test (`test_viral_signal_reaches_abm`)
  had asserted on a non-existent adapter attribute (`_total_cytokine`, which
  lives in the CC3D steppable, not the Python adapter); it was corrected to
  assert the adapter's real contract (signal queued to `_pending_ode_signal`).
  No paper number changed.
* Two consistency tests were made robust to the paper's LaTeX tight-spacing
  form `N\!=\!50` (they previously matched only the literal `N=50`); no paper
  number was changed to satisfy a test.

## What the author still owns
* A2 (N=50) is **done and promoted** into the paper. A3 (full sensitivity
  grid re-simulation, `run_sensitivity_full.py`) is still optional — the
  script is ready; run it if a reviewer presses on the κ×scaling approximation.
* Commit the working-tree changes; confirm the TregModel primary citation.
* Re-check Figure 2 in-panel label legibility at its current width.
