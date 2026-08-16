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
    labels = {"real": "COLLECTED", "derived": "ANALYSIS", "predicted": "OUTLOOK"}
    return f'<span class="mandi-tag tag-{kind}">{labels.get(kind, kind.upper())}</span>'


def branch_label(branch_id: str) -> str:
    """Convert an internal branch identifier into a readable business label."""
    return str(branch_id).replace("_", " ").title()


def experience_label(value: str) -> str:
    """Convert an internal experience-area value into manager-friendly text."""
    labels = {
        "ambience": "Ambience",
        "food_quality": "Food Quality",
        "price_value": "Price and Value",
        "service": "Service",
        "wait_time": "Wait Time",
    }
    return labels.get(str(value), str(value).replace("_", " ").title())


BUSINESS_COLUMN_LABELS = {
    "alert_reasons": "why it needs attention",
    "alert_severity": "urgency",
    "anomaly_score": "unusualness indicator",
    "aspect": "experience area",
    "average_rating": "average rating",
    "average_sentiment_score": "customer mood indicator",
    "branch_id": "branch",
    "branch_name": "branch",
    "cluster_id": "customer group",
    "confidence": "reliability",
    "consequent": "also mentioned",
    "dominant_topic": "main theme",
    "issue": "customer issue",
    "lift": "strength of pattern",
    "mention_count": "mentions",
    "month": "month",
    "negative_lift": "negative-review concentration",
    "negative_mentions": "negative mentions",
    "negative_ratio": "negative feedback share",
    "negative_share": "share within negative reviews",
    "negative_share_pct": "negative share %",
    "overall_share": "overall share",
    "positive_mentions": "positive mentions",
    "priority": "priority",
    "priority_score": "priority indicator",
    "predicted_average_rating": "expected rating",
    "rating": "rating",
    "recommended_action": "recommended action",
    "review_count": "reviews",
    "review_date": "review date",
    "review_id": "review reference",
    "review_text": "customer comment",
    "sentiment_label": "customer mood",
    "sentiment_score": "customer mood indicator",
    "size": "reviews in group",
    "support": "frequency",
    "top_terms": "common words",
    "total_mentions": "total mentions",
    "lower_bound": "lower expected range",
    "upper_bound": "upper expected range",
}


def business_dataframe(df, columns=None):
    """Return a copy with presentation-friendly labels and values."""
    if columns is not None:
        columns = [column for column in columns if column in df.columns]
        df = df[columns]
    display_df = df.copy()
    for column in ("branch_id", "branch_name"):
        if column in display_df.columns:
            display_df[column] = display_df[column].map(branch_label)
    for column in ("aspect", "issue"):
        if column in display_df.columns:
            display_df[column] = display_df[column].map(experience_label)
    return display_df.rename(columns=BUSINESS_COLUMN_LABELS)
