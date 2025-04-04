#!/usr/bin/env python3
"""
Script to precompute embeddings for all words in our wordlists using sentence-transformers.
These precomputed embeddings are then stored in a compressed NumPy file
for efficient loading and use in the runtime wordlists package.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Optional
from sentence_transformers import SentenceTransformer
import argparse
import time

# Constants
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
WORDLISTS_DIR = DATA_DIR / "wordlists"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_OUTPUT = "precomputed_embeddings.npz"


def load_words_from_file(file_path: Path) -> List[str]:
    """
    Load words from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of words
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different JSON formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "words" in data:
            return data["words"]
        elif isinstance(data, dict):
            # Some wordlists store words as dictionary keys
            return list(data.keys())
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    
    return []


def collect_words_from_directory(directory: Path) -> Set[str]:
    """
    Recursively collect words from all JSON files in a directory.
    
    Args:
        directory: Directory to scan for JSON files
        
    Returns:
        Set of words
    """
    all_words = set()
    if not directory.exists():
        return all_words
    
    for file_path in directory.glob("**/*.json"):
        if file_path.is_file():
            words = load_words_from_file(file_path)
            all_words.update(words)
    
    return all_words


def download_model(model_name: str) -> SentenceTransformer:
    """
    Download and return the specified sentence transformer model.
    
    Args:
        model_name: Name of the model to download
        
    Returns:
        SentenceTransformer model
    """
    print(f"Downloading sentence transformer model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"Model downloaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    return model


def compute_embeddings(model: SentenceTransformer, words: List[str], batch_size: int = 64) -> np.ndarray:
    """
    Compute embeddings for a list of words using sentence-transformers.
    
    Args:
        model: SentenceTransformer model
        words: List of words to embed
        batch_size: Batch size for embedding computation
        
    Returns:
        NumPy array of embeddings
    """
    print(f"Computing embeddings for {len(words)} words...")
    start_time = time.time()
    
    # Use the model's encode method with batching
    embeddings = model.encode(words, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True)
    
    elapsed_time = time.time() - start_time
    print(f"Embeddings computed in {elapsed_time:.2f} seconds")
    
    return embeddings


def save_embeddings(embeddings: np.ndarray, words: List[str], output_file: Path) -> None:
    """
    Save embeddings and words to a compressed NumPy file.
    
    Args:
        embeddings: NumPy array of embeddings
        words: List of words corresponding to the embeddings
        output_file: Path to save the embeddings
    """
    print(f"Saving embeddings to {output_file}...")
    
    # Create the embeddings directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert words to a numpy array
    words_array = np.array(words, dtype=object)
    
    # Save the embeddings and words
    np.savez_compressed(
        output_file,
        embeddings=embeddings,
        words=words_array
    )
    
    # Save metadata
    metadata = {
        "num_words": len(words),
        "embedding_dim": embeddings.shape[1],
        "model": DEFAULT_MODEL,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file_size_mb": os.path.getsize(output_file) / (1024 * 1024),
    }
    
    with open(output_file.with_suffix('.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved {len(words)} embeddings with dimension {embeddings.shape[1]}")
    print(f"File size: {metadata['file_size_mb']:.2f} MB")


def main() -> None:
    """Main function to precompute embeddings."""
    parser = argparse.ArgumentParser(description="Precompute embeddings for wordlists.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Sentence transformer model name")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="Output file name")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size for embedding computation")
    args = parser.parse_args()
    
    # Create the embeddings directory if it doesn't exist
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = EMBEDDINGS_DIR / args.output
    
    # Collect words from all wordlists
    print("Collecting words from all wordlists...")
    all_words = set()
    
    # Historical wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "historical"))
    
    # Corpus wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "corpus"))
    
    # Categories wordlists
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "categories"))
    
    # Stop words
    all_words.update(collect_words_from_directory(WORDLISTS_DIR / "stop"))
    
    # Sort words alphabetically for consistency
    sorted_words = sorted(list(all_words))
    print(f"Collected {len(sorted_words)} unique words from all wordlists")
    
    # Download the model
    model = download_model(args.model)
    
    # Compute embeddings
    embeddings = compute_embeddings(model, sorted_words, batch_size=args.batch_size)
    
    # Save embeddings
    save_embeddings(embeddings, sorted_words, output_path)
    
    print(f"Precomputation complete. Embeddings saved to {output_path}")


if __name__ == "__main__":
    main() 