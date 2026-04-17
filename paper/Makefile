# Build helper for the IEEE BIBM 2026 OISA submission.
# Requires TeX Live (or equivalent) with IEEEtran, booktabs,
# tabularx, makecell, listings, xcolor, hyperref, graphicx.

DOC       = main
BIB       = references
LATEXMK   = latexmk
PDFLATEX  = pdflatex
BIBTEX    = bibtex

.PHONY: all pdf quick clean distclean check

all: pdf

# Preferred path: latexmk does the right number of passes itself.
pdf:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(DOC).tex

# Fallback for environments without latexmk.
quick:
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error $(DOC).tex
	$(BIBTEX) $(DOC)
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error $(DOC).tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error $(DOC).tex

# Print the page count of the compiled PDF (BIBM limit: 8 pages).
check: $(DOC).pdf
	@pages=$$(pdfinfo $(DOC).pdf | awk '/^Pages:/ {print $$2}'); \
	 echo "Compiled page count: $$pages"; \
	 if [ "$$pages" -gt 8 ]; then \
	   echo "WARNING: exceeds IEEE BIBM 8-page limit."; exit 1; \
	 else \
	   echo "OK: within IEEE BIBM 8-page limit."; \
	 fi

clean:
	-rm -f $(DOC).aux $(DOC).bbl $(DOC).blg $(DOC).log $(DOC).out \
	       $(DOC).toc $(DOC).fls $(DOC).fdb_latexmk $(DOC).synctex.gz

distclean: clean
	-rm -f $(DOC).pdf
