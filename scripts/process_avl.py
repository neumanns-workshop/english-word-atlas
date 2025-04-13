import json
from pathlib import Path
import os
import sys

# Define paths relative to the script location or project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "sources"

# Input and Output filenames
INPUT_FILE = "AVL.txt"
OUTPUT_FILE = "AVL.json"

def main():
    """Parses AVL.txt file, reports counts, and creates a combined JSON source file."""
    unique_words = set()
    total_processed_count = 0
    duplicate_count = 0
    malformed_count = 0

    input_path = SOURCE_DIR / INPUT_FILE
    output_path = SOURCE_DIR / OUTPUT_FILE

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Processing {INPUT_FILE}...")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            header = f.readline() # Read and discard header
            if not header:
                print("Warning: Input file might be empty.")
                # Optionally check header format if needed
                # expected_header_start = "Number \t Word \t"
                # if not header.startswith(expected_header_start):
                #    print(f"Warning: Unexpected header format: {header.strip()}")

            line_num = 1 # Start counting after header
            for line in f:
                line_num += 1
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    word = parts[1].strip().lower()
                    if word:
                        total_processed_count += 1
                        if word in unique_words:
                            duplicate_count += 1
                            # Optional: print first few duplicates found
                            # if duplicate_count <= 5:
                            #     print(f"  - Duplicate found on line {line_num}: '{word}'")
                            # elif duplicate_count == 6:
                            #     print("  - (Reporting only first 5 duplicates)")
                        else:
                            unique_words.add(word)
                else:
                    if line.strip(): # Report non-empty lines with too few columns
                         malformed_count += 1
                         print(f"Warning: Skipping malformed line {line_num}: {line.strip()}")

    except Exception as e:
        print(f"Error processing {INPUT_FILE} line {line_num}: {e}")
        sys.exit(1)

    print("\n--- Processing Summary ---")
    print(f"Total non-empty words processed (col 2): {total_processed_count}")
    print(f"Duplicate words found (col 2): {duplicate_count}")
    print(f"Malformed/skipped lines: {malformed_count}")
    print(f"Final unique words: {len(unique_words)}")

    if not unique_words:
        print("\nNo unique words extracted. Exiting without writing file.")
        sys.exit(1)

    sorted_words = sorted(list(unique_words))

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sorted_words, f, indent=2)
        print(f"\nSuccessfully created/updated {output_path}")
    except Exception as e:
        print(f"\nError writing output file {output_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 