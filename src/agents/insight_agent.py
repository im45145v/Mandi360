"""Insight/Investigation Agent: turns compact evidence into an investigative narrative."""
from __future__ import annotations

import json
from typing import Any

from src.agents import tools
from src.agents.llm_client import LLMClient

SYSTEM_PROMPT = (
    "You are a CRM data-investigation analyst for a Hyderabad Mandi restaurant brand. "
    "You are given a compact JSON evidence bundle built from real customer reviews and "
    "statistical/ML models (sentiment, aspects, topics, clusters, anomalies, forecasts). "
    "Clearly distinguish REAL data (ratings, dates, review counts) from DERIVED data "
    "(sentiment/aspect/topic labels) and PREDICTED data (forecasts, risk levels). "
    "Never invent facts not present in the evidence. Never claim causation from correlation. "
    "If evidence is sparse, say so explicitly. For comparison questions, use the "
    "branch_performance rows as the authoritative source and discuss every row exactly "
    "once. Never claim a branch is missing when its row is present. If observed is "
    "false, say that the requested period is unavailable; do not substitute lifetime "
    "data. Report observed values as REAL, model outputs as DERIVED or PREDICTED, and "
    "distinguish zero observations from unavailable data."
)


def _period_summary(branch_id: str, period: str | None) -> dict[str, Any] | None:
    if not period:
        return None
    rows = tools.get_sentiment_trend(branch_id)
    for row in rows:
        if row.get("month") == period:
            return row
    return {"branch_id": branch_id, "month": period, "is_observed": False}


def build_evidence(
    branch_id: str | None = None,
    branch_ids: list[str] | None = None,
    period: str | None = None,
) -> dict[str, Any]:
    """Assemble a compact evidence bundle for a brand-wide or single-branch investigation."""
    evidence: dict[str, Any] = {
        "brand_summary": tools.get_brand_summary(),
        "top_topics": tools.get_top_topics(limit=5),
        "association_rules": tools.get_association_rules(limit=10),
    }
    if period:
        evidence["requested_period"] = period
    if branch_ids:
        evidence["branch_performance"] = tools.get_branch_performance(branch_ids, period)
        evidence["branch_comparison"] = [
            {
                "branch_id": selected_branch,
                "branch_summary": tools.get_branch_summary(selected_branch),
                "period_summary": _period_summary(selected_branch, period),
                "sentiment_trend": tools.get_sentiment_trend(selected_branch),
                "forecast": tools.get_forecast(selected_branch),
                "anomalies": tools.get_anomalies(selected_branch),
            }
            for selected_branch in branch_ids
        ]
    elif branch_id:
        evidence["branch_summary"] = tools.get_branch_summary(branch_id)
        evidence["period_summary"] = _period_summary(branch_id, period)
        evidence["sentiment_trend"] = tools.get_sentiment_trend(branch_id)
        evidence["aspect_sentiment"] = tools.get_aspect_sentiment(branch_id)
        evidence["anomalies"] = tools.get_anomalies(branch_id)
        evidence["forecast"] = tools.get_forecast(branch_id)
    else:
        evidence["anomalies"] = tools.get_anomalies()
    return evidence


def investigate(
    llm_client: LLMClient,
    branch_id: str | None = None,
    question: str | None = None,
    branch_ids: list[str] | None = None,
    period: str | None = None,
) -> dict[str, Any]:
    """Build evidence and ask the LLM to produce an evidence-grounded investigative narrative."""
    evidence = build_evidence(branch_id, branch_ids=branch_ids, period=period)
    user_prompt = (
        f"Question: {question or 'Summarize the key customer-experience findings.'}\n\n"
        "Reasoning requirements:\n"
        "- Answer the requested scope and period, if present.\n"
        "- For a branch comparison, start with a compact table or bullets covering "
        "every branch_performance row.\n"
        "- Use only values in the evidence; do not infer missing values.\n\n"
        f"Evidence (strict JSON): {json.dumps(evidence, ensure_ascii=True, sort_keys=True)}"
    )
    narrative = llm_client(SYSTEM_PROMPT, user_prompt)
    return {"branch_id": branch_id, "evidence": evidence, "narrative": narrative}
