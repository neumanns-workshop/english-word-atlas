"""
Unit tests for the wordlist module.
"""

import pytest
from pathlib import Path
import json

from word_atlas.wordlist import WordlistBuilder


class TestWordlistBuilder:
    """Test the WordlistBuilder class."""

    def test_initialization(self, mock_atlas):
        """Test WordlistBuilder initialization."""
        # Test with existing atlas
        builder = WordlistBuilder(atlas=mock_atlas)
        assert builder.atlas == mock_atlas
        assert len(builder.words) == 0
        assert builder.metadata["name"] == "Custom Wordlist"

        # Test with data_dir
        builder = WordlistBuilder(data_dir=mock_atlas.data_dir)
        assert builder.atlas is not None
        assert len(builder.words) == 0

    def test_add_words(self, mock_atlas):
        """Test adding words to the wordlist."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test adding existing words
        count = builder.add_words(["apple", "banana"])
        assert count == 2
        assert "apple" in builder.words
        assert "banana" in builder.words

        # Test adding non-existent words
        count = builder.add_words(["nonexistent"])
        assert count == 0
        assert "nonexistent" not in builder.words

        # Test adding duplicate words
        count = builder.add_words(["apple"])
        assert count == 1
        assert len(builder.words) == 2  # Should still only have 2 unique words

    def test_add_by_search(self, mock_atlas):
        """Test adding words by search pattern."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test regex search
        count = builder.add_by_search("^a")
        assert count > 0
        assert all(word.startswith("a") for word in builder.words)

        # Test substring search
        builder.clear()
        count = builder.add_by_search("pp")
        assert count > 0
        assert all("pp" in word for word in builder.words)

    def test_add_by_attribute(self, mock_atlas):
        """Test adding words by attribute."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test adding by GSL attribute
        count = builder.add_by_attribute("GSL")
        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("GSL", False) for word in builder.words
        )

        # Test adding by Roget category
        builder.clear()
        count = builder.add_by_attribute("ROGET_FOOD")
        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("ROGET_FOOD", False) for word in builder.words
        )

    def test_add_by_frequency(self, mock_atlas):
        """Test adding words by frequency."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test with min frequency
        count = builder.add_by_frequency(min_freq=1)
        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("FREQ_GRADE", 0) >= 1
            for word in builder.words
        )

        # Test with max frequency
        builder.clear()
        count = builder.add_by_frequency(max_freq=2)
        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("FREQ_GRADE", float("inf")) <= 2
            for word in builder.words
        )

    def test_add_by_syllable_count(self, mock_atlas):
        """Test adding words by syllable count."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test adding words with specific syllable count
        count = builder.add_by_syllable_count(2)
        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("SYLLABLE_COUNT") == 2
            for word in builder.words
        )

    def test_remove_words(self, mock_atlas):
        """Test removing words from the wordlist."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        # Test removing existing words
        count = builder.remove_words(["apple"])
        assert count == 1
        assert "apple" not in builder.words
        assert "banana" in builder.words

        # Test removing non-existent words
        count = builder.remove_words(["nonexistent"])
        assert count == 0
        assert len(builder.words) == 1

    def test_metadata(self, mock_atlas):
        """Test metadata management."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test setting metadata
        builder.set_metadata(
            name="Test List",
            description="A test wordlist",
            creator="Test User",
            tags=["test", "example"],
        )

        metadata = builder.get_metadata()
        assert metadata["name"] == "Test List"
        assert metadata["description"] == "A test wordlist"
        assert metadata["creator"] == "Test User"
        assert metadata["tags"] == ["test", "example"]

    def test_save_and_load(self, mock_atlas, tmp_path):
        """Test saving and loading wordlists."""
        # Create and save a wordlist
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])
        builder.set_metadata(name="Test List")

        save_path = tmp_path / "test_wordlist.json"
        builder.save(save_path)

        # Load the wordlist
        loaded = WordlistBuilder.load(save_path, atlas=mock_atlas)
        assert loaded.words == builder.words
        assert loaded.metadata["name"] == "Test List"

    def test_analyze(self, mock_atlas):
        """Test wordlist analysis."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        analysis = builder.analyze()
        assert "size" in analysis
        assert "single_words" in analysis
        assert "phrases" in analysis
        assert "syllable_distribution" in analysis
        assert "wordlist_coverage" in analysis
        assert "frequency" in analysis

        # Check specific values
        assert analysis["size"] == 2
        assert analysis["single_words"] == 2
        assert analysis["phrases"] == 0
        assert isinstance(analysis["syllable_distribution"], dict)
        assert isinstance(analysis["wordlist_coverage"], dict)
        assert isinstance(analysis["frequency"], dict)

    def test_export_text(self, mock_atlas, tmp_path):
        """Test exporting wordlist to text file."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        export_path = tmp_path / "test_wordlist.txt"
        builder.export_text(export_path)

        with open(export_path) as f:
            content = f.read()
            assert "apple" in content
            assert "banana" in content

    def test_add_similar_words(self, mock_atlas):
        """Test adding similar words."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test with existing word
        count = builder.add_similar_words("apple", n=2)
        assert count > 0
        assert len(builder.words) > 0

        # Test with non-existent word
        count = builder.add_similar_words("nonexistent")
        assert count == 0

    def test_remove_by_search(self, mock_atlas):
        """Test removing words by search pattern."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        # Test regex search removal
        count = builder.remove_by_search("^a")
        assert count == 1
        assert "banana" in builder.words
        assert "apple" not in builder.words

    def test_remove_by_attribute(self, mock_atlas):
        """Test removing words by attribute."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        # Test removing by GSL attribute
        count = builder.remove_by_attribute("GSL")
        assert count > 0
        assert len(builder.words) == 0

    def test_get_wordlist(self, mock_atlas):
        """Test getting sorted wordlist."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["banana", "apple"])

        wordlist = builder.get_wordlist()
        assert isinstance(wordlist, list)
        assert len(wordlist) == 2
        assert wordlist == ["apple", "banana"]  # Should be sorted

    def test_analyze_edge_cases(self, mock_atlas):
        """Test wordlist analysis edge cases."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test empty wordlist
        analysis = builder.analyze()
        assert analysis == {"size": 0}

        # Test with words having different frequency buckets
        builder.add_words(["apple", "banana"])
        analysis = builder.analyze()
        assert "frequency" in analysis
        assert "distribution" in analysis["frequency"]
        assert isinstance(analysis["frequency"]["distribution"], dict)

    def test_export_text_edge_cases(self, mock_atlas, tmp_path):
        """Test exporting wordlist edge cases."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test exporting empty wordlist
        export_path = tmp_path / "empty_wordlist.txt"
        builder.export_text(export_path)
        assert export_path.exists()
        with open(export_path) as f:
            content = f.read()
            assert "# Custom Wordlist" in content
            assert "# Size: 0 words" in content
            assert not any(
                line for line in content.splitlines() if not line.startswith("#")
            )  # No non-comment lines

        # Test exporting without metadata
        export_path = tmp_path / "empty_no_metadata.txt"
        builder.export_text(export_path, include_metadata=False)
        assert export_path.exists()
        with open(export_path) as f:
            content = f.read()
            assert not content.strip()  # Should be empty

    def test_error_handling(self, mock_atlas, tmp_path):
        """Test error handling in various methods."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test saving to invalid directory
        with pytest.raises(OSError):
            builder.save("/nonexistent/dir/wordlist.json")

        # Test loading non-existent file
        with pytest.raises(FileNotFoundError):
            WordlistBuilder.load("/nonexistent/wordlist.json")

        # Test loading invalid JSON
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{invalid")
        with pytest.raises(json.JSONDecodeError):
            WordlistBuilder.load(invalid_json)

    def test_add_by_custom_filter(self, mock_atlas):
        """Test adding words using a custom filter."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test filter for words with exactly 2 syllables and GSL=True
        def custom_filter(word: str, attrs: dict) -> bool:
            return attrs.get("SYLLABLE_COUNT") == 2 and attrs.get("GSL", False)

        count = builder.add_by_custom_filter(custom_filter, "2 syllables and GSL words")

        assert count > 0
        assert all(
            mock_atlas.get_word(word).get("SYLLABLE_COUNT") == 2
            and mock_atlas.get_word(word).get("GSL")
            for word in builder.words
        )

        # Test filter that matches nothing
        def no_match_filter(word: str, attrs: dict) -> bool:
            return False

        builder.clear()
        count = builder.add_by_custom_filter(
            no_match_filter, "filter that matches nothing"
        )
        assert count == 0
        assert len(builder.words) == 0

    def test_analyze_frequency_stats(self, mock_atlas):
        """Test frequency statistics in analyze method."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])  # Both have FREQ_GRADE = 1

        analysis = builder.analyze()
        assert "frequency" in analysis
        assert "distribution" in analysis["frequency"]
        assert "average" in analysis["frequency"]

        # Test with word that has no frequency
        # Temporarily modify mock data to test different frequency buckets
        word_data = mock_atlas.get_word("apple")
        orig_freq = word_data["FREQ_GRADE"]

        # Test each frequency bucket
        freqs = [0, 5, 50, 500, 5000]
        for freq in freqs:
            word_data["FREQ_GRADE"] = freq
            analysis = builder.analyze()
            assert analysis["frequency"]["average"] > 0

        # Restore original frequency
        word_data["FREQ_GRADE"] = orig_freq

    def test_analyze_empty_word_data(self, mock_atlas):
        """Test analyze method with empty word data."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple"])

        # Temporarily remove all attributes from word data
        word_data = mock_atlas.get_word("apple")
        orig_data = word_data.copy()
        word_data.clear()

        analysis = builder.analyze()
        assert "syllable_distribution" in analysis
        assert "wordlist_coverage" in analysis
        assert "frequency" in analysis

        # Restore original data
        word_data.update(orig_data)

    def test_export_text_with_full_metadata(self, mock_atlas, tmp_path):
        """Test exporting wordlist with all metadata fields."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        # Set all metadata fields
        builder.set_metadata(
            name="Test List",
            description="A test description",
            creator="Test User",
            tags=["test", "example"],
        )

        export_path = tmp_path / "full_metadata.txt"
        builder.export_text(export_path)

        with open(export_path) as f:
            content = f.read()
            assert "# Test List" in content
            assert "# Description: A test description" in content
            assert "# Creator: Test User" in content
            assert "# Tags: test, example" in content
            assert "# Size: 2 words" in content

    def test_size_methods(self, mock_atlas):
        """Test different ways to get wordlist size."""
        builder = WordlistBuilder(atlas=mock_atlas)
        assert len(builder) == 0  # Test __len__
        assert builder.get_size() == 0  # Test get_size

        builder.add_words(["apple", "banana"])
        assert len(builder) == 2
        assert builder.get_size() == 2

        builder.clear()
        assert len(builder) == 0
        assert builder.get_size() == 0
        assert not builder.metadata["criteria"]  # Check criteria cleared
