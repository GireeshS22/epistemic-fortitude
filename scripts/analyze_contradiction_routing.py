"""Analyze contradiction routing in experiments.

This script analyzes all conversation logs to see which contradictions
were routed to which agent (arbiter_agent vs primary_agent).

Usage:
    poetry run python scripts/analyze_contradiction_routing.py
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def analyze_contradiction_routing(exp_dir):
    """Analyze contradiction routing from experiment logs.

    Args:
        exp_dir: Path to experiment directory

    Returns:
        Dict with analysis results
    """
    exp_path = Path(exp_dir)

    # Find all conversation JSON files (exclude metadata files)
    json_files = [
        f for f in exp_path.glob("*.json")
        if f.name not in ["metadata.json", "conversations_summary.json", "epistemic_summary.json", "errors.json"]
    ]

    print(f"\n{'='*70}")
    print(f"CONTRADICTION ROUTING ANALYSIS")
    print(f"{'='*70}")
    print(f"Found {len(json_files)} conversation files\n")

    # Track routing statistics
    stats = {
        "total_contradictions": 0,
        "routed_to_arbiter": 0,
        "routed_to_primary": 0,
        "by_tier": defaultdict(lambda: {"arbiter": 0, "primary": 0}),
        "by_mechanism": defaultdict(lambda: {"arbiter": 0, "primary": 0}),
        "misrouted_examples": [],
        "all_examples": []  # Store ALL contradictions for CSV
    }

    # Process each conversation
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)

            example_id = conversation.get("example_id", "unknown")

            # Find contradiction turns
            for turn in conversation.get("turns", []):
                if turn.get("is_contradiction", False):
                    stats["total_contradictions"] += 1

                    user_message = turn.get("user_message", "")
                    routed_to = turn.get("routed_to", "unknown")
                    tier = turn.get("contradiction_tier", "unknown")
                    mechanism = turn.get("contradiction_mechanism", "unknown")

                    # Store ALL examples for CSV
                    stats["all_examples"].append({
                        "example_id": example_id,
                        "message": user_message,  # Full message
                        "tier": tier,
                        "mechanism": mechanism,
                        "routed_to": routed_to
                    })

                    # Count routing
                    if routed_to == "arbiter_agent":
                        stats["routed_to_arbiter"] += 1
                        stats["by_tier"][tier]["arbiter"] += 1
                        stats["by_mechanism"][mechanism]["arbiter"] += 1
                    elif routed_to == "primary_agent":
                        stats["routed_to_primary"] += 1
                        stats["by_tier"][tier]["primary"] += 1
                        stats["by_mechanism"][mechanism]["primary"] += 1

                        # Record misrouted examples for display
                        stats["misrouted_examples"].append({
                            "example_id": example_id,
                            "message": user_message[:100],  # Truncate for display
                            "tier": tier,
                            "mechanism": mechanism
                        })

        except Exception as e:
            print(f"⚠️  Error processing {json_file.name}: {e}")

    return stats


def print_analysis(stats):
    """Print analysis results.

    Args:
        stats: Analysis statistics dict
    """
    total = stats["total_contradictions"]
    arbiter = stats["routed_to_arbiter"]
    primary = stats["routed_to_primary"]

    print(f"{'='*70}")
    print(f"OVERALL ROUTING")
    print(f"{'='*70}")
    print(f"Total contradictions: {total}")
    print(f"✓ Routed to arbiter_agent: {arbiter} ({arbiter/total*100:.1f}%)")
    print(f"✗ Routed to primary_agent: {primary} ({primary/total*100:.1f}%)")

    print(f"\n{'='*70}")
    print(f"ROUTING BY TIER")
    print(f"{'='*70}")
    for tier in sorted(stats["by_tier"].keys()):
        tier_stats = stats["by_tier"][tier]
        tier_total = tier_stats["arbiter"] + tier_stats["primary"]
        print(f"\nTier {tier}:")
        print(f"  Arbiter: {tier_stats['arbiter']}/{tier_total} ({tier_stats['arbiter']/tier_total*100:.1f}%)")
        print(f"  Primary: {tier_stats['primary']}/{tier_total} ({tier_stats['primary']/tier_total*100:.1f}%)")

    print(f"\n{'='*70}")
    print(f"ROUTING BY MECHANISM")
    print(f"{'='*70}")
    for mechanism in sorted(stats["by_mechanism"].keys()):
        mech_stats = stats["by_mechanism"][mechanism]
        mech_total = mech_stats["arbiter"] + mech_stats["primary"]
        print(f"\n{mechanism.capitalize()}:")
        print(f"  Arbiter: {mech_stats['arbiter']}/{mech_total} ({mech_stats['arbiter']/mech_total*100:.1f}%)")
        print(f"  Primary: {mech_stats['primary']}/{mech_total} ({mech_stats['primary']/mech_total*100:.1f}%)")

    if stats["misrouted_examples"]:
        print(f"\n{'='*70}")
        print(f"MISROUTED EXAMPLES (sent to primary_agent instead of arbiter)")
        print(f"{'='*70}")
        print(f"Total misrouted: {len(stats['misrouted_examples'])}\n")

        # Group by tier/mechanism
        by_category = defaultdict(list)
        for example in stats["misrouted_examples"]:
            key = f"Tier {example['tier']} ({example['mechanism']})"
            by_category[key].append(example)

        for category, examples in sorted(by_category.items()):
            print(f"\n{category}: {len(examples)} misrouted")
            for ex in examples[:3]:  # Show first 3 examples
                print(f"  • {ex['message'][:80]}...")
            if len(examples) > 3:
                print(f"  ... and {len(examples) - 3} more")


def save_csv_report(stats, output_path):
    """Save detailed CSV report with ALL contradictions.

    Args:
        stats: Analysis statistics dict
        output_path: Path to save CSV file
    """
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Example ID", "Contradiction Message", "Tier", "Mechanism", "Routed To Agent"])

        # Write ALL examples sorted by tier and mechanism
        sorted_examples = sorted(
            stats["all_examples"],
            key=lambda x: (x["tier"], x["mechanism"], x["routed_to"])
        )

        for ex in sorted_examples:
            writer.writerow([
                ex["example_id"],
                ex["message"],
                ex["tier"],
                ex["mechanism"],
                ex["routed_to"]
            ])

    print(f"\n📊 Detailed report saved to: {output_path}")
    print(f"   Total rows: {len(stats['all_examples'])}")


def main():
    """Main entry point."""
    # Path to experiment directory (default: SWE-bench arbiter)
    exp_dir = Path(__file__).parent.parent / "logs" / "experiments" / "swebench_langgraph_arbiter"

    if not exp_dir.exists():
        print(f"❌ Error: Experiment directory not found: {exp_dir}")
        return 1

    # Analyze routing
    stats = analyze_contradiction_routing(exp_dir)

    # Print results
    print_analysis(stats)

    # Save CSV report
    csv_path = exp_dir / "contradiction_routing_analysis.csv"
    save_csv_report(stats, csv_path)

    print(f"\n{'='*70}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
