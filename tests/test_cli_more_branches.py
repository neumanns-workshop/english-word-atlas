import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from word_atlas.cli import search_command, stats_command


class TestMoreCLIBranches(unittest.TestCase):
    """Additional tests for CLI edge cases to increase coverage"""

    def setUp(self):
        # Redirect stdout to capture print outputs
        self.stdout_backup = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.stdout_backup

    @patch("word_atlas.WordAtlas")
    def test_handle_stats_detailed(self, mock_atlas):
        """Test detailed stats command"""
        args = MagicMock(detailed=True, basic=False, data_dir=None)
        mock_atlas_instance = mock_atlas.return_value
        mock_atlas_instance.get_stats.return_value = {
            "total_entries": 100,
            "single_words": 80,
            "phrases": 20,
            "embedding_dim": 384,
        }
        mock_atlas_instance.get_syllable_counts.return_value = [1, 2]
        mock_atlas_instance.filter_by_syllable_count.return_value = ["test"]
        mock_atlas_instance.word_data = {"test": {"FREQ_GRADE": 5}}
        mock_atlas_instance.filter_by_attribute.return_value = ["test"]

        stats_command(args)

    @patch("word_atlas.WordAtlas")
    def test_search_with_invalid_options(self, mock_atlas):
        """Test search with incompatible options"""
        args = MagicMock(
            pattern="test",
            words_only=True,
            phrases_only=True,
            attribute=None,
            min_freq=None,
            max_freq=None,
            limit=None,
            verbose=False,
            data_dir=None,
        )
        mock_atlas_instance = mock_atlas.return_value
        mock_atlas_instance.search.return_value = ["test"]
        mock_atlas_instance.has_word.return_value = True
        mock_atlas_instance.get_word.return_value = {}

        # This should handle the conflicting words_only and phrases_only
        search_command(args)


if __name__ == "__main__":
    unittest.main()
