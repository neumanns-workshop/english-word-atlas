"""
Unit tests for the data module.
"""

import pytest
from pathlib import Path
import numpy as np
import os
import json

from word_atlas.data import (
    get_data_dir,
    load_dataset,
    get_word_index,
    get_embeddings,
    get_word_data,
    get_available_attributes,
)


def test_get_data_dir(mock_data_dir):
    """Test finding the data directory."""
    # Test with explicit path
    data_dir = get_data_dir(mock_data_dir)
    assert isinstance(data_dir, Path)
    assert data_dir.exists()

    # Test required files exist
    assert (data_dir / "word_index.json").exists()
    assert (data_dir / "embeddings.npy").exists()
    assert (data_dir / "word_data.json").exists()

    # Test with invalid path
    with pytest.raises(FileNotFoundError):
        get_data_dir("/nonexistent/path")


def test_get_data_dir_search_paths(mock_data_dir, tmp_path):
    """Test searching for data directory in common locations."""
    # Save original working directory and data files
    original_cwd = os.getcwd()
    original_data_dir = Path(__file__).parent.parent.parent / "data"
    original_files = {}

    try:
        # If real data directory exists, temporarily move its files
        if original_data_dir.exists():
            original_files = {
                "word_index.json": original_data_dir / "word_index.json",
                "embeddings.npy": original_data_dir / "embeddings.npy",
                "word_data.json": original_data_dir / "word_data.json",
            }
            temp_backup = tmp_path / "backup"
            temp_backup.mkdir()
            for name, path in original_files.items():
                if path.exists():
                    path.rename(temp_backup / name)

        # Create test directories
        data_paths = [
            tmp_path / "data",  # Current directory
            tmp_path / "package" / "data",  # Package directory
            tmp_path / "home" / "english_word_atlas" / "data",  # User home directory
            Path(
                "/usr/local/share/english_word_atlas/data"
            ),  # System directory (skip this one)
        ]

        # Create minimal test data
        mock_data = {"apple": 0, "banana": 1}
        mock_embeddings = np.random.rand(2, 384)
        mock_embeddings = mock_embeddings / np.linalg.norm(
            mock_embeddings, axis=1, keepdims=True
        )

        # Create directories and add mock data
        for path in data_paths[:-1]:  # Skip system directory
            path.parent.mkdir(parents=True, exist_ok=True)
            path.mkdir(exist_ok=True)

            # Create required files
            (path / "word_index.json").write_text(json.dumps(mock_data))
            np.save(path / "embeddings.npy", mock_embeddings)
            (path / "word_data.json").write_text(json.dumps(mock_data))

        # Test current directory
        os.chdir(tmp_path)
        data_dir = get_data_dir()
        assert data_dir == data_paths[0]

        # Remove current directory and test package directory
        os.remove(data_paths[0] / "word_index.json")
        os.remove(data_paths[0] / "embeddings.npy")
        os.remove(data_paths[0] / "word_data.json")
        os.rmdir(data_paths[0])

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(Path, "cwd", lambda: tmp_path / "package")
            data_dir = get_data_dir()
            assert data_dir == data_paths[1]

        # Remove package directory and test home directory
        os.remove(data_paths[1] / "word_index.json")
        os.remove(data_paths[1] / "embeddings.npy")
        os.remove(data_paths[1] / "word_data.json")
        os.rmdir(data_paths[1])
        os.rmdir(data_paths[1].parent)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(Path, "home", lambda: tmp_path / "home")
            data_dir = get_data_dir()
            assert data_dir == data_paths[2]

        # Remove all directories and test error
        os.remove(data_paths[2] / "word_index.json")
        os.remove(data_paths[2] / "embeddings.npy")
        os.remove(data_paths[2] / "word_data.json")
        os.rmdir(data_paths[2])
        os.rmdir(data_paths[2].parent)
        os.rmdir(data_paths[2].parent.parent)

        with pytest.raises(FileNotFoundError):
            get_data_dir()

    finally:
        # Restore original working directory
        os.chdir(original_cwd)

        # Restore original data files if they existed
        if original_files:
            for name, path in original_files.items():
                if (tmp_path / "backup" / name).exists():
                    (tmp_path / "backup" / name).rename(path)


def test_load_dataset(mock_data_dir):
    """Test loading the complete dataset."""
    dataset = load_dataset(mock_data_dir)

    # Check structure
    assert isinstance(dataset, dict)
    assert len(dataset) > 0

    # Check a sample word's structure
    sample_word = next(iter(dataset.values()))
    assert isinstance(sample_word, dict)
    assert "SYLLABLE_COUNT" in sample_word
    assert "FREQ_GRADE" in sample_word
    assert "EMBEDDINGS_ALL_MINILM_L6_V2" in sample_word


def test_get_word_index(mock_data_dir):
    """Test getting the word index mapping."""
    word_index = get_word_index(mock_data_dir)

    # Check structure
    assert isinstance(word_index, dict)
    assert len(word_index) > 0

    # Check specific words from our mock data
    assert "apple" in word_index
    assert "banana" in word_index

    # Check index values
    assert isinstance(word_index["apple"], int)
    assert isinstance(word_index["banana"], int)

    # Check indices are sequential starting from 0
    indices = sorted(word_index.values())
    assert indices == list(range(len(indices)))


def test_get_embeddings(mock_data_dir):
    """Test getting the embedding matrix."""
    # First get the word index to know how many words we expect
    word_index = get_word_index(mock_data_dir)
    num_words = len(word_index)

    embeddings = get_embeddings(mock_data_dir)

    # Check structure
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.ndim == 2
    assert embeddings.shape[0] == num_words  # Number of words matches index
    assert embeddings.shape[1] == 384  # Embedding dimension

    # Check embeddings are normalized
    norms = np.linalg.norm(embeddings, axis=1)
    assert np.allclose(norms, 1.0, rtol=1e-5)


def test_get_word_data(mock_data_dir):
    """Test getting word attributes without embeddings."""
    word_data = get_word_data(mock_data_dir)

    # Check structure
    assert isinstance(word_data, dict)
    assert len(word_data) > 0

    # Check specific words from our mock data
    assert "apple" in word_data
    assert "banana" in word_data

    # Check word attributes
    apple_data = word_data["apple"]
    assert isinstance(apple_data, dict)
    assert "SYLLABLE_COUNT" in apple_data
    assert "FREQ_GRADE" in apple_data
    assert "GSL" in apple_data
    assert "ROGET_FOOD" in apple_data
    assert "ROGET_PLANT" in apple_data
    assert "ARPABET" in apple_data

    # Verify embeddings are not included
    assert "EMBEDDINGS_ALL_MINILM_L6_V2" not in apple_data


def test_get_available_attributes(mock_data_dir):
    """Test getting available attributes and their coverage."""
    attributes = get_available_attributes(mock_data_dir)

    # Check structure
    assert isinstance(attributes, dict)
    assert len(attributes) > 0

    # Check common attributes exist with correct counts
    assert "SYLLABLE_COUNT" in attributes
    assert attributes["SYLLABLE_COUNT"] == 2  # apple and banana

    assert "FREQ_GRADE" in attributes
    assert attributes["FREQ_GRADE"] == 2  # apple and banana

    assert "GSL" in attributes
    assert attributes["GSL"] == 2  # both are True

    assert "ROGET_FOOD" in attributes
    assert attributes["ROGET_FOOD"] == 2  # both are True

    assert "ROGET_PLANT" in attributes
    assert attributes["ROGET_PLANT"] == 2  # both are True

    # Verify embeddings are not included
    assert "EMBEDDINGS_ALL_MINILM_L6_V2" not in attributes
