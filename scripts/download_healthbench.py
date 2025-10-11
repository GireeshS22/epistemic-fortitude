"""Download HealthBench dataset from Hugging Face to local data/ folder.

This script downloads all available HealthBench datasets (main, consensus, hard)
and saves them as JSONL files in the data/healthbench/ directory.
"""

import os
import json
from pathlib import Path
from datasets import load_dataset


def download_healthbench():
    """Download HealthBench dataset and save as JSONL files."""

    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "healthbench"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("HealthBench Dataset Downloader")
    print("=" * 60)
    print(f"Downloading to: {data_dir}")
    print()

    try:
        # Load dataset from Hugging Face
        print("Loading dataset from Hugging Face: openai/healthbench")
        dataset = load_dataset("openai/healthbench")

        print(f"✓ Dataset loaded successfully")
        print(f"  Available splits: {list(dataset.keys())}")
        print()

        # Save each split as JSONL
        for split_name, split_data in dataset.items():
            output_file = data_dir / f"{split_name}.jsonl"

            print(f"Saving {split_name} split...")
            print(f"  - Examples: {len(split_data)}")
            print(f"  - Output: {output_file.name}")

            # Write JSONL file
            with open(output_file, 'w', encoding='utf-8') as f:
                for example in split_data:
                    json_line = json.dumps(example, ensure_ascii=False)
                    f.write(json_line + '\n')

            print(f"  ✓ Saved {len(split_data)} examples\n")

        print("=" * 60)
        print("✓ Download complete!")
        print("=" * 60)
        print(f"All files saved to: {data_dir}")
        print()

        # Summary
        print("Files created:")
        for jsonl_file in sorted(data_dir.glob("*.jsonl")):
            file_size = jsonl_file.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {jsonl_file.name} ({file_size:.2f} MB)")

    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify Hugging Face datasets library is installed")
        print("  3. Try running: poetry install")
        return 1

    return 0


if __name__ == "__main__":
    exit(download_healthbench())
