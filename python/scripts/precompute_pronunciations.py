#!/usr/bin/env python3
"""
Script to precompute Arpabet pronunciations for all words in our wordlists.
These precomputed pronunciations are stored in a JSON file for efficient
loading and use in the runtime wordlists package.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
import time
import re

# Add parent directory to path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists.arpabet import ArpabetDictionary

# Constants
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
WORDLISTS_DIR = DATA_DIR / "wordlists"
DICT_DIR = DATA_DIR / "dictionaries"
OUTPUT_FILE = DICT_DIR / "precomputed_pronunciations.json"


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


def precompute_pronunciations(dictionary: ArpabetDictionary, words: List[str]) -> Dict[str, List[List[str]]]:
    """
    Precompute pronunciations for a list of words.
    
    Args:
        dictionary: ArpabetDictionary instance
        words: List of words to compute pronunciations for
        
    Returns:
        Dictionary mapping words to their pronunciations
    """
    print(f"Computing pronunciations for {len(words)} words...")
    start_time = time.time()
    
    pronunciations = {}
    found = 0
    multi_word_phrases = 0
    single_words = 0
    
    for i, word in enumerate(words):
        if i % 1000 == 0 and i > 0:
            print(f"  Processed {i}/{len(words)} words ({i/len(words)*100:.1f}%)")
        
        # Check if it's a multi-word phrase
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            prons = dictionary.get_pronunciation(word)
            if prons:
                pronunciations[word] = prons
                found += 1
                multi_word_phrases += 1
                continue
            
            # No need to try other variants for multi-word phrases
            # since get_pronunciation already handles them
            continue
        
        # First try with the original word
        prons = dictionary.get_pronunciation(word)
        if prons:
            # Store with original casing for user convenience
            pronunciations[word] = prons
            found += 1
            single_words += 1
            continue
            
        # Try lowercase
        lower_word = word.lower()
        if lower_word != word:
            prons = dictionary.get_pronunciation(lower_word)
            if prons:
                pronunciations[word] = prons
                found += 1
                single_words += 1
                continue
        
        # Try title case for proper nouns
        title_word = word.title()
        if title_word != word and title_word != lower_word:
            prons = dictionary.get_pronunciation(title_word)
            if prons:
                pronunciations[word] = prons
                found += 1
                single_words += 1
                continue
                
        # As a last resort, clean the word and try again
        clean_word = re.sub(r'[^a-zA-Z\']', '', word.lower())
        if clean_word and clean_word != word and clean_word != lower_word:
            prons = dictionary.get_pronunciation(clean_word)
            if prons:
                pronunciations[word] = prons
                found += 1
                single_words += 1
                continue
    
    elapsed_time = time.time() - start_time
    coverage = found / len(words) * 100 if words else 0
    
    print(f"Pronunciations computed in {elapsed_time:.2f} seconds")
    print(f"Coverage: {coverage:.1f}% ({found}/{len(words)} words)")
    print(f"Found {single_words} single words and {multi_word_phrases} multi-word phrases")
    
    return pronunciations


def save_pronunciations(pronunciations: Dict[str, List[List[str]]], output_file: Path) -> None:
    """
    Save pronunciations to a JSON file.
    
    Args:
        pronunciations: Dictionary mapping words to their pronunciations
        output_file: Path to save the pronunciations
    """
    print(f"Saving pronunciations to {output_file}...")
    
    # Create the dictionaries directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the pronunciations
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pronunciations, f, indent=2)
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Saved {len(pronunciations)} pronunciations")
    print(f"File size: {file_size_mb:.2f} MB")


def main() -> None:
    """Main function to precompute pronunciations."""
    # Create the dictionaries directory if it doesn't exist
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load the Arpabet dictionary
    print("Loading Arpabet dictionary...")
    dictionary = ArpabetDictionary()
    dictionary.load()
    
    # Collect words from all wordlists
    print("Collecting words from all wordlists...")
    all_words = set()
    
    # Historical wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "historical"))
    
    # Corpus wordlists (if they exist)
    corpus_dir = WORDLISTS_DIR / "corpus"
    if corpus_dir.exists():
        all_words.update(collect_words_from_directory(corpus_dir))
    
    # Categories wordlists (if they exist)
    categories_dir = WORDLISTS_DIR / "categories"
    if categories_dir.exists():
        all_words.update(collect_words_from_directory(categories_dir))
    
    # Stop words (if they exist)
    stop_dir = WORDLISTS_DIR / "stop"
    if stop_dir.exists():
        all_words.update(collect_words_from_directory(stop_dir))
    
    # Sort words alphabetically for consistency
    sorted_words = sorted(list(all_words))
    print(f"Collected {len(sorted_words)} unique words from all wordlists")
    
    # Precompute pronunciations
    pronunciations = precompute_pronunciations(dictionary, sorted_words)
    
    # Save pronunciations
    save_pronunciations(pronunciations, OUTPUT_FILE)
    
    print(f"Precomputation complete. Pronunciations saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main() 