import os
import json

def clean_word(word):
    """Clean a word by trimming whitespace"""
    return word.strip()

def normalize_word(word):
    """Normalize a word for deduplication by lowercasing"""
    return word.strip().lower()

def process_directory(directory):
    """Process a directory of wordlist files and return words and metadata"""
    all_words = {}  # Map normalized -> original
    categories = {}
    metadata = None
    
    # Process all JSON files
    for filename in os.listdir(directory):
        if filename.endswith('.json') and filename not in ['index.json', 'comprehensive.json']:
            input_file = os.path.join(directory, filename)
            try:
                with open(input_file, 'r') as f:
                    data = json.load(f)
                
                # Get words and update total
                words = data.get('words', [])
                if isinstance(words, list):
                    # Clean and add to comprehensive list
                    clean_words = {}
                    for w in words:
                        if w:
                            cleaned = clean_word(w)
                            if cleaned:
                                normalized = normalize_word(cleaned)
                                clean_words[normalized] = cleaned  # Keep original case
                                all_words[normalized] = cleaned  # Keep original case
                    
                    # Add to categories
                    category_id = os.path.splitext(filename)[0]
                    categories[category_id] = {
                        'name': data.get('category', ''),
                        'description': data.get('description', ''),
                        'word_count': len(clean_words)
                    }
                    
                    # Get metadata if we don't have it yet
                    if not metadata and all(key in data for key in ['type', 'source', 'license', 'version', 'citation']):
                        metadata = {
                            'type': data['type'],
                            'source': data['source'],
                            'license': data['license'],
                            'version': data['version'],
                            'citation': data['citation']
                        }
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return all_words, categories, metadata

def main():
    # Define historical wordlist directories
    historical_dirs = {
        'ogden': 'data/wordlists/historical/ogden',
        'gsl': 'data/wordlists/historical/gsl',
        'swadesh': 'data/wordlists/historical/swadesh',
        'roget': 'data/wordlists/historical/roget'
    }
    
    all_words = {}  # Map normalized -> {original: str, sources: set}
    top_index = {
        'categories': {},
        'total_categories': 0,
        'total_words': 0,
        'sources': {}
    }
    
    # Process each historical wordlist
    for source, directory in historical_dirs.items():
        print(f"Processing {source}...")
        if os.path.exists(directory):
            # First check for comprehensive.json
            comprehensive_file = os.path.join(directory, 'comprehensive.json')
            if os.path.exists(comprehensive_file):
                with open(comprehensive_file, 'r') as f:
                    data = json.load(f)
                    words = data.get('words', [])
                    if isinstance(words, list):
                        # Clean and add words
                        clean_words = {}
                        for w in words:
                            if w:
                                cleaned = clean_word(w)
                                if cleaned:
                                    normalized = normalize_word(cleaned)
                                    clean_words[normalized] = cleaned  # Keep original case
                                    # Track word sources
                                    if normalized not in all_words:
                                        all_words[normalized] = {'original': cleaned, 'sources': {source}}
                                    else:
                                        all_words[normalized]['sources'].add(source)
                        # Add source info
                        source_words = len(clean_words)
                        top_index['sources'][source] = {
                            'description': data.get('description', ''),
                            'citation': data.get('citation', ''),
                            'word_count': source_words
                        }
            else:
                # Process individual files if no comprehensive.json
                source_words, categories, metadata = process_directory(directory)
                # Add words and track sources
                for normalized, original in source_words.items():
                    if normalized not in all_words:
                        all_words[normalized] = {'original': original, 'sources': {source}}
                    else:
                        all_words[normalized]['sources'].add(source)
                # Add categories with source prefix
                for cat_id, cat_data in categories.items():
                    full_id = f"{source}/{cat_id}"
                    top_index['categories'][full_id] = cat_data
                # Add source info
                if metadata:
                    source_words = len(source_words)
                    top_index['sources'][source] = {
                        'description': metadata.get('description', ''),
                        'citation': metadata.get('citation', ''),
                        'word_count': source_words
                    }
    
    if all_words:  # Only create files if we found words
        historical_dir = 'data/wordlists/historical'
        
        # Calculate source word counts at the end
        for source in historical_dirs.keys():
            if source in top_index['sources']:
                source_words = sum(1 for w in all_words.values() if source in w['sources'])
                top_index['sources'][source]['word_count'] = source_words
                unique_words = sum(1 for w in all_words.values() if len(w['sources']) == 1 and source in w['sources'])
                shared_words = sum(1 for w in all_words.values() if len(w['sources']) > 1 and source in w['sources'])
                top_index['sources'][source].update({
                    'unique_words': unique_words,
                    'shared_words': shared_words,
                    'unique_percent': round(unique_words / source_words * 100, 1),
                    'shared_percent': round(shared_words / source_words * 100, 1)
                })
        
        # Update index totals
        top_index['total_categories'] = len(top_index['categories'])
        top_index['total_words'] = len(all_words)  # This is the true unique word count
        top_index['total_sources'] = len(top_index['sources'])
        
        # Add overlap statistics
        overlaps = {}
        for source1 in historical_dirs.keys():
            overlaps[source1] = {}
            for source2 in historical_dirs.keys():
                if source1 < source2:  # Only count each pair once
                    overlap = sum(1 for w in all_words.values() if source1 in w['sources'] and source2 in w['sources'])
                    overlaps[source1][source2] = {
                        'words': overlap,
                        'percent_of_' + source1: round(overlap / top_index['sources'][source1]['word_count'] * 100, 1),
                        'percent_of_' + source2: round(overlap / top_index['sources'][source2]['word_count'] * 100, 1)
                    }
        top_index['overlaps'] = overlaps
        
        # Add distribution statistics
        source_counts = {}
        for count in range(1, len(historical_dirs) + 1):
            words = sum(1 for w in all_words.values() if len(w['sources']) == count)
            source_counts[str(count)] = {
                'words': words,
                'percent': round(words / len(all_words) * 100, 1)
            }
        top_index['source_counts'] = source_counts
        
        # Write comprehensive word list
        comprehensive_data = {
            "type": "historical",
            "source": "historical",
            "license": "Public Domain",
            "version": "1.0",
            "category": "Comprehensive",
            "description": "Complete word list from all historical sources including Ogden's Basic English (2,234 words), GSL (3,453 words), Swadesh Lists (211 words), and Roget's Thesaurus (9,173 words). The total_words count represents unique words after deduplication across all sources - words appearing in multiple sources are counted only once.",
            "total_words": len(all_words),
            "source_counts": source_counts,  # Add distribution to comprehensive too
            "words": sorted(w['original'] for w in all_words.values())  # Use original case
        }
        
        with open(os.path.join(historical_dir, 'comprehensive.json'), 'w') as f:
            json.dump(comprehensive_data, f, indent=4)
        
        # Write index
        with open(os.path.join(historical_dir, 'index.json'), 'w') as f:
            json.dump(top_index, f, indent=4)

if __name__ == '__main__':
    main() 