"""Split agreement stats by scenario (Agent-is-Right vs User-is-Right)."""
import json
from pathlib import Path
import numpy as np

SCORES = Path(__file__).resolve().parent / "data" / "human_scores.jsonl"

rows = [json.loads(l) for l in SCORES.read_text(encoding="utf-8").splitlines() if l.strip()]


def alpha(pairs):
    if len(pairs) < 2:
        return float("nan")
    arr = np.array(pairs, dtype=float)
    n = len(pairs)
    Do = np.sum((arr[:, 0] - arr[:, 1]) ** 2) / n
    all_vals = np.concatenate([arr[:, 0], arr[:, 1]])
    N = len(all_vals)
    De = sum(
        (all_vals[i] - all_vals[j]) ** 2
        for i in range(N) for j in range(N) if i != j
    ) / (N * (N - 1))
    return 1.0 - Do / De if De else float("nan")


def stats(label, subset):
    if not subset:
        print(f"\n{label}: no samples")
        return
    h = np.array([r["human_total"] for r in subset], dtype=float)
    l = np.array([r["llm_total"] for r in subset], dtype=float)
    d = l - h
    pairs = list(zip(h.tolist(), l.tolist()))
    pearson = (
        float(np.corrcoef(h, l)[0, 1])
        if np.std(h) > 0 and np.std(l) > 0 else float("nan")
    )
    print(f"\n{label}  (n={len(subset)})")
    print(f"  Mean Δ    = {np.mean(d):+.2f}")
    print(f"  Mean |Δ|  = {np.mean(np.abs(d)):.2f}")
    print(f"  Pearson r = {pearson:.3f}")
    print(f"  Krippendorff α = {alpha(pairs):.3f}")
    print(f"  H mean={np.mean(h):.1f}, L mean={np.mean(l):.1f}")


agent_right = [r for r in rows if not r["user_is_right"]]
user_right = [r for r in rows if r["user_is_right"]]

stats("OVERALL", rows)
stats("AGENT IS RIGHT", agent_right)
stats("USER IS RIGHT", user_right)
