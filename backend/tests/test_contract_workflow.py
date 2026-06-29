"""Tests for the contract processing LangGraph workflow."""

from unittest.mock import MagicMock, patch

from app.state.contract_state import ContractState
from app.workflows.contract_workflow import build_contract_graph

# ── Minimal valid single-page PDF bytes ────────────────────────────────────────
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


def _mock_storage():
    """Return a mock that simulates Supabase Storage returning PDF bytes."""
    mock_client = MagicMock()
    mock_client.storage.from_.return_value.download.return_value = _MINIMAL_PDF
    return mock_client


def test_graph_compiles() -> None:
    """The StateGraph should compile without raising."""
    graph = build_contract_graph()
    assert graph is not None


def test_graph_invoke_returns_completed_status() -> None:
    """A full graph run should set processing_status to 'completed'."""
    graph = build_contract_graph()
    with patch(
        "app.agents.document_agent.DocumentAgent.execute",
        return_value=ContractState(
            extracted_text="sample text",
            metadata={"file_size": len(_MINIMAL_PDF), "page_count": 1, "word_count": 2, "format": "pdf"},
            processing_status="document_processed",
        ),
    ):
        result: ContractState = graph.invoke(_initial_state())

    assert result["processing_status"] == "completed"


def test_graph_invoke_no_errors() -> None:
    """A run with no failures should accumulate no errors."""
    graph = build_contract_graph()
    with patch(
        "app.agents.document_agent.DocumentAgent.execute",
        return_value=ContractState(
            extracted_text="sample text",
            metadata={"file_size": len(_MINIMAL_PDF), "page_count": 1, "word_count": 2, "format": "pdf"},
            processing_status="document_processed",
        ),
    ):
        result: ContractState = graph.invoke(_initial_state())

    assert result.get("errors", []) == []


def test_graph_invoke_preserves_session_id() -> None:
    """State fields not touched by any node should be preserved."""
    graph = build_contract_graph()
    with patch(
        "app.agents.document_agent.DocumentAgent.execute",
        return_value=ContractState(
            extracted_text="sample text",
            metadata={},
            processing_status="document_processed",
        ),
    ):
        result: ContractState = graph.invoke(_initial_state())

    assert result["session_id"] == "test-session-1"
