"""N-fold Rotation Rosette Pattern Generator (Cyclic group C_n).

Matrices creating the symmetry
------------------------------
To place `n` copies of a motif evenly around a centre `(cx, cy)` at radius `R`:
1. `M_local = Matrix.shear(shx, shy) @ Matrix.rotate(base_rot) @ Matrix.scale(motif_scale)`
   shapes the symbol in local space.
2. `M_offset = Matrix.translate(0.0, -ring_radius)` pushes the motif outward from
   the origin along the y-axis.
3. `M_ring_rot = Matrix.rotate(i * (360.0 / n))` rotates that offset motif by
   step angle `i * 360 / n` around the origin.
4. `M_center = Matrix.translate(cx, cy)` moves the entire rosette to the canvas
   centre `(cx, cy)`.

Composed right-to-left:
    `M_i = M_center @ M_ring_rot @ M_offset @ M_local`

Equivalently, `M_ring_rot` around `(cx, cy)` is `Matrix.rotate(angle, pivot=(cx, cy))`.
"""

from __future__ import annotations

import random

from engine.color import Palette
from engine.matrix import Matrix
from patterns import PatternScene, place_symbol
from symbols.loader import Symbol


def generate_rosette(
    symbol: Symbol,
    palette: Palette,
    width: float = 800.0,
    height: float = 800.0,
    folds: int = 8,
    rings: int = 2,
    motif_scale: float = 55.0,
    base_rotation: float = 0.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
) -> PatternScene:
    """Generate an N-fold rotational rosette with optional concentric rings."""
    rng = random.Random(seed)
    cx, cy = width / 2.0, height / 2.0
    scene = PatternScene(
        width=width,
        height=height,
        background=palette.background,
        metadata={"symmetry": "rosette", "symbol": symbol.id, "folds": str(folds), "seed": str(seed)},
    )

    # Central anchor motif at (cx, cy)
    center_scale = motif_scale * 0.9
    m_center_motif = (
        Matrix.translate(cx, cy)
        @ Matrix.shear(shear_x, shear_y)
        @ Matrix.rotate(base_rotation)
        @ Matrix.scale(center_scale)
    )
    scene.shapes.extend(place_symbol(symbol, m_center_motif, palette, stroke_scale=center_scale))

    max_radius = min(width, height) * 0.38
    for ring_idx in range(1, rings + 1):
        ring_radius = (max_radius * ring_idx) / max(1, rings)
        ring_folds = folds if ring_idx == 1 else folds * 2
        ring_scale = motif_scale * (0.75 if ring_idx == 1 else 0.55)
        # Seeded angular stagger between rings for visual richness (deterministic for a given seed)
        phase_offset = rng.choice([0.0, 180.0 / ring_folds])

        for i in range(ring_folds):
            angle = phase_offset + i * (360.0 / ring_folds)
            # Compose: translate to centre -> rotate around origin -> push out by ring_radius -> local shape
            m_local = (
                Matrix.shear(shear_x, shear_y)
                @ Matrix.rotate(base_rotation)
                @ Matrix.scale(ring_scale)
            )
            m_place = (
                Matrix.translate(cx, cy)
                @ Matrix.rotate(angle)
                @ Matrix.translate(0.0, -ring_radius)
                @ m_local
            )
            scene.shapes.extend(place_symbol(symbol, m_place, palette, stroke_scale=ring_scale))

    return scene
