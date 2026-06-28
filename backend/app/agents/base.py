"""Placeholder agent base class.

Concrete agents (e.g. ContractAnalysisAgent) will subclass ``BaseAgent``
and implement the ``run`` method once business logic is introduced.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Abstract base for all LangGraph-backed agents."""

    @abstractmethod
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent and return its output.

        Args:
            input_data: Structured payload passed to the agent.

        Returns:
            Structured result produced by the agent.
        """
