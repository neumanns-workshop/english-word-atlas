import json
from pathlib import Path

def create_basic_index():
    # Define the main categories from the original Ogden's Basic English
    categories = [
        {
            "name": "Operations",
            "id": "operations",
            "description": "Words expressing operations and relationships",
            "word_count": 100
        },
        {
            "name": "Things - General",
            "id": "things_general",
            "description": "General vocabulary for things and objects",
            "word_count": 400
        },
        {
            "name": "Things - Picturable",
            "id": "things_picturable",
            "description": "Concrete, picturable objects and things",
            "word_count": 200
        },
        {
            "name": "Qualities - General",
            "id": "qualities_general",
            "description": "General adjectives and qualities",
            "word_count": 100
        },
        {
            "name": "Qualities - Opposites",
            "id": "qualities_opposites",
            "description": "Opposite pairs of qualities",
            "word_count": 50
        }
    ]
    
    index = {
        "type": "historical",
        "source": "ogden",
        "description": "Ogden's Basic English - Core word categories",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd.",
        "total_categories": len(categories),
        "total_words": sum(cat["word_count"] for cat in categories),
        "categories": categories
    }
    
    # Create output directory if it doesn't exist
    output_dir = Path('data/wordlists/historical/ogden/basic')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write index file
    with open(output_dir / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

if __name__ == "__main__":
    create_basic_index() 