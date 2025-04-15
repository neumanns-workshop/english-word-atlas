# English Word Atlas

[![CI](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/neumanns-workshop/english-word-atlas/branch/main/graph/badge.svg)](https://codecov.io/gh/neumanns-workshop/english-word-atlas)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://github.com/neumanns-workshop/english-word-atlas)
[![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/neumanns-workshop/english-word-atlas/main/pyproject.toml&query=$.project.version&label=version&color=brightgreen)](https://github.com/neumanns-workshop/english-word-atlas/blob/main/CHANGELOG.md)

A curated dataset of English words and phrases from popular wordlists designed to capture the conceptual diversity of English.

> **Note:** This project is focused on local development and is not distributed via PyPI. Please use the local installation methods described below.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/neumanns-workshop/english-word-atlas.git
cd english-word-atlas

# Set up environment with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
./init-uv.sh  # or init-uv.ps1 on Windows
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

```python
# Basic usage example
from word_atlas import WordAtlas

# Initialize the dataset
atlas = WordAtlas()

# Check if a word exists and get its basic info
word = "freedom"
if atlas.has_word(word):
    print(f"Information for '{word}':")
    try:
        sources = atlas.get_sources(word)
        print(f"  Sources: {sources}")
    except KeyError:
        print("  Sources: Not found in any source list.") # Should not happen if has_word is true

    try:
        freq = atlas.get_frequency(word)
        print(f"  Frequency: {freq:.2f}")
    except KeyError:
        print("  Frequency: N/A") # Word might exist but have no frequency data

    # Get embedding (if needed)
    # embedding = atlas.get_embedding(word)
    # if embedding is not None:
    #     print(f"  Embedding dimensions: {embedding.shape[0]}")
else:
    print(f"Word '{word}' not found.")

# Search for words matching a pattern
matches = atlas.search("libert.*")
print(f"\nWords matching 'libert.*': {matches}")
```

For `uv` usage, see [README-uv.md](README-uv.md).

## Repository Structure

```
english_word_atlas/
├── README.md           # Project documentation
├── CHANGELOG.md        # Version history
├── ROADMAP.md          # Development roadmap
├── CONTRIBUTING.md     # Contribution guidelines
├── requirements.txt    # Development dependencies (managed via pyproject.toml)
├── pyproject.toml      # Package configuration and dependencies
├── run_tests.py        # Test runner script (deprecated, use pytest)
├── run-with-uv.sh      # Helper for uv (Unix/macOS)
├── run-with-uv.ps1     # Helper for uv (Windows)
├── README-uv.md        # uv usage instructions
├── examples/           # Example usage scripts
├── tests/              # Test suite (unit, integration)
│   ├── conftest.py     # Pytest fixtures
│   ├── unit/           # Unit tests for modules
│   └── ...
├── word_atlas/         # Python package source
│   ├── __init__.py
│   ├── __main__.py     # Main script entry point
│   ├── atlas.py        # WordAtlas class
│   ├── cli.py          # Command-line interface logic
│   ├── data.py         # Data loading utilities
│   └── wordlist.py     # WordlistBuilder class
└── data/               # Dataset files (git-lfs managed)
    ├── frequencies/
    │   └── word_frequencies.json # SUBTLWF frequency data
    ├── sources/
    │   ├── gsl.txt           # Example source list (General Service List)
    │   └── ...               # Other source lists (.txt or .json)
    ├── embeddings.npy          # Pre-calculated embedding vectors
    └── word_index.json         # Word/phrase to index mapping
```

## Installation

Clone the repository to get started:

```bash
git clone https://github.com/neumanns-workshop/english-word-atlas.git
cd english-word-atlas
```

### Installation with uv (recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the virtual environment and install dependencies
./init-uv.sh  # or init-uv.ps1 on Windows

# Activate the environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### Installation with pip

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install the package in editable mode with optional dev dependencies
pip install -e ".[dev]"
```

### Data Files

All data files are included in the `data` directory and managed with Git LFS. Ensure you have Git LFS installed (`git lfs install`).

- `data/frequencies/word_frequencies.json`: Word frequency data derived from SUBTLEX-US.
- `data/sources/`: Directory containing various source lists (e.g., `gsl.txt`, `awl.txt`) as simple text files or JSON lists, indicating word membership in those lists.
- `data/word_index.json`: Mapping from words/phrases to embedding vector indices.
- `data/embeddings.npy`: Pre-calculated `all-MiniLM-L6-v2` embedding vectors (384 dimensions).

## Usage

### Basic Usage (Python API)

```python
from word_atlas import WordAtlas

# Initialize the atlas (loads data automatically from default data directory)
# Optionally provide a custom path: WordAtlas(data_dir='/path/to/custom/data')
atlas = WordAtlas()

# Check if a word or phrase exists
print(f"Has 'platypus'? {atlas.has_word('platypus')}")
print(f"Has 'kick the bucket'? {atlas.has_word('kick the bucket')}")

# Get sources and frequency
try:
    sources = atlas.get_sources("elephant")
    print(f"Sources for 'elephant': {sources}")
except KeyError:
    print("Word 'elephant' not found in any source list.") # Should not happen based on mock data

try:
    freq = atlas.get_frequency("elephant")
    print(f"Frequency of 'elephant': {freq:.2f}")
except KeyError:
    print("Word 'elephant' has no frequency data.")

# Get embedding vector (NumPy array)
vector = atlas.get_embedding("elephant")
if vector is not None:
    print(f"Embedding shape: {vector.shape}")

# Search for words using regex
regex_matches = atlas.search(r"happi(ness|ly)")
print(f"Words matching pattern: {regex_matches}")

# Filter words (example: find words in 'GSL' source list with frequency > 100)
filtered_words = atlas.filter(sources=["GSL"], min_freq=100)
print(f"Filtered words: {filtered_words[:10]}...") # Show first 10
```

### Creating Wordlists (Python API)

```python
from word_atlas import WordAtlas, WordlistBuilder

atlas = WordAtlas()
builder = WordlistBuilder(atlas)

# Set metadata
builder.set_metadata(name="Common GSL Words", description="Words from GSL with freq < 1000")

# Add words using criteria
builder.add_by_source("GSL") # Add all words from the GSL source list
builder.add_by_frequency(max_freq=1000) # Add words with frequency <= 1000
builder.add_by_search(".*ness") # Add words ending in 'ness'

# Remove specific words
builder.remove_words(["apple", "banana"])

# Save the wordlist
output_file = "common_gsl.json"
builder.save(output_file)
print(f"Wordlist saved to {output_file} with {len(builder.words)} words.")

# Load an existing wordlist
loaded_builder = WordlistBuilder.load(output_file, atlas)
print(f"Loaded '{loaded_builder.metadata['name']}' with {len(loaded_builder.words)} words.")
```

### Command-line Interface (CLI)

After installation (`pip install -e .` or using `uv`), you can use the `word_atlas` command. Use `--data-dir` to specify a custom data directory if needed.

```bash
# Get information about a word (sources, frequency)
word_atlas info happiness

# Search for words matching a regex pattern
word_atlas search "happ.*"

# Search and filter by source list and frequency
word_atlas search ".*" --source GSL --max-freq 100

# Search and filter, showing verbose output (includes frequency)
word_atlas search "an.*" --source GSL --verbose

# Show dataset statistics
word_atlas stats

# --- Wordlist Commands ---

# Create a wordlist from search, source, and frequency criteria
word_atlas wordlist create --name "Common GSL Words" --output common_gsl.json \\
    --source GSL --max-freq 1000 --search-pattern ".*ness"

# Modify a wordlist: add/remove specific words, update metadata
word_atlas wordlist modify common_gsl.json --add cat dog --remove happiness \\
    --description "Updated description" --tags "common,gsl"

# Modify a wordlist: add/remove based on patterns, sources, frequency
word_atlas wordlist modify common_gsl.json --add-pattern "^a" --remove-pattern "ness$" \\
    --add-source AWL --remove-source OTHER \\
    --add-min-freq 50 --add-max-freq 200

# Analyze a wordlist (show stats: size, single/phrase count, frequency info, source coverage)
word_atlas wordlist analyze common_gsl.json

# Analyze and export analysis results to JSON
word_atlas wordlist analyze common_gsl.json --export analysis_results.json

# Analyze and export the wordlist itself to a text file
word_atlas wordlist analyze common_gsl.json --export-text wordlist_plain.txt

# Merge two wordlists
word_atlas wordlist merge list1.json list2.json --output combined.json --name "Combined List"

# Get help for a specific command
word_atlas wordlist modify --help
```

## Data Details

```python
# Example entry in word_data_base.json
# (Note: actual file might be structured differently, e.g., as a list)
{
  "aardvark": {
    "ARPABET": ["AA1 R D V AA2 R K"],
    "SYLLABLE_COUNT": 2
    # Other potential base annotations...
  },
  // ... more words
}

# Example entry in word_frequencies.json
{
  "aardvark": 1.23,
  "abandon": 45.67,
  // ... more words
}

# Example source file (e.g., data/sources/gsl.txt)
# Can be .txt (one word per line) or .json (list of strings)
apple
banana
# ... more words
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Data sources may have their own licenses.
