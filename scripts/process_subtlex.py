import json
from pathlib import Path
import os
import sys
import csv

# Define paths relative to the script location or project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
FREQ_DIR = PROJECT_ROOT / "data" / "frequencies" # Input and output dir

# Input and Output filenames
INPUT_FILE = "subtlex_us.txt"
OUTPUT_FILE = "word_frequencies.json"

# Column names to extract
WORD_COLUMN = "Word" # Assumed column name for the word
FREQ_COLUMN = "SUBTLWF" # Assumed column name for SUBTLEX Word Frequency

def main():
    """Parses SUBTLEX_US file and creates a JSON frequency map."""
    word_freqs = {}
    input_path = FREQ_DIR / INPUT_FILE
    output_path = FREQ_DIR / OUTPUT_FILE

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Processing {INPUT_FILE}...")
    line_count = 0
    processed_count = 0
    error_count = 0

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            # Use csv.reader for robust handling of potential quoting/escapes
            # Specify tab as the delimiter
            reader = csv.reader(f, delimiter='\t')
            
            # Read header and find column indices
            header = next(reader)
            line_count += 1
            try:
                word_idx = header.index(WORD_COLUMN)
                freq_idx = header.index(FREQ_COLUMN)
            except ValueError as e:
                print(f"Error: Required column '{e}' not found in header: {header}")
                sys.exit(1)

            # Process data lines
            for row in reader:
                line_count += 1
                if len(row) <= max(word_idx, freq_idx):
                    print(f"Warning: Skipping malformed line {line_count} (too few columns): {row}")
                    error_count += 1
                    continue

                word = row[word_idx].strip().lower()
                freq_str = row[freq_idx].strip()

                if not word:
                    # print(f"Warning: Skipping line {line_count} (empty word).")
                    error_count += 1
                    continue
                    
                try:
                    frequency = float(freq_str)
                except ValueError:
                    print(f"Warning: Skipping line {line_count} (invalid frequency '{freq_str}'): {row}")
                    error_count += 1
                    continue

                # Store frequency, keeping the highest if word is duplicated
                if word not in word_freqs or frequency > word_freqs[word]:
                     word_freqs[word] = frequency
                processed_count +=1 # Count successfully processed entries

    except Exception as e:
        print(f"Error processing {INPUT_FILE} around line {line_count}: {e}")
        sys.exit(1)

    print("\n--- Processing Summary ---")
    print(f"Total lines read (incl. header): {line_count}")
    print(f"Successfully processed entries: {processed_count}")
    print(f"Entries skipped due to errors: {error_count}")
    print(f"Final unique words with frequency: {len(word_freqs)}")

    if not word_freqs:
        print("\nNo frequency data extracted. Exiting without writing file.")
        sys.exit(1)

    # Sort by word for consistent output (optional, dicts are unordered)
    # sorted_freqs = dict(sorted(word_freqs.items()))

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            # json.dump(sorted_freqs, f, indent=2) # Use sorted if desired
            json.dump(word_freqs, f, indent=2) # Save as is
        print(f"\nSuccessfully created/updated {output_path}")
    except Exception as e:
        print(f"\nError writing output file {output_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 