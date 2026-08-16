"""Customer Patterns view — recurring review groups and co-occurring issues."""
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
from app.theme import CHART_SEQUENCE, apply_theme, banner, business_dataframe, data_tag

apply_theme("Data Mining")
banner("Data Mining for Customer Patterns", "Recurring review groups and issues that appear together")
st.markdown(
    data_tag("derived") + " This page supports the Data Mining subject while keeping the findings manager-friendly. "
    "These patterns help managers decide where to investigate first. "
    "They show issues that move together, not confirmed cause-and-effect.",
    unsafe_allow_html=True,
)

st.subheader("Recurring Review Groups")
cluster_model = load_cluster_model()
if cluster_model:
    st.caption(
        f"Review groups found: {cluster_model['params']['selected_k']} · "
        f"Reviews analyzed: {cluster_model['params']['documents_used']:,}"
    )
    clusters_df = pd.DataFrame(cluster_model["clusters"])
    clusters_df["customer_group"] = [f"Group {index}" for index in range(1, len(clusters_df) + 1)]
    clusters_df["top_terms"] = clusters_df["top_terms"].apply(lambda terms: ", ".join(terms[:6]))
    fig = px.bar(
        clusters_df,
        x="customer_group",
        y="size",
        color="customer_group",
        color_discrete_sequence=CHART_SEQUENCE,
        labels={"customer_group": "customer group", "size": "reviews in group"},
    )
    fig.update_layout(showlegend=False, title="Recurring Customer Groups")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        clusters_df[["customer_group", "size", "top_terms"]].rename(
            columns={"customer_group": "customer group", "size": "reviews in group", "top_terms": "common customer words"}
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Recurring review groups are not available yet. Refresh the latest review analysis first.")

st.subheader("Issues That Appear Together")
rules_result = load_association_rules()
if rules_result and rules_result.get("rules"):
    rules_df = pd.DataFrame(rules_result["rules"])
    rules_df["antecedent"] = rules_df["antecedent"].apply(lambda items: ", ".join(items))
    rules_df["consequent"] = rules_df["consequent"].apply(lambda items: ", ".join(items))
    fig2 = px.scatter(
        rules_df, x="support", y="confidence", size="lift", color="lift",
        hover_data=["antecedent", "consequent"], color_continuous_scale=["#F6E3B4", "#A6192E"],
        title="How Common and Reliable Each Pattern Is",
        labels={
            "support": "frequency",
            "confidence": "reliability",
            "lift": "strength of pattern",
            "antecedent": "when customers mention",
            "consequent": "they also mention",
        },
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(
        business_dataframe(rules_df.sort_values("lift", ascending=False), ["antecedent", "consequent", "support", "confidence", "lift"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No strong issue combinations were found, or this summary is not available yet.")
