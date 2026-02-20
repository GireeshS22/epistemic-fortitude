"""Ablation Study Statistical Analysis & Figures.

Analyzes the "Prompt vs Architecture" ablation study (50 examples x 4 models).
Produces statistical tests (t-tests, Mann-Whitney U, Cohen's d, Bonferroni correction)
and 4 publication-ready figures.

Usage:
    poetry run python scripts/ablation_figures.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Paths
EXPERIMENTS_DIR = Path(__file__).parent.parent / "logs" / "experiments"
OUTPUT_DIR = Path(__file__).parent.parent / "logs" / "sensitivity_analysis"

# Folder -> model name mapping for all three conditions
BASELINE_MAPPING = {
    "swebench_langgraph_baseline": "Gemini",
    "swebench_langgraph_claude-sonnet-4-5-20250929_baseline": "Claude",
    "swebench_langgraph_gpt-5-1_baseline": "GPT-5.1",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_baseline": "Llama-3.3-70B",
}

ABLATION_MAPPING = {
    "swebench_langgraph_gemini-2-5-flash_ablation": "Gemini",
    "swebench_langgraph_claude-sonnet-4-5-20250929_ablation": "Claude",
    "swebench_langgraph_gpt-5-1_ablation": "GPT-5.1",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_ablation": "Llama-3.3-70B",
}

ARBITER_MAPPING = {
    "swebench_langgraph_arbiter": "Gemini",
    "swebench_langgraph_claude-sonnet-4-5-20250929_arbiter": "Claude",
    "swebench_langgraph_gpt-5-1_arbiter": "GPT-5.1",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_arbiter": "Llama-3.3-70B",
}

SCORE_DIMENSIONS = [
    "epistemic_responsibility",
    "quality_of_rationale",
    "apology_and_deference",
    "confidence_and_assertiveness",
    "defense_quality",
    "total_epistemic_fortitude",
]

MODEL_ORDER = ["Llama-3.3-70B", "Claude", "GPT-5.1", "Gemini"]


def load_scores(folder_mapping, mode_label):
    """Load epistemic scores from experiment folders into a DataFrame."""
    records = []
    for folder_name, model_name in folder_mapping.items():
        folder_path = EXPERIMENTS_DIR / folder_name / "epistemic_scores"
        if not folder_path.exists():
            print(f"  Warning: {folder_path} not found, skipping...")
            continue

        json_files = list(folder_path.glob("*.json"))
        print(f"  Loading {len(json_files)} files from {folder_name}")

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                record = {
                    "example_id": data.get("example_id", json_file.stem),
                    "model": model_name,
                    "mode": mode_label,
                }
                scores = data.get("scores", {})
                for dim in SCORE_DIMENSIONS:
                    record[dim] = scores.get(dim, 0)
                records.append(record)
            except Exception as e:
                print(f"  Error loading {json_file}: {e}")

    return pd.DataFrame(records)


def compute_cohens_d(group1, group2):
    """Compute Cohen's d effect size with interpretation."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0, "undefined"
    d = (group2.mean() - group1.mean()) / pooled_std
    abs_d = abs(d)
    if abs_d < 0.2:
        interp = "negligible"
    elif abs_d < 0.5:
        interp = "small"
    elif abs_d < 0.8:
        interp = "medium"
    else:
        interp = "large"
    return d, interp


def run_statistical_tests(df):
    """Run pairwise statistical tests for all models and condition pairs."""
    pairs = [
        ("Baseline", "Ablation"),
        ("Ablation", "Arbiter"),
        ("Baseline", "Arbiter"),
    ]
    results = []

    for model in MODEL_ORDER:
        model_df = df[df["model"] == model]
        for mode_a, mode_b in pairs:
            scores_a = model_df[model_df["mode"] == mode_a]["total_epistemic_fortitude"].values
            scores_b = model_df[model_df["mode"] == mode_b]["total_epistemic_fortitude"].values

            if len(scores_a) == 0 or len(scores_b) == 0:
                continue

            # T-test
            t_stat, t_pval = stats.ttest_ind(scores_a, scores_b)

            # Mann-Whitney U
            u_stat, u_pval = stats.mannwhitneyu(scores_a, scores_b, alternative="two-sided")

            # Cohen's d
            d, d_interp = compute_cohens_d(scores_a, scores_b)

            results.append({
                "model": model,
                "comparison": f"{mode_a} vs {mode_b}",
                "mean_a": scores_a.mean(),
                "mean_b": scores_b.mean(),
                "diff": scores_b.mean() - scores_a.mean(),
                "t_statistic": t_stat,
                "t_p_value": t_pval,
                "u_statistic": u_stat,
                "u_p_value": u_pval,
                "cohens_d": d,
                "effect_interpretation": d_interp,
                "n_a": len(scores_a),
                "n_b": len(scores_b),
            })

    results_df = pd.DataFrame(results)

    # Bonferroni correction (12 comparisons: 3 pairs x 4 models)
    n_comparisons = len(results_df)
    results_df["t_p_bonferroni"] = np.minimum(results_df["t_p_value"] * n_comparisons, 1.0)
    results_df["u_p_bonferroni"] = np.minimum(results_df["u_p_value"] * n_comparisons, 1.0)
    results_df["t_sig_bonferroni"] = results_df["t_p_bonferroni"] < 0.05
    results_df["u_sig_bonferroni"] = results_df["u_p_bonferroni"] < 0.05

    return results_df


def compute_decomposition(df):
    """Compute prompt vs architecture contribution per model."""
    rows = []
    for model in MODEL_ORDER:
        model_df = df[df["model"] == model]
        baseline_mean = model_df[model_df["mode"] == "Baseline"]["total_epistemic_fortitude"].mean()
        ablation_mean = model_df[model_df["mode"] == "Ablation"]["total_epistemic_fortitude"].mean()
        arbiter_mean = model_df[model_df["mode"] == "Arbiter"]["total_epistemic_fortitude"].mean()

        prompt_gain = ablation_mean - baseline_mean
        arch_gain = arbiter_mean - ablation_mean
        total_gain = arbiter_mean - baseline_mean

        rows.append({
            "model": model,
            "baseline_mean": baseline_mean,
            "ablation_mean": ablation_mean,
            "arbiter_mean": arbiter_mean,
            "prompt_contribution": prompt_gain,
            "architecture_contribution": arch_gain,
            "total_improvement": total_gain,
            "prompt_pct": (prompt_gain / total_gain * 100) if total_gain != 0 else 0,
            "architecture_pct": (arch_gain / total_gain * 100) if total_gain != 0 else 0,
        })

    return pd.DataFrame(rows)


def compute_correlation(decomposition_df):
    """Compute correlation between baseline score and architecture benefit."""
    x = decomposition_df["baseline_mean"].values
    y = decomposition_df["architecture_pct"].values
    r, p = stats.pearsonr(x, y)
    return r, p


# --- Figures ---

def figure_three_condition_comparison(df, output_dir):
    """Figure 1: Grouped bar chart with 3 bars per model."""
    fig, ax = plt.subplots(figsize=(12, 6))

    summary = df.groupby(["model", "mode"])["total_epistemic_fortitude"].mean().unstack()
    summary = summary.reindex(MODEL_ORDER)

    x = np.arange(len(MODEL_ORDER))
    width = 0.25

    bars_bl = ax.bar(x - width, summary["Baseline"], width, label="Baseline", color="#E74C3C")
    bars_ab = ax.bar(x, summary["Ablation"], width, label="Ablation (Prompt Only)", color="#F39C12")
    bars_ar = ax.bar(x + width, summary["Arbiter"], width, label="Arbiter (Full System)", color="#27AE60")

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Mean Epistemic Fortitude Score", fontsize=12)
    ax.set_title("Three-Condition Comparison: Baseline vs Ablation vs Arbiter",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(MODEL_ORDER, fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 65)

    # Value labels
    for bars in [bars_bl, bars_ab, bars_ar]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

    # Improvement % annotations (baseline -> arbiter)
    for i, model in enumerate(MODEL_ORDER):
        baseline = summary.loc[model, "Baseline"]
        arbiter = summary.loc[model, "Arbiter"]
        improvement = ((arbiter - baseline) / baseline) * 100 if baseline > 0 else 0
        top = max(baseline, summary.loc[model, "Ablation"], arbiter)
        ax.annotate(f"+{improvement:.0f}%",
                    xy=(i, top + 4),
                    ha="center", fontsize=10, fontweight="bold", color="#2C3E50")

    plt.tight_layout()
    for ext in ["png", "pdf"]:
        plt.savefig(output_dir / f"ablation_figure_three_condition_comparison.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: ablation_figure_three_condition_comparison.png")


def figure_decomposition_stacked(decomposition_df, output_dir):
    """Figure 2: Stacked bar chart of prompt vs architecture contribution."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(decomposition_df))
    models = decomposition_df["model"].values
    prompt = decomposition_df["prompt_contribution"].values
    arch = decomposition_df["architecture_contribution"].values

    bars_prompt = ax.bar(x, prompt, label="Prompt Contribution", color="#F39C12")
    bars_arch = ax.bar(x, arch, bottom=prompt, label="Architecture Contribution", color="#3498DB")

    ax.set_xlabel("Model (ordered by baseline score)", fontsize=12)
    ax.set_ylabel("Improvement over Baseline (points)", fontsize=12)
    ax.set_title("Improvement Decomposition: Prompt vs Architecture",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend(fontsize=10)

    # Percentage labels on each segment
    for i in range(len(decomposition_df)):
        row = decomposition_df.iloc[i]
        # Prompt segment label
        if abs(row["prompt_contribution"]) > 0.5:
            ax.text(i, row["prompt_contribution"] / 2, f"{row['prompt_pct']:.0f}%",
                    ha="center", va="center", fontsize=10, fontweight="bold", color="white")
        # Architecture segment label
        if abs(row["architecture_contribution"]) > 0.5:
            ax.text(i, row["prompt_contribution"] + row["architecture_contribution"] / 2,
                    f"{row['architecture_pct']:.0f}%",
                    ha="center", va="center", fontsize=10, fontweight="bold", color="white")

    plt.tight_layout()
    for ext in ["png", "pdf"]:
        plt.savefig(output_dir / f"ablation_figure_decomposition_stacked.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: ablation_figure_decomposition_stacked.png")


def figure_score_distributions(df, output_dir):
    """Figure 3: Violin plots, 2x2 grid, one per model."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    mode_order = ["Baseline", "Ablation", "Arbiter"]
    palette = {"Baseline": "#E74C3C", "Ablation": "#F39C12", "Arbiter": "#27AE60"}

    models = [m for m in MODEL_ORDER if m in df["model"].unique()]

    for idx, model in enumerate(models):
        ax = axes[idx]
        model_df = df[df["model"] == model]

        sns.violinplot(
            data=model_df, x="mode", y="total_epistemic_fortitude",
            hue="mode", palette=palette, order=mode_order,
            hue_order=mode_order, legend=False, ax=ax
        )
        sns.stripplot(
            data=model_df, x="mode", y="total_epistemic_fortitude",
            color="black", alpha=0.3, size=3,
            order=mode_order, ax=ax
        )

        ax.set_title(f"{model}", fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Epistemic Fortitude Score" if idx % 2 == 0 else "")
        ax.set_ylim(0, 65)

        for i, mode in enumerate(mode_order):
            mean_val = model_df[model_df["mode"] == mode]["total_epistemic_fortitude"].mean()
            ax.annotate(f"\u03bc={mean_val:.1f}", xy=(i, mean_val),
                        xytext=(i + 0.2, mean_val + 3),
                        fontsize=9, fontweight="bold")

    plt.suptitle("Ablation Study: Score Distributions by Model and Condition",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    for ext in ["png", "pdf"]:
        plt.savefig(output_dir / f"ablation_figure_score_distributions.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: ablation_figure_score_distributions.png")


def figure_capability_threshold(decomposition_df, output_dir):
    """Figure 4: Scatter plot of baseline score vs architecture contribution %."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = decomposition_df["baseline_mean"].values
    y = decomposition_df["architecture_pct"].values
    models = decomposition_df["model"].values

    ax.scatter(x, y, s=120, c="#3498DB", edgecolors="black", zorder=5)

    # Label each point
    for i, model in enumerate(models):
        ax.annotate(model, (x[i], y[i]),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=10, fontweight="bold")

    # Regression line
    if len(x) > 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_line = np.linspace(x.min() - 2, x.max() + 2, 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, "--", color="red", alpha=0.7, linewidth=1.5)
        ax.annotate(f"R\u00b2 = {r_value**2:.3f}\np = {p_value:.3f}",
                    xy=(0.05, 0.95), xycoords="axes fraction",
                    fontsize=11, va="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

    ax.set_xlabel("Baseline Mean Score", fontsize=12)
    ax.set_ylabel("Architecture Contribution (%)", fontsize=12)
    ax.set_title("Capability Threshold: Baseline Score vs Architecture Benefit",
                 fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    for ext in ["png", "pdf"]:
        plt.savefig(output_dir / f"ablation_figure_capability_threshold.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: ablation_figure_capability_threshold.png")


def print_statistical_report(stats_df, decomposition_df, r, r_p):
    """Print a full statistical report to console."""
    print("\n" + "=" * 70)
    print("STATISTICAL TEST RESULTS")
    print("=" * 70)

    for model in MODEL_ORDER:
        model_rows = stats_df[stats_df["model"] == model]
        print(f"\n--- {model} ---")
        for _, row in model_rows.iterrows():
            sig = ""
            if row["t_p_bonferroni"] < 0.001:
                sig = "***"
            elif row["t_p_bonferroni"] < 0.01:
                sig = "**"
            elif row["t_p_bonferroni"] < 0.05:
                sig = "*"
            else:
                sig = "ns"

            print(f"  {row['comparison']:25s}  "
                  f"diff={row['diff']:+6.2f}  "
                  f"t={row['t_statistic']:6.2f}  p={row['t_p_value']:.4f}  "
                  f"p_bonf={row['t_p_bonferroni']:.4f} {sig}  "
                  f"U={row['u_statistic']:.0f}  p_U={row['u_p_value']:.4f}  "
                  f"d={row['cohens_d']:.3f} ({row['effect_interpretation']})")

    print("\n" + "=" * 70)
    print("IMPROVEMENT DECOMPOSITION")
    print("=" * 70)
    for _, row in decomposition_df.iterrows():
        print(f"\n  {row['model']}:")
        print(f"    Baseline={row['baseline_mean']:.2f}  "
              f"Ablation={row['ablation_mean']:.2f}  "
              f"Arbiter={row['arbiter_mean']:.2f}")
        print(f"    Prompt: +{row['prompt_contribution']:.2f} ({row['prompt_pct']:.1f}%)  "
              f"Architecture: +{row['architecture_contribution']:.2f} ({row['architecture_pct']:.1f}%)")

    print(f"\n  Correlation (baseline vs architecture %): r={r:.3f}, p={r_p:.3f}")


def main():
    print("=" * 60)
    print("ABLATION STUDY: STATISTICAL ANALYSIS & FIGURES")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load data for all three conditions
    print("\n[1/6] Loading baseline scores...")
    baseline_df = load_scores(BASELINE_MAPPING, "Baseline")
    print(f"  Total: {len(baseline_df)} records")

    print("\n[2/6] Loading ablation scores...")
    ablation_df = load_scores(ABLATION_MAPPING, "Ablation")
    print(f"  Total: {len(ablation_df)} records")

    print("\n[3/6] Loading arbiter scores...")
    arbiter_df = load_scores(ARBITER_MAPPING, "Arbiter")
    print(f"  Total: {len(arbiter_df)} records")

    # Combine into single DataFrame
    df = pd.concat([baseline_df, ablation_df, arbiter_df], ignore_index=True)
    print(f"\n  Combined: {len(df)} records, "
          f"Models: {list(df['model'].unique())}, "
          f"Modes: {list(df['mode'].unique())}")

    # Statistical tests
    print("\n[4/6] Running statistical tests...")
    stats_df = run_statistical_tests(df)
    stats_df.to_csv(OUTPUT_DIR / "ablation_statistical_tests.csv", index=False)
    print(f"  Saved: ablation_statistical_tests.csv")

    # Decomposition
    decomposition_df = compute_decomposition(df)
    decomposition_df.to_csv(OUTPUT_DIR / "ablation_decomposition.csv", index=False)
    print(f"  Saved: ablation_decomposition.csv")

    # Correlation
    r, r_p = compute_correlation(decomposition_df)

    # Print full report
    print_statistical_report(stats_df, decomposition_df, r, r_p)

    # Figures
    print("\n[5/6] Generating figures...")
    figure_three_condition_comparison(df, OUTPUT_DIR)
    figure_decomposition_stacked(decomposition_df, OUTPUT_DIR)
    figure_score_distributions(df, OUTPUT_DIR)
    figure_capability_threshold(decomposition_df, OUTPUT_DIR)

    # Summary
    print("\n[6/6] Summary")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    for f in sorted(OUTPUT_DIR.glob("ablation_*")):
        print(f"  - {f.name}")

    print("\n" + "=" * 60)
    print("ABLATION ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
