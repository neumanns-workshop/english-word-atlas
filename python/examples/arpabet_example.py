#!/usr/bin/env python3
"""
Example script demonstrating how to use the Arpabet pronunciation dictionary functionality.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import (
    get_pronunciation,
    get_rhymes,
    get_alliterations,
    get_syllable_count,
    get_phonetic_similarity,
    get_wordlist,
    ArpabetDictionary
)


def main():
    """Main function to demonstrate Arpabet dictionary usage."""
    print("Loading Arpabet dictionary...")
    
    try:
        # Load the dictionary
        dictionary = ArpabetDictionary()
    except FileNotFoundError:
        print("CMU Dictionary file not found. Please make sure it exists at data/dictionaries/cmudict-0.7b")
        return

    # Example 1: Get pronunciation for a word
    words = ["happy", "computer", "water", "book"]
    print("\n=== Example 1: Word Pronunciations ===")
    for word in words:
        pronunciations = get_pronunciation(word)
        if pronunciations:
            print(f"'{word}' is pronounced as:")
            for i, pron in enumerate(pronunciations):
                print(f"  {i+1}. [{' '.join(pron)}]")
        else:
            print(f"No pronunciation found for '{word}'")
    
    # Example 2: Get pronunciation without stress markers
    print("\n=== Example 2: Pronunciation without stress markers ===")
    for word in words[:2]:  # Just the first two words
        pronunciations = get_pronunciation(word, remove_stress=True)
        if pronunciations:
            print(f"'{word}' without stress markers:")
            for pron in pronunciations:
                print(f"  [{' '.join(pron)}]")
    
    # Example 3: Find rhyming words
    print("\n=== Example 3: Rhyming Words ===")
    for word in ["light", "happy", "blue"]:
        rhymes = get_rhymes(word, syllables=1)[:5]  # Get just the first 5 rhymes
        print(f"Words that rhyme with '{word}':")
        for rhyme in rhymes:
            print(f"  {rhyme}")
    
    # Example 4: Find alliterations
    print("\n=== Example 4: Alliterations ===")
    for word in ["star", "bright", "quick"]:
        alliterations = get_alliterations(word)[:5]  # Get just the first 5 alliterations
        print(f"Words that alliterate with '{word}':")
        for alliteration in alliterations:
            print(f"  {alliteration}")
    
    # Example 5: Count syllables
    print("\n=== Example 5: Syllable Counting ===")
    for word in ["university", "computer", "cake", "antidisestablishmentarianism"]:
        syllables = get_syllable_count(word)
        print(f"'{word}' has {syllables} syllables")
    
    # Example 6: Phonetic similarity
    print("\n=== Example 6: Phonetic Similarity ===")
    word_pairs = [
        ("tomato", "potato"),
        ("table", "stable"),
        ("light", "night"),
        ("happy", "sad"),
        ("dog", "cat")
    ]
    for word1, word2 in word_pairs:
        similarity = get_phonetic_similarity(word1, word2)
        print(f"Similarity between '{word1}' and '{word2}': {similarity:.2f}")
    
    # Example 7: Check for specific words in a wordlist
    print("\n=== Example 7: Pronunciation Coverage of a Wordlist ===")
    try:
        # Try to get wordlist using package API
        try:
            basic_english = get_wordlist("basic-english")
        except Exception as e:
            # If package API fails, load directly from file
            import json
            with open(Path(__file__).parent.parent.parent / "data" / "wordlists" / "historical" / "ogden" / "basic" / "comprehensive.json", 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    basic_english = data
                else:
                    basic_english = data.get("words", [])
        
        total = len(basic_english)
        in_dict = 0
        
        # Check the first 10 words
        sample = basic_english[:10]
        print(f"First 10 words of Basic English:")
        for word in sample:
            has_pron = word in dictionary
            in_dict += 1 if has_pron else 0
            status = "✓" if has_pron else "✗"
            print(f"  {word}: {status}")
        
        # Calculate overall coverage
        for word in basic_english[10:]:  # Skip the first 10 we already checked
            if word in dictionary:
                in_dict += 1
        
        coverage = in_dict / total * 100
        print(f"\nOverall pronunciation coverage: {coverage:.1f}% ({in_dict}/{total} words)")
        
    except Exception as e:
        print(f"Error checking wordlist coverage: {e}")


if __name__ == "__main__":
    main() 