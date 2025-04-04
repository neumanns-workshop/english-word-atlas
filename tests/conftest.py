"""Pytest configuration and fixtures for the English Word Atlas package."""

import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from word_atlas import WordAtlas


@pytest.fixture(scope="session")
def mock_data_dir():
    """Create a temporary directory with mock dataset files for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Create mock data files

        # Mock word_index.json
        word_index = {
            "apple": 0,
            "banana": 1,
            "cat": 2,
            "dog": 3,
            "elephant": 4,
            "freedom": 5,
            "good idea": 6,
            "happy": 7,
            "sad": 8,
            "swim": 9,
        }

        with open(os.path.join(temp_dir, "word_index.json"), "w") as f:
            json.dump(word_index, f)

        # Mock embeddings.npy - 10 words with 4-dimensional embeddings
        embeddings = np.array(
            [
                [0.1, 0.2, 0.3, 0.4],  # apple
                [0.2, 0.3, 0.4, 0.5],  # banana
                [0.3, 0.4, 0.5, 0.6],  # cat
                [0.4, 0.5, 0.6, 0.7],  # dog
                [0.5, 0.6, 0.7, 0.8],  # elephant
                [0.6, 0.7, 0.8, 0.9],  # freedom
                [0.7, 0.8, 0.9, 1.0],  # good idea
                [0.8, 0.9, 1.0, 0.1],  # happy
                [0.9, 1.0, 0.1, 0.2],  # sad
                [1.0, 0.1, 0.2, 0.3],  # swim
            ]
        )

        # Normalize embeddings for cosine similarity
        for i in range(embeddings.shape[0]):
            embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])

        np.save(os.path.join(temp_dir, "embeddings.npy"), embeddings)

        # Mock word_data.json
        word_data = {
            "apple": {
                "SYLLABLE_COUNT": 2,
                "ARPABET": [["AE1", "P", "AH0", "L"]],
                "FREQ_GRADE": 350.5,
                "GSL": True,
                "ROGET_FOOD": True,
            },
            "banana": {
                "SYLLABLE_COUNT": 3,
                "ARPABET": [["B", "AH0", "N", "AE1", "N", "AH0"]],
                "FREQ_GRADE": 150.2,
                "GSL": True,
                "ROGET_FOOD": True,
            },
            "cat": {
                "SYLLABLE_COUNT": 1,
                "ARPABET": [["K", "AE1", "T"]],
                "FREQ_GRADE": 400.0,
                "GSL": True,
                "SWADESH": True,
                "ROGET_ANIMAL": True,
            },
            "dog": {
                "SYLLABLE_COUNT": 1,
                "ARPABET": [["D", "AO1", "G"]],
                "FREQ_GRADE": 450.3,
                "GSL": True,
                "SWADESH": True,
                "ROGET_ANIMAL": True,
            },
            "elephant": {
                "SYLLABLE_COUNT": 3,
                "ARPABET": [["EH1", "L", "AH0", "F", "AH0", "N", "T"]],
                "FREQ_GRADE": 120.5,
                "ROGET_ANIMAL": True,
            },
            "freedom": {
                "SYLLABLE_COUNT": 2,
                "ARPABET": [["F", "R", "IY1", "D", "AH0", "M"]],
                "FREQ_GRADE": 200.8,
                "NGSL": True,
                "ROGET_ABSTRACT": True,
            },
            "good idea": {
                "SYLLABLE_COUNT": 3,
                "ARPABET": [["G", "UH1", "D", "AY0", "D", "IY1", "AH0"]],
                "FREQ_GRADE": 80.1,
                "ROGET_THOUGHT": True,
            },
            "happy": {
                "SYLLABLE_COUNT": 2,
                "ARPABET": [["HH", "AE1", "P", "IY0"]],
                "FREQ_GRADE": 350.5,
                "GSL": True,
                "OGDEN": True,
                "ROGET_EMOTION": True,
            },
            "sad": {
                "SYLLABLE_COUNT": 1,
                "ARPABET": [["S", "AE1", "D"]],
                "FREQ_GRADE": 250.0,
                "GSL": True,
                "OGDEN": True,
                "ROGET_EMOTION": True,
            },
            "swim": {
                "SYLLABLE_COUNT": 1,
                "ARPABET": [["S", "W", "IH1", "M"]],
                "FREQ_GRADE": 180.5,
                "GSL": True,
                "ROGET_MOTION": True,
            },
        }

        with open(os.path.join(temp_dir, "word_data.json"), "w") as f:
            json.dump(word_data, f)

        yield Path(temp_dir)
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


@pytest.fixture
def atlas(mock_data_dir):
    """Initialize a WordAtlas instance with mock data."""
    return WordAtlas(data_dir=mock_data_dir)
