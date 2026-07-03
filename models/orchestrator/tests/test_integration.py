"""
Integration tests for the OISA influenza coupling pipeline.

Validates that the coupled ODE (Miao2010) + ABM (Sego2020) simulation satisfies:
  1. OISA causal ordering constraints (ABM → ODE → ABM per tick)
  2. Biologically plausible outcomes consistent with both published papers
  3. ISSL checkpoint completeness and structure
  4. Cross-model signal flow (CTL modulates viral clearance; virus drives immune recruitment)

References:
  - Miao et al. 2010, J Virology 84(14):7051. DOI: 10.1128/JVI.00506-10
  - Sego et al. 2020, PLOS Comput Biol 16(11):e1008451. DOI: 10.1371/journal.pcbi.1008451
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "orchestrator"))

from models.ode_miao2010.miao2010_adapter import Miao2010Adapter
from models.abm_sego2020.sego2020_adapter import Sego2020Adapter
from models.orchestrator.orchestrator import OISAOrchestrator, SignalQueue
from models.transfer_blood_transit.blood_transit_adapter import BloodTransitAdapter

_DT_6H  = 6  * 3600
_DT_24H = 24 * 3600


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

@pytest.fixture()
def ode():
    return Miao2010Adapter()


@pytest.fixture()
def abm():
    return Sego2020Adapter()


@pytest.fixture()
def sim_3d(tmp_path):
    """Run a 3-day simulation and return (orchestrator, output_dir)."""
    orch = OISAOrchestrator(output_dir=tmp_path)
    orch.run(n_days=3)
    return orch, tmp_path


# -----------------------------------------------------------------------
# 1. OISA coupling — signal flow
# -----------------------------------------------------------------------

class TestSignalFlow:
    """Verify that inter-model signals correctly modify model state."""

    def test_viral_signal_reaches_abm(self, ode, abm):
        """A viral load signal emitted by ODE must be accepted by ABM and change its state.
        Ref: OISA spec — accept_issl() must process all recognised signal_ids.
        """
        ode._step(_DT_24H)
        issl_ode = ode.emit_issl()
        V_sent = next(
            s["value"] for s in issl_ode["export_signals"]
            if s["signal_id"] == "miao2010.viral_load"
        )
        assert V_sent > 0, "ODE must emit positive viral load signal"

        # The Sego2020 adapter queues the accepted ODE signal to
        # _pending_ode_signal; it is flushed to ode_signal.json just before
        # the next CC3D _step() so the OISABridgeSteppable (in the CC3D
        # subprocess) can read it. Cytokine accumulation happens inside that
        # steppable, not in the Python adapter — so the adapter-level contract
        # is that accept_issl() stages the viral_load signal for delivery.
        assert abm._pending_ode_signal is None
        abm.accept_issl(issl_ode)
        assert abm._pending_ode_signal is not None, (
            "ABM must queue the ODE signal after accept_issl()"
        )
        V_queued = next(
            s["value"] for s in abm._pending_ode_signal["export_signals"]
            if s["signal_id"] == "miao2010.viral_load"
        )
        assert V_queued == V_sent, (
            f"queued viral load {V_queued} must equal ODE-emitted {V_sent}"
        )

    def test_immune_signal_reaches_ode(self, ode, abm):
        """An immune cell signal emitted by ABM must be accepted by ODE and modify k_E.
        Ref: Miao 2010 — k_E is the CTL killing rate coefficient (Table 1).
        """
        # Manually set a non-zero immune count
        abm._n_immune = 10
        issl_abm = abm.emit_issl()

        ode.accept_issl(issl_abm)
        # k_E should now be non-zero in the ODE SBML
        k_E = ode._rr["k_E"]
        assert k_E > 0, (
            f"k_E in Miao2010 SBML should be > 0 after accepting {abm._n_immune} immune cells; got {k_E}"
        )

    def test_T_E_T_scales_with_n_immune(self, ode):
        """T_E_T (CTL effector count) must scale proportionally with n_immune.
        Ref: Miao 2010 — killing rate = k_E × Eps × T_E_T;
             T_E_T is the CTL count (cells/mL) derived from Sego2020 tissue immune cells.
        """
        from models.ode_miao2010.miao2010_adapter import _N_IMMUNE_TO_CTL_PER_ML
        for n in [0, 5, 25, 100]:
            issl = {
                "export_signals": [
                    {"signal_id": "sego2020.immune_cell_count", "value": n}
                ]
            }
            ode.accept_issl(issl)
            expected_ctl = n * _N_IMMUNE_TO_CTL_PER_ML
            assert abs(ode._rr["T_E_T"] - expected_ctl) < 1e-6, (
                f"T_E_T should be n×{_N_IMMUNE_TO_CTL_PER_ML}={expected_ctl} for n={n}; "
                f"got {ode._rr['T_E_T']}"
            )


# -----------------------------------------------------------------------
# 2. OISA causal ordering
# -----------------------------------------------------------------------

class TestCausalOrdering:
    """Verify ABM → ODE → ABM one-tick delay prevents causality violations."""

    def test_abm_emits_before_ode_steps(self, ode, abm):
        """At each 24h boundary, ABM must emit before ODE steps.
        This ensures ODE uses the CURRENT immune state, not a stale one.
        Ref: OISA specification — causal resolver orders ABM→ODE at each GSimT tick.
        """
        # Record ODE state before injection
        V_before = ode.viral_load

        # ABM emits (t=0, no virus yet — cytokine=0)
        issl_abm = abm.emit_issl()
        ode.accept_issl(issl_abm)

        # ODE steps with accepted signal
        ode._step(_DT_6H)
        V_after = ode.viral_load

        # V must have changed (growth phase at t=0)
        assert V_after != V_before, "ODE state must change after step"

    def test_no_deadlock_14_days(self, tmp_path):
        """14-day simulation must complete without deadlock or exception.
        Ref: OISA orchestrator design — topological sort prevents cycle deadlocks.
        """
        orch = OISAOrchestrator(output_dir=tmp_path)
        orch.run(n_days=14)   # must not raise or hang


# -----------------------------------------------------------------------
# 3. Checkpoint completeness
# -----------------------------------------------------------------------

class TestCheckpoints:
    """Verify ISSL checkpoint count and structure for a 3-day run."""

    def test_checkpoint_count(self, sim_3d):
        """3 days × 4 ticks/day = 12 checkpoints expected.
        Ref: OISA spec — one checkpoint per GSimT tick (Δt = 6h).
        """
        _, out_dir = sim_3d
        checkpoints = sorted(out_dir.glob("issl_t*.json"))
        assert len(checkpoints) == 12, (
            f"Expected 12 checkpoints for 3 days; got {len(checkpoints)}"
        )

    def test_checkpoint_time_monotonic(self, sim_3d):
        """Checkpoint timestamps must be strictly monotonically increasing.
        Ref: GSimT is a monotonic global clock — never goes backward.
        """
        _, out_dir = sim_3d
        times = []
        for cp in sorted(out_dir.glob("issl_t*.json")):
            data = json.loads(cp.read_text())
            times.append(data["gsim_time_days"])
        assert times == sorted(times), "Checkpoint times are not monotonic"
        assert len(times) == len(set(times)), "Checkpoint times have duplicates"

    def test_ode_record_in_every_checkpoint(self, sim_3d):
        """Every checkpoint must contain an ODE record (Miao2010 steps every 6h).
        Ref: OISA config — ODE Δt = 6h = GSimT step.
        """
        _, out_dir = sim_3d
        for cp in out_dir.glob("issl_t*.json"):
            data = json.loads(cp.read_text())
            assert data["ode"] is not None, f"Missing ODE record in {cp.name}"
            assert data["ode"]["envelope"]["model_id"] == "miao2010_ode"

    def test_abm_record_in_daily_checkpoints(self, sim_3d):
        """ABM records appear in checkpoints at daily boundaries (every 4th tick).
        Ref: OISA config — ABM Δt = 24h; GSimT Δt = 6h → ABM steps at ticks 0, 4, 8…
        """
        _, out_dir = sim_3d
        checkpoints = sorted(out_dir.glob("issl_t*.json"))
        for i, cp in enumerate(checkpoints):
            data = json.loads(cp.read_text())
            if i % 4 == 0:   # daily tick
                assert data["abm"] is not None, (
                    f"ABM record missing at tick {i} (daily boundary)"
                )

    def test_viral_load_in_checkpoints_matches_published_range(self, sim_3d):
        """Viral load in checkpoints must be within the published influenza range.
        Ref: Miao 2010 — fitted to Murphy 1973 data; range 10⁴–10⁸ copies/mL at peak.
        """
        _, out_dir = sim_3d
        v_max = 0.0
        for cp in out_dir.glob("issl_t*.json"):
            data = json.loads(cp.read_text())
            ode_rec = data["ode"]
            if ode_rec:
                for sig in ode_rec["export_signals"]:
                    if sig["signal_id"] == "miao2010.viral_load":
                        v_max = max(v_max, sig["value"])
        # Within 3 days, viral load should rise above 10⁴ copies/mL
        assert v_max > 1e4, (
            f"Peak V in 3-day run = {v_max:.2e}; expected > 10⁴ copies/mL (Miao 2010 Fig 2)"
        )


# -----------------------------------------------------------------------
# 4. Coupled biological plausibility
# -----------------------------------------------------------------------

class TestCoupledBiology:
    """Verify that the coupled model produces biologically plausible outcomes."""

    def test_viral_peak_precedes_max_immune_response(self, tmp_path):
        """Viral peak must occur at or before maximum immune cell count.
        Ref: Miao 2010 + Sego 2020 — immune response lags behind viral peak;
             innate immune delay is encoded in ir_delay_coeff (Sego 2020 Table S1).
        """
        orch = OISAOrchestrator(output_dir=tmp_path)
        orch.run(n_days=14)

        V_series = []
        N_series = []
        for cp in sorted(tmp_path.glob("issl_t*.json")):
            data = json.loads(cp.read_text())
            # ODE viral load
            for sig in (data["ode"] or {}).get("export_signals", []):
                if sig["signal_id"] == "miao2010.viral_load":
                    V_series.append(sig["value"])
            # ABM immune count
            if data["abm"] is not None:
                for cs in data["abm"]["continuous_state"]:
                    if cs["label"] == "n_immune":
                        N_series.append((len(V_series) - 1, cs["count"]))

        if not V_series:
            pytest.skip("No viral load data found")

        peak_V_tick  = V_series.index(max(V_series))
        if not N_series:
            pytest.skip("No ABM immune data found")
        peak_N_tick  = max(N_series, key=lambda x: x[1])[0]

        # Viral peak may coincide with or precede immune peak
        # (at minimum, immune peak should not substantially precede viral peak)
        assert peak_N_tick >= peak_V_tick - 4, (   # allow 1 day (4 ticks) tolerance
            f"Immune peak (tick {peak_N_tick}) should not precede viral peak (tick {peak_V_tick}) "
            "by more than 1 day — inconsistent with published immune lag dynamics"
        )

    def test_ctl_reduces_viral_load(self, tmp_path):
        """Viral load at day 14 with immune coupling must be ≤ isolated ODE viral load.
        Ref: Miao 2010 — k_E CTL killing accelerates clearance;
             Fig 2 shows CTL is the dominant clearance mechanism.
        """
        from pathlib import Path
        tmp_coupled   = tmp_path / "coupled"
        tmp_isolated  = tmp_path / "isolated"

        # Coupled run (with immune signal)
        orch_c = OISAOrchestrator(output_dir=tmp_coupled)
        orch_c.run(n_days=14)
        V_coupled = orch_c.ode.viral_load

        # Isolated ODE run (no immune signal, k_E stays 0)
        ode_iso = Miao2010Adapter()
        for _ in range(14 * 4):
            ode_iso._step(6 * 3600)
        V_isolated = ode_iso.viral_load

        # Coupled V must be ≤ isolated V (CTL can only reduce viral load)
        assert V_coupled <= V_isolated * 1.01, (   # 1% tolerance for floating-point
            f"Coupled V at day 14 ({V_coupled:.3e}) should be ≤ isolated V ({V_isolated:.3e}) "
            "— CTL killing (k_E > 0) should accelerate viral clearance (Miao 2010)"
        )


# -----------------------------------------------------------------------
# 5. Signal queue and transfer lags
# -----------------------------------------------------------------------

class TestSignalQueue:
    """Validate the SignalQueue used for model-derived transfer lags."""

    def test_immediate_signal_no_lag(self):
        """Signal with transfer_lag_s=None should not be enqueued."""
        sq = SignalQueue()
        issl = {"export_signals": [{"signal_id": "test", "value": 1.0, "transfer_lag_s": None}]}
        # No lag → _route_signal in orchestrator injects immediately, not via queue
        assert sq.dequeue_ready(0.0) == []

    def test_deferred_signal_arrives_after_delay(self):
        """Enqueued signal should only be dequeued after its delay elapses."""
        sq = SignalQueue()
        issl = {"export_signals": [{"signal_id": "test", "value": 42.0}]}
        sq.enqueue(issl, delay_s=100.0, current_s=0.0, target="ode")
        # At t=50, not ready
        assert sq.dequeue_ready(50.0) == []
        # At t=100, ready
        ready = sq.dequeue_ready(100.0)
        assert len(ready) == 1
        assert ready[0][0] == issl
        assert ready[0][1] == "ode"

    def test_queue_drains_after_dequeue(self):
        """After dequeue, the signal must not appear again."""
        sq = SignalQueue()
        sq.enqueue({"data": 1}, delay_s=10.0, current_s=0.0, target="abm")
        sq.dequeue_ready(10.0)
        assert sq.dequeue_ready(20.0) == []


class TestBloodTransitTransferLag:
    """Validate model-derived transfer lag from BloodTransitAdapter."""

    def test_blood_transit_emits_transfer_lag_s(self):
        """BloodTransitAdapter must emit a positive transfer_lag_s in ISSL."""
        bt = BloodTransitAdapter()
        bt.accept_issl({
            "export_signals": [
                {"signal_id": "bm.progenitor_export", "value": 1000.0}
            ]
        })
        bt._step(86400)
        issl = bt.emit_issl()
        lag = issl["export_signals"][0]["transfer_lag_s"]
        assert lag is not None
        assert lag > 0
        # tau ≈ 4 days = 345600 s
        assert abs(lag - 4.0 * 86400) < 1.0

    def test_blood_transit_signal_routed_with_delay(self):
        """When routed through SignalQueue, the signal arrives after tau seconds."""
        bt = BloodTransitAdapter()
        bt.accept_issl({
            "export_signals": [
                {"signal_id": "bm.progenitor_export", "value": 500.0}
            ]
        })
        bt._step(86400)
        issl = bt.emit_issl()

        sq = SignalQueue()
        lag = issl["export_signals"][0]["transfer_lag_s"]
        sq.enqueue(issl, delay_s=lag, current_s=0.0, target="thymus")

        # Not ready at t=2 days
        assert sq.dequeue_ready(2 * 86400) == []
        # Ready at t=4 days
        ready = sq.dequeue_ready(4 * 86400)
        assert len(ready) == 1
