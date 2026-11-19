# CSSD 315 Report Outline (4–6 Pages)

**Suggested Title:** *Adinkra & Kente Pattern Generator: 2D Homogeneous Transformations and Wallpaper Symmetries from Scratch*

---

## Page 1: Title, Abstract & Concept
- **1.1 Project Concept:** Bridging Ghanaian Adinkra iconography and Kente strip weaving with 2D computer graphics transformations.
- **1.2 Core Engineering Constraint:** All geometric placement is computed by a custom `3x3` homogeneous `Matrix` class (`engine/matrix.py`); SVG/PDF files store pre-transformed coordinates with zero library transform helpers.
- **1.3 Cultural Context:** Brief overview of the 8 digitized Adinkra symbols and Kente colour symbolism (referencing verified sources from `symbols/MEANINGS.md` and `kente/kente.py`).

## Page 2–3: System Architecture & How It Was Built
- **2.1 Matrix Engine (`engine/matrix.py`):**
  - Column-vector convention (`M @ p`) and why homogeneous coordinates unify translation with linear transforms.
  - Analytical `3x3` cofactor inverse (no `np.linalg.inv`) and pivot rotation (`T(p) @ R(θ) @ T(-p)`).
- **2.2 Vector Symbols & Bezier Flattening (`symbols/loader.py`):**
  - Normalized `[-1, 1]` JSON format using lines (`L`) and quadratic/cubic Bezier curves (`Q`, `C`) sampled into polylines before matrix application.
- **2.3 Symmetry Pattern Generators (`patterns/`):**
  - Explain the matrix compositions for all 5 symmetries: Rosette (`C_n`), Mirror Grid (`pmm`), Glide-Reflection Frieze (`p11g`), Hexagonal Tiling (`p6`), and Square Rotation Grid (`p4`).
- **2.4 Kente Strip Generator & HSB Colour Engine (`kente/kente.py`, `engine/color.py`):**
  - Seeded PRNG rules for warp stripes and weft motifs; perceptual HSB-to-RGB/HEX conversion.
- **2.5 Export & UI (`export/`, `ui/app.py`, `cli.py`):**
  - Transform-free SVG serialization (`svgwrite`), A3 PDF (`297 x 420 mm` via ReportLab with Y-axis inversion matrix), CLI, and Streamlit UI.

## Page 4: Visual Results & Screenshots
- **3.1 Gallery Highlights:** Include 3–4 rendered designs from `/gallery/` (e.g., Rosette, Glide Frieze, Hex Tiling, Kente Strips).
- **3.2 Product Mock-up:** Include `gallery/11_shirt_mockup.svg` demonstrating pattern clipping onto a garment outline.
- **3.3 Streamlit UI Screenshot:** Show the interactive sliders, HSB swatches, and export buttons.

## Page 5: Testing, Problems & Fixes
- **4.1 Automated Testing (`pytest`):**
  - Summarize the 23 unit and integration tests (`test_matrix.py`, `test_symbols.py`, `test_patterns.py`, `test_kente.py`, `test_export_and_cli.py`).
  - Highlight tests for non-commutativity (`R @ T != T @ R`), pivot rotation, inverse accuracy, and `"transform=" not in svg`.
- **4.2 Problems Encountered & Fixes:**
  - *Coordinate-system flip for PDF:* SVG uses top-down Y, while ReportLab PDF uses bottom-up Y. Fixed by composing `Matrix.translate(ox, oy + h) @ Matrix.scale(s, -s)`.
  - *Stroke width scaling:* Local `[-1, 1]` symbols need stroke widths scaled proportionally when placed at canvas scale (`stroke_width * stroke_scale`).
  - *Deterministic reproducibility:* Isolated `random.Random(seed)` instances per generation call so UI slider changes remain reproducible.

## Page 6: References & AI-Use Declaration
- **5.1 References:**
  - Course lecture notes for CSSD 315.
  - Verified Adinkra & Kente cultural references (e.g., Willis, *The Adinkra Dictionary*; Arthur, *Cloth as Metaphor* — verify exact bibliographic details before submitting).
  - Python, NumPy, ReportLab, and Streamlit official documentation.
- **5.2 AI-Use Declaration:**
  - Transparently state how AI coding assistance was used (e.g., scaffolding modules, generating initial symbol Bezier coordinates, writing unit tests, and drafting documentation), and confirm that you reviewed, ran, tested, and verified all code, maths, and cultural meanings yourself.
