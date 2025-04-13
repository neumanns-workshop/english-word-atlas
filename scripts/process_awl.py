import json
from pathlib import Path
import os

# Define paths relative to the script location or project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "sources"

# Input filenames
INPUT_FILES = [f"AWL_SUBLIST_{i}.txt" for i in range(1, 11)]

# Output filename
OUTPUT_FILE = "AWL.json"

def main():
    """Parses AWL sublist files and creates a combined JSON source file."""
    unique_words = set()

    print("Processing AWL sublist files...")

    for filename in INPUT_FILES:
        input_path = SOURCE_DIR / filename
        if not input_path.exists():
            print(f"Warning: Input file not found: {input_path}")
            continue

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        unique_words.add(word)
            print(f"  - Processed {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if not unique_words:
        print("No words found in input files. Exiting.")
        return

    sorted_words = sorted(list(unique_words))
    output_path = SOURCE_DIR / OUTPUT_FILE

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sorted_words, f, indent=2)
        print(f"\nSuccessfully created {output_path}")
        print(f"Total unique AWL words found: {len(sorted_words)}")
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")

if __name__ == "__main__":
    main() 