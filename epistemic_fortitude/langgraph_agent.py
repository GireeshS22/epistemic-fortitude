"""Main LangGraph-based Epistemic Fortitude Agent.

This module provides the compiled graph for use in experiments.
It replaces the ADK-based agent.py module.

Usage in experiments:
    from epistemic_fortitude.langgraph_agent import epistemic_graph, ENABLE_ARBITER
    from langchain_core.messages import HumanMessage

    result = epistemic_graph.invoke(
        {
            "messages": [HumanMessage(content="How do I fix this Python bug in my code?")],
            "arbiter_enabled": ENABLE_ARBITER,
            "conversation_id": "exp_001",
            "turn_number": 1
        },
        config={"configurable": {"thread_id": "exp_001"}}
    )
"""

import os
import warnings
import logging

# Suppress Google Cloud warnings
os.environ["GLOG_minloglevel"] = "3"  # Suppress Google logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Suppress specific Google Cloud ALTS warnings
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport").setLevel(logging.ERROR)
logging.getLogger("google.auth.transport.requests").setLevel(logging.ERROR)

from .langgraph import create_epistemic_graph

# Feature flag: Enable/disable arbiter agent for A/B testing
# Same as ADK version for backward compatibility
ENABLE_ARBITER = os.getenv("ENABLE_ARBITER", "true").lower() == "true"

# Create compiled graph with pure LLM routing (no keyword detection)
# This is the main export that replaces ADK's root_agent
epistemic_graph = create_epistemic_graph(use_hybrid_routing=False)

print(f"\n{'='*70}")
print("EPISTEMIC FORTITUDE - LangGraph Implementation (SWE-bench)")
print(f"{'='*70}")
print(f"Arbiter: {'ENABLED' if ENABLE_ARBITER else 'DISABLED'}")
print(f"Routing: Pure LLM (100% LLM, no keywords)")
print(f"Domain: Software Engineering (SWE-bench)")
print(f"Using context-aware prompting for contradiction detection")
print(f"{'='*70}\n")

# Export for external use
__all__ = ["epistemic_graph", "ENABLE_ARBITER"]
