"""Tests to verify that the example scripts run without errors."""

import os
import sys
import importlib.util
from unittest.mock import patch
import pytest


@pytest.mark.integration
class TestExamples:
    """Test that example scripts run correctly."""
    
    def test_basic_usage_example(self, atlas, capsys):
        """Test that the basic usage example runs without errors."""
        # Path to the example script
        example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "examples", "basic_usage.py")
        
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("basic_usage", example_path)
        module = importlib.util.module_from_spec(spec)
        
        # Mock the WordAtlas class to return our test instance
        with patch("word_atlas.WordAtlas", return_value=atlas):
            # Execute the module
            spec.loader.exec_module(module)
            module.main()
        
        # Get the printed output
        captured = capsys.readouterr()
        
        # Verify that the script produced some output
        assert "Loading the English Word Atlas" in captured.out
        assert "Words similar to 'freedom'" in captured.out
        assert "Similarity between 'happy' and 'sad'" in captured.out
    
    def test_text_analysis_example(self, atlas, capsys):
        """Test that the text analysis example runs without errors."""
        # Path to the example script
        example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "examples", "text_analysis.py")
        
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("text_analysis", example_path)
        module = importlib.util.module_from_spec(spec)
        
        # Mock the WordAtlas class to return our test instance
        with patch("word_atlas.WordAtlas", return_value=atlas):
            # Mock sys.argv to simulate no command-line arguments
            with patch("sys.argv", ["text_analysis.py"]):
                # Execute the module
                spec.loader.exec_module(module)
                module.main()
        
        # Get the printed output
        captured = capsys.readouterr()
        
        # Verify that the script produced some output
        assert "Using sample text" in captured.out
        assert "Text Analysis Results" in captured.out
        assert "Words found in atlas" in captured.out 