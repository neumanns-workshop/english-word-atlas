#!/usr/bin/env python3
"""
List all wordlists and Roget categories available in the English Word Atlas.
"""

from word_atlas import WordAtlas

# Initialize the Word Atlas
print("Initializing Word Atlas...")
atlas = WordAtlas()
print(f"Successfully loaded atlas with {len(atlas)} entries\n")

# Get all attribute keys
all_keys = set()
for word in atlas.word_data:
    all_keys.update(atlas.word_data[word].keys())

print(f"Found {len(all_keys)} total attribute keys")

# Separate Roget categories from other wordlists
roget_categories = []
wordlists = []
metadata_attrs = []

for key in sorted(all_keys):
    if key.startswith("ROGET_"):
        roget_categories.append(key)
    elif key in ["SYLLABLE_COUNT", "FREQ_GRADE", "FREQ_COUNT", "ARPABET"]:
        metadata_attrs.append(key)
    else:
        # Check if this is a boolean flag by examining the value
        # Find a word that has this attribute
        for word in atlas.word_data:
            if key in atlas.word_data[word]:
                if isinstance(atlas.word_data[word][key], bool):
                    wordlists.append(key)
                else:
                    metadata_attrs.append(key)
                break

print(f"\n1. WORDLISTS ({len(wordlists)} total):")
print("-" * 50)
for wordlist in sorted(wordlists):
    # Count words in this wordlist
    count = sum(1 for word in atlas.word_data 
                if wordlist in atlas.word_data[word] and atlas.word_data[word][wordlist])
    
    percentage = (count / len(atlas)) * 100
    print(f"  {wordlist}: {count} words ({percentage:.1f}%)")

print(f"\n2. ROGET CATEGORIES ({len(roget_categories)} total):")
print("-" * 50)
for category in sorted(roget_categories):
    # Count words in this category
    count = sum(1 for word in atlas.word_data 
                if category in atlas.word_data[word] and atlas.word_data[word][category])
    
    percentage = (count / len(atlas)) * 100
    print(f"  {category}: {count} words ({percentage:.1f}%)")

print(f"\n3. METADATA ATTRIBUTES ({len(metadata_attrs)} total):")
print("-" * 50)
for attr in sorted(metadata_attrs):
    # Count words with this attribute
    count = sum(1 for word in atlas.word_data if attr in atlas.word_data[word])
    
    percentage = (count / len(atlas)) * 100
    print(f"  {attr}: {count} words ({percentage:.1f}%)")

print("\n4. EXAMPLES FROM TOP WORDLISTS:")
print("-" * 50)
# Get examples from the top 5 wordlists by coverage
top_wordlists = sorted([(wl, sum(1 for word in atlas.word_data 
                           if wl in atlas.word_data[word] and atlas.word_data[word][wl]))
                      for wl in wordlists], key=lambda x: -x[1])[:5]

for wordlist, count in top_wordlists:
    words = list(atlas.filter_by_attribute(wordlist))
    print(f"\n{wordlist} ({count} words)")
    print(f"  Examples: {', '.join(sorted(words[:10]))}")
    
    # Get some statistics
    syllable_counts = {}
    for word in words[:100]:  # Sample the first 100 words
        if "SYLLABLE_COUNT" in atlas.word_data[word]:
            count = atlas.word_data[word]["SYLLABLE_COUNT"]
            syllable_counts[count] = syllable_counts.get(count, 0) + 1
            
    print("  Syllable distribution (sample):")
    for count, freq in sorted(syllable_counts.items()):
        print(f"    {count} syllable(s): {freq} words") 