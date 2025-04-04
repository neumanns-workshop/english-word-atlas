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
                    
                    # Get metadata from any file
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
    # Process Swadesh directory
    swadesh_dir = 'data/wordlists/historical/swadesh'
    
    print(f"Processing {swadesh_dir}...")
    all_words, categories, metadata = process_directory(swadesh_dir)
    
    if all_words:  # Only create files if we found words
        # Update index totals
        top_index = {
            'categories': categories,
            'total_categories': len(categories),
            'total_words': len(all_words)
        }
        
        # Use default metadata if none found
        if not metadata:
            metadata = {
                "type": "historical",
                "source": "swadesh",
                "license": "Public Domain",
                "version": "1.0",
                "citation": "Swadesh, Morris. (1971). The Origin and Diversification of Language. Aldine Atherton."
            }
        
        # Write comprehensive word list
        comprehensive_data = {
            **metadata,
            "category": "Comprehensive",
            "description": "Swadesh List - Complete word list including all variants",
            "total_words": len(all_words),
            "words": sorted(list(all_words))
        }
        
        with open(os.path.join(swadesh_dir, 'comprehensive.json'), 'w') as f:
            json.dump(comprehensive_data, f, indent=4)
        
        # Write index
        with open(os.path.join(swadesh_dir, 'index.json'), 'w') as f:
            json.dump(top_index, f, indent=4)

if __name__ == '__main__':
    main() 