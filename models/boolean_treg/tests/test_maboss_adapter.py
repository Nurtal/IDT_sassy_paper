"""Tests for the MaBoSS Treg OISA adapter (contract + native ci_95 properties)."""
import json
import math
import os

import pytest

import importlib.util
# Adapter lives one level up (models/boolean_treg/); tests live in tests/.
_HERE = os.path.dirname(__file__)
_ADAPTER_DIR = os.path.dirname(_HERE)
_spec = importlib.util.spec_from_file_location("maboss_adapter", os.path.join(_ADAPTER_DIR, "maboss_adapter.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MaBoSSTregAdapter = _mod.MaBoSSTregAdapter
wilson_ci95 = _mod.wilson_ci95


def _ode_issl(infected_fraction):
    return {"export_signals": [
        {"signal_id": "miao2010.viral_load", "value": 9e6, "ci_95": None},
        {"signal_id": "miao2010.infected_fraction", "value": infected_fraction, "ci_95": None}]}


# ---- Wilson interval unit tests --------------------------------------------
def test_wilson_bounded_unit_interval():
    for p in (0.0, 0.01, 0.5, 0.9, 1.0):
        lo, hi = wilson_ci95(p, 10000)
        assert 0.0 <= lo <= hi <= 1.0


def test_wilson_contains_point_estimate():
    for p in (0.1, 0.3, 0.58, 0.9):
        lo, hi = wilson_ci95(p, 20000)
        assert lo <= p <= hi


def test_wilson_width_shrinks_with_n():
    w_small = wilson_ci95(0.5, 1000)
    w_large = wilson_ci95(0.5, 64000)
    assert (w_large[1] - w_large[0]) < (w_small[1] - w_small[0])


def test_wilson_scales_as_inv_sqrt_n():
    # width * sqrt(n) approximately constant
    ws = [(n, (wilson_ci95(0.5, n)[1] - wilson_ci95(0.5, n)[0]) * math.sqrt(n))
          for n in (2000, 8000, 32000)]
    vals = [v for _, v in ws]
    assert max(vals) - min(vals) < 0.05 * max(vals)


def test_wilson_widest_at_half():
    w_half = wilson_ci95(0.5, 10000)
    w_edge = wilson_ci95(0.05, 10000)
    assert (w_half[1] - w_half[0]) > (w_edge[1] - w_edge[0])


# ---- Adapter contract tests -------------------------------------------------
@pytest.fixture(scope="module")
def adapter():
    return MaBoSSTregAdapter(sample_count=10000)


def test_emit_issl_structure(adapter):
    issl = adapter.emit_issl()
    assert set(issl.keys()) >= {"envelope", "continuous_state", "export_signals", "watchdog"}
    assert issl["envelope"]["formalism"] == "BOOLEAN"
    assert issl["envelope"]["model_id"] == "maboss_treg_boolean"


def test_export_signals_present(adapter):
    sigs = {s["signal_id"] for s in adapter.emit_issl()["export_signals"]}
    assert "maboss_treg.treg_fraction" in sigs
    assert "maboss_treg.proliferation" in sigs


def test_ci95_native_present_and_bounded(adapter):
    for cs in adapter.emit_issl()["continuous_state"]:
        ci = cs["ci_95"]
        assert ci is not None and len(ci) == 2
        assert 0.0 <= ci[0] <= ci[1] <= 1.0
        assert "native" in cs["ci_95_source"]


def test_accept_increases_treg_with_antigen():
    a = MaBoSSTregAdapter(sample_count=10000)
    a.accept_issl(_ode_issl(0.0)); a._step(6 * 3600)
    low = a.treg_fraction
    a.accept_issl(_ode_issl(0.6)); a._step(6 * 3600)
    high = a.treg_fraction
    assert high > low


def test_ci95_matches_schema(adapter):
    schema_path = os.path.join(_ADAPTER_DIR, "..", "..", "schemas", "issl_v1.schema.json")
    if not os.path.exists(schema_path):
        pytest.skip("patched schema not colocated")
    schema = json.load(open(schema_path))
    jsonschema = pytest.importorskip("jsonschema")
    a = MaBoSSTregAdapter(sample_count=10000)
    a.accept_issl(_ode_issl(0.5)); a._step(6 * 3600)
    jsonschema.validate(a.emit_issl(), schema)


def test_viral_load_fallback():
    # When infected_fraction absent, viral_load is normalised to an antigen proxy
    a = MaBoSSTregAdapter(sample_count=8000)
    a.accept_issl({"export_signals": [
        {"signal_id": "miao2010.viral_load", "value": 9e6, "ci_95": None}]})
    a._step(6 * 3600)
    assert a.treg_fraction > 0.0
