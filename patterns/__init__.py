"""Symmetry pattern generators built exclusively with our 3x3 Matrix engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.color import Palette
from engine.matrix import Matrix, Point2D
from symbols.loader import Symbol


@dataclass(frozen=True)
class RenderedShape:
    """A single polygon or polyline in final canvas coordinates (no SVG transform needed)."""

    points: tuple[Point2D, ...]
    closed: bool
    fill_color: str | None
    stroke_color: str | None
    stroke_width: float = 1.5


@dataclass
class PatternScene:
    """Complete 2D vector scene ready for SVG or PDF export."""

    width: float
    height: float
    background: str
    shapes: list[RenderedShape] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


_UNIT_TILE: tuple[Point2D, ...] = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


def add_coloured_tiles(
    scene: PatternScene,
    cols: int,
    rows: int,
    cell_w: float,
    cell_h: float,
    palette: Palette,
    seed: int = 42,
) -> None:
    """Fill each grid cell with alternating coloured tiles placed via `Matrix`."""
    import random

    rng = random.Random(seed)
    tile_colors = [palette.background, palette.accent, palette.detail]
    shift = rng.randint(0, len(tile_colors) - 1)
    for r in range(rows):
        for c in range(cols):
            # (c + 2*r + shift) % 3 ensures no two orthogonally adjacent tiles share a colour
            col = tile_colors[(c + 2 * r + shift) % len(tile_colors)]
            m_tile = Matrix.translate(c * cell_w, r * cell_h) @ Matrix.scale(cell_w, cell_h)
            scene.shapes.append(
                RenderedShape(
                    points=tuple(m_tile.apply_many(_UNIT_TILE)),
                    closed=True,
                    fill_color=col,
                    stroke_color=None,
                    stroke_width=0.0,
                )
            )


def place_symbol(
    symbol: Symbol,
    transform: Matrix,
    palette: Palette,
    stroke_scale: float = 1.0,
) -> list[RenderedShape]:
    """Transform `symbol` by `transform` and convert its paths to `RenderedShape`s.

    `stroke_scale` scales local stroke widths into canvas units (typically the
    motif's overall scale factor).
    """
    rendered: list[RenderedShape] = []
    for path in symbol.transformed(transform):
        color = palette.color_for_role(path.role)
        sw = max(0.5, path.stroke_width * stroke_scale)
        if path.fill:
            rendered.append(
                RenderedShape(
                    points=path.points,
                    closed=path.closed,
                    fill_color=color,
                    stroke_color=None,
                    stroke_width=0.0,
                )
            )
        else:
            rendered.append(
                RenderedShape(
                    points=path.points,
                    closed=path.closed,
                    fill_color=None,
                    stroke_color=color,
                    stroke_width=sw,
                )
            )
    return rendered
