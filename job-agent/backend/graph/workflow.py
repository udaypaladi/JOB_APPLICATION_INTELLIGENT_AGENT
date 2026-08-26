"""
Wires every node from the architecture doc into a single StateGraph.
Uses SqliteSaver so a session can be closed mid-flow (e.g. right at the
approval gate) and resumed later without losing state.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from graph.state import ApplicationState
from graph.nodes.ingest_parse import ingest_and_parse_node
from graph.nodes.scoring import fit_score_node, gap_analysis_node
from graph.nodes.research import company_research_node
from graph.nodes.drafting import interview_prep_node, draft_generation_node
from graph.nodes.approval_export import approval_gate_node, export_node


def build_graph():
    graph = StateGraph(ApplicationState)

    graph.add_node("ingest_and_parse", ingest_and_parse_node)
    graph.add_node("company_research", company_research_node)
    graph.add_node("fit_score", fit_score_node)
    graph.add_node("gap_analysis", gap_analysis_node)
    graph.add_node("interview_prep", interview_prep_node)
    graph.add_node("draft_generation", draft_generation_node)
    graph.add_node("approval_gate", approval_gate_node)
    graph.add_node("export", export_node)

    graph.add_edge(START, "ingest_and_parse")
    graph.add_conditional_edges(
        "ingest_and_parse",
        lambda state: "failed" if state.get("errors") else "continue",
        {"continue": "company_research", "failed": END},
    )
    graph.add_edge("company_research", "fit_score")
    graph.add_edge("fit_score", "gap_analysis")
    graph.add_edge("gap_analysis", "interview_prep")
    graph.add_edge("interview_prep", "draft_generation")
    graph.add_edge("draft_generation", "approval_gate")
    graph.add_edge("approval_gate", "export")
    graph.add_edge("export", END)

    # SqliteSaver.from_conn_string now returns a context manager.  Use the
    # built-in in-memory saver for this local development scaffold instead.
    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)


compiled_graph = build_graph()
