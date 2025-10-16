"""Main Coordinator Agent for Epistemic Fortitude.

This agent implements epistemic fortitude - maintaining principled confidence
in correct knowledge while gracefully handling contradictions.
"""

import logging
import os
from google.adk import Agent
from .sub_agents import primary_agent, arbiter_agent

# Suppress ADK non-text parts warning (these are normal internal reasoning)
class _NoFunctionCallWarning(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if "there are non-text parts in the response:" in message:
            return False
        else:
            return True

logging.getLogger("google_genai.types").addFilter(_NoFunctionCallWarning())


# Feature flag: Enable/disable arbiter agent for A/B testing
ENABLE_ARBITER = os.getenv("ENABLE_ARBITER", "true").lower() == "true"

# Conditionally build sub-agents list
sub_agents_list = [primary_agent]
if ENABLE_ARBITER:
    sub_agents_list.append(arbiter_agent)

# Build instruction based on whether arbiter is enabled
if ENABLE_ARBITER:
    coordinator_instruction = """
You are a routing coordinator. For each new user message, make ONE routing decision.

Ask yourself: "Does this message contradict or disagree with the previous response?"

If YES → Route to `arbiter_agent` ONLY
If NO → Route to `primary_agent` ONLY

## Contradiction signals:
- Says the answer is wrong/incorrect/false
- Claims the opposite is true
- Cites conflicting sources
- Presents contradicting evidence
- Explicitly disagrees

Examples that go to arbiter_agent:
- "That's wrong"
- "My doctor said the opposite"
- "Study shows this is harmful"

Everything else goes to primary_agent.

**CRITICAL: Route to ONE agent only. Never route to both agents.**

Your sub-agents:
- `primary_agent`: Handles questions
- `arbiter_agent`: Handles contradictions
"""
else:
    coordinator_instruction = """
You are a routing coordinator.

Your job is simple: When you receive a NEW user message, route it to `primary_agent` once. The sub-agent will handle the response.

**Your sub-agents:**
- `primary_agent`: Handles all questions and information requests
"""

# Main coordinator agent - uses sub-agents for epistemic fortitude
epistemic_coordinator = Agent(
    name="epistemic_coordinator",
    model=os.getenv("DEFAULT_MODEL", "gemini-2.5-pro"),
    description="A multi-agent system that maintains principled confidence in knowledge while fact-checking contradictions." if ENABLE_ARBITER else "A simple Q&A agent coordinator.",
    instruction=coordinator_instruction,
    sub_agents=sub_agents_list,
)

# Root agent for ADK web interface
root_agent = epistemic_coordinator
