"""Print-ready A3 PDF exporter (297 x 420 mm) using ReportLab.

All geometry placement and Y-axis inversion (SVG top-down -> PDF bottom-up)
is computed by our own `Matrix` engine rather than ReportLab canvas transforms.
"""

from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from engine.color import hex_to_rgb01
from engine.matrix import Matrix
from patterns import PatternScene


def _render_to_canvas(scene: PatternScene, c: canvas.Canvas) -> None:
    page_w, page_h = A3  # 297 mm x 420 mm in points (1 pt = 1/72 in)
    margin = 15.0 * mm
    avail_w = page_w - 2.0 * margin
    avail_h = page_h - 2.5 * margin  # extra bottom room for caption

    scale_factor = min(avail_w / max(1.0, scene.width), avail_h / max(1.0, scene.height))
    drawn_w = scene.width * scale_factor
    drawn_h = scene.height * scale_factor

    offset_x = (page_w - drawn_w) / 2.0
    offset_y = (page_h - drawn_h) / 2.0 + 4.0 * mm

    # Map SVG top-down coordinates [0..W, 0..H] to PDF bottom-up coordinates
    m_pdf = Matrix.translate(offset_x, offset_y + drawn_h) @ Matrix.scale(scale_factor, -scale_factor)

    # Draw background rectangle
    bg_r, bg_g, bg_b = hex_to_rgb01(scene.background)
    c.setFillColorRGB(bg_r, bg_g, bg_b)
    c.setStrokeColorRGB(bg_r, bg_g, bg_b)
    c.rect(offset_x, offset_y, drawn_w, drawn_h, stroke=0, fill=1)

    # Clip shapes to the artwork rectangle so overhanging edge motifs stay crisp
    c.saveState()
    clip_path = c.beginPath()
    clip_path.rect(offset_x, offset_y, drawn_w, drawn_h)
    c.clipPath(clip_path, stroke=0, fill=0)

    c.setLineCap(1)   # round cap
    c.setLineJoin(1)  # round join

    for shape in scene.shapes:
        if len(shape.points) < 2:
            continue
        pts = m_pdf.apply_many(shape.points)
        p = c.beginPath()
        p.moveTo(pts[0][0], pts[0][1])
        for x, y in pts[1:]:
            p.lineTo(x, y)
        if shape.closed:
            p.close()

        do_fill = 1 if shape.fill_color else 0
        do_stroke = 1 if shape.stroke_color else 0

        if shape.fill_color:
            r, g, b = hex_to_rgb01(shape.fill_color)
            c.setFillColorRGB(r, g, b)
        if shape.stroke_color:
            r, g, b = hex_to_rgb01(shape.stroke_color)
            c.setStrokeColorRGB(r, g, b)
            c.setLineWidth(max(0.4, shape.stroke_width * scale_factor))

        c.drawPath(p, stroke=do_stroke, fill=do_fill)

    c.restoreState()

    # Print-ready footer metadata
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.setFont("Helvetica", 9)
    meta_parts = [f"{k}: {v}" for k, v in scene.metadata.items()]
    footer = "Adinkra & Kente Pattern Generator (CSSD 315) | A3 Print (297 x 420 mm) | " + " | ".join(meta_parts)
    c.drawCentredString(page_w / 2.0, 9.0 * mm, footer)


def scene_to_pdf_bytes(scene: PatternScene) -> bytes:
    """Render `scene` to an in-memory A3 PDF byte string."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A3)
    c.setTitle("Adinkra & Kente Pattern (A3)")
    _render_to_canvas(scene, c)
    c.showPage()
    c.save()
    return buf.getvalue()


def write_pdf(scene: PatternScene, output_path: str | Path) -> Path:
    """Write `scene` to `output_path` as a print-ready A3 PDF (297 x 420 mm)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(scene_to_pdf_bytes(scene))
    return path
