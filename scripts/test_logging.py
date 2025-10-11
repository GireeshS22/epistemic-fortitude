"""Test script for logging infrastructure.

This script tests the ExperimentLogger with 1 HealthBench example,
capturing all metrics including token counts and latency.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / "epistemic_fortitude" / ".env"
load_dotenv(env_path)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from epistemic_fortitude.agent import root_agent
from epistemic_fortitude.utils import ExperimentLogger


def load_healthbench_example(jsonl_path, index=0):
    """Load a single example from HealthBench JSONL file."""
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == index:
                return json.loads(line)
    raise ValueError(f"Example {index} not found in file")


def extract_token_counts_from_events(events):
    """Extract token counts from ADK events.

    ADK events may contain usage metadata with token counts.
    This function searches through events to find and extract them.

    Args:
        events: List of ADK Event objects

    Returns:
        Dict with prompt_tokens, completion_tokens, total_tokens
        or None if not found
    """
    for event in events:
        # Check if event has usage metadata
        if hasattr(event, 'usage_metadata') and event.usage_metadata:
            usage = event.usage_metadata
            return {
                "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                "total_tokens": getattr(usage, 'total_token_count', 0),
            }

        # Also check in content metadata if available
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'usage_metadata') and event.content.usage_metadata:
                usage = event.content.usage_metadata
                return {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                }

    # If no token counts found, return None
    return None


async def test_logging_with_example(example_index=5, arbiter_enabled=True):
    """Test logging with a single HealthBench example.

    Args:
        example_index: Which example to test
        arbiter_enabled: Whether arbiter is enabled

    Returns:
        Path to experiment directory
    """
    print("\n" + "=" * 70)
    print("PHASE 3: LOGGING INFRASTRUCTURE TEST")
    print("=" * 70)

    # Load example
    jsonl_path = Path(__file__).parent.parent / "data" / "healthbench" / "2025-05-07-06-14-12_oss_eval.jsonl"
    example = load_healthbench_example(jsonl_path, example_index)

    print(f"\n📋 Example: {example['prompt_id']}")
    print(f"🏷️  Theme: {example.get('example_tags', [''])[0]}")
    print(f"💬 Turns: {len(example['prompt'])}")
    print(f"🛡️  Arbiter: {'ENABLED' if arbiter_enabled else 'DISABLED'}")

    # Create logger
    experiment_id = f"test_logging_{'arbiter' if arbiter_enabled else 'baseline'}_{int(time.time())}"
    logger = ExperimentLogger(
        experiment_id=experiment_id,
        arbiter_enabled=arbiter_enabled
    )

    print(f"\n📁 Logging to: {logger.get_experiment_dir()}")

    # Start conversation log
    conversation_log = logger.start_conversation(
        example_id=example['prompt_id'],
        theme=example.get('example_tags', [''])[0] if example.get('example_tags') else 'unknown',
        tags=example.get('example_tags', []),
        rubrics=example.get('rubrics', [])
    )

    # Create ADK runner
    runner = Runner(
        app_name="epistemic_fortitude",
        agent=root_agent,
        session_service=InMemorySessionService()
    )

    # Create session
    session_service = runner.session_service
    user_id = "test_logging"
    session_id = f"log_test_{example['prompt_id'][:8]}"

    await session_service.create_session(
        app_name="epistemic_fortitude",
        user_id=user_id,
        session_id=session_id
    )

    print("\n" + "=" * 70)
    print("RUNNING CONVERSATION")
    print("=" * 70)

    # Replay conversation
    turn_number = 0
    for turn in example['prompt']:
        if turn['role'] != 'user':
            continue  # Skip assistant turns

        turn_number += 1
        user_message = turn['content']

        print(f"\n{'─'*70}")
        print(f"TURN {turn_number}")
        print(f"{'─'*70}")
        print(f"\n👤 USER: {user_message[:100]}...")

        # Create message
        message = types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )

        # Track timing
        start_time = time.time()

        # Run agent and collect events
        turn_events = []
        agent_response = ""

        print("\n🤖 AGENT: ", end="", flush=True)

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            turn_events.append(event)

            # Collect response text
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        agent_response += part.text
                        print(part.text[:50], end="", flush=True)

        print("...")

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Determine which agent was used
        routed_to = "primary_agent"  # default
        for event in turn_events:
            if event.author == "arbiter_agent":
                routed_to = "arbiter_agent"
                break

        # Extract token counts
        token_counts = extract_token_counts_from_events(turn_events)

        # Log the turn
        logger.log_turn(
            conversation_log=conversation_log,
            turn_number=turn_number,
            user_message=user_message,
            agent_response=agent_response,
            routed_to=routed_to,
            events=turn_events,
            latency_ms=latency_ms,
            token_counts=token_counts
        )

        # Print metrics
        print(f"\n📊 Metrics:")
        print(f"   - Agent: {routed_to}")
        print(f"   - Latency: {latency_ms:.0f}ms")
        print(f"   - Events: {len(turn_events)}")
        if token_counts:
            print(f"   - Tokens: {token_counts['total_tokens']} "
                  f"(prompt: {token_counts['prompt_tokens']}, "
                  f"completion: {token_counts['completion_tokens']})")
        else:
            print(f"   - Tokens: Not available")

    # Finish conversation
    print("\n" + "=" * 70)
    print("FINISHING CONVERSATION")
    print("=" * 70)

    conv_path = logger.finish_conversation(conversation_log)
    print(f"\n✅ Conversation saved: {Path(conv_path).name}")

    # Save experiment summary
    print("\n" + "=" * 70)
    print("SAVING EXPERIMENT SUMMARY")
    print("=" * 70)

    exp_dir = logger.save_experiment_summary()

    print("\n" + "=" * 70)
    print("✅ PHASE 3 TEST COMPLETE!")
    print("=" * 70)

    print(f"\n📂 Experiment directory: {exp_dir}")
    print(f"📊 Conversations logged: {len(logger.conversation_logs)}")
    print(f"🛡️  Arbiter invocations: {conversation_log['arbiter_invocations']}")
    print(f"🔢 Total tokens: {conversation_log['total_tokens']}")
    print(f"⏱️  Total latency: {conversation_log['total_latency_ms']:.0f}ms")

    return exp_dir


async def main():
    """Main test function."""
    try:
        # Test with single-turn example (index 0) to avoid agent loop issues
        exp_dir = await test_logging_with_example(example_index=0, arbiter_enabled=True)

        print("\n" + "=" * 70)
        print("📁 CHECK THE LOGS:")
        print("=" * 70)
        print(f"\nExperiment directory: {exp_dir}")
        print("\nFiles created:")
        print("  - metadata.json (experiment info)")
        print("  - conversations_summary.json (overview)")
        print("  - conversations/*.json (individual conversation logs)")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
