from src.agents import crm_agent, insight_agent, orchestrator


class StubLLMClient:
    """Captures prompts instead of calling a real LLM, for isolated testing."""

    def __init__(self, response: str = "stub response"):
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.response


def test_insight_agent_builds_branch_evidence_and_calls_llm():
    stub = StubLLMClient("branch narrative")

    result = insight_agent.investigate(stub, branch_id="banjara_hills", question="How is banjara hills doing?")

    assert result["narrative"] == "branch narrative"
    assert result["evidence"]["branch_summary"]["branch_id"] == "banjara_hills"
    assert len(stub.calls) == 1


def test_insight_agent_builds_brand_wide_evidence_without_branch():
    stub = StubLLMClient()

    result = insight_agent.investigate(stub, branch_id=None)

    assert "branch_summary" not in result["evidence"]
    assert "brand_summary" in result["evidence"]


def test_crm_agent_recommends_based_on_investigation():
    stub = StubLLMClient("do X, do Y")
    investigation = insight_agent.investigate(StubLLMClient("narrative"), branch_id="gachibowli")

    result = crm_agent.recommend(stub, investigation)

    assert result["recommendations"] == "do X, do Y"
    assert result["branch_id"] == "gachibowli"


def test_orchestrator_routes_to_crm_agent_when_action_requested():
    stub = StubLLMClient("response")

    result = orchestrator.handle_query(stub, "What actions should we take for Banjara Hills?")

    assert result["branch_id"] == "banjara_hills"
    assert "crm_recommendation" in result
    assert len(stub.calls) == 2  # one for investigation, one for recommendation


def test_orchestrator_skips_crm_agent_for_plain_question():
    stub = StubLLMClient("response")

    result = orchestrator.handle_query(stub, "How is sentiment trending overall?")

    assert result["branch_id"] is None
    assert "crm_recommendation" not in result
    assert len(stub.calls) == 1


def test_orchestrator_includes_all_branches_in_comparison_question():
    stub = StubLLMClient("comparison response")

    result = orchestrator.handle_query(
        stub,
        "Compare Banjara Hills vs Jubilee Hills vs Gachibowli performance in July 2026",
    )

    comparison = result["investigation"]["evidence"]["branch_comparison"]
    assert [row["branch_id"] for row in comparison] == [
        "banjara_hills",
        "gachibowli",
        "jubilee_hills",
    ]
    assert result["branch_id"] is None


def test_orchestrator_infers_all_branches_and_period_from_generic_question():
    stub = StubLLMClient("comparison response")

    result = orchestrator.handle_query(stub, "How did the branches perform in July 2026?")

    evidence = result["investigation"]["evidence"]
    assert evidence["requested_period"] == "2026-07"
    assert [row["branch_id"] for row in evidence["branch_performance"]] == [
        "banjara_hills",
        "gachibowli",
        "jubilee_hills",
    ]
    assert [row["average_rating"] for row in evidence["branch_performance"]] == [
        "3.9189",
        "3.8",
        "3.5538",
    ]
    assert [row["branch_id"] for row in evidence["branch_comparison"]] == [
        "banjara_hills",
        "gachibowli",
        "jubilee_hills",
    ]
    assert [row["period_summary"]["month"] for row in evidence["branch_comparison"]] == [
        "2026-07",
        "2026-07",
        "2026-07",
    ]


def test_investigation_prompt_serializes_evidence_as_json():
    stub = StubLLMClient()

    insight_agent.investigate(
        stub,
        branch_ids=["banjara_hills", "gachibowli", "jubilee_hills"],
        period="2026-07",
        question="Compare all branches in July 2026",
    )

    prompt = stub.calls[0][1]
    assert "Evidence (strict JSON):" in prompt
    assert '"branch_performance"' in prompt
    assert "'branch_performance'" not in prompt


def test_period_specific_evidence_marks_unobserved_month():
    evidence = insight_agent.build_evidence(branch_id="gachibowli", period="2017-01")

    assert evidence["period_summary"] == {
        "branch_id": "gachibowli",
        "month": "2017-01",
        "is_observed": False,
    }
