"""
Check Attributes - Display available attributes in the Word Atlas dataset

This script identifies and displays the different types of attributes 
available in the Word Atlas dataset, with counts of how many words
have each attribute.
"""

from word_atlas import WordAtlas
import json

def main():
    """Check and display available attributes in the dataset."""
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    
    # Check wordlist-related attributes
    print("\nWordlist-related attributes:")
    wordlist_attributes = ["GSL_NEW", "GSL_ORIGINAL", "SWADESH_CORE", "SWADESH_EXTENDED"]
    for attr in wordlist_attributes:
        words = atlas.filter_by_attribute(attr)
        print(f"  {attr}: {len(words)} words")
    
    # Check Roget categories (sample)
    print("\nRoget categories (sample):")
    roget_categories = [
        "ROGET_ABSTRACT", "ROGET_AUTHORITY", "ROGET_CAUSATION",
        "ROGET_CHANGE", "ROGET_COMMERCE", "ROGET_COMMUNICATION",
        "ROGET_CONFLICT", "ROGET_DIMENSION", "ROGET_EFFORT",
        "ROGET_EMOTION"
    ]
    
    for attr in roget_categories:
        words = atlas.filter_by_attribute(attr)
        print(f"  {attr}: {len(words)} words")
    
    # Try to get actual wordlists
    print("\nTrying to get actual wordlists:")
    attributes_to_check = ["GSL_ORIGINAL", "GSL_NEW", "SWADESH_CORE", "SWADESH_EXTENDED"]
    
    for attr in attributes_to_check:
        wordlist = atlas.filter_by_attribute(attr)
        sample = sorted(list(wordlist))[:5]
        print(f"  {attr}: {len(wordlist)} words")
        print(f"    Sample: {sample}")
    
    # Check for ARPABET information
    print("\nChecking ARPABET pronunciation information:")
    # Get some sample words
    sample_words = list(atlas.word_data.keys())[:10]
    
    # Print ARPABET for sample words
    print("Sample word ARPABET pronunciations:")
    arpabet_count = 0
    for word in sample_words:
        word_data = atlas.get_word(word)
        arpabet = word_data.get('ARPABET')
        print(f"  {word}: {arpabet}")
        if arpabet is not None:
            arpabet_count += 1
    
    # Count words with ARPABET
    words_with_arpabet = sum(1 for word, attrs in atlas.word_data.items() 
                            if 'ARPABET' in attrs and attrs['ARPABET'] is not None)
    print(f"\nWords with ARPABET information: {words_with_arpabet} out of {len(atlas.word_data)}")
    
    # Check how ARPABET data is structured
    if arpabet_count > 0:
        # Get the first word with ARPABET
        for word, attrs in atlas.word_data.items():
            if 'ARPABET' in attrs and attrs['ARPABET'] is not None:
                print(f"\nExample ARPABET structure for word '{word}':")
                print(f"  Type: {type(attrs['ARPABET'])}")
                print(f"  Value: {attrs['ARPABET']}")
                
                # If it's a list, check what's inside it
                if isinstance(attrs['ARPABET'], list) and len(attrs['ARPABET']) > 0:
                    print(f"  First element type: {type(attrs['ARPABET'][0])}")
                    print(f"  First element value: {attrs['ARPABET'][0]}")
                    
                    # If the first element is also a list, check what's inside it
                    if isinstance(attrs['ARPABET'][0], list) and len(attrs['ARPABET'][0]) > 0:
                        print(f"  First sub-element type: {type(attrs['ARPABET'][0][0])}")
                        print(f"  First sub-element value: {attrs['ARPABET'][0][0]}")
                        
                        # Count vowel phonemes to estimate syllable count
                        vowel_phonemes = [p for p in attrs['ARPABET'][0] if any(c.isdigit() for c in p)]
                        print(f"  Vowel phonemes (potential syllables): {vowel_phonemes}")
                        print(f"  Estimated syllable count: {len(vowel_phonemes)}")
                break

if __name__ == "__main__":
    main() 