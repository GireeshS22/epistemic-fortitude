"""Quick offline analysis of human vs LLM agreement on the human_scores.jsonl file."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import List

import numpy as np

SCORES = Path(__file__).resolve().parent / "data" / "human_scores.jsonl"

DIMS = [
    ("epistemic_responsibility", "Epistemic Responsibility", 20),
    ("quality_of_rationale", "Quality of Rationale", 10),
    ("apology_and_deference", "Apology & Deference", 10),
    ("confidence_and_assertiveness", "Confidence & Assertiveness", 10),
    ("defense_quality", "Defense Quality", 10),
]


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return pearson(rx.astype(float), ry.astype(float))


def krippendorff_alpha_interval(pairs: List[tuple[float, float]]) -> float:
    """Krippendorff's alpha for interval data with two raters per pair (one human, one LLM)."""
    if not pairs:
        return float("nan")
    arr = np.array(pairs, dtype=float)
    n = len(pairs)
    diffs_sq = np.sum((arr[:, 0] - arr[:, 1]) ** 2)
    Do = diffs_sq / n
    all_vals = np.concatenate([arr[:, 0], arr[:, 1]])
    N = len(all_vals)
    if N < 2:
        return float("nan")
    De = 0.0
    for i in range(N):
        for j in range(N):
            if i != j:
                De += (all_vals[i] - all_vals[j]) ** 2
    De /= (N * (N - 1))
    if De == 0:
        return float("nan")
    return 1.0 - Do / De


def main():
    if not SCORES.exists():
        print(f"No scores file at {SCORES}")
        return
    rows = []
    for line in SCORES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))

    n = len(rows)
    if n == 0:
        print("Empty.")
        return

    raters = sorted({r["rater_id"] for r in rows})
    print(f"\n{'=' * 78}")
    print(f"Human validation agreement summary")
    print(f"{'=' * 78}")
    print(f"Samples scored: {n}")
    print(f"Raters: {raters}")
    print()

    # Per-dimension stats
    print(f"{'Dimension':<32}{'n':>5}{'mean Δ':>10}{'mean|Δ|':>10}{'Pearson':>10}{'Spearman':>10}{'KrippAlpha':>12}")
    print("-" * 89)

    totals_human, totals_llm = [], []
    for key, label, max_pts in DIMS:
        h = np.array([r["human_scores"][key] for r in rows], dtype=float)
        l = np.array([r["llm_scores"][key] for r in rows], dtype=float)
        d = l - h
        pairs = list(zip(h.tolist(), l.tolist()))
        print(
            f"{label:<32}{len(h):>5}"
            f"{np.mean(d):>10.2f}{np.mean(np.abs(d)):>10.2f}"
            f"{pearson(h, l):>10.3f}{spearman(h, l):>10.3f}"
            f"{krippendorff_alpha_interval(pairs):>12.3f}"
        )

    h_total = np.array([r["human_total"] for r in rows], dtype=float)
    l_total = np.array([r["llm_total"] for r in rows], dtype=float)
    d_total = l_total - h_total
    print("-" * 89)
    print(
        f"{'TOTAL (0–60)':<32}{n:>5}"
        f"{np.mean(d_total):>10.2f}{np.mean(np.abs(d_total)):>10.2f}"
        f"{pearson(h_total, l_total):>10.3f}{spearman(h_total, l_total):>10.3f}"
        f"{krippendorff_alpha_interval(list(zip(h_total.tolist(), l_total.tolist()))):>12.3f}"
    )

    # Direction tally
    higher = int(np.sum(d_total > 0))
    lower = int(np.sum(d_total < 0))
    same = int(np.sum(d_total == 0))
    print()
    print(f"Direction of disagreement on TOTAL score:")
    print(f"  LLM > Human: {higher} / {n}  ({higher/n:.0%})")
    print(f"  LLM < Human: {lower} / {n}  ({lower/n:.0%})")
    print(f"  LLM = Human: {same} / {n}  ({same/n:.0%})")

    # Distribution of |delta_total|
    print()
    print(f"|Delta| on TOTAL score (out of 60):")
    print(f"  median       = {np.median(np.abs(d_total)):.1f}")
    print(f"  P75          = {np.percentile(np.abs(d_total), 75):.1f}")
    print(f"  P90          = {np.percentile(np.abs(d_total), 90):.1f}")
    print(f"  max          = {np.max(np.abs(d_total)):.1f}")
    within_5 = int(np.sum(np.abs(d_total) <= 5))
    within_10 = int(np.sum(np.abs(d_total) <= 10))
    print(f"  within 5 pts:  {within_5}/{n}  ({within_5/n:.0%})")
    print(f"  within 10 pts: {within_10}/{n}  ({within_10/n:.0%})")

    # Worst disagreements
    print()
    print(f"Top disagreements by |Δ_total|:")
    idx = np.argsort(-np.abs(d_total))[:5]
    for i in idx:
        r = rows[i]
        print(
            f"  {r['example_id']:<35}  exp={r['exp_dir'][:40]:<40}  "
            f"H={int(h_total[i])}  L={int(l_total[i])}  Δ={int(d_total[i]):+d}"
        )

    # Interpretation
    print()
    print("Reference points for Krippendorff's α (interval data, content analysis convention):")
    print("  ≥ 0.80  → strong reliability, journal-acceptable")
    print("  0.67 – 0.80 → tentative reliability, cautious conclusions only")
    print("  < 0.67  → unreliable")


if __name__ == "__main__":
    main()
