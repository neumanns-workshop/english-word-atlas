"""
Wordlist Builder - Tools for creating and managing custom wordlists from the Word Atlas.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, Callable

from word_atlas.atlas import WordAtlas


class WordlistBuilder:
    """Builder for creating custom wordlists from the Word Atlas dataset."""

    def __init__(
        self,
        atlas: Optional[WordAtlas] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize the wordlist builder.

        Args:
            atlas: An existing WordAtlas instance, or None to create a new one
            data_dir: Directory containing the dataset files (only used if atlas is None)
        """
        self.atlas = atlas or WordAtlas(data_dir)
        self.words: Set[str] = set()
        self.metadata: Dict[str, Any] = {
            "name": "Custom Wordlist",
            "description": "",
            "creator": "",
            "tags": [],
            "criteria": [],
        }

    def add_words(self, words: List[str]) -> int:
        """Add specific words to the wordlist.

        Args:
            words: List of words to add

        Returns:
            Number of words successfully added (existing in the dataset)
        """
        valid_words = [w for w in words if self.atlas.has_word(w)]
        self.words.update(valid_words)

        # Record the criteria
        if valid_words:
            self.metadata["criteria"].append(
                {
                    "type": "explicit_words",
                    "count": len(valid_words),
                    "description": f"Explicitly added {len(valid_words)} words",
                }
            )

        return len(valid_words)

    def add_by_search(self, pattern: str) -> int:
        """Add words matching a search pattern.

        Args:
            pattern: Search pattern (regex or substring)

        Returns:
            Number of words added
        """
        matching_words = self.atlas.search(pattern)
        original_count = len(self.words)
        self.words.update(matching_words)

        # Record the criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "search",
                    "pattern": pattern,
                    "count": added_count,
                    "description": f"Added {added_count} words matching '{pattern}'",
                }
            )

        return added_count

    def add_by_attribute(self, attribute: str, value: Any = True) -> int:
        """Add words with a specific attribute.

        Args:
            attribute: Attribute name (e.g., 'ROGET_123', 'GSL')
            value: Required attribute value (default: True)

        Returns:
            Number of words added
        """
        matching_words = self.atlas.filter_by_attribute(attribute, value)
        original_count = len(self.words)
        self.words.update(matching_words)

        # Record the criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "attribute",
                    "attribute": attribute,
                    "value": str(value),
                    "count": added_count,
                    "description": f"Added {added_count} words with attribute {attribute}={value}",
                }
            )

        return added_count

    def add_by_frequency(
        self, min_freq: float = 0, max_freq: Optional[float] = None
    ) -> int:
        """Add words within a frequency range.

        Args:
            min_freq: Minimum frequency
            max_freq: Maximum frequency (None for no upper limit)

        Returns:
            Number of words added
        """
        matching_words = self.atlas.filter_by_frequency(min_freq, max_freq)
        original_count = len(self.words)
        self.words.update(matching_words)

        # Record the criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            freq_desc = (
                f">= {min_freq}" if max_freq is None else f"{min_freq}-{max_freq}"
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

    def add_by_syllable_count(self, count: int) -> int:
        """Add words with a specific syllable count.

        Args:
            count: Number of syllables

        Returns:
            Number of words added
        """
        matching_words = self.atlas.filter_by_syllable_count(count)
        original_count = len(self.words)
        self.words.update(matching_words)

        # Record the criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "syllable_count",
                    "count": count,
                    "added": added_count,
                    "description": f"Added {added_count} words with {count} syllables",
                }
            )

        return added_count

    def add_by_custom_filter(
        self, filter_func: Callable[[str, Dict[str, Any]], bool], description: str
    ) -> int:
        """Add words using a custom filter function.

        Args:
            filter_func: Function that takes a word and its attributes and returns True to include
            description: Description of the filter for the metadata

        Returns:
            Number of words added
        """
        matching_words = set()
        for word, attributes in self.atlas.word_data.items():
            if filter_func(word, attributes):
                matching_words.add(word)

        original_count = len(self.words)
        self.words.update(matching_words)

        # Record the criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "custom_filter",
                    "count": added_count,
                    "description": f"Added {added_count} words using custom filter: {description}",
                }
            )

        return added_count

    def add_similar_words(self, word: str, n: int = 10) -> int:
        """Add words similar to a given word.

        Args:
            word: Target word to find similar words for
            n: Number of similar words to add

        Returns:
            Number of words added
        """
        if not self.atlas.has_word(word):
            return 0

        similar_words = self.atlas.get_similar_words(word, n)
        words_to_add = [w for w, _ in similar_words]

        original_count = len(self.words)
        self.add_words(words_to_add)

        # Add criteria
        added_count = len(self.words) - original_count
        if added_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "similar_words",
                    "target_word": word,
                    "count": added_count,
                    "description": f"Added {added_count} words similar to '{word}'",
                }
            )

        return added_count

    def remove_words(self, words: List[str]) -> int:
        """Remove specific words from the wordlist.

        Args:
            words: List of words to remove

        Returns:
            Number of words removed
        """
        original_count = len(self.words)
        self.words.difference_update(words)

        # Record the criteria
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

    def remove_by_search(self, pattern: str) -> int:
        """Remove words matching a search pattern.

        Args:
            pattern: Search pattern (regex or substring)

        Returns:
            Number of words removed
        """
        matching_words = self.atlas.search(pattern)
        original_count = len(self.words)
        self.words.difference_update(matching_words)

        # Record the criteria
        removed_count = original_count - len(self.words)
        if removed_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "remove_search",
                    "pattern": pattern,
                    "count": removed_count,
                    "description": f"Removed {removed_count} words matching '{pattern}'",
                }
            )

        return removed_count

    def remove_by_attribute(self, attribute: str, value: Any = True) -> int:
        """Remove words with a specific attribute.

        Args:
            attribute: Attribute name (e.g., 'ROGET_123', 'GSL')
            value: Required attribute value (default: True)

        Returns:
            Number of words removed
        """
        matching_words = self.atlas.filter_by_attribute(attribute, value)
        original_count = len(self.words)
        self.words.difference_update(matching_words)

        # Record the criteria
        removed_count = original_count - len(self.words)
        if removed_count > 0:
            self.metadata["criteria"].append(
                {
                    "type": "remove_attribute",
                    "attribute": attribute,
                    "value": str(value),
                    "count": removed_count,
                    "description": f"Removed {removed_count} words with attribute {attribute}={value}",
                }
            )

        return removed_count

    def get_wordlist(self) -> List[str]:
        """Get the current wordlist.

        Returns:
            Sorted list of words in the wordlist
        """
        return sorted(list(self.words))

    def set_metadata(
        self,
        name: str = None,
        description: str = None,
        creator: str = None,
        tags: List[str] = None,
    ) -> None:
        """Set metadata for the wordlist.

        Args:
            name: Wordlist name
            description: Wordlist description
            creator: Creator name/ID
            tags: List of tags for categorization
        """
        if name is not None:
            self.metadata["name"] = name
        if description is not None:
            self.metadata["description"] = description
        if creator is not None:
            self.metadata["creator"] = creator
        if tags is not None:
            self.metadata["tags"] = tags

    def get_metadata(self) -> Dict[str, Any]:
        """Get the wordlist metadata.

        Returns:
            Dictionary with metadata
        """
        # Add current size to metadata
        metadata = self.metadata.copy()
        metadata["size"] = len(self.words)
        return metadata

    def save(self, filename: Union[str, Path]) -> None:
        """Save the wordlist to a JSON file.

        Args:
            filename: Path to save the wordlist to
        """
        filename = Path(filename)
        # Make sure the directory exists
        os.makedirs(filename.parent, exist_ok=True)

        data = {"metadata": self.get_metadata(), "words": list(self.words)}

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(
        cls,
        filename: Union[str, Path],
        atlas: Optional[WordAtlas] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ) -> "WordlistBuilder":
        """Load a wordlist from a JSON file.

        Args:
            filename: Path to the wordlist JSON file
            atlas: Optional existing WordAtlas instance
            data_dir: Directory containing dataset files (only used if atlas is None)

        Returns:
            New WordlistBuilder instance with the loaded wordlist
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create a new builder
        builder = cls(atlas, data_dir)

        # Load metadata
        if "metadata" in data:
            metadata = data["metadata"]
            builder.set_metadata(
                name=metadata.get("name"),
                description=metadata.get("description"),
                creator=metadata.get("creator"),
                tags=metadata.get("tags"),
            )

            # Copy criteria if available
            if "criteria" in metadata and isinstance(metadata["criteria"], list):
                builder.metadata["criteria"] = metadata["criteria"]

        # Add words
        builder.add_words(data["words"])

        return builder

    def analyze(self) -> Dict[str, Any]:
        """Analyze the wordlist and provide statistics.

        Returns:
            Dictionary with statistics about the wordlist
        """
        if not self.words:
            return {"size": 0}

        # Basic stats
        stats = {
            "size": len(self.words),
            "single_words": sum(1 for w in self.words if " " not in w),
            "phrases": sum(1 for w in self.words if " " in w),
        }

        # Syllable distribution
        syllable_counts = {}
        for word in self.words:
            word_data = self.atlas.get_word(word)
            if "SYLLABLE_COUNT" in word_data:
                count = word_data["SYLLABLE_COUNT"]
                syllable_counts[count] = syllable_counts.get(count, 0) + 1

        stats["syllable_distribution"] = {
            str(count): value for count, value in sorted(syllable_counts.items())
        }

        # Identify all wordlist attributes in the data
        wordlist_attributes = {}
        for attr in self.atlas.word_data.get(next(iter(self.atlas.word_data)), {}):
            if (
                attr.startswith("GSL_")
                or attr.startswith("SWADESH_")
                or attr.startswith("NGSL_")
                or attr.startswith("OGDEN_")
                or attr == "GSL"
                or attr == "SWADESH"
                or attr == "NGSL"
                or attr == "OGDEN"
            ):
                wordlist_attributes[attr] = 0

        # Count words in each wordlist
        for word in self.words:
            word_data = self.atlas.get_word(word)
            for attr in wordlist_attributes:
                if attr in word_data and word_data[attr]:
                    wordlist_attributes[attr] += 1

        # Format the wordlist coverage stats
        stats["wordlist_coverage"] = {
            attr: {
                "count": count,
                "percentage": (
                    round(count / len(self.words) * 100, 1) if self.words else 0
                ),
            }
            for attr, count in wordlist_attributes.items()
        }

        # Frequency stats
        freq_buckets = {"0": 0, "1-10": 0, "11-100": 0, "101-1000": 0, ">1000": 0}
        total_freq = 0
        freq_words = 0

        for word in self.words:
            word_data = self.atlas.get_word(word)
            if "FREQ_GRADE" in word_data:
                freq = word_data["FREQ_GRADE"]
                total_freq += freq
                freq_words += 1

                if freq == 0:
                    freq_buckets["0"] += 1
                elif freq <= 10:
                    freq_buckets["1-10"] += 1
                elif freq <= 100:
                    freq_buckets["11-100"] += 1
                elif freq <= 1000:
                    freq_buckets["101-1000"] += 1
                else:
                    freq_buckets[">1000"] += 1

        # Store raw counts for programmatic access
        freq_distribution = {}
        for bucket, count in freq_buckets.items():
            freq_distribution[bucket] = count

        stats["frequency"] = {
            "distribution": freq_distribution,
            "average": round(total_freq / freq_words, 2) if freq_words > 0 else 0,
        }

        return stats

    def export_text(
        self,
        filename: Union[str, Path],
        include_metadata: bool = True,
        sort_key: Optional[Callable[[str], Any]] = None,
        word_format: Optional[Callable[[str], str]] = None,
    ) -> None:
        """Export the wordlist to a text file (one word per line).

        Args:
            filename: Path to save the wordlist to
            include_metadata: Whether to include metadata as comments
            sort_key: Optional function to use as sort key (default: alphabetical)
            word_format: Optional function to format words before writing
        """
        filename = Path(filename)
        # Make sure the directory exists
        os.makedirs(filename.parent, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            # Write metadata as comments if requested
            if include_metadata:
                f.write(f"# {self.metadata['name']}\n")
                if self.metadata["description"]:
                    f.write(f"# Description: {self.metadata['description']}\n")
                if self.metadata["creator"]:
                    f.write(f"# Creator: {self.metadata['creator']}\n")
                if self.metadata["tags"]:
                    f.write(f"# Tags: {', '.join(self.metadata['tags'])}\n")
                f.write(f"# Size: {len(self.words)} words\n")
                f.write("#\n")

            # Write words (one per line)
            words = sorted(self.words, key=sort_key) if sort_key else sorted(self.words)
            for word in words:
                formatted_word = word_format(word) if word_format else word
                f.write(f"{formatted_word}\n")

    def __len__(self) -> int:
        """Return the number of words in the wordlist."""
        return len(self.words)

    def clear(self) -> None:
        """Clear the wordlist, removing all words and criteria."""
        self.words.clear()
        self.metadata["criteria"] = []  # Clear criteria history

    def get_size(self) -> int:
        """Get the number of words in the wordlist.

        Returns:
            Number of words in the wordlist
        """
        return len(self.words)
