"""Topics & Aspects view — recurring themes and experience dimensions."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from app.data_loader import load_review_aspects, load_topic_model
from app.display import branch_label, business_dataframe
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag

apply_theme("Customer Themes")
banner("Customer Themes", "Recurring customer topics and experience areas")

st.markdown(
    data_tag("derived") + " Themes are discovered from review language; experience areas "
    "use a transparent keyword review. Treat them as management signals, not final labels.",
    unsafe_allow_html=True,
)

topic_model = load_topic_model()
if topic_model:
    st.caption(
        f"Themes identified: {topic_model['params']['num_topics_fitted']} · "
        f"Reviews analyzed: {topic_model['params']['documents_used']:,}"
    )
    for display_number, topic in enumerate(topic_model["topics"], start=1):
        with st.expander(f"Theme {display_number}: {', '.join(topic['top_terms'][:5]).title()}"):
            df = pd.DataFrame({"customer words": topic["top_terms"][:8], "relative importance": topic["top_term_weights"][:8]})
            fig = px.bar(df, x="relative importance", y="customer words", orientation="h", color_discrete_sequence=[CHART_SEQUENCE[0]])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            fig.update_xaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Customer themes are not available yet. Refresh the latest review analysis first.")

st.subheader("Experience Areas")
aspects = load_review_aspects()
if not aspects.empty:
    branch_ids = sorted(aspects["branch_id"].dropna().unique().tolist())
    branch_options = {"All": "All"} | {branch_label(branch_id): branch_id for branch_id in branch_ids}
    selected_label = st.selectbox("Branch", list(branch_options.keys()))
    selected = branch_options[selected_label]
    filtered = aspects if selected == "All" else aspects[aspects["branch_id"] == selected]

    agg = (
        filtered.groupby("aspect")
        .agg(mention_count=("aspect", "count"), average_sentiment_score=("aspect_sentiment_score", "mean"))
        .reset_index()
        .sort_values("mention_count", ascending=False)
    )
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(agg, x="aspect", y="mention_count", color="aspect", color_discrete_sequence=CHART_SEQUENCE)
        fig.update_layout(showlegend=False, title="Customer Mention Volume")
        fig.update_xaxes(title="experience area")
        fig.update_yaxes(title="mentions")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(agg, x="aspect", y="average_sentiment_score", color="aspect", color_discrete_sequence=CHART_SEQUENCE)
        fig2.update_layout(showlegend=False, title="Average Customer Mood by Area")
        fig2.update_xaxes(title="experience area")
        fig2.update_yaxes(title="customer mood indicator")
        st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(
        business_dataframe(agg, ["aspect", "mention_count", "average_sentiment_score"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Experience-area summary is not available yet.")
