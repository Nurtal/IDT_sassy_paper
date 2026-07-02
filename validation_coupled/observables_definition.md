# Coupled-System Biological Face-Validity — Design Note

## Purpose
Add a *biological* validation of the **coupled** OISA system (distinct from the
orchestration-correctness validation and from the per-model plausibility checks
already in Table `tab:plausibility`). The claim we can honestly support is
**emergent face-validity**: temporal features that arise from the coupling — and
were *not* fit to any joint dataset — agree with independent published murine
influenza kinetics.

## Emergent observables (measured, not fit)
Extracted from the canonical N=20 ensemble (`results/issl_14d_n20`, 56 ticks ×
20 replicates) and the tri-formalism run:

| ID | Observable | Why emergent |
|----|-----------|--------------|
| O1 | Day of viral peak | ODE-driven; **anchor**, not credited (see circularity) |
| O2 | Day of immune-recruitment peak | ABM recruitment kinetics × coupling; not fit to influenza immune data |
| O3 | Peak-to-peak lag (immune peak − viral peak) | Pure coupling property (transfer lag + recruitment response) |
| O4 | Day of viral clearance (<1% of peak) | Emerges from CTL→clearance feedback edge |
| O5 | Normalised immune rise slope (day1→peak) | Shape of coupled response, scale-free |

All reported as **median [2.5th–97.5th percentile]** across the 20 stochastic
replicates (matches the `ci_95` convention used everywhere else in the paper).

## Anti-circularity strategy (explicit)
1. **Miao 2010 (ODE)** is calibrated against murine *viral-load* data
   (Murphy et al. 1973). Therefore we do **not** claim validation credit for the
   viral-load magnitude or peak timing (O1); O1 serves only as the temporal
   *anchor* against which the immune features are measured.
2. **Sego 2020 (ABM)** derives from a **SARS-CoV-2** tissue simulator
   (Getz et al. 2020) — its immune-recruitment machinery was **not** fit to
   influenza CD8/immune kinetics. Hence O2, O3, O5 (immune-compartment timing
   and shape) are independent of both models' calibration data.
3. **The coupling itself** (κ, N_IMMUNE_TO_CTL scaling, one-tick back-edge lag)
   was set from first principles / sensitivity analysis, **not** fit to any
   joint viral+immune time series. O3 and O4 are therefore genuine coupled-system
   predictions.
4. **Comparison is on timing and normalised shape, never absolute counts.**
   `n_immune` is a CC3D agent count on a 90×90×2 grid, not a physiological CD8
   count per mL; comparing absolute magnitudes would be meaningless. We compare
   *when* (days) and *relative shape* (normalised to each series' own peak).

## Reference data requirement
1–2 published murine influenza A time-course studies reporting **both** viral
titer and CD8/effector kinetics, from sources independent of Murphy 1973 and of
the SARS-CoV-2 Getz lineage. Target features to extract: day of viral peak, day
of CD8/effector peak, peak-to-peak lag, day of viral clearance. If no
sufficiently independent joint time series is accessible, fall back to
consensus physiological ranges (viral peak day 1–3; CD8 peak day 7–10;
clearance day 8–12 in primary murine IAV) with that limitation stated openly.

## Framing for the paper
- This is **weak but real** biological validation of the *coupled* system:
  emergent temporal features match independent data.
- It does **not** upgrade to biological *prediction* — no fit to simultaneous
  in-vivo measurements of this specific coupled configuration.
- Update abstract + "No biological novelty is claimed" paragraph to acknowledge
  emergent face-validity without over-promising; update Limitations.

---

# Implementation record (executed)

## Emergent observables measured (N=20, [2.5,97.5] percentile)
| Observable | Median | CI95 | Role |
|-----------|--------|------|------|
| Viral-peak day (O1) | 2.25 d | [2.25, 2.25] | anchor (NOT credited) |
| Immune-recruitment onset (O3) | 1.0 d | [1.0, 1.0] | emergent |
| Viral clearance <1% peak (O2) | 9.5 d | [9.5, 9.75] | emergent (key coupled prediction) |
| Recruitment delay (O4) | 0.5 d | [0.5, 0.5] | emergent |

NOTE on the immune observable redefinition: n_immune plateaus at 57 agents
(day 13–13.75) and does NOT peak-then-contract within the 14-day window.
Sego2020's n_immune is a generic recruited-immune-cell count, not a CD8
compartment with contraction. Reporting an "immune peak day" would have been a
window-truncation artifact and would have created a false mismatch against
published CD8 peak+contraction (day 8 peak). We therefore report recruitment
ONSET (honest w.r.t. what the ABM represents), not peak.

## Reference datasets selected
- **PRIMARY — Myers, Smith et al. 2021, eLife (10.7554/eLife.68864)**: BALB/cJ,
  75 TCID50 A/PR8. Joint viral titer + total lung CD8 kinetics. Viral peak ~day 2;
  biphasic decline; clearance 60% of mice by day 8, 40% by day 9; CD8 expansion
  5–8 d, peak day 8; model infection duration ~7.8 d. INDEPENDENT of Murphy 1973
  (Miao calibration) and of the SARS-CoV-2 Getz2020 lineage (Sego basis).
- **SECONDARY (innate onset) — Lv et al. 2014, Virol J (10.1186/1743-422X-11-57)**:
  A/PR8 murine, macrophage/neutrophil early accumulation. This is a high-dose
  FATAL model (delayed CD8 d10–14, clearance d12–14) so used ONLY for
  innate-recruitment onset timescale, NOT for clearance timing.
- Innate-onset also cross-referenced to consensus (iwasaki2010innate).

## Anti-circularity verification (in bib)
Confirmed present in references.bib: getz2020sarscov2 (Sego basis = SARS-CoV-2),
miao2010influenza (calibrated on viral load), plus new myers2021influenza,
lv2014kinetics. Coupling constants (κ, _N_IMMUNE_TO_CTL_PER_ML, one-tick lag)
set by first principles + sensitivity sweep, not fit to any joint series.

## Paper integration
- \subsubsection{Coupled-System Biological Face-Validity}\label{sec:coupled-valid}
  → renders as §V-B5, p.8.
- Table IV \label{tab:coupled-valid}; Figure 3 \label{fig:coupled-valid}.
- Abstract: added emergent face-validity sentence (not prediction).
- Limitations: refined first point to state face-validity scope explicitly.
- Recompiled: 11 pages, 0 undefined references/citations, all labels resolve.
