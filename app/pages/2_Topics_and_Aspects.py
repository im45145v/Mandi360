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
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag

apply_theme("Topics & Aspects")
banner("Topics & Aspects", "Recurring customer themes and experience dimensions")

st.markdown(
    data_tag("derived") + " Themes are discovered from review language; experience dimensions "
    "use a transparent keyword baseline. These are signals for management review, not final labels.",
    unsafe_allow_html=True,
)

topic_model = load_topic_model()
if topic_model:
    st.caption(
        f"Themes identified: {topic_model['params']['num_topics_fitted']} · "
        f"Reviews analyzed: {topic_model['params']['documents_used']:,}"
    )
    for topic in topic_model["topics"]:
        with st.expander(f"Theme {topic['topic_id'] + 1} — representative terms: {', '.join(topic['top_terms'][:5])}"):
            df = pd.DataFrame({"term": topic["top_terms"], "weight": topic["top_term_weights"]})
            fig = px.bar(df, x="weight", y="term", orientation="h", color_discrete_sequence=[CHART_SEQUENCE[0]])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Topic model not available yet. Run `python -m src.pipeline`.")

st.subheader("Experience Dimensions")
aspects = load_review_aspects()
if not aspects.empty:
    branches = ["All"] + sorted(aspects["branch_id"].dropna().unique().tolist())
    selected = st.selectbox("Branch", branches)
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
        fig.update_layout(showlegend=False, title="Aspect Mention Volume")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(agg, x="aspect", y="average_sentiment_score", color="aspect", color_discrete_sequence=CHART_SEQUENCE)
        fig2.update_layout(showlegend=False, title="Average Aspect Sentiment")
        st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(agg, use_container_width=True)
else:
    st.info("Aspect table not available yet.")
