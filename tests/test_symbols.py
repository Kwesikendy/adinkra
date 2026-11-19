"""Tests for Adinkra symbol loading and Bezier-to-polyline flattening."""

from engine.matrix import Matrix
from symbols.loader import flatten_cubic_bezier, flatten_quadratic_bezier, list_symbols, load_symbol

EXPECTED_SYMBOLS = {
    "gye_nyame",
    "sankofa",
    "adinkrahene",
    "dwennimmen",
    "funtunfunefu",
    "nyame_dua",
    "akoma",
    "mpuannum",
}


def test_bezier_flattening_endpoints() -> None:
    q = flatten_quadratic_bezier((0.0, 0.0), (0.5, 1.0), (1.0, 0.0), steps=10)
    assert len(q) == 10
    assert abs(q[-1][0] - 1.0) < 1e-9 and abs(q[-1][1] - 0.0) < 1e-9

    c = flatten_cubic_bezier((0.0, 0.0), (0.2, 1.0), (0.8, -1.0), (1.0, 0.0), steps=12)
    assert len(c) == 12
    assert abs(c[-1][0] - 1.0) < 1e-9 and abs(c[-1][1] - 0.0) < 1e-9


def test_all_eight_symbols_load_and_transform() -> None:
    available = set(list_symbols())
    assert EXPECTED_SYMBOLS.issubset(available), f"Missing: {EXPECTED_SYMBOLS - available}"

    m = Matrix.translate(100.0, 100.0) @ Matrix.scale(40.0)
    for sym_id in sorted(EXPECTED_SYMBOLS):
        sym = load_symbol(sym_id)
        assert sym.id == sym_id
        assert len(sym.paths) >= 2
        transformed = sym.transformed(m)
        assert len(transformed) == len(sym.paths)
        for path in transformed:
            assert len(path.points) >= 2
            for x, y in path.points:
                assert 40.0 <= x <= 160.0
                assert 40.0 <= y <= 160.0
