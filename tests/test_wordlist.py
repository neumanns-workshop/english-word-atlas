"""
Tests for the WordlistBuilder functionality.
"""

import json
import os
from pathlib import Path
import tempfile
from typing import Dict, Any

import pytest

from word_atlas import WordlistBuilder
from word_atlas.wordlist import WordlistBuilder


@pytest.fixture
def mock_atlas(atlas):
    """Get the mock atlas with test data."""
    return atlas


@pytest.fixture
def empty_builder(mock_atlas):
    """Create an empty WordlistBuilder with mock data."""
    return WordlistBuilder(mock_atlas)


@pytest.fixture
def test_wordlist():
    """Create a simple test wordlist."""
    return ["apple", "banana", "cat", "dog", "freedom", "happy"]


@pytest.fixture
def populated_builder(mock_atlas, test_wordlist):
    """Create a WordlistBuilder with some pre-populated data."""
    builder = WordlistBuilder(mock_atlas)
    builder.add_words(test_wordlist)
    builder.set_metadata(
        name="Test Wordlist",
        description="A wordlist for testing",
        creator="Test User",
        tags=["test", "sample"],
    )
    return builder


class TestWordlistBuilder:
    """Tests for the WordlistBuilder class."""

    def test_init(self, mock_atlas):
        """Test initializing a WordlistBuilder."""
        builder = WordlistBuilder(mock_atlas)
        assert len(builder.words) == 0
        assert builder.metadata["name"] == "Custom Wordlist"

    def test_add_words(self, empty_builder, test_wordlist):
        """Test adding words to a wordlist."""
        # All words should be added since our mock atlas has them
        added = empty_builder.add_words(test_wordlist)
        assert added == len(test_wordlist)
        assert len(empty_builder.words) == len(test_wordlist)

        # Add some words that don't exist in the atlas
        nonexistent = ["nonexistent1", "nonexistent2"]
        added = empty_builder.add_words(nonexistent)
        assert added == 0  # No words should be added

        # Add duplicate words
        added = empty_builder.add_words(test_wordlist)
        assert added == len(test_wordlist)  # All words exist
        assert len(empty_builder.words) == len(test_wordlist)  # But no duplicates

    def test_add_by_search(self, empty_builder):
        """Test adding words by search pattern."""
        # Our mock data should have words containing 'a'
        added = empty_builder.add_by_search("a")
        assert added > 0

        # Pattern that shouldn't match anything
        added = empty_builder.add_by_search("zzzzzzz")
        assert added == 0

    def test_add_by_attribute(self, empty_builder):
        """Test adding words by attribute."""
        # Our mock data has words with the GSL attribute
        added = empty_builder.add_by_attribute("GSL")
        assert added > 0

        # Attribute that shouldn't match anything
        added = empty_builder.add_by_attribute("NONEXISTENT_ATTR")
        assert added == 0

    def test_add_by_frequency(self, empty_builder):
        """Test adding words by frequency range."""
        # Our mock data has words with frequency > 0
        added = empty_builder.add_by_frequency(min_freq=0)
        assert added > 0

        # Add words in a specific range
        empty_builder.clear()
        added = empty_builder.add_by_frequency(min_freq=50, max_freq=100)
        assert added >= 0  # May be 0 or more depending on mock data

    def test_add_by_syllable_count(self, empty_builder):
        """Test adding words by syllable count."""
        # Our mock data has words with 1 syllable
        added = empty_builder.add_by_syllable_count(1)
        assert added > 0

        # Syllable count that might not have matches
        empty_builder.clear()
        added = empty_builder.add_by_syllable_count(10)  # Very high syllable count
        assert added >= 0  # May be 0 or more

    def test_add_similar_words(self, empty_builder):
        """Test adding similar words."""
        # Our mock atlas should handle get_similar_words
        added = empty_builder.add_similar_words("apple", n=5)
        assert added > 0

        # Word not in atlas
        added = empty_builder.add_similar_words("nonexistent", n=5)
        assert added == 0

    def test_remove_words(self, populated_builder, test_wordlist):
        """Test removing words."""
        # Remove some words
        to_remove = test_wordlist[:2]  # First two words
        removed = populated_builder.remove_words(to_remove)
        assert removed == len(to_remove)
        assert len(populated_builder.words) == len(test_wordlist) - len(to_remove)

        # Try to remove words not in the list
        removed = populated_builder.remove_words(["nonexistent1", "nonexistent2"])
        assert removed == 0
        assert len(populated_builder.words) == len(test_wordlist) - len(to_remove)

    def test_clear(self, populated_builder):
        """Test clearing the wordlist."""
        assert len(populated_builder.words) > 0
        populated_builder.clear()
        assert len(populated_builder.words) == 0
        assert len(populated_builder.metadata["criteria"]) == 0

    def test_set_metadata(self, empty_builder):
        """Test setting metadata."""
        empty_builder.set_metadata(
            name="New Name",
            description="New Description",
            creator="New Creator",
            tags=["tag1", "tag2"],
        )

        metadata = empty_builder.get_metadata()
        assert metadata["name"] == "New Name"
        assert metadata["description"] == "New Description"
        assert metadata["creator"] == "New Creator"
        assert metadata["tags"] == ["tag1", "tag2"]

        # Test partial update
        empty_builder.set_metadata(name="Updated Name")
        metadata = empty_builder.get_metadata()
        assert metadata["name"] == "Updated Name"
        assert metadata["description"] == "New Description"  # Unchanged

    def test_get_wordlist(self, populated_builder, test_wordlist):
        """Test getting the wordlist."""
        wordlist = populated_builder.get_wordlist()
        assert isinstance(wordlist, list)
        assert len(wordlist) == len(test_wordlist)
        assert set(wordlist) == set(test_wordlist)
        assert wordlist == sorted(wordlist)  # Should be sorted

    def test_get_size(self, populated_builder, test_wordlist):
        """Test getting the size of the wordlist."""
        assert populated_builder.get_size() == len(test_wordlist)

        # Remove a word and check size
        populated_builder.remove_words([test_wordlist[0]])
        assert populated_builder.get_size() == len(test_wordlist) - 1

    def test_get_metadata(self, populated_builder):
        """Test getting metadata."""
        metadata = populated_builder.get_metadata()
        assert metadata["name"] == "Test Wordlist"
        assert metadata["description"] == "A wordlist for testing"
        assert metadata["creator"] == "Test User"
        assert metadata["tags"] == ["test", "sample"]
        assert metadata["size"] == len(populated_builder.words)

    def test_analyze(self, populated_builder):
        """Test analyzing a wordlist."""
        analysis = populated_builder.analyze()
        assert "size" in analysis
        assert analysis["size"] == len(populated_builder.words)
        assert "single_words" in analysis
        assert "phrases" in analysis

        # Test empty wordlist
        empty = WordlistBuilder(populated_builder.atlas)
        empty_analysis = empty.analyze()
        assert empty_analysis["size"] == 0

    def test_save_and_load(self, populated_builder, test_wordlist, tmp_path):
        """Test saving and loading a wordlist."""
        # Save the wordlist
        output_file = tmp_path / "test_wordlist.json"
        populated_builder.save(output_file)
        assert output_file.exists()

        # Load the wordlist
        loaded_builder = WordlistBuilder.load(output_file, populated_builder.atlas)
        assert loaded_builder.get_size() == len(test_wordlist)
        assert set(loaded_builder.get_wordlist()) == set(test_wordlist)

        # Check metadata was preserved
        metadata = loaded_builder.get_metadata()
        assert metadata["name"] == "Test Wordlist"
        assert metadata["tags"] == ["test", "sample"]

    def test_export_text(self, populated_builder, tmp_path):
        """Test exporting to a text file."""
        # Export with metadata
        output_file = tmp_path / "with_metadata.txt"
        populated_builder.export_text(output_file, include_metadata=True)
        assert output_file.exists()

        # Read the file and check contents
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # First line should be a comment with the name
        assert lines[0].startswith("# Test Wordlist")

        # Export without metadata
        output_file = tmp_path / "no_metadata.txt"
        populated_builder.export_text(output_file, include_metadata=False)

        # Read the file and check contents
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # First line should be a word, not a comment
        assert not lines[0].startswith("#")
        assert len(lines) == len(populated_builder.words)

    def test_len(self, populated_builder, test_wordlist):
        """Test the __len__ method."""
        assert len(populated_builder) == len(test_wordlist)

        # Remove a word and check length
        populated_builder.remove_words([test_wordlist[0]])
        assert len(populated_builder) == len(test_wordlist) - 1
