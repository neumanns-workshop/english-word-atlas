"""
Word Atlas - Main interface for working with the English Word Atlas dataset.
"""

from pathlib import Path
import re
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json
import os
import sys  # Added for warnings

from word_atlas.data import get_data_dir, get_word_index, get_word_frequencies


class WordAtlas:
    """Main interface for the English Word Atlas dataset (word index, frequency, sources ONLY)."""

    def __init__(self, data_dir: Union[str, Path, None] = None):
        """Initialize the Word Atlas with the dataset.

        Args:
            data_dir: Directory containing the dataset files (word_index.json,
                frequencies/word_frequencies.json, sources/ directory).
                If None, searches common locations.

        Raises:
            FileNotFoundError: If the required dataset files cannot be found
        """
        self.data_dir = get_data_dir(data_dir)
        self._load_data()

    def _load_data(self):
        """Load the core dataset components (index, frequencies, sources)."""
        self.word_to_idx = get_word_index(self.data_dir)
        self.frequencies = get_word_frequencies(self.data_dir)
        self.all_words = set(self.word_to_idx.keys())

        self.sources_dir = self.data_dir / "sources"
        self.available_sources = self._discover_sources()
        self._source_lists = {}  # Cache for loaded source lists (Set[str])
        self._load_all_sources()  # Load all sources into cache at init

    def _discover_sources(self) -> Dict[str, Path]:
        """Scan the data/sources directory recursively for source files (*.json or *.txt).
        Source names are generated as 'subdirectory_filestem' (e.g., 'GSL_NEW',
        'AFINN_NEG_5') or just 'filestem' if the file is directly in data/sources/.
        """
        sources = {}
        if not (self.sources_dir.exists() and self.sources_dir.is_dir()):
            print(
                f"Warning: Sources directory not found or is not a directory: {self.sources_dir}",
                file=sys.stderr,
            )
            return sources

        # Scan for both .json and .txt files recursively
        for extension in ["*.json", "*.txt"]:
            # Use rglob to search recursively
            for file_path in self.sources_dir.rglob(extension):
                # Determine the source name based on location
                relative_path = file_path.relative_to(self.sources_dir)
                file_stem = file_path.stem  # e.g., 'NEW', 'NEG_5'

                if len(relative_path.parts) > 1:  # File is in a subdirectory
                    subdir_name = relative_path.parts[0]  # e.g., 'GSL', 'AFINN'
                    # Combine subdirectory and stem for the internal source name
                    source_name = f"{subdir_name}_{file_stem}"
                else:  # File is directly in sources_dir
                    source_name = file_stem

                if source_name in sources:
                    # Handle potential duplicates
                    # If paths are different, it's a true name collision. If paths are same, it's just txt vs json.
                    if sources[source_name] != file_path:
                        print(
                            f"Warning: Duplicate source name '{source_name}' generated.",
                            file=sys.stderr,
                        )
                        print(f"  Existing: {sources[source_name]}", file=sys.stderr)
                        print(f"  New (ignored): {file_path}", file=sys.stderr)
                    # If paths are the same (just different extension), we implicitly keep the first one found.
                else:
                    sources[source_name] = file_path
                    # print(f"Discovered source: '{source_name}' -> {file_path}") # Debugging
        return sources

    def _load_all_sources(self):
        """Load all discovered source lists (.json or *.txt) into the cache."""
        for source_name, file_path in self.available_sources.items():
            source_list_words = set()
            unknown_words = set()
            invalid_items = 0
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if file_path.suffix == ".json":
                        source_data = json.load(f)
                        if isinstance(source_data, list):
                            for item in source_data:
                                if isinstance(item, str):
                                    if self.has_word(item):
                                        source_list_words.add(item)
                                    else:
                                        unknown_words.add(item)
                                else:
                                    invalid_items += 1
                        else:
                            print(
                                f"Warning: Source JSON '{source_name}' ignored (not a JSON list).",
                                file=sys.stderr,
                            )
                            continue  # Skip to next source
                    elif file_path.suffix == ".txt":
                        for line in f:
                            word = line.strip()
                            if word and not word.startswith(
                                "#"
                            ):  # Ignore empty lines and comments
                                if self.has_word(word):
                                    source_list_words.add(word)
                                else:
                                    unknown_words.add(word)
                    else:
                        # Should not happen due to discovery filter, but safeguard
                        print(
                            f"Warning: Unknown source file type for '{source_name}': {file_path.suffix}",
                            file=sys.stderr,
                        )
                        continue

            except FileNotFoundError:
                print(
                    f"Warning: Source file '{source_name}' disappeared before loading: {file_path}",
                    file=sys.stderr,
                )
            except json.JSONDecodeError as e:
                print(
                    f"Warning: Could not parse source JSON '{source_name}' from {file_path}: {e}",
                    file=sys.stderr,
                )
            except Exception as e:  # Catch other potential read errors
                print(
                    f"Warning: Could not load source '{source_name}' from {file_path}: {e}",
                    file=sys.stderr,
                )

            # Report warnings after processing file
            if invalid_items:
                print(
                    f"Warning: Source '{source_name}' contained {invalid_items} non-string items.",
                    file=sys.stderr,
                )
            if unknown_words:
                print(
                    f"Warning: Source '{source_name}' contains {len(unknown_words)} words not found in master index (e.g., '{next(iter(unknown_words))}'). These will be ignored.",
                    file=sys.stderr,
                )

            # Store the successfully loaded and validated words
            self._source_lists[source_name] = source_list_words

    # ---- Basic Data Retrieval ----

    def has_word(self, word: str) -> bool:
        """Check if a word exists in the master index."""
        return word in self.all_words

    def get_all_words(self) -> List[str]:
        """Get a sorted list of all words in the master index."""
        return sorted(list(self.all_words))

    def get_frequency(self, word: str) -> Optional[float]:
        """Get the frequency for a word."""
        # Frequencies might be stored case-insensitively, check lowercase
        return self.frequencies.get(word.lower())

    def get_sources(self, word: str) -> List[str]:
        """Return a list of source names containing the given word."""
        if word not in self.word_to_idx:
            raise KeyError(f"Word '{word}' not found in the main index.")
        # Only return sources where the word is present AND exists in the master index
        return sorted(
            [name for name, words in self._source_lists.items() if word in words]
        )

    def get_source_list_names(self) -> List[str]:
        """Get a sorted list of all available source list names."""
        return sorted(list(self.available_sources.keys()))

    def get_words_in_source(self, source_name: str) -> Set[str]:
        """Get the set of words belonging to a specific source list.
        Words returned are guaranteed to exist in the master index.
        """
        if source_name not in self._source_lists:
            if source_name not in self.available_sources:
                raise ValueError(f"Source '{source_name}' not found.")
            else:
                # Source exists but failed to load or was invalid
                print(
                    f"Warning: Returning empty set for source '{source_name}' which failed to load or was invalid.",
                    file=sys.stderr,
                )
                return set()
        # Return the cached set (already filtered for master index membership)
        return self._source_lists[source_name]

    # ---- Search and Filtering ----

    def search(self, pattern: str, case_sensitive: bool = False) -> List[str]:
        """Search for words matching a pattern (substring search)."""
        if not case_sensitive:
            pattern = pattern.lower()
            return [word for word in self.all_words if pattern in word.lower()]
        else:
            return [word for word in self.all_words if pattern in word]

    def filter(
        self,
        sources: Optional[List[str]] = None,
        min_freq: Optional[float] = None,
        max_freq: Optional[float] = None,
    ) -> Set[str]:
        """Filter words based on source lists and frequency.

        Args:
            sources: List of source list names. Word must be in ALL listed sources.
            min_freq: Minimum frequency (inclusive).
            max_freq: Maximum frequency (inclusive).

        Returns:
            Set of words matching ALL specified criteria.
        """
        # Start with all words if no criteria specified, otherwise start filtering
        if not any([sources, min_freq is not None, max_freq is not None]):
            return self.all_words.copy()

        filtered_words = self.all_words.copy()

        # 1. Filter by Source Lists (Intersection)
        if sources:
            source_intersection = set()
            first_source = True
            for src_name in sources:
                # get_words_in_source handles errors and returns set() of known words
                words_in_src = self.get_words_in_source(src_name)
                if first_source:
                    source_intersection.update(words_in_src)
                    first_source = False
                else:
                    source_intersection.intersection_update(words_in_src)
                    # Optimization: if intersection is empty, no need to check more sources
                    if not source_intersection:
                        return set()
            filtered_words.intersection_update(source_intersection)
            if not filtered_words:
                return set()  # Early exit if no words match sources

        # 2. Filter by Frequency
        if min_freq is not None or max_freq is not None:
            freq_matches = set()
            min_f = min_freq if min_freq is not None else -float("inf")
            max_f = max_freq if max_freq is not None else float("inf")

            for word in filtered_words:
                freq = self.get_frequency(word)
                if freq is not None:
                    if min_f <= freq <= max_f:
                        freq_matches.add(word)
            filtered_words.intersection_update(freq_matches)

        return filtered_words

    # ---- Statistics ----

    def get_stats(self) -> dict:
        """Calculate and return statistics about the loaded dataset."""
        # Initialize stats with defaults
        stats = {
            "total_words": 0,
            "total_phrases": 0,
            "total_entries": 0,
            "coverage": {},
        }
        # No need for separate counters now
        # total_words = 0
        # total_phrases = 0
        words_by_source = {source: set() for source in self.get_source_list_names()}

        for word, data in self.word_to_idx.items():
            is_phrase = " " in word
            if is_phrase:
                stats["total_phrases"] += 1
            else:
                stats["total_words"] += 1

            # Correctly get sources for the word
            # sources = data.get("sources", []) # INCORRECT: data is index (int)
            sources = self.get_sources(word)  # CORRECT: Use the method

            for source in sources:
                if source in words_by_source:
                    words_by_source[source].add(word)

        stats["total_entries"] = stats["total_words"] + stats["total_phrases"]

        # Calculate coverage percentage for each source list
        stats["coverage"] = {
            source: (
                len(words_in_source) / stats["total_entries"] * 100
                if stats["total_entries"] > 0  # Use the value from stats dict
                else 0
            )
            for source, words_in_source in words_by_source.items()
        }

        # Add embedding dimension if present
        # ... existing code ...

        return stats

    # ---- Utility Methods ----
    def __len__(self) -> int:
        """Return the total number of unique words in the master index."""
        return len(self.all_words)

    def __contains__(self, word: str) -> bool:
        """Check if a word is in the master index."""
        return word in self.all_words
