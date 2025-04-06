"""
Unit tests for the atlas module.
"""

import pytest
import numpy as np
from pathlib import Path

from word_atlas.atlas import WordAtlas


class TestWordAtlas:
    """Test the WordAtlas class."""

    def test_initialization(self, mock_data_dir):
        """Test WordAtlas initialization."""
        atlas = WordAtlas(mock_data_dir)

        # Check basic attributes
        assert hasattr(atlas, "embeddings")
        assert hasattr(atlas, "word_to_idx")
        assert hasattr(atlas, "word_data")
        assert hasattr(atlas, "idx_to_word")

        # Check statistics
        assert "total_entries" in atlas.stats
        assert "single_words" in atlas.stats
        assert "phrases" in atlas.stats
        assert "embedding_dim" in atlas.stats

        # Check values
        assert atlas.stats["total_entries"] == len(atlas.word_data)
        assert atlas.stats["embedding_dim"] == atlas.embeddings.shape[1]

    def test_get_word(self, mock_atlas):
        """Test retrieving word information."""
        # Test existing word
        word_info = mock_atlas.get_word("apple")
        assert isinstance(word_info, dict)
        assert "SYLLABLE_COUNT" in word_info
        assert "FREQ_GRADE" in word_info
        assert "GSL" in word_info
        assert word_info["SYLLABLE_COUNT"] == 2

        # Test non-existent word
        assert mock_atlas.get_word("nonexistent") == {}

    def test_get_embedding(self, mock_atlas):
        """Test getting word embeddings."""
        # Test existing word
        embedding = mock_atlas.get_embedding("apple")
        assert isinstance(embedding, np.ndarray)
        assert embedding.ndim == 1
        assert embedding.shape[0] == 384  # From mock data

        # Test non-existent word
        assert mock_atlas.get_embedding("nonexistent") is None

    def test_has_word(self, mock_atlas):
        """Test word existence check."""
        assert mock_atlas.has_word("apple")
        assert mock_atlas.has_word("banana")
        assert not mock_atlas.has_word("nonexistent")

    def test_get_all_words(self, mock_atlas):
        """Test getting all words."""
        words = mock_atlas.get_all_words()
        assert isinstance(words, list)
        assert len(words) == 2  # From mock data
        assert "apple" in words
        assert "banana" in words

    def test_search(self, mock_atlas):
        """Test word search functionality."""
        # Test regex search
        results = mock_atlas.search("^a")
        assert isinstance(results, list)
        assert len(results) == 1
        assert "apple" in results

        # Test substring search
        results = mock_atlas.search("ana")
        assert isinstance(results, list)
        assert len(results) == 1
        assert "banana" in results

        # Test invalid regex - should return empty list
        results = mock_atlas.search("[")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_filter_by_attribute(self, mock_atlas):
        """Test filtering by attribute."""
        # Test boolean attribute
        gsl_words = mock_atlas.filter_by_attribute("GSL")
        assert isinstance(gsl_words, set)
        assert len(gsl_words) == 2  # Both words are GSL
        assert "apple" in gsl_words
        assert "banana" in gsl_words

        # Test Roget category
        food_words = mock_atlas.filter_by_attribute("ROGET_FOOD")
        assert isinstance(food_words, set)
        assert len(food_words) == 2
        assert "apple" in food_words
        assert "banana" in food_words

    def test_filter_by_syllable_count(self, mock_atlas):
        """Test filtering by syllable count."""
        # Test 2-syllable words
        two_syllables = mock_atlas.filter_by_syllable_count(2)
        assert isinstance(two_syllables, set)
        assert len(two_syllables) == 1
        assert "apple" in two_syllables

        # Test 3-syllable words
        three_syllables = mock_atlas.filter_by_syllable_count(3)
        assert isinstance(three_syllables, set)
        assert len(three_syllables) == 1
        assert "banana" in three_syllables

    def test_filter_by_frequency(self, mock_atlas):
        """Test filtering by frequency."""
        # Test with min frequency
        words = mock_atlas.filter_by_frequency(min_freq=1)
        assert isinstance(words, list)
        assert len(words) == 2  # Both words have FREQ_GRADE = 1

        # Test with max frequency
        words = mock_atlas.filter_by_frequency(max_freq=1)
        assert isinstance(words, list)
        assert len(words) == 2

        # Test with both
        words = mock_atlas.filter_by_frequency(min_freq=1, max_freq=1)
        assert isinstance(words, list)
        assert len(words) == 2

    def test_word_similarity(self, mock_atlas):
        """Test word similarity calculation."""
        # Test existing words
        similarity = mock_atlas.word_similarity("apple", "banana")
        assert isinstance(similarity, (float, np.floating))
        assert -1 <= float(similarity) <= 1

        # Test with non-existent word
        assert mock_atlas.word_similarity("apple", "nonexistent") == 0.0
        assert mock_atlas.word_similarity("nonexistent", "banana") == 0.0

    def test_get_similar_words(self, mock_atlas):
        """Test getting similar words."""
        # Test with existing word
        similar = mock_atlas.get_similar_words("apple", n=1)
        assert isinstance(similar, list)
        assert len(similar) == 1
        assert len(similar[0]) == 2  # (word, score) tuple
        assert isinstance(similar[0][0], str)
        assert isinstance(similar[0][1], (float, np.floating))

        # Test with non-existent word
        assert mock_atlas.get_similar_words("nonexistent") == []

        # Test with n=0
        assert mock_atlas.get_similar_words("apple", n=0) == []

    def test_syllable_counting(self, mock_atlas):
        """Test syllable counting from ARPABET."""
        # Test with mock data
        word_data = mock_atlas.get_word("apple")
        assert "ARPABET" in word_data
        assert word_data["SYLLABLE_COUNT"] == 2

        word_data = mock_atlas.get_word("banana")
        assert "ARPABET" in word_data
        assert word_data["SYLLABLE_COUNT"] == 3

    def test_frequency_indexing(self, mock_atlas):
        """Test frequency indexing."""
        # Both mock words have FREQ_GRADE = 1
        words = mock_atlas.filter_by_frequency(min_freq=1, max_freq=1)
        assert len(words) == 2
        assert "apple" in words
        assert "banana" in words

        # No words with high frequency
        words = mock_atlas.filter_by_frequency(min_freq=1000)
        assert len(words) == 0

    def test_utility_methods(self, mock_atlas):
        """Test various utility methods."""
        # Test __len__
        assert len(mock_atlas) == 2

        # Test __contains__
        assert "apple" in mock_atlas
        assert "nonexistent" not in mock_atlas

        # Test get_roget_categories
        categories = mock_atlas.get_roget_categories()
        assert isinstance(categories, list)
        assert "ROGET_FOOD" in categories
        assert "ROGET_PLANT" in categories

        # Test get_syllable_counts
        counts = mock_atlas.get_syllable_counts()
        assert isinstance(counts, list)
        assert 2 in counts  # apple
        assert 3 in counts  # banana

    def test_arpabet_syllable_counting(self, mock_atlas):
        """Test ARPABET syllable counting in detail."""
        # Test with mock data that has ARPABET but no SYLLABLE_COUNT
        word_data = mock_atlas.get_word("apple")
        orig_data = word_data.copy()

        # Remove SYLLABLE_COUNT to force ARPABET counting
        del word_data["SYLLABLE_COUNT"]
        assert word_data["ARPABET"] == [["AE1", "P", "AH0", "L"]]  # From mock data

        # Re-index to trigger ARPABET counting
        mock_atlas._build_indices()

        # Check that syllable count was calculated from ARPABET
        assert mock_atlas.filter_by_syllable_count(2)

        # Restore original data
        word_data.update(orig_data)

    def test_phrases_and_single_words(self, mock_atlas):
        """Test phrase and single word filtering."""
        # Add a mock phrase
        mock_atlas.word_data["red apple"] = {
            "SYLLABLE_COUNT": 3,
            "FREQ_GRADE": 1,
            "GSL": True,
        }

        phrases = mock_atlas.get_phrases()
        assert len(phrases) == 1
        assert "red apple" in phrases

        singles = mock_atlas.get_single_words()
        assert len(singles) == 2
        assert "apple" in singles
        assert "banana" in singles

        # Clean up
        del mock_atlas.word_data["red apple"]

    def test_roget_categories_complete(self, mock_atlas):
        """Test complete Roget category functionality."""
        # Add a mock word with different Roget categories
        mock_atlas.word_data["orange"] = {
            "ROGET_FOOD": True,
            "ROGET_COLOR": True,
            "FREQ_GRADE": 1,
        }
        mock_atlas._build_indices()

        categories = mock_atlas.get_roget_categories()
        assert len(categories) >= 3  # FOOD, PLANT, COLOR
        assert "ROGET_FOOD" in categories
        assert "ROGET_PLANT" in categories
        assert "ROGET_COLOR" in categories

        # Test filtering with new category
        color_words = mock_atlas.filter_by_attribute("ROGET_COLOR")
        assert len(color_words) == 1
        assert "orange" in color_words

        # Clean up
        del mock_atlas.word_data["orange"]
        mock_atlas._build_indices()

    def test_get_stats(self, mock_atlas):
        """Test getting dataset statistics."""
        stats = mock_atlas.get_stats()
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "single_words" in stats
        assert "phrases" in stats
        assert "embedding_dim" in stats
        assert stats["total_entries"] == len(mock_atlas)
        assert stats["embedding_dim"] == mock_atlas.embeddings.shape[1]
