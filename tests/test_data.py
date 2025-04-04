"""Tests for the data loading functions."""

import os
import numpy as np
import pytest

from word_atlas.data import (
    get_data_dir,
    load_dataset,
    get_word_index,
    get_embeddings,
    get_word_data,
    get_available_attributes,
)


class TestDataLoading:
    """Test the data loading functions."""

    def test_get_data_dir(self, mock_data_dir):
        """Test finding the data directory."""
        # Test with explicit path
        data_dir = get_data_dir(mock_data_dir)
        assert data_dir == mock_data_dir

        # Test with non-existent path
        with pytest.raises(FileNotFoundError):
            get_data_dir("nonexistent_path")

    def test_load_dataset(self, mock_data_dir):
        """Test loading the complete dataset."""
        dataset = load_dataset(mock_data_dir)

        # Check that the dataset contains all expected words
        assert set(dataset.keys()) == {
            "apple",
            "banana",
            "cat",
            "dog",
            "elephant",
            "freedom",
            "good idea",
            "happy",
            "sad",
            "swim",
        }

        # Check that embeddings were added
        assert "EMBEDDINGS_ALL_MINILM_L6_V2" in dataset["apple"]
        assert len(dataset["apple"]["EMBEDDINGS_ALL_MINILM_L6_V2"]) == 4

        # Check some attribute values
        assert dataset["cat"]["SYLLABLE_COUNT"] == 1
        assert dataset["cat"]["ROGET_ANIMAL"] is True

    def test_get_word_index(self, mock_data_dir):
        """Test getting the word index mapping."""
        word_index = get_word_index(mock_data_dir)

        # Check that it contains the expected words
        assert set(word_index.keys()) == {
            "apple",
            "banana",
            "cat",
            "dog",
            "elephant",
            "freedom",
            "good idea",
            "happy",
            "sad",
            "swim",
        }

        # Check that indices are correct
        assert word_index["apple"] == 0
        assert word_index["banana"] == 1
        assert word_index["cat"] == 2

    def test_get_embeddings(self, mock_data_dir):
        """Test getting the raw embeddings."""
        embeddings = get_embeddings(mock_data_dir)

        # Check the shape
        assert embeddings.shape == (10, 4)  # 10 words, 4D embeddings

        # Check that embeddings are normalized
        for i in range(embeddings.shape[0]):
            assert np.isclose(np.linalg.norm(embeddings[i]), 1.0)

    def test_get_word_data(self, mock_data_dir):
        """Test getting the word attributes."""
        word_data = get_word_data(mock_data_dir)

        # Check that it contains the expected words
        assert set(word_data.keys()) == {
            "apple",
            "banana",
            "cat",
            "dog",
            "elephant",
            "freedom",
            "good idea",
            "happy",
            "sad",
            "swim",
        }

        # Check some attribute values
        assert word_data["dog"]["SYLLABLE_COUNT"] == 1
        assert word_data["dog"]["FREQ_GRADE"] == 450.3
        assert word_data["dog"]["GSL"] is True

        # Embeddings should not be included here
        assert "EMBEDDINGS_ALL_MINILM_L6_V2" not in word_data["apple"]

    def test_get_available_attributes(self, mock_data_dir):
        """Test getting the available attributes."""
        attributes = get_available_attributes(mock_data_dir)

        # Check that it contains expected attributes
        assert "SYLLABLE_COUNT" in attributes
        assert "FREQ_GRADE" in attributes
        assert "GSL" in attributes
        assert "ROGET_ANIMAL" in attributes

        # Check counts for some attributes
        assert attributes["GSL"] == 7  # 7 words have GSL=True
        assert attributes["ROGET_ANIMAL"] == 3  # 3 words have ROGET_ANIMAL=True
