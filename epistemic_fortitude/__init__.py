"""Epistemic Fortitude - A multi-agent AI system with principled knowledge confidence."""

__version__ = "0.1.0"

from . import agent
from . import sub_agents

# Export key components for easy access
from .agent import epistemic_coordinator, root_agent
from .sub_agents import primary_agent, arbiter_agent
