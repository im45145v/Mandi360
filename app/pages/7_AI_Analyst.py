"""AI Analyst — management question answering over prepared evidence."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.display import business_dataframe
from app.theme import apply_theme, banner, data_tag
from src.agents import orchestrator
from src.agents.llm_client import LLMNotConfiguredError, make_openai_client

apply_theme("AI Analyst")
banner("AI Analyst", "Ask management questions and receive evidence-grounded answers")

st.markdown(
    data_tag("derived") + data_tag("predicted")
    + " Answers combine collected reviews with CRM, data-mining, and predictive-analysis outputs. Verify recommendations before acting.",
    unsafe_allow_html=True,
)

question = st.text_input(
    "Ask a question", value="How is Banjara Hills performing and what actions should we take?"
)

if st.button("Investigate", type="primary"):
    try:
        llm_client = make_openai_client()
    except LLMNotConfiguredError:
        st.error(
            "The AI answer service is not configured in this environment. Showing the evidence summary "
            "that would be used for the management answer instead."
        )
        from src.agents.orchestrator import _detect_branch_ids

        branch_ids = _detect_branch_ids(question)
        branch_id = branch_ids[0] if len(branch_ids) == 1 else None
        st.subheader("Evidence-Ranked Management Actions")
        cases = orchestrator.tools.get_crm_cases(branch_id=branch_id) if branch_id else orchestrator.tools.get_crm_cases()
        if cases:
            st.dataframe(
                business_dataframe(pd.DataFrame(cases), ["branch_id", "issue", "priority", "mention_count", "recommended_action"]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No evidence-ranked management actions are available for this question.")
    else:
        with st.spinner("Reviewing the evidence and preparing a management answer..."):
            result = orchestrator.handle_query(llm_client, question)

        evidence = result["investigation"]["evidence"]
        if evidence.get("branch_performance"):
            st.subheader("Verified Period Performance")
            st.dataframe(
                business_dataframe(pd.DataFrame(evidence["branch_performance"]), ["branch_id", "review_count", "average_rating", "negative_ratio"]),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Investigation")
        st.write(result["investigation"]["narrative"])
        if "crm_recommendation" in result:
            st.subheader("Management Recommendations")
            st.write(result["crm_recommendation"]["recommendations"])
        st.caption("Evidence reviewed from collected reviews, CRM priorities, data-mining patterns, and branch outlooks.")
