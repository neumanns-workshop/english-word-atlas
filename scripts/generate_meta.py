import os
import json

def process_directory(directory):
    """Process a directory of wordlist files and return words and metadata"""
    all_words = set()
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
                    # Update the file's word count if needed
                    if data.get('total_words') != len(words):
                        data['total_words'] = len(words)
                        with open(input_file, 'w') as f:
                            json.dump(data, f, indent=4)
                    
                    # Add to comprehensive list
                    all_words.update(words)
                    
                    # Add to categories
                    category_id = os.path.splitext(filename)[0]
                    categories[category_id] = {
                        'name': data.get('category', ''),
                        'description': data.get('description', ''),
                        'word_count': len(words)
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
    # Process Ogden directories
    ogden_dirs = [
        'data/wordlists/historical/ogden/basic',
        'data/wordlists/historical/ogden/supplement',
        'data/wordlists/historical/ogden/unofficial'
    ]
    
    # First process each directory
    all_words = set()
    top_index = {
        'categories': {},
        'total_categories': 0,
        'total_words': 0
    }
    metadata = None
    
    for directory in ogden_dirs:
        if os.path.exists(directory):
            print(f"Processing {directory}...")
            dir_words, dir_categories, dir_metadata = process_directory(directory)
            
            # Update comprehensive words
            all_words.update(dir_words)
            
            # Update metadata if we found it
            if dir_metadata:
                metadata = dir_metadata
            
            # Add categories with directory prefix
            dir_name = os.path.basename(directory)
            for cat_id, cat_data in dir_categories.items():
                full_id = f"{dir_name}/{cat_id}"
                top_index['categories'][full_id] = cat_data
    
    if all_words:  # Only create files if we found words
        # Create top-level files
        top_dir = 'data/wordlists/historical/ogden'
        
        # Update index totals
        top_index['total_categories'] = len(top_index['categories'])
        top_index['total_words'] = len(all_words)
        
        # Use default metadata if none found
        if not metadata:
            metadata = {
                "type": "historical",
                "source": "ogden",
                "license": "Public Domain",
                "version": "1.0",
                "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd."
            }
        
        # Write comprehensive word list
        comprehensive_data = {
            **metadata,
            "category": "Comprehensive",
            "description": "Ogden's Basic English - Complete word list from all categories including basic, supplement, and unofficial lists",
            "total_words": len(all_words),
            "words": sorted(list(all_words))
        }
        
        with open(os.path.join(top_dir, 'comprehensive.json'), 'w') as f:
            json.dump(comprehensive_data, f, indent=4)
        
        # Write index
        with open(os.path.join(top_dir, 'index.json'), 'w') as f:
            json.dump(top_index, f, indent=4)

if __name__ == '__main__':
    main() 