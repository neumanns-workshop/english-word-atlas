"""
Module for accessing word frequency data from SUBTLEX-US corpus.

SUBTLEX-US is based on 51 million words from US film and TV subtitles.
It provides word frequencies that better predict human processing times
compared to traditional frequency counts.
"""

import os
import json
import csv
from typing import Dict, List, Optional, Union, Tuple, Callable
from pathlib import Path


# Constants
DATA_DIR = Path(os.environ.get("WORDLISTS_DATA_DIR", 
                              str(Path(__file__).parent.parent.parent / "data")))
FREQ_DIR = DATA_DIR / "frequencies"
DEFAULT_SUBTLEX_FILE = FREQ_DIR / "subtlex_us.txt"
DEFAULT_PRECOMPUTED_FILE = FREQ_DIR / "precomputed_frequencies.json"


class FrequencyDictionary:
    """
    Class for accessing word frequency data.
    
    Provides access to frequency data from the SUBTLEX-US corpus or other sources.
    Can work with either the raw frequency file or a precomputed JSON file for faster loading.
    """
    
    def __init__(self, 
                 subtlex_file: Optional[Union[str, Path]] = None, 
                 precomputed_file: Optional[Union[str, Path]] = None,
                 case_sensitive: bool = False):
        """
        Initialize the FrequencyDictionary.
        
        Args:
            subtlex_file: Path to SUBTLEX-US file (defaults to data/frequencies/subtlex_us.txt)
            precomputed_file: Path to precomputed frequencies JSON file
            case_sensitive: Whether to preserve case when looking up words
        """
        self.subtlex_file = Path(subtlex_file) if subtlex_file else DEFAULT_SUBTLEX_FILE
        self.precomputed_file = Path(precomputed_file) if precomputed_file else DEFAULT_PRECOMPUTED_FILE
        self.case_sensitive = case_sensitive
        self.frequencies = {}
        self._loaded = False
        
    def load(self) -> None:
        """Load frequency data from either precomputed file or original SUBTLEX file."""
        if self._loaded:
            return
        
        # Try precomputed file first for faster loading
        if self.precomputed_file and self.precomputed_file.exists():
            try:
                with open(self.precomputed_file, 'r', encoding='utf-8') as f:
                    self.frequencies = json.load(f)
                print(f"Loaded {len(self.frequencies)} precomputed frequencies from {self.precomputed_file}")
                self._loaded = True
                return
            except Exception as e:
                print(f"Warning: Failed to load precomputed frequencies: {e}")
        
        # Fall back to original SUBTLEX file
        if self.subtlex_file and self.subtlex_file.exists():
            try:
                self._load_subtlex_file()
                self._loaded = True
            except Exception as e:
                raise RuntimeError(f"Failed to load frequencies from SUBTLEX file: {e}")
        else:
            raise FileNotFoundError(f"SUBTLEX frequency file not found at {self.subtlex_file}")
        
    def _load_subtlex_file(self) -> None:
        """Load and parse the SUBTLEX frequency file."""
        with open(self.subtlex_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                word = row['Word']
                if not self.case_sensitive:
                    word = word.lower()
                
                # Store all relevant frequency metrics
                self.frequencies[word] = {
                    'freq_count': int(float(row['FREQcount'])),  # Raw frequency count
                    'cd_count': int(float(row['CDcount'])),      # Contextual diversity count (number of films/shows)
                    'subtl_wf': float(row['SUBTLWF']),          # Word frequency per million words
                    'lg10wf': float(row['Lg10WF']),             # Log10 of word frequency
                    'subtl_cd': float(row['SUBTLCD']),          # Contextual diversity percentage
                    'lg10cd': float(row['Lg10CD'])              # Log10 of contextual diversity
                }
        
        print(f"Loaded {len(self.frequencies)} words from SUBTLEX file {self.subtlex_file}")
        
    def get_frequency(self, word: str, metric: str = 'subtl_wf') -> float:
        """
        Get the frequency for a word.
        
        Args:
            word: Word to get frequency for
            metric: Frequency metric to return, one of:
                   'freq_count': Raw frequency count
                   'cd_count': Contextual diversity count
                   'subtl_wf': Word frequency per million (default)
                   'lg10wf': Log10 of word frequency
                   'subtl_cd': Contextual diversity percentage
                   'lg10cd': Log10 of contextual diversity
                   
        Returns:
            Frequency value or 0.0 if word not found
        """
        if not self._loaded:
            self.load()
            
        lookup_word = word if self.case_sensitive else word.lower()
        
        # Handle multi-word phrases by averaging or summing component words
        if ' ' in lookup_word:
            words = lookup_word.split()
            # Get frequencies for each word
            frequencies = [self.get_frequency(w, metric) for w in words]
            # Filter out zeros
            frequencies = [f for f in frequencies if f > 0]
            
            if not frequencies:
                return 0.0
                
            # For raw counts, sum the frequencies
            if metric in ['freq_count', 'cd_count']:
                return sum(frequencies)
            # For other metrics, take the average
            return sum(frequencies) / len(frequencies)
            
        # Handle single words
        word_data = self.frequencies.get(lookup_word, {})
        return word_data.get(metric, 0.0)
    
    def get_all_metrics(self, word: str) -> Dict[str, float]:
        """
        Get all frequency metrics for a word.
        
        Args:
            word: Word to get metrics for
            
        Returns:
            Dictionary with all frequency metrics or empty dict if not found
        """
        if not self._loaded:
            self.load()
            
        lookup_word = word if self.case_sensitive else word.lower()
        
        # Handle multi-word phrases
        if ' ' in lookup_word:
            words = lookup_word.split()
            metrics = {}
            
            # Get metrics for each word
            word_metrics = [self.get_all_metrics(w) for w in words]
            word_metrics = [m for m in word_metrics if m]  # Filter out empty dicts
            
            if not word_metrics:
                return {}
                
            # Combine metrics appropriately
            for metric in ['freq_count', 'cd_count', 'subtl_wf', 'lg10wf', 'subtl_cd', 'lg10cd']:
                values = [m.get(metric, 0.0) for m in word_metrics]
                
                # Sum raw counts, average other metrics
                if metric in ['freq_count', 'cd_count']:
                    metrics[metric] = sum(values)
                else:
                    metrics[metric] = sum(values) / len(values)
                    
            return metrics
        
        # Handle single words
        return self.frequencies.get(lookup_word, {})
    
    def get_percentile(self, word: str, metric: str = 'subtl_wf') -> float:
        """
        Get the frequency percentile of a word (0-100).
        
        Args:
            word: Word to get percentile for
            metric: Frequency metric to use
            
        Returns:
            Percentile (0-100) or 0.0 if word not found
        """
        if not self._loaded:
            self.load()
            
        freq = self.get_frequency(word, metric)
        if freq == 0.0:
            return 0.0
            
        # Get all values for this metric
        all_values = sorted([data.get(metric, 0.0) for data in self.frequencies.values()])
        if not all_values:
            return 0.0
            
        # Find position of this frequency in sorted list
        position = next((i for i, v in enumerate(all_values) if v >= freq), len(all_values))
        
        # Calculate percentile
        return (position / len(all_values)) * 100
    
    def get_frequency_band(self, word: str, num_bands: int = 5, metric: str = 'subtl_wf') -> int:
        """
        Get the frequency band of a word (1 = highest frequency, num_bands = lowest).
        
        Args:
            word: Word to get band for
            num_bands: Number of bands to divide frequencies into
            metric: Frequency metric to use
            
        Returns:
            Band number (1 to num_bands) or 0 if word not found
        """
        percentile = self.get_percentile(word, metric)
        if percentile == 0.0:
            return 0
            
        # Convert percentile to band (reverse order: higher percentile = lower band number)
        band = num_bands - int((percentile / 100) * num_bands)
        # Ensure band is between 1 and num_bands
        return max(1, min(band, num_bands))
    
    def get_most_frequent(self, n: int = 10, metric: str = 'subtl_wf') -> List[Tuple[str, float]]:
        """
        Get the n most frequent words.
        
        Args:
            n: Number of words to return
            metric: Frequency metric to use
            
        Returns:
            List of (word, frequency) tuples, sorted by descending frequency
        """
        if not self._loaded:
            self.load()
            
        # Sort by the specified metric
        sorted_words = sorted(
            [(word, data.get(metric, 0.0)) for word, data in self.frequencies.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_words[:n]
    
    def get_least_frequent(self, n: int = 10, metric: str = 'subtl_wf') -> List[Tuple[str, float]]:
        """
        Get the n least frequent words that have non-zero frequency.
        
        Args:
            n: Number of words to return
            metric: Frequency metric to use
            
        Returns:
            List of (word, frequency) tuples, sorted by ascending frequency
        """
        if not self._loaded:
            self.load()
            
        # Get words with non-zero frequency for the metric
        non_zero_words = [
            (word, data.get(metric, 0.0)) 
            for word, data in self.frequencies.items()
            if data.get(metric, 0.0) > 0
        ]
        
        # Sort by the specified metric
        sorted_words = sorted(non_zero_words, key=lambda x: x[1])
        
        return sorted_words[:n]
    
    def filter_by_frequency(self, words: List[str], 
                          min_freq: float = 0.0, 
                          max_freq: Optional[float] = None,
                          metric: str = 'subtl_wf') -> List[str]:
        """
        Filter a list of words by frequency.
        
        Args:
            words: List of words to filter
            min_freq: Minimum frequency (inclusive)
            max_freq: Maximum frequency (inclusive) or None for no upper limit
            metric: Frequency metric to use
            
        Returns:
            Filtered list of words
        """
        if not self._loaded:
            self.load()
            
        result = []
        for word in words:
            freq = self.get_frequency(word, metric)
            
            if freq >= min_freq and (max_freq is None or freq <= max_freq):
                result.append(word)
                
        return result
    
    def find_words(self, predicate: Callable[[str, Dict[str, float]], bool], limit: Optional[int] = None) -> List[str]:
        """
        Find words that satisfy a predicate function.
        
        Args:
            predicate: Function taking (word, metrics_dict) and returning True/False
            limit: Maximum number of words to return or None for all
            
        Returns:
            List of words that satisfy the predicate
        """
        if not self._loaded:
            self.load()
            
        result = []
        for word, metrics in self.frequencies.items():
            if predicate(word, metrics):
                result.append(word)
                if limit is not None and len(result) >= limit:
                    break
                    
        return result
    
    def __contains__(self, word: str) -> bool:
        """Check if a word exists in the frequency dictionary."""
        if not self._loaded:
            self.load()
            
        lookup_word = word if self.case_sensitive else word.lower()
        
        # Handle multi-word phrases
        if ' ' in lookup_word:
            words = lookup_word.split()
            return all(w in self for w in words)
            
        return lookup_word in self.frequencies
        
    def __len__(self) -> int:
        """Get the number of words in the frequency dictionary."""
        if not self._loaded:
            self.load()
            
        return len(self.frequencies)


# Module-level frequency dictionary
_frequency_dict = None

def get_frequency_dictionary(subtlex_file: Optional[Union[str, Path]] = None,
                           precomputed_file: Optional[Union[str, Path]] = None,
                           case_sensitive: bool = False) -> FrequencyDictionary:
    """
    Get a shared FrequencyDictionary instance.
    
    Args:
        subtlex_file: Path to SUBTLEX file
        precomputed_file: Path to precomputed frequencies file
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        FrequencyDictionary instance
    """
    global _frequency_dict
    
    if _frequency_dict is None:
        _frequency_dict = FrequencyDictionary(
            subtlex_file=subtlex_file,
            precomputed_file=precomputed_file,
            case_sensitive=case_sensitive
        )
    
    return _frequency_dict

# Convenience functions
def get_frequency(word: str, metric: str = 'subtl_wf', case_sensitive: bool = False) -> float:
    """
    Get the frequency for a word.
    
    Args:
        word: Word to get frequency for
        metric: Frequency metric to return
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        Frequency value or 0.0 if word not found
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.get_frequency(word, metric)

def get_all_metrics(word: str, case_sensitive: bool = False) -> Dict[str, float]:
    """
    Get all frequency metrics for a word.
    
    Args:
        word: Word to get metrics for
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        Dictionary with all frequency metrics or empty dict if not found
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.get_all_metrics(word)

def get_percentile(word: str, metric: str = 'subtl_wf', case_sensitive: bool = False) -> float:
    """
    Get the frequency percentile of a word (0-100).
    
    Args:
        word: Word to get percentile for
        metric: Frequency metric to use
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        Percentile (0-100) or 0.0 if word not found
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.get_percentile(word, metric)

def get_frequency_band(word: str, num_bands: int = 5, metric: str = 'subtl_wf', 
                     case_sensitive: bool = False) -> int:
    """
    Get the frequency band of a word (1 = highest frequency, num_bands = lowest).
    
    Args:
        word: Word to get band for
        num_bands: Number of bands to divide frequencies into
        metric: Frequency metric to use
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        Band number (1 to num_bands) or 0 if word not found
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.get_frequency_band(word, num_bands, metric)

def get_most_frequent(n: int = 10, metric: str = 'subtl_wf', case_sensitive: bool = False) -> List[Tuple[str, float]]:
    """
    Get the n most frequent words.
    
    Args:
        n: Number of words to return
        metric: Frequency metric to use
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        List of (word, frequency) tuples, sorted by descending frequency
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.get_most_frequent(n, metric)

def filter_by_frequency(words: List[str], min_freq: float = 0.0, max_freq: Optional[float] = None,
                      metric: str = 'subtl_wf', case_sensitive: bool = False) -> List[str]:
    """
    Filter a list of words by frequency.
    
    Args:
        words: List of words to filter
        min_freq: Minimum frequency (inclusive)
        max_freq: Maximum frequency (inclusive) or None for no upper limit
        metric: Frequency metric to use
        case_sensitive: Whether to preserve case when looking up words
        
    Returns:
        Filtered list of words
    """
    dict_instance = get_frequency_dictionary(case_sensitive=case_sensitive)
    return dict_instance.filter_by_frequency(words, min_freq, max_freq, metric) 