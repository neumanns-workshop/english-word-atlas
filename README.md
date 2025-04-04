# English Wordlists API

A programmatic API for accessing classic, widely-used English wordlists.

## Overview

This repository provides developers with programmatic access to high-quality, curated English wordlists for common use cases. Instead of hunting down scattered text files or web scraping, this API offers a clean, consistent way to access and filter standard wordlists.

## Core Philosophy

This project intentionally focuses on **simple, classic wordlists** rather than complex linguistic data structures. We prioritize:

- **Raw word collections** over semantic networks or synsets
- **Minimal metadata** that's sufficient for practical use
- **Established, well-known lists** with historical significance
- **Practical filtering and combination options** for real-world applications

This approach ensures the API remains lightweight, easy to understand, and broadly applicable across various domains.

## Core Wordlists (MVP)

### Historical and Fundamental Lists
- **Swadesh List**: Core vocabulary lists used in comparative linguistics (100 word version)
- **Basic English**: Ogden's simplified subset of 850 English words
- **Roget's Thesaurus Categories**: Semantically categorized word lists derived from Roget's Thesaurus
  - 76 distinct categories organized by class and section
  - 2,163 unique words with clear semantic relationships
  - Hierarchical organization (Class → Section → Category)
  - Includes multi-word phrases that are semantically coherent

### Common English Lists
- **Dolch Sight Words**: 220 most common words that readers should recognize on sight
- **Fry's 1000 Instant Words**: Most frequently used English words

### Grammatical Parts of Speech
- **Prepositions**: Common English prepositions
- **Articles**: Definite and indefinite articles
- **Conjunctions**: Coordinating and subordinating conjunctions
- **Pronouns**: Personal, possessive, relative, and demonstrative pronouns
- **Auxiliary Verbs**: Helping verbs that support main verbs

### Technical Lists
- **Common English Stop Words**: Words typically filtered out in NLP applications
  - Customizable stop word sets from different sources (NLTK, spaCy, etc.)
  - Ability to combine or subtract from standard stop word lists

## Additional Valuable Lists

- **Dale-Chall Readability List**: ~3000 words familiar to US 4th graders
- **Academic Word List (Coxhead)**: Words common in academic texts

## Features (MVP)

- **Complete List Access**: Retrieve entire wordlists in JSON format
- **Pattern Matching**: Support for regex pattern matching across wordlists
- **Set Operations**: Check if words exist in specific lists with `isin` functionality
- **Consistent Format**: All lists available in standardized JSON format
- **Customizable Stop Words**: Create personalized stop word lists by combining or subtracting from standard lists
- **Word Frequencies**: Access frequency data for words and phrases from the SUBTLEX corpus

## Word Frequencies

The package includes frequency data from the SUBTLEX-US corpus, which is based on 51 million words from US film and TV subtitles. This provides more accurate frequency estimates for everyday language compared to traditional text-based corpora.

### Frequency Features

- **Precomputed Frequencies**: Fast access to frequency data for all words in our wordlists
- **Multiple Metrics**: Access various frequency metrics (raw count, per million, log frequency, etc.)
- **Multi-word Phrase Support**: Handles phrases (especially in Roget's thesaurus) by calculating component-based frequencies
- **Frequency Bands**: Group words into frequency bands (1-5, with 1 being most frequent)
- **Percentile Rankings**: See how words rank relative to others in the corpus

### Using Frequencies

```python
from wordlists.frequencies import FrequencyDictionary

# Initialize and load the frequency dictionary
freq_dict = FrequencyDictionary()
freq_dict.load()

# Get frequency for a single word (per million)
freq = freq_dict.get_frequency("computer")  # Returns 59.04

# Get all frequency metrics for a word
metrics = freq_dict.get_all_metrics("computer")
# Returns dictionary with freq_count, cd_count, subtl_wf, lg10wf, subtl_cd, lg10cd

# Get frequency for a multi-word phrase (e.g., from Roget's thesaurus)
phrase_freq = freq_dict.get_frequency("computer science")  # Returns 48.14

# Get frequency band (1-5, with 1 being most frequent)
band = freq_dict.get_frequency_band("the")  # Returns 1

# Get frequency percentile (0-100)
percentile = freq_dict.get_percentile("the")  # Returns 100.0

# Get most frequent words
top_words = freq_dict.get_most_frequent(10)
# Returns list of (word, frequency) tuples, sorted by frequency
```

## Usage

```javascript
import { getWordlist, createStopWordList, matchPattern, isInList } from 'wordlists';

// Get complete Basic English list
const basicEnglish = await getWordlist('basic-english');

// Get all words from a specific Roget category
const existenceWords = await getWordlist('roget-01001'); // "BEING, IN THE ABSTRACT"

// Get the complete Roget hierarchical structure
const rogetComplete = await getWordlist('roget-complete');

// Get all words from a specific Roget section
const existenceSection = rogetComplete.classes['WORDS EXPRESSING ABSTRACT RELATIONS']
                                    .sections['EXISTENCE'];

// Find all words in a specific semantic category
const motionWords = await matchPattern(/.*/, ['roget-12001']); // "MOTION IN GENERAL"

// Find all words matching a regex pattern
const contractions = await matchPattern(/\'s$/);  // Words ending with 's

// Check if specific words exist in a list
const results = await isInList(['hello', 'computer', 'spoon'], 'basic-english');
// Returns: { hello: true, computer: true, spoon: false }

// Create a custom stop word list
const customStopWords = createStopWordList({
  base: 'nltk',           // Start with NLTK's stop words
  add: ['custom', 'words'], // Add these words
  remove: ['not', 'no', 'nor'] // Remove negation words
});

// Get all prepositions
const prepositions = await getWordlist('prepositions');

// Combine grammatical elements
const functionalWords = await getWordlist(['articles', 'prepositions', 'conjunctions']);
```

## API Documentation

### Core Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `getWordlist(name)` | Retrieves complete wordlist | `name`: List identifier string or array of identifiers |
| `matchPattern(pattern, lists)` | Finds words matching regex pattern | `pattern`: RegExp object, `lists`: Optional array of list names to search (defaults to all) |
| `isInList(words, list)` | Checks if words exist in a list | `words`: Array of words to check, `list`: Name of list to check against |
| `createStopWordList(options)` | Creates custom stop word list | `options`: Configuration object with base list and modifications |

### List Identifiers

| Identifier | Description | Word Count |
|------------|-------------|------------|
| `swadesh-100` | Swadesh 100 word list | 100 |
| `basic-english` | Ogden's Basic English | 850 |
| `dolch` | Complete Dolch sight words | 220 |
| `fry-1000` | Complete Fry 1000 words | 1000 |
| `prepositions` | English prepositions | ~70 |
| `articles` | English articles | 3 |
| `conjunctions` | English conjunctions | ~25 |
| `pronouns` | English pronouns | ~35 |
| `auxiliary-verbs` | English auxiliary verbs | ~25 |
| `stop-words-nltk` | NLTK's English stop words | ~179 |
| `stop-words-spacy` | spaCy's English stop words | ~326 |
| `stop-words-smart` | SMART Information Retrieval stop words | ~571 |
| `stop-words-minimal` | Minimal English stop words | ~35 |
| `roget-complete` | Complete Roget's hierarchical structure | 2,163 |
| `roget-{id}` | Individual Roget category (e.g., `roget-01001`) | varies |

### Roget's Thesaurus Data Format

The Roget's Thesaurus data is organized hierarchically:

```javascript
{
  "classes": {
    "WORDS EXPRESSING ABSTRACT RELATIONS": {
      "name": "WORDS EXPRESSING ABSTRACT RELATIONS",
      "sections": {
        "EXISTENCE": {
          "name": "EXISTENCE",
          "categories": {
            "01001": {
              "name": "BEING, IN THE ABSTRACT",
              "id": "01001",
              "words": ["actually", "exist", "existence", ...]
            }
          }
        }
      }
    }
  },
  "total_categories": 76,
  "total_words": 2163
}
```

Individual category files are also available in a simpler format:

```javascript
{
  "class": "WORDS EXPRESSING ABSTRACT RELATIONS",
  "section": "EXISTENCE",
  "category": "BEING, IN THE ABSTRACT",
  "words": ["actually", "exist", "existence", ...]
}
```

## Project Structure

```
wordlists/
├── data/                  # Raw wordlist data files
│   ├── basic-english.json
│   ├── dolch.json
│   ├── fry-1000.json
│   ├── grammar/           # Grammatical parts of speech
│   │   ├── prepositions.json
│   │   ├── articles.json
│   │   ├── conjunctions.json
│   │   ├── pronouns.json
│   │   └── auxiliary-verbs.json
│   ├── stop-words/        # Multiple stop word list variants
│   │   ├── nltk.json
│   │   ├── spacy.json
│   │   ├── smart.json
│   │   └── minimal.json
│   ├── wordlists/         # Categorized word lists
│   │   └── categories/
│   │       └── roget/     # Roget's Thesaurus derived lists
│   │           ├── roget_unified.json    # Complete hierarchical data
│   │           ├── index.json            # Category index with metadata
│   │           └── [category files...]   # Individual category files
│   └── swadesh-100.json
│   ├── frequencies/       # Word frequency data
│   │   ├── subtlex_us.txt                 # Raw SUBTLEX frequency data
│   │   └── precomputed_frequencies.json   # Precomputed frequencies for all wordlists
│   ├── dictionaries/      # Pronunciation dictionaries
│   │   ├── cmudict-0.7b                   # CMU Pronunciation Dictionary
│   │   └── precomputed_pronunciations.json # Precomputed pronunciations for all wordlists
├── src/                   # Source code
│   ├── index.js           # Main entry point
│   ├── wordlists.js       # Core wordlist functions
│   ├── stop-words.js      # Stop word customization functions
│   ├── grammar.js         # Grammatical categories functions
│   └── utils.js           # Helper utilities
├── python/                # Python implementation
│   ├── wordlists/         # Python package
│   │   ├── __init__.py    # Package initialization
│   │   ├── wordlists.py   # Core functionality
│   │   ├── frequencies.py # Frequency functionality
│   │   ├── arpabet.py     # Pronunciation functionality
│   │   └── types.py       # Type definitions
│   ├── examples/          # Example scripts
│   └── scripts/           # Utility scripts for precomputation
├── package.json           # Project metadata and dependencies
└── README.md              # This documentation file
```

## Future Enhancements (Post-MVP)

- Additional wordlists (Oxford 3000, IELTS vocabulary, etc.)
- Advanced filtering (by part of speech, frequency)
- Simple word metadata (length, syllable count)
- CLI tools and REST API endpoints
- Domain-specific stop word lists (medical, legal, technical)
- Dictionary-free word statistics (frequency, commonality)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# Wordlists

A collection of curated word lists for various purposes, including stop words and semantic categories.

## Data Structure

```
data/
├── wordlists/
│   ├── categories/           # Semantic category word lists
│   │   └── roget/           # Roget's Thesaurus categories
│   │       ├── index.json   # Category index with metadata
│   │       └── *.json       # Individual category files
│   │
│   └── stop_words/          # Stop word lists from various sources
│       ├── nltk_stop_words.json      # NLTK English corpus (Apache 2.0)
│       ├── spacy_stop_words.json     # spaCy English model (MIT)
│       ├── sklearn_stop_words.json   # scikit-learn English corpus (BSD-3)
│       ├── minimal_stop_words.json   # Common words across all sources
│       └── comprehensive_stop_words.json  # All words from all sources
├── frequencies/
│   ├── subtlex_us.txt                # SUBTLEX-US frequency data
│   └── precomputed_frequencies.json  # Precomputed frequencies for all words
├── dictionaries/
│   ├── cmudict-0.7b                  # CMU Pronunciation Dictionary
│   └── precomputed_pronunciations.json # Precomputed pronunciations
```

## Stop Words

Stop words are common words that are often filtered out in natural language processing tasks. Our collection includes:

### Source Lists
- **NLTK** (Apache License 2.0)
  - From the NLTK English corpus
  - Comprehensive list of common English stop words

- **spaCy** (MIT License)
  - From the spaCy English model
  - Includes contractions and common function words

- **scikit-learn** (BSD 3-Clause License)
  - From the scikit-learn English corpus
  - Focused on common English words

### Combined Lists
- **Minimal Stop Words**
  - Intersection of words common across all sources
  - Most conservative approach to stop word filtering

- **Comprehensive Stop Words**
  - Union of all words from all sources
  - Most inclusive approach to stop word filtering

## Categories

### Roget's Thesaurus Categories
Organized semantic categories from Roget's Thesaurus, including:
- Abstract concepts (being, relation, quantity)
- Physical concepts (matter, space, time)
- Mental concepts (intellect, emotion, morality)
- Social concepts (interaction, communication, behavior)

Each category file contains:
- Category name and number
- Section information
- List of related words with parts of speech
- Metadata about the category

## Usage

### Stop Words
```python
import json

# Load a specific stop word list
with open('data/wordlists/stop_words/nltk_stop_words.json') as f:
    stop_words = json.load(f)['words']

# Load the minimal stop word list
with open('data/wordlists/stop_words/minimal_stop_words.json') as f:
    minimal_stop_words = json.load(f)['words']
```

### Categories
```python
import json

# Load the category index
with open('data/wordlists/categories/roget/index.json') as f:
    categories = json.load(f)

# Load a specific category
with open('data/wordlists/categories/roget/001_being_in_the_abstract.json') as f:
    category = json.load(f)
```

## License

This project includes data from various sources, each with its own license:
- NLTK data: Apache License 2.0
- spaCy data: MIT License
- scikit-learn data: BSD 3-Clause License

Please refer to individual source files for specific licensing information. 