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
            # Verify required files exist
            required_files = ["word_index.json", "embeddings.npy", "word_data.json"]
            if all((path / file).exists() for file in required_files):
                return path

    raise FileNotFoundError(
        "Could not find the English Word Atlas dataset. "
        "Please specify the path to the data directory containing "
        "word_index.json, embeddings.npy, and word_data.json."
    )


def load_dataset(
    data_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Load the complete English Word Atlas dataset.

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        Dictionary mapping words to their attributes including embeddings

    Raises:
        FileNotFoundError: If the dataset files cannot be found
    """
    data_path = get_data_dir(data_dir)

    # Load word index
    with open(data_path / "word_index.json", "r") as f:
        word_to_idx = json.load(f)

    # Load embeddings
    embeddings = np.load(data_path / "embeddings.npy")

    # Load main data
    with open(data_path / "word_data.json", "r") as f:
        word_data = json.load(f)

    # Reconstruct complete data structure
    for word in word_data:
        if word in word_to_idx:
            word_data[word]["EMBEDDINGS_ALL_MINILM_L6_V2"] = embeddings[
                word_to_idx[word]
            ].tolist()

    return word_data


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


def get_embeddings(data_dir: Optional[Union[str, Path]] = None) -> np.ndarray:
    """Get the raw embedding matrix.

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        NumPy array containing word embeddings
    """
    data_path = get_data_dir(data_dir)

    return np.load(data_path / "embeddings.npy")


def get_word_data(
    data_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Get the word attribute data (without embeddings).

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        Dictionary mapping words to their attributes (without embeddings)
    """
    data_path = get_data_dir(data_dir)

    with open(data_path / "word_data.json", "r") as f:
        return json.load(f)


def get_available_attributes(
    data_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, int]:
    """Get a list of available attributes and their coverage.

    Args:
        data_dir: Optional directory containing the dataset files

    Returns:
        Dictionary mapping attribute names to the count of words having that attribute
    """
    word_data = get_word_data(data_dir)

    attributes = {}
    for word, attrs in word_data.items():
        for attr in attrs:
            if attr not in attributes:
                attributes[attr] = 0

            # Count truthy values for boolean flags
            if attrs[attr]:
                attributes[attr] += 1

    return attributes
