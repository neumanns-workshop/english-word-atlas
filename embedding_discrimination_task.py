#!/usr/bin/env python3
"""
Embedding-based semantic discrimination task.
For each question, three words are semantically similar in embedding space,
and one word is the odd one out with a different embedding.
"""

import random
import time
import numpy as np
from word_atlas import WordAtlas

def main():
    print("Initializing Word Atlas...")
    atlas = WordAtlas()
    print(f"Loaded {len(atlas)} words and phrases\n")
    
    print("=" * 60)
    print("EMBEDDING-BASED SEMANTIC DISCRIMINATION TASK")
    print("=" * 60)
    print("Instructions: For each set of 4 words, identify the word that is")
    print("semantically different from the others (the odd one out).")
    print("This task uses word embeddings (vector representations) to measure")
    print("semantic similarity, not just categories.")
    print()
    
    # Create question sets with varying difficulty
    easy_questions = generate_embedding_questions(atlas, difficulty="easy", count=3)
    medium_questions = generate_embedding_questions(atlas, difficulty="medium", count=3)
    hard_questions = generate_embedding_questions(atlas, difficulty="hard", count=3)
    
    all_questions = easy_questions + medium_questions + hard_questions
    random.shuffle(all_questions)
    
    score = 0
    total = len(all_questions)
    
    # Start the task
    print(f"Starting task with {total} questions...")
    input("Press Enter to begin.")
    print()
    
    start_time = time.time()
    
    for i, (words, correct_index, similarities, difficulty) in enumerate(all_questions):
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


def generate_embedding_questions(atlas, difficulty="medium", count=5):
    """Generate discrimination task questions using pure embedding distances.
    
    Each question has 3 semantically similar words and 1 dissimilar word,
    determined solely by embedding similarity, not categories.
    
    The difficulty level affects how dissimilar the odd word is:
    - easy: Very dissimilar (cosine similarity < 0.3)
    - medium: Moderately dissimilar (cosine similarity 0.3-0.5)
    - hard: Slightly dissimilar (cosine similarity 0.5-0.7)
    """
    questions = []
    
    # Get words with embeddings (filter out rare words and multi-word phrases)
    vocabulary = [word for word in atlas.get_all_words() 
                 if " " not in word and atlas.word_data[word].get("FREQ_GRADE", 0) > 10]
    
    # Sample a reasonable subset to work with
    core_vocab = random.sample(vocabulary, min(1000, len(vocabulary)))
    
    # For each question
    while len(questions) < count:
        # Randomly select an anchor word
        anchor_word = random.choice(core_vocab)
        anchor_embedding = atlas.get_embedding(anchor_word)
        
        if anchor_embedding is None:
            continue
            
        # Find similar words to the anchor
        similar_pairs = atlas.get_similar_words(anchor_word, n=200)
        
        # Create pools for different similarity ranges
        high_similar = [(w, s) for w, s in similar_pairs if s >= 0.7 and " " not in w]
        medium_similar = [(w, s) for w, s in similar_pairs if 0.5 <= s < 0.7 and " " not in w]
        low_similar = [(w, s) for w, s in similar_pairs if 0.3 <= s < 0.5 and " " not in w]
        very_dissimilar = [(w, s) for w, s in similar_pairs if s < 0.3 and " " not in w]
        
        # Ensure we have enough words in each similarity range
        if len(high_similar) < 3 or len(medium_similar) < 1 or len(low_similar) < 1 or len(very_dissimilar) < 1:
            continue
            
        # Depending on difficulty, select cluster words and the odd one out
        if difficulty == "easy":
            # Very clear distinction - cluster of highly similar words + very dissimilar odd word
            cluster_words = [w for w, _ in random.sample(high_similar, 3)]
            odd_word, odd_sim = random.choice(very_dissimilar)
            
            # Calculate similarities between odd word and cluster words
            similarities = [atlas.word_similarity(odd_word, w) for w in cluster_words]
            
        elif difficulty == "medium":
            # Medium distinction - cluster of similar words + low-similarity odd word  
            cluster_words = [w for w, _ in random.sample(high_similar, 3)]
            odd_word, odd_sim = random.choice(low_similar)
            
            # Calculate similarities between odd word and cluster words
            similarities = [atlas.word_similarity(odd_word, w) for w in cluster_words]
            
        else:  # hard
            # Subtle distinction - cluster of similar words + medium-similarity odd word
            cluster_words = [w for w, _ in random.sample(high_similar, 3)]
            odd_word, odd_sim = random.choice(medium_similar)
            
            # Calculate similarities between odd word and cluster words
            similarities = [atlas.word_similarity(odd_word, w) for w in cluster_words]
        
        # Combine and shuffle
        all_words = cluster_words + [odd_word]
        random.shuffle(all_words)
        
        # Record the correct answer (index of the odd word)
        correct_index = all_words.index(odd_word)
        
        # Add to questions
        questions.append((all_words, correct_index, similarities, difficulty))
    
    return questions


if __name__ == "__main__":
    main() 