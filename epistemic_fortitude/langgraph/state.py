"""State schema for epistemic fortitude LangGraph implementation.

This module defines the conversation state that flows through the graph.
"""

from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage


class EpistemicState(TypedDict):
    """State for epistemic fortitude conversations.

    This state schema replaces ADK's implicit session state with explicit fields
    that track the conversation, routing decisions, and metrics.
    """

    # Core conversation
    messages: List[BaseMessage]
    """Conversation history"""

    # Routing information
    routed_to: Optional[str]
    """Which agent handled this turn: 'primary' or 'arbiter'"""

    routing_reason: Optional[str]
    """Why this routing decision was made: 'keyword_strong', 'keyword_soft', 'llm_detection', 'normal_qa'"""

    # Experiment configuration
    arbiter_enabled: bool
    """Whether arbiter agent is enabled (for A/B testing)"""

    conversation_id: str
    """Unique identifier for this conversation"""

    turn_number: int
    """Current turn number in the conversation"""

    # Response metrics (for logging)
    agent_response: Optional[str]
    """The agent's text response for this turn"""

    latency_ms: Optional[float]
    """Response latency in milliseconds"""

    prompt_tokens: Optional[int]
    """Number of tokens in the prompt"""

    completion_tokens: Optional[int]
    """Number of tokens in the completion"""

    total_tokens: Optional[int]
    """Total tokens used (prompt + completion)"""
