"""Agent nodes for epistemic fortitude LangGraph.

This module converts ADK agents to LangGraph node functions.
Each node is a function that takes state and returns updated state.
"""

import os
import time
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, AIMessage
from .state import EpistemicState
from ..prompts import PRIMARY_AGENT_INSTRUCTIONS, INTERVENTIONAL_AGENT_INSTRUCTIONS, MERGED_AGENT_INSTRUCTIONS


def primary_agent_node(state: EpistemicState) -> dict:
    """Primary agent node - handles normal Q&A.

    Maps from: ADK sub_agents/primary_agent.py

    Args:
        state: Current conversation state

    Returns:
        Updated state with agent response and metrics
    """
    print("➡️  Routing to primary agent for Q&A")

    # Initialize LLM (same model as ADK version)
    model_name = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    model_provider = os.getenv("MODEL_PROVIDER", "google_genai")
    temperature = float(os.getenv("PRIMARY_AGENT_TEMPERATURE", "0.7"))

    llm = init_chat_model(
        model=model_name,
        model_provider=model_provider,
        temperature=temperature
    )

    # Build messages with system instruction
    messages = [
        SystemMessage(content=PRIMARY_AGENT_INSTRUCTIONS),
        *state["messages"]
    ]

    # Invoke LLM and track timing
    start_time = time.time()
    response = llm.invoke(messages)
    latency_ms = (time.time() - start_time) * 1000

    # Extract token counts from usage metadata
    usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)

    print(f"  ✓ Primary agent responded ({latency_ms:.0f}ms, {prompt_tokens + completion_tokens} tokens)")

    # Return updated state
    return {
        "messages": [AIMessage(content=response.content)],
        "agent_response": response.content,
        "routed_to": "primary",
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens
    }


def arbiter_agent_node(state: EpistemicState) -> dict:
    """Arbiter agent node - handles contradictions and fact-checking.

    Maps from: ADK sub_agents/arbiter_agent.py

    Args:
        state: Current conversation state

    Returns:
        Updated state with arbiter response and metrics
    """
    print("➡️  Routing to arbiter for fact-checking")

    # Initialize LLM - use ARBITER_MODEL if specified, otherwise use DEFAULT_MODEL
    model_name = os.getenv("ARBITER_MODEL", os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"))
    # Allow arbiter to use different provider if specified
    model_provider = os.getenv("ARBITER_PROVIDER", os.getenv("MODEL_PROVIDER", "google_genai"))
    temperature = float(os.getenv("INTERVENTIONAL_AGENT_TEMPERATURE", "0.3"))

    llm = init_chat_model(
        model=model_name,
        model_provider=model_provider,
        temperature=temperature
    )

    # Build messages with system instruction
    # The arbiter sees full conversation history for context
    messages = [
        SystemMessage(content=INTERVENTIONAL_AGENT_INSTRUCTIONS),
        *state["messages"]
    ]

    # Invoke LLM and track timing
    start_time = time.time()
    response = llm.invoke(messages)
    latency_ms = (time.time() - start_time) * 1000

    # Extract token counts from usage metadata
    usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)

    print(f"  ✓ Arbiter agent responded ({latency_ms:.0f}ms, {prompt_tokens + completion_tokens} tokens)")
    print("  🛡️  Epistemic fortitude: Defending correct information")

    # Return updated state
    return {
        "messages": [AIMessage(content=response.content)],
        "agent_response": response.content,
        "routed_to": "arbiter",
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens
    }


def merged_agent_node(state: EpistemicState) -> dict:
    """Merged single-agent node for ablation study.

    Uses the combined primary + arbiter prompt with primary agent temperature.
    This tests whether the multi-agent architecture matters or if a single agent
    with the same instructions can achieve the same effect.

    Args:
        state: Current conversation state

    Returns:
        Updated state with agent response and metrics
    """
    print("➡️  Routing to merged agent (ablation)")

    model_name = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    model_provider = os.getenv("MODEL_PROVIDER", "google_genai")
    temperature = float(os.getenv("PRIMARY_AGENT_TEMPERATURE", "0.7"))

    llm = init_chat_model(
        model=model_name,
        model_provider=model_provider,
        temperature=temperature
    )

    messages = [
        SystemMessage(content=MERGED_AGENT_INSTRUCTIONS),
        *state["messages"]
    ]

    start_time = time.time()
    response = llm.invoke(messages)
    latency_ms = (time.time() - start_time) * 1000

    usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)

    print(f"  ✓ Merged agent responded ({latency_ms:.0f}ms, {prompt_tokens + completion_tokens} tokens)")

    return {
        "messages": [AIMessage(content=response.content)],
        "agent_response": response.content,
        "routed_to": "merged",
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens
    }
