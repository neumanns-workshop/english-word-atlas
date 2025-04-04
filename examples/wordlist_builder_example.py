"""
Wordlist Builder Example - Demonstrates how to build custom wordlists

This script shows how to use the WordlistBuilder class to create, manipulate,
and save custom wordlists from the English Word Atlas dataset.
"""

from word_atlas import WordAtlas, WordlistBuilder

def main():
    # Initialize the WordAtlas and WordlistBuilder
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    builder = WordlistBuilder(atlas)
    
    # Set metadata for the custom wordlist
    builder.set_metadata(
        name="Academic Terminology",
        description="Common words used in academic writing",
        creator="Word Atlas Demo",
        tags=["academic", "education", "learning"]
    )
    
    # Add words using different methods
    print("\nBuilding wordlist:")
    
    # Add words with specific pattern
    print("  Adding academic terms...")
    builder.add_by_search("research.*")
    builder.add_by_search("analy.*")
    builder.add_by_search("theor.*")
    
    # Add words from a specific category
    print("  Adding abstract relation terms...")
    builder.add_by_attribute("ROGET_ABSTRACT")
    
    # Add specific words
    print("  Adding specific academic words...")
    academic_words = ["hypothesis", "methodology", "conclusion", "empirical", "framework"]
    added = builder.add_words(academic_words)
    print(f"    Added {added} of {len(academic_words)} specified words")
    
    # Add high frequency words
    print("  Adding common scholarly terms...")
    builder.add_by_frequency(min_freq=100, max_freq=500)
    
    # Find similar words to "research"
    print("  Adding words similar to 'research'...")
    builder.add_similar_words("research", n=10)
    
    # Remove some words that aren't useful
    print("  Removing some common articles and prepositions...")
    builder.remove_words(["a", "the", "in", "of", "on", "and", "or"])
    
    # Print wordlist stats
    print(f"\nWordlist built with {len(builder)} words")
    
    # Print a sample of the words
    word_sample = sorted(list(builder.get_wordlist()))[:20]
    print(f"\nSample words from the list:")
    for word in word_sample:
        print(f"  {word}")
    
    # Save the wordlist
    output_file = "academic_wordlist.json"
    builder.save(output_file)
    print(f"\nWordlist saved to {output_file}")
    
    # Print metadata
    metadata = builder.get_metadata()
    print("\nWordlist metadata:")
    for key, value in metadata.items():
        if key != "criteria":  # Skip the criteria list for brevity
            print(f"  {key}: {value}")
    
    # Analyze the wordlist
    print("\nWordlist analysis:")
    analysis = builder.analyze()
    # Print the first few analysis keys
    print("  Available analysis data:")
    for i, key in enumerate(analysis.keys()):
        if i < 5:  # Just show first 5 keys
            print(f"    - {key}: {analysis[key]}")
    
    # You can also load a saved wordlist
    print("\nLoading saved wordlist:")
    loaded_builder = WordlistBuilder.load(output_file, atlas)
    print(f"  Loaded wordlist with {len(loaded_builder)} words")
    
    # Export as text file
    text_file = "academic_wordlist.txt"
    builder.export_text(text_file)
    print(f"\nWordlist exported as text to {text_file}")

if __name__ == "__main__":
    main() 