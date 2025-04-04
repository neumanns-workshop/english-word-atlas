"""
Basic usage example for the English Word Atlas package.

This script demonstrates the fundamental operations available in the 
Word Atlas, including word lookup, similarity calculations, and filtering.
"""

from word_atlas import WordAtlas

def main():
    # Initialize the Word Atlas
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    
    # Print some basic statistics
    print(f"Loaded {len(atlas)} words and phrases")
    print(f"  - {len(atlas.get_single_words())} single words")
    print(f"  - {len(atlas.get_phrases())} multi-word phrases\n")
    
    # Look up a word
    word = "freedom"
    print(f"Information about '{word}':")
    info = atlas.get_word(word)
    
    print(f"  Syllables: {info.get('SYLLABLE_COUNT')}")
    if 'ARPABET' in info:
        print(f"  Pronunciation: /{info['ARPABET'][0]}/")
    print(f"  Frequency: {info.get('FREQ_GRADE', 'Unknown')}\n")
    
    # Find similar words
    print(f"Words similar to '{word}':")
    similar_words = atlas.get_similar_words(word, n=5)
    for similar_word, score in similar_words:
        print(f"  {similar_word}: {score:.4f}")
    print()
    
    # Check similarity between specific words
    word1 = "happy"
    word2 = "sad"
    similarity = atlas.word_similarity(word1, word2)
    print(f"Similarity between '{word1}' and '{word2}': {similarity:.4f}\n")
    
    # Filter by attribute
    category = "ROGET_ABSTRACT"
    abstract_words = atlas.filter_by_attribute(category)
    print(f"Found {len(abstract_words)} words in the {category} category")
    print(f"  Examples: {', '.join(list(abstract_words)[:5])}\n")
    
    # Filter by syllable count
    syllable_count = 1
    one_syllable_words = atlas.filter_by_syllable_count(syllable_count)
    print(f"Found {len(one_syllable_words)} words with {syllable_count} syllable")
    print(f"  Examples: {', '.join(list(one_syllable_words)[:5])}\n")
    
    # Filter by frequency
    high_freq_words = atlas.filter_by_frequency(min_freq=500)
    print(f"Found {len(high_freq_words)} high-frequency words (freq >= 500)")
    print(f"  Examples: {', '.join(high_freq_words[:5])}\n")
    
    # Search for words
    pattern = "happi.*"
    happiness_words = atlas.search(pattern)
    print(f"Words matching '{pattern}':")
    for word in happiness_words:
        print(f"  {word}")

if __name__ == "__main__":
    main() 