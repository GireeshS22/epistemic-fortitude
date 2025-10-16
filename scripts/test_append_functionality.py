"""Test script to verify append functionality for metadata and conversations_summary.

This script simulates resuming an experiment by creating two sessions
in the same experiment directory.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from epistemic_fortitude.utils import ExperimentLogger


def create_mock_conversation_log(example_id, theme, turns, tokens, arbiter_invocations):
    """Create a mock conversation log for testing."""
    return {
        "example_id": example_id,
        "theme": theme,
        "tags": [theme],
        "num_rubrics": 3,
        "rubrics": [],
        "start_time": datetime.now().isoformat(),
        "turns": [{"turn_number": i+1} for i in range(turns)],
        "total_latency_ms": 10000,
        "total_tokens": tokens,
        "arbiter_invocations": arbiter_invocations,
        "total_turns": turns,
        "end_time": datetime.now().isoformat(),
        "avg_latency_ms": 10000 / turns,
        "avg_tokens_per_turn": tokens / turns,
    }


def test_append_functionality():
    """Test that metadata and conversations_summary append correctly."""

    print("\n" + "=" * 70)
    print("TESTING APPEND FUNCTIONALITY")
    print("=" * 70)

    experiment_id = "test_append_demo"
    exp_dir = Path(__file__).parent.parent / "logs" / "experiments" / experiment_id

    # SESSION 1: Create first session
    print("\n--- SESSION 1: Creating initial experiment ---")
    logger1 = ExperimentLogger(
        experiment_id=experiment_id,
        arbiter_enabled=True
    )

    # Add 2 conversations to session 1
    conv1 = create_mock_conversation_log("conv-001", "theme:test1", 2, 1000, 1)
    conv2 = create_mock_conversation_log("conv-002", "theme:test2", 3, 1500, 0)

    logger1.finish_conversation(conv1)
    logger1.finish_conversation(conv2)

    logger1.save_experiment_summary()

    print(f"✓ Session 1 completed: 2 conversations logged")

    # Read and display metadata after session 1
    metadata_path = exp_dir / "metadata.json"
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print(f"\nMetadata after Session 1: {len(metadata)} sessions")
    for session in metadata:
        print(f"  - Session {session['session']}: {session['conversations_completed']} conversations")

    # Read and display conversations_summary after session 1
    summary_path = exp_dir / "conversations_summary.json"
    with open(summary_path, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    print(f"\nConversations summary after Session 1: {len(summaries)} total conversations")

    # SESSION 2: Resume experiment with new conversations
    print("\n--- SESSION 2: Resuming experiment ---")
    logger2 = ExperimentLogger(
        experiment_id=experiment_id,
        arbiter_enabled=True
    )

    # Add 1 conversation to session 2
    conv3 = create_mock_conversation_log("conv-003", "theme:test3", 2, 1200, 1)

    logger2.finish_conversation(conv3)

    logger2.save_experiment_summary()

    print(f"✓ Session 2 completed: 1 conversation logged")

    # Read and display metadata after session 2
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print(f"\nMetadata after Session 2: {len(metadata)} sessions")
    for session in metadata:
        print(f"  - Session {session['session']}: {session['conversations_completed']} conversations, "
              f"tokens: {session['aggregate_stats']['total_tokens']}")

    # Read and display conversations_summary after session 2
    with open(summary_path, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    print(f"\nConversations summary after Session 2: {len(summaries)} total conversations")
    for summary in summaries:
        print(f"  - {summary['example_id']}: {summary['theme']}, {summary['total_tokens']} tokens")

    # SESSION 3: One more resume
    print("\n--- SESSION 3: Resuming again ---")
    logger3 = ExperimentLogger(
        experiment_id=experiment_id,
        arbiter_enabled=True
    )

    # Add 2 conversations to session 3
    conv4 = create_mock_conversation_log("conv-004", "theme:test4", 1, 800, 0)
    conv5 = create_mock_conversation_log("conv-005", "theme:test5", 4, 2000, 2)

    logger3.finish_conversation(conv4)
    logger3.finish_conversation(conv5)

    logger3.save_experiment_summary()

    print(f"✓ Session 3 completed: 2 conversations logged")

    # Read and display final metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    print(f"\nMetadata: {len(metadata)} sessions total")
    for session in metadata:
        print(f"\n  Session {session['session']}:")
        print(f"    - Conversations: {session['conversations_completed']}")
        print(f"    - Total tokens: {session['aggregate_stats']['total_tokens']}")
        print(f"    - Arbiter invocations: {session['aggregate_stats']['total_arbiter_invocations']}")
        print(f"    - Start: {session['start_time']}")
        print(f"    - End: {session['end_time']}")

    # Read and display final conversations_summary
    with open(summary_path, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    print(f"\nConversations summary: {len(summaries)} total conversations")
    print(f"Expected: 5 conversations (2 + 1 + 2)")

    # Verify correctness
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print(f"{'='*70}")

    success = True
    if len(metadata) != 3:
        print(f"❌ Expected 3 sessions, got {len(metadata)}")
        success = False
    else:
        print(f"✓ Correct number of sessions: 3")

    if len(summaries) != 5:
        print(f"❌ Expected 5 conversations, got {len(summaries)}")
        success = False
    else:
        print(f"✓ Correct number of conversations: 5")

    if success:
        print(f"\n✅ All tests passed! Append functionality working correctly.")
    else:
        print(f"\n❌ Tests failed!")

    print(f"\n📁 Test experiment directory: {exp_dir}")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = test_append_functionality()
    sys.exit(exit_code)
