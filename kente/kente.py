"""Woven-Style Kente Strip Pattern Generator (CSSD 315).

Traditional Asante and Ewe Kente cloth is woven on a narrow strip loom in
long strips (roughly 10 cm wide) and sewn edge-to-edge. Each strip alternates
between solid/striped warp-faced bands and intricate geometric weft-float
motifs (diamonds, zigzags, and checkerboards).

Every rectangle, stripe, and geometric motif in this module is placed by
composing our own 3x3 `Matrix` transforms (`translate`, `scale`, `rotate`,
`shear`) on normalized unit geometry.
"""

from __future__ import annotations

import random

from engine.color import hsb_to_hex
from engine.matrix import Matrix, Point2D
from patterns import PatternScene, RenderedShape


# Colour rules and documented cultural meanings.
# All colours are defined in HSB and converted to HEX via `hsb_to_hex`.
COLOUR_MEANINGS: list[dict[str, object]] = [
    {
        "name": "Gold (Sika)",
        "hsb": (44.0, 92.0, 88.0),
        "hex": hsb_to_hex(44.0, 92.0, 88.0),
        "meaning": "Royalty, wealth, high status, and spiritual richness.",
        "verify": "[VERIFY] Confirm Twi term and exact symbolism against your course reference.",
    },
    {
        "name": "Green (Ahabanmono)",
        "hsb": (142.0, 72.0, 44.0),
        "hex": hsb_to_hex(142.0, 72.0, 44.0),
        "meaning": "Vegetation, planting, growth, and spiritual renewal.",
        "verify": "[VERIFY] Confirm exact Twi spelling and agricultural association.",
    },
    {
        "name": "Red (Kɔkɔɔ)",
        "hsb": (4.0, 82.0, 72.0),
        "hex": hsb_to_hex(4.0, 82.0, 72.0),
        "meaning": "Political and spiritual passion, sacrifice, and seriousness.",
        "verify": "[VERIFY] Confirm funerary vs. political usage in Asante/Ewe traditions.",
    },
    {
        "name": "Blue (Bire)",
        "hsb": (218.0, 76.0, 46.0),
        "hex": hsb_to_hex(218.0, 76.0, 46.0),
        "meaning": "Peacefulness, harmony, and love.",
        "verify": "[VERIFY] Confirm exact Twi colour term.",
    },
    {
        "name": "Black (Tuntum)",
        "hsb": (30.0, 12.0, 12.0),
        "hex": hsb_to_hex(30.0, 12.0, 12.0),
        "meaning": "Maturity, intensified spiritual energy, and ancestral heritage.",
        "verify": "[VERIFY] Confirm symbolic distinction between black and dark indigo.",
    },
    {
        "name": "White (Fitaa)",
        "hsb": (42.0, 10.0, 96.0),
        "hex": hsb_to_hex(42.0, 10.0, 96.0),
        "meaning": "Purity, cleansing, and festive/victorious occasions.",
        "verify": "[VERIFY] Confirm celebratory context.",
    },
    {
        "name": "Maroon (Kɔkɔɔ-tuntum)",
        "hsb": (352.0, 68.0, 40.0),
        "hex": hsb_to_hex(352.0, 68.0, 40.0),
        "meaning": "Mother Earth, healing, and protection from evil.",
        "verify": "[VERIFY] Confirm Mother Earth / protection attribution.",
    },
]

# Unit square [0, 1] x [0, 1] and unit diamond [-0.5, 0.5]^2 in local space
_UNIT_RECT: tuple[Point2D, ...] = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
_UNIT_DIAMOND: tuple[Point2D, ...] = ((0.0, -0.5), (0.5, 0.0), (0.0, 0.5), (-0.5, 0.0))
_UNIT_ZIGZAG: tuple[Point2D, ...] = (
    (-0.5, 0.35),
    (-0.25, -0.35),
    (0.0, 0.35),
    (0.25, -0.35),
    (0.5, 0.35),
)


def _rect_shape(x: float, y: float, w: float, h: float, color: str) -> RenderedShape:
    """Place a unit rectangle at `(x, y)` with size `(w, h)` using `Matrix`."""
    m = Matrix.translate(x, y) @ Matrix.scale(w, h)
    return RenderedShape(
        points=tuple(m.apply_many(_UNIT_RECT)),
        closed=True,
        fill_color=color,
        stroke_color=None,
        stroke_width=0.0,
    )


def generate_kente_strips(
    width: float = 800.0,
    height: float = 800.0,
    num_strips: int = 5,
    seed: int = 42,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
) -> PatternScene:
    """Generate a woven-style Kente strip cloth pattern with seeded randomness.

    Colour rules:
    - Each strip picks a dominant royal/earth background colour and 2-3 contrasting
      accent colours from `COLOUR_MEANINGS`.
    - Adjacent strips alternate phase so woven blocks interlock visually.
    - Warp stripes run vertically; weft blocks and geometric motifs (diamonds,
      zigzags, checkerboards) repeat horizontally within each strip.
    """
    rng = random.Random(seed)
    colors = [str(c["hex"]) for c in COLOUR_MEANINGS]
    gold_hex = str(COLOUR_MEANINGS[0]["hex"])
    black_hex = str(COLOUR_MEANINGS[4]["hex"])
    white_hex = str(COLOUR_MEANINGS[5]["hex"])

    scene = PatternScene(
        width=width,
        height=height,
        background=black_hex,
        metadata={"symmetry": "kente_strips", "strips": str(num_strips), "seed": str(seed)},
    )

    strip_w = width / max(1, num_strips)
    # Build a deterministic strip-level colour scheme
    accent_pool = [c for c in colors if c != black_hex]

    for s_idx in range(num_strips):
        sx = s_idx * strip_w
        strip_bg = rng.choice([gold_hex, colors[1], colors[2], colors[3], colors[6]])
        c_a = rng.choice([c for c in accent_pool if c != strip_bg])
        c_b = rng.choice([c for c in accent_pool if c not in (strip_bg, c_a)])

        # 1. Strip base
        scene.shapes.append(_rect_shape(sx, 0.0, strip_w, height, strip_bg))

        # 2. Vertical warp stripes along the edges and centre of the strip
        edge_w = strip_w * 0.08
        scene.shapes.append(_rect_shape(sx, 0.0, edge_w, height, black_hex))
        scene.shapes.append(_rect_shape(sx + strip_w - edge_w, 0.0, edge_w, height, black_hex))
        scene.shapes.append(_rect_shape(sx + edge_w, 0.0, edge_w * 0.5, height, gold_hex))
        scene.shapes.append(_rect_shape(sx + strip_w - edge_w * 1.5, 0.0, edge_w * 0.5, height, gold_hex))

        # 3. Repeating vertical weft blocks along the strip
        num_blocks = rng.randint(5, 7)
        block_h = height / num_blocks
        inner_x = sx + edge_w * 1.6
        inner_w = strip_w - edge_w * 3.2

        for b_idx in range(num_blocks):
            by = b_idx * block_h
            # Alternate block styles: solid stripe band, diamond motif, zigzag, or checkerboard
            block_style = (b_idx + s_idx) % 4

            if block_style == 0:
                # Multi-band horizontal weft stripes
                sub_bands = 4
                sub_h = block_h / sub_bands
                band_colors = [c_a, gold_hex, c_b, black_hex]
                for k in range(sub_bands):
                    scene.shapes.append(
                        _rect_shape(inner_x, by + k * sub_h, inner_w, sub_h, band_colors[k])
                    )

            elif block_style == 1:
                # Centered diamond motif (Babadua / geometric weft float)
                scene.shapes.append(_rect_shape(inner_x, by, inner_w, block_h, black_hex))
                cx = inner_x + inner_w * 0.5
                cy = by + block_h * 0.5
                m_outer = (
                    Matrix.translate(cx, cy)
                    @ Matrix.shear(shear_x, shear_y)
                    @ Matrix.scale(inner_w * 0.85, block_h * 0.80)
                )
                scene.shapes.append(
                    RenderedShape(
                        points=tuple(m_outer.apply_many(_UNIT_DIAMOND)),
                        closed=True,
                        fill_color=gold_hex,
                        stroke_color=None,
                        stroke_width=0.0,
                    )
                )
                m_inner = (
                    Matrix.translate(cx, cy)
                    @ Matrix.shear(shear_x, shear_y)
                    @ Matrix.scale(inner_w * 0.42, block_h * 0.40)
                )
                scene.shapes.append(
                    RenderedShape(
                        points=tuple(m_inner.apply_many(_UNIT_DIAMOND)),
                        closed=True,
                        fill_color=c_a,
                        stroke_color=None,
                        stroke_width=0.0,
                    )
                )

            elif block_style == 2:
                # Zigzag motif (Nkyinkyim-inspired weft)
                scene.shapes.append(_rect_shape(inner_x, by, inner_w, block_h, c_b))
                cx = inner_x + inner_w * 0.5
                for dy_frac, col in ((-0.22, gold_hex), (0.22, white_hex)):
                    m_zig = (
                        Matrix.translate(cx, by + block_h * (0.5 + dy_frac))
                        @ Matrix.shear(shear_x, shear_y)
                        @ Matrix.scale(inner_w * 0.88, block_h * 0.34)
                    )
                    scene.shapes.append(
                        RenderedShape(
                            points=tuple(m_zig.apply_many(_UNIT_ZIGZAG)),
                            closed=False,
                            fill_color=None,
                            stroke_color=col,
                            stroke_width=max(2.0, strip_w * 0.045),
                        )
                    )

            else:
                # Checkerboard weft block (Adwinasa-inspired)
                grid_cols = 4
                grid_rows = 4
                cw = inner_w / grid_cols
                ch = block_h / grid_rows
                for gr in range(grid_rows):
                    for gc in range(grid_cols):
                        col = gold_hex if (gr + gc) % 2 == 0 else black_hex
                        scene.shapes.append(
                            _rect_shape(inner_x + gc * cw, by + gr * ch, cw, ch, col)
                        )

    return scene
