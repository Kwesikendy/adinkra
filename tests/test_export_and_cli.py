"""Tests for A3 PDF export, HSB colour conversion, and CLI."""

from pathlib import Path

from cli import main as cli_main
from engine.color import PRESET_PALETTES, hsb_to_hex, hsb_to_rgb
from export.pdf_export import scene_to_pdf_bytes
from patterns.factory import generate_pattern


def test_hsb_conversion() -> None:
    assert hsb_to_rgb(0.0, 100.0, 100.0) == (255, 0, 0)
    assert hsb_to_rgb(120.0, 100.0, 100.0) == (0, 255, 0)
    assert hsb_to_rgb(240.0, 100.0, 100.0) == (0, 0, 255)
    assert hsb_to_hex(0.0, 0.0, 100.0) == "#FFFFFF"
    assert hsb_to_hex(0.0, 0.0, 0.0) == "#000000"


def test_pdf_export_bytes() -> None:
    scene = generate_pattern("rosette", "sankofa", PRESET_PALETTES["Indigo Adinkra"], seed=7)
    pdf_bytes = scene_to_pdf_bytes(scene)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000


def test_cli_generates_svg_and_pdf(tmp_path: Path) -> None:
    svg_out = tmp_path / "test_out.svg"
    pdf_out = tmp_path / "test_out.pdf"
    rc = cli_main([
        "--symmetry", "square_grid",
        "--symbol", "dwennimmen",
        "--palette", "Forest & Gold",
        "--seed", "11",
        "--out", str(svg_out),
        "--pdf", str(pdf_out),
    ])
    assert rc == 0
    assert svg_out.exists() and "transform=" not in svg_out.read_text(encoding="utf-8")
    assert pdf_out.exists() and pdf_out.read_bytes().startswith(b"%PDF-")
