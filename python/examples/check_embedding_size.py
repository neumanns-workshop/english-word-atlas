#!/usr/bin/env python3
"""
Script to check the size of embeddings when filtered to our comprehensive wordlist.
"""

import sys
import os
import json
from pathlib import Path
import zipfile
import numpy as np
from time import time

# Add the parent directory to the path so we can import the local package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import get_embeddings


def extract_glove_file(embedding_file="glove.6B.50d.txt"):
    """Extract the GloVe embedding file from the zip if it doesn't exist."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    embeddings_dir = data_dir / "embeddings"
    embedding_path = embeddings_dir / embedding_file
    zip_path = embeddings_dir / "glove.6B.zip"
    
    if not embedding_path.exists() and zip_path.exists():
        print(f"Extracting {embedding_file} from {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if embedding_file in zip_ref.namelist():
                zip_ref.extract(embedding_file, embeddings_dir)
                print(f"Extraction complete: {embedding_path}")
            else:
                print(f"Warning: {embedding_file} not found in {zip_path}")
                print(f"Available files: {zip_ref.namelist()}")
                return False
    
    return embedding_path.exists()


def check_file_size(file_path):
    """Check the size of a file in MB."""
    size_bytes = Path(file_path).stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def load_full_embeddings(embedding_file="glove.6B.50d.txt"):
    """Load the full GloVe embeddings and report stats."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    embeddings_dir = data_dir / "embeddings"
    embedding_path = embeddings_dir / embedding_file
    
    if not embedding_path.exists():
        print(f"Error: {embedding_path} does not exist")
        return None
    
    print(f"File size: {check_file_size(embedding_path):.2f} MB")
    
    # Count lines and vector dimension
    word_count = 0
    vector_size = 0
    
    with open(embedding_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:  # First line
                parts = line.strip().split()
                if len(parts) == 2:  # Header line (vocab_size, vector_size)
                    continue
                else:
                    # First actual embedding
                    vector_size = len(parts) - 1
            word_count += 1
            if i == 0:
                vector_size = len(line.strip().split()) - 1
                sample_line = line.strip()
    
    print(f"Full embeddings stats:")
    print(f"  Words: {word_count}")
    print(f"  Vector size: {vector_size}")
    print(f"  Memory usage estimate: {word_count * vector_size * 4 / (1024*1024):.2f} MB")
    print(f"  Sample: {sample_line[:60]}...")
    
    return word_count, vector_size


def load_words_from_file(file_path):
    """Load words from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "words" in data and isinstance(data["words"], list):
                return data["words"]
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
    
    return []


def main():
    """Check the size of embeddings when filtered to our wordlists."""
    print("Checking GloVe Embeddings Size After Filtering\n")
    
    # First ensure the GloVe file is extracted
    file_exists = extract_glove_file()
    if not file_exists:
        print("Failed to extract GloVe file")
        return
    
    # Load basic stats about the full embeddings
    print("\nFull Embeddings:")
    full_stats = load_full_embeddings()
    if not full_stats:
        return
    
    # Get our comprehensive wordlist by loading directly from the JSON files
    print("\nFiltering to wordlists:")
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load words from files
    wordlists = {}
    
    # Historical comprehensive
    historical_file = data_dir / "wordlists" / "historical" / "comprehensive.json"
    if historical_file.exists():
        wordlists["historical"] = load_words_from_file(historical_file)
    
    # Swadesh 100
    swadesh_100_file = data_dir / "wordlists" / "historical" / "swadesh" / "swadesh_100.json"
    if swadesh_100_file.exists():
        wordlists["swadesh-100"] = load_words_from_file(swadesh_100_file)
    
    # Swadesh 207
    swadesh_207_file = data_dir / "wordlists" / "historical" / "swadesh" / "swadesh_207.json"
    if swadesh_207_file.exists():
        wordlists["swadesh-207"] = load_words_from_file(swadesh_207_file)
    
    # Basic English
    basic_english_file = data_dir / "wordlists" / "historical" / "ogden" / "basic" / "comprehensive.json"
    if basic_english_file.exists():
        wordlists["basic-english"] = load_words_from_file(basic_english_file)
    
    # Stop words
    stop_words_file = data_dir / "wordlists" / "stop_words" / "comprehensive.json"
    if stop_words_file.exists():
        wordlists["stop-words"] = load_words_from_file(stop_words_file)
    
    # Print stats for each list
    for name, words in wordlists.items():
        print(f"  {name}: {len(words)} words")
    
    # Create a combined set
    all_words = set()
    for words in wordlists.values():
        all_words.update(words)
    
    print(f"\nTotal unique words across all lists: {len(all_words)}")
    
    # Time the loading of filtered embeddings
    print("\nLoading filtered embeddings:")
    start_time = time()
    embeddings = get_embeddings(word_filter=all_words)
    load_time = time() - start_time
    
    # Get coverage stats
    coverage = embeddings.get_vocabulary_coverage(list(all_words))
    
    print(f"Filtered embeddings stats:")
    print(f"  Load time: {load_time:.2f} seconds")
    print(f"  Words: {len(embeddings.vocabulary)}")
    print(f"  Vector size: {embeddings.vector_size}")
    print(f"  Memory usage estimate: {len(embeddings.vocabulary) * embeddings.vector_size * 4 / (1024*1024):.2f} MB")
    print(f"  Coverage: {coverage['percent']:.1f}% of wordlists")
    print(f"  Missing examples: {', '.join(coverage['missing'])}")
    
    # Calculate savings
    if full_stats:
        full_word_count, _ = full_stats
        savings_percent = (1 - len(embeddings.vocabulary) / full_word_count) * 100
        print(f"\nSize reduction: {savings_percent:.1f}% smaller than full embeddings")


if __name__ == "__main__":
    main() 