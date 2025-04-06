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

For uv usage, see [README-uv.md](README-uv.md).

## Repository Structure

```
english_word_atlas/
├── README.md           # Project documentation
├── CHANGELOG.md        # Version history
├── ROADMAP.md          # Development roadmap
├── CONTRIBUTING.md     # Contribution guidelines
├── requirements.txt    # Development dependencies
├── pyproject.toml      # Package configuration
├── run_tests.py        # Test runner script
├── run-with-uv.sh      # Helper for uv (Unix/macOS)
├── run-with-uv.ps1     # Helper for uv (Windows)
├── README-uv.md        # uv usage instructions
├── examples/           # Example usage scripts
├── tests/              # Test suite
├── word_atlas/         # Python package
└── data/               # Dataset files
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

# Install dependencies
pip install -e ".[dev,visualization,web]"
```

### Data Files

All data files are included in the `data` directory:

- `data/word_data.json`: Linguistic and semantic annotations for each word
- `data/word_index.json`: Indices for the embedding vectors
- `data/embeddings.npy`: Pre-calculated embedding vectors

## Usage

### Basic Usage

```python
from word_atlas import WordAtlas

# Initialize the atlas
atlas = WordAtlas()

# Get information about a word
data = atlas.get_word("elephant")
print(f"Word data: {data}")

# Get embedding vector
vector = atlas.get_embedding("elephant")
print(f"Embedding shape: {vector.shape}")

# Find similar words
similar = atlas.find_similar("elephant", n=5)
print(f"Similar words: {similar}")
```

### Advanced Features

```python
from word_atlas import WordAtlas

# Initialize the WordAtlas
# It will automatically locate the dataset in standard locations
atlas = WordAtlas()

# Or specify a custom data directory
# atlas = WordAtlas(data_dir="/path/to/data")

# Get information about a word
info = atlas.get_word("happiness")
print(f"Syllables: {info.get('SYLLABLE_COUNT')}")
print(f"Pronunciation: {info.get('ARPABET', [['?']])[0]}")
print(f"Frequency: {info.get('FREQ_GRADE', 0)}")

# Get embedding for a word (returns numpy ndarray)
embedding = atlas.get_embedding("happiness")

# Find similar words (returns list of (word, score) tuples)
similar_words = atlas.get_similar_words("happiness", n=10)
for word, score in similar_words:
    print(f"{word}: {score:.4f}")

# Check if a word exists in the dataset
if atlas.has_word("serendipity"):
    print("Serendipity is in the dataset")

# Get all phrases in the dataset
phrases = atlas.get_phrases()

# Get all single words
single_words = atlas.get_single_words()

# Search by regular expression
regex_matches = atlas.search("happi.*")

# Filter by attributes
freedom_words = atlas.filter_by_attribute("ROGET_ABSTRACT")
gsl_words = atlas.filter_by_attribute("GSL")

# Filter by frequency
common_words = atlas.filter_by_frequency(min_freq=100)
rare_words = atlas.filter_by_frequency(max_freq=10)

# Filter by syllable count
three_syllable_words = atlas.filter_by_syllable_count(3)

# Get similarity between two words
similarity = atlas.word_similarity("happy", "sad")
```

### Data Access Functions

For advanced usage, you can access the raw data files directly:

```python
from word_atlas.data import (
    load_dataset,     # Load the complete dataset with embeddings
    get_word_data,    # Get word attributes without embeddings
    get_embeddings,   # Get the raw embedding matrix
    get_word_index    # Get the mapping of words to embedding indices
)

# Load the entire dataset with embeddings
complete_data = load_dataset()

# Access only the word attributes
word_attributes = get_word_data()

# Get the raw embeddings matrix
embeddings_matrix = get_embeddings()

# Get the word to index mapping
word_to_index = get_word_index()
```

### Command-line Interface

The package includes a comprehensive command-line interface for exploring the dataset:

```bash
# Get information about a word
python -m word_atlas info happiness

# Search for words matching a pattern
python -m word_atlas search "happ.*" --words-only

# Filter by attributes
python -m word_atlas search ".*" --attribute GSL --min-freq 200

# Show dataset statistics
python -m word_atlas stats

# Show detailed statistics
python -m word_atlas stats --detailed

# Get help for a specific command
python -m word_atlas info --help
```

### Examples

The package includes example scripts in the `examples/` directory:

```bash
# Run the basic usage example
python examples/basic_usage.py

# Run the text analysis example
python examples/text_analysis.py /path/to/your/text.txt
```

## Testing

The package includes a comprehensive test suite using pytest.

```bash
# With the run_tests.py script
python run_tests.py

# With uv
./run-with-uv.sh test

# Directly with pytest
pytest
```

## Dataset Contents

### Semantic Categories
- **Roget's Categories** (32 main categories, covering 28.5% at highest)
  - Abstract Relations
  - Space
  - Matter
  - Intellect
  - Volition
  - Affections
  - Includes numerous multi-word phrases and expressions
  
- **Basic English Categories**
  - Basic Operations and Qualities
  - Field-specific Vocabularies (19 fields)
  - Supplementary Technical Terms
  
- **Core Vocabulary Lists**
  - GSL (General Service List): 26.0% coverage
  - NGSL (New General Service List v1.2): 32.2% coverage
  - Swadesh Lists (Core 100 and Extended 207)

### Linguistic Features
- **Embeddings**: ALL-MiniLM-L6-v2 (384 dimensions)
  - Complete coverage (100% of entries)
  - Normalized vectors (L2 norm = 1.000)
  - Distributed semantic space (no dominant components)
  - Full coverage of both single words and phrases

- **Pronunciations**: ARPABET format
  - Average 1.24 variants per word
  - 18.3% of entries have multiple pronunciations
  - Maximum 8 variants for some phrases
  - Comprehensive coverage of multi-word expressions
  - Example: "be so good as" → [('B', 'IY1', 'S', 'OW1', 'G', 'UH1', 'D', 'AE1', 'Z'), ...]

- **Frequencies**: Raw counts and computed grades
  - Raw frequency counts for single words
  - Computed frequency grades for all entries (words and phrases)
  - Phrase frequencies derived from component words
  - Zero frequencies flagged for review
  - Example: "take money" → freq_count: 640.76

### Stop Word Classifications
Multiple standard NLP stop word lists:
- NLTK (0.9% coverage)
- scikit-learn (2.4% coverage)
- spaCy (2.4% coverage)
- Fox (2.8% coverage)

## Statistics

### Realistic Vocabulary Coverage Analysis

Our analysis of wordlist coverage against SUBTLEX-US frequency data reveals some eye-opening statistics:

#### Key Coverage Findings

- **Standard Wordlists Are Limited**: The widely-used GSL (General Service List) covers only 59.9% of the top 1,000 most frequent English words, despite containing 2,218 words
- **Vocabulary Efficiency**: The ALL_INTERSECTION set (26 words) appears in all major wordlists and covers 14% of the top 100 most frequent words
- **Coverage Sweet Spot**: OGDEN_BASIC_ALL (831 words) achieves 46% coverage of the top 100 most frequent words
- **Frequency Drop-off**: STOP_NLTK (75 words) covers 44% of the top 100 most frequent words, but only 7.2% of the top 1,000

#### Beyond Single-Word Coverage

Unlike most wordlists, English Word Atlas includes:
- **Common Idiomatic Phrases**: Multi-word expressions like "take heart" and "bear in mind" that are essential for natural language use
- **Semantic Diversity**: Words deliberately selected to cover the full conceptual space of English, not just frequency-based selection
- **Rich Annotations**: Each entry includes pronunciation, embeddings, and multiple categorical annotations

#### Word Atlas Capabilities

The English Word Atlas provides accurate coverage statistics and powerful filtering capabilities to:
- Combine existing wordlists for optimal frequency coverage
- Filter by syllable count, frequency, and semantic categories
- Create custom wordlists tailored to specific learning objectives
- Analyze real coverage against frequency data rather than inflated claims

With 8,536 words and phrases categorized across multiple dimensions, English Word Atlas offers unparalleled flexibility for language learning, teaching, and linguistics research.

### Distribution
- Total entries: 8,536 words and phrases
  - Includes both single words and multi-word expressions
  - Phrases primarily from Roget's Thesaurus categories
- Syllable distribution:
  - 1 syllable: 20.1%
  - 2 syllables: 36.5%
  - 3 syllables: 26.8%
  - 4+ syllables: 16.6% (including multi-word phrases)

### Coverage
- Complete embedding coverage (100%)
- Category coverage varies from 0.1% to 32.2%
- Multiple pronunciation variants for 1,564 entries

## Data Format

The dataset is provided as a set of files designed for efficient storage and access:

## Development Workflow

This project uses a protected `main` branch and requires all changes to go through pull requests:

1. Development work should be done on the `develop` branch
2. Create a pull request from `develop` to `main` when ready to release
3. CI checks must pass before merging
4. Once approved, changes will be merged to `main`
