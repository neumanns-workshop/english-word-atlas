"""Core functionality for loading and working with word lists."""

import os
import json
import re
from typing import Dict, List, Set, Union, Optional, Any, Tuple, Pattern
from pathlib import Path

from .types import WordlistId, WordlistMeta, IsInListResult, RogetThesaurus


# Constants
DATA_DIR = Path(os.environ.get("WORDLISTS_DATA_DIR", 
                              str(Path(__file__).parent.parent.parent / "data" / "wordlists")))
HISTORICAL_DIR = DATA_DIR / "historical"
STOP_WORDS_DIR = DATA_DIR / "stop_words"


def get_wordlist(wordlist_id: Union[str, List[str]]) -> List[str]:
    """
    Retrieve a complete word list by its identifier.
    
    Args:
        wordlist_id: String identifier or list of identifiers to combine
        
    Returns:
        List of words from the specified wordlist(s)
    
    Raises:
        ValueError: If the wordlist_id is not recognized
    """
    if isinstance(wordlist_id, list):
        # Combine multiple wordlists
        result = set()
        for wl_id in wordlist_id:
            result.update(get_wordlist(wl_id))
        return sorted(result)
    
    # Single wordlist
    if wordlist_id.startswith("swadesh"):
        if wordlist_id == "swadesh-100":
            return _load_json_wordlist(HISTORICAL_DIR / "swadesh" / "swadesh_100.json")
        elif wordlist_id == "swadesh-207":
            return _load_json_wordlist(HISTORICAL_DIR / "swadesh" / "swadesh_207.json")
        else:
            raise ValueError(f"Unknown Swadesh list: {wordlist_id}")
    
    elif wordlist_id.startswith("stop-words"):
        parts = wordlist_id.split("-")
        if len(parts) < 3:
            raise ValueError(f"Invalid stop words identifier: {wordlist_id}")
        
        source = parts[2]
        if source == "nltk":
            return _load_json_wordlist(STOP_WORDS_DIR / "nltk_stop_words.json")
        elif source == "spacy":
            return _load_json_wordlist(STOP_WORDS_DIR / "spacy_stop_words.json")
        elif source == "sklearn":
            return _load_json_wordlist(STOP_WORDS_DIR / "sklearn_stop_words.json")
        elif source == "fox":
            return _load_json_wordlist(STOP_WORDS_DIR / "fox_stop_words.json")
        elif source == "comprehensive":
            return _load_json_wordlist(STOP_WORDS_DIR / "comprehensive.json")
        else:
            raise ValueError(f"Unknown stop words source: {source}")
    
    elif wordlist_id.startswith("roget"):
        if wordlist_id == "roget-complete":
            # This would load the complete Roget thesaurus structure
            return _load_roget_all_words()
        elif wordlist_id.startswith("roget-"):
            # Handle individual Roget categories
            category_id = wordlist_id[6:]  # Remove 'roget-' prefix
            return _load_roget_category(category_id)
        else:
            raise ValueError(f"Invalid Roget identifier: {wordlist_id}")
    
    elif wordlist_id == "basic-english":
        # Basic English (Ogden)
        return _load_json_wordlist(HISTORICAL_DIR / "ogden" / "basic_english.json")
    
    else:
        raise ValueError(f"Unknown wordlist identifier: {wordlist_id}")


def _load_json_wordlist(file_path: Path) -> List[str]:
    """Load a word list from a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Wordlist file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return sorted(data.get("words", []))


def _load_roget_all_words() -> List[str]:
    """Load all words from Roget's Thesaurus."""
    with open(HISTORICAL_DIR / "comprehensive.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    words = set()
    for word_data in data:
        if isinstance(word_data, dict) and "word" in word_data:
            words.add(word_data["word"])
        elif isinstance(word_data, str):
            words.add(word_data)
    
    return sorted(words)


def _load_roget_category(category_id: str) -> List[str]:
    """Load words from a specific Roget category."""
    # In a real implementation, this would load from the appropriate file
    # For simplicity, we'll load from the comprehensive file and filter
    with open(HISTORICAL_DIR / "comprehensive.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    words = set()
    for word_data in data:
        if isinstance(word_data, dict) and "categories" in word_data:
            if category_id in word_data.get("categories", []):
                words.add(word_data["word"])
    
    return sorted(words)


def match_pattern(pattern: Union[str, Pattern], wordlists: Optional[List[str]] = None) -> List[str]:
    """
    Find words matching a regex pattern across word lists.
    
    Args:
        pattern: Regular expression pattern to match
        wordlists: Optional list of wordlist identifiers to search (defaults to all)
    
    Returns:
        List of words matching the pattern
    """
    # If no specific wordlists are requested, use a comprehensive set
    if wordlists is None:
        # Load from comprehensive lists
        historical_words = _load_comprehensive_historical()
        return _filter_by_pattern(historical_words, pattern)
    
    # Load specified wordlists and filter
    all_words = set()
    for wl_id in wordlists:
        all_words.update(get_wordlist(wl_id))
    
    return _filter_by_pattern(list(all_words), pattern)


def _filter_by_pattern(words: List[str], pattern: Union[str, Pattern]) -> List[str]:
    """Filter a list of words by a regex pattern."""
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    return sorted([word for word in words if pattern.search(word)])


def _load_comprehensive_historical() -> List[str]:
    """Load the comprehensive historical word list."""
    with open(HISTORICAL_DIR / "comprehensive.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # This assumes the comprehensive file is a list of words
    # Adjust based on the actual structure
    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return sorted(data)
        else:
            # Extract words from more complex structures
            words = set()
            for item in data:
                if isinstance(item, dict) and "word" in item:
                    words.add(item["word"])
                elif isinstance(item, str):
                    words.add(item)
            return sorted(words)
    else:
        # If it's a different structure, adjust accordingly
        return []


def is_in_list(words: List[str], wordlist_id: str) -> IsInListResult:
    """
    Check if words exist in a specific word list.
    
    Args:
        words: List of words to check
        wordlist_id: Identifier of the word list to check against
    
    Returns:
        Dictionary mapping each word to True/False based on presence in the list
    """
    word_list = set(get_wordlist(wordlist_id))
    return {word: word in word_list for word in words}


def get_wordlist_info(wordlist_id: Optional[str] = None) -> Union[WordlistMeta, Dict[str, WordlistMeta]]:
    """
    Get metadata about a wordlist or all available wordlists.
    
    Args:
        wordlist_id: Optional identifier of the wordlist to get info for
    
    Returns:
        Metadata about the specified wordlist or all wordlists if none specified
    
    Raises:
        ValueError: If the wordlist_id is not recognized
    """
    # Build the metadata once
    all_metadata = _build_wordlist_metadata()
    
    if wordlist_id is None:
        return all_metadata
    
    if wordlist_id in all_metadata:
        return all_metadata[wordlist_id]
    
    raise ValueError(f"Unknown wordlist identifier: {wordlist_id}")


def _build_wordlist_metadata() -> Dict[str, WordlistMeta]:
    """Build metadata for all available wordlists."""
    metadata = {}
    
    # Historical words
    if (HISTORICAL_DIR / "index.json").exists():
        with open(HISTORICAL_DIR / "index.json", "r", encoding="utf-8") as f:
            historical_data = json.load(f)
            
        for source, info in historical_data.get("sources", {}).items():
            if source == "swadesh":
                # Add Swadesh-100
                metadata["swadesh-100"] = {
                    "id": "swadesh-100",
                    "name": "Swadesh 100 Word List",
                    "description": "A refined core vocabulary list for historical-comparative linguistics",
                    "source": "swadesh",
                    "type": "historical",
                    "count": 100,
                    "citation": info.get("citation", "")
                }
                
                # Add Swadesh-207
                metadata["swadesh-207"] = {
                    "id": "swadesh-207",
                    "name": "Swadesh 207 Word List",
                    "description": "Original core vocabulary list for historical-comparative linguistics",
                    "source": "swadesh",
                    "type": "historical",
                    "count": 207,
                    "citation": info.get("citation", "")
                }
            
            elif source == "ogden":
                metadata["basic-english"] = {
                    "id": "basic-english",
                    "name": "Ogden's Basic English",
                    "description": info.get("description", ""),
                    "source": "ogden",
                    "type": "historical",
                    "count": info.get("word_count", 0),
                    "citation": info.get("citation", "")
                }
            
            elif source == "roget":
                metadata["roget-complete"] = {
                    "id": "roget-complete",
                    "name": "Roget's Thesaurus",
                    "description": info.get("description", ""),
                    "source": "roget",
                    "type": "historical",
                    "count": info.get("word_count", 0),
                    "citation": info.get("citation", "")
                }
    
    # Stop words
    if (STOP_WORDS_DIR / "index.json").exists():
        with open(STOP_WORDS_DIR / "index.json", "r", encoding="utf-8") as f:
            stop_words_data = json.load(f)
            
        for source, info in stop_words_data.get("sources", {}).items():
            metadata[f"stop-words-{source}"] = {
                "id": f"stop-words-{source}",
                "name": f"{source.upper()} Stop Words",
                "description": info.get("description", ""),
                "source": source,
                "type": "stop_words",
                "count": info.get("word_count", 0),
                "citation": info.get("citation", "")
            }
        
        # Add comprehensive stop words
        metadata["stop-words-comprehensive"] = {
            "id": "stop-words-comprehensive",
            "name": "Comprehensive Stop Words",
            "description": "Combined stop words from all sources",
            "type": "stop_words",
            "count": stop_words_data.get("total_words", 0)
        }
    
    return metadata