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

def parse_section(text, section_name):
    # Extract words between the section name and the next section or end
    pattern = f"{section_name}(.*?)(?=\n\w+ -|$)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    
    # Split into words and clean
    words_text = match.group(1)
    words = [clean_word(w) for w in words_text.replace('\n', ' ').split(',')]
    return [w for w in words if w]  # Remove empty strings

def create_wordlist_json(words, category, output_path):
    data = {
        "type": "historical",
        "source": "ogden",
        "description": f"Ogden's Basic English - {category} word list",
        "license": "Public Domain",
        "version": "1.0",
        "citation": "Ogden, C. K. (1930). Basic English: A General Introduction with Rules and Grammar. Paul Treber & Co., Ltd.",
        "total_words": len(words),
        "words": words
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    # Read input file
    with open('data/wordlists/historical/ogden/temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create output directory
    output_dir = Path('data/wordlists/historical/ogden')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse each section
    sections = {
        "operations": ("OPERATIONS - 100 words", "operations"),
        "things_general": ("THINGS - 400 General words", "things_general"),
        "things_picturable": ("THINGS - 200 Picturable words", "things_picturable"),
        "qualities_general": ("QUALITIES - 100 General", "qualities_general"),
        "qualities_opposites": ("QUALITIES - 50 Opposites", "qualities_opposites")
    }
    
    # Create individual files
    for file_name, (section_header, category_name) in sections.items():
        words = parse_section(text, section_header)
        output_path = output_dir / f"{file_name}.json"
        create_wordlist_json(words, category_name, output_path)
    
    # Create combined file with all words
    all_words = []
    for _, (section_header, _) in sections.items():
        all_words.extend(parse_section(text, section_header))
    
    create_wordlist_json(
        all_words,
        "complete",
        output_dir / "basic_english.json"
    )

if __name__ == "__main__":
    main() 