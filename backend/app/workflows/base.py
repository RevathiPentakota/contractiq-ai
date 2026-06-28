"""Placeholder LangGraph workflow base class.

Workflows orchestrate one or more agents using a LangGraph ``StateGraph``.
Concrete workflows will be added here as features are developed.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseWorkflow(ABC):
    """Abstract base for all LangGraph state-graph workflows."""

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Run the workflow state machine.

        Args:
            state: Initial LangGraph state dictionary.

        Returns:
            Final state after all graph nodes have executed.
        """
