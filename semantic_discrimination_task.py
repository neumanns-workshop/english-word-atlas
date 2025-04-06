#!/usr/bin/env python3
"""
Semantic discrimination task: identify the word that doesn't belong in each set.
Each set contains 3 semantically similar words and 1 dissimilar word.
"""

import random
import time
from word_atlas import WordAtlas

def main():
    print("Initializing Word Atlas...")
    atlas = WordAtlas()
    print(f"Loaded {len(atlas)} words and phrases\n")
    
    print("=" * 60)
    print("SEMANTIC DISCRIMINATION TASK")
    print("=" * 60)
    print("Instructions: For each set of 4 words, identify the word that doesn't")
    print("belong with the others (the odd one out).")
    print()
    
    # Create question sets with varying difficulty
    easy_questions = generate_questions(atlas, difficulty="easy", count=3)
    medium_questions = generate_questions(atlas, difficulty="medium", count=3)
    hard_questions = generate_questions(atlas, difficulty="hard", count=3)
    
    all_questions = easy_questions + medium_questions + hard_questions
    random.shuffle(all_questions)
    
    score = 0
    total = len(all_questions)
    
    # Start the task
    print(f"Starting task with {total} questions...")
    input("Press Enter to begin.")
    print()
    
    start_time = time.time()
    
    for i, (words, correct_index, category, difficulty) in enumerate(all_questions):
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
        
        # Provide explanation
        similar_category = "ROGET_" + category if not category.startswith("ROGET_") else category
        print(f"The similar words belong to the {similar_category} category.")
        print()
    
    # Show results
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 60)
    print(f"Task complete! Your score: {score}/{total} ({score/total*100:.1f}%)")
    print(f"Time taken: {duration:.1f} seconds")
    print("=" * 60)


def generate_questions(atlas, difficulty="medium", count=5):
    """Generate discrimination task questions with the specified difficulty.
    
    Each question has 3 semantically similar words and 1 dissimilar word.
    The difficulty level affects how dissimilar the odd word is:
    - easy: Very dissimilar (from a completely different category)
    - medium: Moderately dissimilar (related but different category)
    - hard: Slightly dissimilar (similar but from a different subcategory)
    """
    questions = []
    
    # Get major Roget categories with enough words
    roget_categories = []
    for key in atlas.word_data[next(iter(atlas.word_data))].keys():
        if key.startswith("ROGET_"):
            # Count words in this category
            count_words = sum(1 for word in atlas.word_data 
                             if key in atlas.word_data[word] and atlas.word_data[word][key])
            if count_words >= 20:  # Ensure enough words to choose from
                roget_categories.append((key, count_words))
    
    # Sort by word count (largest first)
    roget_categories.sort(key=lambda x: -x[1])
    
    # Use top categories
    main_categories = [cat for cat, _ in roget_categories[:15]]
    
    # For each question
    while len(questions) < count:
        # Pick a category for the similar words
        category = random.choice(main_categories)
        category_name = category.replace("ROGET_", "")
        
        # Get words from this category
        category_words = list(atlas.filter_by_attribute(category))
        
        # Filter for single words (no spaces) that are common enough
        category_words = [w for w in category_words if " " not in w and 
                         atlas.word_data[w].get("FREQ_GRADE", 0) > 5]
        
        if len(category_words) < 3:
            continue  # Skip if not enough words
            
        # Select 3 random words from the category
        similar_words = random.sample(category_words, 3)
        
        # Select the dissimilar word based on difficulty
        if difficulty == "easy":
            # Pick a completely different category
            other_categories = [c for c in main_categories if c != category]
            other_category = random.choice(other_categories)
            other_words = list(atlas.filter_by_attribute(other_category))
            other_words = [w for w in other_words if " " not in w and 
                          w not in similar_words and
                          atlas.word_data[w].get("FREQ_GRADE", 0) > 5]
            
            if not other_words:
                continue
                
            dissimilar_word = random.choice(other_words)
            
        elif difficulty == "medium":
            # Find words with moderate similarity to our category words
            sample_word = random.choice(similar_words)
            similar_to_sample = atlas.get_similar_words(sample_word, n=100)
            
            # Filter for words not in our category
            candidates = []
            for word, similarity in similar_to_sample:
                if " " not in word and word not in similar_words:
                    # Check if it's in a different category
                    if category not in atlas.word_data[word] or not atlas.word_data[word][category]:
                        if 0.3 <= similarity <= 0.6:  # Medium similarity range
                            candidates.append(word)
            
            if not candidates:
                continue
                
            dissimilar_word = random.choice(candidates)
            
        else:  # hard
            # Find words with high similarity but in a different category
            sample_word = random.choice(similar_words)
            similar_to_sample = atlas.get_similar_words(sample_word, n=100)
            
            # Filter for words not in our category but highly similar
            candidates = []
            for word, similarity in similar_to_sample:
                if " " not in word and word not in similar_words:
                    # Check if it's in a different category
                    if category not in atlas.word_data[word] or not atlas.word_data[word][category]:
                        if similarity >= 0.7:  # High similarity
                            candidates.append(word)
            
            if not candidates:
                continue
                
            dissimilar_word = random.choice(candidates)
        
        # Combine and shuffle
        all_words = similar_words + [dissimilar_word]
        random.shuffle(all_words)
        
        # Record the correct answer (index of the dissimilar word)
        correct_index = all_words.index(dissimilar_word)
        
        # Add to questions
        questions.append((all_words, correct_index, category_name, difficulty))
    
    return questions


if __name__ == "__main__":
    main() 