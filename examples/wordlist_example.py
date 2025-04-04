#!/usr/bin/env python3
"""
Example of using the WordlistBuilder to create custom wordlists.

This script demonstrates several common use cases for creating wordlists:
1. A basic vocabulary list for language learners
2. A domain-specific wordlist for science vocabulary
3. A creative writing wordlist with descriptive terms

Each example shows different filtering techniques and how to analyze,
save, and export the resulting wordlists.
"""

import os
from pathlib import Path
from pprint import pprint

from word_atlas import WordAtlas, WordlistBuilder


def create_basic_vocabulary():
    """Create a basic vocabulary list for language learners (A1-A2 level)."""
    print("\n=== Creating Basic Vocabulary List ===")
    
    # Initialize the builder
    builder = WordlistBuilder()
    builder.set_metadata(
        name="Basic English Vocabulary",
        description="Common words for beginner English learners (A1-A2 level)",
        creator="English Word Atlas",
        tags=["beginner", "ESL", "vocabulary", "learning"]
    )
    
    # Add high-frequency single words (top ~1000 most common words)
    # GSL (General Service List) contains common English words
    added = builder.add_by_attribute("GSL")
    print(f"Added {added} words from General Service List")
    
    # Add more words by frequency
    added = builder.add_by_frequency(min_freq=100)
    print(f"Added {added} high-frequency words")
    
    # Limit to mostly 1-2 syllable words for beginners
    words_to_remove = []
    for word in builder.get_wordlist():
        word_data = builder.atlas.get_word(word)
        if " " in word:  # Remove phrases
            words_to_remove.append(word)
        elif word_data.get("SYLLABLE_COUNT", 0) > 2:  # Remove longer words
            words_to_remove.append(word)
    
    removed = builder.remove_words(words_to_remove)
    print(f"Removed {removed} complex words and phrases")
    
    # Analyze the wordlist
    analysis = builder.analyze()
    print(f"\nCreated wordlist with {analysis['size']} words")
    print("Syllable distribution:")
    for syllables, count in analysis["syllable_distribution"].items():
        print(f"  {syllables} syllable(s): {count} words")
    
    # Save the wordlist
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    
    builder.save(output_dir / "basic_vocabulary.json")
    builder.export_text(output_dir / "basic_vocabulary.txt")
    print(f"Saved wordlist to output/basic_vocabulary.json and .txt")
    
    return builder


def create_science_vocabulary():
    """Create a domain-specific wordlist for scientific vocabulary."""
    print("\n=== Creating Science Vocabulary List ===")
    
    # Initialize the builder
    builder = WordlistBuilder()
    builder.set_metadata(
        name="Scientific Vocabulary",
        description="Terms commonly used in scientific writing and discussion",
        creator="English Word Atlas",
        tags=["science", "academic", "technical", "vocabulary"]
    )
    
    # Add words from relevant Roget's categories
    # These categories cover various scientific and technical domains
    for category in ["ROGET_MATTER", "ROGET_INTELLECT", "ROGET_SPACE"]:
        added = builder.add_by_attribute(category)
        print(f"Added {added} words from {category}")
    
    # Add words matching scientific patterns
    patterns = [
        "log[yi]", "method", "scien", "theor", "analy", "data",
        "examin", "hypoth", "experim", "observ", "measur"
    ]
    
    for pattern in patterns:
        added = builder.add_by_search(pattern)
        print(f"Added {added} words matching '{pattern}'")
    
    # Add words similar to key scientific terms
    key_terms = ["science", "theory", "analysis", "research", "experiment"]
    for term in key_terms:
        if builder.atlas.has_word(term):
            added = builder.add_similar_words(term, n=5)
            print(f"Added {added} words similar to '{term}'")
    
    # Analyze the wordlist
    analysis = builder.analyze()
    print(f"\nCreated science wordlist with {analysis['size']} words")
    
    # Print frequency distribution
    if "frequency" in analysis:
        print(f"Average frequency: {analysis['frequency']['average']}")
        print("Frequency distribution:")
        for bucket, count in analysis["frequency"]["distribution"].items():
            print(f"  {bucket}: {count} words")
    
    # Save the wordlist
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    
    builder.save(output_dir / "science_vocabulary.json")
    print(f"Saved wordlist to output/science_vocabulary.json")
    
    return builder


def create_descriptive_vocabulary():
    """Create a creative writing wordlist with descriptive terms."""
    print("\n=== Creating Descriptive Vocabulary for Creative Writing ===")
    
    # Initialize the builder
    builder = WordlistBuilder()
    builder.set_metadata(
        name="Descriptive Vocabulary",
        description="Vivid and expressive words for creative writing",
        creator="English Word Atlas",
        tags=["creative", "writing", "descriptive", "expressive"]
    )
    
    # Add words from relevant Roget's categories related to perception and emotion
    categories = ["ROGET_AFFECTIONS", "ROGET_SENSATION"]
    for category in categories:
        added = builder.add_by_attribute(category)
        print(f"Added {added} words from {category}")
    
    # Add specific descriptive words
    descriptive_patterns = [
        "vivid", "bright", "dark", "gentle", "harsh", "soft", 
        "loud", "quiet", "sweet", "bitter", "gleam", "glow",
        "shimmer", "vibrant", "mellow", "sharp", "smooth"
    ]
    
    for pattern in descriptive_patterns:
        added = builder.add_by_search(pattern)
        print(f"Added {added} words matching '{pattern}'")
    
    # Add words with 3+ syllables (often more expressive/specific)
    for syllable_count in range(3, 6):
        added = builder.add_by_syllable_count(syllable_count)
        print(f"Added {added} words with {syllable_count} syllables")
    
    # Custom filtering: remove very common words (less expressive)
    def filter_by_uncommonness(word, attrs):
        # Keep words that are moderately uncommon but not too rare
        if "FREQ_GRADE" in attrs:
            # High enough to be known, low enough to be interesting
            return 5 <= attrs["FREQ_GRADE"] <= 50
        return False
    
    added = builder.add_by_custom_filter(
        filter_by_uncommonness,
        "Words with moderate frequency (uncommon but recognizable)"
    )
    print(f"Added {added} moderately uncommon words")
    
    # Analyze the wordlist
    analysis = builder.analyze()
    print(f"\nCreated descriptive wordlist with {analysis['size']} words")
    
    # Save the wordlist
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    
    builder.save(output_dir / "descriptive_vocabulary.json")
    print(f"Saved wordlist to output/descriptive_vocabulary.json")
    
    # Print some sample words
    print("\nSample descriptive words:")
    sample = sorted(list(builder.words))[:10]
    for word in sample:
        print(f"  {word}")
    
    return builder


def merge_specialized_lists(builders):
    """Merge multiple specialized wordlists into a comprehensive vocabulary."""
    print("\n=== Creating Merged Comprehensive Vocabulary ===")
    
    # Create a new empty wordlist
    merged = WordlistBuilder()
    merged.set_metadata(
        name="Comprehensive English Vocabulary",
        description="Combined vocabulary from multiple specialized wordlists",
        creator="English Word Atlas",
        tags=["comprehensive", "merged", "vocabulary"]
    )
    
    # Add words from each builder
    for builder in builders:
        wordlist = builder.get_wordlist()
        name = builder.metadata["name"]
        
        added = merged.add_words(wordlist)
        print(f"Added {added} words from '{name}'")
    
    # Analyze the merged wordlist
    analysis = merged.analyze()
    print(f"\nCreated merged wordlist with {analysis['size']} words")
    
    # Save the wordlist
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    
    merged.save(output_dir / "comprehensive_vocabulary.json")
    print(f"Saved wordlist to output/comprehensive_vocabulary.json")
    
    return merged


if __name__ == "__main__":
    # Create the output directory
    os.makedirs("output", exist_ok=True)
    
    # Create different specialized wordlists
    basic = create_basic_vocabulary()
    science = create_science_vocabulary()
    descriptive = create_descriptive_vocabulary()
    
    # Merge them into a comprehensive vocabulary
    comprehensive = merge_specialized_lists([basic, science, descriptive])
    
    print("\n=== Summary ===")
    print(f"Basic Vocabulary: {basic.get_size()} words")
    print(f"Science Vocabulary: {science.get_size()} words")
    print(f"Descriptive Vocabulary: {descriptive.get_size()} words")
    print(f"Comprehensive Vocabulary: {comprehensive.get_size()} words")
    
    print("\nAll wordlists saved to the 'output' directory") 