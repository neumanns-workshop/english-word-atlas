import unittest
from unittest.mock import patch, MagicMock
import sys
import importlib


class TestMain(unittest.TestCase):
    """Test the __main__ module"""

    @patch.object(sys, "argv", ["word_atlas"])
    def test_main_module_import(self):
        """Test that the __main__ module can be imported and run"""
        # Create a mock for cli.main
        mock_main = MagicMock()

        # Patch the main function that gets imported in __main__
        with patch("word_atlas.cli.main", mock_main):
            # Import the module - since this is done inside the context manager,
            # our patched version will be used when the module executes
            importlib.import_module("word_atlas.__main__")

            # Since __main__ only calls main() when __name__ == "__main__",
            # we need to simulate that condition
            import word_atlas.__main__

            # Call the conditional block directly
            if True:  # Simulating __name__ == "__main__"
                word_atlas.__main__.main()

            # Now verify if our mock was called
            mock_main.assert_called_once()


if __name__ == "__main__":
    unittest.main()
