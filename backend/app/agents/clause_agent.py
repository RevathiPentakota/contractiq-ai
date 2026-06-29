"""ClauseAgent – fourth node in the contract processing graph.

Responsibility:
    Receive the extracted contract text from ContractState, send it to
    the LLM via LLMService, and store the resulting clause extraction
    back into the state.

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


class ClauseAgent(BaseAgent):
    """Extract important clauses from a contract.

    Reads ``extracted_text`` from the shared state, delegates to
    ``LLMService.generate_clauses``, and returns the result as a
    partial state update.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        """Initialize the agent with an optional LLMService instance.

        Args:
            llm_service: Injected LLMService for testability.
                         Defaults to a new ``LLMService()`` instance.
        """
        self.llm_service = llm_service or LLMService()

    def execute(self, state: ContractState) -> ContractState:
        """Extract important clauses from the contract.

        Args:
            state: Must contain a non-empty ``extracted_text`` field.

        Returns:
            Partial state with ``clauses`` (list of dicts) and
            ``processing_status`` = ``"clause_completed"``.
            On failure, returns ``processing_status`` = ``"clause_failed"``
            and appends an error message to ``errors``.
        """
        contract_id = state.get("contract_id", "unknown")
        extracted_text = state.get("extracted_text", "")

        logger.info(
            "[ClauseAgent] Extracting clauses | contract_id={contract_id}",
            contract_id=contract_id,
        )

        if not extracted_text or not extracted_text.strip():
            error_msg = (
                f"ClauseAgent: extracted_text is empty for "
                f"contract_id={contract_id}. Skipping LLM call."
            )
            logger.warning(error_msg)
            return ContractState(
                clauses=[],
                errors=[error_msg],
                processing_status="clause_failed",
            )

        try:
            clauses = self.llm_service.generate_clauses(extracted_text)

            logger.info(
                "[ClauseAgent] Clause extraction complete | contract_id={contract_id} | "
                "{count} clauses extracted",
                contract_id=contract_id,
                count=len(clauses),
            )

            return ContractState(
                clauses=clauses,
                processing_status="clause_completed",
            )

        except Exception as err:
            error_msg = f"ClauseAgent: LLM call failed — {err}"
            logger.error(
                "[ClauseAgent] {error}",
                error=error_msg,
            )
            return ContractState(
                clauses=[],
                errors=[error_msg],
                processing_status="clause_failed",
            )
