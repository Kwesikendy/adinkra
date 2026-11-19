"""Hexagonal Lattice Tiling Pattern Generator (p6-style symmetry).

Matrices creating the symmetry
------------------------------
A regular hexagonal lattice has two basis vectors of length `spacing`:
    `a1 = (spacing, 0)`
    `a2 = (spacing * 0.5, spacing * sqrt(3) / 2)`

Each lattice node `(col, row)` is located at:
    `(cx, cy) = (col * spacing + (row % 2) * spacing * 0.5, row * spacing * sqrt(3) / 2)`

At each node, we optionally place a 6-fold (or 1-fold) motif cluster using:
1. `M_local = Matrix.shear(shx, shy) @ Matrix.rotate(base_rot) @ Matrix.scale(motif_scale)`
2. `M_node = Matrix.translate(cx, cy) @ Matrix.rotate(k * 60.0) @ Matrix.translate(0.0, -sub_r)`
   (or directly `Matrix.translate(cx, cy) @ Matrix.rotate(k * 60.0)` when `sub_r == 0`).

Composed right-to-left:
    `M = M_node @ M_local`
"""

from __future__ import annotations

import math
import random

from engine.color import Palette
from engine.matrix import Matrix
from patterns import PatternScene, place_symbol
from symbols.loader import Symbol


def generate_hex_tiling(
    symbol: Symbol,
    palette: Palette,
    width: float = 800.0,
    height: float = 800.0,
    spacing: float = 160.0,
    motif_scale: float = 34.0,
    base_rotation: float = 0.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
) -> PatternScene:
    """Generate a hexagonal lattice tiling with 6-fold rotated motifs at each node."""
    rng = random.Random(seed)
    scene = PatternScene(
        width=width,
        height=height,
        background=palette.background,
        metadata={"symmetry": "hex_tiling", "symbol": symbol.id, "seed": str(seed)},
    )

    row_dy = spacing * math.sqrt(3.0) / 2.0
    cols = int(width / spacing) + 2
    rows = int(height / row_dy) + 2

    sub_r = motif_scale * 1.15
    petal_scale = motif_scale * 0.55
    phase = rng.choice([0.0, 30.0])

    m_local = (
        Matrix.shear(shear_x, shear_y)
        @ Matrix.rotate(base_rotation)
        @ Matrix.scale(petal_scale)
    )

    for r in range(-1, rows):
        y_shift = r * row_dy
        x_offset = (spacing * 0.5) if (r % 2 == 1) else 0.0
        for c in range(-1, cols):
            cx = c * spacing + x_offset
            cy = y_shift
            # Skip nodes far outside the canvas
            if cx < -spacing or cx > width + spacing or cy < -spacing or cy > height + spacing:
                continue

            for k in range(6):
                angle = phase + k * 60.0
                m_total = (
                    Matrix.translate(cx, cy)
                    @ Matrix.rotate(angle)
                    @ Matrix.translate(0.0, -sub_r)
                    @ m_local
                )
                scene.shapes.extend(place_symbol(symbol, m_total, palette, stroke_scale=petal_scale))

    return scene
