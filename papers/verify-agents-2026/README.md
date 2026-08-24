# NeurIPS 2026 Workshop Paper: spanbind

Demo paper for the "Who Verifies the Agents?" workshop at NeurIPS 2026.

## Paper Details

- **Title:** spanbind: A Simple CI Tool for Detecting Ungrounded Claims in LLM Outputs
- **Author:** Abinesh Haridoss (University of North Texas / EXL, Irving TX)
- **Workshop:** Who Verifies the Agents? ([https://verify-agents-workshop.github.io/](https://verify-agents-workshop.github.io/))
- **Deadline:** August 29, 2026 (AoE)
- **Format:** Non-archival demo paper, ≤4 pages (excluding references)
- **Pages:** 4 pages (exactly at limit)

## Files

- `spanbind-paper.tex` - Main LaTeX source
- `spanbind-paper.pdf` - Compiled PDF (4 pages)
- `neurips_2026.sty` - NeurIPS 2026 LaTeX style file
- `README.md` - This file

## Building the Paper

### Option 1: Pre-built PDF

The compiled PDF is included: `spanbind-paper.pdf`

### Option 2: Build from source

Requirements:
- LaTeX distribution (TeX Live or MiKTeX)
- Required packages: neurips_2026, hyperref, url, booktabs, amsmath, amsfonts, nicefrac, microtype, xcolor

Build commands:

```bash
cd papers/verify-agents-2026
pdflatex spanbind-paper.tex
pdflatex spanbind-paper.tex  # Run twice for references
```

### Option 3: Overleaf

Upload `spanbind-paper.tex` and `neurips_2026.sty` to Overleaf and compile.

## Paper Content

The paper presents an honest evaluation of the spanbind tool:

### What's Included:
- Real test results: 23/23 tests pass (reproducible via `pytest`)
- Demo results: 2 bound/0 unbound vs. 1 bound/1 unbound (reproducible via `spanbind demo`)
- Actual corpus size: 2 documents, 427 characters total
- Heuristic overlap threshold: 0.55 (not empirically validated)
- Honest limitations: toy corpus, no benchmark evaluation, 0 stars, no users

### What's NOT Included:
- No invented F1/accuracy numbers
- No false claims about attribution methods
- No exaggerated capabilities
- No invented citations or users
- No fabricated GitHub stars

All empirical results are reproducible by:

```bash
cd /workspace
python3 -m pip install -e ".[dev]"
pytest                    # 23/23 tests pass
spanbind demo            # Demo corpus results
cd examples/starter && python3 demo.py  # 8-sentence example
```

## Key Stats (Reproducible)

- **Test suite:** 23/23 tests pass (100%)
- **Demo corpus:** 2 documents (425 total chars)
- **Bound answer:** 2/2 sentences successfully bound
- **Unbound answer:** 1/2 bound, 1/2 unbound (warranty hallucination detected)
- **Fake generator:** 8/8 sentences bound (copy-paste style)

## Installation

From the repository root:

```bash
pip install git+https://github.com/abinesha312/spanbind.git
```

## Workshop Submission

Prepared for the "Who Verifies the Agents?" workshop at NeurIPS 2026. This is a non-archival demo paper showcasing a practical CI tool for grounding verification in RAG systems.

## License

The paper describes software released under MIT license. See repository root `LICENSE` file.
