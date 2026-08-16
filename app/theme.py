"""Shared Hyderabadi visual theme for the Streamlit dashboard.

Colors are inspired by Hyderabad's Charminar (maroon/sandstone), Nizami gold
work, and the city's pearl trade. Only presentation logic lives here; no
analytics.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

MAROON = "#A6192E"
GOLD = "#C9A227"
TEAL = "#0F6B72"
CREAM = "#FFF8E7"
DARK_MAROON = "#3B0A0A"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "assets" / "mandi36_logo.svg"

CHART_SEQUENCE = [MAROON, GOLD, TEAL, "#7A1F2B", "#E3B23C", "#134E4A", "#D98324"]

BRAND_CSS = f"""
<style>
.stApp {{
    background-color: {CREAM};
}}
h1, h2, h3 {{
    color: {DARK_MAROON};
    font-family: Georgia, 'Times New Roman', serif;
}}
[data-testid="stMetricValue"] {{
    color: {MAROON};
}}
.mandi-banner {{
    background: linear-gradient(90deg, {MAROON} 0%, {GOLD} 100%);
    padding: 1.1rem 1.6rem;
    border-radius: 10px;
    color: {CREAM};
    margin-bottom: 1.2rem;
    font-family: Georgia, 'Times New Roman', serif;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}}
.mandi-banner h1 {{
    color: {CREAM};
    margin: 0;
}}
.mandi-banner p {{
    color: {CREAM};
    opacity: 0.9;
    margin: 0.2rem 0 0 0;
}}
.mandi-tag {{
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.35rem;
}}
.tag-real {{ background: {TEAL}; color: white; }}
.tag-derived {{ background: {GOLD}; color: {DARK_MAROON}; }}
.tag-predicted {{ background: {MAROON}; color: white; }}
</style>
"""


def apply_theme(page_title: str) -> None:
    """Configure page chrome and inject the shared Hyderabadi CSS/banner."""
    st.set_page_config(
        page_title=f"Mandi360 | {page_title}",
        page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(BRAND_CSS, unsafe_allow_html=True)
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        st.caption("Customer experience intelligence")


def banner(title: str, subtitle: str) -> None:
    """Render the shared Charminar-inspired header banner."""
    st.markdown(
        f"""<div class="mandi-banner"><h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def data_tag(kind: str) -> str:
    """Return an inline HTML badge distinguishing real/derived/predicted data."""
    labels = {"real": "REAL DATA", "derived": "DERIVED", "predicted": "PREDICTED"}
    return f'<span class="mandi-tag tag-{kind}">{labels.get(kind, kind.upper())}</span>'


def branch_label(branch_id: str) -> str:
    """Convert an internal branch identifier into a readable business label."""
    return str(branch_id).replace("_", " ").title()
