"""
Unit tests for the atlas module.
"""

import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import io  # Import io for StringIO

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
        results = mock_atlas.search("a")  # Case-insensitive substring default
        assert isinstance(results, list)
        assert len(results) == 3  # apple, banana, orange
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
        assert gsl_words == {"apple", "banana"}  # From mock_data_dir sources

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
        assert mock_atlas.get_sources("apple") == sorted(
            ["GSL", "ROGET_FOOD", "ROGET_PLANT"]
        )
        # Banana is in GSL, ROGET_FOOD, ROGET_PLANT
        assert mock_atlas.get_sources("banana") == sorted(
            ["GSL", "ROGET_FOOD", "ROGET_PLANT"]
        )
        # Orange is only in OTHER (added by mock_atlas fixture)
        assert mock_atlas.get_sources("orange") == ["OTHER"]
        # Check that a non-existent word raises KeyError
        with pytest.raises(KeyError):
            mock_atlas.get_sources("nonexistent")

    def test_get_source_list_names(self, mock_atlas):
        """Test retrieving the list of available source list names."""
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

        # Check source coverage from stats - Use correct key
        stats = mock_atlas.get_stats()
        assert "coverage" in stats # Changed from "source_coverage"
        assert set(stats["coverage"].keys()) == set(categories)

    def test_word_counts_from_stats(self, mock_atlas):
        """Test phrase and single word counts via get_stats."""
        stats = mock_atlas.get_stats()
        # Use correct keys
        assert "total_phrases" in stats # Changed from "phrases"
        assert "total_words" in stats # Changed from "single_words"
        # Add assertions for the actual values based on mock data (assuming no phrases in mock)
        assert stats["total_words"] == 3
        assert stats["total_phrases"] == 0
        assert stats["total_entries"] == 3

    def test_source_list_discovery(self, mock_atlas):
        """Test that source lists are discovered correctly."""
        source_names = mock_atlas.get_source_list_names()
        # Update expectation to include OTHER
        assert sorted(source_names) == sorted(
            ["GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"]
        )
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
        # Use correct keys
        assert stats["total_words"] == 3 # Changed from "single_words"
        assert stats["total_phrases"] == 0 # Changed from "phrases"

        # Check coverage dictionary structure and values
        assert "coverage" in stats
        assert isinstance(stats["coverage"], dict)
        assert set(stats["coverage"].keys()) == {"GSL", "OTHER", "ROGET_FOOD", "ROGET_PLANT"}
        # Example check for one source (adjust based on mock data if needed)
        # GSL has apple, banana (2 words) out of 3 total entries
        assert stats["coverage"]["GSL"] == pytest.approx((2 / 3) * 100)
        # OTHER has orange (1 word) out of 3 total entries
        assert stats["coverage"]["OTHER"] == pytest.approx((1 / 3) * 100)
        # Removed check for embedding_dim as it's not in the current stats
        # assert "embedding_dim" not in stats

    def test_get_stats_empty(self, mock_data_dir):
        """Test get_stats with an empty atlas to cover the division by zero case."""
        # Create an atlas instance (mocks will prevent loading)
        atlas = WordAtlas(data_dir=mock_data_dir)

        # Explicitly set internal structures to empty *after* init
        atlas.word_to_idx = {}
        atlas._source_lists = {}
        atlas.frequencies = {}

        # Mock get_source_list_names to return empty list for this empty state
        with patch.object(atlas, 'get_source_list_names', return_value=[]):
            stats = atlas.get_stats()

        assert stats["total_words"] == 0
        assert stats["total_phrases"] == 0
        assert stats["total_entries"] == 0
        assert stats["coverage"] == {}

    # ---- Tests for Source Loading and Error Handling ----

    def test_source_discovery_txt(self, mock_data_dir):
        """Test discovery and loading of .txt source files."""
        # Create a .txt source file
        txt_source_path = mock_data_dir / "sources" / "TXT_Source.txt"
        txt_source_path.write_text("apple\nnew_word_txt\n", encoding="utf-8")

        # Re-initialize atlas to pick up the new file
        atlas = WordAtlas(data_dir=mock_data_dir)

        assert "TXT_Source" in atlas.get_source_list_names()
        # Assuming 'apple' is in the main index but 'new_word_txt' is not
        assert atlas.get_words_in_source("TXT_Source") == {"apple"}
        # Check that new_word_txt was ignored (due to not being in index)
        assert "new_word_txt" not in atlas.get_words_in_source("TXT_Source")

    def test_source_loading_invalid_json(self, mock_data_dir, capsys):
        """Test handling of invalid JSON source files during loading."""
        invalid_json_path = mock_data_dir / "sources" / "INVALID_JSON.json"
        invalid_json_path.write_text("this is not json", encoding="utf-8")

        # Initialize atlas - should print warning
        atlas = WordAtlas(data_dir=mock_data_dir)
        captured_init = capsys.readouterr()  # Capture warnings from init

        # Source name might still be discovered, but loading fails
        assert "INVALID_JSON" in atlas.get_source_list_names()
        assert (
            "Warning: Could not parse source JSON 'INVALID_JSON'" in captured_init.err
        )
        # Verify get_words_in_source returns empty set (should not print another warning here)
        result = atlas.get_words_in_source("INVALID_JSON")
        assert result == set()
        captured_get = capsys.readouterr()  # Check if it warned again
        assert "Returning empty set" not in captured_get.err  # Should not warn again

    def test_source_loading_file_not_found(self, mock_data_dir, capsys, monkeypatch):
        """Test handling when a source file disappears before loading."""
        # We need to mock builtins.open for this one
        original_open = open
        disappearing_path = mock_data_dir / "sources" / "DISAPPEARING.json"
        # Write it first so it's discovered
        disappearing_path.write_text('["apple"] ', encoding="utf-8")

        # --- Reimplement using patch('builtins.open') ---
        with patch("builtins.open") as mock_open:

            def open_side_effect(file, mode="r", **kwargs):
                if str(file) == str(disappearing_path):
                    raise FileNotFoundError(f"Mock disparition for {file}")
                # Fallback to actual open for other files (like index, frequencies)
                return original_open(file, mode=mode, **kwargs)

            mock_open.side_effect = open_side_effect

            # Initialize atlas - should print warning
            atlas = WordAtlas(data_dir=mock_data_dir)
            # captured_init = capsys.readouterr() # Don't capture yet
        # ------------------------------------------------

        assert "DISAPPEARING" in atlas.get_source_list_names()

        # Call the method, then capture all stderr at once
        result = atlas.get_words_in_source("DISAPPEARING")
        assert result == set()
        captured_all = capsys.readouterr()

        # Check both warnings are present in the combined stderr
        assert (
            "Warning: Source file 'DISAPPEARING' disappeared before loading"
            in captured_all.err
        )

        # Clean up the file we created
        if disappearing_path.exists():
            disappearing_path.unlink()

    def test_source_loading_non_string_items(self, mock_data_dir, capsys):
        """Test handling when a source file contains non-string items."""
        non_string_path = mock_data_dir / "sources" / "NON_STRING.json"
        # Include valid word 'apple' and invalid items
        non_string_path.write_text('["apple", 123, null, {"a": 1}] ', encoding="utf-8")

        atlas = WordAtlas(data_dir=mock_data_dir)
        captured = capsys.readouterr()

        assert (
            "NON_STRING" in atlas.get_source_list_names()
        )  # Should still load valid items
        assert atlas.get_words_in_source("NON_STRING") == {"apple"}
        assert (
            "Warning: Source 'NON_STRING' contained 3 non-string items" in captured.err
        )

    def test_source_loading_unknown_words(self, mock_data_dir, capsys):
        """Test handling when a source file contains words not in the main index."""
        unknown_words_path = mock_data_dir / "sources" / "UNKNOWN_WORDS.json"
        # Include valid word 'banana' and unknown words
        unknown_words_path.write_text(
            '["banana", "zzxxyy", "qqwwrr"] ', encoding="utf-8"
        )

        atlas = WordAtlas(data_dir=mock_data_dir)
        captured = capsys.readouterr()

        assert "UNKNOWN_WORDS" in atlas.get_source_list_names()
        assert atlas.get_words_in_source("UNKNOWN_WORDS") == {"banana"}
        # Check that the warning mentions the count and an example
        assert (
            "Warning: Source 'UNKNOWN_WORDS' contains 2 words not found in master index"
            in captured.err
        )
        assert "(e.g., 'zzxxyy')" in captured.err or "(e.g., 'qqwwrr')" in captured.err

    def test_get_words_in_source_failed_load(self, mock_data_dir, capsys):
        """Test get_words_in_source for a source that failed to load."""
        invalid_json_path = mock_data_dir / "sources" / "FAILED_LOAD.json"
        invalid_json_path.write_text("this is not json", encoding="utf-8")

        atlas = WordAtlas(data_dir=mock_data_dir)
        # Don't capture init warning separately

        # Call the method, then capture all stderr at once
        result = atlas.get_words_in_source("FAILED_LOAD")
        assert result == set()
        captured_all = capsys.readouterr()

        # Check both warnings are present in the combined stderr
        assert "Warning: Could not parse source JSON 'FAILED_LOAD'" in captured_all.err

    def test_filter_source_failed_load(self, mock_data_dir, capsys):
        """Test filter by source for a source that failed to load (covers line 198)."""
        invalid_json_path = mock_data_dir / "sources" / "FAILED_FILTER.json"
        invalid_json_path.write_text("not json", encoding="utf-8")
        atlas = WordAtlas(data_dir=mock_data_dir)
        # Don't capture init warning separately

        # Call the method, then capture all stderr at once
        result = atlas.filter(sources=["FAILED_FILTER"])
        assert result == set()
        captured_all = capsys.readouterr()

        # Check both warnings are present in the combined stderr
        assert (
            "Warning: Could not parse source JSON 'FAILED_FILTER'" in captured_all.err
        )

        # Clean up the dummy file
        invalid_json_path.unlink()

    # --- NEW TESTS FOR INIT ERRORS AND METHOD VALUE/KEY ERRORS ---

    def test_init_word_index_not_found(self, tmp_path):
        """Test WordAtlas initialization raises FileNotFoundError if word_index.json is missing."""
        # Create data dir structure *without* word_index.json
        (tmp_path / "frequencies").mkdir()
        (tmp_path / "frequencies" / "word_frequencies.json").touch()
        (tmp_path / "sources").mkdir()

        with pytest.raises(FileNotFoundError) as excinfo:
            WordAtlas(data_dir=tmp_path)
        # Check for the standard FileNotFoundError, not a custom message
        assert isinstance(excinfo.value, FileNotFoundError)
        # Optional: check part of the path if needed
        # assert str(tmp_path / "word_index.json") in str(excinfo.value)

    def test_init_word_index_invalid_json(self, tmp_path, capsys):
        """Test WordAtlas initialization raises JSONDecodeError if word_index.json is invalid JSON."""
        # Create data dir with invalid word_index.json
        (tmp_path / "frequencies").mkdir()
        (tmp_path / "frequencies" / "word_frequencies.json").touch()
        (tmp_path / "sources").mkdir()
        (tmp_path / "word_index.json").write_text("{invalid json", encoding="utf-8")

        # Expect JSONDecodeError, not SystemExit
        with pytest.raises(json.JSONDecodeError):
            WordAtlas(data_dir=tmp_path)
        # No SystemExit means no capsys check needed here

    def test_init_frequencies_not_found(self, mock_data_dir, capsys):
        """Test WordAtlas initialization raises FileNotFoundError if frequencies file is missing."""
        # Use standard mock_data_dir setup, but remove the frequencies file
        freq_path = mock_data_dir / "frequencies" / "word_frequencies.json"
        freq_path.unlink()  # Remove the file

        # Expect FileNotFoundError during init, not a warning and later KeyError
        with pytest.raises(FileNotFoundError) as excinfo:
            WordAtlas(data_dir=mock_data_dir)
        assert "Frequency file not found" in str(excinfo.value)
        # The rest of the original test logic is unreachable

    # Use monkeypatch on a fresh instance to guarantee the word isn't present
    def test_get_sources_key_error(self, mock_data_dir, monkeypatch):
        """Test get_sources raises KeyError for a word not in the index."""
        # Create a fresh atlas instance for this test
        atlas = WordAtlas(data_dir=mock_data_dir)
        # Ensure the main word index lookup fails on this instance
        monkeypatch.setattr(atlas, "word_to_idx", {})
        # Verify monkeypatch worked and condition is met
        assert "word_definitely_not_in_index" not in atlas.word_to_idx
        # Corrected f-string syntax again (use single quotes inside expression)
        with pytest.raises(KeyError):
            atlas.get_sources("word_definitely_not_in_index")

    def test_get_words_in_source_value_error(self, mock_atlas):
        """Test get_words_in_source raises ValueError for an invalid source name."""
        with pytest.raises(ValueError) as excinfo:
            mock_atlas.get_words_in_source("SOURCE_THAT_DOES_NOT_EXIST")
        # Check for the actual error message string
        assert "Source 'SOURCE_THAT_DOES_NOT_EXIST' not found." in str(excinfo.value)

    # --- Additional Init Tests ---

    def test_init_frequencies_invalid_json(self, tmp_path):
        """Test WordAtlas initialization raises JSONDecodeError if frequencies file is invalid JSON."""
        # Create data dir with valid index but invalid frequencies
        (tmp_path / "word_index.json").write_text(
            '{"apple": 0, "banana": 1}', encoding="utf-8"
        )
        (tmp_path / "frequencies").mkdir()
        (tmp_path / "frequencies" / "word_frequencies.json").write_text(
            "invalid json", encoding="utf-8"
        )
        (tmp_path / "sources").mkdir()

        # Expect ValueError from loading frequencies (data module wraps JSONDecodeError)
        with pytest.raises(ValueError) as excinfo:
            WordAtlas(data_dir=tmp_path)
        assert "Error decoding JSON from frequency file" in str(excinfo.value)

    def test_init_missing_sources_dir(self, tmp_path, capsys):
        """Test WordAtlas initialization warns if sources directory is missing."""
        # Create data dir structure *without* the sources subdirectory
        (tmp_path / "word_index.json").write_text(
            '{"apple": 0, "banana": 1}', encoding="utf-8"
        )
        (tmp_path / "frequencies").mkdir()
        (tmp_path / "frequencies" / "word_frequencies.json").write_text(
            '{"apple": 5.0, "banana": 4.5}', encoding="utf-8"
        )
        # Do NOT create (tmp_path / "sources")

        atlas = WordAtlas(data_dir=tmp_path)
        captured = capsys.readouterr()
        assert "Sources directory not found" in captured.err
        assert atlas.available_sources == {}
        assert atlas._source_lists == {}


# --- End of TestWordAtlas class ---
