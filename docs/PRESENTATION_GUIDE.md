# 10-Minute Presentation Guide (CSSD 315)

## Timing Breakdown (10 Minutes Total)

| Time | Segment | Goal |
| :--- | :--- | :--- |
| **0:00 – 1:30** | **1. Concept & Cultural Context** | Introduce Adinkra symbols, Kente weaving, and the constraint: *every coordinate is computed by our own 3x3 Matrix engine (zero SVG transform helpers)*. |
| **1:30 – 3:30** | **2. Worked Maths Example** | Walk through homogeneous coordinates and rotating `(2, 1)` by `45°`, plus why `R @ T != T @ R`. |
| **3:30 – 5:30** | **3. Architecture & Code Tour** | Briefly show `engine/matrix.py`, `symbols/gye_nyame.json`, one pattern file (`patterns/rosette.py`), and `pytest` passing. |
| **5:30 – 8:00** | **4. Live Demo + Class Activity** | Run Streamlit UI live and build a pattern suggested by classmates! |
| **8:00 – 9:30** | **5. Export & Product Mock-up** | Show A3 PDF export (297 x 420 mm) and `gallery/11_shirt_mockup.svg`. |
| **9:30 – 10:00** | **6. Q&A / Wrap-up** | Answer questions on inverse matrices, Bezier flattening, or HSB->RGB conversion. |

---

## Worked Example for the Board / Slide (2 Minutes)

Write on the board or slide:
1. Point `p = (2, 1)` in homogeneous form: `[2, 1, 1]^T`.
2. `R(45°)` has `cos(45°) = sin(45°) ≈ 0.7071`:
   - `x' = 0.7071(2) - 0.7071(1) = 0.7071`
   - `y' = 0.7071(2) + 0.7071(1) = 2.1213`
3. Pivot rotation formula: `T(px, py) @ R(θ) @ T(-px, -py)` — explain "move to origin -> rotate -> move back".

---

## Live Demo Script (2.5 Minutes)

Before your turn, start Streamlit in a terminal:
```bash
.venv\Scripts\streamlit run ui/app.py
```

1. **Show default Rosette:** Point out Gye Nyame in the centre and the 8-fold ring.
2. **Toggle Shear & Rotation:** Move `Base Rotation` to `30°` and `Shear X` to `0.25` to show affine distortion in real time.
3. **Switch to Kente Strips:** Show the woven strip generator and expand the `COLOUR_MEANINGS` table.
4. **Class Activity ("Co-Design Live!"):**
   - Ask classmates: *"Give me 1 Adinkra symbol, 1 symmetry type, and 1 colour palette (or custom HSB hue)!"*
   - Select their choices in the sidebar, set a memorable seed (e.g., `315`), and generate the pattern live.
   - Click **Download Print-Ready A3 PDF** to show it is immediately ready for printing.
5. **Prove No Cheating:** Open one exported `.svg` in a text editor and `Ctrl+F` for `transform=` — show `0 results`!
