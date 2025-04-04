"""Analysis functions for word lists."""

from typing import Dict, List, Set, Any, Optional, Union
from collections import defaultdict

from .types import OverlapStats, WordlistMeta


def analyze_overlap(words1: Set[str], words2: Set[str]) -> OverlapStats:
    """
    Calculate overlap statistics between two sets of words.
    
    Args:
        words1: First set of words
        words2: Second set of words
    
    Returns:
        Statistics about the overlap between the two sets
    """
    intersection = words1.intersection(words2)
    
    return {
        "words": len(intersection),
        "percent_of_first": (len(intersection) / len(words1)) * 100 if words1 else 0,
        "percent_of_second": (len(intersection) / len(words2)) * 100 if words2 else 0
    }


def analyze_word_frequency(words: List[str]) -> Dict[str, int]:
    """
    Analyze word frequency in a list of words.
    
    Args:
        words: List of words to analyze
    
    Returns:
        Dictionary mapping words to their frequency counts
    """
    frequency = defaultdict(int)
    
    for word in words:
        frequency[word] += 1
    
    return dict(frequency)


def find_common_words(wordlists: Dict[str, Set[str]], threshold: float = 0.5) -> Set[str]:
    """
    Find words that appear in at least threshold% of word lists.
    
    Args:
        wordlists: Dictionary mapping word list names to sets of words
        threshold: Minimum proportion of lists that must contain a word (0-1)
    
    Returns:
        Set of words that meet the threshold
    """
    if not wordlists:
        return set()
    
    word_counts = defaultdict(int)
    total_lists = len(wordlists)
    
    for wordlist in wordlists.values():
        for word in wordlist:
            word_counts[word] += 1
    
    return {
        word for word, count in word_counts.items()
        if count / total_lists >= threshold
    }


def compare_wordlists(list1: Set[str], list2: Set[str], name1: str = "list1", name2: str = "list2") -> Dict[str, Any]:
    """
    Compare two word lists and return detailed statistics.
    
    Args:
        list1: First set of words
        list2: Second set of words
        name1: Name of the first list (for reporting)
        name2: Name of the second list (for reporting)
    
    Returns:
        Dictionary with comparison statistics
    """
    intersection = list1.intersection(list2)
    union = list1.union(list2)
    
    only_in_first = list1.difference(list2)
    only_in_second = list2.difference(list1)
    
    return {
        "total_unique_words": len(union),
        "shared_words": {
            "count": len(intersection),
            "percent_of_total": (len(intersection) / len(union)) * 100 if union else 0,
            "percent_of_first": (len(intersection) / len(list1)) * 100 if list1 else 0,
            "percent_of_second": (len(intersection) / len(list2)) * 100 if list2 else 0,
            "examples": sorted(list(intersection))[:10]  # First 10 examples
        },
        f"only_in_{name1}": {
            "count": len(only_in_first),
            "percent_of_first": (len(only_in_first) / len(list1)) * 100 if list1 else 0,
            "examples": sorted(list(only_in_first))[:10]  # First 10 examples
        },
        f"only_in_{name2}": {
            "count": len(only_in_second),
            "percent_of_second": (len(only_in_second) / len(list2)) * 100 if list2 else 0,
            "examples": sorted(list(only_in_second))[:10]  # First 10 examples
        },
        "jaccard_similarity": len(intersection) / len(union) if union else 0
    }


def analyze_source_overlaps(sources: Dict[str, Set[str]]) -> Dict[str, Dict[str, OverlapStats]]:
    """
    Calculate all pairwise overlaps between multiple word list sources.
    
    Args:
        sources: Dictionary mapping source names to sets of words
    
    Returns:
        Nested dictionary with overlap statistics between all pairs of sources
    """
    overlaps = {}
    
    for source1 in sources:
        overlaps[source1] = {}
        for source2 in sources:
            if source1 != source2 and source2 not in overlaps.get(source1, {}):
                overlaps[source1][source2] = analyze_overlap(sources[source1], sources[source2])
    
    return overlaps


def calculate_source_distribution(sources: Dict[str, Set[str]]) -> Dict[int, Dict[str, Union[int, float]]]:
    """
    Calculate how many words appear in 1, 2, 3... sources.
    
    Args:
        sources: Dictionary mapping source names to sets of words
    
    Returns:
        Dictionary mapping counts to statistics
    """
    if not sources:
        return {}
        
    # Count how many sources each word appears in
    word_source_counts = defaultdict(int)
    all_words = set()
    
    for source_words in sources.values():
        for word in source_words:
            word_source_counts[word] += 1
            all_words.add(word)
    
    # Group by count
    count_distribution = defaultdict(list)
    for word, count in word_source_counts.items():
        count_distribution[count].append(word)
    
    # Calculate stats
    result = {}
    total_words = len(all_words)
    
    for count, words in count_distribution.items():
        result[count] = {
            "words": len(words),
            "percent": (len(words) / total_words) * 100 if total_words else 0
        }
    
    return result 