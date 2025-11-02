"""Calculate theme breakdown for n=300"""
import json
from pathlib import Path
from collections import defaultdict
import statistics

# Paths
baseline_dir = Path(r"C:\Users\ADMIN\OneDrive\Documents\SNUC\Consistency-Preserving-Architectures\epistemic_fortitude\logs\experiments\swebench_langgraph_baseline")
arbiter_dir = Path(r"C:\Users\ADMIN\OneDrive\Documents\SNUC\Consistency-Preserving-Architectures\epistemic_fortitude\logs\experiments\swebench_langgraph_arbiter")

def get_theme_and_score(conv_file, scores_dir):
    """Extract theme and epistemic fortitude score"""
    try:
        # Load conversation file
        with open(conv_file, 'r', encoding='utf-8') as f:
            conv_data = json.load(f)

        theme = conv_data.get('theme', 'unknown')

        # Load epistemic score
        score_file = scores_dir / "epistemic_scores" / f"{conv_file.stem}.json"
        if not score_file.exists():
            return theme, None

        with open(score_file, 'r', encoding='utf-8') as f:
            score_data = json.load(f)

        ef_score = score_data.get('scores', {}).get('total_epistemic_fortitude', None)

        return theme, ef_score
    except Exception as e:
        print(f"Error processing {conv_file.name}: {e}")
        return None, None

# Collect data
baseline_data = defaultdict(list)  # theme -> list of EF scores
arbiter_data = defaultdict(list)

print("Processing baseline conversations...")
for conv_file in baseline_dir.glob("*.json"):
    if conv_file.stem in ['conversations_summary', 'epistemic_summary', 'metadata', 'errors']:
        continue
    theme, score = get_theme_and_score(conv_file, baseline_dir)
    if theme is not None and score is not None:
        baseline_data[theme].append(score)

print("Processing arbiter conversations...")
for conv_file in arbiter_dir.glob("*.json"):
    if conv_file.stem in ['conversations_summary', 'epistemic_summary', 'metadata', 'errors']:
        continue
    theme, score = get_theme_and_score(conv_file, arbiter_dir)
    if theme is not None and score is not None:
        arbiter_data[theme].append(score)

print("\n" + "="*80)
print("THEME-BY-THEME PERFORMANCE (n=300)")
print("="*80)

# Map theme names
theme_names = {
    'django/django': 'Django',
    'astropy/astropy': 'Astropy',
    'matplotlib/matplotlib': 'Matplotlib',
    'sympy/sympy': 'SymPy',
    'scikit-learn/scikit-learn': 'Scikit-learn',
    'pytest-dev/pytest': 'Pytest',
    'sphinx-doc/sphinx': 'Sphinx',
    'pylint-dev/pylint': 'Pylint',
    'psf/requests': 'Requests',
    'pallets/flask': 'Flask',
    'pydata/xarray': 'Xarray',
    'mwaskom/seaborn': 'Seaborn'
}

total_baseline = 0
total_arbiter = 0

print("\nPer-Theme Statistics:")
print()

for theme in sorted(baseline_data.keys()):
    baseline_scores = baseline_data[theme]
    arbiter_scores = arbiter_data.get(theme, [])

    if len(baseline_scores) == 0:
        continue

    n = len(baseline_scores)
    baseline_mean = statistics.mean(baseline_scores)
    baseline_std = statistics.stdev(baseline_scores) if len(baseline_scores) > 1 else 0

    arbiter_mean = statistics.mean(arbiter_scores) if arbiter_scores else 0
    arbiter_std = statistics.stdev(arbiter_scores) if len(arbiter_scores) > 1 else 0

    improvement_pct = ((arbiter_mean - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0

    theme_display = theme_names.get(theme, theme)

    print(f"{theme_display:15s} & {n:3d} & {baseline_mean:.1f} ({baseline_std:.1f}) & {arbiter_mean:.1f} ({arbiter_std:.1f}) & {improvement_pct:+.1f}\\% \\\\")

    total_baseline += len(baseline_scores)
    total_arbiter += len(arbiter_scores)

print(f"\nTotal conversations: Baseline={total_baseline}, Arbiter={total_arbiter}")

# Show percentage breakdown
print("\n\nPercentage Distribution:")
for theme in sorted(baseline_data.keys()):
    n = len(baseline_data[theme])
    pct = n / total_baseline * 100
    theme_display = theme_names.get(theme, theme)
    print(f"{theme_display:15s}: {n:3d} ({pct:5.1f}%)")
