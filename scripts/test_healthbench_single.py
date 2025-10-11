"""Test script to validate HealthBench example processing.

This script loads 1 HealthBench example and tests running it through
the epistemic fortitude agents.
"""

import asyncio
import json
import os
import sys
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


def load_healthbench_example(jsonl_path, index=0):
    """Load a single example from HealthBench JSONL file.

    Args:
        jsonl_path: Path to the JSONL file
        index: Which example to load (0-indexed)

    Returns:
        dict: The parsed example
    """
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == index:
                return json.loads(line)
    raise ValueError(f"Example {index} not found in file")


def print_example_info(example):
    """Print structured information about a HealthBench example."""
    print("\n" + "=" * 70)
    print("HEALTHBENCH EXAMPLE INFO")
    print("=" * 70)

    print(f"\n📋 Example ID: {example.get('prompt_id', 'N/A')}")
    print(f"🏷️  Tags: {', '.join(example.get('example_tags', []))}")

    # Print conversation
    print(f"\n💬 Conversation ({len(example['prompt'])} turns):")
    print("-" * 70)
    for i, turn in enumerate(example['prompt'], 1):
        role = turn['role'].upper()
        content = turn['content'][:100] + "..." if len(turn['content']) > 100 else turn['content']
        print(f"\n{i}. [{role}]: {content}")

    # Print rubrics summary
    rubrics = example.get('rubrics', [])
    print(f"\n📊 Rubrics: {len(rubrics)} criteria")
    print("-" * 70)

    # Count by axis
    axis_counts = {}
    for rubric in rubrics:
        for tag in rubric.get('tags', []):
            if tag.startswith('axis:'):
                axis = tag.split(':')[1]
                axis_counts[axis] = axis_counts.get(axis, 0) + 1

    print("By axis:")
    for axis, count in sorted(axis_counts.items()):
        print(f"  - {axis}: {count}")

    # Show point distribution
    positive_points = sum(r['points'] for r in rubrics if r['points'] > 0)
    negative_points = sum(r['points'] for r in rubrics if r['points'] < 0)
    print(f"\nPoint distribution:")
    print(f"  - Positive criteria: {positive_points} points")
    print(f"  - Negative criteria: {negative_points} points")


async def replay_healthbench_conversation(example, arbiter_enabled=True):
    """Replay a HealthBench conversation through ADK agents.

    Args:
        example: The HealthBench example dict
        arbiter_enabled: Whether arbiter is enabled

    Returns:
        list: Events from all turns
    """
    print("\n" + "=" * 70)
    print(f"RUNNING CONVERSATION (ARBITER: {'ENABLED' if arbiter_enabled else 'DISABLED'})")
    print("=" * 70)

    # Create runner
    runner = Runner(
        app_name="epistemic_fortitude",
        agent=root_agent,
        session_service=InMemorySessionService()
    )

    # Create session
    session_service = runner.session_service
    user_id = "healthbench_test"
    session_id = f"hb_{example['prompt_id'][:8]}"

    await session_service.create_session(
        app_name="epistemic_fortitude",
        user_id=user_id,
        session_id=session_id
    )

    print(f"\n✓ Created session: {session_id}\n")

    # Replay conversation turn by turn
    all_events = []
    conversation = example['prompt']

    for turn_num, turn in enumerate(conversation, 1):
        if turn['role'] != 'user':
            continue  # Skip assistant turns (we'll generate those)

        print(f"\n{'='*70}")
        print(f"TURN {turn_num}")
        print(f"{'='*70}")
        print(f"\n👤 USER: {turn['content']}\n")

        # Create message
        message = types.Content(
            role="user",
            parts=[types.Part(text=turn['content'])]
        )

        # Run agent
        turn_events = []
        print("🤖 AGENT: ", end="", flush=True)

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            turn_events.append(event)

            # Print response as it streams
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)

        print()  # Newline after response
        all_events.extend(turn_events)

        # Show which agent was used
        agent_used = "unknown"
        for event in turn_events:
            if event.author in ["primary_agent", "arbiter_agent"]:
                agent_used = event.author

        print(f"\n📍 Agent used: {agent_used}")
        print(f"📦 Events: {len(turn_events)}")

    return all_events


async def main():
    """Main test function."""

    # Load first example
    jsonl_path = Path(__file__).parent.parent / "data" / "healthbench" / "2025-05-07-06-14-12_oss_eval.jsonl"

    print("\n" + "=" * 70)
    print("PHASE 2: SINGLE HEALTHBENCH EXAMPLE TEST")
    print("=" * 70)

    print(f"\n📂 Loading from: {jsonl_path.name}")

    # Load example (using index 5 for multi-turn conversation)
    example = load_healthbench_example(jsonl_path, index=5)

    # Print info
    print_example_info(example)

    # Test with arbiter enabled
    print("\n\n" + "🛡️  " * 20)
    events_with_arbiter = await replay_healthbench_conversation(example, arbiter_enabled=True)

    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n✅ Successfully replayed {len(example['prompt'])} turns")
    print(f"📊 Total events captured: {len(events_with_arbiter)}")

    # Check if arbiter was used
    arbiter_used = any(e.author == "arbiter_agent" for e in events_with_arbiter)
    print(f"🛡️  Arbiter invoked: {'YES' if arbiter_used else 'NO'}")

    print("\n" + "=" * 70)
    print("✅ PHASE 2 TEST COMPLETE!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
