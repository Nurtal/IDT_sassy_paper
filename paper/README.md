# OISA — IEEE BIBM 2026 LaTeX source

Camera-ready typesetting of the OISA manuscript, authored by
**Nathan Foulquier** (LBAI, Inserm U1227, UBO / CDC CHU de Brest) for
submission to the IEEE BIBM 2026 conference.

## Files

| File | Purpose |
| --- | --- |
| `main.tex` | IEEEtran conference source (two-column, 10 pt, letter). |
| `references.bib` | 20 BibTeX entries, aligned with the Markdown draft. |
| `Makefile` | `make pdf`, `make quick`, `make check`, `make clean`. |
| `../figures/oisa_workflow.pdf` | Fig. 1 — orchestration workflow. |
| `../figures/oisa_trajectory.pdf` | Fig. 2 — coupled 14-day trajectory. |

The Markdown reference draft lives at
`docs/OISA_paper_IEEE_BIBM2026.md`; this directory is the
IEEEtran port of that document.

## Build

Requires a TeX Live (or equivalent) installation with the standard IEEE
conference toolchain:

```
IEEEtran  booktabs  tabularx  makecell  array  multirow
listings  xcolor    hyperref  graphicx  amsmath amssymb
```

Preferred build (single command, handles passes automatically):

```bash
cd paper
make pdf
```

Fallback (explicit passes):

```bash
cd paper
make quick
```

Verify the output fits the IEEE BIBM 8-page limit:

```bash
make check
```

Cleanup:

```bash
make clean      # remove auxiliary files
make distclean  # also remove main.pdf
```

## Format compliance checklist

- [x] `\documentclass[conference,letterpaper,10pt]{IEEEtran}`.
- [x] Two-column layout, US letter.
- [x] `\IEEEauthorblockN` / `\IEEEauthorblockA` author block.
- [x] `abstract` + `IEEEkeywords` (Index Terms, not Keywords).
- [x] Numbered references via `\bibliographystyle{IEEEtran}`.
- [x] Figures referenced by `\ref{fig:...}` with `\label` inside caption.
- [x] Tables use `booktabs` rules; no vertical lines.
- [x] Clean compile: 0 warnings, 0 overfull/underfull hboxes
      reported as errors.
- [x] **8 pages** (within IEEE BIBM strict limit, no over-length fee).

## Current build state (2026-04-17)

Last verified compile: **8 pages**, clean log (0 warnings, 0 overfull).
Steps: `latexmk -pdf -interaction=nonstopmode main.tex` from this dir
(requires `IEEEtran.cls` + `IEEEtran.bst` — vendored in this directory
for reproducibility, since the host `texlive-publishers` package is not
installed system-wide).

A backup of the earlier 10-page (over-length) version is preserved
under `backup_10pages/` for reference. Tables IV, V, VIII, IX and
Box 2 (ABM JSON listing) were dropped or inlined to fit 8 pages;
Tables II and III were also compressed to inline prose.

## Known residual TODOs

1. Replace the `[repository URL to be added prior to submission]`
   placeholder in the *Data, Code, and Competing Interests* paragraph
   once the public repo is provisioned.
