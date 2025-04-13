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

        # Check basic attributes (index, frequencies, sources)
        assert hasattr(atlas, "word_to_idx")
        assert hasattr(atlas, "frequencies")
        assert hasattr(atlas, "_source_lists")
        assert hasattr(atlas, "all_words")

        # Check stats are accessible (calculation tested separately)
        assert hasattr(atlas, "get_stats")

    def test_has_word(self, mock_atlas):
        """Test word existence check."""
        assert mock_atlas.has_word("apple")
        assert mock_atlas.has_word("banana")
        assert not mock_atlas.has_word("nonexistent")

    def test_get_all_words(self, mock_atlas):
        """Test getting all words."""
        words = mock_atlas.get_all_words()
        assert isinstance(words, list)
        assert len(words) == 3  # apple, banana, orange
        assert "apple" in words
        assert "banana" in words
        assert "orange" in words

    def test_search(self, mock_atlas):
        """Test word search functionality."""
        # Test prefix search (now simple substring)
        results = mock_atlas.search("a") # Case-insensitive substring default
        assert isinstance(results, list)
        assert len(results) == 3 # apple, banana, orange
        assert set(results) == {"apple", "banana", "orange"}

        # Test substring search
        results = mock_atlas.search("ana")
        assert isinstance(results, list)
        assert len(results) == 1
        assert "banana" in results

        # Test substring search for added word
        results = mock_atlas.search("ora")
        assert isinstance(results, list)
        assert len(results) == 1
        assert "orange" in results

        # Test search with special characters (should be treated literally)
        results = mock_atlas.search("(")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_filter(self, mock_atlas):
        """Test filtering by various criteria."""
        # Test filtering by source list
        gsl_words = mock_atlas.filter(sources=["GSL"])
        assert isinstance(gsl_words, set)
        assert gsl_words == {"apple", "banana"} # From mock_data_dir sources

        # Test filtering by another source list
        food_words = mock_atlas.filter(sources=["ROGET_FOOD"])
        assert isinstance(food_words, set)
        assert food_words == {"apple", "banana"}

        # Test filtering by multiple source lists (intersection)
        gsl_food_words = mock_atlas.filter(sources=["GSL", "ROGET_FOOD"])
        assert isinstance(gsl_food_words, set)
        assert gsl_food_words == {"apple", "banana"}

        # Test filtering by a source list not present
        with pytest.raises(ValueError, match="Source 'UNKNOWN_SOURCE' not found."):
            mock_atlas.filter(sources=["UNKNOWN_SOURCE"])

        # Test filtering by frequency
        # apple=150.5, banana=10.2, orange=90.0
        high_freq_words = mock_atlas.filter(min_freq=100.0)
        assert high_freq_words == {"apple"}
        low_freq_words = mock_atlas.filter(max_freq=50.0)
        assert low_freq_words == {"banana"}
        range_freq_words = mock_atlas.filter(min_freq=50.0, max_freq=100.0)
        assert range_freq_words == {"orange"}

        # Test combining filters (source + frequency)
        gsl_low_freq = mock_atlas.filter(sources=["GSL"], max_freq=50.0)
        assert gsl_low_freq == {"banana"}

    def test_get_frequency(self, mock_atlas):
        """Test retrieving word frequency."""
        assert mock_atlas.get_frequency("apple") == 150.5
        assert mock_atlas.get_frequency("banana") == 10.2
        assert mock_atlas.get_frequency("orange") == 90.0
        assert mock_atlas.get_frequency("nonexistent") is None

    def test_get_sources(self, mock_atlas):
        """Test retrieving sources for a word."""
        # Apple is in GSL, ROGET_FOOD, ROGET_PLANT
        assert mock_atlas.get_sources("apple") == sorted(["GSL", "ROGET_FOOD", "ROGET_PLANT"])
        # Banana is in GSL, ROGET_FOOD, ROGET_PLANT
        assert mock_atlas.get_sources("banana") == sorted(["GSL", "ROGET_FOOD", "ROGET_PLANT"])
        # Orange is only in OTHER (added by mock_atlas fixture)
        assert mock_atlas.get_sources("orange") == ["OTHER"]
        assert mock_atlas.get_sources("nonexistent") == []

    def test_get_source_list_names(self, mock_atlas):
        """Test getting all available source list names."""
        names = mock_atlas.get_source_list_names()
        assert isinstance(names, list)
        # Expect OTHER to be included now
        assert names == sorted(["GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"])

    def test_get_words_in_source(self, mock_atlas):
        """Test getting words belonging to a specific source."""
        assert mock_atlas.get_words_in_source("GSL") == {"apple", "banana"}
        assert mock_atlas.get_words_in_source("ROGET_PLANT") == {"apple", "banana"}
        assert mock_atlas.get_words_in_source("ROGET_FOOD") == {"apple", "banana"}
        # Check OTHER source added by fixture
        assert mock_atlas.get_words_in_source("OTHER") == {"orange"}
        with pytest.raises(ValueError, match="Source 'UNKNOWN' not found."):
            mock_atlas.get_words_in_source("UNKNOWN")

    def test_utility_methods(self, mock_atlas):
        """Test various utility methods."""
        assert len(mock_atlas) == 3
        assert "apple" in mock_atlas
        assert "nonexistent" not in mock_atlas

        # Test get_source_list_names includes OTHER
        categories = mock_atlas.get_source_list_names()
        assert isinstance(categories, list)
        assert categories == sorted(["GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"])

        # Check source coverage from stats
        stats = mock_atlas.get_stats()
        assert "source_coverage" in stats
        # Update expected coverage to include OTHER
        assert stats["source_coverage"] == {
            "GSL": 2,
            "OTHER": 1,
            "ROGET_FOOD": 2,
            "ROGET_PLANT": 2
        }
        assert "metadata_attributes" not in stats
        assert "embedding_dim" not in stats

    def test_word_counts_from_stats(self, mock_atlas):
        """Test phrase and single word counts via get_stats."""
        stats = mock_atlas.get_stats()
        assert "phrases" in stats
        assert "single_words" in stats
        # Based on mock_data_dir fixture (apple, banana, orange)
        assert stats["phrases"] == 0
        assert stats["single_words"] == 3

    def test_source_list_discovery(self, mock_atlas):
        """Test that source lists are discovered correctly."""
        source_names = mock_atlas.get_source_list_names()
        # Update expectation to include OTHER
        assert sorted(source_names) == sorted(["GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"])
        gsl_words = mock_atlas.get_words_in_source("GSL")
        assert gsl_words == {"apple", "banana"}
        # Check OTHER source content
        other_words = mock_atlas.get_words_in_source("OTHER")
        assert other_words == {"orange"}

    def test_get_stats(self, mock_atlas):
        """Test the get_stats method."""
        stats = mock_atlas.get_stats()
        assert isinstance(stats, dict)

        assert stats["total_entries"] == 3
        assert stats["single_words"] == 3
        assert stats["phrases"] == 0
        assert "entries_with_frequency" in stats
        assert stats["entries_with_frequency"] == 3

        assert "source_lists" in stats
        # Update expectation to include OTHER
        assert sorted(stats["source_lists"]) == sorted(["GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"])
        assert "source_coverage" in stats
        # Update expected coverage to include OTHER
        assert stats["source_coverage"] == {
            "GSL": 2,
            "OTHER": 1,
            "ROGET_FOOD": 2,
            "ROGET_PLANT": 2
        }
        assert "embedding_dim" not in stats
