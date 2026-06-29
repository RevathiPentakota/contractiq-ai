"""SummaryAgent – second node in the contract processing graph.

Responsibility:
    Receive the extracted contract text from ContractState, send it to
    the LLM via LLMService, and store the resulting executive summary
    back into the state.

Design:
    This agent is intentionally thin.  All LLM communication — HTTP,
    retry, timeout, prompt construction — is delegated to LLMService.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.core.logging import logger
from app.services.llm_service import LLMService
from app.state.contract_state import ContractState


class SummaryAgent(BaseAgent):
    """Generate a concise executive summary of the contract text.

    Reads ``extracted_text`` from the shared state, delegates to
    ``LLMService.generate_summary``, and returns the result as a
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
        """Generate a plain-language executive summary of the contract.

        Args:
            state: Must contain a non-empty ``extracted_text`` field.

        Returns:
            Partial state with ``summary`` and
            ``processing_status`` = ``"summary_completed"``.
            On failure, returns ``processing_status`` = ``"summary_failed"``
            and appends an error message to ``errors``.
        """
        contract_id = state.get("contract_id", "unknown")
        extracted_text = state.get("extracted_text", "")

        logger.info(
            "[SummaryAgent] Generating summary | contract_id={contract_id}",
            contract_id=contract_id,
        )

        if not extracted_text or not extracted_text.strip():
            error_msg = (
                f"SummaryAgent: extracted_text is empty for "
                f"contract_id={contract_id}. Skipping LLM call."
            )
            logger.warning(error_msg)
            return ContractState(
                summary="",
                errors=[error_msg],
                processing_status="summary_failed",
            )

        try:
            summary = self.llm_service.generate_summary(extracted_text)

            logger.info(
                "[SummaryAgent] Summary complete | contract_id={contract_id}",
                contract_id=contract_id,
            )

            return ContractState(
                summary=summary,
                processing_status="summary_completed",
            )

        except Exception as err:
            error_msg = f"SummaryAgent: LLM call failed — {err}"
            logger.error(
                "[SummaryAgent] {error}",
                error=error_msg,
            )
            return ContractState(
                summary="",
                errors=[error_msg],
                processing_status="summary_failed",
            )
