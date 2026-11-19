"""Load Adinkra vector symbols from JSON and flatten Bezier curves to polylines.

Each symbol is stored in normalized local coordinates centered at `(0, 0)`
within approximately `[-1, 1] x [-1, 1]`.

Why flatten Bezier curves to polylines?
--------------------------------------
An affine transformation (our 3x3 `Matrix`) maps straight lines to straight
lines, and it also maps Bezier control points accurately. However, by flattening
curves to dense polylines in local space first and then transforming every
vertex with `Matrix.apply_many()`, we guarantee that:
1. All final SVG/PDF coordinates are 100% computed by our own `Matrix` engine.
2. No SVG `<path>` curve or `transform` helper is needed to place shapes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from engine.matrix import Matrix, Point2D

SYMBOLS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class SymbolPath:
    """A single polyline subpath belonging to a symbol."""

    points: tuple[Point2D, ...]
    closed: bool = True
    fill: bool = True
    role: str = "primary"  # "primary", "accent", or "cutout"
    stroke_width: float = 0.06  # Relative to [-1, 1] local space


@dataclass(frozen=True)
class Symbol:
    """A complete Adinkra symbol made of one or more polylines."""

    id: str
    name: str
    paths: tuple[SymbolPath, ...]

    def transformed(self, matrix: Matrix) -> list[SymbolPath]:
        """Return a new list of `SymbolPath`s with all points transformed by `matrix`."""
        result: list[SymbolPath] = []
        for path in self.paths:
            pts = tuple(matrix.apply_many(path.points))
            result.append(
                SymbolPath(
                    points=pts,
                    closed=path.closed,
                    fill=path.fill,
                    role=path.role,
                    stroke_width=path.stroke_width,
                )
            )
        return result


def flatten_quadratic_bezier(
    p0: Point2D, p1: Point2D, p2: Point2D, steps: int = 14
) -> list[Point2D]:
    """Sample a quadratic Bezier curve B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2."""
    pts: list[Point2D] = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1.0 - t
        x = u * u * p0[0] + 2.0 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2.0 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def flatten_cubic_bezier(
    p0: Point2D, p1: Point2D, p2: Point2D, p3: Point2D, steps: int = 16
) -> list[Point2D]:
    """Sample a cubic Bezier curve from P0 to P3 with control points P1, P2."""
    pts: list[Point2D] = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1.0 - t
        u2 = u * u
        t2 = t * t
        x = (u2 * u) * p0[0] + 3.0 * u2 * t * p1[0] + 3.0 * u * t2 * p2[0] + (t2 * t) * p3[0]
        y = (u2 * u) * p0[1] + 3.0 * u2 * t * p1[1] + 3.0 * u * t2 * p2[1] + (t2 * t) * p3[1]
        pts.append((x, y))
    return pts


def _parse_segments(segments: Sequence[dict], bezier_steps: int = 16) -> tuple[Point2D, ...]:
    """Convert a list of M/L/Q/C segment dicts into a tuple of 2D polyline points."""
    pts: list[Point2D] = []
    current: Point2D = (0.0, 0.0)

    for seg in segments:
        seg_type = seg["type"].upper()
        if seg_type == "M":
            current = (float(seg["to"][0]), float(seg["to"][1]))
            pts.append(current)
        elif seg_type == "L":
            nxt = (float(seg["to"][0]), float(seg["to"][1]))
            pts.append(nxt)
            current = nxt
        elif seg_type == "Q":
            ctrl = (float(seg["ctrl"][0]), float(seg["ctrl"][1]))
            nxt = (float(seg["to"][0]), float(seg["to"][1]))
            pts.extend(flatten_quadratic_bezier(current, ctrl, nxt, steps=bezier_steps))
            current = nxt
        elif seg_type == "C":
            c1 = (float(seg["ctrl1"][0]), float(seg["ctrl1"][1]))
            c2 = (float(seg["ctrl2"][0]), float(seg["ctrl2"][1]))
            nxt = (float(seg["to"][0]), float(seg["to"][1]))
            pts.extend(flatten_cubic_bezier(current, c1, c2, nxt, steps=bezier_steps))
            current = nxt
        else:
            raise ValueError(f"Unsupported segment type: {seg_type}")

    return tuple(pts)


def load_symbol(symbol_id: str, bezier_steps: int = 16) -> Symbol:
    """Load a symbol JSON file from `/symbols/<symbol_id>.json`."""
    path = SYMBOLS_DIR / f"{symbol_id}.json"
    if not path.exists():
        available = ", ".join(list_symbols())
        raise FileNotFoundError(f"Symbol '{symbol_id}' not found. Available: {available}")

    data = json.loads(path.read_text(encoding="utf-8"))
    parsed_paths: list[SymbolPath] = []
    for p in data["paths"]:
        pts = _parse_segments(p["segments"], bezier_steps=bezier_steps)
        parsed_paths.append(
            SymbolPath(
                points=pts,
                closed=bool(p.get("closed", True)),
                fill=bool(p.get("fill", True)),
                role=str(p.get("role", "primary")),
                stroke_width=float(p.get("stroke_width", 0.06)),
            )
        )

    return Symbol(id=data["id"], name=data["name"], paths=tuple(parsed_paths))


def list_symbols() -> list[str]:
    """Return sorted list of available symbol IDs in `/symbols/`."""
    return sorted(p.stem for p in SYMBOLS_DIR.glob("*.json"))
