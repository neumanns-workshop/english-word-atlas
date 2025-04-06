#!/usr/bin/env python3
"""
Fast embedding-based semantic discrimination task.
Uses pre-generated sets of semantically related words.
"""

import random
import time
from word_atlas import WordAtlas

# Pre-selected anchor words from different semantic domains
ANCHOR_WORDS = [
    # Emotions
    "happiness", "anger", "fear", "sadness", 
    # Abstract concepts
    "freedom", "justice", "truth", "knowledge",
    # Concrete objects
    "tree", "car", "house", "book",
    # Actions
    "run", "eat", "sleep", "talk",
    # Qualities
    "beautiful", "strong", "smart", "tall"
]

# Pre-defined difficulty levels with similarity thresholds
DIFFICULTY_THRESHOLDS = {
    "easy": (0.0, 0.3),    # Very dissimilar (similarity < 0.3)
    "medium": (0.3, 0.5),  # Moderately dissimilar (similarity 0.3-0.5)
    "hard": (0.5, 0.7)     # Slightly dissimilar (similarity 0.5-0.7)
}

def main():
    print("Initializing Word Atlas...")
    atlas = WordAtlas()
    print(f"Loaded {len(atlas)} words and phrases\n")
    
    print("=" * 60)
    print("FAST EMBEDDING-BASED SEMANTIC DISCRIMINATION TASK")
    print("=" * 60)
    print("Instructions: For each set of 4 words, identify the word that is")
    print("semantically different from the others (the odd one out).")
    print()
    
    # Create questions with varying difficulty
    questions = []
    
    print("Preparing questions...")
    for difficulty, (min_sim, max_sim) in DIFFICULTY_THRESHOLDS.items():
        print(f"Generating {difficulty} questions...")
        # Try different anchor words until we have enough questions
        for anchor in random.sample(ANCHOR_WORDS, len(ANCHOR_WORDS)):
            q = create_question(atlas, anchor, min_sim, max_sim)
            if q:
                words, odd_idx, sims = q
                questions.append((words, odd_idx, sims, difficulty))
                print(f"  Created {difficulty} question using '{anchor}'")
                # Only need one question per difficulty level
                break
    
    # Start the task
    score = 0
    total = len(questions)
    
    print(f"\nStarting task with {total} questions...")
    input("Press Enter to begin.")
    print()
    
    start_time = time.time()
    
    for i, (words, correct_index, similarities, difficulty) in enumerate(questions):
        # Display the question
        print(f"Question {i+1}/{total} [{difficulty}]:")
        for j, word in enumerate(words):
            print(f"  {j+1}. {word}")
        
        # Get user's answer
        while True:
            try:
                answer = int(input("\nWhich word doesn't belong? (1-4): "))
                if 1 <= answer <= 4:
                    break
                print("Please enter a number between 1 and 4.")
            except ValueError:
                print("Please enter a number between 1 and 4.")
        
        # Check answer
        correct = (answer - 1) == correct_index
        if correct:
            score += 1
            print("Correct! ✓")
        else:
            print(f"Incorrect. The odd one out was: {words[correct_index]} (option {correct_index+1})")
        
        # Provide explanation about embeddings
        similar_words = [words[j] for j in range(4) if j != correct_index]
        print(f"Similarity analysis:")
        print(f"  The odd word '{words[correct_index]}' has these similarity scores to the other words:")
        for word, sim in zip(similar_words, similarities):
            print(f"    - {word}: {sim:.3f}")
        print()
    
    # Show results
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 60)
    print(f"Task complete! Your score: {score}/{total} ({score/total*100:.1f}%)")
    print(f"Time taken: {duration:.1f} seconds")
    print("=" * 60)


def create_question(atlas, anchor, min_sim, max_sim):
    """Create a single discrimination question efficiently.
    
    Args:
        atlas: The WordAtlas instance
        anchor: The anchor word to build the question around
        min_sim: Minimum similarity for the odd word
        max_sim: Maximum similarity for the odd word
    
    Returns:
        Tuple of (all_words, odd_index, similarities) or None if question couldn't be created
    """
    # Get similar words to the anchor to form the cluster
    similar_pairs = atlas.get_similar_words(anchor, n=30)
    
    # Find highly similar words for the cluster (similarity > 0.7)
    high_similar = [(w, s) for w, s in similar_pairs if s >= 0.7 and " " not in w 
                    and w != anchor]
    
    # Find words in the desired similarity range for the odd one out
    odd_candidates = [(w, s) for w, s in similar_pairs 
                     if min_sim <= s <= max_sim and " " not in w 
                     and w != anchor]
    
    # Ensure we have enough words
    if len(high_similar) < 3 or not odd_candidates:
        return None
    
    # Select 3 similar words and 1 odd word
    cluster_words = [w for w, _ in random.sample(high_similar, 3)]
    odd_word, _ = random.choice(odd_candidates)
    
    # Calculate similarities between odd word and cluster words
    similarities = [atlas.word_similarity(odd_word, w) for w in cluster_words]
    
    # Combine and shuffle
    all_words = cluster_words + [odd_word]
    random.shuffle(all_words)
    
    # Find index of the odd word
    odd_index = all_words.index(odd_word)
    
    return all_words, odd_index, similarities


if __name__ == "__main__":
    main() 