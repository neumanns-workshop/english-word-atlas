#!/usr/bin/env python3
"""
Example script demonstrating how to use precomputed sentence-transformer embeddings.
"""

import os
import sys
from pathlib import Path
import numpy as np

# Add the parent directory to the path so we can import our package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists.embeddings import PrecomputedEmbeddings


def main():
    """Main function to demonstrate precomputed embeddings usage."""
    # Initialize precomputed embeddings
    print("Loading precomputed embeddings...")
    
    try:
        # Load the default precomputed embeddings
        embeddings = PrecomputedEmbeddings()
    except FileNotFoundError:
        print("Precomputed embeddings not found. Please run the precompute_embeddings.py script first.")
        print("Example: python scripts/precompute_embeddings.py")
        return

    # Example 1: Get embedding for a word
    word = "computer"
    embedding = embeddings.get_embedding(word)
    if embedding is not None:
        print(f"\nEmbedding for '{word}':")
        print(f"  Shape: {embedding.shape}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print(f"\nNo embedding found for '{word}'")

    # Example 2: Find similar words
    word = "happy"
    print(f"\nWords similar to '{word}':")
    similar_words = embeddings.find_similar_words(word, n=5)
    for similar_word, similarity in similar_words:
        print(f"  {similar_word}: {similarity:.4f}")

    # Example 3: Solve analogy
    print("\nSolving analogy: 'man is to woman as king is to ?'")
    results = embeddings.solve_analogy("man", "woman", "king", n=3)
    for word, score in results:
        print(f"  {word}: {score:.4f}")

    # Example 4: Check vocabulary coverage against a simple list
    test_words = ["dog", "cat", "computer", "algorithm", "nonexistentword123", "happiness"]
    coverage, with_embeddings, without_embeddings = embeddings.get_vocabulary_coverage(test_words)
    
    print(f"\nVocabulary coverage for test words:")
    print(f"  Coverage: {coverage:.2%}")
    print(f"  Words with embeddings: {', '.join(sorted(list(with_embeddings)))}")
    print(f"  Words without embeddings: {', '.join(sorted(list(without_embeddings)))}")

    # Example 5: Check if words are in the vocabulary
    words_to_check = ["hello", "world", "nonexistentword456"]
    print("\nChecking if words are in vocabulary:")
    for word in words_to_check:
        print(f"  '{word}': {word in embeddings}")

    # Example 6: Get embedding size
    print(f"\nEmbedding vocabulary size: {len(embeddings)} words")
    print(f"Embedding dimension: {embeddings.embedding_dim}")


if __name__ == "__main__":
    main() 