"""
Tests for the main entry point of the Word Atlas CLI.
"""

from unittest.mock import patch
import pytest
import runpy
import sys

# Import the main function we are testing
from word_atlas.cli import main


def test_main_import():
    """Test that main can be imported from cli module."""
    from word_atlas.cli import main

    assert callable(main)


def test_main_execution():
    """Test that __main__.py executes main() when run as script."""
    with patch("word_atlas.cli.main") as mock_main:
        # Use runpy to execute __main__.py as if it was run directly
        with patch.object(sys, "argv", ["word_atlas"]):
            runpy.run_module("word_atlas.__main__", run_name="__main__")
        mock_main.assert_called_once()


# --- Tests for command dispatch ---


@patch("word_atlas.cli.info_command")
def test_main_dispatch_info(mock_cmd):
    """Test that main() dispatches to info_command."""
    with patch.object(sys, "argv", ["word_atlas", "info", "testword"]):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.search_command")
def test_main_dispatch_search(mock_cmd):
    """Test that main() dispatches to search_command."""
    with patch.object(sys, "argv", ["word_atlas", "search", "pattern"]):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.stats_command")
def test_main_dispatch_stats(mock_cmd):
    """Test that main() dispatches to stats_command."""
    with patch.object(sys, "argv", ["word_atlas", "stats"]):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.wordlist_create_command")
def test_main_dispatch_wordlist_create(mock_cmd):
    """Test that main() dispatches to wordlist_create_command."""
    with patch.object(
        sys, "argv", ["word_atlas", "wordlist", "create", "--output", "wl.json"]
    ):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.wordlist_modify_command")
def test_main_dispatch_wordlist_modify(mock_cmd):
    """Test that main() dispatches to wordlist_modify_command."""
    with patch.object(
        sys, "argv", ["word_atlas", "wordlist", "modify", "wl.json", "--add", "new"]
    ):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.wordlist_analyze_command")
def test_main_dispatch_wordlist_analyze(mock_cmd):
    """Test that main() dispatches to wordlist_analyze_command."""
    with patch.object(sys, "argv", ["word_atlas", "wordlist", "analyze", "wl.json"]):
        main()
    mock_cmd.assert_called_once()


@patch("word_atlas.cli.wordlist_merge_command")
def test_main_dispatch_wordlist_merge(mock_cmd):
    """Test that main() dispatches to wordlist_merge_command."""
    with patch.object(
        sys,
        "argv",
        [
            "word_atlas",
            "wordlist",
            "merge",
            "wl1.json",
            "wl2.json",
            "--output",
            "merged.json",
        ],
    ):
        main()
    mock_cmd.assert_called_once()


# Test help output branches
def test_main_no_command(capsys):
    """Test main() prints help/error and exits when no command is given."""
    with patch.object(sys, "argv", ["word_atlas"]):
        # Expect SystemExit because argparse exits on required arg error
        with pytest.raises(SystemExit) as e:
            main()
        # Optionally check the exit code
        assert e.value.code == 2 

    # Check that the error message was printed to stderr
    captured = capsys.readouterr()
    assert "usage: word_atlas" in captured.err
    assert "error: the following arguments are required: command" in captured.err


def test_main_wordlist_no_subcommand(capsys):
    """Test main() prints help when 'wordlist' is given with no subcommand."""
    # Argparse might not exit in test context, check stderr
    with patch.object(sys, "argv", ["word_atlas", "wordlist"]):
        main()
    outerr = capsys.readouterr()
    # Check stdout for help text
    assert "usage: word_atlas wordlist" in outerr.out
    assert "{create,modify,analyze,merge}" in outerr.out
