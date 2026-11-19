"""Tests for Adinkra symbol loading and Bezier-to-polyline flattening."""

from engine.matrix import Matrix
from symbols.loader import flatten_cubic_bezier, flatten_quadratic_bezier, list_symbols, load_symbol


def test_bezier_flattening_endpoints() -> None:
    q = flatten_quadratic_bezier((0.0, 0.0), (0.5, 1.0), (1.0, 0.0), steps=10)
    assert len(q) == 10
    assert abs(q[-1][0] - 1.0) < 1e-9 and abs(q[-1][1] - 0.0) < 1e-9

    c = flatten_cubic_bezier((0.0, 0.0), (0.2, 1.0), (0.8, -1.0), (1.0, 0.0), steps=12)
    assert len(c) == 12
    assert abs(c[-1][0] - 1.0) < 1e-9 and abs(c[-1][1] - 0.0) < 1e-9


def test_load_gye_nyame_and_transform() -> None:
    assert "gye_nyame" in list_symbols()
    sym = load_symbol("gye_nyame")
    assert sym.id == "gye_nyame"
    assert len(sym.paths) >= 4
    for p in sym.paths:
        assert len(p.points) >= 2

    # Transform using our Matrix engine
    m = Matrix.translate(100.0, 100.0) @ Matrix.scale(40.0)
    transformed = sym.transformed(m)
    assert len(transformed) == len(sym.paths)
    # Check points are near (100, 100) within radius ~40
    for path in transformed:
        for x, y in path.points:
            assert 40.0 <= x <= 160.0
            assert 40.0 <= y <= 160.0
