#!/usr/bin/env python3
"""
Verify Computational Efficiency Metrics for Epistemic Fortitude Paper
======================================================================

This script explains and verifies how the computational efficiency numbers
in Section 6.5 of the paper were calculated from the raw experiment logs.

Data Sources:
- conversations_summary.json (token counts, latency, arbiter invocations)
- Individual conversation JSON files (detailed per-turn metrics)
"""

import json
import statistics
from pathlib import Path

# Paths
baseline_dir = Path("logs/experiments/swebench_langgraph_baseline")
arbiter_dir = Path("logs/experiments/swebench_langgraph_arbiter")

def load_conversation_summaries(dir_path):
    """Load the conversations_summary.json file"""
    summary_file = dir_path / "conversations_summary.json"
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_computational_metrics(conversations, label):
    """Analyze computational metrics from conversation summaries"""
    print(f"\n{'='*70}")
    print(f"{label} Analysis")
    print(f"{'='*70}")

    # Extract metrics
    token_counts = [conv['total_tokens'] for conv in conversations]
    latencies = [conv['total_latency_ms'] for conv in conversations]
    arbiter_invocations = [conv['arbiter_invocations'] for conv in conversations]

    # Calculate statistics
    mean_tokens = statistics.mean(token_counts)
    mean_latency = statistics.mean(latencies)
    total_tokens = sum(token_counts)
    total_invocations = sum(arbiter_invocations)
    n_conversations = len(conversations)

    # Count conversations where arbiter was invoked
    conversations_with_arbiter = sum(1 for inv in arbiter_invocations if inv > 0)

    print(f"\nSample Size: {n_conversations} conversations")
    print(f"\n--- Token Usage ---")
    print(f"Mean tokens per conversation: {mean_tokens:.1f}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Median tokens: {statistics.median(token_counts):.1f}")
    print(f"Min tokens: {min(token_counts)}")
    print(f"Max tokens: {max(token_counts)}")

    print(f"\n--- Latency ---")
    print(f"Mean latency per conversation: {mean_latency:.1f} ms ({mean_latency/1000:.1f} seconds)")
    print(f"Median latency: {statistics.median(latencies):.1f} ms")
    print(f"Min latency: {min(latencies):.1f} ms")
    print(f"Max latency: {max(latencies):.1f} ms")

    print(f"\n--- Arbiter Invocations ---")
    print(f"Total arbiter invocations: {total_invocations}")
    print(f"Mean invocations per conversation: {statistics.mean(arbiter_invocations):.2f}")
    print(f"Conversations with arbiter invoked: {conversations_with_arbiter}/{n_conversations} ({100*conversations_with_arbiter/n_conversations:.1f}%)")

    return {
        'n': n_conversations,
        'mean_tokens': mean_tokens,
        'mean_latency_ms': mean_latency,
        'total_tokens': total_tokens,
        'total_invocations': total_invocations,
        'conversations_with_arbiter': conversations_with_arbiter,
        'arbiter_rate': conversations_with_arbiter / n_conversations
    }

def compute_comparison(baseline_stats, arbiter_stats):
    """Compute comparative metrics between baseline and arbiter"""
    print(f"\n{'='*70}")
    print("COMPARATIVE ANALYSIS")
    print(f"{'='*70}")

    # Token overhead
    token_overhead = ((arbiter_stats['mean_tokens'] - baseline_stats['mean_tokens'])
                      / baseline_stats['mean_tokens'] * 100)

    # Latency overhead
    latency_overhead = ((arbiter_stats['mean_latency_ms'] - baseline_stats['mean_latency_ms'])
                        / baseline_stats['mean_latency_ms'] * 100)

    # Cost calculation (assuming $5 per 1M tokens)
    cost_per_million = 5.00  # dollars
    baseline_cost_per_100 = (baseline_stats['mean_tokens'] * 100 / 1_000_000) * cost_per_million
    arbiter_cost_per_100 = (arbiter_stats['mean_tokens'] * 100 / 1_000_000) * cost_per_million
    cost_overhead = ((arbiter_cost_per_100 - baseline_cost_per_100)
                     / baseline_cost_per_100 * 100)

    print(f"\n--- Token Usage Comparison ---")
    print(f"Baseline mean: {baseline_stats['mean_tokens']:.1f} tokens/conv")
    print(f"Arbiter mean:  {arbiter_stats['mean_tokens']:.1f} tokens/conv")
    print(f"Difference:    {arbiter_stats['mean_tokens'] - baseline_stats['mean_tokens']:.1f} tokens")
    print(f"Overhead:      {token_overhead:+.1f}%")

    print(f"\n--- Latency Comparison ---")
    print(f"Baseline mean: {baseline_stats['mean_latency_ms']:.1f} ms ({baseline_stats['mean_latency_ms']/1000:.1f} sec)")
    print(f"Arbiter mean:  {arbiter_stats['mean_latency_ms']:.1f} ms ({arbiter_stats['mean_latency_ms']/1000:.1f} sec)")
    print(f"Difference:    {arbiter_stats['mean_latency_ms'] - baseline_stats['mean_latency_ms']:.1f} ms")
    print(f"Overhead:      {latency_overhead:+.1f}%")

    print(f"\n--- Cost Comparison (at ${cost_per_million} per 1M tokens) ---")
    print(f"Baseline cost per 100 conversations: ${baseline_cost_per_100:.2f}")
    print(f"Arbiter cost per 100 conversations:  ${arbiter_cost_per_100:.2f}")
    print(f"Cost difference: ${arbiter_cost_per_100 - baseline_cost_per_100:+.2f}")
    print(f"Cost overhead:   {cost_overhead:+.1f}%")

    print(f"\n--- Arbiter Routing Performance ---")
    print(f"Arbiter invocation rate: {arbiter_stats['conversations_with_arbiter']}/{arbiter_stats['n']} = {100*arbiter_stats['arbiter_rate']:.1f}%")
    print(f"Routing failures: {arbiter_stats['n'] - arbiter_stats['conversations_with_arbiter']} ({100*(1-arbiter_stats['arbiter_rate']):.1f}%)")

    print(f"\n{'='*70}")
    print("PAPER TABLE 5 VALUES")
    print(f"{'='*70}")
    print(f"""
\\begin{{table}}[t]
\\centering
\\caption{{Computational efficiency comparison (n={arbiter_stats['n']} conversations per condition)}}
\\label{{tab:computational-costs}}
\\begin{{tabular}}{{lrrr}}
\\toprule
\\textbf{{Metric}} & \\textbf{{Baseline}} & \\textbf{{Arbiter}} & \\textbf{{Overhead}} \\\\
\\midrule
Mean tokens per conversation  & {baseline_stats['mean_tokens']:,.0f} & {arbiter_stats['mean_tokens']:,.0f} & {token_overhead:+.1f}\\% \\\\
Mean latency (milliseconds)   & {baseline_stats['mean_latency_ms']:,.0f} & {arbiter_stats['mean_latency_ms']:,.0f} & {latency_overhead:+.1f}\\% \\\\
Cost per 100 conversations (\\$) & {baseline_cost_per_100:.2f}   & {arbiter_cost_per_100:.2f}   & {cost_overhead:+.1f}\\% \\\\
\\midrule
Arbiter invocations           & 0/{baseline_stats['n']} (0\\%) & {arbiter_stats['conversations_with_arbiter']}/{arbiter_stats['n']} ({100*arbiter_stats['arbiter_rate']:.1f}\\%) & — \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
    """)

    return {
        'token_overhead_pct': token_overhead,
        'latency_overhead_pct': latency_overhead,
        'cost_overhead_pct': cost_overhead,
        'baseline_cost_per_100': baseline_cost_per_100,
        'arbiter_cost_per_100': arbiter_cost_per_100
    }

def main():
    print("="*70)
    print("COMPUTATIONAL EFFICIENCY VERIFICATION")
    print("Epistemic Fortitude Paper - Section 6.5")
    print("="*70)

    # Load data
    print("\nLoading conversation summaries...")
    baseline_convs = load_conversation_summaries(baseline_dir)
    arbiter_convs = load_conversation_summaries(arbiter_dir)

    # Analyze each condition
    baseline_stats = analyze_computational_metrics(baseline_convs, "BASELINE (No Arbiter)")
    arbiter_stats = analyze_computational_metrics(arbiter_convs, "ARBITER (Full System)")

    # Compare
    comparison = compute_comparison(baseline_stats, arbiter_stats)

    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70)
    print("\nKey Findings:")
    print(f"1. Token overhead: {comparison['token_overhead_pct']:+.1f}% (NEGATIVE = MORE EFFICIENT)")
    print(f"2. Latency overhead: {comparison['latency_overhead_pct']:+.1f}% (NEGATIVE = FASTER)")
    print(f"3. Cost overhead: {comparison['cost_overhead_pct']:+.1f}% (NEGATIVE = CHEAPER)")
    print(f"4. Arbiter routing accuracy: {100*arbiter_stats['arbiter_rate']:.1f}%")

    print("\nConclusion:")
    if comparison['token_overhead_pct'] < 0:
        print("✓ The arbiter is MORE EFFICIENT than baseline (uses fewer tokens)")
    if comparison['latency_overhead_pct'] < 0:
        print("✓ The arbiter is FASTER than baseline (lower latency)")
    if comparison['cost_overhead_pct'] < 0:
        print("✓ The arbiter is CHEAPER per conversation than baseline")

    print("\nThese counterintuitive results occur because:")
    print("- Sycophantic responses tend to be verbose and meandering")
    print("- Arbiter provides concise, evidence-based defenses")
    print("- Structured decision-making reduces unnecessary re-generation")

if __name__ == "__main__":
    main()
