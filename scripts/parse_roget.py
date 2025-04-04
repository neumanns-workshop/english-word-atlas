import re
import json
import os

def clean_word(word):
    # Remove common annotations and punctuation
    word = re.sub(r'\[.*?\]', '', word)  # Remove [...] annotations
    word = re.sub(r'\&c\.', '', word)    # Remove &c.
    word = re.sub(r'\(.*?\)', '', word)  # Remove (...) annotations
    word = re.sub(r'[,;.]', '', word)    # Remove punctuation
    word = word.strip()
    return word

def sanitize_filename(name):
    # Remove any text within brackets and their contents
    name = re.sub(r'\[.*?\]', '', name)
    # Remove any text within angle brackets and their contents
    name = re.sub(r'<.*?>', '', name)
    # Replace any non-alphanumeric characters with underscores
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Replace multiple underscores with a single one
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Convert to lowercase
    return name.lower()

def parse_roget(filename):
    current_class = ""
    current_section = ""
    current_category = ""
    current_category_num = ""
    categories = {}
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match CLASS
        class_match = re.match(r'\s*CLASS\s+([IVX]+)', line)
        if class_match:
            current_class = class_match.group(1)
            continue
            
        # Match SECTION
        section_match = re.match(r'\s*SECTION\s+([IVX]+)\.\s*(.*)', line)
        if section_match:
            current_section = f"{section_match.group(1)}. {section_match.group(2)}"
            continue
            
        # Match category number and name
        category_match = re.match(r'\s*#(\d+)\.\s*(.*?)\.?--', line)
        if category_match:
            current_category_num = category_match.group(1)
            current_category = category_match.group(2)
            categories[current_category_num] = {
                "class": current_class,
                "section": current_section,
                "category": current_category,
                "words": []
            }
            continue
            
        # Match word lists (lines starting with N., V., Adj., Adv.)
        word_line_match = re.match(r'\s*(N\.|V\.|Adj\.|Adv\.)\s*(.*)', line)
        if word_line_match and current_category_num:
            pos = word_line_match.group(1).rstrip('.')
            words_text = word_line_match.group(2)
            
            # Split on obvious word boundaries and clean each word
            words = [w for w in re.split(r'[,;]', words_text) if w.strip()]
            clean_words = []
            for word in words:
                cleaned = clean_word(word)
                if cleaned and len(cleaned) > 1:  # Avoid single letters
                    clean_words.append(cleaned)
            
            # Add to category with POS tag
            if clean_words:
                categories[current_category_num]["words"].extend([
                    {"word": w, "pos": pos} for w in clean_words
                ])

    return categories

def save_categories(categories, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each category to a separate file
    for num, data in categories.items():
        # Format number as 3-digit string and sanitize category name
        num_str = num.zfill(3)
        safe_category = sanitize_filename(data['category'])
        filename = f"{num_str}_{safe_category}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    # Create an index file
    index = {
        num: {
            "class": data["class"],
            "section": data["section"],
            "category": data["category"],
            "word_count": len(data["words"])
        }
        for num, data in categories.items()
    }
    
    with open(os.path.join(output_dir, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    input_file = "roget15a.txt"
    output_dir = "data/wordlists/categories/roget"
    
    print("Parsing Roget's Thesaurus...")
    categories = parse_roget(input_file)
    print(f"Found {len(categories)} categories")
    
    print("Saving categories to separate files...")
    save_categories(categories, output_dir)
    print("Done!") 