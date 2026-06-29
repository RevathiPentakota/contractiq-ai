"""ContractWorkflow – LangGraph StateGraph for contract processing.

This module assembles the end-to-end contract analysis pipeline as a
directed LangGraph ``StateGraph``.  The graph defines execution order
only; all business logic lives inside the individual agent nodes.

Execution order
---------------
START
  └─► document_agent        (extract text from raw file)
        └─► summary_agent   (generate plain-language summary)
              └─► risk_agent         (identify risk signals)
                    └─► clause_agent (extract and label clauses)
                          └─► recommendation_agent (produce recommendations)
                                └─► persistence_agent (save results)
                                      └─► END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.clause_agent import ClauseAgent
from app.agents.document_agent import DocumentAgent
from app.agents.persistence_agent import PersistenceAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.summary_agent import SummaryAgent
from app.state.contract_state import ContractState

# ── Agent instances ────────────────────────────────────────────────────────────
# Agents are instantiated once and reused across all graph invocations.
# Replace with dependency-injected instances when services are wired up.

_document_agent = DocumentAgent()
_summary_agent = SummaryAgent()
_risk_agent = RiskAgent()
_clause_agent = ClauseAgent()
_recommendation_agent = RecommendationAgent()
_persistence_agent = PersistenceAgent()


# ── Node wrapper functions ─────────────────────────────────────────────────────
# LangGraph nodes must be plain callables: (state) -> partial_state.
# These thin wrappers delegate to each agent's execute() method.


def document_node(state: ContractState) -> ContractState:
    """LangGraph node: document extraction."""
    return _document_agent.execute(state)


def summary_node(state: ContractState) -> ContractState:
    """LangGraph node: contract summarisation."""
    return _summary_agent.execute(state)


def risk_node(state: ContractState) -> ContractState:
    """LangGraph node: risk analysis."""
    return _risk_agent.execute(state)


def clause_node(state: ContractState) -> ContractState:
    """LangGraph node: clause extraction."""
    return _clause_agent.execute(state)


def recommendation_node(state: ContractState) -> ContractState:
    """LangGraph node: recommendation generation."""
    return _recommendation_agent.execute(state)


def persistence_node(state: ContractState) -> ContractState:
    """LangGraph node: result persistence."""
    return _persistence_agent.execute(state)


# ── Graph construction ─────────────────────────────────────────────────────────


def build_contract_graph() -> StateGraph:
    """Construct and compile the contract processing StateGraph.

    Returns:
        A compiled LangGraph ``StateGraph`` ready to be invoked with an
        initial ``ContractState``.

    Usage::

        graph = build_contract_graph()
        result = graph.invoke({
            "session_id": "...",
            "contract_id": "...",
            "file_name": "contract.pdf",
            "storage_path": "contracts/contract.pdf",
            "processing_status": "pending",
            "errors": [],
        })
    """
    builder = StateGraph(ContractState)

    # ── Register nodes ─────────────────────────────────────────────────────────
    builder.add_node("document_agent", document_node)
    builder.add_node("summary_agent", summary_node)
    builder.add_node("risk_agent", risk_node)
    builder.add_node("clause_agent", clause_node)
    builder.add_node("recommendation_agent", recommendation_node)
    builder.add_node("persistence_agent", persistence_node)

    # ── Define edges (execution order) ─────────────────────────────────────────
    builder.add_edge(START, "document_agent")
    builder.add_edge("document_agent", "summary_agent")
    builder.add_edge("summary_agent", "risk_agent")
    builder.add_edge("risk_agent", "clause_agent")
    builder.add_edge("clause_agent", "recommendation_agent")
    builder.add_edge("recommendation_agent", "persistence_agent")
    builder.add_edge("persistence_agent", END)

    return builder.compile()


# Module-level compiled graph instance.
# Import and invoke this directly: ``from app.workflows.contract_workflow import contract_graph``
contract_graph = build_contract_graph()
