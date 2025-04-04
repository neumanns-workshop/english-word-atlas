#!/usr/bin/env python3
"""
Example script demonstrating how to use the Arpabet pronunciation dictionary 
with multi-word phrases.
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
    ArpabetDictionary
)


def main():
    """Main function to demonstrate Arpabet dictionary with multi-word phrases."""
    print("Loading Arpabet dictionary...")
    
    try:
        # Load the dictionary
        dictionary = ArpabetDictionary()
    except FileNotFoundError:
        print("CMU Dictionary file not found. Please make sure it exists at data/dictionaries/cmudict-0.7b")
        return

    # Example 1: Get pronunciation for multi-word phrases
    phrases = ["high school", "New York", "United States", "make sense", "machine learning"]
    print("\n=== Example 1: Multi-Word Phrase Pronunciations ===")
    for phrase in phrases:
        pronunciations = get_pronunciation(phrase)
        if pronunciations:
            print(f"'{phrase}' is pronounced as:")
            for i, pron in enumerate(pronunciations):
                if i < 3:  # Limit to 3 pronunciations to avoid long output
                    print(f"  {i+1}. [{' '.join(pron)}]")
            if len(pronunciations) > 3:
                print(f"  ... and {len(pronunciations) - 3} more pronunciation variants")
        else:
            print(f"No pronunciation found for '{phrase}'")
    
    # Example 2: Get pronunciation without stress markers
    print("\n=== Example 2: Pronunciation without stress markers ===")
    for phrase in phrases[:2]:  # Just the first two phrases
        pronunciations = get_pronunciation(phrase, remove_stress=True)
        if pronunciations and len(pronunciations) > 0:
            print(f"'{phrase}' without stress markers:")
            print(f"  [{' '.join(pronunciations[0])}]")
    
    # Example 3: Find rhyming words for phrases (uses last word)
    print("\n=== Example 3: Rhyming with Multi-Word Phrases ===")
    for phrase in ["high school", "New York", "artificial intelligence"]:
        # Try different rhyming strengths
        print(f"Words that rhyme with '{phrase}' (using last word):")
        
        # Perfect rhymes
        perfect_rhymes = get_rhymes(phrase, strength="perfect")[:3]
        print(f"  Perfect rhymes: {', '.join(perfect_rhymes) if perfect_rhymes else 'None'}")
        
        # Normal rhymes (default)
        normal_rhymes = get_rhymes(phrase, syllables=1, strength="normal")[:3]
        print(f"  Normal rhymes (1 syllable): {', '.join(normal_rhymes) if normal_rhymes else 'None'}")
        
        # Weak rhymes
        weak_rhymes = get_rhymes(phrase, strength="weak")[:3]
        print(f"  Weak rhymes: {', '.join(weak_rhymes) if weak_rhymes else 'None'}")
        print()
    
    # Example 4: Find alliterations for phrases (uses first word)
    print("\n=== Example 4: Alliterations with Multi-Word Phrases ===")
    for phrase in ["bright star", "quick brown fox", "machine learning"]:
        alliterations = get_alliterations(phrase)[:5]  # Get just the first 5 alliterations
        print(f"Words that alliterate with '{phrase}' (using first word):")
        for alliteration in alliterations:
            print(f"  {alliteration}")
    
    # Example 5: Count syllables in phrases
    print("\n=== Example 5: Syllable Counting for Phrases ===")
    for phrase in ["high school", "artificial intelligence", "united nations", "theoretical physics"]:
        syllables = get_syllable_count(phrase)
        print(f"'{phrase}' has {syllables} syllables")
    
    # Example 6: Phonetic similarity between phrases
    print("\n=== Example 6: Phonetic Similarity between Phrases ===")
    phrase_pairs = [
        # Same length pairs (word by word comparison)
        ("high school", "high level"),        # First word identical, second different
        ("machine learning", "machine earning"),  # Small difference
        ("artificial intelligence", "artificial negligence"),  # Last word different
        
        # Different length pairs
        ("New York", "new jersey city"),  # Different number of words
        ("quantum physics", "physics of quantum mechanics"),  # Shared words, different order
        
        # Same words, different order
        ("machine learning", "learning machine"),
        
        # Single word to phrase comparison
        ("school", "high school"),
        ("intelligence", "artificial intelligence")
    ]
    
    print("Phonetic similarity between phrases:")
    for phrase1, phrase2 in phrase_pairs:
        similarity = get_phonetic_similarity(phrase1, phrase2)
        print(f"  '{phrase1}' and '{phrase2}': {similarity:.2f}")
    
    # Example 7: Find phrases from wordlists
    print("\n=== Example 7: Multi-Word Phrases from Wordlists ===")
    # Load a few sample phrases from our dictionary to check
    # These are likely to come from Roget's thesaurus
    sample_phrases = [
        "central idea", 
        "human race", 
        "world without end",
        "quantum physics",
        "deep learning"
    ]
    
    print("Checking if phrases are in dictionary:")
    for phrase in sample_phrases:
        has_pron = phrase in dictionary
        status = "✓" if has_pron else "✗"
        if has_pron:
            prons = dictionary.get_pronunciation(phrase)
            variants = len(prons) if prons else 0
            print(f"  '{phrase}': {status} ({variants} pronunciation variants)")
        else:
            print(f"  '{phrase}': {status}")


if __name__ == "__main__":
    main() 