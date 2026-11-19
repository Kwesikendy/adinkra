# Learning Guide: 2D Transformations & Symmetry Maths (CSSD 315)

This guide explains the computer graphics mathematics behind the **Adinkra & Kente Pattern Generator** in plain English, with step-by-step numeric examples.

---

## 1. Why Do We Use Homogeneous Coordinates?

In 2D, a point is `(x, y)`. Scaling, rotation, reflection, and shear are all **linear** transformations, so they can be written as a `2 x 2` matrix multiplying `[x, y]^T`.

However, **translation** (`x' = x + tx`, `y' = y + ty`) is **not** linear: it cannot be written as a `2 x 2` matrix multiplication because a `2 x 2` matrix always maps `(0, 0)` to `(0, 0)`.

**The solution: Homogeneous Coordinates.**
We add a third coordinate `w = 1`, turning `(x, y)` into a 3D column vector `[x, y, 1]^T`, and upgrade all transformation matrices to `3 x 3`:

```text
[ x' ]   [ 1  0  tx ] [ x ]   [ x + tx ]
[ y' ] = [ 0  1  ty ] [ y ] = [ y + ty ]
[ 1  ]   [ 0  0   1 ] [ 1 ]   [   1    ]
```

Now **every** 2D affine transformation (translation, rotation, scale, reflection, shear) is a `3 x 3` matrix, and combining multiple steps is just **matrix multiplication**.

---

## 2. Worked Numeric Example: Rotate `(2, 1)` by `45°`

The counterclockwise rotation matrix by angle `θ` around the origin `(0, 0)` is:

```text
R(θ) = [ cos(θ)  -sin(θ)  0 ]
       [ sin(θ)   cos(θ)  0 ]
       [   0        0     1 ]
```

For `θ = 45°`:
- `cos(45°) = √2 / 2 ≈ 0.7071`
- `sin(45°) = √2 / 2 ≈ 0.7071`

Multiply `R(45°)` by `[2, 1, 1]^T`:

1. `x' = (0.7071)(2) + (-0.7071)(1) + (0)(1) = 1.4142 - 0.7071 = 0.7071` (exact: `√2 / 2`)
2. `y' = (0.7071)(2) + (0.7071)(1) + (0)(1) = 1.4142 + 0.7071 = 2.1213` (exact: `3√2 / 2`)
3. `w' = (0)(2) + (0)(1) + (1)(1) = 1`

Result: `(2, 1)` rotated `45°` counterclockwise becomes `(0.7071, 2.1213)`.
Notice the distance from the origin is preserved:
`√(2² + 1²) = √5 ≈ 2.2361`, and `√(0.7071² + 2.1213²) = √(0.5 + 4.5) = √5 ≈ 2.2361`.

---

## 3. Why Matrix Order Matters (Non-Commutativity)

Because we use **column vectors** (`M @ p`), transformations in a product `A @ B` are applied **right-to-left**: `B` happens first, then `A`.

Let's test this on `p = (1, 0)` with:
- `T = Matrix.translate(5, 0)` (shift right by 5)
- `R = Matrix.rotate(90)` (rotate `90°` CCW)

**Case 1: `R @ T` (Translate first, then Rotate)**
1. `T.apply((1, 0)) = (6, 0)`
2. `R.apply((6, 0)) = (0, 6)`

**Case 2: `T @ R` (Rotate first, then Translate)**
1. `R.apply((1, 0)) = (0, 1)`
2. `T.apply((0, 1)) = (5, 1)`

`(0, 6) ≠ (5, 1)`! Matrix multiplication is **not commutative**.

---

## 4. Rotating About an Arbitrary Pivot `(px, py)`

To rotate a shape around a point `(px, py)` instead of `(0, 0)`, we compose three steps:
1. `T(-px, -py)`: move the pivot to the origin.
2. `R(θ)`: rotate around the origin.
3. `T(px, py)`: move the origin back to the pivot.

```text
M_pivot = T(px, py) @ R(θ) @ T(-px, -py)
```

**Worked Example:** Rotate `(3, 1)` by `90°` around pivot `(1, 1)`:
1. `T(-1, -1)` maps `(3, 1) -> (2, 0)`.
2. `R(90°)` maps `(2, 0) -> (0, 2)`.
3. `T(1, 1)` maps `(0, 2) -> (1, 3)`.

---

## 5. How the 5 Symmetry Patterns Work

| Pattern | File | Matrix Recipe |
| :--- | :--- | :--- |
| **Rosette (`C_n`)** | `patterns/rosette.py` | `T(cx, cy) @ R(i * 360/n) @ T(0, -radius) @ M_local` |
| **Mirror Grid (`pmm`)** | `patterns/mirror_grid.py` | `T(cx, cy) @ (reflect_x / reflect_y based on row/col parity) @ M_local` |
| **Glide Frieze (`p11g`)** | `patterns/frieze.py` | Even step: `T(x, y - dy) @ M_local`; Odd step: `T(x, y + dy) @ reflect_x() @ M_local` |
| **Hexagonal Tiling (`p6`)** | `patterns/hex_tiling.py` | Offset rows by `spacing/2`, place 6-fold rosette at each lattice node `(cx, cy)` |
| **Square Grid (`p4`)** | `patterns/square_grid.py` | `T(cx, cy) @ R(k * 90°) @ T(offset, -offset) @ M_local` for `k = 0..3` |

---

## 6. Bezier Curves to Polylines

Our Adinkra symbols use cubic Bezier curves `B(t)` for smooth horns and spirals:

`B(t) = (1-t)³ P0 + 3(1-t)²t P1 + 3(1-t)t² P2 + t³ P3` for `t ∈ [0, 1]`.

In `symbols/loader.py`, we sample `t` at 16 equal steps to turn each curve into a polyline, then transform every vertex with `Matrix.apply_many()`.
