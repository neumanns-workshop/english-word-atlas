"""
Data loading and management for the English Word Atlas dataset.
"""

import json
import numpy as np
from pathlib import Path
import os
from typing import Dict, Any, Optional, Union


def get_data_dir(data_dir: Optional[Union[str, Path]] = None) -> Path:
    """Find the data directory containing the dataset files.

    Args:
        data_dir: Optional user-specified data directory

    Returns:
        Path to the directory containing dataset files

    Raises:
        FileNotFoundError: If the dataset files cannot be found
    """
    if data_dir is not None:
        path = Path(data_dir)
        if path.exists():
            return path
        raise FileNotFoundError(f"Specified data directory '{path}' not found")

    # Try common locations
    possible_paths = [
        Path.cwd() / "data",  # Current directory
        Path(__file__).parent.parent / "data",  # Package directory
        Path.home() / "english_word_atlas/data",  # User home directory
        Path("/usr/local/share/english_word_atlas/data"),  # System directory
    ]

    for path in possible_paths:
        if path.exists():
            # Verify required base files exist
            # Now requires word_index.json and the frequencies file
            required_files = ["word_index.json"]
            required_dirs = ["sources"]  # Require sources dir
            required_freq_file = Path("frequencies/word_frequencies.json")

            base_files_exist = all((path / file).exists() for file in required_files)
            dirs_exist = all((path / d).is_dir() for d in required_dirs)
            freq_file_exists = (path / required_freq_file).exists()

            if base_files_exist and dirs_exist and freq_file_exists:
                return path

    # Update error message
    raise FileNotFoundError(
        "Could not find the required English Word Atlas dataset components.\n"
        "Please ensure the data directory contains: "
        "- word_index.json\n"
        "- frequencies/word_frequencies.json\n"
        "- sources/ (directory)\n"
        "Or specify the correct path using --data-dir."
    )


# Deprecated: load_dataset - WordAtlas now loads components directly
# def load_dataset(
#     data_dir: Optional[Union[str, Path]] = None,
# ) -> Dict[str, Dict[str, Any]]:
#     """Load the complete English Word Atlas dataset.
#
#     Args:
#         data_dir: Optional directory containing the dataset files
#
#     Returns:
#         Dictionary mapping words to their attributes including embeddings
#
#     Raises:
#         FileNotFoundError: If the dataset files cannot be found
#     """
#     data_path = get_data_dir(data_dir)
#
#     # Load word index
#     with open(data_path / "word_index.json", "r") as f:
#         word_to_idx = json.load(f)
#
#     # Load embeddings
#     embeddings = np.load(data_path / "embeddings.npy")
#
#     # Load main data
#     with open(data_path / "word_data.json", "r") as f:
#         word_data = json.load(f)
#
#     # Reconstruct complete data structure
#     for word in word_data:
#         if word in word_to_idx:
#             word_data[word]["EMBEDDINGS_ALL_MINILM_L6_V2"] = embeddings[
#                 word_to_idx[word]
#             ].tolist()
#
#     return word_data


def get_word_index(data_dir: Optional[Union[str, Path]] = None) -> Dict[str, int]:
    """Get the mapping of words to their embedding indices.

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        Dictionary mapping words to indices in the embedding matrix
    """
    data_path = get_data_dir(data_dir)

    with open(data_path / "word_index.json", "r") as f:
        return json.load(f)


def get_word_frequencies(
    data_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, float]:
    """Load the word frequency map from frequencies/word_frequencies.json.

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        Dictionary mapping words to their frequencies

    Raises:
        FileNotFoundError: If the frequency file cannot be found
        ValueError: If there is an error decoding the JSON from the frequency file
        RuntimeError: If there is an error loading the frequency file
    """
    data_path = get_data_dir(data_dir)
    freq_file = data_path / "frequencies" / "word_frequencies.json"

    if not freq_file.exists():
        raise FileNotFoundError(f"Frequency file not found: {freq_file}")

    try:
        with open(freq_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from frequency file {freq_file}: {e}")
    except Exception as e:
        raise RuntimeError(f"Could not load frequency file {freq_file}: {e}")
