"""Workflows package.

LangGraph ``StateGraph`` workflows live here.  Each workflow composes
one or more agents into a directed graph of processing nodes.

Planned workflows (not yet implemented):
- ContractIngestionWorkflow  – parse, chunk, embed, and store a contract
- ContractReviewWorkflow     – run analysis and generate a review report
"""

from app.workflows.base import BaseWorkflow

__all__ = ["BaseWorkflow"]
