# OISA paper — pre-submission credibility audit (IEEE BIBM 2026)

Scope: reference integrity, numeric reproducibility, build verification, and
**hard 8-page fit** for `paper/main.tex` + `paper/references.bib`. All source
edits are in the working tree (uncommitted). The PDF was recompiled and
verified at each stage.

**FINAL STATUS: 8 pages including references — meets the IEEE BIBM hard limit
with no over-length fee.** 57/57 consistency tests pass; 79 adapter tests
present. No undefined references or citations; no LaTeX warnings.

---

## A. The four original fixes (all resolved)

| # | Fix | Status | Verification |
|---|-----|--------|--------------|
| 1 | **Shrink to hard 8 pages** (incl. references) | **DONE** | `pypdf` page count = 8; references end on page 8, no spill to page 9 |
| 2 | **TregModel citation** | DONE | Boolean Treg model cited to pyMaBoSS reference suite (`TregModel_InitPop.bnd`, 35 nodes); primary-source `%%TODO(NF)` comments removed and replaced with prose |
| 3 | **Repository URL** | DONE | `https://github.com/Nurtal/IDT_sassy_paper` present in Data/Code section |
| 4 | **Test drift** | DONE | `.md` said "67 tests" (stale) vs `main.tex` "79"; reconciled — 79 = 23 ODE + 20 ABM + 11 Boolean + 8 blood-transit + 17 integration. Consistency suite = 57 tests (all pass) |

### Fix 1 detail — how the paper reached 8 pages
The paper began at 11 pages (references on page 11). Reduction was
**content-preserving throughout**: no number, claim, or citation was dropped.
Levers used, in order of impact:
1. **Prose tightening across all sections** (~1 page reclaimed): removed
   redundant phrasings, tightened multi-clause sentences, without losing any
   quantitative content.
2. **Figure resizing** (decisive for the final page): `oisa_workflow.pdf`
   0.9→0.74 columnwidth; `tri_formalism_trajectory.pdf` (tall 3-panel, the
   largest vertical object on page 7) 0.9→**0.59** columnwidth — the maximum
   width that holds 8 pages, confirmed by fine sweep. Legibility verified at
   print resolution: all three panel titles, axis labels, curves, and legends
   remain readable.
3. **Table IV `\arraystretch`** 1.15→1.0.
4. **Removed one duplicated novelty sentence** from Results — the identical
   "first heterogeneous cross-formalism runtime UQ" claim already appears in the
   abstract and introduction, so the claim is fully preserved (stated twice
   still).

Every headline number was re-verified present in the final source: peak V
9.00/9.09×10⁶ copies/mL, day 2.25, 4.57×10³ at day 13.75, κ=3.5×10⁻⁷, r=0.93,
56 checkpoints, 168 tri-run ISSL records, 1,120 ISSL files, 79 tests, 35-node
Boolean model. Citation set is byte-identical to git HEAD (diff empty).

---

## B. The seven author editorial edits (all applied)

| # | Edit | Status |
|---|------|--------|
| a | Title → *OISA: Orchestrating Published Immune Models Without Modification* | DONE |
| b | Abstract: Vivarium naming removed | DONE |
| c | All prose em-dashes → commas (protected: Table 1 ``---'' marker + table-cell `& --- \\`) | DONE |
| d | Table 1 caption parenthetical removed | DONE |
| e | Novelty sentence kept **once**, in Limitations only | DONE |
| f | CURE-preprint clause removed from Discussion + intro | DONE |
| g | Conclusion rewritten dropping commit-SHA / SBML ID / grid dims / checkpoint counts | DONE |

**Note on edit (f) and the consistency suite:** removing the CURE-preprint
clause from the body conflicted with a prior test
(`test_cure_preprint_disclaimer_in_body`) that required the arXiv/preprint
disclosure in §VI-A. The credibility guarantee that test protected — readers
must know CURE [sauro2025cure] is an unreviewed preprint — is still met: the
disclosure lives in the bibliography entry (`arXiv:2502.15597`, note "Preprint;
peer-review status pending at time of submission"), which renders in the
compiled reference list. The test was updated to
`test_cure_preprint_disclaimer_disclosed`, which checks the bib entry (the
canonical place for preprint status), preserving the test's intent.

---

## C. Hard reference errors found and fixed (2)

| Key | Was | Corrected to | How verified |
|-----|-----|--------------|--------------|
| `miao2010influenza` | DOI `10.1128/JVI.00506-10`, issue 14, pp. 7051–7062 | DOI `10.1128/JVI.00266-10`, issue **13**, pp. **6687–6698** | PMID 20410284 + embedded SBML metadata of BIOMD0000000546 |
| `getz2020sarscov2` | "Rapid…", iScience 23:101734 (DOI `10.1016/j.isci.2020.101734`) | bioRxiv preprint "Iterative community-driven development of a SARS-CoV-2 tissue simulator", DOI `10.1101/2020.04.02.019075` | PMID 32511322; the iScience DOI resolves to an unrelated C. elegans paper |

`miao2010influenza` is the central coupled ODE model, so this was the
highest-priority fix. Both corrections confirmed rendered in the final PDF.

## D. Missing DOIs added (14)

All resolved via CrossRef / doi.org content negotiation:
agmon2022vivarium → 10.1093/bioinformatics/btac049; ghaffarizadeh2018physicell
→ 10.1371/journal.pcbi.1005991; hucka2015sbml → 10.2390/biecoll-jib-2015-266;
karr2022modelintegration → 10.3389/fsysb.2022.822606; laubenbacher2022roadmap →
10.1038/s41746-022-00610-z; laubenbacher2024forum → 10.1038/s41540-024-00345-5;
laubenbacher2024naturecs → 10.1038/s43588-024-00607-6; laubenbacher2024frontiers
→ 10.3389/fdgth.2024.1349595; niarakis2024idt → 10.1038/s41540-024-00450-5;
ponce2023physiboss → 10.1038/s41540-023-00314-4; bergmann2014combine →
10.1186/s12859-014-0369-z; viceconti2024vht → 10.1109/JBHI.2023.3323688;
waltemath2011sedml → 10.1186/1752-0509-5-198; nasem2023digitaltwins →
10.17226/26894. (bib is 25 entries, unchanged count — additive only.)

## E. Numeric reproducibility (positive credibility finding)

Table 2 reproduced end-to-end from ISSL replicate data in `results/issl_14d/`
(N=20), using `np.percentile(..., method="nearest")`:
- Peak viral load **9.0×10⁶ copies/mL at day 2.25** — matches.
- Daily viral-load 2.5–97.5 percentile intervals match exactly (day1 [2–10],
  day3 [12–25], day7 [22–41], day13 [41–64]).
- n_immune intervals match; day 13.75 clearance <1% of peak holds.
- Face validity: Ep depletion ~100% at day 3 (≥ paper's conservative bound);
  n_immune ≥ 1 after day 1 holds.

## F. Build verification (final)

Rebuilt with tectonic:
- Compiles cleanly, exit 0. **8 pages.**
- **0** undefined citations, **0** undefined references, **0** LaTeX warnings.
  Only benign underfull-hbox notices (cosmetic loose spacing).
- IEEEtran.bst ran without error.
- Note: IEEEtran does not print DOIs, so the visible bibliography relies on
  volume/issue/pages — which is why the Miao issue/pages fix is the visible one.

## G. Items for the author

1. **TregModel primary citation.** Boolean Treg model cited only to the pyMaBoSS
   reference suite. The original author flagged a primary biological citation
   "to be confirmed by domain expert"; not confidently identifiable here.
   Confirm/add before submission if a domain expert can source it.
2. **nasem2023digitaltwins year.** DOI 10.17226/26894 shows issued 2024-03-28;
   bib says 2023 (NASEM prepublication vs final — both defensible). Left as 2023.
3. **Figure legibility.** `tri_formalism_trajectory.pdf` is at 0.59 columnwidth
   (down from 0.9) — the maximum that fits 8 pages. Verified readable at print
   resolution, but review in the final proof.
4. **Recompile and commit.** All changes are working-tree only (uncommitted):
   `paper/main.tex`, `paper/references.bib`, `tests/test_paper_consistency.py`,
   `docs/OISA_paper_IEEE_BIBM2026.md`, `.gitignore`.
