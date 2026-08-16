"""Orchestrator Agent: routes a natural-language question to Insight/CRM agents."""
from __future__ import annotations

import re
from typing import Any

from src.agents import crm_agent, insight_agent, tools
from src.agents.llm_client import LLMClient
from src.config.settings import DEFAULT_SOURCES

_CRM_KEYWORDS = ("recommend", "action", "should we", "what to do", "improve", "fix")
_COMPARISON_KEYWORDS = (
    "compare",
    "comparison",
    "across branches",
    "all branches",
    "branches",
    "each branch",
    "versus",
    " vs ",
)


def _detect_branch_id(question: str) -> str | None:
    branch_ids = _detect_branch_ids(question)
    return branch_ids[0] if branch_ids else None


def _detect_branch_ids(question: str) -> list[str]:
    lowered = question.lower()
    detected = [
        source.branch_id
        for source in DEFAULT_SOURCES
        if source.branch_id.replace("_", " ") in lowered or source.branch_name.lower() in lowered
    ]
    if len(detected) > 1 or any(keyword in lowered for keyword in _COMPARISON_KEYWORDS):
        return [source.branch_id for source in DEFAULT_SOURCES]
    return detected


def _detect_period(question: str) -> str | None:
    """Return an explicitly requested month as YYYY-MM when one is present."""
    numeric_match = re.search(r"\b(20\d{2})[-/]?(0?[1-9]|1[0-2])\b", question)
    if numeric_match:
        return f"{numeric_match.group(1)}-{int(numeric_match.group(2)):02d}"

    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    lowered = question.lower()
    for month_name, month_number in month_names.items():
        match = re.search(rf"\b{month_name}\s+(20\d{{2}})\b", lowered)
        if match:
            return f"{match.group(1)}-{month_number:02d}"
    return None


def _wants_recommendations(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in _CRM_KEYWORDS)


def handle_query(llm_client: LLMClient, question: str) -> dict[str, Any]:
    """Route a natural-language question to the investigation and/or CRM agent.

    Branch detection and intent routing are rule-based (no LLM call needed for
    routing), keeping LLM usage limited to the actual reasoning steps.
    """
    branch_ids = [branch_id for branch_id in _detect_branch_ids(question) if tools.get_branch_summary(branch_id)]
    branch_id = branch_ids[0] if len(branch_ids) == 1 else None
    period = _detect_period(question)

    investigation = insight_agent.investigate(
        llm_client,
        branch_id=branch_id,
        branch_ids=branch_ids if len(branch_ids) > 1 else None,
        period=period,
        question=question,
    )
    result: dict[str, Any] = {"question": question, "branch_id": branch_id, "investigation": investigation}

    if _wants_recommendations(question):
        result["crm_recommendation"] = crm_agent.recommend(llm_client, investigation)

    return result
