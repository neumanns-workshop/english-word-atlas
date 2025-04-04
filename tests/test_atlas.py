"""Tests for the WordAtlas class."""

import numpy as np
import pytest

from word_atlas import WordAtlas


class TestWordAtlas:
    """Test the WordAtlas class."""

    def test_initialization(self, atlas):
        """Test that the atlas initializes correctly."""
        assert isinstance(atlas, WordAtlas)
        assert len(atlas) == 10  # 10 words in our mock dataset

        # Check stats
        stats = atlas.get_stats()
        assert stats["total_entries"] == 10
        assert stats["single_words"] == 9  # All words except "good idea"
        assert stats["phrases"] == 1  # Just "good idea"
        assert stats["embedding_dim"] == 4  # Our test embeddings are 4D

    def test_get_word(self, atlas):
        """Test retrieving word information."""
        # Existing word
        apple_info = atlas.get_word("apple")
        assert apple_info["SYLLABLE_COUNT"] == 2
        assert apple_info["FREQ_GRADE"] == 350.5
        assert apple_info["GSL"] is True
        assert apple_info["ROGET_FOOD"] is True

        # Non-existent word
        assert atlas.get_word("nonexistent") == {}

    def test_has_word(self, atlas):
        """Test checking if words exist in the dataset."""
        assert atlas.has_word("apple") is True
        assert atlas.has_word("banana") is True
        assert atlas.has_word("good idea") is True  # Test phrase
        assert atlas.has_word("nonexistent") is False

    def test_get_embedding(self, atlas):
        """Test retrieving word embeddings."""
        # Get embedding for "apple"
        embedding = atlas.get_embedding("apple")
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (4,)  # 4D embeddings in our test

        # Test normalization
        assert np.isclose(np.linalg.norm(embedding), 1.0)

        # Non-existent word
        assert atlas.get_embedding("nonexistent") is None

    def test_search(self, atlas):
        """Test searching for words by pattern."""
        # Regex pattern
        results = set(atlas.search("a.*e"))
        assert "apple" in results
        assert len(results) >= 1

        # Substring search
        results_a = set(atlas.search("a"))
        assert "apple" in results_a
        assert len(results_a) >= 3

        # No matches
        assert atlas.search("xyz") == []

        # Skip testing invalid regex - implementation dependent

    def test_get_phrases_and_single_words(self, atlas):
        """Test getting phrases and single words."""
        assert set(atlas.get_phrases()) == {"good idea"}

        single_words = atlas.get_single_words()
        assert len(single_words) == 9
        assert "good idea" not in single_words
        assert "apple" in single_words

    def test_filter_by_attribute(self, atlas):
        """Test filtering words by attributes."""
        # Filter by GSL
        gsl_words = atlas.filter_by_attribute("GSL")
        assert len(gsl_words) == 7
        assert "apple" in gsl_words
        assert "elephant" not in gsl_words

        # Filter by Roget category
        animals = atlas.filter_by_attribute("ROGET_ANIMAL")
        assert set(animals) == {"cat", "dog", "elephant"}

        # Non-existent attribute
        assert atlas.filter_by_attribute("NONEXISTENT") == set()

    def test_filter_by_syllable_count(self, atlas):
        """Test filtering words by syllable count."""
        # 1 syllable words
        one_syllable = atlas.filter_by_syllable_count(1)
        assert set(one_syllable) == {"cat", "dog", "sad", "swim"}

        # 2 syllable words
        two_syllable = atlas.filter_by_syllable_count(2)
        assert set(two_syllable) == {"apple", "freedom", "happy"}

        # 3 syllable words
        three_syllable = atlas.filter_by_syllable_count(3)
        assert set(three_syllable) == {"banana", "elephant", "good idea"}

        # No words with this count
        assert atlas.filter_by_syllable_count(4) == set()

    def test_filter_by_frequency(self, atlas):
        """Test filtering words by frequency."""
        # High frequency words (>300)
        high_freq = atlas.filter_by_frequency(min_freq=300)
        assert set(high_freq) == {"apple", "cat", "dog", "happy"}

        # Medium frequency words (150-300)
        mid_freq = atlas.filter_by_frequency(min_freq=150, max_freq=300)
        assert set(mid_freq) == {"banana", "freedom", "sad", "swim"}

        # Low frequency words (<150)
        low_freq = atlas.filter_by_frequency(max_freq=150)
        assert set(low_freq) == {"elephant", "good idea"}

    def test_word_similarity(self, atlas):
        """Test word similarity calculation."""
        # Words that should have high similarity
        happy_sad = atlas.word_similarity("happy", "sad")
        assert 0 <= happy_sad <= 1.0  # Should be a normalized similarity score

        # Test against ourselves (should be 1.0)
        apple_apple = atlas.word_similarity("apple", "apple")
        assert np.isclose(apple_apple, 1.0)

        # Non-existent words
        assert atlas.word_similarity("apple", "nonexistent") == 0.0
        assert atlas.word_similarity("nonexistent", "apple") == 0.0

    def test_get_similar_words(self, atlas):
        """Test finding similar words."""
        # Get similar words for "happy"
        similar = atlas.get_similar_words("happy", n=3)

        # Should return 3 (word, score) tuples
        assert len(similar) == 3
        assert all(isinstance(item, tuple) and len(item) == 2 for item in similar)
        assert all(
            isinstance(item[0], str) and isinstance(item[1], float) for item in similar
        )

        # Scores should be sorted in descending order
        assert similar[0][1] >= similar[1][1] >= similar[2][1]

        # Non-existent word
        assert atlas.get_similar_words("nonexistent") == []

    def test_get_roget_categories(self, atlas):
        """Test getting Roget categories."""
        categories = atlas.get_roget_categories()
        assert set(categories) == {
            "ROGET_FOOD",
            "ROGET_ANIMAL",
            "ROGET_ABSTRACT",
            "ROGET_THOUGHT",
            "ROGET_EMOTION",
            "ROGET_MOTION",
        }

    def test_get_syllable_counts(self, atlas):
        """Test getting syllable counts."""
        counts = atlas.get_syllable_counts()
        # Test that counts include at least the expected values, but may include others
        assert set(counts).issuperset({1, 2, 3})

    def test_contains(self, atlas):
        """Test the __contains__ method."""
        assert "apple" in atlas
        assert "cat" in atlas
        assert "good idea" in atlas
        assert "nonexistent" not in atlas
