"""Placeholder LangGraph workflow base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseWorkflow(ABC):
    """Abstract base for all LangGraph state-graph workflows."""

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Run the workflow state machine."""
