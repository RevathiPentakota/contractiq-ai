"""RecommendationAgent – fifth node in the contract processing graph.

Responsibility:
    Receive the contract summary, risks, and clauses from ContractState,
    send them to the LLM via LLMService, and store the resulting
    recommendations back into the state.

Design:
    This agent is intentionally thin.  All LLM communication — HTTP,
    retry, timeout, prompt construction, JSON parsing — is delegated
    to LLMService.
"""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.logging import logger
from app.services.llm_service import LLMService
from app.state.contract_state import ContractState


class RecommendationAgent(BaseAgent):
    """Generate actionable recommendations from contract analysis.

    Reads ``summary``, ``risks``, and ``clauses`` from the shared state,
    delegates to ``LLMService.generate_recommendations``, and returns
    the result as a partial state update.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        """Initialize the agent with an optional LLMService instance.

        Args:
            llm_service: Injected LLMService for testability.
                         Defaults to a new ``LLMService()`` instance.
        """
        self.llm_service = llm_service or LLMService()

    def execute(self, state: ContractState) -> ContractState:
        """Generate actionable recommendations based on contract analysis.

        Args:
            state: Must contain ``summary``, ``risks``, and ``clauses`` fields.

        Returns:
            Partial state with ``recommendations`` (list of dicts) and
            ``processing_status`` = ``"recommendation_completed"``.
            On failure, returns ``processing_status`` = ``"recommendation_failed"``
            and appends an error message to ``errors``.
        """
        contract_id = state.get("contract_id", "unknown")
        summary = state.get("summary", "")
        risks = state.get("risks", [])
        clauses = state.get("clauses", [])

        logger.info(
            "[RecommendationAgent] Generating recommendations | contract_id={contract_id}",
            contract_id=contract_id,
        )

        if not summary or not summary.strip():
            error_msg = (
                f"RecommendationAgent: summary is empty for "
                f"contract_id={contract_id}. Skipping LLM call."
            )
            logger.warning(error_msg)
            return ContractState(
                recommendations=[],
                errors=[error_msg],
                processing_status="recommendation_failed",
            )

        try:
            recommendations = self.llm_service.generate_recommendations(
                summary=summary,
                risks=risks,
                clauses=clauses,
            )

            logger.info(
                "[RecommendationAgent] Recommendation generation complete | contract_id={contract_id} | "
                "{count} recommendations generated",
                contract_id=contract_id,
                count=len(recommendations),
            )

            return ContractState(
                recommendations=recommendations,
                processing_status="recommendation_completed",
            )

        except Exception as err:
            error_msg = f"RecommendationAgent: LLM call failed — {err}"
            logger.error(
                "[RecommendationAgent] {error}",
                error=error_msg,
            )
            return ContractState(
                recommendations=[],
                errors=[error_msg],
                processing_status="recommendation_failed",
            )
