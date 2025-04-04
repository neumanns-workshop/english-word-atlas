import re
import json
from pathlib import Path

def clean_word(word):
    # Remove punctuation and whitespace
    word = word.strip(' .,')
    # Handle alternative spellings
    if '/' in word:
        word = word.split('/')[0]  # Take first variant
    return word

def parse_categories(text):
    # Split into sections by blank lines
    sections = text.split('\n\n')
    categories = {}
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # First line is the category name
        category = lines[0].split('/')[0].strip()
        words = []
        
        # Process remaining lines
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('By adding'):  # Skip instructions
                continue
            # Split on periods and commas, then split on spaces
            parts = re.split('[,.]', line)
            for part in parts:
                part = part.strip()
                if part:
                    words.extend(w.strip() for w in part.split() if w.strip())
        
        # Clean and filter words
        words = [clean_word(w) for w in words]
        words = [w for w in words if w and not w.startswith('(') and not w.startswith('-')]
        
        if category and words:
            categories[category] = words
    
    return categories

def create_category_json(words, category, output_path):
    # Convert category name to file-friendly format
    category_id = re.sub(r'[^a-z0-9]+', '_', category.lower()).strip('_')
    
    data = {
        "type": "historical",
        "source": "ogden",
        "category": category,
        "description": f"Ogden's Basic English - {category} semantic category",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd.",
        "total_words": len(words),
        "words": sorted(list(set(words)))  # Remove duplicates and sort
    }
    
    with open(output_path / f"{category_id}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def create_comprehensive_json(categories, output_path):
    # Get all unique words across all categories
    all_words = set()
    for words in categories.values():
        all_words.update(words)
    
    data = {
        "type": "historical",
        "source": "ogden",
        "description": "Ogden's Basic English - Complete list of all words across all semantic categories",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd.",
        "total_words": len(all_words),
        "words": sorted(list(all_words))
    }
    
    with open(output_path / "comprehensive.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    # Read input file
    with open('data/wordlists/historical/ogden/categories/temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create output directory
    output_dir = Path('data/wordlists/historical/ogden/categories')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse categories
    categories = parse_categories(text)
    
    # Create individual category files
    for category, words in categories.items():
        create_category_json(words, category, output_dir)
    
    # Create comprehensive file with all words
    create_comprehensive_json(categories, output_dir)
    
    # Create index file
    index = {
        "type": "historical",
        "source": "ogden",
        "description": "Ogden's Basic English - Semantic Categories Index",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd.",
        "categories": [
            {
                "name": category,
                "id": re.sub(r'[^a-z0-9]+', '_', category.lower()).strip('_'),
                "word_count": len(words)
            }
            for category, words in categories.items()
        ]
    }
    
    with open(output_dir / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

if __name__ == "__main__":
    main() 