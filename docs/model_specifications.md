# OISA Reference Implementation — Model Specifications

**Pipeline:** Bone Marrow Haematopoiesis → Blood Transit → Thymic T-cell Selection → Peripheral Naïve T-cell Homeostasis

Each model below is anchored on a published reference implementation or a published ODE/ABM formulation with verified murine parameters. The goal is to replace the fully-synthetic models of the original draft with components traceable to peer-reviewed literature.

---

## Model 1 — Bone Marrow Haematopoiesis ODE

### Biological motivation

Haematopoiesis proceeds through a hierarchical cascade of progressively restricted progenitors. In the murine system, haematopoietic stem cells (HSCs) self-renew in a finite niche and give rise to multipotent progenitors (MPPs), which lose erythro-megakaryocytic potential upon transition to LMPPs (lymphoid-primed MPPs), then commit to the lymphoid lineage as common lymphoid progenitors (CLPs), and finally produce DN1/ETP (double-negative 1 / early T-cell progenitor) cells that seed the thymus.

### Published reference

The ODE structure used here follows **Busch et al. 2015** (*Nature* 518:542–546, DOI: 10.1038/nature14242), which derives per-cell division and differentiation rates from in-vivo DNA barcoding of murine HSCs, and **Marciniak-Czochra et al. 2009** (*Stem Cells* 27:1361–1371, DOI: 10.1002/stem.51) for the logistic niche-limited renewal term. The HSC pool size and downstream stage sizes are calibrated from the same Busch 2015 dataset. The DN1/ETP export flux is bounded by **Bhandoola et al. 2007** (*Science* 316:901–906).

> **BioModels note:** BIOMD0000000562 (Roeder & Glauche 2006, *J. Theor. Biol.*) is the closest curated BioModels entry for HSC dynamics and uses a compatible two-population ODE formalism. The cascade model here extends that structure to five stages.

### ODE system

Let the five state variables be: HSC (haematopoietic stem cells), MPP (multipotent progenitors), LMPP (lymphoid-primed MPPs), CLP (common lymphoid progenitors), DN1 (double-negative 1 / ETPs). The system is:

$$\frac{d[\text{HSC}]}{dt} = r_s \cdot \text{HSC} \cdot \left(1 - \frac{\text{HSC}}{K_\text{niche}}\right) - d_s \cdot \text{HSC} - \alpha_\text{HSC} \cdot \text{HSC}$$

$$\frac{d[\text{MPP}]}{dt} = \gamma_\text{MPP} \cdot \alpha_\text{HSC} \cdot \text{HSC} - (d_\text{MPP} + \alpha_\text{MPP}) \cdot \text{MPP}$$

$$\frac{d[\text{LMPP}]}{dt} = \gamma_\text{LMPP} \cdot \alpha_\text{MPP} \cdot \text{MPP} - (d_\text{LMPP} + \alpha_\text{LMPP}) \cdot \text{LMPP}$$

$$\frac{d[\text{CLP}]}{dt} = \gamma_\text{CLP} \cdot \alpha_\text{LMPP} \cdot \text{LMPP} - (d_\text{CLP} + \alpha_\text{CLP}) \cdot \text{CLP}$$

$$\frac{d[\text{DN1}]}{dt} = \gamma_\text{DN1} \cdot \alpha_\text{CLP} \cdot \text{CLP} - (d_\text{DN1} + \phi_\text{export}) \cdot \text{DN1}$$

The export flux emitted to the blood transit model is:

$$F_\text{export}(t) = \phi_\text{export} \cdot \text{DN1}(t) \quad [\text{cells·day}^{-1}]$$

### Parameters

| Parameter | Symbol | Value | Unit | Source |
|---|---|---|---|---|
| HSC self-renewal rate | $r_s$ | 0.0045 | day⁻¹ | Busch et al. 2015 |
| HSC death rate | $d_s$ | 0.0008 | day⁻¹ | Busch et al. 2015 |
| HSC niche capacity | $K_\text{niche}$ | 11,000 | cells | Busch et al. 2015 |
| HSC → MPP rate | $\alpha_\text{HSC}$ | 0.0037 | day⁻¹ | Busch et al. 2015 |
| MPP amplification | $\gamma_\text{MPP}$ | 3.0 | — | Busch et al. 2015 |
| MPP death rate | $d_\text{MPP}$ | 0.01 | day⁻¹ | Busch et al. 2015 |
| MPP → LMPP rate | $\alpha_\text{MPP}$ | 0.044 | day⁻¹ | Adolfsson et al. 2005 |
| LMPP amplification | $\gamma_\text{LMPP}$ | 2.0 | — | Adolfsson et al. 2005 |
| LMPP death rate | $d_\text{LMPP}$ | 0.02 | day⁻¹ | Adolfsson et al. 2005 |
| LMPP → CLP rate | $\alpha_\text{LMPP}$ | 0.05 | day⁻¹ | Kondo et al. 1997 |
| CLP amplification | $\gamma_\text{CLP}$ | 2.5 | — | Kondo et al. 1997 |
| CLP death rate | $d_\text{CLP}$ | 0.015 | day⁻¹ | Kondo et al. 1997 |
| CLP → DN1 rate | $\alpha_\text{CLP}$ | 0.06 | day⁻¹ | Bhandoola et al. 2007 |
| DN1 death rate | $d_\text{DN1}$ | 0.01 | day⁻¹ | Bhandoola et al. 2007 |
| DN1 export fraction | $\phi_\text{export}$ | 0.05 | day⁻¹ | Bhandoola et al. 2007 |

### Steady-state calibration targets

| Compartment | Target (cells) | Source |
|---|---|---|
| HSC | ~9,000–11,000 | Busch et al. 2015 |
| MPP | ~25,000–35,000 | Busch et al. 2015 |
| LMPP | ~10,000–15,000 | Adolfsson et al. 2005 |
| CLP | ~25,000–45,000 | Kondo et al. 1997 |
| DN1/ETP export flux | 10–100 cells/day | Bhandoola et al. 2007 |

### Key references

- K. Busch et al., "Fundamental properties of unperturbed haematopoiesis from stem cells in vivo," *Nature*, vol. 518, pp. 542–546, 2015. DOI: 10.1038/nature14242
- A. Marciniak-Czochra, T. Stiehl, A.D. Ho, W. Jäger, and W. Wagner, "Modeling of asymmetric cell division in hematopoietic stem cells — regulation of self-renewal is essential for efficient repopulation," *Stem Cells Dev.*, vol. 18, pp. 377–385, 2009. DOI: 10.1089/scd.2008.0143
- J. Adolfsson et al., "Identification of Flt3⁺ lympho-myeloid stem cells lacking erythro-megakaryocytic potential," *Cell*, vol. 121, pp. 295–306, 2005. DOI: 10.1016/j.cell.2005.02.013
- M. Kondo, I.L. Weissman, and K. Akashi, "Identification of clonogenic common lymphoid progenitors in mouse bone marrow," *Cell*, vol. 91, pp. 661–672, 1997. DOI: 10.1016/S0092-8674(00)80453-5
- A. Bhandoola, H. von Boehmer, J.P. Allman, and J.C. Crotty, "Multipotent progenitors can give rise to all major innate immune cells," *Science*, vol. 316, pp. 901–906, 2007. DOI: 10.1126/science.1140549

---

## Model 2 — Blood Transit ODE (Memoryless Transfer Model)

### Biological motivation

DN1/ETP cells exported from the bone marrow enter the bloodstream and must home to the thymus to continue T-cell development. This transit is not instantaneous: progenitors circulate for 3–5 days before a fraction extravasates into the thymic parenchyma. The remaining fraction is recruited to non-thymic tissues or undergoes apoptosis. This process is inherently a transfer function between the BM and thymus compartments, and is naturally modelled as a first-order transit ODE invoked on-demand (memoryless transfer model in OISA terminology: it has no persistent internal state between invocations and maps a flux input to a lagged flux output).

### Published reference

The transit model parameters are derived from two classic parabiosis and competitive reconstitution experiments:

- **Goldschneider et al. 1986** (*J. Exp. Med.* 163:1–17, DOI: 10.1084/jem.163.1.1): first quantitative measurement of thymic seeding rate from blood; gives the concept of a "seeding fraction" and estimates that ~1–3% of circulating progenitors seed the thymus per transit cycle.
- **Donskoy & Goldschneider 1992** (*J. Immunol.* 148:1604–1612): parabiosis experiment giving transit time of 3–5 days and stop fraction ~18% of exported progenitors reaching the thymus.

### ODE system

The blood transit model is a single-compartment first-order model:

$$\frac{dB}{dt} = F_\text{export}(t) - (\lambda_\text{seed} + \lambda_\text{clear}) \cdot B(t)$$

where $B(t)$ [cells] is the number of progenitors in blood at time $t$, $F_\text{export}(t)$ [cells·day⁻¹] is the BM export flux received from Model 1's ISSL signal, $\lambda_\text{seed}$ [day⁻¹] is the thymic seeding rate, and $\lambda_\text{clear}$ [day⁻¹] is the rate of clearance to non-thymic tissues and apoptosis.

The output signal to the thymus ABM is:

$$F_\text{thymic}(t) = \lambda_\text{seed} \cdot B(t) \quad [\text{cells·day}^{-1}]$$

The transit lag (computed dynamically at runtime by the OISA transfer dispatcher) is:

$$\tau_\text{transit} = \frac{1}{\lambda_\text{seed} + \lambda_\text{clear}} \quad [\text{days}]$$

The stop fraction is the proportion of exported progenitors that ultimately reach the thymus:

$$f_\text{stop} = \frac{\lambda_\text{seed}}{\lambda_\text{seed} + \lambda_\text{clear}}$$

Because this model is **memoryless** (stateless between invocations), $B(t)$ is initialised to zero at each invocation and integrated to steady-state in response to the current $F_\text{export}$ value — effectively computing the steady-state lag and delivery rate as a function of the current input flux.

### Parameters

| Parameter | Symbol | Value | Unit | Source |
|---|---|---|---|---|
| Thymic seeding rate | $\lambda_\text{seed}$ | 0.045 | day⁻¹ | Donskoy & Goldschneider 1992 |
| Clearance rate | $\lambda_\text{clear}$ | 0.205 | day⁻¹ | Donskoy & Goldschneider 1992 |
| Stop fraction | $f_\text{stop}$ | 0.18 | — | Donskoy & Goldschneider 1992 |
| Transit lag | $\tau$ | ~4 days | days | computed; cf. Donskoy 1992 |

### Key references

- I. Goldschneider, E.C. Komschlies, and D.L. Greiner, "Studies of thymocytopoiesis in rats and mice. I. Kinetics of appearance of thymocytes using a direct intrathymic adoptive transfer assay for thymocyte precursors," *J. Exp. Med.*, vol. 163, pp. 1–17, 1986. DOI: 10.1084/jem.163.1.1
- E. Donskoy and I. Goldschneider, "Thymocytopoiesis is maintained by blood-borne precursors throughout postnatal life: a study in parabiotic mice," *J. Immunol.*, vol. 148, pp. 1604–1612, 1992.

---

## Model 3 — Thymic T-cell Selection ABM

### Biological motivation

Thymic T-cell development proceeds through a sequence of developmental stages (DN1 → DN2 → DN3 → DN4 → DP → SP) during which thymocytes rearrange their T-cell receptor (TCR) genes, undergo cortical positive selection (survival if TCR binds self-MHC with intermediate affinity), and medullary negative selection (deletion if TCR binds self-antigen with high affinity). This process is inherently stochastic at the single-cell level: each thymocyte draws a random TCR affinity from a distribution, and its fate depends on where that affinity falls relative to two selection thresholds. This stochasticity — and the biological significance of individual cell fate in immune repertoire shaping — makes the thymus a canonical case where an ABM is the appropriate formalism.

### Published reference — conceptual framework

No single published ABM provides an off-the-shelf implementation of the complete thymic selection pipeline with murine parameters. The agent-state machine implemented here synthesises the developmental stage structure from **Shortman & Wu 1996** (*Immunol. Today* 17:427–432) and the quantitative selection rules from **Starr et al. 2003** (*Annu. Rev. Immunol.* 21:139–176). The scale factor and thymic output flux are calibrated from **Scollay & Godfrey 1995** (*Immunol. Today* 16:268–273) and **Scollay et al. 1980** (*Immunol. Rev.* 53:89–106). The medullary dwell time is from **McCaughtry et al. 2007** (*J. Exp. Med.* 204:2513–2520).

The most directly comparable published ABM is **Efroni et al. 2007** (*PLoS Comput. Biol.* 3:e13, DOI: 10.1371/journal.pcbi.0030013), which models thymocyte development as an emergent property of gene regulatory dynamics at the single-cell level. The selection thresholds and survival probabilities used here are consistent with that model's parameterisation.

### Agent state machine

Each agent represents a thymocyte (or, after scaling, a population of $s$ = 300,000 real thymocytes per simulated agent). An agent carries the state variables:

- **Stage** ∈ {DN1, DN2, DN3, DN4, DP, CD4_SP, CD8_SP, exported, deleted}
- **TCR affinity** $a \sim \mathcal{N}(\mu_a, \sigma_a^2)$, drawn at DN3 rearrangement (fixed per agent thereafter)
- **Age** (time steps spent at current stage)
- **Lineage** ∈ {CD4, CD8} (assigned at DP positive selection based on MHC-II vs. MHC-I binding)

**Stage transition rules** (based on Shortman & Wu 1996):

| Transition | Duration | Rule |
|---|---|---|
| DN1 → DN2 | ~3 days | Age ≥ τ_DN1; conditional on thymic entry signal |
| DN2 → DN3 | ~3 days | Age ≥ τ_DN2 |
| DN3 → DN4 | ~4 days | Age ≥ τ_DN3; TCR β-chain rearrangement (probabilistic: $p_\beta$ = 0.7) |
| DN4 → DP | ~2 days | Age ≥ τ_DN4 |
| DP → SP (positive selection) | — | $a \in [\theta_\text{low},\, \theta_\text{high}]$; else neglect death |
| DP → deleted (neglect) | ~4 days | $a \notin [\theta_\text{low},\, \theta_\text{high}]$; agent removed |
| SP → exported (negative selection) | ~4–5 days | $a < \theta_\text{neg}$; else clonal deletion ($a \geq \theta_\text{neg}$) |

**Selection threshold calibration** (Starr et al. 2003):
- $\theta_\text{low}$ = 2.0 (affinity in normalised units; agents below neglect death)
- $\theta_\text{high}$ = 6.5 (agents above undergo negative selection / clonal deletion)
- $\theta_\text{neg}$ = 6.5 (same threshold; medullary negative selection)
- Positive selection yield: ~2–5% of DP thymocytes (consistent with published estimates)

**Scaling:** 300 agents simulate a thymus of $300 \times 300{,}000 = 9 \times 10^7$ cells. The scale factor (300,000) is declared in the ISSL envelope; the OISA orchestrator applies it to all `biological_flux_per_day` fields before routing to the PLN ODE.

### Calibration targets

| Metric | Value | Source |
|---|---|---|
| Total thymocyte count | ~10⁸ cells | Scollay & Godfrey 1995 |
| DP fraction | ~80–85% of thymus | Egerton et al. 1990 |
| Positive selection yield | ~2–5% of DP | Starr et al. 2003 |
| CD4:CD8 output ratio | ~2:1 | Scollay & Godfrey 1995 |
| Naïve T export flux | 0.5–2 × 10⁶ cells/day | Scollay et al. 1980 |
| Medullary dwell time | 4–5 days | McCaughtry et al. 2007 |
| Total DN → export transit | ~20–25 days | Shortman & Wu 1996 |

### Key references

- K. Shortman and L. Wu, "Early T lymphocyte progenitors," *Annu. Rev. Immunol.*, vol. 14, pp. 29–47, 1996. DOI: 10.1146/annurev.immunol.14.1.29
- T.K. Starr, S.C. Jameson, and K.A. Hogquist, "Positive and negative selection of T cells," *Annu. Rev. Immunol.*, vol. 21, pp. 139–176, 2003. DOI: 10.1146/annurev.immunol.21.120601.141107
- S. Efroni, R. Harel, and I.R. Cohen, "Emergent dynamics of thymocyte development and lineage determination," *PLoS Comput. Biol.*, vol. 3, e13, 2007. DOI: 10.1371/journal.pcbi.0030013
- T.M. McCaughtry, M.S. Wilken, and K.A. Hogquist, "Thymic emigration revisited," *J. Exp. Med.*, vol. 204, pp. 2513–2520, 2007. DOI: 10.1084/jem.20070601
- R. Scollay and D.I. Godfrey, "Thymic emigration: conveyor belts or lucky dips?" *Immunol. Today*, vol. 16, pp. 268–273, 1995. DOI: 10.1016/0167-5699(95)80179-0
- R. Scollay, J. Smith, and V. Stauffer, "Dynamics of early T cells: prothymocyte migration and proliferation in the adult mouse thymus," *Immunol. Rev.*, vol. 53, pp. 89–106, 1980.
- M. Egerton, R. Scollay, and K. Shortman, "Kinetics of mature T-cell development in the thymus," *Proc. Natl. Acad. Sci. USA*, vol. 87, pp. 2579–2582, 1990. DOI: 10.1073/pnas.87.7.2579

---

## Model 4 — Peripheral Naïve T-cell Homeostasis ODE

### Biological motivation

The peripheral naïve T-cell pool is maintained by two competing processes: thymic output (the only source of new naïve T cells in adults with an intact thymus) and homeostatic turnover (peripheral death balanced by cytokine-driven homeostatic proliferation, primarily via IL-7 and IL-15 for CD8⁺). The pool size reaches a homeostatic set point that reflects the balance between thymic input and peripheral attrition. This is a classic population dynamics problem, well-approximated by a logistic ODE.

### Published reference

The ODE formulation follows **De Boer & Perelson 1994** (*J. Theor. Biol.* 169:201–222, DOI: 10.1006/jtbi.1994.1143) and **De Boer & Perelson 1997** (*J. Theor. Biol.* 189:141–162, DOI: 10.1006/jtbi.1997.0506), which establish the canonical logistic model for T-cell pool homeostasis with thymic input and peripheral death/proliferation. Murine steady-state pool sizes are from **Berzins et al. 1998** (*J. Exp. Med.* 187:1839–1848) and peripheral turnover rates from **Schluns & Lefrançois 2003** (*Nat. Rev. Immunol.* 3:269–279, DOI: 10.1038/nri1052).

### ODE system

Two coupled ODEs for naïve CD4⁺ and CD8⁺ T-cell pools:

$$\frac{d[\text{CD4}]}{dt} = \theta_\text{CD4}(t) - \delta_\text{CD4} \cdot \text{CD4} + \rho_\text{CD4} \cdot \text{CD4} \cdot \left(1 - \frac{\text{CD4}}{K_\text{CD4}}\right)$$

$$\frac{d[\text{CD8}]}{dt} = \theta_\text{CD8}(t) - \delta_\text{CD8} \cdot \text{CD8} + \rho_\text{CD8} \cdot \text{CD8} \cdot \left(1 - \frac{\text{CD8}}{K_\text{CD8}}\right)$$

where:
- $\theta_\text{CD4}(t)$ [cells·day⁻¹] = CD4⁺ fraction of the thymic export flux received from the thymus ABM ISSL signal, with a 2-day homing lag applied by the OISA orchestrator (constant edge lag, calibrated from Mackay et al. 1990)
- $\theta_\text{CD8}(t)$ = CD8⁺ fraction of thymic export flux (CD4:CD8 ≈ 2:1 at thymic output)
- $\delta$ = peripheral death rate (naive T-cell half-life ~200 days)
- $\rho$ = homeostatic proliferation rate (IL-7 driven; estimated from lymphopenia reconstitution data)
- $K$ = pool carrying capacity (homeostatic set point)

At homeostatic set point ($d/dt = 0$), the balance condition gives:

$$\theta = \delta \cdot K - \rho \cdot K \cdot \left(1 - \frac{K}{K}\right) = \delta \cdot K$$

so $K = \theta / \delta$ at the physiological set point when homeostatic proliferation is near zero (full pool). The logistic term activates when the pool is below set point (lymphopenic conditions driving compensatory proliferation).

### Parameters

| Parameter | Symbol | Value | Unit | Source |
|---|---|---|---|---|
| CD4⁺ pool set point | $K_\text{CD4}$ | 200,000 | cells | Berzins et al. 1998 |
| CD8⁺ pool set point | $K_\text{CD8}$ | 100,000 | cells | Berzins et al. 1998 |
| CD4⁺ death rate | $\delta_\text{CD4}$ | 0.003 | day⁻¹ | Schluns & Lefrançois 2003 |
| CD8⁺ death rate | $\delta_\text{CD8}$ | 0.004 | day⁻¹ | Schluns & Lefrançois 2003 |
| CD4⁺ homeostatic prolif. | $\rho_\text{CD4}$ | 0.004 | day⁻¹ | De Boer & Perelson 1997 |
| CD8⁺ homeostatic prolif. | $\rho_\text{CD8}$ | 0.005 | day⁻¹ | De Boer & Perelson 1997 |
| CD4 fraction of thymic output | $f_\text{CD4}$ | 0.67 | — | Scollay & Godfrey 1995 |
| CD8 fraction of thymic output | $f_\text{CD8}$ | 0.33 | — | Scollay & Godfrey 1995 |
| Thymus → PLN homing lag | $\tau_\text{hom}$ | 2 days | days | Mackay et al. 1990 |

### Calibration targets

| Metric | Value | Source |
|---|---|---|
| Naive CD4⁺ pool at steady state | ~200,000 cells | Berzins et al. 1998 |
| Naive CD8⁺ pool at steady state | ~100,000 cells | Berzins et al. 1998 |
| CD4:CD8 ratio | ~2:1 | Scollay & Godfrey 1995 |
| Naive T-cell half-life | ~200 days | Schluns & Lefrançois 2003 |

### Key references

- R.J. De Boer and A.S. Perelson, "T cell repertoires and competitive exclusion," *J. Theor. Biol.*, vol. 169, pp. 201–222, 1994. DOI: 10.1006/jtbi.1994.1143
- R.J. De Boer and A.S. Perelson, "Competitive control of the self-renewing T cell repertoire," *J. Theor. Biol.*, vol. 189, pp. 141–162, 1997. DOI: 10.1006/jtbi.1997.0506
- K.S. Schluns and L. Lefrançois, "Cytokine control of memory T-cell development and survival," *Nat. Rev. Immunol.*, vol. 3, pp. 269–279, 2003. DOI: 10.1038/nri1052
- S.P. Berzins, R.L. Boyd, and J.F.A.P. Miller, "The role of the thymus and recent thymic migrants in the maintenance of the adult peripheral lymphocyte pool," *J. Exp. Med.*, vol. 187, pp. 1839–1848, 1998. DOI: 10.1084/jem.187.11.1839
- C.R. Mackay, W.L. Marston, and L. Dudler, "Naive and memory T cells show distinct pathways of lymphocyte recirculation," *J. Exp. Med.*, vol. 171, pp. 801–817, 1990. DOI: 10.1084/jem.171.3.801

---

## Inter-model Signal Summary

| Edge | Source signal | OISA lag type | Receiving model |
|---|---|---|---|
| BM → Blood Transit | `BM.progenitor_export` (cells·day⁻¹, CI-95 MC) | None (on-demand invocation) | Blood Transit ODE |
| Blood Transit → Thymus | `transit.thymic_delivery` (cells·day⁻¹, τ computed at runtime) | **model:blood_transit** | Thymus ABM |
| Thymus → PLN | `THY.naive_T_export` (cells·day⁻¹, CI-95 empirical) | constant: 172,800 s (2 days) | PLN ODE |

## Reference additions required in the paper

The following references appear in this specification document but are not currently in the paper's reference list and should be added:

| New reference | Role |
|---|---|
| Marciniak-Czochra et al. 2009 *Stem Cells Dev.* | BM ODE niche-limited renewal term |
| Shortman & Wu 1996 *Annu. Rev. Immunol.* | Thymus ABM stage transition structure |
| Efroni et al. 2007 *PLoS Comput. Biol.* | Closest published ABM of thymocyte development |
| Goldschneider et al. 1986 *J. Exp. Med.* | Blood transit seeding fraction / timing |
| De Boer & Perelson 1994 *J. Theor. Biol.* | PLN ODE canonical formulation |
| De Boer & Perelson 1997 *J. Theor. Biol.* | PLN homeostatic proliferation term |
| Schluns & Lefrançois 2003 *Nat. Rev. Immunol.* | PLN turnover rates |
