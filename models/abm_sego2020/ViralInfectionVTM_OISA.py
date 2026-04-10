"""
ViralInfectionVTM_OISA.py — CC3D main script for OISA-coupled Sego2020 ABM.

This file registers ALL original Sego et al. 2020 steppables (ZERO modifications)
plus one additional steppable: OISABridgeSteppable (OISA coupling only — no biology).

Biological equations: UNCHANGED from the published model (commit 5b7e42c).
Lines modified in Sego2020 source: 0.
Lines added here (OISA coupling): ~40.

References:
  - Sego et al. 2020, PLoS Comput Biol 16(11):e1008451.
    DOI: 10.1371/journal.pcbi.1008451
  - Original script: SegoAponte2020/example/ViralInfectionVTM.py (unmodified)
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve Sego2020 path roots using absolute path of this script file.
# NOTE: CC3D exec()s this script, so __file__ may point to sim_runner.py.
#       We use an environment variable or a hard-coded resolution instead.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(os.environ.get(
    "OISA_SCRIPT_DIR",
    Path("/home/drfox/workspace/IDT_sassy_paper/models/abm_sego2020")
))
_SEGO_BASE  = (_SCRIPT_DIR / "sego2020" / "CC3D" / "Models" / "BiocIU"
               / "SARSCoV2MultiscaleVTM" / "Model")
_MODELS_DIR = _SEGO_BASE / "Models"
_SIM_DIR    = _SEGO_BASE / "Simulation"

for p in [str(_MODELS_DIR), str(_SEGO_BASE), str(_SIM_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from ViralInfectionVTMModelInputs import __file__ as _inputs_f
os.environ["ViralInfectionVTM"] = os.path.dirname(os.path.dirname(_inputs_f))

# ---------------------------------------------------------------------------
# CC3D imports
# ---------------------------------------------------------------------------
from cc3d import CompuCellSetup

# ---------------------------------------------------------------------------
# Register ALL original Sego2020 steppables — ZERO CHANGES
# (exact copy of SegoAponte2020/example/ViralInfectionVTM.py registration block)
# ---------------------------------------------------------------------------
from Models.SegoAponte2020.ViralInfectionVTMSteppables import ViralReplicationSteppable
_step = ViralReplicationSteppable(frequency=1)
_step.step_period = 20.0 * 60
_step.voxel_length = 4.0
CompuCellSetup.register_steppable(steppable=_step)

from Models.SegoAponte2020.ViralInfectionVTMSteppables import CellsInitializerSteppable
CompuCellSetup.register_steppable(steppable=CellsInitializerSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ViralInternalizationSteppable
CompuCellSetup.register_steppable(steppable=ViralInternalizationSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ViralSecretionSteppable
CompuCellSetup.register_steppable(steppable=ViralSecretionSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ImmuneCellKillingSteppable
CompuCellSetup.register_steppable(steppable=ImmuneCellKillingSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ChemotaxisSteppable
CompuCellSetup.register_steppable(steppable=ChemotaxisSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ImmuneCellSeedingSteppable
CompuCellSetup.register_steppable(steppable=ImmuneCellSeedingSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import SimDataSteppable
CompuCellSetup.register_steppable(steppable=SimDataSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import CytokineProductionAbsorptionSteppable
CompuCellSetup.register_steppable(steppable=CytokineProductionAbsorptionSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import ImmuneRecruitmentSteppable
CompuCellSetup.register_steppable(steppable=ImmuneRecruitmentSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import oxidationAgentModelSteppable
CompuCellSetup.register_steppable(steppable=oxidationAgentModelSteppable(frequency=1))

from Models.SegoAponte2020.ViralInfectionVTMSteppables import VirusFieldInitializerSteppable
CompuCellSetup.register_steppable(steppable=VirusFieldInitializerSteppable(frequency=1))

# ---------------------------------------------------------------------------
# OISA Bridge — the ONLY addition (no biology, coupling only)
# Frequency = 72 MCS = 72 × 20 min = 24h = one ABM GSimT tick
# ---------------------------------------------------------------------------
sys.path.insert(0, str(_SCRIPT_DIR))
from oisa_bridge_steppable import OISABridgeSteppable
CompuCellSetup.register_steppable(steppable=OISABridgeSteppable(frequency=72))

# ---------------------------------------------------------------------------
# Launch CC3D
# ---------------------------------------------------------------------------
CompuCellSetup.run()
