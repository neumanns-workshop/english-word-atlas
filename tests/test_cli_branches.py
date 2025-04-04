import pytest
import os
import sys
import json
from unittest.mock import patch
from pathlib import Path

from word_atlas.cli import (
    main,
    info_command,
    search_command,
    stats_command,
    wordlist_create_command,
    wordlist_analyze_command,
    wordlist_modify_command,
    wordlist_merge_command,
)
from word_atlas.atlas import WordAtlas

# Import the mock_data_dir fixture from conftest.py
from tests.conftest import mock_data_dir


@pytest.fixture
def atlas(mock_data_dir):
    """Initialize a WordAtlas instance with mock data."""
    return WordAtlas(data_dir=mock_data_dir)


class TestCLIBranches:
    """Test additional branches in the CLI module."""

    def test_search_command_with_attribute(self, atlas, capsys):
        """Test the search command with an attribute filter."""
        args = type(
            "Args",
            (),
            {
                "pattern": "",  # Empty string is a valid pattern
                "attribute": "ROGET_ANIMAL",
                "min_freq": None,
                "max_freq": None,
                "phrases_only": False,
                "words_only": False,
                "limit": None,
                "verbose": True,  # Test verbose output
                "data_dir": atlas.data_dir,
            },
        )

        search_command(args)
        captured = capsys.readouterr()

        assert "Found" in captured.out
        assert "cat" in captured.out
        assert "dog" in captured.out
        assert "elephant" in captured.out
        # With verbose, should show frequency and syllable details
        assert "freq:" in captured.out
        assert "syl:" in captured.out

    def test_search_command_with_frequency(self, atlas, capsys):
        """Test the search command with frequency filters."""
        args = type(
            "Args",
            (),
            {
                "pattern": "",  # Empty string is a valid pattern
                "attribute": None,
                "min_freq": 200,
                "max_freq": 400,
                "phrases_only": False,
                "words_only": False,
                "limit": 5,  # Test limit
                "verbose": False,
                "data_dir": atlas.data_dir,
            },
        )

        search_command(args)
        captured = capsys.readouterr()

        assert "Found" in captured.out
        # Check for words in the expected frequency range
        assert any(word in captured.out for word in ["freedom", "sad"])

    def test_search_command_filtered_by_type(self, atlas, capsys):
        """Test the search command with type filters (phrases/words only)."""
        # Test phrases only
        args_phrases = type(
            "Args",
            (),
            {
                "pattern": "",  # Empty string is a valid pattern
                "attribute": None,
                "min_freq": None,
                "max_freq": None,
                "phrases_only": True,
                "words_only": False,
                "limit": None,
                "verbose": False,
                "data_dir": atlas.data_dir,
            },
        )

        search_command(args_phrases)
        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "good idea" in captured.out

        # Test words only
        args_words = type(
            "Args",
            (),
            {
                "pattern": "",  # Empty string is a valid pattern
                "attribute": None,
                "min_freq": None,
                "max_freq": None,
                "phrases_only": False,
                "words_only": True,
                "limit": None,
                "verbose": False,
                "data_dir": atlas.data_dir,
            },
        )

        search_command(args_words)
        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "apple" in captured.out
        assert "good idea" not in captured.out

    def test_stats_command_basic(self, atlas, capsys):
        """Test the stats command with basic flag."""
        args = type("Args", (), {"basic": True, "data_dir": atlas.data_dir})

        stats_command(args)
        captured = capsys.readouterr()

        assert "English Word Atlas Statistics" in captured.out
        # Basic stats should be shorter and not contain detailed distributions
        assert "Attribute distribution" not in captured.out

    def test_wordlist_create_similar_words(self, atlas, capsys, tmp_path):
        """Test creating a wordlist with similar words."""
        args = type(
            "Args",
            (),
            {
                "name": "Similar Words",
                "description": "Similar words test",
                "creator": "Test User",
                "tags": None,
                "search_pattern": None,
                "attribute": None,
                "syllables": None,
                "min_freq": None,
                "max_freq": None,
                "similar_to": "cat",
                "similar_count": 5,
                "input_file": None,
                "output": str(tmp_path / "similar_output.json"),
                "no_analyze": False,
                "data_dir": atlas.data_dir,
            },
        )

        wordlist_create_command(args)
        captured = capsys.readouterr()

        assert "Added" in captured.out
        assert "words similar to 'cat'" in captured.out
