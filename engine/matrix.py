"""2D Homogeneous Transformation Matrix Engine (CSSD 315: Computer Graphics).

This module implements a 3x3 homogeneous transformation matrix from scratch.
NumPy is used ONLY for storing the 3x3 float64 array and performing basic
matrix multiplication (`@`). No library transform helpers or `np.linalg`
functions are used.

Column-vector convention
------------------------
Every 2D point `(x, y)` is represented as a homogeneous column vector `[x, y, 1]^T`.
A transformation matrix `M` maps `(x, y)` to `(x', y')` via:

    [ x' ]   [ m00  m01  m02 ] [ x ]
    [ y' ] = [ m10  m11  m12 ] [ y ]
    [ 1  ]   [  0    0    1  ] [ 1 ]

Because we use column vectors, transformations are applied **right-to-left**:
    `(A @ B).apply(p) == A.apply(B.apply(p))`
That is, `B` happens first, then `A`.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np


Point2D = tuple[float, float]


class Matrix:
    """3x3 homogeneous transformation matrix for 2D computer graphics."""

    def __init__(self, rows: Sequence[Sequence[float]] | np.ndarray) -> None:
        """Create a Matrix from a 3x3 sequence or NumPy array."""
        arr = np.array(rows, dtype=np.float64)
        if arr.shape != (3, 3):
            raise ValueError(f"Expected a 3x3 matrix, got shape {arr.shape}")
        self.m: np.ndarray = arr

    # ------------------------------------------------------------------
    # Constructors for elementary 2D affine transformations
    # ------------------------------------------------------------------

    @classmethod
    def identity(cls) -> Matrix:
        """Return the 3x3 identity matrix (leaves every point unchanged)."""
        return cls([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])

    @classmethod
    def translate(cls, tx: float, ty: float) -> Matrix:
        """Return a translation matrix shifting points by `(tx, ty)`.

        Note why homogeneous coordinates are needed: translation is NOT linear
        in 2D, so it cannot be written as a 2x2 matrix. Adding the 3rd row
        `[0, 0, 1]` turns 2D translation into a 3x3 matrix multiplication.
        """
        return cls([
            [1.0, 0.0, float(tx)],
            [0.0, 1.0, float(ty)],
            [0.0, 0.0, 1.0],
        ])

    @classmethod
    def rotate(
        cls,
        angle_deg: float,
        pivot: tuple[float, float] | None = None,
    ) -> Matrix:
        """Return a counterclockwise rotation matrix by `angle_deg` degrees.

        If `pivot=(px, py)` is None, rotates about the origin `(0, 0)`.
        If `pivot` is provided, composes:
            `T(px, py) @ R(angle_deg) @ T(-px, -py)`
        Step 1: translate pivot to origin (`T(-px, -py)`).
        Step 2: rotate about origin (`R(angle_deg)`).
        Step 3: translate origin back to pivot (`T(px, py)`).
        """
        rad = math.radians(angle_deg)
        c = math.cos(rad)
        s = math.sin(rad)
        rot = cls([
            [c, -s, 0.0],
            [s,  c, 0.0],
            [0.0, 0.0, 1.0],
        ])
        if pivot is None:
            return rot
        px, py = pivot
        return cls.translate(px, py) @ rot @ cls.translate(-px, -py)

    @classmethod
    def scale(
        cls,
        sx: float,
        sy: float | None = None,
        pivot: tuple[float, float] | None = None,
    ) -> Matrix:
        """Return a scaling matrix by `(sx, sy)` (uniform if `sy` is None).

        If `pivot=(px, py)` is given, scales relative to that fixed point via:
            `T(px, py) @ S(sx, sy) @ T(-px, -py)`
        """
        if sy is None:
            sy = sx
        s_mat = cls([
            [float(sx), 0.0, 0.0],
            [0.0, float(sy), 0.0],
            [0.0, 0.0, 1.0],
        ])
        if pivot is None:
            return s_mat
        px, py = pivot
        return cls.translate(px, py) @ s_mat @ cls.translate(-px, -py)

    @classmethod
    def reflect_x(cls) -> Matrix:
        """Return a reflection matrix across the x-axis (`y -> -y`)."""
        return cls([
            [1.0,  0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0,  0.0, 1.0],
        ])

    @classmethod
    def reflect_y(cls) -> Matrix:
        """Return a reflection matrix across the y-axis (`x -> -x`)."""
        return cls([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 0.0, 0.0, 1.0],
        ])

    @classmethod
    def reflect_line(cls, angle_deg: float) -> Matrix:
        """Return a reflection across a line through the origin at `angle_deg`.

        Derived by rotating the line onto the x-axis (`R(-theta)`), reflecting
        across the x-axis (`reflect_x()`), and rotating back (`R(theta)`):
            `R(theta) @ reflect_x() @ R(-theta)`
        This equals:
            [[cos(2*theta),  sin(2*theta), 0],
             [sin(2*theta), -cos(2*theta), 0],
             [0,             0,            1]]
        """
        return cls.rotate(angle_deg) @ cls.reflect_x() @ cls.rotate(-angle_deg)

    @classmethod
    def shear(cls, shx: float = 0.0, shy: float = 0.0) -> Matrix:
        """Return a 2D shear matrix (`x' = x + shx*y`, `y' = shy*x + y`)."""
        return cls([
            [1.0, float(shx), 0.0],
            [float(shy), 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])

    # ------------------------------------------------------------------
    # Matrix operations: composition, inverse, and point application
    # ------------------------------------------------------------------

    def multiply(self, other: Matrix) -> Matrix:
        """Return the matrix product `self @ other`."""
        if not isinstance(other, Matrix):
            raise TypeError(f"Can only multiply Matrix by Matrix, got {type(other)}")
        return Matrix(self.m @ other.m)

    def __matmul__(self, other: Matrix) -> Matrix:
        """Support the `@` operator for composing matrices: `A @ B`."""
        return self.multiply(other)

    def inverse(self) -> Matrix:
        """Return the analytical 3x3 inverse `M^-1` (without `np.linalg.inv`).

        For an affine 3x3 matrix whose bottom row is `[0, 0, 1]`, we compute
        the full 3x3 cofactor/adjugate inverse so it works for any invertible
        3x3 matrix. Raises `ValueError` if the matrix is singular (det == 0).
        """
        m = self.m
        a, b, c = m[0, 0], m[0, 1], m[0, 2]
        d, e, f = m[1, 0], m[1, 1], m[1, 2]
        g, h, i = m[2, 0], m[2, 1], m[2, 2]

        # Cofactors of each entry
        c00 = e * i - f * h
        c01 = -(d * i - f * g)
        c02 = d * h - e * g

        c10 = -(b * i - c * h)
        c11 = a * i - c * g
        c12 = -(a * h - b * g)

        c20 = b * f - c * e
        c21 = -(a * f - c * d)
        c22 = a * e - b * d

        det = a * c00 + b * c01 + c * c02
        if abs(det) < 1e-12:
            raise ValueError("Matrix is singular (determinant is zero) and cannot be inverted.")

        inv_det = 1.0 / det
        # Adjugate is the transpose of the cofactor matrix
        return Matrix([
            [c00 * inv_det, c10 * inv_det, c20 * inv_det],
            [c01 * inv_det, c11 * inv_det, c21 * inv_det],
            [c02 * inv_det, c12 * inv_det, c22 * inv_det],
        ])

    def apply(self, point: Sequence[float]) -> Point2D:
        """Apply this transformation to a single 2D point `(x, y)`."""
        x, y = float(point[0]), float(point[1])
        vec = np.array([x, y, 1.0], dtype=np.float64)
        res = self.m @ vec
        # Divide by w in case a general projective matrix was constructed
        w = res[2]
        if abs(w) < 1e-12:
            raise ZeroDivisionError("Homogeneous coordinate w is zero.")
        return (float(res[0] / w), float(res[1] / w))

    def apply_many(self, points: Iterable[Sequence[float]]) -> list[Point2D]:
        """Apply this transformation to a sequence of 2D points.

        Packs all points into a `3 x N` homogeneous matrix and performs a single
        NumPy matrix multiplication `self.m @ pts_h`.
        """
        pts = list(points)
        if not pts:
            return []
        arr = np.array([[float(p[0]), float(p[1]), 1.0] for p in pts], dtype=np.float64)
        # arr is (N, 3); transpose to (3, N) for column-vector multiplication
        transformed = (self.m @ arr.T).T
        w = transformed[:, 2:3]
        if np.any(np.abs(w) < 1e-12):
            raise ZeroDivisionError("Homogeneous coordinate w is zero for one or more points.")
        xy = transformed[:, :2] / w
        return [(float(row[0]), float(row[1])) for row in xy]

    def approx_equal(self, other: Matrix, tol: float = 1e-9) -> bool:
        """Return True if all entries of `self` and `other` are within `tol`."""
        return bool(np.allclose(self.m, other.m, atol=tol, rtol=0.0))

    def __repr__(self) -> str:
        return f"Matrix(\n{np.array2string(self.m, precision=4, suppress_small=True)}\n)"
