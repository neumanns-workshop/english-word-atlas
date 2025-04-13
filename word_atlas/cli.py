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
    """Show information about a word or phrase (sources and frequency)."""
    atlas = WordAtlas(args.data_dir)

    word_to_check = args.word
    if not atlas.has_word(word_to_check):
        print(f"Word or phrase '{word_to_check}' not found in the master index.")
        sys.exit(1)

    # Get available information: sources and frequency
    word_sources = atlas.get_sources(word_to_check)
    word_frequency = atlas.get_frequency(word_to_check)

    if args.json:
        try:
            # Combine info for JSON output
            info = {
                "word": word_to_check,
                "sources": word_sources,
                "frequency": word_frequency,  # Could be None
            }
            print(json.dumps(info, indent=2))
        except TypeError as e:
            print(f"Error generating JSON: {str(e)}")
            sys.exit(1)
        return

    # Print basic information
    print(f"Information for '{word_to_check}':")

    # Print Frequency
    if word_frequency is not None:
        print(f"  Frequency (SUBTLWF): {word_frequency:.2f}")
    else:
        print("  Frequency: Not available")

    # Show source list membership
    if word_sources:
        print(f"  Sources: {', '.join(word_sources)}")
    else:
        print("  Sources: None")


def search_command(args):
    """Search for words/phrases matching a pattern, optionally filter by source/frequency."""
    atlas = WordAtlas(args.data_dir)

    # Initial search based on pattern
    search_results = set(atlas.search(args.pattern))
    initial_count = len(search_results)
    final_results = search_results.copy()

    # Filter by source attribute if specified
    if args.attribute:
        # This argument now ONLY filters by source name
        source_name = args.attribute
        try:
            source_filtered_set = atlas.filter(sources=[source_name])
            final_results.intersection_update(source_filtered_set)
        except ValueError as e:  # Handle case where source doesn't exist
            print(f"Warning: {e}", file=sys.stderr)
            final_results = set()  # No results if source is invalid

    # Filter by frequency if specified
    if args.min_freq is not None or args.max_freq is not None:
        min_f = args.min_freq if args.min_freq is not None else 0
        max_f = args.max_freq
        # Use the new filter method
        freq_filtered_set = atlas.filter(min_freq=min_f, max_freq=max_f)
        final_results.intersection_update(freq_filtered_set)

    # Convert final set to sorted list for output
    results_list = sorted(list(final_results))

    # Limit results
    if args.limit:
        results_list = results_list[: args.limit]

    # Print results
    print(f"Found {len(results_list)} matches (after filtering from {initial_count}):")
    for result in results_list:
        if args.verbose:
            # Show word and its frequency if available
            freq = atlas.get_frequency(result)
            freq_str = f" (freq: {freq:.2f})" if freq is not None else " (freq: N/A)"
            print(f"  {result}{freq_str}")
        else:
            print(f"  {result}")


def stats_command(args):
    """Show statistics about the dataset (entry count and source coverage)."""
    atlas = WordAtlas(args.data_dir)

    try:
        stats = atlas.get_stats()
        print("English Word Atlas Statistics:")
        print(f"  Total unique words in index: {stats.get('total_entries', 0)}")
        print(f"    Single words: {stats.get('single_words', 0)}")
        print(f"    Phrases: {stats.get('phrases', 0)}")
        print(
            f"  Entries with frequency data: {stats.get('entries_with_frequency', 0)}"
        )

        # Show source list coverage (from stats dict)
        source_coverage = stats.get("source_coverage", {})
        if source_coverage:
            print("\nSource List Coverage:")
            total_entries = stats.get("total_entries", 0)
            for source_name, count in sorted(source_coverage.items()):
                # Calculate percentage against master word index size
                percentage = (count / total_entries * 100) if total_entries > 0 else 0
                print(
                    f"  {source_name}: {count} entries ({percentage:.1f}% of total index)"
                )
        else:
            print("\nSource List Coverage: No source lists found or loaded.")

    except Exception as e:
        print(f"Error loading or processing stats: {str(e)}")
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

            # Use the simplified add_by_source method
            added = builder.add_by_source(attr_name)
            print(f"Added {added} words from source {attr_name}")
        except ValueError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    if args.min_freq is not None or args.max_freq is not None:
        min_f = args.min_freq if args.min_freq is not None else 0
        added = builder.add_by_frequency(min_f, args.max_freq)
        freq_range = (
            f">= {min_f}" if args.max_freq is None else f"{min_f} - {args.max_freq}"
        )
        print(f"Added {added} words with frequency {freq_range}")

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

    if hasattr(args, "add_source") and args.add_source:
        try:
            added = builder.add_by_source(args.add_source)
            print(f"Added {added} words from source '{args.add_source}'")
            total_modified += added
        except ValueError as e:
            print(f"Error adding source: {e}", file=sys.stderr)

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

    if hasattr(args, "remove_source") and args.remove_source:
        try:
            removed = builder.remove_by_source(args.remove_source)
            print(f"Removed {removed} words from source '{args.remove_source}'")
            total_modified += removed
        except ValueError as e:
            print(f"Error removing source: {e}", file=sys.stderr)

    # Add/Remove by Frequency
    if hasattr(args, "add_min_freq") and args.add_min_freq is not None:
        min_f = args.add_min_freq
        max_f = args.add_max_freq
        added = builder.add_by_frequency(min_f, max_f)
        freq_range = f">= {min_f}" if max_f is None else f"{min_f} - {max_f}"
        print(f"Added {added} words with frequency {freq_range}")
        total_modified += added

    # Save the wordlist
    output_file = args.output if args.output else args.wordlist
    try:
        builder.save(output_file)
        print(f"Wordlist saved to '{output_file}' with {len(builder.words)} words")
    except Exception as e:
        print(f"Error saving wordlist: {e}", file=sys.stderr)
        sys.exit(1)


def wordlist_analyze_command(args):
    """Analyze a wordlist and show statistics."""
    atlas = WordAtlas(args.data_dir)
    try:
        builder = WordlistBuilder.load(args.wordlist, atlas)
        stats = builder.analyze()

        # Handle JSON output first
        if args.json:
            try:
                print(json.dumps(stats, indent=2))
            except TypeError as e:
                print(f"Error generating JSON: {str(e)}", file=sys.stderr)
                sys.exit(1)
            return  # Exit after printing JSON

        # --- Regular text output --- (Only runs if args.json is False)

        print(
            f"Analyzing wordlist '{builder.metadata.get('name', 'Unnamed')}' with {len(builder.words)} words"
        )

        # Print basic stats
        print("\nBasic statistics:")
        print(f"  Total words: {stats['size']}")
        print(f"  Single words: {stats['single_words']}")
        print(f"  Phrases: {stats['phrases']}")

        # Print frequency distribution
        freq_stats = stats.get("frequency", {})
        if freq_stats.get("count", 0) > 0:
            print("\nFrequency distribution:")
            dist = freq_stats.get("distribution", {})
            total_freq_words = freq_stats["count"]
            for bin_label, count in sorted(dist.items()):
                percentage = (count / total_freq_words) * 100 if total_freq_words else 0
                print(f"  Frequency {bin_label}: {count} words ({percentage:.1f}%)")
            print(f"  Average frequency: {freq_stats.get('average', 0.0):.1f}")
        else:
            print(
                "\nFrequency distribution: No frequency data available for words in list."
            )

        # Print source coverage
        coverage_stats = stats.get("source_coverage", {})
        if coverage_stats:
            print("\nSource List Coverage:")
            for src_name, src_data in sorted(coverage_stats.items()):
                count = src_data.get("count", 0)
                percentage = src_data.get("percentage", 0.0)
                if count > 0:
                    print(f"  {src_name}: {count} words ({percentage:.1f}%)")
        else:
            print("\nSource List Coverage: No source lists analyzed.")

        # Optional exports
        if args.export:
            export_path = Path(args.export)
            try:
                export_path.parent.mkdir(parents=True, exist_ok=True)
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)
                print(f"\nAnalysis exported to '{export_path}'")
            except Exception as e:
                print(
                    f"\nError exporting analysis to {export_path}: {e}", file=sys.stderr
                )

        if args.export_text:
            export_text_path = Path(args.export_text)
            try:
                builder.export_text(
                    export_text_path, include_metadata=False
                )  # Export only words
                print(f"\nWordlist exported to '{export_text_path}'")
            except Exception as e:
                print(
                    f"\nError exporting wordlist to {export_text_path}: {e}",
                    file=sys.stderr,
                )

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error loading or analyzing wordlist: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during analysis: {str(e)}")
        sys.exit(1)


def wordlist_merge_command(args):
    """Merge multiple wordlists."""
    if not args.inputs or len(args.inputs) < 2:
        print("Error: At least two input files are required for merging")
        sys.exit(1)

    atlas = WordAtlas(args.data_dir)
    merged = WordlistBuilder(atlas)

    # Set metadata for the merged list
    merged.set_metadata(
        name=args.name if args.name else "Merged Wordlist",
        description=args.description,
        creator=args.creator,
        tags=args.tags.split(",") if args.tags else [],
    )

    # Load and merge wordlists
    total_added = 0
    for input_file in args.inputs:
        try:
            wordlist = WordlistBuilder.load(input_file, atlas)
            print(
                f"Loaded '{wordlist.metadata.get('name', 'Unnamed')}' with {len(wordlist.words)} words"
            )
            added = merged.add_words(wordlist.words)
            print(
                f"Added {added} unique words from '{wordlist.metadata.get('name', input_file)}'"
            )
            total_added += added
            # Safely extend criteria using .get()
            merged.metadata["criteria"].extend(wordlist.metadata.get("criteria", []))
        except (FileNotFoundError, ValueError, IOError) as e:
            print(f"Error loading wordlist '{input_file}': {e}", file=sys.stderr)
            sys.exit(1)

    # Save the merged wordlist
    output_file = args.output
    if not output_file:
        print("Error: Output file must be specified for merge.", file=sys.stderr)
        sys.exit(1)

    try:
        merged.save(output_file)
        print(
            f"\nMerged wordlist saved to '{output_file}' with {len(merged.words)} unique words ({total_added} added in total)."
        )
    except Exception as e:
        print(f"Error saving merged wordlist: {e}", file=sys.stderr)
        sys.exit(1)


def sources_command(args):
    """Handle the 'sources' command."""
    try:
        atlas = WordAtlas(data_dir=args.data_dir)
        source_names = atlas.get_source_list_names()

        if not source_names:
            print("No source lists found in the data directory.")
        else:
            print("Available source lists:")
            for name in source_names:
                print(f"- {name}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "Please ensure the data directory and required files exist.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def setup_common_args(parser):
    """Add common arguments like --data-dir to a parser."""
    parser.add_argument(
        "--data-dir",
        help="Directory containing the dataset files (overrides default search paths)",
    )


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="CLI for the English Word Atlas (wordlists & frequency)."
    )
    # Add --data-dir to the main parser as well, so it's available before subcommand parsing if needed
    setup_common_args(parser)

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Info command
    parser_info = subparsers.add_parser(
        "info", help="Show source lists and frequency for a specific word."
    )
    parser_info.add_argument("word", type=str, help="Word or phrase to look up.")
    parser_info.add_argument(
        "--json", action="store_true", help="Output information in JSON format."
    )
    parser_info.set_defaults(func=info_command)

    # Search command
    parser_search = subparsers.add_parser(
        "search", help="Search words, optionally filter by source or frequency."
    )
    parser_search.add_argument("pattern", type=str, help="Regex pattern to search for.")
    # Simplified attribute filter to only accept source name
    parser_search.add_argument(
        "--attribute",
        type=str,
        help="Filter results to words present in this source list (e.g., GSL).",
    )
    parser_search.add_argument(
        "--min-freq", type=float, help="Minimum frequency (SUBTLWF) to include."
    )
    parser_search.add_argument(
        "--max-freq", type=float, help="Maximum frequency (SUBTLWF) to include."
    )
    # Removed phrase/word only args
    # parser_search.add_argument(...)
    parser_search.add_argument(
        "--limit", type=int, help="Limit the number of results displayed."
    )
    parser_search.add_argument(
        "--verbose", action="store_true", help="Show frequency with results."
    )
    parser_search.set_defaults(func=search_command)

    # Stats command
    parser_stats = subparsers.add_parser(
        "stats", help="Show overall statistics (word count, source coverage)."
    )
    # Removed --basic flag as detailed stats are removed
    # parser_stats.add_argument(...)
    parser_stats.set_defaults(func=stats_command)

    # Wordlist command group (will need updates later)
    parser_wordlist = subparsers.add_parser(
        "wordlist", help="Create, modify, or analyze wordlists."
    )
    wordlist_subparsers = parser_wordlist.add_subparsers(
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
    create_parser.add_argument("--min-freq", type=float, help="Minimum frequency")
    create_parser.add_argument("--max-freq", type=float, help="Maximum frequency")
    create_parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip analyzing the wordlist after creation.",
    )
    create_parser.add_argument(
        "--output", help="Output file to save the wordlist (.json)"
    )
    create_parser.set_defaults(func=wordlist_create_command)

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
    modify_parser.add_argument("--add-source", help="Add words from this source list")
    modify_parser.add_argument(
        "--remove-source", help="Remove words from this source list"
    )
    modify_parser.add_argument(
        "--add-min-freq", type=float, help="Add words with frequency >= this value"
    )
    modify_parser.add_argument(
        "--add-max-freq", type=float, help="Add words with frequency <= this value"
    )
    modify_parser.add_argument(
        "--remove-pattern", help="Remove words matching this pattern"
    )
    modify_parser.add_argument(
        "--output",
        help="Output file to save the modified wordlist (default: overwrite input)",
    )
    modify_parser.set_defaults(func=wordlist_modify_command)

    # Analyze wordlist
    analyze_parser = wordlist_subparsers.add_parser(
        "analyze", help="Analyze a wordlist and show statistics"
    )
    analyze_parser.add_argument("wordlist", help="Wordlist file to analyze")
    analyze_parser.add_argument("--export", help="Export analysis to a JSON file")
    analyze_parser.add_argument(
        "--export-text", help="Export wordlist to a text file (one word per line)"
    )
    analyze_parser.set_defaults(func=wordlist_analyze_command)

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
    merge_parser.set_defaults(func=wordlist_merge_command)

    # --- Sources Command ---
    sources_parser = subparsers.add_parser(
        "sources", help="List available source wordlists discovered in data/sources"
    )
    setup_common_args(sources_parser)
    sources_parser.set_defaults(func=sources_command)

    args = parser.parse_args()

    # Updated dispatch logic to handle wordlist subcommands
    if args.command == "wordlist":
        # Check if a wordlist subcommand was provided
        if hasattr(args, "func") and args.wordlist_command:
            args.func(args)
        else:
            # If no subcommand (like 'create', 'modify') is given for 'wordlist',
            # print the help for the 'wordlist' subparser itself.
            parser_wordlist.print_help()
    elif hasattr(args, "func"):
        # Handle top-level commands (info, search, stats)
        args.func(args)
    else:
        # No command or subcommand provided, print main help
        parser.print_help()


if __name__ == "__main__":
    main()
