"""
Wordlist Builder - Tools for creating and managing custom wordlists from the Word Atlas.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, Callable

from word_atlas.atlas import WordAtlas


class WordlistBuilder:
    """Builder for creating custom wordlists using WordAtlas (frequency and sources only)."""

    def __init__(
        self,
        atlas: Optional[WordAtlas] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize the wordlist builder.

        Args:
            atlas: An existing WordAtlas instance, or None to create a new one.
            data_dir: Directory containing the dataset files (only used if atlas is None).
        """
        # Ensure we have a valid WordAtlas instance
        if atlas is None:
            self.atlas = WordAtlas(data_dir=data_dir)
        else:
            # Basic check if the provided atlas seems compatible (has expected methods)
            if not all(
                hasattr(atlas, method)
                for method in [
                    "has_word",
                    "search",
                    "filter",
                    "get_frequency",
                    "get_sources",
                    "get_source_list_names",
                ]
            ):
                raise TypeError(
                    "Provided atlas object does not have the expected methods."
                )
            self.atlas = atlas

        self.words: Set[str] = set()
        self.metadata: Dict[str, Any] = {
            "name": "Custom Wordlist",
            "description": "",
            "creator": "",
            "tags": [],
            "criteria": [],  # Tracks how the list was built
        }

    def add_words(self, words_to_add: Union[List[str], Set[str]]) -> int:
        """Add specific words to the wordlist, checking against the atlas.

        Args:
            words_to_add: List or set of words to add.

        Returns:
            Number of words successfully added (i.e., exist in the atlas index).
        """
        added_count = 0
        valid_words = set()
        for word in words_to_add:
            if self.atlas.has_word(word):
                if word not in self.words:
                    valid_words.add(word)
                    added_count += 1
            # else: word not in atlas, ignore

        if valid_words:
            self.words.update(valid_words)
            self.metadata["criteria"].append(
                {
                    "type": "explicit_words",
                    "count": added_count,
                    "description": f"Added {added_count} valid words explicitly",
                }
            )
        return added_count

    def add_by_search(self, pattern: str, case_sensitive: bool = False) -> int:
        """Add words matching a search pattern.

        Args:
            pattern: Search pattern (substring).
            case_sensitive: Whether the search should be case sensitive.

        Returns:
            Number of words added.
        """
        matching_words = self.atlas.search(pattern, case_sensitive=case_sensitive)
        original_count = len(self.words)
        self.words.update(matching_words)
        added_count = len(self.words) - original_count

        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "search",
                    "pattern": pattern,
                    "case_sensitive": case_sensitive,
                    "count": added_count,
                    "description": f"Added {added_count} words matching '{pattern}' (case_sensitive={case_sensitive})",
                }
            )
        return added_count

    def add_by_source(self, source_name: str) -> int:
        """Add words belonging to a specific source list.

        Args:
            source_name: The name of the source list (e.g., 'GSL', 'AWL').

        Returns:
            Number of words added.

        Raises:
            ValueError: If the source name is not found.
        """
        # filter handles the ValueError if source_name is invalid
        matching_words = self.atlas.filter(sources=[source_name])
        original_count = len(self.words)
        self.words.update(matching_words)
        added_count = len(self.words) - original_count

        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "source",
                    "source": source_name,
                    "count": added_count,
                    "description": f"Added {added_count} words from source '{source_name}'",
                }
            )
        return added_count

    def add_by_frequency(
        self, min_freq: float = 0, max_freq: Optional[float] = None
    ) -> int:
        """Add words within a frequency range.

        Args:
            min_freq: Minimum frequency (inclusive).
            max_freq: Maximum frequency (inclusive, None for no upper limit).

        Returns:
            Number of words added.
        """
        matching_words = self.atlas.filter(min_freq=min_freq, max_freq=max_freq)
        original_count = len(self.words)
        self.words.update(matching_words)
        added_count = len(self.words) - original_count

        if added_count > 0:
            freq_desc = (
                f">= {min_freq}"
                if max_freq is None
                else f"between {min_freq} and {max_freq}"
            )
            self.metadata["criteria"].append(
                {
                    "type": "frequency",
                    "min_freq": min_freq,
                    "max_freq": max_freq,
                    "count": added_count,
                    "description": f"Added {added_count} words with frequency {freq_desc}",
                }
            )
        return added_count

    def remove_words(self, words_to_remove: Union[List[str], Set[str]]) -> int:
        """Remove specific words from the wordlist.

        Args:
            words_to_remove: List or set of words to remove.

        Returns:
            Number of words actually removed from the list.
        """
        original_count = len(self.words)
        self.words.difference_update(words_to_remove)
        removed_count = original_count - len(self.words)

        if removed_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "remove_words",
                    "count": removed_count,
                    "description": f"Removed {removed_count} specific words",
                }
            )
        return removed_count

    def remove_by_search(self, pattern: str, case_sensitive: bool = False) -> int:
        """Remove words matching a search pattern.

        Args:
            pattern: Search pattern (substring).
            case_sensitive: Whether the search should be case sensitive.

        Returns:
            Number of words removed.
        """
        matching_words = self.atlas.search(pattern, case_sensitive=case_sensitive)
        return self.remove_words(
            matching_words
        )  # Delegate removal and criteria logging

    def remove_by_source(self, source_name: str) -> int:
        """Remove words belonging to a specific source list.

        Args:
            source_name: The name of the source list.

        Returns:
            Number of words removed.

        Raises:
            ValueError: If the source name is not found.
        """
        # filter handles the ValueError if source_name is invalid
        words_to_remove = self.atlas.filter(sources=[source_name])
        removed_count = self.remove_words(words_to_remove)  # Delegate removal

        # Add specific criteria for this removal type
        if removed_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "remove_source",
                    "source": source_name,
                    "count": removed_count,
                    "description": f"Attempted removal of {removed_count} words belonging to source '{source_name}'",
                }
            )
        return removed_count

    def get_wordlist(self) -> List[str]:
        """Return the current wordlist as a sorted list."""
        return sorted(list(self.words))

    def set_metadata(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        creator: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Set metadata fields for the wordlist.

        Existing values are overwritten only if a new value is provided.
        Tags are replaced entirely if provided.
        """
        if name is not None:
            self.metadata["name"] = name
        if description is not None:
            self.metadata["description"] = description
        if creator is not None:
            self.metadata["creator"] = creator
        if tags is not None:  # Allow replacing with empty list
            self.metadata["tags"] = tags

    def get_metadata(self) -> Dict[str, Any]:
        """Return the current metadata dictionary."""
        # Return a copy to prevent external modification
        return self.metadata.copy()

    def save(self, filename: Union[str, Path], overwrite: bool = False) -> None:
        """Save the wordlist (words and metadata) to a JSON file.

        Args:
            filename: The path to save the JSON file.
            overwrite: If True, overwrite the file if it exists. Defaults to False.

        Raises:
            FileExistsError: If the file exists and overwrite is False.
            IOError: If there is an error writing the file.
        """
        filepath = Path(filename)
        if filepath.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}")

        save_path = Path(filename)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        wordlist_data = {
            "metadata": self.metadata,
            "words": self.get_wordlist(),  # Save sorted list
        }
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(wordlist_data, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save wordlist to {save_path}: {e}") from e

    @classmethod
    def load(
        cls,
        filename: Union[str, Path],
        atlas: Optional[WordAtlas] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ) -> "WordlistBuilder":
        """Load a wordlist from a JSON file.

        Args:
            filename: Path to the wordlist JSON file.
            atlas: An existing WordAtlas instance, or None to create one.
            data_dir: Data directory (only used if atlas is None).

        Returns:
            A new WordlistBuilder instance populated with the loaded data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not valid JSON or has incorrect structure.
        """
        load_path = Path(filename)
        # Ensure FileNotFoundError is raised if file doesn't exist
        if not load_path.is_file():  # Check if it's a file specifically
            raise FileNotFoundError(
                f"Wordlist file not found or is not a file: {load_path}"
            )

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                wordlist_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in wordlist file {load_path}: {e}") from e
        except Exception as e:
            raise IOError(f"Failed to read wordlist file {load_path}: {e}") from e

        if (
            not isinstance(wordlist_data, dict)
            or "metadata" not in wordlist_data
            or "words" not in wordlist_data
            or not isinstance(wordlist_data["words"], list)
        ):
            raise ValueError(
                f"Invalid wordlist file format in {load_path}. Expected dict with 'metadata' and 'words' list."
            )

        # Create a new builder instance
        builder = cls(atlas=atlas, data_dir=data_dir)

        # Populate metadata directly
        loaded_meta = wordlist_data.get("metadata", {})
        builder.metadata = {
            "name": loaded_meta.get("name", "Loaded Wordlist"),
            "description": loaded_meta.get("description", ""),
            "creator": loaded_meta.get("creator", ""),
            "tags": loaded_meta.get("tags", []),
            "criteria": loaded_meta.get(
                "criteria", []
            ),  # Directly assign loaded criteria
        }

        # Directly assign validated words, don't use add_words
        loaded_words = wordlist_data.get("words", [])
        valid_words = set()
        for word in loaded_words:
            if builder.atlas.has_word(word):
                valid_words.add(word)
            # else: word not in atlas, ignore

        builder.words = valid_words  # Assign the validated set directly

        return builder

    def analyze(self) -> Dict[str, Any]:
        """Analyze the current wordlist (size, frequency, source coverage)."""

        stats: Dict[str, Any] = {
            "size": len(self.words),
            "single_words": 0,
            "phrases": 0,
            "frequency": {  # Added average init
                "total": 0.0,
                "count": 0,
                "average": 0.0,
                "distribution": {},
            },
            "source_coverage": {},
        }

        if not self.words:
            return stats  # Return defaults if wordlist is empty

        all_source_names = self.atlas.get_source_list_names()
        for src_name in all_source_names:
            stats["source_coverage"][src_name] = {"count": 0, "percentage": 0.0}

        for word in self.words:
            # Count single words vs phrases
            if " " in word:
                stats["phrases"] += 1
            else:
                stats["single_words"] += 1

            # Frequency statistics
            frequency = self.atlas.get_frequency(word)
            if frequency is not None:
                stats["frequency"]["total"] += frequency
                stats["frequency"]["count"] += 1
                # Example distribution bins (can be adjusted)
                if frequency <= 10:
                    bin_label = "0-10"
                elif frequency <= 100:
                    bin_label = "11-100"
                elif frequency <= 1000:
                    bin_label = "101-1000"
                else:
                    bin_label = ">1000"
                stats["frequency"]["distribution"][bin_label] = (
                    stats["frequency"]["distribution"].get(bin_label, 0) + 1
                )

            # Source list coverage
            word_sources = self.atlas.get_sources(word)
            for src_name in word_sources:
                # Ensure src_name is valid before incrementing
                if src_name in stats["source_coverage"]:
                    stats["source_coverage"][src_name]["count"] += 1

        # Calculate frequency average
        if stats["frequency"]["count"] > 0:
            stats["frequency"]["average"] = (
                stats["frequency"]["total"] / stats["frequency"]["count"]
            )
        # else: average remains 0.0

        # Calculate source percentages
        total_words = len(self.words)
        # Check total_words > 0 before division
        if total_words > 0:
            for src_name in stats["source_coverage"]:
                count = stats["source_coverage"][src_name]["count"]
                stats["source_coverage"][src_name]["percentage"] = (
                    count / total_words
                ) * 100

        return stats

    def export_text(
        self,
        filename: Union[str, Path],
        include_metadata: bool = True,
        sort_key: Optional[Callable[[str], Any]] = None,
        word_format: Optional[Callable[[str], str]] = None,
    ) -> None:
        """Export the wordlist to a plain text file.

        Args:
            filename: Path to the output text file.
            include_metadata: Whether to include metadata as comments at the top.
            sort_key: Optional function to sort words before saving.
            word_format: Optional function to format each word before saving.
        """
        export_path = Path(filename)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        words_to_export = list(self.words)
        if sort_key:
            words_to_export.sort(key=sort_key)
        else:
            words_to_export.sort()  # Default sort alphabetically

        try:
            with open(export_path, "w", encoding="utf-8") as f:
                if include_metadata:
                    f.write(f"# Wordlist Name: {self.metadata.get('name', 'N/A')}\n")
                    f.write(
                        f"# Description: {self.metadata.get('description', 'N/A')}\n"
                    )
                    f.write(f"# Creator: {self.metadata.get('creator', 'N/A')}\n")
                    f.write(f"# Tags: {self.metadata.get('tags', [])}\n")
                    f.write(f"# Criteria: {self.metadata.get('criteria', [])}\n")
                    f.write(f"# Total Words: {len(words_to_export)}\n\n")

                for word in words_to_export:
                    formatted_word = word_format(word) if word_format else word
                    f.write(f"{formatted_word}\n")
        except Exception as e:
            raise IOError(f"Failed to export wordlist to {export_path}: {e}") from e

    def __len__(self) -> int:
        """Return the number of words in the wordlist."""
        return len(self.words)

    def clear(self) -> None:
        """Remove all words and reset criteria from the wordlist."""
        self.words.clear()
        self.metadata["criteria"] = []

    def get_size(self) -> int:
        """Return the number of words currently in the wordlist."""
        return len(self.words)
