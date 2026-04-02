# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic writing project for a paper on **Immune Digital Twins (IDT)** and interoperability of different immune models. The goal is to refine and submit the paper to **IEEE BIBM 2026** (Bioinformatics and Biomedicine conference).

The paper body is in `docs/OISA_paper_v3_npj.docx` (Word format). The target deliverable is a polished Markdown version of the paper.

## TODO (from README)

- Review the existing paper and propose/implement improvements
- Write the paper in Markdown format
- Verify references carefully

## Python Environment

A Python 3.12.11 virtual environment is available at `venv/`. Activate with:

```bash
source venv/bin/activate
```

No dependencies are currently installed. Use `pip install <package>` as needed for document processing (e.g., `python-docx` to read the `.docx` file).

## Working with the Paper

The source document is a `.docx` file. To read its content programmatically:

```python
from docx import Document
doc = Document('docs/OISA_paper_v3_npj.docx')
for para in doc.paragraphs:
    print(para.text)
```

Install with: `pip install python-docx`

Use academic skill
