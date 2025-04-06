#!/usr/bin/env python3
"""
Test the speed of embedding similarity operations with Word Atlas.
"""

import time
import random
from word_atlas import WordAtlas

def main():
    print("Initializing Word Atlas...")
    start_time = time.time()
    atlas = WordAtlas()
    load_time = time.time() - start_time
    print(f"Loaded {len(atlas)} words and phrases in {load_time:.2f} seconds\n")
    
    # Test 1: Getting a word embedding
    print("Test 1: Getting a single word embedding")
    start_time = time.time()
    embedding = atlas.get_embedding("happiness")
    duration = time.time() - start_time
    print(f"  Got embedding with shape {embedding.shape} in {duration:.6f} seconds")
    
    # Test 2: Computing similarity between two words
    print("\nTest 2: Computing similarity between two words")
    start_time = time.time()
    similarity = atlas.word_similarity("happiness", "joy")
    duration = time.time() - start_time
    print(f"  Similarity between 'happiness' and 'joy': {similarity:.4f}")
    print(f"  Computed in {duration:.6f} seconds")
    
    # Test 3: Finding similar words
    print("\nTest 3: Finding similar words")
    start_time = time.time()
    similar_words = atlas.get_similar_words("happiness", n=10)
    duration = time.time() - start_time
    print(f"  Found {len(similar_words)} similar words in {duration:.6f} seconds")
    print(f"  Top results:")
    for word, score in similar_words:
        print(f"    {word}: {score:.4f}")
    
    # Test 4: Batch similarity computation
    print("\nTest 4: Computing similarities for 100 random word pairs")
    # Select 100 random words
    random_words = random.sample(list(atlas.word_data.keys()), 200)
    word_pairs = [(random_words[i], random_words[i+1]) for i in range(0, 199, 2)]
    
    start_time = time.time()
    similarities = [atlas.word_similarity(w1, w2) for w1, w2 in word_pairs[:100]]
    duration = time.time() - start_time
    avg_similarity = sum(similarities) / len(similarities)
    print(f"  Computed {len(similarities)} similarities in {duration:.6f} seconds")
    print(f"  Average time per pair: {duration/len(similarities):.6f} seconds")
    print(f"  Average similarity: {avg_similarity:.4f}")
    
    # Test 5: Getting similar words for multiple queries
    print("\nTest 5: Getting similar words for 10 random words")
    test_words = random.sample(list(atlas.word_data.keys()), 10)
    start_time = time.time()
    for word in test_words:
        similar = atlas.get_similar_words(word, n=10)
    duration = time.time() - start_time
    print(f"  Found similar words for 10 queries in {duration:.6f} seconds")
    print(f"  Average time per query: {duration/10:.6f} seconds")
    
    # Test 6: Memory usage
    import sys
    print("\nMemory Usage:")
    embedding_size_bytes = sys.getsizeof(atlas.embeddings)
    word_data_size_bytes = sys.getsizeof(atlas.word_data)
    print(f"  Embeddings: {embedding_size_bytes / (1024*1024):.2f} MB")
    print(f"  Word data: {word_data_size_bytes / (1024*1024):.2f} MB")
    
    print("\nDone!")

if __name__ == "__main__":
    main() 