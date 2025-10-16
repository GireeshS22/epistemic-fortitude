"""Test if coordinator sees conversation history.

This test verifies whether the coordinator agent receives
the full conversation history or just the latest message.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / "epistemic_fortitude" / ".env"
load_dotenv(env_path)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from epistemic_fortitude.agent import root_agent


async def test_history():
    """Test if coordinator sees conversation history."""

    print("\n" + "="*70)
    print("TESTING COORDINATOR HISTORY VISIBILITY")
    print("="*70)
    print("\nThis test checks if the coordinator agent receives")
    print("conversation history or only the latest user message.\n")

    runner = Runner(
        app_name="test_history",
        agent=root_agent,
        session_service=InMemorySessionService()
    )

    session_service = runner.session_service
    await session_service.create_session(
        app_name="test_history",
        user_id="test_user",
        session_id="history_test_123"
    )

    # Turn 1 - Normal question
    print("="*70)
    print("TURN 1: Normal Question")
    print("="*70)
    user_msg_1 = "What is aspirin used for?"
    print(f"User: {user_msg_1}")

    msg1 = types.Content(role="user", parts=[types.Part(text=user_msg_1)])
    routed_to_1 = None
    response_1 = ""

    async for event in runner.run_async(
        user_id="test_user",
        session_id="history_test_123",
        new_message=msg1
    ):
        if event.author:
            routed_to_1 = event.author
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_1 += part.text

    print(f"\n✓ Routed to: {routed_to_1}")
    print(f"✓ Response (first 150 chars): {response_1[:150]}...\n")

    # Turn 2 - Simple contradiction (should trigger arbiter if history is visible)
    print("="*70)
    print("TURN 2: Contradiction")
    print("="*70)
    user_msg_2 = "That's wrong"
    print(f"User: {user_msg_2}")
    print("\nExpected behavior:")
    print("  - If coordinator sees history → Should route to arbiter_agent")
    print("  - If coordinator doesn't see history → Will route to primary_agent")

    msg2 = types.Content(role="user", parts=[types.Part(text=user_msg_2)])
    routed_to_2 = None
    response_2 = ""

    async for event in runner.run_async(
        user_id="test_user",
        session_id="history_test_123",
        new_message=msg2
    ):
        if event.author:
            routed_to_2 = event.author
            print(f"➡️  Routing to: {event.author}")
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_2 += part.text

    print(f"\n✓ Final routed to: {routed_to_2}")
    print(f"✓ Response (first 150 chars): {response_2[:150]}...\n")

    # Results
    print("="*70)
    print("TEST RESULTS")
    print("="*70)

    if routed_to_2 == "arbiter_agent":
        print("\n✅ SUCCESS: Coordinator routed to ARBITER")
        print("   → Coordinator CAN see conversation history")
        print("   → The problem is likely prompt instruction-following")
    elif routed_to_2 == "primary_agent":
        print("\n❌ FAILURE: Coordinator routed to PRIMARY")
        print("   → Coordinator CANNOT see conversation history")
        print("   → OR coordinator is ignoring the history")
        print("   → This is the ROOT CAUSE of low arbiter invocation rate")
    else:
        print(f"\n⚠️  UNEXPECTED: Routed to {routed_to_2}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_history())
