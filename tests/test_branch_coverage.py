import pytest
import os
import json
import re
import numpy as np
from pathlib import Path
from word_atlas.atlas import WordAtlas
from word_atlas.wordlist import WordlistBuilder

# Reuse fixtures from test_wordlist.py
from tests.test_wordlist import (
    mock_atlas,
    empty_builder,
    test_wordlist,
    populated_builder,
)


class TestBranchCoverage:
    """Tests specifically targeting branch coverage."""

    # WordlistBuilder tests

    def test_add_similar_non_existent_word(self, empty_builder):
        """Test add_similar_words with a word that doesn't exist."""
        result = empty_builder.add_similar_words("nonexistent_word")
        assert result == 0
        assert empty_builder.get_size() == 0

    def test_add_by_custom_filter_no_matches(self, empty_builder):
        """Test add_by_custom_filter with a filter that matches nothing."""

        def never_match(word, attrs):
            return False

        result = empty_builder.add_by_custom_filter(
            never_match, "Never matches anything"
        )
        assert result == 0
        assert empty_builder.get_size() == 0

    def test_add_by_custom_filter_with_matches(self, empty_builder):
        """Test add_by_custom_filter with a filter that matches some words."""

        def match_cat(word, attrs):
            return word == "cat"

        result = empty_builder.add_by_custom_filter(match_cat, "Only matches 'cat'")
        assert result == 1
        assert "cat" in empty_builder.get_wordlist()

    def test_remove_words_empty_list(self, populated_builder):
        """Test remove_words with an empty list."""
        initial_size = populated_builder.get_size()
        result = populated_builder.remove_words([])
        assert result == 0
        assert populated_builder.get_size() == initial_size

    def test_remove_words_non_existent(self, populated_builder):
        """Test remove_words with words that don't exist in the wordlist."""
        initial_size = populated_builder.get_size()
        result = populated_builder.remove_words(["nonexistent_word"])
        assert result == 0
        assert populated_builder.get_size() == initial_size

    def test_remove_by_search_no_matches(self, populated_builder):
        """Test remove_by_search with a pattern that doesn't match anything."""
        initial_size = populated_builder.get_size()
        result = populated_builder.remove_by_search("xyz123nonexistent")
        assert result == 0
        assert populated_builder.get_size() == initial_size

    def test_remove_by_attribute_no_matches(self, populated_builder):
        """Test remove_by_attribute with an attribute that doesn't match anything."""
        initial_size = populated_builder.get_size()
        result = populated_builder.remove_by_attribute("NONEXISTENT_ATTR")
        assert result == 0
        assert populated_builder.get_size() == initial_size

    def test_set_metadata_all_none(self, empty_builder):
        """Test set_metadata with all None values."""
        initial_metadata = empty_builder.get_metadata().copy()
        empty_builder.set_metadata(None, None, None, None)
        assert empty_builder.get_metadata() == initial_metadata

    def test_load_minimal_json(self, empty_builder, tmp_path):
        """Test loading a minimal JSON file with just words and no metadata."""
        # Create a minimal JSON file
        minimal_data = {"words": ["apple", "banana", "cat"]}

        output_file = tmp_path / "minimal.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(minimal_data, f)

        # Load the minimal file
        loaded = WordlistBuilder.load(output_file, empty_builder.atlas)
        assert loaded.get_size() == 3
        assert set(loaded.get_wordlist()) == {"apple", "banana", "cat"}

        # Check default metadata field existence
        metadata = loaded.get_metadata()
        assert "name" in metadata
        assert "size" in metadata
        assert metadata["size"] == 3

    def test_analyze_empty_wordlist(self, empty_builder):
        """Test analyze with an empty wordlist."""
        analysis = empty_builder.analyze()
        assert analysis == {"size": 0}

    def test_analyze_with_word_no_attributes(self, mock_atlas, empty_builder):
        """Test analyze with a word that has no special attributes."""
        # Add a word to the wordlist
        empty_builder.add_words(["cat"])

        # Verify the analysis has expected fields
        analysis = empty_builder.analyze()
        assert analysis["size"] > 0
        assert "syllable_distribution" in analysis
        assert "wordlist_coverage" in analysis

    def test_export_text_without_metadata(self, populated_builder, tmp_path):
        """Test export_text with include_metadata=False."""
        output_file = tmp_path / "no_metadata.txt"
        populated_builder.export_text(output_file, include_metadata=False)

        # Read the file and check contents
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # First line should be a word, not a comment
        assert not lines[0].startswith("#")
        # Should have exactly one line per word
        assert len(lines) == populated_builder.get_size()

    # WordAtlas tests

    def test_search_invalid_regex(self, mock_atlas):
        """Test search with an invalid regex pattern."""
        # Using a pattern that will cause a regex error but exists as substring
        results = mock_atlas.search(
            "[cat"
        )  # Invalid regex, should fall back to substring

        # Words containing the substring "[cat" (none in our test data)
        assert isinstance(results, list)
        # The exact result depends on the test data, just verify the method didn't crash

    def test_filter_by_attribute_roget_category(self, mock_atlas):
        """Test filter_by_attribute with a Roget category."""
        # Test the specific branch for Roget categories
        results = mock_atlas.filter_by_attribute("ROGET_ANIMAL")
        assert isinstance(results, set)

        # Check if the results include expected animal words
        # Our test might not have all these, just check that results are sensible
        animal_words = set(["cat", "dog", "elephant"])
        common_words = results.intersection(animal_words)
        assert len(common_words) > 0

    def test_filter_by_frequency_no_max(self, mock_atlas):
        """Test filter_by_frequency with no maximum."""
        # Test the branch where max_freq is None
        results = mock_atlas.filter_by_frequency(min_freq=300)
        assert isinstance(results, list)

        # Should include words with freq >= 300, if any exist in test data
        for word in results:
            word_data = mock_atlas.get_word(word)
            assert word_data.get("FREQ_GRADE", 0) >= 300

    def test_word_similarity_missing_word(self, mock_atlas):
        """Test word_similarity with missing words."""
        # Test the branch where a word doesn't exist
        similarity = mock_atlas.word_similarity("nonexistent_word", "cat")
        assert similarity == 0.0

        # Test when both words don't exist
        similarity = mock_atlas.word_similarity("nonexistent1", "nonexistent2")
        assert similarity == 0.0

    def test_get_similar_words_nonexistent(self, mock_atlas):
        """Test get_similar_words with a non-existent word."""
        results = mock_atlas.get_similar_words("nonexistent_word")
        assert results == []

    def test_get_similar_words_identical_word(self, mock_atlas):
        """Test get_similar_words skips the target word itself."""
        # Using a word that exists in our test data
        results = mock_atlas.get_similar_words("cat")

        # The word itself should be skipped in the results
        assert all(word != "cat" for word, _ in results)

    def test_filter_by_syllable_count_nonexistent(self, mock_atlas):
        """Test filter_by_syllable_count with a count that doesn't exist."""
        # Test the branch for a syllable count that isn't in the index
        results = mock_atlas.filter_by_syllable_count(99)
        assert results == set()

    def test_count_syllables_no_vowels(self, mock_atlas):
        """Test _count_syllables_from_arpabet with a pronunciation without vowels."""
        # This is an edge case that shouldn't happen in real data
        # but it tests a branch in the code
        result = mock_atlas._count_syllables_from_arpabet(["S", "T", "P"])
        assert result == 0
