"""Tests for RiskAgent and LLMService.generate_risks()."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from typing import Any

import httpx
import pytest

from app.agents.risk_agent import RiskAgent
from app.services.llm_service import LLMService
from app.state.contract_state import ContractState

# ── Shared fixtures ────────────────────────────────────────────────────────────

_SAMPLE_CONTRACT = (
    "This Service Agreement is entered into as of January 1, 2025, between "
    "Acme Corp ('Client') and Globex Solutions ('Provider'). "
    "The Provider agrees to deliver software development services. "
    "Globex has unlimited liability for any damages. "
    "Either party may terminate without notice. "
    "All intellectual property created by Provider remains Globex property."
)

_SAMPLE_RISKS: list[dict[str, Any]] = [
    {
        "category": "Financial",
        "severity": "High",
        "title": "Unlimited Liability",
        "description": "Provider has unlimited liability for damages with no cap.",
        "clause_reference": "Section 8.2",
        "recommendation": "Limit liability to contract value or annual fees."
    },
    {
        "category": "Termination",
        "severity": "High",
        "title": "Termination Without Notice",
        "description": "Either party may terminate the agreement without providing notice.",
        "clause_reference": "Section 3.1",
        "recommendation": "Require 30 days written notice for termination."
    }
]

_MOCK_LLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": str(_SAMPLE_RISKS),  # LLM returns JSON array as string
            }
        }
    ]
}


def _make_mock_llm_service(risks: list[dict[str, Any]] = _SAMPLE_RISKS) -> MagicMock:
    """Return a mock LLMService that returns fixed risks."""
    mock = MagicMock(spec=LLMService)
    mock.generate_risks.return_value = risks
    return mock


# ── LLMService.generate_risks() tests ──────────────────────────────────────────


class TestLLMServiceGenerateRisks:
    """Unit tests for LLMService.generate_risks()."""

    def test_generate_risks_empty_text_raises(self) -> None:
        """Raise ValueError when contract_text is empty."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_risks("")

    def test_generate_risks_whitespace_text_raises(self) -> None:
        """Raise ValueError when contract_text is only whitespace."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_risks("   ")

    def test_generate_risks_success(self) -> None:
        """Return parsed risk list on successful LLM response."""
        # Convert risks to JSON string as LLM would
        import json
        risks_json = json.dumps(_SAMPLE_RISKS)
        
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": risks_json,
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            result = service.generate_risks(_SAMPLE_CONTRACT)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Unlimited Liability"
        assert result[1]["severity"] == "High"

    def test_generate_risks_empty_array(self) -> None:
        """Return empty list when LLM identifies no risks."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "[]",
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            result = service.generate_risks(_SAMPLE_CONTRACT)

        assert result == []

    def test_generate_risks_invalid_json_raises(self) -> None:
        """Raise ValueError when LLM returns invalid JSON."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "{ this is not valid json }",
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            with pytest.raises(ValueError, match="did not return valid JSON"):
                service.generate_risks(_SAMPLE_CONTRACT)

    def test_generate_risks_non_list_json_raises(self) -> None:
        """Raise ValueError when LLM returns JSON but not an array."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": '{"error": "some object"}',  # Dict, not array
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            service = LLMService()
            with pytest.raises(ValueError, match="Expected JSON array"):
                service.generate_risks(_SAMPLE_CONTRACT)

    def test_generate_risks_http_error_raises(self) -> None:
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
                service.generate_risks(_SAMPLE_CONTRACT)

    def test_generate_risks_timeout_raises(self) -> None:
        """Re-raise TimeoutException when LLM proxy times out."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.TimeoutException("timed out")

            service = LLMService()
            with pytest.raises(httpx.TimeoutException):
                service.generate_risks(_SAMPLE_CONTRACT)

    def test_generate_risks_network_error_raises(self) -> None:
        """Re-raise RequestError on network-level failure."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.RequestError("connection refused")

            service = LLMService()
            with pytest.raises(httpx.RequestError):
                service.generate_risks(_SAMPLE_CONTRACT)

    def test_generate_risks_bad_response_structure_raises(self) -> None:
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
                service.generate_risks(_SAMPLE_CONTRACT)


# ── RiskAgent tests ────────────────────────────────────────────────────────────


class TestRiskAgent:
    """Unit tests for RiskAgent."""

    def _state_with_text(self, text: str = _SAMPLE_CONTRACT) -> ContractState:
        return ContractState(
            session_id="test-session",
            contract_id="contract-1",
            file_name="contract.pdf",
            storage_path="contracts/contract.pdf",
            extracted_text=text,
            processing_status="summary_completed",
            errors=[],
        )

    def test_agent_instantiation_default(self) -> None:
        """Instantiate RiskAgent with default LLMService."""
        agent = RiskAgent()
        assert isinstance(agent.llm_service, LLMService)

    def test_agent_instantiation_injected(self) -> None:
        """Instantiate RiskAgent with an injected mock LLMService."""
        mock_service = _make_mock_llm_service()
        agent = RiskAgent(llm_service=mock_service)
        assert agent.llm_service is mock_service

    def test_execute_success(self) -> None:
        """Return risks and 'risk_completed' status on success."""
        mock_service = _make_mock_llm_service()
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        assert result["risks"] == _SAMPLE_RISKS
        assert result["processing_status"] == "risk_completed"
        assert "errors" not in result or result.get("errors") == []
        mock_service.generate_risks.assert_called_once_with(_SAMPLE_CONTRACT)

    def test_execute_empty_text_returns_failed_status(self) -> None:
        """Return 'risk_failed' when extracted_text is empty."""
        mock_service = _make_mock_llm_service()
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text(text=""))

        assert result["processing_status"] == "risk_failed"
        assert result["risks"] == []
        assert len(result.get("errors", [])) > 0
        mock_service.generate_risks.assert_not_called()

    def test_execute_missing_text_returns_failed_status(self) -> None:
        """Return 'risk_failed' when extracted_text key is absent."""
        mock_service = _make_mock_llm_service()
        agent = RiskAgent(llm_service=mock_service)
        state = ContractState(
            session_id="s1",
            contract_id="c1",
            processing_status="summary_completed",
            errors=[],
        )

        result = agent.execute(state)

        assert result["processing_status"] == "risk_failed"
        mock_service.generate_risks.assert_not_called()

    def test_execute_llm_failure_returns_failed_status(self) -> None:
        """Return 'risk_failed' and append error when LLM raises."""
        mock_service = MagicMock(spec=LLMService)
        mock_service.generate_risks.side_effect = httpx.RequestError(
            "proxy unreachable"
        )
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        assert result["processing_status"] == "risk_failed"
        assert result["risks"] == []
        errors = result.get("errors", [])
        assert len(errors) == 1
        assert "proxy unreachable" in errors[0]

    def test_execute_empty_risks_list(self) -> None:
        """Successfully return empty risks list when none found."""
        mock_service = _make_mock_llm_service(risks=[])
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        assert result["risks"] == []
        assert result["processing_status"] == "risk_completed"

    def test_execute_returns_only_partial_state(self) -> None:
        """Agent returns only the keys it modifies, not the full state."""
        mock_service = _make_mock_llm_service()
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        # Only risks and processing_status should be in the returned dict
        assert set(result.keys()) <= {"risks", "processing_status", "errors"}

    def test_execute_risk_structure(self) -> None:
        """Verify that returned risks have the expected structure."""
        mock_service = _make_mock_llm_service(risks=_SAMPLE_RISKS)
        agent = RiskAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_text())

        risks = result["risks"]
        assert len(risks) > 0
        
        # Check first risk has all required fields
        first_risk = risks[0]
        assert "category" in first_risk
        assert "severity" in first_risk
        assert "title" in first_risk
        assert "description" in first_risk
        assert "clause_reference" in first_risk
        assert "recommendation" in first_risk
