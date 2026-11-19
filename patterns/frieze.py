"""Glide-Reflection Frieze Pattern Generator (Frieze group p11g).

Matrices creating the symmetry
------------------------------
A glide reflection is the composition of a translation along a frieze axis
and a reflection across that same axis:
    `G(dx) = Matrix.translate(dx, 0) @ Matrix.reflect_x()`

Across each horizontal frieze band centred at `band_y`:
1. `M_local = Matrix.shear(shx, shy) @ Matrix.rotate(base_rot) @ Matrix.scale(motif_scale)`
   shapes the symbol in local space.
2. For step `i = 0, 1, 2, ...`:
   - `x = (i + 0.5) * step_x`
   - When `i` is even: `M_glide = Matrix.translate(x, band_y - offset_y)`
   - When `i` is odd:  `M_glide = Matrix.translate(x, band_y + offset_y) @ Matrix.reflect_x()`
     (reflected vertically across the band's midline and shifted half a period).

Composed right-to-left:
    `M_i = M_glide @ M_local`
"""

from __future__ import annotations

import random

from engine.color import Palette
from engine.matrix import Matrix
from patterns import PatternScene, RenderedShape, place_symbol
from symbols.loader import Symbol


def generate_frieze(
    symbol: Symbol,
    palette: Palette,
    width: float = 800.0,
    height: float = 800.0,
    bands: int = 3,
    repeats: int = 8,
    motif_scale: float = 38.0,
    base_rotation: float = 12.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
) -> PatternScene:
    """Generate stacked glide-reflection frieze bands across the canvas."""
    rng = random.Random(seed)
    scene = PatternScene(
        width=width,
        height=height,
        background=palette.background,
        metadata={"symmetry": "frieze", "symbol": symbol.id, "seed": str(seed)},
    )

    band_h = height / max(1, bands)
    step_x = width / max(1, repeats)
    offset_y = min(band_h * 0.18, motif_scale * 0.65)
    jitter = rng.uniform(-8.0, 8.0)

    m_local = (
        Matrix.shear(shear_x, shear_y)
        @ Matrix.rotate(base_rotation + jitter)
        @ Matrix.scale(motif_scale)
    )

    for b in range(bands):
        band_y = (b + 0.5) * band_h

        # Decorative woven border lines framing each frieze band
        for dy in (-band_h * 0.42, band_h * 0.42):
            line_y = band_y + dy
            p1 = Matrix.translate(0.0, line_y).apply((20.0, 0.0))
            p2 = Matrix.translate(0.0, line_y).apply((width - 20.0, 0.0))
            scene.shapes.append(
                RenderedShape(
                    points=(p1, p2),
                    closed=False,
                    fill_color=None,
                    stroke_color=palette.accent,
                    stroke_width=3.0,
                )
            )

        for i in range(repeats):
            cx = (i + 0.5) * step_x
            if i % 2 == 0:
                m_glide = Matrix.translate(cx, band_y - offset_y)
            else:
                # Glide reflection: reflect across x-axis, then translate to (cx, band_y + offset_y)
                m_glide = Matrix.translate(cx, band_y + offset_y) @ Matrix.reflect_x()

            m_total = m_glide @ m_local
            scene.shapes.extend(place_symbol(symbol, m_total, palette, stroke_scale=motif_scale))

    return scene
