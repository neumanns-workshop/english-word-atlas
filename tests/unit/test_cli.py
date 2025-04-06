"""Unit tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path
from argparse import Namespace

from word_atlas.cli import (
    info_command,
    search_command,
    stats_command,
    wordlist_create_command,
    wordlist_modify_command,
    wordlist_analyze_command,
    wordlist_merge_command,
)
from word_atlas.wordlist import WordlistBuilder
from word_atlas.atlas import WordAtlas


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_basic(self, mock_cli_atlas, capsys):
        """Test basic word information display."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="apple", data_dir="test_dir", no_similar=True, json=False
            )
            info_command(args)

        captured = capsys.readouterr()
        assert "Information for 'apple'" in captured.out
        assert "Syllables: 2" in captured.out
        assert "Pronunciation: /['AE1', 'P', 'AH0', 'L']/" in captured.out
        assert "Frequency grade: 5.20" in captured.out
        assert "In wordlists: GSL, NGSL" in captured.out
        assert "Roget categories: 2" in captured.out

    def test_info_not_found(self, mock_cli_atlas, capsys):
        """Test handling of non-existent words."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="nonexistent", data_dir="test_dir", no_similar=True, json=False
            )
            with pytest.raises(SystemExit) as exc_info:
                info_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found in the dataset" in captured.out

    def test_info_with_similar_words(self, capsys):
        """Test displaying similar words."""
        # Configure the mock behaviour specifically for this test
        with patch("word_atlas.cli.WordAtlas") as MockWordAtlas:
            instance_mock = MockWordAtlas.return_value
            instance_mock.has_word.return_value = True  # Need this
            instance_mock.get_word.return_value = {  # Need some data
                "SYLLABLE_COUNT": 2,
                "FREQ_GRADE": 5.0,
                "GSL": True,
            }
            instance_mock.get_similar_words.return_value = [
                ("pear", 0.85),
                ("orange", 0.82),
            ]  # The crucial part

            args = MagicMock(
                word="apple",
                data_dir="test_dir",
                no_similar=False,  # The condition
                json=False,
            )
            info_command(args)

        captured = capsys.readouterr()
        assert "Similar words/phrases:" in captured.out  # Check line 97
        assert "pear: 0.8500" in captured.out  # Check line 100
        assert "orange: 0.8200" in captured.out  # Check line 100

    def test_info_roget_categories_overflow(self, mock_cli_atlas_many_roget, capsys):
        """Test info command output when there are more than 5 Roget categories."""
        # Use the test word configured in the fixture
        test_word = "testword_many_roget"

        # Simulate args
        args = MagicMock(
            word=test_word, data_dir="dummy_dir", no_similar=True, json=False
        )

        # Patching WordAtlas happens implicitly via the fixture
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas_many_roget):
            info_command(args)

        captured = capsys.readouterr()

        # Assertions (fixture provides the necessary word data)
        assert f"Information for '{test_word}'" in captured.out
        assert "Roget categories: 6" in captured.out
        assert "Syllables: 2" in captured.out
        assert "Frequency grade: 5.00" in captured.out
        assert "In wordlists: GSL" in captured.out
        assert "    - ROGET_1" in captured.out
        assert "    - ROGET_2" in captured.out
        assert "    - ROGET_3" in captured.out
        assert "    - ROGET_4" in captured.out
        assert "    - ROGET_5" in captured.out
        assert "    - ... and 1 more" in captured.out  # Check the overflow message

    def test_info_json_output(self, mock_cli_atlas, capsys):
        """Test info command with JSON output."""
        word_data = {
            "SYLLABLE_COUNT": 2,
            "FREQ_GRADE": 1.0,
            "GSL": True,
            "EMBEDDINGS_ALL_MINILM_L6_V2": [0.1, 0.2, 0.3],  # Add embeddings
        }
        mock_cli_atlas.has_word.side_effect = lambda w: True
        mock_cli_atlas.get_word.side_effect = lambda w: word_data.copy()
        mock_cli_atlas.get_similar_words.return_value = []
        mock_cli_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error

        # Mock the WordAtlas instance used by the command
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="test_word", data_dir="test_dir", no_similar=False, json=True
            )
            info_command(args)

        captured = capsys.readouterr()

        # Assert exit code is implicitly 0 (no SystemExit)
        assert "EMBEDDINGS_ALL_MINILM_L6_V2" not in captured.out
        assert "SYLLABLE_COUNT" in captured.out
        assert "FREQ_GRADE" in captured.out
        assert "GSL" in captured.out

    def test_info_phrase(self, mock_cli_atlas, capsys):
        """Test displaying information for a multi-word phrase."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="banana split", data_dir="test_dir", no_similar=True, json=False
            )
            info_command(args)

        captured = capsys.readouterr()
        assert "Information for 'banana split'" in captured.out
        assert "Syllables: 4" in captured.out
        assert (
            "Pronunciation: /['B', 'AH0', 'N', 'AE1', 'N', 'AH0', 'S', 'P', 'L', 'IH1', 'T']/"
            in captured.out
        )
        assert "Frequency grade: 15.80" in captured.out
        assert "Roget categories: 1" in captured.out

    def test_info_invalid_word(self, mock_cli_atlas, capsys):
        """Test info command with invalid word format."""
        mock_cli_atlas.get_word.return_value = None  # Word not found

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="", data_dir="test_dir", no_similar=True, json=False  # Empty word
            )
            with pytest.raises(SystemExit) as exc_info:
                info_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Word or phrase '' not found in the dataset" in captured.out

    def test_info_json_error(self, mock_cli_atlas, capsys):
        """Test info command with JSON encoding error."""
        mock_cli_atlas.has_word.side_effect = lambda w: True
        mock_cli_atlas.get_word.side_effect = lambda w: {
            "key": object()
        }  # object() cannot be JSON serialized
        mock_cli_atlas.get_similar_words.return_value = []
        mock_cli_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                word="test_word", data_dir="test_dir", no_similar=False, json=True
            )
            with pytest.raises(SystemExit) as exc_info:
                info_command(args)

            captured = capsys.readouterr()
            assert (
                "Error: Object of type object is not JSON serializable" in captured.out
            )
            assert exc_info.value.code == 1


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_basic(self, mock_cli_atlas, capsys):
        """Test basic search functionality."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="ap",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches:" in captured.out
        assert "apple" in captured.out

    def test_search_with_filters(self, mock_cli_atlas, capsys):
        """Test search with frequency and attribute filters."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute="GSL=true",
                min_freq=1,
                max_freq=10,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "apple" in captured.out
        assert "freq: 5.2" in captured.out
        assert "banana split" not in captured.out  # Filtered out by GSL=true

    def test_search_phrases_only(self, mock_cli_atlas, capsys):
        """Test searching for phrases only."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=True,
                words_only=False,
                limit=None,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "banana split" in captured.out
        assert "apple" not in captured.out

    def test_search_words_only(self, mock_cli_atlas, capsys):
        """Test searching for single words only."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=True,
                limit=None,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "apple" in captured.out
        assert "banana split" not in captured.out

    def test_search_with_limit(self, mock_cli_atlas, capsys):
        """Test search with result limit."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=1,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        output_lines = [
            line.strip() for line in captured.out.split("\n") if line.strip()
        ]
        assert len(output_lines) == 2  # Header + 1 result
        assert "Found" in output_lines[0]

    def test_search_attribute_exists(self, mock_cli_atlas, capsys):
        """Test searching for words with a specific attribute (existence only)."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute="GSL",  # No value specified
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "apple" in captured.out  # Has GSL=True
        assert "banana split" not in captured.out  # Doesn't have GSL

    def test_search_invalid_frequency(self, mock_cli_atlas, capsys):
        """Test search with invalid frequency range."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute=None,
                min_freq=10,
                max_freq=1,  # Invalid: max < min
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 0 matches" in captured.out

    def test_search_invalid_attribute(self, mock_cli_atlas, capsys):
        """Test search with invalid attribute format."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute="INVALID:true",  # Invalid format, should be =
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 0 matches" in captured.out

    def test_search_no_results(self, mock_cli_atlas, capsys):
        """Test search with no matching results."""
        mock_cli_atlas.search.return_value = set()  # No results

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="nonexistent",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 0 matches" in captured.out

    def test_search_numeric_attribute(self, mock_cli_atlas, capsys):
        """Test search with numeric attribute value."""
        mock_cli_atlas.search.side_effect = lambda pattern: ["word1", "word2"]
        mock_cli_atlas.has_word.side_effect = lambda w: True
        mock_cli_atlas.get_word.side_effect = lambda w: {
            "FREQ_GRADE": float(5) if w == "word1" else float(3)  # Convert to float
        }

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="test",
                data_dir="test_dir",
                attribute="FREQ_GRADE=5.0",  # Use float value
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches:" in captured.out
        assert "word1" in captured.out
        assert "word2" not in captured.out

    def test_search_phrase_filtering(self, mock_cli_atlas, capsys):
        """Test search with phrase filtering."""
        # Define test data
        phrases = ["test phrase", "another phrase"]
        words = ["singleword"]
        all_results = phrases + words

        # Set up mocks
        mock_cli_atlas.search.side_effect = lambda pattern: all_results
        mock_cli_atlas.has_word.side_effect = lambda w: True
        mock_cli_atlas.get_word.side_effect = lambda w: {"FREQ_GRADE": 5}

        # Test phrases only
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="test",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=True,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 2 matches:" in captured.out
        for phrase in phrases:
            assert phrase in captured.out
        assert "singleword" not in captured.out

        # Test words only
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="test",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=True,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches:" in captured.out
        assert "singleword" in captured.out
        for phrase in phrases:
            assert phrase not in captured.out

    def test_search_verbose_output(self, mock_cli_atlas, capsys):
        """Test search with verbose output."""
        test_word = "test"
        word_data = {"FREQ_GRADE": 5.0, "SYLLABLE_COUNT": 1}

        mock_cli_atlas.search.side_effect = lambda pattern: [test_word]
        mock_cli_atlas.has_word.side_effect = lambda w: True
        mock_cli_atlas.get_word.side_effect = lambda w: word_data.copy()

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="test",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=True,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches:" in captured.out
        assert test_word in captured.out
        assert "(freq: 5.0, syl: 1)" in captured.out

    def test_search_attribute_exists_truthy(self, mock_cli_atlas, capsys):
        """Test search filtering by attribute existence and truthiness."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",  # Matches apple and banana split initially
                data_dir="test_dir",
                attribute="GSL",  # Check for GSL existing and being truthy
                min_freq=None,
                max_freq=None,
                phrases_only=False,
                words_only=False,
                limit=None,
                verbose=False,
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches:" in captured.out  # Should only find apple
        assert "apple" in captured.out
        assert "banana split" not in captured.out  # Does not have GSL=True


class TestStatsCommand:
    """Tests for the stats command."""

    def test_stats_basic(self, mock_cli_atlas, capsys):
        """Test basic statistics display."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            stats_command(args)

        captured = capsys.readouterr()
        assert "English Word Atlas Statistics:" in captured.out
        assert "Total entries: 2" in captured.out
        assert "Single words: 1" in captured.out
        assert "Phrases: 1" in captured.out
        assert "Embedding dimensions: 384" in captured.out

    def test_stats_detailed(self, mock_cli_atlas, capsys):
        """Test detailed statistics display."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(data_dir="test_dir", basic=False)
            stats_command(args)

        captured = capsys.readouterr()
        # Basic stats
        assert "English Word Atlas Statistics:" in captured.out
        # Syllable distribution
        assert "Syllable distribution:" in captured.out
        # The actual format is "2 syllable(s): 123"
        assert any(
            line.strip().startswith("2 syllable(s):")
            for line in captured.out.split("\n")
        )
        # Frequency distribution
        assert "Frequency distribution:" in captured.out
        assert any(
            line.strip().startswith("Frequency 1-10:")
            for line in captured.out.split("\n")
        )
        # Wordlist coverage
        assert "Wordlist coverage:" in captured.out
        assert any(line.strip().startswith("GSL:") for line in captured.out.split("\n"))

    def test_stats_empty_dataset(self, capsys):
        """Test stats command with an empty dataset."""
        mock_empty_atlas = MagicMock(spec=WordAtlas)
        mock_empty_atlas.get_stats.return_value = {
            "total_entries": 0,
            "single_words": 0,
            "phrases": 0,
            "embedding_dim": 384,
        }

        with patch("word_atlas.cli.WordAtlas", return_value=mock_empty_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            stats_command(args)

        captured = capsys.readouterr()
        assert "Total entries: 0" in captured.out
        assert "Single words: 0" in captured.out
        assert "Phrases: 0" in captured.out

    def test_stats_data_error(self, capsys):
        """Test stats command with data loading error."""
        mock_error_atlas = MagicMock(spec=WordAtlas)
        mock_error_atlas.get_stats.side_effect = Exception("Data error")
        mock_error_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error
        mock_error_atlas._load_dataset = MagicMock()  # Prevent dataset loading

        with patch("word_atlas.cli.WordAtlas", return_value=mock_error_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            with pytest.raises(SystemExit) as exc_info:
                stats_command(args)

            captured = capsys.readouterr()
            assert "Error: Data error" in captured.out
            assert exc_info.value.code == 1


class TestWordlistCommand:
    """Tests for the wordlist commands."""

    def test_wordlist_create(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test creating a wordlist with basic criteria."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.name = "Test List"
        args.description = "A test wordlist"
        args.creator = "Test User"
        args.tags = "test,demo"
        args.search_pattern = "a"
        args.attribute = None
        args.syllables = None
        args.min_freq = None
        args.max_freq = None
        args.similar_to = None
        args.output = "test_wordlist.json"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            wordlist_create_command(args)

        captured = capsys.readouterr()
        assert "Added 1 words matching pattern 'a'" in captured.out
        mock_wordlist_builder.set_metadata.assert_called_once_with(
            name="Test List",
            description="A test wordlist",
            creator="Test User",
            tags=["test", "demo"],
        )

    def test_wordlist_create_with_multiple_criteria(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test creating a wordlist with multiple search criteria."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.name = "Test List"
        args.description = "A test wordlist"
        args.creator = "Test User"
        args.tags = "test,demo"
        args.search_pattern = "a"
        args.attribute = "GSL=true"
        args.syllables = 2
        args.min_freq = 1
        args.max_freq = 10
        args.similar_to = None
        args.output = "test_wordlist.json"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            wordlist_create_command(args)

        captured = capsys.readouterr()
        assert "Added 1 words matching pattern 'a'" in captured.out
        assert "Added 1 words with attribute GSL=true" in captured.out
        assert "Added 1 words with 2 syllables" in captured.out
        assert "frequency 1-10" in captured.out

        mock_wordlist_builder.add_by_search.assert_called_once_with("a")
        mock_wordlist_builder.add_by_attribute.assert_called_once_with("GSL", True)
        mock_wordlist_builder.add_by_syllable_count.assert_called_once_with(2)
        mock_wordlist_builder.add_by_frequency.assert_called_once_with(1, 10)

    def test_wordlist_create_with_similar_words(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test creating a wordlist with similar words."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.name = "Similar Words List"
        args.description = "Words similar to apple"
        args.creator = "Test User"
        args.tags = "test,similar"
        args.search_pattern = None
        args.attribute = None
        args.syllables = None
        args.min_freq = None
        args.max_freq = None
        args.similar_to = "apple"
        args.similar_count = 10
        args.output = "similar_words.json"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            wordlist_create_command(args)

        captured = capsys.readouterr()
        assert "Added 2 words similar to 'apple'" in captured.out
        mock_wordlist_builder.add_similar_words.assert_called_once_with("apple", 10)

    def test_wordlist_modify_add(self, mock_cli_atlas, mock_wordlist, capsys):
        """Test modifying a wordlist by adding words."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.wordlist = "input_list.json"
        args.output = "modified_list.json"
        args.add = ["apple", "banana split"]
        args.remove = None
        args.name = None
        args.description = None
        args.creator = None
        args.tags = None
        args.add_pattern = None
        args.add_attribute = None
        args.add_similar_to = None
        args.remove_pattern = None

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist
        ):
            wordlist_modify_command(args)

        captured = capsys.readouterr()
        assert "Added 2 words to the wordlist" in captured.out
        mock_wordlist.add_words.assert_called_once_with({"apple", "banana split"})

    def test_wordlist_modify_remove(self, mock_cli_atlas, mock_wordlist, capsys):
        """Test modifying a wordlist by removing words."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.wordlist = "input_list.json"
        args.output = "modified_list.json"
        args.add = None
        args.remove = ["apple"]
        args.name = None
        args.description = None
        args.creator = None
        args.tags = None
        args.add_pattern = None
        args.add_attribute = None
        args.add_similar_to = None
        args.remove_pattern = None

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist
        ):
            wordlist_modify_command(args)

        captured = capsys.readouterr()
        assert "Removed 1 words from the wordlist" in captured.out
        mock_wordlist.remove_words.assert_called_once_with({"apple"})

    def test_wordlist_modify_metadata(self, mock_cli_atlas, mock_wordlist, capsys):
        """Test modifying wordlist metadata."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.wordlist = "input_list.json"
        args.output = "modified_list.json"
        args.add = None
        args.remove = None
        args.name = "Updated List"
        args.description = "Updated description"
        args.creator = "New Creator"
        args.tags = "new,tags"
        args.add_pattern = None
        args.add_attribute = None
        args.add_similar_to = None
        args.remove_pattern = None

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist
        ):
            wordlist_modify_command(args)

        captured = capsys.readouterr()
        assert "Updated wordlist metadata" in captured.out
        mock_wordlist.set_metadata.assert_called_once_with(
            name="Updated List",
            description="Updated description",
            creator="New Creator",
            tags=["new", "tags"],
        )

    def test_wordlist_analyze_basic(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test basic wordlist analysis."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.input = "input_list.json"
        args.json = False
        args.basic = True

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder
        ):
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert "Basic statistics:" in captured.out
        assert "Total words: 2" in captured.out
        assert "Single words: 1" in captured.out
        assert "Phrases: 1" in captured.out

    def test_wordlist_analyze_detailed(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test detailed wordlist analysis."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.input = "input_list.json"
        args.json = False
        args.basic = False

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder
        ):
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        # Basic info
        assert "Basic statistics:" in captured.out
        assert "Total words: 2" in captured.out
        # Syllable distribution
        assert "Syllable distribution:" in captured.out
        assert any(
            line.strip().startswith("2 syllable(s):")
            for line in captured.out.split("\n")
        )
        # Word types
        assert "Single words: 1" in captured.out
        assert "Phrases: 1" in captured.out
        # Frequency distribution
        assert "Frequency distribution:" in captured.out
        assert any(
            line.strip().startswith("Frequency 1-10:")
            for line in captured.out.split("\n")
        )

    def test_wordlist_analyze_json(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test JSON output for wordlist analysis."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.input = "input_list.json"
        args.json = True
        args.basic = False
        args.export = "analysis.json"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder
        ):
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert "Analysis exported to 'analysis.json'" in captured.out

    def test_wordlist_merge(
        self, mock_cli_atlas, mock_wordlist_builder, mock_wordlist, capsys
    ):
        """Test merging multiple wordlists."""
        mock_wordlist1 = mock_wordlist
        mock_wordlist1.metadata = {
            "name": "List 1",
            "description": "First list",
            "creator": "Test User",
            "tags": ["test"],
            "created": "2024-03-20",
            "modified": "2024-03-21",
            "criteria": [],
        }
        mock_wordlist2 = MagicMock(spec=WordlistBuilder)
        mock_wordlist2.words = {"banana split"}
        mock_wordlist2.metadata = {
            "name": "List 2",
            "description": "Second list",
            "creator": "Test User",
            "tags": ["test"],
            "created": "2024-03-20",
            "modified": "2024-03-21",
            "criteria": [],
        }
        mock_wordlist2.get_size.return_value = len(mock_wordlist2.words)
        mock_wordlist2.get_wordlist.return_value = mock_wordlist2.words

        args = MagicMock()
        args.data_dir = "test_dir"
        args.inputs = ["list1.json", "list2.json"]
        args.output = "merged_list.json"
        args.name = "Merged List"
        args.description = "A merged wordlist"
        args.creator = "Test User"
        args.tags = "merged,test"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ), patch(
            "word_atlas.cli.WordlistBuilder.load",
            side_effect=[mock_wordlist1, mock_wordlist2],
        ):
            wordlist_merge_command(args)

        captured = capsys.readouterr()
        assert "Loaded 'List 1' with 2 words" in captured.out
        assert "Added 2 words from 'List 1'" in captured.out
        assert "Loaded 'List 2' with 1 word" in captured.out
        assert "Added 1 words from 'List 2'" in captured.out
        assert "Merged wordlist saved to 'merged_list.json'" in captured.out

    def test_wordlist_merge_with_duplicates(
        self, mock_cli_atlas, mock_wordlist_builder, mock_wordlist, capsys
    ):
        """Test merging wordlists with duplicate words."""
        mock_wordlist1 = mock_wordlist
        mock_wordlist1.metadata = {
            "name": "List 1",
            "description": "First list",
            "creator": "Test User",
            "tags": ["test"],
            "created": "2024-03-20",
            "modified": "2024-03-21",
            "criteria": [],
        }
        mock_wordlist2 = MagicMock(spec=WordlistBuilder)
        mock_wordlist2.words = {"apple", "orange"}
        mock_wordlist2.metadata = {
            "name": "List 2",
            "description": "Second list",
            "creator": "Test User",
            "tags": ["test"],
            "created": "2024-03-20",
            "modified": "2024-03-21",
            "criteria": [],
        }
        mock_wordlist2.get_size.return_value = len(mock_wordlist2.words)
        mock_wordlist2.get_wordlist.return_value = mock_wordlist2.words

        args = MagicMock()
        args.data_dir = "test_dir"
        args.inputs = ["list1.json", "list2.json"]
        args.output = "merged_list.json"
        args.name = "Merged List"
        args.description = "A merged wordlist"
        args.creator = "Test User"
        args.tags = "merged,test"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ), patch(
            "word_atlas.cli.WordlistBuilder.load",
            side_effect=[mock_wordlist1, mock_wordlist2],
        ):
            wordlist_merge_command(args)

        captured = capsys.readouterr()
        assert "Loaded 'List 1' with 2 words" in captured.out
        assert "Added 2 words from 'List 1'" in captured.out
        assert "Loaded 'List 2' with 2 words" in captured.out
        assert "Added 2 words from 'List 2'" in captured.out
        assert "Merged wordlist saved to 'merged_list.json'" in captured.out

    def test_wordlist_create_invalid_criteria(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test creating a wordlist with invalid criteria."""
        mock_wordlist_builder.add_by_attribute.side_effect = ValueError(
            "Invalid attribute"
        )
        mock_cli_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error
        mock_cli_atlas._load_dataset = MagicMock()  # Prevent dataset loading
        mock_cli_atlas._build_indices = MagicMock()  # Prevent index building

        args = MagicMock()
        args.data_dir = "test_dir"
        args.name = "Test List"
        args.description = "A test wordlist"
        args.creator = "Test User"
        args.tags = "test"
        args.search_pattern = None
        args.attribute = "INVALID=true"
        args.syllables = None
        args.min_freq = None
        args.max_freq = None
        args.similar_to = None
        args.output = "test_wordlist.json"
        args.no_analyze = True  # Skip analysis to avoid ARPABET issues

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            with pytest.raises(SystemExit) as exc_info:
                wordlist_create_command(args)

            captured = capsys.readouterr()
            assert "Error: Invalid attribute" in captured.out
            assert exc_info.value.code == 1

    def test_wordlist_modify_file_not_found(self, mock_cli_atlas, capsys):
        """Test modifying a non-existent wordlist file."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.wordlist = "nonexistent.json"
        args.output = "modified_list.json"  # Although it won't be used
        args.add = ["word"]
        args.remove = None
        args.name = None
        args.description = None
        args.creator = None
        args.tags = None

        # Mock the load method to raise FileNotFoundError
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load",
            side_effect=FileNotFoundError("File not found"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                wordlist_modify_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error loading wordlist: File not found" in captured.out

    def test_wordlist_analyze_invalid_file(self, mock_cli_atlas, capsys):
        """Test analyzing a wordlist file that does not exist."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.input = "invalid.json"
        args.json = False
        args.basic = True

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load",
            side_effect=json.JSONDecodeError("Invalid JSON", "", 0),
        ):
            with pytest.raises(SystemExit) as exc_info:
                wordlist_analyze_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error loading wordlist" in captured.out

    def test_wordlist_merge_no_inputs(self, mock_cli_atlas, capsys):
        """Test merging with no input files."""
        mock_cli_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error
        mock_cli_atlas._load_dataset = MagicMock()  # Prevent dataset loading
        mock_cli_atlas._build_indices = MagicMock()  # Prevent index building

        args = MagicMock()
        args.data_dir = "test_dir"
        args.inputs = []
        args.output = "merged_list.json"
        args.name = "Merged List"
        args.description = "A merged wordlist"
        args.creator = "Test User"
        args.tags = "merged,test"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            with pytest.raises(SystemExit) as exc_info:
                wordlist_merge_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: At least two input files are required" in captured.out

    def test_wordlist_merge_invalid_file(self, mock_cli_atlas, capsys):
        """Test merging with an invalid input file."""
        mock_cli_atlas.word_data = {}  # Empty dataset to avoid ARPABET split error
        mock_cli_atlas._load_dataset = MagicMock()  # Prevent dataset loading
        mock_cli_atlas._build_indices = MagicMock()  # Prevent index building

        args = MagicMock()
        args.data_dir = "test_dir"
        args.inputs = ["list1.json", "invalid.json"]
        args.output = "merged_list.json"
        args.name = "Merged List"
        args.description = "A merged wordlist"
        args.creator = "Test User"
        args.tags = "merged,test"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder.load",
            side_effect=[MagicMock(), json.JSONDecodeError("Invalid JSON", "", 0)],
        ):
            with pytest.raises(SystemExit) as exc_info:
                wordlist_merge_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error loading wordlist" in captured.out

    def test_wordlist_create_no_tags(self, mock_cli_atlas, mock_wordlist_builder):
        """Test wordlist create command when no tags are provided."""
        # Use argparse.Namespace for args to avoid MagicMock attribute issues
        args = Namespace(
            name="No Tags List",
            description=None,
            creator=None,
            tags=None,  # Explicitly None
            search_pattern=None,
            attribute=None,
            syllables=None,
            min_freq=None,
            max_freq=None,
            similar_to=None,
            similar_count=None,
            input_file=None,
            output="no_tags_list.json",
            no_analyze=True,
            data_dir="test_dir",
        )

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            wordlist_create_command(args)

        # Now assert the call with the expected literal values
        mock_wordlist_builder.set_metadata.assert_called_with(
            name="No Tags List",
            description=None,
            creator=None,
            tags=[],  # Check tags specifically
        )
        mock_wordlist_builder.save.assert_called_once_with("no_tags_list.json")

    def test_wordlist_create_with_multiple_criteria(
        self, mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test creating a wordlist using multiple criteria."""
        args = MagicMock()
        args.data_dir = "test_dir"
        args.name = "Test List"
        args.description = "A test wordlist"
        args.creator = "Test User"
        args.tags = "test,demo"
        args.search_pattern = "a"
        args.attribute = "GSL=true"
        args.syllables = 2
        args.min_freq = 1
        args.max_freq = 10
        args.similar_to = None
        args.output = "test_wordlist.json"

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder", return_value=mock_wordlist_builder
        ):
            wordlist_create_command(args)

        captured = capsys.readouterr()
        assert "Added 1 words matching pattern 'a'" in captured.out
        assert "Added 1 words with attribute GSL=true" in captured.out
        assert "Added 1 words with 2 syllables" in captured.out
        assert "frequency 1-10" in captured.out

        mock_wordlist_builder.add_by_search.assert_called_once_with("a")
        mock_wordlist_builder.add_by_attribute.assert_called_once_with("GSL", True)
        mock_wordlist_builder.add_by_syllable_count.assert_called_once_with(2)
        mock_wordlist_builder.add_by_frequency.assert_called_once_with(1, 10)
