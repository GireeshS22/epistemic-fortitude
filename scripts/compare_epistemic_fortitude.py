"""Compare epistemic fortitude between baseline and arbiter conditions.

This script performs statistical comparison of epistemic fortitude scores:
- Baseline condition (ENABLE_ARBITER=false): Agent caves to contradictions
- Arbiter condition (ENABLE_ARBITER=true): Agent defends correct information
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from scipy import stats
import numpy as np


def load_epistemic_summary(exp_dir: Path) -> Dict:
    """Load epistemic fortitude summary from experiment."""
    summary_path = exp_dir / "epistemic_summary.json"
    if not summary_path.exists():
        raise ValueError(f"Epistemic summary not found: {summary_path}")

    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
    """Calculate Cohen's d effect size."""
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
        description="Compare epistemic fortitude between baseline and arbiter"
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

    # Load both summaries
    print("Loading epistemic fortitude summaries...")
    baseline_summary = load_epistemic_summary(Path(args.baseline))
    arbiter_summary = load_epistemic_summary(Path(args.arbiter))

    # Extract scores
    baseline_convs = baseline_summary["scored_conversations"]
    arbiter_convs = arbiter_summary["scored_conversations"]

    baseline_total = [c["scores"]["total_epistemic_fortitude"] for c in baseline_convs]
    arbiter_total = [c["scores"]["total_epistemic_fortitude"] for c in arbiter_convs]

    baseline_responsibility = [c["scores"]["epistemic_responsibility"] for c in baseline_convs]
    arbiter_responsibility = [c["scores"]["epistemic_responsibility"] for c in arbiter_convs]

    baseline_rationale = [c["scores"]["quality_of_rationale"] for c in baseline_convs]
    arbiter_rationale = [c["scores"]["quality_of_rationale"] for c in arbiter_convs]

    baseline_apology = [c["scores"]["apology_and_deference"] for c in baseline_convs]
    arbiter_apology = [c["scores"]["apology_and_deference"] for c in arbiter_convs]

    baseline_confidence = [c["scores"]["confidence_and_assertiveness"] for c in baseline_convs]
    arbiter_confidence = [c["scores"]["confidence_and_assertiveness"] for c in arbiter_convs]

    baseline_defense = [c["scores"]["defense_quality"] for c in baseline_convs]
    arbiter_defense = [c["scores"]["defense_quality"] for c in arbiter_convs]

    print(f"[OK] Baseline: {len(baseline_convs)} conversations")
    print(f"[OK] Arbiter: {len(arbiter_convs)} conversations\n")

    # Statistical tests on total epistemic fortitude
    print("Running statistical tests...")
    t_stat, p_value = stats.ttest_ind(baseline_total, arbiter_total)
    cohens_d = calculate_cohens_d(baseline_total, arbiter_total)
    effect_interpretation = interpret_effect_size(cohens_d)
    p_interpretation = interpret_pvalue(p_value)

    # Additional test
    mannwhitney_u, mannwhitney_p = stats.mannwhitneyu(
        baseline_total,
        arbiter_total,
        alternative='two-sided'
    )

    # Statistical tests per dimension
    dimension_tests = {}
    for dim_name, baseline_scores, arbiter_scores in [
        ("epistemic_responsibility", baseline_responsibility, arbiter_responsibility),
        ("quality_of_rationale", baseline_rationale, arbiter_rationale),
        ("apology_and_deference", baseline_apology, arbiter_apology),
        ("confidence_and_assertiveness", baseline_confidence, arbiter_confidence),
        ("defense_quality", baseline_defense, arbiter_defense)
    ]:
        t, p = stats.ttest_ind(baseline_scores, arbiter_scores)
        d = calculate_cohens_d(baseline_scores, arbiter_scores)
        dimension_tests[dim_name] = {
            "t_statistic": float(t),
            "p_value": float(p),
            "cohens_d": float(d),
            "significant": bool(p < 0.05)
        }

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
            "n_conversations": len(baseline_total),
            "total_epistemic_fortitude": {
                "mean": float(np.mean(baseline_total)),
                "std": float(np.std(baseline_total, ddof=1)),
                "min": float(np.min(baseline_total)),
                "max": float(np.max(baseline_total)),
                "median": float(np.median(baseline_total)),
            },
            "epistemic_responsibility": {
                "mean": float(np.mean(baseline_responsibility)),
                "std": float(np.std(baseline_responsibility, ddof=1)),
            },
            "quality_of_rationale": {
                "mean": float(np.mean(baseline_rationale)),
                "std": float(np.std(baseline_rationale, ddof=1)),
            },
            "apology_and_deference": {
                "mean": float(np.mean(baseline_apology)),
                "std": float(np.std(baseline_apology, ddof=1)),
            },
            "confidence_and_assertiveness": {
                "mean": float(np.mean(baseline_confidence)),
                "std": float(np.std(baseline_confidence, ddof=1)),
            },
            "defense_quality": {
                "mean": float(np.mean(baseline_defense)),
                "std": float(np.std(baseline_defense, ddof=1)),
            },
        },
        "arbiter": {
            "experiment_dir": args.arbiter,
            "arbiter_enabled": True,
            "n_conversations": len(arbiter_total),
            "total_epistemic_fortitude": {
                "mean": float(np.mean(arbiter_total)),
                "std": float(np.std(arbiter_total, ddof=1)),
                "min": float(np.min(arbiter_total)),
                "max": float(np.max(arbiter_total)),
                "median": float(np.median(arbiter_total)),
            },
            "epistemic_responsibility": {
                "mean": float(np.mean(arbiter_responsibility)),
                "std": float(np.std(arbiter_responsibility, ddof=1)),
            },
            "quality_of_rationale": {
                "mean": float(np.mean(arbiter_rationale)),
                "std": float(np.std(arbiter_rationale, ddof=1)),
            },
            "apology_and_deference": {
                "mean": float(np.mean(arbiter_apology)),
                "std": float(np.std(arbiter_apology, ddof=1)),
            },
            "confidence_and_assertiveness": {
                "mean": float(np.mean(arbiter_confidence)),
                "std": float(np.std(arbiter_confidence, ddof=1)),
            },
            "defense_quality": {
                "mean": float(np.mean(arbiter_defense)),
                "std": float(np.std(arbiter_defense, ddof=1)),
            },
        },
        "statistical_tests": {
            "total_epistemic_fortitude": {
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
            "per_dimension": dimension_tests
        },
        "interpretation": {
            "absolute_difference": float(np.mean(arbiter_total) - np.mean(baseline_total)),
            "percent_improvement": float(
                (np.mean(arbiter_total) - np.mean(baseline_total)) /
                np.mean(baseline_total) * 100
            ) if np.mean(baseline_total) > 0 else 0,
            "conclusion": (
                "The arbiter agent significantly improves epistemic fortitude" if p_value < 0.05
                else "No significant difference in epistemic fortitude between conditions"
            )
        }
    }

    # Save comparison
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"epistemic_fortitude_comparison_{timestamp}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)

    # Print results
    print(f"{'='*70}")
    print("RESULTS - TOTAL EPISTEMIC FORTITUDE (out of 60)")
    print(f"{'='*70}\n")

    print("BASELINE (No Arbiter - Expected to cave to contradictions):")
    print(f"  Total Score: {comparison['baseline']['total_epistemic_fortitude']['mean']:.2f} ± {comparison['baseline']['total_epistemic_fortitude']['std']:.2f} (out of 60)")
    print(f"  - Epistemic Responsibility (0-20):     {comparison['baseline']['epistemic_responsibility']['mean']:.2f} ± {comparison['baseline']['epistemic_responsibility']['std']:.2f}")
    print(f"  - Quality of Rationale (0-10):         {comparison['baseline']['quality_of_rationale']['mean']:.2f} ± {comparison['baseline']['quality_of_rationale']['std']:.2f}")
    print(f"  - Apology & Deference (0-10):          {comparison['baseline']['apology_and_deference']['mean']:.2f} ± {comparison['baseline']['apology_and_deference']['std']:.2f}")
    print(f"  - Confidence & Assertiveness (0-10):   {comparison['baseline']['confidence_and_assertiveness']['mean']:.2f} ± {comparison['baseline']['confidence_and_assertiveness']['std']:.2f}")
    print(f"  - Defense Quality (0-10):              {comparison['baseline']['defense_quality']['mean']:.2f} ± {comparison['baseline']['defense_quality']['std']:.2f}")

    print(f"\nARBITER (Epistemic Fortitude - Expected to defend correct info):")
    print(f"  Total Score: {comparison['arbiter']['total_epistemic_fortitude']['mean']:.2f} ± {comparison['arbiter']['total_epistemic_fortitude']['std']:.2f} (out of 60)")
    print(f"  - Epistemic Responsibility (0-20):     {comparison['arbiter']['epistemic_responsibility']['mean']:.2f} ± {comparison['arbiter']['epistemic_responsibility']['std']:.2f}")
    print(f"  - Quality of Rationale (0-10):         {comparison['arbiter']['quality_of_rationale']['mean']:.2f} ± {comparison['arbiter']['quality_of_rationale']['std']:.2f}")
    print(f"  - Apology & Deference (0-10):          {comparison['arbiter']['apology_and_deference']['mean']:.2f} ± {comparison['arbiter']['apology_and_deference']['std']:.2f}")
    print(f"  - Confidence & Assertiveness (0-10):   {comparison['arbiter']['confidence_and_assertiveness']['mean']:.2f} ± {comparison['arbiter']['confidence_and_assertiveness']['std']:.2f}")
    print(f"  - Defense Quality (0-10):              {comparison['arbiter']['defense_quality']['mean']:.2f} ± {comparison['arbiter']['defense_quality']['std']:.2f}")

    print(f"\nDIFFERENCE:")
    print(f"  Absolute: {'+' if comparison['interpretation']['absolute_difference'] > 0 else ''}{comparison['interpretation']['absolute_difference']:.2f} points")
    print(f"  Relative: {'+' if comparison['interpretation']['percent_improvement'] > 0 else ''}{comparison['interpretation']['percent_improvement']:.1f}%")

    print(f"\nSTATISTICAL TESTS (Total Epistemic Fortitude):")
    print(f"  Independent t-test:")
    print(f"    t-statistic: {t_stat:.3f}")
    print(f"    p-value: {p_value:.6f} {p_interpretation}")
    print(f"  Mann-Whitney U test:")
    print(f"    U-statistic: {mannwhitney_u:.1f}")
    print(f"    p-value: {mannwhitney_p:.6f}")
    print(f"  Effect Size:")
    print(f"    Cohen's d: {cohens_d:.3f} ({effect_interpretation} effect)")

    print(f"\nPER-DIMENSION ANALYSIS:")
    for dim, tests in dimension_tests.items():
        sig_marker = "*" if tests["significant"] else " "
        print(f"  {dim.replace('_', ' ').title()}:")
        print(f"    {sig_marker} p={tests['p_value']:.4f}, d={tests['cohens_d']:.3f}")

    print(f"\nCONCLUSION:")
    print(f"  {comparison['interpretation']['conclusion']}")

    print(f"\n{'='*70}")
    print(f"[OK] Comparison saved to: {output_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
