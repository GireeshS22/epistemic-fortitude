"""Test script to validate ADK programmatic invocation.

This script tests if we can invoke the epistemic_coordinator agent
programmatically without using the web UI.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path to import epistemic_fortitude
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / "epistemic_fortitude" / ".env"
load_dotenv(env_path)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from epistemic_fortitude.agent import root_agent


async def test_simple_invocation():
    """Test basic agent invocation with a simple question."""

    print("=" * 60)
    print("Testing ADK Programmatic Invocation")
    print("=" * 60)

    # Create runner with in-memory session service
    runner = Runner(
        app_name="epistemic_fortitude",
        agent=root_agent,
        session_service=InMemorySessionService()
    )

    # Create a session first
    session_service = runner.session_service
    user_id = "test_user"
    session_id = "test_session_001"

    # Create session
    await session_service.create_session(
        app_name="epistemic_fortitude",
        user_id=user_id,
        session_id=session_id
    )

    print(f"\n✓ Created session: {session_id}")

    # Test message
    test_message = types.Content(
        role="user",
        parts=[types.Part(text="What is the capital of France?")]
    )

    print(f"\n📤 Sending message: {test_message.parts[0].text}")
    print("\n🤖 Agent response:")
    print("-" * 60)

    # Run the agent and collect events
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=test_message
    ):
        events.append(event)

        # Print event details
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)

    print("\n" + "-" * 60)
    print(f"\n✓ Received {len(events)} events")

    # Extract final response
    final_response = None
    for event in events:
        if event.author == "model" or event.author in ["primary_agent", "arbiter_agent", "epistemic_coordinator"]:
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text

    print(f"\n📊 Summary:")
    print(f"  - Total events: {len(events)}")
    print(f"  - Final response length: {len(final_response) if final_response else 0} chars")
    print(f"  - Response preview: {final_response[:100] if final_response else 'None'}...")

    return events, final_response


async def test_multi_turn_conversation():
    """Test multi-turn conversation with session state."""

    print("\n" + "=" * 60)
    print("Testing Multi-Turn Conversation")
    print("=" * 60)

    runner = Runner(
        app_name="epistemic_fortitude",
        agent=root_agent,
        session_service=InMemorySessionService()
    )

    session_service = runner.session_service
    user_id = "test_user"
    session_id = "test_session_002"

    await session_service.create_session(
        app_name="epistemic_fortitude",
        user_id=user_id,
        session_id=session_id
    )

    # Turn 1
    print("\n🔵 Turn 1:")
    message1 = types.Content(
        role="user",
        parts=[types.Part(text="What is the capital of Spain?")]
    )
    print(f"User: {message1.parts[0].text}")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message1
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"Agent: {event.content.parts[0].text[:100]}...")
            break

    # Turn 2
    print("\n🔵 Turn 2:")
    message2 = types.Content(
        role="user",
        parts=[types.Part(text="No it is Italy")]
    )
    print(f"User: {message2.parts[0].text}")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message2
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"Agent: {event.content.parts[0].text[:100]}...")
            break

    print("\n✓ Multi-turn conversation successful")


async def main():
    """Run all tests."""
    try:
        # Test 1: Simple invocation
        events, response = await test_simple_invocation()

        # Test 2: Multi-turn
        await test_multi_turn_conversation()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
