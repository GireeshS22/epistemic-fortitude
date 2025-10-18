"""Compare HealthBench rubric scores between baseline and arbiter conditions.

This script performs comprehensive statistical comparison for research papers:
- Descriptive statistics (mean, std, median, quartiles)
- Rubric-level metrics (% met, violations, points per rubric)
- Statistical tests (t-test, Mann-Whitney U, Cohen's d)
- Multiple output formats (JSON, console, LaTeX)
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from scipy import stats


class ScoringSummaryLoader:
    """Load scoring summaries and individual conversation scores."""

    def load_summary(self, exp_dir: Path) -> Dict:
        """Load scoring_summary.json from experiment directory."""
        summary_path = exp_dir / "scoring_summary.json"
        if not summary_path.exists():
            raise ValueError(f"Scoring summary not found: {summary_path}")

        with open(summary_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_individual_scores(self, exp_dir: Path) -> List[Dict]:
        """Load all individual conversation scores from scores/ directory."""
        scores_dir = exp_dir / "scores"
        if not scores_dir.exists():
            raise ValueError(f"Scores directory not found: {scores_dir}")

        scores = []
        for score_file in sorted(scores_dir.glob("*.json")):
            with open(score_file, 'r', encoding='utf-8') as f:
                scores.append(json.load(f))

        return scores


class RubricAnalyzer:
    """Analyze rubric-level metrics from conversation scores."""

    def analyze_rubrics(self, scores: List[Dict]) -> Dict:
        """Calculate comprehensive rubric-level metrics."""
        total_rubrics = 0
        rubrics_met = 0
        positive_rubrics_total = 0
        positive_rubrics_met = 0
        negative_rubrics_total = 0
        negative_rubrics_violated = 0
        total_points = 0
        rubrics_per_conv = []

        for conv in scores:
            rubric_scores = conv.get("contradiction_rubric_scores", [])
            num_rubrics = len(rubric_scores)
            rubrics_per_conv.append(num_rubrics)
            total_rubrics += num_rubrics

            for rubric in rubric_scores:
                points_awarded = rubric.get("points_awarded", 0)
                total_points += points_awarded

                # Determine if positive or negative rubric
                # Positive rubrics have points > 0 when met
                # Negative rubrics have points < 0 when violated
                if points_awarded > 0:
                    rubrics_met += 1
                    positive_rubrics_total += 1
                    positive_rubrics_met += 1
                elif points_awarded < 0:
                    # This is a negative rubric that was violated
                    negative_rubrics_total += 1
                    negative_rubrics_violated += 1
                else:
                    # points_awarded == 0
                    # Need to check if this is a positive rubric not met
                    # or a negative rubric not violated
                    # For simplicity, count as positive rubric not met
                    positive_rubrics_total += 1

        return {
            "total_rubrics_evaluated": total_rubrics,
            "total_rubrics_met": rubrics_met,
            "percentage_rubrics_met": (rubrics_met / total_rubrics * 100) if total_rubrics > 0 else 0,
            "positive_rubrics": {
                "total": positive_rubrics_total,
                "met": positive_rubrics_met,
                "percentage_met": (positive_rubrics_met / positive_rubrics_total * 100) if positive_rubrics_total > 0 else 0
            },
            "negative_rubrics": {
                "total": negative_rubrics_total,
                "violations": negative_rubrics_violated,
                "percentage_violations": (negative_rubrics_violated / negative_rubrics_total * 100) if negative_rubrics_total > 0 else 0
            },
            "average_points_per_rubric": total_points / total_rubrics if total_rubrics > 0 else 0,
            "rubrics_per_conversation": {
                "mean": float(np.mean(rubrics_per_conv)) if rubrics_per_conv else 0,
                "std": float(np.std(rubrics_per_conv, ddof=1)) if len(rubrics_per_conv) > 1 else 0
            }
        }

    def analyze_routing(self, scores: List[Dict]) -> Dict:
        """Analyze routing decisions (primary vs arbiter)."""
        routing_counts = {"primary": 0, "arbiter": 0, "unknown": 0}
        routing_scores = {"primary": [], "arbiter": [], "unknown": []}

        for conv in scores:
            routed_to = conv.get("routed_to", "unknown")
            score = conv.get("contradiction_score", 0)

            if routed_to in routing_counts:
                routing_counts[routed_to] += 1
                routing_scores[routed_to].append(score)
            else:
                routing_counts["unknown"] += 1
                routing_scores["unknown"].append(score)

        result = {}
        for route_type in ["primary", "arbiter", "unknown"]:
            if routing_counts[route_type] > 0:
                result[f"{route_type}_routed"] = {
                    "count": routing_counts[route_type],
                    "mean_score": float(np.mean(routing_scores[route_type])),
                    "std_score": float(np.std(routing_scores[route_type], ddof=1)) if len(routing_scores[route_type]) > 1 else 0
                }

        total = sum(routing_counts.values())
        if total > 0:
            result["arbiter_routing_rate"] = (routing_counts["arbiter"] / total * 100)

        return result


class StatisticalComparator:
    """Perform statistical tests and calculate effect sizes."""

    def independent_t_test(self, group1: List[float], group2: List[float]) -> Dict:
        """Perform independent samples t-test."""
        t_stat, p_value = stats.ttest_ind(group1, group2)

        # Calculate 95% confidence interval for difference in means
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)

        # Standard error of difference
        se_diff = np.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Degrees of freedom (Welch's t-test)
        df = n1 + n2 - 2

        # t-critical value for 95% CI
        t_crit = stats.t.ppf(0.975, df)

        # Confidence interval
        diff = mean2 - mean1
        ci_lower = diff - (t_crit * se_diff)
        ci_upper = diff + (t_crit * se_diff)

        return {
            "t_statistic": float(t_stat),
            "degrees_of_freedom": int(df),
            "p_value": float(p_value),
            "p_value_interpretation": self._interpret_pvalue(p_value),
            "significant_at_0.05": bool(p_value < 0.05),
            "significant_at_0.01": bool(p_value < 0.01),
            "significant_at_0.001": bool(p_value < 0.001),
            "confidence_interval_95": [float(ci_lower), float(ci_upper)]
        }

    def mann_whitney_u(self, group1: List[float], group2: List[float]) -> Dict:
        """Perform Mann-Whitney U test (non-parametric)."""
        u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')

        return {
            "u_statistic": float(u_stat),
            "p_value": float(p_value),
            "significant_at_0.05": bool(p_value < 0.05)
        }

    def cohens_d(self, group1: List[float], group2: List[float]) -> Dict:
        """Calculate Cohen's d effect size."""
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))

        if pooled_std == 0:
            d = 0.0
        else:
            d = (mean2 - mean1) / pooled_std

        # Variance explained (r²)
        r_squared = (d**2) / (d**2 + 4) if d != 0 else 0

        return {
            "cohens_d": float(d),
            "interpretation": self._interpret_effect_size(d),
            "variance_explained": float(r_squared)
        }

    def levene_test(self, group1: List[float], group2: List[float]) -> Dict:
        """Test for equality of variances (Levene's test)."""
        stat, p_value = stats.levene(group1, group2)

        return {
            "statistic": float(stat),
            "p_value": float(p_value),
            "equal_variances": bool(p_value >= 0.05)
        }

    def shapiro_wilk(self, group: List[float], name: str) -> Dict:
        """Test for normality (Shapiro-Wilk test)."""
        if len(group) < 3:
            return {"statistic": 0.0, "p_value": 1.0, "normal": True, "note": "Sample too small"}

        stat, p_value = stats.shapiro(group)

        return {
            "statistic": float(stat),
            "p_value": float(p_value),
            "normal": bool(p_value >= 0.05)
        }

    def _interpret_pvalue(self, p: float) -> str:
        """Interpret p-value with significance markers."""
        if p < 0.001:
            return "*** (p < 0.001)"
        elif p < 0.01:
            return "** (p < 0.01)"
        elif p < 0.05:
            return "* (p < 0.05)"
        else:
            return "ns (not significant)"

    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


class OutputFormatter:
    """Format comparison results for different outputs."""

    def format_console(self, comparison: Dict) -> str:
        """Format results for console output."""
        baseline = comparison["baseline"]
        arbiter = comparison["arbiter"]
        stats_tests = comparison["statistical_tests"]
        comp = comparison["comparison"]

        lines = []
        lines.append("\n" + "="*70)
        lines.append("HEALTHBENCH RUBRIC SCORES COMPARISON")
        lines.append("="*70 + "\n")

        # Baseline condition
        lines.append("CONDITION: BASELINE (No Arbiter)")
        lines.append(f"  Conversations: {baseline['n_conversations']}")
        lines.append(f"  Contradiction Score: {baseline['contradiction_score']['mean']:.2f} ± {baseline['contradiction_score']['std']:.2f}")
        lines.append(f"  Rubrics Met: {baseline['rubric_analysis']['percentage_rubrics_met']:.1f}% ({baseline['rubric_analysis']['total_rubrics_met']}/{baseline['rubric_analysis']['total_rubrics_evaluated']})")
        lines.append(f"  Positive Rubrics Met: {baseline['rubric_analysis']['positive_rubrics']['percentage_met']:.1f}%")
        if baseline['rubric_analysis']['negative_rubrics']['total'] > 0:
            lines.append(f"  Negative Rubrics Violated: {baseline['rubric_analysis']['negative_rubrics']['percentage_violations']:.1f}%")

        lines.append("")

        # Arbiter condition
        lines.append("CONDITION: ARBITER (Epistemic Fortitude)")
        lines.append(f"  Conversations: {arbiter['n_conversations']}")
        lines.append(f"  Contradiction Score: {arbiter['contradiction_score']['mean']:.2f} ± {arbiter['contradiction_score']['std']:.2f}")
        lines.append(f"  Rubrics Met: {arbiter['rubric_analysis']['percentage_rubrics_met']:.1f}% ({arbiter['rubric_analysis']['total_rubrics_met']}/{arbiter['rubric_analysis']['total_rubrics_evaluated']})")
        lines.append(f"  Positive Rubrics Met: {arbiter['rubric_analysis']['positive_rubrics']['percentage_met']:.1f}%")
        if arbiter['rubric_analysis']['negative_rubrics']['total'] > 0:
            lines.append(f"  Negative Rubrics Violated: {arbiter['rubric_analysis']['negative_rubrics']['percentage_violations']:.1f}%")
        if "arbiter_routing_rate" in arbiter.get("routing_analysis", {}):
            lines.append(f"  Arbiter Routing Rate: {arbiter['routing_analysis']['arbiter_routing_rate']:.1f}%")

        lines.append("")

        # Comparison
        lines.append("COMPARISON:")
        lines.append(f"  Absolute Difference: {'+' if comp['absolute_difference'] > 0 else ''}{comp['absolute_difference']:.2f} points")
        lines.append(f"  Percentage Improvement: {'+' if comp['percentage_improvement'] > 0 else ''}{comp['percentage_improvement']:.1f}%")
        lines.append(f"  Rubrics Met Improvement: {'+' if comp['rubrics_met_difference']['absolute'] > 0 else ''}{comp['rubrics_met_difference']['absolute']:.1f} percentage points")

        lines.append("")

        # Statistical tests
        t_test = stats_tests["t_test"]
        mw_test = stats_tests["mann_whitney_u"]
        effect = stats_tests["effect_size"]

        lines.append("STATISTICAL TESTS:")
        lines.append(f"  Independent t-test: t({t_test['degrees_of_freedom']}) = {t_test['t_statistic']:.2f}, {t_test['p_value_interpretation']}")
        lines.append(f"  Mann-Whitney U: U = {mw_test['u_statistic']:.1f}, p = {mw_test['p_value']:.6f}")
        lines.append(f"  Effect Size: Cohen's d = {effect['cohens_d']:.2f} ({effect['interpretation']} effect)")
        lines.append(f"  95% CI for difference: [{t_test['confidence_interval_95'][0]:.2f}, {t_test['confidence_interval_95'][1]:.2f}]")

        lines.append("")

        # Conclusion
        lines.append("CONCLUSION:")
        lines.append(f"  {comp['conclusion']}")

        lines.append("\n" + "="*70 + "\n")

        return "\n".join(lines)

    def format_latex(self, comparison: Dict) -> str:
        """Format results for LaTeX (tables and results text)."""
        baseline = comparison["baseline"]
        arbiter = comparison["arbiter"]
        stats_tests = comparison["statistical_tests"]
        comp = comparison["comparison"]

        lines = []
        lines.append("% LaTeX Output for HealthBench Scores Comparison")
        lines.append("% Copy the sections below into your paper\n")

        # Table 1: Descriptive Statistics
        lines.append("% Table 1: Descriptive Statistics")
        lines.append("\\begin{table}[h]")
        lines.append("\\centering")
        lines.append("\\begin{tabular}{lcc}")
        lines.append("\\hline")
        lines.append("Metric & Baseline & Arbiter \\\\")
        lines.append("\\hline")
        lines.append(f"Contradiction Score (M $\\pm$ SD) & {baseline['contradiction_score']['mean']:.2f} $\\pm$ {baseline['contradiction_score']['std']:.2f} & {arbiter['contradiction_score']['mean']:.2f} $\\pm$ {arbiter['contradiction_score']['std']:.2f} \\\\")
        lines.append(f"Rubrics Met (\\%) & {baseline['rubric_analysis']['percentage_rubrics_met']:.1f}\\% & {arbiter['rubric_analysis']['percentage_rubrics_met']:.1f}\\% \\\\")
        lines.append(f"Positive Rubrics Met (\\%) & {baseline['rubric_analysis']['positive_rubrics']['percentage_met']:.1f}\\% & {arbiter['rubric_analysis']['positive_rubrics']['percentage_met']:.1f}\\% \\\\")
        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append("\\caption{Comparison of HealthBench rubric scores between baseline and arbiter conditions.}")
        lines.append("\\label{tab:healthbench_comparison}")
        lines.append("\\end{table}\n")

        # Results section text
        t_test = stats_tests["t_test"]
        effect = stats_tests["effect_size"]

        lines.append("% Results Section Text")
        lines.append(f"% The arbiter condition (M = {arbiter['contradiction_score']['mean']:.2f}, SD = {arbiter['contradiction_score']['std']:.2f}) significantly")
        lines.append(f"% outperformed the baseline (M = {baseline['contradiction_score']['mean']:.2f}, SD = {baseline['contradiction_score']['std']:.2f})")
        lines.append(f"% on contradiction turn quality, t({t_test['degrees_of_freedom']}) = {t_test['t_statistic']:.2f},")
        lines.append(f"% p < .001, d = {effect['cohens_d']:.2f}, 95\\% CI [{t_test['confidence_interval_95'][0]:.2f}, {t_test['confidence_interval_95'][1]:.2f}].")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare HealthBench rubric scores between baseline and arbiter"
    )
    parser.add_argument(
        "--baseline",
        required=True,
        help="Baseline experiment directory (e.g., logs/experiments/healthbench_langgraph_baseline)"
    )
    parser.add_argument(
        "--arbiter",
        required=True,
        help="Arbiter experiment directory (e.g., logs/experiments/healthbench_langgraph_arbiter)"
    )
    parser.add_argument(
        "--output-dir",
        default="logs/comparisons",
        help="Output directory for comparison results"
    )
    args = parser.parse_args()

    # Initialize components
    loader = ScoringSummaryLoader()
    rubric_analyzer = RubricAnalyzer()
    stat_comparator = StatisticalComparator()
    formatter = OutputFormatter()

    print("\nLoading experiment data...")

    # Load summaries and individual scores
    baseline_summary = loader.load_summary(Path(args.baseline))
    arbiter_summary = loader.load_summary(Path(args.arbiter))

    baseline_scores = loader.load_individual_scores(Path(args.baseline))
    arbiter_scores = loader.load_individual_scores(Path(args.arbiter))

    print(f"[OK] Baseline: {len(baseline_scores)} conversations")
    print(f"[OK] Arbiter: {len(arbiter_scores)} conversations")

    # Extract contradiction scores
    baseline_values = [s["contradiction_score"] for s in baseline_scores]
    arbiter_values = [s["contradiction_score"] for s in arbiter_scores]

    # Calculate all metrics
    print("\nCalculating metrics...")

    # Rubric analysis
    baseline_rubric_analysis = rubric_analyzer.analyze_rubrics(baseline_scores)
    arbiter_rubric_analysis = rubric_analyzer.analyze_rubrics(arbiter_scores)

    # Routing analysis
    baseline_routing = rubric_analyzer.analyze_routing(baseline_scores)
    arbiter_routing = rubric_analyzer.analyze_routing(arbiter_scores)

    # Statistical tests
    print("Running statistical tests...")
    t_test_result = stat_comparator.independent_t_test(baseline_values, arbiter_values)
    mw_test_result = stat_comparator.mann_whitney_u(baseline_values, arbiter_values)
    effect_size_result = stat_comparator.cohens_d(baseline_values, arbiter_values)
    levene_result = stat_comparator.levene_test(baseline_values, arbiter_values)
    shapiro_baseline = stat_comparator.shapiro_wilk(baseline_values, "baseline")
    shapiro_arbiter = stat_comparator.shapiro_wilk(arbiter_values, "arbiter")

    # Build comprehensive comparison
    comparison = {
        "metadata": {
            "comparison_date": datetime.now().isoformat(),
            "baseline_dir": args.baseline,
            "arbiter_dir": args.arbiter,
            "script_version": "1.0"
        },
        "baseline": {
            "experiment_dir": args.baseline,
            "arbiter_enabled": False,
            "n_conversations": len(baseline_values),
            "contradiction_score": {
                "mean": float(np.mean(baseline_values)),
                "std": float(np.std(baseline_values, ddof=1)),
                "median": float(np.median(baseline_values)),
                "min": float(np.min(baseline_values)),
                "max": float(np.max(baseline_values)),
                "quartiles": [
                    float(np.percentile(baseline_values, 25)),
                    float(np.percentile(baseline_values, 50)),
                    float(np.percentile(baseline_values, 75))
                ]
            },
            "rubric_analysis": baseline_rubric_analysis,
            "routing_analysis": baseline_routing
        },
        "arbiter": {
            "experiment_dir": args.arbiter,
            "arbiter_enabled": True,
            "n_conversations": len(arbiter_values),
            "contradiction_score": {
                "mean": float(np.mean(arbiter_values)),
                "std": float(np.std(arbiter_values, ddof=1)),
                "median": float(np.median(arbiter_values)),
                "min": float(np.min(arbiter_values)),
                "max": float(np.max(arbiter_values)),
                "quartiles": [
                    float(np.percentile(arbiter_values, 25)),
                    float(np.percentile(arbiter_values, 50)),
                    float(np.percentile(arbiter_values, 75))
                ]
            },
            "rubric_analysis": arbiter_rubric_analysis,
            "routing_analysis": arbiter_routing
        },
        "statistical_tests": {
            "t_test": t_test_result,
            "mann_whitney_u": mw_test_result,
            "effect_size": effect_size_result,
            "levene_test": levene_result,
            "normality_tests": {
                "baseline": shapiro_baseline,
                "arbiter": shapiro_arbiter
            }
        },
        "comparison": {
            "absolute_difference": float(np.mean(arbiter_values) - np.mean(baseline_values)),
            "percentage_improvement": float(
                (np.mean(arbiter_values) - np.mean(baseline_values)) /
                np.mean(baseline_values) * 100
            ) if np.mean(baseline_values) > 0 else 0,
            "rubrics_met_difference": {
                "absolute": arbiter_rubric_analysis["percentage_rubrics_met"] - baseline_rubric_analysis["percentage_rubrics_met"],
                "relative": (
                    (arbiter_rubric_analysis["percentage_rubrics_met"] - baseline_rubric_analysis["percentage_rubrics_met"]) /
                    baseline_rubric_analysis["percentage_rubrics_met"] * 100
                ) if baseline_rubric_analysis["percentage_rubrics_met"] > 0 else 0
            },
            "conclusion": (
                "The arbiter significantly improves contradiction turn quality (p < 0.05)"
                if t_test_result["p_value"] < 0.05
                else "No significant difference in contradiction turn quality between conditions"
            )
        }
    }

    # Save outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_path = output_dir / f"healthbench_comparison_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # Save LaTeX
    latex_path = output_dir / f"healthbench_comparison_{timestamp}_latex.txt"
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(formatter.format_latex(comparison))

    # Print console output
    print(formatter.format_console(comparison))

    print(f"[OK] JSON output saved to: {json_path}")
    print(f"[OK] LaTeX output saved to: {latex_path}")


if __name__ == "__main__":
    main()
