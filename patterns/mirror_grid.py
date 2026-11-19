"""Mirror Grid Symmetry Pattern Generator (Wallpaper group pmm).

Matrices creating the symmetry
------------------------------
Each cell `(col, row)` of size `(cell_w, cell_h)` is mirrored depending on the
parity of `col` and `row`:
1. `M_local = Matrix.shear(shx, shy) @ Matrix.rotate(base_rot) @ Matrix.scale(motif_scale)`
   shapes the symbol in local space.
2. `M_reflect`:
   - `Matrix.identity()` when `col` is even and `row` is even
   - `Matrix.reflect_y()` when `col` is odd (flips horizontally across y-axis)
   - `Matrix.reflect_x()` when `row` is odd (flips vertically across x-axis)
   - `Matrix.reflect_y() @ Matrix.reflect_x()` when both `col` and `row` are odd
     (equivalent to a 180-degree rotation!).
3. `M_cell = Matrix.translate(cx, cy)` places the mirrored motif at the cell
   centre `(cx, cy)`.

Composed right-to-left:
    `M = M_cell @ M_reflect @ M_local`
"""

from __future__ import annotations

import random

from engine.color import Palette
from engine.matrix import Matrix
from patterns import PatternScene, place_symbol
from symbols.loader import Symbol


def generate_mirror_grid(
    symbol: Symbol,
    palette: Palette,
    width: float = 800.0,
    height: float = 800.0,
    cols: int = 5,
    rows: int = 5,
    motif_scale: float = 48.0,
    base_rotation: float = 15.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
) -> PatternScene:
    """Generate a mirror-symmetric grid (pmm-style alternating X/Y reflections)."""
    rng = random.Random(seed)
    cell_w = width / max(1, cols)
    cell_h = height / max(1, rows)

    scene = PatternScene(
        width=width,
        height=height,
        background=palette.background,
        metadata={"symmetry": "mirror_grid", "symbol": symbol.id, "seed": str(seed)},
    )

    # Seeded slight local rotation jitter shared across all cells so symmetry is preserved
    jitter = rng.uniform(-10.0, 10.0)
    m_local = (
        Matrix.shear(shear_x, shear_y)
        @ Matrix.rotate(base_rotation + jitter)
        @ Matrix.scale(motif_scale)
    )

    for r in range(rows):
        for c in range(cols):
            cx = (c + 0.5) * cell_w
            cy = (r + 0.5) * cell_h

            m_reflect = Matrix.identity()
            if c % 2 == 1:
                m_reflect = Matrix.reflect_y() @ m_reflect
            if r % 2 == 1:
                m_reflect = Matrix.reflect_x() @ m_reflect

            m_total = Matrix.translate(cx, cy) @ m_reflect @ m_local
            scene.shapes.extend(place_symbol(symbol, m_total, palette, stroke_scale=motif_scale))

    return scene
