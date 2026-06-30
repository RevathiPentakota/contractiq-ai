"""Tests for the contract processing LangGraph workflow.

Parallel execution note
-----------------------
SummaryAgent, RiskAgent, and ClauseAgent now run in parallel after
DocumentAgent.  All six pipeline agents are patched in integration tests
so no real LLM or database calls are made.
"""

from unittest.mock import MagicMock, patch

from app.state.contract_state import ContractState
from app.workflows.contract_workflow import build_contract_graph

_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f\n"
    b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n196\n%%EOF"
)


def _initial_state() -> ContractState:
    return ContractState(
        session_id="test-session-1",
        contract_id="test-contract-1",
        file_name="sample.pdf",
        storage_path="contracts/sample.pdf",
        processing_status="pending",
        errors=[],
    )


def _patch_all_agents():
    """Return patches for every agent in the pipeline.

    Covers DocumentAgent, the three parallel analysis agents
    (Summary/Risk/Clause), RecommendationAgent, and PersistenceAgent so
    no real LLM or database calls are made during graph invocation tests.
    """
    return (
        patch(
            "app.agents.document_agent.DocumentAgent.execute",
            return_value=ContractState(
                extracted_text="sample text",
                metadata={"file_size": len(_MINIMAL_PDF), "page_count": 1, "word_count": 2, "format": "pdf"},
                processing_status="document_processed",
            ),
        ),
        patch(
            "app.agents.summary_agent.SummaryAgent.execute",
            return_value=ContractState(summary="Test summary.", processing_status="summary_completed"),
        ),
        patch(
            "app.agents.risk_agent.RiskAgent.execute",
            return_value=ContractState(risks=[], processing_status="risk_completed"),
        ),
        patch(
            "app.agents.clause_agent.ClauseAgent.execute",
            return_value=ContractState(clauses=[], processing_status="clause_completed"),
        ),
        patch(
            "app.agents.recommendation_agent.RecommendationAgent.execute",
            return_value=ContractState(recommendations=[], processing_status="recommendation_completed"),
        ),
        patch(
            "app.agents.persistence_agent.PersistenceAgent.execute",
            return_value=ContractState(processing_status="completed"),
        ),
    )


def test_graph_compiles() -> None:
    """The StateGraph should compile without raising."""
    graph = build_contract_graph()
    assert graph is not None


def test_graph_invoke_returns_completed_status() -> None:
    """A full graph run should set processing_status to 'completed'."""
    graph = build_contract_graph()
    doc, summary, risk, clause, rec, persist = _patch_all_agents()
    with doc, summary, risk, clause, rec, persist:
        result: ContractState = graph.invoke(_initial_state())

    assert result["processing_status"] == "completed"


def test_graph_invoke_no_errors() -> None:
    """A run with no failures should accumulate no errors."""
    graph = build_contract_graph()
    doc, summary, risk, clause, rec, persist = _patch_all_agents()
    with doc, summary, risk, clause, rec, persist:
        result: ContractState = graph.invoke(_initial_state())

    assert result.get("errors", []) == []


def test_graph_invoke_preserves_session_id() -> None:
    """State fields not touched by any node should be preserved."""
    graph = build_contract_graph()
    doc, summary, risk, clause, rec, persist = _patch_all_agents()
    with doc, summary, risk, clause, rec, persist:
        result: ContractState = graph.invoke(_initial_state())

    assert result["session_id"] == "test-session-1"
