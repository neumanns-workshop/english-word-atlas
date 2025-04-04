#!/usr/bin/env python3
"""
Example script to test Arpabet phonetic handling with phrases from Roget's thesaurus.
"""

import sys
import json
from pathlib import Path
from collections import Counter
import glob

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import (
    get_pronunciation,
    get_syllable_count,
    ArpabetDictionary
)

# Constants
DATA_DIR = Path(Path(__file__).parent.parent.parent / "data" / "wordlists")
ROGET_DIR = DATA_DIR / "historical" / "roget"
ROGET_INDEX = ROGET_DIR / "index.json"


def find_multi_word_phrases(wordlist):
    """Find multi-word phrases in a wordlist."""
    return [word for word in wordlist if " " in word]


def load_roget_categories():
    """Load all Roget's thesaurus categories by combining all category files."""
    all_words = set()
    
    # Get all category files
    category_files = glob.glob(str(ROGET_DIR / "*.json"))
    
    # Exclude index and comprehensive files
    category_files = [f for f in category_files if 
                     'index.json' not in f and 
                     'comprehensive.json' not in f]
    
    print(f"Found {len(category_files)} category files")
    
    # Load words from each category file
    for i, file_path in enumerate(category_files):
        if i % 100 == 0 and i > 0:
            print(f"Processed {i}/{len(category_files)} files...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if "words" in data:
                    all_words.update(data["words"])
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
    
    return sorted(all_words)


def main():
    """Test Arpabet with Roget thesaurus phrases."""
    print("Loading Roget's thesaurus categories...")
    
    # Load all categories by combining all files
    categories = load_roget_categories()
    
    if not categories:
        print("Error: Could not load categories from Roget's files")
        return
    
    # Find multi-word phrases
    phrases = find_multi_word_phrases(categories)
    
    # Print stats
    print(f"Found {len(phrases)} multi-word phrases out of {len(categories)} total entries.")
    
    # Load Arpabet dictionary
    print("\nLoading Arpabet dictionary...")
    arpabet = ArpabetDictionary()
    
    # Sample phrases for analysis
    print("\n=== Sample Phrases from Roget's Thesaurus ===")
    sample_phrases = phrases[:15]  # First 15 phrases
    
    for phrase in sample_phrases:
        pronunciations = get_pronunciation(phrase)
        if pronunciations:
            syllables = get_syllable_count(phrase)
            print(f"'{phrase}': {syllables} syllables")
            print(f"  Pronunciation: [{' '.join(pronunciations[0])}]")
            if len(pronunciations) > 1:
                print(f"  ({len(pronunciations)} variants)")
        else:
            print(f"'{phrase}': No pronunciation found")
    
    # Check coverage
    print("\n=== Pronunciation Coverage Analysis ===")
    covered = sum(1 for phrase in phrases if phrase in arpabet)
    print(f"Phrases with pronunciations: {covered}/{len(phrases)} ({covered/len(phrases)*100:.1f}%)")
    
    # Analyze word counts in phrases
    word_counts = Counter(len(phrase.split()) for phrase in phrases)
    print("\n=== Word Count Distribution ===")
    for count, frequency in sorted(word_counts.items()):
        print(f"{count} word phrases: {frequency} ({frequency/len(phrases)*100:.1f}%)")
    
    # Find the longest phrases
    longest_phrases = sorted(phrases, key=lambda p: len(p.split()), reverse=True)[:5]
    print("\n=== Longest Phrases ===")
    for phrase in longest_phrases:
        words = len(phrase.split())
        print(f"'{phrase}': {words} words")
        if phrase in arpabet:
            syllables = get_syllable_count(phrase)
            print(f"  {syllables} syllables")
        else:
            print("  No pronunciation available")


if __name__ == "__main__":
    main() 