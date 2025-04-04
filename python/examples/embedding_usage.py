#!/usr/bin/env python3
"""
Example script demonstrating the use of word embeddings with the wordlists package.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the local package
sys.path.append(str(Path(__file__).parent.parent))

from wordlists import (
    get_wordlist,
    get_word_embedding,
    get_similar_words,
    get_analogy,
    get_embeddings
)


def main():
    """Demonstrate the use of word embeddings with the wordlists package."""
    print("Word Embeddings Examples\n")
    
    # Example 1: Load embeddings filtered to our word lists
    print("=== Example 1: Load Embeddings ===")
    # Get a combined set of words from our wordlists
    swadesh_100 = set(get_wordlist("swadesh-100"))
    basic_english = set(get_wordlist("basic-english"))
    combined_words = swadesh_100.union(basic_english)
    
    print(f"Combined wordlists have {len(combined_words)} unique words")
    
    # Load embeddings for just these words
    embeddings = get_embeddings(word_filter=combined_words)
    
    # Check coverage statistics
    coverage = embeddings.get_vocabulary_coverage(list(combined_words))
    print(f"Coverage statistics:")
    print(f"  Total words: {coverage['total']}")
    print(f"  Words with embeddings: {coverage['covered']} ({coverage['percent']:.1f}%)")
    print(f"  First few missing words: {', '.join(coverage['missing'])}")
    print()
    
    # Example 2: Find similar words
    print("=== Example 2: Find Similar Words ===")
    for word in ["water", "king", "happy", "long"]:
        if word in embeddings.vocabulary:
            similar = get_similar_words(word, n=5)
            print(f"Words similar to '{word}':")
            for similar_word, similarity in similar:
                print(f"  {similar_word}: {similarity:.4f}")
        else:
            print(f"'{word}' not found in embeddings")
        print()
    
    # Example 3: Solve analogies
    print("=== Example 3: Solve Analogies ===")
    analogies = [
        ("man", "woman", "king"),
        ("water", "ice", "hot"),
        ("good", "better", "bad")
    ]
    
    for word1, word2, word3 in analogies:
        if all(w in embeddings.vocabulary for w in [word1, word2, word3]):
            results = get_analogy(word1, word2, word3, n=3)
            print(f"'{word1}' is to '{word2}' as '{word3}' is to:")
            for result_word, score in results:
                print(f"  {result_word}: {score:.4f}")
        else:
            print(f"Analogy '{word1}:{word2}::{word3}:?' cannot be solved (missing words)")
        print()
    
    # Example 4: Explore semantic clusters
    print("=== Example 4: Explore Semantic Clusters ===")
    semantic_seeds = {
        "body_parts": ["head", "hand", "foot", "eye"],
        "colors": ["red", "green", "blue", "yellow"],
        "animals": ["dog", "cat", "bird", "horse"],
        "time": ["day", "night", "month", "year"]
    }
    
    for category, seeds in semantic_seeds.items():
        print(f"Words in semantic category '{category}':")
        # Get words similar to any of the seed words
        all_similar = {}
        for seed in seeds:
            if seed in embeddings.vocabulary:
                for word, score in get_similar_words(seed, n=10):
                    # Accumulate the highest similarity score for each word
                    if word not in all_similar or score > all_similar[word]:
                        all_similar[word] = score
        
        # Show top words excluding the seeds
        top_words = sorted(
            [(w, s) for w, s in all_similar.items() if w not in seeds],
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        for word, score in top_words:
            print(f"  {word}: {score:.4f}")
        print()


if __name__ == "__main__":
    main() 