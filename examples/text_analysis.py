"""
Text Analysis Example with the English Word Atlas.

This example demonstrates how to analyze a text to determine:
1. Word coverage (what percentage of words in the text are in the atlas)
2. Category distribution (which semantic categories are most represented)
3. Vocabulary complexity based on frequency and syllable count
"""

import re
import sys
from collections import Counter
from typing import Dict, List, Set, Tuple

from word_atlas import WordAtlas

def tokenize_text(text: str) -> List[str]:
    """Split text into words, removing punctuation and converting to lowercase."""
    # Replace line breaks with spaces
    text = text.replace('\n', ' ')
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and split into words
    words = re.findall(r'\b[a-z]+\b', text)
    
    return words

def analyze_text(atlas: WordAtlas, text: str) -> Dict:
    """Analyze a text using the Word Atlas.
    
    Args:
        atlas: WordAtlas instance
        text: Text to analyze
        
    Returns:
        Dictionary with analysis results
    """
    # Tokenize the text
    words = tokenize_text(text)
    total_words = len(words)
    
    if total_words == 0:
        return {"error": "No words found in the text"}
    
    # Count unique words
    word_counts = Counter(words)
    unique_words = len(word_counts)
    
    # Check coverage
    covered_words = {word for word in word_counts if atlas.has_word(word)}
    coverage_percent = len(covered_words) / unique_words * 100
    
    # Analyze frequency
    frequencies = []
    syllable_counts = []
    
    for word in covered_words:
        word_info = atlas.get_word(word)
        
        if 'FREQ_GRADE' in word_info:
            frequencies.append(word_info['FREQ_GRADE'])
            
        if 'SYLLABLE_COUNT' in word_info:
            syllable_counts.append(word_info['SYLLABLE_COUNT'])
    
    avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0
    avg_syllables = sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0
    
    # Analyze categories
    roget_categories = Counter()
    
    for word in covered_words:
        word_info = atlas.get_word(word)
        
        # Count Roget categories
        for key, value in word_info.items():
            if key.startswith('ROGET_') and value:
                roget_categories[key] += 1
    
    # Get top categories
    top_categories = roget_categories.most_common(5)
    
    # Find words not in atlas
    unknown_words = {word for word in word_counts if not atlas.has_word(word)}
    
    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "covered_words": len(covered_words),
        "coverage_percent": coverage_percent,
        "avg_frequency": avg_frequency,
        "avg_syllables": avg_syllables,
        "top_categories": top_categories,
        "unknown_words": list(unknown_words)[:10],  # Limit to 10 unknown words
        "unknown_count": len(unknown_words)
    }

def print_analysis(analysis: Dict):
    """Print analysis results in a readable format."""
    print("Text Analysis Results:")
    print(f"Total words: {analysis['total_words']}")
    print(f"Unique words: {analysis['unique_words']}")
    print(f"Words found in atlas: {analysis['covered_words']} ({analysis['coverage_percent']:.1f}%)")
    
    print("\nVocabulary metrics:")
    print(f"  Average word frequency: {analysis['avg_frequency']:.1f}")
    print(f"  Average syllable count: {analysis['avg_syllables']:.1f}")
    
    print("\nTop semantic categories:")
    for category, count in analysis['top_categories']:
        print(f"  {category}: {count} words")
    
    print(f"\nWords not found in atlas: {analysis['unknown_count']} total")
    if analysis['unknown_words']:
        print(f"  Examples: {', '.join(analysis['unknown_words'])}")

def main():
    # Check if a file was provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as file:
                text = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # Use a sample text
        text = """
        The pursuit of happiness is a fundamental right. Freedom of expression
        allows individuals to speak their mind without fear of persecution.
        Knowledge and wisdom are distinct: one is information, the other is
        understanding. Scientific pursuit requires both curiosity and
        methodical analysis. The balance between liberty and security
        continues to challenge modern societies.
        """
        print("Using sample text. You can provide your own file as an argument.")
    
    # Initialize Word Atlas
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    
    # Analyze the text
    analysis = analyze_text(atlas, text)
    
    # Print results
    print_analysis(analysis)

if __name__ == "__main__":
    main() 