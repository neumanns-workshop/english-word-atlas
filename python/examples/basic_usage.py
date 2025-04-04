#!/usr/bin/env python3
"""
Basic usage examples for the wordlists package.
This script demonstrates the core functionality of the package.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the local package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import (
    get_wordlist,
    match_pattern,
    is_in_list,
    create_stop_word_list,
    analyze_overlap,
    compare_wordlists
)


def main():
    """Demonstrate basic usage of the wordlists package."""
    print("Wordlists Package Examples\n")
    
    # Example 1: Get complete word lists
    print("=== Example 1: Get Complete Word Lists ===")
    swadesh_100 = get_wordlist("swadesh-100")
    basic_english = get_wordlist("basic-english")
    nltk_stop_words = get_wordlist("stop-words-nltk")
    
    print(f"Swadesh 100 word list has {len(swadesh_100)} words")
    print(f"Basic English word list has {len(basic_english)} words")
    print(f"NLTK stop words list has {len(nltk_stop_words)} words")
    print(f"First 10 words in Swadesh 100: {swadesh_100[:10]}")
    print()
    
    # Example 2: Check if words exist in lists
    print("=== Example 2: Check Word Membership ===")
    test_words = ["water", "computer", "dog", "the", "and", "heart"]
    for list_name in ["swadesh-100", "basic-english", "stop-words-nltk"]:
        results = is_in_list(test_words, list_name)
        print(f"In {list_name}:")
        for word, exists in results.items():
            print(f"  {word}: {exists}")
    print()
    
    # Example 3: Find words matching patterns
    print("=== Example 3: Pattern Matching ===")
    water_pattern = r"water"
    water_words = match_pattern(water_pattern, ["swadesh-100", "basic-english"])
    print(f"Words containing 'water': {water_words}")
    
    animal_pattern = r"^(dog|cat|bird)"
    animal_words = match_pattern(animal_pattern, ["basic-english"])
    print(f"Animal words (dog/cat/bird): {animal_words}")
    print()
    
    # Example 4: Create custom stop word lists
    print("=== Example 4: Custom Stop Word Lists ===")
    custom_stopwords = create_stop_word_list({
        "base": "stop-words-nltk",
        "include": ["custom", "specific", "words"],
        "exclude": ["not", "no", "nor"]
    })
    
    # Verify exclusions
    print("Verification of exclusions:")
    for word in ["not", "no", "nor"]:
        print(f"  '{word}' in custom stop words: {word in custom_stopwords}")
    
    # Verify inclusions
    print("Verification of inclusions:")
    for word in ["custom", "specific", "words"]:
        print(f"  '{word}' in custom stop words: {word in custom_stopwords}")
    
    print(f"Custom stop word list has {len(custom_stopwords)} words")
    print(f"Sample: {custom_stopwords[:10]}")
    print()
    
    # Example 5: Analyze overlap between word lists
    print("=== Example 5: Overlap Analysis ===")
    overlap = analyze_overlap(set(swadesh_100), set(basic_english))
    print(f"Overlap between Swadesh 100 and Basic English:")
    print(f"  {overlap['words']} words")
    print(f"  {overlap['percent_of_first']:.1f}% of Swadesh")
    print(f"  {overlap['percent_of_second']:.1f}% of Basic English")
    print()
    
    # Example 6: Detailed comparison between word lists
    print("=== Example 6: Detailed Comparison ===")
    comparison = compare_wordlists(
        set(swadesh_100), 
        set(nltk_stop_words),
        name1="swadesh", 
        name2="nltk"
    )
    
    print(f"Comparison between Swadesh 100 and NLTK stop words:")
    print(f"  Total unique words: {comparison['total_unique_words']}")
    print(f"  Shared words: {comparison['shared_words']['count']} ({comparison['shared_words']['percent_of_total']:.1f}% of total)")
    print(f"  Words only in Swadesh: {comparison['only_in_swadesh']['count']} ({comparison['only_in_swadesh']['percent_of_first']:.1f}%)")
    print(f"  Words only in NLTK: {comparison['only_in_nltk']['count']} ({comparison['only_in_nltk']['percent_of_second']:.1f}%)")
    print(f"  Jaccard similarity: {comparison['jaccard_similarity']:.3f}")
    print(f"  Examples of shared words: {', '.join(comparison['shared_words']['examples'])}")
    print()


if __name__ == "__main__":
    main() 