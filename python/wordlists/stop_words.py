"""Functionality for working with stop word lists."""

from typing import Dict, List, Optional, Set, Union

from .types import StopWordsOptions, WordlistId
from .wordlists import get_wordlist


def create_stop_word_list(options: StopWordsOptions) -> List[str]:
    """
    Create a custom stop word list by combining or modifying existing lists.
    
    Args:
        options: Configuration options for creating the stop word list
            - base: Base stop word list to start with (optional)
            - include: Words or wordlists to include (optional)
            - exclude: Words to exclude (optional)
    
    Returns:
        Customized stop word list
    
    Examples:
        >>> # Start with NLTK's stop words and add custom words
        >>> custom_stop_words = create_stop_word_list({
        ...     'base': 'stop-words-nltk',
        ...     'include': ['custom', 'words'],
        ...     'exclude': ['not', 'no', 'nor']
        ... })
    """
    result: Set[str] = set()
    
    # Start with base list if provided
    if 'base' in options and options['base']:
        base_id = options['base']
        result.update(get_wordlist(base_id))
    
    # Add included words or wordlists
    if 'include' in options and options['include']:
        for item in options['include']:
            if isinstance(item, str) and item.startswith('stop-words-'):
                # It's a wordlist ID
                result.update(get_wordlist(item))
            else:
                # It's an individual word
                result.add(item)
    
    # Remove excluded words
    if 'exclude' in options and options['exclude']:
        result.difference_update(options['exclude'])
    
    return sorted(result)


def get_common_stop_words(threshold: float = 0.5) -> List[str]:
    """
    Get stop words that appear in at least threshold% of all stop word lists.
    
    Args:
        threshold: Minimum proportion of lists that must contain a word (0-1)
    
    Returns:
        List of common stop words that meet the threshold
    """
    # Get all stop word sources
    sources = [
        "stop-words-nltk",
        "stop-words-spacy", 
        "stop-words-sklearn",
        "stop-words-fox"
    ]
    
    # Count occurrences of each word
    word_counts: Dict[str, int] = {}
    for source in sources:
        words = set(get_wordlist(source))
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Filter by threshold
    total_sources = len(sources)
    common_words = [
        word for word, count in word_counts.items()
        if count / total_sources >= threshold
    ]
    
    return sorted(common_words)


def get_minimal_stop_words() -> List[str]:
    """
    Get a minimal set of the most common English stop words.
    
    Returns:
        List of the most common stop words (appears in all major lists)
    """
    return get_common_stop_words(threshold=0.75) 