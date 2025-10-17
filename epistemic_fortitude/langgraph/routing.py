"""Hybrid routing logic for epistemic fortitude.

This module implements the key improvement over ADK's pure LLM routing:
- Tier 1: Strong keyword detection (deterministic, fast)
- Tier 2: Soft keyword detection (deterministic, catches subtle contradictions)
- Tier 3: LLM fallback (flexible, handles edge cases)

Expected improvement: 44% → 85%+ arbiter invocation rate
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .state import EpistemicState


def route_message_hybrid(state: EpistemicState) -> str:
    """Hybrid routing: Keywords (fast) + LLM fallback (flexible).

    This is the main routing function that solves the 44% invocation problem
    identified in Sessions 5-6 of the ADK implementation.

    Routing Strategy:
    1. Check if arbiter is disabled → route to primary
    2. Check strong contradiction keywords → route to arbiter
    3. Check soft contradiction keywords → route to arbiter
    4. Use LLM for subtle contradictions → route based on LLM decision

    Args:
        state: Current conversation state

    Returns:
        "primary" or "arbiter" - which node to route to
    """
    # If arbiter disabled (baseline condition), always route to primary
    if not state.get("arbiter_enabled", True):
        state["routing_reason"] = "arbiter_disabled"
        return "primary"

    # Get last user message
    last_message = state["messages"][-1].content.lower()

    # Tier 1: Strong contradiction keywords (deterministic)
    # Based on the 16 contradiction prompts from Session 6
    STRONG_KEYWORDS = [
        "wrong", "incorrect", "false", "not true", "dangerous",
        "harmful", "misleading", "not safe", "that's not right",
        "that's incorrect", "disagree", "not correct", "that's wrong",
        "you're wrong", "i disagree", "completely different"
    ]

    for keyword in STRONG_KEYWORDS:
        if keyword in last_message:
            state["routing_reason"] = f"keyword_strong:{keyword}"
            print(f"  🔍 Routing reason: Strong keyword detected '{keyword}'")
            return "arbiter"

    # Tier 2: Soft contradiction patterns (deterministic)
    # Catches concern/doubt/questioning language that suggests disagreement
    SOFT_KEYWORDS = [
        "worried", "concerned", "risky", "doubt", "side effects",
        "contradicts", "not sure", "sounds risky", "concerning",
        "dangerous for", "problem", "issue", "doesn't sound right",
        "i don't think", "can't follow", "opposite", "not what",
        "that doesn't", "shouldn't", "guidance", "guidelines say"
    ]

    for keyword in SOFT_KEYWORDS:
        if keyword in last_message:
            state["routing_reason"] = f"keyword_soft:{keyword}"
            print(f"  🔍 Routing reason: Soft keyword detected '{keyword}'")
            return "arbiter"

    # Tier 3: LLM fallback for subtle contradictions
    # Only invoked if no keywords matched (saves cost and latency)
    print("  🤖 No keywords matched, using LLM for routing decision...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",  # Use advanced model for better reasoning
        temperature=0.0  # Deterministic
    )

    # Previous assistant message for context (if it exists)
    previous_response = ""
    if len(state["messages"]) >= 2:
        for msg in reversed(state["messages"][:-1]):  # Exclude current user message
            if hasattr(msg, 'type') and msg.type == 'ai':
                previous_response = msg.content
                break

    prompt = f"""You are a routing system for a medical Q&A agent with epistemic fortitude.

Your task: Determine if the user's message contradicts, disagrees with, or questions the previous medical advice.

Previous assistant response:
{previous_response if previous_response else "(none - this is the first turn)"}

Current user message:
{state["messages"][-1].content}

Does this user message express:
- Disagreement with the previous advice?
- A contradiction to what was stated?
- Concern that the advice is wrong or dangerous?
- Citation of conflicting information (doctor, study, guidelines)?

Answer with ONLY "yes" or "no"."""

    response = llm.invoke([HumanMessage(content=prompt)])

    if "yes" in response.content.lower():
        state["routing_reason"] = "llm_detection"
        print("  🔍 Routing reason: LLM detected contradiction")
        return "arbiter"
    else:
        state["routing_reason"] = "normal_qa"
        print("  🔍 Routing reason: Normal Q&A")
        return "primary"


def route_message_llm_only(state: EpistemicState) -> str:
    """Pure LLM routing with context-aware prompting.

    This provides 100% LLM-based routing without keyword detection.
    Unlike the original ADK implementation, this version includes
    conversation context for better contradiction detection.

    Args:
        state: Current conversation state

    Returns:
        "primary" or "arbiter" - which node to route to
    """
    # If arbiter disabled, always route to primary
    if not state.get("arbiter_enabled", True):
        state["routing_reason"] = "arbiter_disabled"
        return "primary"

    print("  🤖 Using LLM-only routing (no keyword detection)...")

    # Use LLM to detect contradiction
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",  # Use advanced model for better reasoning
        temperature=0.0  # Deterministic
    )

    # Get previous assistant message for context (if it exists)
    previous_response = ""
    if len(state["messages"]) >= 2:
        for msg in reversed(state["messages"][:-1]):  # Exclude current user message
            if hasattr(msg, 'type') and msg.type == 'ai':
                previous_response = msg.content
                break

    # Context-aware prompt (improved from ADK's simple approach)
    prompt = f"""You are a routing system for a medical Q&A agent with epistemic fortitude.

Your task: Determine if the user's message contradicts, disagrees with, or questions the previous medical advice.

Previous assistant response:
{previous_response if previous_response else "(none - this is the first turn)"}

Current user message:
{state["messages"][-1].content}

Does this user message express:
- Disagreement with the previous advice?
- A contradiction to what was stated?
- Concern that the advice is wrong or dangerous?
- Citation of conflicting information (doctor, study, guidelines)?

Answer with ONLY "yes" or "no"."""

    response = llm.invoke([HumanMessage(content=prompt)])

    if "yes" in response.content.lower():
        state["routing_reason"] = "llm_only"
        print("  🔍 Routing reason: LLM detected contradiction (no keywords)")
        return "arbiter"
    else:
        state["routing_reason"] = "normal_qa"
        print("  🔍 Routing reason: Normal Q&A")
        return "primary"
