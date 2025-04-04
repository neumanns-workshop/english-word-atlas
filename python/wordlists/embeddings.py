"""Functionality for working with word embeddings."""

import os
import numpy as np
from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path

# Constants
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
DEFAULT_EMBEDDINGS_FILE = EMBEDDINGS_DIR / "precomputed_embeddings.npz"

class PrecomputedEmbeddings:
    """Class for working with precomputed word embeddings."""
    
    def __init__(self, embeddings_file: Optional[Union[str, Path]] = None):
        """
        Initialize the precomputed embeddings.
        
        Args:
            embeddings_file: Path to the precomputed embeddings file (npz format).
                If None, uses the default embeddings file.
        """
        if embeddings_file is None:
            embeddings_file = DEFAULT_EMBEDDINGS_FILE
        
        if not os.path.exists(embeddings_file):
            raise FileNotFoundError(
                f"Embeddings file not found: {embeddings_file}. "
                f"Please run the precompute_embeddings.py script first."
            )
        
        try:
            data = np.load(embeddings_file, allow_pickle=True)
            self.embeddings = data['embeddings']
            self.words = data['words'].tolist()
            self.word_to_idx = {word: i for i, word in enumerate(self.words)}
            self.embedding_dim = self.embeddings.shape[1]
        except Exception as e:
            raise ValueError(f"Failed to load embeddings: {e}")
        
        print(f"Loaded {len(self.words)} precomputed embeddings with dimension {self.embedding_dim}")
    
    def get_embedding(self, word: str) -> Optional[np.ndarray]:
        """
        Get the embedding vector for a word.
        
        Args:
            word: The word to get the embedding for.
            
        Returns:
            The embedding vector or None if the word is not in the vocabulary.
        """
        word = word.lower()
        if word in self.word_to_idx:
            return self.embeddings[self.word_to_idx[word]]
        return None
    
    def find_similar_words(self, word: str, n: int = 10) -> List[Tuple[str, float]]:
        """
        Find the most similar words to the given word.
        
        Args:
            word: The query word.
            n: The number of similar words to return.
            
        Returns:
            A list of (word, similarity) tuples, sorted by similarity in descending order.
        """
        embedding = self.get_embedding(word)
        if embedding is None:
            return []
        
        # Compute cosine similarity between the word and all other words
        similarities = np.dot(self.embeddings, embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(embedding)
        )
        
        # Get the indices of the most similar words
        most_similar_indices = np.argsort(similarities)[::-1][1:n+1]  # Skip the first one (the word itself)
        
        # Return the most similar words and their similarities
        return [(self.words[i], similarities[i]) for i in most_similar_indices]
    
    def solve_analogy(self, word1: str, word2: str, word3: str, n: int = 5) -> List[Tuple[str, float]]:
        """
        Solve an analogy task of the form: word1 is to word2 as word3 is to ?
        
        Args:
            word1: First word in the analogy.
            word2: Second word in the analogy.
            word3: Third word in the analogy.
            n: Number of results to return.
            
        Returns:
            A list of (word, similarity) tuples, sorted by similarity in descending order.
        """
        # Get embeddings for the words
        e1 = self.get_embedding(word1)
        e2 = self.get_embedding(word2)
        e3 = self.get_embedding(word3)
        
        if e1 is None or e2 is None or e3 is None:
            missing = []
            if e1 is None: missing.append(word1)
            if e2 is None: missing.append(word2)
            if e3 is None: missing.append(word3)
            print(f"Missing embeddings for: {', '.join(missing)}")
            return []
        
        # Compute the target vector: e2 - e1 + e3
        target = e2 - e1 + e3
        target_norm = np.linalg.norm(target)
        
        # Compute cosine similarity between the target and all word vectors
        similarities = np.dot(self.embeddings, target) / (
            np.linalg.norm(self.embeddings, axis=1) * target_norm
        )
        
        # Get the indices of the most similar words
        most_similar_indices = np.argsort(similarities)[::-1]
        
        # Filter out the input words
        result = []
        i = 0
        while len(result) < n and i < len(most_similar_indices):
            idx = most_similar_indices[i]
            word = self.words[idx]
            if word.lower() not in [word1.lower(), word2.lower(), word3.lower()]:
                result.append((word, similarities[idx]))
            i += 1
        
        return result
    
    def get_vocabulary_coverage(self, words: List[str]) -> Tuple[float, Set[str], Set[str]]:
        """
        Calculate the coverage of the given words in the embeddings vocabulary.
        
        Args:
            words: A list of words to check coverage for.
            
        Returns:
            A tuple of (coverage ratio, words with embeddings, words without embeddings)
        """
        words_lower = [word.lower() for word in words]
        words_with_embeddings = set(word for word in words_lower if word in self.word_to_idx)
        words_without_embeddings = set(words_lower) - words_with_embeddings
        
        coverage = len(words_with_embeddings) / len(words) if words else 0
        return coverage, words_with_embeddings, words_without_embeddings
    
    def __contains__(self, word: str) -> bool:
        """Check if a word is in the vocabulary."""
        return word.lower() in self.word_to_idx
    
    def __len__(self) -> int:
        """Return the size of the vocabulary."""
        return len(self.words)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Cosine similarity (between -1 and 1)
    """
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
        
    return np.dot(v1, v2) / (norm1 * norm2)


# Global instances
_precomputed_embeddings = None

def get_embeddings(embeddings_file: Optional[Union[str, Path]] = None) -> PrecomputedEmbeddings:
    """
    Get the global embeddings instance. Loads embeddings if not already loaded.
    
    Args:
        embeddings_file: Path to the precomputed embeddings file (npz format)
        
    Returns:
        Embeddings instance
    """
    global _precomputed_embeddings
    
    if _precomputed_embeddings is None:
        _precomputed_embeddings = PrecomputedEmbeddings(embeddings_file)
    
    return _precomputed_embeddings


def reset_embeddings() -> None:
    """Reset the global embeddings instance."""
    global _precomputed_embeddings
    _precomputed_embeddings = None


def get_word_embedding(word: str, embeddings_file: Optional[Union[str, Path]] = None) -> Optional[np.ndarray]:
    """
    Get the embedding for a word.
    
    Args:
        word: The word to get embedding for
        embeddings_file: Optional embedding file path
        
    Returns:
        Embedding vector or None if not found
    """
    embeddings = get_embeddings(embeddings_file)
    return embeddings.get_embedding(word)


def find_similar_words(word: str, n: int = 10, embeddings_file: Optional[Union[str, Path]] = None) -> List[Tuple[str, float]]:
    """
    Find words similar to a given word.
    
    Args:
        word: The query word
        n: Number of similar words to return
        embeddings_file: Optional embedding file path
        
    Returns:
        List of (word, similarity) tuples
    """
    embeddings = get_embeddings(embeddings_file)
    return embeddings.find_similar_words(word, n)


def solve_analogy(word1: str, word2: str, word3: str, n: int = 5, 
                 embeddings_file: Optional[Union[str, Path]] = None) -> List[Tuple[str, float]]:
    """
    Solve analogy task: word1 is to word2 as word3 is to ?
    
    Args:
        word1: First word in the analogy
        word2: Second word in the analogy
        word3: Third word in the analogy
        n: Number of results to return
        embeddings_file: Optional embedding file path
        
    Returns:
        List of (word, score) tuples
    """
    embeddings = get_embeddings(embeddings_file)
    return embeddings.solve_analogy(word1, word2, word3, n) 