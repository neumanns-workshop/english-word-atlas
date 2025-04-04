"""
Tests for the CLI interface of the Word Atlas.
"""

import json
import os
import tempfile
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from word_atlas.cli import info_command, search_command, stats_command, main
from word_atlas.cli import wordlist_create_command, wordlist_analyze_command, wordlist_modify_command, wordlist_merge_command


class TestCLI:
    """Tests for the CLI module."""
    
    def test_info_command(self, atlas, capsys):
        """Test the info command."""
        args = type('Args', (), {
            'word': 'apple',
            'no_similar': False,
            'json': False,
            'data_dir': atlas.data_dir
        })
        
        info_command(args)
        captured = capsys.readouterr()
        
        assert "Information for 'apple'" in captured.out
        assert "Syllables:" in captured.out
        assert "Pronunciation:" in captured.out
        assert "Similar words" in captured.out
    
    def test_search_command(self, atlas, capsys):
        """Test the search command."""
        args = type('Args', (), {
            'pattern': 'a',
            'attribute': None,
            'min_freq': None,
            'max_freq': None,
            'phrases_only': False,
            'words_only': False,
            'limit': None,
            'verbose': False,
            'data_dir': atlas.data_dir
        })
        
        search_command(args)
        captured = capsys.readouterr()
        
        assert "Found" in captured.out
        assert "apple" in captured.out
    
    def test_stats_command(self, atlas, capsys):
        """Test the stats command."""
        args = type('Args', (), {
            'basic': False,
            'data_dir': atlas.data_dir
        })
        
        stats_command(args)
        captured = capsys.readouterr()
        
        assert "English Word Atlas Statistics" in captured.out
        assert "Total entries:" in captured.out
        assert "Syllable distribution:" in captured.out
    
    def test_main_no_args(self, capsys):
        """Test the main function with no arguments."""
        with patch.object(sys, 'argv', ['word_atlas']):
            main()
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out
    
    def test_main_with_info_command(self, atlas, capsys):
        """Test the main function with info command."""
        with patch.object(sys, 'argv', ['word_atlas', 'info', 'apple', '--no-similar']):
            with patch('word_atlas.cli.WordAtlas', return_value=atlas):
                main()
        
        captured = capsys.readouterr()
        assert "Information for 'apple'" in captured.out
    
    def test_wordlist_create_command(self, atlas, capsys, tmp_path):
        """Test the wordlist create command."""
        # Create a test file with words
        word_file = tmp_path / "words.txt"
        with open(word_file, 'w') as f:
            f.write("apple\nbanana\ncat\ndog\n")
        
        args = type('Args', (), {
            'name': "Test Wordlist",
            'description': "Test description",
            'creator': "Test User",
            'tags': "test,sample",
            'search_pattern': None,
            'attribute': "GSL",  # Use General Service List attribute
            'syllables': None,
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': None,
            'output': str(tmp_path / "output.json"),
            'no_analyze': False,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(args)
        captured = capsys.readouterr()
        
        # Check output messages
        assert "Added" in captured.out
        assert "words with attribute GSL" in captured.out
        assert "Wordlist saved to" in captured.out
        
        # Check that the output file was created
        assert (tmp_path / "output.json").exists()
        
        # Check file contents
        with open(tmp_path / "output.json", 'r') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "words" in data
            assert data["metadata"]["name"] == "Test Wordlist"
            assert len(data["words"]) > 0
    
    def test_wordlist_create_from_file(self, atlas, capsys, tmp_path):
        """Test creating a wordlist from an input file."""
        # Create a test file with words
        word_file = tmp_path / "words.txt"
        with open(word_file, 'w') as f:
            f.write("apple\nbanana\ncat\ndog\n")
        
        args = type('Args', (), {
            'name': "File-based Wordlist",
            'description': "Created from file",
            'creator': "Test User",
            'tags': None,
            'search_pattern': None,
            'attribute': None,
            'syllables': None,
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': str(word_file),  # Convert Path to string
            'output': str(tmp_path / "file_output.json"),  # Convert Path to string
            'no_analyze': True,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(args)
        captured = capsys.readouterr()
        
        # Check output messages
        assert "Added" in captured.out
        assert "words from" in captured.out
        assert "Wordlist saved to" in captured.out
        
        # Check that the output file was created
        assert (tmp_path / "file_output.json").exists()
    
    def test_wordlist_analyze_command(self, atlas, capsys, tmp_path):
        """Test the wordlist analyze command."""
        # First create a wordlist
        create_args = type('Args', (), {
            'name': "Analyze Test",
            'description': "For analysis",
            'creator': "Test User",
            'tags': None,
            'search_pattern': None,
            'attribute': "GSL",
            'syllables': None,
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': None,
            'output': str(tmp_path / "analyze_test.json"),
            'no_analyze': True,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(create_args)
        
        # Now analyze it
        analyze_args = type('Args', (), {
            'wordlist': str(tmp_path / "analyze_test.json"),
            'export': str(tmp_path / "analysis.json"),
            'export_text': str(tmp_path / "wordlist.txt"),
            'data_dir': atlas.data_dir
        })
        
        wordlist_analyze_command(analyze_args)
        captured = capsys.readouterr()
        
        # Check output messages
        assert "Analyzing wordlist" in captured.out
        assert "Basic statistics:" in captured.out
        assert "Analysis exported to" in captured.out
        assert "Wordlist exported to" in captured.out
        
        # Check that the output files were created
        assert (tmp_path / "analysis.json").exists()
        assert (tmp_path / "wordlist.txt").exists()
    
    def test_wordlist_modify_command(self, atlas, capsys, tmp_path):
        """Test the wordlist modify command."""
        # First create a wordlist
        create_args = type('Args', (), {
            'name': "Modify Test",
            'description': "For modification",
            'creator': "Test User",
            'tags': None,
            'search_pattern': None,
            'attribute': "GSL",
            'syllables': None,
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': None,
            'output': str(tmp_path / "modify_test.json"),
            'no_analyze': True,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(create_args)
        
        # Now modify it
        modify_args = type('Args', (), {
            'wordlist': str(tmp_path / "modify_test.json"),
            'name': "Modified Wordlist",
            'description': "After modification",
            'creator': None,
            'tags': "modified,test",
            'add_pattern': None,
            'add_attribute': None,
            'add_similar_to': "dog",
            'similar_count': 3,
            'remove_pattern': None,
            'output': str(tmp_path / "modified.json"),
            'data_dir': atlas.data_dir
        })
        
        wordlist_modify_command(modify_args)
        captured = capsys.readouterr()
        
        # Check output messages
        assert "Loaded wordlist" in captured.out
        assert "Updated wordlist metadata" in captured.out
        assert "Added" in captured.out
        assert "words similar to" in captured.out
        assert "Wordlist saved to" in captured.out
        
        # Check that the output file was created
        assert (tmp_path / "modified.json").exists()
        
        # Check file contents
        with open(tmp_path / "modified.json", 'r') as f:
            data = json.load(f)
            assert data["metadata"]["name"] == "Modified Wordlist"
            assert "modified" in data["metadata"]["tags"]
    
    def test_wordlist_merge_command(self, atlas, capsys, tmp_path):
        """Test the wordlist merge command."""
        # First create two wordlists
        create_args1 = type('Args', (), {
            'name': "Merge Test 1",
            'description': "For merging",
            'creator': "Test User",
            'tags': None,
            'search_pattern': None,
            'attribute': "GSL",
            'syllables': None,
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': None,
            'output': str(tmp_path / "merge_test1.json"),
            'no_analyze': True,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(create_args1)
        
        create_args2 = type('Args', (), {
            'name': "Merge Test 2",
            'description': "For merging",
            'creator': "Test User",
            'tags': None,
            'search_pattern': None,
            'attribute': None,
            'syllables': 1,  # 1-syllable words
            'min_freq': None,
            'max_freq': None,
            'similar_to': None,
            'similar_count': None,
            'input_file': None,
            'output': str(tmp_path / "merge_test2.json"),
            'no_analyze': True,
            'data_dir': atlas.data_dir
        })
        
        wordlist_create_command(create_args2)
        
        # Now merge them
        merge_args = type('Args', (), {
            'wordlists': [str(tmp_path / "merge_test1.json"), str(tmp_path / "merge_test2.json")],
            'name': "Merged Wordlist",
            'description': "Result of merging",
            'creator': "Test User",
            'tags': "merged,test",
            'output': str(tmp_path / "merged.json"),
            'ignore_errors': False,
            'data_dir': atlas.data_dir
        })
        
        wordlist_merge_command(merge_args)
        captured = capsys.readouterr()
        
        # Check output messages
        assert "Added" in captured.out
        assert "words from" in captured.out
        assert "Merged wordlist saved to" in captured.out
        
        # Check that the output file was created
        assert (tmp_path / "merged.json").exists()
        
        # Check file contents
        with open(tmp_path / "merged.json", 'r') as f:
            data = json.load(f)
            assert data["metadata"]["name"] == "Merged Wordlist"
            assert "merged" in data["metadata"]["tags"]
    
    def test_main_with_wordlist_create(self, atlas, capsys, tmp_path):
        """Test the main function with wordlist create command."""
        output_file = str(tmp_path / "cli_wordlist.json")
        with patch.object(sys, 'argv', [
            'word_atlas', 'wordlist', 'create',
            '--name', 'CLI Created Wordlist',
            '--attribute', 'GSL',
            '--output', output_file
        ]):
            with patch('word_atlas.cli.WordAtlas', return_value=atlas):
                main()
        
        captured = capsys.readouterr()
        assert "Added" in captured.out
        assert "words with attribute GSL" in captured.out
        assert f"Wordlist saved to '{output_file}'" in captured.out
        
        # Check that the output file was created
        assert Path(output_file).exists()
    
    def test_main_with_wordlist_help(self, capsys):
        """Test the main function with wordlist help."""
        with patch.object(sys, 'argv', ['word_atlas', 'wordlist']):
            main()
        
        captured = capsys.readouterr()
        assert "wordlist" in captured.out
        assert "Wordlist operation" in captured.out 