#!/usr/bin/env python3
"""
Example demonstrating the use of the frequency functionality in the wordlists package.
This example shows how to use the FrequencyDictionary class to get frequency data
for words and phrases from the SUBTLEX-US corpus.
"""

import sys
import json
from pathlib import Path
import time

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists.frequencies import FrequencyDictionary

# Constants
DATA_DIR = Path(__file__).parent.parent.parent / "data"
WORDLISTS_DIR = DATA_DIR / "wordlists"

def main():
    """Main example function."""
    # Initialize the frequency dictionary
    # It will automatically use the precomputed data if available
    print("Initializing frequency dictionary...")
    start_time = time.time()
    freq_dict = FrequencyDictionary()
    
    # Load the data
    freq_dict.load()
    load_time = time.time() - start_time
    print(f"Loaded frequency data in {load_time:.4f} seconds\n")
    
    # Example 1: Get frequency for a single word
    word = "the"
    freq = freq_dict.get_frequency(word)
    percentile = freq_dict.get_percentile(word)
    band = freq_dict.get_frequency_band(word)
    
    print(f"Example 1: Single word frequency")
    print(f"Word: '{word}'")
    print(f"  Frequency per million: {freq:.2f}")
    print(f"  Percentile: {percentile:.1f}")
    print(f"  Frequency band (1-5): {band}")
    
    # Example 2: Compare different metrics
    word = "computer"
    metrics = freq_dict.get_all_metrics(word)
    
    print(f"\nExample 2: All metrics for a word")
    print(f"Word: '{word}'")
    print(f"  Raw frequency count: {metrics.get('freq_count', 0)}")
    print(f"  Contextual diversity count: {metrics.get('cd_count', 0)}")
    print(f"  Frequency per million: {metrics.get('subtl_wf', 0):.2f}")
    print(f"  Log10 frequency: {metrics.get('lg10wf', 0):.2f}")
    print(f"  Contextual diversity %: {metrics.get('subtl_cd', 0):.2f}")
    print(f"  Log10 contextual diversity: {metrics.get('lg10cd', 0):.2f}")
    
    # Example 3: Multi-word phrases
    phrase = "computer science"
    freq = freq_dict.get_frequency(phrase)
    
    print(f"\nExample 3: Multi-word phrase")
    print(f"Phrase: '{phrase}'")
    print(f"  Frequency per million: {freq:.2f}")
    
    # Example 4: Get most frequent words
    print(f"\nExample 4: Top 10 most frequent words")
    top_words = freq_dict.get_most_frequent(10)
    for i, (word, freq) in enumerate(top_words, 1):
        print(f"  {i}. '{word}': {freq:.2f} per million")
    
    # Example 5: Compare frequencies across a wordlist
    print(f"\nExample 5: Frequency analysis of Basic English words")
    # Load Basic English words directly from file
    basic_english_file = WORDLISTS_DIR / "historical" / "ogden" / "basic" / "comprehensive.json"
    with open(basic_english_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        basic_english = data.get("words", [])
    
    # Sample the first 10 words for brevity
    sample_words = basic_english[:10]
    
    print(f"Analyzing {len(sample_words)} sample words from Basic English...")
    for word in sample_words:
        freq = freq_dict.get_frequency(word)
        band = freq_dict.get_frequency_band(word)
        print(f"  '{word}': {freq:.2f} per million (band {band})")
    
    # Calculate average frequency
    frequencies = [freq_dict.get_frequency(word) for word in basic_english]
    avg_freq = sum(frequencies) / len(frequencies)
    print(f"\nAverage frequency of Basic English words: {avg_freq:.2f} per million")
    
    # Count words in each frequency band
    bands = [freq_dict.get_frequency_band(word) for word in basic_english]
    band_counts = {band: bands.count(band) for band in range(1, 6)}
    print("Frequency band distribution:")
    for band, count in band_counts.items():
        percentage = (count / len(basic_english)) * 100
        print(f"  Band {band}: {count} words ({percentage:.1f}%)")
    
    # Count words with zero frequency (not found in SUBTLEX)
    zero_freq = sum(1 for f in frequencies if f == 0)
    zero_percentage = (zero_freq / len(basic_english)) * 100
    print(f"Words not found in SUBTLEX: {zero_freq} ({zero_percentage:.1f}%)")


if __name__ == "__main__":
    main() 