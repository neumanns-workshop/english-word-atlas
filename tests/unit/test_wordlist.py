"""
Unit tests for the wordlist module.
"""

import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

from word_atlas.wordlist import WordlistBuilder
from word_atlas.atlas import WordAtlas  # Import for type hinting/mocking


class TestWordlistBuilder:
    """Test the WordlistBuilder class (simplified: frequency and sources only)."""

    def test_initialization(self, mock_atlas):
        """Test WordlistBuilder initialization."""
        # Test with existing atlas
        builder = WordlistBuilder(atlas=mock_atlas)
        assert builder.atlas == mock_atlas
        assert len(builder.words) == 0
        assert builder.metadata["name"] == "Custom Wordlist"

        # Test with data_dir (ensure it creates a simplified WordAtlas)
        # This relies on WordAtlas init being correct
        builder_from_dir = WordlistBuilder(data_dir=mock_atlas.data_dir)
        assert builder_from_dir.atlas is not None
        # Check if it has the expected simplified methods
        assert hasattr(builder_from_dir.atlas, "get_frequency")
        assert hasattr(builder_from_dir.atlas, "get_sources")
        assert not hasattr(
            builder_from_dir.atlas, "get_metadata"
        )  # Verify simplification
        assert len(builder_from_dir.words) == 0

    def test_add_words(self, mock_atlas):
        """Test adding words to the wordlist."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test adding existing words
        count = builder.add_words(["apple", "banana"])
        assert count == 2
        assert builder.words == {"apple", "banana"}

        # Test adding non-existent words
        count = builder.add_words(["nonexistent"])
        assert count == 0
        assert "nonexistent" not in builder.words

        # Test adding duplicate words
        count = builder.add_words(["apple"])
        assert count == 0  # Already present, so 0 new words added
        assert len(builder.words) == 2

    def test_add_by_search(self, mock_atlas):
        """Test adding words by search pattern."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test substring search (case-insensitive default)
        count = builder.add_by_search("a")  # apple, banana, orange
        assert count == 3
        assert builder.words == {"apple", "banana", "orange"}

        # Test case-sensitive search
        builder.clear()
        count = builder.add_by_search("Apple", case_sensitive=True)
        assert count == 0  # MOCK_WORDS are lowercase
        builder.clear()
        count = builder.add_by_search("apple", case_sensitive=True)
        assert count == 1
        assert builder.words == {"apple"}

    def test_add_by_source(self, mock_atlas):
        """Test adding words by source list."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test adding by GSL source
        count = builder.add_by_source("GSL")
        assert count == 2  # apple, banana in mock GSL source
        assert builder.words == {"apple", "banana"}
        # Verify the added words are indeed in GSL
        assert all("GSL" in mock_atlas.get_sources(word) for word in builder.words)

        # Test adding by another source (ROGET_PLANT also has apple, banana)
        count = builder.add_by_source("ROGET_PLANT")
        assert count == 0  # Apple and banana already added
        assert len(builder.words) == 2

        # Test adding by OTHER source (orange)
        count = builder.add_by_source("OTHER")
        assert count == 1
        assert builder.words == {"apple", "banana", "orange"}

        # Test adding by a non-existent source
        with pytest.raises(ValueError, match="Source 'INVALID_SOURCE' not found"):
            builder.add_by_source("INVALID_SOURCE")

    def test_add_by_frequency(self, mock_atlas):
        """Test adding words by frequency."""
        builder = WordlistBuilder(atlas=mock_atlas)

        # Test with min frequency (apple=150.5, banana=10.2, orange=90.0 from MOCK_WORDS)
        count = builder.add_by_frequency(min_freq=100.0)
        assert count == 1  # apple
        assert builder.words == {"apple"}

        # Test with max frequency
        builder.clear()
        count = builder.add_by_frequency(max_freq=50.0)
        assert count == 1  # banana
        assert builder.words == {"banana"}

        # Test with both
        builder.clear()
        count = builder.add_by_frequency(min_freq=50.0, max_freq=100.0)
        assert count == 1  # orange
        assert builder.words == {"orange"}

    def test_remove_words(self, mock_atlas):
        """Test removing words from the wordlist."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])

        # Test removing existing words
        count = builder.remove_words(["apple"])
        assert count == 1
        assert builder.words == {"banana"}

        # Test removing non-existent words
        count = builder.remove_words(["nonexistent"])
        assert count == 0
        assert len(builder.words) == 1

        # Test removing already removed words
        count = builder.remove_words(["apple"])
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
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])
        builder.set_metadata(name="Test SaveLoad")
        builder.metadata["criteria"].append(
            {"type": "test", "value": 123}
        )  # Add dummy criteria

        save_path = tmp_path / "test_saveload.json"
        builder.save(save_path)

        # Load the wordlist using the same atlas
        loaded = WordlistBuilder.load(save_path, atlas=mock_atlas)
        assert loaded.words == {"apple", "banana"}
        assert loaded.metadata["name"] == "Test SaveLoad"
        assert loaded.metadata["criteria"] == builder.metadata["criteria"]

    def test_analyze(self, mock_atlas):
        """Test wordlist analysis (simplified)."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])  # Freqs: 150.5, 10.2

        analysis = builder.analyze()
        assert analysis["size"] == 2
        assert analysis["single_words"] == 2
        assert analysis["phrases"] == 0

        # Check frequency stats
        assert "frequency" in analysis
        assert analysis["frequency"]["count"] == 2
        assert analysis["frequency"]["total"] == pytest.approx(150.5 + 10.2)
        assert analysis["frequency"]["average"] == pytest.approx((150.5 + 10.2) / 2)
        # Check frequency distribution based on mock frequencies
        assert analysis["frequency"]["distribution"] == {
            "101-1000": 1,  # apple (150.5)
            "11-100": 1,  # banana (10.2)
        }

        # Check source coverage based on mock setup
        assert "source_coverage" in analysis
        assert analysis["source_coverage"]["GSL"]["count"] == 2
        assert analysis["source_coverage"]["GSL"]["percentage"] == 100.0
        assert analysis["source_coverage"]["ROGET_FOOD"]["count"] == 2
        assert analysis["source_coverage"]["ROGET_PLANT"]["count"] == 2
        assert analysis["source_coverage"]["OTHER"]["count"] == 0
        assert analysis["source_coverage"]["OTHER"]["percentage"] == 0.0

        # Check that removed fields are not present
        assert "syllable_distribution" not in analysis
        assert "metadata_attributes" not in analysis  # Check this just in case

    def test_export_text(self, mock_atlas, tmp_path):
        """Test exporting wordlist to text file."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["banana", "apple"])

        export_path = tmp_path / "test_export.txt"
        builder.export_text(export_path)

        with open(export_path) as f:
            lines = [
                line.strip() for line in f if not line.startswith("#") and line.strip()
            ]
            assert lines == ["apple", "banana"]  # Should be sorted

    def test_remove_by_search(self, mock_atlas):
        """Test removing words by search pattern."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana", "orange"])

        # Case-insensitive default
        count = builder.remove_by_search("a")  # Removes all 3
        assert count == 3
        assert len(builder.words) == 0

        # Case-sensitive
        builder.add_words(["apple", "banana", "orange"])
        count = builder.remove_by_search("Apple", case_sensitive=True)
        assert count == 0
        assert len(builder.words) == 3
        count = builder.remove_by_search("apple", case_sensitive=True)
        assert count == 1
        assert builder.words == {"banana", "orange"}

    def test_remove_by_source(self, mock_atlas):
        """Test removing words by source list."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana", "orange"])

        # Remove by GSL source
        count = builder.remove_by_source("GSL")
        assert count == 2  # apple, banana removed
        assert builder.words == {"orange"}

        # Test removing by a non-existent source
        with pytest.raises(ValueError, match="Source 'INVALID_SOURCE' not found"):
            builder.remove_by_source("INVALID_SOURCE")

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
        # Check structure for empty list
        assert analysis["size"] == 0
        assert analysis["single_words"] == 0
        assert analysis["phrases"] == 0
        assert analysis["frequency"]["count"] == 0
        assert analysis["frequency"]["average"] == 0.0
        assert analysis["frequency"]["distribution"] == {}
        assert "source_coverage" in analysis  # Should exist
        for src_stats in analysis["source_coverage"].values():
            assert src_stats["count"] == 0
            assert src_stats["percentage"] == 0.0

        # Test wordlist with words having no frequency
        builder.add_words(["apple"])  # Has frequency initially
        # Temporarily remove frequency from the MOCK object for this test
        original_freq = mock_atlas.frequencies.pop("apple", None)

        analysis_no_freq = builder.analyze()
        assert analysis_no_freq["frequency"]["count"] == 0
        assert analysis_no_freq["frequency"]["average"] == 0.0
        assert analysis_no_freq["frequency"]["distribution"] == {}

        # Restore frequency if it was removed
        if original_freq is not None:
            mock_atlas.frequencies["apple"] = original_freq

    def test_export_text_edge_cases(self, mock_atlas, tmp_path):
        """Test exporting text file edge cases."""
        builder = WordlistBuilder(atlas=mock_atlas)
        export_path = tmp_path / "empty.txt"

        # Test empty list
        builder.export_text(export_path)
        with open(export_path) as f:
            lines = [
                line.strip() for line in f if not line.startswith("#") and line.strip()
            ]
            assert not lines

        # Test without metadata
        builder.add_words(["apple"])
        builder.export_text(export_path, include_metadata=False)
        with open(export_path) as f:
            content = f.read()
            assert not content.startswith("#")
            assert "apple" in content

    def test_error_handling(self, mock_atlas, tmp_path):
        """Test error handling for load/save."""
        # Test loading non-existent file
        with pytest.raises(FileNotFoundError):
            WordlistBuilder.load("nonexistent.json", atlas=mock_atlas)

        # Test loading invalid JSON
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("this is not json")
        with pytest.raises(ValueError, match="Invalid JSON"):
            WordlistBuilder.load(invalid_json, atlas=mock_atlas)

        # Test loading file with incorrect format
        bad_format = tmp_path / "bad_format.json"
        bad_format.write_text(json.dumps({"wrong_key": []}))
        with pytest.raises(ValueError, match="Invalid wordlist file format"):
            WordlistBuilder.load(bad_format, atlas=mock_atlas)

    def test_size_methods(self, mock_atlas):
        """Test different ways to get wordlist size."""
        builder = WordlistBuilder(atlas=mock_atlas)
        builder.add_words(["apple", "banana"])
        assert len(builder) == 2
        assert builder.get_size() == 2

    def test_save_file_exists_error(self, tmp_path, mock_atlas):
        """Test that save() raises FileExistsError if overwrite=False and file exists."""
        filepath = tmp_path / "existing_list.json"
        filepath.touch()  # Create the file

        builder = WordlistBuilder(atlas=mock_atlas)  # Use real instance with mock atlas
        builder.add_words(["apple"])

        with pytest.raises(FileExistsError):
            builder.save(filepath)  # Default overwrite=False

        # Should succeed with overwrite=True
        builder.save(filepath, overwrite=True)
        assert filepath.exists()

        # Verify that the metadata is saved correctly by accessing the metadata dict
        loaded_builder = WordlistBuilder.load(filepath, atlas=mock_atlas)
        assert loaded_builder.words == {"apple"}
        assert loaded_builder.metadata["name"] == "Custom Wordlist"  # Default name
        assert loaded_builder.metadata["description"] == ""  # Default description
        assert loaded_builder.metadata["creator"] == ""  # Default creator
        assert loaded_builder.metadata["tags"] == []  # Default tags

    def test_load_invalid_json(self, tmp_path, mock_atlas):
        """Test that load() raises ValueError for invalid JSON."""
        filepath = tmp_path / "invalid.json"
        filepath.write_text("this is not valid json", encoding="utf-8")

        # Call load as a classmethod, passing the mock atlas
        with pytest.raises(ValueError) as excinfo:
            WordlistBuilder.load(filepath, atlas=mock_atlas)
        # Update assertion to match actual error message
        assert "Invalid JSON in wordlist file" in str(excinfo.value)

    def test_remove_by_source_invalid_source(self, mock_atlas):
        """Test remove_by_source raises ValueError for an invalid source name."""
        builder = WordlistBuilder(atlas=mock_atlas)  # Use real builder with mock atlas
        builder.add_words(["apple", "banana", "orange"])

        with pytest.raises(ValueError) as excinfo:
            builder.remove_by_source("INVALID_SOURCE_NAME")
        # Update assertion to match actual error message
        assert "Source 'INVALID_SOURCE_NAME' not found" in str(excinfo.value)

    def test_get_wordlist(self, mock_wordlist_builder):
        """Test retrieving the wordlist."""

    def test_init_invalid_atlas_type(self):
        """Test WordlistBuilder init raises TypeError for invalid atlas object."""

        class BadAtlas:
            pass  # Missing required methods

        with pytest.raises(TypeError) as excinfo:
            WordlistBuilder(atlas=BadAtlas())
        assert "Provided atlas object does not have the expected methods" in str(
            excinfo.value
        )

    def test_initialization(self, mock_wordlist_builder):
        """Test basic initialization fixture works."""
        assert mock_wordlist_builder is not None

    def test_add_words(self, mock_wordlist_builder):
        """Test adding words to the wordlist."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

        # Test adding existing words
        count = builder.add_words(["apple", "banana"])
        assert count == 2
        assert builder.words == {"apple", "banana"}

        # Test adding non-existent words
        count = builder.add_words(["nonexistent"])
        assert count == 0
        assert "nonexistent" not in builder.words

        # Test adding duplicate words
        count = builder.add_words(["apple"])
        assert count == 0  # Already present, so 0 new words added
        assert len(builder.words) == 2

    def test_add_by_search(self, mock_wordlist_builder):
        """Test adding words by search pattern."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

        # Test substring search (case-insensitive default)
        count = builder.add_by_search("a")  # apple, banana, orange
        assert count == 3
        assert builder.words == {"apple", "banana", "orange"}

        # Test case-sensitive search
        builder.clear()
        count = builder.add_by_search("Apple", case_sensitive=True)
        assert count == 0  # MOCK_WORDS are lowercase
        builder.clear()
        count = builder.add_by_search("apple", case_sensitive=True)
        assert count == 1
        assert builder.words == {"apple"}

    def test_add_by_source(self, mock_wordlist_builder):
        """Test adding words by source list."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

        # Test adding by GSL source
        count = builder.add_by_source("GSL")
        assert count == 2  # apple, banana in mock GSL source
        assert builder.words == {"apple", "banana"}
        # Verify the added words are indeed in GSL
        assert all(
            "GSL" in mock_wordlist_builder.atlas.get_sources(word)
            for word in builder.words
        )

        # Test adding by another source (ROGET_PLANT also has apple, banana)
        count = builder.add_by_source("ROGET_PLANT")
        assert count == 0  # Apple and banana already added
        assert len(builder.words) == 2

        # Test adding by OTHER source (orange)
        count = builder.add_by_source("OTHER")
        assert count == 1
        assert builder.words == {"apple", "banana", "orange"}

        # Test adding by a non-existent source
        with pytest.raises(ValueError, match="Source 'INVALID_SOURCE' not found"):
            builder.add_by_source("INVALID_SOURCE")

    def test_add_by_frequency(self, mock_wordlist_builder):
        """Test adding words by frequency."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

        # Test with min frequency (apple=150.5, banana=10.2, orange=90.0 from MOCK_WORDS)
        count = builder.add_by_frequency(min_freq=100.0)
        assert count == 1  # apple
        assert builder.words == {"apple"}

        # Test with max frequency
        builder.clear()
        count = builder.add_by_frequency(max_freq=50.0)
        assert count == 1  # banana
        assert builder.words == {"banana"}

        # Test with both
        builder.clear()
        count = builder.add_by_frequency(min_freq=50.0, max_freq=100.0)
        assert count == 1  # orange
        assert builder.words == {"orange"}

    def test_remove_words(self, mock_wordlist_builder):
        """Test removing words from the wordlist."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["apple", "banana"])

        # Test removing existing words
        count = builder.remove_words(["apple"])
        assert count == 1
        assert builder.words == {"banana"}

        # Test removing non-existent words
        count = builder.remove_words(["nonexistent"])
        assert count == 0
        assert len(builder.words) == 1

        # Test removing already removed words
        count = builder.remove_words(["apple"])
        assert count == 0
        assert len(builder.words) == 1

    def test_metadata(self, mock_wordlist_builder):
        """Test metadata management."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

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

    def test_save_and_load(self, mock_wordlist_builder, tmp_path):
        """Test saving and loading wordlists."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["apple", "banana"])
        builder.set_metadata(name="Test SaveLoad")
        builder.metadata["criteria"].append(
            {"type": "test", "value": 123}
        )  # Add dummy criteria

        save_path = tmp_path / "test_saveload.json"
        builder.save(save_path)

        # Load the wordlist using the same atlas
        loaded = WordlistBuilder.load(save_path, atlas=mock_wordlist_builder.atlas)
        assert loaded.words == {"apple", "banana"}
        assert loaded.metadata["name"] == "Test SaveLoad"
        assert loaded.metadata["criteria"] == builder.metadata["criteria"]

    def test_analyze(self, mock_wordlist_builder):
        """Test wordlist analysis (simplified)."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["apple", "banana"])  # Freqs: 150.5, 10.2

        analysis = builder.analyze()
        assert analysis["size"] == 2
        assert analysis["single_words"] == 2
        assert analysis["phrases"] == 0

        # Check frequency stats
        assert "frequency" in analysis
        assert analysis["frequency"]["count"] == 2
        assert analysis["frequency"]["total"] == pytest.approx(150.5 + 10.2)
        assert analysis["frequency"]["average"] == pytest.approx((150.5 + 10.2) / 2)
        # Check frequency distribution based on mock frequencies
        assert analysis["frequency"]["distribution"] == {
            "101-1000": 1,  # apple (150.5)
            "11-100": 1,  # banana (10.2)
        }

        # Check source coverage based on mock setup
        assert "source_coverage" in analysis
        assert analysis["source_coverage"]["GSL"]["count"] == 2
        assert analysis["source_coverage"]["GSL"]["percentage"] == 100.0
        assert analysis["source_coverage"]["ROGET_FOOD"]["count"] == 2
        assert analysis["source_coverage"]["ROGET_PLANT"]["count"] == 2
        assert analysis["source_coverage"]["OTHER"]["count"] == 0
        assert analysis["source_coverage"]["OTHER"]["percentage"] == 0.0

        # Check that removed fields are not present
        assert "syllable_distribution" not in analysis
        assert "metadata_attributes" not in analysis  # Check this just in case

    def test_export_text(self, mock_wordlist_builder, tmp_path):
        """Test exporting wordlist to text file."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["banana", "apple"])

        export_path = tmp_path / "test_export.txt"
        builder.export_text(export_path)

        with open(export_path) as f:
            lines = [
                line.strip() for line in f if not line.startswith("#") and line.strip()
            ]
            assert lines == ["apple", "banana"]  # Should be sorted

    def test_remove_by_search(self, mock_wordlist_builder):
        """Test removing words by search pattern."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["apple", "banana", "orange"])

        # Case-insensitive default
        count = builder.remove_by_search("a")  # Removes all 3
        assert count == 3
        assert len(builder.words) == 0

        # Case-sensitive
        builder.add_words(["apple", "banana", "orange"])
        count = builder.remove_by_search("Apple", case_sensitive=True)
        assert count == 0
        assert len(builder.words) == 3
        count = builder.remove_by_search("apple", case_sensitive=True)
        assert count == 1
        assert builder.words == {"banana", "orange"}

    def test_remove_by_source(self, mock_wordlist_builder):
        """Test removing words by source list."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["apple", "banana", "orange"])

        # Remove by GSL source
        count = builder.remove_by_source("GSL")
        assert count == 2  # apple, banana removed
        assert builder.words == {"orange"}

        # Test removing by a non-existent source
        with pytest.raises(ValueError, match="Source 'INVALID_SOURCE' not found"):
            builder.remove_by_source("INVALID_SOURCE")

    def test_get_wordlist(self, mock_wordlist_builder):
        """Test getting sorted wordlist."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        builder.add_words(["banana", "apple"])

        wordlist = builder.get_wordlist()
        assert isinstance(wordlist, list)
        assert len(wordlist) == 2
        assert wordlist == ["apple", "banana"]  # Should be sorted

    def test_analyze_edge_cases(self, mock_wordlist_builder):
        """Test wordlist analysis edge cases."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)

        # Test empty wordlist
        analysis = builder.analyze()
        # Check structure for empty list
        assert analysis["size"] == 0
        assert analysis["single_words"] == 0
        assert analysis["phrases"] == 0
        assert analysis["frequency"]["count"] == 0
        assert analysis["frequency"]["average"] == 0.0
        assert analysis["frequency"]["distribution"] == {}
        assert "source_coverage" in analysis  # Should exist
        for src_stats in analysis["source_coverage"].values():
            assert src_stats["count"] == 0
            assert src_stats["percentage"] == 0.0

        # Test wordlist with words having no frequency
        builder.add_words(["apple"])  # Has frequency initially
        # Temporarily remove frequency from the MOCK object for this test
        original_freq = mock_wordlist_builder.atlas.frequencies.pop("apple", None)

        analysis_no_freq = builder.analyze()
        assert analysis_no_freq["frequency"]["count"] == 0
        assert analysis_no_freq["frequency"]["average"] == 0.0
        assert analysis_no_freq["frequency"]["distribution"] == {}

        # Restore frequency if it was removed
        if original_freq is not None:
            mock_wordlist_builder.atlas.frequencies["apple"] = original_freq

    def test_export_text_edge_cases(self, mock_wordlist_builder, tmp_path):
        """Test exporting text file edge cases."""
        builder = WordlistBuilder(atlas=mock_wordlist_builder.atlas)
        export_path = tmp_path / "empty.txt"

        # Test empty list
        builder.export_text(export_path)
        with open(export_path) as f:
            lines = [
                line.strip() for line in f if not line.startswith("#") and line.strip()
            ]
            assert not lines

        # Test without metadata
        builder.add_words(["apple"])
        builder.export_text(export_path, include_metadata=False)
        with open(export_path) as f:
            content = f.read()
            assert not content.startswith("#")
            assert "apple" in content

    def test_error_handling(self, mock_wordlist_builder, mock_atlas):
        """Test various error conditions."""

    def test_export_text_formatting_options(self, tmp_path, mock_data_dir):
        """Test export_text with sort_key and word_format options."""
        # Add kiwi to the mock data index for this test
        index_path = mock_data_dir / "word_index.json"
        current_index = json.loads(index_path.read_text())
        current_index["kiwi"] = len(current_index)  # Add kiwi
        index_path.write_text(json.dumps(current_index))

        filepath_sort = tmp_path / "sorted_export.txt"
        filepath_format = tmp_path / "formatted_export.txt"
        filepath_both = tmp_path / "sorted_formatted_export.txt"

        # Use a real atlas and builder for this test
        atlas = WordAtlas(data_dir=mock_data_dir)
        builder = WordlistBuilder(atlas=atlas)
        builder.add_words(["kiwi", "banana", "apple"])  # Add words

        # Verify words are present before export
        assert builder.words == {"kiwi", "banana", "apple"}

        # Test sorting by length
        builder.export_text(filepath_sort, sort_key=len, include_metadata=False)
        content_sort = filepath_sort.read_text(encoding="utf-8").splitlines()
        assert content_sort == [
            "kiwi",
            "apple",
            "banana",
        ]  # kiwi(4), apple(5), banana(6)

        # Test formatting to uppercase
        builder.export_text(
            filepath_format, word_format=str.upper, include_metadata=False
        )
        content_format = filepath_format.read_text(encoding="utf-8").splitlines()
        # Order should be default alphabetical due to set iteration then sorting
        assert content_format == ["APPLE", "BANANA", "KIWI"]

        # Test both
        builder.export_text(
            filepath_both, sort_key=len, word_format=str.upper, include_metadata=False
        )
        content_both = filepath_both.read_text(encoding="utf-8").splitlines()
        assert content_both == ["KIWI", "APPLE", "BANANA"]
