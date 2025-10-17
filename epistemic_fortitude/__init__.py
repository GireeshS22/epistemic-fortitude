"""Epistemic Fortitude - A multi-agent AI system with principled knowledge confidence.

This package now uses LangGraph for improved routing and epistemic fortitude.
ADK code has been archived to epistemic_fortitude/adk/ for reference.
"""

__version__ = "0.1.0"

# Export LangGraph components
from .langgraph_agent import epistemic_graph, ENABLE_ARBITER

# Export utilities
from .utils import ExperimentLogger

__all__ = ["epistemic_graph", "ENABLE_ARBITER", "ExperimentLogger"]
