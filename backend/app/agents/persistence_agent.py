"""PersistenceAgent – final node in the contract processing graph.

Responsibility:
    Persist all processing results to the database and mark the contract
    session as completed (or failed if errors were accumulated).

Design:
    This agent is intentionally thin.  All database communication —
    connection management, query execution, transaction handling — is
    delegated to DatabaseService.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.core.logging import logger
from app.services.database_service import DatabaseService
from app.state.contract_state import ContractState


class PersistenceAgent(BaseAgent):
    """Persist contract analysis results to the database.

    Reads all analysis results from the shared state, delegates to
    ``DatabaseService.save_contract_analysis``, and returns a final
    state update indicating completion or failure.
    """

    def __init__(self, database_service: DatabaseService | None = None) -> None:
        """Initialize the agent with an optional DatabaseService instance.

        Args:
            database_service: Injected DatabaseService for testability.
                              Defaults to a new ``DatabaseService()`` instance.
        """
        self.database_service = database_service or DatabaseService()

    def execute(self, state: ContractState) -> ContractState:
        """Persist contract analysis results and finalise the processing session.

        Args:
            state: The fully populated state from all previous agents.

        Returns:
            Partial state with ``processing_status`` set to ``"completed"``
            if the save operation succeeded, or ``"persistence_failed"``
            if the save operation failed.
        """
        contract_id = state.get("contract_id", "unknown")
        existing_errors = state.get("errors", [])

        logger.info(
            "[PersistenceAgent] Persisting contract analysis | contract_id={contract_id}",
            contract_id=contract_id,
        )

        if existing_errors:
            logger.info(
                "[PersistenceAgent] Contract has {count} errors from previous agents | "
                "contract_id={contract_id}",
                count=len(existing_errors),
                contract_id=contract_id,
            )

        try:
            self.database_service.save_contract_analysis(state)

            logger.info(
                "[PersistenceAgent] Contract analysis persisted successfully | "
                "contract_id={contract_id}",
                contract_id=contract_id,
            )

            return ContractState(
                processing_status="completed",
            )

        except Exception as err:
            error_msg = f"PersistenceAgent: Database save failed — {err}"
            logger.error(
                "[PersistenceAgent] {error}",
                error=error_msg,
            )
            return ContractState(
                errors=[error_msg],
                processing_status="persistence_failed",
            )
