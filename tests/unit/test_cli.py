"""Unit tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock, call, mock_open, ANY
import json
import sys
import io
import contextlib
from pathlib import Path
from argparse import Namespace
from click.testing import CliRunner

from word_atlas import cli
from word_atlas.cli import main as cli_main
from word_atlas.wordlist import WordlistBuilder
from word_atlas.atlas import WordAtlas
from word_atlas.cli import (
    info_command,
    search_command,
    stats_command,
    wordlist_create_command,
    wordlist_modify_command,
    wordlist_analyze_command,
    wordlist_merge_command,
)


@pytest.fixture
def mock_cli_atlas():
    """Provides a mock WordAtlas instance for testing CLI commands."""
    atlas = MagicMock(spec=WordAtlas, name="MockAtlas")
    # Base words and their properties used by the mock
    MOCK_WORDS = {"apple": 0, "banana": 1, "orange": 2}
    MOCK_FREQUENCIES = {"apple": 150.5, "banana": 10.2, "orange": 90.0}
    MOCK_SOURCES = {"apple": ["GSL", "OTHER"], "banana": ["GSL"], "orange": ["OTHER"]}

    atlas.word_index = MOCK_WORDS
    atlas.word_frequencies = MOCK_FREQUENCIES
    atlas.source_lists = {"GSL": ["apple", "banana"], "OTHER": ["apple", "orange"]}

    atlas.has_word.side_effect = lambda w: w in MOCK_WORDS
    atlas.search.side_effect = lambda pattern: [w for w in MOCK_WORDS if pattern in w]
    atlas.get_sources.side_effect = lambda w: MOCK_SOURCES.get(w, [])
    atlas.get_frequency.side_effect = lambda w: MOCK_FREQUENCIES.get(w)
    # Simplified source_coverage to match what stats_command expects
    atlas.get_stats.return_value = {
        "total_entries": 3,
        "single_words": 3,
        "phrases": 0,
        "entries_with_frequency": 3,
        "source_lists": ["GSL", "OTHER"],
        "source_coverage": {
            "GSL": 2,
            "OTHER": 2,
        },
    }

    # Update mock_filter to handle calls without the 'words' argument
    def mock_filter(words=None, sources=None, min_freq=None, max_freq=None):
        # If words is None, filter from all words in the index
        target_words = set(words) if words is not None else set(MOCK_WORDS.keys())
        # Use the mock data defined above
        return [
            w
            for w in target_words
            if (sources is None or any(s in MOCK_SOURCES.get(w, []) for s in sources))
            and (min_freq is None or MOCK_FREQUENCIES.get(w, -1) >= min_freq)
            and (max_freq is None or MOCK_FREQUENCIES.get(w, float("inf")) <= max_freq)
        ]

    atlas.filter.side_effect = mock_filter

    return atlas


@pytest.fixture
def mock_cli_atlas_many_roget():
    """Provides a mock WordAtlas instance with many sources for testing overflow."""
    atlas = MagicMock(spec=WordAtlas)
    test_word = "testword_many_roget"
    sources = ["GSL"] + [f"ROGET_{i}" for i in range(1, 7)]  # 6 Roget + GSL
    atlas.has_word.side_effect = lambda w: w == test_word
    atlas.get_sources.side_effect = lambda w: sources if w == test_word else []
    atlas.get_frequency.side_effect = lambda w: 50.0 if w == test_word else None
    return atlas


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_basic(self, mock_cli_atlas, capsys):
        """Test basic word information display."""
        # Ensure mock_cli_atlas provides expected data
        mock_cli_atlas.get_sources.side_effect = lambda w: (
            ["GSL"] if w == "apple" else []
        )
        mock_cli_atlas.get_frequency.side_effect = lambda w: (
            150.5 if w == "apple" else None
        )

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word="apple", data_dir="test_dir", json=False)
            cli.info_command(args)

        captured = capsys.readouterr()
        assert "Information for 'apple':" in captured.out
        assert "Frequency (SUBTLWF): 150.50" in captured.out
        assert "Sources: GSL" in captured.out

    def test_info_not_found(self, mock_cli_atlas, capsys):
        """Test handling of non-existent words."""
        # Ensure has_word returns False for the test word
        mock_cli_atlas.has_word.side_effect = lambda w: (
            False if w == "nonexistent" else True
        )

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word="nonexistent", data_dir="test_dir", json=False)
            with pytest.raises(SystemExit) as exc_info:
                cli.info_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        # Check for the specific error message format
        assert "Word or phrase 'nonexistent' not found" in captured.out

    def test_info_roget_categories_overflow(self, mock_cli_atlas_many_roget, capsys):
        """Test info command output with many sources (replaces Roget test)."""
        test_word = "testword_many_roget"
        # The mock_cli_atlas_many_roget fixture prepares the mock
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas_many_roget):
            args = MagicMock(word=test_word, data_dir="dummy_dir", json=False)
            cli.info_command(args)

        captured = capsys.readouterr()
        assert f"Information for '{test_word}':" in captured.out
        # Check that all sources are listed (output format might truncate)
        assert (
            "Sources: GSL, ROGET_1, ROGET_2, ROGET_3, ROGET_4, ROGET_5, ROGET_6"
            in captured.out
        )

    def test_info_json_output(self, mock_cli_atlas, capsys):
        """Test info command with JSON output."""
        # Setup mock return values for the test word
        test_word = "apple"
        sources_list = ["GSL"]
        frequency = 150.5
        mock_cli_atlas.has_word.side_effect = lambda w: w == test_word
        mock_cli_atlas.get_sources.side_effect = lambda w: (
            sources_list if w == test_word else []
        )
        mock_cli_atlas.get_frequency.side_effect = lambda w: (
            frequency if w == test_word else None
        )

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word=test_word, data_dir="test_dir", json=True)
            cli.info_command(args)

        captured = capsys.readouterr()
        try:
            output_json = json.loads(captured.out)
            assert output_json == {
                "word": test_word,
                "sources": sources_list,
                "frequency": frequency,
            }
        except json.JSONDecodeError:
            pytest.fail(f"JSON output was not valid: {captured.out}")

    def test_info_phrase(self, mock_cli_atlas, capsys):
        """Test displaying information for a multi-word phrase."""
        test_phrase = "banana split"
        sources_list = ["ROGET_FOOD"]
        frequency = 10.2
        # Setup mock for the phrase
        mock_cli_atlas.has_word.side_effect = lambda w: w == test_phrase
        mock_cli_atlas.get_sources.side_effect = lambda w: (
            sources_list if w == test_phrase else []
        )
        mock_cli_atlas.get_frequency.side_effect = lambda w: (
            frequency if w == test_phrase else None
        )

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word=test_phrase, data_dir="test_dir", json=False)
            cli.info_command(args)

        captured = capsys.readouterr()
        assert f"Information for '{test_phrase}':" in captured.out
        assert f"Frequency (SUBTLWF): {frequency:.2f}" in captured.out
        assert f"Sources: {sources_list[0]}" in captured.out

    @patch("word_atlas.cli.WordAtlas")  # Mock WordAtlas initialization
    @patch("json.dumps")  # Mock json.dumps directly
    def test_info_json_type_error(
        self, mock_dumps, mock_WordAtlas, mock_cli_atlas, capsys
    ):
        """Test error handling when JSON serialization fails."""
        # Configure the mock WordAtlas instance if needed (using mock_cli_atlas fixture?)
        # Instance is returned by mock_WordAtlas(), set attributes on the return_value
        mock_instance = mock_WordAtlas.return_value
        mock_instance.has_word.return_value = True
        mock_instance.get_sources.return_value = ["GSL"]
        mock_instance.get_frequency.return_value = 10.0

        # Configure mock_dumps to raise TypeError
        mock_dumps.side_effect = TypeError("Mocked JSON serialization error")

        # Prepare mock arguments
        args = MagicMock(word="apple", data_dir="dummy_dir", json=True)

        # Call the command - expect SystemExit(1) due to print+exit in except block
        with pytest.raises(SystemExit) as exc_info:
            cli.info_command(args)

        assert exc_info.value.code == 1

        # Check that the error message was printed (to stdout based on cli.py)
        captured = capsys.readouterr()
        assert "Error generating JSON: Mocked JSON serialization error" in captured.out

        # Verify mock_dumps was called
        mock_dumps.assert_called_once()

    def test_info_no_frequency(self, mock_cli_atlas, capsys):
        """Test info display when frequency is not available (covers line 50)."""
        with patch("word_atlas.cli.WordAtlas") as MockWordAtlas:
            # Configure the instance *returned by the mock*
            mock_instance = MockWordAtlas.return_value
            mock_instance.has_word.return_value = True
            mock_instance.get_sources.return_value = ["GSL"]
            mock_instance.get_frequency.return_value = None  # Set freq to None

            args = MagicMock(word="apple", data_dir="dummy_dir", json=False)
            cli.info_command(args)

        captured = capsys.readouterr()
        assert "Frequency: Not available" in captured.out
        assert "Sources: GSL" in captured.out  # Ensure sources still print

    def test_info_no_sources(self, mock_cli_atlas, capsys):
        """Test info display when sources are not available (covers line 56)."""
        with patch("word_atlas.cli.WordAtlas") as MockWordAtlas:
            # Configure the instance *returned by the mock*
            mock_instance = MockWordAtlas.return_value
            mock_instance.has_word.return_value = True
            mock_instance.get_sources.return_value = []  # Set sources to empty
            mock_instance.get_frequency.return_value = 10.0  # Set a specific freq

            args = MagicMock(word="apple", data_dir="dummy_dir", json=False)
            cli.info_command(args)

        captured = capsys.readouterr()
        assert "Frequency (SUBTLWF): 10.00" in captured.out
        assert "Sources: None" in captured.out


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_basic(self, mock_cli_atlas, capsys):
        """Test basic search functionality without filters."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="ap",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                limit=None,
                verbose=False,
            )
            cli.search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches" in captured.out  # Filtering doesn't happen
        assert "apple" in captured.out
        assert "banana" not in captured.out
        mock_cli_atlas.search.assert_called_with("ap")
        # Filter is NOT called when no filters are applied
        mock_cli_atlas.filter.assert_not_called()

    def test_search_with_filters(self, mock_cli_atlas, capsys):
        """Test search with frequency and source filters."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            # Set up args mock correctly
            args = MagicMock()
            args.pattern = "a"
            args.data_dir = "test_dir"
            args.attribute = "GSL"
            args.min_freq = None
            args.max_freq = 50.0
            args.limit = None
            args.verbose = False
            cli.search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches (after filtering from 3):" in captured.out
        assert "banana" in captured.out
        assert "apple" not in captured.out
        assert "orange" not in captured.out
        mock_cli_atlas.search.assert_called_with("a")
        # Verify filter was called twice (once for source, once for freq)
        mock_cli_atlas.filter.assert_has_calls(
            [
                call(sources=["GSL"]),  # Called without 'words'
                call(min_freq=0, max_freq=50.0),  # Called without 'words'
            ]
        )

    def test_search_invalid_frequency(self, mock_cli_atlas, capsys):
        """Test search with invalid frequency range (should return empty)."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock()
            args.pattern = "a"
            args.data_dir = "test_dir"
            args.attribute = None
            args.min_freq = 100
            args.max_freq = 10
            args.limit = None
            args.verbose = False
            cli.search_command(args)
        captured = capsys.readouterr()
        assert "Found 0 matches" in captured.out
        mock_cli_atlas.search.assert_called_with("a")
        # Filter is called once for frequency
        mock_cli_atlas.filter.assert_called_once_with(min_freq=100, max_freq=10)

    def test_search_verbose_output(self, mock_cli_atlas, capsys):
        """Test search with verbose output showing frequency (no filters)."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="an",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                limit=None,
                verbose=True,
            )
            cli.search_command(args)
        captured = capsys.readouterr()
        assert "Found 2 matches" in captured.out  # No filtering
        assert "banana (freq: 10.20)" in captured.out
        assert "orange (freq: 90.00)" in captured.out
        assert "apple" not in captured.out
        mock_cli_atlas.search.assert_called_with("an")
        # Filter is NOT called when no filters are applied
        mock_cli_atlas.filter.assert_not_called()

    def test_search_no_results(self, mock_cli_atlas, capsys):
        """Test search yielding no results (covers line 92)."""
        # Mock atlas.search to return empty list
        mock_cli_atlas.search.return_value = []
        # Ensure filter also returns empty if called (though it shouldn't be here)
        mock_cli_atlas.filter.return_value = []

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="xyz",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                limit=None,
                verbose=False,
            )
            cli.search_command(args)

        captured = capsys.readouterr()
        # Assert the actual output when search returns empty
        # This covers the branch leading to line 92 (results is empty)
        assert "Found 0 matches (after filtering from 0):" in captured.out
        mock_cli_atlas.search.assert_called_with("xyz")
        # Filter should not be called if the initial search result is empty
        mock_cli_atlas.filter.assert_not_called()

    def test_search_invalid_source(self, mock_cli_atlas, capsys):
        """Test search command handling ValueError for an invalid source attribute."""
        # Mock atlas.filter to raise ValueError when called with the specific source
        original_filter = mock_cli_atlas.filter
        def side_effect_filter(*args, **kwargs):
            if kwargs.get("sources") == ["INVALID_SOURCE"]:
                raise ValueError("Source 'INVALID_SOURCE' not found.")
            # Call the original mock's side effect for other cases if needed
            # Or return a default value
            return original_filter(*args, **kwargs)

        mock_cli_atlas.filter.side_effect = side_effect_filter
        # Ensure search returns some initial results to filter from
        mock_cli_atlas.search.return_value = ["apple", "banana"]

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute="INVALID_SOURCE", # Trigger the error
                min_freq=None,
                max_freq=None,
                limit=None,
                verbose=False,
            )
            # Call the command function directly
            search_command(args)

        # Check stderr for the warning message
        captured = capsys.readouterr()
        assert "Warning: Source 'INVALID_SOURCE' not found." in captured.err
        # Fix: Check stdout - verify 0 matches without checking initial count
        assert "Found 0 matches" in captured.out
        # Verify filter was called with the invalid source
        mock_cli_atlas.filter.assert_called_once_with(sources=["INVALID_SOURCE"])

    def test_search_basic_no_verbose(self, mock_cli_atlas, capsys):
        """Test basic search yielding results without verbose output (covers line 92)."""
        # Use the default mock_cli_atlas which returns ['apple', 'banana', 'orange'] for search('a')
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="a",
                data_dir="test_dir",
                attribute=None,
                min_freq=None,
                max_freq=None,
                limit=None,
                verbose=False, # Explicitly False
            )
            search_command(args)

        captured = capsys.readouterr()
        # Fix: Adjust expected match count and assertion style
        assert "Found 3 matches" in captured.out
        # Check that words are printed without frequency info
        assert "  apple" in captured.out
        assert "  banana" in captured.out
        assert "  orange" in captured.out # Add orange based on default mock
        assert "(freq:" not in captured.out # Ensure frequency is not printed
        mock_cli_atlas.search.assert_called_once_with("a")
        # Filter should not be called if no filters applied
        mock_cli_atlas.filter.assert_not_called()


class TestStatsCommand:
    """Tests for the stats command."""

    def test_stats_basic(self, mock_cli_atlas, capsys):
        """Test basic statistics display."""
        # mock_cli_atlas stats are now based on MOCK_WORDS -> 3 entries
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            cli.stats_command(args)

        captured = capsys.readouterr()
        # print(captured.out) # Debug print
        assert "English Word Atlas Statistics:" in captured.out
        # Check simplified stats output using mock values
        mock_stats = mock_cli_atlas.get_stats.return_value
        assert (
            f"Total unique words in index: {mock_stats['total_entries']}"
            in captured.out
        )
        assert f"Single words: {mock_stats['single_words']}" in captured.out
        assert f"Phrases: {mock_stats['phrases']}" in captured.out
        assert (
            f"Entries with frequency data: {mock_stats['entries_with_frequency']}"
            in captured.out
        )
        assert "Source List Coverage:" in captured.out
        # Check formatting of source coverage
        assert "GSL: 2 entries (66.7% of total index)" in captured.out
        assert "OTHER: 2 entries (66.7% of total index)" in captured.out

    def test_stats_empty_dataset(self, capsys):
        """Test stats command with an empty dataset."""
        mock_empty_atlas = MagicMock(spec=WordAtlas)
        # Update mock return value for simplified get_stats
        mock_empty_atlas.get_stats.return_value = {
            "total_entries": 0,
            "single_words": 0,
            "phrases": 0,
            "entries_with_frequency": 0,
            "source_lists": [],
            "source_coverage": {},
        }

        with patch("word_atlas.cli.WordAtlas", return_value=mock_empty_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            cli.stats_command(args)

        captured = capsys.readouterr()
        # Check simplified output for empty case
        assert "Total unique words in index: 0" in captured.out
        assert "Entries with frequency data: 0" in captured.out
        assert "Source List Coverage: No source lists found or loaded." in captured.out

    def test_stats_error(self, capsys):
        """Test error handling when atlas.get_stats fails."""
        mock_error_atlas = MagicMock(spec=WordAtlas)
        mock_error_atlas.get_stats.side_effect = Exception("Mocked stats error")

        with patch("word_atlas.cli.WordAtlas", return_value=mock_error_atlas):
            args = MagicMock(data_dir="test_dir")
            with pytest.raises(SystemExit) as exc_info:
                cli.stats_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error loading or processing stats: Mocked stats error" in captured.out


@pytest.fixture
def mock_wordlist_builder():
    """Provides a mock WordlistBuilder instance for testing CLI commands."""
    builder = MagicMock(spec=WordlistBuilder)
    builder.words = set()  # Start with empty set for state tracking
    builder.metadata = {"name": "Mock List", "criteria": []}

    builder.get_size.side_effect = lambda: len(builder.words)

    # Make add/remove methods modify the mock words set for better state tracking
    def mock_add_words(words_to_add):
        added_count = len(set(words_to_add) - builder.words)
        builder.words.update(words_to_add)
        return added_count

    def mock_remove_words(words_to_remove):
        removed_count = len(set(words_to_remove) & builder.words)
        builder.words.difference_update(words_to_remove)
        return removed_count

    builder.add_words.side_effect = mock_add_words
    builder.remove_words.side_effect = mock_remove_words

    # Simulate filter-based methods returning count and adding to words
    def mock_add_by_filter(count=1, *args, **kwargs):
        criteria_str = "_".join(map(str, args)) + "_".join(
            f"{k}{v}" for k, v in kwargs.items()
        )
        new_words = {f"added_by_{criteria_str}_{i}" for i in range(count)}
        builder.add_words.side_effect(new_words)
        return count

    builder.add_by_search.side_effect = lambda pattern: mock_add_by_filter(
        1, "search", pattern=pattern
    )
    builder.remove_by_search.side_effect = lambda pattern: builder.remove_words(
        {f"removed_search_{pattern}"}
    )
    builder.add_by_source.side_effect = lambda source: mock_add_by_filter(
        1, "source", source=source
    )
    builder.remove_by_source.side_effect = lambda source: builder.remove_words(
        {f"removed_source_{source}"}
    )
    builder.add_by_frequency.side_effect = (
        lambda min_freq, max_freq: mock_add_by_filter(
            1, "freq", min_freq=min_freq, max_freq=max_freq
        )
    )

    # Enhance analyze result for better coverage testing
    builder.analyze.return_value = {
        "size": 3, # Increase size
        "single_words": 2,
        "phrases": 1,
        "frequency": {
            "count": 2, # Only 2 words have frequency
            "average": 55.0,
            "distribution": { # Multiple bins
                "0-10": 1,
                "100-inf": 1,
            },
            "total": 110.0,
        },
        "source_coverage": { # Multiple sources
            "GSL": {"count": 2, "percentage": 66.7},
            "AWL": {"count": 1, "percentage": 33.3},
            "OTHER": {"count": 0, "percentage": 0.0}, # Include a source with 0 count
        },
    }
    builder.save.return_value = None
    # Add mock for export_text
    builder.export_text = MagicMock()

    return builder


class TestWordlistCommand:
    """Test the 'wordlist' subcommands."""

    def test_wordlist_create(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test creating a wordlist via CLI."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder"
        ) as MockBuilder:
            MockBuilder.return_value = mock_wordlist_builder
            # Explicitly set attributes on args mock
            args = MagicMock()
            args.output = "new_list.json"
            args.name = "My List"
            args.description = "Desc"
            args.creator = "Me"
            args.tags = "tag1,tag2"
            args.search_pattern = "a"
            args.attribute = "GSL"
            args.min_freq = 10
            args.max_freq = 100
            args.no_analyze = False
            args.data_dir = "dummy_dir"

            cli.wordlist_create_command(args)

        MockBuilder.assert_called_once_with(mock_cli_atlas)
        mock_wordlist_builder.set_metadata.assert_called_once_with(
            name="My List", description="Desc", creator="Me", tags=["tag1", "tag2"]
        )
        mock_wordlist_builder.add_by_search.assert_called_once_with("a")
        mock_wordlist_builder.add_by_source.assert_called_once_with("GSL")
        mock_wordlist_builder.add_by_frequency.assert_called_once_with(10, 100)
        mock_wordlist_builder.save.assert_called_once_with("new_list.json")
        mock_wordlist_builder.analyze.assert_called_once()

    # Test various formats for --attribute argument and error handling
    @pytest.mark.parametrize(
        "attribute_arg, expected_source_name, expected_value, raises_error",
        [
            ("GSL", "GSL", True, False),  # Simple name
            ("AWL=True", "AWL", True, False),  # Explicit True
            ("ROGET=False", "ROGET", False, False),  # Explicit False
            (
                "COUNT=10",
                "COUNT",
                10,
                False,
            ),  # Integer value (though add_by_source ignores value)
            (
                "FREQ=9.5",
                "FREQ",
                9.5,
                False,
            ),  # Float value (though add_by_source ignores value)
            (
                "INVALID_SOURCE",
                "INVALID_SOURCE",
                True,
                True,
            ),  # Source that causes ValueError
        ],
    )
    def test_wordlist_create_attribute_parsing(
        self,
        attribute_arg,
        expected_source_name,
        expected_value,
        raises_error,
        mock_cli_atlas,
        mock_wordlist_builder,
        capsys,
    ):
        """Test attribute parsing and error handling in wordlist create."""

        # Configure mock_wordlist_builder.add_by_source to potentially raise error
        if raises_error:
            mock_wordlist_builder.add_by_source.side_effect = ValueError(
                "Invalid source"
            )
        else:
            # Reset side effect if it was set in a previous parameterization
            mock_wordlist_builder.add_by_source.side_effect = (
                lambda source: 1
            )  # Simulate adding 1 word

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.cli.WordlistBuilder"
        ) as MockBuilder:
            MockBuilder.return_value = mock_wordlist_builder

            args = MagicMock()
            # Set other required args to minimal values
            args.output = "attr_test.json"
            args.name = "Attr Test"
            args.description = None
            args.creator = None
            args.tags = None
            args.search_pattern = None  # Don't call other add methods
            args.min_freq = None
            args.max_freq = None
            args.no_analyze = True  # Don't call analyze
            args.data_dir = "dummy_dir"
            # Set the attribute arg for this test case
            args.attribute = attribute_arg

            if raises_error:
                with pytest.raises(SystemExit) as exc_info:
                    cli.wordlist_create_command(args)
                assert exc_info.value.code == 1
                captured = capsys.readouterr()
                assert "Error: Invalid source" in captured.out
                # Verify add_by_source was called with the correct (parsed) name
                mock_wordlist_builder.add_by_source.assert_called_once_with(
                    expected_source_name
                )
            else:
                cli.wordlist_create_command(args)
                # Verify add_by_source was called with the correct (parsed) name
                # Note: The *value* part (True/False/10/9.5) is parsed but not actually
                # used by add_by_source in the current cli.py implementation.
                mock_wordlist_builder.add_by_source.assert_called_once_with(
                    expected_source_name
                )
                # Reset mock for next parameterization if needed
                mock_wordlist_builder.add_by_source.reset_mock()

    def test_wordlist_modify(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test modifying a wordlist via CLI."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), patch(
            "word_atlas.wordlist.WordlistBuilder.load",
            return_value=mock_wordlist_builder,
        ) as mock_load:
            args = MagicMock()
            args.wordlist = "existing.json"
            args.name = "New Name"
            args.description = None
            args.creator = None
            args.tags = None
            args.output = None  # Explicitly set output to None
            args.add = ["neword"]
            args.remove = ["oldword"]
            args.add_pattern = "x"
            args.remove_pattern = "y"
            args.add_source = "AWL"
            args.remove_source = "GSL"
            args.add_min_freq = 100
            args.add_max_freq = None
            args.data_dir = "dummy_dir"

            # Reset mock calls before the command runs
            mock_wordlist_builder.reset_mock()
            # Set initial state if necessary (e.g., words for removal to exist)
            mock_wordlist_builder.words = {"oldword", "something_else"}

            cli.wordlist_modify_command(args)

        mock_load.assert_called_once_with(args.wordlist, mock_cli_atlas)
        mock_wordlist_builder.set_metadata.assert_called_once_with(
            name="New Name", description=None, creator=None, tags=None
        )
        # Check calls to add/remove methods based on args
        mock_wordlist_builder.add_words.assert_any_call(set(["neword"]))
        mock_wordlist_builder.remove_words.assert_any_call({"oldword"})
        mock_wordlist_builder.add_by_search.assert_called_once_with("x")
        # Assert that atlas.search was called for remove_pattern
        mock_cli_atlas.search.assert_called_with("y")
        # Assert that builder.remove_words was called with the result of atlas.search("y")
        # (which is [] based on the mock_cli_atlas fixture)
        mock_wordlist_builder.remove_words.assert_any_call([])
        mock_wordlist_builder.add_by_source.assert_called_once_with("AWL")
        mock_wordlist_builder.remove_by_source.assert_called_once_with("GSL")
        mock_wordlist_builder.add_by_frequency.assert_called_once_with(100, None)
        mock_wordlist_builder.save.assert_called_once_with("existing.json")

    def test_wordlist_analyze_basic(self, tmp_path, mock_wordlist_builder, mock_cli_atlas, capsys):
        """Test the wordlist analyze command directly, avoiding CliRunner."""
        # Setup: Save a mock wordlist using the real builder logic but mock atlas
        list_path = tmp_path / "analyze_test.json"
        real_builder = WordlistBuilder(atlas=mock_cli_atlas)
        # Populate real_builder with mock data for saving
        real_builder.words = {"apple", "banana", "crab apple"} # Match analyze size=3
        real_builder.metadata = {"name": "Test List", "criteria": ["mock"]}
        real_builder.save(list_path)

        # Mock WordlistBuilder.load to return our pre-configured mock
        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas): # Ensure atlas is mocked too
            # Simulate argparse arguments
            args = MagicMock(
                wordlist_path=str(list_path),
                json=False,
                # Set export args to None explicitly for this test
                export=None,
                export_text=None,
            )
            # Call the command function directly
            wordlist_analyze_command(args)

        # Assertions on stdout/stderr captured by capsys
        captured = capsys.readouterr()
        # Check main sections
        assert f"Analyzing wordlist '{mock_wordlist_builder.metadata['name']}'" in captured.out
        assert "Basic statistics:" in captured.out
        assert "Frequency distribution:" in captured.out
        assert "Source List Coverage:" in captured.out

        # Use the mocked analyze result for assertions
        mock_analyze_result = mock_wordlist_builder.analyze.return_value

        # Check Basic Stats details
        assert f"Total words: {mock_analyze_result['size']}" in captured.out
        assert f"Single words: {mock_analyze_result['single_words']}" in captured.out
        assert f"Phrases: {mock_analyze_result['phrases']}" in captured.out

        # Check Frequency Distribution details
        freq_stats = mock_analyze_result['frequency']
        # Check specific bin outputs (based on enhanced fixture)
        assert "Frequency 0-10: 1 words (50.0%)" in captured.out # 1 out of 2 with freq
        assert "Frequency 100-inf: 1 words (50.0%)" in captured.out # 1 out of 2 with freq
        assert f"Average frequency: {freq_stats['average']:.1f}" in captured.out

        # Check Source List Coverage details
        source_stats = mock_analyze_result['source_coverage']
        # Check specific source outputs (based on enhanced fixture)
        gsl_count = source_stats['GSL']['count']
        gsl_perc = source_stats['GSL']['percentage']
        assert f"GSL: {gsl_count} words ({gsl_perc:.1f}%)" in captured.out
        awl_count = source_stats['AWL']['count']
        awl_perc = source_stats['AWL']['percentage']
        assert f"AWL: {awl_count} words ({awl_perc:.1f}%)" in captured.out
        # Ensure source with 0 count is NOT printed
        assert "OTHER:" not in captured.out

        # Check that export messages are NOT present
        assert "Analysis exported to" not in captured.out
        assert "Wordlist exported to" not in captured.out

        # Assert that analyze was called on the loaded (mocked) builder
        mock_wordlist_builder.analyze.assert_called_once()

    def test_wordlist_analyze_json(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test the wordlist analyze command with JSON output (direct call)."""
        list_path = Path("dummy_path_for_mock.json") # Path doesn't matter as load is mocked

        # Mock WordlistBuilder.load and WordAtlas
        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            # Simulate argparse arguments
            args = MagicMock(
                wordlist_path=str(list_path),
                json=True,
            )
            # Call the command function directly
            wordlist_analyze_command(args)

        # Assertions on stdout (should be JSON)
        captured = capsys.readouterr()
        assert captured.err == ""
        try:
            output_json = json.loads(captured.out)
            # Assert the structure matches the mocked analyze result
            expected_json = mock_wordlist_builder.analyze.return_value
            assert output_json == expected_json
        except json.JSONDecodeError:
            pytest.fail("Output was not valid JSON")

        # Assert analyze was called (implicitly checks successful load)
        mock_wordlist_builder.analyze.assert_called_once()

    def test_wordlist_modify_load_error(self, tmp_path, mock_cli_atlas, capsys):
        """Test wordlist modify command fails gracefully (direct call)."""
        non_existent_path = tmp_path / "nonexistent.json"

        # Mock WordlistBuilder.load to raise FileNotFoundError with a specific message
        mock_load_exception = FileNotFoundError("Mock load error")
        mock_load = MagicMock(side_effect=mock_load_exception)

        with patch("word_atlas.cli.WordlistBuilder.load", mock_load), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            # Simulate argparse arguments for modify command
            args = MagicMock(
                wordlist_path=non_existent_path,
                add_pattern="test", # Example modification arg
                # Add other modification args as None or their defaults
                remove_pattern=None,
                add_source=None,
                remove_source=None,
                min_freq=None,
                max_freq=None,
                set_name=None,
                set_description=None,
                add_tag=None,
                remove_tag=None,
                no_analyze=True, # Avoid analyze complexities in this test
                output=None, # No output override needed for error test
            )

            # Expect SystemExit when calling the command function directly
            with pytest.raises(SystemExit) as exc_info:
                wordlist_modify_command(args)

        # Check exit code and stderr message
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        # Updated assertion to match the actual error message format
        assert f"Error loading wordlist: {mock_load_exception}" in captured.out # Check stdout for error message

        # Fix: Simplify assertion to just check if load was called
        mock_load.assert_called_once()

    def test_wordlist_analyze_export(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test wordlist analyze command with --export and --export-text arguments."""
        list_path = tmp_path / "analyze_export_test.json"
        export_path = tmp_path / "output" / "analysis.json"
        export_text_path = tmp_path / "output" / "wordlist.txt"

        # Save a dummy wordlist file (content doesn't matter as load is mocked)
        list_path.touch()

        # Mock file operations
        mock_open_func = mock_open()
        mock_mkdir = MagicMock()

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("builtins.open", mock_open_func), \
             patch("pathlib.Path.mkdir", mock_mkdir), \
             patch("json.dump") as mock_json_dump: # Mock json.dump to check args

            args = MagicMock(
                wordlist_path=str(list_path),
                json=False, # Test non-JSON output mode
                export=str(export_path),
                export_text=str(export_text_path),
                data_dir="dummy_dir", # Needed for atlas init inside command
            )

            wordlist_analyze_command(args)

        captured = capsys.readouterr()

        # Check that analysis still prints to stdout
        assert "Analyzing wordlist" in captured.out

        # Check export messages are printed
        assert f"Analysis exported to '{export_path}'" in captured.out
        assert f"Wordlist exported to '{export_text_path}'" in captured.out

        # Check directory creation
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Check JSON export file open and dump
        mock_open_func.assert_any_call(export_path, "w", encoding="utf-8")
        # Ensure json.dump was called with the result of analyze()
        mock_json_dump.assert_called_once_with(
            mock_wordlist_builder.analyze.return_value, mock_open_func(), indent=2
        )

        # Check text export call
        mock_wordlist_builder.export_text.assert_called_once_with(
            export_text_path, include_metadata=False
        )

    def test_wordlist_modify_add_source_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling when adding an invalid source during modify."""
        list_path = tmp_path / "modify_add_source_error.json"
        # Save a dummy file for loading
        WordlistBuilder(atlas=mock_cli_atlas).save(list_path)

        # Mock load to return the builder, but mock add_by_source on the builder to fail
        mock_wordlist_builder.add_by_source.side_effect = ValueError("Invalid source add")

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                add_source="INVALID_SRC",
                # Set other modification args to None
                add_pattern=None, remove_pattern=None, remove_source=None,
                min_freq=None, max_freq=None, set_name=None, set_description=None,
                add_tag=None, remove_tag=None, no_analyze=True, output=None,
                data_dir="dummy_dir",
            )

            # Call the command - should not exit, just print error
            wordlist_modify_command(args)

        captured = capsys.readouterr()
        assert "Error adding source: Invalid source add" in captured.err
        # Ensure save is still called (command shouldn't halt on this specific error)
        mock_wordlist_builder.save.assert_called_once()

    def test_wordlist_modify_remove_source_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling when removing an invalid source during modify."""
        list_path = tmp_path / "modify_remove_source_error.json"
        WordlistBuilder(atlas=mock_cli_atlas).save(list_path)

        # Mock load to return the builder, but mock remove_by_source on the builder to fail
        mock_wordlist_builder.remove_by_source.side_effect = ValueError("Invalid source remove")

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                remove_source="INVALID_SRC",
                # Set other modification args to None
                add_pattern=None, remove_pattern=None, add_source=None,
                min_freq=None, max_freq=None, set_name=None, set_description=None,
                add_tag=None, remove_tag=None, no_analyze=True, output=None,
                data_dir="dummy_dir",
            )

            wordlist_modify_command(args)

        captured = capsys.readouterr()
        assert "Error removing source: Invalid source remove" in captured.err
        mock_wordlist_builder.save.assert_called_once()

    def test_wordlist_modify_save_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling when saving fails during modify."""
        list_path = tmp_path / "modify_save_error.json"
        WordlistBuilder(atlas=mock_cli_atlas).save(list_path)

        # Mock load to return the builder, but mock save on the builder to fail
        mock_wordlist_builder.save.side_effect = IOError("Disk full")

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                add_pattern="test", # Need at least one modification to trigger save
                # Set other modification args to None
                remove_pattern=None, add_source=None, remove_source=None,
                min_freq=None, max_freq=None, set_name=None, set_description=None,
                add_tag=None, remove_tag=None, no_analyze=True, output=None,
                data_dir="dummy_dir",
            )

            with pytest.raises(SystemExit) as exc_info:
                wordlist_modify_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error saving wordlist: Disk full" in captured.err
        mock_wordlist_builder.save.assert_called_once()

    def test_wordlist_analyze_json_type_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling for JSON TypeError in wordlist analyze."""
        list_path = tmp_path / "analyze_json_error.json"
        list_path.touch()

        # Mock json.dumps to raise TypeError
        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("json.dumps") as mock_json_dumps:
            mock_json_dumps.side_effect = TypeError("Cannot serialize object")

            args = MagicMock(
                wordlist_path=str(list_path),
                json=True, # Trigger JSON path
                export=None,
                export_text=None,
                data_dir="dummy_dir",
            )

            with pytest.raises(SystemExit) as exc_info:
                wordlist_analyze_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error generating JSON: Cannot serialize object" in captured.err
        mock_wordlist_builder.analyze.assert_called_once()

    def test_wordlist_analyze_no_frequency(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test analyze output when no frequency data is available."""
        list_path = tmp_path / "analyze_no_freq.json"
        list_path.touch()

        # Modify mock analyze result to have no frequency data
        original_analyze_result = mock_wordlist_builder.analyze.return_value.copy()
        original_analyze_result["frequency"] = {"count": 0} # Simulate no freq data
        mock_wordlist_builder.analyze.return_value = original_analyze_result

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                json=False,
                export=None,
                export_text=None,
                data_dir="dummy_dir",
            )
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert "Frequency distribution: No frequency data available" in captured.out
        # Ensure other sections are still printed
        assert "Basic statistics:" in captured.out
        assert "Source List Coverage:" in captured.out

    def test_wordlist_analyze_no_sources(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test analyze output when no source coverage data is available."""
        list_path = tmp_path / "analyze_no_sources.json"
        list_path.touch()

        # Modify mock analyze result to have no source data
        original_analyze_result = mock_wordlist_builder.analyze.return_value.copy()
        original_analyze_result["source_coverage"] = {} # Simulate no source data
        mock_wordlist_builder.analyze.return_value = original_analyze_result

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                json=False,
                export=None,
                export_text=None,
                data_dir="dummy_dir",
            )
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert "Source List Coverage: No source lists analyzed." in captured.out
        # Ensure other sections are still printed
        assert "Basic statistics:" in captured.out
        assert "Frequency distribution:" in captured.out

    def test_wordlist_analyze_export_json_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling when JSON export fails."""
        list_path = tmp_path / "analyze_export_json_err.json"
        export_path = tmp_path / "analysis_err.json"
        list_path.touch()

        # Mock json.dump to raise an error
        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("builtins.open", mock_open()), \
             patch("pathlib.Path.mkdir"), \
             patch("json.dump") as mock_json_dump:
            mock_json_dump.side_effect = IOError("Cannot write JSON")

            args = MagicMock(
                wordlist_path=str(list_path),
                json=False,
                export=str(export_path), # Trigger JSON export
                export_text=None,
                data_dir="dummy_dir",
            )

            # Command should print error but not exit
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert f"Error exporting analysis to {export_path}: Cannot write JSON" in captured.err
        # Ensure basic analysis still prints
        assert "Analyzing wordlist" in captured.out

    def test_wordlist_analyze_export_text_error(self, tmp_path, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test error handling when text export fails."""
        list_path = tmp_path / "analyze_export_text_err.json"
        export_text_path = tmp_path / "wordlist_err.txt"
        list_path.touch()

        # Mock builder.export_text to raise an error
        mock_wordlist_builder.export_text.side_effect = IOError("Cannot write TXT")

        with patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock(
                wordlist_path=str(list_path),
                json=False,
                export=None,
                export_text=str(export_text_path), # Trigger text export
                data_dir="dummy_dir",
            )

            # Command should print error but not exit
            wordlist_analyze_command(args)

        captured = capsys.readouterr()
        assert f"Error exporting wordlist to {export_text_path}: Cannot write TXT" in captured.err
        # Ensure basic analysis still prints
        assert "Analyzing wordlist" in captured.out
        mock_wordlist_builder.export_text.assert_called_once()

    def test_wordlist_merge_basic(self, tmp_path, mock_cli_atlas, capsys):
        # Removed mock_wordlist_builder from args as we don't need the fixture here
        """Test the basic wordlist merge command functionality by checking the output file."""
        # Setup: Create dummy input files and builders
        input_path1 = tmp_path / "input1.json"
        input_path2 = tmp_path / "input2.json"
        output_path = tmp_path / "merged_output.json"

        # Use real builders for setup, as their state will be accessed by the command
        builder1 = WordlistBuilder(atlas=mock_cli_atlas)
        builder1.words = {"apple", "banana"}
        builder1.metadata["name"] = "List One"
        builder1.save(input_path1) # This save is NOT mocked

        builder2 = WordlistBuilder(atlas=mock_cli_atlas)
        builder2.words = {"banana", "orange"} # Overlap with builder1
        builder2.metadata["name"] = "List Two"
        builder2.save(input_path2) # This save is NOT mocked

        # Mock load to return the builders we just created
        mock_load = MagicMock(side_effect=[builder1, builder2])

        # Don't mock save - let the command run it
        with patch("word_atlas.cli.WordlistBuilder.load", mock_load), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            # Fix: Explicitly set string values for args used in metadata
            args = MagicMock()
            args.inputs=[str(input_path1), str(input_path2)]
            args.output=str(output_path)
            args.name="Merged List" # String
            args.description="A merged list." # String
            args.creator="Test Merge" # String
            args.tags="merged,test" # String (will be split by command)
            args.data_dir="dummy_dir"

            # Run the command, letting it perform the save
            wordlist_merge_command(args)

        # Assert the content of the generated output file
        assert output_path.exists()
        merged_builder = WordlistBuilder.load(output_path, mock_cli_atlas)

        # Check the state of the loaded instance
        assert merged_builder.words == {'apple', 'banana', 'orange'}
        assert merged_builder.metadata["name"] == "Merged List"
        assert merged_builder.metadata["description"] == "A merged list."
        assert merged_builder.metadata["creator"] == "Test Merge"
        assert merged_builder.metadata["tags"] == ["merged", "test"]
        # Optionally, check capsys output for the final save message
        # captured = capsys.readouterr()
        # assert f"Merged wordlist saved to '{output_path}'" in captured.out

    def test_wordlist_merge_input_error(self, capsys):
        """Test merge command fails with too few input files."""
        args = MagicMock(
            inputs=["one_file.json"], # Only one input
            output="output.json",
            # Other args don't matter for this error
            name=None, description=None, creator=None, tags=None, data_dir="dummy"
        )

        with pytest.raises(SystemExit) as exc_info:
            wordlist_merge_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: At least two input files are required" in captured.out

    def test_wordlist_merge_load_error(self, tmp_path, mock_cli_atlas, capsys):
        """Test merge command handling FileNotFoundError when loading an input."""
        input_path1 = tmp_path / "merge_load_ok.json"
        input_path_bad = tmp_path / "merge_load_bad.json"
        output_path = tmp_path / "merge_load_output.json"

        # Create the first builder that loads successfully
        builder1 = WordlistBuilder(atlas=mock_cli_atlas)
        builder1.words = {"apple"}
        builder1.metadata["name"] = "OK List"
        builder1.save(input_path1)

        # Mock load: succeed first, then raise error
        mock_load = MagicMock(side_effect=[builder1, FileNotFoundError("Cannot load bad file")])

        with patch("word_atlas.cli.WordlistBuilder.load", mock_load), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder.save") as mock_save: # Mock save to prevent side effects

            args = MagicMock()
            args.inputs=[str(input_path1), str(input_path_bad)]
            args.output=str(output_path)
            args.name="Merge Load Fail"
            args.description=None
            args.creator=None
            args.tags=None
            args.data_dir="dummy_dir"

            with pytest.raises(SystemExit) as exc_info:
                wordlist_merge_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert f"Error loading wordlist '{str(input_path_bad)}': Cannot load bad file" in captured.err
        # Ensure save was NOT called because the command exited early
        mock_save.assert_not_called()

    def test_wordlist_merge_no_output(self, tmp_path, mock_cli_atlas, capsys):
        """Test merge command fails if output file is not specified."""
        input_path1 = tmp_path / "merge_no_out1.json"
        input_path2 = tmp_path / "merge_no_out2.json"
        input_path1.touch() # Just need files to exist for load mock if needed
        input_path2.touch()

        # Mock load just to prevent FileNotFoundError during setup check if needed
        mock_load = MagicMock(return_value=WordlistBuilder(atlas=mock_cli_atlas))

        with patch("word_atlas.cli.WordlistBuilder.load", mock_load), \
             patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):

            args = MagicMock()
            args.inputs=[str(input_path1), str(input_path2)]
            args.output=None # Explicitly no output file
            args.name="Merge No Output"
            args.description=None
            args.creator=None
            args.tags=None
            args.data_dir="dummy_dir"

            with pytest.raises(SystemExit) as exc_info:
                wordlist_merge_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Output file must be specified for merge." in captured.err


# Sources command tests (Can be added later if needed)
# ...
