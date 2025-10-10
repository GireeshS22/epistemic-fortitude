"""Primary Agent - Fast conversational agent for normal Q&A."""

import os
from google.adk import Agent
from ..prompts import PRIMARY_AGENT_INSTRUCTIONS


def return_to_coordinator(callback_context):
    """Transfer control back to coordinator after answering.

    This ensures the coordinator sees all subsequent messages and can
    detect contradictions throughout the conversation.
    """
    callback_context._event_actions.transfer_to_agent = "epistemic_coordinator"
    return None  # Use agent's original response


def create_primary_agent() -> Agent:
    """Create and configure the primary conversational agent.

    Returns:
        Agent: Configured primary agent instance
    """
    model = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

    agent = Agent(
        name="primary_agent",
        model=model,
        description="Fast conversational agent that answers user questions accurately and confidently.",
        instruction=PRIMARY_AGENT_INSTRUCTIONS,
        after_agent_callback=return_to_coordinator,
    )

    return agent


# Primary agent instance
primary_agent = create_primary_agent()
