"""Primary agent definition for Epistemic Fortitude."""

import os
from google.adk import Agent
from .prompts import PRIMARY_AGENT_INSTRUCTIONS


def create_primary_agent() -> Agent:
    """Create and configure the primary conversational agent.

    Returns:
        Agent: Configured primary agent instance
    """
    model = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

    agent = Agent(
        name="primary_agent",
        model=model,
        instruction=PRIMARY_AGENT_INSTRUCTIONS,
    )

    return agent


# Create default agent instance
root_agent = create_primary_agent()
