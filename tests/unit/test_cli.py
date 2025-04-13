"""Unit tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock, call
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


@pytest.fixture
def mock_cli_atlas():
    """Provides a mock WordAtlas instance for testing CLI commands."""
    atlas = MagicMock(spec=WordAtlas, name="MockAtlas")
    # Base words and their properties used by the mock
    MOCK_WORDS = {"apple": 0, "banana": 1, "orange": 2}
    MOCK_FREQUENCIES = {"apple": 150.5, "banana": 10.2, "orange": 90.0}
    MOCK_SOURCES = {
        "apple": ["GSL", "OTHER"],
        "banana": ["GSL"],
        "orange": ["OTHER"]
    }

    atlas.word_index = MOCK_WORDS
    atlas.word_frequencies = MOCK_FREQUENCIES
    atlas.source_lists = {
        "GSL": ["apple", "banana"],
        "OTHER": ["apple", "orange"]
    }

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
        }
    }

    # Update mock_filter to handle calls without the 'words' argument
    def mock_filter(words=None, sources=None, min_freq=None, max_freq=None):
        # If words is None, filter from all words in the index
        target_words = set(words) if words is not None else set(MOCK_WORDS.keys())
        # Use the mock data defined above
        return [
            w for w in target_words
            if (sources is None or any(s in MOCK_SOURCES.get(w, []) for s in sources)) and
               (min_freq is None or MOCK_FREQUENCIES.get(w, -1) >= min_freq) and
               (max_freq is None or MOCK_FREQUENCIES.get(w, float('inf')) <= max_freq)
        ]
    atlas.filter.side_effect = mock_filter

    return atlas

@pytest.fixture
def mock_cli_atlas_many_roget():
    """Provides a mock WordAtlas instance with many sources for testing overflow."""
    atlas = MagicMock(spec=WordAtlas)
    test_word = "testword_many_roget"
    sources = ["GSL"] + [f"ROGET_{i}" for i in range(1, 7)] # 6 Roget + GSL
    atlas.has_word.side_effect = lambda w: w == test_word
    atlas.get_sources.side_effect = lambda w: sources if w == test_word else []
    atlas.get_frequency.side_effect = lambda w: 50.0 if w == test_word else None
    return atlas


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_basic(self, mock_cli_atlas, capsys):
        """Test basic word information display."""
        # Ensure mock_cli_atlas provides expected data
        mock_cli_atlas.get_sources.side_effect = lambda w: ["GSL"] if w == "apple" else []
        mock_cli_atlas.get_frequency.side_effect = lambda w: 150.5 if w == "apple" else None

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word="apple", data_dir="test_dir", json=False)
            info_command(args)

        captured = capsys.readouterr()
        assert "Information for 'apple':" in captured.out
        assert "Frequency (SUBTLWF): 150.50" in captured.out
        assert "Sources: GSL" in captured.out

    def test_info_not_found(self, mock_cli_atlas, capsys):
        """Test handling of non-existent words."""
        # Ensure has_word returns False for the test word
        mock_cli_atlas.has_word.side_effect = lambda w: False if w == "nonexistent" else True

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word="nonexistent", data_dir="test_dir", json=False)
            with pytest.raises(SystemExit) as exc_info:
                info_command(args)

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
            info_command(args)

        captured = capsys.readouterr()
        assert f"Information for '{test_word}':" in captured.out
        # Check that all sources are listed (output format might truncate)
        assert "Sources: GSL, ROGET_1, ROGET_2, ROGET_3, ROGET_4, ROGET_5, ROGET_6" in captured.out

    def test_info_json_output(self, mock_cli_atlas, capsys):
        """Test info command with JSON output."""
        # Setup mock return values for the test word
        test_word = "apple"
        sources_list = ["GSL"]
        frequency = 150.5
        mock_cli_atlas.has_word.side_effect = lambda w: w == test_word
        mock_cli_atlas.get_sources.side_effect = lambda w: sources_list if w == test_word else []
        mock_cli_atlas.get_frequency.side_effect = lambda w: frequency if w == test_word else None

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word=test_word, data_dir="test_dir", json=True)
            info_command(args)

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
        mock_cli_atlas.get_sources.side_effect = lambda w: sources_list if w == test_phrase else []
        mock_cli_atlas.get_frequency.side_effect = lambda w: frequency if w == test_phrase else None


        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(word=test_phrase, data_dir="test_dir", json=False)
            info_command(args)

        captured = capsys.readouterr()
        assert f"Information for '{test_phrase}':" in captured.out
        assert f"Frequency (SUBTLWF): {frequency:.2f}" in captured.out
        assert f"Sources: {sources_list[0]}" in captured.out

    @patch('word_atlas.cli.WordAtlas') # Mock WordAtlas initialization
    @patch('json.dumps') # Mock json.dumps directly
    def test_info_json_type_error(self, mock_dumps, mock_WordAtlas, mock_cli_atlas, capsys):
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
             info_command(args)
        
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
            mock_instance.get_frequency.return_value = None # Set freq to None
            
            args = MagicMock(word="apple", data_dir="dummy_dir", json=False)
            info_command(args)
            
        captured = capsys.readouterr()
        assert "Frequency: Not available" in captured.out
        assert "Sources: GSL" in captured.out # Ensure sources still print

    def test_info_no_sources(self, mock_cli_atlas, capsys):
        """Test info display when sources are not available (covers line 56)."""
        with patch("word_atlas.cli.WordAtlas") as MockWordAtlas:
            # Configure the instance *returned by the mock*
            mock_instance = MockWordAtlas.return_value
            mock_instance.has_word.return_value = True
            mock_instance.get_sources.return_value = [] # Set sources to empty
            mock_instance.get_frequency.return_value = 10.0 # Set a specific freq
            
            args = MagicMock(word="apple", data_dir="dummy_dir", json=False)
            info_command(args)
            
        captured = capsys.readouterr()
        assert "Frequency (SUBTLWF): 10.00" in captured.out
        assert "Sources: None" in captured.out


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_basic(self, mock_cli_atlas, capsys):
        """Test basic search functionality without filters."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="ap", data_dir="test_dir", attribute=None,
                min_freq=None, max_freq=None, limit=None, verbose=False
            )
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches" in captured.out # Filtering doesn't happen
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
            search_command(args)

        captured = capsys.readouterr()
        assert "Found 1 matches (after filtering from 3):" in captured.out
        assert "banana" in captured.out
        assert "apple" not in captured.out
        assert "orange" not in captured.out
        mock_cli_atlas.search.assert_called_with("a")
        # Verify filter was called twice (once for source, once for freq)
        mock_cli_atlas.filter.assert_has_calls([
            call(sources=['GSL']), # Called without 'words'
            call(min_freq=0, max_freq=50.0) # Called without 'words'
        ])


    def test_search_invalid_frequency(self, mock_cli_atlas, capsys):
        """Test search with invalid frequency range (should return empty)."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock()
            args.pattern="a"
            args.data_dir="test_dir"
            args.attribute=None
            args.min_freq=100
            args.max_freq=10
            args.limit=None
            args.verbose=False
            search_command(args)
        captured = capsys.readouterr()
        assert "Found 0 matches" in captured.out
        mock_cli_atlas.search.assert_called_with("a")
        # Filter is called once for frequency
        mock_cli_atlas.filter.assert_called_once_with(min_freq=100, max_freq=10)


    def test_search_verbose_output(self, mock_cli_atlas, capsys):
        """Test search with verbose output showing frequency (no filters)."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(
                pattern="an", data_dir="test_dir", attribute=None,
                min_freq=None, max_freq=None, limit=None, verbose=True
            )
            search_command(args)
        captured = capsys.readouterr()
        assert "Found 2 matches" in captured.out # No filtering
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
                pattern="xyz", data_dir="test_dir", attribute=None,
                min_freq=None, max_freq=None, limit=None, verbose=False
            )
            search_command(args)

        captured = capsys.readouterr()
        # Assert the actual output when search returns empty
        # This covers the branch leading to line 92 (results is empty)
        assert "Found 0 matches (after filtering from 0):" in captured.out
        mock_cli_atlas.search.assert_called_with("xyz")
        # Filter should not be called if the initial search result is empty
        mock_cli_atlas.filter.assert_not_called() 


class TestStatsCommand:
    """Tests for the stats command."""

    def test_stats_basic(self, mock_cli_atlas, capsys):
        """Test basic statistics display."""
        # mock_cli_atlas stats are now based on MOCK_WORDS -> 3 entries
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            stats_command(args)

        captured = capsys.readouterr()
        # print(captured.out) # Debug print
        assert "English Word Atlas Statistics:" in captured.out
        # Check simplified stats output using mock values
        mock_stats = mock_cli_atlas.get_stats.return_value
        assert f"Total unique words in index: {mock_stats['total_entries']}" in captured.out
        assert f"Single words: {mock_stats['single_words']}" in captured.out
        assert f"Phrases: {mock_stats['phrases']}" in captured.out
        assert f"Entries with frequency data: {mock_stats['entries_with_frequency']}" in captured.out
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
            "source_coverage": {}
        }

        with patch("word_atlas.cli.WordAtlas", return_value=mock_empty_atlas):
            args = MagicMock(data_dir="test_dir", basic=True)
            stats_command(args)

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
                stats_command(args)
                
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error loading or processing stats: Mocked stats error" in captured.out


@pytest.fixture
def mock_wordlist_builder():
    """Provides a mock WordlistBuilder instance for testing CLI commands."""
    builder = MagicMock(spec=WordlistBuilder)
    builder.words = set() # Start with empty set for state tracking
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
        # Use the criteria to generate somewhat unique words
        criteria_str = "_".join(map(str, args)) + "_".join(f"{k}{v}" for k, v in kwargs.items())
        new_words = {f"added_by_{criteria_str}_{i}" for i in range(count)}
        # Call the side_effect directly to update internal state
        builder.add_words.side_effect(new_words)
        return count # Return the count as the original methods do

    builder.add_by_search.side_effect = lambda pattern: mock_add_by_filter(1, 'search', pattern=pattern)
    builder.remove_by_search.side_effect = lambda pattern: builder.remove_words({f"removed_search_{pattern}"}) # Simulate removal
    builder.add_by_source.side_effect = lambda source: mock_add_by_filter(1, 'source', source=source)
    builder.remove_by_source.side_effect = lambda source: builder.remove_words({f"removed_source_{source}"}) # Simulate removal
    builder.add_by_frequency.side_effect = lambda min_freq, max_freq: mock_add_by_filter(1, 'freq', min_freq=min_freq, max_freq=max_freq)

    # Simplified analyze result based on *potential* mock state (might need test-specific overrides)
    builder.analyze.return_value = {
        "size": 1,
        "single_words": 1,
        "phrases": 0,
        "frequency": {"count": 1, "average": 10.0, "distribution": {"0-10": 1}, "total": 10.0},
        "source_coverage": {"GSL": {"count": 1, "percentage": 100.0}}
    }
    builder.save.return_value = None
    # REMOVED global patch of WordlistBuilder.load
    # WordlistBuilder.load = MagicMock(return_value=builder)

    return builder

class TestWordlistCommand:
    """Test the 'wordlist' subcommands."""

    def test_wordlist_create(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test creating a wordlist via CLI."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder") as MockBuilder:
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

            wordlist_create_command(args)

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
            ("GSL", "GSL", True, False), # Simple name
            ("AWL=True", "AWL", True, False), # Explicit True
            ("ROGET=False", "ROGET", False, False), # Explicit False
            ("COUNT=10", "COUNT", 10, False), # Integer value (though add_by_source ignores value)
            ("FREQ=9.5", "FREQ", 9.5, False), # Float value (though add_by_source ignores value)
            ("INVALID_SOURCE", "INVALID_SOURCE", True, True), # Source that causes ValueError
        ]
    )
    def test_wordlist_create_attribute_parsing(
        self, attribute_arg, expected_source_name, expected_value, raises_error,
        mock_cli_atlas, mock_wordlist_builder, capsys
    ):
        """Test attribute parsing and error handling in wordlist create."""
        
        # Configure mock_wordlist_builder.add_by_source to potentially raise error
        if raises_error:
            mock_wordlist_builder.add_by_source.side_effect = ValueError("Invalid source")
        else:
            # Reset side effect if it was set in a previous parameterization
            mock_wordlist_builder.add_by_source.side_effect = lambda source: 1 # Simulate adding 1 word
            
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder") as MockBuilder:
            MockBuilder.return_value = mock_wordlist_builder
            
            args = MagicMock()
            # Set other required args to minimal values
            args.output = "attr_test.json"
            args.name = "Attr Test"
            args.description = None
            args.creator = None
            args.tags = None
            args.search_pattern = None # Don't call other add methods
            args.min_freq = None
            args.max_freq = None
            args.no_analyze = True # Don't call analyze
            args.data_dir = "dummy_dir"
            # Set the attribute arg for this test case
            args.attribute = attribute_arg
            
            if raises_error:
                with pytest.raises(SystemExit) as exc_info:
                    wordlist_create_command(args)
                assert exc_info.value.code == 1
                captured = capsys.readouterr()
                assert "Error: Invalid source" in captured.out
                # Verify add_by_source was called with the correct (parsed) name
                mock_wordlist_builder.add_by_source.assert_called_once_with(expected_source_name)
            else:
                wordlist_create_command(args)
                # Verify add_by_source was called with the correct (parsed) name
                # Note: The *value* part (True/False/10/9.5) is parsed but not actually
                # used by add_by_source in the current cli.py implementation.
                mock_wordlist_builder.add_by_source.assert_called_once_with(expected_source_name)
                # Reset mock for next parameterization if needed
                mock_wordlist_builder.add_by_source.reset_mock()

    def test_wordlist_modify(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test modifying a wordlist via CLI."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.wordlist.WordlistBuilder.load", return_value=mock_wordlist_builder) as mock_load:
            args = MagicMock()
            args.wordlist="existing.json"
            args.name="New Name"
            args.description=None
            args.creator=None
            args.tags=None
            args.output=None # Explicitly set output to None
            args.add=["neword"]
            args.remove=["oldword"]
            args.add_pattern="x"
            args.remove_pattern="y"
            args.add_source="AWL"
            args.remove_source="GSL"
            args.add_min_freq=100
            args.add_max_freq=None
            args.data_dir="dummy_dir"

            # Reset mock calls before the command runs
            mock_wordlist_builder.reset_mock()
            # Set initial state if necessary (e.g., words for removal to exist)
            mock_wordlist_builder.words = {"oldword", "something_else"}

            wordlist_modify_command(args)

        mock_load.assert_called_once_with("existing.json", mock_cli_atlas)
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

    def test_wordlist_analyze_basic(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test basic analysis output."""
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder) as mock_load:
            mock_stats = mock_wordlist_builder.analyze.return_value
            args = MagicMock()
            args.wordlist="wl.json"
            args.json=False
            args.data_dir="dummy_dir"
            args.export=None # Ensure export args are None if not used
            args.export_text=None

            wordlist_analyze_command(args)

        mock_load.assert_called_once_with("wl.json", mock_cli_atlas)
        captured = capsys.readouterr()
        # Adjust assertion to match expected text output structure
        assert "Analyzing wordlist 'Mock List'" in captured.out
        assert "Basic statistics:" in captured.out
        assert f"Total words: {mock_stats['size']}" in captured.out
        assert "Source List Coverage:" in captured.out
        assert "GSL: 1 words (100.0%)" in captured.out
        # Check that export messages are NOT present
        assert "Analysis exported to" not in captured.out
        assert "Wordlist exported to" not in captured.out

    def test_wordlist_analyze_json(self, mock_cli_atlas, mock_wordlist_builder, capsys):
        """Test analysis JSON output."""
        # Use patch context manager for WordlistBuilder.load
        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder.load", return_value=mock_wordlist_builder) as mock_load:
            mock_stats = mock_wordlist_builder.analyze.return_value

            args = MagicMock(wordlist="wl.json", json=True, data_dir="dummy_dir")
            wordlist_analyze_command(args)

        mock_load.assert_called_once_with("wl.json", mock_cli_atlas)
        captured = capsys.readouterr()
        # Keep assertions, but note the test might still fail if cli.py prints extra text
        try:
            output_json = json.loads(captured.out)
            assert output_json == mock_stats
        except json.JSONDecodeError:
            pytest.fail(f"JSON output was not valid: {captured.out}")

    def test_wordlist_merge(self, mock_cli_atlas, mock_wordlist_builder, capsys, tmp_path):
        """Test merging wordlists via CLI."""
        input1_builder = MagicMock(spec=WordlistBuilder)
        input1_builder.words = {"apple", "banana"}
        input1_builder.metadata = {"name": "List 1", "criteria": []}
        input2_builder = MagicMock(spec=WordlistBuilder)
        input2_builder.words = {"banana", "orange"}
        input2_builder.metadata = {"name": "List 2", "criteria": []}

        with patch("word_atlas.cli.WordAtlas", return_value=mock_cli_atlas), \
             patch("word_atlas.cli.WordlistBuilder") as MockBuilder, \
             patch("word_atlas.cli.WordlistBuilder.load", side_effect=[input1_builder, input2_builder]) as mock_load:

            mock_wordlist_builder.words = set()
            # Ensure the mock returned by MockBuilder() has the save method mocked
            mock_returned_builder = MagicMock(spec=WordlistBuilder)
            mock_returned_builder.words = set() # Give it its own word set
            mock_returned_builder.metadata = {"criteria": []} # Initialize criteria key
            # Define add_words side effect for the returned builder
            def mock_returned_add_words(words_to_add):
                added_count = len(set(words_to_add) - mock_returned_builder.words)
                mock_returned_builder.words.update(words_to_add)
                return added_count # Return count
            mock_returned_builder.add_words.side_effect = mock_returned_add_words
            # Define set_metadata side effect for the returned builder
            def mock_returned_set_metadata(name=None, description=None, creator=None, tags=None):
                if name is not None: mock_returned_builder.metadata["name"] = name
                if description is not None: mock_returned_builder.metadata["description"] = description
                if creator is not None: mock_returned_builder.metadata["creator"] = creator
                if tags is not None: mock_returned_builder.metadata["tags"] = tags # Check for None, not truthiness
                # Update criteria if needed (though not strictly necessary for this test)
                # mock_returned_builder.metadata["criteria"] = [] # Reset criteria
            mock_returned_builder.set_metadata.side_effect = mock_returned_set_metadata
            MockBuilder.return_value = mock_returned_builder

            output_path = tmp_path / "merged.json"
            args = MagicMock()
            args.inputs=["list1.json", "list2.json"]
            args.output=str(output_path)
            args.name="Merged"
            args.description=None
            args.creator=None
            args.tags=None
            args.data_dir="dummy_dir"

            wordlist_merge_command(args)

        MockBuilder.assert_called_once_with(mock_cli_atlas)
        mock_load.assert_has_calls([
            call("list1.json", mock_cli_atlas),
            call("list2.json", mock_cli_atlas)
        ], any_order=False)

        # Check metadata was set correctly on the *returned* builder
        mock_returned_builder.set_metadata.assert_called_once_with(
            name="Merged", description=None, creator=None, tags=[] # tags=None becomes []
        )
        # Check the final state of the merged words set on the *returned* builder
        assert mock_returned_builder.words == {"apple", "banana", "orange"}
        # Check metadata was set correctly on the *returned* builder
        assert mock_returned_builder.metadata["name"] == "Merged"
        assert mock_returned_builder.metadata["tags"] == [] # Tags=None becomes []

        # Check save was called on the *returned* builder
        mock_returned_builder.save.assert_called_once_with(str(output_path))
