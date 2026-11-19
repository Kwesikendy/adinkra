"""Tests for all 5 symmetry pattern generators and SVG output."""

import pytest

from engine.color import PRESET_PALETTES
from export.svg_export import scene_to_svg_string
from patterns.frieze import generate_frieze
from patterns.hex_tiling import generate_hex_tiling
from patterns.mirror_grid import generate_mirror_grid
from patterns.rosette import generate_rosette
from patterns.square_grid import generate_square_grid
from symbols.loader import load_symbol


@pytest.mark.parametrize(
    "generator",
    [
        generate_rosette,
        generate_mirror_grid,
        generate_frieze,
        generate_hex_tiling,
        generate_square_grid,
    ],
)
def test_symmetry_generators_produce_valid_transform_free_svg(generator) -> None:
    sym = load_symbol("gye_nyame")
    pal = PRESET_PALETTES["Asante Royal Gold"]

    scene1 = generator(sym, pal, seed=123)
    scene2 = generator(sym, pal, seed=123)

    assert len(scene1.shapes) > 0
    # Deterministic for same seed + settings
    assert scene1.shapes == scene2.shapes

    svg = scene_to_svg_string(scene1)
    assert "transform=" not in svg
    assert "<svg" in svg
    assert "<polygon" in svg or "<polyline" in svg


def test_alternating_coloured_tiles_on_grids() -> None:
    sym = load_symbol("sankofa")
    pal = PRESET_PALETTES["Adinkra Earth Tiles"]
    plain = generate_mirror_grid(sym, pal, cols=4, rows=4, tile_colors=False)
    tiled = generate_mirror_grid(sym, pal, cols=4, rows=4, tile_colors=True)
    assert len(tiled.shapes) == len(plain.shapes) + 16
    sq_tiled = generate_square_grid(sym, pal, cells=3, tile_colors=True)
    assert len(sq_tiled.shapes) > 9
