"""
Command-line interface for the English Word Atlas.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

from word_atlas.atlas import WordAtlas
from word_atlas.wordlist import WordlistBuilder


def info_command(args):
    """Show information about a word or phrase."""
    atlas = WordAtlas(args.data_dir)

    if not atlas.has_word(args.word):
        print(f"Word or phrase '{args.word}' not found in the dataset.")
        sys.exit(1)

    word_info = atlas.get_word(args.word)

    if args.json:
        try:
            # Remove embedding to save space
            if "EMBEDDINGS_ALL_MINILM_L6_V2" in word_info:
                word_info_copy = word_info.copy()
                del word_info_copy["EMBEDDINGS_ALL_MINILM_L6_V2"]
            else:
                word_info_copy = word_info
            print(json.dumps(word_info_copy, indent=2))
        except TypeError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        return

    # Print basic information
    print(f"Information for '{args.word}':")

    if "SYLLABLE_COUNT" in word_info:
        print(f"  Syllables: {word_info['SYLLABLE_COUNT']}")

    if "ARPABET" in word_info:
        print(f"  Pronunciation: /{word_info['ARPABET'][0]}/")

    if "FREQ_COUNT" in word_info:
        print(f"  Frequency count: {word_info['FREQ_COUNT']:.2f}")

    if "FREQ_GRADE" in word_info:
        print(f"  Frequency grade: {word_info['FREQ_GRADE']:.2f}")

    # Check if word is in various lists
    wordlists = []
    for list_name in ["OGDEN", "GSL", "NGSL", "SWADESH"]:
        if list_name in word_info and word_info[list_name]:
            wordlists.append(list_name)

    if wordlists:
        print(f"  In wordlists: {', '.join(wordlists)}")

    # Show Roget categories
    categories = [
        key for key in word_info if key.startswith("ROGET_") and word_info[key]
    ]
    if categories:
        print(f"  Roget categories: {len(categories)}")
        for cat in sorted(categories)[:5]:
            print(f"    - {cat}")
        if len(categories) > 5:
            print(f"    - ... and {len(categories) - 5} more")

    # Find similar words
    if not args.no_similar:
        print("\nSimilar words/phrases:")
        similar = atlas.get_similar_words(args.word, n=5)
        for similar_word, score in similar:
            print(f"  {similar_word}: {score:.4f}")


def search_command(args):
    """Search for words/phrases matching a pattern."""
    atlas = WordAtlas(args.data_dir)

    results = atlas.search(args.pattern)

    # Filter by attribute if specified
    if args.attribute:
        attr_name, _, value = args.attribute.partition("=")
        if value:
            # Handle boolean values
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            # Handle numeric values
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)

            results = [
                w
                for w in results
                if atlas.has_word(w)
                and attr_name in atlas.get_word(w)
                and atlas.get_word(w)[attr_name] == value
            ]
        else:
            # Just check if attribute exists and is truthy
            results = [
                w
                for w in results
                if atlas.has_word(w)
                and attr_name in atlas.get_word(w)
                and atlas.get_word(w)[attr_name]
            ]

    # Filter by frequency if specified
    if args.min_freq is not None:
        results = [
            w
            for w in results
            if atlas.has_word(w)
            and "FREQ_GRADE" in atlas.get_word(w)
            and atlas.get_word(w)["FREQ_GRADE"] >= args.min_freq
        ]

    if args.max_freq is not None:
        results = [
            w
            for w in results
            if atlas.has_word(w)
            and "FREQ_GRADE" in atlas.get_word(w)
            and atlas.get_word(w)["FREQ_GRADE"] <= args.max_freq
        ]

    # Filter phrases or single words if specified
    if args.phrases_only:
        results = [w for w in results if " " in w]
    elif args.words_only:
        results = [w for w in results if " " not in w]

    # Limit results
    if args.limit:
        results = results[: args.limit]

    # Print results
    print(f"Found {len(results)} matches:")
    for result in results:
        if args.verbose:
            word_info = atlas.get_word(result)
            freq = word_info.get("FREQ_GRADE", 0)
            syl = word_info.get("SYLLABLE_COUNT", "?")
            print(f"  {result} (freq: {freq:.1f}, syl: {syl})")
        else:
            print(f"  {result}")


def stats_command(args):
    """Show statistics about the dataset."""
    atlas = WordAtlas(args.data_dir)

    try:
        stats = atlas.get_stats()
        print("English Word Atlas Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Single words: {stats['single_words']}")
        print(f"  Phrases: {stats['phrases']}")
        print(f"  Embedding dimensions: {stats['embedding_dim']}")

        # Count by syllables
        if not args.basic:
            print("\nSyllable distribution:")
            syllable_counts = {}
            for count in atlas.get_syllable_counts():
                syllable_counts[count] = len(atlas.filter_by_syllable_count(count))

            for count in sorted(syllable_counts.keys()):
                print(f"  {count} syllable(s): {syllable_counts[count]}")

            # Count by frequency buckets
            print("\nFrequency distribution:")
            freq_buckets = {"0": 0, "1-10": 0, "11-100": 0, "101-1000": 0, ">1000": 0}

            for word, info in atlas.word_data.items():
                if "FREQ_GRADE" in info:
                    freq = info["FREQ_GRADE"]
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

            for bucket, count in freq_buckets.items():
                print(f"  Frequency {bucket}: {count}")

            # Count by wordlists
            print("\nWordlist coverage:")
            wordlists = {"OGDEN": 0, "GSL": 0, "NGSL": 0, "SWADESH": 0}

            for list_name in wordlists:
                wordlists[list_name] = len(atlas.filter_by_attribute(list_name))

            for list_name, count in wordlists.items():
                print(
                    f"  {list_name}: {count} words ({count/stats['total_entries']*100:.1f}%)"
                )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def wordlist_create_command(args):
    """Create a new wordlist."""
    atlas = WordAtlas(args.data_dir)
    builder = WordlistBuilder(atlas)

    # Set metadata
    builder.set_metadata(
        name=args.name,
        description=args.description,
        creator=args.creator,
        tags=args.tags.split(",") if args.tags else [],
    )

    # Add words based on criteria
    if args.search_pattern:
        added = builder.add_by_search(args.search_pattern)
        print(f"Added {added} words matching pattern '{args.search_pattern}'")

    if args.attribute:
        try:
            # Parse attribute=value format
            if "=" in args.attribute:
                attr_name, value = args.attribute.split("=", 1)
                # Convert value to appropriate type
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)
            else:
                attr_name = args.attribute
                value = True

            added = builder.add_by_attribute(attr_name, value)
            print(
                f"Added {added} words with attribute {args.attribute}"
            )  # Use original attribute string
        except ValueError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    if args.syllables:
        added = builder.add_by_syllable_count(args.syllables)
        print(f"Added {added} words with {args.syllables} syllables")

    if args.min_freq is not None:
        added = builder.add_by_frequency(args.min_freq, args.max_freq)
        print(f"Added {added} words with frequency {args.min_freq}-{args.max_freq}")

    if args.similar_to:
        similar_count = args.similar_count or 10
        added = builder.add_similar_words(args.similar_to, similar_count)
        print(f"Added {added} words similar to '{args.similar_to}'")

    # Save the wordlist
    builder.save(args.output)
    print(f"Wordlist saved to '{args.output}' with {len(builder.words)} words")

    # Analyze the wordlist
    if not args.no_analyze:
        stats = builder.analyze()
        print("\nWordlist statistics:")
        print(f"  Total entries: {stats['size']}")
        print(f"  Single words: {stats['single_words']}")
        print(f"  Phrases: {stats['phrases']}")


def wordlist_modify_command(args):
    """Modify an existing wordlist."""
    atlas = WordAtlas(args.data_dir)

    # Load existing wordlist
    try:
        builder = WordlistBuilder.load(args.wordlist, atlas)
        print(
            f"Loaded wordlist '{builder.metadata['name']}' with {builder.get_size()} words"
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading wordlist: {e}")
        sys.exit(1)

    # Update metadata if provided
    if any([args.name, args.description, args.creator, args.tags]):
        builder.set_metadata(
            name=args.name,
            description=args.description,
            creator=args.creator,
            tags=args.tags.split(",") if args.tags else None,
        )
        print("Updated wordlist metadata")

    # Add words from criteria
    total_modified = 0

    if args.add:
        added = builder.add_words(set(args.add))
        print(f"Added {added} words to the wordlist")
        total_modified += added

    if hasattr(args, "add_pattern") and args.add_pattern:
        added = builder.add_by_search(args.add_pattern)
        print(f"Added {added} words matching pattern '{args.add_pattern}'")
        total_modified += added

    if hasattr(args, "add_attribute") and args.add_attribute:
        attr_name, _, value = args.add_attribute.partition("=")
        if value:
            # Handle boolean values
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False

            added = builder.add_by_attribute(attr_name, value)
        else:
            added = builder.add_by_attribute(attr_name)

        print(f"Added {added} words with attribute {args.add_attribute}")
        total_modified += added

    if hasattr(args, "add_similar_to") and args.add_similar_to:
        if not atlas.has_word(args.add_similar_to):
            print(f"Error: Word '{args.add_similar_to}' not found in the dataset")
        else:
            n = args.similar_count or 10
            added = builder.add_similar_words(args.add_similar_to, n)
            print(f"Added {added} words similar to '{args.add_similar_to}'")
            total_modified += added

    if args.remove:
        removed = builder.remove_words(set(args.remove))
        print(f"Removed {removed} words from the wordlist")
        total_modified += removed

    if hasattr(args, "remove_pattern") and args.remove_pattern:
        # Find words to remove
        to_remove = atlas.search(args.remove_pattern)
        removed = builder.remove_words(to_remove)
        print(f"Removed {removed} words matching pattern '{args.remove_pattern}'")
        total_modified += removed

    # Save the wordlist
    if args.output:
        output_path = args.output
    else:
        output_path = args.wordlist

    try:
        builder.save(output_path)
        print(f"Wordlist saved to '{output_path}' with {builder.get_size()} words")
    except Exception as e:
        print(f"Error saving wordlist: {e}")
        sys.exit(1)


def wordlist_analyze_command(args):
    """Analyze a wordlist and show statistics."""
    atlas = WordAtlas(args.data_dir)

    # Load existing wordlist
    try:
        builder = WordlistBuilder.load(args.wordlist, atlas)
        print(
            f"Analyzing wordlist '{builder.metadata['name']}' with {builder.get_size()} words"
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading wordlist: {e}")
        sys.exit(1)

    # Perform analysis
    analysis = builder.analyze()

    # Print analysis
    print("\nBasic statistics:")
    print(f"  Total words: {analysis['size']}")
    print(f"  Single words: {analysis['single_words']}")
    print(f"  Phrases: {analysis['phrases']}")

    # Syllable distribution
    if "syllable_distribution" in analysis:
        print("\nSyllable distribution:")
        for count, num in analysis["syllable_distribution"].items():
            print(
                f"  {count} syllable(s): {num} words ({num/analysis['size']*100:.1f}%)"
            )

    # Frequency distribution
    if "frequency" in analysis:
        print("\nFrequency distribution:")
        for bucket, count in analysis["frequency"]["distribution"].items():
            percentage = count / analysis["size"] * 100 if analysis["size"] > 0 else 0
            print(f"  Frequency {bucket}: {count} words ({percentage:.1f}%)")
        print(f"  Average frequency: {analysis['frequency']['average']}")

    # Wordlist coverage
    if "wordlist_coverage" in analysis:
        print("\nWordlist coverage:")
        for list_name, data in analysis["wordlist_coverage"].items():
            print(f"  {list_name}: {data['count']} words ({data['percentage']}%)")

    # Export analysis if requested
    if args.export:
        try:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            print(f"\nAnalysis exported to '{args.export}'")
        except Exception as e:
            print(f"Error exporting analysis: {e}")
            sys.exit(1)

    # Export wordlist in text format if requested
    if args.export_text:
        try:
            builder.export_text(args.export_text)
            print(f"\nWordlist exported to '{args.export_text}'")
        except Exception as e:
            print(f"Error exporting wordlist: {e}")
            sys.exit(1)


def wordlist_merge_command(args):
    """Merge multiple wordlists."""
    if not args.inputs:
        print("Error: At least two input files are required")
        sys.exit(1)

    atlas = WordAtlas(args.data_dir)
    merged = WordlistBuilder(atlas)

    # Set metadata
    merged.metadata["name"] = args.name
    merged.metadata["description"] = args.description
    merged.metadata["creator"] = args.creator
    merged.metadata["tags"] = args.tags.split(",") if args.tags else []

    # Load and merge wordlists
    for input_file in args.inputs:
        try:
            wordlist = WordlistBuilder.load(input_file, atlas)
            print(
                f"Loaded '{wordlist.metadata['name']}' with {len(wordlist.words)} words"
            )
            merged.words.update(wordlist.words)
            merged.metadata["criteria"].extend(wordlist.metadata["criteria"])
            print(
                f"Added {len(wordlist.words)} words from '{wordlist.metadata['name']}'"
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading wordlist '{input_file}': {e}")
            sys.exit(1)

    # Save merged wordlist
    merged.save(args.output)
    print(f"Merged wordlist saved to '{args.output}' with {len(merged.words)} words")


def main():
    parser = argparse.ArgumentParser(
        description="English Word Atlas - Explore the linguistic dataset"
    )
    parser.add_argument("--data-dir", help="Directory containing the dataset files")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Info command
    info_parser = subparsers.add_parser(
        "info", help="Show information about a word or phrase"
    )
    info_parser.add_argument("word", help="Word or phrase to look up")
    info_parser.add_argument(
        "--no-similar", action="store_true", help="Don't show similar words"
    )
    info_parser.add_argument(
        "--json", action="store_true", help="Include full data in JSON format"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search for words/phrases matching a pattern"
    )
    search_parser.add_argument(
        "pattern", help="Regular expression pattern or substring to search for"
    )
    search_parser.add_argument(
        "--attribute", help="Filter by attribute (e.g., 'GSL=true', 'ROGET_123')"
    )
    search_parser.add_argument("--min-freq", type=float, help="Minimum frequency")
    search_parser.add_argument("--max-freq", type=float, help="Maximum frequency")
    search_parser.add_argument(
        "--phrases-only", action="store_true", help="Only show multi-word phrases"
    )
    search_parser.add_argument(
        "--words-only", action="store_true", help="Only show single words"
    )
    search_parser.add_argument(
        "--limit", type=int, help="Maximum number of results to show"
    )
    search_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show additional information about each result",
    )

    # Stats command
    stats_parser = subparsers.add_parser(
        "stats", help="Show statistics about the dataset"
    )
    stats_parser.add_argument(
        "--basic", action="store_true", help="Only show basic statistics"
    )

    # Wordlist commands
    wordlist_parser = subparsers.add_parser(
        "wordlist", help="Work with custom wordlists"
    )
    wordlist_subparsers = wordlist_parser.add_subparsers(
        dest="wordlist_command", help="Wordlist operation"
    )

    # Create wordlist
    create_parser = wordlist_subparsers.add_parser(
        "create", help="Create a new wordlist"
    )
    create_parser.add_argument(
        "--name", default="Custom Wordlist", help="Name of the wordlist"
    )
    create_parser.add_argument("--description", help="Description of the wordlist")
    create_parser.add_argument("--creator", help="Creator of the wordlist")
    create_parser.add_argument("--tags", help="Comma-separated list of tags")
    create_parser.add_argument(
        "--search-pattern",
        help="Regular expression pattern or substring to match words",
    )
    create_parser.add_argument(
        "--attribute", help="Filter by attribute (e.g., 'GSL=true', 'ROGET_123')"
    )
    create_parser.add_argument("--syllables", type=int, help="Filter by syllable count")
    create_parser.add_argument("--min-freq", type=float, help="Minimum frequency")
    create_parser.add_argument("--max-freq", type=float, help="Maximum frequency")
    create_parser.add_argument("--similar-to", help="Find words similar to this word")
    create_parser.add_argument(
        "--similar-count",
        type=int,
        help="Number of similar words to include (default: 10)",
    )
    create_parser.add_argument(
        "--input-file", help="File containing words to include (one per line or JSON)"
    )
    create_parser.add_argument(
        "--output", help="Output file to save the wordlist (.json)"
    )
    create_parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Don't show analysis of the created wordlist",
    )

    # Modify wordlist
    modify_parser = wordlist_subparsers.add_parser(
        "modify", help="Modify an existing wordlist"
    )
    modify_parser.add_argument("wordlist", help="Wordlist file to modify")
    modify_parser.add_argument("--name", help="New name for the wordlist")
    modify_parser.add_argument("--description", help="New description for the wordlist")
    modify_parser.add_argument("--creator", help="New creator for the wordlist")
    modify_parser.add_argument("--tags", help="New comma-separated list of tags")
    modify_parser.add_argument("--add", nargs="+", help="Add words to the wordlist")
    modify_parser.add_argument(
        "--remove", nargs="+", help="Remove words from the wordlist"
    )
    modify_parser.add_argument("--add-pattern", help="Add words matching this pattern")
    modify_parser.add_argument("--add-attribute", help="Add words with this attribute")
    modify_parser.add_argument(
        "--add-similar-to", help="Add words similar to this word"
    )
    modify_parser.add_argument(
        "--similar-count", type=int, help="Number of similar words to add (default: 10)"
    )
    modify_parser.add_argument(
        "--remove-pattern", help="Remove words matching this pattern"
    )
    modify_parser.add_argument(
        "--output",
        help="Output file to save the modified wordlist (default: overwrite input)",
    )

    # Analyze wordlist
    analyze_parser = wordlist_subparsers.add_parser(
        "analyze", help="Analyze a wordlist and show statistics"
    )
    analyze_parser.add_argument("wordlist", help="Wordlist file to analyze")
    analyze_parser.add_argument("--export", help="Export analysis to a JSON file")
    analyze_parser.add_argument(
        "--export-text", help="Export wordlist to a text file (one word per line)"
    )

    # Merge wordlists
    merge_parser = wordlist_subparsers.add_parser(
        "merge", help="Merge multiple wordlists into a single wordlist"
    )
    merge_parser.add_argument("inputs", nargs="+", help="Wordlist files to merge")
    merge_parser.add_argument("--name", help="Name for the merged wordlist")
    merge_parser.add_argument(
        "--description", help="Description for the merged wordlist"
    )
    merge_parser.add_argument("--creator", help="Creator of the merged wordlist")
    merge_parser.add_argument("--tags", help="Comma-separated list of tags")
    merge_parser.add_argument(
        "--output", help="Output file to save the merged wordlist"
    )

    args = parser.parse_args()

    # Handle commands
    if args.command == "info":
        info_command(args)
    elif args.command == "search":
        search_command(args)
    elif args.command == "stats":
        stats_command(args)
    elif args.command == "wordlist":
        if args.wordlist_command == "create":
            wordlist_create_command(args)
        elif args.wordlist_command == "modify":
            wordlist_modify_command(args)
        elif args.wordlist_command == "analyze":
            wordlist_analyze_command(args)
        elif args.wordlist_command == "merge":
            wordlist_merge_command(args)
        else:
            wordlist_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
