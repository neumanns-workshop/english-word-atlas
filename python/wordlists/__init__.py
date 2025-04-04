"""Core functionalities for working with word lists."""

# Version
__version__ = '0.1.0'

# Import functions from modules
from .wordlists import get_wordlist, match_pattern, is_in_list, get_wordlist_info
from .embeddings import (
    get_word_embedding,
    find_similar_words,
    solve_analogy,
    get_embeddings,
    reset_embeddings,
    PrecomputedEmbeddings
)
from .arpabet import (
    get_pronunciation,
    get_rhymes,
    get_alliterations,
    get_syllable_count,
    get_phonetic_similarity,
    ArpabetDictionary,
    get_arpabet_dictionary,
    reset_arpabet_dictionary
)
from .frequencies import (
    get_frequency,
    get_all_metrics,
    get_percentile,
    get_frequency_band,
    get_most_frequent,
    filter_by_frequency,
    FrequencyDictionary
)

# Define aliases for better naming
get_embedding = get_word_embedding
get_similar_words = find_similar_words
get_similarity = lambda word1, word2: get_embedding(word1).dot(get_embedding(word2))

__all__ = [
    # Wordlist functions
    "get_wordlist",
    "match_pattern",
    "is_in_list",
    "get_wordlist_info",
    
    # Embedding functions
    "get_embedding",
    "get_word_embedding",
    "get_similarity",
    "get_similar_words",
    "find_similar_words",
    "solve_analogy",
    "get_embeddings",
    "reset_embeddings",
    "PrecomputedEmbeddings",
    
    # Arpabet functions
    "get_pronunciation",
    "get_rhymes",
    "get_alliterations",
    "get_syllable_count",
    "get_phonetic_similarity",
    "get_arpabet_dictionary",
    "reset_arpabet_dictionary",
    "ArpabetDictionary",
    
    # Frequency functions
    "get_frequency",
    "get_all_metrics",
    "get_percentile",
    "get_frequency_band",
    "get_most_frequent",
    "filter_by_frequency",
    "FrequencyDictionary"
] 