# English Word Atlas

[![CI](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/neumanns-workshop/english-word-atlas/branch/main/graph/badge.svg)](https://codecov.io/gh/neumanns-workshop/english-word-atlas)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://github.com/neumanns-workshop/english-word-atlas)
[![Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/neumanns-workshop/english-word-atlas/main/pyproject.toml&query=$.project.version&label=version&color=brightgreen)](https://github.com/neumanns-workshop/english-word-atlas/blob/main/CHANGELOG.md)

A curated dataset of 8,536 English words and phrases with comprehensive linguistic and semantic annotations, designed to capture the conceptual diversity of English. This dataset combines historical lexicographic resources with modern NLP tools to provide rich annotations for cognitive and computational linguistics research. Notably, due to Roget's Thesaurus entries, it includes multi-word phrases (e.g., "be so good as", "put a good face on") alongside single words, with full embedding and pronunciation coverage for both.

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

# Explore a word
word_info = atlas.get_word("freedom")
print(f"Freedom has {word_info['SYLLABLE_COUNT']} syllables")
print(f"Freedom pronunciation: {word_info['ARPABET'][0]}")

# Find similar words
similar_words = atlas.get_similar_words("freedom", n=5)
for word, score in similar_words:
    print(f"{word}: {score:.4f}")
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
    ├── embeddings.npy
    ├── word_data.json
    └── word_index.json
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

- `data/word_data.json`: Linguistic and semantic annotations for each word/phrase.
- `data/word_index.json`: Mapping from words/phrases to embedding vector indices.
- `data/embeddings.npy`: Pre-calculated `all-MiniLM-L6-v2` embedding vectors (384 dimensions).

## Usage

### Basic Usage (Python API)

```python
from word_atlas import WordAtlas

# Initialize the atlas (loads data automatically)
atlas = WordAtlas()

# Get information about a word
data = atlas.get_word("elephant")
if data:
    print(f"Syllables: {data.get('SYLLABLE_COUNT')}")
    print(f"Frequency Grade: {data.get('FREQ_GRADE')}")
else:
    print("Word not found.")


# Get embedding vector (NumPy array)
vector = atlas.get_embedding("elephant")
if vector is not None:
    print(f"Embedding shape: {vector.shape}")

# Find similar words
similar = atlas.get_similar_words("elephant", n=5)
print(f"Words similar to 'elephant': {similar}")

# Check if word exists
print(f"Has 'platypus'? {atlas.has_word('platypus')}")
```

### Advanced Features (Python API)

```python
# Filter words by attributes
gsl_words = atlas.filter_by_attribute("GSL") # Words in the General Service List
roget_words = atlas.filter_by_attribute("ROGET_ANIMAL") # Words in a Roget category

# Filter by frequency grade
common_words = atlas.filter_by_frequency(min_freq=1, max_freq=10)

# Filter by syllable count
two_syllable_words = atlas.filter_by_syllable_count(2)

# Search using regex
regex_matches = atlas.search(r"happi(ness|ly)")

# Get all phrases
phrases = atlas.get_phrases()

# Get word similarity
similarity = atlas.word_similarity("happy", "joyful")
print(f"Similarity(happy, joyful): {similarity:.4f}")
```

### Creating Wordlists (Python API)

```python
from word_atlas import WordAtlas, WordlistBuilder

atlas = WordAtlas()
builder = WordlistBuilder(atlas)

# Set metadata
builder.set_metadata(name="Common GSL Words", description="Words from GSL with freq < 10")

# Add words using criteria
builder.add_by_attribute("GSL")
builder.add_by_frequency(max_freq=10)

# Save the wordlist
output_file = "common_gsl.json"
builder.save(output_file)
print(f"Wordlist saved to {output_file} with {builder.get_size()} words.")

# Load an existing wordlist
loaded_builder = WordlistBuilder.load(output_file, atlas)
print(f"Loaded '{loaded_builder.metadata['name']}' with {loaded_builder.get_size()} words.")
```

### Command-line Interface (CLI)

After installation (`pip install -e .`), you can use the `word_atlas` command.

```bash
# Get information about a word
word_atlas info happiness

# Get info and similar words
word_atlas info freedom

# Search for words matching a pattern
word_atlas search "happ.*" --words-only

# Search and filter by attribute and frequency
word_atlas search ".*" --attribute GSL=true --min-freq 5

# Search for words with the ROGET_ANIMAL attribute (existence check)
word_atlas search ".*" --attribute ROGET_ANIMAL

# Show dataset statistics
word_atlas stats

# Show detailed statistics
word_atlas stats --detailed # Use --basic for less detail

# --- Wordlist Commands ---

# Create a wordlist from search and attribute
word_atlas wordlist create --name "Common Animals" \
    --search-pattern ".*" --attribute ROGET_ANIMAL \
    --max-freq 20 --output animals.json

# Create a wordlist of words similar to 'happy'
word_atlas wordlist create --name "Happy Synonyms" \
    --similar-to happy --similar-count 15 \
    --output happy_similar.json

# Modify a wordlist: add and remove words
word_atlas wordlist modify animals.json --add cat dog --remove elephant

# Modify a wordlist: update metadata
word_atlas wordlist modify animals.json --description "Common land animals" --tags "fauna,common"

# Analyze a wordlist
word_atlas wordlist analyze animals.json

# Merge two wordlists
word_atlas wordlist merge animals.json happy_similar.json --output combined.json --name "Combined List"

# Get help for a specific command
word_atlas search --help
word_atlas wordlist create --help
```

### Examples

The package includes example scripts in the `examples/` directory:

```bash
# Run the basic usage example
python examples/basic_usage.py

# Run the text analysis example
# python examples/text_analysis.py /path/to/your/text.txt
```

## Testing

The package includes a comprehensive test suite using `pytest`. Ensure development dependencies are installed (`pip install -e ".[dev]"`).

Run the tests and generate a coverage report:

```bash
# Run unit tests with coverage report
pytest tests/unit/ --cov=word_atlas --cov-report term-missing -v
```

Current status: 101 tests passing, 93.41% coverage.

## Data Sources

The dataset integrates information from various sources:

1.  **Roget's Thesaurus (Project Gutenberg):** Semantic categories and headwords.
2.  **CMU Pronouncing Dictionary:** Phonetic transcriptions (ARPABET).
3.  **General Service List (GSL) & New General Service List (NGSL):** Core vocabulary lists.
4.  **Ogden's Basic English:** Simplified English vocabulary.
5.  **Swadesh List:** Basic concepts for historical linguistics.
6.  **Word frequency data:** Primarily based on SUBTLEXus frequencies, mapped to logarithmic grades.
7.  **Sentence Transformers (`all-MiniLM-L6-v2`):** Pre-trained embeddings for semantic similarity.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Data sources may have their own licenses.
