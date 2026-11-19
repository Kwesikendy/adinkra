# Adinkra & Kente Pattern Generator (CSSD 315)

A computer graphics project for **CSSD 315** that generates print-ready fabric and wallpaper patterns inspired by Ghanaian **Adinkra symbols** and **Kente weaving**.

Every shape placement, rotation, reflection, shear, and scaling operation is computed from scratch by a custom `3x3` homogeneous [`Matrix`](engine/matrix.py) class. NumPy is used **only** for basic array storage and matrix multiplication inside `Matrix`. Generated SVGs contain **already-transformed coordinates** with zero SVG `transform` attributes.

---

## Repository Structure

```text
adinkra/
├── engine/
│   ├── matrix.py          # 3x3 homogeneous Matrix class (no library transform helpers)
│   └── color.py           # HSB -> RGB/HEX converter and preset palettes
├── symbols/
│   ├── *.json             # 8 digitized Adinkra vector symbols (lines + Bezier curves)
│   ├── loader.py          # JSON loader + Bezier-to-polyline flattener
│   └── MEANINGS.md        # Symbol meanings & verification checklist
├── patterns/
│   ├── rosette.py         # N-fold rotation rosette (C_n)
│   ├── mirror_grid.py     # Mirror grid (pmm)
│   ├── frieze.py          # Glide-reflection frieze (p11g)
│   ├── hex_tiling.py      # Hexagonal lattice tiling (p6)
│   ├── square_grid.py     # 4-fold square rotation grid (p4)
│   └── factory.py         # Unified pattern dispatcher
├── kente/
│   └── kente.py           # Woven-style Kente strip generator + COLOUR_MEANINGS
├── export/
│   ├── svg_export.py      # Transform-free SVG writer (svgwrite)
│   └── pdf_export.py      # Print-ready A3 PDF (297 x 420 mm via ReportLab)
├── ui/
│   └── app.py             # Interactive Streamlit web UI
├── cli.py                 # Command-line mode (`python -m cli ...`)
├── gallery/               # 10 generated designs + 1 programmatic shirt mock-up
├── tests/                 # pytest unit & integration tests
├── diary/
│   └── WEEK_TEMPLATE.md   # Weekly course diary template
├── docs/
│   ├── LEARNING.md        # Plain-English maths guide + worked numeric examples
│   ├── PRESENTATION_GUIDE.md
│   └── REPORT_OUTLINE.md
└── requirements.txt
```

---

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

---

## Running the Project

### 1. Streamlit Interactive UI
```powershell
.venv\Scripts\streamlit run ui/app.py
```

### 2. Command-Line Mode (`python -m cli`)
```powershell
.venv\Scripts\python -m cli `
  --symmetry rosette `
  --symbol gye_nyame `
  --palette "Asante Royal Gold" `
  --folds 8 `
  --seed 42 `
  --out output/my_pattern.svg `
  --pdf output/my_pattern_A3.pdf
```

### 3. Regenerate the Gallery & Shirt Mock-up
```powershell
.venv\Scripts\python gallery/generate_gallery.py
```

---

## Running Tests

```powershell
.venv\Scripts\python -m pytest -v
```

---

## Cultural Verification Notice
Before submitting your report or presenting, please double-check the cultural meanings marked `[VERIFY]` in [`symbols/MEANINGS.md`](symbols/MEANINGS.md) and [`kente/kente.py`](kente/kente.py) against a primary Ghanaian cultural source.
