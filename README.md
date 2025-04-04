# English Word Atlas

[![CI](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/neumanns-workshop/english-word-atlas/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/neumanns-workshop/english-word-atlas/branch/main/graph/badge.svg)](https://codecov.io/gh/neumanns-workshop/english-word-atlas)
[![PyPI version](https://badge.fury.io/py/english-word-atlas.svg)](https://badge.fury.io/py/english-word-atlas)
[![Python Versions](https://img.shields.io/pypi/pyversions/english-word-atlas.svg)](https://pypi.org/project/english-word-atlas/)

A curated dataset of 8,536 English words and phrases with comprehensive linguistic and semantic annotations, designed to capture the conceptual diversity of English. This dataset combines historical lexicographic resources with modern NLP tools to provide rich annotations for cognitive and computational linguistics research. Notably, due to Roget's Thesaurus entries, it includes multi-word phrases (e.g., "be so good as", "put a good face on") alongside single words, with full embedding and pronunciation coverage for both.

## Quick Start

```bash
# Install the package
pip install english-word-atlas

# Or install from source for development
git clone https://github.com/neumanns-workshop/english-word-atlas.git
cd english-word-atlas
pip install -e ".[dev]"
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
├── examples/           # Example usage scripts
├── tests/              # Test suite
├── word_atlas/         # Python package
│   ├── __init__.py     # Package initialization
│   ├── atlas.py        # Main WordAtlas class
│   ├── data.py         # Data loading utilities
│   ├── cli.py          # Command-line interface
│   └── __main__.py     # Entry point for CLI
└── data/               # Dataset files
    ├── embeddings.npy     # Word embeddings (8536 x 384)
    ├── word_index.json    # Word to embedding index mapping
    └── word_data.json     # Word attributes and annotations
```

## Using the Package

### Installation

```bash
# Install from PyPI (when published)
pip install english-word-atlas

# Install from source with all dependencies
# For development with visualization and web features
pip install -e ".[dev,visualization,web]"

# For basic usage
pip install -e .
```

### Basic Usage

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

The package includes a comprehensive test suite using pytest. The tests use a mock dataset to ensure they can run without the full dataset.

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
python run_tests.py

# Run tests with verbose output
python run_tests.py -v

# Run specific test modules
python run_tests.py tests/test_atlas.py

# Run tests that match a pattern
python run_tests.py -k "similarity"

# Run tests against the real dataset (requires dataset to be installed)
python run_tests.py --no-mock
```

### Test Coverage

The test suite covers:
- Core data loading functionality
- WordAtlas class methods
- Command-line interface
- Example scripts

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

```
data/
├── embeddings.npy          # Word embeddings as numpy array (8536 x 384)
├── word_index.json         # Mapping of words to embedding indices
└── word_data.json          # Categorical and pronunciation data
```

* `embeddings.npy`: Dense numpy array of word embeddings
* `word_index.json`: Maps words to their position in the embeddings array
* `word_data.json`: Contains all other word attributes (pronunciations, category flags)

Each word in the dataset has a corresponding entry in `word_data.json` with this structure:

```json
{
    "word": {
        "EMBEDDINGS_ALL_MINILM_L6_V2": [...],  // 384-dimensional array
        "ARPABET": [["P", "R", "AH0", "N", "AH1", "N", "S"], ...],  // Pronunciation variants
        "ROGET_ABSTRACT": true,  // Category flags
        "GSL_ORIGINAL": false,
        "FREQ_COUNT": 123.45,    // Raw frequency count (single words)
        "FREQ_GRADE": 456.78,    // Computed frequency grade (all entries)
        ...
    }
}
```

The embedding data is loaded automatically when initializing the `WordAtlas` class:

```python
from word_atlas import WordAtlas

# The class automatically finds and loads the dataset files
atlas = WordAtlas()

# Access word information
word = "freedom"
info = atlas.get_word(word)

# The embedding is available directly
embedding = atlas.get_embedding(word)
```

## Use Cases

The English Word Atlas can be used for a variety of applications:

### Research
- Psycholinguistic studies (word similarity, frequency effects)
- Semantic relationship analysis
- Cross-category lexical analysis
- Phonological pattern research

### NLP Applications
- Text analysis and readability assessment
- Vocabulary complexity measurement
- Text simplification algorithms
- Word embedding analysis and benchmarking

### Education
- Vocabulary teaching and assessment
- Text material selection and adaptation
- Language learning applications
- Readability analysis of educational materials

### Example: Text Analysis

```python
from word_atlas import WordAtlas
import re
from collections import Counter

# Initialize the Word Atlas
atlas = WordAtlas()

# Analyze a text
def analyze_text(text):
    # Tokenize text
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Get unique words
    unique_words = set(words)
    
    # Check coverage in atlas
    known_words = {word for word in unique_words if atlas.has_word(word)}
    coverage = len(known_words) / len(unique_words) * 100 if unique_words else 0
    
    # Analyze frequency
    frequencies = [atlas.get_word(word).get('FREQ_GRADE', 0) for word in known_words]
    avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0
    
    # Count categories
    categories = Counter()
    for word in known_words:
        for attr in atlas.get_word(word):
            if attr.startswith('ROGET_') and atlas.get_word(word)[attr]:
                categories[attr] += 1
    
    # Return results
    return {
        'total_words': len(words),
        'unique_words': len(unique_words),
        'coverage': coverage,
        'avg_frequency': avg_frequency,
        'top_categories': categories.most_common(5)
    }

# Example usage
text = "The pursuit of happiness is a fundamental right. Freedom and liberty are essential concepts."
results = analyze_text(text)
print(f"Coverage: {results['coverage']:.1f}%")
print(f"Average frequency: {results['avg_frequency']:.1f}")
print("Top categories:")
for category, count in results['top_categories']:
    print(f"  {category}: {count}")
```

## License

This dataset is distributed under the Apache License 2.0, as determined by the most restrictive license of its components (NLTK's stop words).

## Contributing

Contributions to the English Word Atlas are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Citation

If you use this dataset in your research, please cite:
```bibtex
@dataset{english_word_atlas_2024,
    title = {English Word Atlas},
    year = {2024},
    author = {[Your name]},
    note = {Combines multiple linguistic resources for comprehensive word analysis},
    url = {[repository URL]}
}
```

## Acknowledgments

### Core Word Lists
- **Swadesh Lists** (1952, 1955)
  - Created by Morris Swadesh
  - 100-word and 207-word lists for comparative linguistics
  - Public Domain

- **General Service List (GSL)**
  - Original GSL by Michael West (1953)
  - New GSL by Browne, Culligan & Phillips (2013)
  - Tokyo University of Foreign Studies

- **Ogden's Basic English** (1930)
  - Created by Charles Kay Ogden
  - Basic English Institute
  - Public Domain

- **Roget's Thesaurus** (1911, 15a edition)
  - Originally created by Peter Mark Roget (1779-1869)
  - 1911 edition edited by Robert A. Dutch
  - 15a edition extracted for this dataset
  - Public Domain

### Modern NLP Resources
- **ALL-MiniLM-L6-v2 Embeddings**
  - Created by Microsoft Research
  - MIT License
  - https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

### Stop Word Lists
- **NLTK Stop Words**
  - Natural Language Toolkit
  - Bird, Steven, Edward Loper and Ewan Klein (2009)
  - Apache License 2.0

- **scikit-learn Stop Words**
  - scikit-learn developers
  - BSD 3-Clause License

- **spaCy Stop Words**
  - Explosion AI
  - MIT License

- **Fox Stop Words**
  - Christopher Fox (1989)
  - "A Stop List for General Text"
  - Technical Report, University of Rochester

### Pronunciation Data
- **CMU Pronouncing Dictionary**
  - Carnegie Mellon University
  - Version 0.7b
  - Public Domain

## Contact

For questions or issues, please open an issue in the repository. 