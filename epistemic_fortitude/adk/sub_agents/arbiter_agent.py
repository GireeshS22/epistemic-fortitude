"""Arbiter Agent - Fact-checking interventional agent for contradictions."""

import os
from google.adk import Agent
from ..prompts import INTERVENTIONAL_AGENT_INSTRUCTIONS


def on_arbiter_agent_start(callback_context):
    """Called when arbiter agent receives control."""
    print("➡️  [COORDINATOR → ARBITER_AGENT] Routing to arbiter for fact-checking")
    return None


def return_to_coordinator(callback_context):
    """Transfer control back to coordinator after fact-checking.

    This ensures the coordinator regains control after the arbiter
    has reviewed and responded to a contradiction.
    """
    print("⬅️  [ARBITER_AGENT → COORDINATOR] Transferring control back")
    callback_context._event_actions.transfer_to_agent = "epistemic_coordinator"
    return None  # Use agent's original response


def create_arbiter_agent() -> Agent:
    """Create and configure the interventional arbiter agent.

    The arbiter agent is responsible for fact-checking and adjudicating
    disputes when users contradict the primary agent's responses.

    Returns:
        Agent: Configured arbiter agent instance
    """
    model = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

    agent = Agent(
        name="arbiter_agent",
        model=model,
        description="Fact-checking agent that reviews contradictions and defends correct answers or gracefully corrects errors.",
        instruction=INTERVENTIONAL_AGENT_INSTRUCTIONS,
        before_agent_callback=on_arbiter_agent_start,
        after_agent_callback=return_to_coordinator,
    )

    return agent


# Create default arbiter agent instance
arbiter_agent = create_arbiter_agent()
