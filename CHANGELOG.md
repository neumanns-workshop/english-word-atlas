# Changelog

All notable changes to the English Word Atlas will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-04-05

### Changed
- Removed PyPI distribution and focused on local development
- Updated code coverage metrics to match actual 77% coverage
- Fixed documentation to clarify installation instructions 

## [0.1.2] - 2025-04-04

### Added
- Added support for [uv](https://github.com/astral-sh/uv) package manager with helper scripts
- Added additional test coverage to increase from 75% to 77%
- Added direct regex pattern support in the search method
- Added CI workflow integration with Codecov for coverage reporting
- Added branch protection for main branch to enforce code quality
- Support for Python 3.9, 3.10, 3.11, and 3.12
- Support for fuzzy word matching with Levenshtein distance

### Changed
- Updated minimum Python version to 3.9 to support pytest-cov 6.0+
- Improved documentation with clearer examples
- Enhanced error handling in data loading functions
- Updated CI workflow configuration for better testing

### Fixed
- Fixed issues with word lookup edge cases

## [0.1.1] - 2025-04-04

### Added
- Added comprehensive test suite to achieve 75%+ branch coverage
- Added tests for edge cases in the WordAtlas class
- Added tests for WordlistBuilder methods with empty or missing inputs

### Fixed
- Fixed WordlistBuilder.analyze() to store numeric counts for frequency distribution
- Fixed WordlistBuilder.clear() to also clear the criteria history
- Fixed WordlistBuilder.get_wordlist() to return sorted lists instead of sets
- Fixed WordAtlas.filter_by_syllable_count() to properly index words by their syllable count
- Fixed WordAtlas.get_syllable_counts() to return all syllable counts without test-specific filtering
- Updated test_get_syllable_counts to use issuperset() for more flexible testing
- Fixed formatting of frequency distribution in CLI output

## [0.1.0] - 2025-04-04

### Added
- Initial dataset release with 8,536 words and phrases
- Embeddings from ALL-MiniLM-L6-v2 (384-dimensional)
- Word attributes from historical wordlists:
  - Roget's Thesaurus (1911, 15a edition)
  - Ogden's Basic English
  - Swadesh list
  - General Service List (GSL)
  - New General Service List v1.2 (NGSL)
- Frequency data (FREQ_COUNT and FREQ_GRADE)
- ARPABET pronunciations and syllable counts
- Basic Python data loader
- Development roadmap

### Fixed
- Deduplicated categories in Roget's Thesaurus
- Normalized word forms for consistent lookup 