# Changelog

All notable changes to the English Word Atlas will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-04-13

### Added
- Added support for Academic Word List (AWL) and Academic Vocabulary List (AVL) source lists.
- Added support for AFINN-111 sentiment word list as a source.
- Added numerous unit tests to improve coverage for `word_atlas.atlas`, `word_atlas.data`, and `word_atlas.wordlist` modules, focusing on error handling and edge cases.
- Added `overwrite` parameter to `WordlistBuilder.save()` method.

### Changed
- Regenerated `word_index.json` to include AWL and AVL words.
- Refactored tests in `tests/unit/test_data.py` for `get_data_dir` search logic using more robust mocking.
- Refactored tests in `tests/unit/test_atlas.py` for handling failed source loads during initialization and subsequent method calls.
- Improved overall test coverage significantly, ensuring all modules meet the 77% target (overall ~87%).
- Updated `README.md` to reflect current API usage (`get_sources`, `get_frequency`), remove references to obsolete data files (`word_data_base.json`), and clarify CLI command descriptions.
- Reformatted codebase using `black`.

## [0.1.4] - 2025-04-06

### Fixed
- Resolved multiple failing unit tests in `tests/unit/test_cli.py` related to mock setups and assertions (`test_info_json_output`, `test_search_numeric_attribute`, `test_search_phrase_filtering`, `test_search_verbose_output`, `test_info_roget_categories_overflow`, `test_wordlist_create_no_tags`, `test_wordlist_modify_file_not_found`).
- Corrected syntax and test logic issues introduced during test fixing.

### Added
- New unit tests in `tests/unit/test_main.py` to cover CLI argument parsing and command dispatch logic in `cli.main()`.
- New unit tests in `tests/unit/test_cli.py` to cover specific branches in command functions (`info_command`, `search_command`, `wordlist_create_command`).
- New fixture `mock_cli_atlas_many_roget` in `tests/conftest.py` for testing `info_command` edge case.

### Changed
- Increased overall test coverage from ~77% to 93.41%.
- Significantly improved test coverage for `word_atlas/cli.py` from ~64% to 87%.
- Updated `README.md` with current test status, improved API/CLI examples, updated testing instructions, and refined repository structure description.
- Enhanced mock data in `tests/conftest.py` (`mock_cli_atlas`) to improve coverage of detailed statistics calculation in `stats_command`.

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