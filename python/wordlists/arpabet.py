"""Functionality for working with word pronunciations in Arpabet format."""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Constants
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
DICT_DIR = DATA_DIR / "dictionaries"
DEFAULT_DICT_FILE = DICT_DIR / "cmudict-0.7b"
PRECOMPUTED_FILE = DICT_DIR / "precomputed_pronunciations.json"

class ArpabetDictionary:
    """Class for working with Arpabet pronunciation dictionaries."""
    
    def __init__(self, dict_file: Optional[Union[str, Path]] = None, use_precomputed: bool = True):
        """
        Initialize the Arpabet dictionary.
        
        Args:
            dict_file: Path to the dictionary file. If None, uses the default CMU dictionary.
            use_precomputed: Whether to use precomputed pronunciations if available.
        """
        if dict_file is None:
            dict_file = DEFAULT_DICT_FILE
        
        self.dict_file = dict_file
        self.pronunciations: Dict[str, List[List[str]]] = {}
        self._loaded = False
        self._use_precomputed = use_precomputed
    
    def load(self) -> bool:
        """
        Load the dictionary from file.
        
        Returns:
            True if loading succeeded, False otherwise
        """
        if self._loaded:
            return True
        
        # Try to load precomputed pronunciations first if enabled
        if self._use_precomputed and PRECOMPUTED_FILE.exists():
            try:
                with open(PRECOMPUTED_FILE, 'r', encoding='utf-8') as f:
                    self.pronunciations = json.load(f)
                
                self._loaded = True
                print(f"Loaded {len(self.pronunciations)} precomputed pronunciations from {PRECOMPUTED_FILE}")
                return True
            except Exception as e:
                print(f"Error loading precomputed pronunciations: {e}")
                print("Falling back to CMU dictionary...")
        
        # Fall back to CMU dictionary
        if not os.path.exists(self.dict_file):
            print(f"Dictionary file not found: {self.dict_file}")
            return False
        
        try:
            # Try different encodings to handle potential encoding issues
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(self.dict_file, 'r', encoding=encoding) as f:
                        for line in f:
                            # Skip comments and empty lines
                            if line.startswith(';;;') or not line.strip():
                                continue
                            
                            # Parse the line
                            parts = line.strip().split('  ')
                            if len(parts) < 2:
                                continue
                            
                            word = parts[0].lower()
                            
                            # Remove alternate pronunciation numbers (e.g., TOMATO(1))
                            word = re.sub(r'\(\d+\)$', '', word)
                            
                            # Get the pronunciation
                            pron = parts[1].split()
                            
                            # Store the pronunciation (handle multiple pronunciations for same word)
                            if word not in self.pronunciations:
                                self.pronunciations[word] = []
                            self.pronunciations[word].append(pron)
                    
                    # If we got here, the encoding worked
                    self._loaded = True
                    print(f"Loaded {len(self.pronunciations)} words from {self.dict_file} using {encoding} encoding")
                    return True
                    
                except UnicodeDecodeError:
                    # Try the next encoding
                    continue
            
            # If we get here, none of the encodings worked
            print(f"Could not read the dictionary file with any supported encoding")
            return False
            
        except Exception as e:
            print(f"Error loading Arpabet dictionary: {e}")
            return False
    
    def get_pronunciation(self, word: str, remove_stress: bool = False) -> List[List[str]]:
        """
        Get the pronunciation(s) for a word or phrase.
        
        Args:
            word: The word or phrase to get pronunciations for
            remove_stress: Whether to remove stress markers from phonemes
            
        Returns:
            A list of pronunciations, where each pronunciation is a list of phonemes
        """
        if not self._loaded:
            self.load()
        
        # Check if this is a multi-word phrase
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            # Split into individual words
            words = word.split()
            
            # Get pronunciation for each word
            word_pronunciations = []
            for w in words:
                prons = self.get_pronunciation(w, remove_stress=False)
                if not prons:
                    # If any word has no pronunciation, return empty list
                    # Alternative: could return partial pronunciation
                    return []
                word_pronunciations.append(prons)
            
            # Combine all possible pronunciation combinations
            combined_pronunciations = [[]]
            for word_prons in word_pronunciations:
                new_combined = []
                for existing in combined_pronunciations:
                    for pron in word_prons:
                        new_combined.append(existing + pron)
                combined_pronunciations = new_combined
            
            if remove_stress:
                # Remove stress markers
                return [[re.sub(r'\d+', '', phoneme) for phoneme in pron] for pron in combined_pronunciations]
            
            return combined_pronunciations
        
        # Single word case (or quoted phrase that should be treated as a single entity)
        # Try with the original word first
        pronunciations = self.pronunciations.get(word, [])
        
        # If not found, try lowercase
        if not pronunciations:
            pronunciations = self.pronunciations.get(word.lower(), [])
        
        # If still not found, try with title case (for proper nouns)
        if not pronunciations:
            pronunciations = self.pronunciations.get(word.title(), [])
        
        # If still not found, try cleaning the word (removing non-alphabetic characters)
        if not pronunciations:
            clean_word = re.sub(r'[^a-zA-Z\']', '', word.lower())
            if clean_word:
                pronunciations = self.pronunciations.get(clean_word, [])
        
        if remove_stress and pronunciations:
            # Remove stress markers (digits) from phonemes
            return [[re.sub(r'\d+', '', phoneme) for phoneme in pron] for pron in pronunciations]
        
        return pronunciations
    
    def get_rhymes(self, word: str, syllables: Optional[int] = None, 
                   strength: str = "normal") -> List[str]:
        """
        Find words that rhyme with the given word or phrase.
        
        For multi-word phrases, the rhyming is based on the last word of the phrase.
        
        Args:
            word: The word or phrase to find rhymes for
            syllables: Optional number of syllables to filter rhymes (None for any)
            strength: Rhyming strength: "perfect" (exact match from last stressed vowel), 
                     "normal" (match vowel sound and final consonants),
                     "weak" (match only final vowel sound)
            
        Returns:
            List of words that rhyme with the given word
        """
        if not self._loaded:
            self.load()
        
        # Handle multi-word phrases by focusing on the last word
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            # Get the last word from the phrase
            last_word = word.split()[-1]
            
            # Get rhymes for the last word
            rhymes = self.get_rhymes(last_word, syllables, strength)
            
            # Filter out the original phrase if it's in the results
            return [r for r in rhymes if r != word]
        
        # Get all variants of the word's pronunciation
        pronunciations = self.get_pronunciation(word)
        if not pronunciations:
            # Try with lowercase if original fails
            if word.lower() != word:
                pronunciations = self.get_pronunciation(word.lower())
            
            # Still no pronunciations
            if not pronunciations:
                return []
        
        # Get the first pronunciation variant
        pron = pronunciations[0]
        
        # Determine which phonemes to match based on rhyming strength
        rhyme_part = self._get_rhyme_part(pron, strength)
        if not rhyme_part:
            return []
            
        # Find all words with matching rhyme pattern
        rhymes = []
        for candidate, candidate_prons in self.pronunciations.items():
            # Skip exact match
            if candidate.lower() == word.lower():
                continue
                
            # Skip if syllable count doesn't match requested count
            if syllables:
                candidate_syllables = self.get_syllable_count(candidate)
                if candidate_syllables != syllables:
                    continue
            
            # Check each pronunciation variant of the candidate
            for candidate_pron in candidate_prons:
                candidate_rhyme_part = self._get_rhyme_part(candidate_pron, strength)
                if not candidate_rhyme_part:
                    continue
                    
                # Check if rhyme parts match
                if candidate_rhyme_part == rhyme_part:
                    rhymes.append(candidate)
                    break
        
        return sorted(rhymes)
    
    def _get_rhyme_part(self, pronunciation: List[str], strength: str = "normal") -> List[str]:
        """
        Extract the part of a pronunciation that should match for rhyming.
        
        Args:
            pronunciation: Phonetic pronunciation as a list of phonemes
            strength: Rhyming strength (perfect, normal, weak)
            
        Returns:
            List of phonemes that should match for a rhyme
        """
        # Find the last stressed vowel position
        last_stressed_pos = -1
        for i, phoneme in enumerate(pronunciation):
            if any(phoneme.startswith(v) and phoneme.endswith('1') 
                   for v in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                last_stressed_pos = i
        
        # If no stressed vowel, try to find any vowel
        if last_stressed_pos == -1:
            for i, phoneme in enumerate(pronunciation):
                if any(phoneme.startswith(v) 
                       for v in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                    last_stressed_pos = i
        
        # Still no vowel found
        if last_stressed_pos == -1:
            return []
        
        if strength == "perfect":
            # Perfect rhyme: everything from last stressed vowel to end
            return pronunciation[last_stressed_pos:]
        elif strength == "normal":
            # Normal rhyme: match the vowel and final consonants
            return pronunciation[last_stressed_pos:]
        elif strength == "weak":
            # Weak rhyme: just match the final vowel sound
            vowel = pronunciation[last_stressed_pos]
            vowel_no_stress = re.sub(r'\d+', '', vowel)
            return [vowel_no_stress]
        else:
            # Default to normal rhyme
            return pronunciation[last_stressed_pos:]
    
    def _levenshtein_distance(self, seq1: List[str], seq2: List[str]) -> int:
        """
        Calculate the Levenshtein (edit) distance between two sequences.
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            The edit distance between the sequences
        """
        m, n = len(seq1), len(seq2)
        
        # Initialize the distance matrix
        dist = [[0 for _ in range(n+1)] for _ in range(m+1)]
        
        # Initialize first row and column
        for i in range(m+1):
            dist[i][0] = i
        for j in range(n+1):
            dist[0][j] = j
        
        # Fill the matrix
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost = 0 if seq1[i-1] == seq2[j-1] else 1
                dist[i][j] = min(
                    dist[i-1][j] + 1,      # deletion
                    dist[i][j-1] + 1,      # insertion
                    dist[i-1][j-1] + cost  # substitution
                )
        
        return dist[m][n]
    
    def get_alliterations(self, word: str) -> List[str]:
        """
        Find words that alliterate with the given word or phrase.
        For phrases, focuses on the first word as the alliterating element.
        
        Args:
            word: The word or phrase to find alliterations for
            
        Returns:
            A list of words that alliterate with the given word or phrase
        """
        if not self._loaded:
            self.load()
        
        # For multi-word phrases, focus on the first word for alliteration
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            words = word.split()
            first_word = words[0]
            return self.get_alliterations(first_word)
        
        # Single word case
        pronunciations = self.get_pronunciation(word)
        if not pronunciations:
            return []
        
        # Use the first pronunciation as the reference
        pron = pronunciations[0]
        
        # Get the initial consonant cluster
        initial_cluster = []
        for phoneme in pron:
            # Check if it's a consonant
            if not any(phoneme.startswith(p) for p in 
                      ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                initial_cluster.append(phoneme)
            else:
                # Stop at the first vowel
                break
        
        if not initial_cluster:
            return []
        
        # Find words with matching initial cluster
        alliterations = []
        for w, prons in self.pronunciations.items():
            if w == word.lower():
                continue
            
            for p in prons:
                if len(p) >= len(initial_cluster) and p[:len(initial_cluster)] == initial_cluster:
                    alliterations.append(w)
                    break
        
        return alliterations
    
    def get_syllable_count(self, word: str) -> int:
        """
        Count the number of syllables in a word or phrase.
        
        Args:
            word: The word or phrase to count syllables for
            
        Returns:
            The number of syllables in the word or phrase
        """
        if not self._loaded:
            self.load()
        
        # Handle multi-word phrases
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            # First try to get pronunciation for the entire phrase
            pronunciations = self.get_pronunciation(word)
            if pronunciations:
                # Use the first pronunciation as the reference
                pron = pronunciations[0]
                
                # Count vowel phonemes
                syllables = 0
                for phoneme in pron:
                    if any(phoneme.startswith(p) for p in 
                        ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                        syllables += 1
                
                return syllables
            
            # If we don't have a pronunciation for the entire phrase,
            # split into individual words and sum their syllable counts
            words = word.split()
            return sum(self.get_syllable_count(w) for w in words)
        
        # Single word case
        pronunciations = self.get_pronunciation(word)
        if not pronunciations:
            # Try alternate cases if no pronunciation found
            if word.lower() != word:
                pronunciations = self.get_pronunciation(word.lower())
            if not pronunciations and word.title() != word:
                pronunciations = self.get_pronunciation(word.title())
            if not pronunciations:
                # Last resort: estimate syllables using a simple heuristic
                # Count vowel groups as a fallback when no pronunciation exists
                clean_word = re.sub(r'[^a-zA-Z]', '', word.lower())
                vowels = 'aeiouy'
                count = 0
                prev_is_vowel = False
                
                for char in clean_word:
                    is_vowel = char in vowels
                    if is_vowel and not prev_is_vowel:
                        count += 1
                    prev_is_vowel = is_vowel
                    
                # Handle silent e at end of word
                if clean_word and clean_word[-1] == 'e' and count > 1:
                    count -= 1
                    
                return max(1, count)  # Ensure at least one syllable
        
        if not pronunciations:
            return 0
        
        # Use the first pronunciation as the reference
        pron = pronunciations[0]
        
        # Count the number of vowel phonemes
        syllables = 0
        for phoneme in pron:
            # Check if it's a vowel
            if any(phoneme.startswith(p) for p in 
                 ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                syllables += 1
        
        return syllables
    
    def get_phonetic_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate the phonetic similarity between two words or phrases.
        
        For multi-word phrases, compares corresponding words and returns a weighted average.
        
        Args:
            word1: First word or phrase
            word2: Second word or phrase
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not self._loaded:
            self.load()
        
        # Split if phrases
        word1_parts = word1.split() if ' ' in word1 else [word1]
        word2_parts = word2.split() if ' ' in word2 else [word2]
        
        # Handle multi-word phrases
        if len(word1_parts) > 1 or len(word2_parts) > 1:
            # Different approaches based on length differences
            if len(word1_parts) == len(word2_parts):
                # Same number of words - compare corresponding words
                similarities = []
                total_weight = 0
                
                for i, (w1, w2) in enumerate(zip(word1_parts, word2_parts)):
                    # Give more weight to content words (longer words)
                    weight = max(len(w1), len(w2)) / 2
                    total_weight += weight
                    
                    # Calculate similarity for this word pair
                    sim = self.get_phonetic_similarity(w1, w2)
                    similarities.append((sim, weight))
                
                # Calculate weighted average
                if total_weight > 0:
                    return sum(sim * weight for sim, weight in similarities) / total_weight
                return 0.0
            
            else:
                # Different number of words - find best matches
                min_len = min(len(word1_parts), len(word2_parts))
                max_len = max(len(word1_parts), len(word2_parts))
                
                # Compare corresponding words up to min_len
                similarities = []
                for i in range(min_len):
                    sim = self.get_phonetic_similarity(word1_parts[i], word2_parts[i])
                    similarities.append(sim)
                
                # Penalize for length difference
                length_penalty = min_len / max_len
                
                # Return average similarity adjusted for length difference
                if similarities:
                    return sum(similarities) / len(similarities) * length_penalty
                return 0.0
        
        # Single-word comparison
        pron1 = self.get_pronunciation(word1)
        pron2 = self.get_pronunciation(word2)
        
        if not pron1 or not pron2:
            # Try alternate cases
            if word1.lower() != word1:
                pron1 = self.get_pronunciation(word1.lower()) or pron1
            if word2.lower() != word2:
                pron2 = self.get_pronunciation(word2.lower()) or pron2
            
            # Still no pronunciations
            if not pron1 or not pron2:
                return 0.0
        
        # Use the first pronunciation for each word
        pron1 = pron1[0]
        pron2 = pron2[0]
        
        # Remove stress markers for better comparison
        pron1 = [re.sub(r'\d+', '', p) for p in pron1]
        pron2 = [re.sub(r'\d+', '', p) for p in pron2]
        
        # Compute Levenshtein distance
        max_len = max(len(pron1), len(pron2))
        if max_len == 0:
            return 1.0  # Both empty
            
        distance = self._levenshtein_distance(pron1, pron2)
        similarity = 1.0 - distance / max_len
        
        return max(0.0, similarity)  # Ensure non-negative
    
    def __contains__(self, word: str) -> bool:
        """Check if a word or phrase is in the dictionary."""
        if not self._loaded:
            self.load()
        
        # Handle multi-word phrases
        if ' ' in word and not word.startswith('"') and not word.startswith("'"):
            # Split into individual words and check if all are in the dictionary
            words = word.split()
            return all(w in self for w in words)
        
        # Single word case
        # Try with original word first
        if word in self.pronunciations:
            return True
        
        # Try lowercase
        if word.lower() in self.pronunciations:
            return True
        
        # Try title case
        if word.title() in self.pronunciations:
            return True
        
        # Try cleaned word
        clean_word = re.sub(r'[^a-zA-Z\']', '', word.lower())
        if clean_word and clean_word in self.pronunciations:
            return True
        
        return False
    
    def __len__(self) -> int:
        """Return the size of the dictionary."""
        if not self._loaded:
            self.load()
        return len(self.pronunciations)


# Global instance
_arpabet_dictionary = None

def get_arpabet_dictionary(dict_file: Optional[Union[str, Path]] = None, use_precomputed: bool = True) -> ArpabetDictionary:
    """
    Get the global Arpabet dictionary instance. Loads the dictionary if not already loaded.
    
    Args:
        dict_file: Path to the dictionary file
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        ArpabetDictionary instance
    """
    global _arpabet_dictionary
    
    if _arpabet_dictionary is None:
        _arpabet_dictionary = ArpabetDictionary(dict_file, use_precomputed)
        _arpabet_dictionary.load()
    
    return _arpabet_dictionary

def reset_arpabet_dictionary() -> None:
    """Reset the global Arpabet dictionary instance."""
    global _arpabet_dictionary
    _arpabet_dictionary = None

def get_pronunciation(word: str, remove_stress: bool = False, dict_file: Optional[Union[str, Path]] = None, 
                    use_precomputed: bool = True) -> List[List[str]]:
    """
    Get the Arpabet pronunciation for a word or phrase.
    
    Args:
        word: Word or phrase to get pronunciation for
        remove_stress: Whether to remove stress markers from the pronunciation
        dict_file: Optional dictionary file path
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        List of possible pronunciations, each a list of phonemes
    """
    dictionary = get_arpabet_dictionary(dict_file, use_precomputed)
    return dictionary.get_pronunciation(word, remove_stress)

def get_rhymes(word: str, syllables: Optional[int] = None, strength: str = "normal", 
              dict_file: Optional[Union[str, Path]] = None, use_precomputed: bool = True) -> List[str]:
    """
    Find words that rhyme with the given word or phrase.
    
    For multi-word phrases, the rhyming is based on the last word of the phrase.
    
    Args:
        word: The word or phrase to find rhymes for
        syllables: Optional number of syllables to filter rhymes (None for any)
        strength: Rhyming strength: "perfect" (exact match from last stressed vowel), 
                "normal" (match vowel sound and final consonants),
                "weak" (match only final vowel sound)
        dict_file: Optional dictionary file path
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        List of words that rhyme with the given word or phrase
    """
    dictionary = get_arpabet_dictionary(dict_file, use_precomputed)
    return dictionary.get_rhymes(word, syllables, strength)

def get_alliterations(word: str, dict_file: Optional[Union[str, Path]] = None, 
                     use_precomputed: bool = True) -> List[str]:
    """
    Find words that alliterate with the given word or phrase.
    
    For multi-word phrases, the alliteration is based on the first word of the phrase.
    
    Args:
        word: The word or phrase to find alliterations for
        dict_file: Optional dictionary file path
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        List of words that alliterate with the given word or phrase
    """
    dictionary = get_arpabet_dictionary(dict_file, use_precomputed)
    return dictionary.get_alliterations(word)

def get_syllable_count(word: str, dict_file: Optional[Union[str, Path]] = None, use_precomputed: bool = True) -> int:
    """
    Count the number of syllables in a word or phrase.
    
    Args:
        word: The word or phrase to count syllables for
        dict_file: Optional dictionary file path
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        The number of syllables in the word or phrase
    """
    dictionary = get_arpabet_dictionary(dict_file, use_precomputed)
    return dictionary.get_syllable_count(word)

def get_phonetic_similarity(word1: str, word2: str, dict_file: Optional[Union[str, Path]] = None, 
                           use_precomputed: bool = True) -> float:
    """
    Calculate the phonetic similarity between two words or phrases.
    
    For multi-word phrases, compares corresponding words and returns a weighted average.
    
    Args:
        word1: First word or phrase
        word2: Second word or phrase
        dict_file: Optional dictionary file path
        use_precomputed: Whether to use precomputed pronunciations if available
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    dictionary = get_arpabet_dictionary(dict_file, use_precomputed)
    return dictionary.get_phonetic_similarity(word1, word2) 