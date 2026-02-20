"""Generate publication-ready figures for the "User is Right" experiment.

Creates 4 figures:
1. Score distributions (violin plots) - User is Right
2. Dual experiment comparison (Agent is Right vs User is Right)
3. Per-dimension heatmap - User is Right
4. Effect size comparison across experiments

Usage:
    poetry run python scripts/user_is_right_figures.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Paths
EXPERIMENTS_DIR = Path(__file__).parent.parent / "logs" / "experiments"
COMPARISONS_DIR = Path(__file__).parent.parent / "logs" / "comparisons"
OUTPUT_DIR = Path(__file__).parent.parent / "logs" / "sensitivity_analysis"

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# User-is-Right experiment folder mapping
UIR_MODEL_MAPPING = {
    "user_is_right_meta-llama-Llama-3-3-70B-Instruct-Turbo_arbiter": "Llama-3.3-70B",
    "user_is_right_meta-llama-Llama-3-3-70B-Instruct-Turbo_baseline": "Llama-3.3-70B",
    "user_is_right_gemini-2-5-flash_arbiter": "Gemini",
    "user_is_right_gemini-2-5-flash_baseline": "Gemini",
    "user_is_right_gpt-5-1_arbiter": "GPT-5.1",
    "user_is_right_gpt-5-1_baseline": "GPT-5.1",
    "user_is_right_claude-sonnet-4-5-20250929_arbiter": "Claude",
    "user_is_right_claude-sonnet-4-5-20250929_baseline": "Claude",
}

# Original experiment folder mapping (for dual comparison)
ORIG_MODEL_MAPPING = {
    "swebench_langgraph_arbiter": "Gemini",
    "swebench_langgraph_baseline": "Gemini",
    "swebench_langgraph_claude-sonnet-4-5-20250929_arbiter": "Claude",
    "swebench_langgraph_claude-sonnet-4-5-20250929_baseline": "Claude",
    "swebench_langgraph_gpt-5-1_arbiter": "GPT-5.1",
    "swebench_langgraph_gpt-5-1_baseline": "GPT-5.1",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_arbiter": "Llama-3.3-70B",
    "swebench_langgraph_meta-llama-Llama-3-3-70B-Instruct-Turbo_baseline": "Llama-3.3-70B",
}

SCORE_DIMENSIONS = [
    "epistemic_responsibility",
    "quality_of_rationale",
    "apology_and_deference",
    "confidence_and_assertiveness",
    "defense_quality",
    "total_epistemic_fortitude",
]


def load_scores(model_mapping):
    """Load epistemic scores from experiment folders into a DataFrame."""
    records = []
    for folder_name, model_name in model_mapping.items():
        folder_path = EXPERIMENTS_DIR / folder_name / "epistemic_scores"
        if not folder_path.exists():
            print(f"  Warning: {folder_path} not found, skipping...")
            continue

        mode = "Arbiter" if folder_name.endswith("_arbiter") else "Baseline"
        json_files = list(folder_path.glob("*.json"))
        print(f"  Loading {len(json_files)} files from {folder_name}")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                record = {
                    "example_id": data.get("example_id", json_file.stem),
                    "model": model_name,
                    "mode": mode,
                }
                scores = data.get("scores", {})
                for dim in SCORE_DIMENSIONS:
                    record[dim] = scores.get(dim, 0)
                records.append(record)
            except Exception as e:
                print(f"  Error loading {json_file}: {e}")

    return pd.DataFrame(records)


def compute_effect_size(group1, group2):
    """Compute Cohen's d."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (group2.mean() - group1.mean()) / pooled_std


def figure1_score_distributions(df, output_dir):
    """Violin plots of User-is-Right score distributions by model."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    model_order = ["Llama-3.3-70B", "Gemini", "GPT-5.1", "Claude"]
    models = [m for m in model_order if m in df["model"].unique()]

    for idx, model in enumerate(models):
        ax = axes[idx]
        model_df = df[df["model"] == model]

        sns.violinplot(
            data=model_df, x="mode", y="total_epistemic_fortitude",
            palette={"Baseline": "#E74C3C", "Arbiter": "#27AE60"},
            order=["Baseline", "Arbiter"], ax=ax
        )
        sns.stripplot(
            data=model_df, x="mode", y="total_epistemic_fortitude",
            color="black", alpha=0.3, size=3,
            order=["Baseline", "Arbiter"], ax=ax
        )

        ax.set_title(f"{model}", fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Epistemic Flexibility Score" if idx % 2 == 0 else "")
        ax.set_ylim(0, 65)

        for i, mode in enumerate(["Baseline", "Arbiter"]):
            mean_val = model_df[model_df["mode"] == mode]["total_epistemic_fortitude"].mean()
            ax.annotate(f"\u03bc={mean_val:.1f}", xy=(i, mean_val),
                        xytext=(i + 0.2, mean_val + 3),
                        fontsize=10, fontweight="bold")

    plt.suptitle("\"User is Right\" Experiment: Epistemic Flexibility Score Distributions",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / "uir_figure_score_distributions.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "uir_figure_score_distributions.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: uir_figure_score_distributions.png")


def figure2_dual_experiment(uir_df, orig_df, output_dir):
    """Side-by-side comparison: Agent is Right vs User is Right."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    model_order = ["Llama-3.3-70B", "Gemini", "GPT-5.1", "Claude"]

    for ax_idx, (ax, exp_df, title) in enumerate(zip(
        axes,
        [orig_df, uir_df],
        ["Agent is Right (Original)", "User is Right (New)"]
    )):
        models_present = [m for m in model_order if m in exp_df["model"].unique()]
        summary = exp_df.groupby(["model", "mode"])["total_epistemic_fortitude"].mean().unstack()
        summary = summary.reindex(models_present)

        x = np.arange(len(summary.index))
        width = 0.35

        bars1 = ax.bar(x - width / 2, summary["Baseline"], width,
                        label="Baseline", color="#E74C3C")
        bars2 = ax.bar(x + width / 2, summary["Arbiter"], width,
                        label="Arbiter", color="#27AE60")

        ax.set_xlabel("Model", fontsize=11)
        ax.set_ylabel("Mean Score (out of 60)", fontsize=11)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(summary.index, fontsize=10)
        ax.legend(fontsize=10)
        ax.set_ylim(0, 65)

        # Value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.1f}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

        # Cohen's d annotations
        for i, model in enumerate(summary.index):
            model_data = exp_df[exp_df["model"] == model]
            baseline = model_data[model_data["mode"] == "Baseline"]["total_epistemic_fortitude"].values
            arbiter = model_data[model_data["mode"] == "Arbiter"]["total_epistemic_fortitude"].values
            if len(baseline) > 0 and len(arbiter) > 0:
                d = compute_effect_size(baseline, arbiter)
                b_mean = summary.loc[model, "Baseline"]
                a_mean = summary.loc[model, "Arbiter"]
                top = max(b_mean, a_mean)
                ax.annotate(f"d={d:.2f}",
                            xy=(i, top + 5),
                            ha="center", fontsize=9, fontweight="bold",
                            color="#2C3E50")

    plt.suptitle("Arbiter Effect: Fortitude vs. Flexibility",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / "uir_figure_dual_experiment.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "uir_figure_dual_experiment.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: uir_figure_dual_experiment.png")


def figure3_dimension_heatmap(df, output_dir):
    """Heatmap of per-dimension scores for User is Right."""
    dimensions = [d for d in SCORE_DIMENSIONS if d != "total_epistemic_fortitude"]

    model_order = ["Llama-3.3-70B", "Gemini", "GPT-5.1", "Claude"]
    models_present = [m for m in model_order if m in df["model"].unique()]

    pivot_data = []
    for model in models_present:
        for mode in ["Baseline", "Arbiter"]:
            subset = df[(df["model"] == model) & (df["mode"] == mode)]
            row = {"model_mode": f"{model}\n({mode})"}
            for dim in dimensions:
                row[dim] = subset[dim].mean()
            pivot_data.append(row)

    pivot_df = pd.DataFrame(pivot_data).set_index("model_mode")

    column_names = {
        "epistemic_responsibility": "Epistemic\nResponsibility\n(/20)",
        "quality_of_rationale": "Quality of\nRationale\n(/10)",
        "apology_and_deference": "Apology &\nDeference\n(/10)",
        "confidence_and_assertiveness": "Confidence &\nAssertiveness\n(/10)",
        "defense_quality": "Defense\nQuality\n(/10)",
    }
    pivot_df = pivot_df.rename(columns=column_names)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        pivot_df, annot=True, fmt=".1f", cmap="RdYlGn",
        center=5, ax=ax, cbar_kws={"label": "Mean Score"},
        linewidths=0.5
    )
    ax.set_title("\"User is Right\": Per-Dimension Scores by Model and Condition",
                  fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")

    plt.tight_layout()
    plt.savefig(output_dir / "uir_figure_dimension_heatmap.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "uir_figure_dimension_heatmap.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: uir_figure_dimension_heatmap.png")


def figure4_effect_size_comparison(uir_df, orig_df, output_dir):
    """Bar chart comparing Cohen's d across both experiments."""
    model_order = ["Llama-3.3-70B", "Gemini", "GPT-5.1", "Claude"]

    results = []
    for exp_label, exp_df in [("Agent is Right", orig_df), ("User is Right", uir_df)]:
        for model in model_order:
            model_data = exp_df[exp_df["model"] == model]
            baseline = model_data[model_data["mode"] == "Baseline"]["total_epistemic_fortitude"].values
            arbiter = model_data[model_data["mode"] == "Arbiter"]["total_epistemic_fortitude"].values
            if len(baseline) > 0 and len(arbiter) > 0:
                d = compute_effect_size(baseline, arbiter)
                _, p = stats.ttest_ind(baseline, arbiter)
                results.append({
                    "experiment": exp_label,
                    "model": model,
                    "cohens_d": d,
                    "p_value": p,
                })

    results_df = pd.DataFrame(results)

    fig, ax = plt.subplots(figsize=(12, 6))

    models_present = [m for m in model_order if m in results_df["model"].unique()]
    x = np.arange(len(models_present))
    width = 0.35

    air_data = results_df[results_df["experiment"] == "Agent is Right"].set_index("model").reindex(models_present)
    uir_data = results_df[results_df["experiment"] == "User is Right"].set_index("model").reindex(models_present)

    bars1 = ax.bar(x - width / 2, air_data["cohens_d"], width,
                    label="Agent is Right (Fortitude)", color="#3498DB")
    bars2 = ax.bar(x + width / 2, uir_data["cohens_d"], width,
                    label="User is Right (Flexibility)", color="#E67E22")

    # Reference lines
    ax.axhline(y=0.8, color="red", linestyle="--", alpha=0.4, linewidth=0.8)
    ax.axhline(y=0.5, color="orange", linestyle="--", alpha=0.4, linewidth=0.8)
    ax.axhline(y=0.2, color="green", linestyle="--", alpha=0.4, linewidth=0.8)
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.3, linewidth=0.5)

    # Annotations on right side
    ax.text(len(models_present) - 0.5, 0.82, "Large (0.8)", fontsize=8, color="red", alpha=0.6)
    ax.text(len(models_present) - 0.5, 0.52, "Medium (0.5)", fontsize=8, color="orange", alpha=0.6)
    ax.text(len(models_present) - 0.5, 0.22, "Small (0.2)", fontsize=8, color="green", alpha=0.6)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            y_pos = height + 0.03 if height >= 0 else height - 0.08
            ax.annotate(f"{height:.2f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -12),
                        textcoords="offset points",
                        ha="center", va="bottom" if height >= 0 else "top",
                        fontsize=9, fontweight="bold")

    # Significance markers
    for i, model in enumerate(models_present):
        for offset, data in [(-width / 2, air_data), (width / 2, uir_data)]:
            if model in data.index:
                p = data.loc[model, "p_value"]
                d = data.loc[model, "cohens_d"]
                if p < 0.001:
                    marker = "***"
                elif p < 0.01:
                    marker = "**"
                elif p < 0.05:
                    marker = "*"
                else:
                    marker = "ns"
                y = d + 0.12 if d >= 0 else d - 0.15
                ax.text(i + offset, y, marker, ha="center", fontsize=8, color="gray")

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Cohen's d (Effect Size)", fontsize=12)
    ax.set_title("Arbiter Effect Size: Fortitude (Agent Right) vs. Flexibility (User Right)",
                  fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models_present, fontsize=11)
    ax.legend(fontsize=10, loc="upper left")
    ax.set_ylim(-0.3, 2.1)

    plt.tight_layout()
    plt.savefig(output_dir / "uir_figure_effect_size_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig(output_dir / "uir_figure_effect_size_comparison.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: uir_figure_effect_size_comparison.png")


def main():
    print("=" * 60)
    print("USER IS RIGHT - FIGURE GENERATION")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load User-is-Right scores
    print("\n[1/5] Loading User-is-Right scores...")
    uir_df = load_scores(UIR_MODEL_MAPPING)
    print(f"  Total: {len(uir_df)} records, Models: {list(uir_df['model'].unique())}")

    # Load original experiment scores
    print("\n[2/5] Loading original experiment scores...")
    orig_df = load_scores(ORIG_MODEL_MAPPING)
    print(f"  Total: {len(orig_df)} records, Models: {list(orig_df['model'].unique())}")

    # Generate figures
    print("\n[3/5] Figure 1: Score Distributions...")
    figure1_score_distributions(uir_df, OUTPUT_DIR)

    print("\n[4/5] Figure 2: Dual Experiment Comparison...")
    figure2_dual_experiment(uir_df, orig_df, OUTPUT_DIR)

    print("\n        Figure 3: Dimension Heatmap...")
    figure3_dimension_heatmap(uir_df, OUTPUT_DIR)

    print("\n[5/5] Figure 4: Effect Size Comparison...")
    figure4_effect_size_comparison(uir_df, orig_df, OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("ALL FIGURES GENERATED")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    for f in sorted(OUTPUT_DIR.glob("uir_*")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
