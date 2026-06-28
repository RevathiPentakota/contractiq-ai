"""Agents package.

This package will contain LangGraph-powered agents for ContractIQ.
Each agent subclasses ``BaseAgent`` and encapsulates a single AI capability.

Planned agents (not yet implemented):
- ContractAnalysisAgent   – extract clauses and risk signals
- SummaryAgent            – produce plain-language contract summaries
- ComparisonAgent         – diff two contract versions
"""

from app.agents.base import BaseAgent

__all__ = ["BaseAgent"]
