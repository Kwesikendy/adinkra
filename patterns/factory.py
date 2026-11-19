"""Unified pattern factory used by both the CLI and Streamlit UI."""

from __future__ import annotations

from typing import Callable

from engine.color import PRESET_PALETTES, Palette
from kente.kente import generate_kente_strips
from patterns import PatternScene
from patterns.frieze import generate_frieze
from patterns.hex_tiling import generate_hex_tiling
from patterns.mirror_grid import generate_mirror_grid
from patterns.rosette import generate_rosette
from patterns.square_grid import generate_square_grid
from symbols.loader import load_symbol

SYMMETRY_TYPES: dict[str, str] = {
    "rosette": "N-Fold Rotation Rosette (C_n)",
    "mirror_grid": "Mirror Grid (pmm)",
    "frieze": "Glide-Reflection Frieze (p11g)",
    "hex_tiling": "Hexagonal Lattice Tiling (p6)",
    "square_grid": "4-Fold Square Rotation Grid (p4)",
    "kente": "Kente Woven Strips",
}


def generate_pattern(
    symmetry: str,
    symbol_id: str = "gye_nyame",
    palette: Palette | None = None,
    width: float = 800.0,
    height: float = 800.0,
    scale: float = 48.0,
    rotation: float = 0.0,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    seed: int = 42,
    folds: int = 8,
    grid_count: int = 5,
) -> PatternScene:
    """Generate a `PatternScene` for any supported symmetry type or Kente."""
    pal = palette or PRESET_PALETTES["Asante Royal Gold"]

    if symmetry == "kente":
        return generate_kente_strips(
            width=width,
            height=height,
            num_strips=max(2, grid_count),
            seed=seed,
            shear_x=shear_x,
            shear_y=shear_y,
        )

    sym = load_symbol(symbol_id)
    if symmetry == "rosette":
        return generate_rosette(
            sym,
            pal,
            width=width,
            height=height,
            folds=folds,
            motif_scale=scale,
            base_rotation=rotation,
            shear_x=shear_x,
            shear_y=shear_y,
            seed=seed,
        )
    if symmetry == "mirror_grid":
        return generate_mirror_grid(
            sym,
            pal,
            width=width,
            height=height,
            cols=grid_count,
            rows=grid_count,
            motif_scale=scale,
            base_rotation=rotation,
            shear_x=shear_x,
            shear_y=shear_y,
            seed=seed,
        )
    if symmetry == "frieze":
        return generate_frieze(
            sym,
            pal,
            width=width,
            height=height,
            bands=max(1, grid_count - 2),
            repeats=max(4, grid_count + 3),
            motif_scale=scale * 0.85,
            base_rotation=rotation,
            shear_x=shear_x,
            shear_y=shear_y,
            seed=seed,
        )
    if symmetry == "hex_tiling":
        return generate_hex_tiling(
            sym,
            pal,
            width=width,
            height=height,
            spacing=max(80.0, scale * 3.4),
            motif_scale=scale * 0.75,
            base_rotation=rotation,
            shear_x=shear_x,
            shear_y=shear_y,
            seed=seed,
        )
    if symmetry == "square_grid":
        return generate_square_grid(
            sym,
            pal,
            width=width,
            height=height,
            cells=max(2, grid_count - 1),
            motif_scale=scale * 0.85,
            base_rotation=rotation,
            shear_x=shear_x,
            shear_y=shear_y,
            seed=seed,
        )

    raise ValueError(f"Unknown symmetry '{symmetry}'. Choose from: {', '.join(SYMMETRY_TYPES)}")
