"""
Splits the AFINN lexicon (data/sources/AFINN.txt) into separate JSON files
based on sentiment score (-5 to +5), saving them back into data/sources/.
"""

import json
from collections import defaultdict
from pathlib import Path
import sys
import os

def get_project_root() -> Path:
    """Gets the project root directory based on script location."""
    # Assumes the script is in a subdirectory (like 'scripts') of the project root
    return Path(__file__).parent.parent

def generate_output_filename(score: int) -> str:
    """Generates the filename based on the sentiment score."""
    if score == 0:
        return "AFINN_NEUT_0.json"
    elif score < 0:
        return f"AFINN_NEG_{abs(score)}.json"
    else: # score > 0
        return f"AFINN_POS_{score}.json"

def split_afinn_lexicon():
    """Reads AFINN.txt and writes out 11 JSON files based on score."""
    project_root = get_project_root()
    sources_dir = project_root / "data" / "sources"
    input_file = sources_dir / "AFINN.txt"
    
    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}", file=sys.stderr)
        sys.exit(1)

    if not sources_dir.exists():
        print(f"Creating output directory: {sources_dir}")
        sources_dir.mkdir(parents=True, exist_ok=True) # Create if it doesn't exist

    words_by_score = defaultdict(list)
    line_count = 0
    error_count = 0

    print(f"Reading and parsing {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                line = line.strip()
                if not line:
                    continue # Skip empty lines
                
                parts = line.split('	')
                if len(parts) != 2:
                    print(f"Warning: Skipping malformed line {line_count}: '{line}'", file=sys.stderr)
                    error_count += 1
                    continue
                
                word = parts[0].strip()
                score_str = parts[1].strip()
                
                try:
                    score = int(score_str)
                    if not (-5 <= score <= 5):
                        raise ValueError("Score out of range")
                    words_by_score[score].append(word)
                except ValueError:
                    print(f"Warning: Skipping line {line_count} with invalid score: '{line}'", file=sys.stderr)
                    error_count += 1
                    continue
                    
    except IOError as e:
        print(f"Error reading input file {input_file}: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Processed {line_count} lines with {error_count} errors.")
    print(f"Found words for scores: {sorted(words_by_score.keys())}")

    # Write output files
    print("Writing output JSON files...")
    files_written = 0
    for score in range(-5, 6): # Iterate through all possible scores
        if score in words_by_score:
            word_list = sorted(list(set(words_by_score[score]))) # Sort and ensure unique
            output_filename = generate_output_filename(score)
            output_path = sources_dir / output_filename
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(word_list, f, indent=2)
                print(f"  - Created {output_path} ({len(word_list)} words)")
                files_written += 1
            except IOError as e:
                print(f"Error writing output file {output_path}: {e}", file=sys.stderr)
        else:
             print(f"  - No words found for score {score}. Skipping file generation.")

    print(f"Finished writing {files_written} JSON files to {sources_dir}")

if __name__ == "__main__":
    # Ensure the script runs from the project root or adjusts paths accordingly
    # A simple check: does 'data/sources' exist relative to CWD?
    if not Path("data/sources").exists():
         print("Warning: 'data/sources' not found in current directory.", file=sys.stderr)
         print("Attempting to run from project root based on script location.", file=sys.stderr)
         # Note: get_project_root() handles path finding if script is in 'scripts/'
         
    split_afinn_lexicon() 