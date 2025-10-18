"""Explore SWE-bench dataset and select suitable examples for epistemic fortitude testing.

This script:
1. Downloads SWE-bench Lite dataset (500 verified examples)
2. Saves complete dataset to data/swebench/swebench_lite_complete.json
3. Analyzes dataset structure and content
4. Filters for suitable examples (Python, medium complexity)
5. Saves filtered examples to data/swebench/swebench_filtered.json

Usage:
    poetry run python scripts/explore_swebench.py
"""

import json
import sys
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from datasets import load_dataset
except ImportError:
    print("❌ Error: 'datasets' package not installed")
    print("Run: poetry install")
    sys.exit(1)


def download_swebench():
    """Download SWE-bench Lite dataset from HuggingFace."""
    print("\n" + "="*70)
    print("DOWNLOADING SWE-BENCH LITE DATASET")
    print("="*70)
    print("\nDataset: princeton-nlp/SWE-bench_Lite")
    print("Size: 500 verified examples")
    print("Source: Real GitHub issues with test suites\n")

    try:
        dataset = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
        print(f"✅ Downloaded {len(dataset)} examples\n")
        return dataset
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify HuggingFace access")
        print("3. Try: pip install --upgrade datasets")
        sys.exit(1)


def analyze_dataset_structure(dataset) -> None:
    """Print dataset structure and field information."""
    print("="*70)
    print("DATASET STRUCTURE")
    print("="*70)

    # Get first example
    example = dataset[0]

    print("\nAvailable fields:")
    for i, (key, value) in enumerate(example.items(), 1):
        value_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        print(f"{i}. {key:20s} - {type(value).__name__:15s} - {value_preview}")

    print("\n" + "="*70)
    print("EXAMPLE RECORD")
    print("="*70)

    # Print a sample record for inspection
    print(f"\nInstance ID: {example.get('instance_id', 'N/A')}")
    print(f"Repo: {example.get('repo', 'N/A')}")
    print(f"\nProblem Statement:")
    print("-"*70)
    problem = example.get('problem_statement', example.get('text', 'N/A'))
    print(problem[:500] + "..." if len(problem) > 500 else problem)
    print("-"*70)

    # Check for hints
    if 'hints_text' in example and example['hints_text']:
        print(f"\nHints: {example['hints_text'][:200]}...")

    print()


def get_programming_language(repo: str, problem: str) -> str:
    """Infer programming language from repo name and problem statement."""
    repo_lower = repo.lower()
    problem_lower = problem.lower()

    # Check repo name patterns
    if 'django' in repo_lower or 'flask' in repo_lower or 'python' in repo_lower:
        return 'python'
    if 'spring' in repo_lower or '.java' in problem_lower:
        return 'java'
    if 'react' in repo_lower or 'node' in repo_lower or '.js' in problem_lower:
        return 'javascript'
    if '.cpp' in problem_lower or '.c' in problem_lower:
        return 'c++'
    if '.go' in problem_lower:
        return 'go'
    if '.rs' in problem_lower:
        return 'rust'

    # Check problem text for language indicators
    if any(kw in problem_lower for kw in ['python', 'pip', 'pytest', 'django', 'flask']):
        return 'python'
    if any(kw in problem_lower for kw in ['java', 'maven', 'gradle']):
        return 'java'
    if any(kw in problem_lower for kw in ['javascript', 'npm', 'node', 'react']):
        return 'javascript'

    return 'unknown'


def analyze_dataset_statistics(dataset) -> Dict[str, Any]:
    """Analyze dataset statistics and distributions."""
    print("="*70)
    print("DATASET STATISTICS")
    print("="*70)

    languages = []
    repos = []
    problem_lengths = []

    for example in dataset:
        # Get language
        problem = example.get('problem_statement', example.get('text', ''))
        repo = example.get('repo', '')

        lang = get_programming_language(repo, problem)
        languages.append(lang)
        repos.append(repo)
        problem_lengths.append(len(problem.split()))

    # Language distribution
    lang_counts = Counter(languages)
    print("\n📊 Language Distribution:")
    for lang, count in lang_counts.most_common():
        percentage = (count / len(dataset)) * 100
        print(f"  {lang:15s}: {count:3d} ({percentage:5.1f}%)")

    # Problem length distribution
    avg_length = sum(problem_lengths) / len(problem_lengths)
    print(f"\n📝 Problem Statement Length:")
    print(f"  Average: {avg_length:.0f} words")
    print(f"  Min: {min(problem_lengths)} words")
    print(f"  Max: {max(problem_lengths)} words")

    # Repository diversity
    unique_repos = len(set(repos))
    print(f"\n🗂️  Repository Diversity:")
    print(f"  Total examples: {len(dataset)}")
    print(f"  Unique repos: {unique_repos}")

    # Top repositories
    repo_counts = Counter(repos)
    print(f"\n🔝 Top 10 Repositories:")
    for repo, count in repo_counts.most_common(10):
        print(f"  {repo:40s}: {count:2d}")

    return {
        "languages": lang_counts,
        "avg_problem_length": avg_length,
        "problem_lengths": problem_lengths,
        "unique_repos": unique_repos
    }


def filter_suitable_examples(dataset, stats: Dict[str, Any]) -> List[Dict]:
    """Filter for examples suitable for epistemic fortitude testing.

    Criteria:
    - Python language (most common, easiest to understand)
    - Medium complexity (50-500 words)
    - Clear problem statement (not too vague)
    """
    print("\n" + "="*70)
    print("FILTERING SUITABLE EXAMPLES")
    print("="*70)

    print("\nCriteria:")
    print("  ✓ Python language")
    print("  ✓ Problem length: 50-500 words (medium complexity)")
    print("  ✓ Has clear problem statement")

    suitable = []

    for example in dataset:
        problem = example.get('problem_statement', example.get('text', ''))
        repo = example.get('repo', '')

        # Check language
        lang = get_programming_language(repo, problem)
        if lang != 'python':
            continue

        # Check length
        word_count = len(problem.split())
        if word_count < 50 or word_count > 500:
            continue

        # Check has content
        if not problem or len(problem.strip()) < 100:
            continue

        suitable.append(dict(example))

    print(f"\n✅ Found {len(suitable)} suitable examples out of {len(dataset)}")
    print(f"   Filter rate: {(len(suitable)/len(dataset))*100:.1f}%")

    return suitable


def save_complete_dataset(dataset, output_dir: Path) -> None:
    """Save the complete SWE-bench Lite dataset to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert dataset to list of dictionaries
    complete_data = [dict(example) for example in dataset]
    
    output_file = output_dir / "swebench_lite_complete.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Complete dataset saved to: {output_file}")
    print(f"   Examples: {len(complete_data)}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def save_filtered_examples(examples: List[Dict], output_dir: Path) -> None:
    """Save filtered examples to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "swebench_filtered.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Filtered examples saved to: {output_file}")
    print(f"   Examples: {len(examples)}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def print_sample_examples(examples: List[Dict], num_samples: int = 3) -> None:
    """Print sample examples for manual inspection."""
    print("\n" + "="*70)
    print(f"SAMPLE EXAMPLES (showing {num_samples})")
    print("="*70)

    for i, example in enumerate(examples[:num_samples], 1):
        print(f"\n{'─'*70}")
        print(f"Example {i}/{num_samples}")
        print(f"{'─'*70}")
        print(f"Instance ID: {example.get('instance_id', 'N/A')}")
        print(f"Repository: {example.get('repo', 'N/A')}")

        problem = example.get('problem_statement', example.get('text', ''))
        words = len(problem.split())
        print(f"Problem ({words} words):")
        print("-"*70)
        print(problem[:400] + "..." if len(problem) > 400 else problem)
        print("-"*70)


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("SWE-BENCH DATASET EXPLORATION")
    print("="*70)
    print("\nThis script downloads and analyzes SWE-bench for epistemic fortitude testing")

    # Create data directory
    data_dir = Path(__file__).parent.parent / "data" / "swebench"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Download dataset
    dataset = download_swebench()

    # Save complete dataset
    save_complete_dataset(dataset, data_dir)

    # Analyze structure
    analyze_dataset_structure(dataset)

    # Analyze statistics
    stats = analyze_dataset_statistics(dataset)

    # Filter suitable examples
    suitable_examples = filter_suitable_examples(dataset, stats)

    # Save filtered examples
    save_filtered_examples(suitable_examples, data_dir)

    # Print samples
    print_sample_examples(suitable_examples, num_samples=3)

    # Final summary
    print("\n" + "="*70)
    print("EXPLORATION COMPLETE")
    print("="*70)
    print(f"\n📂 Dataset location: {data_dir}")
    print(f"📄 Complete dataset: {data_dir / 'swebench_lite_complete.json'}")
    print(f"📄 Filtered examples: {data_dir / 'swebench_filtered.json'}")
    print(f"✅ Ready for: {len(suitable_examples)} experiments")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review sample examples above")
    print("2. Check filtered examples file for quality")
    print("3. Proceed to Phase 2: Contradiction Engineering")
    print()


if __name__ == "__main__":
    main()
