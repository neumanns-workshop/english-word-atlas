"""
Renames files within the subdirectories of data/sources/ 
to remove redundant prefixes based on the parent directory name.

For example:
- data/sources/AFINN/AFINN_NEG_1.json -> data/sources/AFINN/NEG_1.json
- data/sources/GSL/GSL_gsl_new.json   -> data/sources/GSL/gsl_new.json
"""

import os
from pathlib import Path
import sys

def get_project_root() -> Path:
    """Gets the project root directory based on script location."""
    # Assumes the script is in a subdirectory (like 'scripts') of the project root
    return Path(__file__).parent.parent

def rename_source_files():
    """Scans data/sources subdirectories and renames files with redundant prefixes."""
    project_root = get_project_root()
    sources_dir = project_root / "data" / "sources"

    if not sources_dir.is_dir():
        print(f"Error: Sources directory not found at {sources_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning subdirectories in {sources_dir}...")
    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for item in sources_dir.iterdir():
        if item.is_dir():
            subdir_name = item.name
            prefix_to_remove = f"{subdir_name}_"
            print(f"\nProcessing directory: {item}")

            try:
                for filename in item.iterdir():
                    if filename.is_file():
                        if filename.name.startswith(prefix_to_remove):
                            new_name = filename.name[len(prefix_to_remove):]
                            new_path = item / new_name

                            if new_path.exists():
                                print(f"  - Skipping rename: Target '{new_path.name}' already exists for '{filename.name}'", file=sys.stderr)
                                skipped_count += 1
                                continue
                            
                            try:
                                filename.rename(new_path)
                                print(f"  - Renamed '{filename.name}' -> '{new_name}'")
                                renamed_count += 1
                            except OSError as e:
                                print(f"  - Error renaming '{filename.name}': {e}", file=sys.stderr)
                                error_count += 1
                        else:
                             # print(f"  - Skipping '{filename.name}' (no prefix '{prefix_to_remove}')")
                             pass # No action needed if prefix doesn't match
            except OSError as e:
                print(f"Error accessing directory {item}: {e}", file=sys.stderr)
                error_count += 1

    print(f"\nFinished processing.")
    print(f"Renamed: {renamed_count}")
    print(f"Skipped (target existed): {skipped_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    rename_source_files() 