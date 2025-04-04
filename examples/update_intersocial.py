#!/usr/bin/env python3
"""
Script to update word_data.json to add ROGET_INTERSOCIAL attribute.
- Adds ROGET_INTERSOCIAL=False to all words
- Sets ROGET_INTERSOCIAL=True for all uncategorized words
"""

import json
import os
from pathlib import Path
import sys

def main():
    # Add parent directory to path so we can import word_atlas
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Load uncategorized words from file
    with open('uncategorized_words.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Skip the first line (comment) and strip whitespace
        uncategorized = set(line.strip() for line in lines[1:] if line.strip())
    
    print(f"Loaded {len(uncategorized)} uncategorized words")
    
    # Find the word_data.json file
    data_dir = Path(__file__).parent.parent / 'data'
    word_data_path = data_dir / 'word_data.json'
    
    if not word_data_path.exists():
        print(f"Error: Could not find word_data.json at {word_data_path}")
        # Try to find it in common locations
        possible_paths = [
            Path.cwd() / 'data' / 'word_data.json',
            Path.cwd().parent / 'data' / 'word_data.json',
            Path.home() / 'english_word_atlas' / 'data' / 'word_data.json',
        ]
        
        for path in possible_paths:
            if path.exists():
                word_data_path = path
                print(f"Found word_data.json at {word_data_path}")
                break
        
        if not word_data_path.exists():
            print("Error: Could not find word_data.json in any common location.")
            print("Please specify the full path to word_data.json:")
            user_path = input("> ")
            word_data_path = Path(user_path)
            if not word_data_path.exists():
                print(f"Error: {word_data_path} does not exist.")
                return
    
    # Create backup of word_data.json
    backup_path = word_data_path.with_name(f"{word_data_path.stem}_backup.json")
    print(f"Creating backup at {backup_path}")
    with open(word_data_path, 'r', encoding='utf-8') as f:
        word_data = json.load(f)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(word_data, f, indent=2)
    
    # Add ROGET_INTERSOCIAL attribute to all words, setting it to True for uncategorized words
    modified_count = 0
    for word, attrs in word_data.items():
        if "ROGET_INTERSOCIAL" not in attrs:
            attrs["ROGET_INTERSOCIAL"] = word in uncategorized
            modified_count += 1
    
    # Save updated word_data.json
    print(f"Modified {modified_count} words.")
    print(f"Setting ROGET_INTERSOCIAL=True for {len(uncategorized)} uncategorized words.")
    print(f"Writing updated word_data.json to {word_data_path}")
    
    with open(word_data_path, 'w', encoding='utf-8') as f:
        json.dump(word_data, f, indent=2)
    
    print("Done!")
    print("You may need to rebuild any indices in your WordAtlas class.")

if __name__ == "__main__":
    main() 