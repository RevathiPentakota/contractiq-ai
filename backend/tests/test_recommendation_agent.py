"""Tests for RecommendationAgent and LLMService.generate_recommendations()."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from typing import Any

import httpx
import pytest

from app.agents.recommendation_agent import RecommendationAgent
from app.services.llm_service import LLMService
from app.state.contract_state import ContractState

# ── Shared fixtures ────────────────────────────────────────────────────────────

_SAMPLE_SUMMARY = (
    "This Service Agreement outlines a software development engagement between "
    "Acme Corp and Globex Solutions. The agreement includes unlimited liability "
    "and allows termination without notice."
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

_SAMPLE_CLAUSES: list[dict[str, Any]] = [
    {
        "title": "Scope of Services",
        "category": "Services",
        "clause_reference": "Section 1",
        "description": "Provider agrees to deliver software development services to Client.",
        "importance": "High"
    },
    {
        "title": "Intellectual Property Rights",
        "category": "IP",
        "clause_reference": "Section 6",
        "description": "All intellectual property created by Provider remains Globex property.",
        "importance": "High"
    }
]

_SAMPLE_RECOMMENDATIONS: list[dict[str, Any]] = [
    {
        "priority": "High",
        "category": "Financial",
        "recommendation": "Limit liability to contract value or annual fees.",
        "rationale": "Unlimited liability creates excessive financial exposure for both parties."
    },
    {
        "priority": "High",
        "category": "Termination",
        "recommendation": "Require 30 days written notice before termination.",
        "rationale": "Termination without notice could disrupt ongoing services and cause operational harm."
    },
    {
        "priority": "Medium",
        "category": "IP",
        "recommendation": "Clarify IP ownership for derivative works.",
        "rationale": "Current clause does not clearly define ownership of modifications to existing IP."
    }
]


def _make_mock_llm_service(
    recommendations: list[dict[str, Any]] = _SAMPLE_RECOMMENDATIONS,
) -> MagicMock:
    """Return a mock LLMService that returns fixed recommendations."""
    mock = MagicMock(spec=LLMService)
    mock.generate_recommendations.return_value = recommendations
    return mock


# ── LLMService.generate_recommendations() tests ────────────────────────────────


class TestLLMServiceGenerateRecommendations:
    """Unit tests for LLMService.generate_recommendations()."""

    def test_generate_recommendations_empty_summary_raises(self) -> None:
        """Raise ValueError when summary is empty."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_recommendations(
                summary="",
                risks=_SAMPLE_RISKS,
                clauses=_SAMPLE_CLAUSES,
            )

    def test_generate_recommendations_whitespace_summary_raises(self) -> None:
        """Raise ValueError when summary is only whitespace."""
        service = LLMService()
        with pytest.raises(ValueError, match="must not be empty"):
            service.generate_recommendations(
                summary="   ",
                risks=_SAMPLE_RISKS,
                clauses=_SAMPLE_CLAUSES,
            )

    def test_generate_recommendations_success(self) -> None:
        """Return parsed recommendation list on successful LLM response."""
        import json
        recommendations_json = json.dumps(_SAMPLE_RECOMMENDATIONS)
        
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": recommendations_json,
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
            result = service.generate_recommendations(
                summary=_SAMPLE_SUMMARY,
                risks=_SAMPLE_RISKS,
                clauses=_SAMPLE_CLAUSES,
            )

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["priority"] == "High"
        assert result[1]["category"] == "Termination"

    def test_generate_recommendations_empty_array(self) -> None:
        """Return empty list when LLM identifies no recommendations."""
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
            result = service.generate_recommendations(
                summary=_SAMPLE_SUMMARY,
                risks=_SAMPLE_RISKS,
                clauses=_SAMPLE_CLAUSES,
            )

        assert result == []

    def test_generate_recommendations_with_empty_risks_and_clauses(self) -> None:
        """Accept empty risks and clauses lists."""
        import json
        recommendations_json = json.dumps(_SAMPLE_RECOMMENDATIONS[:1])
        
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": recommendations_json,
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
            result = service.generate_recommendations(
                summary=_SAMPLE_SUMMARY,
                risks=[],
                clauses=[],
            )

        assert len(result) == 1
        assert result[0]["priority"] == "High"

    def test_generate_recommendations_invalid_json_raises(self) -> None:
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
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )

    def test_generate_recommendations_non_list_json_raises(self) -> None:
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
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )

    def test_generate_recommendations_http_error_raises(self) -> None:
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
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )

    def test_generate_recommendations_timeout_raises(self) -> None:
        """Re-raise TimeoutException when LLM proxy times out."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.TimeoutException("timed out")

            service = LLMService()
            with pytest.raises(httpx.TimeoutException):
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )

    def test_generate_recommendations_network_error_raises(self) -> None:
        """Re-raise RequestError on network-level failure."""
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.RequestError("connection refused")

            service = LLMService()
            with pytest.raises(httpx.RequestError):
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )

    def test_generate_recommendations_bad_response_structure_raises(self) -> None:
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
                service.generate_recommendations(
                    summary=_SAMPLE_SUMMARY,
                    risks=_SAMPLE_RISKS,
                    clauses=_SAMPLE_CLAUSES,
                )


# ── RecommendationAgent tests ──────────────────────────────────────────────────


class TestRecommendationAgent:
    """Unit tests for RecommendationAgent."""

    def _state_with_analysis(
        self,
        summary: str = _SAMPLE_SUMMARY,
        risks: list[dict[str, Any]] = _SAMPLE_RISKS,
        clauses: list[dict[str, Any]] = _SAMPLE_CLAUSES,
    ) -> ContractState:
        return ContractState(
            session_id="test-session",
            contract_id="contract-1",
            file_name="contract.pdf",
            storage_path="contracts/contract.pdf",
            summary=summary,
            risks=risks,
            clauses=clauses,
            processing_status="clause_completed",
            errors=[],
        )

    def test_agent_instantiation_default(self) -> None:
        """Instantiate RecommendationAgent with default LLMService."""
        agent = RecommendationAgent()
        assert isinstance(agent.llm_service, LLMService)

    def test_agent_instantiation_injected(self) -> None:
        """Instantiate RecommendationAgent with an injected mock LLMService."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)
        assert agent.llm_service is mock_service

    def test_execute_success(self) -> None:
        """Return recommendations and 'recommendation_completed' status on success."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        assert result["recommendations"] == _SAMPLE_RECOMMENDATIONS
        assert result["processing_status"] == "recommendation_completed"
        assert "errors" not in result or result.get("errors") == []
        mock_service.generate_recommendations.assert_called_once_with(
            summary=_SAMPLE_SUMMARY,
            risks=_SAMPLE_RISKS,
            clauses=_SAMPLE_CLAUSES,
        )

    def test_execute_empty_summary_returns_failed_status(self) -> None:
        """Return 'recommendation_failed' when summary is empty."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis(summary=""))

        assert result["processing_status"] == "recommendation_failed"
        assert result["recommendations"] == []
        assert len(result.get("errors", [])) > 0
        mock_service.generate_recommendations.assert_not_called()

    def test_execute_missing_summary_returns_failed_status(self) -> None:
        """Return 'recommendation_failed' when summary key is absent."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)
        state = ContractState(
            session_id="s1",
            contract_id="c1",
            processing_status="clause_completed",
            errors=[],
        )

        result = agent.execute(state)

        assert result["processing_status"] == "recommendation_failed"
        mock_service.generate_recommendations.assert_not_called()

    def test_execute_with_empty_risks_and_clauses(self) -> None:
        """Accept empty risks and clauses lists."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(
            self._state_with_analysis(risks=[], clauses=[])
        )

        assert result["recommendations"] == _SAMPLE_RECOMMENDATIONS
        assert result["processing_status"] == "recommendation_completed"
        mock_service.generate_recommendations.assert_called_once_with(
            summary=_SAMPLE_SUMMARY,
            risks=[],
            clauses=[],
        )

    def test_execute_llm_failure_returns_failed_status(self) -> None:
        """Return 'recommendation_failed' and append error when LLM raises."""
        mock_service = MagicMock(spec=LLMService)
        mock_service.generate_recommendations.side_effect = httpx.RequestError(
            "proxy unreachable"
        )
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        assert result["processing_status"] == "recommendation_failed"
        assert result["recommendations"] == []
        errors = result.get("errors", [])
        assert len(errors) == 1
        assert "proxy unreachable" in errors[0]

    def test_execute_empty_recommendations_list(self) -> None:
        """Successfully return empty recommendations list when none found."""
        mock_service = _make_mock_llm_service(recommendations=[])
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        assert result["recommendations"] == []
        assert result["processing_status"] == "recommendation_completed"

    def test_execute_returns_only_partial_state(self) -> None:
        """Agent returns only the keys it modifies, not the full state."""
        mock_service = _make_mock_llm_service()
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        # Only recommendations and processing_status should be in the returned dict
        assert set(result.keys()) <= {
            "recommendations",
            "processing_status",
            "errors",
        }

    def test_execute_recommendation_structure(self) -> None:
        """Verify that returned recommendations have the expected structure."""
        mock_service = _make_mock_llm_service(
            recommendations=_SAMPLE_RECOMMENDATIONS
        )
        agent = RecommendationAgent(llm_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        
        # Check first recommendation has all required fields
        first_rec = recommendations[0]
        assert "priority" in first_rec
        assert "category" in first_rec
        assert "recommendation" in first_rec
        assert "rationale" in first_rec
