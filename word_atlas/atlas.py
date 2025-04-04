"""
Word Atlas - Main interface for working with the English Word Atlas dataset.
"""

import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Any, Optional, Set, Tuple, Union

from word_atlas.data import get_data_dir, get_embeddings, get_word_index, get_word_data


class WordAtlas:
    """Main interface for the English Word Atlas dataset."""
    
    def __init__(self, data_dir: Union[str, Path, None] = None):
        """Initialize the Word Atlas with the dataset.
        
        Args:
            data_dir: Directory containing the dataset files.
                If None, uses the package's default data location.
                
        Raises:
            FileNotFoundError: If the dataset files cannot be found
        """
        self.data_dir = get_data_dir(data_dir)
        self._load_dataset()
        
    def _load_dataset(self):
        """Load the dataset and build indices for efficient lookups."""
        # Load embeddings and word data
        self.embeddings = get_embeddings(self.data_dir)
        self.word_to_idx = get_word_index(self.data_dir)
        self.word_data = get_word_data(self.data_dir)
        
        # Create reverse mapping
        self.idx_to_word = {v: k for k, v in self.word_to_idx.items()}
        
        # Build indices for faster lookup
        self._build_indices()
        
        # Statistics
        self.stats = {
            'total_entries': len(self.word_data),
            'single_words': sum(1 for w in self.word_data if ' ' not in w),
            'phrases': sum(1 for w in self.word_data if ' ' in w),
            'embedding_dim': self.embeddings.shape[1] if self.embeddings.shape[0] > 0 else 0,
        }
        
    def _build_indices(self):
        """Build indices for faster attribute-based lookups."""
        # Index for Roget categories
        self.roget_category_index = {}
        # Index for words by syllable count
        self.syllable_index = {}
        # Index for frequency ranges
        self.frequency_index = {}
        
        for word, attributes in self.word_data.items():
            # Index Roget categories
            for attr, value in attributes.items():
                if attr.startswith('ROGET_') and value:
                    if attr not in self.roget_category_index:
                        self.roget_category_index[attr] = set()
                    self.roget_category_index[attr].add(word)
            
            # Use SYLLABLE_COUNT attribute for syllable indexing
            if 'SYLLABLE_COUNT' in attributes:
                syllable_count = attributes['SYLLABLE_COUNT']
                if syllable_count not in self.syllable_index:
                    self.syllable_index[syllable_count] = set()
                self.syllable_index[syllable_count].add(word)
            # Calculate syllable count from ARPABET if SYLLABLE_COUNT not present
            elif 'ARPABET' in attributes and attributes['ARPABET']:
                # Calculate syllable count using the first pronunciation variant
                syllable_count = self._count_syllables_from_arpabet(attributes['ARPABET'][0])
                # Store the syllable count in the word data for quick reference
                attributes['SYLLABLE_COUNT'] = syllable_count
                # Index by syllable count
                if syllable_count not in self.syllable_index:
                    self.syllable_index[syllable_count] = set()
                self.syllable_index[syllable_count].add(word)
                
            # Index by frequency (logarithmic buckets)
            if 'FREQ_GRADE' in attributes:
                freq = attributes['FREQ_GRADE']
                if freq > 0:
                    bucket = int(np.log10(freq) * 2) if freq > 1 else 0
                    if bucket not in self.frequency_index:
                        self.frequency_index[bucket] = set()
                    self.frequency_index[bucket].add(word)
    
    def _count_syllables_from_arpabet(self, pronunciation: List[str]) -> int:
        """Count syllables based on ARPABET pronunciation.
        
        In ARPABET, syllables are marked by vowel phonemes, which contain stress markers (0, 1, 2).
        
        Args:
            pronunciation: List of ARPABET phonemes
            
        Returns:
            Number of syllables
        """
        # Count phonemes containing digits (stress markers) which indicate vowels/syllables
        vowel_phonemes = [p for p in pronunciation if any(c.isdigit() for c in p)]
        return len(vowel_phonemes)
    
    # ---- Basic Word Retrieval ----
    
    def get_word(self, word: str) -> Dict[str, Any]:
        """Retrieve all data for a specific word.
        
        Args:
            word: The word to look up
            
        Returns:
            Dictionary of word attributes or empty dict if not found
        """
        return self.word_data.get(word, {})
    
    def get_embedding(self, word: str) -> Optional[np.ndarray]:
        """Get the embedding vector for a word.
        
        Args:
            word: The word to get the embedding for
            
        Returns:
            Numpy array containing the embedding, or None if not found
        """
        if word not in self.word_to_idx:
            return None
        
        idx = self.word_to_idx[word]
        return self.embeddings[idx]
    
    def has_word(self, word: str) -> bool:
        """Check if a word exists in the dataset.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word exists, False otherwise
        """
        return word in self.word_data
    
    def get_all_words(self) -> List[str]:
        """Get all words in the dataset.
        
        Returns:
            List of all words and phrases
        """
        return list(self.word_data.keys())
    
    # ---- Search and Filtering ----
    
    def search(self, pattern: str) -> List[str]:
        """Search for words matching a pattern.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            List of matching words
        """
        try:
            regex = re.compile(pattern)
            return [word for word in self.word_data if regex.search(word)]
        except re.error:
            # Fall back to substring search for invalid regex
            return [word for word in self.word_data if pattern.lower() in word.lower()]
    
    def get_phrases(self) -> List[str]:
        """Get all multi-word phrases in the dataset.
        
        Returns:
            List of phrases
        """
        return [word for word in self.word_data if ' ' in word]
    
    def get_single_words(self) -> List[str]:
        """Get all single words in the dataset.
        
        Returns:
            List of single words
        """
        return [word for word in self.word_data if ' ' not in word]
    
    def filter_by_attribute(self, attribute: str, value: Any = True) -> Set[str]:
        """Filter words by a specific attribute.
        
        Args:
            attribute: Attribute name (e.g., 'ROGET_123', 'GSL')
            value: Required attribute value (default: True)
            
        Returns:
            Set of words matching the criteria
        """
        if attribute.startswith('ROGET_') and attribute in self.roget_category_index:
            return self.roget_category_index[attribute]
            
        return {word for word, attrs in self.word_data.items() 
                if attribute in attrs and attrs[attribute] == value}
    
    def filter_by_syllable_count(self, count: int) -> Set[str]:
        """Get words with a specific syllable count.
        
        Args:
            count: Number of syllables
            
        Returns:
            Set of words with that syllable count
        """
        return self.syllable_index.get(count, set())
    
    def filter_by_frequency(self, min_freq: float = 0, max_freq: Optional[float] = None) -> List[str]:
        """Filter words by frequency grade.
        
        Args:
            min_freq: Minimum frequency
            max_freq: Maximum frequency (if None, no upper limit)
            
        Returns:
            List of words within frequency range
        """
        results = []
        for word, attrs in self.word_data.items():
            if 'FREQ_GRADE' in attrs:
                freq = attrs['FREQ_GRADE']
                if freq >= min_freq and (max_freq is None or freq <= max_freq):
                    results.append(word)
        return results
    
    # ---- Similarity and Embeddings ----
    
    def word_similarity(self, word1: str, word2: str) -> float:
        """Calculate cosine similarity between two words.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score (0-1) or 0.0 if either word is not found
        """
        emb1 = self.get_embedding(word1)
        emb2 = self.get_embedding(word2)
        
        if emb1 is None or emb2 is None:
            return 0.0
            
        # Compute cosine similarity
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def get_similar_words(self, word: str, n: int = 10) -> List[Tuple[str, float]]:
        """Find words with similar embeddings.
        
        Args:
            word: Target word
            n: Number of similar words to return
            
        Returns:
            List of (word, similarity_score) tuples
        """
        if word not in self.word_to_idx:
            return []
            
        query_embedding = self.get_embedding(word)
        
        # Calculate cosine similarity with all words
        similarities = []
        for w, idx in self.word_to_idx.items():
            if w == word:
                continue
                
            embedding = self.embeddings[idx]
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            
            similarities.append((w, similarity))
        
        # Return top n most similar words
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:n]
    
    # ---- Statistics and Metadata ----
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the dataset.
        
        Returns:
            Dictionary of statistics
        """
        return self.stats
    
    def get_roget_categories(self) -> List[str]:
        """Get all available Roget's Thesaurus categories.
        
        Returns:
            List of Roget category codes
        """
        return sorted(self.roget_category_index.keys())
    
    def get_syllable_counts(self) -> List[int]:
        """Get all syllable counts in the dataset.
        
        Returns:
            List of syllable counts
        """
        return sorted(self.syllable_index.keys())
    
    def __len__(self) -> int:
        """Get the number of words in the dataset.
        
        Returns:
            Number of words
        """
        return len(self.word_data)
    
    def __contains__(self, word: str) -> bool:
        """Check if a word exists in the dataset."""
        return word in self.word_data 