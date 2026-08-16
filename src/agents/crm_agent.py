"""CRM Recommendation Agent: turns an investigation into actionable CRM recommendations."""
from __future__ import annotations

from typing import Any

from src.agents.llm_client import LLMClient

SYSTEM_PROMPT = (
    "You are a CRM recommendation advisor for a Hyderabad Mandi restaurant brand. "
    "You receive an investigation narrative and its evidence bundle. Produce concrete, "
    "prioritized CRM actions (e.g., staff coaching, process fixes, follow-up outreach). "
    "Every recommendation must cite which evidence it is based on. Label each "
    "recommendation's confidence based on whether it stems from REAL, DERIVED, or "
    "PREDICTED data. Never present a prediction as a certainty. Do not fabricate evidence."
)


def recommend(llm_client: LLMClient, investigation: dict[str, Any]) -> dict[str, Any]:
    """Ask the LLM for CRM recommendations grounded in a prior investigation's evidence."""
    user_prompt = (
        f"Branch: {investigation.get('branch_id') or 'brand-wide'}\n"
        f"Investigation narrative: {investigation.get('narrative')}\n\n"
        f"Evidence (JSON): {investigation.get('evidence')}"
    )
    recommendations = llm_client(SYSTEM_PROMPT, user_prompt)
    return {
        "branch_id": investigation.get("branch_id"),
        "based_on_evidence": investigation.get("evidence"),
        "recommendations": recommendations,
    }
