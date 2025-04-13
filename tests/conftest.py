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
from typing import Any

from word_atlas.atlas import WordAtlas
from word_atlas.wordlist import WordlistBuilder

# Comprehensive mock data for testing
MOCK_WORDS = {
    "apple": {
        "SYLLABLE_COUNT": 2,
        "FREQ_GRADE": 5.2,
        "FREQ_COUNT": 150.5,
        "ARPABET": [["AE1", "P", "AH0", "L"]],
        "EMBEDDING": [0.1] * 384,
    },
    "banana": {
        "SYLLABLE_COUNT": 3,
        "FREQ_GRADE": 15.8,
        "FREQ_COUNT": 10.2,
        "ARPABET": [["B", "AH0", "N", "AE1", "N", "AH0"]],
        "EMBEDDING": [0.2] * 384,
    },
    "orange": {
        "SYLLABLE_COUNT": 2,
        "FREQ_GRADE": 4.1,
        "FREQ_COUNT": 90.0,
        "ARPABET": [["AO1", "R", "AH0", "N", "JH"]],
        "EMBEDDING": [0.3] * 384,
    }
}


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory with mock dataset files (base + sources + frequencies)."""
    # Create word index (includes all mock words)
    word_index = {word: idx for idx, word in enumerate(MOCK_WORDS)}
    (tmp_path / "word_index.json").write_text(json.dumps(word_index))

    # Create embeddings from the mock data - REMOVED
    # embeddings = np.array([word_data["EMBEDDING"] for word_data in MOCK_WORDS.values()])
    # Normalize embeddings (example)
    # norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # embeddings = np.divide(embeddings, norms, out=np.zeros_like(embeddings), where=norms!=0)
    # np.save(tmp_path / "embeddings.npy", embeddings)

    # Create frequencies directory and file with data from MOCK_WORDS
    freq_dir = tmp_path / "frequencies"
    freq_dir.mkdir()
    mock_frequencies = {
        word: data.get("FREQ_COUNT")
        for word, data in MOCK_WORDS.items()
        if "FREQ_COUNT" in data
    }
    (freq_dir / "word_frequencies.json").write_text(json.dumps(mock_frequencies))

    # Create sources directory
    sources_dir = tmp_path / "sources"
    sources_dir.mkdir()

    # Create mock source files based on original MOCK_WORDS structure implicitly
    # (Before refactoring, apple and banana had GSL, ROGET_PLANT, ROGET_FOOD)
    gsl_words = ["apple", "banana"]
    roget_plant_words = ["apple", "banana"]
    roget_food_words = ["apple", "banana"]

    (sources_dir / "GSL.json").write_text(json.dumps(gsl_words))
    (sources_dir / "ROGET_PLANT.json").write_text(json.dumps(roget_plant_words))
    (sources_dir / "ROGET_FOOD.json").write_text(json.dumps(roget_food_words))

    return tmp_path


@pytest.fixture
def mock_atlas(mock_data_dir):
    """Provides a WordAtlas instance initialized with mock data, ensuring necessary sources exist."""
    # Ensure the OTHER.txt source file exists *before* WordAtlas initializes.
    other_source_path = mock_data_dir / "sources" / "OTHER.txt"
    other_source_path.write_text("orange\n") # Overwrite/create with correct content

    # Initialize WordAtlas - it should now load OTHER.txt automatically.
    atlas = WordAtlas(mock_data_dir)

    # Simple verification (optional, can be removed if tests pass reliably)
    if "OTHER" not in atlas.get_source_list_names():
         pytest.fail("mock_atlas fixture failed to load the OTHER source list.")
    if atlas.get_words_in_source("OTHER") != {"orange"}:
         pytest.fail(f"mock_atlas fixture loaded OTHER source with unexpected content: {atlas.get_words_in_source('OTHER')}")

    return atlas


@pytest.fixture
def mock_cli_atlas():
    """Create a mock WordAtlas instance (frequency and sources only)."""
    atlas = MagicMock(spec=WordAtlas)

    # --- Mock Data ---
    # Base metadata REMOVED

    # Use MOCK_WORDS to derive index and frequencies for the mock
    # This ensures consistency if MOCK_WORDS is the source of truth
    mock_word_list = list(MOCK_WORDS.keys())
    mock_index = {word: idx for idx, word in enumerate(mock_word_list)}

    # Frequencies (derived from MOCK_WORDS)
    test_frequencies = {
        word: data.get("FREQ_COUNT")
        for word, data in MOCK_WORDS.items()
        if "FREQ_COUNT" in data
    }

    # Source lists (using keys from MOCK_WORDS)
    test_sources = {
        "GSL": {"apple", "banana"}, # Assuming these are in MOCK_WORDS
        "ROGET_FOOD": {"apple", "banana"},
        "ROGET_PLANT": {"apple", "banana"},
        "OTHER": {"orange"}
    }
    # Filter sources to only include words actually in our mock index
    test_sources = {
        name: {word for word in words if word in mock_index}
        for name, words in test_sources.items()
    }
    test_source_list_names = sorted(list(test_sources.keys()))

    # --- Assign Attributes ---
    # REMOVED atlas.word_data
    atlas.frequencies = test_frequencies
    atlas.all_words = set(mock_index.keys())
    atlas.word_to_idx = mock_index # Keep index for has_word / all_words consistency
    atlas._source_lists = test_sources # Directly assign for mock
    atlas.available_sources = {name: Path(f"mock/sources/{name}.json") for name in test_source_list_names} # Mock paths

    # --- Mock Methods ---
    all_words = list(atlas.all_words)
    atlas.get_all_words.return_value = sorted(all_words)
    atlas.has_word.side_effect = lambda w: w in atlas.all_words

    # REMOVED mock_get_metadata

    def mock_get_frequency(word):
        return test_frequencies.get(word.lower()) # Match simplified WordAtlas
    atlas.get_frequency.side_effect = mock_get_frequency

    def mock_get_sources(word):
        return sorted([name for name, words in test_sources.items() if word in words])
    atlas.get_sources.side_effect = mock_get_sources

    atlas.get_source_list_names.return_value = test_source_list_names

    def mock_get_words_in_source(source_name):
        # Raise error like the real one if source doesn't exist
        if source_name not in test_sources:
             raise ValueError(f"Source '{source_name}' not found.")
        return test_sources.get(source_name, set())
    atlas.get_words_in_source.side_effect = mock_get_words_in_source

    # REMOVED get_metadata_attributes

    # Update mock_filter to handle frequency
    def mock_filter(sources=None, min_freq=None, max_freq=None):
        results = atlas.all_words.copy()

        # Filter by source lists
        if sources:
            source_intersection = set()
            first_source = True
            for src_name in sources:
                words_in_src = mock_get_words_in_source(src_name) # Use mock getter
                if first_source:
                    source_intersection.update(words_in_src)
                    first_source = False
                else:
                    source_intersection.intersection_update(words_in_src)
                    if not source_intersection: return set()
            results.intersection_update(source_intersection)
            if not results: return set()

        # Filter by Frequency
        if min_freq is not None or max_freq is not None:
            freq_matches = set()
            min_f = min_freq if min_freq is not None else -float('inf')
            max_f = max_freq if max_freq is not None else float('inf')
            for word in results:
                freq = mock_get_frequency(word)
                if freq is not None and min_f <= freq <= max_f:
                    freq_matches.add(word)
            results.intersection_update(freq_matches)

        return results
    atlas.filter.side_effect = mock_filter

    def mock_search(pattern, case_sensitive=False):
        if not case_sensitive:
            pattern = pattern.lower()
            return [w for w in all_words if pattern in w.lower()]
        else:
            return [w for w in all_words if pattern in w]
    atlas.search.side_effect = mock_search

    # Mock get_stats (simplified)
    stats = {
        "total_entries": len(all_words),
        "single_words": sum(1 for w in all_words if " " not in w),
        "phrases": sum(1 for w in all_words if " " in w),
        "entries_with_frequency": len(test_frequencies),
        "source_lists": test_source_list_names,
        "source_coverage": {name: len(words) for name, words in test_sources.items()}
    }
    atlas.get_stats.return_value = stats

    return atlas


@pytest.fixture
def mock_cli_atlas_many_roget(mock_cli_atlas):
    """Create a mock WordAtlas for CLI tests with a word having many Roget sources."""
    atlas = mock_cli_atlas  # Get the base mock
    test_word = "testword_many_roget"

    # --- Add data for the new test word ---
    # No base data needed
    new_frequency = 25.0
    many_roget_sources = {f"ROGET_{i}" for i in range(1, 7)}
    word_specific_sources = {"GSL"}.union(many_roget_sources)

    # --- Update mock attributes directly ---
    atlas.all_words.add(test_word)
    atlas.word_to_idx[test_word] = len(atlas.word_to_idx)
    atlas.frequencies[test_word] = new_frequency

    # Update source lists cache
    for src in word_specific_sources:
        if src not in atlas._source_lists:
            atlas._source_lists[src] = set()
        atlas._source_lists[src].add(test_word)
        # Update available_sources mock path if needed
        if src not in atlas.available_sources:
             atlas.available_sources[src] = Path(f"mock/sources/{src}.json")

    # --- Update side_effects that depend on the data ---
    # (Most side effects in mock_cli_atlas use the atlas attributes directly,
    #  so updating the attributes is often sufficient. But we need to update
    #  get_all_words, get_source_list_names, and maybe re-cache stats)

    new_all_words_list = sorted(list(atlas.all_words))
    atlas.get_all_words.return_value = new_all_words_list

    new_source_names = sorted(list(atlas.available_sources.keys()))
    atlas.get_source_list_names.return_value = new_source_names

    # Recalculate and update stats mock
    new_stats = {
        "total_entries": len(atlas.all_words),
        "single_words": sum(1 for w in atlas.all_words if " " not in w),
        "phrases": sum(1 for w in atlas.all_words if " " in w),
        "entries_with_frequency": len(atlas.frequencies),
        "source_lists": new_source_names,
        "source_coverage": {name: len(words) for name, words in atlas._source_lists.items()}
    }
    atlas.get_stats.return_value = new_stats

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
    # builder.add_by_attribute.return_value = 1 # Removed - Method doesn't exist

    # Configure side effects or specific return values for methods if needed
    def analyze_side_effect(*args, **kwargs):
        # Simulate basic analysis results
        wordlist = builder.words
        total_words = len(wordlist)
        avg_freq = 5.0 if total_words > 0 else 0
        sources = {"GSL": total_words} if total_words > 0 else {}
        return {
            "total_words": total_words,
            "average_frequency": avg_freq,
            "source_counts": sources,
        }
    builder.analyze.side_effect = analyze_side_effect

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
