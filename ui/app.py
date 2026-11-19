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

STYLES_PATH = Path(__file__).resolve().parent / "styles.css"


def _load_css() -> None:
    if STYLES_PATH.exists():
        css = STYLES_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


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
    _load_css()

    # Clean geometric studio header (no pill badges, no em dashes, no gradient text)
    st.markdown(
        """
        <div class="studio-header">
          <div class="studio-mark" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9"/>
              <circle cx="12" cy="12" r="5"/>
              <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
            </svg>
          </div>
          <div>
            <h1 class="studio-title">Adinkra &amp; Kente Pattern Studio</h1>
            <p class="studio-subtitle">CSSD 315 Computer Graphics - Pre-transformed vector geometry from our 3x3 Matrix engine</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
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

    col_preview, col_info = st.columns([2.1, 1.0], gap="large")

    with col_preview:
        st.subheader("Drafting Canvas")
        # Responsive HTML wrapper matching our matte neumorphic drafting well
        html_preview = f"""
        <style>
          body {{
            margin: 0;
            padding: 8px;
            background: #EEF2F6;
            font-family: system-ui, sans-serif;
          }}
          .well {{
            background: #EEF2F6;
            border-radius: 22px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.55);
            box-shadow: inset -4px -4px 10px rgba(255,255,255,0.8), inset 4px 4px 10px rgba(163,177,198,0.45);
          }}
          .mat {{
            max-width: 640px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 2px solid #CBD5E1;
            border-radius: 14px;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.08);
            animation: fadeUp 0.28s ease-out;
          }}
          @keyframes fadeUp {{
            from {{ opacity: 0.45; transform: translateY(3px); }}
            to {{ opacity: 1; transform: translateY(0); }}
          }}
          @media (prefers-reduced-motion: reduce) {{
            .mat {{ animation: none; }}
          }}
        </style>
        <div class="well">
          <div class="mat">
            {svg_str.replace('<svg ', '<svg style="width:100%; height:auto; display:block; border-radius:8px;" ', 1)}
          </div>
        </div>
        """
        components.html(html_preview, height=705, scrolling=False)

    with col_info:
        st.subheader("Print & Vector Export")
        base_name = f"{symmetry}_{symbol_id}_seed{seed}"
        st.download_button(
            label="Download SVG (Pre-transformed)",
            data=svg_str.encode("utf-8"),
            file_name=f"{base_name}.svg",
            mime="image/svg+xml",
            use_container_width=True,
        )

        pdf_bytes = scene_to_pdf_bytes(scene)
        st.download_button(
            label="Download A3 PDF (297 x 420 mm)",
            data=pdf_bytes,
            file_name=f"{base_name}_A3.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.subheader("HSB Palette Swatches")
        swatches = [
            ("Background", palette.background_hsb, palette.background),
            ("Primary", palette.primary_hsb, palette.primary),
            ("Accent", palette.accent_hsb, palette.accent),
            ("Detail", palette.detail_hsb, palette.detail),
        ]
        swatch_html = "".join(
            f"""
            <div class="clay-swatch">
              <div class="clay-chip" style="background:{hex_c};"></div>
              <div>
                <div class="clay-swatch-label">{label}</div>
                <div class="clay-swatch-meta">HSB({int(hsb[0])}, {int(hsb[1])}%, {int(hsb[2])}%) -> {hex_c}</div>
              </div>
            </div>
            """
            for label, hsb, hex_c in swatches
        )
        st.markdown(swatch_html, unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="neu-panel">
              <div style="font-size:0.8rem; color:#4A5568; text-transform:uppercase; letter-spacing:0.04em;">
                Computed Geometry
              </div>
              <div style="font-size:1.6rem; font-weight:700; color:#161B22; margin-top:4px;">
                {len(scene.shapes):,} shapes
              </div>
              <div style="font-size:0.82rem; color:#4A5568; margin-top:2px;">
                0 SVG transform attributes
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
