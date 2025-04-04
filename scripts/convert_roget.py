import os
import json

def clean_word(word_obj):
    # Extract the word from the dictionary
    if isinstance(word_obj, dict):
        word = word_obj['word'].split('  ')[0].strip()  # Split on double space to remove POS
    else:
        word = str(word_obj).strip()
    
    # Skip entries that are clearly not words or proper phrases
    if not word or word.startswith(('*', '-', '{', '<', '|', '[')) or word.startswith('"') or word.endswith('"'):
        return ''
    
    # Remove any remaining numbers, control characters and extra whitespace
    word = ''.join(c for c in word if ord(c) >= 32)  # Remove control characters
    
    # Remove part of speech tags that appear after single or double spaces
    parts = word.split()
    if len(parts) > 1 and parts[-1].lower() in ['v', 'adj', 'adv', 'n', 'prep', 'conj', 'pron', 'interj']:
        parts.pop()
    word = ' '.join(parts)
    
    # Remove any remaining numbers and clean up whitespace
    word = ' '.join(''.join(c for c in part if not c.isdigit()).strip() 
                   for part in word.split())
    
    # Skip if the cleaned word is too short or contains odd characters
    if len(word) < 2 or any(c in word for c in '*-{<>}|[]\\'):
        return ''
        
    return word.strip()

def convert_file(input_file, output_file, all_words, index):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    if not data.get('words'):
        return  # Skip empty files
    
    # Extract class, section, and category info
    class_name = data.get('class', '')
    section = data.get('section', '')
    category = data.get('category', '')
    
    # Clean and deduplicate words
    words = data.get('words', [])
    clean_words = set()
    for word_obj in words:
        cleaned = clean_word(word_obj)
        if cleaned:  # Only add non-empty words
            clean_words.add(cleaned)
            all_words.add(cleaned)  # Add to comprehensive list
    
    # Sort the unique words
    clean_words = sorted(list(clean_words))
    
    # Add to index
    category_id = os.path.splitext(os.path.basename(input_file))[0]
    index['categories'][category_id] = {
        'name': category.strip(),
        'section': section,
        'word_count': len(clean_words)
    }
    
    # Create new data structure
    new_data = {
        "type": "historical",
        "source": "roget",
        "category": category.strip(),
        "description": f"Roget's Thesaurus - {class_name} / {section} / {category}",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Roget, P. M. (1852). Thesaurus of English Words and Phrases. Longman, Brown, Green, and Longmans.",
        "total_words": len(clean_words),
        "words": clean_words
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the new format
    with open(output_file, 'w') as f:
        json.dump(new_data, f, indent=4)

def main():
    input_dir = 'data/wordlists/historical/roget'
    output_dir = input_dir  # Output to same directory
    
    # Initialize comprehensive word list and index
    all_words = set()
    index = {
        'categories': {},
        'total_categories': 0,
        'total_words': 0
    }
    
    # Process all JSON files
    for filename in os.listdir(input_dir):
        if filename.endswith('.json') and filename not in ['index.json', 'comprehensive.json']:
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)  # Same filename, just cleaned content
            try:
                convert_file(input_file, output_file, all_words, index)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Update index totals
    index['total_categories'] = len(index['categories'])
    index['total_words'] = len(all_words)
    
    # Write comprehensive word list
    comprehensive_data = {
        "type": "historical",
        "source": "roget",
        "category": "Comprehensive",
        "description": "Roget's Thesaurus - Complete word list from all categories",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Roget, P. M. (1852). Thesaurus of English Words and Phrases. Longman, Brown, Green, and Longmans.",
        "total_words": len(all_words),
        "words": sorted(list(all_words))
    }
    
    with open(os.path.join(output_dir, 'comprehensive.json'), 'w') as f:
        json.dump(comprehensive_data, f, indent=4)
    
    # Write index
    with open(os.path.join(output_dir, 'index.json'), 'w') as f:
        json.dump(index, f, indent=4)

if __name__ == '__main__':
    main() 