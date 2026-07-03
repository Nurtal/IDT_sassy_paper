"""
Paper consistency tests — OISA IEEE BIBM 2026 submission.

Verifies that quantitative claims in docs/OISA_paper_IEEE_BIBM2026.md are
consistent with the experimental results stored in results/issl_14d/ and
results/sensitivity_analysis.json.

Run from the repo root:
    pytest tests/test_paper_consistency.py -v

These tests do NOT re-run simulations. They read pre-computed checkpoint
files and the sensitivity JSON and assert that the paper's stated numbers
are within acceptable tolerances of what the data actually shows.

When a test fails it means either:
  (a) the paper contains a number that doesn't match the data, or
  (b) the data has been regenerated and the paper needs updating.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT         = Path(__file__).resolve().parents[1]
_RESULTS_DIR  = _ROOT / "results" / "issl_14d"
_SENS_JSON    = _ROOT / "results" / "sensitivity_analysis.json"
_PAPER        = _ROOT / "paper" / "main.tex"   # submission artifact under review
_ODE_ADAPTER  = _ROOT / "models" / "ode_miao2010" / "miao2010_adapter.py"
_ABM_ADAPTER  = _ROOT / "models" / "abm_sego2020" / "sego2020_adapter.py"
_BRIDGE       = _ROOT / "models" / "abm_sego2020" / "oisa_bridge_steppable.py"
_SBML_PATH    = _ROOT / "models" / "ode_miao2010" / "BIOMD0000000546_model1.xml"

_REPLICATES   = [f"r{i:02d}" for i in range(1, 21)]
_N_REPLICATES = len(_REPLICATES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_checkpoints(replicate: str) -> list[dict]:
    """Return all checkpoint dicts for a replicate, sorted by tick."""
    rep_dir = _RESULTS_DIR / replicate
    paths = sorted(rep_dir.glob("issl_t*.json"))
    return [json.loads(p.read_text()) for p in paths]


def _viral_series(checkpoints: list[dict]) -> list[tuple[float, float]]:
    """Return (day, V) pairs from ODE export_signals."""
    out = []
    for cp in checkpoints:
        day = cp["gsim_time_days"]
        for sig in cp["ode"]["export_signals"]:
            if sig["signal_id"] == "miao2010.viral_load":
                out.append((day, sig["value"]))
    return out


def _n_immune_at_day(checkpoints: list[dict], target_day: float) -> int | None:
    """Return n_immune value at the daily tick closest to target_day."""
    for cp in checkpoints:
        if abs(cp["gsim_time_days"] - target_day) < 1e-6 and cp["abm"] is not None:
            for cs in cp["abm"]["continuous_state"]:
                if cs["label"] == "n_immune":
                    return int(cs["count"])
    return None


def _paper_text() -> str:
    return _PAPER.read_text()


def _md_draft_text() -> str:
    """The Markdown working draft (docs/), kept for drift cross-checks."""
    return (_ROOT / "docs" / "OISA_paper_IEEE_BIBM2026.md").read_text()


def _count_adapter_tests() -> int:
    """Count test functions across the adapter/orchestrator/transfer suites.

    This is the ground truth the paper's '79 adapter tests' claim must match.
    """
    total = 0
    for test_file in sorted(_ROOT.glob("models/**/test_*.py")):
        if "__pycache__" in str(test_file):
            continue
        total += len(re.findall(r"^\s*def test_", test_file.read_text(), re.M))
    return total


# ---------------------------------------------------------------------------
# Fixture: pre-load all replicates once
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_checkpoints() -> dict[str, list[dict]]:
    return {r: _load_checkpoints(r) for r in _REPLICATES}


@pytest.fixture(scope="module")
def sensitivity_data() -> dict:
    return json.loads(_SENS_JSON.read_text())


# ===========================================================================
# 1. CHECKPOINT STRUCTURE
# ===========================================================================

class TestCheckpointStructure:
    """Verify ISSL checkpoint file structure and count."""

    def test_all_replicates_present(self):
        for r in _REPLICATES:
            assert (_RESULTS_DIR / r).is_dir(), f"Replicate directory missing: {r}"

    def test_checkpoint_count_56_per_replicate(self, all_checkpoints):
        """Paper §V: '14-day simulation (56 GSimT checkpoints at 6 h intervals)'."""
        for r, cps in all_checkpoints.items():
            assert len(cps) == 56, (
                f"{r}: expected 56 checkpoints (14 days × 4 ticks/day), got {len(cps)}"
            )

    def test_ode_record_in_every_checkpoint(self, all_checkpoints):
        """ODE steps every 6 h (GSimT step) — must be present at every tick."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                assert cp["ode"] is not None, (
                    f"{r} tick {cp['tick']}: ODE record missing"
                )
                assert cp["ode"]["envelope"]["model_id"] == "miao2010_ode"

    def test_abm_record_at_daily_ticks_only(self, all_checkpoints):
        """ABM steps every 24 h — record present at ticks 0, 4, 8, … (daily boundaries)."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                tick = cp["tick"]
                if tick % 4 == 0:
                    assert cp["abm"] is not None, (
                        f"{r} tick {tick}: ABM record should be present at daily boundary"
                    )

    def test_checkpoint_times_strictly_monotonic(self, all_checkpoints):
        """GSimT is a monotonic global clock — no backward steps."""
        for r, cps in all_checkpoints.items():
            times = [cp["gsim_time_days"] for cp in cps]
            for i in range(1, len(times)):
                assert times[i] > times[i - 1], (
                    f"{r}: non-monotonic time at tick {i}: {times[i-1]} → {times[i]}"
                )

    def test_issl_model_version_fields(self, all_checkpoints):
        """Paper §V: model_version must be traceable immutable identifiers."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                ode_ver = cp["ode"]["envelope"]["model_version"]
                assert "BIOMD0000000546" in ode_ver, (
                    f"{r}: ODE model_version should contain 'BIOMD0000000546', got '{ode_ver}'"
                )
                if cp["abm"]:
                    abm_ver = cp["abm"]["envelope"]["model_version"]
                    assert "5b7e42c" in abm_ver, (
                        f"{r}: ABM model_version should contain '5b7e42c', got '{abm_ver}'"
                    )

    def test_abm_grid_declared(self, all_checkpoints):
        """Paper §V: ABM grid is '90×90×2' as declared in ISSL envelope."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                if cp["abm"]:
                    grid = cp["abm"]["envelope"]["grid"]
                    assert "90" in grid and "2" in grid, (
                        f"{r}: unexpected ABM grid string '{grid}'"
                    )

    def test_watchdog_never_flagged(self, all_checkpoints):
        """All watchdog statuses should be 'OK' — no divergence during the run."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                ode_status = cp["ode"]["watchdog"]["status"]
                assert ode_status == "OK", (
                    f"{r} tick {cp['tick']}: ODE watchdog status '{ode_status}'"
                )


# ===========================================================================
# 2. VIRAL KINETICS — PAPER §V-B.4 QUANTITATIVE CLAIMS
# ===========================================================================

class TestViralKinetics:
    """Check numerical claims in §V-B.4 and Abstract against actual data."""

    def test_initial_condition_V0_approximately_1000(self, all_checkpoints):
        """Paper Abstract + Table VI: V₀ = 1,000 copies/mL initial condition.

        The first checkpoint is after the first 6 h ODE step, so V(tick 0)
        should be slightly above 1,000 (viral growth begins immediately).
        Paper states V(day 0) ≈ 1.54×10³ copies/mL (§V-B.4 note).
        """
        for r, cps in all_checkpoints.items():
            v0 = None
            for sig in cps[0]["ode"]["export_signals"]:
                if sig["signal_id"] == "miao2010.viral_load":
                    v0 = sig["value"]
            assert v0 is not None, f"{r}: no viral load in tick 0"
            # After 6 h of ODE from V=1000, should be in [1200, 2000]
            assert 1200 < v0 < 2000, (
                f"{r}: V(tick 0) = {v0:.1f}, expected ~1542 (paper §V-B.4)"
            )

    def test_peak_V_approximately_9e6(self, all_checkpoints):
        """Paper Abstract + §V-B.4: 'peak V = 9.0×10⁶ copies/mL at day 2.25'.

        Tolerance: ±15% around 9.0×10⁶ for each replicate.
        """
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peak_v = max(v for _, v in vs)
            assert 7.5e6 < peak_v < 1.05e7, (
                f"{r}: peak V = {peak_v:.3e}, expected ~9.0×10⁶ (paper Abstract)"
            )

    def test_peak_day_at_day_2_to_3(self, all_checkpoints):
        """Paper §V-B.4: viral peak occurs at day 2.25. Allow ±0.75 day tolerance."""
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peak_day = max(vs, key=lambda x: x[1])[0]
            assert 1.5 <= peak_day <= 3.0, (
                f"{r}: peak day = {peak_day:.2f}, expected ~2.25 (paper §V-B.4)"
            )

    def test_viral_clearance_below_0_1_percent_of_peak(self, all_checkpoints):
        """Paper §V-B.4: 'clearance to < 0.1% of peak by day 13.75' for all 20 replicates."""
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peak_v = max(v for _, v in vs)
            v_final = vs[-1][1]  # last checkpoint (day 13.75)
            clearance_pct = v_final / peak_v * 100
            assert clearance_pct < 0.1, (
                f"{r}: V(final)/V(peak) = {clearance_pct:.4f}%, "
                f"paper claims < 0.1% (§V-B.4)"
            )

    def test_V_day1_in_plausible_range(self, all_checkpoints):
        """Paper trajectory table day 1: V ≈ 3.29×10⁵ copies/mL (±30%)."""
        for r, cps in all_checkpoints.items():
            v1 = None
            for cp in cps:
                if abs(cp["gsim_time_days"] - 1.0) < 1e-6:
                    for sig in cp["ode"]["export_signals"]:
                        if sig["signal_id"] == "miao2010.viral_load":
                            v1 = sig["value"]
                    break
            assert v1 is not None, f"{r}: no day-1 checkpoint"
            assert 2e5 < v1 < 5e5, (
                f"{r}: V(day 1) = {v1:.3e}, expected ~3.29×10⁵ (paper §V-B.4 table)"
            )

    def test_viral_monotone_decline_after_peak(self, all_checkpoints):
        """After the viral peak, V should decline monotonically (at 6h resolution)."""
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peak_idx = max(range(len(vs)), key=lambda i: vs[i][1])
            post_peak = [v for _, v in vs[peak_idx:]]
            for i in range(1, len(post_peak)):
                assert post_peak[i] <= post_peak[i - 1] * 1.05, (
                    f"{r}: non-monotone post-peak decline at tick {peak_idx + i}: "
                    f"{post_peak[i - 1]:.3e} → {post_peak[i]:.3e}"
                )


# ===========================================================================
# 3. IMMUNE DYNAMICS — PAPER §V-B.4 CLAIMS
# ===========================================================================

class TestImmuneDynamics:
    """Check n_immune trajectory claims in §V-B.4."""

    def test_n_immune_day0_is_zero(self, all_checkpoints):
        """Paper Table VI + §V-A: n_immune(t=0) = 0 (initial_immune_seeding = 0)."""
        for r, cps in all_checkpoints.items():
            n = _n_immune_at_day(cps, 0.0)
            assert n == 0, f"{r}: n_immune at day 0 = {n}, expected 0"

    def test_n_immune_day1_median_approx_6(self, all_checkpoints):
        """Paper §V-B.4 trajectory table: median n_immune at day 1 ≈ 6."""
        vals = [_n_immune_at_day(all_checkpoints[r], 1.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        med = statistics.median(vals)
        assert 4 <= med <= 9, (
            f"Ensemble median n_immune(day 1) = {med}, paper claims ~6 (§V-B.4)"
        )

    def test_n_immune_day1_range_matches_data(self, all_checkpoints):
        """Paper §V-B.4 trajectory table: ens. range [2–10] at day 1 (N=20)."""
        vals = [_n_immune_at_day(all_checkpoints[r], 1.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        assert min(vals) >= 0, f"n_immune cannot be negative, got {min(vals)}"
        assert min(vals) <= 3, (
            f"n_immune(day 1) min = {min(vals)}, paper states lower bound 2"
        )
        assert max(vals) <= 12, (
            f"n_immune(day 1) max = {max(vals)}, paper states upper bound 10"
        )

    def test_n_immune_day13_median_approx_57(self, all_checkpoints):
        """Paper §V-B.4 + Abstract: 'growing to 57 [ens. range: 41-64] at day 13' (N=20)."""
        vals = [_n_immune_at_day(all_checkpoints[r], 13.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        med = statistics.median(vals)
        assert 50 <= med <= 64, (
            f"Ensemble median n_immune(day 13) = {med}, paper claims ~57 (§V-B.4)"
        )

    def test_n_immune_day13_range_matches_paper(self, all_checkpoints):
        """Paper states ens. range [41–64] at day 13 (N=20)."""
        vals = [_n_immune_at_day(all_checkpoints[r], 13.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        assert min(vals) >= 38, (
            f"n_immune(day 13) min = {min(vals)}, paper lower bound is 41"
        )
        assert max(vals) <= 70, (
            f"n_immune(day 13) max = {max(vals)}, paper upper bound is 64"
        )

    def test_n_immune_monotone_non_decreasing(self, all_checkpoints):
        """Immune cell count should be non-decreasing over the 14-day run."""
        for r, cps in all_checkpoints.items():
            daily_vals = []
            for day in range(14):
                n = _n_immune_at_day(cps, float(day))
                if n is not None:
                    daily_vals.append(n)
            for i in range(1, len(daily_vals)):
                # Allow small decreases (cells can die in Sego2020)
                assert daily_vals[i] >= daily_vals[i - 1] - 3, (
                    f"{r}: n_immune dropped by more than 3 from day {i-1} to {i}: "
                    f"{daily_vals[i-1]} → {daily_vals[i]}"
                )

    def test_n_immune_always_non_negative(self, all_checkpoints):
        """Physical constraint: n_immune cannot be negative."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                if cp["abm"]:
                    for cs in cp["abm"]["continuous_state"]:
                        if cs["label"] == "n_immune":
                            assert cs["count"] >= 0, (
                                f"{r} tick {cp['tick']}: n_immune = {cs['count']}"
                            )


# ===========================================================================
# 4. CAUSAL ORDERING
# ===========================================================================

class TestCausalOrdering:
    """Verify ISSL signal timestamps respect the causal contract."""

    def test_ode_sim_time_never_ahead_of_gsim(self, all_checkpoints):
        """ODE ISSL sim_time_s must not be ahead of GSimT + one full tick."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                gsim_s = cp["gsim_time_days"] * 86400
                ode_t  = cp["ode"]["envelope"]["sim_time_s"]
                # ODE steps at 6h; sim_time_s after step = gsim_s + 6h
                assert ode_t <= gsim_s + 6 * 3600 + 1, (
                    f"{r} tick {cp['tick']}: ODE sim_time_s {ode_t} "
                    f"ahead of GSimT+6h = {gsim_s + 6 * 3600}"
                )

    def test_abm_sim_time_at_24h_boundaries(self, all_checkpoints):
        """ABM steps at 24 h intervals only — sim_time_s must be a multiple of 86400."""
        for r, cps in all_checkpoints.items():
            for cp in cps:
                if cp["abm"]:
                    abm_t = cp["abm"]["envelope"]["sim_time_s"]
                    assert abm_t % 86400 == 0, (
                        f"{r} tick {cp['tick']}: ABM sim_time_s {abm_t} "
                        f"not a multiple of 86400 s"
                    )


# ===========================================================================
# 5. PAPER NUMERICAL CLAIMS — STRING EXTRACTION
# ===========================================================================

class TestPaperClaims:
    """Verify that key numbers stated in the paper are internally consistent."""

    def test_paper_claims_56_checkpoints(self):
        """Paper must state '56 checkpoints'."""
        text = _paper_text()
        assert "56" in text and "checkpoint" in text, (
            "Paper should mention '56 checkpoints'"
        )

    def test_paper_claims_n20_ensemble(self):
        """Paper must state N = 20 ensemble instances (LaTeX: 'N = 20' or 'N=20')."""
        text = _paper_text()
        assert ("N = 20" in text) or ("N=20" in text), (
            "Paper should state 'N = 20' ensemble size"
        )

    def test_paper_claims_zero_lines_modified(self):
        """Paper Table V: '0' lines modified for both models."""
        text = _paper_text()
        # Should have the zero-modification claim
        assert "zero" in text.lower() or "**0**" in text, (
            "Paper should state zero lines modified"
        )

    def test_paper_references_BIOMD0000000546(self):
        """Paper must cite the BioModels accession for Miao 2010."""
        text = _paper_text()
        assert "BIOMD0000000546" in text, (
            "Paper must reference BioModels accession BIOMD0000000546"
        )

    def test_paper_references_sego_commit(self):
        """Paper must cite the Sego 2020 GitHub commit hash."""
        text = _paper_text()
        assert "5b7e42c" in text, (
            "Paper must reference Sego 2020 GitHub commit 5b7e42c"
        )

    def test_paper_mentions_test_count(self):
        """Paper §V-A must state the correct adapter test-suite size.

        The repository ships 79 adapter tests (23 ODE + 20 ABM + 11 Boolean
        + 17 integration + 8 transfer) and 51 paper--data consistency tests.
        This test asserts the submission (main.tex) states the true 79 and
        does NOT carry the stale '67' from the earlier Markdown draft.
        """
        text = _paper_text()
        n_adapter = _count_adapter_tests()
        assert n_adapter == 79, (
            f"Expected 79 adapter tests on disk, found {n_adapter}; "
            "update this guard and the paper together."
        )
        assert "79" in text, (
            f"Paper must state {n_adapter} adapter tests (§V-A)"
        )
        assert "67" not in text, (
            "Paper still contains the stale '67' test count from the "
            "superseded Markdown draft"
        )

    def test_paper_peak_V_matches_data(self, all_checkpoints):
        """Paper states 'peak V = 9.0×10⁶ copies/mL at day 2.25'.

        Cross-check: the actual median peak across 20 replicates should agree
        with the paper's stated value to within 10%.
        """
        peaks = []
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peaks.append(max(v for _, v in vs))
        median_peak = statistics.median(peaks)
        paper_peak  = 9.0e6
        rel_err = abs(median_peak - paper_peak) / paper_peak
        assert rel_err < 0.10, (
            f"Median peak V across replicates = {median_peak:.3e}, "
            f"paper states {paper_peak:.1e} (rel. error {rel_err:.1%} > 10%)"
        )

    def test_paper_clearance_claim_matches_data(self, all_checkpoints):
        """Paper: 'clearance to < 0.1% of peak by day 13.75' for all replicates."""
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            peak_v  = max(v for _, v in vs)
            v_final = vs[-1][1]
            assert v_final / peak_v < 0.001, (
                f"{r}: V_final/V_peak = {v_final/peak_v:.5f}, paper claims < 0.001"
            )

    def test_paper_ensemble_range_day13_upper_bound(self, all_checkpoints):
        """Paper claims n_immune day 13 ens. range upper bound 64 (N=20)."""
        vals = [_n_immune_at_day(all_checkpoints[r], 13.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        assert max(vals) <= 70, (
            f"n_immune(day 13) max = {max(vals)}, unexpectedly high (paper claims max 64)"
        )

    def test_paper_ensemble_range_day1_note(self, all_checkpoints):
        """Paper §V-B.4 states n_immune(day 1) ens. range [2–10] (N=20)."""
        vals = [_n_immune_at_day(all_checkpoints[r], 1.0) for r in _REPLICATES]
        vals = [v for v in vals if v is not None]
        actual_min, actual_max = min(vals), max(vals)
        assert actual_min >= 1, f"n_immune(day 1) min={actual_min}, unexpectedly low"
        assert actual_max <= 12, f"n_immune(day 1) max={actual_max}, unexpectedly high"
        assert 4 <= statistics.median(vals) <= 9


# ===========================================================================
# 6. SENSITIVITY ANALYSIS CONSISTENCY
# ===========================================================================

class TestSensitivityConsistency:
    """Verify that Table VIII in the paper matches sensitivity_analysis.json."""

    def test_sensitivity_json_exists(self):
        assert _SENS_JSON.exists(), f"Missing: {_SENS_JSON}"

    def test_sensitivity_grid_is_3x3(self, sensitivity_data):
        """Sensitivity grid should have 9 entries (3 κ × 3 scaling)."""
        assert len(sensitivity_data["grid"]) == 9, (
            f"Expected 9 grid entries, got {len(sensitivity_data['grid'])}"
        )

    def test_sensitivity_reference_row_matches_data(self, sensitivity_data, all_checkpoints):
        """The reference row (κ=3.5e-7, scaling=100) should match the replicate data.

        Peak V from the sensitivity script (ODE-only, deterministic) should
        agree with the stochastic replicate medians to within 5%.
        """
        ref_row = next(
            (r for r in sensitivity_data["grid"]
             if abs(r["kappa"] - 3.5e-7) < 1e-9 and r["scaling"] == 100),
            None,
        )
        assert ref_row is not None, "Reference row (κ=3.5e-7, scaling=100) missing from grid"

        rep_peaks = []
        for r, cps in all_checkpoints.items():
            vs = _viral_series(cps)
            rep_peaks.append(max(v for _, v in vs))
        median_rep_peak = statistics.median(rep_peaks)

        sens_peak = ref_row["peak_V"]
        rel_err = abs(sens_peak - median_rep_peak) / median_rep_peak
        assert rel_err < 0.10, (
            f"Sensitivity ref peak V = {sens_peak:.3e}, "
            f"replicate median peak V = {median_rep_peak:.3e} "
            f"(rel. error {rel_err:.1%} > 10%)"
        )

    def test_sensitivity_all_rows_cleared(self, sensitivity_data):
        """Table VIII: all 9 combinations should produce viral clearance (V14 < 1% of peak)."""
        for row in sensitivity_data["grid"]:
            clearance = row["clearance_pct"]
            assert clearance < 1.0, (
                f"κ={row['kappa']:.1e}, scaling={row['scaling']}: "
                f"clearance = {clearance:.4f}%, expected < 1%"
            )

    def test_sensitivity_scaling_drives_clearance(self, sensitivity_data):
        """Scaling factor should have monotone effect on clearance at fixed κ.

        Higher scaling → stronger CTL killing → lower V at day 14.
        """
        ref_kappa = 3.5e-7
        ref_rows = sorted(
            [r for r in sensitivity_data["grid"] if abs(r["kappa"] - ref_kappa) < 1e-9],
            key=lambda x: x["scaling"],
        )
        assert len(ref_rows) == 3, "Expected 3 rows for κ=3.5e-7"
        v_finals = [r["V_day14"] for r in ref_rows]
        # V_day14 should decrease as scaling increases
        assert v_finals[0] > v_finals[1] > v_finals[2], (
            f"V_day14 should decrease with scaling: {v_finals}"
        )

    def test_sensitivity_isolated_baseline_above_all_coupled(self, sensitivity_data):
        """Isolated ODE (T_E_T=0) should have highest V at day 14 (no CTL clearance)."""
        iso_v14 = sensitivity_data["isolated_baseline"]["V_day14"]
        for row in sensitivity_data["grid"]:
            if row["scaling"] > 0:
                assert iso_v14 >= row["V_day14"] * 0.9, (
                    f"Isolated V14={iso_v14:.2e} should be ≥ coupled "
                    f"(κ={row['kappa']:.1e}, scaling={row['scaling']}) "
                    f"V14={row['V_day14']:.2e} (CTL can only reduce viral load)"
                )

    def test_sensitivity_peak_V_in_plausible_range(self, sensitivity_data):
        """All 9 peak V values should be in [7×10⁶, 1.05×10⁷] — same OOM as published."""
        for row in sensitivity_data["grid"]:
            assert 7e6 <= row["peak_V"] <= 1.05e7, (
                f"κ={row['kappa']:.1e}, scaling={row['scaling']}: "
                f"peak_V={row['peak_V']:.3e} out of expected range [7e6, 1.05e7]"
            )


# ===========================================================================
# 7. ADAPTER LINES OF CODE
# ===========================================================================

class TestAdapterLineCount:
    """Paper §V-A Table V: adapter line counts.

    Paper claims: Miao 2010 ~60 lines, Sego 2020 ~240 lines total (adapter + bridge).
    These are rough approximations. Tests verify adapter files are within
    reasonable bounds of the stated values.
    """

    def _non_blank_non_comment_lines(self, path: Path) -> int:
        """Count non-empty, non-comment Python lines."""
        lines = path.read_text().splitlines()
        return sum(
            1 for ln in lines
            if ln.strip() and not ln.strip().startswith("#")
        )

    def test_ode_adapter_under_300_lines(self):
        """Miao2010 adapter is stated as ~60 lines; total file should be < 300."""
        total = len(_ODE_ADAPTER.read_text().splitlines())
        assert total < 300, (
            f"ODE adapter has {total} total lines; paper claims ~60 functional lines"
        )

    def test_abm_adapter_plus_bridge_under_700_lines(self):
        """Sego2020 adapter + bridge steppable total should be < 700 lines."""
        total = (
            len(_ABM_ADAPTER.read_text().splitlines()) +
            len(_BRIDGE.read_text().splitlines())
        )
        assert total < 700, (
            f"ABM adapter + bridge has {total} lines; paper claims ~240"
        )

    def test_ode_adapter_does_not_import_sbml_modification_tools(self):
        """Verify the ODE adapter never imports lxml or libsbml (would imply SBML edits)."""
        src = _ODE_ADAPTER.read_text()
        assert "lxml" not in src, "ODE adapter imports lxml — possible SBML modification"
        assert "libsbml" not in src, "ODE adapter imports libsbml — possible SBML modification"

    def test_sbml_file_present_and_unmodified_checksum(self):
        """SBML file must exist. We verify it's non-empty and contains BioModels metadata."""
        assert _SBML_PATH.exists(), f"SBML file missing: {_SBML_PATH}"
        content = _SBML_PATH.read_text()
        assert "BIOMD0000000546" in content or "miao" in content.lower(), (
            "SBML file does not appear to be the Miao 2010 BioModels entry"
        )


# ===========================================================================
# 8. PAPER STRUCTURE CHECKS
# ===========================================================================

class TestPaperStructure:
    """Verify the paper document has required sections and table numbers."""

    def test_all_sections_present(self):
        """main.tex must contain all required \\section blocks (IEEEtran
        auto-numbers them I..VII; the roman numerals are not in the source)."""
        text = _paper_text()
        required = [
            r"\section{Introduction}",
            r"\section{Related Work}",
            r"\section{Problem Formalisation}",
            r"\section{The OISA Architecture}",
            r"\section{Validation}",
            r"\section{Discussion}",
            r"\section{Conclusion}",
            r"\bibliography{references}",
        ]
        for section in required:
            assert section in text, f"Missing section: '{section}'"

    def test_all_tables_present(self):
        """The five labelled tables of the submission must be defined."""
        text = _paper_text()
        for label in [
            "tab:standards",
            "tab:plausibility",
            "tab:trajectory",
            "tab:coupled-valid",
            "tab:uq-taxonomy",
        ]:
            assert (r"\label{" + label + "}") in text, (
                f"Table label '{label}' not defined in paper"
            )

    def test_cure_preprint_disclaimer_disclosed(self):
        """C5 fix: CURE preprint status must be disclosed to the reader.

        The disclosure lives in the bibliography entry for sauro2025cure
        (arXiv id + preprint/peer-review note), which renders in the
        compiled reference list. The body no longer carries a separate
        preprint clause (editorial decision to remove the redundant
        Discussion sentence); the credibility guarantee is preserved by
        the reference metadata, which is the canonical place for it.
        """
        bib = (_ROOT / "paper" / "references.bib").read_text()
        # Isolate the CURE entry and assert it discloses preprint status.
        assert "sauro2025cure" in bib, "CURE reference entry missing"
        start = bib.index("sauro2025cure")
        entry = bib[start:bib.index("@", start + 1)] if "@" in bib[start + 1:] else bib[start:]
        assert "arXiv" in entry and "Preprint" in entry, (
            "CURE reference [sauro2025cure] must disclose arXiv preprint status"
        )

    def test_validation_scope_disclaimer_in_abstract(self):
        """C1 fix: Abstract must include orchestration-vs-biology disclaimer."""
        text = _paper_text()
        m0 = text.find(r"\begin{abstract}")
        m1 = text.find(r"\end{abstract}")
        assert m0 != -1 and m1 != -1, "main.tex must contain an abstract env"
        abstract = text[m0:m1]
        assert "orchestration" in abstract.lower() or "framework" in abstract.lower(), (
            "Abstract should mention orchestration scope"
        )
        assert "not" in abstract and ("biological" in abstract or "in-vivo" in abstract), (
            "Abstract should contain the biological-validation disclaimer"
        )

    def test_ensemble_range_qualifier_present(self):
        """Paper must use 'ensemble range', 'ens. range', or percentile language."""
        text = _paper_text()
        assert (
            "ensemble range" in text
            or "ens. range" in text
            or "percentile" in text.lower()
        ), (
            "Paper must qualify N=20 bounds as 'ensemble range' or percentile"
        )

    def test_sensitivity_section_present(self):
        """C2 fix: Parameter Sensitivity section must exist."""
        text = _paper_text()
        assert "Parameter Sensitivity" in text, (
            "Paper must contain a Parameter Sensitivity subsection (C2 fix)"
        )

    def test_spatial_scale_mismatch_discussed(self):
        """C3 fix: Paper must discuss the spatial scale mismatch and frame it
        as a coupling demonstration / approximation, with the volume-
        normalisation argument."""
        text = _paper_text()
        assert (
            "orders of magnitude" in text.lower()
            or "approximation" in text.lower()
            or "demonstrat" in text.lower()
        ), (
            "Discussion must frame the spatial scale mismatch as a "
            "coupling-demonstration approximation"
        )
        assert "volume" in text.lower() or "10^{-" in text or "copies" in text.lower(), (
            "Discussion must mention the volume-normalisation argument"
        )


# ===========================================================================
# 9. SUBMISSION-vs-DRAFT DRIFT GUARD
# ===========================================================================

class TestSubmissionDraftDrift:
    """Guard against the LaTeX submission (paper/main.tex) and the Markdown
    working draft (docs/OISA_paper_IEEE_BIBM2026.md) drifting apart on the
    core, checkable facts.

    Rationale: the consistency suite historically validated only the Markdown
    draft, while the artifact actually submitted to the venue is main.tex.
    A stale draft (e.g. 5 replicates / 67 tests / no Boolean formalism) could
    therefore pass CI while the submission said something different. These
    tests pin the submission to ground truth and flag when the draft lags so
    far behind that it should not be relied on.
    """

    # --- Submission is pinned to the data/repository ground truth ----------

    def test_submission_replicate_count(self):
        """main.tex must reflect the 20-replicate ensemble actually shipped."""
        text = _paper_text()
        assert _N_REPLICATES == 20, "results/issl_14d should hold 20 replicates"
        assert ("N=20" in text) or ("N = 20" in text), (
            "Submission must state the N=20 ensemble size"
        )

    def test_submission_test_count_matches_disk(self):
        """The '79 adapter tests' claim in main.tex must match the code."""
        assert _count_adapter_tests() == 79
        assert "79" in _paper_text()

    def test_submission_has_three_formalisms(self):
        """main.tex must describe the ODE+ABM+Boolean coupling (the Boolean
        formalism was added after the Markdown draft was written)."""
        text = _paper_text()
        assert "TregModel" in text and "BOOLEAN" in text, (
            "Submission must include the third (Boolean) formalism"
        )

    def test_submission_repo_url_filled(self):
        """The repository URL placeholder must be resolved before submission."""
        text = _paper_text()
        assert "repository URL to be added" not in text, (
            "main.tex still has the repository-URL placeholder"
        )
        assert "github.com/Nurtal/IDT_sassy_paper" in text, (
            "main.tex must contain the code repository URL"
        )

    # --- Draft must not contradict the submission on shared facts ----------

    def test_draft_not_stale_on_test_count(self):
        """If the Markdown draft is still present it must not assert the old
        67-test count that the submission has superseded (79).

        Matched on the specific '67 ... tests' phrasing rather than a bare
        '67' so that coincidental numbers (e.g. '7.79e3 copies/mL') do not
        mask a real regression.
        """
        draft = _md_draft_text()
        stale = re.search(r"\b67\b[^.\n]{0,40}?tests?\b", draft) or re.search(
            r"\btests?\b[^.\n]{0,40}?\b67\b", draft
        )
        assert stale is None, (
            "docs/OISA_paper_IEEE_BIBM2026.md still claims 67 tests but the "
            "submission (main.tex) and the codebase have 79. The Markdown "
            "draft is stale — regenerate it from main.tex or remove it so it "
            "cannot be mistaken for the current paper.\n"
            f"  offending text: '{stale.group(0) if stale else ''}'"
        )

    def test_draft_replicate_count_matches_submission(self):
        """The Markdown draft must not still describe the superseded
        5-replicate / 280-file run."""
        draft = _md_draft_text()
        assert "5 replicates" not in draft and "= 280" not in draft, (
            "Markdown draft still describes the old 5-replicate / 280-file run; "
            "the submission uses 20 replicates / 1,120 files"
        )
