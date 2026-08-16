"""AI Analyst — agentic orchestrator over the deterministic tool layer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.theme import apply_theme, banner, data_tag
from src.agents import orchestrator
from src.agents.llm_client import LLMNotConfiguredError, make_openai_client

apply_theme("AI Analyst")
banner("AI Analyst", "Ask management questions and receive evidence-grounded answers")

st.markdown(
    data_tag("derived") + data_tag("predicted")
    + " Answers combine collected reviews with analytical signals and forecasts. Verify recommendations before acting.",
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
            "OPENAI_API_KEY is not configured in this environment, so the LLM reasoning step "
            "cannot run. Showing the compact evidence bundle the agent would have used instead."
        )
        from src.agents import insight_agent
        from src.agents.orchestrator import _detect_branch_ids, _detect_period

        branch_ids = _detect_branch_ids(question)
        branch_id = branch_ids[0] if len(branch_ids) == 1 else None
        st.json(
            insight_agent.build_evidence(
                branch_id,
                branch_ids=branch_ids if len(branch_ids) > 1 else None,
                period=_detect_period(question),
            )
        )
        st.subheader("Evidence-Ranked Management Actions")
        cases = orchestrator.tools.get_crm_cases(branch_id=branch_id) if branch_id else orchestrator.tools.get_crm_cases()
        if cases:
            st.dataframe(cases, use_container_width=True)
        else:
            st.info("No evidence-ranked management actions are available for this question.")
    else:
        with st.spinner("Orchestrator routing question, gathering evidence, and reasoning..."):
            result = orchestrator.handle_query(llm_client, question)

        evidence = result["investigation"]["evidence"]
        if evidence.get("branch_performance"):
            st.subheader("Verified Period Performance")
            st.dataframe(evidence["branch_performance"], use_container_width=True, hide_index=True)

        st.subheader("Investigation")
        st.write(result["investigation"]["narrative"])
        if "crm_recommendation" in result:
            st.subheader("Management Recommendations")
            st.write(result["crm_recommendation"]["recommendations"])
        with st.expander("Evidence bundle used"):
            st.json(evidence)
