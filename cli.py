"""Command-line interface for Adinkra & Kente Pattern Generator.

Example usage:
    python -m cli --symmetry rosette --symbol gye_nyame --palette "Asante Royal Gold" --out out.svg --pdf out.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

from engine.color import PRESET_PALETTES
from export.pdf_export import write_pdf
from export.svg_export import write_svg
from patterns.factory import SYMMETRY_TYPES, generate_pattern
from symbols.loader import list_symbols


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m cli",
        description="Generate Adinkra & Kente patterns to SVG and print-ready A3 PDF.",
    )
    parser.add_argument(
        "--symmetry",
        choices=list(SYMMETRY_TYPES.keys()),
        default="rosette",
        help="Symmetry pattern type or 'kente'.",
    )
    parser.add_argument(
        "--symbol",
        choices=list_symbols(),
        default="gye_nyame",
        help="Adinkra symbol ID (ignored for 'kente').",
    )
    parser.add_argument(
        "--palette",
        choices=list(PRESET_PALETTES.keys()),
        default="Asante Royal Gold",
        help="Preset HSB colour palette name.",
    )
    parser.add_argument("--scale", type=float, default=48.0, help="Motif scale factor.")
    parser.add_argument("--rotation", type=float, default=0.0, help="Base rotation in degrees.")
    parser.add_argument("--shear-x", type=float, default=0.0, help="Horizontal shear.")
    parser.add_argument("--shear-y", type=float, default=0.0, help="Vertical shear.")
    parser.add_argument("--folds", type=int, default=8, help="Number of folds for rosette.")
    parser.add_argument("--grid-count", type=int, default=5, help="Grid/strip count.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--out", type=Path, required=True, help="Output SVG path.")
    parser.add_argument("--pdf", type=Path, default=None, help="Optional A3 PDF output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    scene = generate_pattern(
        symmetry=args.symmetry,
        symbol_id=args.symbol,
        palette=PRESET_PALETTES[args.palette],
        scale=args.scale,
        rotation=args.rotation,
        shear_x=args.shear_x,
        shear_y=args.shear_y,
        seed=args.seed,
        folds=args.folds,
        grid_count=args.grid_count,
    )
    svg_path = write_svg(scene, args.out)
    print(f"Wrote SVG: {svg_path}")

    if args.pdf is not None:
        pdf_path = write_pdf(scene, args.pdf)
        print(f"Wrote A3 PDF: {pdf_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
