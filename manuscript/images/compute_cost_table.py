"""Compute per-model cost / latency / token table for the R1 revision.

Walks the four model x two condition log directories, aggregates per-turn
token counts and latencies, and produces a markdown summary table plus the
underlying JSON for the manuscript.

Pricing: list prices as of experiment date (Oct 2025). Override via PRICING.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Iterable

LOGS_ROOT = Path(__file__).resolve().parents[2] / "logs" / "experiments"

# Map: family label -> (baseline_dir, arbiter_dir, primary_model, arbiter_model)
FAMILIES: list[tuple[str, str, str, str, str]] = [
    (
        "Gemini 2.5 Flash",
        "swebench_langgraph_baseline",
        "swebench_langgraph_arbiter",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ),
    (
        "GPT-5.1",
        "swebench_langgraph_gpt-5-1_baseline",
        "swebench_langgraph_gpt-5-1_arbiter",
        "gpt-5.1",
        "gpt-5.2",
    ),
    (
        "Claude Sonnet 4.5",
        "swebench_langgraph_claude-sonnet-4-5-20250929_baseline",
        "swebench_langgraph_claude-sonnet-4-5-20250929_arbiter",
        "claude-sonnet-4-5",
        "claude-opus-4-5",
    ),
    (
        "Llama 3.3 70B",
        "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_baseline",
        "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_arbiter",
        "llama-3.3-70b",
        "llama-3.3-70b",
    ),
]

# USD per 1M tokens. (input, output)
PRICING: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-pro": (1.25, 10.00),
    "gpt-5.1": (1.25, 10.00),
    "gpt-5.2": (5.00, 15.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-opus-4-5": (15.00, 25.00),
    "llama-3.3-70b": (0.88, 0.88),
}


def load_conversations(directory: Path) -> list[dict]:
    convs = []
    for path in sorted(directory.glob("*.json")):
        if path.name in {"conversations_summary.json"}:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                obj = json.load(f)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if "turns" not in obj:
            continue
        convs.append(obj)
    return convs


def cost_for_turn(turn: dict, model: str) -> float:
    if model not in PRICING:
        return 0.0
    in_price, out_price = PRICING[model]
    tc = turn.get("token_counts") or {}
    in_tok = tc.get("prompt_tokens", 0)
    out_tok = tc.get("completion_tokens", 0)
    return (in_tok * in_price + out_tok * out_price) / 1_000_000.0


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * pct
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def aggregate_condition(
    convs: list[dict],
    primary_model: str,
    arbiter_model: str,
    is_arbiter_cond: bool,
) -> dict:
    per_conv_tokens: list[int] = []
    per_conv_latency: list[float] = []
    per_conv_cost: list[float] = []
    per_turn_latency: list[float] = []
    per_turn_tokens: list[int] = []
    arbiter_calls = 0
    contradiction_turns = 0
    n_turns_total = 0

    for c in convs:
        conv_tok = 0
        conv_lat = 0.0
        conv_cost = 0.0
        for t in c.get("turns", []):
            n_turns_total += 1
            tc = t.get("token_counts") or {}
            tok = tc.get("total_tokens", 0)
            lat = t.get("latency_ms", 0.0)
            per_turn_latency.append(lat)
            per_turn_tokens.append(tok)
            conv_tok += tok
            conv_lat += lat
            routed = t.get("routed_to", "primary")
            is_contra = bool(t.get("is_contradiction", False))
            if is_contra:
                contradiction_turns += 1
            if is_arbiter_cond and routed == "arbiter":
                arbiter_calls += 1
                model = arbiter_model
            else:
                model = primary_model
            conv_cost += cost_for_turn(t, model)
        per_conv_tokens.append(conv_tok)
        per_conv_latency.append(conv_lat)
        per_conv_cost.append(conv_cost)

    n = len(convs)
    return {
        "n_conversations": n,
        "n_turns_total": n_turns_total,
        "n_contradiction_turns": contradiction_turns,
        "n_arbiter_calls": arbiter_calls,
        "arbiter_invocation_rate": (arbiter_calls / contradiction_turns) if contradiction_turns else 0.0,
        "tokens_per_conv_mean": statistics.mean(per_conv_tokens) if per_conv_tokens else 0,
        "tokens_per_conv_median": statistics.median(per_conv_tokens) if per_conv_tokens else 0,
        "tokens_per_conv_p95": percentile(per_conv_tokens, 0.95),
        "latency_per_conv_mean_ms": statistics.mean(per_conv_latency) if per_conv_latency else 0,
        "latency_per_conv_p50_ms": percentile(per_conv_latency, 0.50),
        "latency_per_conv_p95_ms": percentile(per_conv_latency, 0.95),
        "latency_per_turn_p50_ms": percentile(per_turn_latency, 0.50),
        "latency_per_turn_p95_ms": percentile(per_turn_latency, 0.95),
        "cost_per_conv_mean_usd": statistics.mean(per_conv_cost) if per_conv_cost else 0,
        "cost_per_100conv_usd": statistics.mean(per_conv_cost) * 100 if per_conv_cost else 0,
    }


def pct_delta(arb: float, base: float) -> float:
    if not base:
        return 0.0
    return (arb - base) / base * 100.0


def main() -> None:
    rows = []
    full = {}
    for label, base_dir, arb_dir, prim, arb in FAMILIES:
        bp = LOGS_ROOT / base_dir
        ap = LOGS_ROOT / arb_dir
        if not bp.exists() or not ap.exists():
            print(f"SKIP {label}: missing dir ({bp.exists()=}, {ap.exists()=})")
            continue
        base_convs = load_conversations(bp)
        arb_convs = load_conversations(ap)
        base = aggregate_condition(base_convs, prim, arb, is_arbiter_cond=False)
        arbi = aggregate_condition(arb_convs, prim, arb, is_arbiter_cond=True)
        rows.append((label, base, arbi))
        full[label] = {"baseline": base, "arbiter": arbi}

    # Markdown summary table
    print()
    print("## Per-conversation aggregates (n is conversation count)")
    print()
    print("| Model | Cond. | n | Tokens (mean) | Tokens (P95) | Latency P50 (s) | Latency P95 (s) | $ / 100 conv |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for label, base, arbi in rows:
        for cond_name, d in [("baseline", base), ("arbiter", arbi)]:
            print(
                f"| {label} | {cond_name} | {d['n_conversations']} "
                f"| {d['tokens_per_conv_mean']:.0f} | {d['tokens_per_conv_p95']:.0f} "
                f"| {d['latency_per_conv_p50_ms']/1000:.1f} | {d['latency_per_conv_p95_ms']/1000:.1f} "
                f"| ${d['cost_per_100conv_usd']:.2f} |"
            )

    print()
    print("## Overhead: arbiter vs baseline")
    print()
    print("| Model | Delta tokens | Delta latency (mean) | Delta cost | Arbiter invocation rate | n contradictions |")
    print("|---|---:|---:|---:|---:|---:|")
    for label, base, arbi in rows:
        d_tok = pct_delta(arbi["tokens_per_conv_mean"], base["tokens_per_conv_mean"])
        d_lat = pct_delta(arbi["latency_per_conv_mean_ms"], base["latency_per_conv_mean_ms"])
        d_cost = pct_delta(arbi["cost_per_100conv_usd"], base["cost_per_100conv_usd"])
        rate = arbi["arbiter_invocation_rate"] * 100
        print(
            f"| {label} | {d_tok:+.1f}% | {d_lat:+.1f}% | {d_cost:+.1f}% "
            f"| {rate:.1f}% | {arbi['n_contradiction_turns']} |"
        )

    print()
    print("## Per-turn latency (production-relevant)")
    print()
    print("| Model | Cond. | Turn P50 (s) | Turn P95 (s) |")
    print("|---|---|---:|---:|")
    for label, base, arbi in rows:
        for cond_name, d in [("baseline", base), ("arbiter", arbi)]:
            print(
                f"| {label} | {cond_name} | "
                f"{d['latency_per_turn_p50_ms']/1000:.1f} | {d['latency_per_turn_p95_ms']/1000:.1f} |"
            )

    out_path = Path(__file__).resolve().parent / "cost_table_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full, f, indent=2)
    print(f"\nFull data written to: {out_path}")


if __name__ == "__main__":
    main()
