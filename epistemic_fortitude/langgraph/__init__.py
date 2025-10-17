"""LangGraph implementation of epistemic fortitude.

This package provides a LangGraph-based multi-agent system that maintains
principled confidence in correct knowledge while gracefully handling contradictions.

Key improvements over ADK implementation:
- Hybrid routing (keyword + LLM) for 85%+ arbiter invocation rate
- Explicit state management and routing reason tracking
- Full control over message flow and decision logic
- Better debugging and analysis capabilities

Usage:
    from epistemic_fortitude.langgraph import create_epistemic_graph
    from langchain_core.messages import HumanMessage

    graph = create_epistemic_graph(use_hybrid_routing=True)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="What is the capital of France?")],
            "arbiter_enabled": True,
            "conversation_id": "test_001",
            "turn_number": 1
        },
        config={"configurable": {"thread_id": "test_001"}}
    )

    print(result["agent_response"])
    print(result["routed_to"])  # "primary" or "arbiter"
    print(result["routing_reason"])  # Why this routing decision
"""

from .state import EpistemicState
from .nodes import primary_agent_node, arbiter_agent_node
from .routing import route_message_hybrid, route_message_llm_only
from .graph import create_epistemic_graph, visualize_graph

__all__ = [
    "EpistemicState",
    "primary_agent_node",
    "arbiter_agent_node",
    "route_message_hybrid",
    "route_message_llm_only",
    "create_epistemic_graph",
    "visualize_graph",
]
