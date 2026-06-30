"""ContractWorkflow - LangGraph StateGraph for contract processing.

Execution order
---------------
START
  -> document_agent
        +-> summary_agent  -+
        +-> risk_agent     -+-> recommendation_agent -> persistence_agent -> END
        +-> clause_agent   -+

SummaryAgent, RiskAgent, and ClauseAgent run in parallel (fan-out) after
DocumentAgent. LangGraph fans in at recommendation_agent, waiting for all
three branches before proceeding. RecommendationAgent is sequential because
it reads summary, risks, and clauses produced by the parallel trio.
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

_document_agent = DocumentAgent()
_summary_agent = SummaryAgent()
_risk_agent = RiskAgent()
_clause_agent = ClauseAgent()
_recommendation_agent = RecommendationAgent()
_persistence_agent = PersistenceAgent()


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


def build_contract_graph() -> StateGraph:
    """Construct and compile the contract processing StateGraph."""
    builder = StateGraph(ContractState)

    builder.add_node("document_agent", document_node)
    builder.add_node("summary_agent", summary_node)
    builder.add_node("risk_agent", risk_node)
    builder.add_node("clause_agent", clause_node)
    builder.add_node("recommendation_agent", recommendation_node)
    builder.add_node("persistence_agent", persistence_node)

    # Sequential start
    builder.add_edge(START, "document_agent")

    # Fan-out: document_agent -> three parallel analysis agents
    builder.add_edge("document_agent", "summary_agent")
    builder.add_edge("document_agent", "risk_agent")
    builder.add_edge("document_agent", "clause_agent")

    # Fan-in: all three -> recommendation_agent (waits for all branches)
    builder.add_edge("summary_agent", "recommendation_agent")
    builder.add_edge("risk_agent", "recommendation_agent")
    builder.add_edge("clause_agent", "recommendation_agent")

    # Sequential finish
    builder.add_edge("recommendation_agent", "persistence_agent")
    builder.add_edge("persistence_agent", END)

    return builder.compile()


# Module-level instance - import as: from app.workflows.contract_workflow import contract_graph
contract_graph = build_contract_graph()
