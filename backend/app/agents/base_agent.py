"""Abstract base class for all ContractIQ agents.

Every agent in the system receives the shared ``ContractState``, performs
its work, and returns an updated ``ContractState``.  LangGraph calls each
agent node with the full current state and merges the returned partial
dict back into the graph state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.state.contract_state import ContractState


class BaseAgent(ABC):
    """Abstract base for all LangGraph-backed contract processing agents.

    Subclasses must implement :meth:`execute`.  The method should be
    **synchronous** so LangGraph can call it directly as a graph node.
    For I/O-bound work, wrap calls inside ``asyncio.run`` or use an
    async LangGraph runner.
    """

    @abstractmethod
    def execute(self, state: ContractState) -> ContractState:
        """Process the given state and return an updated state.

        Implementations should:

        1. Read only the keys they need from ``state``.
        2. Perform their specific processing step.
        3. Return a **partial** ``ContractState`` dict containing only
           the keys they modified — LangGraph merges updates automatically.
        4. Append descriptive messages to ``state["errors"]`` for any
           non-fatal issues rather than raising exceptions.

        Args:
            state: The current shared graph state.

        Returns:
            A (partial) ``ContractState`` with updated fields.
        """
