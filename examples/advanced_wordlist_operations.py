"""
Advanced Wordlist Operations - A comprehensive guide to creating specialized wordlists

This script demonstrates sophisticated wordlist creation techniques using
the English Word Atlas. It showcases combining multiple filtering methods,
set operations, and WordlistBuilder features to create highly specific wordlists.
"""

from word_atlas import WordAtlas, WordlistBuilder
import time
import pprint

def main():
    """Main function demonstrating advanced wordlist operations."""
    # Initialize the WordAtlas
    print("Loading the English Word Atlas...")
    start_time = time.time()
    atlas = WordAtlas()
    print(f"Loaded in {time.time() - start_time:.2f} seconds\n")
    
    # === PART 1: EXPLORING AVAILABLE ATTRIBUTES ===
    print("="*80)
    print("PART 1: EXPLORING AVAILABLE ATTRIBUTES")
    print("="*80)
    
    # Get and display wordlist-related attributes
    print("\nWordlist-related attributes:")
    wordlist_attributes = {
        "GSL_ORIGINAL": len(atlas.filter_by_attribute("GSL_ORIGINAL")),
        "GSL_NEW": len(atlas.filter_by_attribute("GSL_NEW")),
        "SWADESH_CORE": len(atlas.filter_by_attribute("SWADESH_CORE")),
        "SWADESH_EXTENDED": len(atlas.filter_by_attribute("SWADESH_EXTENDED")),
    }
    
    for attr, count in wordlist_attributes.items():
        print(f"  {attr}: {count} words")
    
    # Get and display Roget's categories
    print("\nRoget's thesaurus categories (sample):")
    roget_categories = {}
    
    for attr, attrs in atlas.roget_category_index.items():
        roget_categories[attr] = len(attrs)
    
    # Display a sample of categories
    for attr, count in sorted(roget_categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {attr}: {count} words")
    
    # === PART 2: BASIC FILTERING OPERATIONS ===
    print("\n" + "="*80)
    print("PART 2: BASIC FILTERING OPERATIONS")
    print("="*80)
    
    # Filter by syllable count
    print("\nFiltering by syllable count:")
    for count in range(1, 4):
        words = atlas.filter_by_syllable_count(count)
        print(f"  {count} syllable(s): {len(words)} words")
        if words:
            print(f"    Sample: {sorted(list(words))[:5]}")
    
    # Filter by frequency
    print("\nFiltering by frequency:")
    frequency_ranges = [
        (500, None, "Very high frequency (500+)"),
        (100, 500, "High frequency (100-500)"),
        (50, 100, "Medium frequency (50-100)"),
        (10, 50, "Low frequency (10-50)"),
        (0, 10, "Very low frequency (0-10)")
    ]
    
    for min_freq, max_freq, label in frequency_ranges:
        words = atlas.filter_by_frequency(min_freq, max_freq)
        print(f"  {label}: {len(words)} words")
        if words:
            print(f"    Sample: {words[:5]}")
    
    # Search by pattern
    print("\nSearching by pattern:")
    patterns = ["^e.*ing$", "^un.*", ".*ology$"]
    
    for pattern in patterns:
        words = atlas.search(pattern)
        print(f"  Pattern '{pattern}': {len(words)} words")
        if words:
            print(f"    Sample: {sorted(words)[:5]}")
    
    # === PART 3: COMBINING FILTERS WITH SET OPERATIONS ===
    print("\n" + "="*80)
    print("PART 3: COMBINING FILTERS WITH SET OPERATIONS")
    print("="*80)
    
    # Example 1: Basic English core vocabulary
    # Intersection of GSL and 1-2 syllable words
    print("\nExample 1: Basic English core vocabulary")
    gsl_words = atlas.filter_by_attribute("GSL_ORIGINAL")
    one_syllable = atlas.filter_by_syllable_count(1)
    two_syllable = atlas.filter_by_syllable_count(2)
    
    one_two_syllable = one_syllable.union(two_syllable)
    basic_vocabulary = gsl_words.intersection(one_two_syllable)
    
    print(f"  GSL words: {len(gsl_words)}")
    print(f"  1-2 syllable words: {len(one_two_syllable)}")
    print(f"  Intersection: {len(basic_vocabulary)} words")
    print(f"  Sample: {sorted(list(basic_vocabulary))[:10]}")
    
    # Example 2: Emotions vocabulary not in GSL
    # Difference between emotion words and GSL
    print("\nExample 2: Emotions vocabulary not in GSL")
    emotion_words = atlas.filter_by_attribute("ROGET_EMOTION")
    emotions_not_in_gsl = emotion_words.difference(gsl_words)
    
    print(f"  Emotion words: {len(emotion_words)}")
    print(f"  Emotion words not in GSL: {len(emotions_not_in_gsl)}")
    print(f"  Sample: {sorted(list(emotions_not_in_gsl))[:10]}")
    
    # Example 3: Academic vocabulary
    # Intersection of abstract words, frequency 10-100, and 3+ syllables
    print("\nExample 3: Advanced academic vocabulary")
    abstract_words = atlas.filter_by_attribute("ROGET_ABSTRACT")
    medium_freq = atlas.filter_by_frequency(10, 100)
    three_plus_syllable = set()
    for i in range(3, 7):
        three_plus_syllable.update(atlas.filter_by_syllable_count(i))
    
    academic_vocab = abstract_words.intersection(medium_freq).intersection(three_plus_syllable)
    
    print(f"  Abstract concept words: {len(abstract_words)}")
    print(f"  Medium frequency words: {len(medium_freq)}")
    print(f"  3+ syllable words: {len(three_plus_syllable)}")
    print(f"  Intersection (academic vocab): {len(academic_vocab)} words")
    print(f"  Sample: {sorted(list(academic_vocab))[:10]}")
    
    # === PART 4: USING WORDLIST BUILDER FOR COMPLEX WORDLISTS ===
    print("\n" + "="*80)
    print("PART 4: USING WORDLIST BUILDER FOR COMPLEX WORDLISTS")
    print("="*80)
    
    # Create a specialized vocabulary for language learners
    print("\nBuilding a specialized vocabulary list for language learners...")
    
    # Initialize builder
    builder = WordlistBuilder(atlas)
    
    # Set metadata
    builder.set_metadata(
        name="English Learners' Specialized Vocabulary",
        description="A carefully curated wordlist for English language learners, "
                   "combining high-frequency words with essential semantic categories.",
        creator="English Word Atlas Demo",
        tags=["ESL", "language learning", "beginner", "vocabulary", "essential"]
    )
    
    # Add core words that everyone needs to know
    print("  Step 1: Adding core vocabulary from Swadesh list...")
    builder.add_by_attribute("SWADESH_EXTENDED")
    
    # Add common, high-frequency words
    print("  Step 2: Adding high-frequency GSL words...")
    high_freq_gsl = gsl_words.intersection(atlas.filter_by_frequency(100, None))
    builder.add_words(list(high_freq_gsl))
    
    # Add common emotion words
    print("  Step 3: Adding basic emotion words...")
    common_emotions = emotion_words.intersection(gsl_words)
    builder.add_words(list(common_emotions))
    
    # Add short color and number words
    print("  Step 4: Adding colors and number words...")
    color_pattern = atlas.search("(red|blue|green|yellow|black|white|orange|purple|pink|gray|brown|gold)")
    number_pattern = atlas.search("(one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand)")
    builder.add_words(list(color_pattern))
    builder.add_words(list(number_pattern))
    
    # Remove any words that are too complex (4+ syllables)
    print("  Step 5: Removing overly complex words...")
    complex_words = set()
    for i in range(4, 7):
        complex_words.update(atlas.filter_by_syllable_count(i))
    
    builder.remove_words(list(complex_words))
    
    # Print stats for the final wordlist
    print(f"\nFinal wordlist contains {len(builder)} words")
    
    # Save the wordlist
    output_file = "esl_specialized_vocabulary.json"
    builder.save(output_file)
    print(f"Wordlist saved to {output_file}")
    
    # Export as text file
    text_file = "esl_specialized_vocabulary.txt"
    builder.export_text(text_file)
    print(f"Wordlist exported as text to {text_file}")
    
    # === PART 5: ANALYZING A BUILT WORDLIST ===
    print("\n" + "="*80)
    print("PART 5: ANALYZING A BUILT WORDLIST")
    print("="*80)
    
    # Analyze the wordlist
    print("\nAnalyzing the ESL wordlist:")
    analysis = builder.analyze()
    
    # Print all analysis data
    print("\nWordlist analysis data:")
    for key, value in analysis.items():
        if key == "wordlist_coverage":
            print(f"  {key}:")
            # Display wordlist coverage with counts and percentages
            for list_name, stats in value.items():
                print(f"    {list_name}: {stats['count']} words ({stats['percentage']}%)")
        elif key == "frequency":
            print(f"  {key}:")
            # Display frequency distribution
            if "distribution" in value:
                print(f"    distribution:")
                for bucket, count_info in value["distribution"].items():
                    print(f"      {bucket}: {count_info}")
            # Display average frequency
            if "average" in value:
                print(f"    average: {value['average']}")
        elif isinstance(value, dict) and len(str(value)) > 70:
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    # === PART 6: APPLICATION IDEAS ===
    print("\n" + "="*80)
    print("PART 6: APPLICATION IDEAS")
    print("="*80)
    
    print("""
Practical applications for these custom wordlists:

1. Language Learning Resources
   - Tiered vocabulary lists for different proficiency levels
   - Topic-specific vocabulary for specialized courses
   - Spaced repetition flashcard sets

2. Natural Language Processing
   - Training data for language models
   - Stopword lists for text processing
   - Sentiment analysis lexicons

3. Educational Materials
   - Reading difficulty assessment
   - Vocabulary building exercises
   - Age-appropriate content creation

4. Linguistic Research
   - Comparative studies across languages
   - Morphological and semantic analysis
   - Historical language evolution research

5. Accessibility
   - Simplified English for people with reading difficulties
   - Core vocabulary for text simplification algorithms
   - Vocabulary selection for AAC (Augmentative and Alternative Communication) devices
    """)

if __name__ == "__main__":
    main() 