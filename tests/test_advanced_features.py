import unittest
import os
from unittest.mock import patch, mock_open, MagicMock
import numpy as np
from pathlib import Path
import re
from word_atlas.atlas import WordAtlas

class TestAdvancedFeatures(unittest.TestCase):
    """Tests for advanced features and edge cases"""
    
    def test_custom_data_dir_validation(self):
        """Test what happens when a custom data dir doesn't have the necessary files"""
        with patch('os.path.exists') as mock_exists:
            # Make it return True for the directory but False for the required files
            mock_exists.side_effect = lambda p: not p.endswith('.json') and not p.endswith('.npy')
            with self.assertRaises(FileNotFoundError):
                WordAtlas(data_dir="/fake/path")
    
    def test_atlas_with_custom_data_loading(self):
        """Test WordAtlas constructor with direct data loading"""
        # Create minimal test data
        word_data = {"test": {"FREQ_GRADE": 5}}
        embeddings = np.zeros((1, 384))
        word_to_idx = {"test": 0}
        
        # Setup patches for data loading functions
        with patch('word_atlas.atlas.get_word_data', return_value=word_data):
            with patch('word_atlas.atlas.get_embeddings', return_value=embeddings):
                with patch('word_atlas.atlas.get_word_index', return_value=word_to_idx):
                    # Initialize atlas
                    atlas = WordAtlas()
                    
                    # Verify it loaded our test data correctly
                    self.assertTrue(atlas.has_word("test"))
                    self.assertEqual(atlas.get_word("test")["FREQ_GRADE"], 5)
                    
                    # Verify embedding access works
                    np.testing.assert_array_equal(atlas.get_embedding("test"), embeddings[0])
    
    def test_atlas_search_with_compiled_regex(self):
        """Test search with a pre-compiled regex"""
        # Setup patches for data loading
        word_data = {"apple": {"attr": 1}, "banana": {"attr": 2}, "avocado": {"attr": 3}}
        with patch('word_atlas.atlas.get_word_data', return_value=word_data):
            with patch('word_atlas.atlas.get_embeddings', return_value=np.zeros((3, 384))):
                with patch('word_atlas.atlas.get_word_index', return_value={"apple": 0, "banana": 1, "avocado": 2}):
                    # Create a compiled regex pattern
                    pattern = re.compile("^a")  # Words starting with 'a'
                    atlas = WordAtlas()
                    results = atlas.search(pattern)
                    
                    # Verify we got correct results
                    self.assertEqual(len(results), 2)
                    for word in results:
                        self.assertTrue(word.startswith("a"))

if __name__ == '__main__':
    unittest.main() 