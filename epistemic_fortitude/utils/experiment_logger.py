"""Experiment logger for capturing HealthBench conversation data.

This module provides structured logging for experiments, capturing:
- Conversation turns with full messages
- Agent routing decisions
- Token counts and latency
- Metadata for analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExperimentLogger:
    """Logger for capturing experiment data in structured format.

    Each conversation is logged with:
    - Metadata (example_id, arbiter_enabled, theme, etc.)
    - Turn-by-turn data (user messages, agent responses, routing, timing)
    - Aggregate metrics (total tokens, latency, arbiter invocations)
    """

    def __init__(
        self,
        experiment_id: str,
        arbiter_enabled: bool,
        output_dir: str = "logs/experiments"
    ):
        """Initialize the experiment logger.

        Args:
            experiment_id: Unique ID for this experiment run
            arbiter_enabled: Whether arbiter agent is enabled
            output_dir: Directory to save log files
        """
        self.experiment_id = experiment_id
        self.arbiter_enabled = arbiter_enabled
        self.output_dir = Path(output_dir)

        # Create experiment directory (flat structure, no subfolders)
        self.exp_dir = self.output_dir / experiment_id
        self.exp_dir.mkdir(parents=True, exist_ok=True)

        # Track conversations
        self.conversation_logs: List[Dict[str, Any]] = []

        # Metadata
        self.metadata = {
            "experiment_id": experiment_id,
            "arbiter_enabled": arbiter_enabled,
            "start_time": datetime.now().isoformat(),
            "conversations_completed": 0,
        }

    def start_conversation(
        self,
        example_id: str,
        theme: str,
        tags: List[str],
        rubrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Start logging a new conversation.

        Args:
            example_id: HealthBench example ID
            theme: Example theme (e.g., "context_seeking")
            tags: Example tags
            rubrics: Rubric criteria for this example

        Returns:
            Conversation log dict to populate
        """
        conversation_log = {
            "example_id": example_id,
            "arbiter_enabled": self.arbiter_enabled,
            "theme": theme,
            "tags": tags,
            "num_rubrics": len(rubrics),
            "rubrics": rubrics,
            "start_time": datetime.now().isoformat(),
            "turns": [],
            "total_latency_ms": 0,
            "total_tokens": 0,
            "arbiter_invocations": 0,
        }

        return conversation_log

    def log_turn(
        self,
        conversation_log: Dict[str, Any],
        turn_number: int,
        user_message: str,
        agent_response: str,
        routed_to: str,
        events: List[Any],
        latency_ms: float,
        token_counts: Optional[Dict[str, int]] = None,
        is_contradiction: bool = False,
        contradiction_prompt: Optional[str] = None,
        contradiction_tier: Optional[int] = None,
        contradiction_mechanism: Optional[str] = None
    ):
        """Log a single conversation turn.

        Args:
            conversation_log: The conversation log dict
            turn_number: Turn number (1-indexed)
            user_message: User's message
            agent_response: Agent's response
            routed_to: Which agent handled this (primary_agent/arbiter_agent)
            events: List of ADK events from this turn
            latency_ms: Response latency in milliseconds
            token_counts: Dict with prompt_tokens, completion_tokens, total_tokens
            is_contradiction: Whether this is an injected contradiction turn
            contradiction_prompt: The contradiction phrase used (if is_contradiction=True)
            contradiction_tier: Tier of contradiction (1-4, if is_contradiction=True)
            contradiction_mechanism: Mechanism type (authority/evidence/emotion/logic, if is_contradiction=True)
        """
        turn_log = {
            "turn_number": turn_number,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "user_message_length": len(user_message),
            "agent_response": agent_response,
            "agent_response_length": len(agent_response),
            "routed_to": routed_to,
            "latency_ms": latency_ms,
            "num_events": len(events),
            "is_contradiction": is_contradiction,
        }

        # Add contradiction metadata if this is a contradiction turn
        if is_contradiction and contradiction_prompt:
            turn_log["contradiction_prompt"] = contradiction_prompt
            if contradiction_tier is not None:
                turn_log["contradiction_tier"] = contradiction_tier
            if contradiction_mechanism is not None:
                turn_log["contradiction_mechanism"] = contradiction_mechanism

        # Add token counts if available
        if token_counts:
            turn_log["token_counts"] = token_counts
            conversation_log["total_tokens"] += token_counts.get("total_tokens", 0)

        # Track arbiter invocations
        if routed_to == "arbiter_agent":
            conversation_log["arbiter_invocations"] += 1

        # Update totals
        conversation_log["total_latency_ms"] += latency_ms
        conversation_log["turns"].append(turn_log)

    def finish_conversation(
        self,
        conversation_log: Dict[str, Any]
    ) -> str:
        """Finish logging a conversation and save to file.

        Args:
            conversation_log: The completed conversation log

        Returns:
            Path to the saved conversation log file
        """
        conversation_log["end_time"] = datetime.now().isoformat()
        conversation_log["total_turns"] = len(conversation_log["turns"])

        # Calculate averages
        if conversation_log["total_turns"] > 0:
            conversation_log["avg_latency_ms"] = (
                conversation_log["total_latency_ms"] / conversation_log["total_turns"]
            )
            conversation_log["avg_tokens_per_turn"] = (
                conversation_log["total_tokens"] / conversation_log["total_turns"]
            )

        # Save to individual file (flat structure)
        filename = f"{conversation_log['example_id']}.json"
        filepath = self.exp_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_log, f, indent=2, ensure_ascii=False)

        # Add to list
        self.conversation_logs.append(conversation_log)
        self.metadata["conversations_completed"] += 1

        return str(filepath)

    def save_experiment_summary(self):
        """Save experiment-level summary and metadata."""

        # Calculate aggregate statistics for this session
        end_time = datetime.now().isoformat()
        total_conversations = len(self.conversation_logs)

        aggregate_stats = {}
        if self.conversation_logs:
            total_turns = sum(c["total_turns"] for c in self.conversation_logs)
            total_tokens = sum(c["total_tokens"] for c in self.conversation_logs)
            total_arbiter_invocations = sum(
                c["arbiter_invocations"] for c in self.conversation_logs
            )

            aggregate_stats = {
                "total_turns": total_turns,
                "total_tokens": total_tokens,
                "total_arbiter_invocations": total_arbiter_invocations,
                "arbiter_invocation_rate": (
                    total_arbiter_invocations / total_turns * 100
                    if total_turns > 0 else 0
                ),
                "avg_tokens_per_conversation": (
                    total_tokens / len(self.conversation_logs)
                ),
            }

        # Load existing metadata sessions or create new list
        metadata_path = self.exp_dir / "metadata.json"
        sessions = []
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    # Handle both old format (dict) and new format (list)
                    if isinstance(existing_data, list):
                        sessions = existing_data
                    elif isinstance(existing_data, dict):
                        # Convert old format to new format as session 1
                        sessions = [existing_data]
            except (json.JSONDecodeError, IOError):
                sessions = []

        # Create new session entry
        session_number = len(sessions) + 1
        new_session = {
            "session": session_number,
            "experiment_id": self.experiment_id,
            "arbiter_enabled": self.arbiter_enabled,
            "start_time": self.metadata["start_time"],
            "end_time": end_time,
            "conversations_completed": total_conversations,
            "aggregate_stats": aggregate_stats
        }

        # Append new session
        sessions.append(new_session)

        # Save updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)

        # Load existing conversation summaries or create new list
        summary_path = self.exp_dir / "conversations_summary.json"
        all_summaries = []
        if summary_path.exists():
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    all_summaries = json.load(f)
            except (json.JSONDecodeError, IOError):
                all_summaries = []

        # Create summaries for new conversations
        new_summaries = [
            {
                "example_id": c["example_id"],
                "theme": c["theme"],
                "total_turns": c["total_turns"],
                "total_tokens": c["total_tokens"],
                "arbiter_invocations": c["arbiter_invocations"],
                "total_latency_ms": c["total_latency_ms"],
            }
            for c in self.conversation_logs
        ]

        # Append new summaries
        all_summaries.extend(new_summaries)

        # Save updated conversation summaries
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(all_summaries, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Experiment summary saved:")
        print(f"   - Metadata: {metadata_path} (Session {session_number})")
        print(f"   - Summary: {summary_path} ({len(all_summaries)} total conversations)")
        print(f"   - New conversations: {len(self.conversation_logs)} files")

        return str(self.exp_dir)

    def get_experiment_dir(self) -> str:
        """Get the experiment directory path."""
        return str(self.exp_dir)
