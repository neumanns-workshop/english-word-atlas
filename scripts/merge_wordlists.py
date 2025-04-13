#!/usr/bin/env python3
"""
Merges the base word index with words from specified source lists
found in the data/sources directory.
"""

import json
from pathlib import Path
import argparse
import sys
from typing import Dict, List, Union # Added Union

def load_json_file(file_path: Path) -> Union[Dict, List, None]: # Type hint updated
    """Load a JSON file, returning None on error."""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return None

def merge_wordlists(data_dir: Path, output_file: Path, source_glob: str = '*.json'):
    """Merges the base index with words from source lists."""
    print(f"Using data directory: {data_dir}")

    # 1. Load base word index
    base_index_path = data_dir / "word_index.json"
    base_index = load_json_file(base_index_path)
    if base_index is None or not isinstance(base_index, dict):
        print(f"Error: Could not load or parse base word index from {base_index_path}", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(base_index)} words from base index {base_index_path.name}")
    all_words = set(base_index.keys())

    # 2. Find and load source lists
    sources_dir = data_dir / "sources"
    if not sources_dir.is_dir():
        print(f"Error: Sources directory not found: {sources_dir}", file=sys.stderr)
        sys.exit(1)

    # Use rglob for recursive search
    source_files = list(sources_dir.rglob(source_glob))
    if not source_files:
        print(f"Warning: No source files found matching '{source_glob}' recursively in {sources_dir}", file=sys.stderr)
        # Continue without adding sources if none are found matching the glob
    else:
        print(f"Found {len(source_files)} source files recursively in {sources_dir} matching '{source_glob}':")

    sources_loaded_count = 0
    for source_path in sorted(source_files): # Sort for deterministic order
        print(f"  - Loading {source_path.name}...", end='')
        source_data = load_json_file(source_path)
        if source_data is not None and isinstance(source_data, list):
            # Ensure words in source list are strings
            valid_source_words = {str(word) for word in source_data if isinstance(word, str)}
            if len(valid_source_words) != len(source_data):
                 print(f" WARNING (loaded {len(valid_source_words)} valid strings out of {len(source_data)} items)", end='')

            new_words_from_source = len(valid_source_words - all_words)
            all_words.update(valid_source_words)
            print(f" OK ({len(valid_source_words)} valid words, {new_words_from_source} new)")
            sources_loaded_count += 1
        else:
            print(f" FAILED (invalid format or load error)")

    if sources_loaded_count == 0 and source_files:
         print(f"Warning: Failed to load any valid source lists.", file=sys.stderr)


    # 3. Sort unique words and create new index
    # Sort alphabetically for consistency
    sorted_unique_words = sorted(list(all_words))
    new_index = {word: idx for idx, word in enumerate(sorted_unique_words)}
    print(f"\nTotal unique words after merge: {len(new_index)}")

    # 4. Save the new index
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_index, f, indent=2) # Use indent=2 for readability
        print(f"Successfully saved combined word index to: {output_file}")
    except Exception as e:
        print(f"Error saving combined index to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge base word index with words from source lists.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "data_dir",
        type=Path,
        help="Path to the main data directory containing word_index.json and the sources/ subdirectory."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        # Default to overwriting the original index file
        default=None,
        help="Path to save the combined word index file. Defaults to overwriting the original data/word_index.json."
    )
    parser.add_argument(
        "-s", "--source-glob",
        type=str,
        default="*.json",
        help="Glob pattern to match source list files within the sources/ directory."
    )

    args = parser.parse_args()

    # Basic validation
    if not args.data_dir.is_dir():
        print(f"Error: Specified data directory does not exist or is not a directory: {args.data_dir}", file=sys.stderr)
        sys.exit(1)

    # Determine output file path
    output_path = args.output
    if output_path is None:
        output_path = args.data_dir / "word_index.json"
        print(f"Output path not specified. Defaulting to overwrite: {output_path}")
    elif output_path.is_dir():
        print(f"Error: Specified output path is a directory: {output_path}", file=sys.stderr)
        sys.exit(1)

    merge_wordlists(args.data_dir, output_path, args.source_glob) 