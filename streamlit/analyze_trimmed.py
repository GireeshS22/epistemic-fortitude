"""Compare full vs 90% trimmed agreement (drop top 10% by |delta_total|)."""
import json
import math
from pathlib import Path
import numpy as np

SCORES = Path(__file__).resolve().parent / "data" / "human_scores.jsonl"

DIMS = [
    ("epistemic_responsibility", "Epistemic Responsibility"),
    ("quality_of_rationale", "Quality of Rationale"),
    ("apology_and_deference", "Apology & Deference"),
    ("confidence_and_assertiveness", "Confidence & Assertiveness"),
    ("defense_quality", "Defense Quality"),
]


def alpha(pairs):
    if len(pairs) < 2:
        return float("nan")
    arr = np.array(pairs, dtype=float)
    n = len(arr)
    Do = np.sum((arr[:, 0] - arr[:, 1]) ** 2) / n
    flat = np.concatenate([arr[:, 0], arr[:, 1]])
    N = len(flat)
    De = sum(
        (flat[i] - flat[j]) ** 2
        for i in range(N) for j in range(N) if i != j
    ) / (N * (N - 1))
    return 1.0 - Do / De if De else float("nan")


def pearson(x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def block(label, rows):
    if not rows:
        print(f"\n{label}: empty")
        return
    print(f"\n{label}  (n={len(rows)})")
    print(f"{'Dimension':<32}{'mean Δ':>10}{'mean|Δ|':>10}{'Pearson':>10}{'KrippAlpha':>12}")
    print("-" * 74)
    for k, lbl in DIMS:
        h = np.array([r["human_scores"][k] for r in rows], dtype=float)
        l = np.array([r["llm_scores"][k] for r in rows], dtype=float)
        d = l - h
        pairs = list(zip(h.tolist(), l.tolist()))
        print(f"{lbl:<32}{np.mean(d):>10.2f}{np.mean(np.abs(d)):>10.2f}"
              f"{pearson(h, l):>10.3f}{alpha(pairs):>12.3f}")
    h = np.array([r["human_total"] for r in rows], dtype=float)
    l = np.array([r["llm_total"] for r in rows], dtype=float)
    d = l - h
    print("-" * 74)
    print(f"{'TOTAL (0–60)':<32}{np.mean(d):>10.2f}{np.mean(np.abs(d)):>10.2f}"
          f"{pearson(h, l):>10.3f}"
          f"{alpha(list(zip(h.tolist(), l.tolist()))):>12.3f}")
    within_5 = int(np.sum(np.abs(d) <= 5))
    within_10 = int(np.sum(np.abs(d) <= 10))
    print(f"  within 5 pts:  {within_5}/{len(rows)}  ({within_5/len(rows):.0%})")
    print(f"  within 10 pts: {within_10}/{len(rows)}  ({within_10/len(rows):.0%})")


rows = [json.loads(l) for l in SCORES.read_text(encoding="utf-8").splitlines() if l.strip()]
n = len(rows)

# Sort by |delta_total| descending and identify top 10% to drop
deltas_abs = [abs(r["llm_total"] - r["human_total"]) for r in rows]
n_drop = max(1, int(round(0.10 * n)))
sorted_idx = sorted(range(n), key=lambda i: deltas_abs[i], reverse=True)
drop_idx = set(sorted_idx[:n_drop])
kept = [r for i, r in enumerate(rows) if i not in drop_idx]
dropped = [r for i, r in enumerate(rows) if i in drop_idx]

print(f"Total samples: {n}")
print(f"Dropping top {n_drop} by |Δ_total| ({n_drop/n:.0%}):")
for r in sorted(dropped, key=lambda r: abs(r['llm_total']-r['human_total']), reverse=True):
    sc = "user-is-right" if r["user_is_right"] else "agent-is-right"
    print(f"  {r['example_id']:<35} ({sc:<14})  H={r['human_total']:>3}  L={r['llm_total']:>3}  Δ={r['llm_total']-r['human_total']:+d}")

block("FULL (n=47)", rows)
block("TRIMMED 90% (top 10% by |Δ| dropped)", kept)

# Scenario split on trimmed
print()
print("="*78)
print("Scenario split on TRIMMED data:")
agent_right = [r for r in kept if not r["user_is_right"]]
user_right = [r for r in kept if r["user_is_right"]]
block("AGENT IS RIGHT (trimmed)", agent_right)
block("USER IS RIGHT (trimmed)", user_right)
