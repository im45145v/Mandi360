"""Manager-friendly display helpers for dashboard tables and labels."""
from __future__ import annotations


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
    "lower_bound": "lower expected range",
    "mention_count": "mentions",
    "month": "month",
    "negative_lift": "negative-review concentration",
    "negative_mentions": "negative mentions",
    "negative_ratio": "negative feedback share",
    "negative_share": "share within negative reviews",
    "negative_share_pct": "negative share %",
    "overall_share": "overall share",
    "positive_mentions": "positive mentions",
    "predicted_average_rating": "expected rating",
    "priority": "priority",
    "priority_score": "priority indicator",
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
    display_df = display_df.rename(columns=BUSINESS_COLUMN_LABELS)
    return display_df.loc[:, ~display_df.columns.duplicated()]
