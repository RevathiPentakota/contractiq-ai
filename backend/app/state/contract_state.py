"""ContractState – shared LangGraph state schema.

Every node in the contract processing graph reads from and writes to
this TypedDict.  LangGraph merges node outputs back into the graph state
automatically, so each agent only needs to return the keys it modifies.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ContractState(TypedDict, total=False):
    """Shared state that flows through every node of the contract graph.

    Fields are intentionally declared with ``total=False`` so that agents
    can return partial updates — only the keys they touch — without
    needing to re-emit the entire state.

    Attributes:
        session_id:         Unique identifier for the processing session.
        contract_id:        Identifier of the contract record in the database.
        file_name:          Original file name uploaded by the user.
        storage_path:       Location of the raw file in object storage.
        extracted_text:     Full plain-text content extracted from the file.
        summary:            Plain-language summary produced by SummaryAgent.
        risks:              List of identified risk signals (dicts with
                            ``level``, ``description``, ``clause_ref`` keys).
        clauses:            List of extracted clauses (dicts with ``title``
                            and ``text`` keys).
        metadata:           Arbitrary contract metadata (parties, dates, etc.).
        recommendations:    Actionable recommendations from RecommendationAgent.
        processing_status:  Lifecycle status: ``"pending"`` → ``"processing"``
                            → ``"completed"`` | ``"failed"``.
        errors:             Accumulated non-fatal error messages from any node.
        created_at:         ISO-8601 timestamp when the session was created.
    """

    session_id: str
    contract_id: str
    file_name: str
    storage_path: str
    extracted_text: str
    summary: str
    risks: list[dict[str, Any]]
    clauses: list[dict[str, Any]]
    metadata: dict[str, Any]
    recommendations: list[str]
    processing_status: str
    errors: list[str]
    created_at: str
