"""Tests for Kente strip generator and COLOUR_MEANINGS."""

from export.svg_export import scene_to_svg_string
from kente.kente import COLOUR_MEANINGS, generate_kente_strips


def test_colour_meanings_documented() -> None:
    assert len(COLOUR_MEANINGS) >= 6
    for entry in COLOUR_MEANINGS:
        assert "name" in entry and "hex" in entry and "meaning" in entry and "verify" in entry
        assert str(entry["hex"]).startswith("#") and len(str(entry["hex"])) == 7


def test_kente_seeded_determinism_and_svg() -> None:
    s1 = generate_kente_strips(num_strips=5, seed=99)
    s2 = generate_kente_strips(num_strips=5, seed=99)
    s3 = generate_kente_strips(num_strips=5, seed=100)

    assert len(s1.shapes) > 50
    assert s1.shapes == s2.shapes
    assert s1.shapes != s3.shapes

    svg = scene_to_svg_string(s1)
    assert "transform=" not in svg
    assert "<polygon" in svg
