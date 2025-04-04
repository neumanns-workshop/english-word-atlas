import json
import os

def main():
    # Define stopword sources
    stop_word_files = [
        'data/wordlists/stop_words/fox_stop_words.json',
        'data/wordlists/stop_words/nltk_stop_words.json',
        'data/wordlists/stop_words/spacy_stop_words.json',
        'data/wordlists/stop_words/sklearn_stop_words.json'
    ]
    
    all_stop_words = set()  # Use a set for automatic deduplication
    sources = {}
    
    # Process each source
    for file_path in stop_word_files:
        source_name = os.path.basename(file_path).replace('_stop_words.json', '')
        print(f"Processing {source_name}...")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            words = data.get('words', [])
            if isinstance(words, list):
                # Track source stats
                source_words = set(words)  # Convert to set for unique count
                sources[source_name] = {
                    'description': data.get('description', ''),
                    'citation': data.get('citation', ''),
                    'word_count': len(source_words)
                }
                all_stop_words.update(source_words)
    
    # Calculate overlaps
    overlaps = {}
    for source1 in sources:
        overlaps[source1] = {}
        for source2 in sources:
            if source1 < source2:  # Only count each pair once
                with open(f'data/wordlists/stop_words/{source1}_stop_words.json', 'r') as f1, \
                     open(f'data/wordlists/stop_words/{source2}_stop_words.json', 'r') as f2:
                    words1 = set(json.load(f1)['words'])
                    words2 = set(json.load(f2)['words'])
                    overlap = len(words1.intersection(words2))
                    overlaps[source1][source2] = {
                        'words': overlap,
                        'percent_of_' + source1: round(overlap / len(words1) * 100, 1),
                        'percent_of_' + source2: round(overlap / len(words2) * 100, 1)
                    }
    
    # Write comprehensive stop words
    comprehensive_data = {
        "type": "stop_words",
        "source": "comprehensive",
        "license": "Mixed",
        "version": "1.0",
        "category": "Stop Words",
        "description": "Complete stop word list combining Fox, NLTK, spaCy, and scikit-learn stop words",
        "total_words": len(all_stop_words),
        "words": sorted(all_stop_words)
    }
    
    with open('data/wordlists/stop_words/comprehensive.json', 'w') as f:
        json.dump(comprehensive_data, f, indent=4)
    
    # Write index with stats
    index_data = {
        "total_words": len(all_stop_words),
        "sources": sources,
        "overlaps": overlaps
    }
    
    with open('data/wordlists/stop_words/index.json', 'w') as f:
        json.dump(index_data, f, indent=4)
    
    print(f"\nTotal unique stop words: {len(all_stop_words)}")
    print("\nSource counts:")
    for source, data in sources.items():
        print(f"- {source}: {data['word_count']} words")

if __name__ == '__main__':
    main() 