"""RiskAgent – third node in the contract processing graph.

Responsibility:
    Receive the extracted contract text from ContractState, send it to
    the LLM via LLMService, and store the resulting risk analysis
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


class RiskAgent(BaseAgent):
    """Analyse a contract for legal, financial, and operational risks.

    Reads ``extracted_text`` from the shared state, delegates to
    ``LLMService.generate_risks``, and returns the result as a
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
        """Identify legal, financial, and operational risks in the contract.

        Args:
            state: Must contain a non-empty ``extracted_text`` field.

        Returns:
            Partial state with ``risks`` (list of dicts) and
            ``processing_status`` = ``"risk_completed"``.
            On failure, returns ``processing_status`` = ``"risk_failed"``
            and appends an error message to ``errors``.
        """
        contract_id = state.get("contract_id", "unknown")
        extracted_text = state.get("extracted_text", "")

        logger.info(
            "[RiskAgent] Analysing risks | contract_id={contract_id}",
            contract_id=contract_id,
        )

        if not extracted_text or not extracted_text.strip():
            error_msg = (
                f"RiskAgent: extracted_text is empty for "
                f"contract_id={contract_id}. Skipping LLM call."
            )
            logger.warning(error_msg)
            return ContractState(
                risks=[],
                errors=[error_msg],
                processing_status="risk_failed",
            )

        try:
            risks = self.llm_service.generate_risks(extracted_text)

            logger.info(
                "[RiskAgent] Risk analysis complete | contract_id={contract_id} | "
                "{count} risks identified",
                contract_id=contract_id,
                count=len(risks),
            )

            return ContractState(
                risks=risks,
                processing_status="risk_completed",
            )

        except Exception as err:
            error_msg = f"RiskAgent: LLM call failed — {err}"
            logger.error(
                "[RiskAgent] {error}",
                error=error_msg,
            )
            return ContractState(
                risks=[],
                errors=[error_msg],
                processing_status="risk_failed",
            )
