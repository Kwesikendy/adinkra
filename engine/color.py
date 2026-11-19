"""HSB (Hue, Saturation, Brightness) to RGB and HEX colour conversion.

Implemented from scratch for CSSD 315 so students can see how perceptual
HSB colour sliders map to 8-bit RGB channels and SVG/PDF hex strings.
"""

from __future__ import annotations

from dataclasses import dataclass


def hsb_to_rgb(hue_deg: float, saturation: float, brightness: float) -> tuple[int, int, int]:
    """Convert HSB (H in [0, 360], S in [0, 100], B in [0, 100]) to (R, G, B) in [0, 255]."""
    h = float(hue_deg) % 360.0
    s = max(0.0, min(100.0, float(saturation))) / 100.0
    v = max(0.0, min(100.0, float(brightness))) / 100.0

    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v - c

    if h < 60.0:
        r1, g1, b1 = c, x, 0.0
    elif h < 120.0:
        r1, g1, b1 = x, c, 0.0
    elif h < 180.0:
        r1, g1, b1 = 0.0, c, x
    elif h < 240.0:
        r1, g1, b1 = 0.0, x, c
    elif h < 300.0:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    r = round((r1 + m) * 255.0)
    g = round((g1 + m) * 255.0)
    b = round((b1 + m) * 255.0)
    return (r, g, b)


def hsb_to_hex(hue_deg: float, saturation: float, brightness: float) -> str:
    """Convert HSB to a `#RRGGBB` hex string."""
    r, g, b = hsb_to_rgb(hue_deg, saturation, brightness)
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb01(hex_color: str) -> tuple[float, float, float]:
    """Convert `#RRGGBB` to normalized `(r, g, b)` floats in `[0.0, 1.0]` for ReportLab."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Expected 6-digit hex colour, got '{hex_color}'")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


@dataclass(frozen=True)
class Palette:
    """Four-colour pattern palette defined in HSB space and converted to HEX."""

    name: str
    background_hsb: tuple[float, float, float]
    primary_hsb: tuple[float, float, float]
    accent_hsb: tuple[float, float, float]
    detail_hsb: tuple[float, float, float]

    @property
    def background(self) -> str:
        return hsb_to_hex(*self.background_hsb)

    @property
    def primary(self) -> str:
        return hsb_to_hex(*self.primary_hsb)

    @property
    def accent(self) -> str:
        return hsb_to_hex(*self.accent_hsb)

    @property
    def detail(self) -> str:
        return hsb_to_hex(*self.detail_hsb)

    def color_for_role(self, role: str) -> str:
        if role == "primary":
            return self.primary
        if role == "accent":
            return self.accent
        if role == "cutout":
            return self.background
        return self.detail


# Curated HSB palettes inspired by traditional Adinkra cloth & Kente dyes
PRESET_PALETTES: dict[str, Palette] = {
    "Asante Royal Gold": Palette(
        name="Asante Royal Gold",
        background_hsb=(36.0, 18.0, 96.0),
        primary_hsb=(25.0, 75.0, 18.0),
        accent_hsb=(42.0, 88.0, 85.0),
        detail_hsb=(14.0, 80.0, 58.0),
    ),
    "Indigo Adinkra": Palette(
        name="Indigo Adinkra",
        background_hsb=(42.0, 12.0, 95.0),
        primary_hsb=(222.0, 72.0, 32.0),
        accent_hsb=(196.0, 65.0, 56.0),
        detail_hsb=(38.0, 78.0, 78.0),
    ),
    "Kuntunkuni Mourning": Palette(
        name="Kuntunkuni Mourning",
        background_hsb=(0.0, 0.0, 12.0),
        primary_hsb=(40.0, 18.0, 90.0),
        accent_hsb=(2.0, 74.0, 55.0),
        detail_hsb=(42.0, 68.0, 75.0),
    ),
    "Forest & Gold": Palette(
        name="Forest & Gold",
        background_hsb=(46.0, 14.0, 96.0),
        primary_hsb=(148.0, 68.0, 34.0),
        accent_hsb=(44.0, 90.0, 86.0),
        detail_hsb=(12.0, 72.0, 48.0),
    ),
    "Terracotta Earth": Palette(
        name="Terracotta Earth",
        background_hsb=(34.0, 22.0, 94.0),
        primary_hsb=(14.0, 76.0, 48.0),
        accent_hsb=(38.0, 82.0, 80.0),
        detail_hsb=(24.0, 55.0, 22.0),
    ),
}
