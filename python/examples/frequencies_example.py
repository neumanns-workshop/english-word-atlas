#!/usr/bin/env python3
"""
Example script demonstrating how to use the SUBTLEX word frequency functionality.

This example shows how to:
1. Get frequency information for words
2. Compare words by frequency percentile
3. Filter wordlists by frequency
4. Work with frequency bands
5. Handle multi-word phrases
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import (
    get_wordlist,
    get_frequency,
    get_all_metrics,
    get_percentile,
    get_frequency_band,
    get_most_frequent,
    filter_by_frequency,
    FrequencyDictionary
)


def main():
    """Main function to demonstrate frequency functionality."""
    print("Loading SUBTLEX frequency data...")
    
    # Example 1: Get frequency for individual words
    print("\n=== Example 1: Word Frequencies ===")
    
    words = ["the", "cat", "computer", "astronomy", "discombobulated", "supercalifragilisticexpialidocious"]
    
    for word in words:
        freq = get_frequency(word, metric='subtl_wf')  # Frequency per million
        count = get_frequency(word, metric='freq_count')  # Raw count
        diversity = get_frequency(word, metric='subtl_cd')  # % of films/shows containing the word
        
        print(f"'{word}':")
        print(f"  Frequency (per million): {freq:.2f}")
        print(f"  Raw count: {int(count)}")
        print(f"  Contextual diversity: {diversity:.2f}%")
    
    # Example 2: Get all metrics for a word
    print("\n=== Example 2: All Frequency Metrics ===")
    
    metrics = get_all_metrics("dog")
    
    print("Frequency metrics for 'dog':")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")
    
    # Example 3: Compare words by frequency percentile
    print("\n=== Example 3: Frequency Percentiles ===")
    
    comparison_words = ["the", "and", "but", "however", "nevertheless", "notwithstanding"]
    
    print("Frequency percentiles (higher = more frequent):")
    for word in comparison_words:
        percentile = 100 - get_percentile(word)  # Invert for more intuitive percentile
        print(f"  '{word}': {percentile:.1f}%")
    
    # Example 4: Frequency bands (1 = most frequent, 5 = least frequent)
    print("\n=== Example 4: Frequency Bands ===")
    
    print("Frequency bands (1 = most frequent, 5 = least frequent):")
    for word in comparison_words:
        band = get_frequency_band(word, num_bands=5)
        print(f"  '{word}': Band {band}")
    
    # Example 5: Get most frequent words
    print("\n=== Example 5: Most Frequent Words ===")
    
    freq_dict = FrequencyDictionary()
    top_words = freq_dict.get_most_frequent(n=10)
    
    print("Top 10 most frequent words:")
    for i, (word, freq) in enumerate(top_words, 1):
        print(f"  {i}. '{word}': {freq:.2f} per million")
    
    # Example 6: Filter words by frequency
    print("\n=== Example 6: Filtering by Frequency ===")
    
    # Get stop words and filter by frequency
    stop_words = get_wordlist("stop-words-nltk")
    
    # Get medium frequency words (between 50 and 500 per million)
    medium_freq = filter_by_frequency(stop_words, min_freq=50.0, max_freq=500.0)
    high_freq = filter_by_frequency(stop_words, min_freq=500.0)
    low_freq = filter_by_frequency(stop_words, max_freq=50.0)
    
    print(f"NLTK stop words: {len(stop_words)} words")
    print(f"  High frequency (>500 per million): {len(high_freq)} words")
    print(f"  Medium frequency (50-500 per million): {len(medium_freq)} words")
    print(f"  Low frequency (<50 per million): {len(low_freq)} words")
    
    # Example 7: Working with multi-word phrases
    print("\n=== Example 7: Multi-Word Phrases ===")
    
    phrases = [
        "high school", 
        "New York", 
        "artificial intelligence",
        "machine learning"
    ]
    
    print("Frequency information for phrases:")
    for phrase in phrases:
        # For phrases, we average the frequencies of component words
        freq = get_frequency(phrase)
        print(f"  '{phrase}': {freq:.2f} per million")
        
        # Get all metrics to see component calculations
        metrics = get_all_metrics(phrase)
        if metrics:
            # Show the counts which are summed across words
            print(f"    Raw count (sum): {metrics.get('freq_count')}")
            # Show normalized metrics which are averaged
            print(f"    Log10WF (average): {metrics.get('lg10wf'):.2f}")
    
    # Example 8: Finding words by predicate
    print("\n=== Example 8: Finding Words by Predicate ===")
    
    # Find words that appear in at least 90% of films/shows
    def high_diversity(word, metrics):
        return metrics.get('subtl_cd', 0) > 90.0 and len(word) > 3
    
    diverse_words = freq_dict.find_words(high_diversity, limit=10)
    
    print("Words appearing in >90% of films/shows (first 10):")
    for word in diverse_words:
        cd = freq_dict.get_frequency(word, metric='subtl_cd')
        print(f"  '{word}': {cd:.1f}%")


if __name__ == "__main__":
    main() 