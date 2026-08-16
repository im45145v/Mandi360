"""Negative Insights — dedicated fault-finding view mining negative feedback.

Most reviews are positive, but recurring faults surface in the negative
minority. This page isolates negative feedback across branches and periods,
compares it against positive feedback, and surfaces the aspects/topics that
disproportionately drive dissatisfaction, alongside evidence-ranked fixes.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from app.data_loader import (
    load_anomalies,
    load_crm_cases,
    load_nlp_reviews,
    load_review_aspects,
    load_review_topics,
    load_topic_model,
)
from app.theme import CHART_SEQUENCE, apply_theme, banner, branch_label, business_dataframe, data_tag
from app.visuals import show_wordcloud

apply_theme("Negative Insights")
banner("Negative Feedback Insights", "CRM-focused view of complaints, service gaps, and recovery priorities")
st.markdown(
    data_tag("real") + data_tag("derived")
    + " Rating buckets below come from collected reviews. Customer mood, experience-area, and theme breakdowns "
    "are analytical signals that describe correlation, not confirmed cause. Verify before acting.",
    unsafe_allow_html=True,
)

reviews = load_nlp_reviews()
if reviews.empty:
    st.warning("Negative feedback insights are not available yet. Refresh the latest review analysis first.")
    st.stop()

reviews = reviews.copy()
reviews["review_month"] = pd.to_datetime(reviews["review_date"], errors="coerce").dt.to_period("M").astype(str)
reviews["rating_bucket"] = pd.cut(
    reviews["rating"],
    bins=[0, 2, 3, 5],
    labels=["Negative (1-2)", "Neutral (3)", "Positive (4-5)"],
    include_lowest=True,
)

branches = sorted(reviews["branch_id"].dropna().unique().tolist())
branch_labels = {branch_label(branch_id): branch_id for branch_id in branches}
months = sorted(m for m in reviews["review_month"].dropna().unique().tolist() if m != "NaT")

filter_col1, filter_col2 = st.columns([1, 2])
with filter_col1:
    selected_branch_labels = st.multiselect("Branches", list(branch_labels.keys()), default=list(branch_labels.keys()))
    selected_branches = [branch_labels[label] for label in selected_branch_labels]
with filter_col2:
    if months:
        start_month, end_month = st.select_slider("Period", options=months, value=(months[0], months[-1]))
    else:
        start_month = end_month = None

filtered = reviews[reviews["branch_id"].isin(selected_branches)] if selected_branches else reviews.iloc[0:0]
if start_month and end_month:
    filtered = filtered[(filtered["review_month"] >= start_month) & (filtered["review_month"] <= end_month)]

if filtered.empty:
    st.info("No reviews match the selected branches/period.")
    st.stop()

negative_rating = filtered[filtered["rating"] <= 2]
positive_rating = filtered[filtered["rating"] >= 4]
negative_ratio_pct = (len(negative_rating) / len(filtered) * 100) if len(filtered) else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Negative reviews (rating \u2264 2)", f"{len(negative_rating):,}")
col2.metric("Positive reviews (rating \u2265 4)", f"{len(positive_rating):,}")
col3.metric("Negative ratio", f"{negative_ratio_pct:.1f}%")
col4.metric("Reviews in scope", f"{len(filtered):,}")

st.subheader("Negative vs Positive — by Branch")
st.markdown(data_tag("real"), unsafe_allow_html=True)
bucket_counts = (
    filtered.dropna(subset=["rating_bucket"])
    .groupby(["branch_id", "rating_bucket"], observed=True)
    .size()
    .reset_index(name="count")
)
fig = px.bar(
    bucket_counts, x="branch_id", y="count", color="rating_bucket", barmode="group",
    color_discrete_sequence=CHART_SEQUENCE, title="Rating Buckets by Branch",
    labels={"branch_id": "branch", "count": "reviews", "rating_bucket": "rating group"},
)
fig.update_xaxes(ticktext=[branch_label(value) for value in bucket_counts["branch_id"].unique()], tickvals=bucket_counts["branch_id"].unique())
st.plotly_chart(fig, use_container_width=True)

st.subheader("Words Customers Use")
st.markdown(
    data_tag("real") + " Word size reflects how often a term appears in the selected review text. "
    "This is a discovery aid, not proof that a word caused a rating.",
    unsafe_allow_html=True,
)
cloud_col1, cloud_col2 = st.columns(2)
with cloud_col1:
    show_wordcloud(
        negative_rating["review_text"],
        "Negative review language",
        "OrRd",
        "No negative review text is available in this scope.",
    )
with cloud_col2:
    show_wordcloud(
        positive_rating["review_text"],
        "Positive review language",
        "YlGn",
        "No positive review text is available in this scope.",
    )

st.subheader("Complaint Share Trend Over Time")
st.markdown(data_tag("derived") + " Monthly share of reviews with negative customer mood.", unsafe_allow_html=True)
anomalies = load_anomalies()
if not anomalies.empty:
    trend = anomalies[anomalies["branch_id"].isin(selected_branches)]
    if start_month and end_month:
        trend = trend[(trend["month"] >= start_month) & (trend["month"] <= end_month)]
    fig2 = px.line(
        trend, x="month", y="negative_ratio", color="branch_id", markers=True,
        color_discrete_sequence=CHART_SEQUENCE, title="Monthly Complaint Share by Branch",
        labels={"month": "month", "negative_ratio": "complaint share", "branch_id": "branch"},
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Monthly negative-ratio aggregates not available yet.")

st.subheader("Experience Areas Behind Negative Feedback")
st.markdown(data_tag("derived"), unsafe_allow_html=True)
aspects = load_review_aspects()
if not aspects.empty:
    aspects_scoped = aspects[aspects["branch_id"].isin(selected_branches)].copy()
    if start_month and end_month:
        aspects_scoped["review_month"] = (
            pd.to_datetime(aspects_scoped["review_date"], errors="coerce").dt.to_period("M").astype(str)
        )
        aspects_scoped = aspects_scoped[
            (aspects_scoped["review_month"] >= start_month) & (aspects_scoped["review_month"] <= end_month)
        ]

    aspect_agg = (
        aspects_scoped.groupby("aspect")
        .agg(
            negative_mentions=("aspect_sentiment_label", lambda s: (s == "Negative").sum()),
            positive_mentions=("aspect_sentiment_label", lambda s: (s == "Positive").sum()),
            total_mentions=("aspect_sentiment_label", "count"),
        )
        .reset_index()
    )
    aspect_agg["negative_share_pct"] = (
        aspect_agg["negative_mentions"] / aspect_agg["total_mentions"].replace(0, pd.NA) * 100
    ).round(1)
    aspect_agg = aspect_agg.sort_values("negative_mentions", ascending=False)

    aspect_col1, aspect_col2 = st.columns(2)
    with aspect_col1:
        fig3 = px.bar(
            aspect_agg, x="aspect", y=["negative_mentions", "positive_mentions"], barmode="group",
            color_discrete_sequence=CHART_SEQUENCE, title="Negative vs Positive Mentions by Experience Area",
            labels={"aspect": "experience area", "value": "mentions", "variable": "mention type"},
        )
        st.plotly_chart(fig3, use_container_width=True)
    with aspect_col2:
        fig4 = px.bar(
            aspect_agg, x="aspect", y="negative_share_pct", color="aspect",
            color_discrete_sequence=CHART_SEQUENCE, title="Share of Mentions that are Negative (%)",
            labels={"aspect": "experience area", "negative_share_pct": "negative share %"},
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(
        business_dataframe(aspect_agg, ["aspect", "negative_mentions", "positive_mentions", "negative_share_pct"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Aspect table not available yet.")

st.subheader("Themes Over-Represented in Negative Reviews")
st.markdown(
    data_tag("derived") + " A concentration indicator above 1 means the theme appears "
    "more often in negative reviews than in the overall scoped set.",
    unsafe_allow_html=True,
)
topics_df = load_review_topics()
topic_model = load_topic_model()
if not topics_df.empty and topic_model:
    topic_terms = {topic["topic_id"]: ", ".join(topic["top_terms"][:5]) for topic in topic_model["topics"]}
    merged = topics_df.merge(
        filtered[["review_id", "sentiment_label"]], on="review_id", how="inner",
    )
    overall_share = merged["dominant_topic"].value_counts(normalize=True)
    negative_share = merged.loc[merged["sentiment_label"] == "Negative", "dominant_topic"].value_counts(normalize=True)
    lift_df = pd.DataFrame({"overall_share": overall_share, "negative_share": negative_share}).fillna(0.0)
    lift_df = lift_df.rename_axis("topic_id").reset_index()
    lift_df["negative_lift"] = (lift_df["negative_share"] / lift_df["overall_share"].replace(0, pd.NA)).round(2)
    lift_df["theme"] = lift_df["topic_id"].map(topic_terms).str.title()
    lift_df["overall_share"] = (lift_df["overall_share"] * 100).round(1)
    lift_df["negative_share"] = (lift_df["negative_share"] * 100).round(1)
    lift_df = lift_df.sort_values("negative_lift", ascending=False)
    st.dataframe(
        lift_df[["theme", "negative_lift", "negative_share", "overall_share"]].rename(
            columns={
                "theme": "theme",
                "negative_lift": "complaint concentration",
                "negative_share": "share of complaints %",
                "overall_share": "overall share %",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Topic assignments not available yet.")

st.subheader("Suggested CRM Fixes")
st.markdown(data_tag("derived") + " Evidence-ranked action tips based on repeat customer complaints.", unsafe_allow_html=True)
crm_df = load_crm_cases()
if not crm_df.empty:
    crm_scoped = crm_df[crm_df["branch_id"].isin(selected_branches)].copy()
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    crm_scoped["_priority_rank"] = crm_scoped["priority"].map(priority_rank).fillna(3)
    crm_scoped = crm_scoped.sort_values(["_priority_rank", "priority_score"], ascending=[True, False])
    columns = [
        column for column in [
            "branch_id", "issue", "priority", "mention_count", "recommended_action",
        ] if column in crm_scoped.columns
    ]
    st.dataframe(business_dataframe(crm_scoped[columns]), use_container_width=True, hide_index=True)
else:
    st.info("CRM action priorities are not available yet.")

st.subheader("Sample Negative Reviews")
st.markdown(data_tag("real"), unsafe_allow_html=True)
sample_columns = [
    column for column in ["branch_id", "review_date", "rating", "sentiment_label", "review_text"]
    if column in negative_rating.columns
]
st.dataframe(
    business_dataframe(negative_rating.sort_values("review_date", ascending=False)[sample_columns].head(200)),
    use_container_width=True,
    hide_index=True,
)
