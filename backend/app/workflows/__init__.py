"""Workflows package – LangGraph StateGraph workflows."""

from app.workflows.base import BaseWorkflow
from app.workflows.contract_workflow import contract_graph

__all__ = ["BaseWorkflow", "contract_graph"]
