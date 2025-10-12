"""Compare baseline vs arbiter conditions on epistemic fortitude.

This script performs statistical comparison of maintenance ratios between:
- Baseline condition (ENABLE_ARBITER=false): Agent caves to contradictions
- Arbiter condition (ENABLE_ARBITER=true): Agent defends correct information
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from scipy import stats
import numpy as np


def load_scoring_summary(exp_dir: Path) -> Dict:
    """Load scoring summary from experiment."""
    summary_path = exp_dir / "scoring_summary.json"
    if not summary_path.exists():
        raise ValueError(f"Scoring summary not found: {summary_path}")

    with open(summary_path, 'r') as f:
        return json.load(f)


def calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
    """Calculate Cohen's d effect size.

    Interpretation:
    - < 0.2: negligible
    - 0.2-0.5: small
    - 0.5-0.8: medium
    - > 0.8: large
    """
    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    n1, n2 = len(group1), len(group2)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))

    if pooled_std == 0:
        return 0.0

    return (mean2 - mean1) / pooled_std


def interpret_effect_size(cohens_d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def interpret_pvalue(p: float) -> str:
    """Interpret p-value with significance markers."""
    if p < 0.001:
        return "*** (p < 0.001)"
    elif p < 0.01:
        return "** (p < 0.01)"
    elif p < 0.05:
        return "* (p < 0.05)"
    else:
        return "(not significant)"


def main():
    parser = argparse.ArgumentParser(
        description="Compare baseline vs arbiter epistemic fortitude"
    )
    parser.add_argument(
        "--baseline",
        required=True,
        help="Baseline experiment directory"
    )
    parser.add_argument(
        "--arbiter",
        required=True,
        help="Arbiter experiment directory"
    )
    parser.add_argument(
        "--output-dir",
        default="logs/comparisons",
        help="Output directory for comparison results"
    )
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"EPISTEMIC FORTITUDE COMPARISON")
    print(f"{'='*70}\n")

    # Load both scoring summaries
    print("Loading scoring summaries...")
    baseline_summary = load_scoring_summary(Path(args.baseline))
    arbiter_summary = load_scoring_summary(Path(args.arbiter))

    # Extract data
    baseline_convs = baseline_summary["scored_conversations"]
    arbiter_convs = arbiter_summary["scored_conversations"]

    baseline_ratios = [c["maintenance_ratio"] for c in baseline_convs]
    arbiter_ratios = [c["maintenance_ratio"] for c in arbiter_convs]

    baseline_orig_scores = [c["original_score"] for c in baseline_convs]
    arbiter_orig_scores = [c["original_score"] for c in arbiter_convs]

    baseline_contra_scores = [c["contradiction_score"] for c in baseline_convs]
    arbiter_contra_scores = [c["contradiction_score"] for c in arbiter_convs]

    print(f"✓ Baseline: {len(baseline_convs)} conversations")
    print(f"✓ Arbiter: {len(arbiter_convs)} conversations\n")

    # Statistical tests on maintenance ratios
    print("Running statistical tests...")
    t_stat, p_value = stats.ttest_ind(baseline_ratios, arbiter_ratios)
    cohens_d = calculate_cohens_d(baseline_ratios, arbiter_ratios)
    effect_interpretation = interpret_effect_size(cohens_d)
    p_interpretation = interpret_pvalue(p_value)

    # Additional tests
    mannwhitney_u, mannwhitney_p = stats.mannwhitneyu(
        baseline_ratios,
        arbiter_ratios,
        alternative='two-sided'
    )

    # Build comparison report
    comparison = {
        "metadata": {
            "comparison_date": datetime.now().isoformat(),
            "baseline_dir": args.baseline,
            "arbiter_dir": args.arbiter,
        },
        "baseline": {
            "experiment_dir": args.baseline,
            "arbiter_enabled": False,
            "n_conversations": len(baseline_ratios),
            "original_score": {
                "mean": float(np.mean(baseline_orig_scores)),
                "std": float(np.std(baseline_orig_scores, ddof=1)),
                "min": float(np.min(baseline_orig_scores)),
                "max": float(np.max(baseline_orig_scores)),
            },
            "contradiction_score": {
                "mean": float(np.mean(baseline_contra_scores)),
                "std": float(np.std(baseline_contra_scores, ddof=1)),
                "min": float(np.min(baseline_contra_scores)),
                "max": float(np.max(baseline_contra_scores)),
            },
            "maintenance_ratio": {
                "mean": float(np.mean(baseline_ratios)),
                "std": float(np.std(baseline_ratios, ddof=1)),
                "min": float(np.min(baseline_ratios)),
                "max": float(np.max(baseline_ratios)),
                "median": float(np.median(baseline_ratios)),
            },
        },
        "arbiter": {
            "experiment_dir": args.arbiter,
            "arbiter_enabled": True,
            "n_conversations": len(arbiter_ratios),
            "original_score": {
                "mean": float(np.mean(arbiter_orig_scores)),
                "std": float(np.std(arbiter_orig_scores, ddof=1)),
                "min": float(np.min(arbiter_orig_scores)),
                "max": float(np.max(arbiter_orig_scores)),
            },
            "contradiction_score": {
                "mean": float(np.mean(arbiter_contra_scores)),
                "std": float(np.std(arbiter_contra_scores, ddof=1)),
                "min": float(np.min(arbiter_contra_scores)),
                "max": float(np.max(arbiter_contra_scores)),
            },
            "maintenance_ratio": {
                "mean": float(np.mean(arbiter_ratios)),
                "std": float(np.std(arbiter_ratios, ddof=1)),
                "min": float(np.min(arbiter_ratios)),
                "max": float(np.max(arbiter_ratios)),
                "median": float(np.median(arbiter_ratios)),
            },
        },
        "statistical_tests": {
            "t_test": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant_at_0.05": bool(p_value < 0.05),
                "significant_at_0.01": bool(p_value < 0.01),
                "significant_at_0.001": bool(p_value < 0.001),
                "interpretation": p_interpretation,
            },
            "mann_whitney_u": {
                "u_statistic": float(mannwhitney_u),
                "p_value": float(mannwhitney_p),
                "significant_at_0.05": bool(mannwhitney_p < 0.05),
            },
            "effect_size": {
                "cohens_d": float(cohens_d),
                "interpretation": effect_interpretation,
            }
        },
        "interpretation": {
            "maintenance_ratio_difference": float(
                np.mean(arbiter_ratios) - np.mean(baseline_ratios)
            ),
            "percent_improvement": float(
                (np.mean(arbiter_ratios) - np.mean(baseline_ratios)) /
                np.mean(baseline_ratios) * 100
            ) if np.mean(baseline_ratios) > 0 else 0,
            "conclusion": (
                "The arbiter agent significantly improves epistemic fortitude" if p_value < 0.05
                else "No significant difference between conditions"
            )
        }
    }

    # Save comparison
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"baseline_vs_arbiter_{timestamp}.json"

    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)

    # Print results
    print(f"{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print("BASELINE (No Arbiter - Agent Caves to Contradictions):")
    print(f"  Original Score:      {comparison['baseline']['original_score']['mean']:.2f} ± {comparison['baseline']['original_score']['std']:.2f}")
    print(f"  Contradiction Score: {comparison['baseline']['contradiction_score']['mean']:.2f} ± {comparison['baseline']['contradiction_score']['std']:.2f}")
    print(f"  Maintenance Ratio:   {comparison['baseline']['maintenance_ratio']['mean']:.3f} ± {comparison['baseline']['maintenance_ratio']['std']:.3f}")
    print(f"  Range: [{comparison['baseline']['maintenance_ratio']['min']:.3f}, {comparison['baseline']['maintenance_ratio']['max']:.3f}]")

    print(f"\nARBITER (Epistemic Fortitude - Agent Defends Correct Info):")
    print(f"  Original Score:      {comparison['arbiter']['original_score']['mean']:.2f} ± {comparison['arbiter']['original_score']['std']:.2f}")
    print(f"  Contradiction Score: {comparison['arbiter']['contradiction_score']['mean']:.2f} ± {comparison['arbiter']['contradiction_score']['std']:.2f}")
    print(f"  Maintenance Ratio:   {comparison['arbiter']['maintenance_ratio']['mean']:.3f} ± {comparison['arbiter']['maintenance_ratio']['std']:.3f}")
    print(f"  Range: [{comparison['arbiter']['maintenance_ratio']['min']:.3f}, {comparison['arbiter']['maintenance_ratio']['max']:.3f}]")

    print(f"\nDIFFERENCE:")
    print(f"  Absolute: +{comparison['interpretation']['maintenance_ratio_difference']:.3f}")
    print(f"  Relative: +{comparison['interpretation']['percent_improvement']:.1f}%")

    print(f"\nSTATISTICAL TESTS:")
    print(f"  Independent t-test:")
    print(f"    t-statistic: {t_stat:.3f}")
    print(f"    p-value: {p_value:.6f} {p_interpretation}")
    print(f"  Mann-Whitney U test:")
    print(f"    U-statistic: {mannwhitney_u:.1f}")
    print(f"    p-value: {mannwhitney_p:.6f}")
    print(f"  Effect Size:")
    print(f"    Cohen's d: {cohens_d:.3f} ({effect_interpretation} effect)")

    print(f"\nCONCLUSION:")
    print(f"  {comparison['interpretation']['conclusion']}")

    print(f"\n{'='*70}")
    print(f"✅ Comparison saved to: {output_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
