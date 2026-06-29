"""Tests for SummaryAgent and LLMService."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.agents.summary_agent import SummaryAgent
from app.services.llm_service import LLMService
from app.state.contract_state import ContractState

# ── Shared fixtures ────────────────────────────────────────────────────────────

_SAMPLE_TEXT = (
    "This Service Agreement is entered into as of January 1, 2025, between "
    "Acme Corp ('Client') and Globex Solutions ('Provider'). The Provider "
    "agrees to deliver software development services for a monthly fee of "
    "$10,000. The agreement is effective for 12 months and may be terminated "
    "by either party with 30 days written notice."
)

_SAMPLE_SUMMARY = (
    "This is a Service Agreement between Acme Corp and Globex Solutions, "
    "effective January 1, 2025, for a 12-month term. The Provider will "
    "deliver software development services at $10,000 per month. Either "
    "party may terminate with 30 days notice."
)

_MOCK_LLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": _SAMPLE_SUMMARY,
            }
        }
    ]
}


def _make_mock_llm_service(summary: str = _SAMPLE_SUMMARY) -> MagicMock:
    """Return a mock LLMService that returns a fixed summary."""
    mock = MagicMock(spec=LLMService)
    mock.generate_summary.return_value = summary
    return mock


# ── LLMService tests ───────────────────────────────────────────────────────────


class TestLLMService:
    """Unit tests for LLMService."""

    def test_generate_summary_empty_text_raises(self) -> None:
        """Raise ValueError when contract_text is empty."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_summary("")

    def test_generate_summary_whitespace_text_raises(self) -> None:
        """Raise ValueError when contract_text is only whitespace."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_summary("   ")

    def test_generate_summary_success(self) -> None:
        """Return plain-text summary on successful LLM response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = _MOCK_LLM_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            result = service.generate_summary(_SAMPLE_TEXT)

        assert result == _SAMPLE_SUMMARY
        mock_client.post.assert_called_once()

        # Verify the correct endpoint and payload keys
        call_kwargs = mock_client.post.call_args
        assert "/chat/completions" in call_kwargs.kwargs["url"]
        payload = call_kwargs.kwargs["json"]
        assert "messages" in payload
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert _SAMPLE_TEXT in payload["messages"][1]["content"]

    def test_generate_summary_http_error_raises(self) -> None:
        """Re-raise HTTPStatusError on non-2xx response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            with pytest.raises(httpx.HTTPStatusError):
                service.generate_summary(_SAMPLE_TEXT)

    def test_generate_summary_timeout_raises(self) -> None:
        """Re-raise TimeoutException when LLM proxy times out."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.TimeoutException("timed out")

            service = LLMService()
            with pytest.raises(httpx.TimeoutException):
                service.generate_summary(_SAMPLE_TEXT)

    def test_generate_summary_network_error_raises(self) -> None:
        """Re-raise RequestError on network-level failure."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.RequestError("connection refused")

            service = LLMService()
            with pytest.raises(httpx.RequestError):
                service.generate_summary(_SAMPLE_TEXT)

    def test_generate_summary_bad_response_structure_raises(self) -> None:
        """Raise ValueError when LLM returns an unexpected response shape."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"unexpected_key": "value"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            with pytest.raises(ValueError, match="Unexpected LLM response structure"):
                service.generate_summary(_SAMPLE_TEXT)


# ── SummaryAgent tests ─────────────────────────────────────────────────────────


class TestSummaryAgent:
    """Unit tests for SummaryAgent."""

    def _state_with_text(self, text: str = _SAMPLE_TEXT) -> ContractState:
        return ContractState(
            session_id="test-session",
            contract_id="contract-1",
            file_name="contract.pdf",
            storage_path="contracts/contract.pdf",
            extracted_text=text,
            processing_status="document_processed",
            errors=[],
        )

    def test_agent_instantiation_default(self) -> None:
        """Instantiate SummaryAgent with default LLMService."""
        agent = SummaryAgent()
        assert isinstance(agent.llm_service, LLMService)

    def test_agent_instantiation_injected(self) -> None:
        """Instantiate SummaryAgent with an injected mock LLMService."""
        mock_service = _make_mock_llm_service()
        agent = SummaryAgent(llm_service=mock_service)
        assert agent.llm_service is mock_service

    def test_execute_success(self) -> None:
        """Return summary and 'summary_completed' status on success."""
        mock_service = _make_mock_llm_service()
        agent = SummaryAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        assert result["summary"] == _SAMPLE_SUMMARY
        assert result["processing_status"] == "summary_completed"
        assert "errors" not in result or result.get("errors") == []
        mock_service.generate_summary.assert_called_once_with(_SAMPLE_TEXT)

    def test_execute_empty_text_returns_failed_status(self) -> None:
        """Return 'summary_failed' when extracted_text is empty."""
        mock_service = _make_mock_llm_service()
        agent = SummaryAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text(text=""))

        assert result["processing_status"] == "summary_failed"
        assert result["summary"] == ""
        assert len(result.get("errors", [])) > 0
        mock_service.generate_summary.assert_not_called()

    def test_execute_missing_text_returns_failed_status(self) -> None:
        """Return 'summary_failed' when extracted_text key is absent."""
        mock_service = _make_mock_llm_service()
        agent = SummaryAgent(llm_service=mock_service)
        state = ContractState(
            session_id="s1",
            contract_id="c1",
            processing_status="document_processed",
            errors=[],
        )

        result = agent.execute(state)

        assert result["processing_status"] == "summary_failed"
        mock_service.generate_summary.assert_not_called()

    def test_execute_llm_failure_returns_failed_status(self) -> None:
        """Return 'summary_failed' and append error when LLM raises."""
        mock_service = MagicMock(spec=LLMService)
        mock_service.generate_summary.side_effect = httpx.RequestError(
            "proxy unreachable"
        )
        agent = SummaryAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        assert result["processing_status"] == "summary_failed"
        assert result["summary"] == ""
        errors = result.get("errors", [])
        assert len(errors) == 1
        assert "proxy unreachable" in errors[0]

    def test_execute_returns_only_partial_state(self) -> None:
        """Agent returns only the keys it modifies, not the full state."""
        mock_service = _make_mock_llm_service()
        agent = SummaryAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        # Only summary and processing_status should be in the returned dict
        assert set(result.keys()) <= {"summary", "processing_status", "errors"}
