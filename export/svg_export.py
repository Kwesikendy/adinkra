"""SVG exporter using `svgwrite` for serialization ONLY.

All geometry in `PatternScene` has already been transformed by our own
`Matrix` engine. This module never uses `svgwrite` transform helpers or
SVG `transform="..."` attributes.
"""

from __future__ import annotations

from pathlib import Path
import svgwrite

from patterns import PatternScene


def _build_drawing(scene: PatternScene, filename: str = "pattern.svg") -> svgwrite.Drawing:
    dwg = svgwrite.Drawing(
        filename=filename,
        size=(f"{scene.width}px", f"{scene.height}px"),
        viewBox=f"0 0 {scene.width} {scene.height}",
    )
    # Background rectangle
    dwg.add(
        dwg.rect(
            insert=(0, 0),
            size=(scene.width, scene.height),
            fill=scene.background,
        )
    )

    for shape in scene.shapes:
        pts = [(round(x, 2), round(y, 2)) for x, y in shape.points]
        if len(pts) < 2:
            continue

        fill_val = shape.fill_color if shape.fill_color else "none"
        stroke_val = shape.stroke_color if shape.stroke_color else "none"

        if shape.closed:
            dwg.add(
                dwg.polygon(
                    points=pts,
                    fill=fill_val,
                    stroke=stroke_val,
                    stroke_width=round(shape.stroke_width, 2) if shape.stroke_color else 0,
                    stroke_linejoin="round",
                )
            )
        else:
            dwg.add(
                dwg.polyline(
                    points=pts,
                    fill="none",
                    stroke=stroke_val,
                    stroke_width=round(shape.stroke_width, 2),
                    stroke_linecap="round",
                    stroke_linejoin="round",
                )
            )

    return dwg


def scene_to_svg_string(scene: PatternScene) -> str:
    """Serialize `scene` to an SVG XML string."""
    return _build_drawing(scene).tostring()


def write_svg(scene: PatternScene, output_path: str | Path) -> Path:
    """Write `scene` to `output_path` as an SVG file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dwg = _build_drawing(scene, filename=str(path))
    dwg.save(pretty=True)
    return path
