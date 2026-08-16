"""Data Mining view — clustering and association rule mining results."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from app.data_loader import load_association_rules, load_cluster_model
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag

apply_theme("Data Mining")
banner("Data Mining", "Review clustering and association-rule mining")
st.markdown(
    data_tag("derived") + " These patterns help prioritize investigation. They show association, "
    "not confirmed cause-and-effect.",
    unsafe_allow_html=True,
)

st.subheader("Recurring Review Groups")
cluster_model = load_cluster_model()
if cluster_model:
    st.caption(
        f"Selected k: {cluster_model['params']['selected_k']} · "
        f"Silhouette score (sampled): {cluster_model['selected_silhouette_score']} · "
        f"Documents used: {cluster_model['params']['documents_used']:,}"
    )
    clusters_df = pd.DataFrame(cluster_model["clusters"])
    clusters_df["top_terms"] = clusters_df["top_terms"].apply(lambda terms: ", ".join(terms[:6]))
    fig = px.bar(clusters_df, x="cluster_id", y="size", color="cluster_id", color_discrete_sequence=CHART_SEQUENCE)
    fig.update_layout(showlegend=False, title="Cluster Sizes")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(clusters_df, use_container_width=True)
else:
    st.warning("Clustering results not available yet. Run `python -m src.pipeline`.")

st.subheader("Feedback Combinations")
rules_result = load_association_rules()
if rules_result and rules_result.get("rules"):
    rules_df = pd.DataFrame(rules_result["rules"])
    rules_df["antecedent"] = rules_df["antecedent"].apply(lambda items: ", ".join(items))
    rules_df["consequent"] = rules_df["consequent"].apply(lambda items: ", ".join(items))
    fig2 = px.scatter(
        rules_df, x="support", y="confidence", size="lift", color="lift",
        hover_data=["antecedent", "consequent"], color_continuous_scale=["#F6E3B4", "#A6192E"],
        title="Support vs Confidence (bubble size/color = lift)",
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(rules_df.sort_values("lift", ascending=False), use_container_width=True)
else:
    st.info("No association rules met the support/confidence thresholds, or results are not available yet.")
