"""Streamlit UI for the Adinkra & Kente Pattern Generator (CSSD 315).

Run with:
    streamlit run ui/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is importable when running `streamlit run ui/app.py`
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st
import streamlit.components.v1 as components

from engine.color import PRESET_PALETTES, Palette, hsb_to_hex, hsb_to_rgb
from export.pdf_export import scene_to_pdf_bytes
from export.svg_export import scene_to_svg_string
from kente.kente import COLOUR_MEANINGS
from patterns.factory import SYMMETRY_TYPES, generate_pattern
from symbols.loader import list_symbols


def _hsb_picker(label: str, default_hsb: tuple[float, float, float], key_prefix: str) -> tuple[float, float, float]:
    """Render H, S, B sliders and display the converted RGB/HEX value."""
    st.sidebar.markdown(f"**{label}**")
    c1, c2, c3 = st.sidebar.columns(3)
    h = c1.slider("H", 0.0, 360.0, float(default_hsb[0]), step=1.0, key=f"{key_prefix}_h")
    s = c2.slider("S", 0.0, 100.0, float(default_hsb[1]), step=1.0, key=f"{key_prefix}_s")
    b = c3.slider("B", 0.0, 100.0, float(default_hsb[2]), step=1.0, key=f"{key_prefix}_b")
    hex_val = hsb_to_hex(h, s, b)
    rgb_val = hsb_to_rgb(h, s, b)
    st.sidebar.caption(f"RGB {rgb_val} -> `{hex_val}`")
    return (h, s, b)


def main() -> None:
    st.set_page_config(
        page_title="Adinkra & Kente Pattern Generator | CSSD 315",
        layout="wide",
    )

    st.title("Adinkra & Kente Pattern Generator")
    st.caption(
        "CSSD 315 Computer Graphics — All geometry placed using a custom 3x3 homogeneous "
        "Matrix engine (no SVG transform attributes)."
    )

    # ------------------------------------------------------------------
    # Sidebar Controls
    # ------------------------------------------------------------------
    st.sidebar.header("Pattern Controls")

    sym_keys = list(SYMMETRY_TYPES.keys())
    symmetry = st.sidebar.selectbox(
        "Symmetry / Generator",
        options=sym_keys,
        format_func=lambda k: SYMMETRY_TYPES[k],
    )

    symbols = list_symbols()
    symbol_id = st.sidebar.selectbox(
        "Adinkra Symbol",
        options=symbols,
        disabled=(symmetry == "kente"),
    )

    scale = st.sidebar.slider("Motif Scale", min_value=20.0, max_value=180.0, value=78.0, step=2.0)
    rotation = st.sidebar.slider("Base Rotation (deg)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0)
    shear_x = st.sidebar.slider("Shear X", min_value=-0.8, max_value=0.8, value=0.0, step=0.05)
    shear_y = st.sidebar.slider("Shear Y", min_value=-0.8, max_value=0.8, value=0.0, step=0.05)

    folds = 8
    grid_count = 5
    tile_colors = False
    if symmetry == "rosette":
        folds = st.sidebar.slider("Rosette Folds (N)", min_value=3, max_value=16, value=8, step=1)
    elif symmetry != "hex_tiling":
        grid_count = st.sidebar.slider("Grid / Strip Count", min_value=2, max_value=9, value=5, step=1)
        if symmetry in ("mirror_grid", "square_grid"):
            tile_colors = st.sidebar.checkbox("Alternating Coloured Tiles", value=True)

    seed = int(st.sidebar.number_input("Random Seed", min_value=0, max_value=999999, value=42, step=1))

    st.sidebar.header("HSB Colour Palette")
    palette_mode = st.sidebar.radio("Palette Mode", ["Preset", "Custom HSB"])
    if palette_mode == "Preset":
        preset_name = st.sidebar.selectbox("Preset Palette", list(PRESET_PALETTES.keys()))
        palette = PRESET_PALETTES[preset_name]
    else:
        base = PRESET_PALETTES["Asante Royal Gold"]
        bg_hsb = _hsb_picker("Background", base.background_hsb, "bg")
        pri_hsb = _hsb_picker("Primary", base.primary_hsb, "pri")
        acc_hsb = _hsb_picker("Accent", base.accent_hsb, "acc")
        det_hsb = _hsb_picker("Detail", base.detail_hsb, "det")
        palette = Palette(
            name="Custom HSB",
            background_hsb=bg_hsb,
            primary_hsb=pri_hsb,
            accent_hsb=acc_hsb,
            detail_hsb=det_hsb,
        )

    # ------------------------------------------------------------------
    # Generate Scene & Render Live Preview
    # ------------------------------------------------------------------
    scene = generate_pattern(
        symmetry=symmetry,
        symbol_id=symbol_id,
        palette=palette,
        width=800.0,
        height=800.0,
        scale=scale,
        rotation=rotation,
        shear_x=shear_x,
        shear_y=shear_y,
        seed=seed,
        folds=folds,
        grid_count=grid_count,
        tile_colors=tile_colors,
    )
    svg_str = scene_to_svg_string(scene)

    col_preview, col_info = st.columns([2, 1])

    with col_preview:
        st.subheader("Live Preview")
        # Responsive HTML wrapper around the pure-coordinate SVG
        html_preview = f"""
        <div style="display:flex; justify-content:center; align-items:center;
                    border:1px solid #ddd; border-radius:8px; padding:12px; background:#f8f9fa;">
            <div style="width:100%; max-width:650px;">
                {svg_str.replace('<svg ', '<svg style="width:100%; height:auto; display:block;" ', 1)}
            </div>
        </div>
        """
        components.html(html_preview, height=690, scrolling=False)

    with col_info:
        st.subheader("Export")
        base_name = f"{symmetry}_{symbol_id}_seed{seed}"
        st.download_button(
            label="Download SVG",
            data=svg_str.encode("utf-8"),
            file_name=f"{base_name}.svg",
            mime="image/svg+xml",
            use_container_width=True,
        )

        pdf_bytes = scene_to_pdf_bytes(scene)
        st.download_button(
            label="Download Print-Ready A3 PDF (297 x 420 mm)",
            data=pdf_bytes,
            file_name=f"{base_name}_A3.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.divider()
        st.subheader("Active HSB -> HEX Palette")
        swatches = [
            ("Background", palette.background_hsb, palette.background),
            ("Primary", palette.primary_hsb, palette.primary),
            ("Accent", palette.accent_hsb, palette.accent),
            ("Detail", palette.detail_hsb, palette.detail),
        ]
        for label, hsb, hex_c in swatches:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>"
                f"<span style='display:inline-block;width:20px;height:20px;border-radius:4px;"
                f"border:1px solid #999;background:{hex_c};'></span>"
                f"<span><b>{label}</b>: HSB{hsb} &rarr; <code>{hex_c}</code></span></div>",
                unsafe_allow_html=True,
            )

        st.divider()
        st.metric("Transformed Shapes", len(scene.shapes))

    if symmetry == "kente":
        with st.expander("Kente Colour Meanings (Verify Marked Entries)", expanded=True):
            st.table(
                [
                    {
                        "Colour": c["name"],
                        "HEX": c["hex"],
                        "Meaning": c["meaning"],
                        "Verification": c["verify"],
                    }
                    for c in COLOUR_MEANINGS
                ]
            )


if __name__ == "__main__":
    main()
