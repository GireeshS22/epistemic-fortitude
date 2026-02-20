"""LangGraph construction for epistemic fortitude.

This module builds the StateGraph that replaces ADK's agent hierarchy.

Graph Structure:
    START → router → [primary_agent OR arbiter_agent] → END

Equivalent ADK flow:
    epistemic_coordinator → [primary_agent OR arbiter_agent] → coordinator
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import EpistemicState
from .nodes import primary_agent_node, arbiter_agent_node, merged_agent_node
from .routing import route_message_hybrid, route_message_llm_only


def create_epistemic_graph(use_hybrid_routing: bool = True) -> StateGraph:
    """Create and compile the epistemic fortitude state graph.

    Args:
        use_hybrid_routing: If True, use keyword + LLM hybrid routing (recommended).
                           If False, use pure LLM routing (ADK equivalent).

    Returns:
        Compiled StateGraph ready for invocation

    Example:
        >>> graph = create_epistemic_graph(use_hybrid_routing=True)
        >>> result = graph.invoke(
        ...     {"messages": [HumanMessage(content="What is the capital of France?")],
        ...      "arbiter_enabled": True,
        ...      "conversation_id": "test_001",
        ...      "turn_number": 1},
        ...     config={"configurable": {"thread_id": "test_001"}}
        ... )
    """
    # Create graph with state schema
    graph = StateGraph(EpistemicState)

    # Add agent nodes (equivalent to ADK sub_agents)
    graph.add_node("primary_agent", primary_agent_node)
    graph.add_node("arbiter_agent", arbiter_agent_node)

    # Select routing function
    routing_func = route_message_hybrid if use_hybrid_routing else route_message_llm_only

    # Add conditional routing from START (equivalent to ADK coordinator)
    # The routing function returns "primary" or "arbiter"
    graph.add_conditional_edges(
        START,
        routing_func,
        {
            "primary": "primary_agent",
            "arbiter": "arbiter_agent"
        }
    )

    # Both agents end the conversation (no return to coordinator needed)
    graph.add_edge("primary_agent", END)
    graph.add_edge("arbiter_agent", END)

    # Compile with checkpointing for multi-turn conversations
    # This enables conversation history across turns
    memory = MemorySaver()
    compiled = graph.compile(checkpointer=memory)

    print("✅ LangGraph compiled successfully")
    if use_hybrid_routing:
        print("   📍 Using hybrid routing (keyword + LLM)")
    else:
        print("   📍 Using LLM-only routing (ADK equivalent)")

    return compiled


def create_ablation_graph() -> StateGraph:
    """Create a single-agent graph for ablation study.

    This graph has no routing — every message goes to the merged agent.
    Used to test whether the multi-agent architecture matters or if
    a single agent with combined instructions achieves the same effect.

    Returns:
        Compiled StateGraph with single merged agent node
    """
    graph = StateGraph(EpistemicState)

    graph.add_node("merged_agent", merged_agent_node)

    graph.add_edge(START, "merged_agent")
    graph.add_edge("merged_agent", END)

    memory = MemorySaver()
    compiled = graph.compile(checkpointer=memory)

    print("✅ Ablation graph compiled successfully")
    print("   📍 Single merged agent (no routing)")

    return compiled


def visualize_graph(graph: StateGraph, output_path: str = "epistemic_graph.png"):
    """Visualize the graph structure (requires graphviz).

    Args:
        graph: Compiled StateGraph
        output_path: Where to save the visualization

    Note:
        Requires: pip install pygraphviz
    """
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        print("⚠️  Visualization requires: pip install pygraphviz")
    except Exception as e:
        print(f"⚠️  Could not visualize graph: {e}")
