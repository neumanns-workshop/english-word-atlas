"""
Test fixtures for the English Word Atlas tests.
"""

import json
import numpy as np
import pytest
from pathlib import Path
import os
import tempfile
from unittest.mock import MagicMock
from io import StringIO
from unittest.mock import patch
import sys

from word_atlas.atlas import WordAtlas
from word_atlas.wordlist import WordlistBuilder

# Comprehensive mock data for testing
MOCK_WORDS = {
    "apple": {
        "SYLLABLE_COUNT": 2,
        "FREQ_GRADE": 1,
        "GSL": True,
        "ROGET_PLANT": True,
        "ROGET_FOOD": True,
        "ARPABET": [["AE1", "P", "AH0", "L"]],
        "EMBEDDING": [0.1] * 384,
    },
    "banana": {
        "SYLLABLE_COUNT": 3,
        "FREQ_GRADE": 1,
        "GSL": True,
        "ROGET_PLANT": True,
        "ROGET_FOOD": True,
        "ARPABET": [["B", "AH0", "N", "AE1", "N", "AH0"]],
        "EMBEDDING": [0.2] * 384,
    },
}


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory with mock dataset files."""
    # Create word index
    word_index = {word: idx for idx, word in enumerate(MOCK_WORDS)}
    (tmp_path / "word_index.json").write_text(json.dumps(word_index))

    # Create embeddings from the mock data
    embeddings = np.array([word_data["EMBEDDING"] for word_data in MOCK_WORDS.values()])
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    np.save(tmp_path / "embeddings.npy", embeddings)

    # Create word data (without embeddings)
    word_data = {
        word: {k: v for k, v in data.items() if k != "EMBEDDING"}
        for word, data in MOCK_WORDS.items()
    }
    (tmp_path / "word_data.json").write_text(json.dumps(word_data))

    return tmp_path


@pytest.fixture
def mock_atlas(mock_data_dir):
    """Create a WordAtlas instance with mock data."""
    return WordAtlas(mock_data_dir)


@pytest.fixture
def mock_cli_atlas():
    """Create a mock WordAtlas instance with test data for CLI tests."""
    atlas = MagicMock(spec=WordAtlas)

    # Enhanced mock word data for better stats coverage
    test_word_data = {
        "apple": {
            "SYLLABLE_COUNT": 2,
            "ARPABET": [["AE1", "P", "AH0", "L"]],
            "FREQ_COUNT": 150.5,
            "FREQ_GRADE": 5.2,
            "GSL": True,
            "NGSL": True,
            "ROGET_FOOD": True,
            "ROGET_PLANT": True,
        },
        "banana split": {
            "SYLLABLE_COUNT": 4,
            "ARPABET": [
                ["B", "AH0", "N", "AE1", "N", "AH0", "S", "P", "L", "IH1", "T"]
            ],
            "FREQ_COUNT": 10.2,
            "FREQ_GRADE": 15.8,
            "ROGET_FOOD": True,
        },
        "cat": {
            "SYLLABLE_COUNT": 1,
            "ARPABET": [["K", "AE1", "T"]],
            "FREQ_GRADE": 0,
            "OGDEN": True,
        },
        "syllogism": {"SYLLABLE_COUNT": 4, "FREQ_GRADE": 150.0, "SWADESH": True},
        "antidisestablishmentarianism": {"SYLLABLE_COUNT": 12, "FREQ_GRADE": 1200.0},
    }

    atlas.word_data = test_word_data
    atlas.has_word.side_effect = lambda w: w in test_word_data
    atlas.get_word.side_effect = lambda w: test_word_data.get(w, {})
    atlas.get_similar_words.return_value = [("pear", 0.85), ("orange", 0.82)]
    atlas.get_stats.return_value = {
        "total_entries": 2,
        "single_words": 1,
        "phrases": 1,
        "embedding_dim": 384,
    }

    def get_syllable_counts():
        return {
            data.get("SYLLABLE_COUNT")
            for data in test_word_data.values()
            if "SYLLABLE_COUNT" in data
        }

    def filter_by_syllable_count(count):
        return {
            w
            for w, data in test_word_data.items()
            if data.get("SYLLABLE_COUNT") == count
        }

    def filter_by_attribute(attr, value=None):
        if value is None:
            return {w for w, data in test_word_data.items() if data.get(attr, False)}
        return {w for w, data in test_word_data.items() if data.get(attr) == value}

    def search(pattern):
        return [w for w in test_word_data.keys() if pattern.lower() in w.lower()]

    atlas.get_syllable_counts.side_effect = get_syllable_counts
    atlas.filter_by_syllable_count.side_effect = filter_by_syllable_count
    atlas.filter_by_attribute.side_effect = filter_by_attribute
    atlas.search.side_effect = search

    return atlas


@pytest.fixture
def mock_cli_atlas_many_roget(mock_cli_atlas):
    """Create a mock WordAtlas for CLI tests with a word having many Roget categories."""
    # Reuse the base mock_cli_atlas
    atlas = mock_cli_atlas

    word_info_for_test = {
        "SYLLABLE_COUNT": 2,
        "FREQ_GRADE": 5.0,
        "GSL": True,
        "ROGET_1": True,
        "ROGET_2": True,
        "ROGET_3": True,
        "ROGET_4": True,
        "ROGET_5": True,
        "ROGET_6": True,  # More than 5 Roget categories
    }
    test_word = "testword_many_roget"

    # Store original side effects
    original_get_word = atlas.get_word.side_effect
    original_has_word = atlas.has_word.side_effect

    def specific_get_word(word):
        if word == test_word:
            return word_info_for_test
        return original_get_word(word)

    def specific_has_word(word):
        if word == test_word:
            return True
        return original_has_word(word)

    # Apply new side effects
    atlas.get_word.side_effect = specific_get_word
    atlas.has_word.side_effect = specific_has_word

    return atlas


@pytest.fixture
def mock_wordlist_builder(mock_cli_atlas):
    """Create a mock WordlistBuilder instance for testing."""
    builder = MagicMock(spec=WordlistBuilder)
    builder.atlas = mock_cli_atlas
    builder.words = {"apple", "banana split"}
    builder.metadata = {
        "name": "Test List",
        "description": "A test wordlist",
        "creator": "Test User",
        "tags": ["test"],
        "created": "2024-03-20",
        "modified": "2024-03-21",
        "criteria": [],
    }

    builder.get_size.return_value = len(builder.words)
    builder.get_wordlist.return_value = builder.words
    builder.add_by_search.return_value = 1
    builder.add_by_attribute.return_value = 1
    builder.add_by_syllable_count.return_value = 1
    builder.add_by_frequency.return_value = 1
    builder.add_similar_words.return_value = 2
    builder.add_words.return_value = 2
    builder.remove_words.return_value = 1

    def analyze():
        return {
            "size": len(builder.words),
            "single_words": len([w for w in builder.words if " " not in w]),
            "phrases": len([w for w in builder.words if " " in w]),
            "syllable_distribution": {
                2: 1,  # apple
                4: 1,  # banana split
            },
            "frequency": {
                "distribution": {
                    "1-10": 1,
                    "11-100": 1,
                },
                "average": 10.5,
            },
            "wordlist_coverage": {
                "GSL": {"count": 1, "percentage": 50.0},
                "NGSL": {"count": 1, "percentage": 50.0},
                "OGDEN": {"count": 0, "percentage": 0.0},
                "SWADESH": {"count": 0, "percentage": 0.0},
            },
        }

    builder.analyze.side_effect = analyze
    return builder


@pytest.fixture
def mock_wordlist(mock_cli_atlas):
    """Create a mock WordlistBuilder instance for testing."""
    builder = MagicMock(spec=WordlistBuilder)
    builder.atlas = mock_cli_atlas
    builder.words = {"apple", "banana split"}
    builder.metadata = {
        "name": "Test List",
        "description": "A test wordlist",
        "creator": "Test User",
        "tags": ["test"],
        "created": "2024-03-20",
        "modified": "2024-03-21",
        "criteria": [],
    }

    # Mock methods
    builder.add_words.return_value = 2
    builder.remove_words.return_value = 1
    builder.get_wordlist.return_value = list(builder.words)
    builder.get_size.return_value = len(builder.words)
    builder.get_metadata.return_value = builder.metadata

    return builder
