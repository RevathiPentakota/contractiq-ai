"""Tests for PersistenceAgent and DatabaseService."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from typing import Any

import pytest

from app.agents.persistence_agent import PersistenceAgent
from app.services.database_service import DatabaseService
from app.state.contract_state import ContractState

# ── Shared fixtures ────────────────────────────────────────────────────────────

_SAMPLE_SUMMARY = "This Service Agreement outlines a software development engagement."

_SAMPLE_RISKS: list[dict[str, Any]] = [
    {
        "category": "Financial",
        "severity": "High",
        "title": "Unlimited Liability",
        "description": "Provider has unlimited liability for damages.",
        "clause_reference": "Section 8.2",
        "recommendation": "Limit liability.",
    }
]

_SAMPLE_CLAUSES: list[dict[str, Any]] = [
    {
        "title": "Scope of Services",
        "category": "Services",
        "clause_reference": "Section 1",
        "description": "Provider agrees to deliver services.",
        "importance": "High",
    }
]

_SAMPLE_RECOMMENDATIONS: list[dict[str, Any]] = [
    {
        "priority": "High",
        "category": "Financial",
        "recommendation": "Limit liability to contract value.",
        "rationale": "Excessive exposure.",
    }
]

_SAMPLE_METADATA: dict[str, Any] = {
    "file_size": 1024,
    "word_count": 5000,
    "page_count": 20,
    "format": "pdf",
}


def _make_mock_database_service() -> MagicMock:
    """Return a mock DatabaseService."""
    mock = MagicMock(spec=DatabaseService)
    mock.save_contract_analysis.return_value = None
    return mock


# ── DatabaseService tests ──────────────────────────────────────────────────────


class TestDatabaseService:
    """Unit tests for DatabaseService."""

    def _state_with_analysis(
        self,
        contract_id: str = "contract-1",
        file_name: str = "contract.pdf",
        storage_path: str = "contracts/contract.pdf",
        summary: str = _SAMPLE_SUMMARY,
        risks: list[dict[str, Any]] = _SAMPLE_RISKS,
        clauses: list[dict[str, Any]] = _SAMPLE_CLAUSES,
        recommendations: list[dict[str, Any]] = _SAMPLE_RECOMMENDATIONS,
        metadata: dict[str, Any] = _SAMPLE_METADATA,
    ) -> ContractState:
        return ContractState(
            session_id="test-session",
            contract_id=contract_id,
            file_name=file_name,
            storage_path=storage_path,
            summary=summary,
            risks=risks,
            clauses=clauses,
            recommendations=recommendations,
            metadata=metadata,
            processing_status="recommendation_completed",
            errors=[],
        )

    def test_initialization(self) -> None:
        """Initialize DatabaseService successfully."""
        service = DatabaseService()
        assert service.settings is not None

    def test_save_contract_analysis_success(self) -> None:
        """Successfully save contract analysis without raising."""
        service = DatabaseService()
        state = self._state_with_analysis()

        # Should not raise
        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_with_empty_risks(self) -> None:
        """Accept and save analysis with empty risks list."""
        service = DatabaseService()
        state = self._state_with_analysis(risks=[])

        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_with_empty_clauses(self) -> None:
        """Accept and save analysis with empty clauses list."""
        service = DatabaseService()
        state = self._state_with_analysis(clauses=[])

        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_with_empty_recommendations(self) -> None:
        """Accept and save analysis with empty recommendations list."""
        service = DatabaseService()
        state = self._state_with_analysis(recommendations=[])

        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_with_empty_summary(self) -> None:
        """Accept and save analysis with empty summary."""
        service = DatabaseService()
        state = self._state_with_analysis(summary="")

        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_with_missing_fields(self) -> None:
        """Accept and save analysis with missing optional fields."""
        service = DatabaseService()
        state = ContractState(
            session_id="test-session",
            contract_id="contract-1",
            processing_status="completed",
        )

        result = service.save_contract_analysis(state)

        assert result is None

    def test_save_contract_analysis_logs_debug_info(self) -> None:
        """Log debug information for each save operation."""
        service = DatabaseService()
        state = self._state_with_analysis()

        with patch("app.services.database_service.logger") as mock_logger:
            service.save_contract_analysis(state)

            # Should log the overall operation
            assert mock_logger.info.called
            # Should have logged individual operations
            assert mock_logger.debug.call_count >= 5  # metadata, summary, risks, clauses, recommendations


# ── PersistenceAgent tests ─────────────────────────────────────────────────────


class TestPersistenceAgent:
    """Unit tests for PersistenceAgent."""

    def _state_with_analysis(
        self,
        contract_id: str = "contract-1",
        errors: list[str] = [],
    ) -> ContractState:
        return ContractState(
            session_id="test-session",
            contract_id=contract_id,
            file_name="contract.pdf",
            storage_path="contracts/contract.pdf",
            summary=_SAMPLE_SUMMARY,
            risks=_SAMPLE_RISKS,
            clauses=_SAMPLE_CLAUSES,
            recommendations=_SAMPLE_RECOMMENDATIONS,
            metadata=_SAMPLE_METADATA,
            processing_status="recommendation_completed",
            errors=errors,
        )

    def test_agent_instantiation_default(self) -> None:
        """Instantiate PersistenceAgent with default DatabaseService."""
        agent = PersistenceAgent()
        assert isinstance(agent.database_service, DatabaseService)

    def test_agent_instantiation_injected(self) -> None:
        """Instantiate PersistenceAgent with injected mock DatabaseService."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)
        assert agent.database_service is mock_service

    def test_execute_success_no_errors(self) -> None:
        """Return 'completed' status on successful save with no prior errors."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)

        result = agent.execute(self._state_with_analysis(errors=[]))

        assert result["processing_status"] == "completed"
        assert "errors" not in result or result.get("errors") == []
        mock_service.save_contract_analysis.assert_called_once()

    def test_execute_success_with_prior_errors(self) -> None:
        """Return 'completed' status even if prior agents had errors."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)

        result = agent.execute(
            self._state_with_analysis(errors=["SummaryAgent: LLM timeout"])
        )

        assert result["processing_status"] == "completed"
        # Should still try to save
        mock_service.save_contract_analysis.assert_called_once()

    def test_execute_database_failure_returns_persistence_failed(self) -> None:
        """Return 'persistence_failed' when database save raises exception."""
        mock_service = MagicMock(spec=DatabaseService)
        mock_service.save_contract_analysis.side_effect = Exception(
            "Database connection failed"
        )
        agent = PersistenceAgent(database_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        assert result["processing_status"] == "persistence_failed"
        errors = result.get("errors", [])
        assert len(errors) == 1
        assert "Database connection failed" in errors[0]

    def test_execute_returns_only_partial_state(self) -> None:
        """Agent returns only processing_status, not full state."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)

        result = agent.execute(self._state_with_analysis())

        # Should only contain processing_status (or errors if failure)
        assert set(result.keys()) <= {"processing_status", "errors"}

    def test_execute_passes_state_to_database_service(self) -> None:
        """Pass complete state to database service."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)
        state = self._state_with_analysis()

        result = agent.execute(state)

        # Verify the service was called with the state
        call_args = mock_service.save_contract_analysis.call_args
        assert call_args is not None
        passed_state = call_args[0][0]
        assert passed_state["contract_id"] == "contract-1"
        assert passed_state["summary"] == _SAMPLE_SUMMARY
        assert len(passed_state["risks"]) == 1

    def test_execute_logs_contract_id(self) -> None:
        """Log the contract_id for tracking."""
        mock_service = _make_mock_database_service()
        agent = PersistenceAgent(database_service=mock_service)

        with patch("app.agents.persistence_agent.logger") as mock_logger:
            agent.execute(self._state_with_analysis(contract_id="abc-123"))

            # Should have logged with contract_id
            info_calls = [call for call in mock_logger.info.call_args_list]
            assert any("abc-123" in str(call) for call in info_calls)
