"""
Sensitivity Analysis for Epistemic Fortitude Experiments

This script:
1. Loads all epistemic scores from experiment folders
2. Creates a consolidated DataFrame
3. Runs sensitivity analysis across thresholds (35, 40, 45)
4. Generates publication-ready figures

Usage:
    python scripts/sensitivity_analysis.py
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


# Configuration
EXPERIMENTS_DIR = Path(__file__).parent.parent / "logs" / "experiments"
OUTPUT_DIR = Path(__file__).parent.parent / "logs" / "sensitivity_analysis"
THRESHOLDS = [35, 40, 45]

# Model name mapping from folder names
MODEL_MAPPING = {
    "swebench_langgraph_arbiter": "Gemini",
    "swebench_langgraph_baseline": "Gemini",
    "swebench_langgraph_claude-sonnet-4-5-20250929_arbiter": "Claude",
    "swebench_langgraph_claude-sonnet-4-5-20250929_baseline": "Claude",
    "swebench_langgraph_gpt-5-1_arbiter": "GPT-5.1",
    "swebench_langgraph_gpt-5-1_baseline": "GPT-5.1",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_arbiter": "Llama-3.3-70B",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_baseline": "Llama-3.3-70B",
}

# Score dimensions
SCORE_DIMENSIONS = [
    "epistemic_responsibility",
    "quality_of_rationale",
    "apology_and_deference",
    "confidence_and_assertiveness",
    "defense_quality",
    "total_epistemic_fortitude"
]


def load_epistemic_scores() -> pd.DataFrame:
    """Load all epistemic scores from experiment folders into a DataFrame."""

    records = []

    for folder_name, model_name in MODEL_MAPPING.items():
        folder_path = EXPERIMENTS_DIR / folder_name / "epistemic_scores"

        if not folder_path.exists():
            print(f"Warning: {folder_path} does not exist, skipping...")
            continue

        # Determine mode from folder name
        mode = "Arbiter" if folder_name.endswith("_arbiter") else "Baseline"

        # Load all JSON files in epistemic_scores folder
        json_files = list(folder_path.glob("*.json"))
        print(f"Loading {len(json_files)} files from {folder_name}...")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                record = {
                    "example_id": data.get("example_id", json_file.stem),
                    "model": model_name,
                    "mode": mode,
                }

                # Extract scores
                scores = data.get("scores", {})
                for dim in SCORE_DIMENSIONS:
                    record[dim] = scores.get(dim, 0)

                records.append(record)

            except Exception as e:
                print(f"Error loading {json_file}: {e}")

    df = pd.DataFrame(records)
    print(f"\nLoaded {len(df)} total records")
    print(f"Models: {df['model'].unique()}")
    print(f"Modes: {df['mode'].unique()}")

    return df


def compute_statistics(df: pd.DataFrame, group_col: str = "mode") -> pd.DataFrame:
    """Compute descriptive statistics for each group."""

    stats_df = df.groupby(["model", group_col])["total_epistemic_fortitude"].agg([
        "count", "mean", "std", "min", "max", "median"
    ]).round(2)

    return stats_df


def compute_effect_size(group1: np.ndarray, group2: np.ndarray) -> Tuple[float, str]:
    """Compute Cohen's d effect size."""

    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0, "undefined"

    cohens_d = (group2.mean() - group1.mean()) / pooled_std

    # Interpretation
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        interpretation = "negligible"
    elif abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return cohens_d, interpretation


def sensitivity_analysis(df: pd.DataFrame, thresholds: List[int] = THRESHOLDS) -> pd.DataFrame:
    """
    Run sensitivity analysis across different thresholds.

    For each threshold, calculate:
    - % of responses >= threshold (baseline vs arbiter)
    - Effect size (Cohen's d)
    - Statistical significance (t-test p-value)
    """

    results = []

    for model in df["model"].unique():
        model_df = df[df["model"] == model]
        baseline = model_df[model_df["mode"] == "Baseline"]["total_epistemic_fortitude"].values
        arbiter = model_df[model_df["mode"] == "Arbiter"]["total_epistemic_fortitude"].values

        for threshold in thresholds:
            # Calculate % above threshold
            baseline_pct = (baseline >= threshold).mean() * 100
            arbiter_pct = (arbiter >= threshold).mean() * 100

            # Effect size on raw scores (not threshold-based)
            cohens_d, interpretation = compute_effect_size(baseline, arbiter)

            # T-test
            t_stat, p_value = stats.ttest_ind(baseline, arbiter)

            # Mann-Whitney U (non-parametric)
            u_stat, u_pvalue = stats.mannwhitneyu(baseline, arbiter, alternative='two-sided')

            results.append({
                "model": model,
                "threshold": threshold,
                "n_baseline": len(baseline),
                "n_arbiter": len(arbiter),
                "baseline_mean": baseline.mean(),
                "arbiter_mean": arbiter.mean(),
                "baseline_pct_above": baseline_pct,
                "arbiter_pct_above": arbiter_pct,
                "pct_difference": arbiter_pct - baseline_pct,
                "cohens_d": cohens_d,
                "effect_interpretation": interpretation,
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant_0.05": p_value < 0.05,
                "significant_0.01": p_value < 0.01,
                "significant_0.001": p_value < 0.001,
            })

    return pd.DataFrame(results)


def create_distribution_plot(df: pd.DataFrame, output_path: Path):
    """Create violin/box plot showing score distributions by model and mode."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    models = df["model"].unique()

    for idx, model in enumerate(models):
        ax = axes[idx]
        model_df = df[df["model"] == model]

        sns.violinplot(
            data=model_df,
            x="mode",
            y="total_epistemic_fortitude",
            palette={"Baseline": "#E74C3C", "Arbiter": "#27AE60"},
            ax=ax
        )

        # Add individual points
        sns.stripplot(
            data=model_df,
            x="mode",
            y="total_epistemic_fortitude",
            color="black",
            alpha=0.3,
            size=3,
            ax=ax
        )

        ax.set_title(f"{model}", fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Epistemic Fortitude Score" if idx % 2 == 0 else "")
        ax.set_ylim(0, 65)

        # Add mean annotations
        for i, mode in enumerate(["Baseline", "Arbiter"]):
            mean_val = model_df[model_df["mode"] == mode]["total_epistemic_fortitude"].mean()
            ax.annotate(f"μ={mean_val:.1f}", xy=(i, mean_val),
                       xytext=(i + 0.2, mean_val + 3),
                       fontsize=10, fontweight="bold")

    plt.suptitle("Epistemic Fortitude Score Distributions by Model and Condition",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path / "figure_score_distributions.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_path / "figure_score_distributions.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path / 'figure_score_distributions.png'}")


def create_threshold_sensitivity_plot(sensitivity_df: pd.DataFrame, output_path: Path):
    """Create line plot showing effect across different thresholds."""

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: % above threshold
    ax1 = axes[0]
    for model in sensitivity_df["model"].unique():
        model_data = sensitivity_df[sensitivity_df["model"] == model]
        ax1.plot(model_data["threshold"], model_data["arbiter_pct_above"],
                marker="o", label=f"{model} (Arbiter)", linestyle="-")
        ax1.plot(model_data["threshold"], model_data["baseline_pct_above"],
                marker="s", label=f"{model} (Baseline)", linestyle="--", alpha=0.7)

    ax1.set_xlabel("Threshold", fontsize=11)
    ax1.set_ylabel("% Responses ≥ Threshold", fontsize=11)
    ax1.set_title("Threshold Sensitivity: % Above Threshold", fontsize=12, fontweight="bold")
    ax1.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    ax1.set_xticks(THRESHOLDS)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Effect size (Cohen's d) - same across thresholds since it's on raw scores
    ax2 = axes[1]
    models = sensitivity_df["model"].unique()
    # Get one row per model (Cohen's d is same across thresholds)
    effect_data = sensitivity_df.groupby("model").first().reset_index()

    colors = ["#3498DB", "#E74C3C", "#27AE60", "#9B59B6"]
    bars = ax2.bar(effect_data["model"], effect_data["cohens_d"], color=colors)

    ax2.axhline(y=0.8, color="red", linestyle="--", alpha=0.5, label="Large effect (0.8)")
    ax2.axhline(y=0.5, color="orange", linestyle="--", alpha=0.5, label="Medium effect (0.5)")
    ax2.axhline(y=0.2, color="green", linestyle="--", alpha=0.5, label="Small effect (0.2)")

    ax2.set_xlabel("Model", fontsize=11)
    ax2.set_ylabel("Cohen's d", fontsize=11)
    ax2.set_title("Effect Size by Model (Arbiter vs Baseline)", fontsize=12, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=9)

    # Add value labels on bars
    for bar, val in zip(bars, effect_data["cohens_d"]):
        ax2.annotate(f"{val:.2f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path / "figure_threshold_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_path / "figure_threshold_sensitivity.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path / 'figure_threshold_sensitivity.png'}")


def create_dimension_breakdown_heatmap(df: pd.DataFrame, output_path: Path):
    """Create heatmap showing scores across dimensions, models, and modes."""

    dimensions = [d for d in SCORE_DIMENSIONS if d != "total_epistemic_fortitude"]

    # Calculate mean scores for each model/mode/dimension
    pivot_data = []
    for model in df["model"].unique():
        for mode in ["Baseline", "Arbiter"]:
            subset = df[(df["model"] == model) & (df["mode"] == mode)]
            row = {"model_mode": f"{model}\n({mode})"}
            for dim in dimensions:
                row[dim] = subset[dim].mean()
            pivot_data.append(row)

    pivot_df = pd.DataFrame(pivot_data)
    pivot_df = pivot_df.set_index("model_mode")

    # Rename columns for readability
    column_names = {
        "epistemic_responsibility": "Epistemic\nResponsibility",
        "quality_of_rationale": "Quality of\nRationale",
        "apology_and_deference": "Apology &\nDeference",
        "confidence_and_assertiveness": "Confidence &\nAssertiveness",
        "defense_quality": "Defense\nQuality"
    }
    pivot_df = pivot_df.rename(columns=column_names)

    fig, ax = plt.subplots(figsize=(12, 8))

    sns.heatmap(
        pivot_df,
        annot=True,
        fmt=".1f",
        cmap="RdYlGn",
        center=5,
        ax=ax,
        cbar_kws={"label": "Mean Score"}
    )

    ax.set_title("Score Breakdown by Dimension, Model, and Condition",
                fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")

    plt.tight_layout()
    plt.savefig(output_path / "figure_dimension_heatmap.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_path / "figure_dimension_heatmap.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path / 'figure_dimension_heatmap.png'}")


def create_cross_model_comparison(df: pd.DataFrame, output_path: Path):
    """Create grouped bar chart comparing models."""

    fig, ax = plt.subplots(figsize=(10, 6))

    # Calculate means
    summary = df.groupby(["model", "mode"])["total_epistemic_fortitude"].mean().unstack()

    x = np.arange(len(summary.index))
    width = 0.35

    bars1 = ax.bar(x - width/2, summary["Baseline"], width, label="Baseline", color="#E74C3C")
    bars2 = ax.bar(x + width/2, summary["Arbiter"], width, label="Arbiter", color="#27AE60")

    ax.set_xlabel("Model", fontsize=11)
    ax.set_ylabel("Mean Epistemic Fortitude Score", fontsize=11)
    ax.set_title("Cross-Model Comparison: Baseline vs Arbiter", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(summary.index, fontsize=10)
    ax.legend()
    ax.set_ylim(0, 60)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}",
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha="center", va="bottom", fontsize=9)

    # Add improvement percentages
    for i, model in enumerate(summary.index):
        baseline = summary.loc[model, "Baseline"]
        arbiter = summary.loc[model, "Arbiter"]
        improvement = ((arbiter - baseline) / baseline) * 100 if baseline > 0 else 0
        ax.annotate(f"+{improvement:.0f}%",
                   xy=(i, max(baseline, arbiter) + 3),
                   ha="center", fontsize=10, fontweight="bold", color="#2C3E50")

    plt.tight_layout()
    plt.savefig(output_path / "figure_cross_model_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_path / "figure_cross_model_comparison.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path / 'figure_cross_model_comparison.png'}")


def main():
    """Main function to run sensitivity analysis."""

    print("=" * 60)
    print("EPISTEMIC FORTITUDE SENSITIVITY ANALYSIS")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load all data
    print("\n[1/5] Loading epistemic scores...")
    df = load_epistemic_scores()

    # Save consolidated DataFrame
    df.to_csv(OUTPUT_DIR / "consolidated_scores.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'consolidated_scores.csv'}")

    # Step 2: Compute basic statistics
    print("\n[2/5] Computing descriptive statistics...")
    stats_df = compute_statistics(df)
    print(stats_df)
    stats_df.to_csv(OUTPUT_DIR / "descriptive_statistics.csv")

    # Step 3: Run sensitivity analysis
    print("\n[3/5] Running sensitivity analysis...")
    sensitivity_df = sensitivity_analysis(df, THRESHOLDS)
    print("\nSensitivity Analysis Results:")
    print(sensitivity_df.to_string(index=False))
    sensitivity_df.to_csv(OUTPUT_DIR / "sensitivity_analysis_results.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'sensitivity_analysis_results.csv'}")

    # Step 4: Create visualizations
    print("\n[4/5] Creating visualizations...")
    create_distribution_plot(df, OUTPUT_DIR)
    create_threshold_sensitivity_plot(sensitivity_df, OUTPUT_DIR)
    create_dimension_breakdown_heatmap(df, OUTPUT_DIR)
    create_cross_model_comparison(df, OUTPUT_DIR)

    # Step 5: Summary
    print("\n[5/5] Summary")
    print("=" * 60)
    print(f"Total records: {len(df)}")
    print(f"Models: {', '.join(df['model'].unique())}")
    print(f"Thresholds tested: {THRESHOLDS}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    for f in OUTPUT_DIR.glob("*"):
        print(f"  - {f.name}")

    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS COMPLETE")
    print("=" * 60)

    return df, sensitivity_df


if __name__ == "__main__":
    df, sensitivity_df = main()
