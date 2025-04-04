#!/usr/bin/env python3
"""
Script to precompute SUBTLEX word frequencies for all words in our wordlists.

This script reads the SUBTLEX-US frequency data, collects all unique words from
wordlists, extracts frequency data for these words, and saves the results to a
JSON file for faster loading.
"""

import os
import json
import time
import csv
from pathlib import Path
import sys
from typing import List, Dict, Set, Optional
import argparse

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists.frequencies import FrequencyDictionary

# Constants
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
WORDLISTS_DIR = DATA_DIR / "wordlists"
FREQ_DIR = DATA_DIR / "frequencies"
SUBTLEX_FILE = FREQ_DIR / "subtlex_us.txt"
OUTPUT_FILE = FREQ_DIR / "precomputed_frequencies.json"


def load_words_from_file(file_path: Path) -> List[str]:
    """
    Load words from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of words
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different JSON formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "words" in data:
            return data["words"]
        elif isinstance(data, dict):
            # Some wordlists store words as dictionary keys
            return list(data.keys())
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    
    return []


def collect_words_from_directory(directory: Path) -> Set[str]:
    """
    Recursively collect words from all JSON files in a directory.
    
    Args:
        directory: Directory to scan for JSON files
        
    Returns:
        Set of words
    """
    all_words = set()
    if not directory.exists():
        return all_words
    
    for file_path in directory.glob("**/*.json"):
        if file_path.is_file():
            words = load_words_from_file(file_path)
            all_words.update(words)
    
    return all_words


def load_subtlex_frequencies(subtlex_file: Path) -> Dict[str, Dict[str, float]]:
    """Load all frequencies from the SUBTLEX file."""
    frequencies = {}
    
    print(f"Loading SUBTLEX frequencies from {subtlex_file}...")
    with open(subtlex_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row['Word'].lower()
            
            # Store all relevant frequency metrics
            frequencies[word] = {
                'freq_count': int(float(row['FREQcount'])),  # Raw frequency count
                'cd_count': int(float(row['CDcount'])),      # Contextual diversity count (number of films/shows)
                'subtl_wf': float(row['SUBTLWF']),          # Word frequency per million words
                'lg10wf': float(row['Lg10WF']),             # Log10 of word frequency
                'subtl_cd': float(row['SUBTLCD']),          # Contextual diversity percentage
                'lg10cd': float(row['Lg10CD'])              # Log10 of contextual diversity
            }
    
    print(f"Loaded {len(frequencies)} words from SUBTLEX.")
    return frequencies


def extract_frequencies(words: List[str], freq_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Extract frequency data for the specified words."""
    result = {}
    found_count = 0
    
    for word in words:
        # Convert to lowercase for consistency
        lookup_word = word.lower()
        
        if lookup_word in freq_data:
            result[lookup_word] = freq_data[lookup_word]
            found_count += 1
            
        # Handle multi-word phrases separately
        elif ' ' in lookup_word:
            # For phrases, we'll compute frequencies when requested
            # rather than precomputing to avoid excessive combinations
            pass
    
    print(f"Found frequencies for {found_count} out of {len(words)} words ({found_count/len(words)*100:.1f}%)")
    return result


def save_frequencies(frequencies: Dict[str, Dict[str, float]], output_file: Path) -> None:
    """Save frequency data to a JSON file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(frequencies, f, ensure_ascii=False)
    
    file_size = output_file.stat().st_size / (1024 * 1024)  # Size in MB
    print(f"Saved {len(frequencies)} frequencies to {output_file}")
    print(f"File size: {file_size:.2f} MB")


def main():
    """Main function to precompute frequencies."""
    parser = argparse.ArgumentParser(description="Precompute frequencies for wordlists.")
    parser.add_argument("--output", type=str, default=OUTPUT_FILE, help="Output JSON file path")
    parser.add_argument("--subtlex", type=str, default=SUBTLEX_FILE, help="SUBTLEX input file path")
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Check if SUBTLEX file exists
    if not Path(args.subtlex).exists():
        print(f"Error: SUBTLEX file not found at {args.subtlex}")
        return
    
    # Collect words from all wordlists
    print("Collecting words from all wordlists...")
    all_words = set()
    
    # Historical wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "historical"))
    
    # Corpus wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "corpus"))
    
    # Categories wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "categories"))
    
    # Stop words
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "stop"))
    
    # Sort words alphabetically for consistency
    sorted_words = sorted(list(all_words))
    print(f"Collected {len(sorted_words)} unique words from all wordlists")
    
    # Load SUBTLEX frequencies
    freq_data = load_subtlex_frequencies(args.subtlex)
    
    # Include the top 1000 most frequent words from SUBTLEX regardless of our wordlists
    print("Adding top 1000 most frequent words from SUBTLEX...")
    top_words = sorted(
        [(word, data['subtl_wf']) for word, data in freq_data.items()],
        key=lambda x: x[1],
        reverse=True
    )[:1000]
    
    # Extract frequencies for our words
    frequencies = extract_frequencies(sorted_words, freq_data)
    
    added_count = 0
    for word, _ in top_words:
        if word not in frequencies:
            frequencies[word] = freq_data[word]
            added_count += 1
    
    print(f"Added {added_count} additional high-frequency words")
    
    # Save to file
    save_frequencies(frequencies, Path(args.output))
    
    # Check coverage against original file
    original_coverage = len(frequencies) / len(freq_data) * 100
    print(f"Precomputed file contains {original_coverage:.1f}% of the original SUBTLEX entries")
    
    elapsed_time = time.time() - start_time
    print(f"Precomputation complete in {elapsed_time:.2f} seconds.")
    print(f"Precomputed frequencies saved to {args.output}")


if __name__ == "__main__":
    main() 