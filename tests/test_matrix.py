"""Unit tests for the 3x3 homogeneous Matrix engine."""

import math
import pytest

from engine.matrix import Matrix


def assert_point_close(actual: tuple[float, float], expected: tuple[float, float], tol: float = 1e-9) -> None:
    assert abs(actual[0] - expected[0]) < tol, f"x: {actual[0]} != {expected[0]}"
    assert abs(actual[1] - expected[1]) < tol, f"y: {actual[1]} != {expected[1]}"


def test_identity() -> None:
    m = Matrix.identity()
    assert_point_close(m.apply((3.5, -7.2)), (3.5, -7.2))


def test_translate() -> None:
    m = Matrix.translate(10.0, -4.0)
    assert_point_close(m.apply((2.0, 5.0)), (12.0, 1.0))


def test_rotate_origin() -> None:
    # (1, 0) rotated 90 deg CCW -> (0, 1)
    r90 = Matrix.rotate(90.0)
    assert_point_close(r90.apply((1.0, 0.0)), (0.0, 1.0))

    # Worked example from LEARNING.md: (2, 1) rotated 45 deg CCW
    r45 = Matrix.rotate(45.0)
    c = math.cos(math.radians(45.0))
    s = math.sin(math.radians(45.0))
    assert_point_close(r45.apply((2.0, 1.0)), (2.0 * c - 1.0 * s, 2.0 * s + 1.0 * c))


def test_rotate_about_pivot() -> None:
    # Rotate (3, 1) by 90 degrees about pivot (1, 1) -> (1, 3)
    m = Matrix.rotate(90.0, pivot=(1.0, 1.0))
    assert_point_close(m.apply((3.0, 1.0)), (1.0, 3.0))
    # Pivot itself remains fixed
    assert_point_close(m.apply((1.0, 1.0)), (1.0, 1.0))


def test_scale_origin_and_pivot() -> None:
    s_uniform = Matrix.scale(2.5)
    assert_point_close(s_uniform.apply((2.0, -4.0)), (5.0, -10.0))

    s_nonuniform = Matrix.scale(2.0, 0.5)
    assert_point_close(s_nonuniform.apply((3.0, 8.0)), (6.0, 4.0))

    # Scale (4, 3) by 2x about pivot (2, 1) -> (6, 5)
    s_pivot = Matrix.scale(2.0, 2.0, pivot=(2.0, 1.0))
    assert_point_close(s_pivot.apply((4.0, 3.0)), (6.0, 5.0))
    assert_point_close(s_pivot.apply((2.0, 1.0)), (2.0, 1.0))


def test_reflect_x_y_and_line() -> None:
    assert_point_close(Matrix.reflect_x().apply((3.0, 5.0)), (3.0, -5.0))
    assert_point_close(Matrix.reflect_y().apply((3.0, 5.0)), (-3.0, 5.0))

    # Reflect across y = x (45-degree line through origin) swaps (x, y) -> (y, x)
    ref45 = Matrix.reflect_line(45.0)
    assert_point_close(ref45.apply((2.0, 7.0)), (7.0, 2.0))

    # Reflect across 30-degree line twice returns the original point
    ref30 = Matrix.reflect_line(30.0)
    assert (ref30 @ ref30).approx_equal(Matrix.identity())


def test_shear() -> None:
    sh = Matrix.shear(shx=0.5, shy=0.25)
    # x' = 2 + 0.5*4 = 4, y' = 0.25*2 + 4 = 4.5
    assert_point_close(sh.apply((2.0, 4.0)), (4.0, 4.5))


def test_composition_order_matters() -> None:
    t = Matrix.translate(5.0, 0.0)
    r = Matrix.rotate(90.0)
    p = (1.0, 0.0)

    # (R @ T) translates first -> (6, 0), then rotates 90 deg -> (0, 6)
    rt = r @ t
    assert_point_close(rt.apply(p), (0.0, 6.0))
    assert_point_close(rt.apply(p), r.apply(t.apply(p)))

    # (T @ R) rotates first -> (0, 1), then translates -> (5, 1)
    tr = t @ r
    assert_point_close(tr.apply(p), (5.0, 1.0))
    assert_point_close(tr.apply(p), t.apply(r.apply(p)))

    assert not rt.approx_equal(tr)


def test_inverse() -> None:
    m = Matrix.translate(12.0, -7.0) @ Matrix.rotate(37.0, pivot=(3.0, 4.0)) @ Matrix.shear(0.3, -0.2) @ Matrix.scale(1.5, 0.8)
    inv = m.inverse()

    assert (m @ inv).approx_equal(Matrix.identity())
    assert (inv @ m).approx_equal(Matrix.identity())

    p = (4.2, -9.1)
    transformed = m.apply(p)
    recovered = inv.apply(transformed)
    assert_point_close(recovered, p)


def test_singular_matrix_inverse_raises() -> None:
    singular = Matrix.scale(0.0, 2.0)
    with pytest.raises(ValueError, match="singular"):
        singular.inverse()


def test_apply_many() -> None:
    m = Matrix.translate(1.0, 2.0) @ Matrix.scale(2.0)
    pts = [(0.0, 0.0), (1.0, 1.0), (-2.0, 3.0)]
    out = m.apply_many(pts)
    expected = [(1.0, 2.0), (3.0, 4.0), (-3.0, 8.0)]
    assert len(out) == len(expected)
    for a, e in zip(out, expected):
        assert_point_close(a, e)
    assert m.apply_many([]) == []
