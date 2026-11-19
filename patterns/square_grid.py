"""4-Fold Square Rotation Grid Pattern Generator (Wallpaper group p4).

Matrices creating the symmetry
------------------------------
Each square tile centred at `(cx, cy)` has 4-fold rotational symmetry:
1. `M_local = Matrix.shear(shx, shy) @ Matrix.rotate(base_rot) @ Matrix.scale(quad_scale)`
   shapes the symbol in local space.
2. Within each tile, we place 4 copies rotated by `0, 90, 180, 270` degrees
   around the tile centre `(cx, cy)`:
       `M_quad(k) = Matrix.translate(cx, cy) @ Matrix.rotate(k * 90.0) @ Matrix.translate(offset, -offset)`
   for `k in {0, 1, 2, 3}`.

Composed right-to-left:
    `M = M_quad(k) @ M_local`

Because each tile is invariant under a 90-degree rotation about its centre,
tiling these square cells produces the `p4` wallpaper symmetry group.
"""

from __future__ import annotations

import random

from engine.color import Palette
from engine.matrix import Matrix
from patterns import PatternScene, add_coloured_tiles, place_symbol
from symbols.loader import Symbol


def generate_square_grid(
    symbol: Symbol,
    palette: Palette,
    width: float = 800.0,
    height: float = 800.0,
    cells: int = 4,
    motif_scale: float = 42.0,
    base_rotation: float = 15.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
    tile_colors: bool = False,
) -> PatternScene:
    """Generate a 4-fold rotational square grid (p4 wallpaper symmetry)."""
    rng = random.Random(seed)
    cell_size = min(width, height) / max(1, cells)
    cols = max(1, round(width / cell_size))
    rows = max(1, round(height / cell_size))
    cell_w = width / cols
    cell_h = height / rows

    scene = PatternScene(
        width=width,
        height=height,
        background=palette.background,
        metadata={"symmetry": "square_grid", "symbol": symbol.id, "seed": str(seed)},
    )

    if tile_colors:
        add_coloured_tiles(scene, cols, rows, cell_w, cell_h, palette, seed=seed)

    quad_scale = motif_scale * 0.65
    offset = min(cell_w, cell_h) * 0.22
    jitter = rng.uniform(-15.0, 15.0)

    m_local = (
        Matrix.shear(shear_x, shear_y)
        @ Matrix.rotate(base_rotation + jitter)
        @ Matrix.scale(quad_scale)
    )

    for r in range(rows):
        for c in range(cols):
            cx = (c + 0.5) * cell_w
            cy = (r + 0.5) * cell_h

            for k in range(4):
                m_total = (
                    Matrix.translate(cx, cy)
                    @ Matrix.rotate(k * 90.0)
                    @ Matrix.translate(offset, -offset)
                    @ m_local
                )
                scene.shapes.extend(place_symbol(symbol, m_total, palette, stroke_scale=quad_scale))

    return scene
