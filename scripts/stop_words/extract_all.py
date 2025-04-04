import os
import json
from pathlib import Path

# Import all source modules
from sources.nltk_words import extract as extract_nltk
from sources.spacy_words import extract as extract_spacy
from sources.sklearn_words import extract as extract_sklearn

def create_combined_lists():
    """Create minimal and comprehensive combined lists"""
    # Get all individual stop word files
    data_dir = Path('data/wordlists/stop_words')
    stop_word_files = list(data_dir.glob('*_stop_words.json'))
    
    # Load all words
    all_words = set()
    source_words = []
    for file in stop_word_files:
        with open(file, 'r') as f:
            data = json.load(f)
            words = set(data['words'])
            all_words.update(words)
            source_words.append(words)
    
    # Create minimal list (common words across all sources)
    if source_words:
        common_words = set.intersection(*source_words)
        if not common_words:
            # If no common words, use the intersection of the two largest sets
            source_words.sort(key=len, reverse=True)
            if len(source_words) >= 2:
                common_words = set.intersection(source_words[0], source_words[1])
            else:
                common_words = source_words[0]
    else:
        common_words = set()
    
    # Save minimal list
    with open(data_dir / 'minimal_stop_words.json', 'w') as f:
        json.dump({
            'words': sorted(list(common_words)),
            'description': 'Minimal set of stop words common across sources',
            'source': 'combined',
            'license': 'Combined permissive licenses (Apache 2.0, MIT, BSD-3)',
            'sources': ['nltk', 'spacy', 'sklearn']
        }, f, indent=2)
    print(f"Created minimal stop words file with {len(common_words)} words")
    
    # Save comprehensive list
    with open(data_dir / 'comprehensive_stop_words.json', 'w') as f:
        json.dump({
            'words': sorted(list(all_words)),
            'description': 'Comprehensive set of stop words from all sources',
            'source': 'combined',
            'license': 'Combined permissive licenses (Apache 2.0, MIT, BSD-3)',
            'sources': ['nltk', 'spacy', 'sklearn']
        }, f, indent=2)
    print(f"Created comprehensive stop words file with {len(all_words)} words")

def main():
    # Create output directory
    os.makedirs('data/wordlists/stop_words', exist_ok=True)
    
    # Extract from each source
    sources = [
        ('nltk_words', extract_nltk),
        ('spacy_words', extract_spacy),
        ('sklearn_words', extract_sklearn)
    ]
    
    for name, extract_func in sources:
        print(f"\nProcessing {name}...")
        extract_func()
    
    print("\nCreating combined lists...")
    create_combined_lists()

if __name__ == '__main__':
    main() 