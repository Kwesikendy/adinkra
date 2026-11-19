"""Generate 10 gallery designs and 1 programmatic t-shirt product mock-up."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import svgwrite

from engine.color import PRESET_PALETTES
from engine.matrix import Matrix, Point2D
from export.svg_export import write_svg
from patterns.factory import generate_pattern


GALLERY_SPECS = [
    ("01_rosette_gye_nyame.svg", "rosette", "gye_nyame", "Asante Royal Gold", 52.0, 0.0, 0.0, 0.0, 8, 5, 101),
    ("02_rosette_adinkrahene.svg", "rosette", "adinkrahene", "Indigo Adinkra", 46.0, 15.0, 0.0, 0.0, 10, 5, 102),
    ("03_mirror_sankofa.svg", "mirror_grid", "sankofa", "Kuntunkuni Mourning", 50.0, 12.0, 0.0, 0.0, 8, 5, 103),
    ("04_mirror_akoma.svg", "mirror_grid", "akoma", "Terracotta Earth", 48.0, 0.0, 0.15, 0.0, 8, 4, 104),
    ("05_frieze_dwennimmen.svg", "frieze", "dwennimmen", "Forest & Gold", 44.0, 10.0, 0.0, 0.0, 8, 5, 105),
    ("06_frieze_nyame_dua.svg", "frieze", "nyame_dua", "Indigo Adinkra", 42.0, 0.0, 0.1, 0.0, 8, 6, 106),
    ("07_hex_mpuannum.svg", "hex_tiling", "mpuannum", "Asante Royal Gold", 44.0, 0.0, 0.0, 0.0, 8, 5, 107),
    ("08_hex_funtunfunefu.svg", "hex_tiling", "funtunfunefu", "Terracotta Earth", 46.0, 20.0, 0.0, 0.0, 8, 5, 108),
    ("09_square_gye_nyame.svg", "square_grid", "gye_nyame", "Kuntunkuni Mourning", 48.0, 15.0, 0.0, 0.0, 8, 5, 109),
    ("10_kente_royal.svg", "kente", "gye_nyame", "Asante Royal Gold", 48.0, 0.0, 0.0, 0.0, 8, 6, 110),
]


def generate_shirt_mockup(output_path: Path) -> Path:
    """Programmatically place a pattern inside a flat t-shirt outline (no SVG transforms)."""
    width, height = 800.0, 800.0
    scene = generate_pattern(
        symmetry="square_grid",
        symbol_id="dwennimmen",
        palette=PRESET_PALETTES["Indigo Adinkra"],
        width=width,
        height=height,
        scale=38.0,
        rotation=15.0,
        seed=202,
        grid_count=6,
    )

    # Flat t-shirt silhouette in normalized [-1, 1] space, placed via our Matrix
    shirt_norm: list[Point2D] = [
        (-0.24, -0.82),  # left collar
        (-0.10, -0.70),  # collar dip left
        (0.10, -0.70),   # collar dip right
        (0.24, -0.82),   # right collar
        (0.55, -0.72),   # right shoulder
        (0.88, -0.36),   # right sleeve outer top
        (0.68, -0.14),   # right sleeve outer bottom
        (0.46, -0.32),   # right underarm
        (0.46, 0.80),    # right hem
        (-0.46, 0.80),   # left hem
        (-0.46, -0.32),  # left underarm
        (-0.68, -0.14),  # left sleeve outer bottom
        (-0.88, -0.36),  # left sleeve outer top
        (-0.55, -0.72),  # left shoulder
    ]
    m_shirt = Matrix.translate(400.0, 410.0) @ Matrix.scale(360.0)
    shirt_pts = [(round(x, 2), round(y, 2)) for x, y in m_shirt.apply_many(shirt_norm)]

    dwg = svgwrite.Drawing(
        filename=str(output_path),
        size=(f"{width}px", f"{height}px"),
        viewBox=f"0 0 {width} {height}",
    )
    # Studio backdrop
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill="#F2EFE9"))

    # Clip path for the t-shirt silhouette
    clip = dwg.defs.add(dwg.clipPath(id="shirt_clip"))
    clip.add(dwg.polygon(points=shirt_pts))

    # Pattern layer clipped to shirt
    shirt_group = dwg.add(dwg.g(clip_path="url(#shirt_clip)"))
    shirt_group.add(dwg.rect(insert=(0, 0), size=(width, height), fill=scene.background))
    for shape in scene.shapes:
        pts = [(round(x, 2), round(y, 2)) for x, y in shape.points]
        if len(pts) < 2:
            continue
        if shape.closed:
            shirt_group.add(
                dwg.polygon(
                    points=pts,
                    fill=shape.fill_color or "none",
                    stroke=shape.stroke_color or "none",
                    stroke_width=round(shape.stroke_width, 2) if shape.stroke_color else 0,
                )
            )
        else:
            shirt_group.add(
                dwg.polyline(
                    points=pts,
                    fill="none",
                    stroke=shape.stroke_color or "none",
                    stroke_width=round(shape.stroke_width, 2),
                    stroke_linecap="round",
                    stroke_linejoin="round",
                )
            )

    # Shirt outline & collar/hem stitch lines
    dwg.add(dwg.polygon(points=shirt_pts, fill="none", stroke="#222222", stroke_width=4))
    hem_pts = m_shirt.apply_many([(-0.46, 0.74), (0.46, 0.74)])
    dwg.add(
        dwg.polyline(
            points=[(round(x, 2), round(y, 2)) for x, y in hem_pts],
            fill="none",
            stroke="#FFFFFF",
            stroke_width=2,
            stroke_dasharray="6,5",
        )
    )

    dwg.save(pretty=True)
    return output_path


def main() -> None:
    gallery_dir = Path(__file__).resolve().parent
    for fname, sym_type, sym_id, pal_name, scale, rot, shx, shy, folds, grid_c, seed in GALLERY_SPECS:
        scene = generate_pattern(
            symmetry=sym_type,
            symbol_id=sym_id,
            palette=PRESET_PALETTES[pal_name],
            scale=scale,
            rotation=rot,
            shear_x=shx,
            shear_y=shy,
            folds=folds,
            grid_count=grid_c,
            seed=seed,
        )
        out = write_svg(scene, gallery_dir / fname)
        assert "transform=" not in out.read_text(encoding="utf-8")
        print(f"Generated {out.name} ({len(scene.shapes)} shapes)")

    mockup = generate_shirt_mockup(gallery_dir / "11_shirt_mockup.svg")
    assert "transform=" not in mockup.read_text(encoding="utf-8")
    print(f"Generated {mockup.name}")


if __name__ == "__main__":
    main()
